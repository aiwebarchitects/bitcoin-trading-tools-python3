# ATR Calculator (1h)

## Description
`atr_calculator_1h.py` is a Python utility designed to calculate the Average True Range (ATR) volatility indicator for cryptocurrency assets. It specifically targets the **1-hour timeframe**.

The script performs the following operations:
1.  **Data Fetching:** Connects to the Binance public API (no API keys required) to retrieve recent OHLCV (Open, High, Low, Close, Volume) candlestick data.
2.  **Symbol Normalization:** Automatically appends "USDT" to symbols if a base asset is provided (e.g., inputting "BTC" converts to "BTCUSDT").
3.  **Calculation:** Computes the ATR using **Wilder's Smoothing (RMA)** over a standard 14-period lookback.
4.  **Formatting:** Dynamically formats the output precision based on the asset's value (e.g., 6 decimal places for low-value assets, 2 for high-value assets).

## Dependencies
This script requires the `python-binance` library to interact with the Binance API.

```bash
pip install python-binance
```

## Usage
Run the script from the command line, passing the desired trading symbol via the `--symbol` argument.

### Basic Syntax
```bash
python atr_calculator_1h.py --symbol <SYMBOL>
```

### Examples
Calculate ATR for Bitcoin (defaults to BTCUSDT):
```bash
python atr_calculator_1h.py --symbol BTC
```

Calculate ATR for Ethereum (explicit pair):
```bash
python atr_calculator_1h.py --symbol ETHUSDT
```

## Execution Output Analysis

### Observed Output
When the script was executed, the following error occurred:
```text
Error: Traceback (most recent call last):
  ...
  File "<exec>", line 8, in <module>
ModuleNotFoundError: No module named 'binance'
```

### Explanation of Failure
The execution failed due to a **missing dependency**.

The error `ModuleNotFoundError: No module named 'binance'` indicates that the Python environment attempting to run the script did not have the `python-binance` library installed. The script attempts to import `Client` and exceptions from the `binance` package on lines 8 and 9, causing the crash before any logic could be executed.

To resolve this, the user must install the required package using `pip install python-binance`.