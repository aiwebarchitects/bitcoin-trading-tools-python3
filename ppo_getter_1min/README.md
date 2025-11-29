# PPO Getter (1-Minute Timeframe)

## Description
`ppo_getter_1min.py` is a Python utility designed to calculate the Percentage Price Oscillator (PPO) for cryptocurrency assets. It connects to the Binance public data API to retrieve 1-minute interval candlestick data (klines) and computes the PPO indicator locally.

The script performs the following operations:
1.  **Data Fetching:** Retrieves historical price data (default 300 points) for a specified symbol using the `python-binance` library.
2.  **Symbol Normalization:** Automatically appends 'USDT' to the symbol if a trading pair is not explicitly defined (e.g., 'BTC' becomes 'BTCUSDT').
3.  **Technical Analysis:**
    *   Calculates a 12-period Fast EMA and a 26-period Slow EMA.
    *   Seeds the EMA calculation with a Simple Moving Average (SMA) of the first $N$ prices to ensure stability.
    *   Computes PPO using the formula: `((EMA_fast - EMA_slow) / EMA_slow) * 100`.
4.  **Reporting:** Outputs the latest PPO value with its timestamp and a historical "tail" of recent PPO values.

## Dependencies
This script requires the `python-binance` library.

```bash
pip install python-binance
```

## Usage

Run the script from the command line, specifying the target symbol.

### Basic Usage
```bash
python ppo_getter_1min.py --symbol BTC
```

### Advanced Usage
You can customize the amount of data fetched and the number of historical points displayed.

```bash
python ppo_getter_1min.py --symbol ETHUSDT --limit 500 --tail 10
```

### Arguments
| Argument | Type | Required | Default | Description |
| :--- | :--- | :--- | :--- | :--- |
| `--symbol` | String | Yes | N/A | The trading symbol (e.g., `BTC`, `ETHUSDT`). |
| `--limit` | Integer | No | 300 | Number of 1-minute klines to fetch from Binance. |
| `--tail` | Integer | No | 5 | Number of recent PPO values to display in the output summary. |

## Execution Output Analysis

The provided execution output indicates that the script **failed to run** successfully.

### Error Log
```text
Error: Traceback (most recent call last):
  ...
  File "<exec>", line 19, in <module>
ModuleNotFoundError: No module named 'binance'
```

### Explanation of Failure
The error `ModuleNotFoundError: No module named 'binance'` occurs because the required third-party library, `python-binance`, is not installed in the Python environment where the script was executed.

To resolve this, the user must install the package using pip before running the script (see the **Dependencies** section above).