# Donchian Channel 20 (1h) Calculator

## Description
`donchian_channel_20_1h.py` is a Python script designed to perform technical analysis on cryptocurrency pairs using the Binance public API. Specifically, it calculates the **20-period Donchian Channel** based on **1-hour (1h) candlesticks**.

The script fetches historical data to determine the highest high and lowest low of the previous 20 completed periods. It then compares the latest completed candle's closing price to these bounds to detect potential breakout signals (Bullish or Bearish).

### Key Features
*   **Data Source:** Fetches real-time market data via the Binance API (no API keys required for public data).
*   **Periodicity:** Uses 1-hour candle intervals.
*   **Lookback:** Calculates the channel based on the last 20 *completed* candles.
*   **Output:** Generates both a human-readable summary string and a machine-parsable JSON object containing the channel bounds, close price, signal type, and relative distance percentage.

## Prerequisites
*   Python 3.6+
*   `python-binance` library

## Installation
To run this script, you must install the required third-party library:

```bash
pip install python-binance
```

## Usage
Run the script from the command line, providing the trading symbol via the `--symbol` argument.

### Command Syntax
```bash
python donchian_channel_20_1h.py --symbol <TRADING_PAIR>
```

### Example
```bash
python donchian_channel_20_1h.py --symbol BTCUSDT
```

## Output Format
The script prints two lines to standard output:
1.  **Human-Readable Log:** A summary of the time, channel bounds, and breakout status.
2.  **JSON Object:** Structured data suitable for piping into other tools or logs.

**Example JSON Output:**
```json
{
    "symbol": "BTCUSDT",
    "timestamp": "2023-10-27 10:00:00 UTC",
    "donchian": {
        "upper": 34500.00,
        "lower": 33900.00
    },
    "close": 34150.00,
    "signal": "none",
    "distance_pct": 0.0
}
```

## Execution Analysis
Based on the provided execution logs, the script **failed to run successfully**.

### Error Log
```text
ModuleNotFoundError: No module named 'binance'
```

### Explanation of Failure
The script encountered a `ModuleNotFoundError`. This indicates that the Python environment where the script was executed did not have the `python-binance` library installed. The script relies on this library to communicate with the Binance API.

### Resolution
To fix this error, the user must install the missing dependency using pip before running the script again:
```bash
pip install python-binance
```