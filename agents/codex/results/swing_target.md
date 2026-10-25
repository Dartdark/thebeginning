# Swing Target NQ: WATCH for personal research; REJECT as supplied for Apex

Summary: Broad economics reproduce:602 trades, PF1.62 CODE /1.70 CODE_BE; both eras and all9 years positive after repo costs.
The author's matching window gives591 trades rather than584; exact MultiCharts parity is unverified.
At1MNQ,2023+ personal-full addition adds mean annual $2,484/$2,743, with DD95 increases $461/$170; replacement evidence is inconclusive.
Both source versions carry3 holiday trades across dates, so neither belongs on50K/150K evaluation/funded as supplied.
It diversifies the existing book but loses on book-loss days. No new filter, ranking, live change or deployment follows.

Plan: [`swing_target.md`](../plans/swing_target.md), **a4064ac**, committed before real returns. Two fixed economic models; no optimization.
Source: `agents/codex/inputs/swing_target/Swing_Target_NQ.txt`, preserved byte-for-byte. User authorized both BE/no-BE and unknown-template full-session proxy.
Scripts: `analysis/codex_swing_target.py`, `codex_swing_engine.py`, `codex_swing_diagnostics.py`, `codex_swing_accounts.py`, `codex_swing_report.py`.
Outputs: `analysis/outputs/codex_swing_target/`. Current plan source pinned at **62e82a0**; existing caches reused without rebuilding.

## Rule, source/prose differences and execution

CODE follows the uploaded defaults: previous2 stored RTH highs/lows; prior20 stored-session average range; .35 target/.70 stop;
inside opening boundaries, disarm on strict break through08:45; one trade/day. CODE_BE adds only causal entry-price BE after+.30 range.
The file has **no BE rule**; CODE_BE isolates that missing rule and leaves the other source/prose discrepancies visible.
1-minute CT close stamps:08:45 decision=>08:46-labeled entry bar; inclusive14:29 decision permits14:30 entry;
14:59 exit decision fills next bar open, normally the15:00-labeled bar (14:59 wall time), not the cash-close price.
No source rewrite, holiday repair, side-specific setting or fitted regime filter was added.

Use the nearer-extreme OHLC path, worse-open stop gaps and one-point target-through, with entry-bar protection and post-entry-only MAE.
Both resting entries cancel after first fill. A fixed opposite-path stress checks intrabar ambiguity. Price distances are unrounded,
as in the repo engine; tick rounding, true tick paths, limit queues, the author's session template and MNQ prices remain unverified.
The new engine extends the shared market-entry simulator for paired stop entries and causal BE. Independent source/engine review and
synthetic long/short, BE, gap, timing and missing-close checks pass; this is not an independent full-data replica or MC parity pass.
Review: [`swing_target_engine_review.md`](swing_target_engine_review.md).

History: cached2017-12-01–2026-10-09; source history initializes before2018. Run2018–22 before2023+ for both fixed versions.
2023+ was already examined by the author, whose header says many start times were inspected in both eras; prior trial count is unknown.
This is historical replication, not fresh holdout. The declared15-minute rule is not preregistered economic discovery.

## Standalone results

NQ tables pay$7.25 RT plus1 tick at stop entry and stop/BE/time exit; target exits no extra slip.
Native MNQ uses$1.24 RT plus$.50 per market/stop fill, with$1.04 sensitivity. Never divide NQ commission by10.
All/long/short tables include verified strategy-no-trade days, realized P&L on actual exit dates and initial zero for DD.
Ulcer uses the repo's$50,000 reference. Every side/year and trade/EOD DD remain in `metrics.csv`.

