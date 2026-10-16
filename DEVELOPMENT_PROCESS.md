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
4. **Fold stability** (`analysis/robustness.py`): re-optimize on overlapping 3-year windows
   (2018–20, 2019–21, … 2024–26). A robust choice ranks near the top in every fold, and the
   per-fold optimum stays in the same region.
5. **Sensitivity:** move one parameter at a time around the choice, others fixed. Smooth, flat
   curves = robust; a big drop to a neighbouring value = overfit. Prefer the middle of a flat
   region over a higher but isolated peak.
6. Check the result on the 2023-onward holdout and in the funded bench / challenge simulator
   before adopting it. Do it separately for longs and shorts.

## Resampling: how sure, and how bad could it get?

Run `analysis/resampling.py` on the 2023-onward holdout (out of sample) and on 2018–2026,
for the whole strategy and each side:

1. **Block bootstrap** (10-day blocks, 5,000 runs): 90% interval for Sharpe, Sortino, profit
   factor, Calmar, Ulcer and max drawdown, plus P(Sharpe ≤ 0). Adopt only if the low (5%)
   end is still acceptable, not just the point estimate.
2. **Permutation** (5,000 shuffles of the same days): where the real max drawdown ranks among
   the shuffled ones, the 95%/99% shuffled drawdown, and P(drawdown ≥ $1k/$2k/$3k). Size for
   the 95% shuffled drawdown, not the historical one.
3. **Apex window risk**: share of start days with a $2,000 drawdown in the next 20 / 60
   trading days, real order vs shuffled. Real above the shuffled band means losses cluster,
   so the i.i.d. challenge simulator understates the risk.
4. **Monte Carlo** (since 2026-10-16, `analysis/montecarlo.py`, `MC.report(trades, daily, size=...)`): reshuffle the
   trades (10,000 bootstrap runs: 5/50/95% total, P(total ≤ 0), shuffled max drawdown 50/95/99% and where the real one
   ranks, longest losing streak) and block-bootstrap one year of daily P&L (P(loss), 95% drawdown, P(hitting the $2,000
   Apex EOD trailing drawdown)) at the size the strategy would actually trade (e.g. 0.1 for one micro). Every new test
   prints it; a strategy whose one-year P(trailing hit) at plan size is above ~5% needs smaller size or a cushion rule.

## Step 4: decide and recombine

For each side: keep it as is, keep it with its own settings or size, or drop it. Then put
the sides back together and run the funded bench (and the challenge simulator if relevant).
A per-side change is adopted only if the recombined strategy beats the original by more than
the noise of the estimate, in both the 1-year and 2-year payouts.

## Step 5: implement and record

- MultiCharts: one file with `EnableLongs` / `EnableShorts` inputs and separate long/short
  settings where they differ, so the side split stays visible and reversible.
- Record the per-side results in the strategy's README section and in `TIER_LIST.md`.

## Multiple testing: the trials log (added 2026-10-15)

Every ranked item in `TIER_LIST.md` is a trial. `python3 analysis/trials.py` rebuilds `TRIALS.csv` (193 items, ~816 variants
on 2026-10-15) and prints the bar: the best of N noise trials reaches |t| = `metrics.t_threshold(N)` (3.47 at N = 193).
- **A new strategy or filter is promoted above C only if** its t clears `t_threshold(N_items)` or its deflated Sharpe
  (`metrics.deflated_sharpe(per-trade P&L, N_items)`) is >= 0.95,
- **or** it was pre-registered from a stated economic mechanism or a published result, with <= 3 variants: then t >= 2.0
  plus a clean placebo / replication, and the TIER_LIST row says so.
- Scans (many features x strategies) are always judged against their own shuffled-P&L null, as before.
- Status 2026-10-15 (per trade, N_items = 193): Overnight Bias ML DSR 0.99 passes; Vault Break 0.92 and Bridge Monday 0.91
  near; Late-Day Flow 0.79, Monday Long 0.73; EOS 0.42, Vol-Control Sell 0.23, NFP Fade 0.16 do not -- they stand on the
  pre-registered forced-flow rule (mechanism first, few variants, holdout and MultiCharts confirmation) and stay small in
  the plan; the live drift alarm is their real test.

