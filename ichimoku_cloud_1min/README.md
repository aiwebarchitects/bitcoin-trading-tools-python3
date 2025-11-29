# Ichimoku Cloud 1-Minute Signal Generator

## Description
`ichimoku_cloud_1min.py` is a Python script designed to perform technical analysis on cryptocurrency pairs using the **Ichimoku Cloud** indicator. It utilizes the Binance public API to fetch real-time 1-minute candlestick data (klines) and calculates key Ichimoku components to determine market trends and potential entry/exit signals.

The script outputs both a human-readable summary and a machine-parseable JSON block, making it suitable for standalone use or integration into larger trading bots.

### Key Features
*   **Timeframe:** Hardcoded to 1-minute intervals for high-frequency analysis.
*   **Data Source:** Binance Public API (no API keys required for public market data).
*   **Calculated Indicators:**
    *   **Tenkan-sen (Conversion Line):** 9-period high/low average.
    *   **Kijun-sen (Base Line):** 26-period high/low average.
    *   **Senkou Span A (Leading Span A):** Average of Tenkan and Kijun.
    *   **Senkou Span B (Leading Span B):** 52-period high/low average.
    *   **Chikou Span (Lagging Span):** Closing price plotted 26 periods behind.
*   **Signal Detection:**
    *   Identifies Tenkan/Kijun crossovers (Golden Cross/Death Cross).
    *   Determines price position relative to the Cloud (Kumo).
    *   Determines Cloud trend (Bullish/Bearish).

## Prerequisites
The script requires Python 3 and the `python-binance` library.

### Installation
To install the required dependency, run:
```bash
pip install python-binance
```

## Usage
Run the script from the command line. You can specify the target symbol using the `--symbol` argument.

### Basic Usage (Default: BTCUSDT)
```bash
python ichimoku_cloud_1min.py
```

### Specifying a Symbol
You can provide a base symbol (e.g., `ETH`) or a full pair (e.g., `ETHUSDT`). The script automatically appends "USDT" to 3-6 character base symbols.
```bash
python ichimoku_cloud_1min.py --symbol ETH
# OR
python ichimoku_cloud_1min.py --symbol SOLUSDT
```

## Output Format
The script prints analysis to `stdout` in two sections:

1.  **Human-Readable Text:** Lists current prices, indicator values, and signals.
2.  **JSON Block:** A structured object wrapped between `JSON_OUTPUT_START` and `JSON_OUTPUT_END` tags containing the exact calculated values.

**Example JSON Structure:**
```json
{
  "symbol": "BTCUSDT",
  "timeframe": "1m",
  "last_price": 64000.50,
  "tenkan": 64010.00,
  "kijun": 63990.00,
  "price_position": "Above cloud",
  "signal": "TENKAN_KIJUN_CROSS_UP"
  ...
}
```

## Execution Output Analysis
The provided execution logs indicate that the script **failed to run successfully**.

### Error Log
```text
ModuleNotFoundError: No module named 'binance'
```

### Explanation
The error `ModuleNotFoundError` occurs because the external library `python-binance` is not installed in the Python environment where the script was executed. The script attempts to import `Client` from `binance.client` on line 11, but Python cannot locate this package.

### Solution
To fix this error, the user must install the missing dependency using pip:
```bash
pip install python-binance
```