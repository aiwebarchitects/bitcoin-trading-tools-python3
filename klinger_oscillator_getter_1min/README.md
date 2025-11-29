# Klinger Oscillator Getter (1-Minute Interval)

## Overview
`klinger_oscillator_getter_1min.py` is a Python script designed to calculate the **Klinger Oscillator (KO)** for a specific cryptocurrency trading pair. It utilizes the Binance public API to fetch real-time 1-minute candlestick data (klines) and computes the oscillator based on volume and price changes.

The script performs the following operations:
1.  Resolves the input symbol (e.g., converts `BTC` to `BTCUSDT` if necessary).
2.  Fetches the last 500 1-minute candles from Binance.
3.  Computes the Volume-Weighted Price Change (VWPC).
4.  Calculates the Klinger Line (EMA of VWPC).
5.  Derives the Klinger Oscillator by subtracting the Slow EMA (55 periods) from the Fast EMA (34 periods) of the Klinger Line.
6.  Outputs the latest KO value and its timestamp.

## Dependencies
To run this script, you need Python 3 and the `python-binance` library.

```bash
pip install python-binance
```

## Usage
The script is executed via the command line and requires a `--symbol` argument.

```bash
python klinger_oscillator_getter_1min.py --symbol <SYMBOL>
```

**Examples:**
```bash
# Fetch for Bitcoin (defaults to USDT pair)
python klinger_oscillator_getter_1min.py --symbol BTC

# Fetch for Ethereum explicitly
python klinger_oscillator_getter_1min.py --symbol ETHUSDT
```

## Execution Status: Failed
**The script failed to execute successfully.**

### Error Log
```text
  File "<exec>", line 127
    parser = argparse.ArgumentParser(description='Fetch Klinger's Oscillator (KO) for a given symbol on 1-minute candles from Binance.')
                                                                                                                                      ^
SyntaxError: unterminated string literal (detected at line 127)
```

### Explanation of Failure
The script crashed immediately due to a **SyntaxError** on line 127.

The error is caused by an unescaped single quote within a string literal defined by single quotes:
*   **Code:** `description='Fetch Klinger's Oscillator...'`
*   **Issue:** The Python interpreter interprets the apostrophe in `Klinger's` as the end of the string. The subsequent text (`s Oscillator...`) is then treated as invalid code, and the interpreter expects a closing parenthesis or comma that it never finds.

### Recommended Fix
To fix the script, the string definition on line 127 must be modified to handle the apostrophe correctly.

**Option 1: Use double quotes for the string**
```python
parser = argparse.ArgumentParser(description="Fetch Klinger's Oscillator (KO) for a given symbol on 1-minute candles from Binance.")
```

**Option 2: Escape the single quote**
```python
parser = argparse.ArgumentParser(description='Fetch Klinger\'s Oscillator (KO) for a given symbol on 1-minute candles from Binance.')
```