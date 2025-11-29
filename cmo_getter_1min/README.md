# cmo_getter_1min.py - 1-Minute CMO Calculator

## Overview
This script calculates the **Chande Momentum Oscillator (CMO)** for a specific cryptocurrency symbol. It utilizes the **Binance public API** to fetch real-time market data on the **1-minute timeframe**.

The CMO is a technical momentum indicator developed by Tushar Chande. It calculates the difference between the sum of all recent gains and the sum of all recent losses, divided by the sum of all price movement over a given period. The result oscillates between -100 and +100.

### Key Features
- **Real-time Data:** Fetches live kline (candlestick) data from Binance.
- **Smart Symbol Resolution:** Automatically attempts to append "USDT" if the raw symbol (e.g., "BTC") is not found.
- **Configurable Period:** Allows the user to define the lookback period (default is 14).
- **No Authentication Required:** Uses public endpoints, so no Binance API keys are needed.

## Prerequisites

The script requires Python 3 and the `python-binance` library.

### Installation
To install the required dependency, run:

```bash
pip install python-binance
```

## Usage

Run the script from the command line using the following arguments:

```bash
python cmo_getter_1min.py --symbol <SYMBOL> [--period <INT>]
```

### Arguments

| Argument | Type | Required | Default | Description |
| :--- | :--- | :--- | :--- | :--- |
| `--symbol` | String | Yes | N/A | The trading pair (e.g., `BTCUSDT`) or coin symbol (e.g., `BTC`). |
| `--period` | Integer | No | 14 | The number of periods (minutes) used for the CMO calculation. |

### Examples

**1. Calculate CMO for Bitcoin (BTCUSDT) with default period (14):**
```bash
python cmo_getter_1min.py --symbol BTC
```

**2. Calculate CMO for Ethereum (ETHUSDT) with a 20-period lookback:**
```bash
python cmo_getter_1min.py --symbol ETHUSDT --period 20
```

## Execution Output Analysis

Based on the provided execution logs, the script failed to run successfully.

### Error Log
```text
ModuleNotFoundError: No module named 'binance'
```

### Explanation of Failure
The script terminated with a `ModuleNotFoundError`. This indicates that the external dependency **`python-binance`** is not installed in the Python environment where the script was executed.

The script imports `Client` from `binance.client` on line 9. Since the interpreter could not locate this package, execution stopped immediately before entering the `main()` function.

### Resolution
To fix this error, install the missing library using pip as described in the **Installation** section above.