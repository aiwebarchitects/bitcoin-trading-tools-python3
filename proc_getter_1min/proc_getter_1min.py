#!/usr/bin/env python3
"""
Calculates Price Rate of Change (PROC) for a given symbol on 1-minute timeframe using Binance API
Usage: python proc_getter_1min.py --symbol BTC
"""
import argparse
import datetime
import time
import sys
from binance.client import Client

def normalize_symbol(symbol: str) -> str:
    s = symbol.strip().upper()
    if not s:
        return s
    if s.endswith("USDT"):
        return s
    # Basic convenience: allow short symbol like BTC -> BTCUSDT
    return s + "USDT"

def main():
    parser = argparse.ArgumentParser(add_help=True, description="Compute PROC_1m for a given Binance symbol.")
    parser.add_argument('--symbol', required=True, help='Trading symbol or pair (e.g., BTC or BTCUSDT)')
    parser.add_argument('--lookback', type=int, default=20, help='Lookback period in minutes (default 20)')
    args = None
    try:
        args = parser.parse_args()
    except SystemExit as e:
        # argparse will handle printing usage on its own
        sys.exit(e.code)

    if args.lookback < 1:
        print("Error: --lookback must be >= 1")
        parser.print_usage()
        sys.exit(2)

    symbol = normalize_symbol(args.symbol)
    lookback = args.lookback

    # Initialize Binance client (no authentication for free endpoints)
    client = Client("", "", requests_params={'timeout': 10})

    klines = None
    max_attempts = 3
    last_error = None

    for attempt in range(1, max_attempts + 1):
        try:
            klines = client.get_klines(
                symbol=symbol,
                interval=Client.KLINE_INTERVAL_1MINUTE,
                limit=lookback + 1
            )
            break
        except Exception as e:
            last_error = str(e)
            if attempt < max_attempts:
                time.sleep(1)
            else:
                print(f"HTTP request failed: {last_error}")
                sys.exit(3)

    if klines is None or len(klines) < lookback + 1:
        print(f"Symbol not found or insufficient data for {symbol}. Required: {lookback + 1} candles, got: {len(klines) if klines else 0}")
        sys.exit(4)

    try:
        latest_close = float(klines[-1][4])
        past_close = float(klines[-(lookback + 1)][4])
    except (IndexError, ValueError) as e:
        print(f"Error parsing candle data: {e}")
        sys.exit(5)

    if past_close == 0.0:
        print("Invalid past close value (0) encountered; cannot compute PROC.")
        sys.exit(6)

    proc = ((latest_close - past_close) / past_close) * 100.0

    # Timestamp of the latest candle's close time (CloseTime)
    try:
        close_time_ms = int(klines[-1][6])
        ts = datetime.datetime.utcfromtimestamp(close_time_ms / 1000.0).strftime('%Y-%m-%dT%H:%M:%SZ')
    except (IndexError, ValueError) as e:
        ts = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')

    print("PROC_1m({}) = {:.2f}% as of {}".format(symbol, proc, ts))

if __name__ == "__main__":
    main()