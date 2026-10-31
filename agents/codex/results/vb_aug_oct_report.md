# Vault Break August–October upload: WATCH — added losses; execution comparison unresolved

Summary: Supplied 20-MNQ backtest reports -$14,230.00, 39 trades, 51.3% wins and PF 0.69, before costs.
October contributes -$11,690, including -$7,400 after the earlier October-9 cutoff. September remains positive.
Closed-trade DD is $16,120 at 20 MNQ; reported strategy DD is $16,340. Broker results remain unverified.
Bar Magnifier is disabled, with Classic fills and zero fees/slippage; this is not comparable enough for a new deterioration probability.
The prior 8–11% tail result applies only to the original window. No new optimization or setting change follows.

Plan: [`vb_aug_oct_report_addendum.md`](../plans/vb_aug_oct_report_addendum.md), **26ed63e**.
Parent: [`vb_recent_risk.md`](vb_recent_risk.md), baseline audit **2f9f581** / preregistration **832f277**.
Script: `analysis/codex_vb_aug_oct_report.py`. Outputs: `analysis/outputs/codex_vb_aug_oct/`.
Source snapshot: `agents/codex/inputs/vb_aug_oct/vb_aug_oct_mnq.xlsx`, SHA256 `44b179d751eb6e0c23ddb44d2f394d2f19a9ce92cb5ddb7687e736c55bf3bda0`.
New economic models/return replays: **0**. This reconciles a user-supplied backtest, not broker records or a fresh holdout.

## What the report establishes

Report settings: MNQ, $2/point, 20 contracts, target 40 / stop 75, max 3/day, 30-minute chart, original .30 ATR15 rule.
Export setting starts 2026-08-27 12:30:00; nominal end is 2026-10-23 16:00:00. First/last trades are
2026-08-27 12:30:00 / 2026-10-21 14:00:00. No open trades are reported. The report's daily table ends October 21.
October 22–23 native-bar completeness is unverified. August 25–26 are outside this upload's trade range.
The attached Apex Target Guard has StartBalance=150000 / TargetBalance=159050; logger tag VB150.
Every observed exit is a normal target, stop or VB EOD, with no guard-labeled exit. This does not independently verify guard behavior.

| Metric | All = long, at 20 MNQ |
| --- | ---: |
| Reported P&L before fees/slippage | -$14,230.00 |
| Closed trades | 39 |
| Winners / losers | 20 / 19 |
| Win rate | 51.3% |
| Average winner / average loser | $1,600.00 / $2,433.16 |
| Recomputed profit factor | 0.692 |
| Closed-trade peak-to-trough DD, including initial zero | $16,120.00 |
| Reported strategy DD (includes open-position effects) | $16,340.00 |
| Gross P&L / closed-trade DD per one MNQ | -$711.50 / $806.00 |

Shorts: zero, ratios N/A. `Strategy Analysis!B21` stores **negative** PF; standard PF is positive gross profits divided by
absolute gross losses: $32,000 / $46,230 = 0.692. The same sign anomaly affects the average win/loss ratio.
Some unused/undefined cells show `#ERROR!`; totals above reconcile to prices and the complete closed-trade list.
Do not interpret the workbook's Adjusted Net Profit as a fee-adjusted broker result.

## Month and added-period attribution

| Observed month | Trades | Win | Gross at 20 MNQ | Gross / 1 MNQ |
| --- | --- | --- | --- | --- |
| 2026-08 | 2 | 0.0% | -$6,000.00 | -$300.00 |
| 2026-09 | 26 | 61.5% | $3,460.00 | $173.00 |
| 2026-10 | 11 | 36.4% | -$11,690.00 | -$584.50 |

August contains August 27–28 trades only. October's last observed trade is October 21.
September is positive, consistent with the earlier audit. October is the principal new weakness.

| Segment | Trades | Win | Gross at 20 MNQ |
| --- | --- | --- | --- |
| through_Oct9 | 35 | 54.3% | -$6,830.00 |
| after_Oct9 | 4 | 25.0% | -$7,400.00 |
| all_upload | 39 | 51.3% | -$14,230.00 |

The post-cutoff four trades are October 19 stop, October 20 stop, October 21 target and stop.
They are **backtest events**; the October 20 chart trade is not proof of a broker fill, given the prior rejected-entry evidence.

## Stop versus win arithmetic and native costs

