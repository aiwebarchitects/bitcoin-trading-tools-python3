# RSI Calculator (1h Timeframe)

## Overview
`rsi_calculator_1h.py` is a Python script designed to calculate the 14-period Relative Strength Index (RSI) for cryptocurrency assets. It fetches historical price data from the Binance public API using the 1-hour timeframe.

The script utilizes **Wilder's Smoothing Method** to calculate the RSI and interprets the result to categorize the market condition as:
*   **OVERBOUGHT:** RSI ≥ 70
*   **OVERSOLD:** RSI ≤ 30
*   **NEUTRAL:** 30 < RSI < 70

## Features
*   **Automated Data Fetching:** Retrieves the last 100 candlesticks (k-lines) from Binance to ensure accurate smoothing.
*   **Symbol Normalization:** Automatically appends "USDT" if a short symbol (e.g., "BTC") is provided.
*   **No API Keys Required:** Uses public endpoints, so no authentication is necessary.
*   **Error Handling:** Includes robust handling for network errors, invalid symbols, and insufficient data.

## Prerequisites
The script requires Python 3 and the `python-binance` library.

### Installation
To install the required dependency, run:
```bash
pip install python-binance
```

## Usage
Run the script from the command line, specifying the target symbol using the `--symbol` argument.

### Basic Command
```bash
python rsi_calculator_1h.py --symbol BTC
```

### Example Output
```text
2023-10-27 14:00:00 | BTCUSDT | RSI: 45.23 | NEUTRAL
```

### Arguments
*   `--symbol`: (Required) The trading symbol (e.g., `ETH`, `SOL`, `BTCUSDT`).

## Execution Output Analysis
Based on the provided console logs, the execution of the script **failed**.

### Error Log
```text
Error: Traceback (most recent call last):
  ...
  File "<exec>", line 9, in <module>
ModuleNotFoundError: No module named 'binance'
```

### Explanation of Failure
The script crashed with a `ModuleNotFoundError`. This indicates that the external library `python-binance` is not installed in the Python environment where the script was executed.

Line 9 of the source code attempts to import the client:
```python
from binance.client import Client
```
Because the Python interpreter could not locate this package, the script terminated immediately before performing any logic. To fix this, the user must install the package via pip as described in the **Installation** section above.