# SniperAlgo: execution utility / no standalone plan slot

Summary: This class carries out an externally supplied order; it supplies no alpha signal or complete trading strategy. Fourteen disconnected synthetic scenario groups reproduced its callback behavior, including three safety-gap examples. No market backtest, execution saving or account improvement is established. All five homes receive no standalone addition; an execution-helper role remains conditional on separate integration and fill evidence.

Evidence: [feasibility gate](../evidence/sniper_execution_20261027.md).
Plan: [frozen mechanics review](../plans/sniper_execution_20261027.md), local preregistration commit `4b01fec`.
Script: [`analysis/codex_sniper_mechanics_review.py`](../../../analysis/codex_sniper_mechanics_review.py), executed local code commit `5709c27a7521b655b26baa993f6611d183627f76`.
Outputs: [`summary.json`](../../../analysis/outputs/codex_sniper_mechanics_20261027/summary.json), [`cases.json`](../../../analysis/outputs/codex_sniper_mechanics_20261027/cases.json).
New economic trials: **0**. One unchanged execution-code configuration, fourteen predeclared mechanics scenarios; no configuration search or new return observations. Stopped t6 and completed Hunt v2 remain unchanged.

## What the code does

The caller already chooses symbol, LONG/SHORT, OPEN/CLOSE offset, price cap/floor and total quantity. For LONG, it waits until the best ask is at or below the supplied price. For SHORT, it waits until the best bid is at or above it. It submits a limit order at the **supplied price**, with quantity equal to the smaller of remaining target and displayed best-level volume. This is a marketable limit when the observed quote is still available, not necessarily a resting passive order.

The quote is a decision input, not a guaranteed fill. A buy with cap 100 and observed ask 99.75 is submitted with limit 100; the actual fill can differ as the book changes but should respect the limit in normal exchange handling. Displayed depth does not reserve liquidity. Neither spread capture nor an execution-price improvement follows from this code alone.

While `vt_orderid` is set, every subsequent tick calls `cancel_all()` and returns. A terminal order callback clears the ID. A trade callback checks whether the aggregate filled quantity has reached the goal and finishes when it has. The inherited template updates `self.traded` **before** invoking `on_trade`, so that field is not an uninitialized accounting defect. A caller can use CLOSE offset to execute an exit order; the class does not decide when a stop, target or time exit should trigger.

There is no rule for choosing direction, estimating fair value, setting the limit or generating the parent-order schedule. It is therefore not a complete return-generating hypothesis. The label “Sniper” supplies none of those missing rules.

## Source and method

