# Z-Score Price Calculator (1-Minute Interval)

## Overview
`zscore_price_1min.py` is a Python utility designed for cryptocurrency technical analysis. It connects to the Binance public API to fetch the last 20 closing prices for a specified trading pair on 1-minute candlestick intervals. Using this data, it calculates the **Z-score** of the most recent price, indicating how many standard deviations the current price is from the 20-period mean.

This metric is useful for identifying statistical outliers, potential mean reversion opportunities, or momentum breakouts.

## Features
- **Symbol Normalization:** Automatically appends `USDT` to the symbol if omitted (e.g., inputting `BTC` converts to `BTCUSDT`).
- **Real-time Data:** Fetches live market data via the Binance API.
- **Statistical Analysis:** Computes Mean, Standard Deviation, and Z-score based on the last 20 minutes of activity.
- **Error Handling:** Includes checks for API connectivity issues and insufficient data points.

## Prerequisites
The script relies on the `python-binance` library to interact with the exchange API.

### Installation
To install the required dependency, run:
```bash
pip install python-binance
```

## Usage
Run the script from the command line, providing the target cryptocurrency symbol via the `--symbol` argument.

### Basic Command
```bash
python zscore_price_1min.py --symbol BTC
```

### Explicit Pair
```bash
python zscore_price_1min.py --symbol ETHUSDT
```

### Successful Output Example
If the script runs successfully, it outputs the statistical data in the following format:
```text
Symbol: BTC | Z-score (last 20 closes, 1m): 1.245000 | mean=26500.000000 | std=15.500000 | latest=26519.290000 | n=20
```

## Execution Output Analysis
Based on the provided execution logs, the script **failed to run** successfully.

### Log Output
```text
Error: Traceback (most recent call last):
  ...
  File "<exec>", line 9, in <module>
ModuleNotFoundError: No module named 'binance'
```

### Explanation of Failure
The error `ModuleNotFoundError: No module named 'binance'` indicates that the external dependency `python-binance` was not installed in the Python environment where the script was executed.

The script attempts to import `Client` from `binance.client` on line 9. Since the Python interpreter could not locate this package, the execution was aborted immediately.

### Resolution
To fix this error, install the missing package using pip as described in the **Installation** section above.