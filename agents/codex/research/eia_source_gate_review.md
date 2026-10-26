# EIA inventory composition: source feasibility review

This is a source/data gate, not a strategy preregistration or performance result. No strategy returns, CL
price response, sign-agreement counts, candidate selection, account tests or forward execution were run.
Five sampled archived issues establish a concrete free source route, not complete 2018–22 coverage.

This note records the initial five-sample review. Later acquisition, offline repairs and the separately
reported access blocker are documented in agents/codex/results/eia_inventory_input_gate.md and
agents/codex/research/eia_offline_recovery_review.md; the initial conclusion below is historical.

## Files and provenance

Actual returned web-tool responses are preserved in
analysis/outputs/codex_eia_inventory_input_gate/samples/five_highlights_web_response.json and
source_proofs_web_response.json. Five edition-specific records and manifest.json hold parsed facts,
canonical URLs, week-ending dates and limitations. Hashes identify UTF-8 serialized converted web responses;
they are NOT raw PDF checksums. No original PDF byte stream was downloaded or reconstructed.

| Release date | Data week ending | Commercial crude excluding SPR change | Total gasoline change | Distillate change |
|---|---|---:|---:|---:|
| 2018-01-04 | 2017-12-29 | -7.4 | +4.8 | +8.9 |
| 2019-01-09 | 2019-01-04 | -1.7 | +8.1 | +10.6 |
| 2020-07-08 | 2020-07-03 | +5.7 | -4.8 | +3.1 |
| 2021-04-07 | 2021-04-02 | -3.5 | +4.0 | +1.5 |
| 2022-12-29 | 2022-12-23 | +0.7 | -3.1 | +0.3 |

Units are million barrels; positive means build and negative means draw. Values come from the archived
Highlights prose. Do not subtract rounded stock levels: 2022-12-29 shows 419.0 minus 418.2, but its published
crude change is +0.7 because changes use unrounded underlying observations. These are inventory changes,
not consensus surprises. Forecasts, expectations and actual commercial futures hedges are not observed.

## Availability and acquisition route

The [official archive index](https://www.eia.gov/petroleum/supply/weekly/archive/) distinguishes release dates
from data-ending dates. Issue pages link Highlights PDFs, table PDFs and table CSVs. A normal sample is
[2018-01-04](https://www.eia.gov/petroleum/supply/weekly/archive/2018/2018_01_04/wpsr_2018_01_04.php), whose
[Highlights PDF](https://www.eia.gov/petroleum/supply/weekly/archive/2018/2018_01_04/pdf/highlights.pdf)
contains the three published inventory changes in its first inventory paragraph.

The [original 2018 Appendix B](https://www.eia.gov/petroleum/supply/weekly/archive/2018/2018_01_04/pdf/appendixb.pdf),
PDF page5/printed37, explicitly describes Highlights PDF and CSV/XLS tables at 10:30 a.m. Eastern, versus
the full WPSR PDF/HTML at 1 p.m. The original June2022 edition states the same. The regular nominal clock
therefore supports investigating a delayed entry after 09:30 CT on verified regular Wednesday releases.
Individual historical receipt times and holiday/disruption clock exceptions are NOT verified by that policy.
In particular, the two Thursday samples must not simply be assigned the regular Wednesday time.

The [June29,2022 issue](https://www.eia.gov/petroleum/supply/weekly/archive/2022/2022_06_29/wpsr_2022_06_29.php)
explicitly contains delayed June17 data as well as June24 data. A mechanically generated weekly calendar
would misdate the former. Multiple reports on one release date require a frozen rule before return testing.

In the connected web tool, Table1 CSV links returned HTTP400 unsupported application/octet-stream;
this is a rendering limitation, not a403. Some constructed direct opens returned an internal inaccessible
message; normal archive-index to issue-page to actual Highlights-link clicks succeeded. No403 was observed
and no access control was bypassed. Do not use third-party proxy domains or current revised time series.

Link IDs vary: the usual Highlights PDF ID31 becomes ID33 when issue notices add links. Match the line
labelled Weekly Petroleum Status Report Highlights instead of hardcoding31. One sampled issue header
(2019-01-09) omits the day in its week-ending text; the PDF and archive index supply January4. Reconcile
edition, release date and data-ending fields rather than silently trusting a malformed header.

## Revisions, parsing and next gate

Archived files are not established as immutable first-publication vintages. The
[2018-06-27 issue](https://www.eia.gov/petroleum/supply/weekly/archive/2018/2018_06_27/wpsr_2018_06_27.php)
documents a production-statistic correction in its PDF/CSV. That does not establish an inventory correction
on that date, but demonstrates mutable archives. An official
[2026 correction notice](https://www.eia.gov/petroleum/supply/weekly/includes/revision-notice.php) records
an initially wrong distillate-summary direction corrected at12:13ET, while tables were correct. It is source
review evidence only and was not used as a strategy input or return observation. The notice says
“summary text”; it does not specifically identify the Highlights PDF as affected.

Call this input archived-issue changes until field-specific vintage/correction checks justify more. Retain
issue notices and known corrections, distinguish publication policy from actual receipt, and freeze handling
before price returns. A later positive strategy cannot erase these data-review limitations.

Normalize web line prefixes and whitespace, then parse the complete inventory phrases and directions.
Fail closed on unchanged, ambiguous or missing numeric statements. Do not manufacture a value from rounded
levels, a later report, price movement or a consensus expectation. Preserve any skipped records and reasons.

About260 weekly opportunities precede filters. All-three-sign agreement would have about25% incidence under
an independent-sign heuristic, approximately65 tickets before other exclusions. This is an assumption, not a
measured count; it warns against assuming the >=100-trade gate has adequate power. Complete fundamental-only
coverage/feature counts first, then evidence and <=5-model committed preregistration before new returns.

Current decision: acquisition route and five samples verified; full panel, exception clocks, original bytes,
field-specific correction review, and strategy feasibility remain unfinished. This is not a user-action blocker,
a design-pass candidate, a t4/4.5/5/6 milestone, or trading approval. No purchases, accounts, external messages,
commits, pushes, API settings or live configuration changes were performed by this reviewer.
