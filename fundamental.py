import yfinance as yf
import math

def is_invalid(val):
    return val is None or val == 0 or (isinstance(val, float) and (math.isnan(val) or math.isinf(val)))

def safe_get(info, keys, default=0.0):
    for k in keys:
        val = info.get(k)
        if val is not None:
            try:
                fval = float(val)
                if not math.isnan(fval):
                    return fval
            except:
                pass
    return default

def format_pct(val):
    if is_invalid(val): return "N/A"
    return f"{val * 100:.2f}%"

def format_num(val):
    if is_invalid(val): return "N/A"
    return f"{val:.2f}"

def get_fundamental_score(ticker_symbol):
    ticker = yf.Ticker(ticker_symbol)
    try:
        info = ticker.info
    except Exception:
        info = {}
    
    if not info and ("-USD" not in ticker_symbol and "=X" not in ticker_symbol):
        return 0, "Avoid", 0

    pe = safe_get(info, ['trailingPE', 'forwardPE'], 0)
    pb = safe_get(info, ['priceToBook'], 0)
    roe = safe_get(info, ['returnOnEquity'], 0)
    opm = safe_get(info, ['operatingMargins'], 0)
    de_ratio = safe_get(info, ['debtToEquity'], 0)
    if de_ratio > 10: de_ratio = de_ratio / 100.0
    current_ratio = safe_get(info, ['currentRatio'], 0)
    rev_growth = safe_get(info, ['revenueGrowth'], 0)
    fcf = safe_get(info, ['freeCashflow'], 0)
    insiders = safe_get(info, ['heldPercentInsiders'], 0)
    institutions = safe_get(info, ['heldPercentInstitutions'], 0)

    score = 0
    if 0 < pe < 25: score += 1
    if 0 < pb < 3: score += 1
    if roe > 0.15: score += 1
    if opm > 0.10: score += 1
    if de_ratio < 1.0: score += 1
    if current_ratio > 1.2: score += 1
    if rev_growth > 0.10: score += 1
    if fcf > 0: score += 1
    if insiders > 0.40: score += 1
    if institutions > 0.15: score += 1

    if score >= 9: verdict = "Strong BUY"
    elif score >= 7: verdict = "Accumulate"
    elif score >= 5: verdict = "HOLD"
    elif score >= 3: verdict = "SELL"
    else: verdict = "Avoid"
    
    volume = safe_get(info, ['averageVolume', 'volume'], 0)
    
    return score, verdict, volume

