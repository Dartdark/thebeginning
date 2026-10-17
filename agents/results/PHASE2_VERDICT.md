# Antigravity Phase 2 + new idea: Claude's verdict (2026-10-17)

Source: branch `antigravity/jesse`, commit 251f937 (`tasks/out_01..08/improve_*`, `tasks/out_new_es/`).
Task 09 (ES MOC Follow blind check) is not in it yet.

## Phase 2: 8 strategies, 40 pre-registered variants (5 each)

Antigravity followed the rules: a written plan before testing, chosen on 2018-22, one holdout run on 2023-26, the gate
"beat the original on net $ AND drawdown in BOTH periods". **No variant passed; every original is kept.**

| Task | Strategy | Best design variant | Holdout | Gate |
|---|---|---|---|---|
| 01 | CL Sunday Fade | 0.50 ATR stop | more $, bigger DD | keep original |
| 02 | Vault Break | green trigger bar (V4) | $62k vs $81k | keep original |
| 03 | ONB ADX30 | 11:00 cutoff + ADX 32 | both worse | keep original |
| 04 | ONB ML | symmetric score + 0.25 ATR stop (V5) | DD −35%, $ −3% | keep original |
| 05 | Monday Long | first hour up (V1) | $107k vs $148k, DD worse | keep original |
| 06 | Exp. Open Short | gap skip + limit target (V5) | $ lower | keep original |
| 07 | Late-Day Flow | move ≥ 0.50 ATR (V1) | DD −40%, $ −8% | keep original |
| 08 | NFP Fade | reaction ≥ 0.10 ATR (V1) | DD −10%, $ −4% | keep original |

Its own "funded-account options" (ONB ML V5, LDF V1, NFP V1) were picked AFTER seeing the holdout, so they are new
trials, not validated improvements. The most promising one, **LDF V1, on the bootstrapped funded bench**
(`analysis/antigravity_phase2_bench.py`, current plan VB 2 / 1 + ES MOC 2 MES): 2-year payouts +$67 / +$70, blown −0.5 pt,
better in 50.4% of paired histories = **a wash; no change.** (0.50 ATR was already inside the LDF threshold grid when
LDF was built.) The pattern is a known one: the original rules are already near their best, and every filter that
looks better in 2018-22 gives the money back in 2023-26 (Monday V1 is the clearest case).

## New idea: ESEuroCloseTrend (ES, 15 min) — F

Rule: at 10:30 CT (European close) follow the 8:30 → 10:30 move if ≥ 0.25 ATR, above / below VWAP, ADX ≥ 20; stop 0.30
ATR, target 0.75 ATR, out 15:00.
Rebuilt on our data (`analysis/es_euro_close_check.py`): 858 trades (its 844), **$53 a trade, PF 1.13, t 1.4**, 5 of 9
years positive, worst drawdown $24.5k per ES; Sharpe 0.77. Its own numbers match ($59, design 2018-22 weak).
Placebo: deciding at 9:30 gives the same $56; 10:00-13:00 give −$7 to $37. ADX and VWAP add ~$15-20 a trade, not
significant. Far below the t ≥ 3.5 bar; the European-close story is not visible in the data. **F.**

## What to send Antigravity next
- Task 09 (ES MOC Follow blind check), the one still open.
- Phase 2 is finished; no more improvement rounds on these 8 unless a new mechanism comes up.
