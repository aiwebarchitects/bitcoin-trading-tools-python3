#!/usr/bin/env python3
"""
Computes current Volume Weighted Average Price (VWAP) on 15min timeframe
Usage: python vwap_tracker_15min.py --symbol BTC
"""
import sys
import argparse
import json
from datetime import datetime, timezone
from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceRequestException

def main():
    # Parse Command Line Arguments
    parser = argparse.ArgumentParser(description='Calculate intraday VWAP using Binance API.')
    parser.add_argument('--symbol', required=True, help='Trading symbol (e.g., BTC, ETH)')
    args = parser.parse_args()

    # Symbol normalization: If user inputs "BTC", assume "BTCUSDT"
    raw_symbol = args.symbol.strip().upper()
    # Simple heuristic: if length is short and doesn't end in a common quote, append USDT
    if len(raw_symbol) <= 4 and not raw_symbol.endswith("USDT"):
        symbol = f"{raw_symbol}USDT"
    else:
        symbol = raw_symbol

    try:
        # Initialize Binance Client (Unauthenticated)
        client = Client("", "")

        # 1. Initialization & Time Boundary
        # Determine start of the current trading session (00:00 UTC)
        now_utc = datetime.now(timezone.utc)
        start_of_day = now_utc.replace(hour=0, minute=0, second=0, microsecond=0)
        start_ts = int(start_of_day.timestamp() * 1000)

        # 2. Data Retrieval
        # Fetch 15-minute klines from 00:00 UTC to now
        # Kline format: [Open Time, Open, High, Low, Close, Volume, Close Time, ...]
        klines = client.get_klines(
            symbol=symbol,
            interval=Client.KLINE_INTERVAL_15MINUTE,
            startTime=start_ts
        )

        if not klines:
            print(f"Error: No market data found for {symbol} since {start_of_day.isoformat()}")
            sys.exit(1)

        # 3. VWAP Calculation
        cumulative_tp_v = 0.0
        cumulative_v = 0.0

        for k in klines:
            # Parse necessary fields (High, Low, Close, Volume)
            high = float(k[2])
            low = float(k[3])
            close = float(k[4])
            volume = float(k[5])

            # Calculate Typical Price
            typical_price = (high + low + close) / 3.0

            # Accumulate
            cumulative_tp_v += (typical_price * volume)
            cumulative_v += volume

        if cumulative_v == 0:
            print("Error: Total volume is zero, cannot calculate VWAP.")
            sys.exit(1)

        vwap = cumulative_tp_v / cumulative_v

        # 4. Output & Formatting
        output = {
            "symbol": symbol,
            "timeframe": "15m",
            "vwap": round(vwap, 4),
            "session_start": start_of_day.strftime('%Y-%m-%d %H:%M:%S UTC'),
            "candles_analyzed": len(klines)
        }

        print(json.dumps(output, indent=4))

    except BinanceAPIException as e:
        print(f"Binance API Error (Code {e.code}): {e.message}")
        sys.exit(1)
    except BinanceRequestException as e:
        print(f"Network Error: {e.message}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()