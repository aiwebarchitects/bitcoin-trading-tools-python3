#!/usr/bin/env python3
"""
Fetches current Williams %R (14-period) for a given symbol on a 1-minute timeframe using Binance API.
Usage: python williams_r_getter_1min.py --symbol BTC
"""
import argparse
from datetime import datetime
from binance.client import Client

def main():
    parser = argparse.ArgumentParser(description="Fetch Williams %R (14,1m) for a symbol using Binance REST API.")
    parser.add_argument('--symbol', required=True, help='Trading symbol (e.g., BTC, ETH) or trading pair (e.g., BTCUSDT)')
    args = parser.parse_args()

    input_symbol = (args.symbol or "").strip()
    if not input_symbol:
        print("Error: --symbol parameter is required.")
        return

    # Initialize Binance client with no authentication
    client = Client("", "")

    # Prepare candidate symbols to try (handle input like BTC or BTCUSDT)
    base = input_symbol.upper()
    candidates = []
    candidates.append(base)
    if not base.endswith("USDT") and not base.endswith("BUSD") and not base.endswith("BNB"):
        candidates.append(base + "USDT")

    used_symbol = None
    klines = None
    last_error = None

    # Attempt to fetch 14 one-minute candles for each candidate
    for cand in candidates:
        try:
            data = client.get_klines(symbol=cand, interval=Client.KLINE_INTERVAL_1MINUTE, limit=14)
            if data and len(data) >= 14:
                used_symbol = cand
                klines = data
                break
            else:
                last_error = "Insufficient candle data received for symbol {}".format(cand)
        except Exception as e:
            last_error = str(e)
            continue

    if klines is None or used_symbol is None:
        print("Error: Failed to fetch 14 one-minute candles for the provided symbol.")
        if last_error:
            print("Detail: {}".format(last_error))
        print("Tried candidates: {}".format(", ".join(candidates)))
        return

    # Extract 14 candles data
    try:
        highs = [float(kline[2]) for kline in klines]
        lows  = [float(kline[3]) for kline in klines]
        current_close = float(klines[-1][4])  # last candle's close
        close_time_ms = int(klines[-1][6])     # close time in milliseconds

        HighestHigh = max(highs)
        LowestLow = min(lows)

        if HighestHigh == LowestLow:
            print("Error: Division by zero in Williams %R calculation (HighestHigh == LowestLow).")
            return

        WilliamsR14 = (HighestHigh - current_close) / (HighestHigh - LowestLow) * (-100.0)

        # Timestamp formatting (UTC, ISO-like)
        timestamp = datetime.utcfromtimestamp(close_time_ms / 1000.0)
        timestamp_str = timestamp.strftime("%Y-%m-%dT%H:%M:%SZ")

        print("Symbol: {} | Williams %R(14,1m): {:.2f} | High: {:.2f} | Low: {:.2f} | Close: {:.2f} | Timestamp: {}".format(
            used_symbol,
            WilliamsR14,
            HighestHigh,
            LowestLow,
            current_close,
            timestamp_str
        ))
    except Exception as e:
        print("Error: Failed to parse candles data or compute Williams %R.")
        print("Detail: {}".format(str(e)))
        return

if __name__ == "__main__":
    main()