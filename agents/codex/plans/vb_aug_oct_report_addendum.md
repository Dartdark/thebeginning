# Vault Break uploaded August–October report: source-audit addendum

Date: 2026-10-25. Parent plan: `vb_recent_risk.md`, preregistered at 832f277.
User supplied the MNQ MultiCharts backtest after the original incomplete-period audit. This is continuing that audit,
not a new strategy or optimization. Initial workbook inspection already exposed its summary and settings.
Do not represent this document as preregistered ignorance of the uploaded results.

- Preserve the original workbook under `agents/codex/inputs/vb_aug_oct/`, hash it, and leave the Downloads source unchanged.
- Reuse `live_vs_backtest.read_trades` after verifying equal entry/exit counts, order, quantities and closed-trade pairing.
  Reconcile price × quantity × $2 against each raw trade P&L, cumulative equity and report totals.
- Report all uploaded trades, month splits and the added post-October-9 segment. Normalize per MNQ explicitly.
  Distinguish zero-cost workbook P&L from fee/slippage assumptions and actual broker P&L.
- Use the original native-MNQ $1.04 / $1.24 RT fee scenarios, one adverse tick on market/stop fills, for illustration only.
  No parameter, execution convention or size is selected by its result.
- Compare uploaded and saved MC trades on exact entry-bar timestamps and side over their common verified calendar,
  with quantities normalized to points per contract. Preserve unmatched rows and differing exits.
- Inspect the 30-minute no-magnifier assumption, attached target guard and report coverage. A nominal end date,
  a daily zero or last trade does not prove native history completeness. No reconstructed intrabar path after October 9.
- Reuse prior historical diagnosis only for its original window. Do not apply its 8–11% frequency to the longer upload.
  Do not calibrate a new deterioration probability across mismatched instruments/fill settings or treat chart trades as fills.
- No new return model, optimization grid, strategy filter, full account bench or live change. The four-alternative stop remains.

Deliver reproducible `analysis/codex_vb_aug_oct_report.py`, new outputs under `analysis/outputs/codex_vb_aug_oct/`,
and `agents/codex/results/vb_aug_oct_report.md` (Summary <=5 lines). Commit/push only `codex/work`.