## Independent checker (maker-checker split, added 2026-10-15)

Before anything is promoted above C or added to a plan, it goes through a checker that never sees how it was found:
1. The maker writes `checks/candidates/<name>/`: `spec.md` (rules in plain words, instrument, costs, mechanism, variants
   tried, pre-registered or not), `trades.csv` (date, side, net per contract after costs; filters add `kept` and list all
   base trades), `meta.json` (kind, pre_registered, variants), optional `placebo.csv` (run, net).
2. `python3 analysis/checker.py checks/candidates/<name>` runs fixed gates (G1 significance with the trials bar, G2 holdout,
   G3 years, G4 concentration, G5 placebo, G6 resampling; since 2026-10-15 also the Minerva gates G7 MinTRL, G8 regime
   stability rho >= 0.60 over calendar years, G9 PBO <= 0.50 when variant trade lists are supplied) and writes `checker_report.md`.
3. The `strategy-checker` agent (`.claude/agents/strategy-checker.md`, a fresh agent with no access to the maker's scripts,
   outputs or the tier list) rebuilds the rule from `spec.md` on raw data, compares with `trades.csv`, looks for leaks,
   reruns the gates and writes `verdict.md` (PASS / PASS WITH CONCERNS / FAIL).
4. Only a PASS (or PASS WITH CONCERNS that the user accepts) moves on to the funded bench and MultiCharts confirmation.

## Strategy lifecycle: backtest → Apex → live (user's plan, 2026-10-15)

Apex is the live test bench (only fees at risk); a personal account is where proven strategies earn without Apex's
per-account caps (`funded_strategies/FUNDED_PLAN.md`, 'Apex vs a personal account'). Every strategy moves through four
stages and only forward through a gate:

| Stage | Where | Gate to move on |
|---|---|---|
| 1. Research | Python backtest, Steps 1–5 above | t ≥ `metrics.t_threshold(N_items)` or DSR ≥ 0.95 (or pre-registered), clean placebo, 2018–22 and 2023–26 both positive |
| 2. Confirmation | MultiCharts backtest + `strategy-checker` | MC report matches the Python replica; checker verdict PASS |
| 3. Apex incubation | Apex accounts, small size, next to the plan | ≥ 40 live trades (or 6 months for rare strategies) with live / backtest average ≥ 0.75 and no ALARM (`analysis/live_vs_backtest.py`); funded bench with it added does not raise blown |
| 4. Live (personal account) | own capital, MNQ first | sized so the plan's max drawdown is ≤ 20–30% of the account; grows with the account |

Rules:
- **Incubation runs on accounts that carry the whole plan** (copier), with the candidate at the smallest size (1 MNQ or
  its risk equivalent). Never run a candidate alone on a separate Apex account: if it is short while the plan is long on
  another account, that is cross-account hedging, which Apex prohibits. On one account one symbol simply nets.
- Funded-bench check before incubation: the candidate at 1 MNQ may not raise the funded plan's blown rate by more than
  ~1 point (the risk budget is full); if it does, incubate on combine accounts only.
- **Demotion:** ALARM in live → half size and review (as in `live/README.md`); a second ALARM or a live / backtest ratio
  < 0.5 after 40 trades → back to stage 3 (or retired), never straight to deletion of the record.
- Promotion and demotion are recorded in `TIER_LIST.md` (tier + stage) and `NEW_CHAT_BRIEF.md`.
- **Early personal start (user, 2026-10-15): from month 3** at about 1/10 size (MNQ; ~$10k covers the plan's 1-NQ
  drawdown of $24k / 10 at a 25% tolerance), if the plan has ≥ ~100 live trades (it makes ~36 a month), live / backtest
  ≥ 0.75 and no ALARM. Full sizing only after 6–12 months. Why small: the plan's edge is t ≈ 7 over 8.8 years, so 3 months
  of live trades give t ≈ 1.2 (6 months 1.7) — enough to catch a broken plan, not to prove it (a dead edge would still look
  ≥ 75% of the backtest after 3 months about 1 time in 5, after 6 months 1 in 10).
