# NQ Opening Value Rejection: TEST

Summary: New standalone entry builds an opening-hour time-occupancy value distribution, freezes it, and trades
failed escapes back toward its modal price. It neither combines strategies nor uses their signal/trade lists.
This is a newly specified price-only auction hypothesis; tape-exact volume-at-price is not available here.

1. Actor/mechanism: after an hour of two-sided price discovery, responsive liquidity may defend the accepted
   area; a completed return into it can precede rotation toward its mode. Actual inventory/forced orders are
   unobserved. Persistent informed trends can invalidate the area's relevance immediately.
2. Known information: firsthour08:31--09:30CT OHLC of twelve completed5minbars. Each integerpoint touched
   by a bar gets one time-occupancy count. Mode and contiguous70/80%area are frozen at09:30; later two5/15min
   completed closes define rejection. No same-day final profile or revised OF fields, no future bar volume.
3. Transmission: NQ directly toward the frozen modal price after completed acceptance back into the area.
   Unlike old prior-day Grimes/singleprint, reference is a frozen same-day distribution, not priorRTHhigh/low.
4. Data: native NQCT minuteOHLCV2018-2026, complete firsthour and both signalbars, no forwardfill/duplicate
   conflicts. Range-spanning TPO approximation is not tape-exact volume and can count skipped intrabar prices.
5. Costs/overlap: NQ$7.25RT+1tick per market/stop, target1pointthrough; MNQ$1.24RT+$0.50/fill independent.
   Fourtickstress. Cash NQmean-reversion exposure can still lose with existing book; no guaranteed hedge/gap.
6. Power:~1event/day would give~1,200design tickets. AtSD$350,t6requires~$61net/trade. Target mustbe>=0.05ATR
   toavoid trading trivial two-tick rotations. These are power assumptions, not a forecast of eventrate/profit.
7. Prior: prior-day singleprint responsivePOC trade t1.4; Grimes failure test negative; OU/VWAPreversion failed.
   Program35evaluations/34unique plus unknown older searches. Public abstract 'Harvesting the Value Area'
   (Alqaydi,SSRN7546200) suggests area-rejection geometry; fulltext403,NOTread/replicated and not evidence of
   this rule. Source https://papers.ssrn.com/sol3/papers.cfm?abstract_id=7546200 (searchabstract only).
8. Failure: trendday acceptance shifts, openingmode incidental, macro news, sparse/gapped profiles, reference
   lookahead, insufficienttargetdistance, fill-path assumptions. Stop0.10priorATR,targetknownPOCdistance,
   max60min,flat14:55,max4/day. Stops gap; no before-accountbreach offset. Nopaiddata or false volumeclaims.

TEST five frozen models on2018-22. No sourcepaperheadline/t or unseenfulltext used to infer success.
