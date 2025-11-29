# Binance 1-Minute Volume-Price Trend (VPT) Calculator

## Overview
`vpt_getter_1min.py` is a Python utility designed to calculate the Volume-Price Trend (VPT) technical indicator for cryptocurrency assets. It utilizes the Binance public API to fetch real-time 1-minute candlestick data (klines) and computes the cumulative VPT over the most recent 1,000 data points.

## Features
*   **Real-time Data:** Fetches the latest 1-minute klines from Binance.
*   **Smart Symbol Resolution:** Automatically attempts to append "USDT" if the raw symbol (e.g., "BTC") is not found.
*   **Resilient Networking:** Implements exponential backoff and retry logic to handle API rate limits (`429 Too Many Requests`) and network errors.
*   **VPT Calculation:** Computes the indicator using the standard formula: `VPT += Volume * ((Close - Previous Close) / Previous Close)`.

## Prerequisites
*   Python 3.6+
*   `python-binance` library

## Installation
The script relies on the `python-binance` wrapper. You must install it before running the script:

```bash
pip install python-binance
```

## Usage
Run the script from the command line, providing the target symbol via the `--symbol` argument.

### Basic Command
```bash
python vpt_getter_1min.py --symbol <SYMBOL>
```

### Examples
Fetch data for Bitcoin (automatically tries BTCUSDT):
```bash
python vpt_getter_1min.py --symbol BTC
```

Fetch data for Ethereum (explicit pair):
```bash
python vpt_getter_1min.py --symbol ETHUSDT
```

### Expected Output
On success, the script prints the resolved symbol, the UTC timestamp of the last candle, the last closing price, and the calculated VPT value:
```text
Symbol: BTCUSDT
Last Time (UTC): 2023-10-27 14:30
Last Close: 34150.00
VPT (latest): 12504.32
```

## Execution Output Analysis
The provided execution logs indicate that the script **failed to run** successfully.

### Error Log
```text
Error: Traceback (most recent call last):
  ...
  File "<exec>", line 12, in <module>
ModuleNotFoundError: No module named 'binance'
```

### Explanation of Failure
The error `ModuleNotFoundError: No module named 'binance'` indicates that the required third-party library `python-binance` was not installed in the Python environment where the script was executed.

To resolve this issue, the user must install the dependency using `pip install python-binance`.