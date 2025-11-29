# mfi_getter_1min.py

## Overview
`mfi_getter_1min.py` is a Python utility designed to calculate the **Money Flow Index (MFI)** for a specified cryptocurrency asset. It utilizes the Binance public API to fetch market data on a **1-minute timeframe**.

The script calculates the MFI over a standard period of **14** intervals. It outputs the result as a JSON object, making it suitable for integration into larger trading bots, data pipelines, or monitoring dashboards.

## Features
- **Real-time Data:** Fetches the latest OHLCV (Open, High, Low, Close, Volume) data from Binance.
- **1-Minute Precision:** Specifically targets the 1-minute (`1m`) Kline interval.
- **JSON Output:** Returns structured JSON data containing the calculated MFI, timestamp, and status.
- **Error Handling:** Gracefully handles API exceptions and insufficient data by returning JSON error payloads.

## Dependencies
This script requires the `python-binance` library to interact with the Binance API.

```bash
pip install python-binance
```

## Usage

Run the script from the command line, providing the base symbol via the `--symbol` argument. The script automatically appends "USDT" to the provided symbol (e.g., providing `BTC` results in querying `BTCUSDT`).

### Command Syntax
```bash
python mfi_getter_1min.py --symbol <SYMBOL>
```

### Example
To get the MFI for Bitcoin (BTC):
```bash
python mfi_getter_1min.py --symbol BTC
```

## Output Format

The script prints a single line of JSON to the standard output.

### Success Response
```json
{
  "symbol": "BTC",
  "interval": "1m",
  "period": 14,
  "mfi": 56.2341,
  "timestamp": "2023-10-27T10:00:00.000000+00:00",
  "status": "success"
}
```

### Error Response
```json
{
  "status": "error",
  "error": "APIError(code=-1121): Invalid symbol."
}
```

## Execution Output Analysis

Based on the provided console logs, the execution of the script **failed**.

### Log Output
```text
Error: Traceback (most recent call last):
  ...
  File "<exec>", line 10, in <module>
ModuleNotFoundError: No module named 'binance'
```

### Explanation of Failure
The script crashed with a `ModuleNotFoundError`. This indicates that the required third-party library, `python-binance`, is not installed in the Python environment where the script was executed.

The Python interpreter reached line 10 (`from binance.client import Client`) and failed to locate the `binance` package.

### Resolution
To fix this error, install the missing dependency using pip:

```bash
pip install python-binance
```