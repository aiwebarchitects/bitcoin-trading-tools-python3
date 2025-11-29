# roc_getter_1min.py

## Overview
`roc_getter_1min.py` is a Python utility designed to calculate the current Rate of Change (ROC) for cryptocurrency assets over a 1-minute timeframe. It utilizes the Binance public API to fetch real-time candlestick (kline) data and computes the percentage change over a specified period (defaulting to 10 minutes/bars).

## Features
*   **Smart Symbol Resolution:** Automatically attempts to resolve base symbols to common trading pairs (e.g., inputting `BTC` will automatically try `BTCUSDT`, `BTCUSDC`, etc.).
*   **Configurable Period:** Allows users to define the lookback period for the ROC calculation via command-line arguments.
*   **No Authentication Required:** Uses the free, unauthenticated endpoints of the Binance API.
*   **Real-time Data:** Provides the calculated ROC percentage and the timestamp of the latest data point.

## Prerequisites
The script relies on the `python-binance` third-party library.

### Installation
To run this script, you must install the required package:
```bash
pip install python-binance
```

## Usage
Run the script from the command line using Python 3.

### Basic Usage
Calculate ROC for a symbol (defaults to a 10-minute period):
```bash
python roc_getter_1min.py --symbol BTC
```

### Custom Period
Calculate ROC with a custom lookback period (e.g., 20 minutes):
```bash
python roc_getter_1min.py --symbol ETH --roc_period 20
```

### Arguments
| Argument | Required | Default | Description |
| :--- | :---: | :---: | :--- |
| `--symbol` | Yes | N/A | The trading symbol (e.g., `BTC`, `ETHUSDT`). |
| `--roc_period` | No | 10 | The number of 1-minute bars to look back for the calculation. |

## Execution Output Analysis

### Observed Output
When the script was executed, the following error occurred:
```text
Error: Traceback (most recent call last):
  ...
  File "<exec>", line 16, in <module>
ModuleNotFoundError: No module named 'binance'
```

### Explanation of Failure
The execution failed because the Python environment where the script was run did not have the `python-binance` library installed.

1.  **Error Type:** `ModuleNotFoundError`
2.  **Missing Module:** `binance`
3.  **Cause:** The script attempts to import `Client` from `binance.client` on line 16, but the interpreter could not locate this package.

### Resolution
To fix this error, the user must install the missing dependency using pip as described in the **Prerequisites** section above. Once installed, the script will be able to communicate with the Binance API and function correctly.