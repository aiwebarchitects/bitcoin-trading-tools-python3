# KST Momentum Oscillator Calculator (1-Minute)

**File:** `kst_getter_1min.py`

## Description
This Python script calculates the **Know Sure Thing (KST)** momentum oscillator for a specified cryptocurrency symbol using 1-minute timeframe data fetched from Binance.

The KST is a summed, weighted momentum indicator designed to capture market trends. This script implements the following logic:
1.  **Data Fetching:** Retrieves the last 200 1-minute candlesticks (klines) from the Binance public API (no authentication required).
2.  **ROC Calculation:** Computes Rate of Change (ROC) for four distinct periods: 10, 15, 20, and 30.
3.  **Smoothing:** Applies Simple Moving Averages (SMA) to the ROCs with periods of 10, 10, 15, and 15 respectively.
4.  **Weighting:** Calculates the KST line by weighting the smoothed ROCs (Weights: 1, 2, 3, 4).
5.  **Signal & Histogram:** Computes a Signal line (9-period SMA of the KST) and the Histogram (KST minus Signal).

The script includes robust error handling for API connectivity issues (with exponential backoff) and insufficient data scenarios.

## Prerequisites
The script requires Python 3 and the `python-binance` library.

```bash
pip install python-binance
```

## Usage
Run the script from the command line. You can optionally specify a trading symbol. If a base asset is provided (e.g., `BTC`), the script defaults to the USDT pair (`BTCUSDT`).

### Basic Usage (Defaults to BTCUSDT)
```bash
python kst_getter_1min.py
```

### Specify a Symbol
```bash
python kst_getter_1min.py --symbol ETH
```

### Specify a Full Pair
```bash
python kst_getter_1min.py --symbol SOLUSDT
```

## Output Format
The script prints the normalized symbol, the UTC timestamp of the latest candle, and the calculated indicators:
```text
Symbol: BTCUSDT
Time (UTC): 2023-10-27 10:05
KST: 12.345678
Signal: 10.987654
Histogram: 1.358024
```

## Execution Output Analysis
When the script was executed in the provided environment, it failed with the following error:

```text
Error: Traceback (most recent call last):
  ...
  File "<exec>", line 30, in <module>
ModuleNotFoundError: No module named 'binance'
```

### Explanation of Failure
The execution failed because the required third-party library, **`python-binance`**, was not installed in the Python environment where the script was run.

The error `ModuleNotFoundError: No module named 'binance'` indicates that the Python interpreter could not locate the package imported on line 30 (`from binance.client import Client`).

### Resolution
To fix this error, install the missing dependency using pip:
```bash
pip install python-binance
```