# Strategy development process

Adopted 2026-10-12. Applies to every new strategy and to re-reviews of existing ones.

## Step 1: does the strategy have an edge as a whole?

Before any splitting, the full strategy (both sides together) must pass the usual checks:

- Costs: $7.25 per NQ round trip (ES $5) plus 1 tick of slippage on every market and stop fill.
- At least 2018–2026 on the 1-minute data, reported by year and for 2023 onward.
- t-stat, win rate, years positive, and the standard metrics from `analysis/metrics.py`:
  **Sharpe, Sortino, profit factor, Calmar, Ulcer index** (plus max drawdown and Ulcer
  performance). Daily $ P&L, 252 days a year, drawdown % against the $50,000 account.
- Random-entry placebo with the same stop, target and exit (`analysis/vb_random_entry_test.py`,
  `analysis/placebo_onb_eos_test.py`).
- Walk-forward / out-of-sample for anything with fitted parameters.
- Funded bench (`analysis/funded_lab.py`) and, for challenge ideas, the challenge simulator.

## Step 2: split longs and shorts

Treat the long side and the short side as two separate strategies:

| Check | Per side |
|---|---|
| Trades, win rate, average, t | yes |
| Sharpe, Sortino, profit factor, Calmar, Ulcer index | yes |
| By year, and 2023 onward | yes |
| Random-entry placebo (same days, random direction / time) | yes |
| Correlation with the other side and with the funded set | yes |
| Funded bench on its own and with the set | yes |

## Step 3: improve each side on its own

Look for side-specific improvements: filters (trend, volatility, calendar, ML), entry timing,
stop and target, time exit, and size. Each side gets the same overfitting guards as Step 1:
walk-forward for fitted parameters, a count of variants tried, and a check that the
improvement holds by year rather than coming from one period.

## Parameter searches: clusters, not the single best

Whenever parameters are searched (Step 1 or Step 3), don't take the top-scoring combination:
1. Score every combination on the design period only (2018–2022) with a robust measure
   (Calmar or funded payouts, not net profit); keep 2023 onward untouched.
2. Take the top 20%, scale each parameter to 0–1, and cluster them (k-means,
   `analysis/param_clusters.py`).
3. For each cluster, use the tested combination nearest the centre (the medoid). Prefer the
   largest, tightest cluster: a broad plateau of good settings.
4. Check the medoid on the 2023-onward holdout and in the funded bench / challenge simulator
   before adopting it. Do it separately for longs and shorts.

## Step 4: decide and recombine

For each side: keep it as is, keep it with its own settings or size, or drop it. Then put
the sides back together and run the funded bench (and the challenge simulator if relevant).
A per-side change is adopted only if the recombined strategy beats the original by more than
the noise of the estimate, in both the 1-year and 2-year payouts.

## Step 5: implement and record

- MultiCharts: one file with `EnableLongs` / `EnableShorts` inputs and separate long/short
  settings where they differ, so the side split stays visible and reversible.
- Record the per-side results in the strategy's README section and in `TIER_LIST.md`.

## Guardrails

- Each side has about half the trades, so its t-stat is lower. Don't drop a side for one bad
  year or for t < 2 alone; look at years positive, the placebo and the funded effect.
- Fitting separate models per side halves the data; prefer a shared model unless the split
  clearly wins out of sample.
- Count every variant tried; the more tries, the higher the bar.

## Status of the current strategies

| Strategy | Sides | Result of the split |
|---|---|---|
| Vault Break | Long only | Short side was tested earlier and dropped: it lost money from 2023 |
| Overnight Bias ML | Both | See below: both sides kept, shared filter kept, equal size kept |
| Overnight Bias (plain, challenge) | Both | Longs PF 1.40, t = 3.0, 8/9 years; shorts PF 1.39, t = 2.6, 8/9 years |
| Overnight Drift | Long only | By design (buys after down days) |
| Expiration Open Short | Short only | By design; the long side of the same window makes nothing ($47 placebo, random direction) |

### Overnight Bias ML, first application (2026-10-12)

| Side | Trades | Win | Avg | PF | t | Years + | 2023 onward |
|---|---|---|---|---|---|---|---|
| Longs | 230 | 59% | $486 | 1.88 | 3.6 | 8/9 | $759 |
| Shorts | 181 | 50% | $649 | 2.02 | 3.4 | 9/9 | $547 |

