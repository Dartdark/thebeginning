# R2Vault reconstruction: frozen five-model test
Summary: Build the supplied PDF strategy as a research replay and assess every current plan context.
Source settings are frozen; no thresholds, exits or session interpretation will be optimized after returns.
ET and CT are parallel reconstructions because the PDF does not identify its clock or execution settings.
No live-plan change; promotion requires independent review and the latest Claude gates.

Evidence: `agents/codex/evidence/r2vault.md` (TEST). PDF SHA25660742409a30d91902d26bdd0c15b39cb229db13f26394fc4ee86a316872da107.
Author parameter versions2 claimed; full author search unknown. Codex prior unranked return models7
(ORPullback2, night-volume2, Anson3), plus these5; use latest ranked count+12 as a conservative known lower bound.
Plan/context reference172322e5151f45e2cbf1da4dbd9efb20ba12d1a9. No R2 price returns before this commit.

## Hypothesis and source gaps
Price-only hypothesis: a low-R² candle identifies a useful reference for long breakout continuation when576-bar
regression slope is positive. No independently measured forced buyer is established. VaultBreak is nearest overlap.
Source gives no code, contract count, timezone, session-history template, overnight/vault-reset policy or order
renewal/intrabar semantics. OneNQ75/40point geometry is an explicit interpretation of $1500/$800, not verified
source quantity. Reconstruction cannot establish exact parity with the author's headline2518trades/PF1.23.

## Exactly five models
| Model | Entry window CT | Vault | End-of-day behavior | Uses |
|---|---|---|---|---|
| et_raw |08:30–14:30 (source clock ET)|persistent|brackets only, carries allowed|primary personal + standalone|
| et_apex |08:30–14:30|persistent|flat15:55 regular/11:30 early|primary50/150eval/funded|
| ct_raw |09:30–15:30|persistent|brackets only|alternate personal + standalone|
| ct_apex |09:30–15:30|persistent|same Apex flat|alternate50/150eval/funded|
| et_daily_reset_raw |08:30–14:30|reset every CTdate|brackets only|diagnostic standalone only|
Both main timezone interpretations get all five placement tests; no post-results timezone selection.
All models use full24hour observed five-minute closes, midnight-aligned bars from Grid24.bars(5).
The fifth model is only a stated vault-lifetime sensitivity, not another placement candidate.

## Signal and order lifecycle
At each completed observed five-minute bar, standard OLS Close against increasing0..575 gives slope and R².
Constant-price variance gives slope0,R²0; clamp only floating-point errors to[0,1]. Require576 observed bars.
When R²<=.030, replace stored VaultHigh/Low with THIS candle's high/low, including while held/outside entry hours.
Vault range must be positive. Daily-reset model clears vault at each calendarCTdate before new updates.
After updating, if flat, slope>0, a valid vault, filled-entry count<3, and close time>=start and<end, issue a
buy stop for the next five-minute chart bar only: ceil((VaultHigh+.20*(VaultHigh-VaultLow))/.25)*.25.
Only actual filled entries count, reset calendarCTdate. No short trades/pyramiding. No reuse of a filled order
within its source five-minute bar even after a same-bar exit. Re-evaluate at the next completed source bar.
Order cancels when not renewed and at window end. Active price wall times[start,end), equivalently minute-close
columns start+1 through end. A newly crossed stop fills at opening price; no added below-trigger filter.

## Causal minute execution and protection
Use the repository deterministic OHLC heuristic in each observed minute: O-H-L-C if H-O<=O-L, otherwise O-L-H-C.
Process existing orders at opening gaps first, then traverse monotone segments. On an intraminute stop entry,
protection begins exactly at entry crossing and only the remaining path contributes risk. Never use the minute's
pre-entry low or post-exit low. There is no blanket stop-first collision override. Record entry/exit phases and
boundary held adverse extrema sufficient to reconstruct account minute paths.
Long stop entry fills at trigger or worse gap open. Bracket is raw entry−75 stop / raw entry+40 target immediately
active, including entry minute. Stop gaps fill at adverse open; otherwise stop price. A target requires TP+1point
trade-through and executes at TP; favorable opening gaps>=TP+1 execute at open. These are explicit BarMagnifier
proxy assumptions, not exact source platform settings. UseBreakEven=false; R² take-profit threshold2.00 never fires.
At Apex15:55 regular/11:30 early, queue next-minute-open flatten; windows truncate on early closes. No unpriced
synthetic fill when that minute is missing. Mark/drop unknown days transparently at account stage.
At the forced-flat opening minute, the queued market exit has priority over protective opening-gap orders,
including favorable target gaps; it pays market exit slippage. Other opening minutes prioritize resting brackets.
Raw positions retain brackets outside entry windows and across dates. An open final position is saved separately;
do not invent a terminal executed close. Personal includes its last observable mark, labeled unrealized.

