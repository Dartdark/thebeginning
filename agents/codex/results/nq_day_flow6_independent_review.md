# NQ Day Flow Six: PASS WITH CONCERNS for historical ledger/statistics only

Summary: The primary-cost full-history aggregate t≥6 claim is numerically reproducible: 3,615 source tickets, 2,262 sessions, net $71,161.90; ticket t=8.0416, daily iid t=7.1102, NW(5) t=6.7728. This is selected historical composition, not evidence of a new independent alpha or an executable combined strategy. The four-tick stress fails the NW(5)≥6 gate. Two holiday/reopening exits violate the intended intraday behavior; combined platform/Apex clearance is blocked.

Plan: `agents/codex/plans/nq_day_flow6.md`, committed preregistration `d27cda2`. Checker: `analysis/codex_nq_day_flow6_checker.py`. Artifacts: `analysis/outputs/codex_nq_day_flow6_checker/`. Economic variants tested by checker: none; fixed-source reconstruction and the preregistered fee/slippage sensitivities only.

## Independence and scope

I first read the committed preregistration and repository instructions, then reconstructed paired entry/exit rows directly from the six raw workbooks. I did not read the maker script, output files or result report until after saving `independent_snapshot.json` at 2026-10-25 23:31:31 UTC. The snapshot binds the six workbook hashes, runtime versions and the reconstruction-version script hash. The final expanded script hash is recorded in `maker_comparison.json`. No source signals were regenerated, and no independent raw-signal, random-entry placebo, walk-forward, full checker-gate, account simulation or combined MultiCharts replication was performed. This is an independent ledger/statistics check, not the full raw-signal replication required for strategy promotion by DEVELOPMENT_PROCESS.md.

All source entry/exit dates must lie in 2018-01-01 through 2026-10-09 inclusive. Each source ticket represents one MNQ irrespective of reported quantity; all workbook quantities are one. Gross is independently `(exit-entry) × side × $2`, reconciled against reported NQ ticket profit divided by quantity and ten. Costs are $1.24 commission plus $0.50 per slipped fill: one entry and one exit unless the exit signal says Profit/Target. No source prices, entries, weights or tickets were changed.

The daily calendar is derived using only raw day-file date/time columns and the repository Grid24 time-based definition (weekday dates whose last day bar is at least 11:00 CT). It contains 2,262 sessions including zero-trade days. Five short raw dates fall outside that calendar: 2018-12-05 (08:30), 2021-04-02 (08:15), 2023-04-07 (08:15), 2025-01-09 (08:30), 2026-04-03 (08:15). These are time-based calendar exclusions, with no return-based exclusions. All retained tickets survive, including the NFP entry on 2023-04-07; its P&L is realized on the actual exit session. Exits at/after 17:00 CT book to the following CME date. Every realized session maps to the calendar.

Ticket t uses sample SD; Newey-West uses the centered intercept-only series with Bartlett lag weights and autocovariances divided by n, without a finite-sample correction. Daily iid t uses sample SD. Initial zero is used for drawdown only, never as an extra observation. Ticket t is descriptive because sleeves overlap.

## Independent results

| era | side | tickets | sessions | net | trade_t | daily_iid_t | nw5_t | nw20_t |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| full | all | 3,615 | 2,262 | 71,161.90 | 8.0416 | 7.1102 | 6.7728 | 7.2009 |
| full | long | 2,876 | 2,262 | 48,574.76 | 6.3907 | 5.2635 | 5.2655 | 5.8546 |
| full | short | 739 | 2,262 | 22,587.14 | 4.9944 | 4.9798 | 4.7729 | 4.3073 |
| design | all | 1,899 | 1,289 | 27,521.74 | 5.1466 | 4.7253 | 4.4406 | 4.1458 |
| design | long | 1,485 | 1,289 | 15,933.10 | 3.5820 | 3.0673 | 3.0375 | 3.1894 |
| design | short | 414 | 1,289 | 11,588.64 | 3.9213 | 3.7798 | 3.4565 | 2.8263 |
| validation | all | 1,716 | 973 | 43,640.16 | 6.1948 | 5.3722 | 5.2120 | 6.3668 |
| validation | long | 1,391 | 973 | 32,641.66 | 5.3028 | 4.2869 | 4.3586 | 5.2500 |
| validation | short | 325 | 973 | 10,998.50 | 3.2096 | 3.2894 | 3.2991 | 3.3840 |

