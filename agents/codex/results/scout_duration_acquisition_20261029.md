# Treasury duration inputs acquired: PARTIAL / NEEDS DATA

Summary: Saved actual sourced CSV data:4 provider-table observations and3 separately labeled IMF quotations/references.
Only3 of60 design months have an original provider forecast;57 remain missing, and no original available-at clock is verified.
The April2023 provider row is outside2018–22; retrospective April/August2020 quotes are not pre-entry forecasts.
This is usable acquisition evidence and a partial data seed, not a full historical panel or TEST eligibility. New return tests:0.

Date:2026-10-29. Source family: SSRN7601879, *Buying Duration*. The paper itself remains metadata/abstract-only.
Existing [paper/testability review](scout_7601879_testability_20261029.md) and [evidence](../evidence/scout_buying_duration_20261029.md) remain in force.

## Actual files acquired

[Provider forecasts](../inputs/scout_acquisition_20261029/duration/provider_forecasts.csv) ·
[IMF quotes/references](../inputs/scout_acquisition_20261029/duration/institutional_quotes.csv) ·
[60-month coverage ledger](../inputs/scout_acquisition_20261029/duration/coverage_2018_2022.csv) ·
[Canonical observations](../inputs/scout_acquisition_20261029/duration/observations.json) ·
[Manifest](../inputs/scout_acquisition_20261029/duration/manifest.json) ·
[Access/query receipts](../inputs/scout_acquisition_20261029/duration/search_receipts.json).

Numerical facts were read from accessible public PDFs and transcribed with their units/source/page. This is actual
saved structured data rather than a list of links. Whole copyrighted PDFs are not redistributed, no local PDF-byte
hash is claimed, and the validator does not certify original publication/receipt timing.

| Reference month | Change, years | Source type | Document/as-of information | Timing boundary |
|---|---:|---|---|---|
| May2019 | +0.11 | Provider table on public mirror | Index duration as ofMay23; effectiveJune1 | Original publication/receipt unknown |
| August2019 | +0.12 | Provider table on public mirror | As ofAugust19; effectiveSeptember1 | Original publication/receipt unknown |
| March2020 | −0.03 | Provider table on public mirror | As ofMarch27; effectiveApril1 | Negative shortening retained; filename is not a publication clock |
| April2023 | +0.07 | Provider-hosted table | Cover/header datedApril25, as ofApril20; effectiveMay1 | Outside design window; original publication/receipt time unknown |
| April2020 | +0.13 | IMF quoting Bloomberg Barclays | IMF issueMay1, printedp2 | Post-event; cannot be used as an April pre-entry forecast |
| August2020 | +0.16 | IMF retrospective reference | November30 issue says November estimate matches August result | Known only from later source; never backdate to August |
| November2020 | +0.16 | IMF current estimate quoting Bloomberg Barclays | IssueNovember30, printedp2 | Time/zone of original publication/receipt unverified |

Provider sources: [May2019](https://archr.com/wp-content/uploads/2019/05/BBG-BARX-Summary-of-May-Index-Duration-Changes-and-Projected-Duartion-changes-for-June-1st-2019.pdf),
[August2019](https://archr.com/wp-content/uploads/2019/08/BBG-BARX-MONTH-END-SEP-1.pdf),
[March2020](https://archr.com/wp-content/uploads/2020/03/2020-03-30-Summary_Mar_Index_Duration_Changes_and_.pdf),
[April2023](https://assets.bwbx.io/documents/users/iqjWHBFdfxIU/rKfPhv4XjmPg/v0).
Institutional sources: [IMF May1,2020](https://www.imfconnect.org/content/dam/imf/News%20and%20Generic%20Content/GMM/archive/GMM,%20May%201,%202020.pdf),
[IMF November30,2020](https://www.imfconnect.org/content/dam/imf/News%20and%20Generic%20Content/GMM/archive/GMM%20Nov%2030,%202020.pdf).

## Four paper questions and interpretation

1. **About:** month-end benchmark-duration demand in government-bond futures.
2. **Finds:** the paper abstract claims1.19bp versus0.07bp otherwise; those remain authors' unverified return claims.
   The newly retained provider data are duration changes, not returns or a reproduction of that result.
3. **Why could it pay:** benchmark deadlines can concentrate adjustment demand, but these files establish no net edge,
   participant order quantity, source trading window or usable pre-entry information clock.
4. **Build on it:** yes as a partial source-data seed. Original-table coverage is3/60 design months; institutional quotes
   give numerical context for3 other design months but do not close the57-month provider-forecast gap. All available-at
   fields remain unknown; no later issue/reference is relabeled contemporaneous. Full source, historical vintages,
   official event/calendar and contract/cost checks remain necessary before TEST or a preregistration.

The new acquisition routes are a publicly hosted2023 provider report and the official IMF Global Markets Monitor
archive. Neither supplies a complete2018–22 pre-entry panel in the bounded search. Queries for2018/2021/2022,
public provider archives and machine-readable exports yielded no further original provider rows. Public Archr API,
robots and sitemap reads were inaccessible through the connector; access controls were not bypassed. A2024 indexed
quote with unnamed provider was excluded rather than silently pooled into this source series.

## Reproduction and validation

[Script](../../../analysis/codex_acquire_duration_free_data.py) ·
[Output](../../../analysis/outputs/codex_duration_acquisition_20261029.json).

    /workspace/venvs/thebeginning/bin/python analysis/codex_acquire_duration_free_data.py

The configured Python ran successfully. Checks cover ID uniqueness, date/unit sanity, the rounded current/new
duration bridge for original tables, explicit unknown availability clocks, source-type separation and hashes.
The60-month coverage ledger retains missing rows. It does not fill forecasts, rebalance dates, returns or receipt times.
No source-based economic rule, threshold or test was selected. The existing failed ZN family remains preserved.

No subscriptions, purchases, new accounts/keys, credential inspection, author contact, live/VPS/broker change or
return/account simulation occurred. A licensed existing historical index export would still require version/as-of
and original-availability audits; this report does not assert that the user owns such access.

For Claude: `agents/codex/results/scout_duration_acquisition_20261029.md`.
