# dot: final intraday source and replication audit
Author: dot. November 10, 2026. No new numbered candidates.

## Existing Baltussen family, SSRN 3760365
[Published full JFE paper](https://academicweb.nd.edu/~zda/intramom.pdf), [SSRN](https://ssrn.com/abstract=3760365). The source signal is previous chosen close through the start of today's final half-hour, including overnight; only the final half-hour is held. This differs from first-half-hour momentum.

62 futures, December 1974–May 2020. Expanding forecast OOS uses at least 500 observations. Table 6's gross 1/N class Sharpes are equities 1.73, bonds 1.62, commodities 1.42 and currencies .87, not individual-contract results. Main results omit costs and warn trading may be uneconomic; an illustrative S&P one-tick-cost calculation is not broad retail validation.

Source windows: equity indices 15:30–16:00, CL/NG/HO 14:00–14:30, GC 13:00–13:30, Treasuries 14:30–15:00 in its US clock convention. FX tables and prose have conflicting clocks. Dated session conventions remain necessary.

Assessment: ordinary windows precede usual forced-flat deadlines, but account eligibility, native-contract endpoints and executable fills are not certified. Existing weak NQ and failed related momentum results remain. Non-equity extension is not several new independent papers. No new original-author return sample beyond May 2020 found.

### Newer evidence is not a clean universal answer
- [2024 Indian extension](https://www.researchgate.net/profile/Aanjaneya-Sharma/publication/383567351_Hedging_Demand_and_Intraday_Momentum_within_the_Indian_Stock_Market/links/66deae70b1606e24c21b276c/Hedging-Demand-and-Intraday-Momentum-within-the-Indian-Stock-Market.pdf): 2021–July 2024 observations, 44 selected stock futures, changed 20-minute hold and optimized filters. P&L excludes costs; authors warn closing impact can erase returns. Not untouched net US replication.
- [FirmTape](https://firmtape.com/research/is-intraday-momentum-still-alive): 2022–August 2026 SPX slope near zero, but code uses open-to-15:30, omitting overnight. No executable P&L. Not exact falsification.
- [Adaptive Infinity report 005](https://adaptive-infinity.com/graveyard/): SPY 2021–August 2026, reported net −.83 bp/day after .76 bp round trip. Changed ETF/deadband implementation, same-print timing, misattributed class Sharpe and sample beginning before SSRN posting weaken its replication claim.

No verified faithful post-2020 net multi-asset replication established.

## 7008318: changed-rule FX study, not a new qualified sleeve
[Full SSRN paper](https://papers.ssrn.com/sol3/Delivery.cfm?abstractid=7008318&mirid=1), 11 pages, June 27, 2026. London-opening 30-minute direction, entry afterward, unspecified selected London–New York exit. Dukascopy spot 2012–2024; Databento continuous 6J 2019–2024. Spot split 2012–18/2019–24; futures lack an independent earlier training sample. Constant costs. Table 2 reports net USDJPY Sharpe .722 and 6J .432: the abstract's futures rejection is sizing-based, not negative net return.

Source issues: conflicting IS/OOS regression coefficients and significance claims; negative-IS/positive-OOS direction under a supposedly frozen selection; unspecified exit/rolls and full-day volume filtering. These prevent promotion.

Assessment: the opening-window rule is not Baltussen's final-window rule. No post-publication validation, exact current-data fit or portfolio improvement established. The source's absence-of-micro-yen assertion is false: [CME listed Micro JPY/USD effective February 26, 2024](https://www.cmegroup.com/notices/ser/2024/01/SER-9326.html). Three $882 average losses total $2,646, not exhaustion of a $3,000 allowance; a short loss streak is not a pathwise ruin model. Correcting those errors does not validate trading.

## 7388124: novelty not established
[September 2026 SSRN record](https://ssrn.com/abstract=7388124) repeats the substantive nine-currency/21-year fixing mechanism of existing 3521370. Full text remains inaccessible. This supports duplicate-mechanism treatment, not any allegation about authorship. A new posting date is not fresh return evidence. Existing negative customer-cost fixing results remain.

No tests, code changes, purchases, account actions or paused-experiment resumption.
