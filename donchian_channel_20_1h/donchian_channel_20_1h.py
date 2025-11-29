#!/usr/bin/env python3
"""
Calculates 20-period Donchian Channel (high/low) on 1h candles and highlights breakout potential for a given symbol
Usage: python donchian_channel_20_1h.py --symbol BTCUSDT
"""

import argparse
import json
import re
import sys
import time
from datetime import datetime
from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceRequestException


def ms_to_utc(ms: int) -> str:
    return datetime.utcfromtimestamp(ms / 1000.0).strftime('%Y-%m-%d %H:%M:%S UTC')


def is_valid_symbol(symbol: str) -> bool:
    return bool(re.match(r'^[A-Z0-9]+$', symbol)) and 2 <= len(symbol) <= 40


def fetch_klines(client: Client, symbol: str, limit: int = 21):
    # Retry a few times on transient errors
    max_retries = 3
    for attempt in range(max_retries):
        try:
            klines = client.get_klines(symbol=symbol, interval=Client.KLINE_INTERVAL_1HOUR, limit=limit)
            return klines
        except (BinanceAPIException, BinanceRequestException) as e:
            if attempt == max_retries - 1:
                print(f"Error fetching data for {symbol}: {e}", file=sys.stderr)
                sys.exit(1)
            time.sleep(1)
        except Exception as e:
            if attempt == max_retries - 1:
                print(f"Unexpected error fetching data for {symbol}: {e}", file=sys.stderr)
                sys.exit(1)
            time.sleep(1)
    return None


def main():
    parser = argparse.ArgumentParser(description='Calculate DC20 on 1h candles and detect breakout')
    parser.add_argument('--symbol', required=True, help='Trading symbol (e.g., BTCUSDT or BTC)')
    args = parser.parse_args()

    symbol = args.symbol.strip().upper()

    if not symbol or not is_valid_symbol(symbol):
        print("Invalid symbol. Symbol must be a non-empty alphanumeric string (e.g., BTCUSDT).", file=sys.stderr)
        sys.exit(2)

    # Binance API client (no authentication required)
    client = Client("", "")

    # Fetch latest 21 1h candles to compute DC20 on the last 20 complete candles
    klines = fetch_klines(client, symbol, limit=21)

    if not klines or len(klines) < 21:
        print("Insufficient data for DC20 (need 20 1h candles).", file=sys.stderr)
        sys.exit(1)

    # 20 candles for DC window: use the 20 candles ending with the candle just before the latest ([-2])
    dc_window = klines[-21:-1]  # indices -21 ... -2 -> 20 candles

    if len(dc_window) < 20:
        print("Insufficient data for DC20 (need 20 1h candles).", file=sys.stderr)
        sys.exit(1)

    try:
        upper = max(float(k[2]) for k in dc_window)  # high values
        lower = min(float(k[3]) for k in dc_window)  # low values
    except Exception as e:
        print(f"Error parsing candle data: {e}", file=sys.stderr)
        sys.exit(1)

    # The latest completed candle is the last in dc_window: klines[-2]
    latest_completed = klines[-2]
    try:
        close_latest = float(latest_completed[4])
        close_time_ms = int(latest_completed[6])
    except Exception as e:
        print(f"Error extracting OHLC data: {e}", file=sys.stderr)
        sys.exit(1)

    t_str = ms_to_utc(close_time_ms)

    # Donchian channel metrics
    mid = (upper + lower) / 2.0
    range_half = (upper - lower) / 2.0
    distance_pct = 0.0 if range_half == 0 else ((close_latest - mid) / range_half) * 100.0

    if close_latest > upper:
        breakout = "Bull"
        signal = "bullish"
    elif close_latest < lower:
        breakout = "Bear"
        signal = "bearish"
    else:
        breakout = "None"
        signal = "none"

    # Human-readable output
    human_line = (
        f"Symbol: {symbol} | Time: {t_str} | "
        f"DC20-Upper: {upper:.2f} | DC20-Lower: {lower:.2f} | "
        f"Close: {close_latest:.2f} | Breakout: {breakout} | Distance: {distance_pct:.2f}%"
    )
    print(human_line)

    # Machine-friendly JSON output
    output_json = {
        "symbol": symbol,
        "timestamp": t_str,
        "donchian": {
            "upper": round(upper, 2),
            "lower": round(lower, 2)
        },
        "close": round(close_latest, 2),
        "signal": signal,
        "distance_pct": round(distance_pct, 2)
    }

    print(json.dumps(output_json))


if __name__ == "__main__":
    main()