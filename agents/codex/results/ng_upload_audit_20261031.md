# NG upload intake: precision repair needed before a return test

Summary: All ten uploaded files were downloaded, hashed and archived without changing their bytes.
They contain 1,086,667 bars, January 3, 2017 through October 30, 2026, with valid one-minute labels.
All 4,346,668 OHLC values have exactly two decimal places and lie on a 0.01 grid; NG's native tick is 0.001.
The current files are not admitted for native fill/cost testing. Export settings and source/calendar gates remain open.
No strategy returns or portfolio outcomes were computed; no economic trial was consumed.

## Completed checks

Script: `analysis/codex_ng_upload_audit_20261031.py`.
Outputs: `analysis/outputs/codex_ng_upload_audit_20261031/summary.json`, `yearly_quality.csv`,
and `provisional_thursday_coverage.csv`.
Raw archives and SHA256 manifest: `agents/codex/inputs/ng_upload_20261031/`.
Gzip archives preserve the uploaded CSV bytes exactly; the audit can rerun from these archives when the original
attachment workspace is unavailable. They remain separate from admitted data and do not replace another export.

| Check | Observed result |
|---|---:|
| Files | 10, labelled 2017–2026 |
| Rows | 1,086,667 |
| Duplicate date/time rows | 0 |
| Invalid timestamps/numeric cells | 0 / 0 |
| OHLC ordering violations | 0 |
| Serialized prices with exactly two decimals | 4,346,668 / 4,346,668 |
| Prices off the 0.01 grid | 0 |
| Daily clock range in every file | 08:00–15:15, chart timezone unconfirmed |
| Provisional regular Thursdays in 2018–22 | 261 |
| Those Thursdays with both 08:00 and 10:00 labels | 258 |
| Those Thursdays with every label from 08:00 through 10:00 | 223 |

Thursday counts are a timestamp census under the provisional CT assumption, not a verified historical EIA
release universe. Holiday dates, shifted release times, bar-open versus bar-close semantics and missing minutes
still require admission. A missing minute is neither a zero return nor proof of a corrupt file. We did not forward
fill prices or compute Thursday/other-day performance. Later years were inspected for data quality only.

## Precision issue and concrete remedy

[CME NYMEX Chapter 220](https://www.cmegroup.com/rulebook/NYMEX/2/220.pdf), sections220102.B/C,
specifies 10,000MMBtu per standard NG contract and a 0.001 price increment, worth $10 per tick.
The observed exported grid is ten native ticks wide. This is not enough to reconstruct the lost within-cent prices
or establish native slippage and protective-order fills. Appending a third zero does not restore the information.

If the values were rounded to the nearest cent, each endpoint can differ by up to0.005: a two-fill P&L can differ
by up to$100 per standard NG, or$10 for a1,000MMBtu micro-sized price exposure. These are conditional error bounds,
not measured execution losses or a certified native MNG backtest. Truncation or another exporter rule changes
the bound; the actual formatting method remains unconfirmed. No user NG fee measurement was supplied.

The existing `tools/exporters/NQ_Bar_Exporter.txt` already provides a `Decimals` input. Its defaults
(`Decimals(2)`, `StartTime(800)`, `EndTime(1515)`) match the observed formatting/window, but this does not prove
which indicator or settings produced these files. The needed export settings, on a research chart, are:

- NG prices with **Decimals=3 or greater**, preserving the actual 0.001 ticks.
- FilePrefix `NG_1min_`, using a separate output folder to preserve this original delivery.
- One-minute bars and a documented chart timezone. Full-session history is preferred: `StartTime=0`,
  `EndTime=2359`, with a chart session template that actually includes those hours.
- Document symbol/feed, chart session, continuous-contract construction and roll/back-adjustment settings.
  An exporter time filter cannot restore bars excluded by the chart session.
- Confirm whether labels are bar closes. This indicator writes bar-close/chart-time labels and total `Ticks`
  under the CSV `volume` column; use that interpretation only if this exporter is confirmed.

Only re-exporting the underlying unrounded chart/data can repair price precision. No exporter implementation
change is necessary if this is the indicator used. Nothing was installed, run on the user's PC, or changed live.

## Research gate and next work

The intended source lead remains SSRN3575861, a scheduled NG short reported in the earlier targeted screen.
This upload materially improves price-data availability, but it does not resolve full executable source rules,
the paper's decay warning, native micro/standard execution or the historical release calendar. A fresh bounded
source search found the same manuscript candidates; SAGE full text was inaccessible and the IAEE appendix URL
returned404. The earlier Reading access denial and Liverpool embargo were not bypassed/retried.

Source-derived findings and the five paper questions remain in
`agents/codex/results/targeted_diversification_20261030.md`; this report is a data audit, not a new paper review.
The existing research-data question asks for chart/feed/session/timezone/roll/precision settings. Pending that
answer and a native-precision export, no evidence sheet can truthfully declare native TEST eligibility.

After repair: reconcile the chart/export metadata, admit historical EIA events and native costs, pin full rules,
then commit the evidence, bounded code/plan/reservation and checked-head lease before a2018–22return screen.
Only a passing frozen design earns2023+historical validation and current integer BASE/ADD/REPLACE/EMPTY account
comparisons. No winner, Sharpe, profit factor, Sortino, Calmar, Ulcer or payout benefit is inferred from this audit.

The scout budget remains4/10hypotheses and10/30economic definitions; there is no active return reservation.
Data registerD12 is PARTIAL forNG, with the precision/metadata blockers preserved. ZC/ZS remain absent.
