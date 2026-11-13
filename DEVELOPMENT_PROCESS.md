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

## Process additions (2026-10-22, with Codex)

1. **Evidence sheet first** (`agents/codex/BUILDER_BRIEF.md` step 0): who is forced to trade, direction / size / timing
   known beforehand, reaches NQ / ES directly, data that separates it from momentum, beats costs in a real gap, **power**
   (can the test ever reach t >= 2?), already tested? Verdict TEST / NEEDS DATA / DON'T TEST. Forced or scheduled flows
   stay the preferred search area for Apex. Personal-account research may also look at well-supported trend or risk-premium
   ideas, but each still needs a credible reason and the same validation.
2. **Straight into the plan, or the forward log (user, 2026-10-23).** A candidate that clears everything goes straight into
   the plan, monitored live like every plan strategy: MultiCharts-confirmed; t >= the multiple-testing bar AND deflated
   Sharpe >= 0.95; positive in 2018-22 and 2023+ (2023+ t >= 2) with nothing chosen on the full sample or after seeing
   2023+; clean placebos; checker PASS with no open concerns; and a gain on the bootstrapped bench (addition or replacement,
   beating the empty slot). The forward log is a discretionary tool for promising candidates with open doubts about future
   performance. **Forward log with its decision rule written first** (`agents/codex/FORWARD_LOG.md`). Before tracking starts, each
   entry fixes: review dates, minimum observations, costs, and what means CONTINUE / REJECT / EXTEND. Every eligible
   signal is recorded, including missed, rejected and skipped ones (with the reason), never only the filled trades.
