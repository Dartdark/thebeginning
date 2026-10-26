# NQ Auction Demand Confirmation: frozen standalone preregistration

Evidence: agents/codex/evidence/auction_demand_confirmation.md. Commit before new returns. Signal5/15min,
one-minute execution. Prior50evaluations/49unique rules; add5=>55/54, plus much larger unknown old searches.
No old trade lists, rescaling, return regression, price-residual signal or failed-family threshold retuning.

## Event and historical result feature

Use data/treasury_auctions.csv rows with security_type Note/Bond, inflation_index_security No, floating_rate No,
closing_time_comp exactly01:00PM, positive finite BTC, validauctiondate/CUSIP/reopening Yes/No. Normalize
security_term to nearest tenor in[2,3,5,7,10,20,30] if years+months/12 lies within0.5year, otherwise exclude.
Nonpositive/missing BTC is not silently removed from an eligible history: it leaves NaN. Conflicting duplicate
CUSIP/date/result keys block intake; exact duplicates may collapse, counted. Multiple distinct eligible auctions
at12:00CT on a date=>no trade that date, not a choice based on their results. Their valid results can enter later
same-group history. Design intake had no such simultaneous date. Store all exclusions and event counts.

Group by(tenor,reopening). Reference=median of exact last6 strictly earlier same-group results,min4finite,
positive observations. Include priorDecember2017calendar rows for reference, but NQ/ZNprice grids start2018.
Missing histories keep their chronological place. Compute today's reference BEFORE appending today's result.
Deviation D=BTC/reference-1. D=0=>no candidate. This is a historical deviation, not consensus surprise/WItail.

## Price confirmation and five models

On a normal cash date(sharedcalendar,noJuly3/Dec24), require exact NQ/ZNdate mapping and all valid positive
OHLC/nonnegative-volume minutes11:59through decision close12:05(frame5)or12:15(frame15), inclusive.
No forwardfill and no current-day future-completeness mask. ZNreaction=ZNclose atdecision minus exact11:59close.
Zero reaction=>no price-control/candidate. Control side=sign(ZNreaction), reflecting hypothesized rates/equity link.
Candidate side=sign(D) only when sign(D)==control side, and optional minimum |D| below is met.
All controls require the identical result/history/date/input mask even though they omit the demand gate.

Exactly five models and fixedcandidateorder:
1. ADC15:15min, any nonzero D confirmed by ZN,primary.
2. ADC5:5min, same gate.
3. ADC15_D05:15min, additionallyabs(D)>=0.05.
4. ZN15:15min,ZNreaction-only control,omit demand sign/size gate.
5. ZN5:5min corresponding control. Controls unselectable; no nomination after returns.

Assume result public by the decisiontime, then wait one additional native minute: decision j=>entry open j+2
(12:17/12:07CT). Public posting policy supports a buffer but does NOT verify every historical receipt/vintage.
OneNQ per date, no retrigger/BE/trail/overnight/sizing. Stop0.15prior15weekday calendar ATR,target0.30,
ceilto0.25point,entryminuteactive,flat12:55CT. Shared_grid._walk viaF.replayadapter; target1pointthrough,
worse-open stopgaps. Missing scheduled open=>skip that event. ZN is a reference, not a second traded leg.
NQ$7.25RT+1tick($5)market/stopfill; nativeMNQ$1.24RT+$0.50/fill separately. Fixed4tickfillstress,notselectable.

## Cheap design and exact filter controls

Audit result fields/duplicate semantics/tenor and reopening grouping, ET/CT conversion, strictly prior references,
missing exact prices and synthetic execution before real returns. Preserve source hashes/features/intake counts.
2018-22 first:>=100executed tickets,net>0,trade t>=2,dailyNW5>=1.5,PF>=1.20,>=4positiveyears,
nativeMNQnet>0,4tickstressnet>0. All/long/short/year standardshared metrics,cashdayzeros/initialzeroDD,NW20,
costs,counts,missingentry/heldminutes. No data repair/deleting missing-held tickets to improve evidence.

Actual one/date candidate ledgers are exact subsets of same-frame controls: same event/side/entry/exits/costs.
Report actual totalbase/kept/removednet,removedmean/t,1000matched-size random subsets. Require removedmean<0,
kepttotal>=base,p(randomnet>=kept)<=.10 and jointlybetterprofit/DD than>=90%random subsets.
Additionally1000random subsets match kept count within each(year,tenor,reopening)cell without replacement;
require the same pnet/joint gates. If cells are too small, that loss of power is preserved, not repaired by changing
strata. These are random-drop diagnostics, not selected economic strategies. Save all random totals/DD/cell counts.
No capped-path mismatch or overlapping independent signals is needed because there is at most one event/date.

Select first candidate passing ALL gates, not maxreturn; commit design before chosen+matchingcontrol2023--
2026-10-09once, explicitly previously-seen historical validation. Nonepass=>stop this hypothesis's validation/
accounts only; continue a distinct preregistered mechanism. Never invert the failed trade or select its controls.
Full-history milestones4.5/5/6 require BOTH nettrade anddailyNW5 t>=threshold, positive design/validation,
realistic native costs and no known fatal error. Preserve history; lower milestones do not complete t6.

## Conditional completion

After pass only: matched-exit randomside/time5000 (times never before assumedresultavailability+delay),
blockbootstrap/permutation5000,tradeMC10000,oneyeardailyMC5000 at1MNQ; DSR/selection at>=248reported-trial
lowerbound and fixed sensitivities. Extra release-latency/auction-result-vintage checks before qualification.
Fresh spec-only independent checker beforepromotion, then currentpersonal19A-D/FULL1MNQBASE/ADD/
replaceRS/EMPTY. Precise50K/150Kaccount comparisons need validjointchronology; otherwiseLIMITS,no invented
proxy payout/pass improvement. Frozenforwardresult-receipt/fill evidence needed before tradingdecision.

Deliveranalysis/codex_auction_demand_confirmation.py,analysis/outputs/codex_auction_demand_confirmation/,
agents/codex/results/auction_demand_confirmation.md Summary<=5lines. Onlycodex/workandallowedresearchpaths.
No watcher changes,sharedrank/plan/rootTODO/live/VPS/broker/API/purchases/accounts/messages orPLonfailedgate.
