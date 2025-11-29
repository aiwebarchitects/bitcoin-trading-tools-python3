# pivot_point_getter_1min.py

## Overview
This Python script calculates standard intraday Pivot Points (PP, S1, S2, R1, R2) for a specific cryptocurrency trading pair. It utilizes the Binance public API to fetch 1-minute interval price data (klines) for the **previous calendar day (UTC)**.

By aggregating 1-minute candles (1440 data points per day), the script determines the precise High, Low, and Close of the previous day to generate accurate support and resistance levels for the current trading day.

## Features
- **Automatic Symbol Normalization:** Accepts short symbols (e.g., `BTC`) and defaults them to USDT pairs (e.g., `BTCUSDT`) if no pair is specified.
- **UTC Synchronization:** Strictly uses UTC time to define the "previous day" boundary, aligning with standard crypto market analysis.
- **Data Validation:** Verifies that a full day's worth of data (1440 minutes) is retrieved before calculating to ensure accuracy.
- **Standard Formulas:**
  - **PP (Pivot Point):** `(High + Low + Close) / 3`
  - **R1/S1:** Standard first level resistance/support.
  - **R2/S2:** Standard second level resistance/support.

## Prerequisites
The script requires Python 3 and the `python-binance` library.

### Installation
You must install the Binance client library before running the script:
```bash
pip install python-binance
```

## Usage
Run the script from the command line, providing the target symbol via the `--symbol` argument.

### Basic Command
```bash
python pivot_point_getter_1min.py --symbol BTCUSDT
```

### Short Command (Defaults to USDT)
```bash
python pivot_point_getter_1min.py --symbol ETH
```

### Expected Output (Success)
If successful, the script outputs the calculated levels to the console:
```text
Symbol: BTCUSDT
Date: 2023-10-27 (previous day)
PP: 34150.500000
R1: 34500.100000
R2: 34800.250000
S1: 33900.800000
S2: 33650.400000
```

## Execution Output Analysis
When the script was executed in the provided environment, it failed with the following error:

```text
Error: Traceback (most recent call last):
  ...
  File "<exec>", line 18, in <module>
ModuleNotFoundError: No module named 'binance'
```

### Explanation of Failure
The script crashed because of a **Missing Dependency**.
1.  **Error Type:** `ModuleNotFoundError`.
2.  **Cause:** The Python environment attempting to run the code did not have the `python-binance` package installed. Line 18 (`from binance.client import Client`) failed to import the necessary library.
3.  **Resolution:** To fix this error, the user must install the required package using `pip install python-binance`.

## Troubleshooting
- **Incomplete Data Error:** If the script returns "Error: Incomplete data for previous day," it means the Binance API returned fewer than 1440 minutes of data. This usually happens if the token was listed recently or if there was significant API downtime.
- **Binance API Error:** Network issues or IP bans may result in a `BinanceAPIException`. Ensure you have internet access and are not in a restricted region.