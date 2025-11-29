# tsi_getter_1min.py

## Overview

`tsi_getter_1min.py` is a Python command-line utility designed to fetch real-time market data from the Binance exchange and calculate the **True Strength Index (TSI)**.

The script operates on the **1-minute timeframe**. It retrieves candlestick (kline) data, processes the closing prices, and computes the TSI using a Double Smoothed Exponential Moving Average (EMA) approach.

**Key Features:**
*   **Binance Integration:** Uses the `python-binance` library to fetch public market data (no API keys required).
*   **Smart Symbol Resolution:** Automatically appends "USDT" to common symbols (e.g., inputting `BTC` resolves to `BTCUSDT`).
*   **Configurable History:** Allows adjusting the amount of historical data fetched via the `--limit` flag.
*   **Standard TSI Settings:** Uses standard indicator parameters: Long Period ($P$) = 25, Short Period ($Q$) = 13.

## Prerequisites

The script requires Python 3 and the `python-binance` third-party library.

### Installation

To install the required dependency, run:

```bash
pip install python-binance
```

## Usage

Run the script from the terminal using the `--symbol` argument.

### Basic Command
```bash
python tsi_getter_1min.py --symbol BTC
```

### Specifying a Full Pair
```bash
python tsi_getter_1min.py --symbol ETHUSDT
```

### Adjusting Data Limit
To fetch more historical data points (default is 100):
```bash
python tsi_getter_1min.py --symbol SOL --limit 200
```

### Output Format
The script outputs a single line containing the symbol, the ISO timestamp of the latest candle close, the calculated TSI value, and the parameters used.

```text
Symbol: BTCUSDT | Time: 2023-10-27 10:05:00 | TSI: 12.45 | p=25, q=13
```

## Execution Output Analysis

When the script was executed in the provided environment, it resulted in a **failure**.

### Error Log
```text
Error: Traceback (most recent call last):
  ...
  File "<exec>", line 15, in <module>
ModuleNotFoundError: No module named 'binance'
```

### Explanation of Failure
The script failed with a `ModuleNotFoundError`. This indicates that the external dependency **`python-binance`** is not installed in the Python environment where the script was executed.

The script attempts to import `Client` and exceptions from `binance.client` on line 15. Since the library is missing, Python cannot proceed.

### Solution
To fix this error, install the missing package using pip:
```bash
pip install python-binance
```

## Technical Details

### TSI Calculation Logic
The script calculates TSI based on the following steps:
1.  **Momentum ($M$):** $Close_{current} - Close_{previous}$
2.  **First Smoothing ($P=25$):** EMA of $M$ and EMA of $|M|$.
3.  **Second Smoothing ($Q=13$):** EMA of the results from step 2.
4.  **TSI Formula:**
    $$ TSI = 100 \times \frac{EMA(EMA(M, P), Q)}{EMA(EMA(|M|, P), Q)} $$

### API Constraints
*   **Authentication:** The script initializes the Binance client with empty strings (`Client("", "")`), allowing access to public endpoints without an account.
*   **Data Requirements:** The script enforces a minimum fetch limit of $P + Q$ (38 points) to ensure the EMA calculation has enough data to converge reasonably, though a higher limit (default 100) provides better accuracy.