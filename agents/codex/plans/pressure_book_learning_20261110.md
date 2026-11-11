# Frozen batch5: archived depth-conditioned net payoff

Evidence `agents/codex/evidence/pressure_book_learning_20261110.md`. Conditional archival research only: original source
receipt/build/revision proof missing, so a return pass cannot clear data availability or authorize native/live use.
Three definitions, cumulative15 new-study plus previous related book/pressure searches retained. Commit exact source,
input hashes, label-cache Git object and this plan BEFORE actual new features/fits/returns. No new labels generated.

## Fixed inputs and clocks

Native NQ2018–22 minute OHLC,total,buy,sell only for execution and completed five-minute quantities. Strict native hashes.
Book adapter uses exact20 quarterly hashes/headers, ET-close->CT-close, no forward filling or source alignment search.
Positive spread/top/six depths, monotonic depth10<=20<=50/top<=depth10, same native key, closewithin.25,buy/sell exact.
Invalid support is explicit unknown. Endpoint state is the close snapshot, not sum of snapshots. Exact t-5min reference.
Depth same-clock baseline: exact preceding20 normal-cash calendar slots, shifted1,20valid required; roll-date volumes/depth
remain in baselines while candidate/training roll dates are excluded. Calendar from native full grid; no future matching.

Reuse exact `analysis/outputs/codex_pressure_learning_20261110/features_and_labels.csv.gz` Git bytes at
0d61f59e30304a5a9850ef1a20b33a2d1f04cc2d. No clipping, new outcome generation or filtering by future label_valid.
Cached date/day/decision mapping must match the native grid. Both side rows retained on known book eligibility only.

## Fixed37 features / three definitions

Original21 batch2 price, signed-flow, side/interactions. Add9:
spread_ticks; topimb=(topbid-topask)/(sum); depth10imb; depth50imb;
near_fraction=totaldepth10/totaldepth50; log(totaldepth10/prior20sameclockmedian);
log(totaldepth10/exactt-5depth10); spread(t)-spread(t-5); depth10imb(t)-depth10imb(t-5).
Addcapacity_buy=log1p(native5minbuy/endpointaskdepth10), capacity_sell=log1p(sell/biddepth10).
Addside×topimb/depth10imb/depth50imb/imbalancechange5min andside×(capacity_buy-capacity_sell).
Finite current+lag+baselineknown and positive depth are required for all3models. Capacity is a bar-volume/endpointdepth
proxy, not actual queue consumption, native LOBgap or observed replenishment. No wall-price/DLL-derived future label.

1. HGB_BOOK selectableprimary: fixed HGB frombatch2,37features.
2. RIDGE_BOOK selectablealternate: standardized Ridge alpha100,37features.
3. HGB_NOBOOK unselectablecontrol: identicalHGB and sameeligible observations, originalfull21features INCLUDINGq.

Exact126priornormalcashslot training eachcalendar month; >=100sessions/10000maturevalidpairedlabels and fullstop
coverage50/30dates eachside. Labelknownat scheduledfull horizon <fitmonth even if targethit early. Training-only scaler.
HGB max_iter120,max_leaf_nodes7,max_depth3,min_samples_leaf250,l2=10,learning_rate.05,earlystopFalse,seed20261110.
No innersearch. One side with max predictednetR>.02,1e-12 ties skip. Code reuses fresh isolated batch2 module namespace,
no mutation of original module files/globals. Archive fit/scaler/features/cost/run identity and every definition.

## Execution unchanged

Complete5min decisions09:00–14:00, normalcash excludingJuly3/Dec24/fixedquarterrolls. Prior shifted15observedweekdayATR.
Decisionclosej -> rowj+2open (wallj+1) after fullminute allowance. Stopceil(.10ATR/.25)*.25,
targetceil(.3stop/.25)*.25, noBE/trailing/averaging; exitrowj+31close,flat14:55,oneposition,max4actualentries/day.
Shared worsegap/entrybarstop,nearestextremebothhit heuristic with mandatory stop-firststress,1pointtargetthrough.
NQ20$/point,7.25RT+5/marketstopfill; MNQproxy2$/point,1.24RT+.50/fill; four-tick fillstress. Actual native micro fills
and quote/receipt unavailable. Unknown held path blocks, never silently drop it or treat missing as no-trade success.

## Decision and earned stages

Basicgate per selectable:>=250executedtrades/100dates/25eachside;NQnet>0,MNQnet>0,tradet>=2,dailyNW5>=1.5,
PF>=1.2,4positiveyears,positive4tick/stopfirstnet,zero unknownheldpaths. Save whole/long/short/year standardmetrics,
gross/costs/dailyzeros and all3failed/successful variants. Choose HGB_BOOK then RIDGE_BOOK ONLY after every gate.
Onbasicpassonly: paired daily difference againstHGB_NOBOOK,10dayblock90%CI lower>0; Ridgecomparisonwholepolicy.
Thenmatchedrandomside/time same-exitplacebos,selection/dependencesignificance,cost/latencyrobustness,sourcevintageproof.
No basicpass alone permits2023+returnreads. Commit full design decision, resolve source gate, then exactly once2023+
historicalvalidation with unchanged monthly fitting, separate laterinputreconciliation, flowend2026-07-07. No priceend
substitution ormissingflowzero. Independentrawspec/nativeMC and current150Kaccountstage only if all earliergates pass.
No live/platform/notification/purchase work. Negative batch closes this exact rule; no tuning or promoting itscontrol.
