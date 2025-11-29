#!/usr/bin/env python3
"""
Calculates the Momentum (Rate of Change) for any symbol on a 1-minute timeframe using Binance data
Usage: python momentum_getter_1min.py --symbol BTC
- Data retrieval: Binance REST API (no authentication)
- Lookback window: LOOKBACK_N = 10 (default)
- ROC = ((close_today - close_n) / close_n) * 100
- Output: SYMBOL | Momentum 1m (n=10) = XX.XX% as of TIMESTAMP UTC
- Robustness: handles missing data, non-numeric data, HTTP errors, and rate limits with retries

Notes:
- If a user passes a base symbol like BTC, the script will attempt to use BTCUSDT as the trading pair.
  If the user passes BTCUSDT, it will use BTCUSDT as is.
"""

import argparse
import sys
import time
from datetime import datetime
from binance.client import Client

# Configuration
LOOKBACK_N = 10  # number of candles to look back
MAX_RETRIES = 5
BASE_BACKOFF_SEC = 2  # backoff seconds for retries

def construct_pair(symbol_input: str) -> str:
    """Constructs a trading pair for Binance from a given input.
    If input ends with USDT, use as is; otherwise append USDT.
    """
    sym = symbol_input.strip().upper().replace(" ", "")
    if sym.endswith("USDT"):
        return sym
    return f"{sym}USDT"

def fetch_klines_with_retries(client: Client, symbol: str, limit: int):
    """Fetch klines with simple retry/backoff on failures."""
    attempt = 0
    while True:
        try:
            klines = client.get_klines(symbol=symbol, interval=Client.KLINE_INTERVAL_1MINUTE, limit=limit)
            return klines
        except Exception as e:
            attempt += 1
            if attempt > MAX_RETRIES:
                raise
            backoff = BASE_BACKOFF_SEC * attempt
            print(f"Warning: Failed to fetch klines for {symbol} (attempt {attempt}/{MAX_RETRIES}): {e}", file=sys.stderr)
            print(f"Retrying in {backoff} seconds...", file=sys.stderr)
            time.sleep(backoff)

def main():
    parser = argparse.ArgumentParser(description="Calculate Momentum (ROC) on 1-minute candles from Binance.")
    parser.add_argument('--symbol', required=True, help='Trading symbol or base symbol (e.g., BTC or BTCUSDT)')
    args = parser.parse_args()

    symbol_input = args.symbol
    pair = construct_pair(symbol_input)

    # Initialize Binance client (free API, no authentication)
    client = Client("", "")

    # Fetch lookback_n + 1 candles
    limit_needed = LOOKBACK_N + 1
    try:
        klines = fetch_klines_with_retries(client, pair, limit_needed)
    except Exception as e:
        print(f"Fatal: Unable to fetch klines for {pair}. Error: {e}", file=sys.stderr)
        sys.exit(1)

    if klines is None or len(klines) < limit_needed:
        print(f"Fatal: Expected at least {limit_needed} klines for {pair}, but received {len(klines) if klines else 0}.", file=sys.stderr)
        sys.exit(1)

    # Extract closes and validate data
    closes = []
    try:
        for idx, k in enumerate(klines):
            # k is a list: [ OpenTime, Open, High, Low, Close, Volume, CloseTime, ... ]
            close_str = k[4]
            close_val = float(close_str)
            closes.append(close_val)
        # Ensure numeric data integrity
        if any(v != v for v in closes):  # NaN check
            raise ValueError("Non-numeric close data encountered.")
    except Exception as e:
        print(f"Fatal: Non-numeric or invalid close data encountered: {e}", file=sys.stderr)
        sys.exit(1)

    close_today = closes[-1]
    close_n = closes[-(LOOKBACK_N + 1)]

    if close_n == 0:
        print(f"Fatal: Cannot compute ROC because the lookback close value is zero for {pair}.", file=sys.stderr)
        sys.exit(1)

    roc = ((close_today - close_n) / close_n) * 100.0

    # Timestamp for the latest candle (close_time of the last kline)
    try:
        close_time_ms = klines[-1][6]
        dt = datetime.utcfromtimestamp(close_time_ms / 1000.0)
        timestamp_str = dt.strftime('%Y-%m-%d %H:%M:%S')
    except Exception as e:
        print(f"Warning: Could not parse timestamp from klines: {e}. Falling back to current UTC time.", file=sys.stderr)
        timestamp_str = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

    # Output
    print(f"{pair} | Momentum 1m (n={LOOKBACK_N}) = {roc:.2f}% as of {timestamp_str} UTC")

if __name__ == "__main__":
    main()