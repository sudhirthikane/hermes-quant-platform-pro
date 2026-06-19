import streamlit as st
import pandas as pd
import json
import os
import plotly.graph_objects as go
from engine import fetch_data, calculate_ict_indicators, LOG_FILE

st.set_page_config(page_title="Hermes ICT Pro Dashboard", layout="wide", page_icon="📈")

st.title("📈 Hermes ICT Pro Trading Dashboard")
st.markdown("Institutional Grade Algorithmic Tracking (FVGs, Order Blocks, Liquidity Pools, VWMA).")

# Sidebar Configuration
st.sidebar.header("Configuration")

POPULAR_ASSETS = {
    "AAPL": "Apple Inc.",
    "MSFT": "Microsoft",
    "NVDA": "NVIDIA",
    "TSLA": "Tesla",
    "AMZN": "Amazon",
    "RELIANCE.NS": "Reliance Industries (NSE)",
    "TCS.NS": "Tata Consultancy (NSE)",
    "HDFCBANK.NS": "HDFC Bank (NSE)",
    "INFY.NS": "Infosys (NSE)",
    "SBIN.NS": "State Bank of India (NSE)",
    "EURUSD=X": "EUR/USD Forex",
    "GBPUSD=X": "GBP/USD Forex",
    "JPY=X": "USD/JPY Forex",
    "BTC-USD": "Bitcoin",
    "ETH-USD": "Ethereum",
    "GC=F": "Gold Futures",
    "CL=F": "Crude Oil Futures"
}

st.sidebar.markdown("**🔍 Asset Selection**")
asset_options = [""] + [f"{k} ({v})" for k, v in POPULAR_ASSETS.items()]
selected_dropdown = st.sidebar.selectbox("Search Popular Assets:", asset_options, index=1)

st.sidebar.markdown("**Or**")
custom_ticker = st.sidebar.text_input("Enter Custom Ticker (e.g., GOOGL, TATAMOTORS.NS):", value="")

if custom_ticker.strip():
    selected_ticker = custom_ticker.upper().strip()
else:
    selected_ticker = selected_dropdown.split(" ")[0] if selected_dropdown else "AAPL"

st.sidebar.markdown("---")
chart_theme = st.sidebar.radio("Chart Theme", ["Dark", "Light"], index=0)
days_to_show = st.sidebar.slider("Chart Zoom (Days)", min_value=14, max_value=365, value=90, step=7)

st.sidebar.markdown("---")
refresh = st.sidebar.button("↻ Refresh Live Data")

@st.cache_data(ttl=60)
def get_stock_data(ticker, period="1y"):
    df = fetch_data(ticker, period=period, interval="1d")
    df, ict_data = calculate_ict_indicators(ticker, df, generate_logs=True)
    return df, ict_data

def load_logs():
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f:
            try:
                logs = json.load(f)
                return pd.DataFrame(logs)
            except:
                pass
    return pd.DataFrame()

logs_df = load_logs()

# Create Tabs
tab1, tab2 = st.tabs(["📊 Main Dashboard", "📡 Indian Market Scanner"])

