#!/usr/bin/env python3
"""
Computes Fibonacci retracement levels (38.2%, 50%, 61.8%) from the latest 1-minute price swing using Binance OHLCV data for a given symbol
Usage: python fibonacci_retracement_getter_1min.py --symbol BTC
"""
import argparse
import sys
import datetime
from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceRequestException


def normalize_symbol(symbol: str) -> str:
    if not symbol or not symbol.strip():
        raise ValueError("Symbol must be a non-empty string.")
    sym = symbol.strip().upper()
    if not sym.endswith("USDT"):
        sym = f"{sym}USDT"
    return sym


def main():
    parser = argparse.ArgumentParser(description="Compute 1-minute Fibonacci retracement levels from the latest swing.")
    parser.add_argument('--symbol', required=True, help='Trading symbol (e.g., BTC) - will be mapped to BTCUSDT if missing suffix')
    args = parser.parse_args()

    try:
        pair = normalize_symbol(args.symbol)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    # Binance client with no authentication
    client = Client("", "")

    try:
        klines = client.get_klines(symbol=pair, interval="1m", limit=2)
    except (BinanceAPIException, BinanceRequestException) as e:
        print(f"Binance API error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error retrieving data: {e}", file=sys.stderr)
        sys.exit(1)

    if not klines or len(klines) < 2:
        print("Error: Insufficient OHLCV data received from Binance.", file=sys.stderr)
        sys.exit(1)

    candle = klines[0]  # oldest of the two candles (latest completed 1m swing)
    try:
        o = float(candle[1])
        h = float(candle[2])
        l = float(candle[3])
        c = float(candle[4])
        close_time_ms = int(candle[6])
    except Exception as e:
        print(f"Error parsing candle data: {e}", file=sys.stderr)
        sys.exit(1)

    now_ms = int(datetime.datetime.utcnow().timestamp() * 1000)
    if close_time_ms > now_ms:
        print("Error: Latest completed candle close time is in the future; candle may not be completed.", file=sys.stderr)
        sys.exit(1)

    range_price = h - l
    if range_price <= 0:
        print("Error: Non-positive price range detected; no meaningful swing.", file=sys.stderr)
        sys.exit(1)

    bullish = c >= o

    levels = [0.382, 0.5, 0.618]
    price_by_level = {}
    for L in levels:
        if bullish:
            price = h - range_price * L
        else:
            price = l + range_price * L
        price_by_level[L] = price

    # Time string in UTC
    dt = datetime.datetime.utcfromtimestamp(close_time_ms / 1000.0)
    time_str = dt.strftime("%Y-%m-%d %H:%M:%S")

    print(f"Symbol: {pair}")
    print(f"Time (completed candle end): {time_str} UTC")
    print(f"Swing high: {h:.4f}, Swing low: {l:.4f}, Open: {o:.4f}, Close: {c:.4f}")
    print(f"38.2% retracement: {price_by_level[0.382]:.4f}")
    print(f"50.0% retracement: {price_by_level[0.5]:.4f}")
    print(f"61.8% retracement: {price_by_level[0.618]:.4f}")


if __name__ == "__main__":
    main()