3. **Break tests: two kinds, reported separately.**
   - *Implementation stresses* (price noise of a few ticks, nearby indicator settings, ±1-2 ticks of extra slippage,
     2-point target trade-through, a few minutes of delay): a live strategy must BEND (stay profitable and keep at least
     half its Sharpe). A BREAK here is a reason to cut or stop it.
   - *Leak checks* (2026-10-30, `analysis/leak_checks.py`, gates G10-G12 in `checker.py`): every candidate ranked above C
     supplies `fills.csv` (entry / exit times and prices) and, if any part is fitted (thresholds, percentiles, models),
     `trades_fullsample.csv`. Fills must have traded inside their bar; a one-bar entry delay must BEND; a full-sample fit
     must not earn > 1.3x the past-only version. `--selftest` proves planted leaks are caught; `--sweep` reruns the plan.
     The delay check only sees look-ahead into the entry bar; hindsight over the holding period stays the checker's job.
   - *Premise shifts* (moves that change what the strategy is, e.g. ONB's overnight range ending after the 08:30 open,
     VB's first decision at 09:00 or 11:00, broad joint jitter of session clocks): kept and reported as information on
     where the edge lives, not as a pass / fail verdict.
4. **Monte Carlo return / drawdown is descriptive.** Median 1-year P&L / median 1-year max drawdown
   (`analysis/montecarlo.py`) is reported next to P(loss), drawdown p95 and the trailing-limit hit chance. It describes
   the shape of past results; it doesn't show that the edge will last.
5. **Apex risk is judged on the intraday path.** `montecarlo.daily_mc` uses end-of-day P&L only and can miss a day that
   dips through the limit and recovers. Account decisions use the funded / challenge simulators (`analysis/funded_sim.py`,
   `funded_bootstrap.py`, `prop_sim.py`), which check each day's intraday low against the trailing threshold and the daily
   loss limit from the minute paths. That check is mandatory for anything that trades on Apex.

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
(`mc_reports/Backtesting Strategy Performance Report _ @NQ - 15 Minutes Overnight Bias ML (funded) v2.xlsx`,
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

## Pre-screen: will a new strategy help the book? (2026-11-04, user asked to keep this)

**Soft guide (not a rule; the bench decides): a new piece usually improves the personal book if its Sharpe > (book Sharpe) x (its daily correlation with the book).**
Book Sharpe = 3.15 (20 pieces at 1 micro, 2018-26, after costs). Hurdle by correlation: 0.0 -> any edge; 0.2 -> 0.63; 0.3 -> 0.95;
0.4 -> 1.26; 0.5 -> 1.58. The margin above the hurdle sets the size of the gain (noise-area longs: 1.54 vs 3.15 x 0.42 = 1.32 ->
return/DD only 9.0 -> 9.3). A screen, not a substitute for the bench; valid for a small piece next to a large book.

- t says how SURE we are the edge exists (grows with sqrt(trades)); t / sqrt(trades) and $/trade say how BIG it is.
- Another NQ morning breakout (08:30-11:00) correlates ~0.4 with the book: needs Sharpe 1.3+ to help, 1.8+ to help a lot.
  Other markets, overnight, weekend or event trades correlate ~0: almost any real edge (Sharpe 0.6-1.0) helps.
- Apex is stricter: drawdown per MNQ well under $1,000 and profits on days Vault Break / ONB lose.

Book piece stats (personal, per micro, 2018-26; corr = daily corr with the other pieces), medians: $2,153 a year, t 4.0,
Sharpe 1.33, max DD $1,574, return/max DD 1.28 a year, 73 active days a year, 56% winning days, corr 0.23. Leaders:
Twin (ret/DD 2.25, Sharpe 1.77, corr 0.30), Kusho (2.03, 1.68, 0.31), Overnight Tick (1.72, 1.68, 0.20): high Sharpe AND a time
of day / week the rest of the book doesn't trade. Low-corr small pieces (CL Sunday fade, EOS, ES MOC: corr ~0) earn little but
cut book risk. Recompute: `analysis/personal_portfolio.py` P (daily per piece).

- **Checker G13 invariance (2026-11-08, Boutgajouft SSRN 7525240 Gate 2):** trade outcomes in risk units compared across
  years and past-only VIX regimes (normalised Wasserstein-1 vs a Gaussian 95% reference). Soft gate: CONCERN, not FAIL, because
  regime-dependent edges are allowed; a CONCERN means 'name the regime the edge lives in and size for the other one'.

## Ingredients, not papers (user 2026-11-08)

Working strategies combine several ideas; a paper usually supplies one. Every upload / paper is reviewed as a list of ingredients:
1. **Mechanism** (why the money is there), 2. **place and time** where it is strongest, 3. **volatility normalisation**,
4. **exits that fit the edge** (trend: let it run; short flows: tight), 5. **a filter backed by a second mechanism**.

**For each upload:** list its ingredients, then run a drop-one ablation (remove one at a time, per NQ, both periods) before the
whole-strategy tests: it shows which part carries the edge and which parts are decoration (knobs that only add fitting room).
**For new combinations:** build only from ingredients in the register below, at most 2-3 per strategy, rules and settings fixed
before any result, then the full checker (incl. the parameter-perturbation check). Every combination tried counts as a trial.

### Every new strategy: ingredients + full data sweep (user 2026-11-10, standing rule)

Every strategy the user sends, whether or not it passes on its own, goes through three steps in the same reply chain:
1. **Standard test** (testing standard in CLAUDE.md: costs, both periods, placebo, metrics, books add / replace).
2. **Ingredient breakdown:** rebuild it, change ONE part at a time (entry trigger, filters, timing, stop, target, sides), find the
   engine vs supporting vs decoration; record a row in the Ingredient register below.
3. **Full data sweep:** `python3 analysis/strategy_data_sweep.py <trades.csv> <name>` splits its trades by every daily data series
   x regime and judges the best version against the FAIR placebo (best of N random splits picked the same way). A version that beats
   it is a LEAD: book bench (vs the same size spread evenly) and out-of-sample evidence before any plan change.
A weak strategy with a strong version is still worth the user's time: that is how the CL fade OVX sizing and the Overnight Tick lead
were found.

### New data: screen every piece (user 2026-11-10, standing rule)

Whenever a new data source arrives (or an existing one is used in a new way), do not stop at the idea it was fetched for. Also
**screen every plan piece against it**: `python3 analysis/new_data_screen.py <csv> <date col> <value col> <regime> <name>` splits
each personal-book piece's daily P&L by the regime the data defines and flags pieces whose gap clears the multiple-testing bar
with the same sign in both periods. Origin: the OVX data fetched for the CL fade also showed Overnight Tick earning ~3x more on
high-OVX nights (`analysis/ovx_screen.py`, WATCHLIST #37), the biggest book lead of the week. Rules for a screen result:
- it is a LEAD (found by screening): bench it in the books (post hoc, information) and compare with the same average size spread
  evenly, so a sizing gain is not just 'more of the piece';
- adoption needs out-of-sample evidence: older data, another independent market, or the forward log;
- report the screen with its bar (19-20 pieces -> |t| >= ~2.8), not the best line alone.

### Ingredient register (`analysis/ingredient_ablation.py`, 2026-11-08; per NQ, 2018-26) - historical component evidence (exploratory)

Status words (Proven / Decoration / harmless) label already-seen ablations, not causal estimates: removing a part can change later
trades, so a new combination still needs its own pre-registered design gate (Codex review 2026-11-08).

| Ingredient | Where it lives | Evidence (removed / alone) | Status |
|---|---|---|---|
| Morning momentum: vol-normalised extension from a 21-EMA, 08:40-09:30 CT, held to 14:50, **no target** | Twin MO | alone $518, t 4.6 (both periods); with a 1.5x target $184 (t 5.2 -> lower total) | **Proven** (the engine of Twin) |
| Noise band: breakout only beyond open / prior close +- the slot's average move | Bridge noise-area | without the band (vm 0) $62 -> $17, t 5.5 -> 2.2 | **Proven** |
| Closing order flow x VIX regime for the overnight direction | Overnight Tick | alone (any day) $225, t 4.8 (both periods) | **Proven** (stronger than the down-day rule) |
| Overnight drift window 17:05 -> 03:00 CT long | Overnight Tick | every night $108, t 3.1 (2018-22 t 1.6) | Supporting (base rate) |
| Down-day condition for overnight longs | Overnight Tick | down days only $175 vs every night $108 | Supporting |
| Swing-level stop entries (6h fractals, Osler) | Twin BO | alone $113, t 3.5 (2023+ t 1.5); RTH-only entries $309 a trade with the MO | Weak alone; better in RTH |
| Stop / stop cap | all | noise-area without stop AND target (coupled, Codex 2026-11-08): worst trade -$1k -> -$11.8k; Twin uncapped: worst -$2.9k -> -$11.7k | Required for Apex (risk shape, not edge) |
| Target on short-horizon trades | noise-area | without its 25-pt target $62 t 5.5 -> $123 t 3.7 (fewer, choppier) | Helps consistency |
| Daily trade / stop limits | noise-area | no effect (t 5.47 vs 5.50) | Decoration |
| Volatility cap filter (skip after a 2x range day) | Twin | no effect ($248 vs $243) | Decoration (keeps tail days out; harmless) |
| Shorts on NQ trend / momentum rules | noise-area, Donchian | noise-area with shorts $62 -> $40 a trade | Weak (NQ shorts) |
| Jump score: 5-min move / (bipower volatility x time-of-day factor), Marcaccioli 2021 | pino1 jump study (`analysis/jump_lib.py`, 2026-11-11) | Trigger \|J\| > 3 follow, 08:30-15:00: 30-min hold $115 (t 3.1) in 2018-22, -$70 in 2023+; swapping the exit to a 0.3R target lifts wins 52% -> 78% and cuts the net to $13; fade instead: PF 0.90; overnight instead of day: $0; precursor (endogenous / exogenous) filter: no gap | **Decoration** as a direction signal (the 0.3R target only buys win rate); usable as volatility normalisation |
| ATR emergency stop on daily IBS reversion (2.5 x ATR10) | IBS Globex ES v5 (`analysis/ibs_globex_test.py`, 2026-11-12) | Without it PF 1.46 -> 1.58, total $155k -> $168k; 2018-22 $33k -> $57k; 2023+ $116k -> $105k; 2.0 ATR worse (PF 1.36) | **Drag** on mean reversion (stops sell the low the rule buys); size down instead |

Post hoc leads from the ablation (not adopted, need their own pre-registered test): Overnight Tick's order-flow x VIX cell on any day
(t 4.8 vs the full rule's 5.2, twice the nights); Twin's breakout entries in RTH only ($309 vs $248 a trade, total $246k vs $274k).

**Round 2 (`analysis/ingredient_ablation2.py`, 2026-11-08; Vault Break v1, Dual Thrust v4, PAPERTREND v2; per NQ 2018-26, removed -> $ a trade / t):**

| Ingredient | Where | Evidence | Status |
|---|---|---|---|
| Volatility-scaled distance from the open (VB open + 0.3 ATR, DT open +- 0.5 prior range, PT open +- 0.5 ATR; = the noise band) | VB, DT, PT, noise-area | removed: VB $87 t 4.1 -> $55 t 3.2 (DD $13.9k -> $23.6k); DT $139 t 4.4 -> $74 t 2.4; PT $373 t 4.0 -> $126 t 1.7 | **Proven, shared** by four plan pieces (daily corr between them only 0.16-0.29: different days / times) |
| Direction of the break | PT | random side on the same days / times $-12 vs $373 | Proven (the side carries it) |
| Late start (VB entries from 10:00, not 08:30) | VB | from 08:30: $40, t 1.9, 2023+ t 0.7, DD $30.1k | Supporting (strong: the first 90 minutes are noise for VB) |
| Range-regime filter (DT skip RR > 1.2 ADR; PT skip after the widest of 7 ranges) | DT, PT | DT t 4.4 -> 3.6; PT t 4.0 -> 3.5 | Supporting |
| Gap-side filter | PT | t 4.0 -> 3.4, but total $212k -> $301k (more trades) | Supporting per trade; costs total |
| VWAP confirmation | VB | t 4.05 -> 3.81 | Weak supporting |
| Up to 3 entries a day | VB | 1 a day: t 4.1 -> 2.9, total $154k -> $80k | Supporting |
| Stop (target kept) | VB, DT | VB no stop: worst -$1.5k -> -$8.5k, t 2.4; DT both stops off: worst -$19k, 2023+ t 0.8 | Required (risk shape) |
| Target | VB, DT | VB no target $152 t 2.7 (less steady); DT no target $201, **same t 4.37, total $226k -> $327k, DD $19.6k -> $27.4k** | VB: helps; DT: post hoc lead (needs its own pre-registered test) |
| Entry-bar stop, holiday list (DT); 2 x ATR disaster stop (PT) | DT, PT | no change (PT's stop is never the exit that matters in the backtest) | Decoration (PT stop kept for tail risk) |

**Round 3 (`analysis/ingredient_ablation3.py`, 2026-11-08; Relative Strength, Late-Day Flow; LDF rebuild 905 trades $91 vs MultiCharts 895 $95):**

| Ingredient | Where | Evidence (removed -> $ a trade / t) | Status |
|---|---|---|---|
| NQ's move beyond what ES explains (cross-index residual) | Relative Strength | own momentum only $306 t 4.0 -> $189 t 2.1; market part alone $48 t 0.5; random side $-8 | **Proven** (a different engine from the open-breakout family) |
| Early fixed decision time (9:00) | Relative Strength | decide 9:15: $220 t 2.8, DD $28.5k -> $42.9k | Supporting (strong) |
| Big-day condition (move >= 0.4 ATR by 14:00) | Late-Day Flow | follow every day: $91 t 3.4 -> $42 t 2.7 | **Proven** (with the window) |
| Forced-flow window 14:00 -> 14:30 | Late-Day Flow | signal 14:10: $20 t 0.7; exit 15:00: $72, 2023+ t 0.5 | **Proven** (timing is the edge) |
| Volatility scaling of the threshold (Z / ATR vs a raw bp / % threshold, trade count matched) | RS, LDF | RS t 4.0 -> 3.9; LDF t 3.4 -> 3.3 | Decoration here (the threshold matters, its scaling does not; count-matched on the full sample) |
| Target | RS | no target $310 t 3.8 | Decoration |
| Stop | RS, LDF | RS no stop: worst -$6.8k -> -$20.2k, DD $35.3k; LDF no stop: $94 t 3.5, DD $15.0k -> $11.9k, worst -$2.7k -> -$3.1k | RS: required (tail); LDF: little effect (post hoc lead, not a change) |
| Shorts | RS, LDF | RS shorts 2023+ t 1.1 (longs 2.8); LDF shorts $107 vs longs $78 | RS shorts weak recently (50K trades longs only); LDF both sides |

**Round 4 (`analysis/ingredient_ablation4.py`, 2026-11-08; Expiration Open Short, NFP Fade, CL Sunday Gap Fade; rebuilds match: EOS 106 trades
$501 vs 105 / $474, NFP 78 / $343 vs 76 / $319, CL 96 / $653 = the MultiCharts spec exactly):**

| Ingredient | Where | Evidence (changed -> $ a trade / t) | Status |
|---|---|---|---|
| Monthly options expiry (AM settlement) | EOS | other Fridays $-58; long instead $-519; quarterly-only $260 (t 0.8) vs monthly-only $620 (t 2.8) | **Proven** (monthly expiries carry it) |
| Enter at the 08:30 open | EOS | enter 09:00: $77 (t 0.5) | **Proven** (the edge is the first 30 minutes) |
| Exit 10:00 | EOS | 09:00 $369 (t 2.85); 11:00 $551; 14:55 $789 (t 2.73; 2018-22 t 2.8, 2023+ t 1.4) | Lead: a later exit adds money at the same t (post hoc) |
| Fade the payroll reaction | NFP | follow instead $-427 (t -2.6) | **Proven** (direction) |
| Payroll spike condition (07:31-07:35 range > 3x median) | NFP | any first-10-day Friday: $234 (t 1.8) | Supporting |
| Reaction window 07:30 -> 07:45 | NFP | 07:35: $236; 08:00: $325 | Supporting (07:45 best) |
| Stop | EOS, NFP, CL | no stop: EOS $529 (worst -$8.1k), NFP $408 (t 2.2), CL $725 (t 3.5; but a -$16.6k open loss on 2026-03-08) | Risk shape: keep (Apex) |
| Weekend gap threshold (Sunday 17:01 open >= 0.1 ATR above Friday) | CL | every up-gap $243 (t 2.3); >= 0.3 ATR $708 (n 34) | **Proven**; measured on the FIRST print: the gap at the 17:05 close instead gives $259 |
| Fade up-gaps only | CL | follow $-664 (t -4.0); long down-gaps $-60; both sides $370 | **Proven** (up-gaps only) |
| Weekend-specific | CL | the same fade on Mon-Thu reopens $-362 | **Proven** (weekend news gap) |
| Hold to Monday 09:00 CT | CL | out Sunday 23:59 $146; Monday 07:00 $415; 13:30 $593 | Supporting (09:00 best) |

**Round 5 (`analysis/ingredient_ablation5.py`, 2026-11-08; Monday Long, Swing Target v3; ONB ML from Codex's frozen ablation the same day,
`agents/codex/results/ingredients_fc_onb_t_20261108.md`; rebuilds: Monday 414 trades $436 vs research 452 / $413; Swing Target 602 / $316 vs
MultiCharts 598 / $316, same side 100%, P&L corr 0.96):**

| Ingredient | Where | Evidence (changed -> $ a trade / t) | Status |
|---|---|---|---|
| Monday (weekend inflows / Monday 0DTE hedging) | Monday Long | Tue $73, Wed $56, Thu $15, Fri $69 (t <= 0.6); short $-371 | **Proven** |
| Buy the 08:30 open, hold to 15:00 | Monday Long | enter 10:00 $163; out 10:00 $216, out 12:00 $282 | **Proven** (the whole session) |
| After a down Friday | Monday Long | $510 vs $369 after an up Friday | Post hoc lead (both positive) |
| Overnight location sets the side | ONB (Codex) | no overnight-bias direction: $156 / $173 a trade, DD x3-4 | **Proven** |
| ML score (calendar terms most) | ONB ML (Codex) | no score $233 / $312 vs $631 / $711; no calendar terms $463 / $556 | Supporting (in-sample attribution) |
| ADX trend filter | ONB ADX30 (Codex) | no ADX $182 / $316 vs $340 / $409 | Supporting |
| Break of the prior 2 days' RTH range, in the break's direction | Swing Target | fade instead $-284 (t -3.7); 1-day levels $227, 5-day $170 | **Proven** (2-day levels best) |
| Skip days that broke a level 08:31-08:45 | Swing Target | no skip: $208 (t 3.5), DD $15.6k -> $25.4k | **Proven** (supporting, strong) |
| Target 0.35 x range | Swing Target | no target $294 (t 3.4); target 0.7 $315 (t 4.0) | Helps consistency |
| Break-even at 0.30 x range | Swing Target | none: $321 (t 4.5) vs $316 (t 4.6) | Decoration here (Codex's earlier test: lower DD) |
| Shorts | Swing Target | shorts $486 (t 4.7), longs $168 (t 1.9) | Post hoc lead: the shorts carry it |

**Round 6: the capital-expansion bench (`analysis/ingredient_ablation6.py`, 2026-11-08; per contract, removed / changed -> $ a trade / t):**

| Piece | Engine (removing it kills the edge) | Supporting / decoration | Post hoc lead |
|---|---|---|---|
| FVB | regime skip (off: $98 t 2.5) and strong-day short block (off: $92 t 2.4) | 1 trade a day ~same; window 120 best | **shorts $316 (t 3.7, DD $21k) vs longs $67 (t 1.5)** |
| Ricochet 1144 | re-entries at S1 (none: $15 t 0.4); after a red day (green: $25; every day $54) | stop 50 / target 100 as is best | - |
| DriftPullBack v3 | (no single part: drift off is BETTER, $47 t 3.4, DD $46k vs $58k) | target = stop: more $ but DD $75k | 1 trade a day: $60, DD $20.8k (vs $57.5k); shorts dead since 2023 ($5) |
| RollZone 24h | the noise zone (off: $26 t 0.8) | night entries add (off: t 2.0); target irrelevant; stop 0.4 worse | - |
| S30 IBS (NQ) | IBS reversal; hold until IBS > 0.8 (1-day hold $632) | after a down close: worse 2023+ | **entry IBS < 0.10: $2,331 (t 4.9; 2018-22 t 4.0, 2023+ t 3.1), DD $24.8k vs $37.7k, worst -$15k vs -$28k** |
| Prior VWAP Trap | intraday momentum + 0.5 ADR trailing stop (its review: other levels $107-115, random levels $88-169) | the prior-VWAP level itself (~$30) | - |

**Round 7: the three Codex bench pieces (`analysis/ingredient_ablation7.py`, from Codex's frozen ledgers; alternative models + side splits):**

| Piece | Engine | Supporting / decoration | Post hoc lead |
|---|---|---|---|
| Anson momentum | its intended settings (threshold 4.5, hold 20 bars; the uploaded 3 / 6 earn $1) | Apex early flat: no effect | longs $140 (t 2.4) vs shorts $60 (t 1.0) |
| R2Vault (longs only by design) | the CT 09:30-15:30 window (ET window $15, t 0.8; daily reset $25) | Apex flat halves it ($33) | - |
| S03 Noise Area v2 | the noise-area breakout (v1 $144 t 3.3) | v2's 0.4 stop factor: t 3.3 -> 3.8, DD $41k -> $22k (supporting) | longs $158 (t 3.5) vs shorts $84 (2023+ $39) |
(Exit-type splits are shown in the output but are not ablations: stops lose and targets win by construction.)

**Batch of 5 (2026-11-08, pre-registered; TIER_LIST rows):** the engines are market-specific. Morning momentum does not carry to CL / GC / ZN
(t 0.8 / 0.2 / -1.3; it works on NQ and, weaker, on ES); the noise band loses on CL / GC even before costs; the Overnight Tick signal
carries to ES (t 4.4, checker 8/8) but is the same trade (corr 0.94 with OT on NQ). Cross-mechanism filters failed both ways: overnight
flow does not predict Twin's morning side; the noise-area longs do better on calm VIX days (post hoc lead), not volatile ones. Next ingredient
work should look for new mechanisms (other places / times), not move the three engines to other markets.

**Combos (`analysis/ingredient_combos_test.py`, 2026-11-09, pre-registered):** an engine from one piece + a proven filter from another
(flow z on VB, heavy night on S47, DI on Monday Long, LDF agreement on ES MOC) - none beat random skips (p 0.13-0.90). A filter is
proven only on its own engine: it encodes that engine's mechanism (Bridge's DI picks Bridge's Sunday-night trend, T's heavy night
picks an overreaction to fade). Next ingredient work: new engines (new data / places / times), not borrowed filters.

**Round 10: Kusho v9, S47 v2, FC 2B (`analysis/ingredient_ablation10.py`, 2026-11-09, pre-registered; personal-book pieces on forward logs):**

| Piece | Engine | Supporting | Decoration | Notes |
|---|---|---|---|---|
| Kusho v9 ($109, t 5.32, 3,175 trades) | the strong 15-min up-bar entry (random entries at the same rate $4) | EMA50 filter (none: $57, 2023+ $37); small-wick filter (none: $91, DD $18k -> $27k); overnight / weekend hold (flat by 15:45: $91); DOWN-day shorts ($160 a trade) | - | robust in both periods ($108 / $109) |
| S47 v2 ($347, t 4.10) | the London-open impulse (New York only: $114; fade: -$252) | the 09:30 confirmation (v1: $228, DD $16k -> $37k); stop 0.5 x overnight ATR (0.25: $220; none: worst -$20.9k) | - | shorts carry 2023+ ($494 vs longs $183) |
| FC 2B ($255, t 3.74; v1 rebuild) | the flow z filter on the opening drive (no filter: $116; opposite: -$220) | the 150-point trail (none: 2023+ $144 vs $209) | break-even (none: $267, t 3.68) | shorts faded since 2023 ($100); z >= 0.5: t 4.20, total $300k vs $196k but $ a trade lower in both periods |

Every version held up; no variant beats its current version on t AND both periods, so nothing changes. Leads: S47 shorts,
FC 2B longs (both 'one side carries 2023+'), FC 2B z >= 0.5 as a capital-bench idea (more trades, higher t, lower $ a trade).

**Round 9: Bridge Monday, ES MOC, T fade (`analysis/ingredient_ablation9.py`, 2026-11-09, pre-registered; rebuilds 218 / 202 / 376 vs MC 217 / 199 / 348):**

| Piece | Engine | Supporting | Decoration | Notes |
|---|---|---|---|---|
| Bridge Monday Long ($560, t 4.44) | Monday (Tue -$137, Wed $157, Thu $169, Fri -$155) | DI+ > DI- (no filter: 2018-22 $121, 2023+ $742); the Sunday 19:00 entry (Monday 08:30: $419); target 100 (no target $779 but t 3.72, DD $18k) | the ADX 10-50 range (DI only $537, t 4.40) | 2023+ every Monday works (regime) |
| ES MOC Follow ($158, t 3.47) | following a >= 0.3 ATR 14:00-14:50 move into the 15:00 cash close (fade -$150 t -3.5; every day -$13) | stop 0.25 (no stop $142); exit exactly 15:00 (14:55 $36, 15:15 $90) | - | 2023+ $99 (t 1.2): longs hold ($212, t 1.9), shorts faded ($34); same rule on NQ $255 but 2023+ $38 |
| T fade ($221, t 3.39) | fading a HEAVY night (every night $20; quiet nights -$20; follow -$222) | stop 0.40 (none $187, worst -$7k); entry 08:29:00 before the bell (at the bell $171); exit ~08:44 (09:00 $189, 09:30 $145) | - | out 08:40 $234 t 3.81 but 2023+ lower ($243 vs $281): fails the two-bar rule |

Every live version held up; no variant beats its current version on t AND both periods (two-bar rule), so nothing changes.
Leads: ES MOC longs only (shorts flat since 2023; watch #20).

**Round 8: ZT continuation (`analysis/zt_ablation.py` + `analysis/zt_plateau.py`, 2026-11-09; base 15-min, EntryZ 1, Apex window, $148 t 3.03):**
engine = the vol-normalised distance from the 32-EMA (points from the EMA instead: $10, t 0.2; ATR denominator ~same, t 2.6), and it is
Twin's engine (base trades on Twin-active days $343 t 5.6, on Twin-flat days −$194 t −2.5). Supporting: the |ZT| ≤ 0.25 exit (without
$116 t 2.2), the EMA (SMA $96), mean 32 / vol 16-32. Decoration: the ±4 stop (never fires). Holding longer earns more per trade (16 bars
$223 t 3.6) but hurts the evaluation (−2.9%) and the funded bench. Threshold plateau 15-min EntryZ 1.05-1.30 (t 3.4-3.8; ≥ 1.45 dies).
Post hoc lead: EntryZ 1.25 ($246 t 3.5, DD $17.3k vs $32.8k) - the only variant that helps a book (personal +0.06 / +0.11 / +0.12).


## Resize after every plan change (user rule 2026-11-12)
Any change to a plan (piece added / removed / resized / swapped) is followed, in the same reply, by `analysis/resize_book.py` on the
updated `bench150.LIVE_EVAL`: one-at-a-time sizes (0 / 0.5x / 1.5x / 2x), a greedy search ranked on 2018-22 starts, then one holdout
look (2023-26) and the account-now check. Change sizes only when both bands exclude 0. First run 2026-11-12 (book with NBL 3 + LDF $1,000):
search moved JF 1 -> 0 and LDF -> $1,500, holdout -0.1 pt, account -0.3 pt: keep the live sizes.
