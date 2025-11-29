# stddev_getter_1min.py

## Overview
`stddev_getter_1min.py` is a Python utility designed to calculate the **sample standard deviation** of 1-minute closing prices for a specified cryptocurrency. It serves as a tool for assessing short-term market volatility.

The script performs the following operations:
1.  **Symbol Normalization:** Automatically converts inputs like `BTC` or `BTCUSD` to the standard Binance format `BTCUSDT`.
2.  **Data Retrieval:** Connects to the Binance public API (no API keys required) to fetch the most recent 1-minute candlestick (kline) data.
3.  **Statistical Calculation:** Computes the sample standard deviation of the closing prices using a numerically stable algorithm.
4.  **Formatted Output:** Prints the result in a structured, pipe-delimited format for easy parsing by other tools.

## Dependencies
This script requires the `python-binance` library.

```bash
pip install python-binance
```

## Usage

Run the script from the command line using the following arguments:

### Arguments
*   `--symbol` (Required): The trading symbol (e.g., `BTC`, `ETH`, `BTCUSDT`).
*   `--window` (Optional): The number of 1-minute intervals to analyze. Defaults to `20`.

### Examples

**1. Calculate volatility for Bitcoin (default 20 minutes):**
```bash
python stddev_getter_1min.py --symbol BTC
```

**2. Calculate volatility for Ethereum over the last hour (60 minutes):**
```bash
python stddev_getter_1min.py --symbol ETH --window 60
```

### Output Format
On success, the script outputs a single line to `stdout`:
```text
stddev_1min | symbol=BTCUSDT | window=20 | stddev=12.3456
```

## Execution Output Analysis

The following output was observed during the execution attempt:

```text
Error: Traceback (most recent call last):
  File "/lib/python311.zip/_pyodide/_base.py", line 573, in eval_code_async
    await CodeRunner(
  File "/lib/python311.zip/_pyodide/_base.py", line 393, in run_async
    coroutine = eval(self.code, globals, locals)
                ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "<exec>", line 9, in <module>
ModuleNotFoundError: No module named 'binance'
```

### Explanation of Failure
The execution failed due to a **`ModuleNotFoundError`**.

1.  **Cause:** The Python environment attempting to run the script did not have the external library `python-binance` installed. The script attempts to import `Client` from `binance.client` on line 9, which triggered the crash.
2.  **Resolution:** To fix this error, the dependency must be installed in the execution environment using `pip install python-binance`.