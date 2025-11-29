#!/usr/bin/env python3
"""
Calculates Force Index (price change × volume) to gauge buying vs selling pressure on 1-minute candles for a given symbol.
Usage: python force_index_getter_1min.py --symbol BTC
Tips:
  - By default, if you pass a symbol like BTC, the script will attempt to use BTCUSDT.
  - You can override the candle count with --limit (default 200).
  - Use --series to print the full FI series in a JSON-like structure for scripting.
"""
import argparse
import sys
import json
from datetime import datetime
from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceRequestException

def ms_to_iso(ms: int) -> str:
    try:
        dt = datetime.utcfromtimestamp(ms / 1000.0)
        return dt.isoformat() + "Z"
    except Exception:
        return str(ms)

def fetch_force_index(symbol: str, limit: int):
    client = Client("", "")
    try:
        klines = client.get_klines(symbol=symbol, interval=Client.KLINE_INTERVAL_1MINUTE, limit=limit)
    except (BinanceAPIException, BinanceRequestException) as e:
        raise RuntimeError(f"Binance API error: {e}")
    except Exception as e:
        raise RuntimeError(f"Network/HTTP error: {e}")

    if not klines or len(klines) < 2:
        raise RuntimeError("Insufficient candle data received (need at least 2 1m candles).")

    fi_series = []
    for i in range(1, len(klines)):
        prev_close = klines[i-1][4]
        curr_close = klines[i][4]
        volume = klines[i][5]

        try:
            prev_close_f = float(prev_close)
            curr_close_f = float(curr_close)
            volume_f = float(volume)
        except Exception:
            raise RuntimeError("Non-numeric data encountered in OHLCV fields.")

        if volume_f <= 0:
            raise RuntimeError("Non-positive volume encountered in data; cannot compute FI.")

        if curr_close_f is None or prev_close_f is None:
            raise RuntimeError("Missing close price data for FI computation.")

        fi_value = (curr_close_f - prev_close_f) * volume_f
        timestamp_close = klines[i][6]  # close time in ms
        if timestamp_close is None:
            raise RuntimeError("Missing timestamp for FI data point.")

        fi_series.append({"timestamp": int(timestamp_close), "fi": float(fi_value)})

    return {
        "symbol": symbol,
        "interval": "1m",
        "limit": len(klines),
        "fi_series": fi_series
    }

def main():
    parser = argparse.ArgumentParser(description="Calculate Force Index (price change × volume) on 1-minute candles.")
    parser.add_argument('--symbol', required=True, help='Trading symbol (e.g., BTC, BTCUSDT)')
    parser.add_argument('--limit', type=int, default=200, help='Number of 1-minute candles to fetch (default 200)')
    parser.add_argument('--series', action='store_true', help='Print full FI series as JSON-like structure')
    args = parser.parse_args()

    # Normalize symbol: if no known suffix, append USDT by default
    sym = args.symbol.strip().upper()
    known_suffixes = ('USDT', 'USDC', 'BUSD', 'TUSD', 'USD')
    if not any(sym.endswith(suf) for suf in known_suffixes):
        symbol = sym + 'USDT'
    else:
        symbol = sym

    limit = max(2, int(args.limit))

    try:
        result = fetch_force_index(symbol, limit)
        fi_series = result.get("fi_series", [])
        if not fi_series:
            print("Error: FI series is empty after calculation.", file=sys.stderr)
            sys.exit(1)

        latest = fi_series[-1]
        latest_fi = latest["fi"]
        latest_ts = latest["timestamp"]

        print(f"Latest FI: {latest_fi} at {ms_to_iso(latest_ts)}")

        if args.series:
            output = {
                "symbol": result.get("symbol", symbol),
                "interval": result.get("interval", "1m"),
                "limit": result.get("limit", limit),
                "series": [
                    {"timestamp": item["timestamp"], "fi": item["fi"]} for item in fi_series
                ]
            }
            print(json.dumps(output, indent=2))
    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()