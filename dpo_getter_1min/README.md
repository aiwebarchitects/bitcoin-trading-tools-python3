# dpo_getter_1min.py

## Overview
`dpo_getter_1min.py` is a Python script designed to calculate the **Detrended Price Oscillator (DPO)** for a specific cryptocurrency trading pair. It utilizes the Binance public API to fetch real-time 1-minute candlestick data and computes the DPO based on a 20-period window.

## Features
*   **Automated Symbol Resolution:** Accepts raw symbols (e.g., `BTC`) and automatically attempts to resolve them against common stablecoin pairs (USDT, BUSD, USDC).
*   **Real-time Data:** Fetches the latest 1000 data points (klines) from Binance on a 1-minute timeframe.
*   **DPO Calculation:** Computes the DPO using the standard formula with $n=20$ and a displacement of $n/2 + 1$.
*   **Timestamping:** Outputs the calculation time in ISO format.

## Prerequisites
To run this script, you must have Python 3 installed along with the `python-binance` library.

### Installation
The script relies on the `binance` module. Install it via pip:

```bash
pip install python-binance
```

## Usage
Run the script from the command line, providing the target symbol via the `--symbol` argument.

### Command Syntax
```bash
python dpo_getter_1min.py --symbol <SYMBOL>
```

### Examples
**1. Using a full pair name:**
```bash
python dpo_getter_1min.py --symbol BTCUSDT
```

**2. Using a base asset (script defaults to USDT/BUSD/USDC):**
```bash
python dpo_getter_1min.py --symbol ETH
```

### Expected Output
On success, the script prints the symbol, the calculated DPO value, and the timestamp:
```text
Symbol: BTCUSDT | DPO (1m, n=20): 120.500000 | Time: 2023-10-27T10:00:00Z
```

## Execution Output Analysis
When the script was executed in the provided test environment, it produced the following error:

```text
Error: Traceback (most recent call last):
  ...
  File "<exec>", line 11, in <module>
ModuleNotFoundError: No module named 'binance'
```

### Explanation of Failure
The execution failed because the required third-party library, `python-binance`, was not installed in the Python environment where the script was run.

1.  **Error Type:** `ModuleNotFoundError`.
2.  **Missing Module:** `binance`.
3.  **Root Cause:** The script attempts to import `Client` and `BinanceAPIException` from `binance.client` and `binance.exceptions` respectively on lines 11 and 12. Since the package is missing, Python cannot proceed.

### Solution
To fix this error, install the dependency using the installation command provided in the **Prerequisites** section above.