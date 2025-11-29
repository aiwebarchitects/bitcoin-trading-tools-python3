#!/usr/bin/env python3
"""
Calculates Volume-Price Trend (VPT) for a given symbol on 1-minute candles using Binance data
Usage: python vpt_getter_1min.py --symbol BTC
"""

import argparse
import time
from datetime import datetime
from typing import Optional, Tuple

from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceRequestException


def safe_get_klines(client: Client, symbol: str, limit: int = 1000, max_retries: int = 5) -> Optional[list]:
    """
    Fetch 1-minute klines for a symbol with simple backoff on rate limits.
    Tries up to max_retries times.
    """
    for attempt in range(max_retries):
        try:
            klines = client.get_klines(symbol=symbol, interval=Client.KLINE_INTERVAL_1MINUTE, limit=limit)
            return klines
        except BinanceAPIException as e:
            msg = str(e)
            # Basic rate-limit handling
            if isinstance(e, BinanceAPIException) and (e.status_code == 429 or "Rate limit" in msg or "Too Many Requests" in msg or "Too many requests" in msg):
                sleep_sec = 2 ** attempt
                time.sleep(sleep_sec)
                continue
            # If API reports invalid symbol, return None to trigger fallback outside
            if "Invalid symbol" in msg or "Invalid symbol." in msg or "Symbol does not exist" in msg:
                return None
            # Other API exceptions: retry a bit
            time.sleep((2 ** attempt) * 0.5)
            continue
        except BinanceRequestException as e:
            # Network or request error, backoff
            time.sleep((2 ** attempt) * 0.5)
            continue
        except Exception:
            # Unknown error, backoff and retry
            time.sleep((2 ** attempt) * 0.5)
            continue
    return None


def compute_vpt(klines: list) -> float:
    """
    Compute cumulative Volume-Price Trend (VPT) from klines.
    klines: list where each item is [OpenTime, Open, High, Low, Close, Volume, ...]
    Returns the final VPT value as float.
    """
    if klines is None or len(klines) < 2:
        return 0.0

    vpt = 0.0
    # Start from index 1 to compute delta with previous close
    for i in range(1, len(klines)):
        try:
            close_i = float(klines[i][4])
            close_prev = float(klines[i - 1][4])
            vol_i = float(klines[i][5])
        except (ValueError, IndexError):
            # If parsing fails, skip this bar
            continue

        if close_prev != 0.0:
            delta = close_i - close_prev
            vpt += vol_i * (delta / close_prev)
        # If close_prev == 0, skip as per specification to avoid division by zero
    return vpt


def ms_to_utc_str(ms: int) -> str:
    dt = datetime.utcfromtimestamp(ms / 1000.0)
    return dt.strftime("%Y-%m-%d %H:%M")


def main():
    parser = argparse.ArgumentParser(description="Calculate VPT (1-minute) from Binance data for a given symbol.")
    parser.add_argument('--symbol', required=True, help='Trading symbol (e.g., BTC or BTCUSDT)')
    args = parser.parse_args()

    input_symbol = args.symbol.strip().upper()
    if not input_symbol:
        print("Error: --symbol is required.")
        return

    # Initialize Binance client without authentication
    client = Client("", "")

    # Try the provided symbol first; if it fails, attempt common USDT pairing
    symbols_to_try: Tuple[str, ...] = (input_symbol, f"{input_symbol}USDT") if not input_symbol.upper().endswith("USDT") else (input_symbol,)

    used_symbol: Optional[str] = None
    klines: Optional[list] = None

    for sym in symbols_to_try:
        try:
            klines = safe_get_klines(client, sym, limit=1000, max_retries=5)
            if klines is not None:
                used_symbol = sym
                break
        except Exception as e:
            # Print a light debug message and continue trying other symbol variants
            # In production, consider logging the exception
            continue

    if klines is None or used_symbol is None:
        print("Error: Unable to fetch data for the provided symbol. Please verify symbol availability on Binance.")
        return

    if len(klines) < 2:
        print("insufficient data: fewer than 2 bars returned.")
        return

    vpt_latest = compute_vpt(klines)
    last_kline = klines[-1]
    last_time_utc = ms_to_utc_str(int(last_kline[0]))
    last_close = float(last_kline[4])

    # Output
    print(f"Symbol: {used_symbol}")
    print(f"Last Time (UTC): {last_time_utc}")
    print(f"Last Close: {last_close:.2f}")
    print(f"VPT (latest): {vpt_latest:.2f}")


if __name__ == "__main__":
    main()