# Cleansed Data
This directory is intended to store the input files for the Pair Trading strategy.

## Data Source & Acquisition
The empirical analysis uses historical market data obtained from [Stooq.com](https://stooq.com/). Due to data redistribution policies, the raw datasets are not included in this repository. 

To replicate the analysis, please download the hourly data from Stooq and place the files in this directory with the following names:
* `tqqq.us.hourly.txt` (TQQQ: US-listed 3× leveraged ETF tracking the Nasdaq-100)
* `lqq3.uk.hourly.txt` (LQQ3: UK-listed 3× leveraged ETF tracking the Nasdaq-100)
* `gbpusd.hourly.txt`  (GBP/USD: Exchange rate)

*Note: The datasets should cover approximately two years of observations.*

## File Format Requirements
The script expects files in either `.txt` or `.csv` format. Files must contain the following columns:
* **DATE**: Format `YYYYMMDD`
* **TIME**: Format `HHMMSS` (The script filters specifically for `160000`)
* **OPEN**: Price data