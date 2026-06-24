import yfinance as yf
import pandas as pd
import numpy as np
from engine import fetch_data, calculate_ict_indicators

def resample_data(df: pd.DataFrame, target_interval: str) -> pd.DataFrame:
    if not isinstance(df.index, pd.DatetimeIndex):
        df.index = pd.to_datetime(df.index)
    freq = target_interval.lower()
    ohlc_dict = {
        'Open': 'first',
        'High': 'max',
        'Low': 'min',
        'Close': 'last',
        'Volume': 'sum'
    }
    agg_dict = {col: ohlc_dict[col] for col in df.columns if col in ohlc_dict}
    try:
        df_res = df.resample(freq, origin='start').agg(agg_dict)
    except TypeError:
        df_res = df.resample(freq).agg(agg_dict)
    return df_res.dropna()

def run_backtest(ticker: str, period="1y", interval="1d", rr_ratio=2.0):
    """
    Runs a historical backtest of the 'Rule 4' institutional setup strategy.
    
    Parameters:
        ticker (str): The stock ticker (e.g. 'AAPL' or 'TCS.NS').
        period (str): Lookback period (e.g. '6mo', '1y', '2y').
        interval (str): Timeframe interval ('1d', '1h', '3h', '4h').
        rr_ratio (float): Take-profit risk-to-reward multiplier.
        
    Returns:
        dict: Performance metrics, equity curve data, and a list of trade logs.
    """
    ticker = ticker.strip().upper()
    if " " in ticker:
        ticker = ticker.split(" ")[0]
        
    if "." not in ticker:
        us_tickers = {"AAPL", "MSFT", "TSLA", "AMZN", "NFLX", "NVDA", "GOOG", "META", "AMD", "INTC", "QCOM", "BABA"}
        if ticker not in us_tickers:
            ticker = f"{ticker}.NS"

    fetch_interval = "1h" if interval.lower() in ["3h", "4h"] else interval
    df = fetch_data(ticker, period=period, interval=fetch_interval)
    if df.empty:
        return {
            "error": f"Insufficient data loaded for {ticker} (minimum 50 bars required)."
        }
        
    if interval.lower() in ["3h", "4h"]:
        df = resample_data(df, interval)
        
    if len(df) < 50:
        return {
            "error": f"Insufficient data loaded for {ticker} on {interval} timeframe (minimum 50 bars required, loaded {len(df)})."
        }
        
    df, ict_data = calculate_ict_indicators(ticker, df, generate_logs=False)
    if df.empty:
        return {"error": "Technical calculation returned empty dataset."}
        
    dates = df.index
    close_arr = df['Close'].values
    high_arr = df['High'].values
    low_arr = df['Low'].values
    rsi_arr = df['RSI_14'].values
    vwma_arr = df['VWMA_50'].values
    ob_boxes = ict_data.get('ob', [])
    
    trades = []
    active_trade = None
    
    for i in range(50, len(df)):
        current_date = dates[i]
        current_close = close_arr[i]
        
        # 1. Manage Active Trade
        if active_trade:
            trade_low = low_arr[i]
            trade_high = high_arr[i]
            
            if active_trade['type'] == 'Buy':
                # Check Stop Loss first (conservative check)
                if trade_low <= active_trade['SL']:
                    active_trade['exit_date'] = current_date
                    active_trade['exit_price'] = active_trade['SL']
                    active_trade['pnl'] = active_trade['SL'] - active_trade['entry_price']
                    active_trade['return_pct'] = (active_trade['SL'] / active_trade['entry_price'] - 1.0) * 100.0
                    active_trade['outcome'] = 'Loss'
                    trades.append(active_trade)
                    active_trade = None
                elif trade_high >= active_trade['TP']:
                    active_trade['exit_date'] = current_date
                    active_trade['exit_price'] = active_trade['TP']
                    active_trade['pnl'] = active_trade['TP'] - active_trade['entry_price']
                    active_trade['return_pct'] = (active_trade['TP'] / active_trade['entry_price'] - 1.0) * 100.0
                    active_trade['outcome'] = 'Win'
                    trades.append(active_trade)
                    active_trade = None
            elif active_trade['type'] == 'Sell':
                # Check Stop Loss first (conservative check)
                if trade_high >= active_trade['SL']:
                    active_trade['exit_date'] = current_date
                    active_trade['exit_price'] = active_trade['SL']
                    active_trade['pnl'] = active_trade['entry_price'] - active_trade['SL']
                    active_trade['return_pct'] = (1.0 - active_trade['SL'] / active_trade['entry_price']) * 100.0
                    active_trade['outcome'] = 'Loss'
                    trades.append(active_trade)
                    active_trade = None
                elif trade_low <= active_trade['TP']:
                    active_trade['exit_date'] = current_date
                    active_trade['exit_price'] = active_trade['TP']
                    active_trade['pnl'] = active_trade['entry_price'] - active_trade['TP']
                    active_trade['return_pct'] = (1.0 - active_trade['TP'] / active_trade['entry_price']) * 100.0
                    active_trade['outcome'] = 'Win'
                    trades.append(active_trade)
                    active_trade = None
                    
        # 2. Check for setup entry trigger (only if no active trade)
        if not active_trade:
            # Filter active OBs as of date i (no future lookahead)
            active_obs = [
                ob for ob in ob_boxes
                if ob['start'] <= current_date and (ob.get('end') is None or ob['end'] > current_date)
            ]
            
            latest_rsi = rsi_arr[i]
            latest_vwma = vwma_arr[i]
            
            # --- Bullish Setup ---
            bull_obs = [ob for ob in active_obs if ob['type'] == 'Bull OB']
            if bull_obs and latest_rsi >= 55 and current_close > latest_vwma:
                most_recent_ob = bull_obs[-1]
                ob_top = most_recent_ob['top']
                ob_bot = most_recent_ob['bot']
                
                # Entry condition: close must be above top but within 5% of top
                if ob_top < current_close <= ob_top * 1.05:
                    risk = current_close - ob_bot
                    if risk > 0:
                        active_trade = {
                            'type': 'Buy',
                            'entry_date': current_date,
                            'entry_price': current_close,
                            'SL': ob_bot,
                            'TP': current_close + rr_ratio * risk,
                            'ticker': ticker
                        }
                        
            # --- Bearish Setup ---
            if not active_trade:
                bear_obs = [ob for ob in active_obs if ob['type'] == 'Bear OB']
                if bear_obs:
                    most_recent_ob = bear_obs[-1]
                    ob_top = most_recent_ob['top']
                    ob_bot = most_recent_ob['bot']
                    
                    # Entry condition: close must be below bot but within 5% of bot
                    if ob_bot * 0.95 <= current_close < ob_bot:
                        risk = ob_top - current_close
                        if risk > 0:
                            active_trade = {
                                'type': 'Sell',
                                'entry_date': current_date,
                                'entry_price': current_close,
                                'SL': ob_top,
                                'TP': current_close - rr_ratio * risk,
                                'ticker': ticker
                            }
                            
    # If a trade is still active at the end, close it at the final price
    if active_trade:
        final_price = close_arr[-1]
        active_trade['exit_date'] = dates[-1]
        active_trade['exit_price'] = final_price
        if active_trade['type'] == 'Buy':
            active_trade['pnl'] = final_price - active_trade['entry_price']
            active_trade['return_pct'] = (final_price / active_trade['entry_price'] - 1.0) * 100.0
        else:
            active_trade['pnl'] = active_trade['entry_price'] - final_price
            active_trade['return_pct'] = (1.0 - final_price / active_trade['entry_price']) * 100.0
        active_trade['outcome'] = 'Open'
        trades.append(active_trade)
        
    # Calculate performance metrics
    total_trades = len(trades)
    wins = sum(1 for t in trades if t['outcome'] == 'Win')
    losses = sum(1 for t in trades if t['outcome'] == 'Loss')
    open_trades = sum(1 for t in trades if t['outcome'] == 'Open')
    
    win_rate = (wins / (wins + losses) * 100.0) if (wins + losses) > 0 else 0.0
    
    gross_profits = sum(t['pnl'] for t in trades if t['pnl'] > 0)
    gross_losses = sum(abs(t['pnl']) for t in trades if t['pnl'] < 0)
    profit_factor = (gross_profits / gross_losses) if gross_losses > 0 else (float('inf') if gross_profits > 0 else 0.0)
    
    # Calculate equity curve & drawdown
    equity = 100.0 # start at 100 units
    equity_curve = [100.0]
    dates_curve = [df.index[0]]
    
    drawdown = 0.0
    max_equity = 100.0
    max_drawdown = 0.0
    
    for t in trades:
        ret = t['return_pct']
        equity = equity * (1.0 + ret / 100.0)
        equity_curve.append(equity)
        dates_curve.append(t['exit_date'])
        
        if equity > max_equity:
            max_equity = equity
        dd = (max_equity - equity) / max_equity * 100.0
        if dd > max_drawdown:
            max_drawdown = dd
            
    return {
        "trades": trades,
        "total_trades": total_trades,
        "wins": wins,
        "losses": losses,
        "open": open_trades,
        "win_rate": win_rate,
        "profit_factor": profit_factor,
        "max_drawdown": max_drawdown,
        "final_equity": equity,
        "equity_curve": {
            "dates": dates_curve,
            "equity": equity_curve
        }
    }
