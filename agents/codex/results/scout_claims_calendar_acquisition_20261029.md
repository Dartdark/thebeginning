# Initial-claims calendar acquired:261 dates,249 corroborated embargo clocks; NEEDS DATA

Summary: Acquired261 sourced weekly-claims release dates for2018–22, with official date corroboration for each.
Verified249 actual08:30Eastern header facts:223 through the PDF reader and26 through indexed official headers;12 times remain unknown.
Restored the two2019 releases omitted from a public calendar, without generating Thursdays or treating observation weeks as release dates.
Original advance-schedule availability and actual receipt remain unknown; no return test or TEST admission occurred.

Date:2026-10-29. Target: Krohn/Vala SSRN5207418, *Auctions, Announcements, and Abnormal Returns*.
[Paper/source testability](scout_5207418_testability_20261029.md) remains NEEDS DATA: full source specification has not been recovered.

## Acquired data

[Calendar CSV](../inputs/scout_acquisition_20261029/claims_calendar/claims_calendar_2018_2022.csv) ·
[Primary embargo facts](../inputs/scout_acquisition_20261029/claims_calendar/primary_embargo_headers.csv) ·
[Coverage](../inputs/scout_acquisition_20261029/claims_calendar/coverage_2018_2022.csv) ·
[Manifest](../inputs/scout_acquisition_20261029/claims_calendar/manifest.json) ·
[Packet README](../inputs/scout_acquisition_20261029/claims_calendar/README.md).

| Year | Sourced and officially corroborated dates | Individually corroborated embargo clocks | Unknown embargo clocks |
|---|---:|---:|---:|
|2018|52|40|12|
|2019|52|52|0|
|2020|53|53|0|
|2021|52|52|0|
|2022|52|52|0|

The date universe comes from a [pinned public calendar](https://github.com/chris-cheshire/project-midas-mk7/blob/f9e756cbbca3a0576178412a48e1e374c9c76cfe/midas/data/calendar/us_claims.txt),
whose source notes identify the official ETA archive and its dated PDF-link convention. The259 active2018–22 date
facts were not generated from a Thursday rule. Each constructed candidate URL was checked before accepting its
actual embargo header. Inaccessible legacy files remained failures; bounded searches found alternate published
official links or indexed primary headers. Direct PDF parsing and indexed primary evidence remain separate.

The public calendar omitted January3 and October17,2019 after old URLs failed. Actual official releases exist:
[January3 PDF](https://www.dol.gov/sites/dolgov/files/OPA/newsreleases/ui-claims/20190008.pdf) and
[October17 official page](https://www.dol.gov/newsroom/releases/eta/eta20191017). The first was read through the PDF
parser; the latter's indexed primary header was read after direct403 and is explicitly labeled indexed evidence.
Both print08:30Eastern. The current access failure does not mean no economic release occurred.

Holiday exceptions are preserved from actual source facts. For example, the official
[November21,2018 PDF](https://www.dol.gov/sites/dolgov/files/OPA/newsreleases/ui-claims/20181882.pdf),
[November27,2019 PDF](https://oui.doleta.gov/press/2019/112719.pdf) and
[November23,2022 PDF](https://oui.doleta.gov/press/2022/112322.pdf) identify Wednesday releases.
The observation's reference-week-ending date is a separate field. It was not used as a surrogate release date.

Twelve2018 source listings establish the date/reference week but not the embargo time. They retain blank clock/UTC
fields rather than inheriting the current general08:30 policy. The ledger gives261 corroborated dates in the sourced
universe, not independent proof that an exhaustive official archive export was obtained.

## Timing and source limits

The printed embargo-lift timestamp is not a measured actual publication, receipt or original advance calendar announcement.
All `original_schedule_available_at` and `actual_publication_or_receipt_at` values remain blank; `return_eligible` is false.
UTC conversion uses `America/New_York` and historical daylight-saving rules only where the printed clock is verified.
No fixed EST offset, first-Thursday rule or retrospective price spike labels a trade.

An Apache2 public ZipLime dataset was discovered as another possible route, but its actual files were not obtained:
the normal network-enabled proxy returned403, and the connected row API/viewer request was inaccessible. Its advertised
claims coverage was not copied or treated as acquired. No accounts, keys, paid data, contacts or access-control bypass occurred.
The official archive's form/year export was also not obtained through the reader. Exact source attempts and recovery
methods are retained in the packet's `primary_*.json` facts.

## Four paper questions and next gate

1. **About:** the paper links Treasury auctions and following-day macro-announcement FX returns.
2. **Finds:** its abstract claims roughly8bp foreign-currency appreciation; these calendar files do not reproduce that return.
3. **Why could it pay:** dealer-capacity/safe-asset-demand spillovers are the authors' proposed channel, not a verified net edge here.
4. **Build on it:** this acquisition supplies substantially more actual event evidence. Full source rules, remaining clocks,
   original schedule knowledge, exact event universe, native contract/roll/cost checks and independent gates remain missing.

Do not inherit the public calendar's exclusions, select only convenient release types, or call this an exact paper replication.
This packet advances data intake but creates no financial hypothesis, definition, reservation or return-admission PASS.

## Reproduction

[Script](../../../analysis/codex_acquire_claims_calendar_20261029.py) ·
[Actual validation/output](../../../analysis/outputs/codex_claims_calendar_acquisition_20261029.json).

    /workspace/venvs/thebeginning/bin/python analysis/codex_acquire_claims_calendar_20261029.py

The configured Python ran successfully. It validates source-date identity, unique dates, reference-week precedence,
official source paths, timezone conversion, explicit unknown availability and output/source hashes. No market prices,
returns, gross screens, account simulation, live strategy, allocation, VPS, broker setting or API key were touched.

For Claude: `agents/codex/results/scout_claims_calendar_acquisition_20261029.md`.
