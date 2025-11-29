#!/usr/bin/env python3
"""
Gets current Parabolic SAR for any symbol on 1min timeframe
Usage: python parabolic_sar_getter_1min.py --symbol BTCUSDT --limit 500
"""
import argparse
import json
import sys
from datetime import datetime

from binance.client import Client
from binance.exceptions import BinanceAPIException


def compute_parabolic_sar(highs, lows, closes, af_start=0.02, af_increment=0.02, af_max=0.20):
    """
    Compute Parabolic SAR for a series of candles.
    highs, lows, closes: lists of floats of equal length
    Returns (sar_value, trend) for the last candle
    """
    n = len(highs)
    if n < 2:
        return None, None

    # Initialize trend, SAR, EP depending on first movement
    if closes[1] > closes[0]:
        sar = min(lows[0], lows[1])
        trend = "up"
        ep = max(highs[0], highs[1])
    else:
        sar = max(highs[0], highs[1])
        trend = "down"
        ep = min(lows[0], lows[1])

    af = af_start

    for i in range(2, n):
        if trend == "up":
            sar_next = sar + af * (ep - sar)
            # If SAR crosses above the current low, switch to down
            if sar_next > lows[i]:
                sar = lows[i]
                trend = "down"
                ep = lows[i]
                af = af_start
            else:
                sar = sar_next
                # Update EP if new high
                if highs[i] > ep:
                    ep = highs[i]
                    af = min(af + af_increment, af_max)
        else:  # trend == "down"
            sar_next = sar + af * (ep - sar)
            # If SAR crosses below the current high, switch to up
            if sar_next < highs[i]:
                sar = highs[i]
                trend = "up"
                ep = highs[i]
                af = af_start
            else:
                sar = sar_next
                # Update EP if new low
                if lows[i] < ep:
                    ep = lows[i]
                    af = min(af + af_increment, af_max)

    return sar, trend


def main():
    parser = argparse.ArgumentParser(description="Parabolic SAR getter for 1-minute candles using Binance API.")
    parser.add_argument('--symbol', required=True, help='Trading symbol (e.g., BTCUSDT)')
    parser.add_argument('--limit', type=int, default=500, help='Number of candles to fetch (default 500)')
    args = parser.parse_args()

    symbol = (args.symbol or "").strip().upper()
    if not symbol:
        print("ERROR: Invalid symbol")
        sys.exit(2)

    limit = args.limit if args.limit and args.limit > 1 else 500
    # Binance get_klines requires a valid symbol; use free API with no authentication
    client = Client("", "")

    try:
        klines = client.get_klines(symbol=symbol, interval=Client.KLINE_INTERVAL_1MINUTE, limit=limit)
    except BinanceAPIException as e:
        # Provide more specific error messages if possible
        msg = str(e)
        if "Invalid symbol" in msg or "Unknown symbol" in msg:
            print("ERROR: Invalid symbol")
        else:
            print("ERROR: Data fetch failed")
        sys.exit(2)
    except Exception:
        print("ERROR: Data fetch failed")
        sys.exit(2)

    if not klines or len(klines) < 2:
        print("ERROR: Insufficient data")
        sys.exit(2)

    highs = [float(k[2]) for k in klines]
    lows = [float(k[3]) for k in klines]
    closes = [float(k[4]) for k in klines]
    times = [int(k[6]) for k in klines]  # close times in ms

    sar_value, trend = compute_parabolic_sar(highs, lows, closes)
    if sar_value is None or trend not in ("up", "down"):
        print("ERROR: Insufficient data")
        sys.exit(2)

    last_ts_ms = times[-1]
    dt = datetime.utcfromtimestamp(last_ts_ms / 1000.0)
    timestamp_iso = dt.strftime("%Y-%m-%dT%H:%M:%SZ")

    output = {
        "symbol": symbol,
        "timeframe": "1m",
        "sar": float(f"{sar_value:.2f}"),
        "trend": trend,
        "timestamp": timestamp_iso
    }

    print(json.dumps(output))


if __name__ == "__main__":
    main()