# SSRN inputs acquired: PARTIAL; signed SPX book and source-clock gates remain open

Summary: Saved943 primary macro-calendar records and261 officially corroborated weekly-claims dates, with249 printed clocks and12 unknown.
Saved4 provider forecast rows and3 separate institutional references; original provider coverage is3/60 design months.
No signed SPX book was acquired; a fixed2022H2 Cboe sample route is documented but unactivated and eligibility unconfirmed.
Input builders/hashes validate. No return test, trial reservation or account run occurred; budget remains0/10 hypotheses and0/30 economic definitions.

Date:2026-10-29. Work branch:codex/work. Checked parent:1c3aaa51ba7c1663c59570d37220c3a9193374ef.
The user's request was to obtain the inputs for the three existing leads. We collected actual public data rather
than changing the trading rules to match missing data. The full first two manuscripts remain unacquired.

## Delivered files and remaining gaps

| Input | Actual retained data | Important remaining limit |
|---|---|---|
| [Primary macro calendar](../inputs/scout_acquisition_20261029/fx_calendar/primary_release_calendar_2018_2022.csv) |9432018–22 records:783BLS,118BEA,42Fed statement documents | Archive schedule copies and actual statement headers are different kinds. Original advance knowledge and actual feed receipt are not established. |
| [Weekly claims calendar](../inputs/scout_acquisition_20261029/claims_calendar/claims_calendar_2018_2022.csv) |261 official-date-corroborated records;249 verified printed08:30ET headers,12 date-only with blank clocks | Printed embargo is not measured receipt or first schedule announcement. Remaining12 clocks stay unknown. |
| [Provider duration forecasts](../inputs/scout_acquisition_20261029/duration/provider_forecasts.csv) |4 numerical table rows:May2019,August2019,March2020,April2023 | Only3/60 original-table design months;April2023 is outside2018–22. Original availability unknown. |
| [Institutional duration references](../inputs/scout_acquisition_20261029/duration/institutional_quotes.csv) |3 separately labeled official IMF quotations/references | Post-event April/August2020 references are not pre-entry forecasts; do not backdate them. |
| [SPX intake packet](../inputs/scout_acquisition_20261029/spx_positions/REQUEST_SPEC.md) |1 rounded retrospective public example, required fields, versioned vendor terms and unsent request specification |0 raw capacity records,0 reconstructed inventory rows,0 return-eligible rows. The example is not a dealer-position panel. |

[Bundle index](../inputs/scout_acquisition_20261029/README.md) ·
[File/hash inventory](../../../analysis/outputs/codex_scout_acquisition_package_20261029.json).
The separate591-row secondary macro inventory retains its provenance and exclusions. It is not pooled into the
primary counts or used to define the paper's trading universe. Weekly claims independently restored two2019 releases
that the secondary calendar had omitted after old URLs failed.

## Source and clock checks that matter

The macro calendar includes complete60-row CPI, Employment Situation and PPI date sets. The2019 BEA shutdown
canceled original plans and changed estimate labels; the packet retains the dated original/revised evidence without
inventing missing60th GDP/PCE releases. Five PCE10:00ET exceptions remain explicit. The42Fed documents include
unscheduled policy statements; they are not42scheduled meetings. Historical daylight-saving conversion uses named zones.

For duration, source tables include the negativeMarch2020 Treasury extension, rather than assuming every month
requires purchases. Source issue/as-of dates and a mirror filename do not establish original publication/receipt.
All57 missing design-month provider forecasts remain missing; no forecast or market return is imputed.

Cboe's current published terms offer eligible first-time users a **fixedJuly1–December31 2022** Open-Close sample,
not an arbitrary selectable six months. Entitlement/licensing and delivery have not been confirmed; enrollment was
not started. Prior inventory from series inception, full sessions/corrections, option Greeks and receipt clocks are
still necessary. One-minute data have a2–5minute interval-end delay, and the product was introduced in2025 despite
historical backfills. A2022 trade timestamp is not proof of contemporaneous public availability.

Current published standard one-minute rates are12,000USD/month live,4,000USD/recent historical month and
2,500USD/month for five-or-more-year history. These are source categories, not a binding quote, total price or
authorization to buy. No account, trial, vendor/author message, order, subscription, key or payment was initiated.

## Reproduction and review

Configured Python `/workspace/venvs/thebeginning/bin/python` ran all four data builders/audits successfully:

    python analysis/codex_acquire_fx_calendar_20261029.py
    python analysis/codex_acquire_claims_calendar_20261029.py
    python analysis/codex_acquire_duration_free_data.py
    python analysis/codex_acquire_spx_positions_20261029.py --output analysis/outputs/codex_spx_positions_acquisition_20261029.json
    python analysis/codex_scout_acquisition_inventory_20261029.py --output analysis/outputs/codex_scout_acquisition_package_20261029.json

These reproduce retained facts/CSVs and validate dates, identifiers, declared unknowns, arithmetic, coverage and
hashes. They do not fetch fresh vintages or compute financial returns. Direct PDF parsing, indexed official headers,
secondary facts and provider/institutional references remain labeled separately. Whole copyrighted PDFs and licensed
raw market files were not redistributed. Hashes identify retained local facts, not unavailable original PDF bytes.

Detailed source evidence and the four paper questions are retained in the component reports:
[macro](scout_fx_calendar_acquisition_20261029.md), [claims](scout_claims_calendar_acquisition_20261029.md),
[duration](scout_duration_acquisition_20261029.md), [SPX](scout_spx_positions_acquisition_20261029.md).
Their author return claims are not independently verified by collecting these inputs. No evidence sheet reached TEST.

## What still needs access

The first two papers' full source rules and matching complete/as-of inputs remain prerequisites. The exact remaining
SPX acquisition request is prepared and unsent. The existing user contract explicitly prohibits new accounts,
subscriptions, purchases and external messages; this task did not waive those restrictions or confirm existing access.

The execution environment also blocks ordinary public byte downloads from the data hosts. The connected reader
provided the retained facts but cannot deliver ZIP bytes; the manuscript fetch remains unavailable. The exact public
read destinations/resources are in [NETWORK_PUBLIC_DOWNLOADS.md](../inputs/scout_acquisition_20261029/NETWORK_PUBLIC_DOWNLOADS.md).
No environment-configuration write tool is available in this chat; no policy/proxy/route was modified or bypassed.
Allowlisting would permit ordinary requests, not guarantee remote access or grant vendor entitlements.

All three records remain NEEDS DATA. Data acquisition spent no hypothesis/definition budget, held no return-work
lease and did not resume paused programs. Earlier trial history, negative results, live strategies, allocations,
trading plans, VPS, broker settings and keys remain preserved.

For Claude: `agents/codex/results/scout_data_acquisition_20261029.md` and the linked data/manifest files.
