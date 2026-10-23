# OB v2 versus current plans: TEST — conditional replay authorized by the user

Summary: The user authorizes assuming matching data and testing OB v2 against the current plans.
This permits a conditional research replay without waiting for native MC trade pairing; it does not establish parity.
Freeze the submitted ATR-ratio rule and the plan's existing half-day operations, with an unfiltered control.
Use a cheap 2018-22 edge/cost gate, then historical replication and account comparisons without tuning.
No strategy returns were computed before this sheet and the associated plan were committed.

Sources: submitted `agents/codex/inputs/ob_v2/`; prior comparison `agents/codex/results/ob_v2_comparison.md`;
current source/roster snapshot Claude `e7c394f`; cached grids/lab and 2017 warm-up export preserved under
`agents/codex/inputs/ob_v2_bench/`. New return variants authorized: filtered rule and one unfiltered control.
External lookback searches and seen 2023+ outcomes remain part of the selection history.

## 1. Participant and cause

The hypothesis is continuation of inventory/price pressure revealed by the opening location and subsequent
opening-range break; the ATR ratio suppresses unusual volatility expansion. No named forced buyer/seller or
published exact-rule effect size is established. This is a related price-family challenger, not a new external flow.

## 2. Information, direction and timing

Midnight-reset overnight range to 08:30; top/bottom thirds select direction. A completed 15-minute close beyond
the 08:30-08:45 OR can signal after 08:45 through noon, with ADX(16)>=20, prior-bar-range and OR-size gates.
Prior-session RTH ATR15/ATR100 must be in [0.6,1.2]. Signal-close stop is 0.30 ATR15, target 3R, next-bar market,
up to four attempts/day. All variables are available at decision. Both filtered and unfiltered controls require
100 prior usable RTH sessions. Freeze the existing plan's half-day cutoff/11:30 flatten as an explicit overlay.

## 3. Contract transmission

Signal and exposure are NQ/MNQ; no cross-market transmission assumption. No magnitude of residual demand is
known. The new filter is likely highly related to existing ONB exposure, so replacement is central.

## 4. Data feasibility

Owned one-minute grid covers the plan through 2026-10-09. The fetched 2017 daytime export supplies May-December
RTH warm-up absent from the old cached grid. Use it in memory for causal indicators without replacing the cache.
User's matching-data assumption resolves the previous wait for MC reports for this research test only. Preserve
grid/source hashes, both ATR histories and eligibility flags. Native order/MC parity and live quotes remain unverified.

## 5. Costs and gaps

Use the same repo NQ commission/adverse-tick convention as the current baseline, with the repo's one-point
target trade-through. Native MNQ fees remain unknown. Register a conservative candidate-only extra commission
stress, leaving the baseline unchanged; it is a sensitivity rather than a verified broker fee model.
Test every eligible event. US-session overlap with ONB/VB/RS is expected, not a reason to condition the signal
sample on flat-plan days. Later account runs keep cross-strategy daily paths and concurrent risk together.

## 6. Power and cheap gate

The supplied annual rows claim 293 filtered 2018-22 trades; that supports a modest-cost verification, not a
power guarantee. Trade SD and effective clustered n are unknown. No-return coverage checks precede a fixed
cheap screen. Thresholds are in the plan; no other lookback, ratio, ADX, stop, target or size is selected.

## 7. Prior work and falsifiers

The unfiltered Bridge ORB was previously weaker than our account-specific ONB versions; that is not a result
for this ratio filter. Both this filter and our frozen ML have seen-data limitations. Refute an upgrade if it
fails gross-versus-cost screening, behaves like matched random removals, loses its total-dollar contribution,
or does not improve account utility beyond the preregistered margins. Report profitable removed trades honestly.
This is explicitly a risk-filter account test: a positive removed mean defeats a bad-trade-elimination story,
but the user-authorized question is whether that sacrificed profit buys improved payout/drawdown outcomes.

## 8. Failure and diversification

Market entries/stops pay liquidity costs; limits can miss. Losses may cluster during reversals, expansion and
gaps; signal-close anchors change actual stop risk after an entry gap. Existing ONB/VB/RS can share these losses.
No guaranteed offset is assumed. Apply account floors/netted P&L chronologically using existing bench rules,
including cushion sizing. Intraday operations are frozen, research-only and do not authorize a platform change.
Later comparisons include base, addition, replacement and empty slot; do not move opposing legs to other accounts.

## Decision

**TEST under the user's matching-data assumption**, with the frozen research half-day overlay and explicit
execution/cost limitations. Plan: `agents/codex/plans/ob_v2_plan_test.md`. A passing model result can justify
independent review/forward verification, never a live or trading-plan change by this task.
