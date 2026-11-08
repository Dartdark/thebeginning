# Frozen ingredient decomposition: Dual Thrust, Relative Strength, Late-Day Flow

Summary: Determine which specified components add historical net profit and which constrain risk.
User-authorized diagnostic of existing strategies; no optimization or new portfolio candidate selection.
Commit evidence, exact harness and source inputs before returns. Preserve original selection history.

## Fixed variants: 13 total rule cases

**Dual Thrust v4 (5 cases):** original; remove prior-range band distance (K=0, thresholds at RTH open);
remove RR/ADR20>1.2 skip (band=0); remove 100-point target (tp=0, 50-point stop unchanged);
remove entry-bar stop only (entry_bar_stop=False, later stop/target unchanged). Holiday filter stays.
Prior-range entries and fixed exits are as the pinned port; no new parameter values scanned.

**Relative Strength (4 cases):** original residual Z; remove ES by own-momentum Z using own variance;
remove Z magnitude hurdle (abs(Z)>0 instead of >=1.25); remove target only (tgt_f=None, stop unchanged).
Use original source's 09:00 CT decision, 09:01 close-labelled entry bar open, 15:00 close flatten, stop0.6range,
target1.0range and source target-touch convention. The own-momentum comparator necessarily changes the
variance normalizer as part of removing ES; it is not a pure date filter. No entry-bar fill-policy repair here.

**Late-Day Flow (4 cases):** original K0.4, stop0.25ATR, signal14:00, exit14:30; remove large-move hurdle
(K0, skip exactly zero direction); remove stop (stop=1e6ATR, no target exists to accidentally change);
remove early exit (hold to15:00, same entry/stop). Prior15weekday ATR uses existing full-day Grid24 method.
Do not use stop0 as "no stop": that would immediately stop every trade. Verify huge-stop case has no stop exits.

## Timing, data and implementation gates

Source functions are AST-extracted into controlled namespaces, not imported with their top-level cache or
backtest code. Input adapters reproduce their grid/alignment conventions; no market paths invented for speed.
Warm-up2017; first phase2018-01-01–2022-12-30. Only after saving that phase and checking the gates may
the unchanged 13 definitions be run once on already-seen2023-01-01–2026-10-09. This is descriptive historical
replication for an existing strategy, not a held-out promotion test. No selection from either phase.

Verify raw Git blobs against source snapshot fe35af99aa90d7f31b91f8693859251bb44dd9ab; record all hashes.
Temporary symlink-only input subsets feed pinned Grid24; no persistent full-grid cache. Design reads no2023+
minute files. Namespace has one explicit NQ point value20, tick0.25, commission7.25. Native micro cost bridge
uses1.25round-trip commission plus source slippage /10; no ES execution or inherited ES multiplier issue.
Capture missing raw held minutes. RS inherits source forward-fill policy; report counts before filling and
do not claim native fill parity where a held path is unknown. No deletion chosen from returns.
Gate before recent phase: all baselines nonempty; source-like long/short quantities valid; each daily series
sums to trade net within a cent; target/stop cost and intervention identities correct; any unknown price entry/
exit aborts. Missing intratrade quotes flag scope limitations rather than certify a native adverse path.
The engine is not a new native roll ledger; all positions intraday, so no carrying continuous roll jumps.

## Measurements and falsifiers

Use metrics.perf and resampling.max_dd; initial zero-P&L peak included for DD/Calmar. Whole, long, short,
each year and each phase: trades, total/gross/costs, mean, win rate, t, Sharpe, Sortino, PF, Calmar, Ulcer,
max daily DD, worst trade/native MNQ, and full-calendar delta versus original. Mean/trade alone never decides.
Compute paired 20-session moving-block bootstrap (1000, seed20261108) of original-minus-ablation daily P&L;
retain annual-effect5/95%interval. This is conditional uncertainty on chosen history, no correction for all
earlier source selections and no claim of a newly proven causal mechanism.

Pure filter tests: DT band, RS Z hurdle and LDF large-move hurdle. Match common trade date/side/entry/exit;
if these differ, report changed opportunities rather than incorrectly call every difference "removed trades".
Report removed-trade mean/t and total; 1000 within-year random drops, same retained trade count each year,
compare original total and dailyDD with random subsets. Resampling controls are not chosen strategy variants.
ES-removal, distance/timing and exit changes are paired-calendar strategy interventions, not nested filters.

Call a profit contribution historically persistent only if original-minus-ablation total is positive in both
periods; call evidence stronger only if paired intervals exclude zero, while retaining prior-selection limits.
Call an ingredient primarily risk control when removing it worsens drawdown/tail outcomes without reliable
profit gain. Mixed signs/uncertain intervals -> conditional or inconclusive, never "decoration" or "proven".
Do not automatically change a rule based on either label. All results, including negative ablations, retained.

No economic pass/fail promotion is sought here. Any future proposed rule change needs a separate trial,
parity/independent review and then actual current-book BASE/ADD/REPLACE/EMPTY tests at integer sizes.
Do not run account simulations, parameter search or write live/MultiCharts changes as part of this task.
No scout/schedule changes, external messages, paid data, VPS, broker or API-key access.

Pre-return engineering correction: first attempt stopped while constructing the in-memory grid because the
AST namespace omitted the source's NMIN24=1440 constant. Bind that exact source constant; no data, rule,
cost, hypothesis or outcomes changed. No strategy function had run when the NameError occurred.
Second engineering attempt reached RS calendar loading but its namespace lacked the source regex module.
Supply re explicitly. DT cases had run in memory; no economic summaries were written or inspected. Their
replay is the same definitions, not a new parameter trial. Preserve both execution failures in the final record.
