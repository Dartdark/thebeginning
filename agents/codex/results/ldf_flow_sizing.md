# LDF flow sizing: REJECT — no incremental sizing edge in the design screen
Summary: Tested the frozen 1/2/3 MNQ asset/liquidity sizing rule against existing 2 MNQ LDF; design fails.
454 trades from 2018-05-02 through 2022; 38 earlier original trades excluded for registered input warmup.
Incremental net +$388, HAC t 0.30; momentum-adjusted high-minus-low -$54/NQ, t -0.49; placebo p 0.447.
Mandatory D-2 stress also fails; no 2023+ candidate test, funded simulation, parameter rescue or forward log.
Keep the existing LDF sizing unchanged; this result rejects the upgrade, not LDF or the existence of ETF reset flows.

Plan: `agents/codex/plans/ldf_flow_sizing.md`, initial `383014a`, final pre-return amendment **c0b46ed**.

Script: `analysis/codex_ldf_flow_sizing.py` (c0b46ed); report reconciliation: `analysis/codex_ldf_flow_sizing_report.py`.

Output: `analysis/outputs/codex_ldf_flow_sizing/`. Input checkpoint committed **cd2e43e** before outcomes.

Trials: **1 hypothesis, 2 nonbaseline configurations evaluated (R and mandatory S)**; baseline B is a control.
Addition A, empty-slot account E, 2023+ and funded bench were not evaluated because design failed.

## Rule (as tested)

All accepted LDF entries in the registered window, regardless of roster occupancy. No entry/exit/side/stop changes.
`K = 6*TQQQ_assets + 12*SQQQ_assets + 2*QLD_assets + 6*QID_assets`, using the previous cash-session row.
Divide reset notional per fixed 1% move by the trailing 20 completed regular sessions' median NQ last-hour
notional. Rank against the preceding 252 cash sessions, at least 126 observations; low/middle/high gets
1/2/3 MNQ, versus baseline 2. Mandatory stress uses second-prior-session assets. Unavailable joint inputs
stay at 2 MNQ; 3 evaluated trades use that fallback. The fixed-size screen applies no cushion scaling.

Gate-4 controls include absolute RTH return, move/ATR, lagged ATR/price, trailing 63/252 cash-session NQ returns,
side and year. Gate-5 sizes are shuffled within year x side x move/ATR tercile x trailing-63-return tercile.
D-1 plus D-2 stress is accepted for this **exploratory** historical snapshot screen, not proven vintage availability.

The user export at `35b92cf` has 74,717 bars, 2017-05-01 to 2017-12-29, 08:00-15:15 CT, no duplicate keys;
its hash is frozen in the plan. Since it is a partial year, the 252-session control makes the first joint-input
date **2018-05-02**. This input-driven start was registered before outcomes, excluding 38 of the original 492
design entries. No P&L was evaluated for those 38; no alternative start or full-January-2017 data was assumed.

## Results

**Return-free checkpoint first.** Of 454 evaluation trades, 451 have all joint inputs (99.3%); primary groups
contain 192 high, 118 low and 141 middle, represented in all five evaluated years. With the assumed $810 SD,
the pre-return high/low t~2 planning hurdle is $189.50/NQ. Pearson correlations of rank with 63/252-session
momentum are 0.322/0.189 on these entries (Spearman 0.362/0.235). On eligible cash sessions, Pearson is
0.348/0.188. These were saved and committed before any LDF return computation.

Covered-entry flow groups, net per full NQ after $17.25 costs:

| Version/group | Trades | Mean net/NQ | Trade SD/NQ |
|---|---:|---:|---:|
| R high | 192 | $74.73 | $544 |
| R middle | 141 | $43.39 | $607 |
| R low | 118 | $88.72 | $769 |
| S high | 193 | $68.55 | $542 |
| S middle | 139 | $51.74 | $620 |
| S low | 119 | $88.34 | $759 |

The covered high-flow trades do not outperform low-flow trades. The saved raw-label group file also includes
the 3 joint-input fallbacks; use `design_covered_flow_groups.csv` for comparison with the regression population.

