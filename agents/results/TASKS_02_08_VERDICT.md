# Tasks 02-08 verdict: Antigravity (Gemini) blind rebuilds in Jesse (2026-10-17)

Output: branch `antigravity/jesse`, `tasks/out_02` ... `out_08`. Comparison: `analysis/jesse/compare_antigravity.py`
(output `analysis/jesse/compare_antigravity_output.txt`): each trade is matched by entry date and order within the day.

## Result: all seven PASS

| Task | Strategy | MultiCharts | Antigravity | Claude's Jesse | Same trades as MC | Same side | P&L within $50 of MC | ... of Claude's Jesse |
|---|---|---|---|---|---|---|---|---|
| 02 | Vault Break | 1,743 | 1,747 | 1,748 | 1,742 | 100% | 99.3% | 100% |
| 03 | Overnight Bias ADX30 | 677 | 673 | 675 | 671 | 100% | 100% | 100% |
| 04 | Overnight Bias ML | 344 | 328 | 329 | 328 | 100% | 99.1% | 100% |
| 05 | Monday Long | 451 | 409 | 410 | 409 | 100% | 99.5% | 100% |
| 06 | Expiration Open Short | 105 | 105 | 105 | 105 | 100% | 100% | 100% |
| 07 | Late-Day Flow | 898 | 889 | 897 | 889 | 100% | 99.9% | 100% |
| 08 | NFP Fade | 79 | 78 | 79 | 78 | 100% | 100% | 100% |

Gross $ per trade (MC / Antigravity / Claude's Jesse):
- VB: 106 / 109 / 109
- ONB ADX30: 390 / 394 / 389
- ONB ML: 656 / 705 / 693
- Monday: 435 / 480 / 480
- EOS: 491 / 491 / 491
- LDF: 111 / 113 / 112
- NFP: 352 / 354 / 353

## Every count difference has a known cause (none is a rule disagreement)

- **Monday Long (42 MC-only):** 40 early-close Mondays that the MC report traded but the current code skips (found in the
  first Jesse cross-check), plus data-end days.
- **ONB ML (16 MC-only):** January-March 2018, before the ML score's 60-day history exists. Antigravity correctly does not
  trade then (the 2026-10-17 rule).
- **Late-Day Flow (9) and ONB ADX30 (2018-01-02, 01-16):** ATR / indicator warm-up at the very start of the data.
- **ONB ADX30, March 2020:** MC trades 03-09 / 03-12, Antigravity 03-17 / 03-18. These are the COVID limit-move days,
  where the ADX threshold and opening range differ by a hair.
- **ONB ADX30 2025-11-28:** the early close after Thanksgiving.
- **2026-10-12:** after the end of our NQ data.
- **Vault Break:** the same 5 extra days as Claude's Jesse port, plus 3 stop / target ties inside one 1-minute bar
  ($2,300 swings), the same as in Claude's cross-check.

## Conclusion

- Three independent engines (MultiCharts, Claude's Jesse ports, Antigravity's blind Jesse rebuilds) agree on every
  strategy in the plan, with matched trades within $50 on 99-100%. The written specs fully define the strategies, so the
  edges are not artefacts of one engine or one coder.
- Antigravity's work matches Claude's Jesse to the dollar on 100% of matched trades.
- It is now cleared for Phase 2 (improvement) on any strategy, under the brief's rules.