- Strategies that trade rarely (EOS ~12 a year, NFP ~9, CL fade ~11) cannot reach 40 live trades in a year; they move to the
  personal account with the plan as a whole, on the plan-level evidence.
- Current status: the whole plan is at stage 3 (live on Apex since 2026-10-12); personal account from ~month 3 at 1/10 size,
  funded from Apex payouts, full size after 6–12 months of live results that match the backtest.

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

### Fold stability and sensitivity (2026-10-12, `analysis/robustness_vb_onb_test.py`)

**Overnight Bias, ADX 30 / 0.25 ATR (challenge setting): passes both.**
- The per-fold optimum uses ADX 30 in 6 of 7 folds (25 in the last), stop 0.25 ATR in 5 of 7,
  fraction 1/3 in 4 of 7, target 3–4R in all.
- The ADX 30 setting ranks in the top 7% in every fold (93–100%); the current ADX 20 setting
  ranks 46–93%.
- Sensitivity around ADX 30: every one-step change costs at most 22% of Calmar; the target is
  flat from 3R to 6R. Around ADX 20, the bias fraction drops 52% one step away (to 0.4).
- By side: the short side gains most (fold ranks 65–100%); the long side is flat across ADX.

**Vault Break: keep the current settings, with a known weak spot.**
- No stable optimum: the per-fold best moves across noise 0.2–0.5, target 25–80 and stop
  50–90. The current settings rank in the top 6–40% of every fold (60–94th percentile), good
  in every period but never the best.
- Stop and noise curves are smooth (stop 50–110 within 15–30%). The target and start time looked
  like a spike on the coarse grid (40 points: Calmar 1.14; 30 and 50 points: 0.72 and 0.64). A fine
  grid shows a **plateau from 33 to 42 points** (0.94–1.14) that falls away from 45 points up.
  Decision times 9:45 and 10:00 are the same bar on the 30-minute chart; 10:15/10:30 was better in
  2018–22 but much worse in 2023–26. Target 40 sits inside the plateau; nothing to change.

### Robustness of every strategy (2026-10-12, `analysis/robustness_all_test.py`)

Rank = percentile among all tested combinations (higher is better); folds = 3-year windows
2018–20 … 2024–26; holdout = 2023–26 Calmar, never used for choosing.

| Strategy | Combinations | Current: holdout rank | Current: fold ranks | Sensitivity | Action |
|---|---|---|---|---|---|
| Vault Break (challenge + funded) | 720 | 84% | 60–94% | Smooth on stop/noise; target plateau 33–42 pts; start 10:00 regime-dependent | Keep |
| Overnight Bias plain (challenge) | 500 | ADX 20: 59%; **ADX 30 / 0.25 ATR: 99%** | ADX 20: 46–93%; **ADX 30: 93–100%** | ADX 30 setting smooth (≤22% drops) | **Switch to ADX 30 / 0.25 ATR** |
| Overnight Bias ML v2 (funded) | 432 | 63% | 55–98% | Stop and target flat; ADX 20 is a peak (−30% at 15/25), partly by construction (the ML weights were fitted on ADX-20 trades) | Keep. Stop 0.25 tested: better with cushion sizing (+$623 year 1), worse at fixed size (−$433), better only in the two latest folds, so no change |
| Overnight Drift (funded) | 150 | 96% | 90–98% (33% in 2018–20) | **Peaky**: entry 30 min later −48%, exit 2:00/4:00 −40%, stop 0.2 −40%, all days instead of down days −47% | Keep, but it sits on a narrow peak: the least robust strategy, consistent with its B tier |
| Expiration Open Short (funded) | 105 | 91% | 49–74% early, 91–97% since 2022 | Start must be 8:30 (the settlement mechanism, −76% at 8:45); exit flat 9:15–10:30; stop flat 0.2–1.0 | Keep (9:30 exit scores higher over 2018–26 but the same plateau; 105 trades is too few to fine-tune) |

