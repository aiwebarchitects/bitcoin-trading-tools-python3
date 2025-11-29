# Vortex Indicator (1-min) Fetcher

## Overview
`vortex_indicator_getter_1min.py` is a Python utility designed to calculate the **Vortex Indicator (VI)** for a specific cryptocurrency pair. It utilizes the Binance public API to fetch the most recent 1-minute candlestick (kline) data and computes both the positive (VI+) and negative (VI-) vortex components over a 14-period window.

The script outputs the results in a structured JSON format, making it ideal for integration with trading bots, monitoring dashboards, or data analysis pipelines.

## Features
- **Timeframe:** 1-minute interval (`1m`).
- **Period:** Standard 14-period calculation.
- **Data Source:** Binance Public API (No API keys required).
- **Symbol Resolution:** Automatically appends `USDT` if the user provides a base symbol (e.g., `BTC` becomes `BTCUSDT`).
- **Output:** JSON string containing the VI values and the timestamp of the calculation.

## Prerequisites
The script requires Python 3 and the `python-binance` library.

### Installation
To install the required dependency, run:
```bash
pip install python-binance
```

## Usage
Run the script from the command line, specifying the target trading symbol.

### Command Syntax
```bash
python vortex_indicator_getter_1min.py --symbol <SYMBOL>
```

### Examples
Fetch data for Bitcoin (defaults to BTCUSDT):
```bash
python vortex_indicator_getter_1min.py --symbol BTC
```

Fetch data for Ethereum explicitly:
```bash
python vortex_indicator_getter_1min.py --symbol ETHUSDT
```

## Output Format
On success, the script prints a JSON object to `stdout`:

```json
{
    "symbol": "BTCUSDT",
    "interval": "1m",
    "periods": 14,
    "vi_plus": 1.12345,
    "vi_minus": 0.98765,
    "as_of": "2023-10-27T10:00:00Z"
}
```

## Execution Analysis
Based on the provided execution logs, the script failed to run successfully.

### Error Log
```text
ModuleNotFoundError: No module named 'binance'
```

### Explanation of Failure
The script encountered a **`ModuleNotFoundError`**. This indicates that the external dependency `python-binance` is not installed in the Python environment where the script was executed.

The script imports `Client` from `binance.client` on line 11. Since the Python interpreter could not locate this package, execution terminated immediately.

### Resolution
To fix this error, install the missing library using pip:
```bash
pip install python-binance
```