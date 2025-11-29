#!/usr/bin/env python3
"""
Detects significant one-minute volume spikes by comparing current volume to a 20-period moving average
Usage: python volume_spike_detector_1min.py --symbol BTC
"""

import argparse
import json
import sys
import datetime
from binance.client import Client

def resolve_symbol(symbol_arg: str) -> str:
    s = symbol_arg.strip().upper()
    if not s:
        return ""
    if s.endswith("USDT"):
        return s
    else:
        return s + "USDT"

def handle_error(message: str, code: int = None):
    err = {"error": message}
    if code is not None:
        err["code"] = code
    sys.stderr.write(json.dumps(err) + "\n")
    sys.exit(1)

def main():
    parser = argparse.ArgumentParser(
        description="Detects significant one-minute volume spikes against a 20-period MA of volume."
    )
    parser.add_argument("--symbol", required=True, help="Trading symbol (e.g., BTC). The script maps to BTCUSDT.")
    parser.add_argument("--threshold", type=float, default=2.0, help="Spike threshold ratio (default 2.0)")
    parser.add_argument("--datasource", default="binance", help="Data source (default: binance)")
    args = parser.parse_args()

    symbol_pair = resolve_symbol(args.symbol)
    if not symbol_pair:
        handle_error("Missing or invalid --symbol parameter.")

    threshold = args.threshold if args.threshold is not None else 2.0
    datasource = args.datasource  # currently unused; accepted for CLI compatibility

    client = Client("", "")

    try:
        klines = client.get_klines(symbol=symbol_pair, interval=Client.KLINE_INTERVAL_1MINUTE, limit=21)
    except Exception as e:
        handle_error(f"Data fetch error for symbol {symbol_pair}: {str(e)}")

    if not isinstance(klines, list) or len(klines) < 21:
        handle_error(
            f"Insufficient data: expected 21 one-minute bars, received {len(klines) if isinstance(klines, list) else 'N/A'}."
        )

    try:
        volumes = [float(k[5]) for k in klines]  # volume is at index 5
        close_time_ms = int(klines[-1][6])     # close time is at index 6
    except Exception as e:
        handle_error(f"Unexpected data format: parsing klines failed ({str(e)}).")

    ma20 = sum(volumes[0:20]) / 20 if len(volumes) >= 20 else 0.0
    current_vol = volumes[20] if len(volumes) > 20 else 0.0

    if ma20 > 0:
        ratio = current_vol / ma20
        spike = ratio >= threshold
    else:
        ratio = 0.0
        spike = False

    dt = datetime.datetime.utcfromtimestamp(close_time_ms / 1000.0)
    timestamp = dt.strftime("%Y-%m-%dT%H:%M:%SZ")

    output = {
        "symbol": symbol_pair,
        "timestamp": timestamp,
        "volume_current": current_vol,
        "ma20": ma20,
        "ratio": ratio,
        "spike": bool(spike),
        "threshold": threshold
    }

    print(json.dumps(output))

if __name__ == "__main__":
    main()