# GC risk-adjusted: REJECT supplied configuration for the current plan

Summary: Keep the current plan; this code does not establish a profitable or useful addition.
Its $20,000 nominal risk budget is ten times the plan's $2,000 trail, and changing GC to MGC does not fix that budget.
The range endpoints shift on close-stamped bars; entry protection and daily Data2 availability need platform confirmation.
Related gold breakouts are already parked; this different ADR/drift version has no supplied report or independently verified results.
No new returns, account simulations, source fixes or live changes were made.

Scope: `agents/codex/plans/gc_risk_adjusted_source_review.md` (source-review record, not backtest preregistration).
Evidence: `agents/codex/evidence/gc_risk_adjusted.md` (NEEDS DATA).
Input: unchanged `agents/codex/inputs/gc_risk_adjusted/source.txt`, copied from the user's `GC - RISK ADJUSTED.txt`.
Script/output: `analysis/codex_gc_risk_adjusted_review.py`, `analysis/outputs/codex_gc_risk_adjusted_review/summary.json`.
New strategy-return trials / account simulations: **0 / 0**. Source author's trial count and selection history: unknown.
Context: Codex `9d8c1b4b0c33441a432aad508eea6eb239b26e7a`; Claude `b1256664232722b25afefc0004e6f9e04c1976ae`.

## Rule as delivered

GC five-minute Data1 plus daily GC Data2. Build an evening range, retain a session only if the absolute regression drift
relative to range clears the filter, then place buy/sell stop entries at its edges. Default intention is one trade per range
session. Freeze daily ADR at the range close; stop is 140% ADR, target 100% ADR long / 110% short, morning time exit 10:00 CT.
Dynamic sizing floors dollar budget divided by per-contract stop exposure and caps the result. This is a price-based breakout
hypothesis; the file provides no observed forced flow or independent economic evidence for the filter.

## 1. Supplied risk settings are incompatible with Apex sizing

Source lines 29-34 use dynamic sizing, **RiskPerTradeUSD = $20,000**, **MaxContracts = 20** and ForceMinOneContract=false.
Lines 203-222 compute `min(20, floor(20000 / (stop_points * BigPointValue)))`. This bounds modeled stop risk by the input
budget, not by account cushion or the portfolio's remaining loss allowance. Actual allocated risk can be below the budget;
it is incorrect to say every trade necessarily risks exactly $20,000.

