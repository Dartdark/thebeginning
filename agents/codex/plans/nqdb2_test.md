# NQDB2 / DriftBreak v2: frozen proxy test, 2026-10-24

Summary: Test the user's uploaded default rule and isolate its negative-drift veto on identical data.
The user explicitly requested the backtest; missing chart settings are declared research assumptions.
Four fixed rule profiles plus one execution stress; A1 is chosen before returns for any account comparison.
2018-22 is the design screen; no NQDB2 2023+ returns or account simulations until the gate below passes.
No live, plan, VPS, broker, ranking or external account changes are authorized by this test.

## Registration and sources

- Evidence: `agents/codex/evidence/nqdb2_proxy_test.md`; prior exact-source evidence remains NEEDS DATA.
- Upload: `agents/codex/inputs/nqdb2/source.txt`, SHA256
  `648e15c16cad8c4eae5f10cea7cd78fe01e1cf37be1c63f33df2abcc4a1fabdf`.
- Latest builder brief blob `60ed6049860b0f75ba4fc7b0832c76764f5315ac`, Claude context
  `e34d71cd3537a9f019d2521e280fc92f3ffdb4c6`; source review commit `7cf8bb3`.
- Remote Codex parent inspected before registration: `ddd15d2`; preserve its concurrent research.
- Registration commit must exist on `codex/work` BEFORE historical replay. Scripts may be implemented and
  synthetic fixtures run beforehand; no strategy returns, market outcome screens or account simulations.
- The hypothesized mechanism is price continuation/avoiding failed upside breakouts after negative drift.
  There is no independently measured forced flow. Most overlap: current Vault Break SP, then ONB/RS.

## Frozen rule, data and execution

Use existing `scratch_data/g24.pkl`, not rebuilt caches. It spans 2017-12-01 through 2026-10-09; December
provides prior-date warm-up. Use all observed calendar dates, including Sundays, and all eligible trades.
Warm-up is 15 completed positive-range native dates; do not require a weekday-only history. Freeze full-session,
midnight-aligned, close-stamped 30-minute bars, IOG off and one-minute magnifier. The native 00:00 bar includes
the previous date's late minutes but belongs to its close-stamped new Date. Missing minutes remain missing.
Do not infer a holiday liquidation from the last observed RTH price. Any endpoint-unclosed position is censored
and listed, never turned into a final-price winning/losing trade. The terminal data date has prices through
16:00 CT and is not excluded merely for ending then. Reports must state any censoring and incomplete coverage.

Native-source semantics: previous 15 completed Date high-low mean, including Sunday partials; session-open
anchor is first native bar Open on new Date; VWAP is cumulative 30-minute typical-price times **total exported
volume**, explicitly a surrogate for MC `Volume`. Calendar Date resets both. Default veto rejects
100*(Close/Close[4]-1) <= -0.10%, using four previous valid native bars across date boundaries. Long only,
flat, Close > session open + 0.30*mean range and Close > VWAP, 10:00 through 14:00 inclusive, next-bar market,
maximum two submitted attempts/date. There is no quantity or signal optimization. Time<15:30 remains active.
Prearmed whole-position brackets at one NQ: target 40 points, stop 75 points. Seven consecutive closes below
VWAP submit a next-bar exit. Normal 15:30 close submits a next-bar market exit. Calendar rollover submits the
source's Carry exit; SetExitOnClose is the declared 24:00 chart-session endpoint. Preserve actual cross-date
holdings, duplicate-exit submissions and endpoint orders in an audit ledger.

Reuse Grid24 bars and `grid._walk` one-minute OHLC path conventions; extending the shared executor is needed
for dynamic VWAP/carry exits and re-entry. Stop gaps fill at the observed open, not at the stop. Target fills
at its limit only after **1.00 point trade-through**. $7.25/NQ round-trip commission; adverse 0.25 point on each
market/stop fill (one tick), target has no additional exit slippage. Raw bracket levels anchor to the raw entry
per repository convention. Ledger net already includes these costs: never charge `trade_net` again.
Account geometry is from NQ, dollars divided by ten per MNQ; switching raw dollar stops to an MNQ chart is
not this test. Slippage stress changes adverse fills to three ticks and leaves all rules/brackets fixed.

## At most five frozen return streams

| ID | Calendar protection | Veto | Use |
|---|---|---|---|
| S0 | Literal source | Off | Matched source-family control |
| S1 | Literal source | Default 1 | Uploaded rule proxy |
| A0 | Fixed Apex early-close safeguard | Off | Matched safe control |
| A1 | Fixed Apex early-close safeguard | Default 1 | **Primary candidate, chosen now** |
| E1 | Same as A1, three-tick fills | Default 1 | Mandatory execution stress |

Apex safeguard uses the existing deterministic `replica.is_early_close` / `candidates24._early` calendar,
never future prices or plan occupancy: on flagged dates no entries at/after 11:00, flatten at the observed
11:30 bar close; normal-date source times stay fixed. If that native close is absent, no price is invented;
the actual later exit is recorded and legality checked. Residual carry or closure violations block account
scoring. These profiles do not repair any other source feature. No VetoMode2/3, thresholds, range lengths,
lookbacks, bar sizes, clock scans, alternate target fill-through or quantity search. Current VB is an existing
comparator, not a newly optimized sixth rule. Null simulations are inference, not selectable variants.

## Stage 1: design 2018-22, fixed gate

Run the five streams only for 2018-22 first. Describe S0/S1 and A0/A1 side by side; do not choose among them.
Report net total and per trade, counts/win/t, all standard metrics and every calendar year. Long-only implies
whole=long and short count zero, not a missing short analysis. Trade t is mean/(sample SD/sqrt(n)). Daily
series include zero-trade eligible trading dates and reconcile to trade totals; cross-date mark-to-market must
also reconcile net costs, rather than assigning the whole carry P&L to an account day and erasing its exposure.

