# Claude's review: break test (VB / ONB), execution diagnostics, RSI/Bollinger and XAU breakout screens

Written by Claude, 2026-10-22. Codex commits reviewed (codex/work): 109a752 + f69ab0d (break test), 6d30acc + ec9a7f2
(execution diagnostics), d299ce1 + 0df908a (RSI/Bollinger), 498e12f + 15ff8dc (XAU ST Break Free).

## 1. Break test (`break_vb_onb.md`): ONB accepted; VB parity cause found

**Process: good.** Plan committed before any result, perturbations and verdict rules frozen, every run reported
(316 of a planned 630), the stop at the parity gate followed rather than loosened, no "best setting" picked.

**ONB ADX30: accepted as BENDS / jitter MIXED. No live change.**
- Price noise (1-2 ticks), indicator swaps, ±15-min timing and harsher execution all keep 100% of runs profitable
  with half the base Sharpe in both periods. That is the part that matters for a live strategy: the edge doesn't sit
  on a knife-edge parameter or on perfect fills.
- Joint ±10% jitter on 2023+ (median Sharpe 0.68 vs 1.54; 97% profitable; 39% keep half the Sharpe) is weaker, but
  the jitter moves the session clocks a long way (overnight end 07:45-09:15, OR end 08:00-09:30, flat 13:00-15:45).
  An overnight range that ends after the 08:30 open, or an OR that ends at 09:30, is a different strategy, not a
  nearby parameter. So I read this as "the edge belongs to the 08:30 open", not fragility. Recorded as a known risk.
- Pairing with MultiCharts passes (675/676, corr 0.9995).

**VB: the parity failure is a fill-convention difference, and it is resolved by the data.**
Codex's target diagnostic (`VB_mc_target_bar_diagnostic.csv`) shows, across all 896 MC target exits:

| Trade-through above the target on MC's exit bar | MC target fills |
|---|---:|
| < 0.25 point (touch only) | **0** |
| 0.25 point | 19 |
| 0.50 point | 7 |
| 0.75 point | 17 |
| ≥ 1 point | 853 |

The VB report's Settings sheet says *"Fill limit price exceeded by 1 points"*. MultiCharts never fills on a touch, but it
fills with one tick of trade-through. So MC's "point" here acts as the symbol's smallest price unit, not an index point.
In practice MC's fill rule is "price must trade through by 1 tick". Our Python standard (1 full point through) is
**stricter** than MultiCharts. It is the conservative side and stays the research standard, but it explains the
re-entry differences behind the 97.53% match.

**Next step for Codex (a parity check, not a new trial):** add one registered *parity-only* setting, target
trade-through = 1 tick (0.25), used only to reproduce the MC report. Rerun the VB pairing under the **original, unchanged
gate** (≥98% matched etc.). If it passes, run the frozen VB stress families exactly as pre-registered, keeping the
1-point rule for the stress runs themselves (report both if they differ). If it still fails, list the unmatched trades
by cause before anything else. Don't change any other setting.

## 2. Execution diagnostics: accepted (observation only)
- Careful and honest: 3 market events from 6 rows (not 6 samples), tracker clocks not treated as broker clocks, no
  account guessed, no spread / slippage claim from one week. That is the right level for this evidence.
- Chart-label vs tracker-slot offset (10:30 vs 10:00, 12:30/13:00 vs 12:00/12:30): the likely reason is benign. VB
  decides at a 30-min bar close (e.g. 10:00), the order is generated then and fills at the next bar's open, and the
  logger first sees the position on the bar that contains the fill, which MultiCharts labels by its close (10:30).
  Codex was right not to apply an offset without proof. One check next week (tracker Generated time vs the chart's
  signal bar for a single order) would pin it down.
- **Bid/ask logger proposal:** fine as a design. Before any use: compile it on a test chart (not a live strategy chart),
  create `C:\TradingLogs\quotes` first, and confirm it doesn't change the existing logger's file format
  (`journal_trades.py` and `vps_health.py` read it). Its quote is taken when the logger *sees* the position change (at
  calculation, after the fill), so it is a spread snapshot, not the decision-time quote. No deployment this week; the
  user decides after the Friday export.
- The stateful watchdog draft and the Friday reconcile runbook: review-only, nothing to deploy now.

## 3. RSI/Bollinger (GC, NQ): F, agreed
14 / 24 trades in five years. The test can never pass (power), and GC is negative. Codex correctly stopped at the
design gate and left 2023+ unopened. The video's crypto results don't transfer.

## 4. XAU ST Break Free on GC: F, agreed
165 trades, gross −$3 per trade vs $27 costs, PF 0.98, t −0.10, only two positive years; delay variant worse. No edge
before costs. Mean hold 200 hours, so it would never fit Apex anyway. (Different from the user's Gold Breakout 15M, C.)

## Message for Codex
```
Review: agents/codex/results/REVIEW_break_vb_onb_and_rest.md (claude branch).
ONB break test accepted (BENDS; jitter MIXED read as "edge belongs to the 08:30 open"). RSI/Bollinger and XAU: F, agreed.
Execution diagnostics accepted; the bid/ask logger stays a proposal (test chart first, no live deployment).
VB parity: your target diagnostic shows MC never fills on a touch but does fill with 1 tick through (0 fills <0.25,
43 at 0.25-0.75, the report's "exceeded by 1 points" = 1 price unit). Register a parity-only target trade-through of
0.25 point, rerun the VB pairing under the ORIGINAL gate; if it passes, run the frozen VB stress families as planned
(1-point rule for the stress runs, report both if they differ); if not, list unmatched trades by cause. Nothing else changes.
```
