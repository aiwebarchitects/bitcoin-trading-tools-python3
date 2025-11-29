# Hull Moving Average (HMA) 1-Minute Calculator

## Description
`hull_moving_average_1min.py` is a Python script designed to calculate the Hull Moving Average (HMA) for cryptocurrency assets. It utilizes real-time market data from the Binance exchange, specifically focusing on 1-minute candlestick intervals.

The Hull Moving Average is a technical indicator developed by Alan Hull to reduce the lag associated with traditional moving averages while retaining curve smoothing. This script computes the HMA to help identify short-term trend directions (Up, Down, or Flat).

### Key Features
*   **Data Source:** Fetches live 1-minute kline (candlestick) data from Binance.
*   **Algorithm:** Implements the standard HMA formula: $HMA = WMA(2 \times WMA(n/2) - WMA(n), \sqrt{n})$.
*   **Flexible Inputs:** Supports custom symbols (e.g., BTC, ETHUSDT) and adjustable lookback periods.
*   **JSON Output:** Returns structured JSON data containing the calculated HMA, current price, timestamp, and trend direction, making it suitable for integration into larger trading bots or dashboards.

## Execution Output Analysis
The provided execution logs indicate that the script **failed to run successfully**.

### Error Log
```text
ModuleNotFoundError: No module named 'binance'
```

### Explanation
The error `ModuleNotFoundError` occurs because the required third-party library, `python-binance`, is not installed in the Python environment where the script was executed. The script attempts to import `Client` from `binance.client`, but Python cannot locate this package.

To fix this, the dependency must be installed via pip (see **Installation** below).

## Installation

1.  Ensure Python 3 is installed.
2.  Install the required Binance client library:
    ```bash
    pip install python-binance
    ```

## Usage

Run the script from the command line, specifying the target symbol. You can optionally define the HMA period (default is 14).

### Basic Usage
```bash
python hull_moving_average_1min.py --symbol BTC
```
*Note: The script automatically attempts to resolve symbols to their USDT pair (e.g., 'BTC' becomes 'BTCUSDT') if a suffix is not provided.*

### Custom Period
To calculate a 55-period HMA for Ethereum:
```bash
python hull_moving_average_1min.py --symbol ETHUSDT --period 55
```

### Arguments
| Argument | Type | Required | Default | Description |
| :--- | :--- | :--- | :--- | :--- |
| `--symbol` | String | Yes | N/A | The trading symbol (e.g., BTC, ETHUSDT). |
| `--period` | Integer | No | 14 | The lookback period for the HMA calculation. |

## Output Format
On success, the script prints a JSON object to `stdout`:

```json
{
    "symbol": "BTCUSDT",
    "period": 14,
    "hma": 64500.25,
    "last_close": 64510.00,
    "timestamp": "2023-10-27T10:00:00Z",
    "trend": "Up"
}
```

*   **hma**: The calculated Hull Moving Average value.
*   **last_close**: The closing price of the most recent 1-minute candle.
*   **trend**: Indicates the slope of the HMA ("Up", "Down", or "Flat").