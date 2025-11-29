#!/usr/bin/env python3
"""
Computes the Ease of Movement (EOM) for a given symbol on the 1-minute timeframe using Binance public API; usable via the CLI: python eom_getter_1min.py --symbol BTC

Usage: python eom_getter_1min.py --symbol BTC
"""
import argparse
import sys
import time
import json
from datetime import datetime
from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceRequestException

def symbol_to_pair(symbol: str) -> str:
    s = symbol.strip().upper()
    if s.endswith("USDT"):
        return s
    else:
        return s + "USDT"

def ms_to_iso(ms: int) -> str:
    dt = datetime.utcfromtimestamp(ms / 1000.0)
    return dt.strftime('%Y-%m-%dT%H:%M:%SZ')

def compute_eom(klines):
    # klines is a list of candles: [ [OpenTime, Open, High, Low, Close, Volume, ...], ... ]
    eom_values = []
    if len(klines) < 2:
        return eom_values
    high0 = float(klines[0][2])
    low0 = float(klines[0][3])
    m_prev = (high0 + low0) / 2.0
    for i in range(1, len(klines)):
        high_i = float(klines[i][2])
        low_i = float(klines[i][3])
        vol_i = float(klines[i][5])
        m_cur = (high_i + low_i) / 2.0
        if vol_i == 0.0:
            eom = 0.0
        else:
            eom = ((m_cur - m_prev) * (high_i - low_i)) / vol_i
        timestamp = int(klines[i][0])
        eom_values.append((timestamp, eom))
        m_prev = m_cur
    return eom_values

def main():
    parser = argparse.ArgumentParser(description="Compute Ease of Movement (EOM) on 1-minute timeframe using Binance public API.")
    parser.add_argument('--symbol', required=True, help='Trading symbol base asset (e.g., BTC)')
    parser.add_argument('--limit', type=int, default=50, help='Lookback limit for candles (default 50)')
    parser.add_argument('--json', action='store_true', help='Print JSON output')
    args = parser.parse_args()

    pair = symbol_to_pair(args.symbol)
    limit = max(1, int(args.limit))
    fetch_limit = limit + 1  # need N+1 candles to compute N EOM values

    client = Client("", "")

    retries = 3
    backoff = 1.0
    klines = None
    for attempt in range(1, retries + 1):
        try:
            klines = client.get_klines(symbol=pair, interval="1m", limit=fetch_limit)
            break
        except (BinanceAPIException, BinanceRequestException) as e:
            # Handle invalid symbol early
            if isinstance(e, BinanceAPIException) and getattr(e, 'status_code', None) == 400:
                msg = str(e)
                if "Invalid symbol" in msg or "Symbol does not exist" in msg:
                    print("Invalid symbol/pair. Try BTCUSDT or a valid pair.", file=sys.stderr)
                    sys.exit(1)
            if attempt < retries:
                time.sleep(backoff)
                backoff *= 2
            else:
                print("Network/API error while fetching data: {}".format(e), file=sys.stderr)
                sys.exit(1)
        except Exception as e:
            if attempt < retries:
                time.sleep(backoff)
                backoff *= 2
            else:
                print("Unexpected error: {}".format(e), file=sys.stderr)
                sys.exit(1)

    if klines is None:
        print("Failed to retrieve data.", file=sys.stderr)
        sys.exit(1)

    if len(klines) < 2:
        print("Error: Not enough candles returned. Need at least 2 candles.", file=sys.stderr)
        sys.exit(1)

    eom_pairs = compute_eom(klines)  # list of (timestamp_ms, eom)
    if len(eom_pairs) == 0:
        print("No EOM data computed.", file=sys.stderr)
        sys.exit(1)

    if args.json:
        eom_list = []
        for ts, val in eom_pairs:
            eom_list.append({"timestamp": ms_to_iso(ts), "eom": val})
        output = {
            "symbol": pair,
            "interval": "1m",
            "limit": limit,
            "eom": eom_list
        }
        print(json.dumps(output, indent=2))
    else:
        latest_ts, latest_val = eom_pairs[-1]
        latest_iso = ms_to_iso(latest_ts)
        print("Symbol: {}, Interval: 1m, Lookback: {} candles".format(pair, limit))
        print("Latest EOM: {:.6f} at {}".format(latest_val, latest_iso))
        print("\nRecent EOM values (most recent first):")
        start = max(0, len(eom_pairs) - 5)
        for ts, val in eom_pairs[start:]:
            print("  {}  =>  {:.6f}".format(ms_to_iso(ts), val))

if __name__ == "__main__":
    main()