#!/usr/bin/env python3
"""
Fetches the Vortex Indicator (VI+ and VI-) value for a given symbol on the 1-minute timeframe using Binance API
Usage: python vortex_indicator_getter_1min.py --symbol BTC
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from binance.client import Client


def resolve_symbol(input_symbol: str) -> str:
    s = input_symbol.strip().upper()
    if s.endswith('USDT'):
        return s
    else:
        return s + 'USDT'


def fetch_klines(client: Client, symbol: str, limit: int = 15):
    try:
        # 1 minute interval
        klines = client.get_klines(symbol=symbol, interval='1m', limit=limit)
        return klines
    except Exception as e:
        raise e


def compute_vi_from_klines(klines):
    # Expect at least 15 candles (indices 0..14)
    if klines is None or len(klines) < 15:
        return None, None, None

    highs = []
    lows = []
    closes = []
    close_times = []

    for k in klines:
        highs.append(float(k[2]))
        lows.append(float(k[3]))
        closes.append(float(k[4]))
        close_times.append(int(k[6]))

    sum_tr = 0.0
    sum_term_plus = 0.0
    sum_term_minus = 0.0

    # i = 1..14
    for i in range(1, 15):
        H_i = highs[i]
        L_i = lows[i]
        C_i = closes[i]

        H_prev = highs[i - 1]
        L_prev = lows[i - 1]
        C_prev = closes[i - 1]

        TR_i = max(H_i - L_i, abs(H_i - C_prev), abs(L_i - C_prev))
        term_plus_i = abs(H_i - L_prev)
        term_minus_i = abs(L_i - H_prev)

        sum_tr += TR_i
        sum_term_plus += term_plus_i
        sum_term_minus += term_minus_i

    if sum_tr == 0:
        vi_plus = float('nan')
        vi_minus = float('nan')
    else:
        vi_plus = sum_term_plus / sum_tr
        vi_minus = sum_term_minus / sum_tr

    as_of_ms = close_times[14]
    as_of_dt = datetime.fromtimestamp(as_of_ms / 1000.0, tz=timezone.utc)
    as_of_iso = as_of_dt.isoformat().replace('+00:00', 'Z')

    return vi_plus, vi_minus, as_of_iso


def main():
    parser = argparse.ArgumentParser(description='Fetch VI+ and VI- on 1m timeframe for a symbol using Binance API.')
    parser.add_argument('--symbol', required=True, help='Trading symbol (e.g., BTC, BTCUSDT)')
    args = parser.parse_args()

    input_symbol = args.symbol
    symbol = resolve_symbol(input_symbol)

    # Binance client with no API keys (public endpoints)
    client = Client(api_key="", api_secret="")

    try:
        klines = fetch_klines(client, symbol, limit=15)
    except Exception as e:
        print(json.dumps({"error": f"Failed to fetch klines for symbol {symbol}: {str(e)}"}))
        sys.exit(2)

    if not klines or len(klines) < 15:
        print(json.dumps({"error": f"Insufficient candle data received for symbol {symbol}. "
                                f"Expected 15 candles, got {len(klines) if klines else 0}."}))
        sys.exit(3)

    vi_plus, vi_minus, as_of_iso = compute_vi_from_klines(klines)

    # If Vi values are NaN (e.g., sum_tr == 0)
    if vi_plus != vi_plus or vi_minus != vi_minus:
        print(json.dumps({"error": "VI calculation resulted in NaN values (possible sum(TR) == 0)."}))
        sys.exit(4)

    output = {
        "symbol": symbol,
        "interval": "1m",
        "periods": 14,
        "vi_plus": vi_plus,
        "vi_minus": vi_minus,
        "as_of": as_of_iso
    }
    print(json.dumps(output))


if __name__ == "__main__":
    main()