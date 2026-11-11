# Frozen batch3: resting-entry extension of unchanged price-impact repair events

Evidence `agents/codex/evidence/pressure_passive_20261110.md`. Sourceevents bytes/blob must equal
`c852212a:analysis/outputs/codex_pressure_build_20261110/batch1_design_qa2/RESID2_signals.csv.gz`.
No event regeneration or changed threshold/side/confirmation/stop/maxrisk. This is related execution research following
failed market-entry/learning batches, not independentnewalpha. Three definitions; cumulative newstudy9.

## Quotes, activation and reservation

Source confirmation closeT, side s, originalanchoredstopS and maxrisk=.15priorATR remainfixed. At decision:
- **L1** selectable primary: Q=Cconf−s*.25.
- **L2** selectable alternate: Q=midpoint(Cconf,S), longroundedDOWN to.25, shortroundedUP.
- **MARKET** unselectable: sameevent/controlactivation; enteratobservedactivationopen, independently of futurelimitfills.

Forlimits R=s*(Q−S)>0and<=sourceMaxRisk, target=Q+s*ceil(.3R/.25)*.25. Wrongside/oversized decisionrisk rejects theorder.
A viable decision reserves the only slot fromT and counts toward max4SUBMITTEDorders/day, including activationcancel
or eventualnofill. No signalwhile reserved/held, no sameclose reentry, averaging/repricing/retrying/retaRgeting.

Wait ONE FULL5minbar. Activate atwallT+5, native close-labelT+6. A limit must be strictlypassive against thatopenproxy:
longQ<open, shortQ>open; equality or crossedquote cancels. MARKET checkspositive/maximumrisk to unchangedS atthatopen,
then sets its ownrounded.3Rtarget. Maxrisk can be exceeded by separately chargedexecutioncosts.
Quote expires after5activeminutes, close-labelsT+6..T+10inclusive. Fill beforefinalTTLclose haspriority, otherwisecancel.
Atmissingactivationopen/ANYactivepending/heldOHLC, retainUNKNOWN, haltfurther submissions thatday andblockadvancement.
Inactive5minlatency has no liveorder and needs no futureOHLC to inferexposure. Do not callunknowns unfilled/zero.

## Conditional fills/exits and costs

Limitsfill onlyafterlonglow<=Q−1point orshorthigh>=Q+1. FillatQ, no favorablegapimprovement. Pendinggapthroughstop
canfillatQandstopatworseopen. Stopordersareactiveinfillminute; stopfirst ifstopandtargetbothpossible.
ForLMTfillminute a target is credited ONLY if no stoptouch AND the endingclose has tradedbeyond target+1point(long),
or target−1(short). A high/lowonlytouch could precede the entry and gets no profitcredit. ForMARKETentryatopen,
laterH/Ltarget-through is chronologicallyvalid withnostoptouch. Thereaftertargetthrough1point and stopfirstallmodels.
Immediatebracketactivation is an explicit assumption, not exchangeacknowledgment. Exitclosefillrow+29 (30wallmin from
thatbaropenproxy) or14:55. Fullpolicy stress repeatsallmodels with NOtargetcredit inentryminute; label itlatencystress.

NQ20USD/point,7.25RTfee; passiveentryslip0 onlyunderlimitpriceassumption, MARKETentry1tick. Stop/timeexit1tick,
targetexit0slipbut1pointthrough. MNQpriceproxy2USD/point,1.24RTfee,.50/tick. No rebates or nativefillclaims.
Mandatory entrycoststress adds1ticktoeachpassiveentry(MARKETalreadycharges1tick), not a worse-than-limitfill assertion.
NativeBBO/queue/partialfill/receipt and originalcontract/build/roll limitsremain.

## Design gate / advancement

Saveall3order/trade/dayzero/year+side metrics,submitted/fill/cancel counts, unknown exposure, fees and fullstresses.
Candidate basicgate>=150fills,>=25eachside,>=4positivedesignyears,NQandMNQnet>0,trade t>=2,dailyNW5>=1.5,PF>=1.2,
positiveentrycoststressnet,zero unknownactive/heldexposure. Strictno-fillbarTPstress must also staypositive for advancement
under this conservative review. Firstpassingcandidate L1 thenL2, neverlargestSharpe/marketcontrol.
Afterbasicpass: paired policygain vsMARKET with10dayblock90%CI low>0, matchedrandomtime/side/pricequoteplacebos,
fullselection/dependence/latencystresses, then committed designselection BEFORE any2023+outcomes. No promoting acontrol.
Sameconditional fillmodel on reconciled laterinputs; nofillassumption tuning afterresults. Positive laterhistory then
independentrawspeccheck/nativeMCconditionalstatus and earnedcurrent150K BASE/ADD/REPLACE/EMPTY chronology as priorplans.
Failure closes this extension; no changing quote depth, TTL, target-through, stopfirst, entrylatency or sides to force a win.
