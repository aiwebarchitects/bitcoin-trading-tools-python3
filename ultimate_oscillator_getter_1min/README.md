# ultimate_oscillator_getter_1min.py

## Overview
This script calculates the **Ultimate Oscillator (UO)** technical indicator for a specified cryptocurrency symbol. It utilizes real-time 1-minute candlestick (kline) data fetched from the Binance public API.

The script is designed to be robust regarding symbol input, automatically attempting to append "USDT" if the raw symbol is not found (e.g., inputting "BTC" will automatically resolve to "BTCUSDT").

## Features
- **Real-time Data:** Fetches the latest 1-minute OHLC (Open, High, Low, Close) data from Binance.
- **Symbol Fallback:** Automatically tries common trading pairs (e.g., `BTC` -> `BTCUSDT`) if the exact symbol isn't found.
- **Standard UO Calculation:** Computes the oscillator using the standard weighted average of three timeframes:
  - Short: 7 periods
  - Medium: 14 periods
  - Long: 28 periods
- **Timestamped Output:** Returns the calculated UO value with the corresponding UTC timestamp.

## Prerequisites

The script requires Python 3 and the `python-binance` library.

### Installation
To install the required dependency, run:
```bash
pip install python-binance
```

## Usage

Run the script from the command line, providing the target symbol via the `--symbol` argument.

### Basic Command
```bash
python ultimate_oscillator_getter_1min.py --symbol BTC
```

### Optional Arguments
- `--symbol` (Required): The trading symbol (e.g., `ETH`, `BTCUSDT`).
- `--limit` (Optional): Number of candles to fetch (default is 1000).

### Example Output
```text
Symbol BTCUSDT 1m UO: 45.32 (as of 2023-10-27 10:05:00 UTC)
```

## Algorithm Details
The Ultimate Oscillator is calculated as follows:
1. **Buying Pressure (BP):** `Close - Minimum(Low, Previous Close)`
2. **True Range (TR):** `Maximum(High, Previous Close) - Minimum(Low, Previous Close)`
3. **Average (A):** Sum of BP / Sum of TR for periods 7, 14, and 28.
4. **Final UO:** `100 * (4 * A7 + 2 * A14 + A28) / 7`

## Execution Output Analysis

When the script was executed in the provided environment, it failed with the following error:

```text
Error: Traceback (most recent call last):
  ...
  File "<exec>", line 16, in <module>
ModuleNotFoundError: No module named 'binance'
```

### Explanation of Failure
The error `ModuleNotFoundError: No module named 'binance'` indicates that the external dependency required to communicate with the Binance API is missing from the Python environment.

The script attempts to import `Client` from `binance.client` on line 16. Because the `python-binance` package was not installed in the execution environment, Python could not locate the module, causing the script to crash immediately.

### Solution
To fix this error, install the missing package using pip:
```bash
pip install python-binance
```