import os
import json
import time
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
from engine import fetch_data, calculate_ict_indicators

NSE_LIST_FILE = "nse_list.csv"
RESULTS_FILE = "scanner_results.json"
MAX_STOCKS = 2000

def get_tickers():
    if not os.path.exists(NSE_LIST_FILE):
        return []
    try:
        df = pd.read_csv(NSE_LIST_FILE)
        # Ensure 'SYMBOL' exists
        if 'SYMBOL' in df.columns:
            # Append .NS for Yahoo Finance
            tickers = [str(sym).strip() + ".NS" for sym in df['SYMBOL'].tolist() if pd.notna(sym)]
            return tickers[:MAX_STOCKS]
    except Exception as e:
        print(f"Error reading {NSE_LIST_FILE}: {e}")
    return []

def scan_single_ticker(ticker):
    try:
        # Fetch 6mo for VWMA and Swings without excess overhead
        df = fetch_data(ticker, period="6mo", interval="1d")
        if df.empty or len(df) < 50:
            return None
            
        df, ict_data = calculate_ict_indicators(ticker, df, generate_logs=False)
        
        latest_scan = df.iloc[-1]
        cur_price = latest_scan['Close']
        cur_rsi = latest_scan['RSI_14']
        
        bull_bias = ict_data.get('dynamic_bull_bias', False)
        bear_bias = ict_data.get('dynamic_bear_bias', False)
        
        entry = {
            "Ticker": ticker.replace(".NS", ""),
            "Price": round(float(cur_price), 2),
            "RSI": round(float(cur_rsi), 2),
            "Bias": "Bullish" if bull_bias else "Bearish" if bear_bias else "Neutral"
        }
        return entry
    except Exception as e:
        # Silently fail for individual tickers (delisted, no data, etc.)
        return None

def run_background_scan():
    tickers = get_tickers()
    if not tickers:
        print("No tickers found. Make sure nse_list.csv is present.")
        return

    print(f"Starting parallel scan of {len(tickers)} Indian stocks...")
    start_time = time.time()
    
    bullish_list = []
    bearish_list = []
    
    # Use ThreadPoolExecutor for concurrent fetching
    # 20 workers provides a good balance between speed and avoiding Yahoo rate limits
    with ThreadPoolExecutor(max_workers=20) as executor:
        future_to_ticker = {executor.submit(scan_single_ticker, ticker): ticker for ticker in tickers}
        
        completed = 0
        for future in as_completed(future_to_ticker):
            completed += 1
            if completed % 100 == 0:
                print(f"Processed {completed}/{len(tickers)} stocks...")
                
            res = future.result()
            if res:
                if res['Bias'] == 'Bullish':
                    bullish_list.append(res)
                elif res['Bias'] == 'Bearish':
                    bearish_list.append(res)

    end_time = time.time()
    print(f"Scan complete in {round(end_time - start_time, 2)} seconds.")
    print(f"Found {len(bullish_list)} Bullish and {len(bearish_list)} Bearish setups.")
    
    # Sort lists by momentum
    bullish_list = sorted(bullish_list, key=lambda x: x['RSI'], reverse=True)
    bearish_list = sorted(bearish_list, key=lambda x: x['RSI'])
    
    # Save results
    results = {
        "last_updated": time.strftime("%Y-%m-%d %H:%M:%S"),
        "total_scanned": len(tickers),
        "bullish": bullish_list,
        "bearish": bearish_list
    }
    
    with open(RESULTS_FILE, "w") as f:
        json.dump(results, f, indent=4)
    print("Results successfully saved to scanner_results.json")

if __name__ == "__main__":
    run_background_scan()
