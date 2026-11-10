# dot: SSRN continuation, pass 2
Author: dot. Date: 2026-11-10. Branch: codex/work. Research only; no return tests or deployment.
This supplements the ten-paper shortlist, intraday reserves, and existing-data audit. It does not promote papers into the strategy tier list.

## Summary
Three distinct additional hypotheses merit retaining, but none is ready to build or trade.
Pre-refunding Treasury drift is the most useful new calendar lead, with a large headline-Sharpe qualification.
Semivariance-conditioned trend is an implementable research concept, not an established US-futures replication.
Policy-conditioned FX carry needs substantial additional inputs and preserves multiweek exposure.
No new paper in this pass qualifies as both strong evidence and verified testable using current data.

## 21. Pre-Refunding Announcement Gains in U.S. Treasurys
Wang and Zhao. [SSRN 4764295](https://ssrn.com/abstract=4764295). [Author manuscript, July 16 2025](https://chenwang.one/files/pretra.pdf), sections 2–4.3 and Table 5.

**Source evidence:** The paper studies 129 quarterly events from 1991–2023. Medium/long Treasury prices rise on the business day before the borrowing-estimate announcement, usually Monday at 15:00 Eastern; this is not the later Wednesday security-detail release. Mean event-day returns are 12.62 basis points for 10-year and 24.3 for 30-year bonds. Tradeweb midquotes from 2006–2023 show gains during 07:30–17:00 Eastern. The mechanism is resolution of fiscal uncertainty. Table 5 annualizes selected event-day statistics using 252 days, producing a 30-year Sharpe of 4.50. The strategy evidence is gross; four basis points of costs are an illustration, not a complete net execution backtest. No untouched prospective holdout was established. CRSP and Tradeweb provide the principal price inputs.

**dot assessment and build gate:** Personal: conditional lead. Intraday: possible adaptation, not the published daily replication; the 17:00 exit is too late for the previously checked Apex cutoffs. Existing data: not verified. A ZN or ZB translation changes duration, instrument and execution; cash-bond return evidence cannot be copied onto futures.
Four quarterly trades at the reported 30-year mean imply about 0.97% gross annual simple return before idle-cash accounting, not 60% attainable annual return. A simple independent-event Sharpe rescaling gives approximately 0.57, not a validated strategy estimate. Sparse-event exposure could complement frequent equity trades but does not remove duration or fiscal-event losses.
Before any later authorized test: recover historical announcement dates as known then; specify previous-business-day trading, cash/futures mapping, holidays, entry/exit and roll; build a realistic spread/commission model; freeze a recent holdout. Public event dates may be available, but current auction data are not automatically this event calendar. Licensed source data and redistribution rights require checking.
Repository comparison: no exact SSRN/title match found; existing month-end Treasury tests are different. This is a distinct lead, not a new proof of profitability.

## 22. Time Series Momentum and Reversal: Intraday Information from Realized Semivariance
Liu, Lu, Li and Wang. [SSRN 3584014](https://ssrn.com/abstract=3584014). [Full text](https://www.researchgate.net/publication/340925511_Time_Series_Momentum_and_Reversal_Intraday_Information_from_Realized_Semivariance), methods and tables on pages 7, 27–34 and 43.

**Source evidence:** The sample covers 31 Chinese commodity futures during 2007–2018, with open-interest-based rolls. Daily 20-day momentum is conditioned on positive and negative semivariances computed from five-minute returns over five days, compared with trailing 250-day 80th percentiles. Both high means flat; both low preserves momentum; asymmetric extremes can reverse the adverse signal, while S2 also closes the same-direction signal. Positions are daily close-to-close, equal-weight with 40% per-asset volatility targeting. A one-day execution lag is examined. Table 6 reports S2 Sharpe ratios of 1.77 in 2008–2012 and 1.58 in 2013–2018 after a one-basis-point turnover charge. Rolling estimation is described as out of sample, but an untouched sample held aside before choosing the strategy was not demonstrated.

**dot assessment and build gate:** Personal: conditional research hypothesis. Intraday/Apex: no, intraday measurement does not mean intraday holding. Existing-data: a US adaptation may use minute OHLCV, but faithful Chinese-universe replication is unavailable and overnight/session completeness remains unverified. Do not translate the per-instrument 40% target into account risk.
The useful question is whether downside/upside variation improves an already-known trend family after realistic costs. Implementation requires complete correctly timestamped five-minute bars, a causal percentile window, minimum warmup, lagged volatility, roll handling and next-tradable-price fills. One basis point is not adequate proof for microcontracts or stressed markets. Relatedness to existing trend strategies may limit diversification. No exact repository ID match found; this is a new conditioning rule, not an entirely unrelated alpha family. Public manuscript access does not grant a license to its commercial or exchange data.

## 23. The Impact of Currency Carry Trade Activity on the Transmission of Monetary Policy
Boeck, Steshkova and Zörner. [SSRN 4371901](https://ssrn.com/abstract=4371901). [OeNB Working Paper 258, August 2024](https://www.oenb.at/dam/jcr:ba86da7f-b856-435c-9286-c7c3a2ec8907/wp-258.pdf), section 5, pages 29–31.

**Source evidence:** At the FOMC-day close, a positive interest-rate surprise combined with a negative S&P surprise selects long US dollars against an equal-weight currency basket. Otherwise the strategy holds high-forward-discount currencies against low-discount currencies, using upper/lower thirds. Positions persist until the next scheduled meeting, implemented with weekly forwards. For January 2004–June 2019 the all-currency strategy reports annual mean 4.007%, volatility 4.238% and Sharpe 0.945; the developed-market-only Sharpe is 0.514. Its mechanism separates monetary tightening from central-bank information shocks. The reviewed implementation does not establish bid/ask-adjusted returns or an untouched holdout. Bloomberg/Datastream inputs are needed.

**dot assessment and build gate:** Personal: conditional, lower priority than the commodity-curve leads. Intraday/Apex: no. Existing data: no verified forward-discount panel, correct announcement-window rate surprises or matching FX basket.
This is a testable conditional carry rule, but a 6E continuous series is not a substitute for a currency-forward cross-section. Require point-in-time announcement windows, documented surprise construction and availability, forward rolls, financing/spreads, actual trading timestamps and a frozen post-publication validation period. Risk remains concentrated in monetary surprises and carry unwind episodes, so the mechanism should not be called a crash-proof diversifier. No exact repository ID match found. A free central-bank paper is not a license to reproduce its licensed underlying data.

## Further source gates and exclusions
- [SSRN 2648136](https://ssrn.com/abstract=2648136), Turn-of-the-Month: Window Dressing Behavior: potentially relevant final-hour intraday short. Full source unavailable in authorized attempts; no exact rule, net evidence or holdout confirmed. Reserve, not promoted.
- [SSRN 7561158](https://ssrn.com/abstract=7561158), A Multi-Strategy Quantitative Portfolio: recent abstract claims validation and cost stress; no accessible full methods located. Reserve only.
- [SSRN 3575861](https://ssrn.com/abstract=3575861), Natural Gas Announcement Day Puzzle: source blocked; repository already contains a related EIA-event hypothesis. Do not assume distinctness or transplant incomplete rules.
- [SSRN 2682698](https://ssrn.com/abstract=2682698), commodity liquidity timing: existing source-gated family, no recovered primary full source.
- [SSRN 6077836](https://ssrn.com/abstract=6077836): full gold-fixing paper excludes trading costs and relies on overnight historical exposure. Reject as a strong new intraday candidate.
- [SSRN 1920401](https://ssrn.com/abstract=1920401): needs realized-versus-consensus macro surprises; not an OHLCV-only strategy.
- [SSRN 6074846](https://ssrn.com/abstract=6074846): previous source-fidelity stop, not fresh proof.
- [SSRN 7257240](https://ssrn.com/abstract=7257240): gold/silver cross-session candidate, full evidence and session coverage unverified; no promotion.

## Decision
Retain 21–23 as conditional hypotheses, with 21 the highest-value new source audit. They do not replace failed baselines with an unsupported claim of strength. Continue source research; no strategy code, tests, data purchases, live access or deployment performed.