| Model | Period | Side | Trades | Win | Net/trade NQ | t | Sharpe | Sortino | PF | Calmar | Ulcer | EOD DD/NQ |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CODE | 2018-22 | all | 340 | 63.8% | $270.99 | 3.46 | 1.51 | 2.14 | 1.62 | 1.98 | 3.37 | $9,104.93 |
| CODE | 2018-22 | long | 179 | 59.2% | $136.41 | 1.39 | 0.61 | 0.83 | 1.32 | 0.58 | 4.70 | $8,273.41 |
| CODE | 2018-22 | short | 161 | 68.9% | $420.62 | 3.41 | 1.47 | 2.16 | 1.94 | 1.21 | 4.57 | $10,902.13 |
| CODE | 2023+ | all | 262 | 64.1% | $394.32 | 3.17 | 1.59 | 2.26 | 1.62 | 1.37 | 4.47 | $19,526.27 |
| CODE | 2023+ | long | 143 | 61.5% | $243.20 | 1.53 | 0.77 | 1.04 | 1.40 | 0.50 | 5.59 | $18,036.77 |
| CODE | 2023+ | short | 119 | 67.2% | $575.91 | 2.95 | 1.46 | 2.19 | 1.86 | 1.16 | 5.99 | $15,265.86 |
| CODE | all | all | 602 | 64.0% | $324.67 | 4.65 | 1.53 | 2.17 | 1.62 | 1.11 | 3.02 | $19,526.27 |
| CODE | all | long | 322 | 60.2% | $183.84 | 2.06 | 0.69 | 0.92 | 1.36 | 0.37 | 4.57 | $18,036.77 |
| CODE | all | short | 280 | 68.2% | $486.62 | 4.46 | 1.45 | 2.15 | 1.90 | 0.99 | 4.08 | $15,265.86 |
| CODE_BE | 2018-22 | all | 340 | 60.6% | $253.32 | 3.34 | 1.46 | 2.07 | 1.61 | 1.70 | 3.83 | $9,911.08 |
| CODE_BE | 2018-22 | long | 179 | 56.4% | $150.80 | 1.61 | 0.71 | 0.99 | 1.39 | 0.64 | 4.54 | $8,273.41 |
| CODE_BE | 2018-22 | short | 161 | 65.2% | $367.29 | 3.03 | 1.31 | 1.89 | 1.82 | 0.95 | 4.99 | $12,100.36 |
| CODE_BE | 2023+ | all | 262 | 61.1% | $431.50 | 3.74 | 1.87 | 2.73 | 1.80 | 2.03 | 3.74 | $14,430.80 |
| CODE_BE | 2023+ | long | 143 | 60.1% | $309.55 | 2.08 | 1.05 | 1.46 | 1.59 | 0.79 | 4.12 | $14,433.05 |
| CODE_BE | 2023+ | short | 119 | 62.2% | $578.05 | 3.20 | 1.57 | 2.45 | 2.02 | 1.27 | 5.47 | $14,025.86 |
| CODE_BE | all | all | 602 | 60.8% | $330.87 | 5.01 | 1.65 | 2.38 | 1.70 | 1.54 | 3.18 | $14,430.80 |
| CODE_BE | all | long | 322 | 58.1% | $221.30 | 2.63 | 0.87 | 1.21 | 1.50 | 0.55 | 4.05 | $14,433.05 |
| CODE_BE | all | short | 280 | 63.9% | $456.86 | 4.40 | 1.43 | 2.15 | 1.92 | 1.02 | 4.29 | $14,025.86 |

| Model | Year | Trades | Win | Net/1MNQ | PF/NQ costs |
| --- | --- | --- | --- | --- | --- |
| CODE | 2018 | 62 | 64.5% | $1,386.29 | 2.10 |
| CODE | 2019 | 61 | 62.3% | $656.84 | 1.53 |
| CODE | 2020 | 68 | 63.2% | $1,016.52 | 1.29 |
| CODE | 2021 | 71 | 67.6% | $1,700.17 | 1.52 |
| CODE | 2022 | 78 | 61.5% | $4,278.85 | 1.83 |
| CODE | 2023 | 79 | 65.8% | $2,270.65 | 1.64 |
| CODE | 2024 | 68 | 61.8% | $2,751.81 | 1.81 |
| CODE | 2025 | 61 | 67.2% | $2,704.95 | 1.63 |
| CODE | 2026 | 54 | 61.1% | $2,468.75 | 1.47 |
| CODE_BE | 2018 | 62 | 62.9% | $1,381.79 | 2.09 |
| CODE_BE | 2019 | 61 | 59.0% | $627.83 | 1.53 |
| CODE_BE | 2020 | 68 | 58.8% | $704.09 | 1.21 |
| CODE_BE | 2021 | 71 | 63.4% | $1,393.20 | 1.42 |
| CODE_BE | 2022 | 78 | 59.0% | $4,330.72 | 1.95 |
| CODE_BE | 2023 | 79 | 63.3% | $2,385.81 | 1.74 |
| CODE_BE | 2024 | 68 | 60.3% | $2,709.81 | 1.79 |
| CODE_BE | 2025 | 61 | 63.9% | $2,916.25 | 1.81 |
| CODE_BE | 2026 | 54 | 55.6% | $3,158.56 | 1.84 |

