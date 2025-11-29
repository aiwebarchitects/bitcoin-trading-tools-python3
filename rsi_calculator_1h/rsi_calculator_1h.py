#!/usr/bin/env python3
"""
Calculates the 14-period Relative Strength Index (RSI) on the 1h timeframe to measure recent price changes and analyze overbought or oversold conditions.
Usage: python rsi_calculator_1h.py --symbol BTC
"""
import argparse
import sys
import datetime
from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceRequestException

def calculate_rsi(closes, period=14):
    """
    Calculates RSI using Wilder's Smoothing Method.
    """
    if len(closes) < period + 1:
        return None

    # Calculate differences
    deltas = [closes[i] - closes[i-1] for i in range(1, len(closes))]

    # Get initial seed averages (SMA of first 14 periods)
    seed_deltas = deltas[:period]
    seed_gain = sum([x for x in seed_deltas if x >= 0]) / period
    seed_loss = sum([abs(x) for x in seed_deltas if x < 0]) / period

    # Initialize averages
    avg_gain = seed_gain
    avg_loss = seed_loss

    # Apply Wilder's Smoothing for the rest of the data
    # Formula: (Previous Avg * 13 + Current Gain/Loss) / 14
    for delta in deltas[period:]:
        gain = delta if delta > 0 else 0
        loss = abs(delta) if delta < 0 else 0
        
        avg_gain = (avg_gain * (period - 1) + gain) / period
        avg_loss = (avg_loss * (period - 1) + loss) / period

    # Calculate RS and RSI
    if avg_loss == 0:
        return 100.0
    
    rs = avg_gain / avg_loss
    rsi = 100.0 - (100.0 / (1.0 + rs))
    return rsi

def get_condition(rsi_value):
    if rsi_value >= 70:
        return "OVERBOUGHT"
    elif rsi_value <= 30:
        return "OVERSOLD"
    else:
        return "NEUTRAL"

def main():
    parser = argparse.ArgumentParser(description="Calculate 1h RSI for a Binance symbol.")
    parser.add_argument('--symbol', required=True, help='Trading symbol (e.g., BTC, ETH)')
    args = parser.parse_args()

    # Normalize symbol: If user types 'BTC', assume 'BTCUSDT'
    symbol = args.symbol.upper()
    if len(symbol) <= 4 and not symbol.endswith("USDT"):
        symbol += "USDT"

    try:
        # Initialize Client (No API keys needed for public data)
        client = Client("", "")

        # Fetch 100 candles to ensure Wilder's smoothing stabilizes
        # 1h Interval
        klines = client.get_klines(
            symbol=symbol, 
            interval=Client.KLINE_INTERVAL_1HOUR, 
            limit=100
        )

        if not klines or len(klines) < 15:
            print(f"Error: Insufficient data fetched for symbol '{symbol}'.")
            sys.exit(1)

        # Extract closing prices (Index 4 in Binance kline response)
        # Kline format: [Open Time, Open, High, Low, Close, Volume, Close Time, ...]
        closes = [float(k[4]) for k in klines]
        last_close_time_ms = klines[-1][0]
        
        # Calculate RSI
        rsi_value = calculate_rsi(closes)

        if rsi_value is None:
            print(f"Error: Could not calculate RSI (insufficient data points).")
            sys.exit(1)

        # Determine Condition
        condition = get_condition(rsi_value)
        
        # Format Timestamp
        timestamp = datetime.datetime.fromtimestamp(last_close_time_ms / 1000).strftime('%Y-%m-%d %H:%M:%S')

        # Output Result
        # JSON-like structure or aligned text as requested
        output = {
            "Timestamp": timestamp,
            "Symbol": symbol,
            "RSI_1h": round(rsi_value, 2),
            "Condition": condition
        }
        
        print(f"{output['Timestamp']} | {output['Symbol']} | RSI: {output['RSI_1h']} | {output['Condition']}")

    except BinanceAPIException as e:
        print(f"Binance API Error: {e.message} (Code: {e.code})")
        sys.exit(1)
    except BinanceRequestException as e:
        print(f"Network Error: {e.message}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()