# rvi_getter_1min.py - Relative Vigor Index Calculator

This Python script calculates the **Relative Vigor Index (RVI)** for a specified cryptocurrency symbol using 1-minute candlestick data. It utilizes the Binance public API to fetch market data and computes the index based on the difference between closing and opening prices over a defined window.

## Description

The script performs the following operations:
1.  **Symbol Resolution:** Accepts a symbol (e.g., "BTC") and defaults to a USDT pair (e.g., "BTCUSDT") if no suffix is provided.
2.  **Data Fetching:** Retrieves the most recent 1-minute klines (candles) from Binance using the `python-binance` library. No API keys are required as it uses public endpoints.
3.  **Calculation:** Computes the RVI using the formula:
    $$ RVI = 100 \times \frac{\text{SMA}(\text{Close} - \text{Open})}{\text{SMA}(|\text{Close} - \text{Open}|)} $$
4.  **Output:** Prints the calculated RVI value and the timestamp of the last candle to the console.

## Prerequisites

*   Python 3.x
*   `python-binance` library

## Installation

To run this script, you must install the required third-party library:

```bash
pip install python-binance
```

## Usage

Run the script from the command line using the following arguments:

```bash
python rvi_getter_1min.py --symbol <SYMBOL> [--n <NUMBER_OF_CANDLES>]
```

### Arguments
*   `--symbol` (Required): The trading symbol (e.g., `BTC`, `ETHUSDT`).
*   `--n` (Optional): The number of candles to use for the calculation window. Defaults to **10**.

### Examples

**Default usage (BTCUSDT, 10 candles):**
```bash
python rvi_getter_1min.py --symbol BTC
```

**Custom usage (ETHUSDT, 20 candles):**
```bash
python rvi_getter_1min.py --symbol ETH --n 20
```

## Execution Output Analysis

When the script was executed in the provided environment, it resulted in a **failure**.

### Console Logs
```text
Error: Traceback (most recent call last):
  File "/lib/python311.zip/_pyodide/_base.py", line 573, in eval_code_async
    await CodeRunner(
  File "/lib/python311.zip/_pyodide/_base.py", line 393, in run_async
    coroutine = eval(self.code, globals, locals)
                ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "<exec>", line 16, in <module>
ModuleNotFoundError: No module named 'binance'
```

### Explanation of Failure
The script failed with a `ModuleNotFoundError`.

*   **Cause:** The script attempts to import `Client` from the `binance.client` module (line 16: `from binance.client import Client`). However, the `python-binance` package was not installed in the Python environment where the code was executed.
*   **Resolution:** The user must install the dependency via pip (`pip install python-binance`) before running the script.