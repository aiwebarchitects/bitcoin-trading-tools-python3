# Order Book Imbalance (OBI) Calculator

## Description
`order_book_imbalance_getter_1min.py` is a Python script designed to monitor supply and demand pressure for cryptocurrency assets on the Binance exchange.

The script fetches the order book depth (bids and asks) for a specified trading pair and calculates the **Order Book Imbalance (OBI)**. The OBI is a metric ranging from -1 to 1:
*   **Positive values (> 0):** Indicate higher bid pressure (buying momentum).
*   **Negative values (< 0):** Indicate higher ask pressure (selling momentum).
*   **Zero:** Indicates perfect equilibrium or lack of data.

The script runs continuously in a loop, emitting structured JSON data to `stdout` at a defined interval (default: 60 seconds). It handles API rate limits and connection errors with a retry mechanism.

## Dependencies
The script requires the `python-binance` library to interact with the Binance API.

```bash
pip install python-binance
```

## Usage

The script is executed via the command line. It accepts arguments to define the target asset, the depth of the order book to analyze, and the sampling frequency.

### Basic Usage
Monitor Bitcoin (BTCUSDT) with default settings (top 5 levels, every 60 seconds):
```bash
python order_book_imbalance_getter_1min.py --symbol BTC
```

### Advanced Usage
Monitor Ethereum (ETHUSDT), analyzing the top 20 order book levels, sampling every 10 seconds:
```bash
python order_book_imbalance_getter_1min.py --symbol ETH --levels 20 --interval_seconds 10
```

### Arguments
| Argument | Type | Required | Default | Description |
| :--- | :--- | :--- | :--- | :--- |
| `--symbol` | String | Yes | N/A | The base asset symbol (e.g., `BTC`, `ETH`). The script automatically appends `USDT`. |
| `--levels` | Integer | No | 5 | The number of order book levels (depth) to calculate notional value against. |
| `--interval_seconds` | Integer | No | 60 | The wait time between data samples in seconds. |

## Output Format
The script outputs a JSON object for every interval to standard output (`stdout`). Logs and errors are printed to standard error (`stderr`).

**Example JSON Output:**
```json
{
  "timestamp": "2023-10-27T10:00:00Z",
  "symbol": "BTCUSDT",
  "obi": 0.154321,
  "notional_bid": 150000.50,
  "notional_ask": 110000.25,
  "levels": 5
}
```

## Execution Output Analysis

When attempting to run the script in the provided environment, the execution failed.

**Log Output:**
```text
Error: Traceback (most recent call last):
  ...
  File "<exec>", line 12, in <module>
ModuleNotFoundError: No module named 'binance'
```

### Explanation of Failure
The script failed with a `ModuleNotFoundError`. This indicates that the required third-party library, `python-binance`, is not installed in the Python environment where the script was executed.

To fix this error, the user must install the package using pip:
```bash
pip install python-binance
```