with tab1:
    with st.spinner(f"Loading institutional data for {selected_ticker}..."):
        df, ict_data = get_stock_data(selected_ticker)

    if not df.empty:
        latest = df.iloc[-1]
        prev = df.iloc[-2]
        
        # ICT HUD
        col1, col2, col3, col4 = st.columns(4)
        current_price = latest['Close']
        price_change = current_price - prev['Close']
        col1.metric("Current Price", f"${current_price:.2f}", f"{price_change:.2f}")
        
        bias_color = "🟢 BULLISH" if ict_data.get('dynamic_bull_bias') else "🔴 BEARISH" if ict_data.get('dynamic_bear_bias') else "⚪ NEUTRAL"
        col2.metric("Structure Shift (Bias)", bias_color)
        col3.metric("RSI Momentum", f"{latest['RSI_14']:.2f}")
        
        latest_signal = "None"
        if not logs_df.empty and 'ticker' in logs_df.columns:
            ticker_logs = logs_df[logs_df['ticker'] == selected_ticker]
            if not ticker_logs.empty:
                latest_signal_row = ticker_logs.iloc[-1]
                latest_signal = f"{latest_signal_row['action']} @ {latest_signal_row['price']}"
        with col4:
            st.caption("Latest ICT Signal")
            st.markdown(f"#### {latest_signal}")
        
        st.markdown("---")
        st.subheader(f"ICT Institutional Analysis - {selected_ticker}")
        
        fig = go.Figure()
        fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name='OHLC', increasing_line_color='#26A69A', decreasing_line_color='#EF5350'))
        fig.add_trace(go.Scatter(x=df.index, y=df['VWMA_50'], line=dict(color='#FF00FF', width=2), name='VWMA Mean'))
        fig.add_trace(go.Scatter(x=df.index, y=df['CH_High'], line=dict(color='#FFDD00', width=1), name='Channel Cap', opacity=0.7))
        fig.add_trace(go.Scatter(x=df.index, y=df['CH_Low'], line=dict(color='#FFDD00', width=1), name='Channel Floor', opacity=0.7))
        
        max_date = df.index[-1]
        
        for fvg in ict_data.get('fvg', []):
            fcolor = "rgba(0, 255, 170, 0.2)" if fvg['type'] == 'Bull FVG' else "rgba(255, 51, 102, 0.2)"
            end_d = fvg.get('end', max_date)
            fig.add_shape(type="rect", x0=fvg['start'], y0=fvg['bot'], x1=end_d, y1=fvg['top'], line=dict(width=1, color=fcolor.replace("0.2", "0.5")), fillcolor=fcolor, layer="below")
            
        for ob in ict_data.get('ob', []):
            fcolor = "rgba(51, 153, 255, 0.25)" if ob['type'] == 'Bull OB' else "rgba(255, 136, 51, 0.25)"
            fig.add_shape(type="rect", x0=ob['start'], y0=ob['bot'], x1=max_date, y1=ob['top'], line=dict(width=1, color=fcolor.replace("0.25", "0.7")), fillcolor=fcolor, layer="below")
            
        for liq in ict_data.get('liq', []):
            lcolor = "#FF5555" if liq['type'] == 'BSL' else "#55FF99"
            fig.add_shape(type="line", x0=liq['index'], y0=liq['price'], x1=max_date, y1=liq['price'], line=dict(color=lcolor, width=2, dash="dash"), layer="below")
            fig.add_annotation(x=max_date, y=liq['price'], text=f" {liq['type']} ", showarrow=False, xanchor="left", font=dict(color=lcolor, size=11))
            
        safe_days = min(days_to_show, len(df)-1)
        zoom_start = df.index[-safe_days] if safe_days > 0 else df.index[0]
        
        theme_template = "plotly_dark" if chart_theme == "Dark" else "plotly_white"
        bg_color = "#0e1117" if chart_theme == "Dark" else "#ffffff"
        grid_color = "#262730" if chart_theme == "Dark" else "#e6e6e6"

        fig.update_layout(xaxis_rangeslider_visible=False, template=theme_template, height=800, plot_bgcolor=bg_color, paper_bgcolor=bg_color, margin=dict(l=0, r=50, t=30, b=0), xaxis=dict(showgrid=True, gridcolor=grid_color, range=[zoom_start, max_date]), yaxis=dict(showgrid=True, gridcolor=grid_color), legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        st.subheader("Institutional Triggers Log")
        if not logs_df.empty:
            display_df = logs_df.iloc[::-1].reset_index(drop=True)
            st.dataframe(display_df, use_container_width=True)
        else:
            st.info("No active decisions logged yet.")

        st.markdown("---")
        st.subheader("📖 Understanding the Institutional Triggers")
        st.markdown("The triggers log captures key algorithmic actions. Here is what they mean for your trading strategy:")

        col_exp1, col_exp2, col_exp3, col_exp4 = st.columns(4)
        with col_exp1:
            st.info("**MSS (Market Structure Shift)**\n\nIndicates a reversal in trend bias. When price violently breaks a major recent swing high or low, it signals institutions are reversing the market direction.")
        with col_exp2:
            st.success("**FVG (Fair Value Gap)**\n\nA rapid 3-bar pricing inefficiency. Institutions moved so fast they left a gap. Price often gravitates back to this zone to 'fill' or 'mitigate' it before continuing.")
        with col_exp3:
            st.warning("**Order Blocks (OB)**\n\nThe exact candlestick footprint where banks accumulated massive positions (detected via high ATR displacement). It acts as a powerful future support/resistance magnet.")
        with col_exp4:
            st.error("**Liquidity Pools (BSL/SSL)**\n\nAreas where retail stop-losses rest (above old highs and below old lows). Algorithms frequently push price into these lines to grab liquidity before reversing.")

        st.markdown("### The Standard Institutional Trade Flow")
        funnel_fig = go.Figure(go.Funnelarea(
            text=["1. Liquidity Sweep (BSL/SSL)", "2. Structure Shift (MSS)", "3. Footprint Left (OB/FVG)", "4. Retracement & Mitigation", "5. Institutional Expansion (Take Profit)"],
            values=[100, 80, 60, 40, 20],
            marker={"colors": ["#FF5555", "#FFDD00", "#3399FF", "#00FFAA", "#BB77FF"]},
            textfont={"color": "black", "size": 14}
        ))
        funnel_fig.update_layout(template=theme_template if 'theme_template' in locals() else "plotly_dark", paper_bgcolor=bg_color if 'bg_color' in locals() else "#0e1117", height=350, margin=dict(t=30, b=0, l=0, r=0))
        st.plotly_chart(funnel_fig, use_container_width=True)

        st.markdown("---")
        st.subheader(f"🔮 Automated Forecast & Key Levels ({selected_ticker})")
        
        # S/R Logic
        key_levels = []
        for liq in ict_data.get('liq', []): key_levels.append({'name': liq['type'] + " (Liquidity)", 'price': liq['price']})
        for ob in ict_data.get('ob', []):
            if ob['type'] == 'Bull OB': key_levels.append({'name': 'Bull OB Support', 'price': ob['top']})
            else: key_levels.append({'name': 'Bear OB Resistance', 'price': ob['bot']})
        for fvg in ict_data.get('fvg', []):
            if fvg.get('active', True):
                if fvg['type'] == 'Bull FVG': key_levels.append({'name': 'Bull FVG Support', 'price': fvg['top']})
                else: key_levels.append({'name': 'Bear FVG Resistance', 'price': fvg['bot']})

        unique_levels = []
        seen_prices = set()
        for lvl in key_levels:
            p_rounded = round(lvl['price'], 2)
            if p_rounded not in seen_prices:
                seen_prices.add(p_rounded)
                unique_levels.append(lvl)

        supports = sorted([lvl for lvl in unique_levels if lvl['price'] < current_price], key=lambda x: x['price'], reverse=True)
        resistances = sorted([lvl for lvl in unique_levels if lvl['price'] > current_price], key=lambda x: x['price'])

        is_bull = ict_data.get('dynamic_bull_bias', False)
        is_bear = ict_data.get('dynamic_bear_bias', False)
        forecast_text = "Neutral - Waiting for clear Market Structure Shift."
        forecast_color = "gray"

        if is_bull:
            if latest['RSI_14'] > 70:
                forecast_text = "⚠️ **Bullish Overextended:** Momentum is high, but RSI is overbought. A temporary retracement down to the nearest Support is highly probable before further upside."
                forecast_color = "#FFDD00"
            else:
                forecast_text = "🚀 **Bullish Continuation:** Market structure is intact with healthy momentum. Price is projected to hunt the nearest Resistance levels (Buy-Side Liquidity)."
                forecast_color = "#00FFAA"
        elif is_bear:
            if latest['RSI_14'] < 30:
                forecast_text = "⚠️ **Bearish Exhausted:** Momentum is heavy, but RSI is oversold. Expect a short-term relief rally up to the nearest Resistance before continuing the downtrend."
                forecast_color = "#FFDD00"
            else:
                forecast_text = "📉 **Bearish Continuation:** Market structure is heavily bearish. Price is projected to hunt lower Support levels (Sell-Side Liquidity)."
                forecast_color = "#FF3366"

        text_color = "#ffffff" if chart_theme == "Dark" else "#000000"
        st.markdown(f"<div style='padding:15px; border-radius:5px; border-left: 5px solid {forecast_color}; background-color: {bg_color}; color: {text_color}; font-size: 16px; margin-bottom: 20px;'>{forecast_text}</div>", unsafe_allow_html=True)

        col_sup, col_res = st.columns(2)
        with col_sup:
            st.markdown("🛡️ **Immediate Support Levels (Demand)**")
            if supports:
                for i, s in enumerate(supports[:3]): st.markdown(f"- **${s['price']:.2f}** ➔ {s['name']}")
            else: st.markdown("- *No immediate structural support found nearby.*")

        with col_res:
            st.markdown("🎯 **Immediate Resistance Levels (Supply)**")
            if resistances:
                for i, r in enumerate(resistances[:3]): st.markdown(f"- **${r['price']:.2f}** ➔ {r['name']}")
            else: st.markdown("- *No immediate structural resistance found nearby.*")

    else:
        st.warning("No data available for the selected ticker.")

with tab2:
    st.subheader("📡 Interactive Paginated Market Scanner (2000+ Stocks)")
    st.markdown("Select a page below to instantly scan a block of 100 stocks. The algorithmic engine will use 20 parallel threads to return your institutional bias results in roughly 10-15 seconds.")
    
    @st.cache_data
    def get_all_nse_tickers():
        if not os.path.exists("nse_list.csv"): return []
        try:
            df_nse = pd.read_csv("nse_list.csv")
            if 'SYMBOL' in df_nse.columns:
                return [str(sym).strip() + ".NS" for sym in df_nse['SYMBOL'].tolist() if pd.notna(sym)]
        except Exception: return []
        return []

    all_tickers = get_all_nse_tickers()
    total_tickers = len(all_tickers)
    
    if total_tickers == 0:
        st.warning("Could not load nse_list.csv. Please ensure the master file exists.")
    else:
        PAGE_SIZE = 100
        total_pages = (total_tickers // PAGE_SIZE) + (1 if total_tickers % PAGE_SIZE > 0 else 0)
        
        col_page, col_btn = st.columns([1, 2])
        with col_page:
            selected_page = st.number_input(f"Select Page (1 to {total_pages})", min_value=1, max_value=total_pages, value=1)
            
        start_idx = (selected_page - 1) * PAGE_SIZE
        end_idx = min(start_idx + PAGE_SIZE, total_tickers)
        current_batch = all_tickers[start_idx:end_idx]
        
        st.markdown(f"**Ready to scan stocks {start_idx + 1} to {end_idx} (out of {total_tickers})**")
        
        if st.button(f"🚀 Scan Page {selected_page} Now", use_container_width=True):
            bullish_list = []
            bearish_list = []
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            from concurrent.futures import ThreadPoolExecutor, as_completed
            
            def scan_single(ticker):
                try:
                    df_s = fetch_data(ticker, period="6mo", interval="1d")
                    if df_s.empty or len(df_s) < 50: return None
                    df_s, ict_s = calculate_ict_indicators(ticker, df_s, generate_logs=False)
                    cur_price = df_s.iloc[-1]['Close']
                    cur_rsi = df_s.iloc[-1]['RSI_14']
                    bull = ict_s.get('dynamic_bull_bias', False)
                    bear = ict_s.get('dynamic_bear_bias', False)
                    if bull or bear:
                        return {"Ticker": ticker.replace(".NS", ""), "Price (₹)": round(cur_price, 2), "RSI": round(cur_rsi, 2), "Bias": "Bullish" if bull else "Bearish"}
                except Exception: return None
                return None

            completed = 0
            with ThreadPoolExecutor(max_workers=20) as executor:
                future_to_ticker = {executor.submit(scan_single, t): t for t in current_batch}
                for future in as_completed(future_to_ticker):
                    completed += 1
                    status_text.text(f"Scanning... ({completed}/{len(current_batch)})")
                    progress_bar.progress(completed / len(current_batch))
                    
                    res = future.result()
                    if res:
                        if res['Bias'] == 'Bullish': bullish_list.append(res)
                        else: bearish_list.append(res)
                            
            status_text.text(f"Page {selected_page} Scan Complete!")
            
            col_bull, col_bear = st.columns(2)
            with col_bull:
                st.success(f"🟢 **Bullish Bias Detected ({len(bullish_list)})**")
                if bullish_list:
                    bullish_list = sorted(bullish_list, key=lambda x: x['RSI'], reverse=True)
                    st.dataframe(pd.DataFrame(bullish_list).drop(columns=['Bias']), use_container_width=True, hide_index=True)
                else: st.info("No bullish structures found on this page.")
                    
            with col_bear:
                st.error(f"🔴 **Bearish Bias Detected ({len(bearish_list)})**")
                if bearish_list:
                    bearish_list = sorted(bearish_list, key=lambda x: x['RSI'])
                    st.dataframe(pd.DataFrame(bearish_list).drop(columns=['Bias']), use_container_width=True, hide_index=True)
                else: st.info("No bearish structures found on this page.")
