# dot: source upgrades for existing curve and Treasury research
Author: dot. 2026-11-10. No strategy tests, source-code execution or deployment. These are not new inventory slots.

## D06: Short-Term Basis Reversal
[SSRN 5250499](https://ssrn.com/abstract=5250499) is already DATA_NEEDED D06. The [existing prototype checkpoint](weekly_basis_reversal_build_20261029.md) is synthetic-only, not an admitted economic test.

Reviewed the [61-page May 11, 2025 manuscript text](https://www.scribd.com/document/900311637/Short-Term-Basis-Reversal-2025), a third-party mirror. May 12, 2026's 68-page revision remains inaccessible, so version parity is unverified.

Source specification: 22 Datastream commodities, 1980–2022, contracts at least a month from expiration. Weekly b = front-contract percentage return minus second-contract return. Highest four b: long second/short first; lowest four reverse, equal-weight groups. Table 2 gross spread return 7.62%, Sharpe 1.42, t=8.83; post-2000 4.90%, Sharpe .96. Table A.5 delays Thursday signals to Friday-close formation: 3.87%, Sharpe .75, t=4.74. No complete trading-cost model or untouched holdout identified. The time-series variant is a separate implementation.

### Independent replication correction
The [June 10 Quantitativo article](https://www.quantitativo.com/p/short-term-basis-reversal) still advertises strong net results. Its author's [June 24 correction](https://www.quantitativo.com/p/short-term-basis-reversal/comment/128797426) says a backtest bug was found and corrected returns do not survive 10bp/week costs. [July discussion](https://www.quantitativo.com/p/short-term-basis-reversal/comment/136696502) identifies contract-switch artifacts and notes that headline reproduction would require leverage and commodity selection. Corrected code/results were not publicly verified here.

**Assessment:** do not use the unrevised headline as independent net validation. This does not prove the academic paper has the same bug. D06's existing same-contract endpoint gate is essential. Weekly reversal differs from trailing-year Basis Momentum and three-price Relative Basis, but shared inputs do not guarantee portfolio diversification. Continuous front-contract exports cannot reconstruct two simultaneous maturities. Reconcile actual changing-contract weeks, eligibility/FND, executable delayed fills, integer quantities, two-leg costs and collateral before any future trial. Personal weekly only; no intraday claim.

## Treasury cointegration comparator, Dare 2017
[Complete primary paper](https://ux-tauri.unisg.ch/RePEc/usg/econwp/EWP-1716.pdf), printed pp.6–8, 21–29. SSRN identity not verified; 3025542 is a different theoretical paper.

2010–2015 one-minute 2/5/10/30-year futures. Prior-month midquotes estimate cointegration spread and volatility; fade beyond ±2 standard deviations, exit inside ±1 or after the following 100 daytime trading hours. Positions can remain open for weeks. Bid/ask costs are included, but not a full executable fee/slippage/capacity ledger. Fully funded annual excess returns are approximately 6%; approximately 1,500% margin returns use a different denominator. No untouched modern holdout established.

**Assessment:** the word intraday describes sampling, not flat-overnight holdings. Do not use margin-scaled figures as account returns. Formation clocks differ across sections, exact estimator/normalization and integer-contract mapping need resolution, and historical adjusted/OI-based rolls require point-in-time reconstruction. Owned ZN does not establish a synchronized ZT/ZF/ZN/ZB quote/OI panel. Existing failed equity-index pair trades are not exact replications, but this remains an unnumbered, data-gated personal comparator.

## Old Treasury tick-reversal comparator
Cusatis, Kulkarni and Thomas (2009), [full primary paper](https://musabe.org/bfr20092020/40-260-1-PB.pdf), pp.36–48. SSRN identity unverified. September 2000–December 2004, 1,077 days of ten-year futures price-change ticks. Fade first new highs/lows within short daytime periods, ±1/±2-tick brackets and period-end exit. Prior-30-day tick autocorrelation filters are compared. Gross favorable two-tick filtered profits are around .61–.64 ticks per trade, versus a stated .20-tick round-trip cost.

**Assessment:** genuinely same-day in the source, but old transaction-price execution is not bid/ask or queue evidence. Multiple filters, no untouched holdout, ambiguous overlapping high/low trades and barrier sequencing preclude promotion. Existing ZN bar-reversion failures remain unchanged. Minute OHLC cannot reproduce the tick path. Historical context only.
