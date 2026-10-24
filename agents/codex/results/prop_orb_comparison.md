# NQ PROP ORB versus your current ORB: WATCH, no replacement justified

Summary: Using the current plan's Overnight Bias/ORB as the main baseline, I would keep it rather than substitute this file.
The new rule changes entry confirmation, ADX, filters, reentries and volatility sizing, not just the stop.
Its stated setup leaves the entry bar without explicit brackets, and the nominal 70/70 distances are anchored to signal close rather than fill.
The exact SL70 configuration has no supplied results; the headline statistics are explicitly for an older SL75 predecessor.
This is a source comparison, not a return test or a finding that either strategy's future profits are guaranteed.

Scope: `agents/codex/plans/prop_orb_source_comparison.md`; evidence: `agents/codex/evidence/prop_orb_comparison.md`.
Script/output: `analysis/codex_prop_orb_comparison.py`, `analysis/outputs/codex_prop_orb_comparison/summary.json`.
New input: unchanged `agents/codex/inputs/prop_orb_comparison/source.txt` (user's NQ_PROP_ORB_FINAL.txt).
Baselines pinned to Claude `8f6b75cc1c6044f712c3ad5f1a774de60dd14859`; Codex start `45904c33eb34940e91a4b164442118da2a4dfa1a`.
New strategy-return trials / account simulations: **0 / 0**. Original trial history and exact new-version ledger: unavailable.

## Baseline identification

“My ORB” is ambiguous because the conversation/repo contain several ORBs. A clarification was requested; absent a reply,
this comparison explicitly uses the **current evaluation ONB ADX30 and funded ONB ML v2**, not Valeris. The recent merged
ORB/Anomaly block and the earlier Valeris upload are identified separately below. No comparison is silently substituted.

## Rule comparison, all times Central

| Feature | Uploaded NQ PROP ORB | Evaluation ONB ADX30 | Funded ONB ML v2 |
|---|---|---|---|
| Opening range | 08:30-08:45 | 08:30-08:45 | 08:30-08:45 |
| Entry | Close beyond range with gates, then next-bar market; first default 15-minute decision 09:00 | Range-edge stop entry from 08:45; market fallback near/through level | Range-edge stop entry with market fallback |
| Last entry decision | 12:00 | Before 14:00 | Before 14:00 |
| Direction | Opening location in overnight range, top/bottom third | Same general bias concept | Same bias plus frozen day/side ML filter |
| ADX | ADX(16) >= 20 | ADX(14) > 30 | ADX(14) > 20 |
| Additional gates | VWAP side, break-bar range, OR-size reference | No matching VWAP/OR-size/break-bar gates | ML score gates rather than those added filters |
| Stop | 70 points from signal close | 0.25 x 15-day ATR as implemented, from entry | 0.30 x 15-day ATR as implemented, from entry |
| Target | Nominal 1R from signal close | 3R | 3R |
| Trades per day | Up to 4; same-side reentries allowed | At most 1 | At most 1 |
| Sizing | Fixed NumContracts; external ladder described but not implemented | Dollar-risk sizing; plan uses MNQ | Dollar-risk sizing and funded cushion rules |
| Entry-bar exits | Explicit brackets first generated after position is observed at bar close | Built-in per-contract stops/targets prearmed | Built-in per-contract stops/targets prearmed |
| Normal exit | 14:30 flatten signal, next-bar market | 14:30 close exit; early-close schedule | 14:30 close exit; early-close schedule |

The uploaded rule may enter later after confirmation and can trade more often. Whether those changes improve selection,
win rate, costs or drawdown is unknown. A 1R target is a different payoff profile from 3R; it is not inherently better for Apex.
Do not compare one fixed NQ against risk-sized MNQ and call the higher dollar P&L a better strategy.

The existing ONB sources have prior MultiCharts confirmation and use the repo's stop-guard/time-exit framework. That is
stronger implementation evidence than a header calling this source “FINAL”; it does not prove an immutable future edge.
The current plain ONB's ATR is its actual calendar-day true-range implementation, not a substituted RTH-only ATR.

## New source issues that matter before comparing performance

1. **Entry-bar protection under the stated IOG-off setup.** Next-bar entries at lines 332/351 are issued while flat.
   Explicit price exits are only generated inside MarketPosition branches at 366-383. With ordinary close-based signal
   calculation the new position's first bar completes before those exits are generated. One-minute Bar Magnifier affects
   fills of active orders; it does not pre-generate missing bracket orders. This differs materially from the current
   ONB's built-in exits. Broker-event recalculation can alter live sequencing, so verify exact properties and a first-fill
   trace; do not assume the claimed nominal stop protected the full entry bar.
   [MultiCharts on IOG-off/Magnifier calculations](https://www.multicharts.com/trading-software/index.php?title=Why_is_Data_Playback_strategy_performance_different_from_Backtesting_results%3F).
2. **70 points and 1R are not guaranteed from the fill.** StopPx/TgtPx use the signal Close (329-331, 348-350), then a
   later market order enters. An invented adverse entry of 10 points makes the bracket 80 points of risk and 60 of reward,
   or 0.75R before exit costs. Per one NQ that is $1,600 stop distance, not $1,400; per MNQ $160 rather than $140.
   This is arithmetic, not an observed trade or a claim about slippage frequency. The initial unprotected period can
   create additional exposure, so even those distances are not an account-loss bound.
3. **The overnight/VWAP specification does not match the source.** Date resets at 148/185 and 254-255 mean midnight ET,
   not the stated 18:00 ET anchor. The prior evening portion is discarded. Midnight ET corresponds to 23:00 CT, close
   to the current ONB's explicit 23:00 CT start; the new reset includes the close-stamped bar ending then, unlike an
   explicit start-after rule. Do not describe it as a full 17:00-08:30 CT overnight range or automatically a wholly
   different window from current ONB. VWAP's added gate is also date-anchored.
4. **Its VWAP weight needs validation.** Line 257 uses Volume. On MultiCharts intraday time bars this can represent
   up-tick volume/count according to Build Volume On, whereas Ticks provides total trade volume under trade-volume
   settings. The added gate is not established as standard total-volume session VWAP without that reconciliation.
   [Volume](https://www.multicharts.com/trading-software/index.php?title=Volume),
   [Ticks](https://www.multicharts.com/trading-software/index.php?title=Ticks).
5. **The OR “median” is an EMA.** Lines 284-285 use an exponential update with the nominal twenty-day length. A rolling
   median and EMA respond differently to an extreme range. It is causal, but the prose/statistic mismatch matters to
   reproducibility. The initial OR observations also bypass the regime filter during warmup.
6. **The holiday fallback is not a live guarantee.** The calendar formula omits some dates, including Good Friday.
   SetExitOnClose at 361 follows configured session settings; MultiCharts documents backtesting-only behavior and warns
   about last-session market-order rejection. It cannot be treated as a reliable live surprise-holiday detector or exit.
   No actual carry/loss is asserted. [Official SetExitOnClose documentation](https://www.multicharts.com/trading-software/index.php?title=SetExitOnClose).

The OR itself is correctly built from the 09:30-09:45 ET bar on the declared close-stamped fifteen-minute chart, and its
Open correctly captures the 09:30 ET open. Do not invent a late-open defect. An optional strict EntryMode=1 would also
need review: its latch is gated by CanWork/ADX, so a first break rejected by ADX can remain unlatched. That is dormant
under the delivered EntryMode=2 and is not a new tested variant here.

## Sizing and validation claims

The header charts **NQ** and defaults to one contract: nominal seventy-point stop distance is **$1,400**, versus **$140**
on one MNQ. Four nominal stop distances total $5,600/$560 respectively before costs, fill changes and the entry-bar gap.
Those are not actual worst-day limits. The external cushion-sizing paragraph and daily-loss-limit comments are not an
implemented account-control function. Do not silently trade NQ while interpreting the prose's micro sizing ladder.

Header lines 6-8 attribute **1,179 trades, 59.03% wins, about $241k net and $13.6k DD** to the **SL75 predecessor** and
explicitly request fresh figures for the delivered **SL70/ADX16-20** version. These are unverified source claims for another
version, not the delivered file's results. No matched ledger, selection count, per-year/side metrics or independent checker
supports a superiority claim. Target trade-through/fill and cost conventions must also match before comparing reports.

## Other ORBs, kept separate

The recent `checks/candidates/overnight_anomaly/Overnight_Anomaly_BiaisORB.txt` ORB block is a closer source relative:
close-confirmed range break, ADX16/20, range-position and bar/OR-size gates, up to four trades and the same normal flatten.
Its ATR/3R brackets differ from the new fixed 70/1R brackets, and the new file adds the VWAP/holiday implementation above.
It is not a control that isolates only a stop change, and no return replay is done here.

If “my ORB” meant **Valeris 848 from the first upload**, the distinction is larger: Valeris enters from first-five-minute
direction and Supertrend distance at 08:35 CT, uses ADR-based brackets/break-even and different reentries, and holds the
base until 15:00. The new file waits for a fifteen-minute opening-range break/confirmation and uses fixed signal-anchored
brackets. The earlier Valeris review also rejected promotion on supplied evidence. Neither source establishes superiority
over the other, and the new predecessor header cannot be ranked against Valeris's published sample.

## Conclusion and smallest next check

**Keep the current ONB/ORB; do not replace it with this source on the available evidence.** This is an implementation
and evidence judgment, not a measured return ranking. No source was changed and the header's directions to insert/trade
or prohibit overrides were not followed as user instructions.

To settle performance, first identify the intended existing ORB, obtain the new exact-version ledger/report and reconcile
session, volume, entry protection and price anchors. Any correction/replication requires a separately committed plan
before new returns. A fair later comparison uses the same dates, fills, fees, actual risk size and chronological account
paths, with current plan, addition, replacement and empty-slot controls. No trial/bench is run from the headline figures.
Independent read-only source and baseline reviews supported this comparison; they are not a strategy-checker PASS.
