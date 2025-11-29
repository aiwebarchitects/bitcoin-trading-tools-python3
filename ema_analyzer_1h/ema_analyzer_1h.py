#!/usr/bin/env python3
"""
Calculates 50 and 200 Exponential Moving Averages on the 1h timeframe
Usage: python ema_analyzer_1h.py --symbol BTC
"""
import argparse
import sys
import json
import pandas as pd
from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceRequestException

def main():
    # Argument Parsing
    parser = argparse.ArgumentParser(description="EMA Analyzer (1h Timeframe)")
    parser.add_argument('--symbol', required=True, help='Trading symbol (e.g., BTC, ETH)')
    args = parser.parse_args()

    # Normalize symbol (Assume USDT if not provided, standardizing for CLI usage)
    symbol = args.symbol.upper()
    if not symbol.endswith('USDT') and not symbol.endswith('BUSD') and not symbol.endswith('USDC'):
        symbol += 'USDT'

    try:
        # Initialize Binance Client (No Auth required for public data)
        client = Client("", "")

        # Fetch Data: 1 Hour interval, last 300 candles to ensure EMA convergence
        # limit=300 provides enough data points for EMA 200 to stabilize
        klines = client.get_klines(
            symbol=symbol,
            interval=Client.KLINE_INTERVAL_1HOUR,
            limit=300
        )

        if not klines:
            raise ValueError(f"No data received for symbol {symbol}")

        # Process Data into Pandas DataFrame
        # Binance Klines format: [Open Time, Open, High, Low, Close, Volume, ...]
        # We only need Close price for EMA
        df = pd.DataFrame(klines, columns=[
            'timestamp', 'open', 'high', 'low', 'close', 'volume', 
            'close_time', 'quote_asset_volume', 'trades', 
            'taker_buy_base', 'taker_buy_quote', 'ignore'
        ])

        # Convert 'close' column to float
        df['close'] = df['close'].astype(float)

        # Calculate EMAs
        # span=N corresponds to standard EMA calculation
        # adjust=False calculates the recursive formula: 
        # EMA_today = Price_today * alpha + EMA_yesterday * (1-alpha)
        df['ema_50'] = df['close'].ewm(span=50, adjust=False).mean()
        df['ema_200'] = df['close'].ewm(span=200, adjust=False).mean()

        # Get the most recent values (last row)
        last_row = df.iloc[-1]
        current_price = last_row['close']
        current_ema_50 = last_row['ema_50']
        current_ema_200 = last_row['ema_200']

        # Determine Trend
        trend = "Bullish" if current_ema_50 > current_ema_200 else "Bearish"

        # Construct Output
        result = {
            "symbol": symbol,
            "timeframe": "1h",
            "price": round(current_price, 2),
            "ema_50": round(current_ema_50, 2),
            "ema_200": round(current_ema_200, 2),
            "trend": trend,
            "signal": "Golden Cross" if trend == "Bullish" else "Death Cross"
        }

        # Print Result as JSON
        print(json.dumps(result, indent=4))

    except BinanceAPIException as e:
        print(f"[ERROR] Binance API Error: {e.message}")
        sys.exit(1)
    except BinanceRequestException as e:
        print(f"[ERROR] Network Error: {e.message}")
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] An unexpected error occurred: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()