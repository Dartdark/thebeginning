# Six-leg euro reconstruction v1: BUILT; fails the frozen design gate

The Python research engine is built and was actually run on owned2017warmup/
2018–22minute data. The package earned **$7,373.90after modeled M6Eexecution
costs**, Sharpe **1.076**, dailyNewey–West(5)t **2.196**, on1,130usable decision
dates beginning2018-03-06. Weekly Breakout lost money; RSI fails the screen using
fully reconciled costs. **No2023+returns or personal-book comparisons were run.**
This v1does not qualify for any plan. It is our reconstruction, not validation
of the author's results, nativeM6Efills, low correlation or portfolio contribution.

Public preregistration BEFORE data:
[`efe8fba`](https://github.com/Dartdark/thebeginning/commit/efe8fbabd1311a73123d585e924e205a58fa4928).
Public executed code BEFORE data:
[`c4a8fc5`](https://github.com/Dartdark/thebeginning/commit/c4a8fc51443dab854543cd2b046bbb7a98db1921).
Local source commitsf85b93a/fe0b522are also retained in the run manifest.
Plan: [fixed mechanics](../plans/six_e_rebuild_20261027.md).
Evidence: [mechanism/source boundaries](../evidence/six_e_rebuild_20261027.md).
Code: `analysis/codex_six_e_rebuild.py`; audit:
`analysis/codex_six_e_rebuild_review.py`.
Output: `analysis/outputs/codex_six_e_rebuild_20261027/`.
Setup: [Python research setup](../code/SIX_E_REBUILD_SETUP.md).

## What is implemented

All six legs, one unchanged configuration: cross-asset Macro Momentum,
macro-conditioned RSI2pullback, macro-conditioned prior-week breakout,
ZN/own-EUR Macro-Shock, ESStock-Shock and GCGold-Shock. The control replaces
the cross-asset macro score with EUR's own10/21/63trend under identical sizing.

The exact missing choices were frozen BEFORE new returns: mean of horizon
signs, lagged60-change shock means/SDs, WilderRSI2seed, previous completed
calendar week, signal conflicts, ten-decision holding cap, sign at entry,
normal cash-session decision calendar, warmup, whole-contract truncation and
turnover. The source-like base allocations are2/1/1/2/1/2M6E; Macro's5%vol
scaling can make it0–3integer contracts. No minimum-one or fractional rescue.
The5%target refers to the baseEURnotional's return volatility, not5%of cash equity.

Signals use exact15:00Chicago closes (16:00NewYork), then the exact next
15:02close-labelled minute's OPEN, physically15:01CT. EUR reaction uses
07:29and08:30CTclose endpoints. Daily source ranges end at the same decision
cut. No full-session future close or default settlement sneaks into the features.
The CTclock contract follows existing repository conventions; vendor clock/roll
provenance has not been independently authenticated from these CSVs.

There are six virtual states and ONE net broker target. The engine accounts
for partial reductions, reversals, carried positions, FIFOunit tickets and
daily cash/markedPnL. Net broker costs are charged on abs(change in NET target),
not six separate hypothetical accounts. Component curves show standalone costs.
The target API is causal by default; offline sample/unknown-boundary flattening
is an explicit research-runner option, not a live risk-management instruction.

## Design results: actual integer quantities, USD

|Component|Net after modeled costs|Sharpe|Closed M6Eunit roundtrips|
|---|---:|---:|---:|
|Macro Momentum|1,105.50|0.459|80|
|RSI2pullback|308.05|0.139|68|
|Weekly Breakout|−1,020.30|−0.301|72|
|Macro-Shock|2,682.10|0.767|246|
|Stock-Shock|1,073.70|1.028|37|
|Gold-Shock|2,425.60|0.986|106|
|Own-EUR Momentum control|−1,262.20|−0.352|128|
|**Net broker package**|**7,373.90**|**1.076**|**464**|

Two-contract fills produce two unit tickets, not two independent economic bets.
Package trade t3.315is therefore NOT a clean independent-trade or full-history
qualification. DailyNW5t2.196is the primary dependence diagnostic. The current
rankedN326basis gives design dailyDSR0.246; N1000is an explicitly hypothetical
selection sensitivity, DSR0.148. Actual author multiplicity is UNKNOWN, not zero.
No design-only t is a substitute for a passing historical-validation/book test.

Package five metrics: Sharpe1.076, Sortino1.872, PF1.522, Calmar1.044,
Ulcer1.291% at shared50Kreference capital; observed markedDD$1,574.45.
Annual$1,644.44is252KNOWN-decision-day normalization, not a verified full-calendar
annual forecast. The series omits warmup and unknown blocks; do not compare it
directly with the author's complete-history annualized headline.

|Design year|Marked package netUSD|
|---|---:|
|2018(partial warmup)|581.650|
|2019|−486.325|
|2020|2,231.675|
|2021|1,551.775|
|2022|3,495.125|

Both sides exist:179closed long units,+$3,110.40realized;285short units,
+$4,263.50realized. Side/year five-metric CSVs preserve the accounting basis:
side statistics are realized exit-date unitPnL, while package equity is daily
marked. Those are not interchangeable year-by-year attribution conventions.

## Fees, tick projection, netting and the failed gates

The fixed model charges **$1.20per filled M6Eunit SIDE/change** and one adverse
native tick($1.25) per side, plus adverse projection from6E's finer grid toM6E's
0.0001grid. Nominal roundtrip is$4.90 BEFORE projection. Buy prices round up
then add one tick; sell prices round down then subtract one tick. This is a
conservative execution projection of6Eprices, not observed nativeM6EBBO/fills.

Package gross$9,968.125minus total modeled costs$2,594.225equals net$7,373.90.
Netting saves$799.25versus standalone component cost sums; gross component
pricePnL reconciles exactly to broker gross. All eight cash/FIFO/daily ledgers
reconcile; no scaled-return or proxy-derived payout improvement was invented.
Maximum observed NETposition6M6E; maximum simultaneous virtual gross7M6E.
No margin sufficiency or5%-of-equity risk guarantee follows from these sizes.

Weekly is negative even GROSS:−$622.50. It fails the preregistered requirement
that all six components be positive after realistic costs. RSI narrowly passes
the INITIAL MINIMUM-cost screen ($10.083gross/equivalentRTversus$9.80), but
fully reconciled projection/fees require **$11.105gross** for the2xactual-cost
screen. It fails that screen. The original minimum-cost CSV is retained, with
the full-cost addendum in `review/actual_cost_gross_screen.csv`; no result was
overwritten to manufacture a gate pass or hide a discrepancy.

Thus the package gate is FAILED despite positive package net and4/5positive
designyears. No weak leg is removed, no weight/threshold/holding period/sizing
choice is tuned, and no candidate is selected from favorable component tvalues.

## Source coverage and what the test cannot certify

The run audited9,118,882minute observations acrossfive instruments; no duplicate,
conflicting or invalid observed candles. CLnegative prices are supported using
price changes rather than log/percentage-CLreturns. Each input/hash/code version
is bound before values. No2023–26file was loaded for this design experiment.

There are1,249expected normal decision dates in2018–22;1,130are usable after
warmup/required features. Native6E/ZNbeginDecember2017here, so63session signals
cannot be assumed ready inJanuary2018. Five core endpoint dates are incomplete:
CLcut2019-08-20/21/22; allfivecuts2020-11-30; EURfill2021-12-14.
Missing references propagate through fixed rolling windows; they are never
silently removed from a purportedly continuous feature history.

Eight coherent blocks were retained. Offline liquidation at the last observed
arrival before a missing/unknown feature block is a declared DATA diagnostic:
it uses knowledge of the sample boundary and is NOT an executable prediction
of an outage. This can change results; the series is not complete live-strategy
equity. It forbids a clean account/implementationPASS. Exact boundary dates and
feature availability are saved, not concealed as ordinary no-trade days.

CSVcontract IDs and authenticated roll maps are absent. Neither predictor
stitch jumps nor currency roll execution is independently resolved. Observed
minute ranges do not prove full intraday quote coverage. Full6Ebars do not
prove nativeM6Espread/queue/liquidity. A different exact author implementation
could produce different outcomes; no author Sharpe/correlation is verified.

Eleven synthetic groups passed before the financial run. The post-run code
separates causal target generation from opt-in offline boundary liquidation;
twelve groups now pass, including prefix invariance, and the review proves
that the design-runner targets are IDENTICAL to the retained predata run.
No financial experiment was rerun for this API separation. Review is maker QA,
not a fresh independent raw-spec promotion check; no promotion was attempted.

## Placebos, current-book comparisons and all five placement verdicts

The design gate did not unlock2023+historical validation, additional placebos,
MonteCarloor personal-book benches. These are **NOT RUN**, not zero or passed.
The reported author correlation+0.06is unverified and refers to the author's
book, not automatically the current19-piece personal portfolio.

|Plan|Placement for this frozen v1|
|---|---|
|Current personal portfolio|**Not qualified.** Failed component/cost gate; no2023+or BASE/ADD/REPLACE/EMPTY improvement measured. Positive design net alone is insufficient.|
|50Kfunded|**No place as written.** Multi-day/weekend holds conflict with intraday requirements; no conversion or account bench.|
|150Kfunded|**No place as written.** Same holding-period incompatibility; no payout/bootstrap gain claimed.|
|50Kevaluation|**No place as written.** No valid intraday/DLL/target path; no pass-rate improvement claimed.|
|150Kevaluation|**No place as written.** No inference from the50Kor a daily proxy.|

For personal, this is lack of qualification, not measured harm to every plan.
Native execution verification alone would not clear failed gates or demonstrate
marginal contribution. For allfourApexhomes, changing the hold to intraday would
be a different separately registered hypothesis, not an implementation fix.

No PowerLanguage draft was written after a failed design. No installation,
live/VPS/broker/API setting, purchase, new account, external message, automation
or phone-delivery claim. Hunt v2 remains completed and paused, counts unchanged.

**Verdict: independent research code built; frozen v1stops at design. Preserve
the full package and all failed components. Any later ablation/new sizing is
a new bounded study, not a repair of these outcomes or a claimed validated edge.**
