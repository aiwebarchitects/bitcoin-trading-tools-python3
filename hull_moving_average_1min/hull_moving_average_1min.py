#!/usr/bin/env python3
"""
Calculates the Hull Moving Average (HMA) on 1-minute candles to smooth price and highlight short-term trend changes for a given symbol using Binance data.
Usage: python hull_moving_average_1min.py --symbol BTC
"""
import argparse
import json
import math
import sys
from datetime import datetime, timezone

from binance.client import Client


def wma_series(values, window):
    """
    Compute the Weighted Moving Average (WMA) series for a given window.
    Returns a list of WMA values, one per index where a full window can be applied.
    Weights increase from oldest to newest within the window (1..window).
    """
    n = len(values)
    if window <= 0 or n < window:
        return []
    denom = window * (window + 1) // 2
    result = []
    for i in range(window - 1, n):
        acc = 0.0
        for j in range(window):
            weight = j + 1
            idx = i - (window - 1 - j)
            acc += values[idx] * weight
        result.append(acc / denom)
    return result


def compute_hma_from_closes(closes, n):
    """
    Compute Hull Moving Average (HMA) for the given closes and period n.
    Returns a tuple (latest_hma, hma_series) where:
      - latest_hma is the most recent HMA value (or None if insufficient data)
      - hma_series is the full series of HMA values (if computed) or None
    The method follows:
      wma_n = WMA(closes, n)
      wma_n2 = WMA(closes, floor(n/2))
      raw = 2*wma_n2 - wma_n  (as a time series aligned to the end)
      hma = WMA(raw, floor(sqrt(n)))
    """
    if n < 2:
        return None, None

    wma_n_series = wma_series(closes, n)
    wma_n2_series = wma_series(closes, n // 2)

    if not wma_n_series or not wma_n2_series:
        return None, None

    min_len = min(len(wma_n_series), len(wma_n2_series))
    wma_n_series = wma_n_series[-min_len:]
    wma_n2_series = wma_n2_series[-min_len:]

    raw_series = [2.0 * a2 - a1 for a1, a2 in zip(wma_n_series, wma_n2_series)]
    m = int(math.isqrt(n))
    if m <= 0:
        return None, raw_series

    hma_series = wma_series(raw_series, m)
    if not hma_series:
        return None, raw_series

    return hma_series[-1], hma_series


def main():
    parser = argparse.ArgumentParser(description="Hull Moving Average on 1-minute candles from Binance (1m interval).")
    parser.add_argument('--symbol', required=True, help='Trading symbol or base asset (e.g., BTC or BTCUSDT)')
    parser.add_argument('--period', type=int, default=14, help='HMA period (default 14)')
    args = parser.parse_args()

    symbol_input = args.symbol
    period = args.period

    # Validate period
    if period < 2:
        print(json.dumps({"error": f"Invalid period {period}. Must be >= 2"}))
        sys.exit(1)

    # Resolve symbol candidates (support base symbol like BTC or full pair like BTCUSDT)
    base = symbol_input.upper()
    if base.endswith('USDT') or base.endswith('BUSD') or base.endswith('BNB'):
        symbol_candidates = [base]
    else:
        symbol_candidates = [base + 'USDT', base]

    client = Client("", "")

    actual_symbol = None
    klines = None
    closes = None
    last_close = None
    last_kline_time = None
    last_symbol = None
    hma_latest = None
    hma_series = None
    timestamp_iso = None

    # Determine data limit to ensure enough data for HMA calculation
    s = int(math.isqrt(period))
    if s < 1:
        s = 1
    data_limit = period + s  # ensure enough data for WMA windows
    # Binance klines max limit is 1000
    if data_limit > 1000:
        data_limit = 1000

    # Try candidate symbols until one works
    for cand in symbol_candidates:
        try:
            klines = client.get_klines(symbol=cand, interval=Client.KLINE_INTERVAL_1MINUTE, limit=data_limit)
            if klines and len(klines) >= data_limit:
                closes = [float(k[4]) for k in klines]
                last_close = closes[-1]
                last_kline_time = int(klines[-1][6])  # close time in ms
                actual_symbol = cand
                last_symbol = cand
                break
        except Exception:
            # Try next candidate if available
            continue

    if actual_symbol is None:
        print(json.dumps({"error": f"Insufficient data for symbol {symbol_input}"}))
        sys.exit(1)

    if closes is None or len(closes) < period:
        print(json.dumps({"error": f"Insufficient data for symbol {actual_symbol}"}))
        sys.exit(1)

    hma_latest, hma_series = compute_hma_from_closes(closes, period)
    if hma_latest is None:
        print(json.dumps({"error": f"Insufficient data to compute HMA for symbol {actual_symbol}"}))
        sys.exit(1)

    # Timestamp in ISO 8601 UTC
    timestamp_dt = datetime.utcfromtimestamp(last_kline_time / 1000.0).replace(tzinfo=timezone.utc)
    timestamp_iso = timestamp_dt.isoformat().replace('+00:00', 'Z')

    # Basic trend indicator based on HMA values
    trend = "Flat"
    if hma_series and len(hma_series) >= 2:
        if hma_series[-1] > hma_series[-2]:
            trend = "Up"
        elif hma_series[-1] < hma_series[-2]:
            trend = "Down"
        else:
            trend = "Flat"

    output = {
        "symbol": actual_symbol,
        "period": period,
        "hma": round(float(hma_latest), 2) if hma_latest is not None else None,
        "last_close": float(last_close) if last_close is not None else None,
        "timestamp": timestamp_iso,
        "trend": trend
    }

    print(json.dumps(output))


if __name__ == "__main__":
    main()