The aggregate full-history primary gate passes. Validation alone does not have daily iid or NW(5) t≥6, and neither side alone meets all three thresholds. Design meets the preregistered cheap gate: 1,899 tickets, positive net, daily iid 4.7253, NW(5) 4.4406, ticket PF 1.4117, four positive years out of five. Full-history closed daily max drawdown is $2,566.32, versus $2,341.52 design and $2,566.32 validation. These are historical realized-P&L drawdowns, not intraday breach paths.

| era | tickets | sessions | net | trade_t | daily_iid_t | nw5_t | nw20_t |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2018 | 338 | 257 | -341.62 | -0.2453 | -0.2460 | -0.2682 | -0.3392 |
| 2019 | 317 | 258 | 969.92 | 0.9074 | 0.8388 | 0.8374 | 0.9762 |
| 2020 | 387 | 258 | 8,492.62 | 3.5902 | 2.9845 | 2.8921 | 2.9746 |
| 2021 | 414 | 258 | 8,050.14 | 3.1503 | 2.9323 | 3.1500 | 4.0252 |
| 2022 | 443 | 258 | 10,350.68 | 2.8431 | 2.6938 | 2.4226 | 2.2079 |
| 2023 | 439 | 257 | 11,702.64 | 4.7983 | 4.0746 | 4.5099 | 5.1575 |
| 2024 | 436 | 259 | 7,776.86 | 2.5482 | 2.2914 | 2.6912 | 3.1661 |
| 2025 | 448 | 257 | 12,645.48 | 3.1575 | 2.9885 | 3.0565 | 3.3075 |
| 2026 | 393 | 200 | 11,515.18 | 2.6861 | 2.1592 | 1.8866 | 2.6344 |

By-year side results are fully retained in `statistics.csv`. Source reconciliation at primary costs:

| sleeve | raw_tickets | kept | gross | commission | slippage | cost | net |
| --- | --- | --- | --- | --- | --- | --- | --- |
| VB | 1,743 | 1,743 | 18,540.00 | 2,161.32 | 1,295.00 | 3,456.32 | 15,083.68 |
| ONB | 344 | 343 | 22,399.00 | 425.32 | 331.00 | 756.32 | 21,642.68 |
| MON | 451 | 450 | 19,912.00 | 558.00 | 450.00 | 1,008.00 | 18,904.00 |
| EOS | 105 | 105 | 5,156.50 | 130.20 | 105.00 | 235.20 | 4,921.30 |
| LDF | 898 | 895 | 10,013.00 | 1,109.80 | 895.00 | 2,004.80 | 8,008.20 |
| NFP | 79 | 79 | 2,779.00 | 97.96 | 79.00 | 176.96 | 2,602.04 |

There are 920 target exits (VB 896; ONB 24). The other 2,695 exits slip. Five source rows are excluded strictly by the fixed window: two LDF tickets in 2017; one ticket each in ONB, MON and LDF on 2026-10-12 (three later tickets total). Thus 3,620 raw tickets minus five excluded tickets equals 3,615 retained tickets. The later ONB row is an open-mark record with an exit label at midnight before its 09:15 entry; it is outside the study and not used as a closed trade.

## Exact maker reconciliation

After the independent snapshot, I joined maker design/validation trade exports one-to-one on sleeve and original entry/exit timestamps. All 3,615 tickets match in side, prices, source quantity, gross, costs and exit-session booking. Maximum net difference is below $4e-15. All 2,262 daily totals match within $1.2e-13. All 360 compared era/side metric values (counts, dollars, t statistics and drawdown) match within 1e-6, allowing maker CSV precision. Workbook hashes match the maker source binding. `maker_metric_differences.csv` and `maker_comparison.json` preserve the comparisons.

Independent preregistered full-history sensitivities:

| case | net | trade_t | daily_iid_t | nw5_t | nw20_t |
| --- | --- | --- | --- | --- | --- |
| primary | 71,161.90 | 8.0416 | 7.1102 | 6.7728 | 7.2009 |
| fee_1.04 | 71,884.90 | 8.1233 | 7.1787 | 6.8387 | 7.2701 |
| four_ticks | 61,696.90 | 6.9636 | 6.1938 | 5.8924 | 6.2699 |

