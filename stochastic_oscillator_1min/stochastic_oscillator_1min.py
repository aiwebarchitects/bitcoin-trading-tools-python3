#!/usr/bin/env python3
"""
Calculates the fast and slow stochastic oscillator (%K and %D) for a symbol on the 1-minute timeframe using Binance data

Usage:
  python stochastic_oscillator_1min.py --symbol BTC
  # This will interpret BTC as BTCUSDT by default

Algorithm:
- Data input and retrieval: Use a CLI flag --symbol to specify the trading pair (e.g., BTCUSDT). Fetch the latest 1-minute klines from Binance (limit 200) to ensure at least 14 bars for %K calculation. Validate that data exists (at least 14 bars) and handle API/network errors gracefully.
- Indicator calculation (fast and slow stochastic):
  - N = 14 periods for %K and 3-period smoothing
  - K_fast_i = 100 * (C_i - minLow14_i) / (maxHigh14_i - minLow14_i)
    where minLow14_i is the minimum Low over the 14 bars ending at i and maxHigh14_i is the maximum High over the same window.
    If denom is 0, K_fast_i = 0.0
  - D_fast_i = SMA(K_fast over last 3 values) = mean(K_fast_{i-2}, K_fast_{i-1}, K_fast_i)
  - K_slow_i = SMA(K_fast over last 3 values) = D_fast_i (equivalently)
  - D_slow_i = SMA(K_slow over last 3 values) = mean(D_fast_{i-2}, D_fast_{i-1}, D_fast_i)
  - We output the values for the most recent bar (i = M-1, where M is the number of klines retrieved).
- Output: JSON for easy parsing, e.g.:
  { "symbol": "BTCUSDT", "time": "YYYY-MM-DDTHH:MM:SSZ", "fastK": ..., "fastD": ..., "slowK": ..., "slowD": ... }
- Error handling: 
  - If --symbol is missing or invalid, exit with a clear message.
  - If Binance API returns an error or data is insufficient, report the issue and exit non-zero.
  - Handle network timeouts, rate limits, and JSON parsing errors with retries or graceful failure.
Indicators: Stochastic Oscillator
"""

import argparse
import json
import time
from datetime import datetime

from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceRequestException

def normalize_symbol(input_symbol: str) -> str:
    s = input_symbol.strip().upper()
    if s.endswith("USDT"):
        return s
    # If user provides a base asset like BTC, assume BTCUSDT
    return s + "USDT"

def validate_symbol(client: Client, symbol: str) -> bool:
    try:
        # Try to fetch symbol info directly (best effort)
        client.get_symbol_info(symbol)
        return True
    except Exception:
        # Fallback: check in exchange info symbols list
        try:
            info = client.get_exchange_info()
            symbols = [s.get("symbol") for s in info.get("symbols", [])]
            return symbol in symbols
        except Exception:
            return False

def fetch_klines_with_retries(client: Client, symbol: str, interval: str, limit: int, retries: int = 3, backoff: float = 1.0):
    for attempt in range(1, retries + 1):
        try:
            return client.get_klines(symbol=symbol, interval=interval, limit=limit)
        except (BinanceAPIException, BinanceRequestException) as e:
            if attempt == retries:
                raise
            sleep_time = backoff * (2 ** (attempt - 1))
            print(f"Binance API error on attempt {attempt}/{retries}: {e}. Retrying in {sleep_time:.1f}s...", flush=True)
            time.sleep(sleep_time)
        except Exception as e:
            raise

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--symbol', required=True, help='Trading symbol (e.g., BTC to imply BTCUSDT, or BTCUSDT directly)')
    args = parser.parse_args()

    # Initialize Binance client (unauthenticated)
    client = Client("", "")

    # Normalize and validate symbol
    try:
        pair = normalize_symbol(args.symbol)
    except Exception as e:
        print(json.dumps({"error": f"Invalid symbol input: {e}"}))
        raise SystemExit(1)

    if not validate_symbol(client, pair):
        print(json.dumps({"error": f"Symbol '{pair}' not found on Binance. Ensure the pair exists (e.g., BTCUSDT)."}))
        raise SystemExit(1)

    # Fetch latest klines (1 minute, limit 200)
    try:
        klines = fetch_klines_with_retries(
            client,
            symbol=pair,
            interval=Client.KLINE_INTERVAL_1MINUTE,
            limit=200,
            retries=3,
            backoff=1.0,
        )
    except Exception as e:
        print(json.dumps({"error": f"Failed to fetch klines: {e}"}))
        raise SystemExit(1)

    if not klines or len(klines) < 14:
        print(json.dumps({"error": "Insufficient kline data received. Need at least 14 bars."}))
        raise SystemExit(1)

    N = 14
    M = len(klines)

    # Prepare arrays
    K_fast = [None] * M
    D_fast = [None] * M
    D_slow = [None] * M  # SMA of D_fast over last 3 bars

    # Compute K_fast for each end index from N-1 to M-1
    for end in range(N - 1, M):
        window = klines[end - N + 1 : end + 1]  # 14 bars ending at 'end'
        lows = [float(bar[3]) for bar in window]
        highs = [float(bar[2]) for bar in window]
        closes = float(window[-1][4])

        minLow14 = min(lows)
        maxHigh14 = max(highs)
        denom = maxHigh14 - minLow14

        if denom == 0:
            k_val = 0.0
        else:
            k_val = 100.0 * (closes - minLow14) / denom

        K_fast[end] = k_val

    # Compute D_fast = SMA(K_fast, 3)
    for end in range(N - 1, M):
        if None in (K_fast[end - 2], K_fast[end - 1], K_fast[end]):
            D_fast[end] = None
        else:
            D_fast[end] = (K_fast[end - 2] + K_fast[end - 1] + K_fast[end]) / 3.0

    # Compute D_slow = SMA(D_fast, 3)
    for end in range(N - 1, M):
        if None in (D_fast[end - 2], D_fast[end - 1], D_fast[end]):
            D_slow[end] = None
        else:
            D_slow[end] = (D_fast[end - 2] + D_fast[end - 1] + D_fast[end]) / 3.0

    latest = M - 1
    if None in (K_fast[latest], D_fast[latest], D_slow[latest]):
        print(json.dumps({"error": "Insufficient data to compute all stochastic values for the latest bar."}))
        raise SystemExit(1)

    fastK = float(K_fast[latest])
    fastD = float(D_fast[latest])
    slowK = float(D_fast[latest])  # slow %K equals D_fast
    slowD = float(D_slow[latest])

    # Time corresponding to the latest candle (Close time)
    close_time_ms = klines[latest][6]
    time_str = datetime.utcfromtimestamp(close_time_ms / 1000.0).strftime("%Y-%m-%dT%H:%M:%SZ")

    output = {
        "symbol": pair,
        "time": time_str,
        "fastK": round(fastK, 6),
        "fastD": round(fastD, 6),
        "slowK": round(slowK, 6),
        "slowD": round(slowD, 6)
    }

    print(json.dumps(output))

if __name__ == "__main__":
    main()