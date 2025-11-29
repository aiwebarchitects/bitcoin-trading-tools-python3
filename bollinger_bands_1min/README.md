# Bollinger Bands 1-Minute Fetcher

## Description
`bollinger_bands_1min.py` is a Python utility that calculates and displays the current Bollinger Bands for a specified cryptocurrency symbol. It utilizes the Binance Public API to fetch real-time market data.

The script operates on a **1-minute timeframe** and performs the following calculations:
*   **Middle Band:** 20-period Simple Moving Average (SMA).
*   **Standard Deviation:** Population standard deviation of the last 20 close prices.
*   **Upper Band:** Middle Band + (2 * Standard Deviation).
*   **Lower Band:** Middle Band - (2 * Standard Deviation).

## Features
*   **Automatic Symbol Resolution:** If a base asset is provided (e.g., `BTC`), the script defaults to the USDT pair (`BTCUSDT`) unless `BUSD` is specified.
*   **No Authentication Required:** Uses public endpoints of the Binance API.
*   **Real-time Calculation:** Fetches the most recent 20 candles to ensure up-to-date indicator values.

## Prerequisites
The script requires Python 3 and the `python-binance` third-party library.

### Installation
To install the required dependency, run:
```bash
pip install python-binance
```

## Usage
Run the script from the command line using the `--symbol` argument.

### Basic Usage
```bash
python bollinger_bands_1min.py --symbol BTCUSDT
```

### Shorthand Usage (Defaults to USDT)
```bash
python bollinger_bands_1min.py --symbol ETH
```

### Expected Output
On a successful run, the script outputs the calculated bands and the timestamp of the last close:
```text
Symbol: BTCUSDT | Interval: 1m | Time: 2023-10-27 10:00:00 UTC | Middle: 34100.50000000 | Upper: 34150.20000000 | Lower: 34050.80000000 | Last Close: 34110.00000000
```

## Execution Output Analysis
The provided execution logs indicate that the script **failed to run**.

### Error Log
```text
ModuleNotFoundError: No module named 'binance'
```

### Explanation
The error `ModuleNotFoundError` occurs because the external library `python-binance` is not installed in the Python environment where the script was executed. The script attempts to import `Client` and `BinanceAPIException` from the `binance` package on lines 19 and 20, causing the crash.

### Resolution
To fix this error, install the missing package using pip:
```bash
pip install python-binance
```