# 📈 Hermes ICT Pro Trading Dashboard

**Created by SUDHIR THIKANE** ([sudhir.thikane@gmail.com](mailto:sudhir.thikane@gmail.com))

Hermes Quant Platform is a professional-grade equity trading and analysis dashboard specifically designed for algorithmic and institutional traders. It utilizes **ICT (Inner Circle Trader) / Smart Money Concepts** combined with deep fundamental financial analysis to uncover high-probability trading opportunities in the stock market (especially customized for the Indian NSE/BSE markets).

---

## 🔥 Core Features

### 📊 1. Institutional Charting & Main Dashboard
- Interactive, responsive candlestick charting utilizing **Plotly**.
- Automated identification and overlay of **Fair Value Gaps (FVGs)**, bullish/bearish **Order Blocks**, and **Liquidity Pools**.
- **VWMA (Volume Weighted Moving Average)** mapping and multi-timeframe structural bias logic.
- Intelligent range-break filtering that automatically removes weekend/after-hours gaps for a true continuous price feed (TradingView style).
- Print & PDF Export ready format for saving daily setups.

### 📡 2. Advanced Indian Market Scanner
- A multithreaded scanning engine that iterates across thousands of NSE stocks concurrently.
- Actively identifies and flags recent Institutional Footprints (like untouched FVGs or Order Blocks) to build highly actionable watchlists.
- Paginated table interface dynamically loads scan results, keeping UI fast and responsive.

### 📋 3. Expert Analyst Fundamental Engine
- Fully automated algorithmic fundamental analysis engine.
- Calculates an objective **1-10 Fundamental Score** and a final verdict (Buy, Accumulate, Hold, Sell, Avoid).
- Features a beautiful, responsive HTML/CSS "widget card" layout integrated directly into Streamlit for maximum visual impact.
- Parses live metrics from **Yahoo Finance**:
  - **Valuation:** P/E, P/B, EV/EBITDA, PEG
  - **Profitability:** ROE, Operating Margin, Net Margin
  - **Financial Health:** Debt-to-Equity, Current/Quick Ratios
  - **Growth & Cash Flow:** YoY Revenue/Earnings Growth, Free Cash Flow
- Automated fallback to **Google News RSS** to fetch live headlines if primary API data fails.

---

## 🛠️ Technology Stack
- **Python 3.10+**
- **Streamlit** (UI / Frontend layout)
- **Pandas** & **NumPy** (Data processing)
- **Plotly Graph Objects** (Interactive charting)
- **YFinance** (Live market data API)

---

## 🚀 Installation & Setup

1. **Clone the Repository:**
   ```bash
   git clone <repository_url>
   cd hermes-quant-platform
   ```

2. **Install Dependencies:**
   Ensure you have Python installed. Then run:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Dashboard:**
   ```bash
   streamlit run app.py
   ```
   *The app will launch locally on your browser (usually `http://localhost:8501`).*

---

## 📂 Project Structure

- `app.py`: The main Streamlit interface handling layout, CSS styling, and dashboard rendering.
- `engine.py`: The core computational logic for scanning arrays, fetching data, and mapping ICT indicators.
- `fundamental.py`: The autonomous reporting engine that grades financial metrics and returns a sleek HTML widget payload.
- `nse_list.csv`: The master universe dataset containing the symbols of all stocks the scanner monitors.

---

## 🤝 Disclaimer
*This platform is designed for research and educational purposes. It does not constitute financial advice. The ICT indicators and fundamental scoring logic rely on external live data, which may be delayed or missing.*
