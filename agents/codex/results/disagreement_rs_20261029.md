# Prior-month disagreement / RS longs: REJECT this frozen filter

Summary: Actual2018–22 design filter test completed. Base330RS longs earn7,196.30USD/MNQ;
filter keeps192 for3,704.42 and removes138profitable trades worth3,491.88. Drawdown only
falls58USD. Matched randomprofitp=.586/DDp=.863; no filter edge.42unknown-state longs were
retained unchanged. No2023+returns, personalnumericbookbench or filter tuning after failure.

Evidence: ../evidence/disagreement_rs_20261029.md. Plan:
../plans/disagreement_rs_20261029.md, committedb091f9c BEFORE returns; implementationb64da5f.
Warm-up source correction6442e0d before first financial execution; original failed-launch
console retained. Script: analysis/codex_disagreement_rs.py; report:
analysis/codex_disagreement_rs_report.py. Outputs:
analysis/outputs/codex_disagreement_rs_20261029/run_v1/. Trials1primary+2diagnosticcontrols,
plus retained1000matched paths/5000monthlybootstrap draws, not erased prior family looks.

## Four source-paper questions

About: cross-sectional stock returns and monthly absolute overnight/day returns normalized
by monthly close-return SD. Finds: author EWspread1.177%/month,t7.46, much weaker VW/post2000.
Why money: information uncertainty risk compensation is proposed, not established NQ demand.
Build on it: the authorized NQmonthlyfilter transfer is now tested and rejected in this
one frozen form. This is not a replication or rejection of the paper's stock universe.

## Frozen rule, parent and execution boundary

Only LONGS of the existing adopted RelativeStrength NQ/ES MultiCharts ledger are filtered;
all281design shorts unchanged. At the RS decision, keep long if previous complete calendar
month's mean(|overnight|+|intraday|)/SD(close-to-close,ddof1) >=median of the SIX earlier
monthly scores, excluding the feature month. Whole unknown months/thresholds retain the
base trade, not drop a loss.288known-feature longs/42unknown-retained. No inverted threshold,
side/size search or after-result nomination of the volatility control.

Features: NQ08:31labelledOPEN, actual15:00CLOSE or12:00earlycashCLOSE; previous scheduled
cash session's actual close; no price forward/backward fill. Every scheduled day in the
featuremonth must have valid endpoints/priorclose,>=10days. Six known preceding months
required.2017existingDAYwarmup startsMay1; unavailable earliermonths remain unknown.
No2017rootfile was fabricated; first launch failed before prices/returns. The existing
ob_v2_bench2017source was chosen on date/time coverage alone, not return performance.

Immutable MultiCharts source for2018–22, date-first rawXML reader:2023+rows inspected only
for date metadata; future financial values converted0. Costs recomputed1MNQ:1.24RTcommission,
.50entrytick and.50nonlimitexit; zero limit slippage. Price×side gross reconciles to reported
percontract gross/10 for every design trade. Native-fee costing is a model on NQprice paths,
including pre-MNQ-listing2018, not an authenticated historical micro fill.

This measures incremental filtering on an adopted execution ledger, not a new raw-spec
rebuild. Parent entry-bar protection and originaltarget/fill limitations remain; not silently
certified as active-entry-bar execution. Source PL blob matches connected Claude source:
5c7f16c3c93b71877b03a38a2b5b219343169133. Promotion would still require protected raw-spec
checking. Failure means no need to claim a new executable edge from these conditional ledgers.

## Results at1MNQ,2018–22

| model | keptlongs | netUSD | trade t | dailyclosedDDUSD |
| --- | ---: | ---: | ---: | ---: |
| BASE | 330 | 7,196.30 | 1.928 | 2,350.90 |
| score | 192 | 3,704.42 | 1.474 | 2,292.94 |
| vol | 210 | 5,433.60 | 1.563 | 2,350.90 |
| ret | 189 | 3,129.14 | 1.280 | 1,191.06 |

Primary removed138longs make+3,491.88,avg+25.30,t+1.261. Keptt1.474 vsbase1.928.
PF1.331 vsbase1.327 is slightly higher, but loses48.5%of totalprofit and is NOT improvement.
Keptwin57.3% vsbase57.6%. Shared dailySharpe.658 vs.859;Sortino1.011 vs1.335;
Calmar.323 vs.612;Ulcer.970 vs.924 (50Kreference metric capital, not planreturncapital).
DD2,292.94 vs2,350.90: reduction57.96USD,2.5%. Shorts remain unchanged, so full-parent
profit also falls3,491.88. Full-parent/long/short metrics saved separately.

| year | baselong netUSD | filtered netUSD | removed netUSD |
| --- | ---: | ---: | ---: |
| 2018 | 998.16 | 345.74 | 652.42 |
| 2019 | 1,163.18 | 288.06 | 875.12 |
| 2020 | 1,361.22 | 920.10 | 441.12 |
| 2021 | 1,697.88 | 2,105.54 | -407.66 |
| 2022 | 1,975.86 | 44.98 | 1,930.88 |

## Controls and uncertainty

Fixedvolatility-only control keeps210for5,433.60 (delta−1,762.70); laggedreturn control
keeps189for3,129.14 (delta−4,067.16). Both are diagnostics, not replacement strategies.
Primary does not beat both. The score's small PF change cannot substitute for totalprofits.

1000random kept subsets stratifiedyear×weekday, same kept counts among known-state events,
unknown-state events fixed retained. Save all330event IDs,1000membership masks and daily
paths inmatched_paths.npz. P(randomprofit>=actual)=.5864;P(randomDD<=actual)=.8631;
jointp=.5594. These are diagnostic subset paths, not executable portfolios.

5000month-cluster bootstrap draws give95%interval for totalprofitdelta
[−9,990.64,+2,347.70]USD. Draw indices/results retained; this resamples months and does not
establish robustness to all longer-horizon serial dependence from overlapping thresholds.
No selection-adjusted discovery claim. All preregistered gates except4/5keptyearspositive
fail. Gated2023+validation/MC/account tests were not run. No threshold rescue or signflip.

## Five homes and next step

Personal: NO SUPPORTED MODIFICATION; retain existing unfiltered RS. No numericBASE/ADD/
REPLACE/EMPTY portfolio comparison after faileddesign. The leg's lowerprofit is measured;
wholebookutility not measured. Sourcebook2020-11-30coverage remains a limit, not fabricated0.
50Kfunded: current adoptedT_ONESIDEfade replacesRSlongs, so this is not an automatic filter
for an existing slot; no addition supported.150Kfunded: no supportedRSmodification; no valid
fundedbootstrap run.50Kevaluation/150Kevaluation: RSnotadopted as this parent; no eligible
addition/passrate effect established. No payout/marginbenefit inferred from daily paths.

Close this exact feature test. Originalstockpaper remains a separate study; do not call
its t7.46 our result. No newPowerLanguage, rankings, allocations,live/VPS/settings or
pausedprogram changes. User asked for actualtesting; those results are saved here.
