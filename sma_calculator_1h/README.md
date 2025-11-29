# SMA Calculator (1h Timeframe)

## Description
`sma_calculator_1h.py` is a Python utility designed to calculate the 200-period Simple Moving Average (SMA) for a specific cryptocurrency trading pair on the 1-hour timeframe.

The script performs the following operations:
1.  Accepts a trading symbol via command-line arguments (e.g., BTC, ETHUSDT).
2.  Normalizes the symbol (automatically appends 'USDT' if a short symbol like 'BTC' is provided).
3.  Connects to the Binance Public API (no authentication required).
4.  Retrieves the most recent 200 candlesticks (klines) for the 1-hour interval.
5.  Calculates the arithmetic mean of the closing prices.
6.  Outputs the result as a JSON object.

## Prerequisites
This script relies on the third-party `python-binance` library.

### Installation
To run this script, you must install the required dependency:

```bash
pip install python-binance
```

## Usage

Run the script from the command line, specifying the target symbol using the `--symbol` flag.

### Basic Command
```bash
python sma_calculator_1h.py --symbol BTC
```

### Explicit Pair
```bash
python sma_calculator_1h.py --symbol ETHUSDT
```

## Output Format

On success, the script prints a JSON object to standard output:

```json
{
    "symbol": "BTCUSDT",
    "sma_200_1h": 26500.12345678
}
```

On failure (e.g., invalid symbol or network error), it outputs a JSON error message:

```json
{
    "error": "API Error",
    "message": "APIError(code=-1121): Invalid symbol.",
    "symbol": "INVALIDUSDT"
}
```

## Execution Analysis

Based on the provided console logs, the script **failed to execute successfully**.

### Error Log
```text
ModuleNotFoundError: No module named 'binance'
```

### Explanation of Failure
The execution environment threw a `ModuleNotFoundError`. This indicates that the script attempted to import the `binance` module (specifically `from binance.client import Client`), but Python could not find this library in the current environment.

**Reason:** The `python-binance` package was not installed in the environment where the script was executed.

**Solution:** Install the missing dependency using `pip install python-binance` before running the script.