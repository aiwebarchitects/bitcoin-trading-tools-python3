# trix_getter_1min.py - Binance TRIX Indicator (1m)

## Description
This script calculates the **TRIX (Triple Exponential Average)** momentum indicator for a specific cryptocurrency symbol using 1-minute candlestick data. It utilizes the Binance public API to fetch historical price data and computes the triple smoothed EMA rate of change.

The TRIX indicator is used to identify oversold and overbought markets, as well as momentum divergences. This script specifically uses a period of **15** for the EMA calculations.

### Key Features
*   **Data Source:** Fetches real-time 1-minute klines (candlesticks) from Binance.
*   **Symbol Normalization:** Automatically appends `USDT` if a raw symbol (e.g., `BTC`) is provided.
*   **Calculation:** Computes the Triple Exponential Moving Average (TRIX) and the change in value from the previous interval.
*   **Output:** Displays the TRIX percentage, the change value, and the UTC timestamp of the calculation.

## Prerequisites
The script requires Python 3 and the `python-binance` library.

### Installation
To install the required dependency, run:
```bash
pip install python-binance
```

## Usage
Run the script from the command line, providing the target symbol via the `--symbol` argument.

### Command Syntax
```bash
python trix_getter_1min.py --symbol <SYMBOL>
```

### Examples
Fetch TRIX for Bitcoin (BTCUSDT):
```bash
python trix_getter_1min.py --symbol BTC
```

Fetch TRIX for Ethereum (ETHUSDT):
```bash
python trix_getter_1min.py --symbol ETHUSDT
```

## Execution Output Analysis

When attempting to run the script in the provided environment, the execution failed with the following error:

```text
Error: Traceback (most recent call last):
  ...
  File "<exec>", line 11, in <module>
ModuleNotFoundError: No module named 'binance'
```

### Explanation of Failure
The script failed because the external dependency **`python-binance`** was not installed in the Python environment where the script was executed. The script attempts to import `Client` and `BinanceAPIException` from the `binance` package on line 11, resulting in a `ModuleNotFoundError`.

### Resolution
To fix this error, the user must install the missing library using pip before running the script again:
```bash
pip install python-binance
```