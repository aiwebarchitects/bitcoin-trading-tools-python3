# ATR Volatility Calculator (1h)

## Description
`atr_volatility_1h.py` is a Python utility designed to calculate the Average True Range (ATR) volatility metric for cryptocurrency assets on the Binance exchange.

The script operates on the **1-hour timeframe** and performs the following operations:
1.  **Symbol Resolution:** Automatically appends "USDT" to short symbols (e.g., converts "BTC" to "BTCUSDT") for convenience.
2.  **Data Fetching:** Retrieves the most recent 20 hours of OHLC (Open, High, Low, Close) data via the Binance public API.
3.  **Calculation:** 
    *   Computes the True Range (TR) for each period.
    *   Calculates the ATR using a Simple Moving Average (SMA) over the last 14 periods (ATR-14).
    *   Derives the volatility percentage relative to the current price.
4.  **Formatting:** Dynamically adjusts decimal precision based on the asset's price magnitude.

## Prerequisites
This script requires Python 3 and the `python-binance` library.

To install the required dependency:
```bash
pip install python-binance
```

## Usage
Run the script from the command line, providing the target trading symbol using the `--symbol` argument.

**Basic Usage (Defaults to USDT):**
```bash
python atr_volatility_1h.py --symbol BTC
```

**Specific Pair Usage:**
```bash
python atr_volatility_1h.py --symbol ETHUSDT
```

**Expected Output Format:**
```text
[BTCUSDT] 1H Volatility: 125.50 (0.45%)
```

## Execution Output Analysis
When the script was executed in the provided environment, it failed with the following error:

```text
ModuleNotFoundError: No module named 'binance'
```

### Explanation of Failure
The script crashed because the **`python-binance`** library was not installed in the Python environment where the code was executed.

1.  The script attempts to import `Client` from `binance.client` on line 8.
2.  Python could not locate this package in its library path.
3.  The execution terminated immediately with a `ModuleNotFoundError`.

To resolve this, the user must install the package via pip (as shown in the Prerequisites section) before running the script.