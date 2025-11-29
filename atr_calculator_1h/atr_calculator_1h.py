#!/usr/bin/env python3
"""
Calculates Average True Range (ATR) volatility for any symbol on the 1h timeframe
Usage: python atr_calculator_1h.py --symbol BTC
"""
import argparse
import sys
from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceRequestException

def calculate_atr(klines, period=14):
    """
    Calculates ATR using Wilder's Smoothing (RMA).
    
    Args:
        klines (list): List of OHLCV data from Binance
        period (int): Lookback period for ATR (default 14)
        
    Returns:
        float: The most recent ATR value
    """
    # Parse OHLC data
    # Binance kline structure: [Open Time, Open, High, Low, Close, Volume, ...]
    # We need High (index 2), Low (index 3), Close (index 4)
    highs = [float(k[2]) for k in klines]
    lows = [float(k[3]) for k in klines]
    closes = [float(k[4]) for k in klines]

    # Ensure we have enough data points
    # We need 'period' for the initial SMA, plus subsequent data for smoothing
    if len(closes) < period + 1:
        return None

    tr_values = []

    # 1. Calculate True Range (TR) series
    for i in range(len(closes)):
        if i == 0:
            # First TR is simply High - Low (no previous close available)
            tr = highs[i] - lows[i]
        else:
            prev_close = closes[i-1]
            # TR = Max(High - Low, |High - PrevClose|, |Low - PrevClose|)
            hl = highs[i] - lows[i]
            hpc = abs(highs[i] - prev_close)
            lpc = abs(lows[i] - prev_close)
            tr = max(hl, hpc, lpc)
        tr_values.append(tr)

    # 2. Calculate ATR using Wilder's Smoothing
    # The first ATR is the Simple Moving Average (SMA) of the first 'period' TR values
    first_atr = sum(tr_values[:period]) / period
    
    # Subsequent ATRs are smoothed: ATR = ((Prior ATR * 13) + Current TR) / 14
    prev_atr = first_atr
    
    # Iterate from the (period)th element to the end
    for i in range(period, len(tr_values)):
        current_tr = tr_values[i]
        current_atr = ((prev_atr * (period - 1)) + current_tr) / period
        prev_atr = current_atr

    return prev_atr

def main():
    parser = argparse.ArgumentParser(description="Calculate ATR (1h) for a Binance symbol.")
    parser.add_argument('--symbol', required=True, help='Trading symbol (e.g., BTC, ETH)')
    args = parser.parse_args()

    # Handle symbol formatting
    # If user inputs "BTC", assume "BTCUSDT". If "BTCUSDT", keep as is.
    raw_symbol = args.symbol.upper()
    if len(raw_symbol) <= 5 and not raw_symbol.endswith("USDT") and not raw_symbol.endswith("BUSD"):
         symbol = f"{raw_symbol}USDT"
         display_symbol = f"{raw_symbol}/USDT"
    else:
         symbol = raw_symbol
         display_symbol = raw_symbol

    try:
        # Initialize Client (No API keys needed for public market data)
        client = Client("", "")

        # Fetch Data
        # Interval: 1 Hour
        # Limit: 50 (Provides enough buffer for 14-period ATR calculation + smoothing)
        klines = client.get_klines(
            symbol=symbol,
            interval=Client.KLINE_INTERVAL_1HOUR,
            limit=50
        )

        if not klines:
            print(f"Error: No data found for symbol {symbol}")
            sys.exit(1)

        # Calculate ATR
        atr_value = calculate_atr(klines, period=14)

        if atr_value is not None:
            # Format output based on magnitude of value
            if atr_value < 1:
                fmt_atr = f"{atr_value:.6f}"
            else:
                fmt_atr = f"{atr_value:.2f}"
                
            print(f"Symbol: {display_symbol} | Timeframe: 1h | ATR: {fmt_atr}")
        else:
            print("Error: Insufficient data points to calculate ATR.")

    except BinanceAPIException as e:
        print(f"Binance API Error: {e.message} (Code: {e.code})")
        if e.code == -1121:
            print(f"Hint: Check if '{symbol}' is a valid trading pair.")
    except BinanceRequestException as e:
        print(f"Network Error: {e.message}")
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")

if __name__ == "__main__":
    main()