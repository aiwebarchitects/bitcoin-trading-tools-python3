#!/usr/bin/env python3
"""
Fetches current Directional Movement Index (DMI) data for a given symbol on the 1-minute timeframe (DI+, DI-, and DMI value)
Usage: python dmi_getter_1min.py --symbol BTC
Notes:
- Uses Binance free API (no authentication)
- Requires python-binance library
- If symbol does not end with USDT, it will be paired as <SYMBOL>USDT (e.g., BTC -> BTCUSDT)
- Fetches last 15 one-minute candles and computes DMI over the 14 periods using Wilder’s method
"""

import argparse
import sys
from datetime import datetime
from binance.client import Client

def main():
    parser = argparse.ArgumentParser(description="Compute 1m DMI (DI+, DI-, DMI) for a given symbol using Binance public API")
    # Optional default BTC to satisfy "Test with BTC by default" requirement
    parser.add_argument('--symbol', default='BTC', help='Base symbol (e.g., BTC, ETH). Will be paired with USDT if needed (default BTC)')
    args = parser.parse_args()

    symbol_input = (args.symbol or 'BTC').strip().upper()
    if not symbol_input:
        print("Error: Symbol is required.", file=sys.stderr)
        sys.exit(1)

    # Map to trading pair expected by Binance (e.g., BTC -> BTCUSDT)
    if symbol_input.endswith('USDT'):
        pair = symbol_input
    else:
        pair = symbol_input + 'USDT'

    # Initialize Binance client (no API key required for public endpoints)
    client = Client("", "")

    # Fetch last 15 one-minute candles
    try:
        klines = client.get_klines(symbol=pair, interval=Client.KLINE_INTERVAL_1MINUTE, limit=15)
    except Exception as e:
        print(f"Error fetching klines for {pair}: {e}", file=sys.stderr)
        sys.exit(1)

    if not klines or len(klines) < 15:
        got = len(klines) if klines else 0
        print(f"Insufficient data for {pair}: expected 15 candles, received {got}", file=sys.stderr)
        sys.exit(1)

    # Prepare OHLC data arrays
    highs = []
    lows = []
    closes = []
    try:
        for k in klines:
            # k structure: [OpenTime, Open, High, Low, Close, Volume, ...]
            highs.append(float(k[2]))
            lows.append(float(k[3]))
            closes.append(float(k[4]))
    except Exception as e:
        print(f"Error parsing klines data: {e}", file=sys.stderr)
        sys.exit(1)

    # Wilder’s method over 14 periods (between 15 candles -> 14 periods)
    sumPlusDM = 0.0
    sumMinusDM = 0.0
    sumTR = 0.0

    for i in range(1, 15):  # i = 1..14 inclusive
        high_i = highs[i]
        low_i = lows[i]
        high_prev = highs[i - 1]
        low_prev = lows[i - 1]
        close_prev = closes[i - 1]

        UpMove = high_i - high_prev
        DownMove = low_prev - low_i

        if UpMove > DownMove:
            plusDM = max(0.0, UpMove)
            minusDM = 0.0
        elif DownMove > UpMove:
            plusDM = 0.0
            minusDM = max(0.0, DownMove)
        else:
            plusDM = 0.0
            minusDM = 0.0

        TR = max(high_i - low_i, abs(high_i - close_prev), abs(low_i - close_prev))

        sumPlusDM += plusDM
        sumMinusDM += minusDM
        sumTR += TR

    if sumTR == 0.0:
        print("Error: Sum of True Range (TR) is zero; cannot compute DI values.", file=sys.stderr)
        sys.exit(1)

    di_plus = 100.0 * sumPlusDM / sumTR
    di_minus = 100.0 * sumMinusDM / sumTR

    denom = di_plus + di_minus
    if denom == 0.0:
        print("Error: Sum of +DI and -DI is zero; cannot compute DMI.", file=sys.stderr)
        sys.exit(1)

    dmi = 100.0 * abs(di_plus - di_minus) / denom

    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

    # Output in requested, parseable format
    print(f"Symbol: {pair}")
    print("Timeframe: 1m")
    print(f"+DI: {di_plus:.2f}")
    print(f"-DI: {di_minus:.2f}")
    print(f"DMI: {dmi:.2f}")
    print(f"As of: {timestamp}")

if __name__ == "__main__":
    main()