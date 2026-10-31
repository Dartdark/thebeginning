# Paid data that could help (Claude, 2026-10-22). Nothing to buy until the plan produces live results.

Ranked by value for money. Prices: only NYSE's are published (pricing sheet "as of October 2026"); the rest need a quote.
Step 1 for every item is free: ask for a sample and a quote; check coverage back to 2018 and how timestamps work.

| # | Data | Source | Price | What it would test | Why this rank |
|---|---|---|---|---|---|
| 1 | **CME pre-open indicative opening price** for NQ / ES at the Sunday 17:00 CT reopen (MDP 3.0 pre-open messages), 2018-26, only the 16:00-17:05 CT slice on Sundays | CME DataMine, or a reseller of CME Globex history (e.g. Databento, pay-as-you-go) | Quote; a ~1-hour weekly slice of one or two contracts should be among the cheapest items here | WATCHLIST #22 Sunday reopen push: $179 per NQ, t 2.5 at the first print, but only tradable via a pre-open order. Shows whether the indicative price called the side early enough | Strongest existing evidence; smallest, cheapest slice. **Free alternative: log the indicative price yourself on ~20 Sundays** (forward, slower) |
| 2 | **TAQ NYSE Arca Order Imbalances, SPY only** (opening + closing auction), 2018-26 | NYSE (datasales@nyse.com) | List $500 per month of history (≈ $52.5k for 2018-26, ≈ $30k for 2018-22); a SPY-only extract may be cheaper | Codex A (SPY opening imbalance → ES, 08:16-08:25 CT, the plan's emptiest window) and B (post-close reversal) | The empty 08:00-09:00 CT window; only worth it as a cheap SPY-only extract |
| 3 | **Nasdaq NOII** (Net Order Imbalance Indicator, opening and closing cross) for Nasdaq-100 stocks, 2018-26 | Nasdaq (historical TotalView-ITCH / NOII), or resellers | Quote | The NQ version of the auction idea (NYSE data doesn't cover Nasdaq-listed stocks) | Directly NQ, but heavier data and a 2021 rule change in disclosure timing |
| 4 | **Cboe Open-Close Volume Summary, 10-minute intraday** (SPX market-maker buy / sell volume), 2018-26 | Cboe DataShop | Quote | Codex D: expiry-day delta-decay hedging in ES, 14:32-14:49 CT | Novel, but the delivery timing of old intraday files must be verified first; trade-by-trade files arrive T+1 (unusable) |
| 5 | **TAQ NYSE Order Imbalance**, all NYSE stocks, 2018-26 | NYSE | List ≈ $58.5k | Upgrade ES MOC Follow with the real closing imbalance instead of the price proxy | ES MOC already works on the proxy; the most expensive item for an incremental gain |
| 6 | **CME calendar-spread / back-month data** for NQ and ES around quarterly rolls | CME DataMine or reseller | Quote | Roll-week flows traded as a spread (the outright roll shorts were already tested) | Lowest priority: needs a spread-trading setup and an Apex check |

Not needed any more: leveraged-ETF fund history (free from ProShares, test done: F), FINRA short volume and SEC fails
(free, sheets: DON'T TEST), Treasury auction results (free).

Recommendation: buy nothing now. When the plan has produced live results, start with #1 (likely cheapest, best evidence),
and only ask NYSE for a SPY-only quote (#2). Skip #5 and #6 unless something changes.
