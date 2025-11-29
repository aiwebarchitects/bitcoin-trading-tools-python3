# Chaikin Volatility Calculator (1-Minute Timeframe)

## Overview
`chaikin_volatility_getter_1min.py` is a Python script designed to calculate a specific volatility metric for cryptocurrency assets. It utilizes the Binance public API to fetch real-time 1-minute candlestick (kline) data.

The script computes volatility by comparing the Exponential Moving Average (EMA) of the High-Low range against the EMA of the Close price over a specified period ($N$).

## Features
- **Real-time Data:** Fetches live 1-minute market data from Binance.
- **Customizable Period:** Allows users to define the EMA period ($N$) via command-line arguments.
- **No Authentication Required:** Uses public endpoints, so no Binance API keys are needed.
- **Robust Error Handling:** Includes checks for network errors, insufficient data, and mathematical anomalies (NaN/Infinity).

## Algorithm
Based on the source code, the volatility is calculated as follows:
1. **Range Calculation:** $R = High - Low$
2. **EMA Calculation:** Computes the Exponential Moving Average (EMA) for both the Range ($R$) and the Close price over period $N$.
3. **Volatility Formula:**
   $$ \text{Volatility} = 100 \times \left( \frac{\text{EMA}(R)}{\text{EMA}(\text{Close})} - 1.0 \right) $$
   *Note: This formula calculates the percentage ratio of the average range to the average price, normalized against a baseline.*

## Prerequisites
The script requires Python 3 and the `python-binance` library.

### Installation
To install the required dependency, run:
```bash
pip install python-binance
```

## Usage
Run the script from the command line using the following arguments:

### Arguments
- `--symbol` (Required): The trading symbol (e.g., `BTC`, `ETH`). The script automatically appends `USDT` to form the pair (e.g., `BTCUSDT`).
- `--N` (Optional): The EMA period. Default is `10`.
- `--limit` (Optional): Number of candles to fetch. Default is `200`.

### Examples
**Basic Usage (BTC):**
```bash
python chaikin_volatility_getter_1min.py --symbol BTC
```

**Custom Period (ETH with N=20):**
```bash
python chaikin_volatility_getter_1min.py --symbol ETH --N 20
```

**Fetch More Data:**
```bash
python chaikin_volatility_getter_1min.py --symbol SOL --limit 500
```

## Execution Output Analysis
The provided execution logs indicate that the script **failed to run**.

### Error Log
```text
ModuleNotFoundError: No module named 'binance'
```

### Explanation
The error `ModuleNotFoundError` occurs because the external library `python-binance` is not installed in the Python environment where the script was executed. This library is necessary for the script to communicate with the Binance API.

### Solution
Install the missing package using pip:
```bash
pip install python-binance
```

## Exit Codes
The script uses specific exit codes to indicate failure points:
- `0`: Success.
- `1`: Invalid or missing symbol argument.
- `2`: Insufficient data received from API.
- `3`: Network or API connection error.
- `4`: Failed to parse OHLCV data.
- `5`: Not enough valid data after cleaning (removing NaNs).
- `6`: Calculation failure (EMA initialization issues).
- `7`: Result is invalid (NaN or Infinite).