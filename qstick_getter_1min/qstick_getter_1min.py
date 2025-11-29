#!/usr/bin/env python3
"""
Calculates Q-stick momentum oscillator using typical price and moving average on 1-minute candles
Usage: python qstick_getter_1min.py --symbol BTC
Mapping: BTC -> BTCUSDT by default
"""
import argparse
import json
import sys
from datetime import datetime, timezone
from binance.client import Client

def normalize_symbol(symbol: str) -> str:
    s = symbol.strip().upper()
    if len(s) <= 4:
        if s.endswith("USDT"):
            return s
        return s + "USDT"
    return s

def main():
    parser = argparse.ArgumentParser(description="Compute Q-stick momentum (1m) for a symbol using typical price.")
    parser.add_argument('--symbol', required=True, help='Trading symbol (e.g., BTC or BTCUSDT)')
    parser.add_argument('--n', type=int, default=14, help='SMA period for TP (default 14)')
    args = parser.parse_args()

    N = max(1, int(args.n))
    symbol_input = args.symbol

    symbol_code = normalize_symbol(symbol_input)
    # Binance free API client (no authentication)
    client = Client("", "")

    # Fetch at least N bars; add small extra margin
    EXTRA_BARS = 5
    limit = N + EXTRA_BARS

    try:
        klines = client.get_klines(symbol=symbol_code, interval="1m", limit=limit)
    except Exception as e:
        print(f"Error fetching data for symbol {symbol_code}: {e}", file=sys.stderr)
        sys.exit(2)

    if not klines or len(klines) < N:
        print(f"Insufficient data: need at least {N} 1-minute bars for symbol {symbol_code}, got {len(klines)}", file=sys.stderr)
        sys.exit(3)

    tps = []
    times = []
    for k in klines:
        try:
            high = float(k[2])
            low = float(k[3])
            close = float(k[4])
        except Exception:
            print("Error parsing OHLC data from klines response.", file=sys.stderr)
            sys.exit(4)
        tp = (high + low + close) / 3.0
        tps.append(tp)
        times.append(int(k[0]))  # open time in ms

    # Use the last N TPs for SMA
    if len(tps) < N:
        print(f"Insufficient data: computed TPs fewer than N={N}", file=sys.stderr)
        sys.exit(5)

    tp_last = tps[-1]
    sma_window = tps[-N:]
    sma_last = sum(sma_window) / N if N > 0 else 0.0

    if sma_last == 0:
        print("Division by zero avoided: SMA_TP_last is zero.", file=sys.stderr)
        sys.exit(6)

    qstick = ((tp_last - sma_last) / sma_last) * 100.0

    # Time to output
    latest_open_ms = times[-1]
    dt = datetime.fromtimestamp(latest_open_ms / 1000.0, tz=timezone.utc)
    timestr = dt.isoformat().replace("+00:00", "Z")

    output = {
        "symbol": symbol_code,
        "time": timestr,
        "qstick_1m": qstick,
        "ma_period": N
    }

    print(json.dumps(output))

if __name__ == "__main__":
    main()