# Stochastic RSI Getter (1-Minute Timeframe)

## Overview
`stoch_rsi_getter_1min.py` is a Python script designed to calculate the current Stochastic RSI (Relative Strength Index) for a specific cryptocurrency symbol. It utilizes the Binance public API to fetch the most recent 1-minute candlestick data and computes technical indicators locally.

## Features
- **Real-time Data:** Fetches the last 200 1-minute candles (klines) from Binance.
- **No Authentication Needed:** Uses public API endpoints, so no API keys are required.
- **Robust Networking:** Includes retry logic with exponential backoff to handle API rate limits or network jitter.
- **Technical Calculation:**
  - **RSI Period:** 14
  - **Stoch %K:** Calculated over the last 14 RSI values.
  - **Stoch %D:** Simple Moving Average (SMA) of the last 3 %K values.

## Execution Output Analysis
The provided execution logs indicate that the script **failed to run** due to a missing dependency.

**Error Log:**
```text
ModuleNotFoundError: No module named 'binance'
```

**Explanation:**
The script relies on the `python-binance` library to interact with the Binance API. The environment where the script was executed did not have this package installed. To fix this, the library must be installed via pip (see Installation below).

## Prerequisites
- Python 3.6+
- `pip` (Python package manager)

## Installation

1. **Install the required library:**
   The script depends on the `python-binance` wrapper. Install it using the following command:
   ```bash
   pip install python-binance
   ```

## Usage

Run the script from the command line, providing the target symbol using the `--symbol` argument. You can provide the symbol with or without the "USDT" suffix (the script defaults to appending USDT if omitted).

### Basic Command
```bash
python stoch_rsi_getter_1min.py --symbol BTC
```

### Explicit Pair
```bash
python stoch_rsi_getter_1min.py --symbol ETHUSDT
```

### Expected Output
On successful execution, the script prints a single formatted line containing the symbol, timestamp, and calculated values:

```text
BTCUSDT | Time (UTC): 2023-10-27T10:05:00Z | StochRSI_K: 85.20 | StochRSI_D: 80.10 | RSI_current: 65.40 | RSI_min_last14: 40.00 | RSI_max_last14: 70.00
```

## Technical Details

### Calculation Logic
1. **Data Fetching:** Retrieves the most recent 200 candles for the 1-minute interval.
2. **RSI Calculation:** Computes the standard Relative Strength Index over a 14-period window.
3. **Stochastic RSI Calculation:**
   - **%K:** `(Current RSI - Lowest RSI in last 14) / (Highest RSI in last 14 - Lowest RSI in last 14) * 100`
   - **%D:** The average of the last 3 %K values.

### Error Handling
The script implements a `fetch_klines_with_retry` function. If the Binance API returns a 429 (Rate Limit) or a network error occurs, the script will retry up to 5 times with increasing delays between attempts.