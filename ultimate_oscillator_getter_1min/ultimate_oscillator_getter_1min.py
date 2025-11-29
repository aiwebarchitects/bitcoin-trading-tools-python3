#!/usr/bin/env python3
"""
Calculates the Ultimate Oscillator for a given symbol on 1-minute candles using three moving averages of
Typical Price derived from Binance data.

Usage: python ultimate_oscillator_getter_1min.py --symbol BTC
Notes:
- If you pass a base symbol like BTC, the script will try BTCUSDT first, then BTC as a fallback.
- Fetches up to 1000 1-minute candles by default. Requires at least 29 candles for initial UO calculation.

"""

import argparse
import sys
from datetime import datetime
from binance.client import Client


def fetch_klines_with_fallback(symbol_base, limit=1000):
    client = Client("", "")
    s = symbol_base.upper()
    candidates = []
    if s.endswith("USDT"):
        candidates = [s]
    else:
        candidates = [s + "USDT", s]

    for sym in candidates:
        try:
            klines = client.get_klines(symbol=sym, interval=Client.KLINE_INTERVAL_1MINUTE, limit=limit)
            if klines and len(klines) > 0:
                return klines, sym
        except Exception:
            continue
    return None, None


def main():
    parser = argparse.ArgumentParser(description="Calculate Ultimate Oscillator for a given symbol on 1-minute candles.")
    parser.add_argument('--symbol', required=True, help='Trading symbol or base symbol (e.g., BTC or BTCUSDT)')
    parser.add_argument('--limit', type=int, default=1000, help='Number of 1m candles to fetch (default 1000)')
    args = parser.parse_args()

    symbol_input = args.symbol.strip()
    limit = args.limit

    # Data retrieval with fallback for symbol formats
    klines, symbol_used = fetch_klines_with_fallback(symbol_input, limit=limit)
    if klines is None or symbol_used is None:
        print(f"Error: Unable to retrieve data for symbol '{symbol_input}'. Tried common variants (e.g., {symbol_input.upper()}USDT).", file=sys.stderr)
        sys.exit(2)

    # Parse klines into OHLC arrays
    open_times = []
    highs = []
    lows = []
    closes = []

    for k in klines:
        # Binance kline structure:
        # [OpenTime, Open, High, Low, Close, Volume, CloseTime, ...]
        open_times.append(int(k[0]))
        highs.append(float(k[2]))
        lows.append(float(k[3]))
        closes.append(float(k[4]))

    n = len(closes)

    # Need at least 29 candles to compute the first Ultimate Oscillator value
    if n < 29:
        print(f"Error: Insufficient candles for calculation. Retrieved {n} candles for {symbol_used}. Need at least 29 candles.", file=sys.stderr)
        sys.exit(3)

    # Compute r-values as per Ultimate Oscillator
    r_values = []
    for i in range(1, n):
        prev_close = closes[i - 1]
        bp = closes[i] - min(lows[i], prev_close)
        tr = max(highs[i], prev_close) - min(lows[i], prev_close)
        r = 0.0 if tr == 0 else bp / tr
        r_values.append(r)

    if len(r_values) < 28:
        print(f"Error: Not enough r-values to compute 28-period SMA. r_values={len(r_values)}", file=sys.stderr)
        sys.exit(4)

    # Latest UO corresponds to the latest available r index
    i = len(r_values) - 1  # r index, also corresponds to candle index for UO value

    def sma(values, end_idx, window):
        if end_idx - window + 1 < 0:
            return None
        slice_vals = values[end_idx - window + 1 : end_idx + 1]
        if not slice_vals:
            return None
        return sum(slice_vals) / window

    avg7 = sma(r_values, i, 7)
    avg14 = sma(r_values, i, 14)
    avg28 = sma(r_values, i, 28)

    if avg7 is None or avg14 is None or avg28 is None:
        print("Error: Unable to compute SMAs due to insufficient data.", file=sys.stderr)
        sys.exit(5)

    uo = 100.0 * (4.0 * avg7 + 2.0 * avg14 + avg28) / 7.0

    # Timestamp for the UO value: use the candle corresponding to r index i
    ts_ms = open_times[i]
    ts_dt = datetime.utcfromtimestamp(ts_ms / 1000.0)
    ts_str = ts_dt.strftime("%Y-%m-%d %H:%M:%S UTC")

    print(f"Symbol {symbol_used} 1m UO: {uo:.2f} (as of {ts_str})")


if __name__ == "__main__":
    main()