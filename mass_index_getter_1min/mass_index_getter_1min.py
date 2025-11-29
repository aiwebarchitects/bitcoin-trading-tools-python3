#!/usr/bin/env python3
"""
Calculates Mass Index to gauge volatility and potential breakouts on 1-minute candles using EMA of the high-low range

Usage:
    python mass_index_getter_1min.py --symbol BTC
    # The script will default to pairing with USDT (BTCUSDT)

Algorithm:
- Retrieve at least 200 one-minute OHLC candles for the given symbol (paired with USDT if needed)
- For each candle, compute R_t = High_t - Low_t
- Compute two EMAs on R_t: fast_n=9 and slow_n=26 with alpha = 2/(N+1)
- MassIndex_t = EMA_fast_t / EMA_slow_t
- Print the latest Mass Index along with FastEMA and SlowEMA values
- Also emit a compact JSON object for programmatic usage

Notes:
- Uses python-binance (no authentication)
- CLI: --symbol (required)
- Internal lookbacks are fixed (fast_n=9, slow_n=26)
- Data window: >= 200 bars
"""

import argparse
import sys
import json
import math
from datetime import datetime
from binance.client import Client

def compute_ema(series, window):
    """
    Compute EMA for a given series and window.
    alpha = 2 / (window + 1)
    Returns a list of EMA values of same length as input series.
    """
    if not series or window <= 0:
        return []
    alpha = 2.0 / (window + 1)
    emas = [series[0]]
    for v in series[1:]:
        emas.append(alpha * v + (1 - alpha) * emas[-1])
    return emas

def main():
    parser = argparse.ArgumentParser(description="Mass Index on 1-minute candles (EMA of high-low range)")
    parser.add_argument('--symbol', required=True, help='Trading symbol base asset (e.g., BTC). Pair will be constructed as BTCUSDT if not provided with USDT.')
    args = parser.parse_args()

    base = args.symbol.strip().upper()
    if not base:
        print("Error: --symbol must be provided and non-empty.", file=sys.stderr)
        sys.exit(2)

    # Determine trading pair
    if base.endswith("USDT"):
        pair = base
    else:
        pair = f"{base}USDT"

    # Binance client (no API key required for public endpoints)
    client = Client("", "")

    try:
        klines = client.get_klines(symbol=pair, interval=Client.KLINE_INTERVAL_1MINUTE, limit=200)
    except Exception as e:
        print(f"Error retrieving klines for {pair}: {e}", file=sys.stderr)
        sys.exit(3)

    # Build valid data: time and high-low range
    times_ms = []
    ranges = []
    invalid_count = 0
    for kline in klines:
        try:
            open_time = int(kline[0])
            high = float(kline[2])
            low = float(kline[3])
            if high <= low:
                invalid_count += 1
                continue
            r = high - low
            times_ms.append(open_time)
            ranges.append(r)
        except Exception:
            invalid_count += 1
            continue

    if len(ranges) == 0:
        print("Error: No valid OHLC data available after parsing klines.", file=sys.stderr)
        sys.exit(4)

    if len(ranges) < 26:
        print(f"Error: Not enough data points to initialize EMAs (have {len(ranges)}, need at least 26).", file=sys.stderr)
        sys.exit(4)

    fast_n = 9
    slow_n = 26

    fast_ema = compute_ema(ranges, fast_n)
    slow_ema = compute_ema(ranges, slow_n)

    last_idx = len(ranges) - 1
    last_fast = fast_ema[last_idx]
    last_slow = slow_ema[last_idx]

    # Avoid division by zero
    if last_slow == 0:
        mass_val = float('nan')
    else:
        mass_val = last_fast / last_slow

    # Time formatting
    t_last = times_ms[last_idx]
    dt = datetime.utcfromtimestamp(t_last / 1000.0)
    time_str = dt.strftime('%Y-%m-%d %H:%M:%S')
    time_iso = dt.strftime('%Y-%m-%dT%H:%M:%SZ')

    mass_str = f"{mass_val:.4f}" if not math.isnan(mass_val) else "NaN"

    # Output human-readable line
    print(f"Symbol: {pair} | Time: {time_str} | MassIndex: {mass_str} | FastEMA(R) (9): {last_fast:.3f} | SlowEMA(R) (26): {last_slow:.3f}")

    # Output JSON for programmatic use
    mass_json = None if math.isnan(mass_val) else mass_val
    json_out = {
        "symbol": pair,
        "time": time_iso,
        "mass_index": mass_json,
        "fast_ema": last_fast,
        "slow_ema": last_slow
    }
    print(json.dumps(json_out))

if __name__ == "__main__":
    main()