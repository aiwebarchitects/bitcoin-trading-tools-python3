# Awesome Oscillator Getter (1-Minute)

## Description
`awesome_oscillator_getter_1min.py` is a Python utility that calculates the **Awesome Oscillator (AO)** technical indicator for a specified cryptocurrency symbol. It utilizes real-time market data from the Binance REST API.

The script performs the following operations:
1.  Connects to the Binance public API (no authentication required).
2.  Fetches the latest 34 candlesticks (klines) at a **1-minute interval**.
3.  Automatically attempts to resolve the trading pair (e.g., if "BTC" is provided, it tries "BTCUSDT", then "BTC").
4.  Calculates the Awesome Oscillator using the formula:
    *   `Typical Price (TP) = (High + Low + Close) / 3`
    *   `AO = SMA(TP, 5) - SMA(TP, 34)`
5.  Outputs the result as a JSON object containing the symbol, interval, calculated value, and ISO 8601 timestamp.

## Dependencies
This script requires the third-party library `python-binance`.

```bash
pip install python-binance
```

## Usage

Run the script from the command line, providing the target symbol via the `--symbol` argument.

### Command Syntax
```bash
python awesome_oscillator_getter_1min.py --symbol <SYMBOL>
```

### Examples
**Calculate AO for Bitcoin:**
```bash
python awesome_oscillator_getter_1min.py --symbol BTC
```

**Calculate AO for Ethereum:**
```bash
python awesome_oscillator_getter_1min.py --symbol ETH
```

### Output Format
The script prints a single line of JSON to standard output:
```json
{
  "symbol": "BTCUSDT",
  "interval": "1m",
  "awesome_oscillator": 15.234,
  "as_of": "2023-10-27T10:00:00Z"
}
```

## Execution Output Analysis

When the script was executed in the provided environment, it resulted in a **failure**.

### Log Output
```text
Error: Traceback (most recent call last):
  ...
  File "<exec>", line 21, in <module>
ModuleNotFoundError: No module named 'binance'
```

### Explanation of Failure
The execution failed due to a `ModuleNotFoundError`.
*   **Cause:** The Python environment attempting to run the script did not have the required external library `python-binance` installed. The script imports `Client` and `BinanceAPIException` from `binance.client` and `binance.exceptions` respectively (Line 21).
*   **Resolution:** To run this script successfully, the user must install the dependency using `pip install python-binance`.