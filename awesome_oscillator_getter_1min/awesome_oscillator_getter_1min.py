#!/usr/bin/env python3
"""
Calculates the Awesome Oscillator (difference between 5-period and 34-period SMA of typical price)
for the given symbol on 1-minute candles using Binance data.

Usage: python awesome_oscillator_getter_1min.py --symbol BTC

Notes:
- Uses Binance free REST API (no authentication)
- Tries common pairings: BTCUSDT, BTC
- Requires at least 34 1-minute candles
- Output is a JSON line:
  {"symbol":"PAIR","interval":"1m","awesome_oscillator":VALUE,"as_of":"YYYY-MM-DDTHH:MM:SSZ"}
"""

import argparse
import json
import sys
from datetime import datetime

from binance.client import Client
from binance.exceptions import BinanceAPIException


def ms_to_iso(ms: int) -> str:
    """Convert millisecond timestamp to UTC ISO 8601 with 'Z' suffix."""
    dt = datetime.utcfromtimestamp(ms / 1000.0)
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def fetch_last_34_klines(symbol: str):
    """
    Fetch the latest 34 one-minute klines for a given symbol using Binance REST API.
    Tries common pair formats: "<SYMBOL>USDT" first, then the plain "<SYMBOL>".
    Returns tuple (used_symbol, klines) where klines is a list of kline rows.
    """
    client = Client("", "")

    # Binance returns klines as lists of strings: [openTime, open, high, low, close, volume, closeTime, ...]
    candidate_pairs = [f"{symbol}USDT", symbol]

    last_error = None
    for pair in candidate_pairs:
        try:
            klines = client.get_klines(symbol=pair, interval=Client.KLINE_INTERVAL_1MINUTE, limit=34)
            if klines and len(klines) >= 34:
                return pair, klines
            else:
                last_error = BinanceAPIException(f"Insufficient klines data for {pair}: expected 34, got {len(klines) if klines else 0}")
        except BinanceAPIException as e:
            last_error = e
        except Exception as e:
            last_error = e

    raise ValueError(f"Unable to fetch 1m klines for symbol '{symbol}'. "
                     f"Searched pairs {candidate_pairs}. Last error: {last_error}")


def compute_awesome_oscillator(klines):
    """
    Given 34 klines, compute the Awesome Oscillator:
    OA = SMA5(tp) - SMA34(tp), where tp = (high + low + close) / 3
    Returns the OA value and as_of timestamp (closeTime of last kline).
    """
    tps = []
    for k in klines:
        # kline structure as returned by get_klines: [openTime, open, high, low, close, volume, closeTime, ...]
        high = float(k[2])
        low = float(k[3])
        close = float(k[4])
        tp = (high + low + close) / 3.0
        tps.append(tp)

    if len(tps) < 34:
        raise ValueError(f"Not enough typical prices to compute OA (need 34, have {len(tps)}).")

    sma5 = sum(tps[-5:]) / 5.0
    sma34 = sum(tps[-34:]) / 34.0
    oa = sma5 - sma34

    # The most recent candle's closeTime is at index 6 (closeTime)
    as_of_ms = int(klines[-1][6])
    as_of_iso = ms_to_iso(as_of_ms)

    return oa, as_of_iso


def main():
    parser = argparse.ArgumentParser(description="Calculate Awesome Oscillator on 1-minute Binance data.")
    parser.add_argument('--symbol', required=True, help='Trading symbol (e.g., BTC, ETH)')

    args = parser.parse_args()
    raw_symbol = args.symbol.strip().upper()
    if not raw_symbol:
        print("ERROR: --symbol parameter is required.", file=sys.stderr)
        sys.exit(1)

    try:
        used_symbol, klines = fetch_last_34_klines(raw_symbol)
        ao_value, as_of = compute_awesome_oscillator(klines)
        output = {
            "symbol": used_symbol,
            "interval": "1m",
            "awesome_oscillator": ao_value,
            "as_of": as_of
        }
        print(json.dumps(output))
    except BinanceAPIException as e:
        print(f"BINANCE API ERROR: {str(e)}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"DATA ERROR: {str(e)}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("Interrupted by user.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"UNEXPECTED ERROR: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()