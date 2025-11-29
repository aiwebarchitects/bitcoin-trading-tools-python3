# Binance 1-Minute CCI Retriever (`cci_getter_1min.py`)

## Overview
This script retrieves the current Commodity Channel Index (CCI) for a specified cryptocurrency symbol using the Binance REST API. It operates on a **1-minute timeframe**, providing high-frequency technical analysis data without requiring API authentication keys.

## Features
*   **Symbol Resolution:** Automatically attempts to resolve symbols. If `BTC` is provided, it checks for `BTCUSDT` first, falling back to the raw input if the USDT pair is unavailable.
*   **No Authentication Required:** Uses Binance's public market data endpoints.
*   **Custom CCI Calculation:**
    *   Fetches the last 21 one-minute klines (candlesticks).
    *   Calculates the Typical Price (TP) for all 21 periods.
    *   Uses the **first 20** periods to calculate the Simple Moving Average (SMA) and Mean Deviation.
    *   Calculates the CCI for the **21st (most recent)** period against the statistics of the previous 20.
*   **Formatted Output:** Displays Symbol, Interval, calculated CCI, and the UTC timestamp of the data.

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
python cci_getter_1min.py --symbol <SYMBOL>
```

### Examples
**Fetch CCI for Bitcoin (defaults to BTCUSDT):**
```bash
python cci_getter_1min.py --symbol BTC
```

**Fetch CCI for Ethereum explicitly:**
```bash
python cci_getter_1min.py --symbol ETHUSDT
```

## Technical Details
### Calculation Logic
1.  **Data Fetch:** Retrieves 21 candles (1-minute interval).
2.  **Typical Price (TP):** $TP = (High + Low + Close) / 3$
3.  **Windowing:**
    *   `tp_window`: The first 20 TPs (historical context).
    *   `tp_last`: The 21st TP (current price action).
4.  **Statistics:**
    *   $SMA$: Average of `tp_window`.
    *   $MeanDev$: Mean Absolute Deviation of `tp_window`.
5.  **CCI Formula:**
    $$CCI = \frac{TP_{last} - SMA}{0.015 \times MeanDev}$$

## Execution Output Analysis
When the script was executed in the provided environment, it resulted in a **failure**.

### Error Log
```text
Error: Traceback (most recent call last):
  ...
  File "<exec>", line 14, in <module>
ModuleNotFoundError: No module named 'binance'
```

### Explanation
The script failed with a `ModuleNotFoundError`. This indicates that the external library `python-binance` is not installed in the Python environment where the script was executed.

**Solution:** Install the missing package using `pip install python-binance` before running the script.