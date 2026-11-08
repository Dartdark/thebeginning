Pair Trading Strategy: TQQQ and LQQ3
This repository presents a quantitative research project exploring mean-reversion strategies between TQQQ and LQQ3. It provides a transparent, reproducible framework—from historical data processing to final performance metrics.

Project Contents
The Paper: Our comprehensive study on the strategy's theoretical framework and empirical results.
The Code: Fully automated Python pipelines to process market data and generate trade signals.
The Data: Curated hourly datasets sourced from Stooq.com.
The Analysis: A complete performance audit including risk-adjusted returns, alpha, beta, and drawdown metrics.
Research Paper: You can read the full methodology, empirical analysis, and theoretical framework in our Pairtrading Strategy Research Paper.pdf.

Setup Instructions
This script is designed to run in Google Colab.

1. Directory Structure
Before running the code, ensure your Google Drive contains the following folder structure:

My Drive/
└── PairTrading/
    ├── data/
    │   └── cleansed/
    │       ├── tqqq.us.hourly.txt
    │       ├── lqq3.uk.hourly.txt
    │       └── gbpusd.hourly.txt
    └── output/ (The script will create this if it does not exist)

2. Environment
Open the .ipynb file in Google Colab.

The script will automatically prompt you to mount your Google Drive at /content/drive.

Ensure the file paths in the script match your Drive structure.

Requirements
If running locally, install the necessary dependencies:

pip install pandas numpy xlsxwriter

3. Strategy Overview
The strategy computes:

Ratio: TQQQ / (LQQ3_USD)

Z-Score: Mean reversion signal based on an EMA window.

Performance: Returns, Equity, Max Drawdown, Beta, and Alpha calculation.

Output
The script generates an Excel workbook (PairTrade_Final_Metrics_YYYYMMDD_HHMM.xlsx) in your PairTrading/output/ folder, containing raw data, trade signals, and summarized performance metrics.