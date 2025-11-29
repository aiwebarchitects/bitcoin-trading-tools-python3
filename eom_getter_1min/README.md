# Ease of Movement (EOM) Calculator (1-Minute Timeframe)

## Title
**eom_getter_1min.py**

## Description
This Python script computes the **Ease of Movement (EOM)** technical indicator for a specified cryptocurrency symbol. It operates on the **1-minute timeframe** by fetching real-time candlestick (kline) data from the **Binance Public API**.

The script performs the following operations:
1.  Accepts a base asset symbol (e.g., BTC, ETH) via command-line arguments.
2.  Automatically appends "USDT" to the symbol if not provided (e.g., `BTC` becomes `BTCUSDT`).
3.  Fetches the most recent $N+1$ candles to calculate $N$ EOM data points.
4.  Computes EOM using the formula: `((Midpoint_Current - Midpoint_Prev) * (High - Low)) / Volume`.
5.  Outputs the data in either a human-readable summary or a structured JSON format.

## Prerequisites & Installation
The script relies on the `python-binance` library to interact with the exchange API.

To install the required dependency, run:
```bash
pip install python-binance
```

## Usage
Run the script from the command line using the following arguments:

### Arguments
*   `--symbol` (Required): The trading symbol base asset (e.g., `BTC`, `ETH`).
*   `--limit` (Optional): The number of candles to look back (default: 50).
*   `--json` (Optional): If set, outputs the result in JSON format.

### Examples

**1. Basic Usage (Human-Readable Output):**
```bash
python eom_getter_1min.py --symbol BTC
```

**2. Custom Lookback Limit:**
```bash
python eom_getter_1min.py --symbol ETH --limit 100
```

**3. JSON Output (Useful for piping to other tools):**
```bash
python eom_getter_1min.py --symbol SOL --json
```

## Execution Output Analysis

### Observed Output
When the script was executed in the provided environment, the following error occurred:
```text
Error: Traceback (most recent call last):
  ...
  File "<exec>", line 12, in <module>
ModuleNotFoundError: No module named 'binance'
```

### Explanation of Failure
The execution failed because the required third-party library, **`python-binance`**, was not installed in the Python environment where the script was run.

The error `ModuleNotFoundError: No module named 'binance'` indicates that the Python interpreter could not locate the package required to import `Client` and exceptions in line 12:
```python
from binance.client import Client
```

To resolve this, the environment must have internet access and the ability to install packages via `pip`. Once installed, the script will be able to connect to the Binance API and retrieve the necessary market data.