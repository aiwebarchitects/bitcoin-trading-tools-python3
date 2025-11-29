# qstick_getter_1min.py

## Overview
This script calculates the **Q-stick momentum oscillator** for a specified cryptocurrency symbol using 1-minute candlestick data. It utilizes the Binance public API to fetch market data, computes the Typical Price (TP), and compares the latest TP against a Simple Moving Average (SMA) of the TP over a user-defined period.

The result is output as a JSON object containing the calculated Q-stick value, the timestamp, and the symbol.

## Features
- **Data Source:** Fetches real-time 1-minute klines (candlesticks) from Binance.
- **Symbol Normalization:** Automatically appends "USDT" to symbols if omitted (e.g., `BTC` becomes `BTCUSDT`).
- **Calculation:**
  - $TP = (High + Low + Close) / 3$
  - $Qstick = \frac{TP_{last} - SMA(TP, N)}{SMA(TP, N)} \times 100$
- **Output:** Standardized JSON format suitable for piping into other tools or logging.

## Prerequisites
The script requires Python 3 and the `python-binance` library.

### Installation
To install the required dependency, run:
```bash
pip install python-binance
```

## Usage
Run the script from the command line using the following arguments:

```bash
python qstick_getter_1min.py --symbol <SYMBOL> [--n <PERIOD>]
```

### Arguments
- `--symbol` (Required): The trading pair symbol (e.g., `BTC`, `ETHUSDT`).
- `--n` (Optional): The SMA period for the Typical Price calculation. Defaults to **14**.

### Examples
**Default usage (BTCUSDT, Period 14):**
```bash
python qstick_getter_1min.py --symbol BTC
```

**Custom period (ETHUSDT, Period 20):**
```bash
python qstick_getter_1min.py --symbol ETH --n 20
```

## Output Format
On success, the script prints a JSON object to `stdout`:

```json
{
    "symbol": "BTCUSDT",
    "time": "2023-10-27T10:00:00Z",
    "qstick_1m": 0.045,
    "ma_period": 14
}
```

## Execution Analysis
Based on the provided console logs, the script **failed to execute successfully**.

### Execution Log
```text
Error: Traceback (most recent call last):
  ...
  File "<exec>", line 11, in <module>
ModuleNotFoundError: No module named 'binance'
```

### Explanation of Failure
The error `ModuleNotFoundError: No module named 'binance'` indicates that the external dependency `python-binance` is not installed in the Python environment where the script was executed.

The script attempts to import `Client` from `binance.client` on line 11. Since the Python interpreter could not locate this package, the program crashed immediately before performing any logic.

**Resolution:** Install the missing package using `pip install python-binance`.