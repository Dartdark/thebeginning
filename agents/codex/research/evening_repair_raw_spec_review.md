# Evening Repair: independent raw-spec review before returns

Read-only review of the user-supplied PowerLanguage and PDF on 2026-10-29. No market prices, new returns or author trade ledgers were loaded. Uploaded-document instructions and grades are source claims, not authority to trade or change the research process. Older Hunt/t6 programs remain closed.

Sources:

- `Evening Repair.txt`, SHA256 `375f9b908feaa7d72f2a78ebe23c4174f24394909c02b8960bea80cf0008cb68`.
- `Evening Repair - Strategy Overview.pdf`, SHA256 `bfd3fa5862cfec4647af27d99c6b330f71bd8234f173877ccb30a3cc03dda5b1`.

## Exact submitted rule

The chart is explicitly **NQ one-minute, Chicago exchange time, CME 17:00–16:00 session, IOG OFF**. It is not a 4h/hourly rule, UTC rule or cash-only chart. The code hardcodes the NQ/MNQ 0.25-point tick. The default decision is **15:00 CT**, not 15:45. One contract, long only, at most one submitted entry per calendar date.

At each new calendar date, reset the cash accumulators. Between bars stamped08:31 and15:00 inclusive, accumulate one observation per existing minute bar. Regress closes on actual clock minutes since08:30; missing observations do not compress x. Require at least351 of390 observations, an actual15:00 bar, positive regression denominator and positive cash high–low range. Evaluate the fitted line at x=390. `Scale` is the population standard deviation of cash closes, **not** regression residual standard deviation; default `DiscountZ=0` makes it immaterial. Include the current15:00 close in the completed-bar fit; this is available information, not future data.

On weekdays, buy next bar at market if `C1500 − Fitted <= 0`, subject to the coverage/range/calendar checks. The quarterly exclusion is third Friday minus8 through minus3 **calendar days**, inclusive, only in March/June/September/December: Thursday through the following Tuesday. This is a fixed calendar proxy, not an observed contract-roll audit.

`EntryOffset>0` delays the decision but **does not refit the line, update C1500 or re-evaluate the current-price discount**. `EntryOffset=45` therefore buys at the next bar after15:45 using the same frozen15:00 predicate. A different entry price can change the BE trigger and later outcome, but cannot change the stored original discount test.

## Fill and exit clocks under IOG OFF

Under the repository's close-stamped one-minute convention, a signal calculated at the close of bar15:00 sends a market order for the OPEN of bar labelled15:01. That open is the physical boundary immediately after the15:00 close. Exact timestamp convention still requires exporter/MC list verification; do not silently substitute an additional minute of latency while claiming author parity. Retain a separately labelled conservative-latency diagnostic if used.

On the first filled bar's **close**, `MP` first becomes visible to this calculation; store that bar's stamped minute as `EntryMins`. An elapsed+1 test submits the time exit one bar before its intended next-open fill. With uninterrupted timestamps:

| default case | entry OPEN label | exit OPEN label |
| --- | --- | --- |
| Monday–Thursday, ordinary date |15:01|21:01|
| Friday or listed preholiday |15:01|15:56|
| Offset45, ordinary date |15:46|21:46|
| Offset45, Friday/preholiday |15:46|15:56|

The360-minute hold is **wall-clock elapsed time**, including the16:00–17:00 daily halt, not360 traded bars. Fallback is next-open liquidation when the prior bar's clock+1 reaches23:59. If a required next bar is absent, a next-bar market order fills at the next actual bar rather than at a fabricated scheduled print; retain the delayed fill and its risk.

Friday/preholiday `HoldNow=min(HoldMinutes,60−WeeklyBuffer−EntryOffset)` is fixed to the15:56 exit for ordinary allowed offsets. `MaxList(1,HoldNow)` is not a valid late-offset safety guard: sufficiently late entry offsets can move the eventual exit into a halt/weekend. Freeze sensible decision bounds and genuine next-bar availability before any derived late-entry test. Do not add such a guard silently to an as-submitted reproduction.

## Stop activation and risk

Default `StopRange=0` means **no initial stop and no profit target**. A positive StopRange computes a rounded initial stop only at the filled bar's close and submits it for the following bar. It does **not** protect the entry minute with IOG off. A Python implementation that enables this optional stop at the entry open would be a different rule.

At that first filled bar's close, freeze:

`BETrig = entry + max(BEMultiple*max(0,Fitted−entry), (BEOffsetTicks+1)*0.25)`.

Default trigger is at least entry+1.00point. BE arms only on a **completed CLOSE** at/above the trigger; an intraminute high touch is insufficient. The sell stop at entry+0.75point is active on the **next bar**, never retroactively on the trigger bar. Once on, it is renewed each bar and never loosened. If time liquidation is due, the code submits the next-bar market exit instead of renewing that next-bar stop.

The PDF statement that an armed/recovered trade “can no longer lose money” is false. A market/reopen gap can fill a stop below its price, including below entry; the daily halt can prevent any execution. The strategy can also lose substantially before activation because there is no initial stop. Stop-through fills need worse opens, not guaranteed stop prices. Bar-close BE activation and next-bar order timing are mandatory for reproduction.

