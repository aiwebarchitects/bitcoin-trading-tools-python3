#!/usr/bin/env python3
"""
Calculates the Fisher Transform on 1-minute price data from Binance to identify potential reversal points.
Usage: python fisher_transform_getter_1min.py --symbol BTC
"""

import argparse
import sys
import math
from datetime import datetime, timezone
from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceRequestException

def normalize_symbol(user_symbol: str) -> str:
    """
    Normalize the input symbol to a Binance pair.
    If the user provides a base symbol (e.g., BTC), assume BTCUSDT.
    If the user provides a pair (e.g., BTCUSDT or ETHUSDT), keep as is.
    """
    s = user_symbol.strip().upper()
    if s == "":
        return None
    # If the user provided a known pair ending, keep as is
    if s.endswith("USDT") or s.endswith("BUSD") or s.endswith("USDC"):
        return s
    # Otherwise, assume USDT pairing
    return s + "USDT"

def fetch_klines(client: Client, symbol: str, limit: int):
    """
    Fetch 1-minute klines for the given symbol.
    Returns the raw klines data or exits on error.
    """
    try:
        klines = client.get_klines(symbol=symbol, interval=Client.KLINE_INTERVAL_1MINUTE, limit=limit)
        return klines
    except (BinanceAPIException, BinanceRequestException) as e:
        print(f"Binance API error: {e}", file=sys.stderr)
        sys.exit(2)
    except Exception as e:
        print(f"Unexpected error while fetching data: {e}", file=sys.stderr)
        sys.exit(2)

def main():
    parser = argparse.ArgumentParser(description="Fisher Transform on 1-minute Binance price data.")
    parser.add_argument('--symbol', required=True, help='Trading symbol or base asset (e.g., BTC or BTCUSDT)')
    parser.add_argument('--window', type=int, default=10, help='Rolling window size in candles (default 10)')
    parser.add_argument('--limit', type=int, default=300, help='Number of candles to fetch (default 300)')
    args = parser.parse_args()

    if not isinstance(args.symbol, str) or not args.symbol.strip():
        print("Error: --symbol must be a non-empty string.", file=sys.stderr)
        sys.exit(1)

    pair_symbol = normalize_symbol(args.symbol)
    if not pair_symbol:
        print("Error: Unable to normalize symbol. Provide a valid symbol like BTC or BTCUSDT.", file=sys.stderr)
        sys.exit(1)

    # Initialize Binance client with no authentication (public endpoints)
    client = Client("", "")

    # Fetch klines
    klines = fetch_klines(client, pair_symbol, max(1, args.limit))
    if klines is None or len(klines) == 0:
        print("Error: No data returned from Binance for the given symbol.", file=sys.stderr)
        sys.exit(3)

    W = max(1, int(args.window))
    if len(klines) < W:
        print(f"Error: Insufficient data. Requested window {W} requires at least {W} candles, but received {len(klines)}.",
              file=sys.stderr)
        sys.exit(4)

    # Header for CSV-like output
    print("TIMESTAMP,SYMBOL,FISHER,SIGNAL")

    fisher_prev = 0.0
    symbol_out = pair_symbol

    # Compute Fisher Transform
    for i in range(W - 1, len(klines)):
        window = klines[i - W + 1 : i + 1]
        highs = [float(row[2]) for row in window]
        lows = [float(row[3]) for row in window]
        H_t = max(highs)
        L_t = min(lows)
        close_t = float(klines[i][4])
        ts = klines[i][0]
        dt = datetime.fromtimestamp(ts / 1000.0, tz=timezone.utc)
        timestr = dt.strftime("%Y-%m-%dT%H:%M:%SZ")

        fisher_t = fisher_prev
        signal = ""

        if H_t != L_t:
            y_t = (close_t - L_t) / (H_t - L_t)
            # clamp to avoid extreme values
            if y_t < -0.999:
                y_t = -0.999
            if y_t > 0.999:
                y_t = 0.999
            y_norm = 2.0 * y_t - 1.0
            try:
                fisher_t = 0.5 * math.log((1.0 + y_norm) / (1.0 - y_norm)) + fisher_prev
            except ValueError:
                # In case of numerical issues
                fisher_t = fisher_prev

            # Determine cross signals
            if fisher_prev < 0 and fisher_t > 0:
                signal = "CROSS_UP"
            elif fisher_prev > 0 and fisher_t < 0:
                signal = "CROSS_DOWN"
        else:
            # Degenerate window: H_t == L_t
            fisher_t = fisher_prev
            signal = ""

        print(f"{timestr},{symbol_out},{fisher_t:.6f},{signal}")
        fisher_prev = fisher_t

if __name__ == "__main__":
    main()