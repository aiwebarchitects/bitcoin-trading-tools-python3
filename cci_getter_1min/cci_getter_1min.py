#!/usr/bin/env python3
"""
Retrieves current Commodity Channel Index (CCI) for any symbol on the 1-minute timeframe using Binance API
Usage: python cci_getter_1min.py --symbol BTC
Notes:
- Uses Binance REST API (no authentication)
- Tries symbol resolution: supports BTCUSDT or BTC (will attempt BTCUSDT first)
- Fetches last 21 one-minute klines, uses the most recent as TP_last and previous 20 as window
- Computes CCI as described
- Outputs: Symbol | Interval | CCI | Time
"""

import argparse
from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceRequestException
from datetime import datetime

def resolve_symbol(client: Client, base_symbol: str):
    """
    Attempts to resolve a working trading symbol.
    Tries base_symbolUSDT first, then base_symbol.
    Returns resolved symbol string or None if not found.
    """
    candidates = []
    s = base_symbol.strip().upper()

    if "USDT" in s or "BUSD" in s or "USDC" in s:
        candidates = [s]
    else:
        candidates = [s + "USDT", s]

    for cand in candidates:
        try:
            # Quick sanity check: try to fetch at least one kline
            klines = client.get_klines(symbol=cand, interval='1m', limit=1)
            if isinstance(klines, list) and len(klines) >= 1:
                return cand
        except BinanceAPIException:
            pass
        except BinanceRequestException:
            pass
        except Exception:
            pass

    return None

def main():
    parser = argparse.ArgumentParser(description='Retrieve 1-minute CCI for a given symbol on Binance.')
    parser.add_argument('--symbol', required=True, help='Trading symbol or base asset (e.g., BTCUSDT or BTC)')
    args = parser.parse_args()

    user_symbol = args.symbol
    # Binance client with no API key/secret
    client = Client("", "")

    resolved_symbol = resolve_symbol(client, user_symbol)
    if not resolved_symbol:
        print(f"Error: Could not resolve a tradable symbol for input '{user_symbol}'. "
              f"Try something like BTCUSDT or BTC.")
        raise SystemExit(2)

    try:
        klines = client.get_klines(symbol=resolved_symbol, interval='1m', limit=21)
    except BinanceAPIException as e:
        print(f"API error retrieving klines for symbol {resolved_symbol}: {e}")
        raise SystemExit(3)
    except BinanceRequestException as e:
        print(f"Connection error retrieving klines for symbol {resolved_symbol}: {e}")
        raise SystemExit(3)
    except Exception as e:
        print(f"Unexpected error retrieving klines for symbol {resolved_symbol}: {e}")
        raise SystemExit(4)

    if not isinstance(klines, list) or len(klines) < 21:
        received = len(klines) if isinstance(klines, list) else 0
        print(f"Data error: Expected 21 klines, received {received}.")
        raise SystemExit(2)

    # Compute Typical Price (TP) for each kline
    tp_list = []
    for k in klines:
        high = float(k[2])
        low = float(k[3])
        close = float(k[4])
        tp = (high + low + close) / 3.0
        tp_list.append(tp)

    # Window: first 20 TP values, tp_last is the last TP in the 21-candle set
    tp_last = tp_list[-1]
    tp_window = tp_list[:20]

    sma_tp = sum(tp_window) / 20.0
    mean_dev = sum(abs(tp - sma_tp) for tp in tp_window) / 20.0

    if mean_dev == 0:
        cci = 0.0
    else:
        cci = (tp_last - sma_tp) / (0.15 * mean_dev)

    # Time corresponding to the most recently completed candle (close_time)
    close_time_ms = int(klines[-1][6])
    time_utc = datetime.utcfromtimestamp(close_time_ms / 1000.0).strftime('%Y-%m-%dT%H:%M:%SZ')

    print(f"Symbol: {resolved_symbol} | Interval: 1m | CCI: {cci:.2f} | Time: {time_utc}")

if __name__ == "__main__":
    main()