CME specifies GC as 100 ounces, MGC as 10; their dollar values per 1.00 price point are $100 and $10 respectively.
[CME Gold overview](https://www.cmegroup.com/education/lessons/product-gold),
[CME Micro Gold specifications](https://www.cmegroup.com/education/lessons/micro-gold-and-micro-silver-futures-product-overview.html).

For illustration only, **ADR = 50 price points** (not a measured current or historical ADR):

| Chart instrument | Stop, 1.4 ADR | Risk per contract | Contracts from source | Nominal stop exposure |
|---|---:|---:|---:|---:|
| GC | 70 points | $7,000 | 2 | $14,000 |
| MGC | 70 points | $700 | 20, capped | $14,000 |

Changing the symbol therefore does not automatically make the configuration suitable. The cap counts contracts;
it is not an account-loss control. Commissions, adverse slippage and gaps are excluded from the budget, as the source
itself states. Even budgeting the whole $2,000 trail per trade would leave no room for those items or the existing plan.
No replacement risk input is selected in this review; lowering size would not by itself establish an edge.

The sizing structure has good features: correct instrument multiplier, integer floor, position-wide dollar amounts, and
skipping when one contract exceeds the budget rather than forcing a minimum. Keep those separate from the unsuitable input.

## 2. Range and first-break semantics need a precise specification

With five-minute **close-stamped** bars and the default zero time shift, lines 111-114 include labels 20:00 through 23:55
and exclude 00:00. Their price intervals cover approximately **19:55-23:55**, rather than 20:00-00:00. This affects range
high/low and the regression input. The midnight bar is then used by the strict-break conditions (239-242), despite being
excluded from the range. A move may have crossed an edge before the first orders are submitted at 245-253.

This is a confirmed endpoint difference under the stated close-stamp convention; whether it is a bug in the intended
strategy depends on the original chart convention. It does **not** imply a mandatory five-minute delay after midnight:
next-bar orders can be active on the next tick around 00:00, on the bar labeled 00:05. Likewise the 10:00 time-exit calculation
can produce a next-bar-market fill around 10:00, not necessarily 10:05.
[MultiCharts calculation/order lifecycle](https://www.multicharts.com/trading-software/index.php?title=How_Scripts_Work).

`AbsValue(slope)` at line 179 is nondirectional: sufficient upward or downward drift can arm both eligible breakout sides.
It is not a requirement that the breakout agree with the Asian trend. That is literal source behavior, not necessarily a defect.
The source can also accept a partial window meeting MinBars rather than verifying complete session coverage.

## 3. Protection and Data2: unresolved settings dependencies, not invented bugs

- **Entry protection:** `SetStopLoss` and target calls occur only in MarketPosition=+/-1 branches (257-271), and the amount
  depends on CurrentContracts. They are not explicitly initialized while flat when entry orders are issued. Built-in
  stops can operate intrabar and on the entry bar; that fact alone does not prove a correct fresh amount is installed
  before this script's first fill. Treat first-fill activation/stale amounts as a readiness concern requiring a small
  platform trace, not as a measured missing-stop loss. Pin IOG and Bar Magnifier settings; the file does not specify them.
  [Official SetStopLoss behavior](https://www.multicharts.com/trading-software/index.php?title=SetStopLoss).
- **Daily ADR:** line 100 reads unlagged `Average(High-Low, ADRLen) of data2`; line 165 locks it. The comment says the
  last completed daily bar. MultiCharts Realtime-History Matching, enabled by default, uses the completed auxiliary bar;
  disabled it can use an unfinished bar. Thus lack of `[1]` does **not** prove look-ahead. Blindly adding it could introduce
  an extra lag. Confirm Data2 date/session/value at midnight in historical and real-time calculation, with settings fixed.
  [Official Realtime-History Matching documentation](https://www.multicharts.com/trading-software/index.php?title=Realtime-History_Matching).
- **Trade count and dollar conversion:** TotalTrades plus ActiveTrades (139-142) handles ordinary sequential trades;
  no routine off-by-one defect was found. SetStopPosition with distance times BigPointValue times CurrentContracts is
  consistent position-wide arithmetic. Same-bar two-sided crossings/OCO behavior still need platform evidence; no double
  fill or reversal is claimed here.

The source's E-mini session-template label also needs reconciling to the actual GC chart, daily bars and closures.
No chart was opened or changed. No source was compiled, repaired or deployed.

## 4. Against the plan and the earlier gold research

Gold Asian-range breakout is already **C / parked by the user** in the latest tier list and watchlist item 6. Earlier work
used range-based stops and other entry/exit filters. A later saved rebench (`analysis/gold_btc_next_test.py`) found low
correlation yet lower funded payouts: $9,668 / $12,295 versus $9,818 / $12,595, blown 7% versus 4%. Those are published
results for an earlier rule and an earlier plan snapshot, **not** new results for this upload or today's paired benchmark.

This version materially changes exits to daily ADR and adds the absolute regression filter. No exact matching result was
found. Prior weak results do not establish that this version loses; prior low correlation also cannot be transferred to it.
A different market and overnight clock are only a diversification hypothesis. Macro shocks can affect gold and index legs
together, and a later gold gain may arrive after a funded-account breach.

No performance report, List of Trades, costs, selection history, current-version parity export, holdout statistics or
paired add/replace/empty-slot account test accompanies this file. Profit factor, t, Sharpe, Sortino, Calmar, Ulcer,
bootstrap intervals, actual drawdown and incremental payout value are therefore **unknown**, not zero. The title
"risk adjusted" describes a position-sizing mechanism, not demonstrated risk-adjusted investment performance.

## Decision and smallest next evidence

**Do not add this version or replace a plan leg on the supplied evidence; do not use the supplied sizing.** Retain the
existing parked status without ranking the new variant. The next useful evidence is the existing exact-version MultiCharts
report/trade export plus chart properties (Data2, session/clock, IOG, magnifier and matching), original inputs, costs and
selection history. A targeted first-entry/stop and daily-ADR trace would resolve the implementation concerns.

Any changed-rule return test would need a separate committed preregistration, trial accounting and the latest independent
statistical gates before the bootstrapped current-plan addition/replacement/empty-slot bench with intraday paths. No new
backtest, parameter fix, paper/live test or revival of the parked research was started. Two independent read-only subreviews
checked source semantics and prior plan context; that is not a strategy-checker PASS or a profitability certificate.
