# NQ Closing Auction Curvature: TEST

Summary: New standalone entry isolates the closing auction's change of price pace, not the sign of the last hour.
Benchmark execution is scheduled/compulsory; the inferred transient inventory effect is not guaranteed.
The existing broad post-settlement fade is weak after costs. Test this exact shock definition before believing it.

1. Actor/flow: cash-index benchmark orders concentrate in15:00CT closing auctions; hedgers/arbitrageurs may
   release temporary futures inventory afterward. Auction schedules are known; actual imbalance orders are not.
   Curvature plus unusual volume is an imperfect proxy and may be permanent news, not inventory pressure.
2. Inputs: native NQ1/5minute completed lastbar change less its preceding price pace; current lastbar volume,
   prior20normalcash-session same-clock absolutecurvature/volume medians, prior15weekdayATR. Allknown15:00.
3. Transmission: trade NQ opposite curvature at15:02nativeopen, allowing one extra minute for receipt/execution.
   Can disagree with lastbar/day/lasthour direction, so this is not copied existing post-closefade tickets.
4. Data: local NQ2018-2026 CT close labels, exact14:54/14:59/15:00 or14:50/14:55/15:00 anchors,
   complete14:45--15:00 window. No backfill/duplicate conflicts. Normalcash days only, skipJuly3/December24.
5. Costs: NQ$7.25RT+1tick market/stop,1point targetthrough; MNQ$1.24RT+$0.50/fill independent.
   Fixed4tickfillstress. Mostly follows existing cash exposures' exits, but don't presume an empty/hedging slot.
6. Power:~10-20%of1250design days could give125-250tickets; atSD$200,t6requires$76-$107net/event.
   Small postclose ranges and costs may make even a true gross reversal untradeable. These are assumptions.
7. Prior: forced_flows3_test.py postsettlement reversal~$29gross/$12net, YMfade fragile after77variants;
   quarterlyrebalance/postclose effects not significant. New curvature/relative-volume proxy and delayedentry
   have no prior return test found. Program30evaluations/29unique, unknown muchlarger historical search.
8. Failure: permanent repricing, spread expansion aftercashclose, exactly missing auction minute, referenceclock
   mistakes, futures settlement differs fromcashauction, gapstop. Bracket0.05ATRstop/0.10target,flat15:14,
   one trade/day, noovernight. No before-accountbreach benefit shown and no assumption this improves plans.

TEST five frozen variants/controls2018-22. Weak prior and costs justify cheap screen; continue if rejected.
