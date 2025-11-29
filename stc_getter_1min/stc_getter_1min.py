#!/usr/bin/env python3
"""
CLI tool using Binance API to fetch 1-minute candles for a given symbol and compute the Schaff Trend Cycle (STC)
to provide trend timing signals.
Usage: python stc_getter_1min.py --symbol BTC

Usage example:
- python stc_getter_1min.py --symbol BTC
- python stc_getter_1min.py --symbol ETH --limit 800 --verbose

Notes:
- Maps input symbol (e.g., BTC) to BTCUSDT by default unless user provides a symbol ending with USDT.
- Uses python-binance (no authentication: Client("", ""))
- Attempts to fetch at least 500 data points. Exits with a helpful message if data cannot be retrieved.
"""

import argparse
import sys
from binance.client import Client
from binance.exceptions import BinanceAPIException

def map_symbol_to_pair(symbol: str) -> str:
    s = symbol.strip().upper()
    if not s:
        raise ValueError("Symbol must be non-empty")
    if s.endswith("USDT"):
        return s
    return f"{s}USDT"

def fetch_klines(client: Client, pair: str, limit: int):
    # Binance 1m klines max limit is 1000
    limit = min(limit, 1000)
    try:
        klines = client.get_klines(symbol=pair, interval=Client.KLINE_INTERVAL_1MINUTE, limit=limit)
        return klines
    except BinanceAPIException as e:
        code = getattr(e, 'code', None)
        msg = str(e)
        if code is not None and (code == -1003 or code == 429 or code == 1046):
            raise RuntimeError("Rate limit exceeded (HTTP 429) while fetching klines") from e
        if "Unknown symbol" in msg or "Not Found" in msg or "Unknown symbol" in msg:
            raise RuntimeError(f"Symbol not found: {pair}") from e
        raise RuntimeError(f"Binance API error: {msg}") from e
    except Exception as e:
        raise RuntimeError(f"Failed to fetch klines: {e}") from e

def to_float_closes(klines):
    closes = []
    for k in klines:
        try:
            closes.append(float(k[4]))
        except Exception as e:
            raise ValueError(f"Invalid klines payload: {e}")
    return closes

def ema_series(prices, period):
    if period <= 0 or not prices:
        return []
    alpha = 2.0 / (period + 1)
    emas = []
    ema = prices[0]
    emas.append(ema)
    for p in prices[1:]:
        ema = alpha * p + (1 - alpha) * ema
        emas.append(ema)
    return emas

def compute_stc_series(closes):
    # MACD line: EMA(23) - EMA(50)
    ema23 = ema_series(closes, 23)
    ema50 = ema_series(closes, 50)
    min_len = min(len(ema23), len(ema50))
    if min_len <= 0:
        return [], []
    macd = [ema23[-min_len + i] - ema50[-min_len + i] for i in range(min_len)]
    macd_s = ema_series(macd, 10)

    # Stochastic of MACD_S: K with n=14
    n = 14
    K = []
    for i in range(len(macd_s)):
        win_start = max(0, i - n + 1)
        window = macd_s[win_start:i+1]
        min_v = min(window)
        max_v = max(window)
        denom = max_v - min_v
        if denom == 0:
            k = 50.0
        else:
            k = ((macd_s[i] - min_v) / denom) * 100.0
        K.append(k)

    # Schaff Trend Cycle: EMA(K, m) with m=3
    stc = ema_series(K, 3)
    return stc, macd_s

def determine_signal(prev, curr):
    if prev < 75.0 and curr >= 75.0:
        return "BUY"
    if prev > 25.0 and curr <= 25.0:
        return "SELL"
    return "HOLD"

def main():
    parser = argparse.ArgumentParser(description="Fetch 1-minute candles and compute Schaff Trend Cycle (STC) signals.")
    parser.add_argument('--symbol', required=True, help='Trading symbol (e.g., BTC). Will be mapped to BTCUSDT by default.')
    parser.add_argument('--limit', type=int, default=1000, help='Number of 1-minute candles to fetch (default 1000, max 1000)')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose output')
    args = parser.parse_args()

    symbol = args.symbol
    limit = args.limit
    verbose = args.verbose

    try:
        pair = map_symbol_to_pair(symbol)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

    client = Client("", "")

    try:
        klines = fetch_klines(client, pair, limit)
    except RuntimeError as e:
        print(f"Error: {e}")
        sys.exit(1)

    if not klines or len(klines) < 500:
        print("Error: Insufficient data retrieved. Ensure symbol exists and there are enough 1m candles available (>=500).")
        sys.exit(1)

    try:
        closes = to_float_closes(klines)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

    if len(closes) < 2:
        print("Error: Not enough close data.")
        sys.exit(1)

    stc_series, macd_s_series = compute_stc_series(closes)

    if not stc_series:
        print("Error: STC series could not be computed.")
        sys.exit(1)

    stc_last = stc_series[-1]
    if len(stc_series) >= 2:
        prev = stc_series[-2]
        signal = determine_signal(prev, stc_last)
        trend = "UP" if stc_last > prev else ("DOWN" if stc_last < prev else "FLAT")
    else:
        signal = "HOLD"
        trend = "FLAT"

    latest_close = closes[-1]
    macd_s_last = macd_s_series[-1] if macd_s_series else None

    line1 = f"Symbol: {pair} | STC={stc_last:.2f} | Signal={signal}"
    print(line1)

    line2 = f"Close={latest_close:.2f}, MACD_S={macd_s_last:.4f}, Trend={trend}"
    print(line2)

    # Last 5 STC values
    last5 = stc_series[-5:] if len(stc_series) >= 5 else stc_series
    stc_hist = " ".join(f"{v:.2f}" for v in last5)
    print(f"STC history (last {len(last5)}): {stc_hist}")

    if verbose:
        print(f"Debug: data_points={len(closes)}, pair={pair}, limit={limit}, macd_len={len(macd_s_series)}")

if __name__ == "__main__":
    main()