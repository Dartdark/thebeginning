# GreenORB: TEST a declared NQ-data proxy; native MNQ reproduction unverified

Summary: User-uploaded fixed-size GreenORB warrants one bounded replication, not an ORB search.
The author reports $13,101 on 296 MNQ trades; these are unverified, selected-history results.
Owned NQ bars support the price/timing rule, with available-bar overnight VWAP as an explicit proxy.
No verified forced flow, native MNQ volume, Liqport engine or author trade ledger is available.
Commit the frozen plan/code before testing; a failed design gate stops recent/account returns.

Sources received 2026-10-30: [PDF](../inputs/greenorb/GreenORB_strategy.pdf),
[post](../inputs/greenorb/post.txt), [original code](../inputs/greenorb/greenorb_fixed.py),
[hash/access manifest](../inputs/greenorb/source_manifest.json). Public fixed-size run:
https://app.liqport.com/runs/c3757286686143e399076ad5491a2e0e . Connected reader could not access it;
no purchase, login, account or credential access attempted. The uploaded class is archived, never imported.
Return trials for this exact upload before this sheet: zero. Synthetic execution fixtures and timestamp-only
coverage checks preceded this sheet. This direct-upload task does not reserve or reset SSRN scout trials.

## 1. Who trades, and what causes the trade?

The author's hypothesis is that three same-direction opening candles reveal persistent opening demand.
No identified participant is demonstrably forced to trade; price continuation is a prediction, not a measured
order-flow fact. A bounded test is justified by the explicit executable source and standing upload instruction,
not a new causal-flow claim. Opening-drive and ORB selection history remains relevant.

## 2. Direction, size and information clock

All times NY unless marked CT. Three completed 5-minute candles in 09:30–09:45 determine allowed direction.
After their close, a completed 5-minute breakout/VWAP/cap signal between 09:50 and 12:00 can place an order.
At decision time, only bars ending by that time enter OR/VWAP/colour. First executable fill is the next
1-minute open with adverse slippage; no signal-close fill. At most one position/day, fixed one micro.
Flatten at the open at wall 15:58 NY. NY and CT observe the same US DST dates; no constant UTC offset assumed.
Dollar flow and opening imbalance size are unknown; do not infer them from candle colours.

## 3. Transmission to the contract

Nasdaq cash/futures price discovery plausibly transmits opening demand to NQ/MNQ. NQ price bars are a research
proxy for MNQ, not its native liquidity/volume/queue. Pre-MNQ-launch design dates are hypothetical micro valuation
of NQ, not trades that could historically have been placed in MNQ. No exact native cash/fill replication claimed.

## 4. New information and owned-input feasibility

| Input | Exact source/fields | Coverage | Timing and limits | Cost/access |
|---|---|---|---|---|
| Day NQ | `data/NQ_1min_2018.csv` through `_2022.csv`; date,time,OHLC,volume | design 2018–22 | close-stamped CT, decisions on closed bars | owned |
| Night NQ | corresponding `NQ_1min_ON_<year>.csv` | design 2018–22 | prior calendar evening + current prefix; no future VWAP | owned |
| Recent NQ | same day/night families 2023–26, with 2022 warmup | earned only after design PASS | already-seen historical validation, not new OOS | owned; not outcome-tested yet |
| Native MNQ/Liqport | claimed Databento MNQ front month + engine indicator/callback conventions | not obtained | exact native volume, roll, engine parity unresolved | no purchases authorized |

[Preflight](../inputs/greenorb/preflight.json) finds 1,238 complete day scan/possible holding paths in 2018–22.
Overnight exports routinely lack the first 17:01 CT close-stamped minute, and sometimes other minutes.
Do not assert missing volume is zero, forward-fill prices, or switch silently to RTH VWAP. The fixed proxy uses
only observed NQ typical-price × reported volume and retains a missing-prefix audit. It tests that proxy only.
The exporter writes `Ticks`; total volume vs tick count depends on the unavailable chart setting. The author
uses MNQ volume. This is a material exact-reproduction limitation, not a source-equivalence assertion.
Incomplete day paths remain unknown/excluded, including shortened sessions; they are not zero-return days.
Resolved ordinary no-signal days can legitimately have zero strategy P&L. Require >=1,000 resolved design days.

## 5. Costs and actual intraday gaps

Primary: $1.24 round-trip native MNQ commission; 2 ticks = 0.5 point = $1 each market/stop fill, target no
slippage with one tick trade-through. Thus $2.24 target-exit cost or $3.24 market/stop-exit cost. Also show the
author's $1.04 commission sensitivity and exact four-tick execution stress, rebuilding fill-anchored targets.
No additional spread charge on top of slippage. Gross-to-net bridge is saved; gross is quote-reference P&L for
the slipped-fill-derived target, not a separately optimized zero-cost strategy. Breakeven extra cost is net/trades.

Current plan documents are archived read-only at Claude `7a42ea76c62838109d45d168887f57a922933ef2` in
[snapshot manifest](../inputs/greenorb/plan_snapshot/manifest.json). GreenORB trades after the US open until
14:58 CT; this overlaps existing ONB, VB and Monday exposures. No claim of an empty slot is established before
event-level portfolio replay. Test every eligible source event; do not condition the standalone screen on flatness.

## 6. Power before returns

Author frequency is roughly 34/year in 2020–22 and 43/year overall; assume 170–215 trades in five design years,
not an observed local signal count. With assumed $180 trade SD, t=2 needs about $25–28 net/trade, or $28–31
gross including costs. The author's claimed $44/trade makes that plausible enough to screen, not established.
Require >=80 trades and t>=2, positive net and four-tick stress. Serial dependence and prior ORB multiplicity
mean this is only a cheap gate; random controls, historical validation and independent review still apply.
No learned model, fitted scaler, hindsight regime or label-based parameter selection is used.

## 7. Prior tests and falsifiers

TIER_LIST has extensive ORB/ONB/RVOL work and the 64-variant building-block study: three opening up bars
held to the close failed design t (1.5). Those histories are not reset. No exact three opening colours +
overnight VWAP + absolute opposite-OR stop + fixed 1.5R upload replication was found in prior local records.
The source's no-colour ablation allows both directions and potentially two trades/day; our controlled baseline
is explicitly first-entry-only, for a matched one-position/day comparison. It is not the author's ablation ledger.
Reject if the primary fails cheap gates or the filter fails removed-loss/random-drop gates. No clock/cap/side
retuning and no selection of an attractive long-only result after whole-strategy failure.

## 8. Failure and diversification

| Question | Prediction before results | Needed evidence/falsifier |
|---|---|---|
| What stops it working? | transient opening moves, absorption, crowded breakouts | no positive net after costs; failed null controls |
| Liquidity role? | marketable entry/stop, resting limit target | native quote/fill matching; no queue advantage assumed |
| How do losses cluster? | choppy opens, gap-through stops, wide OR, volatility shocks | yearly and trade ledgers; stop is not a guaranteed risk cap |
| Shared losses? | probable ONB/VB opening momentum overlap | event-level joint losses and current account chronology |
| Offset before breach? | not established; rare entries may arrive after other losses | funded/eval integer-size marked replay, not daily proxy inference |

One micro and one simultaneous position/day are frozen. Missing path means unknown, never an invented exit.
No risk-percent sizing or allocation change. All five destinations receive explicit eligibility verdicts.

## Decision

**TEST the disclosed NQ/available-bar-VWAP proxy only.** Exact author-result reproduction remains unverified.
Next: commit [frozen preregistration](greenorb_20261030.md) and exact research implementation before returns.
Any survivor must clear all later gates; failure stops dependent tests and is a completed negative result.
