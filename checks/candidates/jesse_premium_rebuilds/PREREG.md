# Premium rebuilds by matching, round 2 (pre-registered 2026-11-13, before any search result)

User: "go on to the rest of em" after the TrendSwingTrader V2 rebuild (checks/candidates/tst_v2_rebuild/). Same method: the free
parent's code with a settings grid, scored by F1 between the candidate's in-position days and the premium's in-trade days on the
site's daily equity curves (jesse.trade metrics endpoint, user-approved; scratch_data/jesse_site/). Day shift 0 (fixed by the V1
calibration). Search fills on 15-min bars for speed; the accepted rebuild is then tested with 1-min fills.
Fit years: 2022 + 2023. Check years (never used to pick): 2024 + every available quarter of 2025-26.
Accept a rebuild if its check F1 >= 0.6 and within 0.10 of its fit F1 AND above the parent code's own check F1 (else: the premium
is not its parent with new settings). Ceiling per family = the parent code vs the parent's own site curve.

| Premium | Parent (free code) | Grid |
|---|---|---|
| AlligatorV2 (30m) | AlligatorAi | ADX > {20, 25, 30, 35, 40} x CMO {10, 20, 30} x StochRSI {10, 20, 30} (long below x, short above 100 - x) x stop {1.5, 2, 2.5, 3} ATR x target {1.5, 2, 3, 4} ATR x 4h EMA {50, 100, 200} = 2,160 |
| TrendWaveRiderV2 (15m) | TrendWaveRider | ADX > {30, 40, 50} x SMA pair {10/30, 25/50, 50/100, 20/100} x CCI {50, 100, 150} x stop {2, 2.5, 3, 3.5, 4} ATR x target {2, 3, 3.5, 4, 5} ATR = 900 |
| Turtle V2 (1h), Turtle V3 (1h) | TurtleAI | Donchian {10, 20, 30, 55} x 4h SMA {100, 200} x ADX > {20, 25, 30, 35} x Choppiness < {35, 40, 45, 50, off} x trailing stop {1.5, 2, 2.5, 3, 3.5} ATR = 800 each |

Accepted rebuilds get the standard test on our data (2018-06 -> 2026-10, 1-min fills, costs, 2018-21 unseen, placebo).
Each premium counts as one item with its grid size as variants in trials.py.
