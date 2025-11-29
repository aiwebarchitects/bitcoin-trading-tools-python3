# ADX Strength Calculator (1-Minute)

## Description
`adx_strength_1min.py` is a Python script designed to calculate the Average Directional Index (ADX) for a specific cryptocurrency asset. It operates on the **1-minute timeframe** using real-time market data fetched from the Binance API.

The script performs the following operations:
1.  Accepts a trading symbol (e.g., BTC, ETH) via command-line arguments.
2.  Normalizes the symbol to ensure it ends with `USDT` (e.g., converts `BTC` to `BTCUSDT`).
3.  Connects to the Binance public API (unauthenticated) to fetch the latest 100 candlestick bars (klines).
4.  Manually implements **Wilder's Smoothing** algorithm to calculate:
    *   True Range (TR)
    *   Directional Movement (+DM, -DM)
    *   Directional Indicators (+DI, -DI)
    *   Directional Index (DX)
    *   Average Directional Index (ADX) with a period of 14.
5.  Outputs the current ADX strength, timestamp, and directional indicators to the console.

## Dependencies
This script requires Python 3 and the third-party Binance API wrapper.

*   **Python 3.x**
*   **python-binance**: A library to interact with the Binance API.

## Installation
To run this script, you must install the required dependency via pip:

```bash
pip install python-binance
```

## Usage
Run the script from the terminal, providing the target symbol using the `--symbol` argument.

### Basic Command
```bash
python adx_strength_1min.py --symbol BTC
```

### Example Output (Successful Run)
```text
ADX(14) on 1m for BTCUSDT: 25.43 at 2023-10-27T10:05:00
DI+/DI-: 18.20 / 22.15  DX: 9.79
```

## Execution Output Analysis
The provided execution logs indicate that the script **failed to run**.

### Error Log
```text
ModuleNotFoundError: No module named 'binance'
```

### Explanation
The error `ModuleNotFoundError` occurred because the script attempts to import `Client` and exceptions from the `binance` package (lines 10-11), but this package was not found in the Python environment where the script was executed.

### Solution
To fix this error, the user must install the missing library using the installation command provided above (`pip install python-binance`). Once installed, the script will be able to import the necessary modules to fetch data from Binance.