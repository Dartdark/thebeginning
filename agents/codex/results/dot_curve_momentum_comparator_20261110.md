# dot: additional curve-momentum comparator
Author: dot. 2026-11-10. Research only; no tests or strategy changes.

## Status
Paschke, Prokopczuk and Wese Simen, [Curve Momentum, JBF 2020](https://doi.org/10.1016/j.jbankfin.2019.105718). [Full accepted pre-proof inspected](https://centaur.reading.ac.uk/87795/1/1-s2.0-S0378426619302912-main.pdf). SSRN identity remains unverified, so this is an unnumbered published-literature comparator, not another SSRN slot.

## Source findings
The 22-commodity CRB sample spans January 1986–February 2015. Each month, rank the first two nearby return indices by trailing 12-month return; buy the winner and short the loser for one month. Equal-weight markets within seven sectors, then sectors. Roll at the end of the second month before last trading day; returns compare the same native contract across a roll. Gross annual return is 1.76%, volatility 1.38%, Sharpe 1.28. Modeled costs reduce Sharpe to .85–.93 and return to 1.17–1.29%. Monthly turnover per nearby is 125.62% including rolls versus 19.24% for rebalancing alone. The maturity-sensitive cost case gives negative energy and metals returns. Historical bid/ask data were unavailable. Removing the newest signal week remains positive. Sample splits and alternative horizons are robustness checks, not a frozen holdout. The naive always-long-second/short-first spread already earns gross 1.49%, Sharpe 1.03. See §§2–4 and Tables 11–12.

[Curve Momentum in China, JFM 2026](https://doi.org/10.1002/fut.70093) supplies abstract-level changed-market corroboration, not a verified numeric U.S. replication; full source was not recovered.

## Independent assessment and gates
- **Personal:** conditional monthly/overnight curve-relative-value research. **Intraday:** no. **Existing data:** no faithful replication from one continuous ticker.
- This ranks maturities within a commodity, unlike entry 5’s cross-commodity momentum with maturity selection. It relates to BM but is not identical. No exact duplicate appeared in TIER_LIST, MINED_INDEX or the 50-entry index.
- A small CL/GC subset is not supported by the diversified result. The source’s most relevant sector net results are negative; a high portfolio Sharpe with low spread volatility does not guarantee feasible integer lots, margin or survival.
- Both-leg collateral/notional sizing, raw third-contract prices at rolls, expiry mapping, delivery avoidance and historical tick/multiplier units are required. The printed meats cost of .001% warrants a unit reconciliation before trusting implementation economics; it is a flag, not an established error.
- Main question for any later authorized build: does dynamic maturity ranking add enough to a naive spread after actual costs, margin and a frozen post-February-2015 period? No such test was performed here.
