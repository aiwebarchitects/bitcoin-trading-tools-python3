# Momentum Getter (1-Minute Timeframe)

## Overview
`momentum_getter_1min.py` is a Python script designed to calculate the **Momentum (Rate of Change)** for a specific cryptocurrency symbol on a **1-minute timeframe**. It utilizes the Binance REST API to fetch historical candlestick data (klines) and computes the percentage change over a defined lookback period.

### Key Features
*   **Data Source:** Binance Public API (No authentication required).
*   **Timeframe:** 1-minute candles.
*   **Metric:** Rate of Change (ROC) with a default lookback of 10 periods ($n=10$).
*   **Robustness:** Includes retry logic with exponential backoff for network errors and validates data integrity (checks for non-numeric values and zero-division scenarios).
*   **Smart Symbol Handling:** Automatically appends "USDT" to base symbols (e.g., inputting "BTC" converts to "BTCUSDT").

## Algorithm
The script calculates momentum using the following formula:

$$
ROC = \left( \frac{\text{Close}_{current} - \text{Close}_{n}}{\text{Close}_{n}} \right) \times 100
$$

Where:
*   $\text{Close}_{current}$ is the closing price of the most recent candle.
*   $\text{Close}_{n}$ is the closing price 10 minutes ago.

## Dependencies
The script requires the following third-party Python library:
*   `python-binance`

## Usage

### 1. Installation
Before running the script, ensure the required library is installed:
```bash
pip install python-binance
```

### 2. Execution
Run the script from the command line, passing the target symbol via the `--symbol` argument.

**Basic Usage:**
```bash
python momentum_getter_1min.py --symbol BTC
```

**Explicit Pair Usage:**
```bash
python momentum_getter_1min.py --symbol ETHUSDT
```

### 3. Expected Output
On success, the script prints the calculated momentum and the timestamp of the latest candle:
```text
BTCUSDT | Momentum 1m (n=10) = 0.15% as of 2023-10-27 14:30:00 UTC
```

## Execution Output Analysis

During the provided execution attempt, the script failed with the following error:

```text
Error: Traceback (most recent call last):
  ...
  File "<exec>", line 20, in <module>
ModuleNotFoundError: No module named 'binance'
```

### Explanation of Failure
The script crashed because the **`python-binance` library was not installed** in the Python environment where the code was executed.

The error `ModuleNotFoundError: No module named 'binance'` indicates that the Python interpreter could not locate the `binance` package, which is imported on line 20 (`from binance.client import Client`).

### Resolution
To fix this error, install the missing dependency using pip:
```bash
pip install python-binance
```