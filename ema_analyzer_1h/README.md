# EMA Analyzer (1h Timeframe)

**File:** `ema_analyzer_1h.py`

## Description
This Python script performs technical analysis on cryptocurrency pairs using data from the Binance public API. Specifically, it calculates the **50-period** and **200-period Exponential Moving Averages (EMA)** on the **1-hour timeframe**.

Key features include:
*   **Data Fetching:** Retrieves the last 300 candles of 1-hour kline data from Binance.
*   **Symbol Normalization:** Automatically appends 'USDT' to the symbol if no pairing is specified (e.g., inputting `BTC` becomes `BTCUSDT`).
*   **Technical Calculation:** Uses `pandas` to compute EMAs based on closing prices.
*   **Trend Analysis:** Compares EMA 50 vs. EMA 200 to determine if the trend is "Bullish" or "Bearish".
*   **Signal Detection:** Identifies "Golden Cross" or "Death Cross" signals based on the EMA relationship.
*   **JSON Output:** Prints the results in a structured JSON format for easy parsing by other tools.

## Prerequisites
The script requires Python 3 and the following third-party libraries:
*   `pandas`
*   `python-binance`

To install the dependencies, run:
```bash
pip install pandas python-binance
```

## Usage
Run the script from the command line, passing the target trading symbol via the `--symbol` argument.

### Basic Command
```bash
python ema_analyzer_1h.py --symbol BTC
```

### Example Output (Success)
```json
{
    "symbol": "BTCUSDT",
    "timeframe": "1h",
    "price": 64500.50,
    "ema_50": 64200.10,
    "ema_200": 63800.25,
    "trend": "Bullish",
    "signal": "Golden Cross"
}
```

## Execution Output Analysis
During the most recent execution attempt, the script **failed** to run successfully.

### Error Log
```text
Error: Traceback (most recent call last):
  ...
  File "<exec>", line 10, in <module>
ModuleNotFoundError: No module named 'binance'
```

### Explanation of Failure
The script crashed with a `ModuleNotFoundError`. This indicates that the **`python-binance` library is not installed** in the Python environment where the script was executed.

Line 10 (`from binance.client import Client`) attempts to import the Binance wrapper, but Python could not locate it. To resolve this, the user must install the required package using `pip install python-binance`.