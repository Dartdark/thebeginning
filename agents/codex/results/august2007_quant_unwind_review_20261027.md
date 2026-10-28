# August 2007 quant unwind: REFERENCE / no current trading-plan placement

Summary: Khandani and Lo's September 2007 case study explains a plausible common-loss mechanism for apparently diversified funds. Its illustrative strategy is a daily long/short individual-stock reversal basket, with execution costs omitted. It supplies neither a verified modern futures edge nor an observable rule for identifying the end of a liquidation. Keep its lessons for portfolio stress review; no strategy addition is supported here.

Source: user-uploaded `august07.pdf`, *What Happened To The Quants In August 2007?*, Amir E. Khandani and Andrew W. Lo, September 20, 2007 revision, 58 PDF pages. References below use the paper's printed page numbers. SHA256: `990e58ccfe9e32ca9a29043e41a3e21c3287ff394d9bab721ecc48fc69815396`.

Evidence: [mechanism and feasibility sheet](../evidence/august2007_quant_unwind_20261027.md).
New return trials: **0**. No new market returns, configurations, filters, sizing rules, placebos, Monte Carlo or account benches were evaluated. Published historical figures below are source claims, not our replication. Completed Hunt v2 and stopped t6 are unchanged.

## Rule actually studied

Section 3, pp. 7–10, and Appendix A.1, pp. 49–50, define weights proportional to the negative of yesterday's return relative to the equal-weighted stock-universe return:

`w[i,t] = -(r[i,t-1] - mean(r[:,t-1])) / N`.

Buy relative losers, short relative winners, scale positions with the size of the deviation, and rebalance daily. Long and short dollar exposures offset. Dollar neutrality does **not** imply zero beta or absence of common factor, funding or liquidation risk; the authors make that distinction themselves (p. 8, footnote 2).

The source uses US common stocks, CRSP share codes 10/11, with prices above $5 and below $2,000. It studies the full universe and market-capitalization deciles. Its price history is January 3, 1995 through August 31, 2007, not 2018–26. For 2007 the authors use a December 2006 universe and Yahoo adjusted prices, acknowledging unmatched securities and missing dividends (p. 10, footnotes 5/6).

This is a stock-selection strategy. NQ, ES or seven futures markets cannot substitute for thousands of individual stock residual returns while preserving the tested mechanism. The paper's daily close-return formula is a research benchmark: a new implementation would have to freeze when signals become available and use a later executable order/fill, rather than assuming a completed close can both determine and fill an order at that close.

## What the published numbers show

These figures are transcribed from the paper; no raw return series was independently reconstructed.

| Published quantity | Source value | Interpretation |
|---|---:|---|
| All-stock average daily return, 1995 | +1.38% | Before execution costs and other implementation frictions |
| All-stock annualized Sharpe, 1995 | 53.87 | Gross illustrative stock basket; not an achievable modern account estimate |
| All-stock average daily return, 2007 through August | +0.13% | Much smaller gross effect than in 1995 |
| All-stock annualized Sharpe, same 2007 sample | 2.79 | Gross and based on the paper's return normalization |
| August 7 / 8 / 9, 2007 | -1.16% / -2.83% / -2.86% | Daily source strategy losses |
| August 7–9 cumulative loss | -6.85% | Paper's arithmetic aggregation, not geometric compounding |
| August 10 rebound | +5.92% | A later rebound does not finance losses or margin calls already incurred |
| Whole week of August 6 | -0.43% | The weekly aggregate hides the intervening losses |

Sources: Table 2 / pp. 10–15 and Table 3 / pp. 15–16. These are **not** trade t statistics, daily Newey-West statistics, deflated Sharpe results, cost-adjusted returns, placebo passes or plan-bench improvements.

The authors explicitly omit transaction costs, price impact, short-sale constraints and other implementation limitations (pp. 10 and 42). They chose a simple strategy to investigate a historical disturbance, not to document an executable retail strategy. The striking gross Sharpe must be read in that context. Calling the strategy a liquidity supplier does not establish that our orders can capture the spread: passive fills, adverse selection and marketable execution require separate evidence.

## Mechanism and limits of the explanation

The proposed sequence is: a large equity portfolio is unwound; related positions lose; other managers reduce exposure because of losses or financing/risk constraints; their similar trades amplify the dislocation; some prices reverse when that selling/buying pressure abates. A credit-market problem could therefore transmit to otherwise unrelated equity positions through a common owner or financing chain.

