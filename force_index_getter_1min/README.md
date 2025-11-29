# force_index_getter_1min.py

## Overview

This script calculates the **Force Index (FI)** technical indicator for a specified cryptocurrency symbol. It utilizes the Binance API to fetch 1-minute candlestick (kline) data. The Force Index is a measure of the power behind a price move, calculated using the formula:

$$ \text{Force Index} = (\text{Current Close} - \text{Previous Close}) \times \text{Volume} $$

The script is designed to provide a quick snapshot of buying vs. selling pressure on a short timeframe (1-minute) and can output data in a human-readable format or a JSON structure for programmatic use.

## Features

*   **1-Minute Granularity:** Fetches high-frequency data (1m interval).
*   **Smart Symbol Resolution:** Automatically appends `USDT` to symbols if no trading pair suffix is detected (e.g., `BTC` becomes `BTCUSDT`).
*   **Configurable History:** Allows users to specify the number of candles to retrieve via the `--limit` argument.
*   **JSON Output:** Supports a `--series` flag to output the full calculated series in JSON format for integration with other tools.

## Prerequisites

The script requires Python 3 and the `python-binance` library.

```bash
pip install python-binance
```

## Usage

### Basic Usage
Run the script by providing the target symbol.

```bash
python force_index_getter_1min.py --symbol BTC
```

### Arguments

| Argument | Type | Required | Default | Description |
| :--- | :--- | :--- | :--- | :--- |
| `--symbol` | String | Yes | N/A | The trading symbol (e.g., `ETH`, `BTCUSDT`). |
| `--limit` | Integer | No | 200 | Number of 1-minute candles to fetch. |
| `--series` | Flag | No | False | If present, prints the full FI series as JSON. |

### Examples

**1. Get the latest Force Index for Ethereum (defaults to ETHUSDT):**
```bash
python force_index_getter_1min.py --symbol ETH
```

**2. Get the latest Force Index for a specific pair with a larger dataset:**
```bash
python force_index_getter_1min.py --symbol BNBBUSD --limit 500
```

**3. Output the full data series in JSON:**
```bash
python force_index_getter_1min.py --symbol BTC --series
```

## Execution Output Analysis

The script execution provided in the prompt **failed**.

### Error Log
```text
Error: Traceback (most recent call last):
  ...
  File "<exec>", line 14, in <module>
ModuleNotFoundError: No module named 'binance'
```

### Explanation
The script encountered a `ModuleNotFoundError`. This indicates that the external dependency `python-binance` is not installed in the Python environment where the script was executed.

Line 14 (`from binance.client import Client`) attempts to import the Binance client, but Python could not locate the package.

### Solution
To fix this error, install the required library using pip:

```bash
pip install python-binance
```