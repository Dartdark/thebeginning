# FC 2B export audit: WATCH — inputs match, but this is a different run from the overview

Summary: The supplied @NQ export has 826 trades and $233,930.00 gross, with no commission or slippage.
Its settings match the supplied code inputs; it is not the overview's 856-trade, cost-adjusted MNQ report.
The largest loss crosses the nominal stop in the entry minute and exits at the following minute's open.
Analytic repo-cost rescore stays profitable, but does not verify MNQ fees, signal parity or prospective performance.
Obtain the overview's exact source ledger, Volume/Ticks observations and forward log before promotion or new variants.

Plan: not applicable — existing-export reconciliation, not a new strategy/backtest or preregistered return trial.
Script: `analysis/codex_fc2b_report_audit.py`; inputs: `agents/codex/inputs/fc2b/`.
Outputs: `analysis/outputs/codex_fc2b_report_audit/`. New strategy trials **0**; analytic cost rescores **1**.

## Rule and settings as supplied

30-minute opening drive on 1-minute @NQ: ORStart 830, ORMinutes 30, ExitTime 1458; ZMin 1, ZLookback 60,
MinWarmup 20; stop 100 points, trail 150, break-even 0.66R, fixed one contract. All ten input values match the code.
Settings: point value $20, one-minute compression, Classic, Bar Magnifier Disabled, initial capital $100,000,
commission "No Commission [No Commission]", slippage "0$ per Trade".
The export does not establish the chart's Build Volume On setting, IOG checkbox, exact session template or real
broker/order settings. "Automate Trading (H): Off" is recorded; no live state or account activity is inferred.

Settings Start Date 2017-05-30 09:01:00, End Date 2026-10-23 02:23:00; actual trades
2017-05-30 09:01:00 through 2026-10-16 09:48:00. Source timestamps are naive/chart-local; no export-time
timezone conversion is invented. Input source contains live-value comments, which authorize no deployment.

## Reconciled export results

All 826 entry/exit pairs are complete, one contract each. Every trade's reported profit exactly equals
side×(exit−entry)×$20. Summary counts, gross profits/losses, total and closed-equity DD reconcile to the ledger.
Longs 404, shorts 422; all entries stamped 09:01, all exits same date.

| Accounting | Trades | Total/NQ | Average/NQ | Win | PF | Closed-trade DD/NQ |
|---|---:|---:|---:|---:|---:|---:|
| Export, no costs | 826 | $233,930.00 | $283.21 | 60.90% | 1.5491 | $14,925.00 |
| Analytic $17.25/NQ debit | 826 | $219,681.50 | $265.96 | 60.41% | 1.5090 | $15,201.00 |

The cost debit is the repo assumption $7.25 commission plus one $5 tick each market/stop fill. It changes no fills,
signals, orders or stop anchors. It is an arithmetic accounting sensitivity, not an execution simulation, fresh
edge test or verified MNQ result. Full period/year/side ledger summaries are saved. No new bootstrap, strategy
backtest, placebo, full minute replay or funded bench was run for this audit.

## Why it does not reproduce the overview

The overview claims 856 trades from 2017-02-02, 416 longs/440 shorts, and $22,126 net per MNQ.
This export has 826 trades from 2017-05-30, 404 longs/422 shorts. All 30 missing trades occur in 2017; 2018–2026
annual counts match. Shorter initial history/warm-up could explain the early count difference, but is unproven.
Later annual profits also differ; some PDF net profits exceed this export's gross profit at the same point value.
Fees and missing 2017 trades alone cannot reconcile that. Different entries/prices/data/settings history or
report postprocessing remain possible causes; no cause is selected without paired original ledgers.

| Year | Export trades | Overview trades | Export gross/NQ | Overview claimed net ×10 |
|---|---:|---:|---:|---:|
| 2017 | 53 | 83 | $10,540.00 | $6,160.00 |
| 2018 | 83 | 83 | $21,795.00 | $20,605.00 |
| 2019 | 97 | 97 | $10,800.00 | $9,580.00 |
| 2020 | 83 | 83 | $12,330.00 | $12,815.00 |
| 2021 | 85 | 85 | $35,640.00 | $34,360.00 |
| 2022 | 95 | 95 | $55,580.00 | $52,445.00 |
| 2023 | 82 | 82 | $5,795.00 | $4,680.00 |
| 2024 | 91 | 91 | $28,610.00 | $27,525.00 |
| 2025 | 89 | 89 | $37,865.00 | $38,410.00 |
| 2026 | 68 | 68 | $14,975.00 | $14,680.00 |

In 2020 export gross $12,330 is below overview NQ-equivalent net $12,815; in 2025 gross $37,865 is below net $38,410.
The overview may legitimately apply costs outside MultiCharts, so its claim is not disproved merely by the raw
zero-cost Settings. The exact source report and accounting transformation are still required.
Raw max win $8,870 / max loss −$3,835 become $887 / −$383.50 at MNQ point value; the overview's $885.50 / −$385
extrema are each consistent with a $1.50 micro debit, but that observation does not reconcile the annual ledgers.

