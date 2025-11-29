#!/usr/bin/env python3
"""
Calculates the Average Directional Index (ADX) for the given symbol on the 1-minute timeframe using the Binance API data.
Usage: python adx_strength_1min.py --symbol BTC
"""

import argparse
import sys
import datetime
from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceRequestException

N = 14  # period for ADX calculation

def fetch_klines(client, symbol, limit=100, interval='1m'):
    try:
        klines = client.get_klines(symbol=symbol, interval=interval, limit=limit)
        return klines
    except (BinanceAPIException, BinanceRequestException) as e:
        print(f"Binance API error: {e}", file=sys.stderr)
        sys.exit(2)
    except Exception as e:
        print(f"Unexpected error fetching klines: {e}", file=sys.stderr)
        sys.exit(2)

def compute_adx_from_klines(klines, period=N):
    """
    Compute ADX(14) using Wilder smoothing from given 1m klines.
    Returns (adx_value, details_dict) or (None, error_message)
    details_dict contains last_DI_plus, last_DI_minus, last_DX, and last_ADX (optional)
    """
    m = len(klines)
    # klines: list of [Open time, Open, High, Low, Close, Volume, Close time, ...]
    if m < period + 1:
        return None, "Insufficient data: need at least {} bars, got {}".format(period + 1, m)

    highs = [float(k[2]) for k in klines]
    lows = [float(k[3]) for k in klines]
    closes = [float(k[4]) for k in klines]

    # Precompute TR, +DM, -DM for i >= 1
    TR = []
    PlusDM = []
    MinusDM = []
    for i in range(1, m):
        high = highs[i]
        low = lows[i]
        prev_close = closes[i - 1]
        tr = max(high - low, abs(high - prev_close), abs(low - prev_close))
        TR.append(tr)

        up_move = highs[i] - highs[i - 1]
        down_move = lows[i - 1] - lows[i]
        plus = up_move if (up_move > down_move and up_move > 0) else 0
        minus = down_move if (down_move > up_move and down_move > 0) else 0

        PlusDM.append(plus)
        MinusDM.append(minus)

    # Initial Wilder sums for i = 1..period (TR[0..period-1], etc.)
    sumTR = sum(TR[0:period])
    sumPlusDM = sum(PlusDM[0:period])
    sumMinusDM = sum(MinusDM[0:period])

    smoothedTR = sumTR / period if period != 0 else 0.0
    smoothedPlusDM = sumPlusDM / period if period != 0 else 0.0
    smoothedMinusDM = sumMinusDM / period if period != 0 else 0.0

    DX_values = []
    last_DI_plus = None
    last_DI_minus = None
    last_DX = None

    # Iterate i from period to len(TR)-1
    for idx in range(period, len(TR)):
        tr = TR[idx]
        plus = PlusDM[idx]
        minus = MinusDM[idx]

        smoothedTR = (smoothedTR * (period - 1) + tr) / period
        smoothedPlusDM = (smoothedPlusDM * (period - 1) + plus) / period
        smoothedMinusDM = (smoothedMinusDM * (period - 1) + minus) / period

        if smoothedTR == 0:
            # Avoid division by zero; skip this step
            DI_plus = None
            DI_minus = None
            DX = None
        else:
            DI_plus = 100 * smoothedPlusDM / smoothedTR
            DI_minus = 100 * smoothedMinusDM / smoothedTR
            if (DI_plus + DI_minus) == 0:
                DX = None
            else:
                DX = 100 * abs(DI_plus - DI_minus) / (DI_plus + DI_minus)

        if DI_plus is not None and DI_minus is not None:
            last_DI_plus = DI_plus
            last_DI_minus = DI_minus
        if DX is not None:
            last_DX = DX
            DX_values.append(DX)

        # Update smoothed values for next iteration
        smoothedTR, smoothedPlusDM, smoothedMinusDM = smoothedTR, smoothedPlusDM, smoothedMinusDM

    if len(DX_values) < period:
        return None, "Insufficient DX values for ADX: got {}, need {}".format(len(DX_values), period)

    # Initial ADX: average of first 'period' DX values
    adx = sum(DX_values[0:period]) / period
    # Wilder smoothing for subsequent DX values
    for i in range(period, len(DX_values)):
        adx = (adx * (period - 1) + DX_values[i]) / period

    details = {
        'ADX': adx,
        'last_DI_plus': last_DI_plus,
        'last_DI_minus': last_DI_minus,
        'last_DX': last_DX
    }
    return adx, details

def normalize_symbol(symbol_input):
    up = symbol_input.upper()
    if not up.endswith('USDT'):
        up = up + 'USDT'
    return up

def main():
    parser = argparse.ArgumentParser(description="Compute ADX(14) on 1-minute Binance data for a symbol.")
    parser.add_argument('--symbol', required=True, help='Base trading symbol (e.g., BTC). Binance uses BTCUSDT by default.')
    args = parser.parse_args()

    raw_symbol = args.symbol.strip()
    if not raw_symbol:
        print("Error: --symbol must be provided.", file=sys.stderr)
        sys.exit(2)

    symbol = normalize_symbol(raw_symbol)

    # Initialize Binance client (unauthenticated)
    client = Client("", "")

    # Fetch klines
    limit = 100  # ensure enough data (needs at least 15 bars)
    klines = fetch_klines(client, symbol, limit=limit, interval='1m')
    if klines is None or len(klines) < (N + 1):
        print(f"Error: Insufficient data for {symbol}. Need at least {N+1} 1m bars, got {0 if klines is None else len(klines)}.", file=sys.stderr)
        sys.exit(3)

    adx_value, details = compute_adx_from_klines(klines, N)
    if adx_value is None:
        print(f"Error computing ADX: {details}", file=sys.stderr)
        sys.exit(4)

    # Timestamp from the last bar's close time
    last_bar_close_time_ms = int(klines[-1][6])
    timestamp = datetime.datetime.fromtimestamp(last_bar_close_time_ms / 1000.0).isoformat()

    print(f"ADX(14) on 1m for {symbol}: {adx_value:.2f} at {timestamp}")
    if details and details.get('last_DI_plus') is not None and details.get('last_DI_minus') is not None:
        last_DX = details.get('last_DX')
        if last_DX is not None:
            print(f"DI+/DI-: {details['last_DI_plus']:.2f} / {details['last_DI_minus']:.2f}  DX: {last_DX:.2f}")
        else:
            print(f"DI+/DI-: {details['last_DI_plus']:.2f} / {details['last_DI_minus']:.2f}  DX: N/A")

if __name__ == "__main__":
    main()