#!/usr/bin/env python3
"""
Fetch Klinger's Oscillator value for a given symbol on 1-minute candles using Binance data; returns current oscillator value.
Usage: python klinger_oscillator_getter_1min.py --symbol BTC
Notes:
- Uses python-binance (no authentication: Client("", ""))
- Tries symbol as provided, and if needed appends 'USDT' (e.g., BTC -> BTCUSDT)
- Fetches up to 500 1m klines to compute KO
- KO = EMA(KL, fast) - EMA(KL, slow) where KL is EMA of VWPriceChange (Volume * (Close - PrevClose))
- Outputs: KO Symbol=... Interval=1m LatestKO=... Timestamp=...
"""

import argparse
import sys
import math
from datetime import datetime
from binance.client import Client

# Defaults for Klinger's Oscillator computation
KL_PERIOD = 21      # Period for EMA of Volume-Weighted Price Change to form KL
KO_FAST = 34        # Fast EMA for KO
KO_SLOW = 55        # Slow EMA for KO
KL_DATA_LIMIT = 500   # Number of 1m candles to fetch (max 500 as per requirement)

def ms_to_iso(ts_ms: int) -> str:
    dt = datetime.utcfromtimestamp(ts_ms / 1000.0)
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")

def compute_klinger_oscillator(klines, kl_period=KL_PERIOD, fast=KO_FAST, slow=KO_SLOW):
    """
    Compute Klinger's Oscillator (KO) latest value from Binance klines data.
    klines: list of [OpenTime, Open, High, Low, Close, Volume, CloseTime, ...]
    Returns (latest_KO_value, latest_close_time_ms)
    """
    if len(klines) < 2:
        return None, None

    closes = []
    volumes = []
    times = []

    # Extract close prices, volumes, and close times
    for k in klines:
        closes.append(float(k[4]))
        volumes.append(float(k[5]))
        times.append(int(k[6]))  # Close time in ms

    # Build VW Price Change series: VWPC_i = Volume_i * (Close_i - Close_{i-1})
    vwp = []
    for i in range(1, len(closes)):
        price_change = closes[i] - closes[i - 1]
        vwp.append(volumes[i] * price_change)

    if len(vwp) == 0:
        return None, None

    # EMA of VWPC to form Klinger's Line KL
    kl_values = []
    alpha_kl = 2.0 / (kl_period + 1.0)
    kl_ema = vwp[0]  # seed with first VWPC
    kl_values.append(kl_ema)
    for idx in range(1, len(vwp)):
        kl_ema = kl_ema + alpha_kl * (vwp[idx] - kl_ema)
        kl_values.append(kl_ema)

    # KO: EMA of KL with fast and slow windows
    ko_values = []
    ema_fast = None
    ema_slow = None
    alpha_fast = 2.0 / (fast + 1.0)
    alpha_slow = 2.0 / (slow + 1.0)
    for klv in kl_values:
        if ema_fast is None:
            ema_fast = klv
            ema_slow = klv
        else:
            ema_fast = ema_fast + alpha_fast * (klv - ema_fast)
            ema_slow = ema_slow + alpha_slow * (klv - ema_slow)
        ko = ema_fast - ema_slow
        ko_values.append(ko)

    if not ko_values:
        return None, None

    latest_ko = ko_values[-1]
    latest_time_ms = times[-1]  # corresponding to the last kline's CloseTime

    if latest_ko is None or not isinstance(latest_ko, float) or not math.isfinite(latest_ko):
        return None, None

    return latest_ko, latest_time_ms

def resolve_symbol_and_fetch(client, input_symbol, limit=KL_DATA_LIMIT):
    """
    Try resolving symbol variants and fetch klines.
    Returns (resolved_symbol, klines) or (None, None) on failure.
    """
    base = input_symbol.strip().upper()
    candidates = []

    if base.endswith('USDT'):
        candidates.append(base)
    else:
        candidates.append(base + 'USDT')
        candidates.append(base)  # try raw symbol as fallback

    # De-duplicate while preserving order
    seen = set()
    uniq = []
    for c in candidates:
        if c not in seen:
            uniq.append(c)
            seen.add(c)

    for sym in uniq:
        try:
            klines = client.get_klines(symbol=sym, interval=Client.KLINE_INTERVAL_1MINUTE, limit=limit)
            if klines and len(klines) >= 2:
                return sym, klines
        except Exception:
            # Print suppressed to avoid noisy logs; try next candidate
            continue

    return None, None

def main():
    parser = argparse.ArgumentParser(description='Fetch Klinger's Oscillator (KO) for a given symbol on 1-minute candles from Binance.')
    parser.add_argument('--symbol', required=True, help='Trading symbol (e.g., BTCUSDT or BTC)')
    args = parser.parse_args()

    symbol_input = args.symbol
    if not symbol_input or not symbol_input.strip():
        print("Error: --symbol parameter is required and cannot be empty.")
        parser.print_usage()
        sys.exit(1)

    # Initialize Binance client (no API key required for public data)
    client = Client("", "")

    resolved_symbol, klines = resolve_symbol_and_fetch(client, symbol_input, limit=KL_DATA_LIMIT)
    if klines is None or resolved_symbol is None:
        print("Error: Unable to fetch data for symbol '{}'. Check that the symbol exists on Binance and is available for 1m interval.".format(symbol_input))
        sys.exit(1)

    ko_value, ko_time_ms = compute_klinger_oscillator(klines, kl_period=KL_PERIOD, fast=KO_FAST, slow=KO_SLOW)
    if ko_value is None or ko_time_ms is None or not math.isfinite(float(ko_value)):
        print("Error: KO computation failed due to insufficient data. Ensure at least the required number of candles are available.")
        sys.exit(1)

    iso_timestamp = ms_to_iso(int(ko_time_ms))
    # Print result in clear format
    print("KO Symbol={} Interval=1m LatestKO={:.6f} Timestamp={}".format(resolved_symbol, float(ko_value), iso_timestamp))

if __name__ == "__main__":
    main()