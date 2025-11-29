#!/usr/bin/env python3
"""
Fetches the current Aroon Oscillator value for a symbol on 1-minute timeframe from Binance API
Usage: python aroon_oscillator_getter_1min.py --symbol BTC
"""
import argparse
import sys
from datetime import datetime

from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceRequestException


def main():
    parser = argparse.ArgumentParser(description="Fetch Aroon Oscillator (25, 1m) for a symbol from Binance")
    parser.add_argument('--symbol', required=True, help='Trading symbol (e.g., BTC, ETH). Will be converted to SYMBOLUSDT if needed.')
    args = parser.parse_args()

    symbol_input = (args.symbol or "").strip().upper()
    if not symbol_input:
        print("Error: --symbol cannot be empty.")
        sys.exit(3)

    market_symbol = symbol_input if symbol_input.endswith("USDT") else f"{symbol_input}USDT"

    client = Client("", "")

    try:
        klines = client.get_klines(symbol=market_symbol,
                                   interval=Client.KLINE_INTERVAL_1MINUTE,
                                   limit=25)
    except BinanceAPIException as e:
        print(f"Binance API error: {e}")
        sys.exit(5)
    except BinanceRequestException as e:
        print(f"Binance request error: {e}")
        sys.exit(2)
    except Exception as e:
        print(f"Network/API error: {e}")
        sys.exit(2)

    if not klines or len(klines) < 25:
        print("not enough data for 25 periods")
        sys.exit(4)

    N = 25
    highs = [float(k[2]) for k in klines]
    lows = [float(k[3]) for k in klines]

    index_highest = int(max(range(N), key=lambda i: highs[i]))
    index_lowest = int(min(range(N), key=lambda i: lows[i]))

    days_since_highest = (N - 1) - index_highest
    days_since_lowest = (N - 1) - index_lowest

    aroon_up = ((N - days_since_highest) / N) * 100.0
    aroon_down = ((N - days_since_lowest) / N) * 100.0
    aroon_oscillator = aroon_up - aroon_down

    # Time of the last candle's open time (UTC)
    last_open_time_ms = klines[-1][0]
    time_utc = datetime.utcfromtimestamp(last_open_time_ms / 1000.0).strftime("%Y-%m-%dT%H:%M:%SZ")

    print(f"Symbol: {market_symbol} | Time (UTC): {time_utc} | Aroon Oscillator (25, 1m) = {aroon_oscillator:.4f}")


if __name__ == "__main__":
    main()