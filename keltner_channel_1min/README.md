# Keltner Channel Calculator (1-Minute Interval)

## Overview
`keltner_channel_1min.py` is a Python script designed to calculate Keltner Channel indicators using real-time market data from the Binance API. It specifically targets 1-minute candlestick intervals to provide short-term technical analysis data.

The script calculates the following components:
1.  **Middle Band:** 20-period Exponential Moving Average (EMA).
2.  **ATR:** 10-period Average True Range.
3.  **Upper Band:** Middle Band + (Multiplier × ATR).
4.  **Lower Band:** Middle Band - (Multiplier × ATR).

The output is provided in both a machine-readable JSON format and a concise human-readable summary.

## Features
- **Automatic Symbol Normalization:** Automatically appends "USDT" to common cryptocurrency symbols (e.g., "BTC" becomes "BTCUSDT").
- **Customizable Multiplier:** Allows adjustment of the channel width via command-line arguments.
- **Robust Error Handling:** Includes retry logic for API calls and validation for sufficient data points.
- **Public API Access:** Uses Binance public endpoints, requiring no API keys for execution.

## Prerequisites
The script requires Python 3 and the `python-binance` library.

### Installation
To install the required dependency, run:
```bash
pip install python-binance
```

## Usage

Run the script from the command line using the following arguments:

```bash
python keltner_channel_1min.py --symbol <SYMBOL> [options]
```

### Arguments

| Argument | Type | Required | Default | Description |
| :--- | :--- | :--- | :--- | :--- |
| `--symbol` | String | Yes | N/A | The trading pair (e.g., `BTC`, `ETHUSDT`). |
| `--multiplier` | Float | No | 2.0 | The multiplier applied to the ATR for band width. |
| `--limit` | Integer | No | 40 | Number of candles to fetch. Must be sufficient to calculate EMA(20). |

### Examples

**Basic Usage (Default settings):**
```bash
python keltner_channel_1min.py --symbol BTC
```

**Custom Multiplier and Data Limit:**
```bash
python keltner_channel_1min.py --symbol ETH --multiplier 2.5 --limit 60
```

## Output Format

The script prints a JSON object followed by a summary line.

**Example Output:**
```json
{
  "symbol": "BTCUSDT",
  "interval": "1m",
  "time_of_latest_bar": "2023-10-27 10:00:00",
  "middle": 34150.50,
  "upper": 34200.10,
  "lower": 34100.90,
  "multiplier": 2.0,
  "data_count": 40
}
BTCUSDT 1m: Middle=34150.500000, Upper=34200.100000, Lower=34100.900000
```

## Execution Analysis & Troubleshooting

### Observed Execution Output
When the script was executed in the test environment, the following error occurred:

```text
ModuleNotFoundError: No module named 'binance'
```

### Explanation of Failure
The script failed to run because the external dependency `python-binance` was not installed in the Python environment where the code was executed.

The script attempts to import `Client` and `BinanceAPIException` from the `binance` package on lines 12 and 13. Since Python could not locate this package, it raised a `ModuleNotFoundError` and terminated immediately.

### Solution
To resolve this error, install the missing library using pip before running the script:
```bash
pip install python-binance
```