2026 is throughOctober9. At native costs, the full-history one-micro risk/return scale is:

| Model | Annualized net/1MNQ | Closed-trade DD/1MNQ | Worst open MAE/1MNQ |
| --- | --- | --- | --- |
| CODE | $2,141.93 | $1,956.23 | $660.50 |
| CODE_BE | $2,183.49 | $1,444.63 | $660.50 |

Wide nominal stops do not equal the average realized loss: most trades exit by target/time, and the added BE trims some tails.
This explains why Swing's realized win/loss mix can differ from Vault Break's fixed40/75 payoff. It does not ensure smooth future equity.

## Author's February2018–July2026 claims

The user's claim is584 trades,62% wins, PF1.79,$129 average win/$117 average loss,$1,442 DD,$660 worst MAE;
exits262 target/245 EOD/46 stop/31 BE. On that same calendar slice:

| Model | Trades | Native win | Native PF | Avg win/1MNQ | Avg loss/1MNQ | DD/1MNQ | Targets | Time | Stops | BE |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CODE | 591 | 64.3% | 1.69 | $131.58 | $140.40 | $1,444.63 | 278 | 263 | 50 | 0 |
| CODE_BE | 591 | 61.1% | 1.73 | $130.80 | $118.92 | $1,444.63 | 262 | 249 | 47 | 33 |

Our BE version reproduces the262 target count and broadly similar payoff/DD shape, but seven extra trades and differing exits remain.
At native fees, its worst month is-$756.65,
68.6% of months are positive, average open MAE is
$110.51/MNQ and median hold132 minutes.
No author MC export was supplied, so the claimed571/584 matching days cannot be checked; no fake trade match or exact reproduction claim.
Author$1 zero-slippage cost totals and our native costs are kept separate in `author_window_comparison.csv` and the ledgers.

## Uncertainty, nulls and execution stress

2023+5,000-run10-session block-bootstrap90% intervals (PF here is daily PF):

| Model | Metric | Actual | 90% interval |
| --- | --- | --- | --- |
| CODE | sharpe | 1.59 | 0.61 to 2.57 |
| CODE | sortino | 2.26 | 0.80 to 4.03 |
| CODE | pf_day | 1.62 | 1.20 to 2.18 |
| CODE | max_dd | 19526.27 | 11,864.71 to 35,934.22 |
| CODE_BE | sharpe | 1.87 | 0.91 to 2.81 |
| CODE_BE | sortino | 2.73 | 1.22 to 4.60 |
| CODE_BE | pf_day | 1.80 | 1.33 to 2.44 |
| CODE_BE | max_dd | 14430.80 | 9,974.21 to 29,128.76 |

The initial-zero wrapper reuses repo block paths/statistics and prepends the bookkeeping zero to every path; it does not resample it as a market day.
Permutation and10,000-trade-bootstrap outputs are saved, plus full/validation and all/long/short statistics.
The latest pinned ranked-item count is324; plus2 gives326,
t bar3.61. CODE full t4.65/DSR0.941; CODE_BE t5.01/DSR0.970.
The local older tier list had274 items; significance was refreshed from the pinned62e82a0 list before publication, without changing returns or selecting parameters.
This ranked-item count is a lower bound on all historical searches; previous VB bracket trials and unknown author filters/timing searches remain disclosed.
No side is promoted or dropped from its isolated result; short-side strength does not authorize a newly selected short-only strategy.

