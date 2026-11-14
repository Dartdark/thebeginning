# ZiadFrancis/Reinforcement_Trading_Part_2 (PPO gold agent): tested 2026-11-14 — F

User: "Look at this git and test the code(s)" (https://github.com/ZiadFrancis/Reinforcement_Trading_Part_2).

**What it is:** PPO agent (stable-baselines3) on XAUUSD H1 decisions. Each hour it picks long / short / flat plus an SL bucket
(1 / 1.5 / 2 ATR) and a TP bucket (1 / 1.5 / 2 / 3 R), 25 causal features. Brackets are simulated on M1, SL first when both are hit
in one minute, and it risks 0.5% per trade. Sliding walk-forward: 5y train, 6m checkpoint selection, 6m out-of-sample test, 6m step.
No trained model is published. Code review: features causal, resample right-labelled, no look-ahead found.

**How tested:** their code unchanged (cloned to the scratchpad, own venv: torch 2.15 CPU, SB3 2.9.2), on our GC 1-min 2017-12 ->
2026-10 (roll-adjusted, converted to their EET open-stamped format). Costs = 1 GC tick + $7.25 per round trip (0.4625 pts per side;
their XAUUSD default was 0.12 per side). Default 3M steps a fold, seed 42, 8 envs; 6 folds, test windows 2023-06 -> 2026-06.

| On the same 6 test windows, same simulator and costs | Trades | Sum R | t |
|---|---|---|---|
| **PPO agent (their pipeline)** | 318 | **+33.1R** | 1.35 |
| Always long, SL 2 ATR / TP 3R | 501 | +79.3R | 1.94 |
| Their EMA trend_hold baseline | 557 | +70.8R | 1.72 |
| Always long, SL 1.5 ATR / TP 2R | 1,364 | +34.8R | 0.65 |
| Always short | 1,505 | -263.3R | -4.99 |
| Random actions, 20 seeds | | about -753R (p95 -681) | |

- Agent by fold: +2.2 / -3.5 / +0.4 / +6.9 / +19.5 / +7.6 R (5 of 6 positive). Longs +25.9R (137 trades), shorts +7.2R (181).
  Long 60% of the time in a trade.
- Its own deployment gate FAILED (worst fold PF 0.46 < 0.9). Stitched OOS: +17.1%, PF 1.17, max DD -12.6%.
- The author's notebook claims about +80R over 5 folds from Dec 2023 to May 2026 (XAUUSD, tighter costs). That is no more than
  always-long gold over a period when gold roughly doubled. Their own action-vote ensemble lost -4.5%.
- Data sweep (`analysis/outputs/rl_gold_ppo_sweep_output.txt`): no favourable subset (2023+ only).

**Verdict F:** beats random actions only because it leans long during a gold bull market; it earns less than half of plain
always-long with one bracket, t 1.35 (bar ~3). One training seed only (PPO varies by seed; the gap to always-long is large).
Nothing to build on for NQ / ES; RL bracket choice is not an ingredient worth porting.

Files: `run_rt2.py` (launcher), `rt2_bench.py` (benchmarks), `rt2_post.py` (per-trade rollout), `ppo_test_trades.csv`,
`ppo_training_log.txt`.
