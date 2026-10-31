# Uploaded Twin Continuation standalone: WATCH for further verification; REJECT as pasted for Apex
Summary: Exact-default standalone replay is historically profitable: 1,030 primary trades, $330/NQ per trade, PF 1.65.
Realized daily max drawdown is $16,141 at 1 NQ; the worst trade is -$11,717 and four trades cross a flatten deadline.
BO-only and MO-only are profitable separately; these are independent opportunity sets, not summed portfolio results.
No parameters changed. All 1,075 full-2018 replay entries/P&L match the prior independent replica.
Keep the pasted version off Apex; platform/session parity and forward evidence remain unresolved.

Plan: `agents/codex/plans/twin_uploaded_standalone.md`, **8d661f1**. Evidence: `agents/codex/evidence/twin_uploaded_standalone.md`.
Scripts: `analysis/codex_twin_standalone.py`, `analysis/codex_twin_standalone_report.py`.
Output: `analysis/outputs/codex_twin_standalone/`. Replayed configurations **3**; optimized rules **0**.

## Rule (as tested)

The upload's executable code is identical to `checks/candidates/twin_continuation/Twin_Continuation.txt`; only a comment
differs. The preserved upload is `agents/codex/inputs/twin_continuation_uploaded.txt`; hashes are in the manifest.
This is a user-requested replication of an already-ranked strategy, not discovery of a new edge. Nothing was deployed.

NQ, one contract, close-stamped one-minute bars. Combined Twin permits one position and runs confirmed 6h swing
breakouts with opposite-swing stops and 2×15-minute ATR targets, plus 10-minute morning oscillator crossings at
08:40–09:30 CT, 75-point stops and 14:51 exits. BO_MaxStopMult stays **0**. BO-only disables MO; MO-only disables BO.
Each component-only run can take entries that combined Twin blocks while occupied, so their totals are not additive.

The existing independent simulator was imported unchanged. It interprets SetExitOnClose at the **stated 16:00 CT
session end**. Actual chart-session definitions can change this; the historical MC v2 export also contains holiday
inputs absent from the upload. This is a faithful replay of that documented model, not new exact MultiCharts confirmation.

Owned grid: 2017-12-01 through 2026-10-09, 3,105,552 observed minute bars. Six calendar months of warm-up gives
**2018-06-01** as the preregistered main start. No shared caches were rebuilt or data spliced. Full early 2018 is
reported only as short-warm-up sensitivity. 2023+ is previously seen history, not a fresh holdout. All times below are CT.

## Results

All dollar performance below is **per 1 NQ**, after $7.25 commission and one tick per market/stop fill; limit exits have
no slippage. One MNQ is one-tenth these modeled dollars, with a separate real micro fee schedule still needed.

| variant | trades | win | avg | profit_factor | max_dd |
|---|---|---|---|---|---|
| combined | 1030 | 68.1% | $330 | 1.65 | $16,141 |
| breakout_alone | 765 | 76.2% | $262 | 1.58 | $18,964 |
| momentum_alone | 365 | 51.5% | $540 | 1.92 | $13,655 |

Whole, longs and shorts, primary window:

| variant | side | trades | win | avg | t | profit_factor | sharpe | sortino | calmar | ulcer | max_dd |
|---|---|---|---|---|---|---|---|---|---|---|---|
| combined | all | 1030 | 68.1% | $330 | 5.58 | 1.65 | 1.87 | 2.90 | 2.42 | 5.54 | $16,141 |
| combined | long | 565 | 71.5% | $295 | 4.12 | 1.66 | 1.38 | 2.00 | 1.00 | 4.55 | $19,251 |
| combined | short | 465 | 63.9% | $372 | 3.80 | 1.63 | 1.27 | 2.08 | 1.15 | 8.22 | $17,337 |
| breakout_alone | all | 765 | 76.2% | $262 | 4.32 | 1.58 | 1.45 | 1.82 | 1.22 | 6.01 | $18,964 |
| breakout_alone | long | 431 | 77.3% | $195 | 2.60 | 1.47 | 0.88 | 1.06 | 0.33 | 10.01 | $29,014 |
| breakout_alone | short | 334 | 74.9% | $348 | 3.50 | 1.69 | 1.17 | 1.51 | 0.85 | 8.64 | $15,820 |
| momentum_alone | all | 365 | 51.5% | $540 | 4.70 | 1.92 | 1.56 | 3.85 | 1.66 | 4.59 | $13,655 |
| momentum_alone | long | 186 | 57.0% | $566 | 3.99 | 2.13 | 1.31 | 3.13 | 1.41 | 3.73 | $8,586 |
| momentum_alone | short | 179 | 45.8% | $512 | 2.81 | 1.76 | 0.94 | 2.38 | 1.14 | 4.14 | $9,272 |

