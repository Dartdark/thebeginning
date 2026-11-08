# Frozen ES adaptation of SSRN7323419

The user asks to use owned ES data. This expressly supersedes the earlier source-only no-substitution gate for
this labeled adaptation. Evidence: `agents/codex/evidence/delgado_es_20261108.md`. Commit before returns.
Independent review pending. No strategy search, original SPY replication or plan/live change.

## Three definitions, one selectable candidate

1. BASE:14normal-session mean absolute same-clock open movement; symmetric1.0noise multiplier; prior14
   daily return SD; size at entry from min(4,.02/vol)*day-startNAV; wholeESlots toward zero.
2. SHADOW: candidate below but no performance overlay; mechanical external state for candidate, not selectable.
3. CANDIDATE: long multiplier1.3, short1.6, short size.75; cumulative relative-volume clipped.5–1.5versus
   prior14normal-session same-clock volume; size*.7if band rather than VWAP binds the side's exit; otherwise1.
   Previous30completed known SHADOW daily simple returns summed: positive*.9, otherwise*1.1; first30neutral.
   A missing shadow return resets the30known-calendar-day warmup; never insert zero for missing performance.

All versions start flat at$100,000NAV on2018-01-02; native ES$50point,.25tick. Reinvest known net profit
between days; risk/sizing uses day-start NAV and available entry-open price. Final marked exposure capped4x
after every multiplier; deduct entry commission reserve from sizing affordability; position quantity frozen until
exit/reversal. No intratrade rebalance, stop search or other overlays. No broker margin history supplied: the4x
cap is a research notional guard, not broker-margin certification. Negative NAV stops the path.

## Causal implementation choices shared by every version

Use `scratch_data/ge.pkl` via existingGrid24representation; hash cache and raw ES files. RTHopen08:31CTbar
open; minute typical-price total-volume VWAP from08:31through decision. Mean noise/volume uses exactly14
previous **normal**cash sessions, rejecting a missing same-clock feature; prior cash close may come from an
early session. Vol uses14previous actual adjacent cash-session close returns, including early sessions; never
bridge a wholly absent day. No ETF dividends on ES. Continuous ES roll-anchor/volume effects remain limitations.

At09:00,09:30,…14:30CT, long iff close>max(upper,VWAP), short iff close<min(lower,VWAP). Existing
long exits on close<=max(upper,VWAP), short on close>=min(lower,VWAP); an opposite valid entry reverses
with two charged legs. Stops are checkpoint market exits, not intraminute touched stops or ratchets. Early
sessions stop entries before their final checkpoint. EODdecision14:59CTnormal/11:59early; next minute's
open (close-stamped15:00/12:00bar) executes. This avoids the unavailable source same-close liquidation.

Missing current minutes: never fill/forward-fill/back-fill a price. Once cumulative VWAP becomes incomplete,
disable new entries for the remainder of that session. If held, propose liquidation and use the next observed
open; retain an unknown-path flag and unresolved MTM for the gap. A day with an unknown held interval is
excluded from complete-day statistics and separately retained; its observed closed-trade P&L is descriptive,
not asserted complete-day P&L. A wholly absent normal day is NaN, not cash/no trade; all subsequent
history/vol/performance windows require their stated complete inputs. No selecting away future bad days.
If a scheduled next-minute fill is missing, defer to the first subsequent observed open, flag that path and
prevent fresh entry that day. Never use a future open to decide signal side. Terminal unresolved positions halt.

Costs: commission$2.50/ES/side plus adverse.25point market slippage/side. Reserve full RTcommission at
entry; gross-minus-execution-slippage-minus-commission must equal closed net and sum to observed daily net.
Extra-tick stress uses the same filled quantities; it is not a re-compounded alternative candidate.
No MES before its2019launch, no fractional native contracts, no risk-free/collateral income or borrowed SPY costs.

## Design decision and earned stages

Compute2018–22only first, all eligible signals; zero-trade **known**days stay in daily statistics. Count every
definition including shadow. Report each selectable stream whole/long/short/year at actual ES size and per-lot
reference, using `metrics.perf`, daily/trade t and `deflated_sharpe` at `len(TRIALS.csv)+3+80` as a disclosed
conservative lower-bound combined search count (author/local overlap may overcount; no reduced count used).
Use return Sharpe alongside dollar-P&L Sharpe because capital compounds. Drawdown includes initialNAVpeak.

The full candidate must pass: >=300complete closed trades, >=95%known design calendar days, positive
net, positive fixed-fill extra-tick stress, positive at least4of5years, daily **return**t>=2 and trade-net t>=2;
its net/maximum daily drawdown must exceed BASE by at least10%, while retaining at least70%of BASEnet
if BASEnet>0. Candidate cannot be replaced by the shadow or baseline if it fails. No rounding t=1.99to2.
Any missing native hold path also blocks **account promotion**, even if this descriptive design screen passes.

If design fails, stop: no new2023+return calculation, rescue variant, placebo or account stage. Report the
completed design negative and prior historical recent results separately. If design passes, replay frozen2023+
once without retuning, preserving through-timeNAV/shadow state; provide chronological whole/side/year tables,
1000seed7323419daily-block bootstrap intervals(block20),1000matched-duration random-side controls and
BASEmatched comparison. Random-side controls condition on observed exit durations, not proof of endogenous
full-policy causality. Promotion additionally needs repository multiplicity/independent-review/forward gates.

Potential overlap: ES MOC/relative-strength and other intraday trend sleeves; prespecified replacement is
PAPERTREND for personal and VB for prop. If statistical, coverage and execution gates all pass, refresh current
book and compare BASE/ADD/REPLACE/EMPTY with actual MES/ESinteger size, margins and account rules.
Without those gates report all five homes unearned; no invented payout/contribution. Personal$100kreference
is not the user's actual capital or a claim the same strategy is executable in the smaller starter ladder.
