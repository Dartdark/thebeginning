# Direct VB split-stop change: REJECT on the updated 150K evaluation book

Summary: The user wants to change the book; Twin2, DT2 and finish mode are already part of the baseline.
Tested one direct VB change:7 of15 MNQ exit at−37.5 points;8 retain the75-point stop;40-point targets unchanged.
Despite a smaller nominal stop, passes fall38.3%→35.7%, or35.0%→33.8% with adverse DLL execution.
Recovery gains lost exceed stop losses saved. The fixed design gate fails under both fill protocols.
No new2023+ variant results, threshold rescue, MultiCharts code or live change follows.

Evidence: [`vb_loss_split_20261110.md`](../evidence/vb_loss_split_20261110.md).
Initial preregistration **fe5bf0bb**; pre-outcome input amendments **4d95ed29 / 03a660e1**;
date-schema repair **c46fc05e**, before candidate outcomes.
Script: `analysis/codex_vb_loss_split_20261110.py`; saved-output checker:
`analysis/codex_vb_loss_split_check_20261110.py`.
Outputs: `analysis/outputs/codex_vb_loss_split_20261110/`.
Trials: **one new exit proposal; four total candidate/control definitions; two DLL protocols**.
Earlier bracket/cushion and broader strategy searches remain counted; nothing resets their multiplicity.

## Scope correction and current baseline

The user's clarification supersedes the prior assumption that preserving the original book is a constraint.
The objective is better evaluation outcomes, including replacements or removing VB if warranted.
The89% is a backtest statistic; user reports all four recent live accounts ended on a large VB/ONB loss.
Neither establishes the preventable fraction. This test did not reconstruct those four broker outcomes.

Latest fetched Claude head **ec7f9571** confirms the next-purchase150K book:
VB15, ONB ADX30 risk$2750, Bridge5, EOS risk$1250, Twin cap1 v2.1 2, Dual Thrust v4 2 MNQ.
These additions and finish mode were already implemented in repository code; source says not yet compiled.
They are retained in every comparison and are not presented as newly proposed fixes.

Model the existing per-account finish rule: at start-of-day balance≥$156000, round each quantity×.5
to nearest whole, minimum1 when the original quantity is nonzero. VB becomes8; SPLIT then exits4/retains4;
REDUCED becomes6. The normal REDUCED control uses11MNQ. EMPTY removes VB entirely.
This is **single-account**, not the newer copier's group-mean finish rule; no group outcome is inferred.

## Exact test and account results

One fixed loss-side partial exit, no averaging/add-back/extra entries. The original remaining leg keeps
the same full-flat clock and maximum3 daily entries. Normal full-stop gross exposure is$1725 versus$2250
at15MNQ, before fees and gap overshoot. The targets stay40points; entries/anchors/times stay unchanged.

**Design2018–22 only:**1,270 starting dates, first2018-01-02; each exclusive30-calendar-day horizon
ends by2023-01-01. Start150000,target9000,ongoing EOD trail4000,DLL2000; intraday floor enforcement.
Assumed native commission **$1.25 RT/MNQ**, plus1adverse tick per market/stop leg; limit exit has no extra slip.
VB targets require1point trade-through. Every row uses the same dates/cost conventions and integer contracts.

| Model | Pass | Trail fail | Expire | Median successful calendar days | Fee/pass index |
|---|---:|---:|---:|---:|---:|
| BASE |38.27%|58.50%|3.23%|12|2.61×|
| SPLIT |35.75%|60.31%|3.94%|12|2.80×|
| REDUCED VB11 |34.96%|58.27%|6.77%|13|2.86×|
| EMPTY VB |31.89%|51.81%|16.30%|15|3.14×|

Above assumes ideal DLL liquidation at its threshold. The alternative uses the observed adverse minute
mark on DLL liquidation, allowing overshoot to the floor:

| Model | Pass | Trail fail | Expire | Median successful calendar days | Fee/pass index |
|---|---:|---:|---:|---:|---:|
| BASE |35.04%|62.13%|2.83%|12|2.85×|
| SPLIT |33.78%|62.68%|3.54%|12|2.96×|
| REDUCED VB11 |33.46%|61.50%|5.04%|13|2.99×|
| EMPTY VB |29.21%|57.72%|13.07%|15|3.42×|

