import sys
import time
import json
import csv
import numpy as np
import pandas as pd
from binance.client import Client
from binance.exceptions import BinanceAPIException

# -----------------------------------------------------------------------------
# CONFIGURATION
# -----------------------------------------------------------------------------
TIMEFRAME = Client.KLINE_INTERVAL_1HOUR
LIMIT = 100  # Need enough data for 50-period BBW + lookbacks
PAIRS_TO_SCAN = [
    'BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'SOLUSDT', 'XRPUSDT', 
    'ADAUSDT', 'DOGEUSDT', 'AVAXUSDT', 'DOTUSDT', 'LINKUSDT',
    'MATICUSDT', 'LTCUSDT', 'ATOMUSDT', 'NEARUSDT', 'UNIUSDT'
]

# -----------------------------------------------------------------------------
# INDICATOR CALCULATIONS
# -----------------------------------------------------------------------------
def calculate_indicators(df):
    """
    Calculates technical indicators required for the GemHunter algorithm.
    """
    # 1. Bollinger Bands (20, 2) & Band Width
    df['tp'] = (df['high'] + df['low'] + df['close']) / 3
    df['sma_20'] = df['close'].rolling(window=20).mean()
    df['std_20'] = df['close'].rolling(window=20).std()
    df['bb_upper'] = df['sma_20'] + (df['std_20'] * 2)
    df['bb_lower'] = df['sma_20'] - (df['std_20'] * 2)
    
    # BB Width: (Upper - Lower) / Middle
    # Handle division by zero just in case
    df['bbw'] = (df['bb_upper'] - df['bb_lower']) / df['sma_20']
    
    # 2. RSI (14)
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['rsi'] = 100 - (100 / (1 + rs))
    
    # 3. MACD (12, 26, 9)
    exp1 = df['close'].ewm(span=12, adjust=False).mean()
    exp2 = df['close'].ewm(span=26, adjust=False).mean()
    df['macd_line'] = exp1 - exp2
    df['macd_signal'] = df['macd_line'].ewm(span=9, adjust=False).mean()
    df['macd_hist'] = df['macd_line'] - df['macd_signal']
    
    # 4. On-Balance Volume (OBV)
    df['obv'] = (np.sign(df['close'].diff()) * df['volume']).fillna(0).cumsum()
    
    # 5. Volume Oscillator (5, 10) & Volume SMA
    df['vol_sma_5'] = df['volume'].rolling(window=5).mean()
    df['vol_sma_10'] = df['volume'].rolling(window=10).mean()
    df['vol_sma_20'] = df['volume'].rolling(window=20).mean()
    
    # Formula: ((Short - Long) / Long) * 100
    df['vol_osc'] = ((df['vol_sma_5'] - df['vol_sma_10']) / df['vol_sma_10']) * 100
    
    # 6. ATR (14) for Stop Loss
    df['tr1'] = df['high'] - df['low']
    df['tr2'] = abs(df['high'] - df['close'].shift())
    df['tr3'] = abs(df['low'] - df['close'].shift())
    df['tr'] = df[['tr1', 'tr2', 'tr3']].max(axis=1)
    df['atr'] = df['tr'].rolling(window=14).mean()

    return df

def get_obv_slope(obv_series, period=14):
    """Calculates Linear Regression Slope of OBV for the last n periods."""
    if len(obv_series) < period:
        return 0
    y = obv_series.tail(period).values
    x = np.arange(period)
    # Polyfit returns [slope, intercept]
    slope, _ = np.polyfit(x, y, 1)
    return slope

