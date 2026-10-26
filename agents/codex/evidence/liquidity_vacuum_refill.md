# NQ Liquidity Vacuum Refill: TEST

Summary: A new overnight entry tests whether a large, low-participation jump that immediately fails is temporary
liquidity displacement. It fades only after half the jump is lost. This is not a prior-day/overnight-level sweep,
old trade filter, retuned opening-path rule or copied strategy. Five fixed candidate/control models.

1. Actor: thin-session liquidity providers may replenish after a brief price displacement on modest volume.
   Rejection before entry is necessary; the actor/orderbook is not observed, so this is a hypothesis, not proof
   of forced flow. Informed news can instead make the low-volume jump permanent.
2. Inputs: two completed5/15min native NQ bars, prior20normal-session same-clock range/volume medians,
   prior15weekday ATR. No OF feed/revised profile or future minute. Entry after completed rejection bar.
3. Transmission: NQ directly in the rejection direction; both sides. No prior strategy ledger or basket used.
4. Data: local NQ day/night nativeCT OHLCV2018-2026. Complete input windows and prior data required;
   no forward fill. Conflicting duplicates block, no2017warmup. Nighttime spread/receive availability unverified.
5. Costs: NQ$7.25RT+1tick/market-stopfill; target1pointthrough. NativeMNQ$1.24RT+$0.50/fill separately.
   Overnight execution likely worse than cash; fixed4tickfillstress mandatory. Overlaps BridgeMonday overnight
   on some dates but otherwise not a demonstrated plan gap/hedge. No before-breach offset established.
6. Power:~1event/day would yield1,200design tickets; atSD$300,t6needs~$52net/event. Count actuality without
   loosening after returns. A rare event set may make this infeasible; no forecast profit claimed.
7. Prior: broad liquidity/volume predictors mostly failed; Grimes failure/spring used priorRTH extremes and
   lost, London15min regime flip showed timestamp bias. Here no static level or regime label, lowparticipation
   jump plus observed retracement is the whole new entry. Program25evaluations/24unique plus olderunknown.
8. Failure: scheduled/unscheduled European news, trend continuation, widened overnight quotes, missing data
   masquerading as a jump, rolls and US/EUclock changes. FixedCTwindow is not claimed to follow a foreign fix.
   Stop0.08ATR,target0.12,30minute maximum,flat07:25ahead of07:30USrelease,oneposition/max4perday.

TEST frozen2018-22 first; cheapfailure ends this mechanism only. Do not rescue prior failed families on2023+.
