#!/usr/bin/env python3
"""
Calculates MACD (MACD line, signal line, histogram) for a given symbol on 1-minute timeframe using Binance data. CLI usage: python macd_calculator_1m.py --symbol BTC
Usage: python macd_calculator_1m.py --symbol BTC

Notes:
- Data retrieval: Fetch last 200 one-minute candles from Binance for pair (e.g., BTCUSDT).
- MACD calculation: EMA(12) and EMA(26) on close prices to form MACD_line = EMA12 - EMA26; signal line is EMA of MACD_line with span=9; histogram = MACD_line - signal.
- Output: Latest MACD, SIGNAL, HIST values; optional last 5 MACD/SIGNAL values when --verbose is used.
"""

import argparse
import sys
from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceRequestException
from datetime import datetime

def map_symbol_to_pair(symbol: str) -> str:
    s = symbol.upper()
    if s.endswith("USDT"):
        return s
    return f"{s}USDT"

def ema(values, period: int):
    if not values or period <= 0:
        return []
    k = 2.0 / (period + 1)
    result = []
    for i, v in enumerate(values):
        if i == 0:
            result.append(v)
        else:
            result.append(v * k + result[-1] * (1 - k))
    return result

def compute_macd(closes):
    if not closes or len(closes) < 26:
        return None
    ema12 = ema(closes, 12)
    ema26 = ema(closes, 26)
    macd_line = [a - b for a, b in zip(ema12, ema26)]
    signal_line = ema(macd_line, 9)
    histogram = [m - s for m, s in zip(macd_line, signal_line)]
    return macd_line, signal_line, histogram

def main():
    parser = argparse.ArgumentParser(description="MACD calculator on 1m timeframe from Binance data.")
    parser.add_argument('--symbol', required=True, help='Trading symbol (e.g., BTC, ETH)')
    parser.add_argument('--verbose', action='store_true', help='Print last 5 MACD/Signal values')
    args = parser.parse_args()

    symbol_input = args.symbol.upper()
    pair = map_symbol_to_pair(symbol_input)

    # Initialize Binance client (no authentication)
    client = Client("", "")

    try:
        # Fetch last 200 1-minute klines
        klines = client.get_klines(symbol=pair, interval=Client.KLINE_INTERVAL_1MINUTE, limit=200)
        if not klines or len(klines) < 26:
            print(f"Error: Insufficient data for {pair}. Retrieved {len(klines) if klines else 0} candles.")
            sys.exit(2)

        closes = [float(k[4]) for k in klines]

        macd_result = compute_macd(closes)
        if macd_result is None:
            print("Error: Unable to compute MACD due to insufficient data.")
            sys.exit(3)
        macd_line, signal_line, histogram = macd_result

        last_idx = len(macd_line) - 1
        # Time of last candle
        last_close_time_ms = int(klines[-1][6])
        time_str = datetime.utcfromtimestamp(last_close_time_ms / 1000.0).strftime("%Y-%m-%dT%H:%M:%SZ")

        print(f"Symbol: {pair}, Interval: 1m, Time: {time_str}")
        print(f"MACD: {macd_line[last_idx]:.5f}, SIGNAL: {signal_line[last_idx]:.5f}, HIST: {histogram[last_idx]:.5f}")

        if args.verbose and last_idx >= 4:
            last5_macd = macd_line[-5:]
            last5_signal = signal_line[-5:]
            print("Last 5 MACD values: [" + ", ".join(f"{v:.5f}" for v in last5_macd) + "]")
            print("Last 5 SIGNAL values: [" + ", ".join(f"{v:.5f}" for v in last5_signal) + "]")

    except BinanceAPIException as e:
        print(f"Binance API error: {e.message}")
        sys.exit(4)
    except BinanceRequestException as e:
        print(f"Binance request error: {e.message}")
        sys.exit(5)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(6)

if __name__ == "__main__":
    main()