2018–22 begins June 2018; 2023+ ends at available October 2026 data:

| variant | period | side | trades | avg | t | profit_factor | sharpe | max_dd |
|---|---|---|---|---|---|---|---|---|
| combined | 2018-22 | all | 553 | $209 | 2.78 | 1.44 | 1.26 | $16,141 |
| combined | 2018-22 | long | 305 | $136 | 1.58 | 1.32 | 0.71 | $19,251 |
| combined | 2018-22 | short | 248 | $299 | 2.30 | 1.55 | 1.04 | $17,337 |
| combined | 2023+_seen | all | 477 | $470 | 5.05 | 1.86 | 2.50 | $12,149 |
| combined | 2023+_seen | long | 260 | $481 | 4.10 | 2.03 | 2.03 | $11,353 |
| combined | 2023+_seen | short | 217 | $456 | 3.06 | 1.71 | 1.53 | $14,884 |
| breakout_alone | 2018-22 | all | 408 | $121 | 1.52 | 1.27 | 0.70 | $18,964 |
| breakout_alone | 2018-22 | long | 230 | $76 | 0.77 | 1.18 | 0.35 | $29,014 |
| breakout_alone | 2018-22 | short | 178 | $180 | 1.38 | 1.35 | 0.63 | $15,820 |
| breakout_alone | 2023+_seen | all | 357 | $422 | 4.59 | 1.94 | 2.26 | $13,920 |
| breakout_alone | 2023+_seen | long | 201 | $331 | 2.92 | 1.79 | 1.45 | $9,689 |
| breakout_alone | 2023+_seen | short | 156 | $540 | 3.57 | 2.10 | 1.75 | $12,115 |
| momentum_alone | 2018-22 | all | 203 | $508 | 3.65 | 2.04 | 1.63 | $11,922 |
| momentum_alone | 2018-22 | long | 107 | $380 | 2.59 | 1.87 | 1.16 | $8,586 |
| momentum_alone | 2018-22 | short | 96 | $650 | 2.66 | 2.18 | 1.18 | $7,586 |
| momentum_alone | 2023+_seen | all | 162 | $580 | 3.02 | 1.82 | 1.50 | $13,655 |
| momentum_alone | 2023+_seen | long | 79 | $818 | 3.06 | 2.38 | 1.48 | $7,586 |
| momentum_alone | 2023+_seen | short | 83 | $353 | 1.29 | 1.43 | 0.65 | $9,272 |

Annual net dollars, 2018 partial and 2026 year-to-date:

| period | breakout_alone | combined | momentum_alone |
|---|---|---|---|
| 2018_partial | $4,722 | $8,828 | $10,504 |
| 2019 | $-2,549 | $-4,694 | $-3,924 |
| 2020 | $22,104 | $32,627 | $13,009 |
| 2021 | $22,725 | $40,087 | $23,442 |
| 2022 | $2,538 | $38,712 | $60,076 |
| 2023 | $26,981 | $41,894 | $17,553 |
| 2024 | $27,897 | $43,960 | $17,773 |
| 2025 | $35,983 | $45,934 | $17,987 |
| 2026 | $59,900 | $92,227 | $40,582 |

The full-2018 sensitivity includes 1,075 combined trades, versus 1,030 after the registered warm-up exclusion. Its total is $334,963; the primary total is $339,575. All 1,075 entries and their net P&L match the archived independent replica to floating-point precision. The later start improves the total because the excluded period lost money; it was fixed from warm-up requirements, not selected here from returns.

Within combined Twin, BO contributes 692 trades at $222 each and MO 338 at $550 each. Those are attribution figures; the independently traded legs above have different opportunities. Separate year/side metrics and price-normalized t diagnostics are saved.

## Placebos and account level

Seen-2023+ Sharpe moving-block-bootstrap 90% intervals (2,000 samples):

| variant | actual | p5 | p95 |
|---|---|---|---|
| combined | 2.50 | 1.73 | 3.32 |
| breakout_alone | 2.26 | 1.33 | 3.25 |
| momentum_alone | 1.50 | 0.76 | 2.28 |

