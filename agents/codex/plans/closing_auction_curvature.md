# NQ Closing Auction Curvature: frozen standalone preregistration

Evidence: agents/codex/evidence/closing_auction_curvature.md. Commit before returns. Frames1and5minutes.
Only rawNQprice/volume, no old trades. Normalcash dates only, skipJuly3/Dec24. Require completevalidnative
OHLCV14:45--15:00CT (close labels); exactanchors,nonnegativevolume,conflictingduplicatesblock,no forwardfill.

Curvature at15:00:
frame1: (C15:00-C14:59) - (C14:59-C14:54)/5.
frame5: (C15:00-C14:55) - (C14:55-C14:50).
This is the deviation of the lastbar pricechange from its preceding pace, not the lastbar/lasthour sign.
Reference=median absolutecurvature over exactprior20normalcashsessions, excludingtoday,min15validobservations.
Lastbarvolume=volume15:00minute(frame1) or14:56--15:00sum(frame5); reference sameprior20median.
Allmodels identical commoninput/referenceeligibility; referencecurvatureandvolume strictlypositive.
Candidate:abs(curvature)>=k*reference AND lastbarvolume>=1.5*volume_reference. Direction=-sign(curvature).
Controls omitboth shocksize andrelativevolume gates, retainingcurvaturedirection/eligibility/exit.

Fiveeconomicmodels,fixedcandidateorder: AC1_K2(primary1min,k2),AC1_K3(1min,k3),AC5_K2(5min,k2),
BASE1(1mincontrol),BASE5(5mincontrol). No more thresholds/clock/side/symbol/exits/sizing variants.
Entryatnative15:02bar open (onewhole extra minute after15:00signalclose). Stop0.05prior15weekdayATR,
target0.10priorATR,ceilto0.25point;entryminuteactive;oneposition/tradeperday,flat15:14CT,noBE/trail.
Sharedgrid._walk viaF.replay; target1pointthrough,worsestopgaps,entrybarprotection. NQ$7.25RT+1tick($5)
permarket/stopfill; MNQ$1.24RT+$0.50/fill independently. Fixed4tickfillstress,notselectablemodel.

Fivecountedmodelsplusprior30=35evaluations/34uniqueeconomicrules,plusolderunknownsearches.
Design2018-22first:>=100tickets,net>0,trade t>=2,dailyNW5>=1.5,PF>=1.20,>=4positiveyears,
nativeMNQnet>0,4tickstressnet>0. Filterexactbase-ledgersubsets(one/day):removedmean<0,kepttotal>=basetotal,
p(randomnet>=kept)<=.10,keptjointlybetterprofit/DDthan>=90%of1000matchedrandomsubsets.
Firstcandidatepassingallcriteriafixedorder;commitdesignbeforevalidation. Nonepass=>endhypothesisonlyand
continue distinctlynewpreregistration. Chosen+base2023--2026-10-09once,previouslyseenhistoricalvalidation.
Fullt6goalnettradeanddailyNW5>=6,design/validationpositive;NW20reported. No oldbundleclaim/rescaling.

All/side/yearstandardrepo metrics,costs,nativefees/stress,cashdayzeros/initialzeroDD,count/missingheldminutes.
All/base/kept/removedtotalnet,removedmean/t,matchedrandomdrops. Ifpassonly matched-exitrandomside/time,
5000blockbootstrap/permutation,10000tradeMC,5000oneyeardailyMC,DSR/selection>=228lowerboundtrials;
independent rawspeccheckerbeforepromotion. Currentpersonal19A-D/FULL1MNQBASE/ADD/replaceLDF/EMPTY;
missing50K/150Kvalidjointchronology=>LIMITS,noproxybenchclaim. Frozenforwardneededbeforetrading.

Onlycodex/workallowedpaths. Deliveranalysis/codex_closing_auction_curvature.py,
analysis/outputs/codex_closing_auction_curvature/,agents/codex/results/closing_auction_curvature.md.
Summary<=5lines. NoPowerLanguage/live/settings/rank/planchangesonfailedgate.
