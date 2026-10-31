# Frozen attempt to break Vault Break and evaluation ONB ADX30

Task: Claude snapshot **ece20f05bd8bac31424d10fc04e0e858f288c28e**, `agents/codex/TASK_break_vb_onb.md`.
Work on codex/work. This audits existing strategies; it creates no new trading idea and selects no replacement.
No live, VPS, MultiCharts, account, funded-plan or ranked-list changes, even if a strategy fails. User/Claude review
any consequence separately. This is **one robustness trial per strategy**, with every mechanical replay disclosed.
The task's explicit fixed stress list supersedes the normal <=5 new-candidate variants: five stress families,
not an optimization. No best setting will be adopted. Both historical periods are already seen, not fresh holdouts.

## Baselines and applicability

Use candidates24.vault_break24 and candidates24.overnight_bias24(adx_min=30,stop_atr=.25), fixed one NQ.
VB defaults: noise .30, ATR15 SMA, midnight open/VWAP, first 10:00, last/flat14:30, target40, stop75, max3/day,
holiday last11:00/flat11:30. ONB: overnight after23:00–08:30, 08:30–08:45 OR, bias top/bottom third,
ADX14>30, ATR15 SMA stop .25, reward/risk3, last14:00/flat14:30, holiday last11:00/flat11:30, one/day.
Use the existing minute Grid24 and _walk convention, targets requiring one NQ point beyond the limit; market and
stop fills pay one adverse tick, target fills no extra tick. Round-trip commission $7.25; use param_clusters.trade_net.
NQ tick .25 and point value20. These one-NQ stress metrics are not the evaluation's dollar-risk MNQ account results.
ONB's current live entry-buffer/market fallback and broker rejection guard are not represented by the historical
candidate function/report; flag this scope rather than claiming live execution parity. No risk sizing is optimized.

Data: owned full NQ day+overnight exports through last common date in 2026, with existing Grid24/cache reused only
after its provenance/date span is recorded. If missing 2017 daytime warm-up is needed, read the already supplied
file from the pinned source into Codex input paths; no data/ overwrite or shared-cache build. Inputs/hashes saved.
Baseline and each stress report 2018–22, 2023+, full2018–26 and each year, all/long/short; VB shorts are N/A.
MC comparisons use overlapping report/data dates and declared initial warm-up, with no date-specific exclusion to
improve a match. VB report: `... VB v1.xlsx`; ADX30: `... _ @NQ - 15 Minutes NQ Overnight Bias.xlsx`, validated Settings
ADX30, StopAtrPct .25, 15-minute, one NQ fixed size. Do not substitute ADX20 or funded ONB ML.

## Baseline parity gate — before stress runs

Read existing exports with portfolio.load_mc. Pair day/side/entry chart-bar identity (VB30m, ONB15m), retaining every
unmatched row. Require matched fraction >=98% of each list, >=99% paired entries within .25 point, >=95% paired
gross P&L within $20/NQ, paired gross-P&L correlation >=.98, and mean-net difference <=max($20,10% of |MC mean net|).
Show counts, side agreement, price/P&L tolerances, differences and dates. Existing code/engine differences can be
corrected only from documented semantics/fixtures, never tuned to performance. Record any correctness fixes.
If a trustworthy close match cannot be established, stop affected strategy and report PARITY FAIL, rather than
pretending stress results diagnose the deployed rule. Do not quietly relax this gate after results.

## Fixed perturbations (each specified scenario once)

Master seed **8675309**, independent reproducible SeedSequence children for price-noise/jitter. Use the SAME noisy
price realization for both strategies. No seeds are replaced based on performance. Save all parameter/seed manifests.

1. **Price noise: 100 runs per strategy.** For each of SD1 and SD2 ticks, 50 fixed seeds. Add independent zero-mean
   Gaussian draws to each observed minute's O/H/L/C; round to .25, then set H=max(noisyH,noisyO,noisyC) and
   L=min(noisyL,noisyO,noisyC). Missing observations stay missing; volumes unchanged. Recompute signals, aggregates,
   ATR, ADX, VWAP and fills from the same noisy grid. Costs remain baseline. Do not perturb prices only at fills.
2. **Indicators: 6 runs per strategy.** ATR10 SMA, ATR20 SMA, ATR10 Wilder, ATR15 Wilder, ATR20 Wilder (ATR15 SMA is
   the base), each otherwise unchanged. Wilder uses the first n completed valid weekday TRs' arithmetic mean, then
   recurrence (previous*(n-1)+TR)/n, known only on the next calendar date, like the existing lagged SMA convention.
   Sixth: VB VWAP from08:30 instead of midnight (noise open remains midnight); ONB OR through09:00 instead of08:45,
   with overnight-end/bias open fixed08:30 and OR including both15-minute bars. Never use the 08:45 bar's open as
   the 08:30 reference when extending the OR.
3. **Timing: 3 runs per strategy.** Entry one native decision bar later, flat one native bar earlier, flat one native
   bar later, separately. VB delay: freeze qualifying decision, enter30m later at next-minute open; no resignal
   required, no queued duplicates while pending/position open, retain per-day3 limit. ONB delay: a qualifying ADX
   order is first active in the bar after the next15m bar, with frozen OR/bias; an intervening order cannot act early.
   All delayed orders still obey the original last-entry and flat boundaries; missing required fill bars are skipped.
   Flat earlier/later shifts regular AND holiday flat by30m VB /15m ONB. Protective stop/target unchanged and active
   from entry, including that minute. No overnight hold or new late entry just because the flat time is extended.