The supplied implementation corresponds to public [vnpy/vnpy_algotrading SniperAlgo](https://github.com/vnpy/vnpy_algotrading/blob/bee959dc464749f7cce66e766249ccdbb2d4869a/vnpy_algotrading/algos/sniper_algo.py), pinned to commit `bee959dc464749f7cce66e766249ccdbb2d4869a`. Public MIT-licensed snapshots, provenance and license are retained [here](../inputs/sniper_review_20261027/README.md).

The harness executes unchanged SniperAlgo and AlgoTemplate class bodies and the upstream engine's send/cancel/order/trade dispatch methods. Minimal in-memory quote/order/trade objects and a disconnected fake gateway replace transport dependencies. Only integer synthetic quantities are used; the replacement volume-rounding helper is deliberately restricted to that domain. Neither vn.py package is installed in this workspace. This is **not** a full installed-vn.py, gateway, broker or exchange integration test.

The fake gateway records requests and accepts explicitly injected events. It does not automatically fill an order because a quote crosses a limit. There is no market-data replay, order-book simulator, latency estimator, realized cost model or P&L calculation. Reproducing an unsafe behavior is a successful diagnostic assertion, **not** a safety pass.

## Mechanics findings

All fourteen predeclared scenario groups completed. Their traces retain requested limits/quantities, IDs, cancellations, status and cumulative trade callbacks.

| Finding | Measured synthetic behavior | Interpretation |
|---|---|---|
| Direction, price condition and child size | Favorable quotes trigger a limit; unfavorable buy quote does not; OPEN/CLOSE forwarded | Basic intended interface works in the harness |
| Ordered partial-fill sequence | Goal five, fill two, acknowledge cancellation, next child three | Inherited accounting handles the ordinary sequence |
| Completion | Reaching the goal finishes and suppresses later tick orders | Template status gating works |
| Zero displayed depth | Requested zero is rejected by upstream engine before gateway send | Do not falsely claim a zero-quantity order reaches the broker |
| Cancellation policy | Next tick cancels even with an improved quote; repeated ticks repeat requests | This is its fixed policy, not demonstrated fill or fee optimization |
| Pending acknowledgement | Retained ID prevents resubmission, but no active-order entry exists yet to cancel | Behavior depends on timely order events |
| **Invalid quote** | Zero ask plus positive size triggers a buy request at limit 100 | Missing quote-validity guard; it does not mean buying at price zero |
| **Delayed old terminal event** | Terminal message for an earlier order clears a newer ID; next tick creates another child, leaving two one-unit children against target one | Missing ID-specific terminal handling in this stress sequence |
| **Delayed trade report** | Cancellation reports two filled but the trade callback is delayed; a new child for five is sent; later callbacks total seven against goal five | Known cumulative order fills and pending trades need reconciliation before replacement |
| Timer / feed stall | Timer events provide no deadline or flatten action | An external execution-window/risk controller is required |

The three highlighted sequences are constructed examples, not observed historical incidents or estimated failure probabilities. They are routed through the upstream mapping for **older orders belonging to the same algo**; this is not a claim that unrelated algorithms' messages are broadcast to it. Real gateway ordering/deduplication guarantees might prevent some sequences and need specific integration verification. No source modification or proposed fix was installed.

## Why a profit backtest was not run

The existing files include minute OHLCV and aggregated order-flow features. They do not establish the complete tick quote/order/acknowledgement/cancellation/trade sequence needed to model this execution policy. A bar low touching a buy limit cannot establish a fill or queue position. A completed ask quote cannot be treated as still available after arbitrary latency.

More fundamentally, there is no source-defined closed-trade schedule to backtest. Adding random entries, an invented fair-value price, or exits chosen by us would test a different strategy. Missing t, daily Newey-West, DSR, Sharpe, Sortino, PF, Calmar, Ulcer, long/short/year, placebos and Monte Carlo results are **unavailable, not zero**. Native costs cannot be applied to a fictitious fill ledger to create meaningful performance.

The current fetched TIER_LIST already reports that simple limit-for-market substitutions lost to the original entries in the earlier repo study. That is relevant caution about missed winners and adverse selection, **not** empirical rejection of this exact Sniper policy. It supplies no reason to repeat that family under a new name.

Sources reconciled through the connected app: `codex/work` at `475ee845519b6d875726625b2d95bd37edf7e0bb`; latest fetched Claude-branch TIER_LIST blob `2b37b76fe74189ef87b044e8f1aa51cdd755bd0d` and FUNDED_PLAN blob `7ce15d425784dec64a4a80b8eefc2c8f3bac43b6`. Claude's branch was read only. No stale plan constants were used to invent a result.

## Placement for all five homes

| Home | Verdict | Limit / possible future role |
|---|---|---|
| Personal | **No standalone slot** | Could be researched as execution for a separately specified existing strategy; no measured net return/DD benefit |
| 50K funded | **No standalone slot; no execution change authorized** | Needs valid parent signals, protective exits, account controls and native fill evidence; no payout benefit measured |
| 150K funded | **No standalone slot; no execution change authorized** | Same requirements; account size cannot supply missing alpha, and no result is inferred from 50K |
| 50K evaluation | **No standalone slot; no execution change authorized** | No joint path/DLL/target-pass comparison; unfinished execution must be handled by an external controller |
| 150K evaluation | **No standalone slot; no execution change authorized** | No measured pass-rate benefit or inference from the 50K account |

Even assuming its order mechanics were fully verified, a standalone slot would still not follow: it needs a strategy to tell it **what and when to trade**. Current plans use MultiCharts; this vn.py class is not a drop-in signal for that platform. No ADD/REPLACE/EMPTY account bench was run because neither an alpha candidate nor a valid execution-replay ledger exists. That is lack of qualification, not measured harm to every account.

## Verdict

**Move on as a standalone strategy. Retain only as an execution-code reference.** Any later execution study should freeze the existing parent strategy, same decision opportunities and risk rules; compare original execution, Sniper execution and no-fill/opportunity-cost outcomes with complete quote/order replay, realistic costs and paired account histories. These prerequisites are not a new request for purchases or live configuration changes.

No promising-strategy queue entry, shared ranking/plan edit, live/VPS/broker/API action, PowerLanguage draft or automation change was made. No trading benefit or phone delivery is claimed.

For Claude: review `agents/codex/results/sniper_execution_review_20261027.md`; execution helper, fourteen synthetic scenario groups, three constructed safety gaps, zero economic trials, no standalone plan placement.
