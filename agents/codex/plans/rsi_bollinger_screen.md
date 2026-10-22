# MeanReversionRSI: frozen GC and NQ personal-account screen

User authorized testing both markets after the gold breakout, and supplied the mean-reversion transcript.
Source audit is complete; this is a separate performance trial, with no returns computed before this commit.
Evidence: `agents/codex/evidence/rsi_bollinger_standalone.md`. Work only on codex/work and permitted Codex paths.

## Rule and mechanism

Execute the preserved MeanReversionRSI class for signals: 4h RSI(14)>70 long / <30 short, current price above /
below 4h Supertrend(10,3), 1h ADX(14)>20 and 4h ADX(14)>40. Buy lower / sell upper Bollinger(20,2,SMA,
population SD) on 1h. Refresh unfilled orders at every hourly decision; keep only one pending order / position.
On fill, freeze the opposite band target and a six-hourly-ATR(14) stop, recalculated using information available
at the fill. No dynamic target, trailing stop, time exit or overnight restriction. This bets on a pullback within
a strong trend; there is no documented forced trader or independent flow evidence. This is the user's bounded
diagnostic, not a forced-flow discovery. NQ longs overlap existing ONB/Vault Break/other long exposure most;
gold's portfolio independence is unmeasured.

The transcript confirms hourly/four-hour settings, fixed exits (18:08–18:29), and that multiplying quantity by
five was a demonstration after inspecting returns (20:36–21:23). It describes crypto, not a GC/NQ result.
The original source and transcript remain unaltered. Undefined watch_list.bbw is never called; no trading method
is changed. Use fixed one futures contract to isolate the signal, without running the crypto risk helper.
This is an explicit sizing adaptation, not the source's 3%-then-times-five equity curve or a corrected account
risk trial. If the edge passes, a later contract-aware sizing study needs its own frozen specification.

## Data and causal candles

Use existing Grid24 on 2018–22 GC and NQ day+overnight files only. Start with 2018 data for both markets,
require 240 observed hourly AND 240 visible four-hour bars before any signal. This openly loses the initial
warm-up period; do not pretend missing 2017 NQ daytime is complete. No 2023+ price reads before all gates pass.
Convert CT close-stamped minutes to UTC open timestamps by subtracting one minute; reject invalid bars,
record duplicates and stop for ambiguous observed DST timestamps. Do not discard large gaps or infer rolls.
UTC clock-aligned observed 1h/4h candles; no padded closures. Hourly decision is at the hour boundary after all
of its observed minutes. Scalar indicators use the pinned Jesse last-240-bar convention, Rust 1.3.1 kernels.
The last visible 4h bucket INCLUDES its partial hour-to-date contribution, unlike the gold code's explicit
[:-1]. Never use the future high/low/close of that bucket. Pin SDK 9a3ebe075d9d0af5f012f921f46c2286f234af68.

## Four frozen market/execution trials (no parameter search)

For each of GC and NQ, run:
1. Primary: activate limit next minute at the decision boundary, expire at the next hour boundary. Entry and
   target require trade-through: GC 0.1 point / NQ 1 point, matching the repository's NQ target convention.
2. Stress: activate one minute later, require twice that trade-through for entries and targets.

Round limits, stops and targets to nearest contract tick (GC .1 / NQ .25). No better fill than the limit is
credited on favorable opening gaps; fill at the resting limit only after the required through-price is seen.
An order never remains pending over its expiry or renews while a position is open. Missing activation minutes
are skipped rather than queuing into a later session. An exit can be followed by a new order only at a subsequent
hourly decision, including the boundary at the end of that exit's hour.

Use the repository OHLC nearest-extreme path for minute ambiguity. At the through-price event, reconstruct the
forming hour using prior observed minutes plus only the traversed portion of the current minute. Recompute ATR
and bands via the original on_open_position method, freeze brackets and check only the remaining entry-minute
path. Never allow a target touched before the entry to close the trade. For later minutes reuse grid._walk,
including gap-stop-at-open handling. If both brackets are touched the repository path determines the exit.
Ignore partial-minute volume for indicators because these defaults do not use it. Round bracket prices; reject
nonfinite or wrong-side brackets and count them as execution-spec failures, not silent deletions.

Fixed one GC: $100/point, $27.25 round-trip; one NQ: $20/point, $17.25 round-trip. These charge commission $7.25
plus one adverse tick each fill, including limits conservatively. No broker margin or roll costs are assumed
verified. Mark any final open position at the last observed design close; exclude it from completed-trade t and
support, include its P&L in equity. Daily P&L is marked across holding days, trading date = CT minute open +7h.

## Cheap gates, separately per market

Require all of: >=30 completed primary trades, net trade t>=2, gross mean>=1.5x cost, at least three positive
marked calendar years, positive stress-variant total and positive primary total at double costs, and zero unresolved
causal/execution errors. If any fails, stop that market: no optimization, side-only rescue, 2023+, account-sizing
study or funded bench. Always report whole/long/short, all years and both variants, actual support and cost hurdle.
A passing market is at most WATCH because futures roll/quote provenance and exact original-engine parity are
unverified. Do not open 2023+ automatically: record passing gate and implementation review first. Any later
replication is already-seen history and requires forward evidence; it is not a fresh holdout.

## Controls / power / reporting

Before returns, save hourly eligibility counts, warm-up date, candidate limit orders and planning power arithmetic
for n=30/50/100, assumed trade SD=$500/$1,000: approximate net hurdle 2*SD/sqrt(n), not a measured power claim.
Verify source signals/brackets on fixtures, four-hour boundary visibility, future-prefix invariance, no-touch
entry rejection, entry-bar protection, expiry and pre-entry-target exclusion. These checks precede return output.
Afterward report actual trade SD/hurdle; rare trades or correlated overlapping trades across assets do not
provide independent support. No pooling GC and NQ to manufacture significance.

Use repository metrics.perf and resampling for marked daily risk; include initial zero observation for DD.
Use a 10-session block bootstrap (2,000 draws) and 1,000 random-side controls at the same signal opportunities,
with side-appropriate limits and identical exits/execution. Controls rerun single-position sequencing; their
conditional comparison does not independently validate signal timing. Fixed seed 314159. No filtered variants.
No Apex funded bench for a failed or overnight-ineligible strategy. Personal capital/margin recommendations
require a passing signal and separate sizing; $50k here is only a metrics denominator.

Report Summary <=5 lines, all trials including failures, the transcript's small crypto sample and sizing/search
limitations, source/execution differences, causal checks and reproducible scripts/hashes. Commit and push only
codex/work; no live/VPS changes, purchases, new provider accounts or messages to others.
