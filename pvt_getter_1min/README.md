# pvt_getter_1min.py - 1-Minute Price-Volume Trend (PVT) Calculator

## Description
`pvt_getter_1min.py` is a Python script designed to calculate the Price-Volume Trend (PVT) technical indicator for cryptocurrency assets. It utilizes the Binance public API to fetch historical price and volume data on a 1-minute timeframe.

**Key Features:**
*   **Symbol Normalization:** Automatically appends "USDT" to symbols if not provided (e.g., inputting "BTC" converts to "BTCUSDT").
*   **Data Fetching:** Retrieves the last 200 1-minute kline (candlestick) bars from Binance.
*   **Calculation:** Computes the cumulative PVT based on percentage price change multiplied by volume.
*   **Dual Output:** Generates a detailed JSON time-series for programmatic use and a human-readable summary of the latest value.
*   **No Authentication:** Uses public endpoints, so no Binance API keys are required.

## Dependencies
The script requires the following external Python library:
*   `python-binance`

To install the dependency, run:
```bash
pip install python-binance
```

## Usage
Run the script from the command line, providing the target symbol via the `--symbol` argument.

### Command Syntax
```bash
python pvt_getter_1min.py --symbol <SYMBOL>
```

### Examples
**Calculate PVT for Bitcoin (BTCUSDT):**
```bash
python pvt_getter_1min.py --symbol BTC
```

**Calculate PVT for Ethereum (ETHUSDT):**
```bash
python pvt_getter_1min.py --symbol ETHUSDT
```

## Output Format
The script prints a JSON object to `stdout`, followed by a plain text summary line.

**JSON Structure:**
```json
{
  "symbol": "BTCUSDT",
  "interval": "1m",
  "pvt": [
    { "t": 1620000000000, "pvt": 0.0 },
    { "t": 1620000060000, "pvt": 120.5 },
    ...
  ]
}
```
*   `t`: Timestamp (milliseconds)
*   `pvt`: Calculated Price-Volume Trend value

**Summary Line:**
```text
Latest PVT for BTCUSDT at 2023-10-27 10:00:00: 4502.33
```

## Execution Output Analysis
The provided execution logs indicate that the script **failed to run successfully**.

### Error Log
```text
ModuleNotFoundError: No module named 'binance'
```

### Explanation
The error `ModuleNotFoundError` occurred because the external library `python-binance` was not installed in the Python environment where the script was executed.

While the script imports standard libraries (`argparse`, `json`, `sys`, `datetime`, `math`), it relies on `binance.client` to fetch market data. This is a third-party package that must be installed via `pip` before the script can function.