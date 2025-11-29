#!/usr/bin/env python3
"""
Calculates the standard deviation of 1-minute closing prices to assess short-term volatility.
Usage: python stddev_getter_1min.py --symbol BTC
"""
import argparse
import sys
import math
from binance.client import Client

def normalize_symbol(symbol: str) -> str:
    s = symbol.upper().strip()
    if "USDT" in s:
        return s
    if len(s) <= 4 and s.isalpha():
        return f"{s}USDT"
    if s.endswith("USD"):
        base = s[:-3]
        if base:
            return f"{base}USDT"
    return s

def compute_sample_stddev(values):
    n = 0
    mean = 0.0
    M2 = 0.0
    for x in values:
        n += 1
        delta = x - mean
        mean += delta / n
        delta2 = x - mean
        M2 += delta * delta2
    if n < 2:
        raise ValueError("At least two data points are required to compute sample stddev.")
    variance = M2 / (n - 1)
    return math.sqrt(variance)

def main():
    parser = argparse.ArgumentParser(description="Compute the sample standard deviation of 1-minute close prices for a given symbol.")
    parser.add_argument('--symbol', required=True, help='Trading symbol (e.g., BTC, ETH, or BTCUSDT, BTCUSD)')
    parser.add_argument('--window', type=int, default=20, help='Number of 1-minute closes to include (default: 20)')
    args = parser.parse_args()

    symbol_input = args.symbol
    window = args.window

    # Validate window
    if window is None or not isinstance(window, int) or window < 2:
        print(f"Error: --window must be an integer >= 2. Received: {window}", file=sys.stderr)
        sys.exit(2)

    symbol_pair = normalize_symbol(symbol_input)

    try:
        client = Client("", "")
        klines = client.get_klines(symbol=symbol_pair, interval='1m', limit=window)
    except Exception as e:
        print(f"Error: Data/API fetch failed for symbol {symbol_pair}. Details: {e}", file=sys.stderr)
        sys.exit(1)

    if not klines or len(klines) < window:
        print(f"Error: Insufficient data for symbol {symbol_pair}. Requested: {window} points, got: {len(klines) if klines else 0}", file=sys.stderr)
        sys.exit(1)

    closes = []
    for kline in klines:
        close_str = kline[4]
        try:
            closes.append(float(close_str))
        except Exception:
            print(f"Error: Non-numeric close price encountered: {close_str}", file=sys.stderr)
            sys.exit(2)

    if len(closes) < 2:
        print(f"Error: Insufficient close data after parsing. Need at least 2 values.", file=sys.stderr)
        sys.exit(2)

    try:
        stddev = compute_sample_stddev(closes)
    except Exception as e:
        print(f"Error: Could not compute stddev. Details: {e}", file=sys.stderr)
        sys.exit(2)

    # Print result
    print(f"stddev_1min | symbol={symbol_pair} | window={window} | stddev={stddev:.4f}")

if __name__ == "__main__":
    main()