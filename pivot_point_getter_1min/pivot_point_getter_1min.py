#!/usr/bin/env python3
"""
Calculates standard intraday pivot points (PP, S1, S2, R1, R2) from 1-minute Binance price data for a given symbol.
Usage: python pivot_point_getter_1min.py --symbol BTCUSDT

Notes:
- Data retrieval uses UTC. The script fetches the previous calendar day in UTC and computes OHLC
  (PrevHigh, PrevLow, PrevClose) from that day to calculate standard intraday pivot points.
- Symbol handling is flexible: if you pass BTC, it will assume BTCUSDT as the pair.
- Requires python-binance (Banking free API, no authentication).

Example:
python pivot_point_getter_1min.py --symbol BTC
"""
import argparse
import sys
import datetime
from binance.client import Client
from binance.exceptions import BinanceAPIException

def normalize_symbol(symbol_input: str) -> str:
    """
    Normalize the symbol input to a valid Binance trading pair.
    If the input does not contain an exchange pair (e.g., USDT/BUSD), default to USDT pair.
    """
    s = symbol_input.strip().upper()
    if "USDT" not in s and "BUSD" not in s and "USD" not in s:
        s = s + "USDT"
    return s

def main():
    parser = argparse.ArgumentParser(description="Compute standard intraday pivot points from 1-minute Binance data for a given symbol (UTC).")
    parser.add_argument('--symbol', required=True, help='Trading symbol (e.g., BTCUSDT or BTC). The script will default to the USDT pair if missing.')
    args = parser.parse_args()

    symbol_input = args.symbol
    symbol_pair = normalize_symbol(symbol_input)

    # Time window: previous calendar day in UTC
    now_utc = datetime.datetime.utcnow()
    prev_date = (now_utc).date() - datetime.timedelta(days=1)
    start_prev = datetime.datetime(prev_date.year, prev_date.month, prev_date.day, 0, 0, 0, tzinfo=datetime.timezone.utc)
    end_prev = start_prev + datetime.timedelta(days=1)

    try:
        client = Client("", "")

        # Fetch 1-minute klines for the previous day only
        klines = client.get_klines(
            symbol=symbol_pair,
            interval=Client.KLINE_INTERVAL_1MINUTE,
            start_str=start_prev.strftime("%Y-%m-%d %H:%M:%S"),
            end_str=end_prev.strftime("%Y-%m-%d %H:%M:%S")
        )

        if not isinstance(klines, list) or len(klines) == 0:
            print(f"Error: No data returned for previous day for symbol {symbol_pair}.", file=sys.stderr)
            sys.exit(1)

        # Expect 1440 candles for a complete UTC day
        EXPECTED_CANDLES = 24 * 60  # 1440
        if len(klines) < EXPECTED_CANDLES:
            print(f"Error: Incomplete data for previous day. Expected {EXPECTED_CANDLES} candles, got {len(klines)}.", file=sys.stderr)
            sys.exit(1)

        if len(klines) > EXPECTED_CANDLES:
            klines = klines[:EXPECTED_CANDLES]

        # OHLC for the previous day
        prev_high = max(float(k[2]) for k in klines)
        prev_low = min(float(k[3]) for k in klines)
        prev_close = float(klines[-1][4])

        # Pivot calculations
        pp = (prev_high + prev_low + prev_close) / 3.0
        r1 = 2.0 * pp - prev_low
        r2 = pp + (prev_high - prev_low)
        s1 = 2.0 * pp - prev_high
        s2 = pp - (prev_high - prev_low)

        # Output
        print(f"Symbol: {symbol_pair}")
        print(f"Date: {start_prev.date().isoformat()} (previous day)")
        print(f"PP: {pp:.6f}")
        print(f"R1: {r1:.6f}")
        print(f"R2: {r2:.6f}")
        print(f"S1: {s1:.6f}")
        print(f"S2: {s2:.6f}")

    except BinanceAPIException as e:
        print(f"Binance API error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()