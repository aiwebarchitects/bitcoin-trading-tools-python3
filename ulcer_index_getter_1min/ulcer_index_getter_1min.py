#!/usr/bin/env python3
"""
Computes Ulcer Index (UI) using Binance 1-minute close data over a 14-period window
Usage: python ulcer_index_getter_1min.py --symbol BTC
"""
import argparse
import sys
import json
import datetime
from math import sqrt
from binance.client import Client

def compute_ui(closes):
    if not closes or len(closes) < 14:
        raise ValueError("Not enough close data points to compute UI (need 14).")

    peak = max(closes)
    # Protect against division by zero
    if peak == 0:
        dd = [0.0 for _ in closes]
    else:
        dd = [(peak - c) / peak for c in closes]

    sum_sq = sum(d * d for d in dd)
    ui = sqrt(sum_sq / 14.0)
    return ui, peak

def main():
    parser = argparse.ArgumentParser(description="Compute Ulcer Index (UI) from Binance 1-minute closes over a 14-period window.")
    parser.add_argument('--symbol', required=True, help='Trading symbol (e.g., BTCUSDT)')
    args = parser.parse_args()

    symbol = args.symbol.upper()

    # Initialize Binance client (unauthenticated)
    client = Client("", "")

    try:
        klines = client.get_klines(symbol=symbol, interval='1m', limit=14)
    except Exception as e:
        print(f"Error: Failed to retrieve klines for symbol {symbol}: {e}", file=sys.stderr)
        sys.exit(1)

    if not isinstance(klines, list) or len(klines) < 14:
        print(f"Error: Expected 14 klines for symbol {symbol}, received {len(klines) if isinstance(klines, list) else 'unknown'}.", file=sys.stderr)
        sys.exit(1)

    closes = []
    for idx, k in enumerate(klines):
        try:
            closes.append(float(k[4]))
        except Exception:
            print(f"Error: Non-numeric close value encountered at index {idx} for symbol {symbol}.", file=sys.stderr)
            sys.exit(1)

    if len(closes) != 14:
        print(f"Error: Expected 14 close data points, got {len(closes)}.", file=sys.stderr)
        sys.exit(1)

    try:
        ui, peak = compute_ui(closes)
    except Exception as e:
        print(f"Error: Failed to compute UI: {e}", file=sys.stderr)
        sys.exit(1)

    # Timestamp in ISO-8601 (UTC)
    timestamp = datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

    # Human-friendly output
    print(f"Symbol: {symbol}")
    print(f"UI_14m: {ui:.8f}")
    print(f"Last_Close: {closes[-1]:.8f}")
    print(f"Peak_in_Window: {peak:.8f}")

    # Machine-friendly JSON line
    payload = {
        "symbol": symbol,
        "ui_14": round(ui, 8),
        "last_close": closes[-1],
        "peak": peak,
        "window": 14,
        "timestamp": timestamp
    }
    print(json.dumps(payload))

if __name__ == "__main__":
    main()