| Model | Null | Actual net/trade NQ | Null mean | Null >=actual |
| --- | --- | --- | --- | --- |
| CODE | random_time | $324.67 | $467.90 | 100.0% |
| CODE | random_side | $324.67 | -$0.22 | 0.2% |
| CODE_BE | random_time | $330.87 | $461.56 | 99.8% |
| CODE_BE | random_side | $330.87 | -$16.32 | 0.2% |

All500 runs/family/model closed, with exact signal-count checks. Random direction at the selected time is weaker (p≈.002).
The random-time benchmark retains the **later revealed breakout direction and selected trade day**; entries before that information was
known use hindsight. It beats the actual entry but is not an executable alternative or a causal test of entry timing.
We therefore do not claim a clean entry-time placebo pass, or that the15-minute filter adds edge. No after-the-fact replacement null was searched.

| Model | Fixed execution stress | 2023+ net/NQ | PF |
| --- | --- | --- | --- |
| CODE | opposite_minute_path | $103,310.95 | 1.62 |
| CODE | extra_tick | $101,305.95 | 1.60 |
| CODE_BE | opposite_minute_path | $113,053.64 | 1.80 |
| CODE_BE | extra_tick | $111,013.64 | 1.78 |

Opposite-path and extra-tick results remain profitable; these are execution scenarios, not extra economic models or selected parameters.
Standalone252-session EOD-trail illustrations at1MNQ have2023+ hit frequencies10.8% CODE /5.3% CODE_BE and DD95$2,527/$2,133.
They omit intraday account breaches/portfolio rules and do not override the actual Apex source incompatibility.

## Account placement and session failure

| Model | Entry date | Entry label | Exit date | Exit label | Exit |
| --- | --- | --- | --- | --- | --- |
| CODE | 2018-05-28 | 09:33 | 2018-05-29 | 02:47 | stop |
| CODE | 2022-06-20 | 10:27 | 2022-06-21 | 02:32 | target |
| CODE | 2023-07-03 | 08:48 | 2023-07-05 | 15:00 | time |
| CODE_BE | 2018-05-28 | 09:33 | 2018-05-29 | 02:47 | stop |
| CODE_BE | 2022-06-20 | 10:27 | 2022-06-21 | 02:32 | target |
| CODE_BE | 2023-07-03 | 08:48 | 2023-07-05 | 15:00 | time |

Exact15:00 range storage/termination and14:59 exit submission miss holiday/shortened sessions. All1,201 unobserved held minutes
occur on these three spans; they overlap scheduled closures and must not be called1,201 lost-feed minutes. No ordinary intraday trade
has an unobserved held minute. We retain these trades; deleting them or repairing them after results would change the strategy.

| Requested plan | As-supplied conclusion, both models |
| --- | --- |
| 50K evaluation | REJECT as supplied:3 source flat/session violations; no invalid account backtest |
| 150K evaluation | Same concrete source violation; cannot infer legality/survivability from larger drawdown limit |
| 50K funded | REJECT as supplied; no payout recommendation |
| 150K funded | REJECT as supplied; no payout recommendation |
| Personal A–D / full18 | Positive historical addition, higher drawdown; WATCH pending parity, independent replication and forward evidence |

All eight model/Apex-context limits are saved in `apex_operational_limits.json`. No hypothetical holiday-safe strategy was fitted.

## Current personal portfolio: addition, VB replacement and empty slot

Current18 legs/starter ladders are pinned to62e82a0, including OT and newer Kusho/S47/S30/BB_MRM. The baseline separately reproduces
the published1.275-fee annual$38,004 and$5,803 DD before the frozen native-fee repricing. Candidate is1MNQ at the book's common leg scale.
Retain all trades, including observed16:00 marks across carries; no equity is backdated to entry day. Use1,000 paired252-session paths,
10-day blocks. Below is **2023+ source pool**, mean annual addition and **95% historical annual-mean interval** (different from90% above):

