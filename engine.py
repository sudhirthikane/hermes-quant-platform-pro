import yfinance as yf
import pandas as pd
import numpy as np
import ta
import json
import os

LOG_FILE = "signals_log.json"

def fetch_data(ticker: str, period: str = "1y", interval: str = "1d") -> pd.DataFrame:
    df = yf.download(ticker, period=period, interval=interval, progress=False)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.droplevel(1)
    return df

def calculate_ict_indicators(ticker: str, df: pd.DataFrame, generate_logs=False):
    if df.empty:
        return df, {}
        
    df['RSI_14'] = ta.momentum.RSIIndicator(close=df['Close'], window=14).rsi()
    df['ATR_14'] = ta.volatility.AverageTrueRange(high=df['High'], low=df['Low'], close=df['Close'], window=14).average_true_range()
    
    df['Volume'] = df['Volume'].replace(0, 1)
    df['VWMA_50'] = (df['Close'] * df['Volume']).rolling(50).sum() / df['Volume'].rolling(50).sum()
    
    ch_look = int(round(50 * 0.7))
    df['CH_High'] = df['High'].rolling(ch_look).max()
    df['CH_Low'] = df['Low'].rolling(ch_look).min()
    
    liq_strength = 5
    last_swing_high = None
    last_swing_low = None
    dynamic_bull_bias = False
    dynamic_bear_bias = False
    
    fvg_boxes = []
    ob_boxes = []
    liq_lines = []
    signals = []
    
    dates = df.index
    close_arr = df['Close'].values
    high_arr = df['High'].values
    low_arr = df['Low'].values
    open_arr = df['Open'].values
    atr_arr = df['ATR_14'].values
    rsi_arr = df['RSI_14'].values
    
    def is_swing_high(i):
        if i < liq_strength or i > len(df) - liq_strength - 1: return False
        val = high_arr[i]
        for j in range(i - liq_strength, i + liq_strength + 1):
            if high_arr[j] > val: return False
        return True

    def is_swing_low(i):
        if i < liq_strength or i > len(df) - liq_strength - 1: return False
        val = low_arr[i]
        for j in range(i - liq_strength, i + liq_strength + 1):
            if low_arr[j] < val: return False
        return True
        
    last_bull_ob_idx = None
    last_bear_ob_idx = None
    mintick = 0.01

    bias_col = []

    for i in range(len(df)):
        if i < 2: 
            bias_col.append('NEUTRAL')
            continue
            
        if i >= liq_strength * 2:
            pivot_idx = i - liq_strength
            if is_swing_high(pivot_idx):
                last_swing_high = high_arr[pivot_idx]
                liq_lines.append({'type': 'BSL', 'index': dates[pivot_idx], 'price': last_swing_high})
            if is_swing_low(pivot_idx):
                last_swing_low = low_arr[pivot_idx]
                liq_lines.append({'type': 'SSL', 'index': dates[pivot_idx], 'price': last_swing_low})
                
        prev_bull = dynamic_bull_bias
        prev_bear = dynamic_bear_bias
        
        if last_swing_high and close_arr[i] > last_swing_high:
            dynamic_bull_bias = True
            dynamic_bear_bias = False
        if last_swing_low and close_arr[i] < last_swing_low:
            dynamic_bull_bias = False
            dynamic_bear_bias = True
            
        if dynamic_bull_bias and not prev_bull:
            signals.append({'timestamp': dates[i], 'ticker': ticker, 'action': 'MSS BULLISH', 'price': close_arr[i], 'rsi': rsi_arr[i]})
        if dynamic_bear_bias and not prev_bear:
            signals.append({'timestamp': dates[i], 'ticker': ticker, 'action': 'MSS BEARISH', 'price': close_arr[i], 'rsi': rsi_arr[i]})
            
        bias_col.append('BULLISH' if dynamic_bull_bias else 'BEARISH' if dynamic_bear_bias else 'NEUTRAL')
            
        bull_fvg = low_arr[i] > high_arr[i-2] and (low_arr[i] - high_arr[i-2]) > mintick * 2 and dynamic_bull_bias
        bear_fvg = high_arr[i] < low_arr[i-2] and (low_arr[i-2] - high_arr[i]) > mintick * 2 and dynamic_bear_bias
        
        if bull_fvg:
            fvg_boxes.append({'type': 'Bull FVG', 'start': dates[i-2], 'top': low_arr[i], 'bot': high_arr[i-2], 'active': True})
            signals.append({'timestamp': dates[i], 'ticker': ticker, 'action': 'Bullish FVG', 'price': close_arr[i], 'rsi': rsi_arr[i]})
        if bear_fvg:
            fvg_boxes.append({'type': 'Bear FVG', 'start': dates[i-2], 'top': low_arr[i-2], 'bot': high_arr[i], 'active': True})
            signals.append({'timestamp': dates[i], 'ticker': ticker, 'action': 'Bearish FVG', 'price': close_arr[i], 'rsi': rsi_arr[i]})
            
        for b in fvg_boxes:
            if not b['active']: continue
            if b['type'] == 'Bull FVG' and close_arr[i] < b['bot']:
                b['active'] = False
                b['end'] = dates[i]
            elif b['type'] == 'Bear FVG' and close_arr[i] > b['top']:
                b['active'] = False
                b['end'] = dates[i]
                
        # Check active status of OBs
        for ob in ob_boxes:
            if not ob.get('active', True): continue
            if ob['type'] == 'Bull OB' and close_arr[i] < ob['bot']:
                ob['active'] = False
                ob['end'] = dates[i]
            elif ob['type'] == 'Bear OB' and close_arr[i] > ob['top']:
                ob['active'] = False
                ob['end'] = dates[i]
                
        atr_val = atr_arr[i]
        if not np.isnan(atr_val):
            bull_disp = close_arr[i] > open_arr[i] and (close_arr[i] - open_arr[i]) > (atr_val * 2.0) and close_arr[i] > high_arr[i-1] and dynamic_bull_bias
            bear_disp = close_arr[i] < open_arr[i] and (open_arr[i] - close_arr[i]) > (atr_val * 2.0) and close_arr[i] < low_arr[i-1] and dynamic_bear_bias
            
            if bull_disp:
                for j in range(1, 26):
                    if i-j < 0: break
                    if close_arr[i-j] < open_arr[i-j]:
                        if last_bull_ob_idx is None or (i-j) > last_bull_ob_idx:
                            top = max(open_arr[i-j], close_arr[i-j])
                            bot = min(open_arr[i-j], close_arr[i-j])
                            
                            # Check if it was already mitigated before being identified
                            mitigated = False
                            end_date = None
                            for k in range(i-j + 1, i + 1):
                                if close_arr[k] < bot:
                                    mitigated = True
                                    end_date = dates[k]
                                    break
                                    
                            ob_boxes.append({
                                'type': 'Bull OB', 
                                'start': dates[i-j], 
                                'top': top, 
                                'bot': bot, 
                                'active': not mitigated,
                                'end': end_date
                            })
                            last_bull_ob_idx = i-j
                            signals.append({'timestamp': dates[i], 'ticker': ticker, 'action': 'Bull OB Long', 'price': close_arr[i], 'rsi': rsi_arr[i]})
                            break

            if bear_disp:
                for j in range(1, 26):
                    if i-j < 0: break
                    if close_arr[i-j] > open_arr[i-j]:
                        if last_bear_ob_idx is None or (i-j) > last_bear_ob_idx:
                            top = max(open_arr[i-j], close_arr[i-j])
                            bot = min(open_arr[i-j], close_arr[i-j])
                            
                            # Check if it was already mitigated before being identified
                            mitigated = False
                            end_date = None
                            for k in range(i-j + 1, i + 1):
                                if close_arr[k] > top:
                                    mitigated = True
                                    end_date = dates[k]
                                    break
                                    
                            ob_boxes.append({
                                'type': 'Bear OB', 
                                'start': dates[i-j], 
                                'top': top, 
                                'bot': bot, 
                                'active': not mitigated,
                                'end': end_date
                            })
                            last_bear_ob_idx = i-j
                            signals.append({'timestamp': dates[i], 'ticker': ticker, 'action': 'Bear OB Short', 'price': close_arr[i], 'rsi': rsi_arr[i]})
                            break

    df['Bias'] = bias_col
    
    # Cap memory lists roughly like pinescript
    fvg_boxes = fvg_boxes[-20:]
    ob_boxes = ob_boxes[-12:]
    liq_lines = liq_lines[-16:]
    
    ict_data = {
        'fvg': fvg_boxes,
        'ob': ob_boxes,
        'liq': liq_lines,
        'dynamic_bull_bias': dynamic_bull_bias,
        'dynamic_bear_bias': dynamic_bear_bias
    }
    
    if generate_logs and signals:
        write_logs(signals)
        
    return df, ict_data

