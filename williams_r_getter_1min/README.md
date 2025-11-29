# Williams %R (14, 1m) Fetcher

## Description
`williams_r_getter_1min.py` is a Python script designed to calculate the **Williams %R** momentum indicator for a specific cryptocurrency asset. It operates on a **1-minute timeframe** over a standard **14-period** window.

The script utilizes the Binance REST API (via the `python-binance` wrapper) to fetch real-time candlestick (kline) data. It features automatic symbol resolution (e.g., attempting to append "USDT" if a raw symbol like "BTC" is provided) and outputs the calculated indicator value, relevant price points (High, Low, Close), and a UTC timestamp.

## Prerequisites
*   Python 3.x
*   `python-binance` library

## Installation
The script relies on the `python-binance` library to communicate with the exchange. You must install this dependency before running the script:

```bash
pip install python-binance
```

## Usage
Execute the script from the command line, passing the desired asset symbol using the `--symbol` argument.

### Syntax
```bash
python williams_r_getter_1min.py --symbol <SYMBOL>
```

### Examples
**Fetch data for Bitcoin (script will attempt 'BTC' then 'BTCUSDT'):**
```bash
python williams_r_getter_1min.py --symbol BTC
```

**Fetch data for a specific pair:**
```bash
python williams_r_getter_1min.py --symbol ETHBUSD
```

## Execution Analysis
Based on the provided console logs, the execution of the script **failed**.

### Error Log
```text
Error: Traceback (most recent call last):
  ...
  File "<exec>", line 8, in <module>
ModuleNotFoundError: No module named 'binance'
```

### Explanation of Failure
The script crashed immediately upon startup due to a `ModuleNotFoundError`.

1.  **Cause:** The Python environment where the script was executed does not have the `python-binance` library installed. Line 8 (`from binance.client import Client`) failed because the interpreter could not locate the `binance` module.
2.  **Resolution:** The user must install the required library using `pip install python-binance` to fix this error.