At this report's **20 MNQ**, the full stop is **$3,000** and target **$1,600**, before costs.
The point ratio remains 75/40. All 20 winners reach the full target; 13 losses are full stops and
6 are time exits. At the observed average win/loss mix, break-even win rate is
60.3%; actual win rate is 51.3%.
There is no new larger point stop in this export. Dollar losses are larger because its quantity is 20 MNQ versus the earlier eight-MNQ examples.

The workbook charges **no commissions and no slippage**. Apply the already registered $1.04 / $1.24 RT native-MNQ fee
assumptions and one adverse tick at market entry and stop/time exit to these same trades:

| Assumed RT fee/MNQ | Net / 1 MNQ | Net at 20 MNQ | Closed-trade DD at 20 MNQ |
| --- | --- | --- | --- |
| $1.04 | -$781.06 | -$15,621.20 | $16,784.40 |
| $1.24 | -$788.86 | -$15,777.20 | $16,856.40 |

These are illustrations, not actual fees, broker fills or a selected position size. They do not model changed fills, liquidity,
portfolio exposure or account-liquidation rules. Multiplying an unchanged backtest by size cannot establish account survivability.

## Common-period comparison: do not call this execution slippage

Compare exact entry-bar timestamps/side with the saved unfiltered NQ SP report, 2026-08-27–2026-10-09.
Use the repository's `read_trades` and `compare(window=0)`, normalized to points per contract. No fuzzy match or deleted residual.
Both inputs are chart backtests. Pairing output is relabeled from the generic tool's live/bt terminology.

35 uploaded / 34 reference trades: 32 matched,
3 uploaded-only, 2 reference-only.
Uploaded gross is -$6,830.00; reference gross scaled to 20 MNQ is
-$3,780.00. Total points difference is -76.25 per contract;
matched-pair points difference is 0.00.
All residuals and price differences are retained in `common_calendar_pairing.csv`.

Examples: upload adds an October 2 11:30 stopped trade, lacks the reference's October 5 13:00 target,
and has different October 6 re-entry sequencing. **Both reports have Bar Magnifier disabled.** Their limit-fill assumptions differ:
uploaded **Fill Limit price or better (Classic mode)**; reference **Fill limit price exceeded by 1 points.**.
MNQ versus NQ source prices also differ. These observations do not prove which setting caused each mismatch.
Thirty-minute OHLC without native intrabar replay can change exit ordering, same-bar fills and later re-entries.
We cannot repair that by assuming a favorable path or by choosing whichever report has better returns.

## Drawdown verdict and what is still needed

This export **increases concern**: the newer October trade list adds substantial losses. It does not establish permanent
edge decay, and the original 8–11% historical frequency must not be attached to this longer, differently simulated sample.
No new bootstrap alarm or optimization was fitted to this upload. The four bracket alternatives remain rejected by the earlier design gate.
The original audit's complete one-minute history still ends October 9; a report adds results, not the missing raw day/overnight bars.

Next comparable evidence: rerun the **same rule/quantity/dates** in a research chart with one-minute Bar Magnifier, explicit actual
commission/slippage and the documented reference limit-through assumption. Export its report/settings and matching day/overnight minute
bars through October 23. This is a controlled execution check, not an exit-parameter search. An independent offline replay can then
attribute the October 2/5/6 residuals. Merely enabling Bar Magnifier does not establish identical source data or fills.
For the actual-account side, a complete broker fill/exit/fee export is still required. No live chart/settings, account, logger or VPS was changed.

Checks: 39 adjacent entry/exit pairs, matching quantities/order numbers; every price × 20 × $2 equals reported trade P&L;
cumulative, daily, monthly and report totals/win counts reconcile; initial-zero closed-trade DD agrees with reported $16,120.
Source workbook is unchanged and preserved byte-for-byte. No cache rebuilt, library installed, new strategy variant or account bench run.
Additional weekday-based descriptive ratios are in `descriptive_standard_metrics.json`; their calendar is not proof of bar coverage.

Reproduce from repo root with the previously configured Python:

```powershell
$vbPython = 'C:\Users\dmoto\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $vbPython -B analysis/codex_vb_aug_oct_report.py --source agents/codex/inputs/vb_aug_oct/vb_aug_oct_mnq.xlsx
```

Claude review path: `agents/codex/results/vb_aug_oct_report.md`.