| Model | Ladder/full addition | Mean annual increment | 95% historical mean CI | Change in DD95 |
| --- | --- | --- | --- | --- |
| CODE | A__ADD | $2,483.97 | [$677.80, $4,494.37] | $872.79 |
| CODE | B__ADD | $2,483.97 | [$677.80, $4,494.37] | $906.65 |
| CODE | C__ADD | $2,483.97 | [$677.80, $4,494.37] | $808.31 |
| CODE | D__ADD | $2,483.97 | [$677.80, $4,494.37] | $829.99 |
| CODE | FULL__ADD | $2,483.97 | [$677.80, $4,494.37] | $461.30 |
| CODE_BE | A__ADD | $2,742.56 | [$1,157.26, $4,538.64] | $557.47 |
| CODE_BE | B__ADD | $2,742.56 | [$1,157.26, $4,538.64] | $609.93 |
| CODE_BE | C__ADD | $2,742.56 | [$1,157.26, $4,538.64] | $437.55 |
| CODE_BE | D__ADD | $2,742.56 | [$1,157.26, $4,538.64] | $490.43 |
| CODE_BE | FULL__ADD | $2,742.56 | [$1,157.26, $4,538.64] | $170.38 |

For FULL, VB replacement adds only about$267/$525 mean annual and its historical intervals cross zero. The empty-VB control is included;
there is no reliable evidence to replace VB. Exact BASE/ADD/EMPTY/REPLACE tables and full/year statistics are saved per model/fee.
Starter-ladder drawdown increases are materially larger than FULL, so a FULL benefit is not a blanket small-account recommendation.

| Model | Full-book daily corr | Joint losing days | Candidate net on full-book loss days |
| --- | --- | --- | --- |
| CODE | 0.20 | 135 | -$5,824.44 |
| CODE_BE | 0.20 | 141 | -$5,203.75 |

Correlation≈.20 does not make it a hedge. It adds NQ breakout exposure and is negative in aggregate when the current book loses.
Author correlations with Twin/ORB/RelStr/Kusho/KOS10/VWAP/Midday are not all reproducible from the supplied material; our table is our current book.
For a hedge, require positive conditional P&L and timely offsets on book-failure paths, not just low unconditional correlation.
Research directions are a genuinely different risk driver (non-equity scheduled flow) or a separately preregistered failed-breakout reversal;
neither is an established edge here. Avoid adding another overlapping breakout merely because its average correlation is low.

Personal caveats: published fee/day approximations undercount some reentries; MOC/S30 booking approximations and the existing Twin v1-marked
ledger remain. Current OT source endsJuly7,2026; post-source zero columns are missing baseline evidence, not verified no-trade activity.
Thus portfolio conclusions are conditional historical comparisons, not complete current execution/margin/liquidation evidence.
The inherited funded OT whole-night adverse approximation is documented but no Apex performance conclusion was taken from it.

## Decision and next evidence

The strategy merits further personal research; its broad edge is not explained by a high win rate alone. No regime filter or alternative
price stop was optimized. The Howard [primary abstract](https://ssrn.com/abstract=6350238) concerns ES volume-profile breakout events,
January2025–January2026 and a first30-minute effect; it does not validate this NQ prior2day level or15-minute cutoff, nor establish0DTE causation.
Full paper returned403, with no bypass. Wide/open risk can be reduced in dollars by size and portfolio risk budgets, but any exit/filter
change needs a frozen test of return lost versus risk saved. The described BE is already compared here; it improves the later risk shape
without proving optimality. Exact platform parity and a known session/holiday definition are the cheapest next evidence.

The user-requested Vault Break rerun is now an unchecked item in `TODO.md`. No live chart, VPS, broker/API setting, shared cache,
ranking or allocation was changed. Data, code, trial logs and source hashes are saved for Claude's independent review.

Reproduce from repo root using the installed scientific interpreter recorded in the manifest:

```powershell
$swingPython = 'C:\Users\dmoto\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $swingPython -B analysis/codex_swing_target.py --phase design
& $swingPython -B analysis/codex_swing_target.py --phase validation
& $swingPython -B analysis/codex_swing_diagnostics.py
foreach ($swingModel in 'CODE','CODE_BE') {
  foreach ($swingFee in '1.24','1.04') {
    & $swingPython -B analysis/codex_swing_accounts.py --personal --ledger "analysis/outputs/codex_swing_target/${swingModel}_trades.csv" --prereg a4064ac --fee $swingFee
  }
}
& $swingPython -B analysis/codex_swing_report.py
```

Claude review path: `agents/codex/results/swing_target.md`.
