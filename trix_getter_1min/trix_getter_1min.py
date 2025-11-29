#!/usr/bin/env python3
"""
Fetches the TRIX (triple smoothed EMA rate of change) momentum indicator for a given symbol on 1-minute candles using the Binance API. Usage: python trix_getter_1min.py --symbol BTC
Usage example: python trix_getter_1min.py --symbol BTC
"""

import argparse
import sys
from datetime import datetime

from binance.client import Client
from binance.exceptions import BinanceAPIException


def fetch_klines(client: Client, pair: str, limit: int = 1000):
    """
    Fetch 1-minute klines for the given trading pair.
    """
    try:
        klines = client.get_klines(symbol=pair, interval=Client.KLINE_INTERVAL_1MINUTE, limit=limit)
        return klines
    except BinanceAPIException as e:
        raise RuntimeError(f"Binance API error: {e.message}")
    except Exception as e:
        raise RuntimeError(f"Network or other error while fetching data: {e}")


def compute_ema(values, period: int):
    """
    Simple EMA implementation (seed with first value).
    """
    if period <= 0 or not values:
        return []
    k = 2.0 / (period + 1)
    emas = []
    ema_prev = None
    for i, v in enumerate(values):
        if i == 0:
            ema = v
        else:
            ema = v * k + ema_prev * (1 - k)
        emas.append(ema)
        ema_prev = ema
    return emas


def compute_trix(closes, period: int = 15):
    """
    Compute TRIX values given close prices and EMA period.
    Returns a tuple: (trix_list, e3_values)
    trix_list contains None for positions where not enough data to compute.
    """
    e1 = compute_ema(closes, period)
    e2 = compute_ema(e1, period)
    e3 = compute_ema(e2, period)

    trix = []
    for i in range(len(e3)):
        if i == 0:
            trix.append(None)
        else:
            prev = e3[i - 1]
            cur = e3[i]
            if prev is None or cur is None or prev == 0:
                trix.append(None)
            else:
                trix.append(((cur - prev) / prev) * 100.0)
    return trix, e3


def to_timestamp_utc_ms(ms: int) -> str:
    dt = datetime.utcfromtimestamp(ms / 1000.0)
    return dt.strftime('%Y-%m-%dT%H:%M:%SZ')


def main():
    parser = argparse.ArgumentParser(description='Fetch TRIX(1m) for a given symbol using Binance API.')
    parser.add_argument('--symbol', required=True, help='Trading symbol (e.g., BTC, ETH). If not ending with USDT, BTC -> BTCUSDT')
    args = parser.parse_args()

    symbol_input = args.symbol.strip().upper()
    # Normalize to a Binance pair: if already ends with USDT use as is; else append USDT
    pair = symbol_input if symbol_input.endswith('USDT') else f"{symbol_input}USDT"

    # Initialize Binance client (no authentication)
    client = Client("", "")

    try:
        klines = fetch_klines(client, pair, limit=1000)
    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    if not klines or len(klines) == 0:
        print("Invalid symbol, unable to fetch data", file=sys.stderr)
        sys.exit(1)

    closes = []
    for k in klines:
        try:
            closes.append(float(k[4]))
        except (IndexError, ValueError):
            print("Error parsing close prices from data", file=sys.stderr)
            sys.exit(1)

    # Ensure enough history for TRIX: need at least 3*n + 1 points
    n = 15
    required = 3 * n + 1
    if len(closes) < required:
        print(f"Not enough data to compute TRIX. Need at least {required} closes, have {len(closes)}.", file=sys.stderr)
        sys.exit(1)

    trix_vals, _ = compute_trix(closes, period=n)
    # Ensure we have valid latest and previous values
    latest_trix = trix_vals[-1]
    prev_trix = trix_vals[-2] if len(trix_vals) >= 2 else None

    if latest_trix is None or prev_trix is None:
        print("Not enough data to compute TRIX (warming period not complete).", file=sys.stderr)
        sys.exit(1)

    change = latest_trix - prev_trix

    # Timestamp of the latest candle close
    last_close_time_ms = int(klines[-1][6])
    timestamp_str = to_timestamp_utc_ms(last_close_time_ms)

    print(
        f"TRIX(1m) for {pair}: {latest_trix:.4f}% ({change:.4f}%) as of {timestamp_str}"
    )


if __name__ == "__main__":
    main()