Whole/long/short results at fixed planned MNQ sizes. Mean/NQ-equivalent divides total net by contract-round-trip
exposure in full-NQ equivalents; it is a weighted per-contract average. Trade t uses actual sized trade P&L.

| Version/side | Trades | Win | Mean $/trade | Mean/NQ-equiv | Trade t | Total net |
|---|---:|---:|---:|---:|---:|---:|
| B all | 454 | 53.5% | $15.21 | $76.03 | 2.52 | $6,903.70 |
| B long | 247 | 55.1% | $14.16 | $70.81 | 2.02 | $3,497.85 |
| B short | 207 | 51.7% | $16.45 | $82.27 | 1.60 | $3,405.85 |
| R all | 454 | 53.5% | $16.06 | $74.25 | 2.53 | $7,291.55 |
| R long | 247 | 55.1% | $15.90 | $72.72 | 2.15 | $3,927.00 |
| R short | 207 | 51.7% | $16.25 | $76.12 | 1.51 | $3,364.55 |
| S all | 454 | 53.5% | $15.81 | $73.07 | 2.49 | $7,175.55 |
| S long | 247 | 55.1% | $17.07 | $78.22 | 2.30 | $4,216.23 |
| S short | 207 | 51.7% | $14.30 | $66.80 | 1.33 | $2,959.33 |

| Version/side | Sharpe | Sortino | PF | Calmar | Ulcer | Max DD |
|---|---:|---:|---:|---:|---:|---:|
| B all | 1.15 | 1.92 | 1.42 | 0.48 | 2.24 | $3,028 |
| B long | 0.92 | 1.50 | 1.48 | 0.51 | 1.11 | $1,422 |
| B short | 0.73 | 1.25 | 1.37 | 0.44 | 1.46 | $1,618 |
| R all | 1.16 | 1.98 | 1.44 | 0.61 | 1.84 | $2,518 |
| R long | 0.98 | 1.79 | 1.55 | 0.62 | 0.88 | $1,321 |
| R short | 0.69 | 1.14 | 1.36 | 0.49 | 1.23 | $1,451 |
| S all | 1.14 | 1.93 | 1.43 | 0.61 | 1.88 | $2,470 |
| S long | 1.04 | 1.95 | 1.60 | 0.72 | 0.84 | $1,232 |
| S short | 0.61 | 0.98 | 1.31 | 0.43 | 1.27 | $1,430 |

Annual fixed-size net; 2018 begins May 2. Full standard metrics by year and side are in `design_standard_metrics.csv`.

| Year | Baseline B | Primary R | R minus B | Stress S minus B |
|---|---:|---:|---:|---:|
| 2018 partial | $1,283 | $597 | -$686 | -$819 |
| 2019 | -$1,337 | -$1,361 | -$24 | -$19 |
| 2020 | -$244 | $586 | +$830 | +$724 |
| 2021 | $2,361 | $3,302 | +$941 | +$983 |
| 2022 | $4,841 | $4,168 | -$673 | -$597 |

The primary uses 982 contract round trips versus baseline 908, **8.15% more exposure**. Its higher total net is
not evidence of better allocation: weighted net per NQ-equivalent falls from $76.03 to $74.25, the incremental
daily HAC t is only 0.30, and only 2/5 years improve. The existing line's positive standalone t does not validate sizing.

## Placebos, gates and account level

| Registered gate | Result | Evidence |
|---|---|---|
| G1 support | PASS | 99.3% joint coverage; 192 high / 118 low; every evaluated year represented |
| G2 net/cost/years | PASS | R net $7,292; gross $91.50/NQ-equiv > $25.875 hurdle; 4/5 years positive |
| G3 incremental edge | FAIL | +$387.85; daily HAC t 0.297; only 2/5 years improve; bootstrap lower bound <0 |
| G4 momentum-adjusted contrast | FAIL | High-minus-low -$54.01/NQ, SE $111.33, t -0.485 |
| G5 matched sizing placebo | FAIL | One-sided plus-one p 0.447, required <=.05 |
| G6 two-session stress | FAIL | +$271.85 total, but adjusted contrast -$63.48/NQ, t -0.579 |

