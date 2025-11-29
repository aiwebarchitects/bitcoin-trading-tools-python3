# Binance Intraday VWAP Calculator (15min)

## Overview
`vwap_tracker_15min.py` is a Python command-line utility designed to calculate the **Volume Weighted Average Price (VWAP)** for cryptocurrency assets using the Binance public API.

The script calculates the VWAP for the current trading session (starting at 00:00 UTC) based on **15-minute candlestick (kline) data**. It outputs the result in a structured JSON format, making it suitable for integration into trading bots, dashboards, or data analysis pipelines.

## Features
*   **Intraday Calculation:** Resets calculation at 00:00 UTC daily.
*   **Smart Symbol Resolution:** Automatically appends "USDT" to short symbols (e.g., inputting `BTC` resolves to `BTCUSDT`).
*   **Public API Access:** Uses unauthenticated endpoints (no API keys required).
*   **JSON Output:** Returns parsed data including the calculated VWAP, session start time, and candle count.
*   **Error Handling:** Includes specific handling for Binance API errors and network issues.

## Prerequisites
The script requires Python 3 and the `python-binance` library.

### Installation
To install the required dependency, run:
```bash
pip install python-binance
```

## Usage
Run the script from the terminal, providing the target trading symbol via the `--symbol` argument.

### Basic Command
```bash
python vwap_tracker_15min.py --symbol BTC
```

### Arguments
| Argument | Required | Description | Example |
| :--- | :---: | :--- | :--- |
| `--symbol` | Yes | The trading pair symbol. If a short ticker (e.g., ETH) is provided, the script defaults to USDT pairing. | `ETH`, `BTCUSDT`, `SOL` |

## Output Format
On success, the script prints a JSON object to `stdout`:

```json
{
    "symbol": "BTCUSDT",
    "timeframe": "15m",
    "vwap": 64230.5512,
    "session_start": "2023-10-27 00:00:00 UTC",
    "candles_analyzed": 45
}
```

## Execution Analysis
Based on the provided execution logs, the script **failed to run successfully**.

### Observed Error
```text
ModuleNotFoundError: No module named 'binance'
```

### Explanation
The error indicates that the external dependency `python-binance` is not installed in the Python environment where the script was executed. The script attempts to import `Client` and exceptions from `binance`, but the interpreter could not locate the package.

### Resolution
To fix this error, install the missing library using pip:
```bash
pip install python-binance
```