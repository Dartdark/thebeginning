# ProShares Nasdaq-100 leveraged / inverse ETF daily history (downloaded 2026-10-22)

Source: ProShares "NAV History" CSV on each fund page, `https://accounts.profunds.com/etfdata/ByFund/<TICKER>-historical_nav.csv`.
Files: TQQQ (3x), SQQQ (−3x), QLD (2x), QID (−2x), from inception to 2026-10-21.
Columns: Date, NAV, Prior NAV, NAV change, Shares Outstanding (000), Assets Under Management ($).

Point-in-time use: the row dated D is the 16:00 ET NAV of day D, published that evening. For a trade on day D use the
row for D−1 (prior-day assets). NAV and shares are split-adjusted (early rows look odd); use the AUM column, which is
not affected by splits. The files are today's snapshot of history: later revisions can't be ruled out.
