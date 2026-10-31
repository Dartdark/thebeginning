# RS long prior-month disagreement filter — frozen before new returns

Evidence: ../evidence/disagreement_rs_20261029.md. User"Do it" approves one feature test.
Parent fixed: adopted Relative Strength NQ/ES MultiCharts list,1micro, personal both sides;
filter applies LONGS ONLY, short trades unchanged. Source report
mc_reports/Backtesting Strategy Performance Report _ @NQ - 1 Minute Relative Strength.xlsx;
RS code funded_strategies/NQ_Relative_Strength.txt, current-source identity reconciled before
any later numeric book bench. This is conditional immutable-ledger filter evidence; no new
entry, exit, stop, target, size, beta, signal clock or parent optimization.

Primary1configuration: KEEP long trades iff last completed calendar month's
mean(|overnight simple return|+|intraday simple return|)/SD(close-to-close simple returns,ddof1)
is >=median of the SIX immediately preceding monthly scores, excluding the feature month.
All six threshold months and feature month must be fully known. Unknown score/threshold
retains the original trade; tag unknown separately. Do not require opposite signs.
NQ08:31OPEN to15:00cashCLOSE,earlyclose12:00,immediately prior scheduledcashCLOSE. Entire
featuremonth must have valid endpoints/previousclose on every scheduled session,>=10days.
No forward fill, no rolling window/future-month ranks.2017warmup;2018–22design only initially.

Two diagnostic controls, not alternative nominees: (A)prior-monthclose-returnSD>=median of
its preceding six months, (B)prior-monthtotalreturn>=its preceding sixmonthmedian; same
availability and unknown-retain policies, unchanged RS long exits. No choice of control as
strategy. Retain every control statistic and cumulative trial count (1primary+2controls).
Native1MNQcost1.24commissionRT,1tick(.50)entry plus1ticknonlimitexit;no limit slippage.
Read list-of-trades values only2018–22 after date strings; do not convert2023+financialrows.
Monthly price source files2017–22only. Hash files/code/preregistration; runtime cache only
analysis/outputs/codex_disagreement_rs_20261029/cache. No paiddata or account actions.

Assess unfiltered/kept/removed totals, average,t,year,long/short and five metrics; both-side
parent retained with shorts untouched. Monthly-cluster bootstrap5000 draws on long-filter
profitdelta, seed5164956. Matched1000random kept subsets stratifiedyear×weekday preserving
PRIMARY known-state kept counts and fixed unknown-retained set; save memberships and complete
daily paths. Compare profit,DD separately and jointly. Same dailycalendar for all.

Design gate: removed long total<0 and removedt<=−1; fullfilteredlong profit>base; keptlong
trade t>=2; >=4of5 keptlong yearspositive; profitdelta nonnegative>=3of5years;
matched profitp<=.05,DDp<=.05 and jointp<=.05; primaryprofitdelta>bothsimplecontrols;
monthly-cluster95%lower bound delta>0. A failed gate closes this feature before2023+ or
accountMC; nothresholdreversal/side/newwindow tuning.

If passes, immediately test currentpersonalBASE,EMPTY=BASE−RSlong,REPLACE=EMPTY+filteredRSlong
and diagnosticADD=BASE+filteredRSlong at1MNQ vs bothBASE/EMPTY, paired5000one-year20dayblocks.
Preserve source fees/marks/missingbookdays; never fill missing2020-11-30 with0. Missingbook
coverage is a disclosed limit; no funded/evaluation bootstrap from dailyproxies. 50Kfunded
current T_ONESIDE replacesRSlong, so no inventedRSfilteraddition there;150Kfunded/personal
source confirmation required. Evaluations originalRS not adopted. No benefit inferred without
actualbenches. Selection freeze commit BEFORE once-only2023+ historical validation; previously
seenhistory notfreshholdout. Protectedrawspec/source-fill checks mandatory before promotion;
parentknownunprotectedentrybar is not silently certified by ledgerfilter. All failures saved.
