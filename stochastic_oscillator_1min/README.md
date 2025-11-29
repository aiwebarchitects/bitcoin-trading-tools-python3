# Stochastic Oscillator (1-Minute) Calculator

## Description
`stochastic_oscillator_1min.py` is a Python script designed to calculate the Stochastic Oscillator technical indicator for cryptocurrency pairs. It utilizes the Binance API to fetch real-time, 1-minute candlestick (kline) data.

The script computes two variations of the oscillator:
1.  **Fast Stochastic:**
    *   **%K:** Calculated over a 14-period window.
    *   **%D:** 3-period Simple Moving Average (SMA) of Fast %K.
2.  **Slow Stochastic:**
    *   **%K:** Equivalent to Fast %D.
    *   **%D:** 3-period SMA of Slow %K.

The output is provided in a machine-readable JSON format, making it suitable for integration into trading bots or data pipelines.

## Dependencies
The script requires the `python-binance` library to interact with the Binance API.

```bash
pip install python-binance
```

## Usage

Run the script from the command line, providing the target symbol via the `--symbol` argument.

### Basic Command
```bash
python stochastic_oscillator_1min.py --symbol BTCUSDT
```

### Implicit USDT Pairing
The script automatically appends "USDT" if a base asset is provided without a quote currency.
```bash
python stochastic_oscillator_1min.py --symbol BTC
# Interpreted as BTCUSDT
```

## Output Format
On success, the script prints a JSON object to `stdout`:

```json
{
  "symbol": "BTCUSDT",
  "time": "2023-10-27T10:00:00Z",
  "fastK": 85.2341,
  "fastD": 82.1005,
  "slowK": 82.1005,
  "slowD": 79.4421
}
```

## Execution Analysis

### Execution Output
The following error was observed during the execution of the script:

```text
Error: Traceback (most recent call last):
  ...
  File "<exec>", line 34, in <module>
ModuleNotFoundError: No module named 'binance'
```

### Failure Explanation
The script failed to execute because of a **missing dependency**.

1.  **Error Type:** `ModuleNotFoundError`
2.  **Cause:** The Python environment where the script was executed did not have the `python-binance` package installed. The script attempts to import `Client` and exceptions from `binance.client` and `binance.exceptions` on lines 34-35, which triggered the crash.
3.  **Resolution:** To fix this error, the user must install the required library using pip:
    ```bash
    pip install python-binance
    ```