def write_logs(new_signals):
    logs = []
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f:
            try:
                logs = json.load(f)
            except:
                pass
                
    for sig in new_signals:
        sig_entry = {
            "timestamp": sig['timestamp'].isoformat() if hasattr(sig['timestamp'], 'isoformat') else str(sig['timestamp']),
            "ticker": sig['ticker'],
            "action": sig['action'],
            "price": round(float(sig['price']), 2),
            "rsi": round(float(sig['rsi']), 2) if not np.isnan(sig['rsi']) else 0.0
        }
        if not any(l['timestamp'] == sig_entry['timestamp'] and l['ticker'] == sig_entry['ticker'] and l['action'] == sig_entry['action'] for l in logs):
            logs.append(sig_entry)
            
    with open(LOG_FILE, "w") as f:
        json.dump(logs, f, indent=4)

def analyze_indian_sectors():
    sectors = {
        "Nifty Bank": "^NSEBANK",
        "Nifty IT": "^CNXIT",
        "Nifty Auto": "^CNXAUTO",
        "Nifty FMCG": "^CNXFMCG",
        "Nifty Metal": "^CNXMETAL",
        "Nifty Pharma": "^CNXPHARMA",
        "Nifty Energy": "^CNXENERGY",
        "Nifty Realty": "^CNXREALTY",
        "Nifty Infra": "^CNXINFRA",
        "Nifty PSE": "^CNXPSE"
    }
    results = []
    for name, ticker in sectors.items():
        try:
            df = yf.download(ticker, period="3mo", interval="1d", progress=False)
            if df.empty: continue
            
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.droplevel(1)
                
            close_prices = df['Close']
            
            if len(close_prices) > 21:
                ret_1m = (close_prices.iloc[-1] - close_prices.iloc[-21]) / close_prices.iloc[-21] * 100
            else:
                ret_1m = 0
                
            rsi = ta.momentum.RSIIndicator(close=close_prices, window=14).rsi().iloc[-1]
            if pd.isna(rsi): rsi = 50
            
            # Hermes Trend Score Calculation
            score = (ret_1m * 3) + (rsi - 50)
            
            results.append({
                "Sector": name,
                "Return_1M": ret_1m,
                "RSI": rsi,
                "TrendScore": score
            })
        except Exception:
            pass
            
    # Sort by Score
    results = sorted(results, key=lambda x: x["TrendScore"], reverse=True)
    return results

if __name__ == "__main__":
    if os.path.exists(LOG_FILE):
        os.remove(LOG_FILE)
    TICKERS = ["AAPL", "MSFT", "RELIANCE.NS"]
    for ticker in TICKERS:
        print(f"Generating ICT signals for {ticker}...")
        df = fetch_data(ticker)
        calculate_ict_indicators(ticker, df, generate_logs=True)
    print("Done generating ICT logs.")
