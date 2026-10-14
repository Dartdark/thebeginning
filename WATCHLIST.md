# Watchlist

Ideas that looked promising but aren't proven enough to change the plans yet. Each entry says what the evidence is,
what would promote or drop it, and when to look again. Recheck with the listed script after new data comes in
(gamma: re-export `GEX_1min_<year>.csv`; plan trades: new MultiCharts reports).

| # | Item | Evidence so far | Promote if | Drop if | Recheck | Script |
|---|---|---|---|---|---|---|
| 1 | **Late-Day Flow sized by the 0DTE gamma flip at 14:00** (3 MNQ below the flip, 1 above, 2 with no gamma reading) | LDF below the flip $158 / trade (PF 1.64, t 2.0) vs above $36, in both halves of 2023–26; every-day 14:00→14:30 follow $127 vs $28 (placebo p 0.09). Funded bench, 2023+ starts: $10,924 vs $10,489 a year, blown 3% vs 7%, above the shuffled-regime placebo's 95th percentile. In-sample, 2.3 years | Below − above stays ≥ ~$80 a trade on the new months, and the funded gain survives on the out-of-sample stretch (after 2026-07-07) | The gap closes or flips on 6+ new months of data | When the next gamma export covers 2026-07 → 2027-01 | `analysis/gamma_momentum_test.py`, `analysis/ldf_gamma_sizing_check.py` |
| 2 | Open-breakout pullback, 15-min bars (longs, 0.15% break, 3R) | t 2.4, controls clean, but best of 120 combinations; funded neutral at 1 MNQ, combine worse | Positive on new trades (2026-10 →) at the same settings | Negative over the next ~50 trades | Every 6 months | `analysis/open_pullback_15m_test.py` |
| 3 | Vault Break in September | 7/9 years positive overall but September weak; 1 of ~170 time cells | September 2027 weak again (would make a filter worth testing) | September positive again | October 2027 | `analysis/time_clusters_test.py` |
| 4 | DriftPullback shorts 1 MNQ in the funded plan | Within noise (median 245 vs 255 days to $13k), weak since 2023 | Holds up on new data | Keeps fading | Every 6 months | `analysis/funded_today_check.py` |
| 5 | Vol-Control Sell above the gamma flip | Above $1,331 vs below −$262 a trade, t 2.5 on 27 trades | 15+ more trades with the same split | The split shrinks | With the next gamma export | `analysis/gamma_regime_test.py` |
| 6 | Gold Asian-range breakout on MGC (user's file, as described) | GC 2018–26: $83 a trade per GC, Sharpe 0.66 (2023+ 0.88), placebo $1, uncorrelated with the plan; but +0.045 R in risk units (t 1.4), 61% losers, worst 20-trade run −$4,193 per MGC; funded bench worse at every size | A filter that cuts the losing streaks (range width vs ATR, London timing) tested in 2018–22 holds in 2023–26 and the funded bench improves | The filter search fails or 2026–27 trades go negative in R | Next research slot on gold | `analysis/gold_asian_breakout_gc_test.py` |

Added 2026-10-14. Move an item to the plan or to `TIER_LIST.md` (and off this list) once its recheck decides it.