**Strategy design gate:** A1 has >=100 completed trades; net P&L >0; trade t>=2; at least 3 of the 5 calendar
years positive; E1 net >0; no unresolved replay accounting/execution bug or material endpoint censoring.
All conditions must pass to open Stage 2. If it fails, STOP: no 2023+ NQDB2 returns, Monte Carlo or funded/eval
bench. This is a cheap reject at the preregistered gate, not evidence about an unrun recent period.

**Veto claim is assessed separately:** compare total net and drawdown to the same-window unfiltered control;
list removed original trades and newly admitted/re-entry trades by decision identity. Report removed mean/t,
not just improved average of retained trades. For A0->A1 and S0->S1, run >=1,000 random trade drops matching
the net trade-count reduction (and separately the gross removed-original count when re-entry changes it)
and >=1,000 random decision-mask reruns that permit fresh re-entries under the original daily cap. Use actual
vetoed eligible-decision count as the full-replay mask count. Profit and DD ranks >=95th percentile, losing
removed-trade mean with t<=-2 and improved total net/maximum DD are required to support the veto. Failing
that rejects the veto claim; it does not authorize selecting mode0 as the production winner.

Random-side and random-entry-time controls use the same brackets, costs, cap and exits, 100 seeds each.
Time nulls preserve each date's primary-candidate submitted-signal count, sampling valid decisions in that
date's same eligible clock window; no price/veto gate for time nulls. Side nulls randomize direction at the
actual primary decisions, respecting the position/cap and re-executing exits (never simply negate P&L).
Report one-sided empirical profit p=(1+null>=actual)/(1+draws). No null-based retuning. Reusable per-decision
outcomes/batch scheduling may accelerate these simulations, but must match full replay on selected seeds
and all fixed profiles before their outputs are trusted. RNG seed 20261024 and deterministic offsets by null.

## Stage 2: historical replication and account comparisons, conditional

Only after a saved passing design-gate JSON, run the SAME five frozen streams once on 2023 through the
cache's endpoint. This is already seen historical replication, not a fresh holdout. No parameter selection.
Repeat standard results, matched filter/null checks and annual rows; 2023+ daily moving-block bootstrap
using `resampling.bootstrap`, block20, 3,000 draws, seed20261024. Report net, PF, Sharpe and drawdown intervals.

Account simulation additionally requires A1 net>0 in 2023+, source/replay checks clear, zero censored A1
positions, zero out-of-calendar or illegal holds, and ledger/net-path reconciliation. If these fail, publish
the failure/violation rows and stop; never filter the illegal trades away to manufacture an account candidate.

Use the current documented ten-leg funded plan (including ES MOC 2 MES and RS longs) and four-leg 50K
evaluation roster **VB8 / ONB ADX30 $1,100 / EOS $500 / Bridge2**. Freeze exact source manifest and baseline
parity against the current canonical real-fee scoring before evaluating candidate allocations. Reuse current
helpers (pin `a67035be`, verified unchanged at Claude `e34d71c`) rather than old eight-leg or two-leg baselines.

Fixed allocations, no size selection: BASE; ADD A1 at1MNQ; EMPTY VB; REPLACE VB with A1 at existing VB sizes
(funded normal2/flagged1 MNQ, evaluation8 MNQ). Score add and replacement relative to BASE and EMPTY slot.
Paired funded block-bootstrap: 1,000 identical histories, block20, 500 trading-day/two-year horizon, both2018+
and2023+ pools. Use the existing current21-day challenge benchmark. Primary fee $1.04/MNQ round trip and
stress $1.24, with other legs' proper micro fees; reuse identical sampled histories. Report year1/two-year
payouts, breach rate, time to six payouts, evaluation pass rate and speed, with paired uncertainty. Also
`montecarlo` trailing-$2,000 risk for A1 at1MNQ and fixed replacement exposure. Do not select a new size.

Evidence of improvement requires a positive paired 90% interval for funded year1 OR two-year payouts (or
evaluation pass rate), with no two-year payout deterioration, breach increase >1 percentage point or slower
median six-payout time >5days, and replacement beating EMPTY VB on the same criteria. Report weaker/noisy
differences as no demonstrated gain. No recommendation from a favorable point estimate alone.

## Trial accounting, final decision and deliverables

Count all five fixed profiles, including failed/stress streams, in the task-local trial ledger; report every
period opened, null count, seed and implementation correction. Use the latest ranked-item count +this idea
for `metrics.t_threshold` and DSR, and report a conservative +5-profile sensitivity. Do not edit TRIALS/TIER.
Promotion requires the brief's AND conditions: multiple-testing t AND DSR>=.95, positive both periods with
2023+ t>=2, clean placebos, independent checker PASS without concerns, MC confirmation, and account gain
beating the empty slot. This total-volume proxy alone cannot satisfy MC confirmation; no live promotion.

Verdict: REJECT if the design gate fails, net edge/replication fails, or account contribution fails. WATCH if a
promising proxy has unresolved source/data/MC or statistical evidence. CANDIDATE only after all applicable
requirements, never from a proxy alone. Any change after opening a period is a separately registered trial,
not an in-place improvement. No unrelated research, plan changes, chart deployment or messages to others.

Commit scripts under `analysis/codex_nqdb2_*.py`, outputs under `analysis/outputs/codex_nqdb2_test/`, final report
`agents/codex/results/nqdb2_test.md` with Summary<=5lines. Record cache hashes, environment versions, exact
preregistration SHA, all cost/volume/session assumptions, full event/order/violation ledger, and reproduction
commands. Current source-validation blockers remain disclosed even if the proxy earns money.
