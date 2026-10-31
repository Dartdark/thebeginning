# Extended-data refresh: rebuild repaired; current trade reconciliation blocked

Summary: NQ raw bars already extend through October 30, but the dashboard backtest cache ends October 9.
The standard rebuild crashes on an unfinished funded-ONB report position labeled `open`.
A scoped adapter excludes that position, preserves closed trades, and successfully rebuilds g24/ge/lab.
Five regression checks pass. Saved MC reports still end October 9–13; new bars alone cannot extend them.
Next: fresh same-input MC exports through October 30, then refresh the dashboard and reconcile chart trades.

Source: `claude/nq-trading-strategy-params-5h9d20` at `86df2c0fa4b0e530b2c29caddd364830d12edab3`.
Script: `analysis/codex_refresh_audit.py`.
Outputs: `analysis/outputs/codex_refresh_audit/`.
Economic trials: 0. This is a data/import audit, not a strategy or sizing decision.

## What was checked

Read NEW_CHAT_BRIEF, CLAUDE, TODO and LESSONS from the requested GitHub branch, then the Codex builder brief and execution references.
Ran the documented `analysis/build_lab.py scratch_data` on that source snapshot.
It wrote g24/ge, then failed adding ONB_ML2_MC at `portfolio.paths` (`adv[-1]` on an empty segment).

The report's final pair is an EntryShort at **2026-10-12 09:15**, followed by an ExitShort whose signal is **`open`**
and whose date is **2026-10-12 00:00**. Its $1,505 marked profit is not a completed trade's realized profit.
The existing importer produces j0=546 and j1=0, so the path slice is empty.

The new adapter wraps the existing importer for the original builder invocation. It removes only explicitly
`open` exit sentinels, using the same grid-date mask as the existing importer to preserve row alignment.
It does not guess their eventual exits, silently discard other invalid paths, or change report files.
The adapter is scoped to this command and restored afterward. The production importer remains unchanged;
running the original builder directly will still encounter this defect until its owner adopts the fix.

## Coverage

| Source | Coverage |
|---|---|
| Rebuilt NQ grid | Through 2026-10-30 |
| Existing dashboard daily cache | Through 2026-10-09 |
| VB report Settings / last closed exit | 10/09 / 10/06 |
| Evaluation ONB ADX30 report Settings / last closed exit | 10/13 / 10/12 |
| EOS report Settings / last closed exit | 10/11 / 09/18 |
| Bridge Monday report Settings / last closed exit | 10/13 / 10/05 |
| Available VPS trade-log files | 10/20–10/30; no files for 10/12–10/19 |

The last trade is not the report coverage end: no-signal days inside a report are valid. The Settings dates
establish the separate export cutoff. `report_coverage.csv` retains both fields for all ten inspected reports.
`excluded_open_positions.csv` records the unfinished position without treating it as a closed trade.

The rebuild completed with 343 closed funded-ONB trades rather than 344 rows including the open mark.
All eight standard report legs and Bridge loaded; g24.pkl, ge.pkl and lab.pkl were produced locally (git-ignored).
The builder also ran its built-in historical five-, seven- and eight-leg smoke scores, saved in `build_output.txt`.
Those are the builder's **old example portfolios**, not the current ten-strategy plan. They must not be used as
evidence that the current plan or Swing Target adoption has been revalidated.

## Why the TODO remains open

`build_lab.py` and `live_panels.py` import saved MC tickets; neither regenerates strategy signals from new bars.
Running live_panels after this rebuild would extend its daily index using old tickets, recording zeros after
report coverage ends. That would make unknown days look like observed no-trade days. The dashboard cache was
therefore left intact, and no updated plan odds, missed-trade count, drift verdict or live fill claim is reported.
The requested 10/12–10/28 reconciliation is not complete. The existing logger records chart-model positions,
not broker executions, so even a fresh same-day comparison needs that distinction.

## Validation and next action

Five regression cases: unfinished sentinel; case/whitespace normalization; out-of-grid dates without alignment
shift; unrelated exit labels preserved; unequal entry/exit counts rejected. Full adapted rebuild passed on the
source commit above. No live trading, VPS, account settings, TODO, trading plans or strategy code was changed.

On the research/home PC, export the same-input VB, evaluation ONB ADX30, EOS and Bridge reports through October 30.
For the current funded-plan replay, its other report legs also need current coverage. Preserve the existing
report filenames/settings and include native broker order/execution records if actual fills are to be reconciled.
Then rebuild with the adapter, add an explicit coverage gate before publishing dashboard cache rows, and
complete the per-strategy expected/chart/broker reconciliation. Earlier missing logs remain unknown unless recovered.

Reproduction (from the source snapshot, Python with numpy/pandas/numba/openpyxl/scipy):

```
python3 analysis/codex_refresh_audit.py --rebuild
python3 agents/codex/test_refresh_audit.py
```

The audit script is delivered on codex/work; reproduce the recorded source result by copying it and its tests
onto the pinned Claude source commit in a separate checkout. Output summary.json records that source SHA.
Independent verification and production integration remain pending.