4. **Parameter jitter: 200 valid draws per strategy.** Every numeric behavioral input gets an independent uniform
   factor in[.9,1.1], applied simultaneously; not one-at-a-time. VB: mult, ATR length, first/last/flat times, stop,
   target, max-trades, holiday last/flat. ONB: ONStart, ONEnd, OREnd, bias fraction, ADX length/minimum, ATR length,
   stop fraction, R multiple, last/flat, holiday last/flat. Live EntryBufTicks2, RiskPerTrade0 and NumContracts1 are
   recorded as rounding-invariant/structural fixed-unit fields, not additional entry-buffer/sizing experiments.
   Positive integer periods/counts round half up, minimum1; price distances to nearest .25; fractions/ADX thresholds
   to .0001; risk multiples to .01. HHMM inputs are converted to elapsed minutes before multiplication, never
   multiplied as base100. Round clock boundaries to native bar grid (30m VB /15m ONB). Overnight start is on an
   unwrapped previous-day minute axis (23:00=1380); >1440 becomes after midnight on the current day, without
   accidentally including the whole preceding day. Late endpoints are capped to the last native boundary before
   15:59; holiday endpoints capped to11:45 (VB30m grid =>11:30). Reject chronologically invalid draws before any
   evaluation (first>=last, last>flat, earlylast>=earlyflat, ONstart>=ONend, ONend>=ORend, ORend>=last). Log every
   rejected candidate and reason; continue until200 feasible draws. Feasibility conditioning induces parameter
   dependence; disclose that instead of claiming retained draws are fully independent. No outcome-based rejection.
   Structural bar size, tick/value, boolean holiday handling, costs and account size stay fixed. Integer/grid inputs
   may not change after rounding; report how many distinct values each input actually took.
5. **Execution: 5 runs per strategy.** Slippage2ticks/target-through1pt; slippage3ticks/through1pt; baseline1tick/
   through2pt; slippage2ticks/through2pt; slippage3ticks/through2pt. Each fill's slippage is adverse only for market/
   stop fills; targets pay commission but no market/stop slippage. Recompute trades for changed trade-through,
   including VB re-entry opportunities, not a haircut to a fixed profitable trade list. Commission remains7.25.

Totals: **314 stress replays + baseline per strategy (630 total mechanical strategy runs)** if both parity gates
pass. This count includes all noise/jitter draws; they are correlated diagnostics, not630 independent discoveries.
Save all runs, including losses, empty sides and implementation failures. No additional knobs or rescue variants.

## Frozen pass/fail rule

For each strategy and each family, separately in2018–22 and2023+, report median net total/per-trade, t, PF,
daily Sharpe, max DD, and shares with net>0, net>0 AND trade-t>2, and net>0 AND Sharpe>=half of that period's base.
Use whole-strategy metrics for verdicts; also show all/long/short and yearly distributions to expose hidden weakness.

- **BENDS**: strictly more than50% of the family's runs simultaneously retain positive net and >=half base Sharpe,
  in EACH period. A baseline with nonpositive Sharpe cannot earn this label; flag BASELINE WEAK instead.
- **BREAKS**: in EACH period, median total net<=0 OR median daily Sharpe<one-third that period's baseline Sharpe.
  The failing criterion may differ between periods. No condition on which family produces an attractive result.
- Otherwise **MIXED / WATCH**, with the exact failing period and run shares shown.
- Flag every deterministic setting (and any jitter input's distribution) showing losses or Sharpe<one-third base
  in either period. A deterministic setting that fails in both periods is a dependency warning even if its family's
  aggregate passes. Noise/jitter medians do not certify all seeds. Do not label a long timing delay universally
  fatal to an edge merely because it changes which opportunity is traded; explain what was perturbed.

Overall strategy: BREAKS if any family BREAKS; otherwise BENDS only if every family BENDS; otherwise MIXED/WATCH.
All labels diagnose this frozen sensitivity test, not a live stop/size decision or proof against prior overfitting.
No family/seed/side/period is selected as the new strategy. Report t>2 as a diagnostic, not promotion significance.

## Implementation and reporting

Reuse Grid24, candidates24 generators, grid.execute/_walk, param_clusters.trade_net and metrics.perf. Extend in
Codex files for controlled ATR/VWAP overrides, shifted activation/OR and jittered clocks; baseline outputs must
match original generators, and accelerated loops must pass trade-by-trade equivalence before running stresses.
No shift in close-stamped minute semantics: decision close j, next-minute entry j+1. ONB's stop fills and entry-bar
path retain the repository convention, with explicit limitations rather than an unexplained engine rewrite.
Verify noisy OHLC/NaN invariants, past-only ATR/OR visibility, delay activation and flat-time clipping on fixtures.
Use metrics.perf, with initial zero-equity observation for DD; fixed-NQ daily closed P&L is appropriate intraday.
Use repository10-session block bootstrap and permutation on2023+ baseline all/long/short (2,000 draws) to show
conditional uncertainty. No new placebo/optimization or funded addition/replacement bench is needed to audit an
unchanged already-ranked strategy. This task does not alter a trading plan even if a failure is found.

Deliver agents/codex/results/break_vb_onb.md with Summary<=5 lines, plan commit, parity evidence, all five families,
split/side/year tables, deterministic dependency flags, jitter/noise distributions, all seeds/parameters and input/
code hashes. Main script analysis/codex_break_vb_onb.py, outputs analysis/outputs/codex_break_vb_onb/.
Count two robustness trials. Commit/push only codex/work; Claude reviews before any action.
