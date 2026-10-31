# QuantJourney 55-day futures Donchian: NEEDS DATA / ACCOUNTING

Summary: The supplied daily breakout is a personal-only research baseline, not an Apex strategy as written.
The author's headline Sharpe is 0.30; its trade report has unresolved multiplier/reconciliation errors.
No independent return trial is eligible without an executable roll chain and consistent ledger/accounting.
Retain as a low-priority blocked reference, not a new proven edge or a replacement for the current portfolio.

Source: [uploaded code](../inputs/qj_donchian_20261030/uploaded.py), Apache-2.0 header retained;
[public packet](https://backtester.quantjourney.cloud/strategies/example-orders-20-futures-donchian-contracts),
[selected published facts](../inputs/qj_donchian_20261030/published_facts.json), inspected2026-10-30.
Own return trials: **0**. Source/helper arithmetic checks and timestamp inventories do not estimate alpha.

## 1. Who trades, and what causes the trade?

This is trend following, not a measured forced order flow. It hypothesizes slow repricing/position adjustment after
a 55-session extreme. No participant mandate, flow estimate or demonstrated causal mechanism accompanies the code.
The participant story is therefore a hypothesis. Broader commodity/equity exposure can diversify, but does not prove
this specific definition adds to our book. The same broad time-series-momentum family was already reviewed.

## 2. Direction, size and information clock

At today's completed daily bar, compare raw close to prior55 rows' high/low extrema, excluding today.
ATR is the simple20-row mean of true ranges including today's bar. The current adjusted-close series supplies prior
closes for ATR. Public engine v0.10.0 documents next-bar execution; packet says open. Do not use today's close
as both signal and fill. Pending active order skips that instrument. Remaining positions are resized daily.
Provider daily-session timestamps, adjusted/raw equality, actual receipt and dated-contract eligibility are unresolved.

## 3. Traded contract or direct hedge

Declared MES/MNQ/CL/GC contracts are directly relevant to our markets. The Yahoo continuous labels are not contracts
that can be held through expiry. CL/GC are the full-size contracts; do not silently substitute MCL/MGC or fractional
contracts. Equity exposure overlaps current NQ/ES strategies; commodity trend could be different, unmeasured here.

## 4. Input feasibility

| Input | What is available | Unresolved requirement |
|---|---|---|
| Original rule | Complete uploaded class and sizing/ATR helpers | Hosted engine has private reporting; original OHLC/spec payload missing |
| Public engine | Archived v0.10.0 core/contract registry/data mixin | Exact hosted build, payload and source data hash not reproduced |
| Owned four-market minutes | ES/NQ/CL/GC2018–22, date/time/OHLC/volume; timestamps inventoried | No dated contract IDs, adjustment factors, executable roll schedule or roll cashflows |
|2017 NQ daytime | Exists on Claude7a42ea,2017-05-01→12-29; remote receipt retained | Do not mistake absence in stale main/codex checkout for absence from the repository; full overnight warm-up separate |
| Source metrics | Public text/JSON plus screenshot | Trade NAV/lot accounting, integer size, costs and roll treatment need reconciliation |

Public SDK `source=yfinance` still calls authenticated QuantJourney preparation. We did not execute its credential
helper, inspect credential stores or contact its API. Synthetic/sample data would not reproduce the source result.
Owned unadjusted continuous prices cannot measure multiweek cash P&L across splices; dropping a roll bar is insufficient.
New source availability is not a substitute for a correct contract ledger.

## 5. Costs and occupied hours

Author uses1bp adverse fill price plus$2.50/contract/side(minimum$2.50/order). This is a source cost model, not our native
broker fee schedule. No tick rounding, current buying-power check, dated rolls or variation-margin cash accounting
is provided in the example. Full-notional cash and reference-margin sizing are different models from futures collateral.
There is no stop:0.5%NAV per ATR sizes volatility, not maximum trade loss. This holds across nights and days, so it
does not fill an empty intraday window; it is structurally incompatible with the four Apex homes as written.

## 6. Power before a return test

Author reports978fill events but852matched FIFO lots, including daily resizing; neither count is978independent
directional bets. Reported average lot duration is about101days, so overlapping exposures and common factors reduce
effective sample size. No defensible net-trade SD/power threshold can be derived from the unreconciled lot P&L.
Power gate remains unresolved until contract-weighted daily and lot cashflows reconcile. No trial is spent on
manufactured carry returns or zero-filling missing sessions.

## 7. Prior tests and falsifiers

TIER_LIST: six-market weekly volatility-targeted time-series momentum already showed weak standalone returns;
the Turtle book review identifies multiweek trend rules as outside Apex. Public-repositories review retained Donchian
only as a baseline. None is an exact test of this55-day rule; retain family selection history rather than claim novelty.
Falsifiers: insufficient net edge after executable roll/costs; zero integer allocations at intended capital;
no improvement in personal equal-risk return/DD; contract-aware reconciliation cannot reproduce claimed totals.

## 8. Failure and diversification

| Question | Prediction before returns | Evidence needed |
|---|---|---|
| Mechanism failure | Choppy trends/rapid reversals; no persistent repricing | Frozen subsequent design, placebo and recent validation |
| Liquidity role | Daily market delta takes liquidity, including both legs of reversals | Native quotes/fills/ticks and trade quantities |
| Clustered losses | Cross-asset deleveraging, gaps, changing volatility and margin | Dated contract marked paths; no ATR stop assumed |
| Shared losses | NQ/ES trend shares equities; CL/GC may diversify or lose together | Current19-piece synchronized marked series |
| Offset before breach | No guaranteed offset; overnight positions incompatible with Apex | Personal cash/margin stress, no cross-account workaround |

## Decision and next gate

**NEEDS DATA / ACCOUNTING**. Source review,17synthetic/arithmetic checks and timestamp inventory can finish now;
the cheap economic screen and current-book benchmarks are blocked. No strategy preregistration or new return trial
is admitted. Smallest useful next step: reconcile a contract-weighted closed lot for each market and the whole daily
NAV against fills/fees/open positions, then obtain a dated-contract roll ledger. If those pass, preregister one
personal-only rule at real capital; do not silently invent intraday exits, alter caps or replace full-size instruments.
