# STC Getter (1-Minute)

## Description
`stc_getter_1min.py` is a command-line interface (CLI) tool designed to fetch real-time cryptocurrency market data and compute the **Schaff Trend Cycle (STC)** indicator.

The script connects to the **Binance Public API** (no API keys required) to retrieve 1-minute candlestick data (klines). It processes this data to calculate the STC, a technical indicator that combines the MACD and Stochastic oscillators to identify market trends and generate trading signals with reduced lag.

**Key Features:**
*   **Automated Symbol Mapping:** Automatically appends "USDT" to symbols (e.g., inputting `BTC` fetches `BTCUSDT`).
*   **Technical Analysis:** Computes MACD, Stochastic of MACD, and the final STC value.
*   **Signal Generation:** Generates `BUY`, `SELL`, or `HOLD` signals based on STC crossovers (Thresholds: 25 and 75).
*   **Trend Detection:** Identifies immediate trend direction (`UP`, `DOWN`, `FLAT`).

## Prerequisites
The script relies on the `python-binance` library to interact with the exchange API.

```bash
pip install python-binance
```

## Usage

Run the script from the terminal using Python 3.

### Arguments
*   `--symbol` (Required): The asset symbol (e.g., `BTC`, `ETH`, `SOL`).
*   `--limit` (Optional): Number of 1-minute candles to fetch (Default: 1000, Max: 1000).
*   `--verbose` (Optional): Prints debug information regarding data points and array lengths.

### Examples

**1. Basic Usage (Bitcoin):**
```bash
python stc_getter_1min.py --symbol BTC
```

**2. Custom Limit and Verbose Mode (Ethereum):**
```bash
python stc_getter_1min.py --symbol ETH --limit 800 --verbose
```

## Logic & Signals
The script calculates the STC using the following parameters:
1.  **MACD:** Fast EMA (23), Slow EMA (50).
2.  **Stochastic:** Period (10), K-Period (14).
3.  **STC:** EMA (3) of the Stochastic K.

**Signal Logic:**
*   **BUY:** Previous STC < 75.0 and Current STC >= 75.0.
*   **SELL:** Previous STC > 25.0 and Current STC <= 25.0.
*   **HOLD:** No crossover detected.

## Execution Output Analysis

The provided execution output indicates that the script **failed to run successfully**.

### Error Log
```text
ModuleNotFoundError: No module named 'binance'
```

### Explanation of Failure
The error `ModuleNotFoundError` occurs because the required third-party library, `python-binance`, is not installed in the Python environment where the script was executed.

To fix this error, the user must install the dependency via pip before running the script again:
```bash
pip install python-binance
```