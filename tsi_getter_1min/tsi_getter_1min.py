#!/usr/bin/env python3
"""
Fetches current True Strength Index (TSI) for any symbol on 1-minute timeframe using Binance API
Usage: python tsi_getter_1min.py --symbol BTC
Note:
- Uses python-binance (no authentication)
- Symbol mapping: BTC -> BTCUSDT, supports BTCUSDT, ETHUSDT, etc.
- Default limit is 100, but at least p+q data points are required (p=25, q=13 => 38)
- Outputs: Symbol, Time (latest candle close time), TSI value (two decimals), and parameters p,q
"""

import argparse
import sys
from datetime import datetime
from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceRequestException

# Indicator configuration
P = 25
Q = 13

def normalize_symbol(symbol: str) -> str:
    s = symbol.strip().upper()
    if s.endswith("USDT"):
        return s
    if s.isalpha() and len(s) <= 6:
        # Assume USDT pairing for common base symbols (e.g., BTC -> BTCUSDT)
        return s + "USDT"
    return s

def ema(series, period: int):
    if not series:
        return []
    alpha = 2.0 / (period + 1.0)
    emas = [series[0]]
    for v in series[1:]:
        next_val = alpha * v + (1.0 - alpha) * emas[-1]
        emas.append(next_val)
    return emas

def fetch_klines(client: Client, symbol: str, limit: int):
    try:
        klines = client.get_klines(symbol=symbol, interval=Client.KLINE_INTERVAL_1MINUTE, limit=limit)
        if not isinstance(klines, list):
            raise ValueError("Malformed response for klines.")
        return klines
    except (BinanceAPIException, BinanceRequestException) as e:
        raise RuntimeError(f"Binance API error: {e}") from e
    except Exception as e:
        raise RuntimeError(f"Unexpected error while fetching klines: {e}") from e

def main():
    parser = argparse.ArgumentParser(description="Fetch current TSI for a symbol on 1-minute timeframe from Binance.")
    parser.add_argument('--symbol', required=True, help='Trading symbol (e.g., BTC, ETH, or BTCUSDT)')
    parser.add_argument('--limit', type=int, default=100, help='Number of 1m data points to fetch (default: 100)')
    args = parser.parse_args()

    raw_symbol = args.symbol
    limit_requested = args.limit

    # Basic validation
    if not isinstance(raw_symbol, str) or not raw_symbol.strip():
        print("Error: Invalid --symbol value.")
        sys.exit(1)

    if limit_requested is None or not isinstance(limit_requested, int) or limit_requested <= 0:
        print("Error: --limit must be a positive integer.")
        sys.exit(1)

    symbol = normalize_symbol(raw_symbol)
    client = Client("", "")

    # Ensure we have enough data: at least p+q
    min_points = P + Q
    fetch_limit = max(limit_requested, min_points)

    try:
        klines = fetch_klines(client, symbol, fetch_limit)
    except RuntimeError as e:
        print(f"Error: {e}")
        sys.exit(1)

    if not klines or len(klines) < min_points:
        print(f"Error: Insufficient data points received. Required at least {min_points}, got {len(klines)}.")
        sys.exit(1)

    # Extract closing prices and close times
    closes = []
    close_times = []
    for k in klines:
        # kline structure: [open_time, open, high, low, close, volume, close_time, ...]
        try:
            close = float(k[4])
            close_time = int(k[6])
        except (IndexError, ValueError, TypeError) as e:
            print(f"Error: Malformed kline data encountered: {e}")
            sys.exit(1)
        closes.append(close)
        close_times.append(close_time)

    if len(closes) < 2:
        print("Error: Not enough close prices to compute M series.")
        sys.exit(1)

    # Compute M[i] = close[i] - close[i-1]
    M = []
    for i in range(1, len(closes)):
        M.append(closes[i] - closes[i-1])

    M_abs = [abs(v) for v in M]

    # EMA calculations
    P1 = ema(M, P)
    P2 = ema(M_abs, P)
    T1 = ema(P1, Q)
    T2 = ema(P2, Q)

    if not T1 or not T2 or len(T1) != len(T2):
        print("Error: EMA computation produced unexpected results.")
        sys.exit(1)

    # Compute TSI = 100 * (T1 / T2)
    tsi_values = []
    for t1, t2 in zip(T1, T2):
        if t2 == 0:
            tsi = 0.0
        else:
            tsi = 100.0 * (t1 / t2)
        tsi_values.append(tsi)

    if not tsi_values:
        print("Error: No TSI values computed.")
        sys.exit(1)

    tsi_latest = tsi_values[-1]

    # Latest timestamp (close time of the latest candle)
    latest_close_time_ms = close_times[-1]
    latest_dt = datetime.fromtimestamp(latest_close_time_ms / 1000.0)
    latest_time_iso = latest_dt.isoformat(sep=' ')

    # Output
    print(f"Symbol: {symbol} | Time: {latest_time_iso} | TSI: {tsi_latest:.2f} | p={P}, q={Q}")

    # Exit successfully
    sys.exit(0)

if __name__ == "__main__":
    main()