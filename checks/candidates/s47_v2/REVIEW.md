# S47 / S47 v2 (Europe-Open Impulse): Claude's review, 2026-10-23

Source: the user's PowerLanguage files (`S47.txt`, `S47_v2.txt`) and overview PDF (same author as FC 2B). Rebuild
`analysis/s47_test.py` (output `analysis/outputs/s47_test_output.txt`), benches `analysis/s47_bench.py`
(`analysis/outputs/s47_bench_output.txt`). Codex's source review: codex/work `agents/codex/results/s47_source_review.md`.

## Rebuild (2018-26, per NQ after $7.25 + 1 tick per fill)
Matches the author's MultiCharts years closely (2020 $29.3k vs $28.8k, 2022 $59.6k vs $57.6k, 2024 $4.8k vs $5.0k,
2025 $58.2k vs $58.5k). v2: 714 trades, $346, PF 1.51, **t 4.1**, 9/9 years; 2018-22 $366 (t 3.6), 2023+ $321 (t 2.3);
longs $273 (t 2.5; 2023+ t 1.2), shorts $429 (t 3.3); Sharpe 1.35, Sortino 2.69, Calmar 1.73, Ulcer 2.9, max DD $15.7k.
Plain S47: 1,421 trades, $229, PF 1.32, t 3.9, lost 2024.

## Controls
- Random side $54 (max $178); opposite side −$269 (t −3.2). Stop 0.4 / 0.6 and threshold 0.03 / 0.125: $275-346.
- **Does London add beyond New York's first hour? (Codex's control)** New York direction alone, every day: $108 (t 2.3;
  2023+ t 1.0). Split by London: agrees (= v2) $346; opposite −$92; too small $69. London-agree minus the rest $356 a trade
  (t 3.5; 2018-22 t 2.9, 2023+ t 2.2). London carries the edge; New York's hour alone is weak.

## Benches (same as FC 2B)
- 50K funded bootstrap: + 1 MNQ $9,519 / $11,976 vs plan $9,354 / $12,088, blown 8.0% vs 7.0%; 2 MNQ blown 18%;
  + S47 1 + FC 2B 1 worse; in place of RS longs a tie ($12,108 vs slot empty $12,125).
- Combine + 1 / 2 / 3 MNQ: pass 49.7 / 48.5 / 47.0% vs 50.1%.
- **Adds nothing to either Apex plan** (the funded plan is near the payout cap). Corr with the plan +0.28, RS +0.19-0.28, FC 2B +0.19.

## Concerns (with Codex)
1. ~3,700 settings searched; the New York agreement was added after 2023+ had been seen (the author says so).
2. Not a forced flow: cross-session momentum.
3. Code (both versions): entry minute unprotected (stops start one bar later, no SetStopLoss); no fallback when a stop is
   already through the market; `this bar on close` exits; the next-session safety flatten acts only after a carry; plain
   S47's date limits end 2022-12-31 by default.

## Verdict
B now (rebuild only; A on its numbers once the MultiCharts reports confirm it). Not for the Apex plans; candidate for the
personal account and the forward log after (1) both MC reports (.xlsx), (2) a fixed v2 code (entry-bar stop, fallback,
explicit 15:00 / early-close exit).

## Update 2026-10-23: fixed code and days to pass
- **`S47_v2_fixed.txt`**: rule unchanged; [X] lines add an entry-bar backstop (`SetStopLoss` at the rule's stop + 1 tick),
  a market exit when the rule's stop is already through the close, and a guard so the backstop is never armed at zero.
  Exits stay the 15:00 `this bar on close` (a market order at the bar close live); holiday / early-close sessions are
  skipped by the rule, so no session ends with a position open. Needs a MultiCharts run before any use.
- **Days to pass the 50K evaluation** (`analysis/combine_days_test.py`): median 6 days with or without S47 v2 / FC 2B
  (S47 3 MNQ: 5); mean 7.4 → 7.2 / 7.0 / 6.6 (S47 1-3 MNQ) and 7.1 / 6.7 / 6.3 (FC 2B 1-3); passes within 10 days
  37.7% → up to 41.9% (FC 2B 3 MNQ), but pass rates fall (50.1% → 47.0-50.0%): faster passes, slightly more fails.
