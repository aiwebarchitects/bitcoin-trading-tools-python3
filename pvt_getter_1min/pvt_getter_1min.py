#!/usr/bin/env python3
"""
Calculates Price-Volume Trend (PVT) for any symbol on 1min timeframe
Usage: python pvt_getter_1min.py --symbol BTC
Notes:
- Symbol is normalized to a Binance pair (e.g., BTC -> BTCUSDT)
- Fetches last 200 1-minute bars from Binance (no API key required)
- Outputs a JSON time-series and a concise latest value line
"""

import argparse
import json
import sys
from datetime import datetime
import math

from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceRequestException

def normalize_pair(symbol: str) -> str:
    s = symbol.strip().upper()
    if s.endswith("USDT"):
        return s
    return f"{s}USDT"

def fetch_klines(client: Client, pair: str, limit: int = 200):
    try:
        klines = client.get_klines(symbol=pair, interval=Client.KLINE_INTERVAL_1MINUTE, limit=limit)
        if not klines or len(klines) < 2:
            raise ValueError("Insufficient data: need at least 2 bars.")
        times = [int(k[0]) for k in klines]
        closes = [float(k[4]) for k in klines]
        volumes = [float(k[5]) for k in klines]
        return times, closes, volumes
    except BinanceAPIException as e:
        raise RuntimeError(f"Binance API error: {e}") from e
    except BinanceRequestException as e:
        raise RuntimeError(f"Binance request error: {e}") from e
    except Exception as e:
        raise RuntimeError(f"Data fetch error: {e}") from e

def compute_pvt(times, closes, volumes):
    n = len(closes)
    if n < 2:
        raise ValueError("Need at least 2 bars to compute PVT.")
    pvt = [0.0] * n
    for i in range(1, n):
        delta = closes[i] - closes[i - 1]
        prev_close = closes[i - 1]
        if prev_close != 0.0:
            pct_change = delta / prev_close
        else:
            pct_change = 0.0  # avoid division by zero
        pvt[i] = pvt[i - 1] + volumes[i] * pct_change
    return pvt

def main():
    parser = argparse.ArgumentParser(description="Calculate Price-Volume Trend (PVT) for a symbol on 1m timeframe.")
    parser.add_argument('--symbol', required=True, help='Trading symbol base (e.g., BTC, ETH) or pair with USDT (e.g., BTCUSDT)')
    args = parser.parse_args()

    pair = None
    try:
        pair = normalize_pair(args.symbol)
    except Exception as e:
        print(f"Error normalizing symbol '{args.symbol}': {e}", file=sys.stderr)
        sys.exit(1)

    client = Client("", "")

    try:
        times, closes, volumes = fetch_klines(client, pair, limit=200)
    except Exception as e:
        print(f"Error fetching data for {pair}: {e}", file=sys.stderr)
        sys.exit(2)

    try:
        pvt = compute_pvt(times, closes, volumes)
    except Exception as e:
        print(f"Error computing PVT: {e}", file=sys.stderr)
        sys.exit(3)

    # Validate data for NaN/Inf
    if not all(isinstance(v, (int, float)) and math.isfinite(v) for v in pvt):
        print("Data contains non-finite values in PVT computation.", file=sys.stderr)
        sys.exit(4)

    pvt_series = [{"t": int(ts), "pvt": float(p)} for ts, p in zip(times, pvt)]
    output = {"symbol": pair, "interval": "1m", "pvt": pvt_series}

    try:
        print(json.dumps(output))
    except Exception as e:
        print(f"Error producing JSON output: {e}", file=sys.stderr)
        sys.exit(5)

    latest_ts = times[-1]
    latest_pvt = pvt[-1]
    ts_iso = datetime.utcfromtimestamp(latest_ts / 1000.0).strftime('%Y-%m-%d %H:%M:%S')
    print(f"Latest PVT for {pair} at {ts_iso}: {latest_pvt}")

if __name__ == "__main__":
    main()