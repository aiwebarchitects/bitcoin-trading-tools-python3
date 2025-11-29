#!/usr/bin/env python3
"""
Calculates Chaikin Volatility for a given symbol on 1-minute timeframe; compatible with python script.py --symbol BTC
Usage: python chaikin_volatility_getter_1min.py --symbol BTC
"""

import argparse
import sys
import math
import datetime
from binance.client import Client

def ema_full(values, period):
    """
    Calculate EMA values for a list given a period.
    Returns a list of EMA values starting from index (period - 1).
    """
    if values is None or len(values) < period:
        return []
    emas = []
    initial = sum(values[:period]) / period
    emas.append(initial)
    alpha = 2.0 / (period + 1)
    for i in range(period, len(values)):
        next_val = alpha * values[i] + (1 - alpha) * emas[-1]
        emas.append(next_val)
    return emas

def calc_chaikin_volatility(R, Close, N):
    """
    Compute Chaikin Volatility series given:
    - R: list of High-Low ranges
    - Close: list of Close prices
    - N: EMA period
    Returns list of CV values (aligned with EMA outputs).
    """
    ema_R = ema_full(R, N)
    ema_C = ema_full(Close, N)
    length = min(len(ema_R), len(ema_C))
    if length <= 0:
        return []
    CVs = []
    for i in range(length):
        denom = ema_C[i]
        if denom is None or denom == 0 or not math.isfinite(denom):
            CVs.append(float('nan'))
        else:
            CVs.append(100.0 * (ema_R[i] / denom - 1.0))
    return CVs

def main():
    parser = argparse.ArgumentParser(description='Chaikin Volatility on 1-minute candles from Binance')
    parser.add_argument('--symbol', required=True, help='Trading symbol (e.g., BTC)')
    parser.add_argument('--N', type=int, default=10, help='EMA period N (default 10)')
    parser.add_argument('--limit', type=int, default=200, help='Number of 1m candles to fetch (default 200)')
    args = parser.parse_args()

    if not args.symbol or not isinstance(args.symbol, str) or len(args.symbol.strip()) == 0:
        print("Error: --symbol is required and must be a non-empty string.")
        sys.exit(1)

    symbol = args.symbol.upper()
    pair = f"{symbol}USDT"

    # Initialize Binance client with no API keys
    client = Client("", "")

    try:
        klines = client.get_klines(symbol=pair, interval=Client.KLINE_INTERVAL_1MINUTE, limit=args.limit)
        if not klines or len(klines) < args.N:
            print(f"Error: Insufficient data received for {pair}. Candles fetched: {len(klines) if klines else 0}, required: {args.N}.")
            sys.exit(2)
    except Exception as e:
        print(f"Error fetching data for {pair}: {e}")
        sys.exit(3)

    # Build OHLCV arrays
    highs = []
    lows = []
    closes = []
    for k in klines:
        try:
            highs.append(float(k[2]))
            lows.append(float(k[3]))
            closes.append(float(k[4]))
        except Exception:
            continue

    # Validate
    if not highs or not lows or not closes or len(highs) != len(lows) or len(lows) != len(closes):
        print("Error: Failed to parse OHLCV data from Binance.")
        sys.exit(4)

    # Compute range R
    R = [h - l for h, l in zip(highs, lows)]

    # Clean NaNs / invalids
    R_clean = []
    C_clean = []
    for r, c in zip(R, closes):
        if isinstance(r, (int, float)) and isinstance(c, (int, float)) and math.isfinite(r) and math.isfinite(c):
            R_clean.append(float(r))
            C_clean.append(float(c))
    if len(R_clean) < args.N:
        print(f"Error: Not enough valid data after cleaning. Valid candles: {len(R_clean)}, required N={args.N}.")
        sys.exit(5)

    # Calculate Chaikin Volatility
    CVs = calc_chaikin_volatility(R_clean, C_clean, args.N)
    if not CVs:
        print("Error: Could not compute Chaikin Volatility due to insufficient data after EMA initialization.")
        sys.exit(6)

    latest = CVs[-1]
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    if latest is None or not math.isfinite(latest) or math.isnan(latest):
        print("Error: Latest Chaikin Volatility value is invalid (NaN/Inf).")
        sys.exit(7)

    # Print result
    print(f"{now} - Chaikin Volatility (1m, N={args.N}) for {symbol}: {latest:.4f}%")

if __name__ == "__main__":
    main()