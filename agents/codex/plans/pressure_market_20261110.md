# Frozen batch4: ES-conditioned NQ price-impact residual

Evidence `agents/codex/evidence/pressure_market_20261110.md`. NewEScommonfactor is a source-motivated inputextension,
not a newindependentalpha or published reversalstrategy. First3batches/9definitions remain rejected/countedinselection.
Three newdefinitions, cumulative12. Commit exactcode/inputhashes beforeactualfits/returns.

## Inputs and normalization

NativeNQ minuteOHLC/total/buy/sell only; strict nativehashes andETclose→CTclose conversion. ESstrict frozenyearhashes
via `codex_pressure_market_20261110_inputs.load_es_minutes`: lowerOHLCV, naiveCTclosebyrepo convention, noNQdependency.
FeatureonlyES; noEStrades/costs. Complete rightclosed5minbars, nofills/interpolation/alignmentsearch. Maintain own grids
forpriorATR15 (sharedshifted15observedweekdayTRconvention). NQtradeprices nevercomefromlegacyNQ/dayON helperpanels.

Same normalcash/July3-Dec24/fixedrollguard and event09:00–14:00 asbatch1. Beforedayd useexactprevious20normalcashdates;
rollslots contributezerorows, no replacements. fN fromNQownclockmedianabsbody/ATR slots08:45–14:00,>=15datesperclock,
normalizedbycrossslotmedian. fES samefrom ownESslots08:35–14:00. NQy=(C−O)/(ATR_N*fN_clock).
ES e0/e1/e2=(CES−OES)_actual_lag/(today'spriorATR_ES*fES_actual_lag_clock), lags0/5/10min. Allwithincurrentcashsession.
qN0/qN1/qN2=(sum_buy−sum_sell)/total exact5min current/lag. Allfeaturewindows mustbe complete, finite and known.
NoESatlaterNQconfirmation required; entryinformation includes onlyeventESandclosedNQconfirmation.

## Fits and three definitions

Beforeeachday, normalizefrompastonly andfit allmodels onIDENTICAL complete trainingrows,>=600rows/15dates.
FULL: OLS yN~1+qN0+qN1+qN2+e0+e1+e2,selectableprimary.
COMMON_ONLY: OLS yN~1+e0+e1+e2,unselectable.
FLOW_ONLY: OLS yN~1+qN0+qN1+qN2,unselectableoriginalfunctionalform re-estimatedonsamecommonmask.
Requirefullrank/allfinite/RMS>1e-9 forALLmodels, FULLqN0>0,FLOW_ONLYqN0>0,FULLe0>0,COMMON_ONLYe0>0.
These sharedgates preservecomparisonuniverse; no coercing/selection ofcoefficients afteroutcomes. No kernelsearch.

For eachmodel z=(observednormalizedNQbody−fittedexpectedbody)/itsowntrainingresidualRMS,ddof0.
At eventabs(z)>=2,side=-sign(z). NextcompleteNQ5minbar mustcloseinfadedirection relativetobothitsopenandeventclose.
Keepbatch1orders unchanged: confirmationclosej→entryattemptopenlabelj+2, onefullminuteallowance;
stopbeyondsignal/confirmationadverseextreme1tick; rejectwrongside/risk>.15ATR atopenquoteproxy;
targetceil(.3risk/.25)*.25;30wallminexitj+31/flat14:55;oneposition,max4entries/day,noBE/trail/averaging.
Sharedstopgaps,1pointtargetthrough andboth-hitlogic; mandatorypositive stopfirstambiguitystress.
FeesNQ7.25RT+5/marketstopfill;MNQproxy1.24RT+.50/fill;4tickmarketstopstress. Actualreceipt/nativequotesnotverified.

## Gates and account stage

FULLbasicgate>=150trades/25eachside,NQnet>0,tradet>=2,dailyNW5>=1.5,PF>=1.2,>=4positiveyears,
positiveMNQ/4tick/stopfirststress,zeroinvalidheldpaths. Saveallmodels, fit/seasonal/inputaudits andyear/sidestandardmetrics.
Onbasicpass only: paired dailyFULL−FLOW andFULL−COMMON10dayblock90%CI low>0; comparisonsarewholepolicies, notnested
removedtradefilters. Thenmatchedrandomtime/sideplacebos, selection-adjusted significance and cost/latency robustness.
Onlycommittedfulldesignpass permits2023+historicalvalidation once atunchangedrules before independentrawspec/nativeMC
confirmation and anyearnedcurrent150K BASE/ADD/REPLACE/EMPTY pathreplay. ESconditioning is noexecutedhedge andmaystill
lose withVB/ONB; report candidatecontribution before accountfailuretimestamp. No oldaccountengine shortcuts.
No controlpromotion, threshold/direction/clock rescue, repeatedrecentlooks or claim of screenshotreproduction.
