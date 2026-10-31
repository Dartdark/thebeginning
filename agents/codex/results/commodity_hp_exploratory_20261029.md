# Commodity hedging-pressure pair: REJECT this frozen exploratory version

Summary: Actual2018–22 design test completed.195 resolved conditional pair-weeks earn
−$1,944gross/−$3,207.60net at1MCL+1MGC, pair-weekt−0.562, PF0.899. Six additional
weeks remain unresolved. This does not establish a place in the personal plan. No2023+
run, personal numeric bench or post-result gold-only rescue. Does not refute the paper's
34commodity portfolio or prove that all hedging-pressure implementations fail.

Plan: ../plans/commodity_hp_exploratory_20261029.md, committedba2b92a BEFORE new returns.
Implementation9ca9fd2; output/cache separationb4e97d8 before first economic execution.
Script: analysis/codex_commodity_hp_exploratory.py; report/reconciliation script:
analysis/codex_commodity_hp_exploratory_report.py. Outputs:
analysis/outputs/codex_commodity_hp_exploratory/run_v1/. Previous construction gates remain.
Trials:1primary exploratory design;1fixed larger-slippage stress diagnostic, not a nominee.
All prior family looks remain; stoppedt6/Huntv2 not restarted. One earlier launch aborted
at directory creation before data/returns; original console retained, not an economic trial.

## Rule and assumptions

Legacy commercial HP=(shorts−longs)/OI, CL067651 / GC088691. Each Monday select newest
common report at least6calendar days old, maximum21days, ASSUMING prior publication.
This is NOT independently verified original availability/vintage. One micro long in higher
HP, one micro short in lower; tie flat. Monday08:01OPEN→Friday13:01OPEN, independent2ATR20
rawquote-anchored stops; no target/reentry. Entry-bar stop active; worse opening gap fills
atOPEN. Costs per micro1.24RTcommission+one native tick each fill=3.24RT,6.48pair.
One extra tick per fill is a fixed stress, not selection. No actual margin or execution claim.

Fixed whole-week exclusions: US federal holiday weeks, shutdown/recovery interval
2018-12-22–2019-03-15. These were declared before returns, not fitted to losses. Report
snapshot revisions and unverified alias continuity remain. ATR uses20prior observed cash
sessions with actual endpoints and>=90%observed coverage; no future ATR fitting.

Supplied unadjusted continuous CL/GC price proxies retain roll-splice movements. No return-
selected roll deletion or adjusted series was chosen. Prelisting MCL is counterfactual
micro-cost sizing on CL quotes. Missing internal bars are ignored under a conditional
observed-bar assumption, which may omit stop hits; maintenance/weekends contribute to the
missing-minute count. Therefore no certified executable/native account history is claimed.

## Actual results: resolved subset,2018–22 only

| year | resolved pair-weeks | native-cost net USD | pair-week t |
| --- | ---: | ---: | ---: |
| 2018 | 41 | -1,738.68 | -1.040 |
| 2019 | 33 | 1,326.16 | 0.878 |
| 2020 | 40 | 2,198.80 | 0.631 |
| 2021 | 40 | -1,598.20 | -0.709 |
| 2022 | 41 | -3,395.68 | -1.056 |

195resolved pair-weeks /390leg trades. Net−3,207.60; average−16.45per pair-week;
PF0.899; pair-week win43.6%; t−0.562; weeklyNW5−0.605; exit-booked dailyNW5−0.562.
Gross−1,944.00 minus483.60commission minus780.00slippage reconciles to net.
Closed-week equity drawdown6,444.84USD; this is not full intraday/MTM account drawdown.
Exit-booked daily Sharpe−0.248,Sortino−0.360,Calmar−0.097,Ulcer5.699 at50K reference
capital. These daily metrics cover resolved-subset exit booking; they are not personal
capital-return/MTM risk estimates. Source roll uncertainty is unresolved.

Legs: CL−6,770.80; GC+3,563.20. CLshorts165trades−5,946.60 / CLlongs30−824.20;
GClongs165+4,078.40 / GCshorts30−515.20. These are descriptive splits after the test,
not selected new strategies. Two correlated legs count as one pair observation.

## Coverage and gates

261calendar Monday opportunities:195conditional resolved,52fixedholiday exclusions,
8fixedshutdown exclusions,6unknown scheduled-price weeks. Unknown events retained in
all_weeks.csv and null daily cells; no zero-return substitution. The aggregate numbers
above are resolved-subset subtotals, not established totals for the six unknown weeks.
['2018-03-26', '2019-04-15', '2020-04-06', '2020-11-30', '2021-03-29', '2022-04-11'].

SharedGrid24 and grid.execute/_walk used; conflicting sourcekeys were invalidated before
execution; no price forward/backward fills. Synthetic checks before returns covered entry-
bar stop, adverse gap fill and missing scheduled endpoint. Reconciliation validates both
legs/pair, gross minus fees and slippage, and complete status counts. Ledger verification
is not an independent raw-spec checker or author-replication certification.

Every frozen gate fails: gross mean−9.97 is below12.96USD (2xpairRTcost), net negative,
tbelow2,only2/5positive years, crude leg negative, and six unresolved weeks. Larger-slippage
stress net−3,987.60. It cannot be promoted even under the exploratory assumptions.
No historical validation, controls/MonteCarlo/account path tests run after design failure.
No additional variant, gold-only nomination or favorable roll adjustment authorized.

## Five plan verdicts

Personal: NO ADDITION SUPPORTED; failed design, no numeric BASE/ADD/REPLACE/EMPTY comparison.
This is not measured harm to every personal book; diversification was never established.
50Kfunded and150Kfunded: weekly overnight rule ineligible in current intraday implementation;
no funded bootstrap benefit claimed.50Kevaluation and150Kevaluation: likewise no eligible
addition or joint pass-rate result. Existing book data gaps and implementation uncertainties
were not converted to proxy pass/payout improvements.

## Recommendation and evidence boundary

Close this exact two-market version. The paper offered an economically plausible research
lead; that was not evidence it helps our book. These measured results now reject our frozen
pair's design. A substantially different universe would be a separate user-prioritized study,
not an excuse to tune this failed family. No live/settings/shared-ranking changes.
All failed/unknown events, costs, source hashes and ledger records retained. Raw selected
COT rows and cache prices stay local; claim binding records their byte identity only.
