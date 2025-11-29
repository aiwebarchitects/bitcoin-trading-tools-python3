# EMA Calculator (1h Timeframe)

## Description
`ema_calculator_1h.py` is a command-line Python utility designed to calculate the 20-period Exponential Moving Average (EMA) for cryptocurrency assets. 

The script interfaces with the Binance Public API to retrieve the latest 50 candlesticks on a 1-hour timeframe. It processes this data to compute the EMA-20 and returns the current price alongside the calculated EMA in a machine-readable JSON format. It automatically handles symbol normalization (e.g., converting "BTC" to "BTCUSDT") and includes robust error handling for API connectivity and data parsing issues.

## Features
- **Timeframe:** 1 Hour (1h).
- **Indicator:** 20-period Exponential Moving Average (EMA).
- **Input:** Accepts base symbols (e.g., `BTC`) or full pairs (e.g., `ETHUSDT`).
- **Output:** JSON formatted string containing the symbol, timeframe, current price, and EMA value.
- **Error Handling:** Returns JSON-formatted error messages for invalid symbols, network issues, or API failures.

## Dependencies
This script requires the following external Python libraries:
- `python-binance`
- `requests`

## Usage

### Installation
Before running the script, ensure the required dependencies are installed:
```bash
pip install python-binance requests
```

### Running the Script
Run the script from the command line, passing the desired token symbol via the `--symbol` argument.

**Syntax:**
```bash
python ema_calculator_1h.py --symbol <SYMBOL>
```

**Examples:**
```bash
# Calculate for Bitcoin (defaults to BTCUSDT)
python ema_calculator_1h.py --symbol BTC

# Calculate for Ethereum
python ema_calculator_1h.py --symbol ETHUSDT
```

### Expected Output (Success)
```json
{"symbol": "BTC/USDT", "timeframe": "1h", "price": 34500.50, "ema_20": 34420.10}
```

## Execution Output Analysis

**Status:** **FAILED**

The script failed to execute successfully during the provided test run.

### Error Log
```text
Error: Traceback (most recent call last):
  ...
  File "<exec>", line 9, in <module>
ModuleNotFoundError: No module named 'binance'
```

### Explanation of Failure
The execution failed due to a `ModuleNotFoundError`. 
1.  **Line 9:** `from binance.client import Client` attempted to import the Binance client library.
2.  **Cause:** The Python environment where the script was executed does not have the `python-binance` library installed.
3.  **Result:** The Python interpreter stopped execution immediately because it could not locate the required dependency.

### Solution
To fix this error, install the missing library using pip:
```bash
pip install python-binance
```