import os
import json
import time
from telegram_utils import format_telegram_message, send_telegram_message
from fundamental import get_fundamental_score

# ==========================================
# CONFIGURATION
# ==========================================
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "@sudhir_ict_signals")
SCANNER_FILE = "scanner_results.json"

def get_top_candidates(raw_list, req_count=10):
    enriched = []
    for item in raw_list:
        if len(enriched) >= req_count:
            break
            
        # Filter 1: Price > 55
        if item.get("Price", 0) <= 55:
            continue
            
        ticker = item["Ticker"]
        if not ticker.endswith(".NS") and not ticker.endswith(".BO"):
            ticker += ".NS"
            
        score, verdict, volume = get_fundamental_score(ticker)
        
        # Filter 2: Volume > 300,000
        if volume <= 300000:
            continue
        
        verdict_clean = verdict.replace("Strong ", "")
        v_emoji = "🟢" if "BUY" in verdict_clean or "Accumulate" in verdict_clean else "🔴" if "SELL" in verdict_clean else "⚪"
            
        enriched.append({
            "Ticker": item["Ticker"],
            "Price": item.get("Price", "N/A"),
            "ICT Bias": item["Bias"],
            "RSI": item["RSI"],
            "Vol (K)": f"{volume/1000:.0f}K",
            "Fund. Score": f"{score}/10",
            "AI Verdict": f"{v_emoji} {verdict}"
        })
    return enriched

def run_daily_broadcast():
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Starting Daily Hermes Broadcast to {TELEGRAM_CHAT_ID}...")
    
    if TELEGRAM_BOT_TOKEN == "YOUR_BOT_TOKEN_HERE" or not TELEGRAM_BOT_TOKEN:
        print("ERROR: Telegram Bot Token is not set. Please set TELEGRAM_BOT_TOKEN environment variable.")
        return
        
    if not os.path.exists(SCANNER_FILE):
        print(f"ERROR: {SCANNER_FILE} not found. Ensure the scanner has run today.")
        return
        
    with open(SCANNER_FILE, "r") as f:
        scan_data = json.load(f)
        
    print("Crunching fundamental data for Top 10 Bullish and Bearish candidates...")
    bullish_final = get_top_candidates(scan_data.get("bullish", []), 10)
    bearish_final = get_top_candidates(scan_data.get("bearish", []), 10)
    
    msg_text = format_telegram_message(bullish_final, bearish_final)
    
    print("Formatting complete. Dispatching to Telegram...")
    success, resp = send_telegram_message(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, msg_text)
    
    if success:
        print(f"✅ Success! {resp}")
    else:
        print(f"❌ Failed! {resp}")

if __name__ == "__main__":
    run_daily_broadcast()
