#!/usr/bin/env python3
"""
Calculates Chaikin Money Flow (CMF) for a symbol on the 1-minute timeframe using Binance data.
Usage: python cmf_getter_1min.py --symbol BTC

Algorithm Overview:
- Data retrieval: Fetch latest 1-minute klines from Binance (up to 1000 candles).
- CMF calculation over the last N candles (window, default 20):
  - denom = High - Low; if denom == 0, MFM = 0
  - MFM = ((Close - Low) - (High - Close)) / denom
  - MFV = MFM * Volume
  - CMF = sum(MFV) / sum(Volume)
- Output: JSON payload with symbol, timeframe, window, cmf, and timestamp (latest candle close time in UTC).
- Error handling: Print descriptive errors to stderr and exit non-zero on failure.

Example:
  python cmf_getter_1min.py --symbol BTC
"""

import argparse
import json
import sys
import datetime
from binance.client import Client

def normalize_symbol(symbol_input: str) -> str:
    s = symbol_input.strip().upper()
    if not s:
        raise ValueError("Symbol cannot be empty.")
    # If user provides a base symbol like BTC, convert to BTCUSDT
    if not s.endswith("USDT"):
        s = s + "USDT"
    return s

def fetch_klines(client: Client, symbol: str, limit: int = 1000):
    try:
        # 1 minute interval
        interval = Client.KLINE_INTERVAL_1MINUTE
        klines = client.get_klines(symbol=symbol, interval=interval, limit=limit)
        if not isinstance(klines, list) or len(klines) == 0:
            raise ValueError("No klines data returned from Binance.")
        return klines
    except Exception as e:
        raise RuntimeError(f"Failed to fetch klines for {symbol}: {e}")

def compute_cmf(klines, window: int) -> (float, int, int):
    if len(klines) < window:
        raise ValueError(f"Insufficient candles: requested {window}, got {len(klines)}")

    last_n = klines[-window:]

    sum_mfv = 0.0
    sum_vol = 0.0

    for idx, candle in enumerate(last_n):
        # Kline data layout:
        # [0 Open time, 1 Open, 2 High, 3 Low, 4 Close, 5 Volume, 6 Close time, ...]
        high = float(candle[2])
        low = float(candle[3])
        close = float(candle[4])
        vol = float(candle[5])

        denom = high - low
        if denom == 0.0:
            mfm = 0.0
        else:
            mfm = ((close - low) - (high - close)) / denom

        mfv = mfm * vol
        sum_mfv += mfv
        sum_vol += vol

    if sum_vol == 0.0:
        raise ValueError("Sum of volumes is zero, cannot compute CMF.")

    cmf = sum_mfv / sum_vol
    # Use the close time of the latest candle for timestamp
    latest_close_time_ms = int(last_n[-1][6])
    return cmf, latest_close_time_ms, window

def ms_to_utc_iso(ts_ms: int) -> str:
    ts = datetime.datetime.utcfromtimestamp(ts_ms / 1000.0)
    return ts.strftime("%Y-%m-%dT%H:%M:%SZ")

def main():
    parser = argparse.ArgumentParser(description="Calculate CMF on 1-minute Binance data.")
    parser.add_argument('--symbol', required=True, help='Trading symbol or base symbol (e.g., BTC or BTCUSDT)')
    parser.add_argument('--window', type=int, default=20, help='Window size in candles (default: 20)')
    args = parser.parse_args()

    try:
        symbol_name = normalize_symbol(args.symbol)
        window = int(args.window)
        if window <= 0:
            raise ValueError("Window must be a positive integer.")

        # Initialize Binance client (no API key required for public data)
        client = Client("", "")

        # Fetch klines (1m interval, up to 1000 candles)
        klines = fetch_klines(client, symbol_name, limit=1000)

        cmf_value, ts_ms, used_window = compute_cmf(klines, window)
        timestamp_iso = ms_to_utc_iso(ts_ms)

        payload = {
            "symbol": symbol_name,
            "timeframe": "1m",
            "window": used_window,
            "cmf": cmf_value,
            "timestamp": timestamp_iso
        }

        print(json.dumps(payload, indent=2))
        sys.exit(0)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()