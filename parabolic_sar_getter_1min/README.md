# Parabolic SAR Getter (1-Minute Timeframe)

## Description
`parabolic_sar_getter_1min.py` is a Python script designed to calculate the Parabolic SAR (Stop and Reverse) technical indicator for cryptocurrency pairs. It utilizes the Binance public API to fetch 1-minute candlestick (kline) data and performs a custom calculation of the SAR value without relying on external technical analysis libraries like TA-Lib.

**Key Features:**
*   **Timeframe:** Hardcoded to 1-minute intervals.
*   **Algorithm:** Implements the standard Parabolic SAR algorithm with an Acceleration Factor (AF) start/increment of 0.02 and a maximum of 0.20.
*   **Output:** Returns a JSON object containing the calculated SAR, current trend direction ("up" or "down"), and the timestamp.
*   **Authentication:** Uses the unauthenticated endpoints of the Binance API (no API keys required).

## Prerequisites
The script requires Python 3 and the `python-binance` library.

To install the required dependency:
```bash
pip install python-binance
```

## Usage
Run the script from the command line, specifying the target trading symbol.

### Arguments
*   `--symbol` (Required): The trading pair symbol (e.g., `BTCUSDT`, `ETHUSDT`).
*   `--limit` (Optional): The number of historical candles to fetch for the calculation. Defaults to 500.

### Example Commands
**Basic usage:**
```bash
python parabolic_sar_getter_1min.py --symbol BTCUSDT
```

**Specifying a data limit:**
```bash
python parabolic_sar_getter_1min.py --symbol ETHUSDT --limit 1000
```

## Output Format
On success, the script prints a single line of JSON to `stdout`:

```json
{
  "symbol": "BTCUSDT",
  "timeframe": "1m",
  "sar": 26500.50,
  "trend": "up",
  "timestamp": "2023-10-27T10:00:00Z"
}
```

## Execution Output Analysis
The provided execution logs indicate that the script **failed to run successfully**.

### Error Log
```text
Error: Traceback (most recent call last):
  ...
  File "<exec>", line 11, in <module>
ModuleNotFoundError: No module named 'binance'
```

### Explanation of Failure
The script crashed with a `ModuleNotFoundError`. This occurred because the external dependency `python-binance` was not installed in the Python environment where the script was executed.

Line 11 of the source code attempts to import the client:
```python
from binance.client import Client
```
Since Python could not locate the `binance` package, the execution terminated immediately. To resolve this, the user must install the package via pip as described in the **Prerequisites** section.