This is the authors' **tentative hypothesis from indirect evidence**, not an identified account-level causal event. Section 10, pp. 42–44, says they lack proprietary positions, prime-broker records, trading histories and leverage data. Forced versus voluntary initial selling cannot be conclusively distinguished. Neither the initial size nor a usable real-time timestamp for the end of the unwind is provided. The case therefore does not justify a new instruction to buy after an arbitrary number of down days or fade every large NQ move.

## Use for the existing book

The useful implication is to assess candidate losses jointly with the book during stress, not just average correlation. An author's low average correlation, including the earlier 6E package's claim, cannot establish survival during financing or liquidity stress. This paper does not establish that our 6E reconstruction or current book shares the specific 2007 exposures.

For a later separately scoped risk audit, relevant measurements would include common losing days, conditional P&L on the book's worst days, actual concurrent contract exposure, stressed execution costs, and whether any proposed offset arrives before an account boundary is crossed. Synchronized chronological account paths matter. A daily proxy or a rebound after a breach cannot establish funded-account protection. The paper does not validate a particular kill switch, stop, hedge or sizing change for our book.

## Data and existing-research check

The local `data/` filename inventory contains 161 files. No filenames identify CRSP, a stock universe/constituent history, delisting data or borrow data. The documented existing inputs are principally futures minute files and supplementary features. This inventory establishes that the required equity dataset was not identified locally; it is not proof about data the user may own elsewhere. No purchase or external data retrieval was attempted.

TIER_LIST already includes Avellaneda–Lee equity statistical arbitrage and failed futures adaptations of cross-sectional reversal, intraday index spreads and related stock-level effects. Those results are not tests of this exact stock basket, but changing it into another NQ/ES reversal proxy would not reproduce this paper. Do not relabel a previously rejected proxy as a new strategy.

Sources reconciled through the connected GitHub app: `codex/work` at `e41417eed57e63b8375ddab3827aeb1013d094fc`; its funded and personal README sources; and the latest fetched Claude-branch TIER_LIST (blob `2b37b76fe74189ef87b044e8f1aa51cdd755bd0d`) and FUNDED_PLAN (blob `7ce15d425784dec64a4a80b8eefc2c8f3bac43b6`). The Claude branch was read only. No stale roster or backtest dollar constant was used to manufacture a bench result.

## Explicit placement, including assuming a verified backtest

| Home | Current verdict | What verification would and would not change |
|---|---|---|
| Personal | **No earned place; possible equity research only** | An independently profitable modern equity basket could be considered as a separately financed sleeve, but would still need borrow/execution checks, feasible account sizing and paired BASE/ADD/REPLACE/EMPTY book comparisons. None has been measured. |
| 50K funded | **No place as written** | This is an individual-stock long/short basket, outside the futures-only plan. Its daily holding/execution protocol is not the adopted intraday futures protocol. Better historical statistics do not resolve that mismatch. |
| 150K funded | **No place as written** | Same instrument/protocol mismatch; more account size does not create eligibility. No payout benefit is inferred. |
| 50K evaluation | **No place as written** | Same mismatch; no valid joint futures account path, daily-limit or target-pass comparison exists for it. |
| 150K evaluation | **No place as written** | Same mismatch; no pass-rate gain is inferred from 50K or from the source paper. |

No account bench was run. These are eligibility/evidence verdicts, **not measured harm** to all five plans. There is no executable current candidate to add, replace or compare against an empty slot. Full modern metrics, long/short and by-year net results, placebos and account Monte Carlo are unavailable rather than zero.

## Verdict and follow-up

**Keep as risk research; do not adopt or backtest an invented futures port.** The literal equity strategy needs a point-in-time individual-stock dataset with corporate actions/delistings, executable prices and short-borrow/cost assumptions before a committed modern design could be tested. No source-code request is necessary to understand its simple weight formula, but the missing execution and dataset are material.

No promising-strategy queue entry was added: a gross historical diagnostic plus missing inputs does not establish a promising modern trading candidate. No root TODO, shared ranking, plan allocation, watcher, automation or live file was changed. No PowerLanguage draft is appropriate at this gate.

For Claude: review `agents/codex/results/august2007_quant_unwind_review_20261027.md`; reference/risk lesson, zero new return trials, no trading-plan addition.
