#!/usr/bin/env python3
"""
Calculates the Chande Momentum Oscillator (CMO) for a given symbol on the 1-minute timeframe using Binance data
Usage: python cmo_getter_1min.py --symbol BTC
"""
import argparse
import sys
import datetime
from binance.client import Client

def compute_cmo_from_closes(closes):
    """
    Compute CMO given a list of N+1 close prices [c0, c1, ..., cN]
    """
    if closes is None or len(closes) < 2:
        return None
    gain = 0.0
    loss = 0.0
    for i in range(1, len(closes)):
        delta = closes[i] - closes[i - 1]
        if delta > 0:
            gain += delta
        else:
            loss += -delta
    denom = gain + loss
    if denom == 0:
        return 0.0
    return 100.0 * (gain - loss) / denom

def fetch_klines(client, symbol, limit):
    """
    Fetch klines for given symbol and limit. Returns list or None on error.
    """
    try:
        klines = client.get_klines(
            symbol=symbol,
            interval=Client.KLINE_INTERVAL_1MINUTE,
            limit=limit
        )
        if klines is None or len(klines) < limit:
            return None, f"Insufficient klines data: expected {limit}, got {len(klines) if klines else 0}"
        return klines, None
    except Exception as ex:
        return None, str(ex)

def main():
    parser = argparse.ArgumentParser(description="Calculate CMO on 1-minute timeframe from Binance data.")
    parser.add_argument('--symbol', required=True, help='Trading symbol (e.g., BTCUSDT or BTC)')
    parser.add_argument('--period', type=int, default=14, help='CMO period length (default 14)')
    args = parser.parse_args()

    symbol_input = (args.symbol or "").strip()
    if not symbol_input:
        print("Error: --symbol parameter is required.", file=sys.stderr)
        sys.exit(1)

    period = args.period
    if period is None or not isinstance(period, int) or period < 2:
        print("Error: --period must be an integer greater than or equal to 2.", file=sys.stderr)
        sys.exit(1)

    # Initialize Binance client (public endpoints, no API key required)
    client = Client("", "")

    # Prepare symbol variations (try as provided, then try with USDT suffix)
    symbol_upper = symbol_input.upper()
    limit = period + 1  # last N+1 closes
    klines = None
    used_symbol = None

    # First attempt with user-provided symbol
    klines, err = fetch_klines(client, symbol_upper, limit)
    if klines is None:
        # Fallback: try appending USDT if not already present
        if not symbol_upper.endswith("USDT"):
            alt_symbol = symbol_upper + "USDT"
        else:
            alt_symbol = symbol_upper
        klines, err = fetch_klines(client, alt_symbol, limit)
        if klines is not None:
            used_symbol = alt_symbol
        else:
            # If still failed, report error and exit
            error_msg = err if err else f"Unable to fetch klines for {symbol_upper} or {alt_symbol}"
            print(f"Error: {error_msg}", file=sys.stderr)
            sys.exit(1)
    else:
        used_symbol = symbol_upper

    # If we already had klines from first attempt, set used_symbol accordingly
    if not used_symbol:
        used_symbol = symbol_upper

    # Validate data integrity
    if klines is None or len(klines) < limit:
        print(f"Error: Insufficient data received for {used_symbol}. Expected {limit} klines.", file=sys.stderr)
        sys.exit(1)

    # Parse closes
    try:
        closes = [float(k[4]) for k in klines]
    except Exception as ex:
        print(f"Error parsing close prices: {ex}", file=sys.stderr)
        sys.exit(1)

    if len(closes) < limit:
        print(f"Error: Not enough close prices to compute CMO. Required: {limit}, got: {len(closes)}", file=sys.stderr)
        sys.exit(1)

    cmo = compute_cmo_from_closes(closes)
    # Latest close time (CloseTime is at index 6, in milliseconds)
    latest_close_time_ms = klines[-1][6]
    latest_close_dt = datetime.datetime.fromtimestamp(latest_close_time_ms / 1000.0, tz=datetime.timezone.utc)
    latest_close_str = latest_close_dt.isoformat()

    # Output
    if cmo is None:
        print(f"CMO({period}) for {used_symbol} [{latest_close_str}]: N/A", flush=True)
    else:
        print(f"CMO({period}) for {used_symbol} [{latest_close_str}]: {cmo:.2f}%", flush=True)

if __name__ == "__main__":
    main()