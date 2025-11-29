#!/usr/bin/env python3
"""
Calculates current Stochastic RSI for a symbol on the 1-minute timeframe using Binance free API
Usage: python stoch_rsi_getter_1min.py --symbol BTC
Notes:
- Uses python-binance library (no authentication required)
- Fetches last 200 one-minute candles (or more if data allows)
- RSI period = 14
- Stochastic RSI: K over last 14 RSI values, D = SMA of last 3 K values
- Outputs a clear, human-readable line with K, D, RSI and range stats
"""

import argparse
import sys
import time
import math
from datetime import datetime
from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceRequestException

def fetch_klines_with_retry(client, symbol, limit=200, max_retries=5, backoff=1.0):
    """
    Fetch klines with retries to handle rate limits and transient network errors.
    Returns the klines data on success.
    """
    attempt = 0
    delay = backoff
    while attempt < max_retries:
        try:
            klines = client.get_klines(symbol=symbol, interval=Client.KLINE_INTERVAL_1MINUTE, limit=limit)
            if not klines or len(klines) == 0:
                raise BinanceAPIException("No klines data returned for symbol {}".format(symbol))
            return klines
        except (BinanceAPIException, BinanceRequestException) as e:
            # Binance API errors (including 429) may require backoff
            attempt += 1
            if attempt >= max_retries:
                raise
            sys.stderr.write("Binance API error: {}. Retrying {}/{} after {:.1f}s...\n".format(e, attempt, max_retries, delay))
            time.sleep(delay)
            delay = min(delay * 2.0, 60.0)
        except Exception as e:
            # Network or unexpected error
            attempt += 1
            if attempt >= max_retries:
                raise
            sys.stderr.write("Network error: {}. Retrying {}/{} after {:.1f}s...\n".format(e, attempt, max_retries, delay))
            time.sleep(delay)
            delay = min(delay * 2.0, 60.0)
    raise BinanceAPIException("Failed to fetch klines after retries for symbol {}".format(symbol))

def calculate_rsi(prices, period=14):
    """
    Calculate RSI values for a list of prices.
    Returns a list of RSI values corresponding to the price series.
    The first RSI value corresponds to the index 'period' in prices.
    """
    if len(prices) < period + 1:
        return []

    rsis = []

    # Initial average gain/loss
    gains = 0.0
    losses = 0.0
    for i in range(1, period + 1):
        delta = prices[i] - prices[i - 1]
        if delta >= 0:
            gains += delta
        else:
            losses += -delta
    average_gain = gains / period
    average_loss = losses / period

    # First RSI value at index 'period'
    if average_loss == 0:
        rsis.append(100.0)
    else:
        rs = average_gain / average_loss
        rsis.append(100.0 - (100.0 / (1.0 + rs)))

    # Remaining RSI values
    for i in range(period + 1, len(prices)):
        delta = prices[i] - prices[i - 1]
        gain = delta if delta > 0 else 0.0
        loss = -delta if delta < 0 else 0.0

        average_gain = (average_gain * (period - 1) + gain) / period
        average_loss = (average_loss * (period - 1) + loss) / period

        if average_loss == 0:
            rsis.append(100.0)
        else:
            rs = average_gain / average_loss
            rsis.append(100.0 - (100.0 / (1.0 + rs)))

    return rsis

def k_for_window(rsis, end_idx):
    """
    Compute K value for the RSI window ending at end_idx (inclusive).
    Window is rsis[end_idx-13:end_idx+1] (14 values).
    """
    if end_idx < 13:
        return None
    window = rsis[end_idx - 13:end_idx + 1]
    min_r = min(window)
    max_r = max(window)
    curr = rsis[end_idx]
    denom = max_r - min_r
    if denom == 0:
        return 0.0
    return (curr - min_r) / denom * 100.0

def main():
    parser = argparse.ArgumentParser(description="Calculate current Stochastic RSI on 1-minute timeframe from Binance free API.")
    parser.add_argument('--symbol', required=True, help='Trading symbol (e.g., BTCUSDT or BTC)')
    args = parser.parse_args()

    symbol_input = args.symbol.strip().upper()
    if not symbol_input:
        sys.stderr.write("Error: --symbol must be a non-empty string.\n")
        parser.print_help()
        sys.exit(2)

    # Normalize symbol to something Binance accepts; try common forms
    candidates = []
    if symbol_input.endswith('USDT'):
        candidates.append(symbol_input)
    else:
        candidates.append(symbol_input + 'USDT')
        candidates.append(symbol_input)

    client = Client("", "")  # No API keys required for public endpoints
    klines = None
    used_symbol = None

    for cand in candidates:
        try:
            data = fetch_klines_with_retry(client, cand, limit=200, max_retries=5, backoff=1.0)
            if data and len(data) > 0:
                klines = data
                used_symbol = cand
                break
        except Exception as e:
            sys.stderr.write("Warning: could not fetch data for {}: {}\n".format(cand, e))
            continue

    if klines is None:
        sys.stderr.write("Error: Unable to fetch data for symbol {}".format(symbol_input))
        sys.exit(1)

    # Extract closes and close times
    closes = []
    close_times_ms = []
    for k in klines:
        # kline: [Open time, Open, High, Low, Close, Volume, Close time, ...]
        try:
            close = float(k[4])
            closes.append(close)
            close_times_ms.append(int(k[6]))
        except Exception:
            sys.stderr.write("Error parsing kline data. Aborting.\n")
            sys.exit(1)

    if len(closes) < 15:
        sys.stderr.write("Error: not enough data to compute RSI (need at least 15 closes, have {})\n".format(len(closes)))
        sys.exit(1)

    # Calculate RSI values
    RSI_PERIOD = 14
    rsis = calculate_rsi(closes, RSI_PERIOD)
    if len(rsis) < 14:
        sys.stderr.write("Error: not enough RSI values computed (got {}).\n".format(len(rsis)))
        sys.exit(1)

    current_rsi = rsis[-1]
    last14 = rsis[-14:]
    rsi_min_last14 = min(last14)
    rsi_max_last14 = max(last14)

    if rsi_max_last14 - rsi_min_last14 == 0:
        stoch_k_current = 0.0
    else:
        stoch_k_current = (current_rsi - rsi_min_last14) / (rsi_max_last14 - rsi_min_last14) * 100.0

    # Compute D as SMA of last up to 3 K values
    ends_to_consider = [len(rsis) - 1, len(rsis) - 2, len(rsis) - 3]
    k_values = []
    for end in ends_to_consider:
        if end >= 13:
            k_val = k_for_window(rsis, end)
            if k_val is not None:
                k_values.append(k_val)

    if not k_values:
        stoch_d_current = 0.0
    else:
        # D as average of up to last 3 K values (most recent first in k_values)
        last_n = min(3, len(k_values))
        stoch_d_current = sum(k_values[:last_n]) / last_n

    # Time info: use last candle's close time
    last_close_time_ms = close_times_ms[-1]
    dt = datetime.utcfromtimestamp(last_close_time_ms / 1000.0)
    time_str = dt.strftime('%Y-%m-%dT%H:%M:%SZ')

    # Output
    symbol_print = used_symbol if used_symbol is not None else symbol_input
    output = (
        "{} | Time (UTC): {} | StochRSI_K: {:.2f} | StochRSI_D: {:.2f} | "
        "RSI_current: {:.2f} | RSI_min_last14: {:.2f} | RSI_max_last14: {:.2f}"
    ).format(symbol_print, time_str, stoch_k_current, stoch_d_current, current_rsi, rsi_min_last14, rsi_max_last14)

    print(output)

if __name__ == "__main__":
    main()