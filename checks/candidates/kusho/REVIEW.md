# Kusho FAR / v9 and C03: Claude's tests, 2026-10-23

User: "assume the reports agree, test them". Rebuilt from the code (`analysis/kusho_test.py`, fills and exits minute by
minute; output `analysis/outputs/kusho_test_output.txt`); benches `analysis/kusho_bench.py` (`..._bench_output.txt`).
Codex's source reviews: codex/work `agents/codex/results/{kusho,c03}_source_review.md`.

## Standalone (2018-26, per NQ, $7.25 + 1 tick per stop / market fill; limits need 1 tick through, targets 1 point)
| Version | Trades / yr | $ / trade | PF | t | 2018-22 | 2023+ | Years + |
|---|---|---|---|---|---|---|---|
| FAR (exit 21:00, weekend holds) | 311 | $97 | 1.34 | 4.6 | $93 (t 3.8) | $102 (t 2.7) | 9/9 |
| v9 (+ shorts on DOWN days) | 359 | $108 | 1.37 | 5.3 | $108 (t 4.5) | $108 (t 3.0) | 9/9 |
| v9 flat 15:45 (Apex-shaped) | 359 | $92 | 1.33 | 4.8 | $89 (t 3.9) | $95 (t 2.9) | 8/9 |
| C03 (user's intraday version) | 398 | $64 | 1.19 | 3.2 | $43 (t 1.9) | $93 (t 2.6) | 7/9 (2018, 2019 lose) |
- Rebuild ≈ author: FAR $9.69 per MNQ vs $10.01. Fills on touch (author's setting) add ~10% to each.
- Placebo (random signal bars, same limit order and exits): FAR $21, v9 $0, C03 −$12 a trade. EMA condition matters most
  (without it FAR $49, C03 $33); the wick condition adds a little (FAR $84 → $97).
- **Weekend holds:** FAR's 122 weekend trades = $115k of $264k (44%); v9's 134 = $137k of $341k (40%). Without them FAR
  $57, v9 $68 a trade: a large part of the 21:00 versions is the market's weekend drift, not the pattern.
- Tail: the best 10% of trades carry all the profit (FAR $668k vs the rest −$405k per NQ).
- Metrics: v9 Sharpe 1.78, Sortino 3.41, Calmar 2.08, max DD $18.1k; v9 15:45 Sharpe 1.60, max DD $19.8k; C03 Sharpe 1.06,
  max DD $31.1k, Ulcer 21.6. Shorts 2023+: v9 t 1.4, C03 t 0.8.

## Apex benches (Apex-shaped versions only)
- 50K funded bootstrap: + v9 15:45 1 MNQ $9,551 / $11,929 vs plan $9,354 / $12,088, blown 8.5% vs 7.0%; 2 MNQ blown 20.8%;
  + C03 1 MNQ worse ($8,934 / $11,774, blown 9.6%). **VB → v9 15:45 1 MNQ: $9,083 / $12,177, blown 5.7%** (vs plan −$271
  year 1, +$90 year 2, −1.3 pts blown; vs the VB slot empty +$857 / +$157): a trade-off, not a clear win. RS longs → v9 a tie.
- Combine: + v9 15:45 1-3 MNQ 49.2 / 47.1 / 46.8% vs 50.1%; + C03 48.5 / 46.7 / 43.4%; VB 8 → v9 15:45 4 / 8: 44.2 / 39.0%.
- Corr: v9 15:45 with VB +0.31, LDF +0.20, RS +0.19; with C03 +0.67.

## Verdict
- **Kusho v9: B** (t 5.3 but PF 1.37 < 1.4 and 40% of the profit from weekend holds); personal-account candidate.
- **Kusho v9 flat 15:45: B**, the best Apex-shaped version; not added (adds nothing; replacing VB trades year-1 money for
  a lower blown rate). If VB ever weakens live, it is the first replacement to test. Needs its own MC run + entry-bar stop.
- **C03: C** (weaker than plain v9 with a 15:45 flat; 2018-22 t 1.9). The ATR redesign didn't help.
- FAR: superseded by v9.

## Roll-adjusted indicators (Codex's cross-review, 2026-10-23; replay registered before running)
The code removes contract-roll gaps before EMA / ATR / regime / swings; my first test fed raw prices. Corrected replay
(`analysis/kusho_roll_adjusted_replay.py`): 98.9-99.9% of entries identical; FAR $97 → $97, v9 $108 → $107 (t 5.2),
v9 flat 15:45 $92 → $91 (t 4.8), C03 $64 → $62 (t 3.2). Rankings unchanged (v9 B, v9 15:45 B, C03 C); benches not rerun
(changes far smaller than the bench differences).
