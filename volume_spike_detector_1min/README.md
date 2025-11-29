# Volume Spike Detector (1-Minute)

## Overview
`volume_spike_detector_1min.py` is a Python script designed to detect significant trading volume anomalies in real-time. It connects to the Binance public data API to retrieve 1-minute candlestick data.

The script calculates a **20-period Moving Average (MA)** of the volume and compares the current minute's volume against this average. If the current volume exceeds the average by a user-defined threshold ratio, it flags the event as a "spike."

## Features
- **Automatic Symbol Resolution:** Automatically appends "USDT" to symbols if not provided (e.g., `BTC` becomes `BTCUSDT`).
- **Configurable Threshold:** Users can define the ratio required to trigger a spike detection (default is 2.0x the average).
- **JSON Output:** Outputs structured JSON data suitable for piping into other tools or logs.
- **Error Handling:** Outputs JSON-formatted error messages to `stderr` for easier programmatic parsing.

## Prerequisites
The script requires the `python-binance` library to fetch market data.

```bash
pip install python-binance
```

## Usage

### Command Line Arguments
| Argument | Type | Required | Default | Description |
| :--- | :--- | :--- | :--- | :--- |
| `--symbol` | String | Yes | N/A | The trading symbol (e.g., `BTC`, `ETHUSDT`). |
| `--threshold` | Float | No | `2.0` | The ratio of current volume to MA20 required to flag a spike. |
| `--datasource` | String | No | `binance` | Data source identifier (reserved for future compatibility). |

### Examples

**Basic Usage (Default Threshold):**
```bash
python volume_spike_detector_1min.py --symbol BTC
```

**Custom Threshold (3x volume):**
```bash
python volume_spike_detector_1min.py --symbol ETH --threshold 3.0
```

## Output Format

### Success Output (stdout)
The script prints a JSON object containing the analysis results:

```json
{
    "symbol": "BTCUSDT",
    "timestamp": "2023-10-27T10:00:00Z",
    "volume_current": 150.5,
    "ma20": 50.0,
    "ratio": 3.01,
    "spike": true,
    "threshold": 2.0
}
```

### Error Output (stderr)
If an error occurs (e.g., invalid symbol, network error), a JSON error object is printed to standard error:

```json
{"error": "Data fetch error for symbol INVALIDUSDT: ..."}
```

## Execution Analysis

### Observed Output
When attempting to run the script in the provided environment, the following error occurred:

```text
Error: Traceback (most recent call last):
  ...
  File "<exec>", line 11, in <module>
ModuleNotFoundError: No module named 'binance'
```

### Explanation of Failure
The execution failed because the required third-party library, `python-binance`, is not installed in the Python environment where the script was executed.

The script attempts to import `Client` from `binance.client` on line 11. Since the Python interpreter cannot locate this package, it raises a `ModuleNotFoundError` and terminates.

### Resolution
To fix this error, install the required package using pip:
```bash
pip install python-binance
```