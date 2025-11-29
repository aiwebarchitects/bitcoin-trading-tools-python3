#!/usr/bin/env python3
"""
Calculates and returns the Relative Vigor Index (RVI) for a given symbol on 1-minute candles
Usage: python rvi_getter_1min.py --symbol BTC
Notes:
- If you pass BTC, it will assume BTCUSDT by default (e.g., BTC -> BTCUSDT).
- Defaults: N = 10 candles
- No API key/secret required (Binance public endpoints)
- Uses python-binance library: from binance.client import Client
- Handles errors gracefully and exits with non-zero status on failure
"""

import argparse
import sys
from datetime import datetime
from binance.client import Client

def resolve_symbol(symbol: str) -> str:
    s = symbol.strip().upper()
    if s.endswith("USDT") or s.endswith("USDC") or s.endswith("BUSD"):
        return s
    # Default to USDT-paired trading pair if not explicitly provided
    return s + "USDT"

def main():
    parser = argparse.ArgumentParser(description="Compute the 1-minute RVI for a given symbol.")
    parser.add_argument('--symbol', required=True, help='Trading symbol (e.g., BTC or BTCUSDT)')
    parser.add_argument('--n', type=int, default=10, help='Number of candles to use for RVI calculation (default: 10)')
    args = parser.parse_args()

    symbol = resolve_symbol(args.symbol)
    n = int(args.n)
    if n <= 0:
        print("Error: n must be a positive integer", file=sys.stderr)
        sys.exit(3)

    try:
        client = Client("", "")
        candles = client.get_klines(symbol=symbol, interval=Client.KLINE_INTERVAL_1MINUTE, limit=n)
    except Exception as e:
        print(f"Error fetching candles for symbol '{symbol}': {e}", file=sys.stderr)
        sys.exit(1)

    if not candles or len(candles) < n:
        got = len(candles) if candles is not None else 0
        print(f"Insufficient candle data for symbol '{symbol}': requested {n}, got {got}", file=sys.stderr)
        sys.exit(2)

    diffs = []
    times_ms = []
    for k in candles:
        # k[0]: open time in ms, k[1]: open, k[4]: close
        try:
            o = float(k[1])
            c = float(k[4])
            t = int(k[0])
        except (ValueError, TypeError) as e:
            print(f"Data parsing error: {e}", file=sys.stderr)
            sys.exit(4)
        diffs.append(c - o)
        times_ms.append(t)

    # Compute RVI using the last window of size n
    window = n
    if len(diffs) < window:
        print(f"Error: not enough data to compute RVI with window {window}", file=sys.stderr)
        sys.exit(5)

    sum_diff = sum(diffs[-window:])
    sma_diff = sum_diff / window

    sum_abs = sum(abs(d) for d in diffs[-window:])
    sma_abs = sum_abs / window

    if sma_abs == 0:
        rvi_last = 0.0
    else:
        rvi_last = 100.0 * (sma_diff / sma_abs)

    time_last = datetime.fromtimestamp(times_ms[-1] / 1000.0)
    time_str = time_last.strftime("%Y-%m-%d %H:%M:%S")

    print(f"Symbol: {symbol} | Time: {time_str} | RVI(1m, N={n}): {rvi_last:.6f}")

if __name__ == "__main__":
    main()