# Frozen batch 2: monthly causal net barrier-payoff forecasting

Evidence: `agents/codex/evidence/pressure_learning_20261110.md`. Firstbatch RESID2 is REJECT; results/controls retained.
This is a new conditional-payoff forecast protocol, related to previous pressurefamilies. No fading or following is fixed
by a priorfailed sign. Three definitions here, cumulative newstudy6; prior unrelated/related multiplicity also remains.
Commit exact executablecode before labels, fits or return outcomes. Do not overwrite firstbatch artifacts.

## Inputs and eligible signals

Same hashed native2018–22minute/complete5min/calendar/roll/priorATR assumptions as batch1. Every complete5minclose09:00–14:00
on normal cash, excluding fixedrolls; no conditioning on later jumps or incumbent trades. Features require current and
two exact5min lags, prior20normalcashsameclock volume observations (20valid), finite priorATR. No imputing gaps.

Featuredefinitions fixed: body0/body1/body2=(C−O)/priorATR; range0=(H−L)/ATR; loc0=2(C−L)/(H−L)−1;
q0/q1/q2=(buy−sell)/total; efficiency=sumlast3body/sumlast3absbody; logvol=log(currentV/prior20sameclockmedianV);
vol3=sqrt(sumlast3close-return-point²)/ATR; hour; side and side×body0/body1/body2/loc0/q0/q1/q2/efficiency.
Zero denominators/nonfinite required features mean no forecast. Volume normalization is causal per observation.
Monthly scaler mean/std fits training features only; degenerate feature columns use scale1, not future values.

## Labels and orderclock

For every eligible bar and both hypothetical sides, replay independently without occupancy/caps ONLY to form training
labels. Entryopen ofrowj+2 (wallj+1 after onefullminute allowance), stopceil(.10priorATR/.25)*.25,
targetceil(.3stop/.25)*.25; scheduledexitclosemin(j+31,14:55), exactly30wallminutes afterentryopen.
No BE/trail/averaging. Shared _walk entrybar/gap/bothhit rule and1pointtargetthrough. NetR=net_mnq/(2*stopdistance).
Keep timeexit and worse-than−1R outcomes; do not clip payoffs. Every label is marked available only at scheduledhorizon,
evenif its targethit earlier. Unknown labels may be excluded from historical training only; unknown actualcandidate
execution cannot be silently discarded or clear a gate. Preserve stop-first ambiguitycoststress.

## Fitting and three definitions

Fit BEFORE each calendar month using exactprior126normalcashdates; roll/missing slots do not stretchthewindow.
Require>=100represented dates,>=10,000valid long+shortlabelrows,>=50kind0fullstop labels EACHside across>=30sessions.
All label maturity timestamps strictlybefore fitmonth. No dailyrefit or hyperparametersearch. Fixedseed20261110.
1. **RIDGE** selectable primary: standardizedfeatures, Ridge alpha100, defaultintercept.
2. **HGB** selectable alternate: standardizedfeatures, HistGradientBoostingRegressor max_iter120,max_leaf_nodes7,
   max_depth3,min_samples_leaf250,l2_regularization10,learning_rate.05,early_stoppingFalse,random_state20261110.
3. **HGB_PRICE** unselectable control: identical HGB but dropq0/q1/q2 and allside×q; retain same input eligibility.
One shared regressor with side/interactions forecasts both choices. For each signal choose greater predictednetR only
if>.02R; exactties/noadequatefit =>noentry. Oneposition, max4actualentries/day; sameclose suppression. Fit/predict logs
retain trainingdates, labelavailabilitymax, feature/scaler identities, representedsides, loss coverage and forecast.
Numerical ties use absolute1e-12 tolerance. Hour means integerfloor(CTminute/60); volume-baseline20normaldate slots include
roll-date volumes, while modeltrade/labeldates exclude rolls. Both choices are fixed before outcomes.
Choose first candidate that passes ALL gates, RIDGE beforeHGB; never maximumSharpe or the control after outcomes.

## Design gate, then earned validation

Saveall3predictions/signals/trades/dayzeros/year+side metrics and fittedmonthQA. Bothdirectional hypotheticallabelrows
are training outcomes, not independent economicstrategies or an executable equitycurve. All3modeldefinitions count.
Basiccandidate:>=250executabletrades across>=100dates,>=25eachside, positiveNQandMNQnet, tradet>=2,dailyNW5>=1.5,
PF>=1.2,>=4positivedesignyears, positive4tick and stop-firststressnet, zeroinvalidheldpaths. No gate fromtrainperformance.
For basicpassonly: paired daily gain over HGB_PRICE must have10day-block90%CI low>0. Keep fullrandomside/time same-exit
placebos, cost/latencystress and existing dependence/multiplicity gates before finalselection. Profitablecontrols cannot
replace failed candidates. A basicpass alone does not permit readingrecentreturns.
Commit definitive design decision/selectedrule before loading2023+ outcomes. Later samefoldfitting rule stays unchanged,
using only labels matured before each historical fitmonth; readthrough2026-07-07flowend only, no missingflow=zero.
This is already-seen historical validation. Then5000bootstrap/permutation, independent rawspecchecker, matched-native
costs and any earned currentbook account replay. No NativeMC/Windows/phone/broker operation is implied.

## Stop and continuation

If both selectable models fail, reject this specified batch, preserve all6newstudydefinitions plusearlier failures,
and continue only through a newly justified, committed, genuinely changed hypothesis. No threshold/window/direction
rescue, repeatedholdoutlooks, claims of future success or manufactured screenshotmatch.
