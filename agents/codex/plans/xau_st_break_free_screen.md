# XAUSTBreakFree: frozen GC personal-account screen

User asks to test uploaded gold strategy first; queue RSI/Bollinger for later transcript/context. Only gold in
this task. Work on codex/work; preserve uploaded bytes. Evidence: `agents/codex/evidence/xau_st_break_free.md`.
No optimization, live/VPS access, API keys, purchases, account changes or generic strategy search.

## Frozen source and parameters

Use `XAUSTBreakFree` executable methods from the original class through a research adapter. Pin official Jesse
reference to `9a3ebe075d9d0af5f012f921f46c2286f234af68` and Rust indicators to `jesse-rust==1.3.1`.
All defaults: st_period=24, st_factor=4, ema4=10, don_period=85, atr_stop=3, trail_atr=6.5,
exit_on_flip=0, l_adx=10, s_adx=15, s_stop=4, s_trail=3.5, s_tp=5. RISK_PCT=3, MAX_LEV=4.
No DNA/config export was supplied; defaults are the tested specification, not verified author-run settings.

## Data / indicators / availability

Use existing Grid24 on GC 2017–22 files only, no shared-cache writes. Convert CT close-stamped minutes to true
UTC open timestamps (subtract one minute); retain observed candles only. Reject impossible OHLC/nonfinite
observations and record missing/duplicate/ambiguous timestamps. Do not remove large gaps or infer roll dates
from returns. Continuous-contract and unknown rollover treatment remain explicit limits of positive results.

Aggregate observed minutes into UTC clock-aligned 1h/4h candles. A strategy decision occurs only after an observed
hour's closing boundary; never before the last constituent minute was available. Use the source's schedule on
candle-open timestamps, with current historical closures represented by absent observed bars. The uploaded holiday
overrides mostly cover 2026–27; do not invent/backfill them into 2018–22. Record that a calendar-parity limit remains.

Match pinned Jesse observed-bucket get_candles semantics: the last visible 4h bucket is returned and the source
drops it, including when it has just completed exactly on a 4h boundary. Session hourly history excludes the current
hour for the channel. Scalar indicator calls use the last 240 filtered candles, as the pinned helper default does.
Require ≥85 prior session hours and ≥29 filtered anchor bars before a decision. Default source ATR is period 14.
Use official Rust kernels for ATR, ADX, EMA and Supertrend; call supplied source for signal and trailing behavior.
Verify future-prefix invariance and boundary behavior on fixtures before replay. No unfinished future bar is visible.

## Execution: two frozen variants, not a search

1. **Primary next-minute market adaptation:** at a valid hour close, enter at the next observed minute open at that
   boundary. If that minute is missing/market closed, skip the entry; do not queue it across a session/weekend.
2. **Mandatory one-minute delay stress:** same rule, but earliest entry one minute later; require that observed
   minute. Keep source signal and stop fixed at the original decision; if the intended stop is already crossed at
   entry, skip the stale order and record it. Do not move the stop to make a trade fit.

One position at a time, allow overnight/weekend holds. Stop active on entry minute. Source trailing updates only
after hourly decisions and activates from the next minute, never earlier in the completed bar. Best price uses
hourly closes, not intrabar highs/lows. Long has no target; short target is 5×entry ATR4 below the decision price.
No exit-on-flip (default zero). Reuse `grid._walk` for minute stop/target sequencing and gap stop fills, extending
first-minute gap checks for carried positions; target requires one GC tick of trade-through. Round futures stop/
target levels to the nearest 0.1 tick; keep signal indicators unrounded. If stop and target hit together use the
existing walker's stated OHLC-path rule. Close residual positions at the final observed design close, flagged as
terminal marks and excluded from closed-trade t/support; include their marked P&L in equity and yearly results.

Screen at fixed one GC ($100 per price point), subtract $27.25/trade conservatively ($7.25 + 0.1×100 each fill).
Add a double-cost diagnostic on the same trades, not a selected variant. Report source/default versus real futures
execution differences. The author filled market orders at decision close; we do not assume such fills are obtainable.

## Cheap gate: primary design 2018–22 first

Do not read 2023+ price fields, returns or signals until all conditions pass:
- At least 30 completed trades, positive net mean with trade t ≥2, and gross mean ≥1.5×baseline cost.
- At least three positive calendar years in marked-to-market net P&L.
- The mandatory delay and double-cost diagnostics remain net positive; no rule changes after inspection.
- No unresolved implementation/lookahead error. A positive result with unresolved contract-roll/quote provenance
  is only WATCH and cannot establish live readiness.

If any gate fails: report whole/long/short and by year, actual support and costs, and stop. No holdout, sizing study
or funded bench. Do not try shorts/longs alone as replacement candidates or optimize any default.

If it passes: record the design decision before loading 2023+ (through last owned GC date). Run the same frozen
variants once as historical replication, not untouched evidence: the video author optimized on 2024–26 and this
repository has also seen 2023+ in many studies. Retain split/year/side metrics and resampling intervals.
Only then assess a $50k personal-account, contract-aware MGC version of the source's 3% risk / min(4,0.95×4)
notional cap, with integer MGC sizes and explicitly assumed commission. No claims of broker margin sufficiency.
No Apex bench for an overnight-ineligible strategy; explain this applicability boundary.

## Controls, risk and reporting

Use `metrics.perf`, `resampling.bootstrap/permutation`, `montecarlo.trade_mc` as applicable. Daily P&L is actual
mark-to-market across holding days, not all profit assigned to exit day. Include an initial zero-equity observation
when calculating drawdown so the first loss counts. Label $50k as a reporting denominator, not recommended capital.
Report longs and shorts and year counts even when poor. Count two execution variants, no parameter optimization.
No engine output or author's performance will be claimed reproduced without parity evidence.

After the design screen, if enough trades exist, use 1,000 random-side controls with the same eligible hour set,
entry process, ATR exits and single-position rule; do not shuffle already profitable trades as proof of an edge.
The side control is a diagnostic, not a selection gate retrofitted to results. Fixed seed 271828. Bootstrap daily
P&L in 10-session blocks (2,000 draws) for the evaluated period; it measures conditional uncertainty, not freedom
from search bias. Source search count is unknown beyond the ≥200 requested in its docstring.

Final report under agents/codex/results, Summary ≤5 lines, code/input/output hashes, reproduction command,
implementation verification, gate decision, all attempted variants and unresolved limits. Commit and push only
codex/work. Keep the RSI/Bollinger performance test queued; do not conflate its sizing defects with this class.
