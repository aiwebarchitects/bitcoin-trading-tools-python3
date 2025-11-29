#!/usr/bin/env python3
"""
Calculates the Average True Range (ATR) volatility metric on the 1h timeframe
Usage: python atr_volatility_1h.py --symbol BTC
"""
import argparse
import sys
from binance.client import Client
from binance.exceptions import BinanceAPIException
import math

def calculate_precision(price):
    """Determine appropriate precision based on price magnitude."""
    if price == 0:
        return 2
    if price > 1000:
        return 2
    if price > 1:
        return 4
    return 8

def main():
    parser = argparse.ArgumentParser(description="Calculate ATR Volatility (1h)")
    parser.add_argument('--symbol', required=True, help='Trading symbol (e.g., BTC, ETH)')
    args = parser.parse_args()

    # Input Parsing
    symbol = args.symbol.upper()
    
    # Heuristic: If symbol is short (e.g., BTC), assume USDT pair for convenience
    # unless it already looks like a pair.
    if len(symbol) <= 4:
        symbol += "USDT"

    # Initialize Binance Client (No Auth)
    try:
        client = Client("", "")
    except Exception as e:
        print(f"Error: Failed to initialize client. {e}")
        sys.exit(1)

    try:
        # Fetch Data: 1h timeframe, limit 20 candles
        # We need at least 15 candles to calculate TR and then ATR-14
        klines = client.get_klines(symbol=symbol, interval=Client.KLINE_INTERVAL_1HOUR, limit=20)
    except BinanceAPIException as e:
        if e.code == -1121:
            print(f"Error: Invalid Symbol '{symbol}'")
        else:
            print(f"Error: Binance API Exception ({e.message})")
        sys.exit(1)
    except Exception as e:
        print(f"Error: Network Timeout or Connection Error ({e})")
        sys.exit(1)

    # Check Data Sufficiency
    if not klines or len(klines) < 15:
        print("Error: Insufficient Data (Need at least 15 candles)")
        sys.exit(1)

    try:
        # Parse OHLC Data
        # klines structure: [Open Time, Open, High, Low, Close, Volume, ...]
        # We need High, Low, and Previous Close
        
        tr_values = []
        current_close = float(klines[-1][4])
        
        # Iterate from the second candle (index 1) to calculate TR based on Previous Close
        for i in range(1, len(klines)):
            high = float(klines[i][2])
            low = float(klines[i][3])
            prev_close = float(klines[i-1][4])
            
            # Calculate True Range (TR)
            # TR = max(High - Low, |High - PrevClose|, |Low - PrevClose|)
            hl = high - low
            h_pc = abs(high - prev_close)
            l_pc = abs(low - prev_close)
            
            tr = max(hl, h_pc, l_pc)
            tr_values.append(tr)

        # ATR Calculation (Period 14)
        # With limited data (20 candles), we use the Simple Moving Average (SMA) of the last 14 TRs
        # This is the standard initialization method for Wilder's Smoothing
        if len(tr_values) < 14:
            print("Error: Insufficient data to calculate ATR-14")
            sys.exit(1)

        # Get the last 14 TR values
        recent_tr = tr_values[-14:]
        atr = sum(recent_tr) / len(recent_tr)

        # Calculate Percentage
        atr_pct = (atr / current_close) * 100

        # Formatting
        precision = calculate_precision(current_close)
        fmt_str = f"{{:.{precision}f}}"
        
        atr_formatted = fmt_str.format(atr)
        pct_formatted = f"{atr_pct:.2f}"

        print(f"[{symbol}] 1H Volatility: {atr_formatted} ({pct_formatted}%)")

    except ValueError as e:
        print(f"Error: Data parsing error ({e})")
        sys.exit(1)
    except Exception as e:
        print(f"Error: An unexpected error occurred ({e})")
        sys.exit(1)

if __name__ == "__main__":
    main()