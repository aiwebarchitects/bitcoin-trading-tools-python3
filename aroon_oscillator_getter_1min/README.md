# Aroon Oscillator Getter (1-Minute)

## Overview
`aroon_oscillator_getter_1min.py` is a Python script designed to calculate the **Aroon Oscillator** for a specific cryptocurrency trading pair using real-time data from the Binance API.

The script performs the following operations:
1.  Connects to the Binance public API (no API keys required).
2.  Fetches the last 25 candlesticks (klines) for the specified symbol on a **1-minute timeframe**.
3.  Calculates the Aroon Up and Aroon Down values based on the "High" and "Low" prices over the 25-period window.
4.  Computes the Aroon Oscillator (`Aroon Up - Aroon Down`).
5.  Outputs the result along with the UTC timestamp of the latest candle.

## Prerequisites
The script requires Python 3 and the `python-binance` library.

### Installation
To install the required dependency, run:
```bash
pip install python-binance
```

## Usage
Run the script from the command line, providing the target symbol via the `--symbol` argument. The script automatically appends "USDT" if not provided (e.g., `BTC` becomes `BTCUSDT`).

### Basic Command
```bash
python aroon_oscillator_getter_1min.py --symbol BTC
```

### Example Output (Success)
```text
Symbol: BTCUSDT | Time (UTC): 2023-10-27T10:00:00Z | Aroon Oscillator (25, 1m) = 48.0000
```

### Exit Codes
The script uses specific exit codes to indicate failure modes:
*   `0`: Success.
*   `2`: Network or Request error.
*   `3`: Invalid input (empty symbol).
*   `4`: Insufficient data (fewer than 25 candles returned).
*   `5`: Binance API specific error.

## Execution Output Analysis

When the script was executed in the provided environment, it generated the following error:

```text
Error: Traceback (most recent call last):
  ...
  File "<exec>", line 10, in <module>
ModuleNotFoundError: No module named 'binance'
```

### Explanation of Failure
The execution failed because the required third-party library, **`python-binance`**, was not installed in the Python environment where the script was run.

The Python interpreter encountered the line `from binance.client import Client` and raised a `ModuleNotFoundError`. To resolve this, the package must be installed via pip as shown in the **Installation** section above.