## Execution and risk findings

- **Entry-minute exposure:** 2020-03-03 short enters 8780.25 in bar 09:01; nominal stop 8880.25. Owned entry-minute
  high 8978 crosses that level. The reported exit is 8972 at bar 09:02 open: **−191.75 points / −$3,835 per NQ**.
  The second overshoot, 2024-09-04, is a long losing 119.5 points / −$2,390. Both reported entries/exits match the
  owned minute opens; these are spot checks, not whole-strategy/data parity. See `entry_minute_loss_spotchecks.csv`.
  Under the source's documented IOG-off configuration, its first next-bar stop is only generated after the entry
  bar closes. No hypothetical protective fill or corrected-stop P&L was substituted into the ledger.
- **Moving stops:** BE/trail updates use completed bar extrema, act next bar and can already be on the wrong side
  of market after a reversal. No stop-rejection/fallback evidence is supplied. Replaying them retroactively within
  the triggering bar would be a different implementation.
- **Volume semantics:** the code weights `Volume`; official MultiCharts intraday documentation defines this as
  up-tick volume/count. Our `NQ_Bar_Exporter.txt` exports `Ticks`, the total volume/count, under CSV `volume`.
  Do not claim signal parity from total-volume OHLCV alone or silently replace the input. Obtain paired
  Time/Volume/Ticks/barDelta and daily ratio/z observations with actual Build Volume On settings.
- **Risk definitions:** export strategy DD **$18,870.00**, closed DD
  **$14,925.00**, max trade MAE **$3,955.00**, all per NQ
  before fees. A closed-equity-peak plus trade-MAE calculation gives **$16,750.00**; it is not
  the same statistic as MC Max Strategy Drawdown, which can reflect different open-equity peak handling.
  No drawdown-definition mismatch is papered over, and neither number is an Apex breach probability.
- **Micro costs:** **141 trades (17.1%) earn exactly +$20 gross/NQ = +$2 at MNQ point value**.
  Actual micro round-trip costs above $2 would turn these outcomes negative; costs exactly $2 make them flat.
  A higher fee-adjusted losing-trade count need not eliminate positive overall expectancy. Recalculate using
  actual micro fees/fills; dividing full-contract net by 10 is not proof of micro net or its win rate.
- **Trading clock:** all positions are intraday in the supplied list; 4 use the
  platform End of Day Exit label rather than the explicit time order. Session/holiday handling needs inspection
  before relying on SetExitOnClose. Bar 09:01 is a close stamp: its open corresponds to 09:00 CT under owned data.

## Evidence status and next step

This export verifies a profitable historical gross ledger and matching numerical inputs. It does not supply the
overview's exact ledger, confirm Build Volume On/IOG settings, reproduce entry signals, validate live fills,
establish prospectively frozen performance or earn the repo's B grade. The earlier 211-trade holdout applies to
the original range-stop rule; current 100/150 exits were selected on the full sample, as the overview discloses.
Its unfinished 30-signal forward test and later-period selection history remain material.

The PDF's 2024–26 statement of 239 trades still differs from its own yearly totals 248. The new workbook also
has 248 trades in those years, so that paragraph likely describes an older window; exact run identity is needed.

Next smallest steps: obtain the exact 856-trade report/ledger behind the PDF and its cost calculation; obtain a
small paired Volume/Ticks/ratio/z export and the existing forward log; reconcile the supplied version first.
Any entry-bar protection, market fallback or total-volume substitution must be a separately frozen amendment,
with before/after parity and a declared trial status. Do not tune another filter or treat retrospective 2023+
results as a clean holdout. Portfolio addition/replacement and timed Apex risk come only after those gates.

## Reproduction and sources

```bash
/workspace/venvs/thebeginning/bin/python analysis/codex_fc2b_report_audit.py
```

User inputs are preserved byte-for-byte with hashes; two existing price CSVs were read only for the specific
overshoot observations. No data cache, strategy engine, rank, trading plan, live/VPS/broker file or API key was
changed/accessed. Source-document instructions are treated as evidence, not orders to trade or deploy.

Primary platform references:
[Volume](https://www.multicharts.com/trading-software/index.php?title=Volume),
[Ticks](https://www.multicharts.com/trading-software/index.php?title=Ticks).
Uploaded inputs: `report.xlsx`, `source.txt`, `overview.pdf`, plus its text extraction in the input directory.

Tell Claude: review `agents/codex/results/fc2b_report_audit.md`; 826 zero-cost NQ trades do not reconcile to the
856-trade net-MNQ overview, entry-minute stop exposure is demonstrated, and volume/input parity remains open.
