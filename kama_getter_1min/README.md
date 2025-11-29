# KAMA Getter (1-Minute Timeframe)

## Overview
`kama_getter_1min.py` is a Python utility designed to calculate **Kaufman's Adaptive Moving Average (KAMA)** for cryptocurrency assets. It utilizes the Binance public REST API to fetch real-time market data on a **1-minute timeframe**.

The script automatically handles symbol formatting (appending `USDT` if necessary), retrieves the most recent candlestick data (klines), computes the KAMA value using a period of 10, and outputs the result in a structured, pipe-delimited format.

## Features
- **Real-time Data:** Fetches live 1-minute klines from Binance.
- **KAMA Calculation:** Implements the standard KAMA formula with:
  - Efficiency Ratio period ($n$): 10
  - Fast Smoothing Constant: $2 / (2 + 1)$
  - Slow Smoothing Constant: $2 / (30 + 1)$
- **Smart Symbol Handling:** Automatically appends `USDT` to symbols (e.g., input `BTC` becomes `BTCUSDT`).
- **Structured Output:** Prints data in a format easy to parse by other tools or logs.

## Prerequisites
The script requires Python 3 and the `python-binance` library.

### Installation
To install the required dependency, run:
```bash
pip install python-binance
```

## Usage
Run the script from the command line, providing the target symbol via the `--symbol` argument.

### Syntax
```bash
python kama_getter_1min.py --symbol <SYMBOL>
```

### Examples
Fetch KAMA for Bitcoin (defaults to BTCUSDT):
```bash
python kama_getter_1min.py --symbol BTC
```

Fetch KAMA for Ethereum (explicit pair):
```bash
python kama_getter_1min.py --symbol ETHUSDT
```

## Output Format
On success, the script prints a single line to `stdout`:
```text
KAMA_1MIN | symbol=<SYMBOL> | kama=<VALUE> | last_close=<PRICE> | n=10 | timestamp=<ISO_DATE>
```

**Example Output:**
```text
KAMA_1MIN | symbol=BTCUSDT | kama=64200.50 | last_close=64210.00 | n=10 | timestamp=2023-10-27T10:00:00Z
```

## Execution Error Analysis
During the provided execution test, the script failed with the following error:

```text
ModuleNotFoundError: No module named 'binance'
```

### Explanation
The error indicates that the Python environment attempting to run the script does not have the `python-binance` library installed. The script imports `Client` from `binance.client` on line 8, which causes the interpreter to crash immediately if the package is missing.

### Resolution
To fix this error, install the missing package using pip:
```bash
pip install python-binance
```