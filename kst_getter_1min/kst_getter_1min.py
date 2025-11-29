#!/usr/bin/env python3
"""
Calculates the Know Sure Thing (KST) momentum oscillator for a given symbol on the 1-minute timeframe using Binance data.

Usage:
  python kst_getter_1min.py --symbol BTC
  or
  python kst_getter_1min.py --symbol BTCUSDT

Notes:
- Uses python-binance (from binance.client import Client) with no authentication.
- Fetches last 200 1-minute klines and computes KST with ROC periods [10,15,20,30]
  and SMA periods [10,10,15,15] with weights [1,2,3,4].
- Outputs the latest KST, its signal line (SMA(KST,9)) and histogram (KST - Signal)
  in UTC time.

Error handling:
- Invalid/missing symbol prints usage, exits non-zero.
- Handles HTTP/api errors with clear messages and retries (backoff).
- Checks for sufficient data; requires at least ~45 candles to compute all SMAs, recommends 60–100.
- Non-numeric parsing errors are reported with the offending field.
"""

import argparse
import sys
import time
from datetime import datetime
from typing import List, Optional

from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceRequestException


def normalize_symbol(input_symbol: str) -> str:
    s = input_symbol.strip().upper()
    if not s:
        raise ValueError("Symbol cannot be empty.")
    # If user provides a base asset like BTC, default to BTCUSDT
    if len(s) <= 4 and not s.endswith("USDT"):
        s = s + "USDT"
    return s


def fetch_klines_with_backoff(symbol: str, retries: int = 3, backoff_base: float = 2.0) -> List:
    client = Client("", "")
    attempt = 0
    while attempt <= retries:
        try:
            # 1-minute interval, last 200 candles
            klines = client.get_klines(symbol=symbol, interval=Client.KLINE_INTERVAL_1MINUTE, limit=200)
            return klines
        except (BinanceAPIException, BinanceRequestException) as e:
            wait = (backoff_base ** attempt) if attempt > 0 else 1.0
            print(f"Binance API error on attempt {attempt + 1}/{retries + 1}: {e}. Retrying in {wait:.1f}s...", file=sys.stderr)
            time.sleep(wait)
            attempt += 1
        except Exception as e:
            print(f"Unexpected error while fetching klines: {e}", file=sys.stderr)
            sys.exit(1)

    print("Failed to fetch klines after multiple attempts. Exiting.", file=sys.stderr)
    sys.exit(1)


def compute_sma_from_roc(roc_list: List[Optional[float]], t: int, S: int) -> Optional[float]:
    start = t - S + 1
    if start < 0:
        return None
    window = roc_list[start : t + 1]
    if any(v is None for v in window):
        return None
    return sum(window) / S


def main():
    parser = argparse.ArgumentParser(description="Calculate KST on 1-minute Binance data.")
    parser.add_argument(
        "--symbol",
        required=False,
        default="BTC",
        help="Trading symbol (e.g., BTC) or pair (e.g., BTCUSDT). If only base is given, USDT pair will be assumed.",
    )
    args = parser.parse_args()

    raw_symbol = args.symbol
    try:
        symbol_binance = normalize_symbol(raw_symbol)
    except ValueError as ve:
        print(f"Error: {ve}", file=sys.stderr)
        parser.print_usage()
        sys.exit(2)

    print(f"Fetching 1-minute klines for {symbol_binance} (normalized from {raw_symbol})...")

    klines = fetch_klines_with_backoff(symbol_binance, retries=3, backoff_base=2.0)
    if not klines or len(klines) == 0:
        print("Error: No klines returned from Binance API.", file=sys.stderr)
        sys.exit(1)

    # Extract closes and times
    closes = []
    times_utc = []
    try:
        for k in klines:
            close_price = float(k[4])
            closes.append(close_price)
            open_time_ms = int(k[0])
            times_utc.append(datetime.utcfromtimestamp(open_time_ms / 1000.0))
    except (ValueError, TypeError, IndexError) as e:
        print(f"Error parsing klines data: {e}", file=sys.stderr)
        sys.exit(1)

    N = len(closes)
    if N < 45:
        print(f"Insufficient data: need at least 45 candles for stable KST computation, have {N}.", file=sys.stderr)
        sys.exit(1)

    # ROC periods and SMA periods
    P_list = [10, 15, 20, 30]
    S_list = [10, 10, 15, 15]
    weights = [1, 2, 3, 4]

    # Compute ROC arrays
    roc10 = [None] * N
    roc15 = [None] * N
    roc20 = [None] * N
    roc30 = [None] * N

    for t in range(N):
        if t >= 10:
            denom = closes[t - 10]
            if denom != 0:
                roc10[t] = ((closes[t] - denom) / denom) * 100.0
        if t >= 15:
            denom = closes[t - 15]
            if denom != 0:
                roc15[t] = ((closes[t] - denom) / denom) * 100.0
        if t >= 20:
            denom = closes[t - 20]
            if denom != 0:
                roc20[t] = ((closes[t] - denom) / denom) * 100.0
        if t >= 30:
            denom = closes[t - 30]
            if denom != 0:
                roc30[t] = ((closes[t] - denom) / denom) * 100.0

    # Compute SMAs for each ROC
    sma10 = [None] * N
    sma15 = [None] * N
    sma20 = [None] * N
    sma30 = [None] * N

    for t in range(N):
        sma10[t] = compute_sma_from_roc(roc10, t, 10)
        sma15[t] = compute_sma_from_roc(roc15, t, 10)
        sma20[t] = compute_sma_from_roc(roc20, t, 15)
        sma30[t] = compute_sma_from_roc(roc30, t, 15)

    # Compute KST with weights
    kst = [None] * N
    min_t_for_kst = max(10 + 10 - 1, 15 + 10 - 1, 20 + 15 - 1, 30 + 15 - 1)  # 44
    for t in range(N):
        if t >= min_t_for_kst:
            if None in (sma10[t], sma15[t], sma20[t], sma30[t]):
                continue
            kst[t] = (
                weights[0] * sma10[t]
                + weights[1] * sma15[t]
                + weights[2] * sma20[t]
                + weights[3] * sma30[t]
            )

    # Compute signal line SMA(KST, 9)
    signal = [None] * N
    for t in range(N):
        if t >= min_t_for_kst + 9 - 1:  # 44 + 8 = 52
            window = [kst[i] for i in range(t - 9, t + 1) if kst[i] is not None]
            if len(window) == 9:
                signal[t] = sum(window) / 9.0

    # Compute Histogram
    histogram = [None] * N
    for t in range(N):
        if (kst[t] is not None) and (signal[t] is not None):
            histogram[t] = kst[t] - signal[t]

    # Output latest values
    last_index = N - 1
    latest_time = times_utc[last_index].strftime("%Y-%m-%d %H:%M")

    latest_kst = kst[last_index]
    latest_signal = signal[last_index]
    latest_hist = histogram[last_index]

    # Print results
    print(f"Symbol: {raw_symbol.upper()}")
    print(f"Time (UTC): {latest_time}")
    if latest_kst is None:
        print("KST: N/A")
    else:
        print(f"KST: {latest_kst:.6f}")
    if latest_signal is None:
        print("Signal: N/A")
    else:
        print(f"Signal: {latest_signal:.6f}")
    if latest_hist is None:
        print("Histogram: N/A")
    else:
        print(f"Histogram: {latest_hist:.6f}")


if __name__ == "__main__":
    main()