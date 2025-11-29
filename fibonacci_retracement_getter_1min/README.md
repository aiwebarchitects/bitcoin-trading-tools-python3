# Fibonacci Retracement Getter (1-Minute)

## Description
This Python script calculates Fibonacci retracement levels (38.2%, 50%, and 61.8%) for a specified cryptocurrency symbol. It utilizes the Binance public API to fetch the latest completed 1-minute candlestick (OHLCV data).

The script performs the following operations:
1.  **Symbol Normalization:** Accepts a symbol (e.g., "BTC") and defaults it to a USDT pair (e.g., "BTCUSDT") if no suffix is provided.
2.  **Data Retrieval:** Fetches the most recent 1-minute klines from Binance.
3.  **Trend Analysis:** Determines if the latest completed candle was bullish (Close >= Open) or bearish.
4.  **Calculation:** Computes the retracement price levels based on the High-Low range of that specific candle.
    *   **Bullish Candle:** Retracements are calculated downwards from the High.
    *   **Bearish Candle:** Retracements are calculated upwards from the Low.

## Prerequisites
*   Python 3.x
*   `python-binance` library

## Installation
The script requires the `python-binance` third-party library to interact with the Binance API.

```bash
pip install python-binance
```

## Usage
Run the script from the command line, providing the target symbol via the `--symbol` argument.

### Basic Usage
```bash
python fibonacci_retracement_getter_1min.py --symbol BTC
```

### Specifying Full Pair
```bash
python fibonacci_retracement_getter_1min.py --symbol ETHUSDT
```

### Expected Output Format
If successful, the script outputs the following details:
```text
Symbol: BTCUSDT
Time (completed candle end): 2023-10-27 10:00:00 UTC
Swing high: 34000.0000, Swing low: 33900.0000, Open: 33950.0000, Close: 33980.0000
38.2% retracement: 33961.8000
50.0% retracement: 33950.0000
61.8% retracement: 33938.2000
```

## Execution Output Analysis
During the test execution, the script **failed** to run successfully.

**Console Log:**
```text
Error: Traceback (most recent call last):
  ...
  File "<exec>", line 9, in <module>
ModuleNotFoundError: No module named 'binance'
```

## Failure Explanation
The execution failed due to a **missing dependency**.

*   **Error:** `ModuleNotFoundError: No module named 'binance'`
*   **Cause:** The Python environment where the script was executed does not have the `python-binance` library installed. This library is imported on line 9 (`from binance.client import Client`) and is essential for fetching market data.
*   **Resolution:** Install the required package using `pip install python-binance` before running the script.