## Costs and marking
Source signal geometry uses raw prices; costs deducted in money. NQ=$20/point, MNQ=$2/point, tick.25.
Apex perMNQ roundtripfee1.04; fee stress1.24 on baseline AND candidate. Entry stop slip.50/MNQ; stop/marketexit
slip.50; targetlimit exitslip0. Reserve full roundtrip commission plus entry slippage at entry in account/personal
paths; charge exit slippage when executed, no double fee. Thus target geometry stays75/40points at every size.
Personal publishedfee1.275/MNQ roundtrip, same fill-specific slippage. Preserve published baseline fee assumptions,
Twin v1 daily marks/other inherited baseline limits and disclose them. Do not call a mismatched baseline exact.
Personal daily mark at last observable same-date price<=16CT; after16 fills belong next trading session. Handle
intraminute boundary phases and no later-price substitution; reconcile closed+open money to daily totals.

## Samples and staged execution
Design2018–2022 first, then execute the same frozen models2023+ once, including negative results without changes.
This is a source-reproduction/user placement request, so negative design results still get bounded2023+ diagnostic
and all-plan tests, not a rescue search. Already examined repository2023+ prices are historical replication.
Report2018–24,2025+, exact authorOOSstart2025-01-15 and sourceend2026-08-31 where useful, plus cacheextension to
2026-10-09. No2017RTH reproduction. By year and whole/long/emptyshort: trades, win%, net$/NQ, trade t, dailySharpe,
Sortino,PF,Calmar,Ulcer,DD; daily and trade periods identified.20dayblockbootstrap95%mean/total uncertainty on2023+.
Count missing/partial bars, unknown held gaps, crossdate positions and early exits; retain all raw events in ledger.

## Placebos and trial accounting
For mainfourmodels run1000 fixed-entry random-side controls (seed848): keep actual entryevent time/rawprice and
re-execute symmetric75/40brackets±side with the same carry/flat policy and costs. This is an event-conditioned
falsifier, not an executable alternative; source event timing already depends on long signals. Oneposition and
subsequent-event overlap obeyed; counts may differ due to reexecuted holds.
Run1000 long random-time controls(seed849): one random five-minute decision close drawn uniformly inside each
fixed window on each independently eligible observed trading day, market next-minute-open, same75/40brackets,
carry/flatpolicy, no knowledge of whether the actual strategy later traded or its direction/outcome. Flat-only
entries skip overlapping holds, no future-conditioned forced count. Eligible calendar defined from timestamps/
coverage only. Report total$, expectancy,DD, tradecounts and limitations of one/day versus source max3/day.
Controls are null draws, not parameter-selected candidate variants. No filter ablation or parameter tuning.
Use repo metrics.t_threshold and deflated_sharpe with rankeditems+12 lowerbound and sensitivity to unknown
author search. Record every returned model including failures. No favorable subset erases a failed primary.

## All-plan comparison, fixed sizes and controls
Reuse validated prepared baseline;47 dependency blobs unchanged at latestClaude172322e. Do not rebuild market caches.
50Kfunded allocations BASE,EMPTY_VB,ADD1,ADD2,REPLACE_VB2.150Ksame plusADD4. Candidate counts undergo same fractional
account scaling then integer floor as baseline.250/500day horizons;1000 paired L20 whole-day circular histories,
seeds1..4 with250each. Report payoutmean/range,blown%,sixpayouttime, paired95%effects vsBASE ANDempty; preserve
complete candidate/baseline day universe and exact finite-quantity simulator parity allfiveoutputs.
Evaluation: same fixed allocations (plus150KADD4), actual integer counts (VB8/20,Bridge2/5,ONBrisk1100/2750,
EOS500/1250),21real-session rollingwindows, no calendar compression across unknown days. Preserve/disclose inherited
50Kpass-first versus150Kbreach-first same-minute tie. Report pass%, breach%, duration and chronological-blockCIs.
Bothfeelevels compare matched baseline; allcohorts2018–22,2018–24,2023+,2025+,full.
Personal: publishedA/B/C/D/full14;one/twoMNQaddition; C/D/fullVBempty/replacement1MNQ.21configs pertimezone.
5000 paired252day L20 histories(seed1), full2018+ and2025+; noApexlimits. Report medianprofit,DDp95,20%DDcapital,
historicalannualblockCI and paired effects. Continuous equalDD riskbudget is diagnostic, never executable size.
Measure candidate exposure overlap/jointlossdays withVB and portfolios; additional exposure does not imply hedge.

## Decision rule and completion
REJECT placement if costs/noise/gaps or failed recent/multipletest/placebos/accountincrement prevent credible fit.
WATCH if plausible source effect but required evidence remains uncertain; CANDIDATE only if t>=latestfamilythreshold
AND DSR>=.95, positive design,2023+t>=2, clean checker/placebos, matchedallcostMC/paired plan benefit includingempty,
and no unresolved implementation issue. Account improvements cannot bypass failed statistical/review gates.
No ranked-plan edit, no live action. MultiCharts code only afterpassing; Python replay is the requested first build.
Independent agent reviews source, execution and placement evidence; Claude independently reviews/ranks finalreport.
Reports beginSummary<=5lines. Commit/push completed research tocodex/work only, pull beforepush; noPR2 action.
