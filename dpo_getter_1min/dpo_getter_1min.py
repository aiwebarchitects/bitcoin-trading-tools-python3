#!/usr/bin/env python3
"""
Calculates the Detrended Price Oscillator (DPO) for a given symbol on a 1-minute timeframe using Binance data and returns the current DPO value
Usage: python dpo_getter_1min.py --symbol BTCUSDT
Test: python dpo_getter_1min.py --symbol BTC
"""

import argparse
import sys
import datetime
from binance.client import Client
from binance.exceptions import BinanceAPIException


def determine_candidate_pairs(symbol_input):
    s = symbol_input.strip().upper()
    candidates = []
    if s.endswith('USDT') or s.endswith('BUSD') or s.endswith('USDC'):
        candidates.append(s)
    else:
        candidates.append(s + 'USDT')
        candidates.append(s + 'BUSD')
        candidates.append(s + 'USDC')
    # Remove duplicates while preserving order
    seen = set()
    uniq = []
    for c in candidates:
        if c not in seen:
            uniq.append(c)
            seen.add(c)
    return uniq


def fetch_klines_for_candidates(candidates):
    client = Client("", "")
    for pair in candidates:
        try:
            klines = client.get_klines(symbol=pair, interval='1m', limit=1000)
            return pair, klines
        except BinanceAPIException:
            # Try next candidate
            continue
        except Exception as e:
            print(f"Unexpected error while fetching klines for {pair}: {e}")
            sys.exit(1)
    return None, None


def main():
    parser = argparse.ArgumentParser(description="Compute DPO (n=20) on 1-minute Binance data for a symbol.")
    parser.add_argument('--symbol', required=True, help='Trading pair symbol (e.g., BTCUSDT or BTC)')
    args = parser.parse_args()

    symbol_input = args.symbol
    candidates = determine_candidate_pairs(symbol_input)

    pair, klines = fetch_klines_for_candidates(candidates)
    if klines is None:
        print(f"Error: Unable to retrieve valid data for symbol(s): {', '.join(candidates)}. Please verify the symbol and try again.")
        sys.exit(2)

    # Extract closes and open times
    closes = [float(kline[4]) for kline in klines]
    open_times = [kline[0] for kline in klines]  # in ms

    n = 20
    s = n // 2 + 1  # floor(n/2) + 1
    required_points = s + n  # m >= s + n
    if len(closes) < required_points:
        print(f"Error: Insufficient data. Need at least {required_points} data points, got {len(closes)}.")
        sys.exit(3)

    last_i = len(closes) - 1
    # Compute SMA_n for i = last_i
    start = (last_i - s) - (n - 1)
    end = (last_i - s)
    if start < 0 or end < 0 or end >= len(closes) or start > end:
        print("Error: Invalid data window for SMA calculation.")
        sys.exit(4)

    sma = sum(closes[start:end + 1]) / n
    dpo = closes[last_i] - sma

    # Time corresponding to the last data point (open time of the last kline)
    time_ms = open_times[last_i]
    time_iso = datetime.datetime.utcfromtimestamp(time_ms / 1000).strftime('%Y-%m-%dT%H:%M:%SZ')

    print(f"Symbol: {pair} | DPO (1m, n={n}): {dpo:.6f} | Time: {time_iso}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nProcess interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)