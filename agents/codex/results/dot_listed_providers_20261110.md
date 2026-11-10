Author/origin: **dot**. Original acquisition report retained November 10, 2026. No acquisition or QA rerun for this publication. Raw data stays outside Git; paths below refer to the original PC package, not this report directory. See ../DOT_CONTRIBUTIONS.md for attribution and scope.

# Listed-provider data intake
Summary: Acquired 52 of 52 targeted public-data files, 262,684 dated records (247,963 nonmissing observations).
Coverage: 48 FRED series requested from 1990 through 2026-11-09, plus four World Bank annual indicators for USA, China, Japan, UK, Canada and euro area for 1990-2025.
Every saved raw file has a source URL, UTC acquisition timestamp and SHA256. No strategy returns, live changes or paused-scout changes.
These are current revised snapshots. Original release, historical available-at, native contract and executable price gates remain unresolved.
See coverage.csv and manifest.json for exact per-series ranges, failures and counts. Not an assertion of all possible provider data.

## What is useful
FRED: Treasury nominal and real yield curves, breakevens, policy rates, dollar/FX, Fed balance sheet/liquidity, inflation/labor/activity/housing, oil and gas. These support source comparisons and later admitted research; current revised macro data cannot serve as historical surprises.
World Bank: GDP growth, consumer-price inflation, trade/GDP and nominal GDP for six relevant economies. Annual slow-moving context, not intraday timing data.
Existing repository data was checked first: minute NQ/ES/GC/CL/YM/ZN/6E/BTC, Coinbase BTC spot, selected macro proxies, Cboe risk indices and NYFed funding already exist. No duplicate replacement or historical fill.

## Provider disposition
- pandas-datareader is a connector, not a separate owner of data. Downloaded from underlying FRED and World Bank public endpoints directly, without API keys.
- Yahoo/yfinance: no acquisition. yfinance is unofficial; Yahoo terms prohibit automated collection without prior permission. Existing owned Yahoo-derived proxy files were left unchanged.
- Interactive Brokers: no acquisition. Requires an authorized account/TWS or Gateway and appropriate entitlements. No sign-in, API keys, broker changes or orders.
- Polygon, now Massive: no acquisition. An API account/key is required. Current free-plan documentation is separate from the video's dated paid-plan claims. No registration or payment.
- Alpaca: no acquisition. Account credentials and feed entitlements are required for its stock data. Free IEX is not consolidated whole-market equity volume. No account or credentials accessed.
- Binance Vision: not acquired. Current dataset terms require acceptance and impose noncommercial-research restrictions, including prohibition on live proprietary trading execution. Parent asked to resolve terms before acquisition. This is not a technical connectivity failure.

## Validation and limits
CSV schema, numeric nonmissing values and duplicate-date counts checked; no missing-value fills. JSON schema and single-page totals checked. SHA256 recomputed before packaging.
End dates differ because frequency and publication lag differ. A date row with no value is not an observation.
World Bank null records remain null. Unit/frequency/revision metadata must be checked on linked series pages before analysis. Data is not point-in-time vintage history.
No source cross-validation of economic values, calendar-completeness certification or economic backtest was performed.
Two World Bank requests timed out in the full run and succeeded in a bounded longer-timeout retry. One first-run FRED request timed out. Its receipt is preserved; a separate short-timeout acquisition run supplies the package.
Repository snapshot inspected at e7291bfa777a452b092edd937c8ae8e2af2e133e; desktop checkout at eebf2ceae1825e74e0014fedf95488cd3e4bf59a. Raw snapshots are kept in this private delivery, not publicly redistributed.

## Attribution and source/access documentation
Data retrieved via FRED, Federal Reserve Bank of St. Louis: https://fred.stlouisfed.org/legal/
Each FRED series page is recorded in manifest.json and identifies its original agency/source. Retain applicable source rights; no implication of agency endorsement.
World Bank Indicators API: https://datahelpdesk.worldbank.org/knowledgebase/articles/889392
World Bank terms: https://www.worldbank.org/ext/en/legal/terms-conditions
pandas-datareader: https://pandas-datareader.readthedocs.io/en/latest/remote_data.html
Yahoo terms: https://legal.yahoo.com/us/en/yahoo/terms/otos/index.html
yfinance: https://ranaroussi.github.io/yfinance/
IB: https://www.interactivebrokers.com/docs/tws-api/doc/md/market-data-limitations
Massive: https://massive.com/knowledge-base/article/how-much-historical-stock-data-does-massive-have
Alpaca: https://docs.alpaca.markets/us/docs/about-market-data-api
Binance: https://github.com/binance/binance-public-data/blob/master/TERMS_AND_CONDITIONS.md

## Reproduce
python download.py NEW_OUTPUT_DIRECTORY
Standard-library Python only; directory must not exist. This downloads updated snapshots, which may differ. Compare hashes; never overwrite this capture.
