#!/usr/bin/env python3
"""
Calculates the 20-period Exponential Moving Average for any symbol on the 1h timeframe
Usage: python ema_calculator_1h.py --symbol BTC
"""
import argparse
import sys
import json
from binance.client import Client
from binance.exceptions import BinanceAPIException
from requests.exceptions import RequestException

def calculate_ema(prices, period=20):
    """
    Calculates the Exponential Moving Average (EMA) for a list of prices.
    Algorithm:
    1. Start with SMA of the first 'period' data points.
    2. Apply multiplier k = 2 / (N + 1).
    3. EMA_today = (Price_today * k) + (EMA_yesterday * (1 - k)).
    """
    if len(prices) < period:
        return None

    # Step 1: Calculate Initial SMA
    sma = sum(prices[:period]) / period
    ema = sma

    # Step 2: Calculate Multiplier
    multiplier = 2 / (period + 1)

    # Step 3: Calculate EMA for the remaining data points
    for price in prices[period:]:
        ema = (price * multiplier) + (ema * (1 - multiplier))

    return ema

def format_symbol_output(symbol):
    """Helper to format BTCUSDT to BTC/USDT for display if applicable"""
    if symbol.endswith("USDT"):
        return f"{symbol[:-4]}/{symbol[-4:]}"
    return symbol

def main():
    # Input Parsing & Validation
    parser = argparse.ArgumentParser(description="Calculate 20 EMA on 1h timeframe")
    parser.add_argument('--symbol', required=True, help='Trading symbol (e.g., BTC, ETH)')
    args = parser.parse_args()

    # Normalize symbol: If user inputs 'BTC', assume 'BTCUSDT' for Binance API
    raw_symbol = args.symbol.upper().strip()
    # Basic validation to ensure it's alphanumeric
    if not raw_symbol.isalnum():
        print(json.dumps({"error": "Invalid Argument", "message": "Symbol contains invalid characters."}))
        sys.exit(1)

    # Append USDT if it looks like a base asset (len <= 4 usually implies base asset in this context)
    # or if explicitly requested to test with "BTC" which implies a pair is needed.
    trading_pair = raw_symbol
    if len(raw_symbol) <= 4 and not raw_symbol.endswith('USDT'):
        trading_pair = raw_symbol + 'USDT'

    # Data Acquisition
    try:
        # Connect to Binance Public API (Unauthenticated)
        client = Client("", "")

        # Request last 50 candles, 1h timeframe
        # klines format: [Open time, Open, High, Low, Close, Volume, ...]
        klines = client.get_klines(
            symbol=trading_pair,
            interval=Client.KLINE_INTERVAL_1HOUR,
            limit=50
        )

        if not klines:
            print(json.dumps({"error": "Data Fetch Failed", "message": "No data returned from API."}))
            sys.exit(1)

    except BinanceAPIException as e:
        print(json.dumps({"error": "Data Fetch Failed", "message": f"Binance API Error: {e.message}"}))
        sys.exit(1)
    except RequestException as e:
        print(json.dumps({"error": "Data Fetch Failed", "message": "Network connection failed."}))
        sys.exit(1)
    except Exception as e:
        print(json.dumps({"error": "Unknown Error", "message": str(e)}))
        sys.exit(1)

    # EMA Calculation Logic
    try:
        # Extract Close prices (Index 4) and convert to float
        closes = [float(candle[4]) for candle in klines]
        
        # Calculate 20 EMA
        ema_20 = calculate_ema(closes, period=20)
        
        if ema_20 is None:
            print(json.dumps({"error": "Calculation Error", "message": "Not enough data points to calculate EMA."}))
            sys.exit(1)

        current_price = closes[-1]

        # Output Generation
        output = {
            "symbol": format_symbol_output(trading_pair),
            "timeframe": "1h",
            "price": round(current_price, 2),
            "ema_20": round(ema_20, 2)
        }

        print(json.dumps(output))

    except ValueError as e:
        print(json.dumps({"error": "Processing Error", "message": "Failed to parse price data."}))
        sys.exit(1)

if __name__ == "__main__":
    main()