Four adverse ticks per slipped fill reduce NW(5) t to 5.8924. Consequently “t≥6” needs the primary one-tick cost qualification; it is not robust to that fixed stress. The constituent histories/models were already selected using these years, so 2023+ is historical validation, not an untouched holdout. Adding six selected ledgers produces a diversified composition; it does not establish a new signal or incremental alpha beyond those ledgers.

## Carried and late exits

- MON ticket 282: entered 2023-07-03 08:35 CT at 15,355.25; exited 2023-07-03 17:05 at 15,346.75, signal `Monday LX`. Gross -$17.00, net -$19.24, realized CME date 2023-07-04. This is a same-calendar-date position spanning the closure/reopen, after the 15:59 deadline.
- NFP ticket 49: short entered 2023-04-07 07:50 CT at 13,165.25; exited Sunday 2023-04-09 17:05 at 13,169.50, signal `NFP Fade SX`. Gross -$8.50, net -$10.74, realized CME date 2023-04-10. This is the only cross-calendar-date ticket and carries across the weekend.

Both are preserved, not deleted or recosted. Among retained tickets there are no 16:00 exit labels and exactly two 17:05 exits. These cannot be explained by a one-minute 15:59/16:00 bar-label convention. The MON source’s early-close rule omits July 3; NFP’s time exit waits for a bar with Time≥09:00, absent on that Good Friday morning. Session-aware exits or signal suppression would change the executable rule and require a separate tested ledger; an emergency flatten instruction cannot make the historical prices identical. Missing-bar periods also preclude proving intraday risk from this ledger alone.

## Virtual-sleeve reference and execution blockers

After the ledger reconstruction I isolated the maker reference `VirtualSleeves` class and exercised every one of its 729 six-sleeve position states across 18 possible unit target updates (13,122 transitions). The arithmetic is correct: virtual target updates produce the change in the sum of intended signed sleeve positions, opposite sleeves can coexist virtually, immediate duplicate exits give zero delta, and absolute target net cannot exceed six units. Timestamp-based reconstruction has maximum virtual gross and absolute net four MNQ, consistent with the maker’s minute-grid exposure proxy; neither proves intraminute order sequence.

This class stores intent only. It has no actual broker-position feedback, order or ticket generation ID, fill acknowledgement, partial-fill/rejection handling, cancel/replace lifecycle or platform integration. The immediate duplicate-exit test does not protect a new ticket: open ONB short, close it, reopen ONB short, then deliver a delayed exit from the previous ticket; `target('ONB',0)` returns +1 and erases the new short intent. That is a production blocker if such callbacks are connected without ticket identity. Likewise the returned intent delta cannot safely be treated as a filled-position delta when a previous order was rejected or partially filled.

A combined executable implementation still needs per-ticket ownership; idempotent event handling across reentries; reconciliation against confirmed actual net position and pending orders; stale order cancellation; durable restart/recovery behavior; correct protective stops and targets when virtual sleeves offset; fill/cost reconciliation; causal same-bar ordering; session/holiday flattening; and combined MultiCharts playback confirming those behaviors. Gross-ticket costs may be conservative for offsetting activity, but do not prove combined fill attainability. Uncoordinated same-symbol charts or a single MarketPosition variable do not implement this virtual ledger.

Apex clearance further needs the valid joint intraday paths with the actual current account book, including overnight legs, account liquidation/lock/recovery behavior, contract/risk caps, and funded/evaluation ADD/REPLACE/EMPTY controls under the applicable account rules. Standalone EOD-only bootstrap risks cannot substitute for that. Existing six-sleeve duplication and fee/calendar differences must not be called new alpha. I make no allocation, payout, pass-rate or live-readiness recommendation.

## Verdict

**PASS WITH CONCERNS for the narrow historical ledger/statistics reconstruction.** The maker’s primary-cost aggregate t≥6 claim is reproduced with no meaningful accounting discrepancy. **No promotion/combined-execution/Apex clearance is granted.** Independent raw-signal replication, holiday/deadline correction, a real combined manager with platform parity, and valid account-level intraday evidence remain outstanding. No branch changes, commits, pushes, live/VPS/broker/API edits, maker artifact edits or unrelated strategy reruns were made.
