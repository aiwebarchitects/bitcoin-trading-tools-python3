#!/usr/bin/env python3
"""
Tracks Binance funding rate for the given symbol on 1-minute intervals to gauge funding pressure and potential price stress.
Usage: python funding_rate_tracker_1min.py --symbol BTC
Notes:
- Uses python-binance (from binance.client import Client)
- No API key required for fetching funding rate (uses free endpoints)
- Outputs one line per minute with timestamp, funding rate (percent), delta (percent), and trend
- Handles errors gracefully and continues running
"""

import argparse
import datetime
import re
import sys
import time

from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceRequestException


def is_valid_symbol_input(s: str) -> bool:
    """Validate input symbol: 3-12 alphanumeric characters (A-Z, 0-9)."""
    return bool(re.fullmatch(r"[A-Z0-9]{3,12}", s))


def format_rate_percent(rate_decimal: float) -> str:
    """Format decimal rate to percent string with 6 decimals, e.g., 0.0001 -> 0.010000%."""
    return f"{rate_decimal * 100:.6f}%"


def main():
    parser = argparse.ArgumentParser(
        description="Track Binance perpetual funding rate for a given symbol on 1-minute intervals."
    )
    parser.add_argument(
        "--symbol",
        required=True,
        help="Trading symbol (e.g., BTC or BTCUSDT). If a short symbol is provided, it will be appended with USDT (e.g., BTC -> BTCUSDT).",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.00001,
        help="Minimal delta threshold (in decimal terms, e.g., 0.00001) to consider as trend change.",
    )
    args = parser.parse_args()

    raw_symbol = args.symbol.strip().upper()
    if not is_valid_symbol_input(raw_symbol):
        print(
            f"Error: invalid symbol '{args.symbol}'. Expected 3-12 alphanumeric characters (e.g., BTC, ETH, BTCUSDT).",
            file=sys.stderr,
        )
        sys.exit(2)

    # Normalize symbol for Binance: ensure it ends with USDT if not already
    symbol = raw_symbol if raw_symbol.endswith("USDT") else raw_symbol + "USDT"

    # Initialize Binance client (no API key needed for this endpoint)
    client = Client("", "")

    previous_rate = None  # in decimal terms (e.g., 0.0001)
    threshold = float(args.threshold)

    print(f"Starting funding rate tracker for symbol: {symbol}. Press Ctrl+C to exit.", flush=True)

    while True:
        try:
            # Fetch the most recent funding rate data point
            # Endpoint: GET /fapi/v1/fundingRate?symbol=BTCUSDT&limit=1
            data = client.futures_funding_rate(symbol=symbol, limit=1)

            if not isinstance(data, list) or len(data) == 0:
                print(
                    f"[{datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC] WARNING: No funding rate data returned for {symbol}. Retrying in 60s.",
                    file=sys.stderr,
                    flush=True,
                )
                time.sleep(60)
                continue

            item = data[0]
            funding_rate_str = item.get("fundingRate")
            if funding_rate_str is None:
                print(
                    f"[{datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC] WARNING: Missing 'fundingRate' field for {symbol}. Retrying in 60s.",
                    file=sys.stderr,
                    flush=True,
                )
                time.sleep(60)
                continue

            # Binance returns fundingRate as string like "0.00010000"
            current_rate = float(funding_rate_str)

            now_utc = datetime.datetime.utcnow()
            timestamp_str = now_utc.strftime("%Y-%m-%d %H:%M:%S")

            if previous_rate is None:
                delta_decimal = 0.0
                trend = "Neutral"
                delta_pct_str = "+0.000000%"
            else:
                delta_decimal = current_rate - previous_rate
                if delta_decimal > threshold:
                    trend = "Rising"
                elif delta_decimal < -threshold:
                    trend = "Falling"
                else:
                    trend = "Neutral"
                delta_pct = delta_decimal * 100
                delta_pct_str = f"{delta_pct:+.6f}%"

            rate_pct = current_rate * 100
            rate_pct_str = f"{rate_pct:.6f}%"

            # First sample handling (previous_rate is None) -> delta 0 and Neutral
            if previous_rate is None:
                delta_pct_str = "+0.000000%"
                delta_decimal = 0.0
                trend = "Neutral"

            # Print in required format
            print(
                f"[{timestamp_str} UTC] SYMBOL={symbol} FUNDING_RATE={rate_pct_str} DELTA={delta_pct_str} TREND={trend}",
                flush=True,
            )

            # Prepare for next tick
            previous_rate = current_rate

            # Sleep until next 1-minute interval
            time.sleep(60)

        except KeyboardInterrupt:
            print("\nFunding rate tracker interrupted by user. Exiting.")
            sys.exit(0)
        except (BinanceAPIException, BinanceRequestException) as e:
            print(
                f"Binance API error: {e}. Retrying in 60s...",
                file=sys.stderr,
                flush=True,
            )
            time.sleep(60)
        except Exception as e:
            print(
                f"Unexpected error: {e}. Retrying in 60s...",
                file=sys.stderr,
                flush=True,
            )
            time.sleep(60)


if __name__ == "__main__":
    main()