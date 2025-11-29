#!/usr/bin/env python3
"""
Gets current Rate of Change (ROC) for any symbol on 1min timeframe
Usage: python roc_getter_1min.py --symbol BTC

Notes:
- Uses Binance free API (no authentication)
- Tries common symbol formats (e.g., BTC -> BTCUSDT) if the exact symbol is invalid
- ROC_PERIOD defaults to 10 (can be overridden with --roc_period if desired)
- Output: "Symbol: SYMBOL | ROC_1m (period=ROC_PERIOD): value% (as of TIMESTAMP)"
"""

import argparse
import datetime
import sys
from binance.client import Client


ROC_PERIOD_DEFAULT = 10
CLI_INTERVAL = '1m'


def get_roc_for_symbol(client: Client, input_symbol: str, roc_period: int):
    """
    Attempts to fetch ROC data for the given symbol and ROC period.
    Tries a set of common symbol variants if the initial symbol is invalid.
    Returns a tuple: (resolved_symbol, roc_value, timestamp_str)
    """
    if not input_symbol:
        raise ValueError("Symbol is empty. Please provide a valid symbol (e.g., BTC).")

    base = input_symbol.strip().upper()
    candidates = []

    # Build a small set of likely symbol representations
    candidates.append(base)
    candidates.append(base + "USDT")
    candidates.append(base + "USDC")
    candidates.append(base + "BUSD")

    # Remove duplicates while preserving order
    seen = set()
    candidates_unique = []
    for c in candidates:
        if c not in seen:
            seen.add(c)
            candidates_unique.append(c)

    last_error = None

    limit = roc_period + 1
    for symbol in candidates_unique:
        try:
            klines = client.get_klines(symbol=symbol, interval=CLI_INTERVAL, limit=limit)
        except Exception as e:
            last_error = e
            continue

        if not klines or len(klines) < limit:
            # Insufficient data for this symbol variant
            last_error = ValueError(
                f"Insufficient data for symbol '{symbol}': needed {limit} bars, got {len(klines) if klines else 0}."
            )
            continue

        try:
            closes = [float(k[4]) for k in klines]
        except Exception:
            last_error = ValueError(
                f"Non-numeric price data encountered for symbol '{symbol}'."
            )
            continue

        prior_close = closes[-limit]
        current_close = closes[-1]

        if prior_close == 0:
            last_error = ValueError(
                f"Division by zero in ROC calculation for symbol '{symbol}' (prior_close is 0)."
            )
            continue

        roc = ((current_close - prior_close) / prior_close) * 100.0

        # Timestamp for the latest close (Open time of last kline)
        try:
            ts = datetime.datetime.fromtimestamp(klines[-1][0] / 1000.0)
            ts_str = ts.strftime("%Y-%m-%d %H:%M:%S")
        except Exception:
            ts_str = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

        return symbol, roc, ts_str

    # If we reach here, no symbol variant worked
    if last_error:
        raise last_error
    else:
        raise ValueError("Failed to fetch ROC data for the provided symbol.")


def main():
    parser = argparse.ArgumentParser(description="Get current ROC (1m) for a symbol using Binance API.")
    parser.add_argument('--symbol', required=True, help='Trading symbol (e.g., BTC, ETH). If needed, BTC will default to BTCUSDT.')
    parser.add_argument('--roc_period', type=int, default=ROC_PERIOD_DEFAULT, help=f'ROC period in minutes/bars (default={ROC_PERIOD_DEFAULT})')
    args = parser.parse_args()

    symbol_input = args.symbol
    roc_period = args.roc_period

    # Binance client with no authentication
    client = Client("", "")

    try:
        resolved_symbol, roc_value, timestamp_str = get_roc_for_symbol(client, symbol_input, roc_period)
        # Print human-friendly output
        print(f"Symbol: {resolved_symbol} | ROC_1m (period={roc_period}): {roc_value:.2f}% (as of {timestamp_str})")
        sys.exit(0)
    except Exception as e:
        # Print descriptive error and suggested action
        print(f"ERROR: {e}")
        print("Action: verify the symbol is valid on Binance (e.g., BTCUSDT), ensure network access, and try again with sufficient data.")
        sys.exit(1)


if __name__ == "__main__":
    main()