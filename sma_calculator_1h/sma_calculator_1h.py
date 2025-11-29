#!/usr/bin/env python3
"""
Calculates the 200-period Simple Moving Average on the 1h timeframe
Usage: python sma_calculator_1h.py --symbol BTC
"""
import argparse
import sys
import json
from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceRequestException

def main():
    # Input Parsing & Validation
    parser = argparse.ArgumentParser(description='Calculate 200 SMA on 1h timeframe')
    parser.add_argument('--symbol', required=True, help='Trading symbol (e.g., BTC, BTCUSDT)')
    args = parser.parse_args()

    # Normalize symbol: remove slashes, uppercase
    symbol = args.symbol.upper().replace('/', '')

    # Heuristic: If symbol is short (e.g. "BTC"), assume USDT pair to satisfy usage example
    if len(symbol) <= 4 and not symbol.endswith('USDT'):
        symbol += 'USDT'

    try:
        # Data Acquisition: Connect to Binance Public API
        client = Client("", "") # No authentication required for public data

        # Fetch the most recent 200 candles for 1h timeframe
        # klines format: [Open time, Open, High, Low, Close, Volume, ...]
        klines = client.get_klines(
            symbol=symbol,
            interval=Client.KLINE_INTERVAL_1HOUR,
            limit=200
        )

        # Validation: Ensure we received enough data
        if len(klines) < 200:
            raise ValueError(f"Insufficient data: Retrieved {len(klines)} candles, expected 200.")

        # Calculation Logic: Extract Close prices (index 4) and compute SMA
        close_prices = [float(candle[4]) for candle in klines]
        sma_200 = sum(close_prices) / len(close_prices)

        # Output Generation
        result = {
            "symbol": symbol,
            "sma_200_1h": round(sma_200, 8)
        }
        print(json.dumps(result))

    except (BinanceAPIException, BinanceRequestException) as e:
        # Handle API specific errors (e.g., Symbol not found)
        error_msg = {
            "error": "API Error",
            "message": str(e),
            "symbol": symbol
        }
        print(json.dumps(error_msg))
        sys.exit(1)
        
    except Exception as e:
        # Handle general errors
        error_msg = {
            "error": "Execution Error",
            "message": str(e)
        }
        print(json.dumps(error_msg))
        sys.exit(1)

if __name__ == "__main__":
    main()