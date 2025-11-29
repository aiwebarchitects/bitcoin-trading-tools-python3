# Binance Funding Rate Tracker

**File:** `funding_rate_tracker_1min.py`

## Description
This Python script monitors the perpetual futures funding rate for a specific cryptocurrency symbol on Binance. It polls the Binance public API at 1-minute intervals to track the current funding rate, calculate the change (delta) from the previous minute, and determine the immediate trend (Rising, Falling, or Neutral).

This tool is useful for traders looking to gauge funding pressure and potential price stress without requiring an authenticated API session.

**Key Features:**
*   **Real-time Tracking:** Updates every 60 seconds.
*   **Trend Analysis:** Calculates the difference between intervals to identify rising or falling funding costs.
*   **Smart Symbol Handling:** Automatically appends "USDT" if a short symbol (e.g., "BTC") is provided.
*   **Resilience:** Handles network errors and API exceptions by retrying automatically.
*   **No Auth Required:** Uses public endpoints, so no API keys are needed.

## Prerequisites
The script requires Python 3 and the `python-binance` library.

```bash
pip install python-binance
```

## Usage

Run the script from the command line, specifying the target symbol.

### Basic Usage
Track Bitcoin (BTCUSDT) funding rate:
```bash
python funding_rate_tracker_1min.py --symbol BTC
```

### Advanced Usage
Track Ethereum with a custom sensitivity threshold for trend detection:
```bash
python funding_rate_tracker_1min.py --symbol ETH --threshold 0.00005
```

### Arguments
| Argument | Required | Default | Description |
| :--- | :---: | :--- | :--- |
| `--symbol` | Yes | N/A | The trading symbol (e.g., `BTC`, `ETH`, `SOLUSDT`). |
| `--threshold` | No | `0.00001` | The decimal threshold to determine if the trend is "Rising" or "Falling". |

## Output Format
The script outputs one log line per minute to `stdout`:

```text
[YYYY-MM-DD HH:MM:SS UTC] SYMBOL=BTCUSDT FUNDING_RATE=0.010000% DELTA=+0.000000% TREND=Neutral
```

*   **FUNDING_RATE:** The current funding rate in percent.
*   **DELTA:** The change in funding rate compared to the previous minute.
*   **TREND:** `Rising`, `Falling`, or `Neutral` based on the delta threshold.

## Execution Analysis

### Execution Log
When the script was executed in the test environment, the following error occurred:

```text
Error: Traceback (most recent call last):
  File "/lib/python311.zip/_pyodide/_base.py", line 573, in eval_code_async
    await CodeRunner(
  ...
  File "<exec>", line 18, in <module>
ModuleNotFoundError: No module named 'binance'
```

### Failure Explanation
The execution failed because the required third-party library, **`python-binance`**, was not installed in the Python environment where the script was run.

The script attempts to import `Client` from `binance.client` on line 18. Since the module could not be found, Python raised a `ModuleNotFoundError`.

**Resolution:**
To fix this error, install the library using pip before running the script:
```bash
pip install python-binance
```