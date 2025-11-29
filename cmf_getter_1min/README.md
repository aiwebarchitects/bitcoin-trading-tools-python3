# cmf_getter_1min.py

## Overview
`cmf_getter_1min.py` is a Python utility designed to calculate the **Chaikin Money Flow (CMF)** technical indicator for cryptocurrency assets. It utilizes the Binance public API to retrieve real-time 1-minute candlestick (kline) data and computes the CMF over a user-defined lookback window.

The output is formatted as a JSON object, making it suitable for integration into larger trading bots, data pipelines, or monitoring dashboards.

## Features
- **Data Source:** Fetches live market data directly from Binance (no API key required for public data).
- **Timeframe:** Hardcoded to 1-minute intervals for high-frequency analysis.
- **Smart Symbol Handling:** Automatically appends "USDT" if a base symbol (e.g., "BTC") is provided.
- **Customizable Window:** Allows adjustment of the calculation window (default is 20 periods).
- **JSON Output:** Returns structured data including the calculated CMF value and the UTC timestamp of the latest candle.

## Prerequisites
The script requires Python 3 and the `python-binance` library.

### Installation
To install the required dependency, run:
```bash
pip install python-binance
```

## Usage

### Command Line Arguments
| Argument | Type | Required | Default | Description |
| :--- | :--- | :--- | :--- | :--- |
| `--symbol` | String | Yes | N/A | The trading pair (e.g., `BTCUSDT`) or base asset (`BTC`). |
| `--window` | Integer | No | 20 | The number of candles to include in the CMF calculation. |

### Examples

**Basic usage (defaults to 20-candle window):**
```bash
python cmf_getter_1min.py --symbol BTC
```

**Custom window size (e.g., 50 candles):**
```bash
python cmf_getter_1min.py --symbol ETHUSDT --window 50
```

## Output Format
On success, the script prints a JSON object to `stdout`:

```json
{
  "symbol": "BTCUSDT",
  "timeframe": "1m",
  "window": 20,
  "cmf": 0.123456,
  "timestamp": "2023-10-27T10:00:00Z"
}
```

## Algorithm Details
The script calculates CMF using the following logic:
1.  **Fetch Data:** Retrieves the last 1000 1-minute candles.
2.  **Money Flow Multiplier (MFM):**
    $$ \text{MFM} = \frac{(\text{Close} - \text{Low}) - (\text{High} - \text{Close})}{\text{High} - \text{Low}} $$
3.  **Money Flow Volume (MFV):**
    $$ \text{MFV} = \text{MFM} \times \text{Volume} $$
4.  **Chaikin Money Flow (CMF):**
    $$ \text{CMF} = \frac{\sum_{i=1}^{n} \text{MFV}_i}{\sum_{i=1}^{n} \text{Volume}_i} $$
    *(Where $n$ is the window size)*

## Execution Log Analysis

### Observed Output
When the script was executed, the following error occurred:
```text
Error: Traceback (most recent call last):
  ...
  File "<exec>", line 24, in <module>
ModuleNotFoundError: No module named 'binance'
```

### Explanation of Failure
The execution failed because the required third-party library, `python-binance`, was not installed in the Python environment where the script was run.

1.  **Error Type:** `ModuleNotFoundError`.
2.  **Cause:** The script attempts to import `Client` from `binance.client` on line 24, but the interpreter could not locate the package.
3.  **Resolution:** The user must install the package using `pip install python-binance` before running the script.