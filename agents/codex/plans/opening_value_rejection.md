# NQ Opening Value Rejection: frozen standalone preregistration

Evidence: agents/codex/evidence/opening_value_rejection.md. Commit before returns. Signal5/15min; profile5min.
NativeCTminuteclose,normalcash dates,noJuly3/December24. AllnativeOHLCVfinite/valid,volumenonnegative,
no conflictingduplicates/forwardfill. Firsthour08:31--09:30must be complete. Sourcegridsstart2018forwarmup.

## Frozen opening profile

At09:30build twelve5minrange TPOcounts. Integerpoint prices fromfloor(minfirsthourlow) throughceil(maxhigh).
Eachbaraddsonecountto integer prices ceil(barlow)..floor(barhigh), inclusive; otherpriceszero.
POC=lowestpriced maximizer(tie rule fixed). Valuearea startsPOC; expandone adjacentbin atatime toward
larger neighboringcount; tie=>lowerprice, untilcountsum>=f*totalcount. Bounds=selectedminprice-0.5 and
selectedmaxprice+0.5. No profile expansion after09:30; zero-count total invalid. Thisis time-occupancy proxy,
NOT true volume-at-price, not a replication of an unread paper. Preserveallcomputedprofilefeatures.

## Entry and five models

Let A,B consecutivecompleted signalbars, Bclose09:35--14:00(frame5),09:45--14:00(frame15),alignedmidnight.
If Bclose>POC and Bclose<Bopen, potentialshort; if Bclose<POC andBclose>Bopen,potentiallong.
Known targetdistance=abs(Bclose-POC); require0.05priorATR<=distance<=0.30priorATR, stop0.10priorATR.
Candidate additionally: shortAclose>VAH andPOC<Bclose<=VAH; longAclose<VAL andVAL<=Bclose<POC.
This requires a completed return into the frozen area with B's body pointing inward. No staticlevelprobe/oldsignal.
Completebothsignalbars. Entryonewholeextra native minute aftersignalclose: Bclose j=>open j+2.
Stop and targetdistances ceilto0.25point, anchoredto actualentry; thus target equalsentry shifted by the
signal-to-POC distance, NOT an unknowable conditionalnextopenatPOC. Max4/day,oneposition,no stale/sameclose
signals. Timeexitmin(j+60,14:55),entrybaractive,noBE/trail/overnight.

Fivefixedmodels/order: OV5_70(primary5min,f0.70);OV5_80(5min,f0.80);OV15_70(15min,f0.70);
BASE5,BASE15(samepotentialinwardbody/distance/data conditions,omit valueescape/reentry gate). Controlsunselectable.
Prior35+5=40countedevaluations/39uniqueeconomicrules,plus unknown oldersearches. Noexit/size/side/symbolgrid.
NQ$7.25RT+1tick($5)market/stopfill,MNQ$1.24RT+$0.50/fill independent,target1pointthrough,fixed4tickstress.
Sharedgrid._walk/F.replayadapter,protectedentrybar/worsestopgaps. Rejectionknownbefore extraminutedelay.

Design2018-22:>=100tickets,net>0,trade t>=2,dailyNW5>=1.5,PF>=1.20,>=4positiveyears,MNQnet>0,
4tickstressnet>0. Firstfixedcandidatepassing; no maxreturnchoice. Additionalfiltercheckremovedmean<0,
kepttotal>=base,p(randomnet>=kept)<=.10,keptjointlybetterprofit/DDthan>=90%of1000matchedrandomsubsets.
Capsmaymakerealstrategyledgersnon-nested: independent-per-signal diagnostics separatelynonexecutable,
never claimtheir capitalizedperformance or accountimprovement. Commitdesignbefore chosen+base2023--2026-10-09
once,previouslyseenhistoricalvalidation. Nonepass=>endthishypothesisonlyandcontinuedistinctresearch.
Fullt6meansnettradeanddailyNW5>=6,design/validationpositive;NW20reported. Do notrescuefailedfamiliesafter2023+.

All/side/yearstandardrepo metrics, cashdayzeros/initialzeroDD,counts/missingminutes,costs/nativefees/stress,
base/kept/removedtotalnet/removedmean/t/randomdrops. Afterpass onlymatched-exitrandomside/time,
5000blockbootstrap/permutation,10000tradeMC,5000oneyeardailyMC;DSR/selection>=233lowerboundtrials;
freshrawspeccheckerbeforepromotion; currentpersonal19A-D/FULL1MNQBASE/ADD/replaceVB/EMPTY,
wholecontracts. Missing50K/150Kvalidjointchronology=>LIMITS,noproxyimprovementclaims. Frozenforwardneeded.

Onlycodex/workallowedresearchpaths. Deliveranalysis/codex_opening_value_rejection.py,
analysis/outputs/codex_opening_value_rejection/,agents/codex/results/opening_value_rejection.md Summary<=5lines.
NoPowerLanguage,sharedrank/plan,live/VPS/broker/APIchangesonfailedgate.