By side (Overnight Bias ML): the long side's current settings rank 52–99% across folds with
smooth stop/target curves; the short side ranks 44–83% and prefers a tighter stop (0.2–0.25) in
most folds, but the funded bench doesn't confirm a change.

### Bootstrap and permutation (2026-10-12, `analysis/resampling_test.py`)

Fixed sizes (funded: VB 3 MNQ, ONB ML v2 $400, OND $500, EOS $700; combine: VB 8 MNQ, plain
ONB $1,100), no cushion sizing. Bootstrap 90% intervals for Sharpe; permutation = day order.

| | Sharpe 2018–26 (5–95%) | Sharpe 2023–26 (5–95%) | P(Sharpe ≤ 0) 2023–26 | Real max DD 2023–26 | Shuffled 95% DD | Real DD rank |
|---|---|---|---|---|---|---|
| Vault Break 3 MNQ | 1.35 (0.85–1.86) | 1.46 (0.67–2.28) | 0% | $4,085 | $7,680 | 25% |
| ONB ML v2 $400 | 1.71 (1.25–2.12) | 1.77 (1.12–2.48) | 0% | $1,753 | $2,675 | 57% |
| · longs | 1.26 (0.75–1.72) | 1.78 (1.14–2.43) | 0% | $1,048 | $1,613 | 57% |
| · shorts | 1.19 (0.72–1.62) | 0.76 (−0.02–1.54) | 5% | $1,768 | $3,024 | 44% |
| Overnight Drift $500 | 0.40 (−0.10–0.89) | 0.50 (−0.26–1.22) | 14% | $3,530 | $5,525 | 50% |
| Expiration Open Short $700 | 1.06 (0.58–1.50) | 1.12 (0.38–1.75) | 1% | $1,063 | $3,124 | 1% |
| **Funded portfolio** | **2.16 (1.68–2.61)** | **2.22 (1.53–3.00)** | 0% | **$3,351** | **$8,347** | **1%** |
| Combine pair (VB 8 + ONB $1,100) | 1.72 (1.22–2.21) | 1.91 (1.18–2.71) | 0% | $12,972 | $27,072 | 8% |
| · plain ONB longs | 1.10 (0.57–1.57) | 1.51 (0.74–2.23) | 0% | $6,456 | $13,536 | 13% |
| · plain ONB shorts | 0.86 (0.41–1.32) | 0.70 (−0.04–1.47) | 6% | $7,800 | $18,608 | 4% |

- **Edges are not luck of a few days:** every strategy except Overnight Drift keeps a
  positive Sharpe at the 5% end of the full-period bootstrap. OND's interval includes zero
  (P(Sharpe ≤ 0) 9% full, 14% holdout), which matches the placebo: it is the first to cut.
- **Weak spot: the short sides since 2023.** ONB ML shorts and plain ONB shorts both have
  intervals touching zero in the holdout (5–6% chance Sharpe ≤ 0); longs carried 2023–26.
  Not a reason to drop them (2018–26 intervals are clearly positive, zero correlation with
  longs), but the side to watch.
- **The real drawdowns were lucky.** The funded portfolio's 2023–26 drawdown ($3,351) is
  smaller than 99% of shuffled orders of the same days; the median shuffle is $5,333 and the
  95% one $8,347. EOS (1%) and the combine pair (8%) are the same. Plan for drawdowns about
  1.5–2.5× the historical ones; this is what cushion sizing is for.
- **Losses do not cluster.** In the Apex window test the real share of 20/60-day windows with
  a $2,000 drawdown is at or below the shuffled average for every strategy (portfolio 60-day,
  2018–26: 30% real vs 45% shuffled). So the i.i.d. challenge simulator is not too kind, but
  the funded bench, which replays the real order, is probably somewhat optimistic about
  blow-ups.
- ONB ML longs' full-period drawdown ($3,916) ranks above every shuffle: it is all 2018
  (−$2,491 that year), the first year of the frozen model; 2019–2026 were all positive.
