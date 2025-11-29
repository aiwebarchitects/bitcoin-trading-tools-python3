#!/usr/bin/env python3
"""
Calculates the Balance of Power (BOP) indicator value for a given symbol on a 1-minute timeframe using Binance data, to identify buy/sell pressure shifts.
Usage: python balance_of_power_getter_1min.py --symbol BTC
"""

import argparse
import sys
from datetime import datetime
from binance.client import Client
from binance.exceptions import BinanceAPIException

def ms_to_iso(ts_ms):
    dt = datetime.utcfromtimestamp(ts_ms / 1000.0)
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")

def resolve_pair(client, base_symbol):
    base = base_symbol.upper().strip()
    if not base:
        return None
    candidates = [base + "USDT", base + "BUSD", base + "USDC"]
    for pair in candidates:
        try:
            klines = client.get_klines(symbol=pair, interval=Client.KLINE_INTERVAL_1MINUTE, limit=2)
            if isinstance(klines, list) and len(klines) > 0:
                return pair
        except Exception:
            continue
    return None

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--symbol', required=True, help='Trading symbol (e.g., BTC)')
    args = parser.parse_args()

    if not args.symbol or not isinstance(args.symbol, str) or args.symbol.strip() == "":
        print("Error: --symbol must be a non-empty string.")
        sys.exit(1)

    symbol_base = args.symbol.strip()

    # Initialize Binance client (no authentication)
    client = Client("", "")

    pair = resolve_pair(client, symbol_base)
    if pair is None:
        print("Error: Could not resolve a tradable pair for symbol '{}'. Tried USDT/BUSD/USDC markets.".format(symbol_base))
        sys.exit(1)

    try:
        klines = client.get_klines(symbol=pair, interval=Client.KLINE_INTERVAL_1MINUTE, limit=2)
    except BinanceAPIException as e:
        print("Binance API error: {}".format(e))
        sys.exit(1)
    except Exception as e:
        print("Error fetching klines for pair '{}': {}".format(pair, e))
        sys.exit(1)

    if not klines or len(klines) < 1:
        print("Error: No kline data returned for pair '{}'.".format(pair))
        sys.exit(1)

    latest = klines[-1]
    try:
        open_price = float(latest[1])
        high_price = float(latest[2])
        low_price = float(latest[3])
        close_price = float(latest[4])
        close_time_ms = int(latest[6])
    except Exception as e:
        print("Error parsing kline data: {}".format(e))
        sys.exit(1)

    if high_price - low_price == 0:
        bop = 0.0
    else:
        bop = (close_price - open_price) / (high_price - low_price)

    iso_time = ms_to_iso(close_time_ms)

    print("Symbol: {}".format(pair))
    print("Time (UTC): {}".format(iso_time))
    print("BOP_1m: {:.6f}".format(bop))
    if bop > 0:
        interpretation = "Buy pressure (BOP > 0)"
    elif bop < 0:
        interpretation = "Sell pressure (BOP < 0)"
    else:
        interpretation = "Neutral (BOP == 0)"
    print("Interpretation: {}".format(interpretation))

if __name__ == "__main__":
    main()