Random-side conditional controls, 1,000 assignments:

| variant | actual_mean | conditional_mean | p95 | p_ge_actual |
|---|---|---|---|---|
| combined | $330 | $46 | $125 | 0.001 |
| breakout_alone | $262 | $54 | $139 | 0.001 |
| momentum_alone | $540 | $47 | $202 | 0.001 |

Both directions were executed from each actual entry with mirrored stop/target distances and the source time exits. The actual-side reconstruction matches every primary trade in all three runs. These controls support direction value **conditional on the actual entries**; flipped trades can overlap or change later opportunities, so this is not a full-system placebo. Archived full-system/independent placebo evidence remains historical context. Bootstrap and drawdown-permutation results for all sides are in the output CSVs.

One-year daily block-bootstrap probability of hitting a $2,000 EOD floor (5,000 samples):

| variant | 1_MNQ_proportional_cost | 1_NQ |
|---|---|---|
| breakout_alone | 9.4% | 65.3% |
| combined | 6.5% | 62.6% |
| momentum_alone | 0.5% | 56.7% |

This is a **standalone risk diagnostic, not an Apex eligibility or payout simulation**. It uses realized exit-date P&L, so open losses, daily loss limits, account liquidation, fees at the real micro rate and holiday restrictions are not fully represented. A low number does not make the source legal or safe. At 1 MNQ, combined realized daily drawdown is about $1,614; its 95th-percentile one-year block-bootstrap drawdown is about $2,353. Sequential closed-trade drawdown is larger than daily-netted drawdown; both views are saved.

The user requested individual testing, so no addition/replacement, portfolio optimisation or funded-payout bench was run. No account-scale recommendation follows from this report.

## What could make this wrong

- **Actual platform/session behavior:** SetExitOnClose can fire at midnight on a differently configured chart. The related MC v2 report has UseHolidayTimes/EarlyFlatten inputs not present in the upload. Neither its entries nor its returns are substituted for the literal uploaded-code replay. No new MultiCharts report was produced.
- **Protection and fills:** with IOG off and exits issued only after MarketPosition changes, the entry minute has no protective order. The port preserves that exposure. Stop/target conflicts use the existing conservative intrabar convention; targets fill at touch and calculated ATR targets can be fractional ticks. Tick rounding, limit queue, adverse selection and the source's lack of live stop guards remain concerns.
- **Sizing:** median initial BO stop risk is $6,290/NQ, largest $39,945; worst realized trade is -$11,717. At one MNQ the largest nominal stop risk is still about $3,995, above a $2,000 trail. The supplied Qty=1 means one NQ in these tables, not one MNQ.
- **Calendar:** combined has 48 calendar-midnight crossings and four flatten-deadline breaches; those are different classifications. The breaches are BO on 2018-11-23, 2020-05-25, 2021-09-06 and MO on 2024-07-04. The last MO-only breach persists when that leg trades alone. All actual exits, including seven weekend BO exits, remain in the daily series; annualized metrics use the repository's 252-observation convention. This is realized accounting, not marked-to-market equity.
- **Concentration and reused history:** the best 5% of combined trades supply about 71% of net dollars; 2019 loses and 2026 contributes a large share. BO alone has weak 2018–22 evidence (t 1.52). MO-only short 2023+ evidence is weak (t 1.29). Nothing was filtered or tuned after seeing these differences. DSR uses N=277; combined full-primary DSR is 0.995. Repeated historical success does not supply new forward validation.
- **Costs:** source's $6 total/NQ convention gives combined $339/trade; repository costs give $330, and one additional tick on each fill gives $320. Better historical costs do not fix the path/implementation issues.

## Differences between the MultiCharts code and the test

No PowerLanguage changes were written. The upload is preserved unchanged. The Python engine is the prior independent replica, with the stated 16:00 session-close interpretation and documented minute-path assumptions. It is not a licensed MultiCharts execution engine. The six-month warm-up changes the primary evaluation window, not the trading rules; old short-warm-up history remains a labeled sensitivity. Simulated cost deductions do not move the raw entry prices or recompute exit distances from slipped fills.

**Decision:** historical standalone edge remains credible enough for WATCH and further platform/forward verification. **Reject the pasted defaults for Apex use.** No new strategy, deployment or portfolio change is approved here. Tell Claude: review `agents/codex/results/twin_uploaded_standalone.md`; exact-code replication matched, with standalone BO/MO diagnostics and unresolved execution/account constraints.
