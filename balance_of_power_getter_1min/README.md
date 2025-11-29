# Balance of Power (BOP) Calculator (1-Minute)

## Overview
`balance_of_power_getter_1min.py` is a Python script designed to calculate the **Balance of Power (BOP)** indicator for a specific cryptocurrency asset. It utilizes the Binance public API to fetch real-time market data on a 1-minute timeframe.

The BOP indicator is used to assess the strength of buyers versus sellers by evaluating the relationship between the opening and closing prices relative to the high and low prices of the trading session.

### Key Features
*   **Dynamic Pair Resolution:** Automatically attempts to resolve the trading pair by appending `USDT`, `BUSD`, or `USDC` to the provided symbol (e.g., converting "BTC" to "BTCUSDT").
*   **Real-time Calculation:** Fetches the most recent 1-minute kline (candlestick) data.
*   **Trend Interpretation:** Provides a textual interpretation of the BOP value:
    *   **> 0:** Buy pressure (Close > Open).
    *   **< 0:** Sell pressure (Close < Open).
    *   **0:** Neutral.

## Dependencies
This script requires the third-party library `python-binance`.

```bash
pip install python-binance
```

## Usage

Run the script from the command line, passing the asset symbol via the `--symbol` argument.

```bash
python balance_of_power_getter_1min.py --symbol <SYMBOL>
```

### Arguments
*   `--symbol`: (Required) The ticker symbol of the asset (e.g., `BTC`, `ETH`, `SOL`).

### Example
```bash
python balance_of_power_getter_1min.py --symbol ETH
```

## Expected Output (Successful Run)
If the environment is configured correctly, the script outputs the resolved pair, the UTC timestamp of the candle close, the calculated BOP value, and the market interpretation.

```text
Symbol: ETHUSDT
Time (UTC): 2023-10-27T10:05:00Z
BOP_1m: 0.450000
Interpretation: Buy pressure (BOP > 0)
```

## Execution Log Analysis

The provided execution logs indicate that the script **failed to run successfully**.

### Error Log
```text
Error: Traceback (most recent call last):
  ...
  File "<exec>", line 10, in <module>
ModuleNotFoundError: No module named 'binance'
```

### Explanation of Failure
The script crashed with a `ModuleNotFoundError`. This occurred because the Python environment attempting to execute the code did not have the `python-binance` library installed.

The script attempts to import `Client` and `BinanceAPIException` from the `binance` package on lines 10 and 11. Since the package was missing from the system path, the Python interpreter could not proceed.

### Resolution
To fix this error, install the required dependency using pip:
```bash
pip install python-binance
```