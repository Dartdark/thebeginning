# dot: SSRN continuation, pass 22
Author: dot. November 10, 2026. Research only.

## 63. Information in Yield Spread Trades
Yang-Ho Park, [SSRN 3371461](https://ssrn.com/abstract=3371461), [FEDS 2019-025 full manuscript](https://www.federalreserve.gov/econres/feds/files/2019025pap.pdf), March 26, 2019. Full equations inspected visually.

**Source:** Legacy futures-only numbers of noncommercial traders, long minus short, in Eurodollar, ten-year Treasury and thirty-year Treasury futures. Demean across the three markets each date. STEEP averages the indicator of positive excess Eurodollar and negative excess thirty-year net traders over a trailing quarter, t−q < τ ≤ t. At scheduled FOMC meeting t, use STEEP(t) to forecast pre-announcement S&P-futures return at t+1. Trade predicted sign from 09:30 Eastern to fifteen minutes before the next announcement. Initial regression sample September 1997–December 2002; rolling re-estimation, OOS January 2003–July 2017. Table 8 reports same-day OOS R²16.8%, annualized Sharpe 1.085 versus .748 always-long. Annualization formula, rolling-window length, costs and contract ticker are not specified. Overnight variant underperforms. Printed pp.9,18–22,34–35 supply formulas and results.

**Assessment:** A genuine distinct intraday hypothesis, not an admitted strategy. No exact ID/mechanism found in the 62-entry index, TIER_LIST, MINED_INDEX or DATA_NEEDED. Existing failed unconditional pre-FOMC and index-COT filters remain relevant controls, not identical tests.

### Exact gates before any later authorized test
- Use counts of traders, not contract positions. A familiar COT panel may lack the required fields.
- Trailing quarter is causal in the formula; it does not include future calendar-quarter observations. Exact operational quarter definition still needs freezing.
- Observation date is not public-release date. [CFTC schedules](https://www.cftc.gov/MarketReports/CommitmentsofTraders/ReleaseSchedule/index.htm) distinguish them. A Tuesday count may be unreleased at Wednesday's forecast date. Because trading is at the next meeting, the missing release bridge does not automatically prove future-return leakage, but the claimed forecast chronology must be reconstructed.
- Refitting needs completed predictor/outcome pairs, exact window length and historical coefficients. Do not use Table 7's full-sample coefficients as the OOS trading threshold.
- Source identifies S&P500 futures, not a confirmed ES contract. SP in its positioning notation means speculator count, not proof of a ticker.
- Verify event-frequency normalization, cash treatment, zero forecasts, actual announcement clocks, price endpoints, contracts/rolls, commissions and attainable fills. Author-reported Sharpe 1.085 is not independently normalized or net.
- [Eurodollar conversion in April 2023](https://www.cmegroup.com/media-room/press-releases/2023/4/24/cme_group_completeskeymilestonesinconversionofeurodollarfutureso.html) creates a modern signal break. SOFR trader counts cannot be silently spliced.
- Historical pseudo-OOS is not a prospective or untouched modern holdout.

### Version and category
The [published 2022 article](https://ideas.repec.org/a/eee/finmar/v59y2022ipas1386418121000586.html), *Spread position as a leading economic indicator*, emphasizes macroeconomic and Treasury-curve forecasts. Its full text was unavailable. The FOMC trading result is verified in the 2019 working paper only, not established as surviving the final version.

Personal/intraday research: yes, source holding is same-day. Apex holding criterion: plausible only after exact instrument/calendar and forced-flat handling; no blanket legal certification. Existing-data testability: **no admission**, released trader-count history and model specification unresolved. Potential complement is event-selective exposure, but it remains equity-index risk and no account-survival improvement is proven.

## Separate Treasury-efficiency exclusion
Lin, Lo and Qiao, *Macroeconomic news announcements and market efficiency*, [DOI 10.1016/j.jbankfin.2021.106252](https://ideas.repec.org/a/eee/jbfina/v133y2021ics0378426621002119.html). Abstract describes greater measured inefficiency shortly before news. Full source and SSRN identity unverified. A search snippet's profitable order-flow discussion references other research. No executable directional signal or net strategy established here.

## Status
63 numbered research entries, not qualified strategies. No new current-data admission; no tests, orders, code changes, purchases or paused-experiment resumption.