- Both sides have their own edge; their daily P&L correlation is 0.00. Longs correlate 0.29 with
  Vault Break, shorts −0.01, so the short side is the better diversifier.
- Per-side sizing (longs/shorts at $300/$0, $0/$300, $400/$200, $200/$400, $400/$300,
  $500/$200): none beats equal $300 by more than noise ($6,993 vs $6,928 in year 1 at
  $400/$300, but $8,133 vs $8,379 over 2 years).
- A separate ML filter per side (walk-forward): longs kept $348 vs skipped $240 (joint filter
  $395 vs $206), shorts $539 vs $158 (joint $585 vs $131); funded $6,305 / $9,071 vs $6,466 /
  $9,569 for the shared filter. Keep the shared filter.

Standard metrics by side at $300 risk (`analysis/funded_metrics.py`):

| Side | Sharpe | Sortino | PF | Calmar | Ulcer | Max DD |
|---|---|---|---|---|---|---|
| Longs | 1.24 | 2.65 | 1.97 | 0.53 | 1.79 | $3,265 |
| Shorts | 1.33 | 3.56 | 2.34 | 2.25 | 0.58 | $930 |
| Both | 1.82 | 4.35 | 2.14 | 1.63 | 1.18 | $2,348 |

The shorts are the smoother side (Calmar 2.25 vs 0.53, Ulcer 0.58 vs 1.79); the longs carry the
deeper drawdowns. Sizing the shorts up and the longs down was still not better in the funded
bench ($200/$400: $6,031 vs $6,928), so equal sizing stays.

Code: `analysis/side_split_test.py`.

### Overnight Bias ML long side improved (v2, 2026-10-12)

Tried on the 230 long trades (`analysis/onb_ml_long_side_test.py`):
- **Exits:** stops 0.2–0.5 ATR, targets 1.5R–none, time exits 11:00–13:00, breakeven after
  1–1.5R. None better than the current 0.3 ATR / 3R / 14:30 by more than noise; the longs earn
  their money late in the day (every earlier exit is worse).
- **Entry conditions** (15 features by tercile, design 2018–22 vs holdout 2023–26): three were
  consistent: 20-day trend up, a clearly positive ML score, and the open not at the very top of
  the overnight range. As long-only filters in the funded bench only the score rule helped:

| Long-side rule | Kept | Kept vs skipped | Years kept > skipped | Funded 1 y / 2 y |
|---|---|---|---|---|
| None (v1) | 100% | – | – | $6,928 / $8,379 |
| 20-day return > 0 | 62% | $645 vs $229 | 5/9 | $6,904 / $8,383 |
| **ML score ≥ 0.03** | 68% | **$687 vs $60** | **8/9** | **$7,184 / $8,554** |
| Open ≤ 0.88 of overnight range | 65% | $589 vs $291 | 6/9 | $6,789 / $8,043 |
| Combinations | 27–43% | | 5–8/9 | $6,758–6,947 / $8,128–8,306 |

- **Walk-forward check** (model never saw the test year), plain ONB longs 2019+: score 0–0.03
  averaged $127 a trade ($82 in 2023–26) vs $484 at 0.03 and up.
- **Standard metrics, long side at $300:**

| | Sharpe | Sortino | PF | Calmar | Ulcer | Max DD | $/yr |
|---|---|---|---|---|---|---|---|
| Longs v1 | 1.24 | 2.65 | 1.97 | 0.53 | 1.79 | $3,265 | $1,723 |
| **Longs v2** | **1.45** | **3.49** | **2.77** | **0.95** | **0.83** | **$1,776** | $1,682 |
| Whole strategy v1 | 1.82 | 4.35 | 2.14 | 1.63 | 1.18 | $2,348 | $3,816 |
| **Whole strategy v2** | **1.94** | **4.97** | **2.50** | **2.62** | **0.67** | **$1,442** | $3,776 |

Adopted: `LongMinScore` 0.03 in `NQ_Overnight_Bias_ML.txt` (shorts stay at 0).

