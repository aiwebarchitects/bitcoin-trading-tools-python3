# On-Balance-Volume (OBV) Tracker (1-Minute)

## Description
`obv_tracker_1min.py` is a Python script designed to calculate and track the On-Balance-Volume (OBV) technical indicator for cryptocurrency pairs on Binance. It operates on **1-minute candle intervals** in real-time.

The script performs the following operations:
1.  **Connects to Binance:** Uses the public API (no API keys required) to fetch candlestick (kline) data.
2.  **Calculates OBV:** Computes the OBV delta based on price close comparisons against volume.
    *   If Close > Previous Close: `+Volume`
    *   If Close < Previous Close: `-Volume`
    *   If Close == Previous Close: `0`
3.  **State Persistence:** Saves the current OBV, previous close price, and timestamp to a local JSON file (`obv_<SYMBOL>_state.json`). This allows the script to resume calculations accurately after a restart.
4.  **Data Integrity:** Automatically detects data gaps. If a gap larger than 1 minute is detected between the last processed state and the current market time, the script terminates to prevent inaccurate indicator calculation.
5.  **Continuous Monitoring:** Polls for new candles every 5 seconds.

## Prerequisites
The script requires Python 3 and the `python-binance` library.

### Installation
To install the required dependency, run:
```bash
pip install python-binance
```

## Usage

Run the script from the command line. You can optionally specify the trading symbol.

### Default (BTCUSDT)
```bash
python obv_tracker_1min.py
```

### Custom Symbol
The script automatically appends "USDT" if not provided (e.g., `ETH` becomes `ETHUSDT`).
```bash
python obv_tracker_1min.py --symbol ETH
```

## Output Format
The script outputs two lines per update: a human-readable log line and a JSON-formatted line for programmatic parsing.

**Example:**
```text
symbol=BTC | time=2023-10-27 10:00:00 | OBV=120.5 | delta=5.5
{"symbol": "BTC", "time": "2023-10-27 10:00:00", "obv": 120.5, "delta": 5.5}
```

## State Management
The script creates a file named `obv_<SYMBOL>_state.json` in the current directory.
*   **Content:** Stores `obv` (cumulative), `prev_close`, and `last_open_time`.
*   **Purpose:** Ensures continuity. If you stop and restart the script, it loads this file to continue the OBV line from where it left off.

## Execution Analysis

### Execution Output
When the script was executed, the following error occurred:
```text
Error: Traceback (most recent call last):
  ...
  File "<exec>", line 21, in <module>
ModuleNotFoundError: No module named 'binance'
```

### Explanation of Failure
The execution failed because the required third-party library, **`python-binance`**, was not installed in the Python environment where the script was run.

The script attempts to import `Client` from `binance.client` on line 21. Since the environment lacked this package, Python raised a `ModuleNotFoundError`.

### Solution
To fix this error, install the missing library using pip:
```bash
pip install python-binance
```