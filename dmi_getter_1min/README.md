# dmi_getter_1min.py

## Overview
`dmi_getter_1min.py` is a Python script designed to fetch real-time market data from the Binance public API and calculate the Directional Movement Index (DMI) for a specific cryptocurrency on a 1-minute timeframe.

The script computes three key technical indicators using Wilder's method over a 14-period window:
1.  **+DI** (Positive Directional Indicator)
2.  **-DI** (Negative Directional Indicator)
3.  **DMI** (Directional Movement Index / ADX component)

## Features
- **Real-time Data:** Fetches the latest 15 one-minute klines (candles) from Binance.
- **Automatic Pairing:** Automatically appends `USDT` to the symbol if not provided (e.g., `BTC` becomes `BTCUSDT`).
- **No Authentication:** Uses Binance's public endpoints, so no API keys are required.
- **Standard Calculation:** Implements Wilder’s smoothing method for DMI calculation.

## Prerequisites
The script requires Python 3 and the `python-binance` library.

### Installation
To install the required dependency, run:
```bash
pip install python-binance
```

## Usage
Run the script from the command line. You can specify a target symbol using the `--symbol` argument.

### Default Execution (BTCUSDT)
If no symbol is provided, the script defaults to Bitcoin (BTC).
```bash
python dmi_getter_1min.py
```

### Specifying a Symbol
To calculate DMI for Ethereum (ETH):
```bash
python dmi_getter_1min.py --symbol ETH
```
*Note: The script will automatically convert `ETH` to `ETHUSDT`.*

To specify a full pair name:
```bash
python dmi_getter_1min.py --symbol BNBUSDT
```

## Output Format
On successful execution, the script prints the calculated values to the console:
```text
Symbol: BTCUSDT
Timeframe: 1m
+DI: 24.50
-DI: 12.30
DMI: 33.15
As of: 2023-10-27 10:00:00 UTC
```

## Execution Analysis
Based on the provided execution logs, the script failed to run successfully.

### Error Log
```text
ModuleNotFoundError: No module named 'binance'
```

### Explanation of Failure
The script encountered a `ModuleNotFoundError` because the required third-party library, `python-binance`, was not installed in the Python environment where the script was executed.

The script attempts to import `Client` from `binance.client` on line 15:
```python
from binance.client import Client
```
Since Python could not locate this module, the execution was aborted immediately.

### Resolution
To fix this error, install the missing library using pip:
```bash
pip install python-binance
```