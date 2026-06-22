import requests
import json

def format_telegram_message(bullish_list, bearish_list):
    """
    Formats the top bullish and bearish lists into a clean, professional Telegram message
    emulating the 'Hermes AI Agent' persona.
    """
    msg_lines = []
    msg_lines.append("🤖 *Hermes AI Agent - Institutional Signals* 🤖")
    msg_lines.append("===================================")
    msg_lines.append(f"🎯 *Top Probable Setups*")
    msg_lines.append("")
    
    if bullish_list:
        msg_lines.append("🟢 *BULLISH CANDIDATES (Top 10)*")
        for idx, item in enumerate(bullish_list, 1):
            ticker = item.get('Ticker', 'N/A')
            # Extract price safely since item might come from scanner_results or enriched list
            price = item.get('Price', 'N/A') 
            rsi = item.get('RSI', 'N/A')
            score = item.get('Fund. Score', 'N/A')
            verdict = item.get('AI Verdict', 'N/A')
            
            msg_lines.append(f"{idx}. *{ticker}* | ₹{price}")
            msg_lines.append(f"   📈 RSI: {rsi} | Score: {score}")
            msg_lines.append(f"   🤖 {verdict}")
        msg_lines.append("")
        
    if bearish_list:
        msg_lines.append("🔴 *BEARISH CANDIDATES (Top 10)*")
        for idx, item in enumerate(bearish_list, 1):
            ticker = item.get('Ticker', 'N/A')
            price = item.get('Price', 'N/A')
            rsi = item.get('RSI', 'N/A')
            score = item.get('Fund. Score', 'N/A')
            verdict = item.get('AI Verdict', 'N/A')
            
            msg_lines.append(f"{idx}. *{ticker}* | ₹{price}")
            msg_lines.append(f"   📉 RSI: {rsi} | Score: {score}")
            msg_lines.append(f"   🤖 {verdict}")
            
    msg_lines.append("")
    msg_lines.append("⚠️ *Disclaimer:* Automated AI Output. Not financial advice.")
    
    return "\n".join(msg_lines)


def send_telegram_message(bot_token, chat_id, text):
    """
    Sends a formatted message to a Telegram chat/channel using the Bot API.
    """
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown"
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        return True, "Message broadcasted successfully!"
    except Exception as e:
        err_msg = str(e)
        if hasattr(e, 'response') and e.response is not None and hasattr(e.response, 'text'):
            err_msg += f" | Response: {e.response.text}"
        return False, f"Failed to send to Telegram: {err_msg}"
