# Ulcer Index Calculator (1-Minute Interval)

**File:** `ulcer_index_getter_1min.py`

## Description
This Python script calculates the **Ulcer Index (UI)** for a specified cryptocurrency symbol using real-time market data from Binance. It utilizes a **14-period window** based on **1-minute closing prices**.

The Ulcer Index is a technical indicator that measures downside risk in terms of both the depth and duration of price declines. The script fetches the latest 14 minutes of data, computes the index, and outputs the results in both human-readable text and a machine-parsable JSON format.

### Key Features
*   **Data Source:** Fetches live kline (candlestick) data from the Binance public API.
*   **Interval:** 1-minute (`1m`) timeframe.
*   **Window:** Fixed 14-period lookback.
*   **Output:** Provides the calculated UI, the last closing price, the peak price within the window, and a timestamp.

## Prerequisites
The script requires Python 3 and the `python-binance` library.

### Installation
To install the required dependency, run:
```bash
pip install python-binance
```

## Usage
Run the script from the command line, providing the trading symbol (e.g., BTCUSDT, ETHUSDT) via the `--symbol` argument.

```bash
python ulcer_index_getter_1min.py --symbol <SYMBOL>
```

### Example
```bash
python ulcer_index_getter_1min.py --symbol BTCUSDT
```

### Output Format
The script prints human-friendly details followed by a JSON object on the last line.

**Example Output:**
```text
Symbol: BTCUSDT
UI_14m: 0.00123456
Last_Close: 26500.50000000
Peak_in_Window: 26550.00000000
{"symbol": "BTCUSDT", "ui_14": 0.00123456, "last_close": 26500.5, "peak": 26550.0, "window": 14, "timestamp": "2023-10-27T10:00:00Z"}
```

## Execution Analysis
The provided execution attempt failed. Below is an analysis of the error log.

### Error Log
```text
Error: Traceback (most recent call last):
  ...
  File "<exec>", line 11, in <module>
ModuleNotFoundError: No module named 'binance'
```

### Explanation of Failure
The script crashed with a `ModuleNotFoundError`. This indicates that the external library **`python-binance`** is not installed in the Python environment where the script was executed.

The script attempts to import `Client` from `binance.client` on line 11:
```python
from binance.client import Client
```
Because the Python interpreter could not locate this package, the execution was aborted immediately.

### Resolution
To fix this error, install the missing package using pip:
```bash
pip install python-binance
```