**MultiCharts confirmation and correction (2026-10-12)**
(`Backtesting Strategy Performance Report _ @NQ - 15 Minutes Overnight Bias ML (funded) v2.xlsx`,
`analysis/onb_ml_v2_confirm.py`): 343 trades (162 longs, 181 shorts), $646 average, PF 2.14.
Every decision matches the Python model except 6 days in January–February 2018, the filter's
warm-up (as with v1).

**Correction:** the "drawdown nearly halved" figures above compared v1 *including* its
January–March 2018 warm-up losses with v2 *without* them. Like for like, from April 2018:

| ($300 risk, from 2018-04) | Sharpe | Sortino | PF | Calmar | Ulcer | Max DD | $/yr |
|---|---|---|---|---|---|---|---|
| Longs v1 | 1.40 | 3.09 | 2.18 | **1.25** | **0.65** | **$1,502** | $1,878 |
| Longs v2 | **1.46** | **3.40** | **2.72** | 0.92 | 0.85 | $1,778 | $1,635 |
| Whole v1 | 1.97 | 4.83 | 2.30 | **2.97** | **0.59** | **$1,359** | $4,041 |
| Whole v2 | **1.98** | **5.07** | **2.54** | 2.64 | 0.67 | $1,441 | $3,801 |

So v2 improves trade quality (win rate, profit factor, Sharpe, Sortino) but **not** the
drawdown, and it earns about 6% less a year. Funded bench with the MultiCharts lists: fixed
sizes $7,202 / $8,547 vs $6,928 / $8,379 (1 / 2 years); recommended plan with cushion sizing
$6,876 / $11,366 vs $6,995 / $11,485, blown 10% vs 12%. **Net: within noise.** v2 stays the
default (the walk-forward evidence that low-score longs are weak still holds), and
`LongMinScore` 0 returns to v1 at any time.

### First parameter-cluster runs (2026-10-12, `analysis/param_clusters_vb_onb_test.py`)

**Vault Break** (720 combinations: noise 0.2–0.5 ATR, first entry 9:30–11:00, target 25–80,
stop 50–110). The single best design combination (target 60 / stop 75 from 10:30) collapsed
in 2023–26 (holdout Calmar 0.37, worse than 83% of all combinations); the five cluster medoids
scored 0.17–1.02. The **current settings** (0.3 ATR, 10:00, 40/75) score holdout Calmar 1.42,
better than 84% of all combinations, and rank in the top 5% on the design period too.
**Keep Vault Break as is.**

**Overnight Bias** (500 combinations: bias fraction 0.25–0.4, ADX minimum 0–30, stop 0.2–0.5
ATR, target 1.5–6R). The largest top cluster sits at **ADX ≥ 25–30**, stop 0.2–0.3 ATR, 1/3
fraction; its medoid (1/3, **ADX 30, stop 0.25 ATR**, 3R) scores holdout Calmar 2.43 (better
than 99% of all combinations) vs 1.37 for the current settings. ADX 30 appears in every long
cluster and most short clusters.

| Plain Overnight Bias, 2018–26 | Trades | Avg | PF | Sharpe | Sortino | Calmar | Ulcer |
|---|---|---|---|---|---|---|---|
| Current (ADX 20, 0.30 ATR) | 997 | $270 | 1.38 | 1.29 | 2.39 | 1.13 | 4.77 |
| **Medoid (ADX 30, 0.25 ATR)** | 676 | $372 | 1.66 | 1.61 | 3.31 | 2.06 | 2.87 |

- **Challenge** (VB 8 + ONB $1,100): pass **46.8% vs 43.3%** (2023–26: 51.1% vs 45.3%), same
  median 6 days. Adopted as the recommended challenge setting (inputs only: `ADXMin` 30,
  `StopAtrPct` 0.25), pending a MultiCharts backtest.
- **Funded** (ML filter on top): worse ($5,914 / $7,432 vs $7,190 / $8,544; cushion plan $6,318
  vs $6,897 in year 1): the ML filter was trained on the ADX-20 trades and the two filters
  overlap. **Overnight Bias ML keeps ADX 20.**
- By side, longs' current settings already hold up in 2023–26 (holdout Calmar 1.26 vs medoids
  0.52–1.11); shorts improve with ADX 25 / 0.25 ATR (1.00 vs 0.48). Consistent with the ADX 30
  change helping mostly through the short side.
