# GemHunter Dual-Signal Scanner

## Overview
**GemHunter-Dual-Signal-Scanner.py** is a technical analysis automation tool designed to scan cryptocurrency markets for high-probability trading setups. It utilizes the Binance public API to fetch historical candle data and applies a multi-stage algorithmic filter to identify assets undergoing accumulation before a potential breakout.

The script implements a "Dual-Signal" strategy combining volatility squeezes, momentum divergence, and volume anomalies.

## Technical Strategy
The scanner processes a predefined list of pairs (e.g., BTCUSDT, ETHUSDT) on the **1-Hour Timeframe** through four distinct phases:

1.  **Phase 1: Squeeze & Accumulation**
    *   **Bollinger Band Width (BBW):** Detects low volatility. Current BBW must be near the 50-period low.
    *   **On-Balance Volume (OBV):** Checks for a positive slope (linear regression) over the last 14 periods to confirm accumulation during the squeeze.
2.  **Phase 2: Dual-Signal Trigger**
    *   **RSI Divergence:** Identifies bullish divergence (Price makes a Lower Low while RSI makes a Higher Low).
    *   **MACD Validation:** Requires a MACD Histogram flip (negative to positive) or the MACD Line crossing zero.
3.  **Phase 3: Volume Injection**
    *   Validates breakout potential via the Volume Oscillator (> 20) or a raw volume spike (> 150% of the 20-period SMA).
4.  **Phase 4: Risk Management**
    *   Calculates dynamic Stop Loss levels using ATR (Average True Range) or the Lower Bollinger Band.
    *   Sets initial Take Profit targets at the Upper Bollinger Band.

## Prerequisites
*   Python 3.7+
*   Internet connection (to access Binance API)

## Dependencies
The script requires the following external Python libraries:
*   `python-binance` (API wrapper)
*   `pandas` (Data manipulation)
*   `numpy` (Mathematical calculations)

## Installation
1.  Clone or download the repository.
2.  Install the required dependencies using pip:

```bash
pip install python-binance pandas numpy
```

## Usage
Run the script directly from the terminal:

```bash
python GemHunter-Dual-Signal-Scanner.py
```

### Configuration
You can modify the top section of the script to customize the scan:
*   `TIMEFRAME`: Change candle interval (e.g., `Client.KLINE_INTERVAL_4HOUR`).
*   `PAIRS_TO_SCAN`: Add or remove specific trading pairs.
*   `LIMIT`: Adjust the amount of historical data fetched (default is 100 candles).

## Output
If the scanner finds pairs matching all criteria, it generates two files in the working directory:
1.  **`gemhunter_results.json`**: Detailed signal data in JSON format.
2.  **`gemhunter_results.csv`**: A spreadsheet-compatible summary of the signals, including entry price, stop loss, and indicator values.

## Execution Analysis & Troubleshooting

### Observed Execution Output
When running the script in the provided environment, the following error occurred:

```text
Error: Traceback (most recent call last):
  ...
  File "<exec>", line 7, in <module>
ModuleNotFoundError: No module named 'binance'
```

### Explanation of Failure
The script failed to execute because the **`python-binance`** library was not installed in the Python environment. The import statement `from binance.client import Client` triggered a `ModuleNotFoundError`.

### Resolution
To fix this error, you must install the missing library. Run the following command in your terminal or command prompt:

```bash
pip install python-binance
```

Once installed, the script will be able to import the client, connect to the Binance API, and perform the market scan.