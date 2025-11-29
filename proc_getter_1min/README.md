# Binance 1-Minute PROC Calculator (`proc_getter_1min.py`)

## Description
This script calculates the **Price Rate of Change (PROC)** for a specific cryptocurrency symbol using the Binance public API. It utilizes 1-minute candlestick (kline) data to compare the most recent closing price against a closing price from a specified lookback period.

**Key Features:**
*   **Timeframe:** 1-minute intervals.
*   **Symbol Normalization:** Automatically appends `USDT` if a short symbol (e.g., `BTC`) is provided.
*   **Customizable Lookback:** Users can define the period for calculation (default is 20 minutes).
*   **Error Handling:** Includes logic for network retries, insufficient data validation, and zero-division protection.

## Prerequisites
The script requires Python 3 and the `python-binance` library.

### Installation
To install the required dependency, run:
```bash
pip install python-binance
```

## Usage
Run the script from the command line using the `--symbol` argument. You may optionally specify the `--lookback` period (in minutes).

### Arguments
*   `--symbol` (Required): The trading pair (e.g., `BTC`, `ETHUSDT`).
*   `--lookback` (Optional): The number of minutes to look back for the comparison price. Default is `20`.

### Examples
**Basic Usage (Default 20-minute lookback):**
```bash
python proc_getter_1min.py --symbol BTC
```

**Custom Lookback (1 hour):**
```bash
python proc_getter_1min.py --symbol ETH --lookback 60
```

**Full Symbol Specification:**
```bash
python proc_getter_1min.py --symbol SOLUSDT
```

## Execution Output Analysis
When the script was executed in the provided environment, it produced the following error:

```text
Error: Traceback (most recent call last):
  ...
  File "<exec>", line 10, in <module>
ModuleNotFoundError: No module named 'binance'
```

### Explanation of Failure
The execution failed because the **`python-binance` library was not installed** in the Python environment where the script was run.

1.  **Error Type:** `ModuleNotFoundError`
2.  **Cause:** The script attempts to import `Client` from `binance.client` on line 10, but the interpreter could not locate the package.
3.  **Resolution:** Install the missing package using `pip install python-binance` before running the script again.