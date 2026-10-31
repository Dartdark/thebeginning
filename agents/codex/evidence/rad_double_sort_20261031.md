# Monthly commodity momentum/carry double-sort: NEEDS DATA / ACCOUNTING

Summary: Specific four-long/four-short monthly commodity risk-premium strategy, not a scheduled forced flow.
The uploaded thesis claims 20.22% annual excess return before costs over February 1979–October 2011.
Our owned CL/GC outrights lack the second-contract panel and cross-section needed for either sort.
Return/NAV, information clocks and integer contracts also remain unresolved; no return trial admitted.

Source: Hossein Rad, December 2012 EDHEC MSc thesis, SSRN 2614241;
[archived owned upload](../inputs/rad_double_sort_20261031/ssrn-2614241.pdf),
[review](../results/rad_double_sort_review_20261031.md),
[access/acquisition receipts](../inputs/rad_double_sort_20261031/source_access.json).
This is an evidence/feasibility sheet, not a preregistration. New return definitions/reservations:0.

## 1. Who trades, and what causes the trade?

Proposed compensation for commodity inventory/convenience-yield and hedging risk, combined with price persistence.
These are risk-premium hypotheses from the thesis/literature, not identified compulsory orders with known dates,
sizes or guaranteed payment. Broad cross-sectional momentum/carry merits conditional personal research; no current
ES/NQ flow is established. Crowding and cheaper absorption can eliminate net edge.

## 2. Direction, size and timing known before entry

Source: each month rank prior-month mean daily log returns; retain eight winners/eight losers, then select four
highest mean `ln(front/second)` among winners for longs and four lowest among losers for shorts. Hold one month;
equal weights separately within each side initially, then drift. Long and short books each have one collateral
unit of notional: two units gross. Source weights are fractional, not an integer-contract specification.

Needed clock chain: each exchange's dated close/settlement event_time -> original available_at including delay
and revisions -> cross-market decision_time after the last required input -> first executable order/fill -> dated
rolls and exit. Paper supplies no reproducible receipt/decision/fill clocks, holiday synchronization or same-close
execution policy. These fields remain unknown, not assumed contemporaneous. Daily-close overlay changes take effect
next day in the source; there is no proven intraday protective fill.

## 3. Does the mechanism reach the traded instrument?

The source trades commodity futures directly, nearest maturity rolled at month-end before its maturity month.
It does not trade ES/NQ or an adjacent-maturity spread. The second contract is a **signal input**, although a dated
roll later changes the traded contract. No claim that using CL and GC alone, adding indices or intraday liquidation
would preserve the same economic definition. Monthly overnight holdings fail all four Apex homes as written.

## 4. New information and data feasibility

| Input | Exact need | What was inspected | Status |
|---|---|---|---|
| Broad commodity universe | Point-in-time eligibility, currency/venue, listing/delisting; source 37 instruments, initially 22/peak 35 | Thesis PDF 20–25 | Source definition known; owned panel unavailable |
| Momentum | Dated traded-contract prices, vendor roll convention, close time and availability | All 141 CSV headers under data/; CL/GC yearly headers | Outright OHLCV exists, but no admitted contract/roll ledger |
| Carry | Simultaneous first/second maturity closes, IDs, expiry and receipt clocks | Owned schema and bounded free-provider check | Missing; a continuous outright is not a substitute |
| Execution/risk | Executable post-signal prices, ticks, multipliers, notice/expiry dates, margins, FX and fees | No author raw data or execution ledger supplied | Unknown; no assumed fills |
| Source accounting | Self-financing quantity/cash/variation-margin/NAV specification | Eq 1–4, Table 1, Figure 3 | Source sums log returns; compounded wealth not reconciled |

CL and GC filenames span 2017–2026; this is not proof of complete usable sessions. Both have only
date/time/OHLCV fields. Local schema audit reads headers, never prices. The no-account front-month sample request
failed at the network tunnel 403; its advertised schema already lacks the deferred contract. Other inspected free
routes were short samples, old samples, an unavailable archive, or account/paid-history products. No bypass,
signup, credential inspection or purchase. [Detailed receipt](../inputs/rad_double_sort_20261031/source_access.json).
These observations do not prove that no suitable free data exist anywhere. Stop the bounded acquisition here.

## 5. Costs and actual intraday gaps

Source excludes all transaction costs and collateral interest from its excess-return series. No defensible native
gross-to-net bridge can be built without dated contracts, turnover and fills. Required costs include each entry,
exit, roll and stop-driven redistribution, native fees/spread/slippage, FX and execution delay; no fabricated flat
fee rescues missing inputs. Breakeven extra cost and stress remain uncomputed. Existing account occupancy is not a
signal-selection filter. No intraday gap or diversification benefit is measured for the current personal book.

## 6. Power before a return test

There are 60 calendar formation months in 2018–22, not 60 verified eligible baskets. No complete panel means no valid
event census, exclusions, warm-up, effective sample or variance estimate. Eight positions are correlated holdings,
not eight independent monthly experiments. If a future complete census justified IID effective n=60, the generic
t>=2 mean hurdle would be `2*SD/sqrt(60)` before adding costs and multiplicity; that formula is not a passed power
gate. Previously seen 2023+ remains historical validation, not a fresh holdout. No design outcomes were opened.

## 7. Already tested and falsifiers

TIER_LIST's Gorton et al. commodity storage/momentum reference already flags the monthly commodity family; this is
a more explicit source specification, not discovery of a new asset class. Weekly basis reversal SSRN 5250499 is a
different relative-return rule sharing the paired-data prerequisite and remains parked. Preserve the earlier
CL/GC commodity hedging-pressure rejection; do not relabel it as momentum/carry or replace carry with COT.

A future admitted study must freeze genuine incremental controls, including same-universe/window momentum-only
and carry-only books, within the existing definition budget. Failure to beat costs, lack of incremental value,
dependence on missing-return reallocation or inability to reconstruct a cash ledger would refute advancement.
No control or gross screen was executed or reserved here.

## 8. Failure and diversification

| Question | Prediction before results | Needed evidence |
|---|---|---|
| Mechanism failure | Crowded momentum/carry or changed inventories can erase premia | Independent after-cost modern outcomes |
| Liquidity role | Unknown until an executable order policy is frozen | Post-decision quotes/fills and roll liquidity |
| Clustered losses | Reversals, commodity shocks, gaps and concentrated reallocation can hurt both books | Full paths, concentration, daily margin and stress marks |
| Shared portfolio losses | Macro/trend exposures may overlap current futures legs; unmeasured | Joint chronological losses, not asserted diversification |
| Offset before breach | No demonstrated timing or risk offset | Native integer account replay after earlier gates pass |

The source's next-day cutoff is not a guaranteed maximum loss. Undefined logs at non-positive prices require an
ex ante valid policy before any modern replication; silently dropping those observations is forbidden. Missing
selected returns remain unknown, not redistributed into known winners as a replacement for real executable data.
No new stop, time exit, data-failure policy or actual size was invented here.

## Decision and next gate

**NEEDS DATA / ACCOUNTING.** Park one specific monthly momentum/carry research queue item for the personal home.
Smallest next step **only when genuinely new inputs arrive**: reconcile one formation/roll month using identified
front/second contracts and an explicit self-financing cash/quantity ledger; then census 2018–22 without returns.
No recurring unchanged acquisition loop. Evidence, clocks, costs, power, budget lease/reservation and a committed
bounded exact-code preregistration must precede returns. No admission PASS or independent economic verification.
