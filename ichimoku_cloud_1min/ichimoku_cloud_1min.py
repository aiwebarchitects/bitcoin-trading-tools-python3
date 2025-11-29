#!/usr/bin/env python3
"""
Calculates Ichimoku cloud signals for any symbol on 1-minute timeframe using Binance data
Usage: python ichimoku_cloud_1min.py --symbol BTC
"""

import argparse
import sys
import json
import re
from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceRequestException

def build_symbol(input_symbol: str) -> str:
    s = input_symbol.upper().strip()
    # If it's already suffixed with USDT, keep as is
    if s.endswith("USDT"):
        return s
    # If it's a 3-6 character base symbol, append USDT
    if re.match(r'^[A-Z0-9]{3,6}$', s):
        return s + "USDT"
    # Fallback: return as-is
    return s

def fetch_klines(client: Client, symbol_pair: str, limit: int = 600):
    try:
        klines = client.get_klines(symbol=symbol_pair, interval=Client.KLINE_INTERVAL_1MINUTE, limit=limit)
        return klines
    except BinanceAPIException as e:
        print(f"Binance API error while fetching klines: {e}", file=sys.stderr)
        return None
    except BinanceRequestException as e:
        print(f"Binance request error: {e}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"Unexpected error during API call: {e}", file=sys.stderr)
        return None

def main():
    parser = argparse.ArgumentParser(description="Ichimoku Cloud signals on 1-minute timeframe from Binance data")
    parser.add_argument('--symbol', default='BTC', help='Trading symbol base (e.g., BTC) or full pair (e.g., BTCUSDT). Default BTC')
    args = parser.parse_args()

    symbol_input = (args.symbol or "").strip()
    if not symbol_input:
        print("Error: --symbol is required and cannot be empty.", file=sys.stderr)
        sys.exit(2)

    symbol_pair = build_symbol(symbol_input)

    # Basic format validation
    if not re.match(r'^[A-Z0-9]+$', symbol_pair):
        print("Error: Invalid symbol format. Use something like BTCUSDT or BTC. Allowed: uppercase letters and digits.", file=sys.stderr)
        sys.exit(2)

    # Create Binance client (unauthenticated)
    client = Client("", "")

    klines = fetch_klines(client, symbol_pair, limit=600)
    if not klines or len(klines) < 60:
        print("Error: Insufficient klines data retrieved. Ensure the symbol is valid and try again. Data length: {}".format(len(klines) if klines else 0), file=sys.stderr)
        sys.exit(3)

    # Parse highs, lows, closes
    highs = [float(k[2]) for k in klines]
    lows = [float(k[3]) for k in klines]
    closes = [float(k[4]) for k in klines]

    # Sanity: require enough data windows for calculations
    if len(highs) < 52 or len(lows) < 52 or len(closes) < 27:
        print("Error: Not enough data windows for calculations.", file=sys.stderr)
        sys.exit(4)

    # Current values
    tenkan_now = (max(highs[-9:]) + min(lows[-9:])) / 2
    kijun_now = (max(highs[-26:]) + min(lows[-26:])) / 2
    senkou_a = (tenkan_now + kijun_now) / 2
    senkou_b = (max(highs[-52:]) + min(lows[-52:])) / 2
    cloud_top = max(senkou_a, senkou_b)
    cloud_bottom = min(senkou_a, senkou_b)
    last_close = closes[-1]

    # Chikou span (close 26 bars ago)
    chikou = closes[-27] if len(closes) >= 27 else None

    # Previous values for crossover detection
    tenkan_prev = (max(highs[-10:-1]) + min(lows[-10:-1])) / 2
    kijun_prev = (max(highs[-27:-1]) + min(lows[-27:-1])) / 2
    cross_up = (tenkan_prev <= kijun_prev) and (tenkan_now > kijun_now)
    cross_down = (tenkan_prev >= kijun_prev) and (tenkan_now < kijun_now)

    if cross_up:
        cross_signal = "TENKAN_KIJUN_CROSS_UP"
    elif cross_down:
        cross_signal = "TENKAN_KIJUN_CROSS_DOWN"
    else:
        cross_signal = "NONE"

    # Price position relative to cloud
    if last_close > cloud_top:
        price_position = "Above cloud"
    elif last_close < cloud_bottom:
        price_position = "Below cloud"
    else:
        price_position = "Inside cloud"

    cloud_trend = "Bullish" if senkou_a > senkou_b else "Bearish" if senkou_a < senkou_b else "Neutral"

    result = {
        "symbol": symbol_pair,
        "timeframe": "1m",
        "last_price": last_close,
        "tenkan": tenkan_now,
        "kijun": kijun_now,
        "senkou_a": senkou_a,
        "senkou_b": senkou_b,
        "chikou": chikou,
        "cloud_top": cloud_top,
        "cloud_bottom": cloud_bottom,
        "price_position": price_position,
        "cloud_trend": cloud_trend,
        "signal": cross_signal
    }

    # Human-friendly output
    print(f"Ichimoku Cloud signals for {symbol_pair} on 1m timeframe:")
    print(f"  Last price: {last_close}")
    print(f"  Tenkan (9): {tenkan_now:.6f}")
    print(f"  Kijun (26): {kijun_now:.6f}")
    print(f"  Senkou Span A: {senkou_a:.6f}")
    print(f"  Senkou Span B: {senkou_b:.6f}")
    print(f"  Cloud top: {cloud_top:.6f}, cloud bottom: {cloud_bottom:.6f}")
    print(f"  Price position relative to cloud: {price_position}")
    print(f"  Cloud trend: {cloud_trend}")
    if cross_signal != "NONE":
        print(f"  Cross signal: {cross_signal}")
    print(f"  Chikou (26 bars ago): {chikou:.6f}" if chikou is not None else "  Chikou: N/A")

    # JSON machine-parseable block
    try:
        json_block = json.dumps(result, indent=2)
        print("\nJSON_OUTPUT_START")
        print(json_block)
        print("JSON_OUTPUT_END")
    except Exception as e:
        print(f"Error generating JSON output: {e}", file=sys.stderr)

if __name__ == "__main__":
    main()