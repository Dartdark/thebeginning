# Claude's review: Kusho FAR / v9, C03 and OB v2 (codex/work f8025f6, 3998e30, 8f69b12, 7d7714b, 16dc86c)

Written by Claude, 2026-10-23.

## Kusho FAR final / v9 (source review, 0 return trials): agreed, WATCH / NEEDS DATA
- What it is: 15-min bullish bar above EMA(50) with a small lower wick (<= 70 ticks) → buy limit at that bar's open for
  one bar (the retest); swing stop (<= 500 ticks) with a 3R target and break-even at +0.5R, else 200-tick stop / target;
  v9 adds mirrored shorts on down-trend days. Author: 3,142 / 3,586 trades, PF 1.40 / 1.43, $10-11 per MNQ a trade.
- Agreed with Codex: **not Apex-legal as supplied** (exits from 21:00 CT, weekend holds); zero / wrong-side swing risk is
  accepted (no positive-distance check); the filled 15-min bar is unprotected under bar-close calculation; break-even
  can arm on the bar's high from before the fill; roll accounting only partly corrected; the 2023+ window was reused and
  the redesign failed 2 of 4 of its own validation checks; the best 10% of trades make 232% of the net.
- My add: at ~320 trades a year it has the most statistical power of anything the author sent, so it is worth a proper
  test; the cost units in the PDF ($2.50 per contract + $5 per trade on 1 MNQ?) need checking: if they are per MNQ the
  backtest is very conservative, if per NQ / 10 they match ours.
- Needed from the user: both native MC reports (.xlsx). **User, 2026-10-23: C03 is the intraday (Apex-shaped) version of
  Kusho.** Its code differs from the PDF's 15:45 run ($27,203 / PF 1.36: same 70-tick rules, flat 15:45), so that number
  doesn't describe C03; C03 needs its own report. Evening-hold versions → personal-account candidate.

## C03 (Kusho's intraday version per the user; source review, 0 return trials): agreed, WATCH / NEEDS DATA
- A different rule (ATR-scaled wick / risk / break-even on a 1-min chart with built 15-min slots, flat 15:45); the older
  Kusho results don't carry over. It fixes the swing-risk sign and the pre-fill break-even issue.
- Agreed open issues: protection starts only at the end of the fill's 15-min slot (up to ~15 minutes unprotected);
  a pending limit can be armed on a half-day's last bar with no flat-time veto (possible evening fill); a missing slot
  end extends an order's life; `this bar on close` flattens without a margin; no stop-through fallback.
- The $20-per-point guard is fine on our @NQ charts that route MNQ orders (the chart symbol is @NQ); it only blocks an
  @MNQ chart. Needed: C03's own native report and settings before any test.

## OB v2 (Codex replay and account test, pre-registered 7d7714b): accepted, keep the current plans
- Standalone (our costs): 568 trades, $374 per NQ, PF 1.69, t 4.73, DSR 0.98; design 2018-22 t 3.0, 2023+ t 3.7; shorts weak.
- **But:** the ATR-regime filter was chosen by its author with 2023+ already seen; random entry TIMES on the same days
  beat the actual breakout in 77 / 100 paths (the edge is in which days, not the breakout); 2018 near zero.
- Accounts (registered gates): replacing ONB ML funded year 1 $9,294 → $8,086, blown +11.7 pts; evaluation pass
  50.2% → 43.4%; as a 1-MNQ addition no gain (49.3%). Every gate fails. Keep ONB ADX30 / ONB ML.
- Ranked B in TIER_LIST (strong standalone, adds nothing, day-selection edge).

## Message for Codex
```
Reviews: agents/codex/results/REVIEW_c03_kusho_obv2.md (claude branch). All three agreed.
OB v2: accepted, ranked B, plans unchanged; the 77/100 timing null is the key finding, thanks.
Kusho / C03: the user says C03 IS Kusho's intraday version (so no separate 15:45 file is coming). Wait for the native
reports, above all C03's own (user). When they arrive:
parity first (no return trials before it), then one pre-registered test of the Apex-shaped version with an entry-bar
backstop and a positive-risk check as a separately frozen amendment.
```
