import yfinance as yf

sectors = {
    "Bank": "^NSEBANK",
    "IT": "^CNXIT",
    "Auto": "^CNXAUTO",
    "FMCG": "^CNXFMCG",
    "Metal": "^CNXMETAL",
    "Pharma": "^CNXPHARMA",
    "Energy": "^CNXENERGY",
    "Realty": "^CNXREALTY",
    "Infra": "^CNXINFRA",
    "PSE": "^CNXPSE"
}

for name, ticker in sectors.items():
    data = yf.download(ticker, period="1mo", progress=False)
    if not data.empty:
        print(f"Success: {name} ({ticker}) - Last Price: {data['Close'].iloc[-1].values[0]:.2f}")
    else:
        print(f"Failed: {name} ({ticker})")
