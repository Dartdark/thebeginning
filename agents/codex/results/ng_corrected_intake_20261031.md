# Repaired NG data: native precision confirmed; source and clock admission pending

Summary: All ten replacement exports were downloaded and archived separately from the failed two-decimal delivery.
They contain2,959,522bars and genuine0.001prices, with no duplicate timestamps, bad numeric cells or invalidOHLCrows.
Overnight coverage is present. The first/last labels and maintenance gap support NewYork wall time, pending instrument settings.
The full announcement paper remains unavailable through checked free routes; historical event/source admission is incomplete.
No strategy return or account benefit was computed. Do not request another precision re-export.

## Completed checks and reproducibility

Script: `analysis/codex_ng_corrected_audit_20261031.py`.
Outputs: `analysis/outputs/codex_ng_corrected_audit_20261031/`.
Raw CSV gzip archives and hashes: `agents/codex/inputs/ng_corrected_20261031/manifest.json`.
The archives decompress to the exact uploaded bytes. The older delivery and report remain unchanged for provenance.

| Item | Corrected delivery |
|---|---:|
| Files | 10,2017–2026 |
| Bars | 2,959,522 |
| First label | 2017-01-02 18:01 |
| Last label | 2026-10-30 17:00 |
| OHLC cells | 11,838,088 |
| Cells off the0.001grid | 0 |
| Cells off the old0.01grid | 10,624,829 |
| Duplicate timestamps | 0 |
| Invalid timestamp/numeric cells | 0/0 |
| InvalidOHLCordering | 0 |
| Provisional2018–22Thursday dates | 261 |
| Those dates with09:00and11:00labels | 260 |
| Those dates with every09:00–11:00label | 249 |

The sub-cent values establish a genuine precision repair, rather than two-decimal prices padded with zeros.
The new files contain overnight bars rather than the earlier08:00–15:15export window. Neither observation
certifies every event, instrument/roll convention or native micro fill. The Thursday census assumes NewYork
labels; it is not an approved strategy universe or authoritative release-calendar reconstruction. Missing bars
are preserved and have not been converted to zero returns. Later years were examined for quality only.

## Clock reconciliation before return selection

The user's screenshots identify the NQBarExporter, one-minute bars,24Hour sessions and Exchange chart time.
The old screenshot explicitly hadDecimals2/StartTime800/EndTime1515; the replacement files resolve that formatting
problem. No symbol/feed, QuoteManager exchange timezone or continuous-contract settings were visible.

[MultiCharts timestamp documentation](https://www.multicharts.com/trading-software/index.php?title=What_Affects_Chart_Timestamps)
states that Exchange uses the exchange timezone configured in QuoteManager. It cannot universally be read as Chicago.
The new file starts18:01and ends17:00; a2018clock-count diagnostic shows only250bars in hour17versus13,208in hour16,
with250labels at18:01. That strongly supports NewYork labels and the daily17:00–18:00ET maintenance interval.
This remains an inference until the configured instrument clock is confirmed; it is not a reason to test both
timezones and pick whichever earns money. The input question now asks for the exact configured clock and symbol/roll metadata.

[EIA methodology](https://ir.eia.gov/ngs/methodology.html) and the
[current schedule](https://ir.eia.gov/ngs/schedule.html) identify regular releases at10:30ETThursday, with exceptions.
A short90minutes before/cover30minutes after would be09:00–11:00ET, or08:00–10:00CT. Winter/summer conversion
fixtures pass. If these bars are NewYork-labelled, entering08:00by the raw clock would be an hour early.
The exporter uses bar-close labels; exact next-executable fills and source decision times must respect that convention.

The currentEIApage lists2025–26exceptions and cannot retrospectively certify2018–22holiday releases. EIA's
December2020performance report supports scheduled2017–19publication but does not itself supply every historical
exception/time. Additional sources and exact as-of schedules remain required. No revised storage number is used as a
pre-release forecast; historical storage observations and release dates are different inputs.

## Full-source acquisition outcome

The earlier paper lead is *The Natural Gas Announcement Day Puzzle*,SSRN3575861, not one of the user's earlier
three uploaded papers. Its abstract/executive summary was enough to identify an interesting directional rule,
but is not a complete independently read manuscript. The five paper answers and author-claim boundary remain in
`agents/codex/results/targeted_diversification_20261030.md`.

This intake pursued a new author-thesis route:
`https://centaur.reading.ac.uk/105084/17/24895312_Robert%20Wichmann_Thesis_Redacted.pdf` returned an explicit
Anubis access denial. No bypass was attempted. Hannover andICMAauthor listings point to the original DOI or
Reading record, rather than a newly acquired public manuscript. GitHub exact-title/filename searches found
citations and third-party summaries, not an authenticated full source. We did not execute third-party research
code, treat those summaries as primary findings, buy access or retry the known Liverpool embargo.

The SAGE listing remains restricted; the original Reading manuscript was denied in the earlier intake.
The thesis is a different source attempt, not a claim that the original document's access changed.
The report/source record still correctly says`full_text_read:false`.

## Exact continuation

No further price-formatting request is justified. Need the primary full paper, configured exchange timezone,
symbol/feed/continuous-roll conventions, and a historically justified release calendar/cost protocol. NativeNG
commissions are not supplied; the user's measuredMNQfee does not establishNGfees. Any fee assumptions must be
preregistered and stressed rather than represented as measured.

After those inputs: evidence/power feasibility, a bounded exact-code preregistration with the existing scout lease
and admission checks,2018–22cheap design, then only earned2023+historical validation and integer-size account
BASE/ADD/REPLACE/EMPTYcomparisons. No trade returns, optimization, statistical promotion, account allocation,
PowerLanguagestrategy, broker/VPSor schedule change was performed. Budgets remain4/10hypotheses and10/30definitions.

Tell Claude: review `agents/codex/results/ng_corrected_intake_20261031.md`.
