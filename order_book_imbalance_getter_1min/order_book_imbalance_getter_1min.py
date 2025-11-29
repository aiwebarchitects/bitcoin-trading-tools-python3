#!/usr/bin/env python3
"""
Calculates order book imbalance using Binance depth data to gauge supply vs. demand pressure on the 1-minute timeframe
Usage: python order_book_imbalance_getter_1min.py --symbol BTC
"""
import argparse
import json
import time
import sys
import logging
from datetime import datetime
from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceRequestException

def build_pair(symbol_input):
    s = symbol_input.strip().upper()
    if s.endswith("USDT"):
        return s
    return s + "USDT"

def fetch_depth(client, pair, limit):
    return client.get_order_book(symbol=pair, limit=limit)

def compute_obi_from_depth(depth, levels, log=None):
    bids = depth.get('bids', [])
    asks = depth.get('asks', [])
    if not isinstance(bids, list) or not isinstance(asks, list):
        if log:
            log.warning("Depth data malformed: bids/asks not lists")
        return 0.0, 0.0, 0.0

    top_bids = bids[:levels]
    top_asks = asks[:levels]

    notional_bid = 0.0
    notional_ask = 0.0

    for price_str, qty_str in top_bids:
        try:
            price = float(price_str)
            qty = float(qty_str)
            notional_bid += price * qty
        except Exception:
            if log:
                log.warning(f"Invalid bid entry: price={price_str}, qty={qty_str}")
            continue

    for price_str, qty_str in top_asks:
        try:
            price = float(price_str)
            qty = float(qty_str)
            notional_ask += price * qty
        except Exception:
            if log:
                log.warning(f"Invalid ask entry: price={price_str}, qty={qty_str}")
            continue

    denom = notional_bid + notional_ask
    if denom <= 0.0:
        return 0.0, notional_bid, notional_ask
    obi = (notional_bid - notional_ask) / denom
    return obi, notional_bid, notional_ask

def main():
    parser = argparse.ArgumentParser(description="Calculate order book imbalance (OBI) from Binance depth data on a 1-minute cadence.")
    parser.add_argument('--symbol', required=True, help='Trading symbol base asset (e.g., BTC). The script will use USDT pairing (BTCUSDT) by default.')
    parser.add_argument('--levels', type=int, default=5, help='Number of levels to consider from the order book (default: 5)')
    parser.add_argument('--interval_seconds', type=int, default=60, help='Interval between samples in seconds (default: 60)')
    args = parser.parse_args()

    # Logger configured to stderr for warnings/errors
    logger = logging.getLogger("obi_getter")
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stderr)
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(levelname)s:%(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    pair = build_pair(args.symbol)
    levels = max(1, int(args.levels))
    interval = max(1, int(args.interval_seconds))

    client = Client("", "")

    max_retries = 3

    try:
        while True:
            depth_data = None
            obi = 0.0
            notional_bid = 0.0
            notional_ask = 0.0

            attempt = 0
            while attempt < max_retries:
                try:
                    depth_data = fetch_depth(client, pair, levels)
                    break
                except (BinanceAPIException, BinanceRequestException) as e:
                    attempt += 1
                    wait = 2 ** attempt
                    logger.warning(f"Depth fetch failed (attempt {attempt}/{max_retries}): {e}. Retrying in {wait}s...")
                    time.sleep(wait)
                except Exception as e:
                    attempt += 1
                    wait = 2 ** attempt
                    logger.warning(f"Unexpected error fetching depth: {e}. Retrying in {wait}s...")
                    time.sleep(wait)

            if depth_data is None:
                obi = 0.0
                notional_bid = 0.0
                notional_ask = 0.0
                logger.warning("Depth data unavailable after retries. Emitting 0.0 OBI for this interval.")
            else:
                obi, notional_bid, notional_ask = compute_obi_from_depth(depth_data, levels, log=logger)

            ts = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
            output = {
                "timestamp": ts,
                "symbol": pair,
                "obi": round(float(obi), 6),
                "notional_bid": round(float(notional_bid), 6),
                "notional_ask": round(float(notional_ask), 6),
                "levels": levels
            }

            print(json.dumps(output, separators=(',', ':'), ensure_ascii=False))
            sys.stdout.flush()

            time.sleep(interval)

    except KeyboardInterrupt:
        sys.stderr.write("\nInterrupted by user. Exiting.\n")
        sys.exit(0)
    except SystemExit:
        raise
    except Exception as e:
        logger.error(f"Unhandled error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()