# -----------------------------------------------------------------------------
# SCANNER LOGIC
# -----------------------------------------------------------------------------
def analyze_pair(client, symbol):
    try:
        # Fetch Data
        klines = client.get_klines(symbol=symbol, interval=TIMEFRAME, limit=LIMIT)
        
        # Create DataFrame
        df = pd.DataFrame(klines, columns=[
            'timestamp', 'open', 'high', 'low', 'close', 'volume', 
            'close_time', 'quote_asset_volume', 'trades', 
            'taker_buy_base', 'taker_buy_quote', 'ignore'
        ])
        
        # Type conversion
        cols = ['open', 'high', 'low', 'close', 'volume']
        df[cols] = df[cols].astype(float)
        
        # Calculate Indicators
        df = calculate_indicators(df)
        
        # We analyze the last completed candle (index -1)
        # Note: In live trading, you might look at -1 (closed) or -1 (current forming)
        # Here we assume we are scanning for a setup on the just-closed candle
        curr = df.iloc[-1]
        prev = df.iloc[-2]
        
        # ---------------------------------------------------------
        # Phase 1: Squeeze & Accumulation
        # ---------------------------------------------------------
        
        # BBW Logic: Current BBW < Lowest(BBW, last 50) * 1.1
        # Get last 50 BBW values excluding current to find historical low
        last_50_bbw = df['bbw'].iloc[-51:-1] 
        min_bbw_50 = last_50_bbw.min()
        
        is_squeeze = curr['bbw'] < (min_bbw_50 * 1.1)
        
        # OBV Slope Logic
        obv_slope = get_obv_slope(df['obv'], 14)
        is_accumulation = obv_slope > 0
        
        if not (is_squeeze and is_accumulation):
            return None # Fail Phase 1

        # ---------------------------------------------------------
        # Phase 3: Volume Injection (Checked early to save processing)
        # ---------------------------------------------------------
        
        # Vol Osc > 20 OR Vol > 150% of SMA20
        vol_spike = (curr['vol_osc'] > 20) or (curr['volume'] > (curr['vol_sma_20'] * 1.5))
        
        if not vol_spike:
            return None # Fail Phase 3

        # ---------------------------------------------------------
        # Phase 2: Dual-Signal Trigger
        # ---------------------------------------------------------
        
        # Signal A: Bullish RSI Divergence (Last 10 bars)
        # Logic: Price makes Lower Low, RSI makes Higher Low
        # Lookback window (excluding current)
        window_price = df['low'].iloc[-11:-1]
        window_rsi = df['rsi'].iloc[-11:-1]
        
        price_ll = curr['low'] < window_price.min() # Current low is lower than previous 10
        rsi_hl = curr['rsi'] > window_rsi.min()     # Current RSI is higher than previous 10 min
        
        is_divergence = price_ll and rsi_hl
        
        # Signal B: MACD Validation (3-bar window)
        # MACD Hist flip (- to +) OR MACD Line cross 0
        macd_check_window = df.iloc[-3:]
        
        macd_cross_0 = False
        hist_flip = False
        
        # Check if MACD line crossed 0 upwards in last 3 bars
        if (macd_check_window['macd_line'].min() < 0) and (curr['macd_line'] > 0):
            macd_cross_0 = True
            
        # Check if Hist flipped negative to positive
        # Check if any bar in window was negative and current is positive
        if (macd_check_window['macd_hist'].min() < 0) and (curr['macd_hist'] > 0):
            hist_flip = True
            
        is_macd_valid = macd_cross_0 or hist_flip
        
        if not (is_divergence and is_macd_valid):
            return None # Fail Phase 2

        # ---------------------------------------------------------
        # Phase 4: Risk Management Data
        # ---------------------------------------------------------
        
        # Stop Loss: Min(Swing Low - 1ATR, Lower BB)
        # Swing Low is current low in this context of divergence
        sl_atr = curr['low'] - curr['atr']
        sl_bb = curr['bb_lower']
        stop_loss = min(sl_atr, sl_bb)
        
        take_profit_1 = curr['bb_upper']
        
        return {
            'symbol': symbol,
            'price': curr['close'],
            'signal': 'BUY',
            'setup': 'GemHunter Dual-Signal',
            'stop_loss': round(stop_loss, 4),
            'tp_target_1': round(take_profit_1, 4),
            'vol_osc': round(curr['vol_osc'], 2),
            'obv_slope': round(obv_slope, 2),
            'bbw': round(curr['bbw'], 4),
            'timestamp': str(curr['close_time'])
        }

    except Exception as e:
        # print(f"Error analyzing {symbol}: {e}")
        return None

# -----------------------------------------------------------------------------
# MAIN EXECUTION
# -----------------------------------------------------------------------------
def main():
    # Initialize Client (No keys needed for public data)
    client = Client()
    
    print(f"--- GemHunter Dual-Signal Scanner Started ---")
    print(f"Timeframe: {TIMEFRAME}")
    print(f"Scanning {len(PAIRS_TO_SCAN)} pairs...")
    
    results = []
    
    for pair in PAIRS_TO_SCAN:
        # Respect API limits
        time.sleep(0.2) 
        
        signal = analyze_pair(client, pair)
        if signal:
            print(f"[FOUND GEM] {pair} - Price: {signal['price']}")
            results.append(signal)
        else:
            # Optional: Print progress
            # print(f". {pair} checked (no signal)")
            pass

    # Output Results
    if results:
        # JSON Output
        with open('gemhunter_results.json', 'w') as f:
            json.dump(results, f, indent=4)
        
        # CSV Output
        keys = results[0].keys()
        with open('gemhunter_results.csv', 'w', newline='') as f:
            dict_writer = csv.DictWriter(f, fieldnames=keys)
            dict_writer.writeheader()
            dict_writer.writerows(results)
            
        print(f"\nScan Complete. Found {len(results)} signals.")
        print("Results saved to gemhunter_results.json and gemhunter_results.csv")
    else:
        print("\nScan Complete. No signals found matching criteria.")

if __name__ == "__main__":
    """
    Example Usage:
    1. Install dependencies: pip install python-binance pandas numpy
    2. Run script: python gemhunter.py
    3. Check output files for trade signals.
    """
    main()