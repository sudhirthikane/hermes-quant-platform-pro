import streamlit as st
import pandas as pd
import json
import os
import plotly.graph_objects as go
import streamlit.components.v1 as components
from engine import fetch_data, calculate_ict_indicators, LOG_FILE

def add_print_button():
    st.markdown("""
        <style>
        @media print {
            [data-testid="stSidebar"], [data-testid="stHeader"], [data-testid="stToolbar"] { display: none !important; }
            iframe { display: none !important; }
            .stApp { background-color: white !important; }
            * { color: black !important; }
            .main .block-container::before {
                content: "Hermes Quant Platform - Professional Equity Report";
                display: block; font-size: 20px; font-weight: bold; text-align: center;
                margin-bottom: 20px; padding-bottom: 10px; border-bottom: 2px solid #333; color: #333 !important;
            }
        }
        </style>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([5, 1])
    with col2:
        components.html(
            """
            <script>function printDashboard() { window.parent.print(); }</script>
            <div style="display:flex; justify-content:flex-end;">
                <button onclick="printDashboard()" style="background-color: #26A69A; color: white; border: none; padding: 8px 16px; border-radius: 6px; font-family: sans-serif; font-size: 14px; font-weight: bold; cursor: pointer; box-shadow: 0 4px 6px rgba(0,0,0,0.1); transition: all 0.3s ease;">
                    🖨️ Print / Save as PDF
                </button>
            </div>
            <style>
                body { margin: 0; }
                button:hover { transform: scale(1.05) !important; box-shadow: 0 6px 12px rgba(38, 166, 154, 0.4) !important; }
            </style>
            """,
            height=45
        )

st.set_page_config(page_title="Hermes ICT Pro Dashboard", layout="wide", page_icon="📈")

st.markdown("""
<style>
.block-container {
    padding-top: 5rem !important;
}
.fixed-header {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    height: 4rem;
    z-index: 99999;
    background-color: #111827 !important; /* Deep dark blue/grey */
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    text-align: center;
    border-bottom: 4px solid #26A69A;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.5);
}
.fixed-header h1 {
    color: #FFFFFF !important;
    margin: 0;
    padding: 0;
    font-size: 1.4rem !important;
    line-height: 1.2;
}
.fixed-header p {
    color: #94A3B8 !important;
    margin: 0;
    padding: 0;
    font-size: 0.75rem !important;
}
[data-testid="stHeader"] {
    background: transparent !important;
    z-index: 100000 !important; /* Keep Streamlit UI elements clickable */
}
/* Ensure the parent container allows sticky elements to work */
.main .block-container {
    overflow: visible;
}
[data-testid="stMetric"] {
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 8px;
    padding: 10px;
    background: rgba(255, 255, 255, 0.02);
}
[data-testid="stDataFrame"] {
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 8px;
    padding: 2px;
}
/* Border for Custom Ticker text input in sidebar */
[data-testid="stSidebar"] [data-testid="stTextInput"] div[data-baseweb="input"] {
    border: 2px solid #3B82F6 !important;
    border-radius: 8px !important;
    box-shadow: 0 0 8px rgba(59, 130, 246, 0.4) !important;
}
[data-testid="stSidebar"] [data-testid="stTextInput"] div[data-baseweb="input"]:focus-within {
    border-color: #60A5FA !important;
    box-shadow: 0 0 12px rgba(96, 165, 250, 0.6) !important;
}

/* Sidebar Toggle Icons (keyboard_double_arrow_left/right) */
[data-testid="collapsedControl"] svg,
[data-testid="stSidebarCollapseButton"] svg {
    color: #10B981 !important;
    fill: #10B981 !important;
    stroke: #10B981 !important;
}

/* 📱 Smartphone / Mobile Optimization */
@media (max-width: 768px) {
    .fixed-header {
        position: fixed !important;
        padding-left: 1rem !important;
    }
    .fixed-header h1 {
        font-size: 1.1rem !important;
    }
    .fixed-header p {
        font-size: 0.65rem !important;
    }
    [data-testid="stMetricValue"] {
        font-size: 1.2rem !important;
    }
    /* Scale down all custom HTML spans that use 24px+ */
    span[style*="font-size: 26px"], span[style*="font-size: 24px"], h2[style*="font-size: 32px"], h2[style*="font-size: 48px"] {
        font-size: 20px !important;
    }
    /* Reduce gap in flex containers */
    div[style*="gap: 30px"], div[style*="gap: 20px"] {
        gap: 15px !important;
    }
    /* Adjust padding in custom HTML cards */
    div[style*="padding: 20px"], div[style*="padding: 25px"] {
        padding: 12px !important;
    }
}
</style>
<div class="fixed-header">
    <h1>📈 Hermes ICT Pro Trading Dashboard</h1>
    <p>Institutional Grade Algorithmic Tracking (FVGs, Order Blocks, Liquidity Pools, VWMA).</p>
</div>
""", unsafe_allow_html=True)

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

@st.cache_data
def load_all_tickers():
    options = []
    # Add popular first
    for k, v in POPULAR_ASSETS.items():
        options.append(f"{k} ({v})")
    # Add NSE
    try:
        import pandas as pd
        df = pd.read_csv("nse_list.csv")
        for _, row in df.iterrows():
            sym = str(row.iloc[0]).strip()
            name = str(row.iloc[1]).strip()
            options.append(f"{sym}.NS ({name})")
    except Exception:
        pass
    return options

all_ticker_options = load_all_tickers()

selected_dropdown = st.sidebar.selectbox("Search Asset (Type to autocomplete):", all_ticker_options, index=1)

st.sidebar.markdown("**Or**")
from streamlit_searchbox import st_searchbox
def search_asset_sidebar(searchterm: str):
    return [o for o in all_ticker_options if searchterm.lower() in o.lower()] if searchterm else []

with st.sidebar:
    custom_ticker = st_searchbox(
        search_asset_sidebar,
        key="sidebar_searchbox",
        placeholder="Enter Custom Ticker..."
    )

if custom_ticker:
    selected_ticker = custom_ticker.split(" ")[0].upper()
else:
    selected_ticker = selected_dropdown.split(" ")[0] if selected_dropdown else "AAPL"

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

# Set up layout tabs
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["📊 Main Dashboard", "📡 Indian Market Scanner", "🎯 Most Probable B/S", "📋 Stock Analysis", "🧭 Sectorial View", "🛢️ Commodities"])

# --- TAB 1: MAIN DASHBOARD ---
with tab1:
    with st.spinner(f"Loading institutional data for {selected_ticker}..."):
        df, ict_data = get_stock_data(selected_ticker)

    add_print_button()

    if not df.empty:
        latest = df.iloc[-1]
        prev = df.iloc[-2]
        
        # ICT HUD
        st.markdown(f"<h2 style='margin-bottom: 0px; margin-top: 0px; color: #3B82F6;'>{selected_ticker}</h2>", unsafe_allow_html=True)
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
        
        # Chart Controls aligned in a row
        ctrl_col1, ctrl_col2, ctrl_col3 = st.columns([1, 2, 1])
        with ctrl_col1:
            chart_theme = st.radio("Chart Theme", ["Dark", "Light"], index=1, horizontal=True)
        with ctrl_col2:
            days_to_show = st.slider("Chart Zoom (Days)", min_value=14, max_value=365, value=90, step=7)
        with ctrl_col3:
            st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
            refresh = st.button("↻ Refresh Live Data", use_container_width=True)
            if refresh:
                st.cache_data.clear()
        
        fig = go.Figure()
        fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name='OHLC', increasing_line_color='#26A69A', decreasing_line_color='#EF5350', showlegend=False))
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
        bg_color = "rgba(0,0,0,0)" # Transparent to show CSS gradient
        grid_color = "rgba(255,255,255,0.05)" if chart_theme == "Dark" else "rgba(0,0,0,0.05)"
        
        # Inject dynamic CSS for chart gradient and border
        st.markdown(f"""
        <style>
        [data-testid="stPlotlyChart"] {{
            background: {'linear-gradient(180deg, #1e293b 0%, #000000 100%)' if chart_theme == 'Dark' else 'linear-gradient(180deg, #ffffff 0%, #e2e8f0 100%)'};
            border: 2px solid {'#334155' if chart_theme == 'Dark' else '#cbd5e1'};
            border-radius: 12px;
            padding: 15px;
            box-shadow: 0 10px 20px rgba(0,0,0,0.2);
        }}
        </style>
        """, unsafe_allow_html=True)

        fig.update_layout(
            xaxis_rangeslider_visible=False,
            template=theme_template, 
            height=800, 
            plot_bgcolor=bg_color, 
            paper_bgcolor=bg_color, 
            margin=dict(l=0, r=60, t=20, b=0), 
            xaxis=dict(
                showgrid=True, gridcolor=grid_color, griddash='dot', 
                rangebreaks=[dict(bounds=["sat", "mon"])],
                range=[zoom_start, max_date],
                showspikes=True, spikemode='across', spikethickness=1, spikedash='dot', spikecolor='#999999'
            ), 
            yaxis=dict(
                side='right',
                showgrid=True, gridcolor=grid_color, griddash='dot', 
                tickformat='.2f',
                showspikes=True, spikemode='across', spikethickness=1, spikedash='dot', spikecolor='#999999'
            ), 
            legend=dict(
                orientation="v", yanchor="top", y=0.99, xanchor="left", x=0.01, 
                bgcolor="rgba(0,0,0,0)"
            ),
            hovermode='x unified'
        )
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

        text_color = "#000000" # Forced to black as requested
        st.markdown(f"<div style='padding:15px; border-radius:5px; border-left: 5px solid {forecast_color}; background-color: rgba(255,255,255,0.9); color: {text_color}; font-size: 16px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);'>{forecast_text}</div>", unsafe_allow_html=True)

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

with tab3:
    st.subheader("🎯 Top 10 Most Probable Bullish & Bearish Setups")
    st.markdown("This engine cross-references the **ICT Technical Scanner** with the **Hermes AI Fundamental Engine** to find the absolute highest probability trades.")
    
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        st.markdown("### 🤖 Hermes Telegram Integration")
        bot_token = st.text_input("Telegram Bot Token:", type="password", placeholder="Enter your BotFather Token")
        chat_id = st.text_input("Channel/Chat ID:", placeholder="e.g. @sudhir_ict_signals or -100123456789")
    
    st.markdown("---")
    
    col_btn1, col_btn2, col_btn3 = st.columns([2, 2, 1])
    with col_btn1:
        analyze_clicked = st.button("🚀 Analyze Top 10 B/S Setups", use_container_width=True)
    with col_btn2:
        broadcast_clicked = st.button("📤 Broadcast to Telegram", use_container_width=True)
    
    if analyze_clicked:
        if not os.path.exists("scanner_results.json"):
            st.warning("No scanner results found! Please run the 'Indian Market Scanner' on at least one page first.")
        else:
            with st.spinner("Crunching fundamental data for the Top 20 ICT Setups... This takes about 10 seconds..."):
                try:
                    with open("scanner_results.json", "r") as f:
                        scan_data = json.load(f)
                    
                    bullish_raw = scan_data.get("bullish", [])
                    bearish_raw = scan_data.get("bearish", [])
                    
                    from fundamental import get_fundamental_score
                    
                    def enrich_list(raw_list, req_count=10):
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
                            
                            # Determine emoji based on verdict
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
                        
                    bullish_final = enrich_list(bullish_raw, 10)
                    bearish_final = enrich_list(bearish_raw, 10)
                        
                    st.session_state['bullish_final'] = bullish_final
                    st.session_state['bearish_final'] = bearish_final
                    
                except Exception as e:
                    st.error(f"An error occurred during analysis: {e}")

    # Display results if they exist in session state
    if 'bullish_final' in st.session_state and 'bearish_final' in st.session_state:
        bullish_final = st.session_state['bullish_final']
        bearish_final = st.session_state['bearish_final']
        
        col_b1, col_b2 = st.columns(2)
        with col_b1:
            st.success(f"📈 **Top {len(bullish_final)} Bullish Candidates**")
            if bullish_final:
                st.dataframe(pd.DataFrame(bullish_final), use_container_width=True, hide_index=True)
            else:
                st.info("No bullish candidates found in scanner results.")
                
        with col_b2:
            st.error(f"📉 **Top {len(bearish_final)} Bearish Candidates**")
            if bearish_final:
                st.dataframe(pd.DataFrame(bearish_final), use_container_width=True, hide_index=True)
            else:
                st.info("No bearish candidates found in scanner results.")
                
        # --- PDF Download Generation ---
        def generate_pdf_bytes(bullish, bearish):
            import tempfile, os
            try:
                from fpdf import FPDF
            except ImportError:
                return None
            from datetime import datetime
            current_date = datetime.now().strftime("%B %d, %Y | %H:%M")

            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", 'B', 16)
            pdf.cell(190, 10, txt="Hermes ICT Pro - Top 10 B/S Setups", ln=True, align='C')
            
            pdf.set_font("Arial", 'I', 10)
            pdf.set_text_color(100, 100, 100) # grey color
            pdf.cell(190, 6, txt=f"Generated on: {current_date}", ln=True, align='C')
            pdf.set_text_color(0, 0, 0) # reset
            pdf.ln(5)
            def draw_table(title, data, is_bullish):
                pdf.set_font("Arial", 'B', 14)
                if is_bullish:
                    pdf.set_text_color(0, 128, 0) # Dark Green
                else:
                    pdf.set_text_color(200, 0, 0) # Dark Red
                    
                pdf.cell(190, 10, txt=title, ln=True, align='L')
                pdf.set_text_color(0, 0, 0) # Reset to black
                pdf.ln(2)
                
                # Table Headers
                pdf.set_font("Arial", 'B', 10)
                pdf.set_fill_color(240, 240, 240)
                headers = ['Ticker', 'Price', 'RSI', 'Vol (K)', 'Score', 'Verdict']
                widths = [35, 25, 20, 25, 20, 65]
                
                for i in range(len(headers)):
                    pdf.cell(widths[i], 8, txt=headers[i], border=1, align='C', fill=True)
                pdf.ln()
                
                # Table Rows
                pdf.set_font("Arial", '', 10)
                for row in data:
                    pdf.cell(widths[0], 8, txt=str(row.get('Ticker', '')), border=1, align='C')
                    pdf.cell(widths[1], 8, txt=str(row.get('Price', '')), border=1, align='C')
                    pdf.cell(widths[2], 8, txt=str(row.get('RSI', '')), border=1, align='C')
                    pdf.cell(widths[3], 8, txt=str(row.get('Vol (K)', '')), border=1, align='C')
                    pdf.cell(widths[4], 8, txt=str(row.get('Fund. Score', '')), border=1, align='C')
                    
                    verdict = str(row.get('AI Verdict', ''))
                    verdict = verdict.encode('ascii', 'ignore').decode('ascii').strip()
                    pdf.cell(widths[5], 8, txt=verdict, border=1, align='C')
                    pdf.ln()
                pdf.ln(10)

            draw_table("Top Bullish Candidates", bullish, True)
            draw_table("Top Bearish Candidates", bearish, False)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                pdf.output(tmp.name)
                with open(tmp.name, "rb") as f: data = f.read()
            os.unlink(tmp.name)
            return data

        pdf_data = generate_pdf_bytes(bullish_final, bearish_final)
        with col_btn3:
            if pdf_data:
                st.download_button(label="📥 Download PDF", data=pdf_data, file_name="Hermes_Top_10_Setups.pdf", mime="application/pdf", use_container_width=True)
            else:
                st.button("📥 Download PDF", disabled=True, help="Installing PDF tools in background...", use_container_width=True)

        if broadcast_clicked:
            if not bot_token or not chat_id:
                st.error("Please enter your Telegram Bot Token and Chat ID to broadcast.")
            else:
                from telegram_utils import format_telegram_message, send_telegram_message
                msg_text = format_telegram_message(bullish_final, bearish_final)
                success, resp = send_telegram_message(bot_token, chat_id, msg_text)
                if success:
                    st.balloons()
                    st.success("✅ " + resp)
                else:
                    st.error("❌ " + resp)

with tab4:
    st.subheader("📋 Expert Fundamental Analyst")
    st.markdown("Act as an expert equity research analyst. Enter any stock ticker below to conduct a rigorous, data-driven fundamental analysis using live valuation, profitability, and health metrics.")
    
    col_input, col_btn2 = st.columns([2, 1])
    with col_input:
        analysis_ticker_raw = st.selectbox("Search Asset (Type to autocomplete):", all_ticker_options, index=0)
        st.markdown("**Or**")
        from streamlit_searchbox import st_searchbox
        def search_asset_expert(searchterm: str):
            return [o for o in all_ticker_options if searchterm.lower() in o.lower()] if searchterm else []
            
        custom_analysis_ticker = st_searchbox(
            search_asset_expert,
            key="expert_searchbox",
            placeholder="Enter Custom Ticker..."
        )
        
        if custom_analysis_ticker:
            analysis_ticker = custom_analysis_ticker.split(" ")[0].upper()
        else:
            analysis_ticker = analysis_ticker_raw.split(" ")[0] if analysis_ticker_raw else "RELIANCE.NS"
    
    st.markdown("""
        <style>
        /* Add a sleek hover animation to buttons */
        div.stButton > button {
            transition: all 0.3s ease-in-out;
            border-radius: 8px;
        }
        div.stButton > button:hover {
            transform: scale(1.05);
            box-shadow: 0px 5px 15px rgba(38, 166, 154, 0.4);
            border-color: #26A69A;
        }
        </style>
    """, unsafe_allow_html=True)
    
    if st.button("Generate Expert Report"):
        if analysis_ticker:
            with st.spinner(f"Analyzing {analysis_ticker}... fetching live fundamental data from Yahoo Finance..."):
                from fundamental import generate_fundamental_report
                report_md = generate_fundamental_report(analysis_ticker.strip().upper())
                add_print_button()
                st.markdown(report_md, unsafe_allow_html=True)
        else:
            st.warning("Please enter a ticker symbol.")

with tab5:
    st.subheader("🧭 Hermes AI Sectorial View")
    st.markdown("Visualizing the flow of institutional liquidity across major Indian sectors. Colored from **Pastel Green (Trending)** to **Pastel Red (Distribution)** based on the Hermes Trend Score.")
    
    if st.button("Generate Sector Heatmap", use_container_width=True):
        with st.spinner("Analyzing top 10 NSE Sectors... This pulls live data and may take 5-10 seconds."):
            try:
                from engine import analyze_indian_sectors
                sector_data = analyze_indian_sectors()
                if sector_data:
                    st.session_state['sector_data'] = sector_data
                else:
                    st.error("Failed to fetch sector data from Yahoo Finance.")
            except Exception as e:
                st.error(f"Error fetching data: {e}")

    if 'sector_data' in st.session_state:
        try:
            import plotly.express as px
            import pandas as pd
            
            df_sectors = pd.DataFrame(st.session_state['sector_data'])
            df_sectors['SliceSize'] = 1
            
            # Use bar_polar since pie does not support color_continuous_scale
            fig = px.bar_polar(
                df_sectors,
                r='SliceSize',
                theta='Sector',
                color='TrendScore',
                color_continuous_scale='RdYlGn',
                hover_data=["TrendScore", "Return_1M", "RSI"]
            )
            
            fig.update_traces(
                hovertemplate="<b>%{theta}</b><br>Hermes Score: %{customdata[0]:.2f}<br>1M Return: %{customdata[1]:.2f}%<br>RSI: %{customdata[2]:.2f}<extra></extra>"
            )
            
            fig.update_layout(
                polar=dict(
                    radialaxis=dict(showticklabels=False, ticks='', showgrid=False),
                    angularaxis=dict(tickfont=dict(size=14, color='#000000')),
                    hole=0.4
                ),
                showlegend=False,
                margin=dict(t=20, b=20, l=20, r=20),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                coloraxis_colorbar=dict(title="Trend Score")
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("### 📊 Raw Sector Metrics")
            
            # Color coding the dataframe
            def color_score(val):
                if val >= 15: return 'color: #2ecc71; font-weight: bold;' # Light Green
                elif val >= 0: return 'color: #27ae60;' # Dark Green
                elif val <= -15: return 'color: #e74c3c; font-weight: bold;' # Light Red
                else: return 'color: #c0392b;' # Dark Red
                
            def get_star_rating(score):
                if score >= 15: return '⭐⭐⭐⭐⭐'
                elif score >= 5: return '⭐⭐⭐⭐'
                elif score >= -5: return '⭐⭐⭐'
                elif score >= -15: return '⭐⭐'
                else: return '⭐'
                
            display_df = df_sectors[['Sector', 'TrendScore', 'Return_1M', 'RSI']].sort_values('TrendScore', ascending=False)
            display_df['Star Ratings'] = display_df['TrendScore'].apply(get_star_rating)
            
            # Reorder columns
            display_df = display_df[['Sector', 'Star Ratings', 'TrendScore', 'Return_1M', 'RSI']]
            
            styled_df = (display_df.style
                .applymap(color_score, subset=['TrendScore'])
                .format({'TrendScore': "{:.2f}", 'Return_1M': "{:.2f}%", 'RSI': "{:.2f}"})
                .set_properties(**{'text-align': 'right'})
            )
            st.dataframe(styled_df, hide_index=True, use_container_width=False)

            # Intelligent Summary
            st.markdown("### 🧠 Hermes AI Sector Intelligence")
            for _, row in display_df.iterrows():
                sector = row['Sector']
                score = row['TrendScore']
                ret = row['Return_1M']
                rsi = row['RSI']
                
                
                # Custom CSS styling for the cards
                base_style = "padding: 15px; border-radius: 8px; box-shadow: 0px 4px 12px rgba(0,0,0,0.3); margin-bottom: 15px; border: 1px solid rgba(255,255,255,0.05);"
                
                if score >= 15:
                    verdict = "🟢 STRONGLY BULLISH"
                    summary = f"Institutional liquidity is aggressively flowing into **{sector}**. With an impressive **{ret:.2f}%** monthly return and high momentum (RSI: **{rsi:.1f}**), this sector is clearly leading the broader market. Pullbacks present high-probability buying opportunities."
                    card_style = f"{base_style} border-left: 5px solid #2ecc71; background-color: rgba(46, 204, 113, 0.1);"
                elif score >= 0:
                    verdict = "🟢 ACCUMULATION"
                    summary = f"**{sector}** is showing positive underlying strength. A modest **{ret:.2f}%** return combined with stable momentum suggests steady institutional accumulation. The sector is absorbing supply and preparing for continuation."
                    card_style = f"{base_style} border-left: 5px solid #3498db; background-color: rgba(52, 152, 219, 0.1);"
                elif score <= -15:
                    verdict = "🔴 STRONGLY BEARISH"
                    summary = f"Severe distribution detected in **{sector}**. A harsh **{ret:.2f}%** drop and deeply weak momentum (RSI: **{rsi:.1f}**) indicates heavy institutional offloading. Avoid long positions until structural breaks are observed."
                    card_style = f"{base_style} border-left: 5px solid #e74c3c; background-color: rgba(231, 76, 60, 0.1);"
                else:
                    verdict = "🔴 DISTRIBUTION / CHOP"
                    summary = f"**{sector}** is currently facing headwinds. Negative returns (**{ret:.2f}%**) and lagging momentum suggest the sector is out of favor. Liquidity is likely rotating out of this sector and into stronger ones."
                    card_style = f"{base_style} border-left: 5px solid #f1c40f; background-color: rgba(241, 196, 15, 0.1);"

                html_content = f'''
                <div style="{card_style}">
                    <h4 style="margin-top: 0px; margin-bottom: 10px; font-size: 16px;">{verdict} | {sector} <span style="font-size:14px; opacity: 0.7;">(Score: {score:.1f})</span></h4>
                    <p style="margin-bottom: 0px; font-size: 14px; line-height: 1.5;">{summary}</p>
                </div>
                '''
                st.markdown(html_content, unsafe_allow_html=True)

        except Exception as e:
            st.error(f"Error generating sectorial view: {e}")

with tab6:
    st.subheader("🛢️ Commodities Expert Signals (ICT)")
    st.markdown("Live algorithmic analysis for Gold, Silver, Crude Oil, and Natural Gas using Smart Money Concepts (FVG, Order Blocks) to map institutional liquidity zones.")
    
    commodities = {
        "Gold": "GC=F",
        "Silver": "SI=F",
        "Crude Oil (WTI)": "CL=F",
        "Natural Gas": "NG=F"
    }
    
    if st.button("Generate Expert Commodities Report", use_container_width=True):
        with st.spinner("Scanning Global Commodities Data..."):
            for comm_name, comm_ticker in commodities.items():
                try:
                    df_comm, ict_data = get_stock_data(comm_ticker, period="6mo")
                except Exception as e:
                    st.error(f"Failed to fetch data for {comm_name} ({comm_ticker}).")
                    continue
                    
                if df_comm is None or df_comm.empty:
                    st.error(f"Failed to fetch data for {comm_name} ({comm_ticker}).")
                    continue
                
                current_price = df_comm['Close'].iloc[-1]
                
                fvgs = ict_data.get('fvg', [])
                obs = ict_data.get('ob', [])
                
                buy_price = 0
                for fvg in fvgs:
                    if fvg['type'] == 'Bull FVG' and fvg['top'] < current_price:
                        if fvg['top'] > buy_price: buy_price = fvg['top']
                
                for ob in obs:
                    if ob['type'] == 'Bull OB' and ob['top'] < current_price:
                        if ob['top'] > buy_price: buy_price = ob['top']
                        
                sell_price = float('inf')
                for fvg in fvgs:
                    if fvg['type'] == 'Bear FVG' and fvg['bot'] > current_price:
                        if fvg['bot'] < sell_price: sell_price = fvg['bot']
                
                for ob in obs:
                    if ob['type'] == 'Bear OB' and ob['bot'] > current_price:
                        if ob['bot'] < sell_price: sell_price = ob['bot']
                        
                if sell_price == float('inf'):
                    sell_price = current_price * 1.05 # default resistance
                if buy_price == 0:
                    buy_price = current_price * 0.95
                    
                trend_verdict = "🟢 STRONGLY BULLISH" if current_price > df_comm['Close'].rolling(50).mean().iloc[-1] else "🔴 STRONGLY BEARISH"
                
                buy_dist_pct = ((current_price - buy_price) / current_price) * 100 if current_price else 0
                sell_dist_pct = ((sell_price - current_price) / current_price) * 100 if current_price else 0
                rr_ratio = (sell_price - current_price) / (current_price - buy_price) if (current_price - buy_price) > 0 else 0

                if trend_verdict.startswith("🟢"):
                    bias_desc = "Primary institutional bias remains <b style='color:#2ecc71;'>BULLISH</b>. Buy-side liquidity is in control."
                    action_desc = "Wait for a retracement into the discount array."
                else:
                    bias_desc = "Primary institutional bias remains <b style='color:#e74c3c;'>BEARISH</b>. Sell programs are dominating the tape."
                    action_desc = "Seek premium arrays for high-probability short entries."
                    
                # Render UI box for the commodity
                base_style = "padding: 20px; border-radius: 10px; box-shadow: 0px 8px 24px rgba(0,0,0,0.4); margin-bottom: 20px; border: 1px solid rgba(255,255,255,0.08);"
                if trend_verdict.startswith("🟢"):
                    card_style = f"{base_style} border-left: 6px solid #2ecc71; background-color: rgba(46, 204, 113, 0.05);"
                else:
                    card_style = f"{base_style} border-left: 6px solid #e74c3c; background-color: rgba(231, 76, 60, 0.05);"

                html_content = f"""<div style="{card_style}">
<h4 style="margin-top: 0px; margin-bottom: 15px; font-size: 20px; letter-spacing: 0.5px;">{comm_name} <span style="font-size:14px; opacity: 0.6; font-weight: normal;">({comm_ticker})</span></h4>
<div style="display: flex; gap: 30px; margin-bottom: 20px; flex-wrap: wrap; background: rgba(128,128,128,0.1); padding: 15px; border-radius: 8px;">
<div><span style="font-size: 11px; text-transform: uppercase; letter-spacing: 1px; opacity: 0.7;">Live Price</span><br><span style="font-size: 26px; font-weight: 800; font-family: monospace;">${current_price:.2f}</span></div>
<div><span style="font-size: 11px; text-transform: uppercase; letter-spacing: 1px; opacity: 0.7;">Optimal Buy Zone</span><br><span style="font-size: 26px; font-weight: 800; color: #2ecc71; font-family: monospace;">${buy_price:.2f}</span></div>
<div><span style="font-size: 11px; text-transform: uppercase; letter-spacing: 1px; opacity: 0.7;">Optimal Sell Zone</span><br><span style="font-size: 26px; font-weight: 800; color: #e74c3c; font-family: monospace;">${sell_price:.2f}</span></div>
</div>
<h5 style="margin-top: 0; margin-bottom: 10px; font-size: 14px; text-transform: uppercase; letter-spacing: 1px;">🧠 Hermes Expert Trader AI Analysis</h5>
<ul style="margin: 0; padding-left: 20px; font-size: 14px; line-height: 1.8;">
<li><b>Market Context:</b> {bias_desc} Current live pricing is hovering at <b>${current_price:.2f}</b>.</li>
<li><b>Demand Zone (Buy):</b> A high-probability institutional order block/FVG rests at <b>${buy_price:.2f}</b> (<i>{buy_dist_pct:.1f}% below live price</i>). {action_desc if trend_verdict.startswith("🟢") else "This is the primary downside target."}</li>
<li><b>Supply Zone (Sell):</b> Unmitigated sell-side liquidity rests at <b>${sell_price:.2f}</b> (<i>{sell_dist_pct:.1f}% above live price</i>). {action_desc if not trend_verdict.startswith("🟢") else "This serves as the primary upside take-profit objective."}</li>
<li><b>Risk-to-Reward Ratio:</b> Entering a long position at the current live price to target supply, while invalidating below demand, offers an implied R:R of <b>{rr_ratio:.2f}x</b>.</li>
</ul>
</div>"""
                st.markdown(html_content, unsafe_allow_html=True)

st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: gray; padding: 10px; font-size: 14px;'>
        Created by <strong>SUDHIR THIKANE</strong> (<a href="mailto:sudhir.thikane@gmail.com" style="color: #26A69A; text-decoration: none;">sudhir.thikane@gmail.com</a>)
    </div>
    """,
    unsafe_allow_html=True
)