def generate_fundamental_report(ticker_symbol):
    ticker = yf.Ticker(ticker_symbol)
    try:
        info = ticker.info
    except Exception as e:
        if "-USD" in ticker_symbol or "-INR" in ticker_symbol or "=X" in ticker_symbol:
            is_crypto = "-USD" in ticker_symbol or "-INR" in ticker_symbol
            info = {'longName': ticker_symbol, 'quoteType': 'CRYPTOCURRENCY' if is_crypto else 'CURRENCY'}
            try:
                info['regularMarketPrice'] = ticker.fast_info.get('lastPrice', 0)
                info['marketCap'] = ticker.fast_info.get('marketCap', 0)
            except:
                pass
        else:
            return f"Error fetching data for {ticker_symbol}: {str(e)}"
    
    if not info:
        return f"Could not find valid fundamental data for {ticker_symbol}."

    name = info.get('longName', info.get('shortName', ticker_symbol))
    sector = info.get('sector', 'Unknown Sector')
    industry = info.get('industry', 'Unknown Industry')
    exchange = info.get('exchange', 'Unknown Exchange')

    # Fetch Metrics
    pe = safe_get(info, ['trailingPE', 'forwardPE'], 0)
    pb = safe_get(info, ['priceToBook'], 0)
    ev_ebitda = safe_get(info, ['enterpriseToEbitda'], 0)
    peg = safe_get(info, ['pegRatio'], 0)

    roe = safe_get(info, ['returnOnEquity'], 0)
    opm = safe_get(info, ['operatingMargins'], 0)
    npm = safe_get(info, ['profitMargins'], 0)
    
    de_ratio = safe_get(info, ['debtToEquity'], 0)
    # yfinance gives D/E in percentage sometimes (e.g. 36 means 0.36 or 36%)
    # Typically, if it's > 10, it's a percentage. Let's normalize to ratio.
    if de_ratio > 10: de_ratio = de_ratio / 100.0

    current_ratio = safe_get(info, ['currentRatio'], 0)
    quick_ratio = safe_get(info, ['quickRatio'], 0)

    rev_growth = safe_get(info, ['revenueGrowth'], 0)
    earn_growth = safe_get(info, ['earningsGrowth'], 0)
    fcf = safe_get(info, ['freeCashflow'], 0)

    insiders = safe_get(info, ['heldPercentInsiders'], 0)
    institutions = safe_get(info, ['heldPercentInstitutions'], 0)

    # Scoring Logic (Max 10)
    score = 0
    catalysts = []
    risks = []

    # 1. Valuation (2 points)
    if 0 < pe < 25: 
        score += 1
        catalysts.append("Attractive P/E valuation relative to market.")
    elif pe > 40:
        risks.append("Extremely high P/E indicates overvaluation.")
        
    if 0 < pb < 3: 
        score += 1
    elif pb > 8:
        risks.append("High Price-to-Book multiple prices in perfection.")

    # 2. Profitability (2 points)
    if roe > 0.15: 
        score += 1
        catalysts.append("Consistently strong Return on Equity (>15%).")
    elif roe < 0.05 and roe != 0:
        risks.append("Weak Return on Equity indicates poor capital allocation.")
        
    if opm > 0.10: 
        score += 1
    elif opm < 0:
        risks.append("Negative operating margins.")

    # 3. Health (2 points)
    if de_ratio < 1.0: 
        score += 1
    elif de_ratio > 2.0:
        risks.append("High debt-to-equity ratio poses leverage risk.")
        
    if current_ratio > 1.2: 
        score += 1
    elif current_ratio > 0 and current_ratio < 1.0:
        risks.append("Current ratio < 1 suggests short-term liquidity stress.")

    # 4. Growth (2 points)
    if rev_growth > 0.10: 
        score += 1
        catalysts.append("Double-digit revenue growth trajectory.")
    elif rev_growth < 0:
        risks.append("Contracting top-line revenues.")
        
    if fcf > 0: 
        score += 1
    elif fcf < 0:
        risks.append("Cash burn and negative free cash flow generation.")

    # 5. Management (2 points)
    if insiders > 0.40: 
        score += 1
        catalysts.append("High promoter skin-in-the-game (>40%).")
    if institutions > 0.15: 
        score += 1

    # Base case for catalysts/risks
    if not catalysts: catalysts.append("Stable macro environment and sector tailwinds.")
    if not risks: risks.append("Broader market corrections and macroeconomic downturns.")

    # Rating System
    if score >= 9:
        verdict = "Strong BUY"
        stars = "★★★★★"
    elif score >= 7:
        verdict = "Accumulate (Wait for Dips)"
        stars = "★★★★☆"
    elif score >= 5:
        verdict = "HOLD"
        stars = "★★★☆☆"
    elif score >= 3:
        verdict = "SELL"
        stars = "★★☆☆☆"
    else:
        verdict = "Avoid"
        stars = "★☆☆☆☆"

    if is_invalid(fcf):
        fcf_str = "N/A"
    else:
        fcf_str = f"${fcf:,.0f}" if fcf > 0 else f"-${abs(fcf):,.0f}"

    # Events
    events_text = "No major upcoming events or earnings dates found."
    try:
        cal = ticker.calendar
        if isinstance(cal, dict) and 'Earnings Date' in cal:
            dates = [str(d.date()) if hasattr(d, 'date') else str(d) for d in cal['Earnings Date']]
            events_text = f"**Upcoming Earnings:** {', '.join(dates)}"
    except:
        events_text = "Upcoming Events data unavailable."
        
    # News
    news_html = ""
    try:
        news_data = ticker.news
        if not news_data or len(news_data) == 0:
            import urllib.request
            import xml.etree.ElementTree as ET
            try:
                query = ticker_symbol.replace(".NS", "").replace(".BO", "")
                url = f"https://news.google.com/rss/search?q={query}+stock&hl=en-US&gl=US&ceid=US:en"
                req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req, timeout=5) as response:
                    xml_data = response.read()
                root = ET.fromstring(xml_data)
                news_data = []
                for item in root.findall('.//item')[:3]:
                    t = item.find('title').text if item.find('title') is not None else "News Update"
                    l = item.find('link').text if item.find('link') is not None else "#"
                    if " - " in t:
                        h, p = t.rsplit(" - ", 1)
                    else:
                        h, p = t, "Google News"
                    news_data.append({'title': h, 'link': l, 'publisher': p})
            except:
                pass

        if news_data and len(news_data) > 0:
            for item in news_data[:3]:
                title = item.get('title', 'News Update')
                link = item.get('link', '#')
                publisher = item.get('publisher', 'Unknown')
                news_html += f"<div style='margin-bottom: 12px; padding: 12px; background: rgba(128,128,128,0.05); border-left: 3px solid #3B82F6; border-radius: 6px;'><strong style='font-size: 15px;'>{title}</strong> <span style='color: gray; font-size: 13px;'>({publisher})</span><br><a href='{link}' target='_blank' style='color: #3B82F6; text-decoration: none; font-size: 13px; margin-top: 5px; display: inline-block;'>🔗 Read Source Article</a></div>"
        else:
            news_html = "<p style='color: gray;'>No recent news provided by Yahoo or Google News for this ticker.</p>"
    except:
        news_html = "<p style='color: gray;'>Could not fetch latest news.</p>"

    # HTML Layout Builder
    verdict_color = "#10B981" if score >= 7 else "#EF4444" if score <= 4 else "#F59E0B"
    bg_card = "var(--secondary-background-color, rgba(128,128,128,0.05))"
    text_main = "var(--text-color, inherit)"
    
    html = f"""<div style="font-family: 'Inter', sans-serif; max-width: 1200px; margin: auto; color: {text_main};">
    
    <!-- Header Hero -->
    <div style="background: linear-gradient(135deg, #1E293B, #0F172A); padding: 30px; border-radius: 12px; border-left: 6px solid #3B82F6; color: white; margin-bottom: 25px; box-shadow: 0 4px 10px rgba(0,0,0,0.15);">
        <h1 style="margin: 0; font-size: 32px; color: white; letter-spacing: -0.5px;">{name} <span style="color: #94A3B8; font-size: 22px;">({ticker_symbol})</span></h1>
        <div style="margin-top: 15px; display: flex; gap: 10px; flex-wrap: wrap;">
            <span style="background: rgba(255,255,255,0.1); padding: 5px 12px; border-radius: 6px; font-size: 14px; border: 1px solid rgba(255,255,255,0.2);">🏢 Sector: {sector}</span>
            <span style="background: rgba(255,255,255,0.1); padding: 5px 12px; border-radius: 6px; font-size: 14px; border: 1px solid rgba(255,255,255,0.2);">🏭 Industry: {industry}</span>
            <span style="background: rgba(255,255,255,0.1); padding: 5px 12px; border-radius: 6px; font-size: 14px; border: 1px solid rgba(255,255,255,0.2);">📈 Exchange: {exchange}</span>
        </div>
    </div>

    <!-- Metric Cards Row 1: Score & Verdict -->
    <div style="display: flex; gap: 20px; margin-bottom: 25px; flex-wrap: wrap;">
        <!-- Score Card -->
        <div style="flex: 1; min-width: 250px; background: {bg_card}; padding: 25px; border-radius: 12px; text-align: center; border-bottom: 4px solid {verdict_color}; box-shadow: 0 2px 5px rgba(0,0,0,0.05);">
            <h3 style="margin: 0 0 10px 0; font-size: 14px; text-transform: uppercase; letter-spacing: 1px; color: gray;">Overall Fundamental Score</h3>
            <h2 style="margin: 0; font-size: 48px; font-weight: 800; color: {verdict_color};">{score}<span style="font-size: 24px; color: gray;">/10</span></h2>
        </div>
        
        <!-- Verdict Card -->
        <div style="flex: 2; min-width: 300px; background: {bg_card}; padding: 25px; border-radius: 12px; border-bottom: 4px solid {verdict_color}; box-shadow: 0 2px 5px rgba(0,0,0,0.05); display: flex; flex-direction: column; justify-content: center;">
            <h3 style="margin: 0 0 5px 0; font-size: 14px; text-transform: uppercase; letter-spacing: 1px; color: gray;">Final Analyst Verdict</h3>
            <h2 style="margin: 0; font-size: 32px; font-weight: 800; color: {verdict_color};">{verdict}</h2>
            <div style="margin-top: 5px; font-size: 24px; color: #FFD700; letter-spacing: 2px;">{stars}</div>
        </div>
    </div>

    <!-- Section Grid -->
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 20px; margin-bottom: 25px;">
        
        <!-- Box 1 -->
        <div style="background: {bg_card}; padding: 20px; border-radius: 12px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); border: 1px solid rgba(128,128,128,0.1);">
            <h3 style="margin-top: 0; border-bottom: 1px solid rgba(128,128,128,0.2); padding-bottom: 10px; font-size: 16px;">⚖️ 1. Valuation & Pricing</h3>
            <ul style="line-height: 2; margin: 0; padding-left: 20px;">
                <li><b>P/E Ratio:</b> {format_num(pe)}</li>
                <li><b>P/B Ratio:</b> {format_num(pb)}</li>
                <li><b>EV/EBITDA:</b> {format_num(ev_ebitda)}</li>
                <li><b>PEG Ratio:</b> {format_num(peg)}</li>
            </ul>
        </div>

        <!-- Box 2 -->
        <div style="background: {bg_card}; padding: 20px; border-radius: 12px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); border: 1px solid rgba(128,128,128,0.1);">
            <h3 style="margin-top: 0; border-bottom: 1px solid rgba(128,128,128,0.2); padding-bottom: 10px; font-size: 16px;">💰 2. Profitability & Efficiency</h3>
            <ul style="line-height: 2; margin: 0; padding-left: 20px;">
                <li><b>Return on Equity:</b> {format_pct(roe)}</li>
                <li><b>Operating Margin:</b> {format_pct(opm)}</li>
                <li><b>Net Profit Margin:</b> {format_pct(npm)}</li>
            </ul>
        </div>

        <!-- Box 3 -->
        <div style="background: {bg_card}; padding: 20px; border-radius: 12px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); border: 1px solid rgba(128,128,128,0.1);">
            <h3 style="margin-top: 0; border-bottom: 1px solid rgba(128,128,128,0.2); padding-bottom: 10px; font-size: 16px;">🏥 3. Financial Health</h3>
            <ul style="line-height: 2; margin: 0; padding-left: 20px;">
                <li><b>Debt-to-Equity:</b> {format_num(de_ratio)}</li>
                <li><b>Current Ratio:</b> {format_num(current_ratio)}</li>
                <li><b>Quick Ratio:</b> {format_num(quick_ratio)}</li>
            </ul>
        </div>

        <!-- Box 4 -->
        <div style="background: {bg_card}; padding: 20px; border-radius: 12px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); border: 1px solid rgba(128,128,128,0.1);">
            <h3 style="margin-top: 0; border-bottom: 1px solid rgba(128,128,128,0.2); padding-bottom: 10px; font-size: 16px;">📈 4. Growth & Cash Flow</h3>
            <ul style="line-height: 2; margin: 0; padding-left: 20px;">
                <li><b>Revenue Growth (YoY):</b> {format_pct(rev_growth)}</li>
                <li><b>Earnings Growth (YoY):</b> {format_pct(earn_growth)}</li>
                <li><b>Free Cash Flow:</b> {fcf_str}</li>
            </ul>
        </div>
        
        <!-- Box 5 -->
        <div style="background: {bg_card}; padding: 20px; border-radius: 12px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); border: 1px solid rgba(128,128,128,0.1);">
            <h3 style="margin-top: 0; border-bottom: 1px solid rgba(128,128,128,0.2); padding-bottom: 10px; font-size: 16px;">👔 5. Management & Holdings</h3>
            <ul style="line-height: 2; margin: 0; padding-left: 20px;">
                <li><b>Promoter / Insider:</b> {format_pct(insiders)}</li>
                <li><b>Institutions (FII/DII):</b> {format_pct(institutions)}</li>
            </ul>
        </div>
        
        <!-- Box 6 -->
        <div style="background: {bg_card}; padding: 20px; border-radius: 12px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); border: 1px solid rgba(128,128,128,0.1);">
            <h3 style="margin-top: 0; border-bottom: 1px solid rgba(128,128,128,0.2); padding-bottom: 10px; font-size: 16px;">📅 6. Upcoming Events</h3>
            <p style="line-height: 1.5; margin: 0;">{events_text}</p>
        </div>
        
    </div>
    
    <!-- Risk & Catalyst Row -->
    <div style="display: flex; gap: 20px; flex-wrap: wrap; margin-bottom: 25px;">
        <div style="flex: 1; min-width: 300px; background: rgba(16, 185, 129, 0.05); border: 1px solid rgba(16, 185, 129, 0.2); border-left: 5px solid #10B981; padding: 20px; border-radius: 8px;">
            <h3 style="margin: 0 0 10px 0; color: #10B981; font-size: 16px;">🟢 Key Catalyst for Upside</h3>
            <p style="margin: 0; font-size: 14px;">{catalysts[0]}</p>
        </div>
        <div style="flex: 1; min-width: 300px; background: rgba(239, 68, 68, 0.05); border: 1px solid rgba(239, 68, 68, 0.2); border-left: 5px solid #EF4444; padding: 20px; border-radius: 8px;">
            <h3 style="margin: 0 0 10px 0; color: #EF4444; font-size: 16px;">🔴 Major Risk to Thesis</h3>
            <p style="margin: 0; font-size: 14px;">{risks[0]}</p>
        </div>
    </div>

    <!-- News List -->
    <div style="background: {bg_card}; padding: 25px; border-radius: 12px; margin-bottom: 25px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); border: 1px solid rgba(128,128,128,0.1);">
        <h3 style="margin-top: 0; margin-bottom: 15px; border-bottom: 1px solid rgba(128,128,128,0.2); padding-bottom: 10px;">🗞️ Latest Headlines</h3>
        {news_html}
    </div>
    
</div>"""
    
    # Strip all leading/trailing whitespace from every line to absolutely prevent Markdown code-block rendering
    html = "\n".join([line.strip() for line in html.split('\n')])
    return html

if __name__ == "__main__":
    print(generate_fundamental_report("RELIANCE.NS"))
