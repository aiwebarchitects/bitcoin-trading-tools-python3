#!/usr/bin/env python3
"""
Calculates Keltner Channel upper and lower bands using a 20-period EMA and 10-period ATR on 1-minute candles from Binance API
Usage: python keltner_channel_1min.py --symbol BTC
"""
import argparse
import json
import sys
import time
import datetime

from binance.client import Client
from binance.exceptions import BinanceAPIException

def normalize_symbol(symbol_input: str) -> str:
    s = symbol_input.strip().upper()
    if not s:
        return ""
    if s.endswith("USDT"):
        return s
    common = {
        "BTC", "ETH", "BNB", "ADA", "XRP", "DOGE", "SOL", "DOT",
        "MATIC", "LTC", "BCH", "ETC", "SHIB"
    }
    if s in common:
        return s + "USDT"
    # If user provided full symbol already (e.g., ETHUSDT), just return uppercase
    return s

def fetch_klines_with_retry(client: Client, symbol: str, interval: str, limit: int, retries: int = 1):
    for attempt in range(retries + 1):
        try:
            return client.get_klines(symbol=symbol, interval=interval, limit=limit)
        except BinanceAPIException as e:
            # Simple backoff on rate limits or transient API errors
            if attempt < retries:
                time.sleep(1.0)
                continue
            raise
        except Exception:
            if attempt < retries:
                time.sleep(1.0)
                continue
            raise

def main():
    parser = argparse.ArgumentParser(description="Keltner Channel on 1-minute candles from Binance (20 EMA, 10 ATR)")
    parser.add_argument('--symbol', required=True, help='Trading symbol (e.g., BTC or BTCUSDT)')
    parser.add_argument('--multiplier', type=float, default=2.0, help='Keltner channel multiplier (default 2.0)')
    parser.add_argument('--limit', type=int, default=40, help='Number of 1-minute candles to fetch (default 40)')
    args = parser.parse_args()

    symbol_input = args.symbol
    sym = normalize_symbol(symbol_input)
    if not sym:
        print("Error: Invalid or empty symbol provided.")
        sys.exit(1)

    # Initialize Binance client without API keys (public endpoints)
    client = Client("", "")

    # Fetch klines with simple retry in case of transient failures
    try:
        klines = fetch_klines_with_retry(
            client,
            symbol=sym,
            interval=Client.KLINE_INTERVAL_1MINUTE,
            limit=args.limit,
            retries=1
        )
    except BinanceAPIException as e:
        print(f"Error fetching klines for {sym}: Binance API error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error fetching klines for {sym}: {e}")
        sys.exit(1)

    if not isinstance(klines, list) or len(klines) < 21:
        print(f"Insufficient data for EMA(20) and ATR(10). Retrieved candles: {len(klines) if isinstance(klines, list) else 0}. Require at least 21.")
        sys.exit(1)

    # Parse OHLCV data
    n = len(klines)
    try:
        closes = [float(k[4]) for k in klines]
        highs  = [float(k[2]) for k in klines]
        lows   = [float(k[3]) for k in klines]
        open_times = [int(k[0]) for k in klines]
    except Exception as e:
        print(f"Error parsing klines data: {e}")
        sys.exit(1)

    # Build TR values; TR[i] corresponds to bar i (i >= 1). TR[0] remains None.
    TR = [None] * n
    for i in range(1, n):
        tr = max(highs[i] - lows[i], abs(highs[i] - closes[i - 1]), abs(lows[i] - closes[i - 1]))
        TR[i] = tr

    # EMA(20) seed with SMA of first 20 closes
    if n < 20:
        print("Insufficient data for EMA(20). Need at least 20 closes.")
        sys.exit(1)
    alpha_ema = 2.0 / (20.0 + 1.0)
    sma20 = sum(closes[0:20]) / 20.0
    ema20 = sma20
    for i in range(20, n):
        ema20 = alpha_ema * closes[i] + (1 - alpha_ema) * ema20
    middle = ema20

    # ATR(10)
    if n <= 10:
        print("Insufficient data for ATR(10). Need at least 11 candles.")
        sys.exit(1)
    alpha_atr = 2.0 / (10.0 + 1.0)
    # Seed ATR with SMA of TR[1]..TR[10]
    initial_tr_values = [TR[i] for i in range(1, min(n, 11))]  # includes indices 1..10 if available
    if len(initial_tr_values) < 10:
        print("Insufficient TR data to seed ATR(10).")
        sys.exit(1)
    atr = sum(initial_tr_values) / 10.0
    # Propagate ATR to the latest bar
    for i in range(11, n):
        atr = alpha_atr * TR[i] + (1 - alpha_atr) * atr
    atr_latest = atr

    upper = middle + args.multiplier * atr_latest
    lower = middle - args.multiplier * atr_latest

    latest_time_ms = int(open_times[-1])
    iso_time = datetime.datetime.utcfromtimestamp(latest_time_ms / 1000.0).strftime("%Y-%m-%d %H:%M:%S")

    result = {
        "symbol": sym,
        "interval": "1m",
        "time_of_latest_bar": iso_time,
        "middle": middle,
        "upper": upper,
        "lower": lower,
        "multiplier": args.multiplier,
        "data_count": n
    }

    # Machine-readable JSON
    print(json.dumps(result, indent=2))

    # Human-friendly concise line
    print(f"{sym} 1m: Middle={middle:.6f}, Upper={upper:.6f}, Lower={lower:.6f}")

if __name__ == "__main__":
    main()