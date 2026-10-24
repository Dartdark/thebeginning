# ORPullback: frozen current-plan portfolio test

Summary: The user requested a portfolio backtest after the source-only review missed the intended scope.
Replay the supplied fixed rule and compare it with the latest funded and evaluation plans.
Two execution models are frozen; no parameter selection, regime switch or live change is authorized.
This is historical replication of already-seen history, not a fresh holdout or a promotion decision.

Evidence: `agents/codex/evidence/or_pullback_portfolio.md` (TEST for this limited comparison).
Sources: unchanged `agents/codex/inputs/or_pullback/source.txt` and `report.pdf`.
Current-plan reference: Claude `a67035be4189b493098c80f1def979348520fd5d`.
This document must be committed before executing either candidate against actual prices.

## Rule and execution clock

Use existing Grid24 cache and its 5-minute close-stamped bars, Central time. Opening range uses
08:35, 08:40 and 08:45 closes (minutes 08:31 through 08:45). After the range, a close above/below
arms that side. A subsequent red bar still above the range triggers long; green still below triggers
short. Check previously armed flags before arming the current bar. Arming persists across recrosses.
Consume a side on its first trigger, including triggers blocked by another position or other guards.
One position, two entries per day maximum, two gross-negative closed trades maximum. No same-side
reuse. Close entries, fixed 50-point stop and 100-point target, price scaling off. Entries through
14:30 inclusive, normal flat at 14:55. No author's rolling six-month switch, extra filters or resizing.

Exactly two strategy return variants:

1. `reported_rule`: protective orders active from the first minute after the close entry.
2. `literal_mc_delay`: ordinary IOG-off source timing; first five full minutes after entry unprotected,
   orders active from minute entry+6. Missed earlier stop/target touches do not retroactively fill.

Common account adapter: flatten at 11:30 on repository early-close dates, prohibit entries at/after
11:30 on those dates. This is a disclosed source difference, not silently claimed author parity.
Require finite minute OHLC throughout 08:31 through the adapter flat; exclude/audit incomplete sessions
before signal generation. Same-minute stop/target collision is stop first; stops gap at worse open;
targets need repository 1-point trade-through and fill at limit or better gap open. Held price exposure
starts entry+1: the entry-minute range occurred before the close fill. Fees are charged at entry and
included during open paths. No interpolation across missing minute data.

Costs: $1.04 per micro round trip plus 0.25-point slippage on market entry and stop/time exit;
target limits have no exit slippage. Slippage changes money P&L, not trigger/bracket geometry.
Additional frozen sensitivity: $1.24 micro fee for candidate and plan together, reported separately.

## Mechanism and pre-return screen

Hypothesis is price continuation after the opening breakout; no observed forced-flow series establishes
who must trade or why this premium persists. The source is fully specified enough for a price replay.
Reported recent means $9.58-$15.51 per MNQ after the author's $2 allowance exceed the roughly $2.04
ordinary market round-trip cost here. With assumed 300 events/year, five-year n about 1,500 and trade
SD about $140/MNQ, t=2 needs about $7.23 net/trade before dependence. The claimed edge makes this
cheap screen feasible, not passed statistical evidence. Stops can gap and 2 MNQ nominal stop is $200.

## Historical and trial handling

Run 2018-22 design first, with fixed rules and both variants. No winner selection: reported_rule remains
primary even if delayed timing looks better. Run 2023+ once for historical replication. Report all years,
both sides, and the author's recent 2021+ regime as a descriptive split, never as a selected replacement
for 2018+. If design is weak, account comparison remains the user's requested diagnostic and promotion
fails; do not tune away old losses. Count two candidate variants, two fee regimes, all allocation tests
and placebo replicates explicitly; author's prior search count remains unknown. Daily correlation and
joint losses are measured after all candidate events, never used to exclude entries.

## Current plan, baseline and account tests

Reuse ignored price/lab/session caches. Load current roster with pinned latest source semantics, including
actual fees; reconstruct only missing frozen RS baseline ledger with the original fixed RS functions and
compare with committed ledger. Do not rerun RS parameter searches. Preserve the current CL/MOC baseline
path approximations and disclose them. Archive module/data hashes and calendar coverage. Check baseline
against latest saved funded reference: y1 $9,180, y2 $11,982, blown 7.6%, all-six 90.8%, median six 263;
evaluation 49.8% pass. Differences require explanation rather than claiming parity.

Funded plan: VB_N 2 / VB_F 1, ONB ML risk $400, MON 1, EOS risk $700, LDF 2,
NFP risk $500, Bridge 1, CLS 2 MCL, MOC 2 MES, RS longs 1 MNQ. Fixed allocation set:
BASE; EMPTY_VB (remove VB_N and VB_F); each timing mode added at 1 and 2 MNQ; each timing mode
replacing the full VB slot at 2 MNQ. VB is the preselected overlap control because both trade the
opening NQ breakout window; the measured correlation may differ. This is not an ONB-only contest.
All candidate sizes receive the unchanged funded cushion multiplier [.5,1], reference $1,500 and
integer flooring. Reuse funded_sim/funded_bootstrap. For speed the already-checked exact quantity-state
lookup in codex_ob_v2_accounts may be reused, with exact five-output parity against current funded_sim
on five fixed histories per configuration. Use 1,000 paired 500-day circular block histories, length20,
seeds1,2,3,4 each250, matching the saved real-fee benchmark; horizons250 and500.
Run full2018+ and separately2023+ (same frozen draws mapped within that calendar).

Evaluation plan: VB8, ONB ADX30 risk$1,100, Bridge2, EOS risk$500. Compare BASE, EMPTY_VB,
each mode added1/2MNQ, each mode replacingVB with2MNQ. Use the existing challenge simulator,
actual integer plan risk sizes, every chronological start, 21-day limit and joint minute paths.
Keep same-minute breach/target convention inherited from the reference; disclose its limits.
Report pass/fail/time, paired changes, design/2023+ and median passing days.

Funded outputs: expected payouts1y/2y, empirical5-95% payout ranges, blown share, all-six share,
median days to six (include infinite noncompletion), paired mean payout/risk changes with95% intervals
(5,000 resamples of paired histories). Empty-slot and baseline comparisons both required.
Report joint daily losses, daily correlation, occupancy overlap, and candidate contribution on baseline
loss days. Use mark-to-adverse-minute paths and costs throughout; do not substitute sums of closed trades.

## Standard diagnostics and decision

Whole/long/short: trades, win, average and total net $ perNQ/MNQ, t, Sharpe, Sortino, PF, Calmar,
Ulcer and maxDD by year/design/2023+. Reuse metrics/resampling/montecarlo, with 2023+ bootstrap
intervals and 252-day EOD-trail simulation at1/2MNQ. Placebos: 1,000 random-side samples using
same observed entry events and replayed fixed exits (one-side-per-event, no portfolio selection);
1,000 random-time schedules preserving event day, side, first/second chronological order and exits.
Use seeds848/849. These are falsification controls, not 2,000 selectable strategy candidates.

Recommend no plan change unless paired benefit beats baseline and empty, risk is not materially worse,
and all latest promotion gates pass: design positive,2023+t>=2, multiple-test tANDDSR>=.95, clean
placebos, exact MC parity and independent checker PASS. A statistically positive small payout difference
alone does not establish a useful change near the payout cap. Missing original exports/source provenance
remain unresolved even if Python works. Independent agent reviews code/outputs before final report;
Claude reviews/ranks results and user decides trades. No live files, account controls or infrastructure.
