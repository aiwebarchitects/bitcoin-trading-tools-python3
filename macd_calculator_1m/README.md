# MACD Calculator (1-Minute Timeframe)

## Description
`macd_calculator_1m.py` is a command-line utility that calculates the Moving Average Convergence Divergence (MACD) technical indicator for cryptocurrency pairs.

The script performs the following operations:
1.  **Data Retrieval:** Connects to the Binance public API to fetch the latest 200 candlesticks (klines) for a specified symbol on a **1-minute timeframe**.
2.  **Symbol Normalization:** Automatically appends "USDT" to the symbol if not provided (e.g., inputting "BTC" converts to "BTCUSDT").
3.  **Calculation:** Manually computes the technical indicators without relying on heavy data science libraries (like Pandas):
    *   **MACD Line:** Difference between the 12-period EMA and 26-period EMA.
    *   **Signal Line:** 9-period EMA of the MACD Line.
    *   **Histogram:** Difference between the MACD Line and the Signal Line.
4.  **Output:** Prints the latest calculated values to the console.

## Prerequisites
*   Python 3.x
*   `python-binance` library

## Usage

### Basic Usage
Run the script by providing the target symbol using the `--symbol` argument.

```bash
python macd_calculator_1m.py --symbol BTC
```

### Verbose Mode
Use the `--verbose` flag to see the last 5 calculated values for the MACD and Signal lines, rather than just the latest point.

```bash
python macd_calculator_1m.py --symbol ETH --verbose
```

### Arguments
| Argument | Required | Description |
| :--- | :---: | :--- |
| `--symbol` | Yes | The trading symbol (e.g., BTC, ETH, SOL). |
| `--verbose` | No | Prints the last 5 MACD/Signal values for trend analysis. |

## Execution Output Analysis

Based on the provided console logs, the script **failed to execute successfully**.

### Error Log
```text
ModuleNotFoundError: No module named 'binance'
```

### Explanation of Failure
The script crashed immediately upon startup because of a missing dependency. The Python environment attempting to run the code does not have the `python-binance` library installed. This library is required to communicate with the Binance API.

### Resolution
To fix this error, install the required library using pip:

```bash
pip install python-binance
```

Once installed, the script should execute correctly, provided the machine has internet access to reach the Binance API.