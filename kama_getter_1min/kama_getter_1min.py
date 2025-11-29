#!/usr/bin/env python3
"""
Fetches the current Kaufman's Adaptive Moving Average (KAMA) value for a given symbol on the 1-minute timeframe using Binance API.
Usage: python kama_getter_1min.py --symbol BTC
"""
import argparse
import sys
from binance.client import Client
from datetime import datetime

def to_iso(ts_ms: int) -> str:
    return datetime.utcfromtimestamp(ts_ms / 1000.0).strftime("%Y-%m-%dT%H:%M:%SZ")

def fetch_klines(symbol: str, limit: int = 100):
    # Binance public REST API (no authentication required)
    client = Client('', '')
    try:
        klines = client.get_klines(symbol=symbol, interval='1m', limit=limit)
        if not isinstance(klines, list) or len(klines) == 0:
            raise RuntimeError("Empty klines response")
        return klines
    except Exception as e:
        raise RuntimeError(f"Binance API error: {e}")

def compute_kama_from_klines(klines, n: int = 10):
    # Extract close prices
    closes = []
    for k in klines:
        try:
            closes.append(float(k[4]))
        except Exception as e:
            raise RuntimeError(f"Invalid klines data: {e}")

    if len(closes) < n + 1:
        raise ValueError("Insufficient data: need at least n+1 close prices")

    # Timestamp of the last kline close
    ts_iso = to_iso(klines[-1][6])

    FastSC = 2.0 / (2.0 + 1.0)  # ~0.6667
    SlowSC = 2.0 / (30.0 + 1.0)  # ~0.0645

    # Initialize KAMA as SMA of first n closes
    kama = sum(closes[:n]) / n

    for t in range(n, len(closes)):
        denom = 0.0
        for i in range(t - n + 1, t + 1):
            denom += abs(closes[i] - closes[i - 1])
        ER = abs(closes[t] - closes[t - n]) / denom if denom != 0.0 else 0.0
        SC = (ER * (FastSC - SlowSC) + SlowSC) ** 2
        kama = kama + SC * (closes[t] - kama)

    last_close = closes[-1]
    return kama, last_close, ts_iso

def main():
    parser = argparse.ArgumentParser(description="Fetches the current Kaufman's Adaptive Moving Average (KAMA) value for a given symbol on 1-minute timeframe via Binance API.")
    parser.add_argument('--symbol', required=True, help='Trading symbol to fetch (e.g., BTC). Will be used as BTCUSDT on Binance.')
    args = parser.parse_args()

    symbol_input = args.symbol.upper()
    if symbol_input.endswith('USDT'):
        symbol = symbol_input
    else:
        symbol = f"{symbol_input}USDT"

    try:
        klines = fetch_klines(symbol, limit=100)
    except Exception as e:
        print(f"ERROR: Failed to retrieve klines for symbol '{symbol}': {e}")
        sys.exit(1)

    try:
        kama_value, last_close, timestamp = compute_kama_from_klines(klines, n=10)
    except ValueError as ve:
        print(f"ERROR: {ve}")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: Failed to compute KAMA: {e}")
        sys.exit(1)

    print_line = f"KAMA_1MIN | symbol={symbol} | kama={kama_value:.2f} | last_close={last_close:.2f} | n=10 | timestamp={timestamp}"
    print(print_line)

if __name__ == "__main__":
    main()