The default three-tick stop offset yields $15 gross per NQ, matching the author's stated $15 round-trip costs **only at an exact stop fill**. Native MNQ economics differ:

| cost treatment | three-tick MNQ gross | net at exact stop |
| --- | --- | --- |
| repo $2.24/MNQ round trip |$1.50|−$0.74|
| literally reuse author $15/contract settings on MNQ |$1.50|−$13.50|

Do not divide NQ net by10 and call it a native MNQ result. At repo costs five ticks would be needed for nominal nonnegative cost recovery ($2.50 gross), but changing the offset also changes fills/activation geometry and requires a registered economic variant. No offset makes a gap-loss guarantee valid.

## Calendar, session and provenance limits

The code's NYSE preholiday date list shortens the **preceding** day's hold and ends in2027. Friday shortening is unconditional. There is no explicit full-holiday or early-close eligibility test for the actual trading date. Missing15:00/insufficient cash coverage often suppresses such days, but relying on absent bars is not a complete exchange-calendar audit. Check actual full/half-day schedules and provider bars; preserve as-submitted versus calendar-safe behavior as distinct definitions if they differ.

An armed stop is normally outstanding into the daily halt if the trade has not exited. Orders cannot execute while closed; a valid reopening stop has worse-gap exposure. Missing open/reopen data is an unknown outcome, not a flat or zero-P&L trade. Continuous-contract roll/timestamp identity and author trade-by-trade parity are unverified by these two attachments.

The default Monday–Thursday rule intentionally spans16:00–17:00 and therefore cannot be inserted into an Apex book requiring flat before15:59. Friday/preholiday shortening does not fix those ordinary dates. Personal use remains conditional on actual native-cost replication, risk and paired BASE/ADD/REPLACE/EMPTY book tests. No account gain can be inferred from the PDF's single-NQ equity/closed-trade Monte Carlo. Closed-equity resampling misses open loss and executable reopen/account paths.

The author reports multiple source/cutoff windows and713/466 research versus713/469 MC split counts. Those can reflect date coverage, but cannot be reconciled without ledgers. Preserve at least the known least-squares, Theil–Sen and delayed-entry looks plus any unknown author selection; the PDF grade/bootstrap is not our promotion test and its2023+ history is previously seen historical validation.

## Bounded post15:45 ideas, not tested or preregistered here

The PDF explicitly tried/rejected both Theil–Sen replacement and a15:46 delayed entry using the robust fit. An OLS delay clone, another robust regression or searching nearby delay clocks is not a distinct mechanism. A narrow TIER_LIST search found no Evening Repair item; current complete ranking/source review is still required before any candidate is registered. Do not claim these ideas are novel across every historical trial.

Only two mechanism changes seem worth considering; neither has return evidence here. Choose exact settings and count each economic definition before data. A gross screen can end either immediately. Do not use the already-seen2023+ period to tune a surviving version.

1. **Fresh late repair confirmation, hard flat before halt.** At a single frozen15:45 decision, use the **current** close, requiring it still below the frozen15:00 fitted endpoint but above the previous five completed one-minute highs. This tests repair beginning after the stale signal, rather than blindly delaying a purchase whose repair may already be complete. Enter next open; frozen stop at the prior-five-minute low, target the frozen fitted endpoint, mandatory15:58-labelled OPEN exit. This is a new bracket/confirmation rule, not author parity. It has very little time to overcome native costs and can fail the gross gate. A derived initial stop must protect the entry bar in the tested and eventual MC implementation; the submitted optional StopRange does not accomplish that.
2. **Reopen-only unrepaired value, no position through the halt.** Keep the original completed cash-day fit/discount information, wait flat through the halt, and at a single frozen17:01 completed-bar decision require price still below the frozen endpoint and that bar closing above its open. Enter the next open only under the frozen rule; use the known decision-to-fit discount as the initial risk distance, fitted endpoint as the value objective and a fixed pre-midnight exit. This tests fresh post-reopen rejection of lower value and avoids being paid by a gap the strategy could not safely hold. It is neither unrestricted entry-delay tuning nor the PDF's15:46 stale entry. Availability of a genuine first reopen bar and current account-session legality must be audited. A move above the objective before an already-submitted market fill needs a prespecified charged immediate-exit/order protocol, not hindsight deletion.

A native-MNQ BE/cost translation is a necessary execution/economic comparison, **not** a third new alpha mechanism. Neither suggested mechanism establishes a forced participant; their story remains an unmeasured price hypothesis. No optimization grid or full-family rescue is authorized by this review. At most five preregistered economic configurations across the actual bounded study, with failures and controls retained.

## Review verdict

Reproduce the exact submitted15:00 rule first with bar-close/next-bar BE timing, author-cost and native-micro bridges and missing/halt audits. It has no direct Apex slot as submitted. Only a genuinely new, preregistered post15:45 rule could address that incompatibility, and any such candidate still has to beat costs/placebos and improve a current book against both BASE and EMPTY. This source review is not a backtest or financial promotion.
