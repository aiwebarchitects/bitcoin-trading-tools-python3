#!/usr/bin/env python3
"""
Fetches current Bollinger Bands (upper, middle, lower) for a given symbol on the 1-minute timeframe using Binance data.
Usage: python bollinger_bands_1min.py --symbol BTC
Notes:
- Accepts a symbol like BTC or BTCUSDT. If no quote asset is specified, BTCUSDT is assumed.
- Uses a 20-period 1-minute window (middle = 20-period SMA, bands = +/- 2 std dev, population std).
- Data fetched from Binance public API (no authentication).

Example:
    python bollinger_bands_1min.py --symbol BTC
"""
import argparse
import sys
import re
import math
from datetime import datetime, timezone

from binance.client import Client
from binance.exceptions import BinanceAPIException

def validate_symbol_format(symbol: str) -> bool:
    return bool(re.match(r'^[A-Z0-9]+$', symbol))

def main():
    parser = argparse.ArgumentParser(description="Fetch Bollinger Bands for a symbol on 1-minute timeframe from Binance.")
    parser.add_argument('--symbol', required=True, help='Trading symbol (e.g., BTC or BTCUSDT)')
    args = parser.parse_args()

    symbol_input = args.symbol.upper().strip()
    if not validate_symbol_format(symbol_input):
        print("Error: Invalid symbol format. Use only uppercase letters and numbers, e.g., BTCUSDT or BTC.", file=sys.stderr)
        sys.exit(1)

    # If the user provided a base symbol without a quote asset, assume USDT pairing
    symbol = symbol_input
    if "USDT" not in symbol and "BUSD" not in symbol:
        symbol = symbol_input + "USDT"

    # Initialize Binance client (unauthenticated)
    client = Client("", "")

    try:
        klines = client.get_klines(symbol=symbol, interval='1m', limit=20)
    except BinanceAPIException as e:
        print(f"Binance API error while fetching klines for symbol {symbol}: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error while fetching klines for symbol {symbol}: {e}", file=sys.stderr)
        sys.exit(1)

    if not isinstance(klines, list) or len(klines) < 20:
        got = len(klines) if isinstance(klines, list) else 0
        print(f"Error: Insufficient klines data received for symbol {symbol}. Expected 20, got {got}.", file=sys.stderr)
        sys.exit(1)

    closes = []
    last_kline = klines[-1]
    try:
        for k in klines:
            closes.append(float(k[4]))
    except (ValueError, IndexError, TypeError) as e:
        print(f"Error parsing klines data: {e}", file=sys.stderr)
        sys.exit(1)

    if len(closes) != 20:
        print(f"Error: Could not parse 20 close prices from klines. Got {len(closes)}.", file=sys.stderr)
        sys.exit(1)

    # Bollinger Bands calculation (population std)
    middle = sum(closes) / len(closes)
    n = len(closes)
    variance = sum((x - middle) ** 2 for x in closes) / n
    std = math.sqrt(variance)

    upper = middle + 2 * std
    lower = middle - 2 * std

    # Most recent close and its timestamp
    last_close = closes[-1]
    try:
        last_close_ts = last_kline[6]  # close time in ms
        ts_iso = datetime.fromtimestamp(last_close_ts / 1000.0, tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S %Z')
    except Exception:
        ts_iso = "N/A"

    print(f"Symbol: {symbol} | Interval: 1m | Time: {ts_iso} | Middle: {middle:.8f} | Upper: {upper:.8f} | Lower: {lower:.8f} | Last Close: {last_close:.8f}")

if __name__ == "__main__":
    main()