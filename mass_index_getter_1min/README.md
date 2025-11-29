# Mass Index Getter (1-Minute)

**File:** `mass_index_getter_1min.py`

## Description
This Python script calculates a volatility metric—referred to here as the Mass Index—based on 1-minute candlestick data from the Binance cryptocurrency exchange. 

The script gauges volatility and potential breakouts by analyzing the expansion and contraction of the High-Low range. It retrieves historical data, computes Exponential Moving Averages (EMAs) of the trading range, and outputs the ratio between a Fast EMA and a Slow EMA.

**Key Features:**
*   Fetches real-time/historical 1-minute OHLC data via the Binance public API (no API key required).
*   Calculates the High-Low Range ($R_t = High_t - Low_t$).
*   Computes Fast EMA (9-period) and Slow EMA (26-period) of the Range.
*   Outputs the "Mass Index" ratio ($EMA_{fast} / EMA_{slow}$).
*   Provides both a human-readable summary and a machine-parsable JSON object.

## Algorithm
1.  **Data Retrieval:** Fetches the last 200 1-minute candles for the specified symbol (defaults to USDT pair).
2.  **Range Calculation:** For every candle, calculate $R = High - Low$.
3.  **EMA Calculation:**
    *   Fast EMA ($N=9$) of $R$.
    *   Slow EMA ($N=26$) of $R$.
4.  **Ratio Calculation:** $MassIndex = \frac{FastEMA}{SlowEMA}$.

## Prerequisites
The script requires Python 3 and the `python-binance` library.

```bash
pip install python-binance
```

## Usage

Run the script from the command line, providing the target symbol via the `--symbol` argument.

### Basic Command
```bash
python mass_index_getter_1min.py --symbol BTC
```
*Note: If you provide a base asset like `BTC`, the script automatically appends `USDT` to form `BTCUSDT`.*

### Specific Pair
```bash
python mass_index_getter_1min.py --symbol ETHUSDT
```

## Output Format

The script prints two lines to standard output:
1.  **Human-Readable Log:** Details the symbol, timestamp, calculated index, and raw EMA values.
2.  **JSON Object:** A compact JSON string for programmatic integration.

**Example JSON Output:**
```json
{
    "symbol": "BTCUSDT",
    "time": "2023-10-27T10:00:00Z",
    "mass_index": 1.0234,
    "fast_ema": 15.50,
    "slow_ema": 15.14
}
```

## Execution Analysis

### Observed Output
When the script was executed in the test environment, it produced the following error:

```text
Error: Traceback (most recent call last):
  ...
  File "<exec>", line 29, in <module>
ModuleNotFoundError: No module named 'binance'
```

### Explanation of Failure
The execution failed because the required third-party library, **`python-binance`**, was not installed in the Python environment where the script was run.

The script imports `Client` from `binance.client` on line 29. Since this module was missing, Python raised a `ModuleNotFoundError`. To fix this, the dependency must be installed using `pip install python-binance` before running the script.