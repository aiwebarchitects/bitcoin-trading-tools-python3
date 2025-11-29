#!/usr/bin/env python3
"""
Fetches current Money Flow Index (MFI) for a given symbol on 1-minute timeframe using Binance API and outputs JSON
Usage: python mfi_getter_1min.py --symbol BTC
"""

import argparse
import json
import datetime
from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceRequestException

# Number of periods for MFI calculation (N in the algorithm)
N = 14

def build_error_payload(message, code=None):
    payload = {"status": "error", "error": message}
    if code is not None:
        payload["code"] = code
    return payload

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--symbol', required=True, help='Trading symbol base (e.g., BTC, ETH). Will use pair "<symbol>USDT"')
    args = parser.parse_args()

    symbol_base = args.symbol.upper()
    pair = f"{symbol_base}USDT"

    # Initialize Binance client (no authentication)
    client = Client("", "")

    try:
        # Fetch last N+1 one-minute klines
        limit = N + 1
        klines = client.get_klines(symbol=pair, interval=Client.KLINE_INTERVAL_1MINUTE, limit=limit)
    except BinanceAPIException as e:
        code = getattr(e, 'code', None)
        print(json.dumps(build_error_payload(str(e), code)))
        raise SystemExit(1)
    except BinanceRequestException as e:
        print(json.dumps(build_error_payload(str(e))))
        raise SystemExit(1)
    except Exception as e:
        print(json.dumps(build_error_payload(str(e))))
        raise SystemExit(1)

    if not klines or len(klines) < limit:
        msg = f"Not enough klines returned. Expected {limit}, got {len(klines) if klines else 0}."
        print(json.dumps(build_error_payload(msg)))
        raise SystemExit(1)

    # Build TP and MF arrays
    tp_list = []
    mf_list = []

    for k in klines:
        try:
            high = float(k[2])
            low = float(k[3])
            close = float(k[4])
            vol = float(k[5])
        except (ValueError, TypeError) as e:
            print(json.dumps(build_error_payload(f"Invalid candle data: {e}")))
            raise SystemExit(1)

        tp = (high + low + close) / 3.0
        mf = tp * vol
        tp_list.append(tp)
        mf_list.append(mf)

    # Compute MFI using the last N transitions (i from 1 to N)
    positiveMF = 0.0
    negativeMF = 0.0

    for i in range(1, len(tp_list)):
        if tp_list[i] > tp_list[i - 1]:
            positiveMF += mf_list[i]
        elif tp_list[i] < tp_list[i - 1]:
            negativeMF += mf_list[i]
        # if equal, ignore (no change)

    denom = positiveMF + negativeMF

    # Current timestamp in ISO8601 (UTC)
    timestamp = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat()

    if denom == 0:
        # Undefined MFI due to zero denominator; report as success with mfi=null and a note
        output = {
            "symbol": symbol_base,
            "interval": "1m",
            "period": N,
            "mfi": None,
            "timestamp": timestamp,
            "status": "success",
            "note": "denominator zero in MFI calculation; MFI undefined for this window"
        }
    else:
        mfi = 100.0 * positiveMF / denom
        output = {
            "symbol": symbol_base,
            "interval": "1m",
            "period": N,
            "mfi": mfi,
            "timestamp": timestamp,
            "status": "success"
        }

    print(json.dumps(output))

if __name__ == "__main__":
    main()