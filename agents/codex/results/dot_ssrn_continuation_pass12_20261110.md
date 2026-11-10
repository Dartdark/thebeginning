# dot: SSRN continuation, pass 12
Author: dot. 2026-11-10. Branch: codex/work. Source research only.

## 51. Good volatility, bad volatility and the cross section of commodity returns
Kiss and Ferreira Batista Martins. [SSRN 5390453](https://ssrn.com/abstract=5390453). [Full published 2025 paper](https://www.diva-portal.org/smash/get/diva2%3A2013183/FULLTEXT01.pdf), equations 1–3, portfolio tables and Appendix A.1. [DOI](https://doi.org/10.1016/j.frl.2025.108656).

**Source findings:** Monthly RSJ equals the difference between sums of squared positive and negative daily excess returns, divided by their sum. Rank the completed month’s values; long the lowest tercile and short the highest, equal-weight within each, hold one month. This is the profitable reverse of the reported negative high-minus-low factor. Thirty-six commodities span January 1990–July 2024. Favorable-direction gross annual mean is 6.29%, volatility 14.83%, Sharpe .42, t=2.59. Five-basis-point turnover costs are reported as 1.63% annually. The 2009–24 subsample is stronger; excluding agriculture leaves t=1.16. Daily contract switching and vendor mapping are incompletely specified. The paper calls subsequent-month sorting OOS, without a separate untouched test period. Table dates end June while text says July; body cumulative return 484% differs from publisher-highlight 494%. Authors cannot share underlying data.

**Classification:** Personal monthly/overnight: conditional. Intraday/Apex: no. Existing-data testability: not verified.

## Independent assessment
- Simple enough to specify, but not a high-confidence standalone edge. Arithmetic gross-minus-modeled-cost mean is 4.66% annually, not a reproduced net ledger. Return denominator is research collateral accounting, not broker-margin return.
- It is distinct from D09’s 12-month sample skewness, 22 markets and four names per tail, but belongs to the same asymmetry family. The paper’s skewness control uses one-month realized skewness, so its spanning result does not prove incremental value versus actual D09.
- It also differs from entry 22’s five-minute semivariance filter on Chinese time-series momentum. Sharing an input concept does not imply identical rules, nor independent portfolio diversification.
- Broad agriculture/international exposure matters. A CL/GC-only substitute would be a different strategy with no supporting result here.
- Freeze zero-variance/missing-data handling, formation availability, same-contract returns, contract eligibility and actual roll ledger before any future test. A nominal two-month-to-one-month contract return does not resolve nonmonthly expiries or delivery deadlines.
- Uniform turnover costs do not establish legged fills, financing, collateral, stressed spreads, margin or integer-lot survival. No live or account-specific result is claimed.

## Repository and data gate
[Existing D09 review](ssrn_3507947_review_20261030.md) and [build record](commodity_skew_build_20261030.md) confirm the different implementation. Current DATA_NEEDED still marks the commodity panel unadmitted; an 84-series acquisition manifest and partial D09 coverage do not establish a native 36-market RSJ dataset. Raw data were not newly admitted or tested here. No exact 5390453 entry was found in the inspected index/TIER_LIST, a scoped rather than exhaustive novelty claim.

Next useful preparation is a contract-map and coverage audit alongside D09, not a return test or a reduced-universe promotion. No tests, code changes, purchases, accounts, schedules or live actions occurred.
