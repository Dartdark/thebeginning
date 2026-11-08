# Frozen FC2B / ONB / T_ONESIDE ingredient decomposition

Summary:18fixed diagnostic cases,2018–22first, then unchanged already-seen2023–2026-10-09.
No optimum selection, refit, promotion, plan change or fullaccountbench. Commit exact code first.

## Fixed cases

FC2Bv2: originalMCentrydecisions with exactv2exitreplica; remove flowdategate(take all nonzero openingdrives
after20daywarm-up); remove BEonly(BER0, trail150/fixedstop100 unchanged); remove trailonly(Trail0,
BE0.66/fixedstop100unchanged).4cases. No invented up-tick series. Original fixed MCside/entrydates
override only admission; exit state remains replica v2 with backstop, through-close market guard and holidays.

ONBADX30: original; noADXgate; noovernightdirectionrestriction(two-sidedOCOORbreak, firsthitwins);
no3Rtarget(stop0.25ATRunchanged).4cases. No-bias case: gap beyond a boundary chooses thatside; if both
boundaries cross within same minute, nearer-highOPEN→upfirst, nearer-low→downfirst, matching repoOHLC
ordering. This is an assumed counterfactual, not exchange-tick proof. Keep sourceADX/ATR/calendar/lateexit.

ONBML: original frozen score withADX20/stop0.30ATR; noMLscore at identicalparentsettings;
dropcalendar terms only; dropprice terms only(ret1/5/20,rth1,dist50); dropvol terms only(atr_ratio,rv5/20).
5cases. Keep intercept and other coefficients/thresholds fixed, no recentering/retraining. Threshold0.03longs,
0shorts, source59priorobservationwarm-up. The model was fit on allhistoricalyears; all effects are descriptive
fitted-score sensitivity, **not** OOS validation. ONB30is not the noMLcounterfactual because settings differ.

T_ONESIDE: use activefade-onlyv2, noOSleg. OriginalMCheavy-nightentrydecisions; noheavy-nightgate(allvalid
nightfades); reverse direction(follow the night on same parentdates); enter at cashbell(08:31close-labelled
barOPEN rather than08:30); no0.40ATRstop.5cases. Same08:45barOPENexit; regular rawentry08:30OPEN=
08:29CT, delayed08:31OPEN=08:30CT. Entrybarstop active forv2; scheduledexitOPEN has priority. Use exact
prior20completed08:31–15:00rangeATR; stoprounding down forlongsell, up forshortbuy to0.25tick.
Allnight universe begins at first actual MCfadeparentdate, with>=20validnightshistory and>=30nightbars.
Using MCentrydecisions avoids pretending totalTicks reproduces the active Volume gate. Conditional analysis
does not establish calibrated nightvolume thresholds or a newly tradable eventclassifier.

## Implementation and data gates

Reuse owned snapshot / in-memorygridloader from prior ingredients_three study; preserve hashes. Baselines
nonempty and dates/side/entry/exitfinite; daily/tradegross,commissions/slippage/netreconcile. PerNQ$7.25RT
and1tickpermarket/stopleg, targetexitnone; nativeMNQ$1.25RT and same pointslippage. All source constraints
and cases frozen; no proxy field silently used. MCledgers are retained known sources, not hidden freshholdouts.

Before interpreting FC/Texitinterventions: compare replayedoriginals to MC on commonperiodparentdates.
Require>=95%entryprices within1tick and>=95%gross within$5perNQ, allcommonsides equal. If fails, stop that
family's laterperiod, report unmatchedcauses; don't tune stops to fit outcomes. Causal internalengineidentity
check for ONBbaseline versus pinned onb_engine exactsamearrays/settings. Drop-onefilters compared only
after commondateentry/exit/netmatching. If notnested, report changedopportunities, not removed-tradealpha.

Count unknownnominalheldminutes and cross-date trades, retain gaps and exclusions. No futureprice repairs.
ONBuses repository1pointtargettrade-through and OHLCstop/targetordering. Tfade gaps fill adversely; FCv2
entrybackstop and through-closeguards remain even with BE/traildisabled. No unsafe stop/target coupling.
No new full-gridcache. Design data ends2022-12-30before laterfilesread. Latercutoff2026-10-09.

## Measurements and labels

Allcases whole/long/short/year/trades,net/gross/costs,t,Sharpe,Sortino,PF,DD,Calmar,Ulcer,worsttrade,
nativeMNQnet. Paired original-minus-ablationcalendarP&L,1000moving20sessionblockbootstrap(seed20261108).
Purefilters(FCflowdategate,ONBMLscore,noheavyTgate ifnested): removednet/mean/t and1000within-year
equal-count randomdrops onprofit/DD. Other interventions not mistaken for pure datefilters. No past-only
learnedmodel reconstruction or training claim. Values on an alreadyfit MLscore remain selection-conditioned.

Directioncheck Tfade versus same-eventfollow replays bothactualstopdirections, never sign-flipnet as placebo.
Baseline FC/Tgate failures stop dependent recentresults in thatfamily; otherfamilies continue. Source fit/volume
limits must accompany findings even on paritypass. No economicacceptance/promotion gate sought here:
conditional diagnostics of existingrules, not searchfornewcandidate. “Persistentcontribution”requires positive
original-minus-drop in bothperiods; overlappingCI/changedtails→qualified/conditional, not “proven”.

18distinctcases plus controls, allpriorlooksretained. No automatic book/sizing/MultiCharts/live changes,
TIER edits, scoutstate/schedule, paiddata, broker/APIkey/VPS or externalmessages. Any later proposed change
needs separate registered validation and actual currentbookBASE/ADD/REPLACE/EMPTY.
