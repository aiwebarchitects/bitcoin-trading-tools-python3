#!/usr/bin/env python3
"""
Computes the Z-score of the last 20 closing prices to evaluate how far current price deviates from its 20-period mean on 1-minute candles for a given symbol.
Usage: python zscore_price_1min.py --symbol BTC
"""
import sys
import argparse
import math
from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceRequestException

def normalize_symbol(symbol: str) -> str:
    s = symbol.strip().upper()
    if not s:
        raise ValueError("Symbol must be a non-empty string.")
    if not s.endswith('USDT'):
        s = s + 'USDT'
    return s

def fetch_last_20_closes(symbol_pair: str) -> list:
    client = Client("", "")
    try:
        klines = client.get_klines(symbol=symbol_pair, interval='1m', limit=20)
    except (BinanceAPIException, BinanceRequestException) as e:
        raise RuntimeError(f"Error fetching klines for {symbol_pair}: {e}")
    closes = []
    for k in klines:
        try:
            closes.append(float(k[4]))
        except (IndexError, ValueError, TypeError) as e:
            raise RuntimeError(f"Invalid klines data for {symbol_pair}: {e}")
    if len(closes) < 20:
        raise RuntimeError(f"Insufficient data: expected 20 closes, got {len(closes)}")
    return closes

def main():
    parser = argparse.ArgumentParser(description="Compute Z-score of the last 20 1-minute closes for a symbol.")
    parser.add_argument('--symbol', required=True, help='Trading symbol (e.g., BTC, ETH)')
    args = parser.parse_args()
    if not args.symbol or not isinstance(args.symbol, str) or args.symbol.strip() == "":
        parser.error("Symbol must be a non-empty string.")

    input_symbol = args.symbol.strip()
    try:
        symbol_pair = normalize_symbol(input_symbol)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(2)

    try:
        closes = fetch_last_20_closes(symbol_pair)
    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(3)

    mean = sum(closes) / 20.0
    variance = sum((x - mean) ** 2 for x in closes) / 20.0
    std = math.sqrt(variance)
    latest = closes[-1]
    if std > 0:
        z = (latest - mean) / std
    else:
        z = 0.0
        print("Warning: Standard deviation is zero; price series is flat.", file=sys.stderr)

    print(f"Symbol: {input_symbol} | Z-score (last 20 closes, 1m): {z:.6f} | mean={mean:.6f} | std={std:.6f} | latest={latest:.6f} | n=20")

if __name__ == "__main__":
    main()