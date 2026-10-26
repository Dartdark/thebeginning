<div align="center">

# 📈 Global Stock Market Indices Historical Dataset
### Multi-Continental Equity Benchmarks, Derivatives & Volatility Proxies

[![Kaggle](https://img.shields.io/badge/Platform-Kaggle-blue?logo=kaggle)]()
[![Files](https://img.shields.io/badge/Files-54_Indices-blueviolet)]()
[![Domain](https://img.shields.io/badge/Domain-Quantitative_Equities-2c3e50)]()
![Date](https://img.shields.io/badge/date-2026--07--04-blue)

*54 global equity indices mapping the pulse of international market sentiment, systemic risk, and macro-economic health.*

</div>

## 📖 1. Executive Summary & Market Context
Equity indices are the most widely watched macroeconomic barometers in the world. They aggregate millions of micro-decisions into a single quantifiable time-series, reflecting liquidity, corporate earnings expectations, and geopolitical risk. 

This dataset provides daily OHLC historical data for over 50 global stock market indices, meticulously segmented across the Americas, Europe, Asia-Pacific, and the Middle East/Africa. Crucially, this dataset does not stop at cash indices; it includes **E-mini futures contracts** (e.g., E-mini S&P 500, E-mini NASDAQ) and the **VIX (CBOE Volatility Index)**. This makes it a complete, institutional-grade toolkit for analyzing market contagion, systemic risk, and the basis between cash equities and their derivative counterparts.

---

## 🗂️ 2. Dataset Architecture & Exhaustive File Inventory

The `global-stocks/` directory is categorized by geographic regions and instrument types to facilitate cross-continental macro-analysis:

### A. The Americas (North & South)
*   **US Major Indices:** `bourse_sp-500.json` (Large Cap), `bourse_nasdaq.json` (Tech/Growth), `bourse_dow.json` (Blue Chip/Industrial).
*   **US Market Breadth & Futures:** `smallcap-2000.json` (Russell 2000), `us-futures-e-mini-s-p-500.json`, `us-futures-e-mini-nasdaq-100.json`, `us-futures-e-mini-s-p-midcap.json`, `us-futures-e-mini-s-p-smallcap.json`, `us-futures-russell-2000-mini.json`, `us-futures-s-p-500-index.json`.
*   **Latin America:** `bovespa.json` (Brazil), `ipc.json` (Mexico).

### B. Europe (Developed & Emerging)
*   **Core Europe:** `bourse_dax.json` (Germany), `bourse_cac-40.json` (France), `bourse_ftse-100.json` (UK).
*   **Peripheral & Broad Europe:** `euro-stoxx-50.json`, `bourse_stoxx-600.json`, `aex.json` (Netherlands), `bel-20.json` (Belgium), `psi-20.json` (Portugal), `ibex-35.json` (Spain), `ftse-mib.json` (Italy).
*   **Eastern Europe:** `bist-100.json` (Turkey), `micex.json` (Russia), `wig20.json` (Poland), `budapest-se.json` (Hungary).

### C. Asia-Pacific (Advanced & Frontier)
*   **Advanced Asian:** `bourse_nikkei-225.json` (Japan), `bourse_hang-seng.json` (Hong Kong), `kospi.json` (South Korea), `taiwan-weighted.json` (Taiwan), `s-p-asx-200.json` (Australia), `nz-50.json` / `dj-new-zealand.json` (New Zealand).
*   **Emerging Asian:** `bourse_shanghai.json` (China Mainland), `szse-component.json` (Shenzhen), `china-a50.json` (Offshore China), `bse-sensex.json` & `nifty-50.json` (India), `set.json` (Thailand), `idx-composite.json` (Indonesia), `psei-composite.json` (Philippines), `karachi-100.json` (Pakistan).

### D. Middle East & Africa
*   `tadawul-all-share.json` (Saudi Arabia - Tadawul), `cse-all-share.json` (Sri Lanka), `rtsi.json` (Russia RTS).

### E. Volatility & Derivatives (The Fear Gauge)
*   `cboe-s-p-500-vix-us-futures.json` (Crucial for risk modeling), `us-futures-dax-index.json`, `us-futures-djia-mini-sized.json`.

---

## 🧬 3. Deep Data Schema & Ingestion Logic

The data utilizes the standardized JSON wrapper. Because equity indices often have large nominal values (e.g., S&P 500 at 5,000+), comma separation removal is mathematically critical to prevent dimensionality errors in ML models.

### 🛠️ Advanced Python Ingestion & Volatility Engineering
```python
import json
import pandas as pd
import re
import numpy as np

class EquityIndexIngestor:
    @staticmethod
    def load_and_engineer(filepath: str) -> pd.DataFrame:
        with open(filepath, 'r', encoding='utf-8') as f:
            raw = json.load(f)
            
        df = pd.DataFrame(raw['data'], columns=[
            'Open', 'Low', 'High', 'Close', 'Abs_Change', 'Pct_Change', 'Gregorian_Date', 'Jalali_Date'
        ])
        
        # Robust vectorized cleaning
        for col in ['Open', 'Low', 'High', 'Close', 'Abs_Change']:
            df[col] = pd.to_numeric(df[col].astype(str).str.replace(',', ''), errors='coerce')
            
        df['Pct_Change'] = pd.to_numeric(
            df['Pct_Change'].astype(str).str.replace(r'<[^>]+>', '', regex=True).str.replace('%', ''),
            errors='coerce'
        )
        df['Gregorian_Date'] = pd.to_datetime(df['Gregorian_Date'])
        
        # Quant Feature Engineering: Log Returns & Realized Volatility
        df['Log_Return'] = np.log(df['Close'] / df['Close'].shift(1))
        df['Realized_Vol_20D'] = df['Log_Return'].rolling(window=20).std() * np.sqrt(252) # Annualized
        
        return df.set_index('Gregorian_Date').dropna()

# Example: Comparing US Cash vs Futures
# spx_cash = EquityIndexIngestor.load_and_engineer('global-stocks/bourse_sp-500.json')
# spx_futures = EquityIndexIngestor.load_and_engineer('global-stocks/us-futures-e-mini-s-p-500.json')
```

---

## 🔬 4. Advanced Quantitative & Scientific Applications

### A. Market Contagion & Dynamic Correlation Networks
Financial crises rarely stay contained. You can use this dataset to build a **Dynamic Conditional Correlation (DCC-GARCH)** model. By feeding it the `Log_Return` series of the Nikkei, DAX, and S&P 500, you can empirically visualize how a shock in the Asian session propagates to Europe and then the US, measuring the exact increase in cross-asset correlation during a crash.

### B. Risk-On / Risk-Off (RoRo) Regime Detection
Use Unsupervised Machine Learning (e.g., **Hidden Markov Models - HMM** or **Gaussian Mixture Models**) on a matrix consisting of the S&P 500 returns (Risk-On proxy) and the VIX index returns (Risk-Off proxy). This allows you to algorithmically classify historical days into distinct "Regimes" (Bull, Bear, High-Volatility Transition), which is the foundation of modern institutional asset allocation.

### C. Index Arbitrage & Basis Trading
Compare the cash index (`bourse_sp-500.json`) with its respective futures contract (`us-futures-e-mini-s-p-500.json`). The difference between the two is the "Basis". You can build an algorithmic trading model to exploit temporary mispricings between the cash and futures markets, especially as contracts approach expiry (the "roll" period).

---

## 📚 5. Rigorous Academic Citation

**BibTeX Format:**
```bibtex
@misc{amani_2024_stocks,
  author       = {Mohammadreza Amani},
  title        = {Global Stock Market Indices Historical Dataset},
  year         = {2024},
  publisher    = {Kaggle},
  url          = {https://www.kaggle.com/datasets/mohammadrezaamani/global-stock-market-indices-historical-dataset},
  note         = {Includes global cash indices, e-mini futures, and VIX volatility proxies.}
}
```
**APA Format:**
> Amani, M. (2024). *Global Stock Market Indices Historical Dataset* [Data set]. Kaggle. https://www.kaggle.com/datasets/mohammadrezaamani/global-stock-market-indices-historical-dataset

**MLA Format:**
> Amani, Mohammadreza. "Global Stock Market Indices Historical Dataset." *Kaggle*, 2024, www.kaggle.com/datasets/mohammadrezaamani/global-stock-market-indices-historical-dataset.

---

## 👤 6. Author & Contact
**Mohammadreza Amani**  
🔗 [GitHub Profile](https://github.com/MohammadrezaAmani)  
✉️ [more.amani@yahoo.com](mailto:more.amani@yahoo.com)

---
<div align="center">

**⚖️ Disclaimer:** *This dataset is provided for educational, research, and algorithmic backtesting purposes only. While every effort has been made to ensure data quality and consistency, no guarantee is made regarding its completeness or accuracy. This dataset does not constitute financial, investment, or trading advice.*

<br>

**🙏 Acknowledgements:** *The documentation for this project was prepared with the assistance of **Zhipu AI - GLM-4.7**. AI was used to improve the writing, structure, and readability of the documentation, while the dataset, data collection, processing, validation, and maintenance were carried out by the author.*

<br>

*If this dataset saves you hours of data collection or proves useful in your research or projects, please consider giving it an ⭐ on GitHub and an ⬆️ **Upvote** on Kaggle. Your support helps keep the dataset actively maintained and regularly updated.*

</div>
