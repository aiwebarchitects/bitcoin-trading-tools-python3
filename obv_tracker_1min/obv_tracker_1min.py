#!/usr/bin/env python3
"""
Calculates On-Balance-Volume for the given symbol on 1-minute candles and outputs the current OBV and its delta from the previous candle
Usage: python obv_tracker_1min.py --symbol BTC
Tests:
  - Default: python obv_tracker_1min.py --symbol BTC
Notes:
  - Uses python-binance (from binance.client import Client)
  - No authentication: Client("", "")
  - Persists state to obv_<symbol>.state.json to survive restarts
  - If a data gap > 1 minute is detected, the script exits with an error
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone

from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceRequestException


STATE_DIR = "."  # store state in current directory; can be changed if needed


def normalize_symbol(symbol_input: str) -> str:
    symbol = symbol_input.strip().upper()
    if symbol.endswith("USDT"):
        return symbol
    return f"{symbol}USDT"


def kline_to_record(kline) -> dict:
    # Binance KLINE format: [OpenTime, Open, High, Low, Close, Volume, CloseTime, ...]
    return {
        "open_time": int(kline[0]),
        "open": float(kline[1]),
        "high": float(kline[2]),
        "low": float(kline[3]),
        "close": float(kline[4]),
        "volume": float(kline[5]),
    }


def format_time(ts_ms: int) -> str:
    dt = datetime.fromtimestamp(ts_ms / 1000.0, tz=timezone.utc)
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def save_state(state_path: str, state: dict) -> None:
    try:
        with open(state_path, "w") as f:
            json.dump(state, f)
    except Exception as e:
        print(f"WARNING: Failed to save state to {state_path}: {e}", file=sys.stderr)


def load_state(state_path: str) -> dict | None:
    if not os.path.exists(state_path):
        return None
    try:
        with open(state_path, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"WARNING: Failed to load state from {state_path}: {e}", file=sys.stderr)
        return None


def print_line(symbol: str, ts_open_ms: int, obv: float, delta: float) -> None:
    ts_str = format_time(ts_open_ms)
    line = f"symbol={symbol} | time={ts_str} | OBV={obv} | delta={delta}"
    print(line, flush=True)
    # Optional JSON-like line for easy parsing
    json_line = json.dumps({"symbol": symbol, "time": ts_str, "obv": obv, "delta": delta})
    print(json_line, flush=True)


def compute_delta(current_close: float, prev_close: float, volume: float) -> float:
    if current_close > prev_close:
        return volume
    if current_close < prev_close:
        return -volume
    return 0.0


def main():
    parser = argparse.ArgumentParser(description="OBV tracker on 1-minute candles using Binance API (anonymous access).")
    parser.add_argument("--symbol", required=False, default="BTC", help="Trading symbol (e.g., BTC, ETH). Will be mapped to USDT pair (e.g., BTCUSDT).")
    args = parser.parse_args()

    raw_symbol = args.symbol or "BTC"
    symbol_pair = normalize_symbol(raw_symbol)
    state_filename = f"obv_{raw_symbol.upper()}_state.json"
    state_path = os.path.join(STATE_DIR, state_filename)

    # Initialize Binance client (no API keys)
    client = Client("", "")

    obv_state = load_state(state_path)

    # Initial values
    obv_prev = 0.0
    prev_close = None
    last_open_time = None
    symbol = symbol_pair

    try:
        # Validate access by fetching two latest klines
        klines = client.get_klines(symbol=symbol, interval=Client.KLINE_INTERVAL_1MINUTE, limit=2)
        if not klines or len(klines) < 2:
            print("ERROR: Not enough candle data available from Binance for symbol: {}".format(symbol), file=sys.stderr)
            sys.exit(2)

        curr_k = kline_to_record(klines[-1])
        prev_k = kline_to_record(klines[-2])

        if obv_state is None:
            # First run: initialize using previous close and current candle; OBV_prev starts at 0
            prev_close = prev_k["close"]
            delta = compute_delta(curr_k["close"], prev_close, curr_k["volume"])
            obv_curr = obv_prev + delta
            last_open_time = curr_k["open_time"]

            print_line(symbol.replace("USDT", ""), last_open_time, obv_curr, delta)

            # Persist state
            obv_state = {
                "obv": obv_curr,
                "prev_close": curr_k["close"],
                "last_open_time": last_open_time
            }
            save_state(state_path, obv_state)
        else:
            # If a stored state exists, ensure symbol matches
            if "last_open_time" not in obv_state or "obv" not in obv_state or "prev_close" not in obv_state:
                print("ERROR: Corrupted state file. Exiting.", file=sys.stderr)
                sys.exit(3)

            obv_prev = obv_state["obv"]
            prev_close = obv_state["prev_close"]
            last_open_time = int(obv_state["last_open_time"])

            # Determine if there is already a new candle ready to process (first check)
            # We'll fetch the latest candle to see if it's newer than last_open_time
            latest_klines = client.get_klines(symbol=symbol, interval=Client.KLINE_INTERVAL_1MINUTE, limit=2)
            if not latest_klines or len(latest_klines) < 2:
                print("ERROR: Unable to fetch latest candle data for symbol: {}".format(symbol), file=sys.stderr)
                sys.exit(4)

            latest_k = kline_to_record(latest_klines[-1])
            prev_seen_k = kline_to_record(latest_klines[-2])

            # If there is a new candle since last processed
            new_open_time = int(latest_k["open_time"])
            if new_open_time > last_open_time:
                # Data gap detection: allow only a single minute gap for real-time processing
                if new_open_time - last_open_time != 60_000:
                    print("ERROR: Data gap detected (>1 minute) for symbol {}. last_open_time={}, new_open_time={}".format(
                        symbol, last_open_time, new_open_time), file=sys.stderr)
                    sys.exit(5)

                delta = compute_delta(latest_k["close"], prev_close, latest_k["volume"])
                obv_curr = obv_prev + delta
                print_line(symbol.replace("USDT", ""), new_open_time, obv_curr, delta)

                # Update state
                obv_state = {
                    "obv": obv_curr,
                    "prev_close": latest_k["close"],
                    "last_open_time": new_open_time
                }
                save_state(state_path, obv_state)

        # Enter continuous monitoring loop
        while True:
            try:
                klines = client.get_klines(symbol=symbol, interval=Client.KLINE_INTERVAL_1MINUTE, limit=2)
                if not klines or len(klines) < 2:
                    raise BinanceAPIException("Not enough candle data returned by Binance for symbol {}".format(symbol))

                latest_k = kline_to_record(klines[-1])
                prev_k = kline_to_record(klines[-2])

                new_open_time = int(latest_k["open_time"])
                if new_open_time > obv_state["last_open_time"]:
                    if new_open_time - obv_state["last_open_time"] != 60_000:
                        print("ERROR: Data gap detected (>1 minute) for symbol {}. last_open_time={}, new_open_time={}".format(
                            symbol, obv_state["last_open_time"], new_open_time), file=sys.stderr)
                        sys.exit(5)

                    delta = compute_delta(latest_k["close"], obv_state["prev_close"], latest_k["volume"])
                    obv_curr = obv_state["obv"] + delta

                    print_line(symbol.replace("USDT", ""), new_open_time, obv_curr, delta)

                    obv_state = {
                        "obv": obv_curr,
                        "prev_close": latest_k["close"],
                        "last_open_time": new_open_time
                    }
                    save_state(state_path, obv_state)

                # Sleep briefly before re-checking for the next minute
                time.sleep(5)
            except BinanceRequestException as e:
                print(f"ERROR: Binance request exception: {e}", file=sys.stderr)
                time.sleep(5)
            except BinanceAPIException as e:
                print(f"ERROR: Binance API exception: {e}", file=sys.stderr)
                time.sleep(5)
            except KeyboardInterrupt:
                print("Interrupted by user. Exiting gracefully.")
                sys.exit(0)
            except Exception as e:
                print(f"ERROR: Unexpected exception: {e}", file=sys.stderr)
                time.sleep(5)
    except BinanceAPIException as e:
        print(f"ERROR: Binance API exception during initialization: {e}", file=sys.stderr)
        sys.exit(2)
    except BinanceRequestException as e:
        print(f"ERROR: Binance request exception during initialization: {e}", file=sys.stderr)
        sys.exit(2)
    except Exception as e:
        print(f"ERROR: Unexpected error: {e}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()