The 5,000-replicate, 20-day paired design bootstrap puts incremental annualized net at $81, with a 90% interval
**-$424 to +$603**. This is fixed-size strategy P&L, not funded-account payouts. Gate-4 regression has full rank
(13 columns, 451 observations; condition number 11.29). Its lag-5 HAC contrast is not a significance pass.

The 2,000 matched permutations preserve each cell's size counts and the fallback quantities. Of 89 cells,
69 permit actual size rearrangement, covering 377 entries; sparse cells are not pooled after outcomes.
Primary max DD $2,518 is below shuffled median $2,611, but profit does not beat the matched null.
No random-time/side test is substituted for the preregistered sizing placebo on the established LDF entries.

**Stop rule applied.** No 2023+ candidate features/returns, Monte Carlo, funded addition/replacement/empty-slot
simulations, optional mechanism study, size-map rescue, reversed rule or forward log. No new holding strategy
or live decision follows this rejection. Standalone fixed-size DD is not a funded account blow-up estimate.

## What could make this wrong

Historical issuer publication times and revisions remain unverified. D-1/D-2 lags are exploratory assumptions;
same-day fund capital flows and actual remaining hedge orders are still unseen. A null sizing result does not
establish whether daily resets contribute to market movements or explain the existing LDF edge.

The warmup is partial and the test excludes 38 earlier trades. Continuous NQ close ratios are unadjusted
trend controls, not investable roll-adjusted returns. Lagged volume normalization and calendar-year controls
cannot remove every regime confounder. The covered high/low contrast has limited power and sparse within-year
support (e.g. only 6 covered low entries in 2021); no pooling or change of specification was used to rescue it.

Roll-window volume check: 79 usable Thursday/Friday window rows, minimum 19,816 last-hour contracts;
minimum notional/lagged-expected ratio 0.354. Three earlier 2017 rows precede the supplied export and are
unavailable, not zero-filled. This check finds no near-zero valid roll-window denominator.

Dated byte-preserved fund copies are archived with SHA256, UTC storage time and source-commit provenance.
They are copies of Claude's supplied issuer files, **not independent fresh issuer retrievals**. Direct issuer
access was blocked by this environment's HTTP proxy (403). Future forward records would need actual received
files/timestamps; archival storage now cannot prove historical publication timing.

## Differences between MultiCharts code and the test

No new MultiCharts code. Existing MC entry/exit mapping is reused on a date-filtered temporary workbook;
the accepted loader never receives 2023+ trades. Existing `with_slippage` applies two ticks once, plus $7.25
commission = $17.25/NQ round trip. The existing cache is restricted to dates through 2022, with the new raw
2017 file used only for feature warmup. No cache rebuild or shared strategy/data/live-file edit.
MNQ costs use the proportional research convention; this is not an independently verified micro fee schedule.

## Reproduction and verification

Configured Python: `/workspace/venvs/thebeginning/bin/python`; required dependencies verified.
The original two phases were `analysis/codex_ldf_flow_sizing.py inputs` then `design`, with checkpoint commit
cd2e43e between them. The single-run guard prevents silently rerunning an existing design decision.
For an independent reproduction, import the module, set `OUT` to a fresh allowed output directory, then call
`inputs()` and `design()` with the same pinned blobs/cache. Do not delete or overwrite the original evidence.
`analysis/codex_ldf_flow_sizing_report.py` reconciles saved outputs only and does not rerun outcomes or tests.
Arithmetic/date/fallback checks pass; all candidate outcomes end by 2022-12-29. Synthetic rank, covariance and
2023-exclusion checks passed before outcomes. Calendar-only all-NaN ATR warnings occur on empty cache dates;
all evaluated regression inputs are explicitly checked finite.

Tell Claude: review `agents/codex/results/ldf_flow_sizing.md` — REJECT at design; incremental t 0.30,
momentum-adjusted contrast -$54/NQ, placebo p 0.447; 2023+ and funded bench not run. Existing LDF unchanged.
