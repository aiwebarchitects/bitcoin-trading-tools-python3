#!/usr/bin/env python3
"""
Calculates Percentage Price Oscillator (PPO) for any symbol on 1min timeframe using Binance data
Usage: python ppo_getter_1min.py --symbol BTC
Notes:
- Uses python-binance (Client("", ""))
- Fetches 1m klines with a limit (default 300)
- Seeds EMA with SMA of first N prices
- PPO(t) = ((EMA_fast(t) - EMA_slow(t)) / EMA_slow(t)) * 100
- Prints one-line summary and an optional PPO tail

Example:
  python ppo_getter_1min.py --symbol BTC
"""

import argparse
import sys
from datetime import datetime
from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceRequestException


def fetch_klines(symbol_binance: str, limit: int = 300):
    """
    Fetch 1m klines for the given symbol using Binance REST API (unauthenticated)
    """
    client = Client("", "")
    try:
        klines = client.get_klines(symbol=symbol_binance,
                                  interval=Client.KLINE_INTERVAL_1MINUTE,
                                  limit=limit)
        return klines
    except BinanceAPIException as e:
        print(f"Binance API exception: {e}", file=sys.stderr)
        sys.exit(1)
    except BinanceRequestException as e:
        print(f"Binance request exception: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error during API call: {e}", file=sys.stderr)
        sys.exit(1)


def compute_ema_series(prices, period: int):
    """
    Compute EMA series seeded with SMA of the first 'period' prices.
    Returns a list of EMA values starting from index (period-1).
    """
    if len(prices) < period:
        return []
    alpha = 2.0 / (period + 1)
    # Seed with SMA of first 'period' prices
    first_sma = sum(prices[:period]) / period
    emas = [first_sma]
    for i in range(period, len(prices)):
        ema_today = alpha * prices[i] + (1 - alpha) * emas[-1]
        emas.append(ema_today)
    return emas


def compute_ppo_from_closes(closes, fast=12, slow=26):
    """
    Compute PPO values from a list of close prices.
    Returns a list of tuples: (t_index, ppo_value)
    - t_index corresponds to the index in 'closes' for which the PPO is computed
    """
    emas_fast = compute_ema_series(closes, fast)
    emas_slow = compute_ema_series(closes, slow)

    if not emas_fast or not emas_slow:
        return []

    start_t = max(fast - 1, slow - 1)
    ppo = []
    for t in range(start_t, len(closes)):
        fast_idx = t - (fast - 1)
        slow_idx = t - (slow - 1)
        if fast_idx < 0 or slow_idx < 0:
            continue
        if fast_idx >= len(emas_fast) or slow_idx >= len(emas_slow):
            continue
        ema_f = emas_fast[fast_idx]
        ema_s = emas_slow[slow_idx]
        if ema_s == 0:
            continue
        value = ((ema_f - ema_s) / ema_s) * 100.0
        ppo.append((t, value))
    return ppo


def main():
    parser = argparse.ArgumentParser(description="Calculate PPO on 1min Binance data for a given symbol.")
    parser.add_argument('--symbol', required=True, help='Trading symbol base (e.g., BTC) or pair (e.g., BTCUSDT)')
    parser.add_argument('--limit', type=int, default=300, help='Number of 1m klines to fetch (default 300)')
    parser.add_argument('--tail', type=int, default=5, help='Number of PPO values to show in tail (default 5)')
    args = parser.parse_args()

    symbol_input = args.symbol.strip().upper()
    # Normalize to Binance symbol format
    if symbol_input.endswith('USDT') or symbol_input.endswith('BUSD') or symbol_input.endswith('BNB'):
        symbol_binance = symbol_input
    else:
        symbol_binance = symbol_input + 'USDT'

    # Fetch klines
    klines = fetch_klines(symbol_binance, limit=args.limit)

    # Validate and extract closes and times
    if not isinstance(klines, list) or len(klines) == 0:
        print(f"Error: Received invalid response for symbol {symbol_binance}.", file=sys.stderr)
        sys.exit(1)

    closes = []
    times = []
    try:
        for k in klines:
            # k: [OpenTime, Open, High, Low, Close, Volume, ...]
            open_time = int(k[0])
            close_price = float(k[4])
            closes.append(close_price)
            times.append(open_time)
    except Exception as e:
        print(f"Error parsing klines data: {e}", file=sys.stderr)
        sys.exit(1)

    if len(closes) < 26:
        print(f"Error: Insufficient data points. Need at least 26 closes, got {len(closes)}.", file=sys.stderr)
        sys.exit(1)

    # Compute PPO
    ppo_series = compute_ppo_from_closes(closes, fast=12, slow=26)
    if not ppo_series:
        print("Error: Could not compute PPO due to insufficient data after EMA seeding.", file=sys.stderr)
        sys.exit(1)

    # Latest PPO value and timestamp
    latest_idx, latest_ppo = ppo_series[-1]
    latest_time_ms = times[latest_idx]
    latest_timestamp = datetime.utcfromtimestamp(latest_time_ms / 1000.0).strftime('%Y-%m-%dT%H:%M:%SZ')

    print(f"Symbol: {symbol_binance} | PPO(12,26) = {latest_ppo:.4f}% | timestamp={latest_timestamp}")

    # Optional tail
    tail_n = min(args.tail, len(ppo_series))
    if tail_n > 0:
        tail_entries = ppo_series[-tail_n:]
        tail_strs = []
        for t_idx, val in tail_entries:
            ts = datetime.utcfromtimestamp(times[t_idx] / 1000.0).strftime('%Y-%m-%dT%H:%M:%SZ')
            tail_strs.append(f"{ts}:{val:.4f}%")
        print("PPO tail (last {} points): {}".format(tail_n, " | ".join(tail_strs)))


if __name__ == "__main__":
    main()