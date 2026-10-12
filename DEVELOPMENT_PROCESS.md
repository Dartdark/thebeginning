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

Adopted: `LongMinScore` 0.03 in `NQ_Overnight_Bias_ML.txt` (shorts stay at 0). Same yearly
profit, drawdown nearly halved. Pending: MultiCharts confirmation (expected about 337 trades
2018–2026: 156 longs, 181 shorts, average about $667, PF about 2.18).