Fee/pass is1/historical pass fraction, counting expirations as lost attempts. It excludes activation and
other expenses and is not an independence-based forecast of repeated/correlated purchases. Pass times
condition on success. DLL assumptions are modelling scenarios, not exact broker forecasts or hard bounds.

SPLIT minus BASE pass-rate change: **−2.52pp**,90% paired block band **−4.09 to−1.10pp** under ideal fills;
**−1.26pp**, band **−3.23 to+0.87pp** under adverse-minute fills.
Bootstrap:2000draws,60consecutive starting-date blocks,seed20261110. Overlapping starts are dependent.
In the ideal case only2 baseline failures become passes, while34 baseline passes are lost.
Under adverse fills16 failures become passes, but32 passes are lost. These contrasts are conditional on the model/history.

## Why trimming the loss failed

861unchanged VB entries in design. Standalone diagnostics use **normal15MNQ throughout**, without
account exits or finish mode, to isolate the exit effect. Whole and long results are identical; **shorts0/N/A**.

| VB alone | Net | Win | t | Sharpe | Sortino | PF | EOD DD | Calmar | Ulcer |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BASE15 |$91683.75|63.2%|2.52|1.09|1.64|1.22|$16177.50|1.11|5.22|
| SPLIT7/8 |$71761.75|60.3%|2.30|0.99|1.56|1.20|$15395.75|0.91|5.48|
| REDUCED11 |$67234.75|63.2%|2.52|1.09|1.64|1.22|$11863.50|1.11|4.22|

By-year results are in `design_vb_metrics.csv`. EMPTY's aligned zero-vector rows are arithmetic placeholders,
not861executed trades; it has no VB trades and its ratio statistics are N/A.

296entries trigger the shallow stop. At the normal7-contract trim:

| Original final exit | Trimmed entries | Change in total net from trimming |
|---|---:|---:|
|75-point stop |131|+$68775|
|40-point target |56|−$60956|
|Time exit |109|−$27741|

The changes sum to **−$19922**. The exit saves money on131full stops, but reduces exposure on56eventual
targets and109time exits; their combined give-up is larger. EOD drawdown barely improves and the account
race gets worse. Reduced-size/empty controls show that the proposed management is not a qualified improvement
just because nominal stop exposure shrinks. No removed-entry filter/placebo claim is made: entry count is unchanged.

## Checks, limitations and stopping decision

- Nine split-mechanics checks, three new account checks and eight inherited account checks passed before returns.
  Saved-output checks reconcile native costs, entry identity/exit ordering, annual/trade totals, trim-fate totals,
  account counts and the design-only horizon. This is our arithmetic check, not independent economic verification.
- Three preparatory launches stopped before candidate outcomes: raw2026hash mismatch, absent Git metadata in
  the isolated snapshot, and DT adapter's missing date field. Exact original raw bytes are loaded from an isolated
  `fe35af99` tree; shared data were not rewritten. Rule/variant/gates were unchanged. Manifest preserves hashes,
  versions, commits and counts; pre-outcome amendments remain committed.
- VB has2missing held closes in design. Other frozen helpers flag EOS1, DT16, Twin316 and Bridge969; counts
  include known inherited Sunday/calendar mapping limitations and are not counts of proven executable failures.
  Legacy helpers can substitute entry marks for missing minute prices, and Twin carries pre-midnight adversity
  into its exit date. This is **not UNKNOWN-aware/common-price-certified account replay**.
- Opposite sleeves' independently adverse extrema can occur at different instants. Both DLL scenarios inherit
  that aggregation defect. Positive conclusions would require a causal common-price replay; no candidate qualifies here.
- Partial-stop sequencing is inferred from one-minute OHLC nearest-extreme ordering, not recovered ticks.
  NQ prices proxy MNQ; fees are research assumptions. Brackets retain canonical raw-price anchors with
  slippage charged separately, not a newly verified actual-fill-anchor/platform implementation.
- This study differs from earlier38.9% full-history figures: design-only dates, native fees, actual calendar
  expiry, integer finish quantities and rebuilt VB. Do not mix baselines or imply all2018–26were newly tested.

Both frozen design gates fail: passes decrease and failures do not fall. **REJECT this exact split-stop
definition.** No2023+ candidate run, later bootstrap/MonteCarlo/funded bench, alternative split threshold,
parameter rescue, independent promotion or MultiCharts/live change. No general proof that VB cannot be improved.
The user's objective remains direct improvement/replacement of VB within the updated evaluation book;
this negative result does not reinstate preservation of the old book as a constraint.
