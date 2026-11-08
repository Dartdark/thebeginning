# Frozen weekly NQ/VIX adaptation — before returns

Summary: User asked to fill missing formulas rather than stop at source rejection.
One assumed candidate and one simplebaseline, no optimization. Personal-onlyweeklyhold.
Commit this plan and exact script before returns; previous source-audit history remains.

## Fixed assumptions

NQ RTHweeklyclose from owned minuteexports, Monday–Friday calendarweek. Bars are close-labelled.
EMA5andEMA25of weeklyclose: pandas adjust=False,min_periods=length. "Increased" means thisweek>lastweek.
CashVIXlast date<=Friday, at most7daysold. Ratio=weeklyNQclose/VIX; signal1=EMA12ofratio,
signal2=EMA5ofratio. TDMRSI1 interpreted as conventional WilderRSI2of weeklyNQclose, not chained tripleRSI.
Wilderinitialmean first2deltas then recurrence; zero loss/gain→100/0, bothzero→50. TripleRSI14/56andBB
do not enter screenshot's active conditions and are not introduced as extra filters or variants.

Full entry: close>EMA5, EMA5andEMA25rising, ratio>signal1, RSI2<75, VIX<40. Exit: ratio<signal2 or
completed weeklyclose<95%rawentryprice or unavailable/stale VIX. No same-week exit/reentry.
EMA-onlybaseline: sameEMAentry, exitclose<EMA5or same5%weeklycondition; sameexecution/calendar/costs.
OneMNQconstant per position, no compounding or dynamicrisk. Slippage0.25pointleg and commission$0.625leg;
second coststress2ticksperleg, sameorders, counts as one executionstress of each economic rule, not another rule.
ReferenceNQcost$3.625commissionleg+$5slippageleg; display standardizedreference separately from actualMNQ.

## Clock, roll treatment and samples

FridaycompletedRTH+finalVIXdata used for nextweek Monday07:59CTdecision. Execute nextactualsession's
08:01close-labelledbarOPEN(08:00CT), with slippage, includingMondayholidays. Dailyclosemark fromlastRTHbar.
No futureopen as a feature. 2017warm-up; design2018-01-01through2022-12-30only.
Reject duplicate bars and absentexecutionbar for an otherwise active session. Forcecloseatfinaldesign
sessionclose withslippage/commission to avoid censoredresults; identically forbaseline.

Continuouscontracts have unidentifiedrolljumps. Conservativecalendarquarantine: anyweekwhoseMonday–Friday
datesintersectday5–16ofMarch/June/September/December is flat, with exitfirstactual08:00CTbeforethat
week'squarantine. Noentrythatweek. Thisavoidsknownrollwindowspanningpositions without hindsightlargestgap
selection. It does **not** authenticatecontractIDs/actualrolls; rawpricelevels still affectindicators.
Record this materialsource deviation; no claimedexactnativeprofit or riskcertification. Unexpectedrolloutside
window remains a limitation. Stopifdaydatahashmismatchor unrecognizedschema. No overnightbarimputation.

## Gates and stop rule

Designpasses only if ALL: fullrule>=20closedtrades; positivegrossandnet; trade-mean t>=2;
dailySharpe>=0.5; positiveyearlynet>=3of5; stressnet>0; fullruleSharpe>=baselineSharpe+0.10;
fullruleannualprofit/maxdailyDD>=baseline counterpart. Daily/tradecash reconciliation mustpass tocent.
Failureends2023+, placebos, personalportfolio andMultiChartswork. Norescueparameter/date/clock/risk change.
Reportallfailedgates, baseline, annual/longmetrics, zeroshorttrades and actualwarm-up/dataexclusions.
Cheapgate is advancementonly, notpromotion or proof of sufficient independentpower.

Ifdesignpasses, save beforelaterdataread. Validationfrozen2023+historical, not freshholdout; samegatesexcept
>=15trades andpositive>=halfavailableyears. Requirepromotiontrade t>=metrics.t_threshold(max(500,rankeditems+2))
orDSR>=0.95. Then1,000seed5630830circularweeklyshifts of frozenexposure as descriptiveplacebo
(samecostlogic, no claimedsource replication); no multipleplacebochoice. Need95thpercentilenetbeat and
unchangednativequote/roll/cashriskreview beforecurrentpersonalBASE/ADD/REPLACE/EMPTY. Currentbook mustbe
readthen, versions/cutoffscommoncalendarretained; don'tuseolderportfoliosnapshot. NoApexbench forweeklyholds.
Fullportfolio/stressimplementation is dependentwork, not reason to bypassfailedcheapgate.

## Run identity and tools

UseconfiguredPython. Scriptreadsourcecheckoutdataonly; hashagainstcurrentGitblobs, retainSHA256andweekly
features/trades/dailycashledger. Extendrepoexecutioninnewcodexfile: existinggrid.executeis intradaybracket
oriented and cannot correctlyexpressweeklyholds/weeklycloseexit anddailycashmarks here.
Usemetrics.perf andt_threshold; no newmetricdefinitions except explicit trademeant andgrossnet/costbridge.
No actualread/returnafter2022unlessdesigngatepasses; no sourcepaperclaim reused as observedreturn.
Record2economicdefinitions plus2fixedcoststresses, allpriorselectionhistory. No live/VPS/broker/APIkey,
tradingplan,TIER,scouthistory orscheduledautomationchange.
