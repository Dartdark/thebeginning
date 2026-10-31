# Acquired SSRN research inputs —2026-10-29

These are retained data files, source facts and reproducible builders. They are not a complete source-equivalent
trading dataset. Read each file's provenance, timing and missingness flags before using it.

| Package | Main files | What is retained |
|---|---|---|
| Official macro calendars | [Primary CSV](fx_calendar/primary_release_calendar_2018_2022.csv), [report](../../results/scout_fx_calendar_acquisition_20261029.md) | 943 dated/time facts for2018–22 from BLS/BEA/Fed; original availability/receipt remains unknown. |
| Secondary calendar inventory | [CSV](fx_calendar/secondary_calendar_inventory_2018_2022.csv) | Separate591-row date inventory, with publisher exclusions and provenance; not pooled into primary evidence. |
| Weekly claims | [Calendar](claims_calendar/claims_calendar_2018_2022.csv), [header facts](claims_calendar/primary_embargo_headers.csv), [README](claims_calendar/README.md) | 261 officially corroborated dates;249 printed embargo clocks corroborated and12 blank. Advance knowledge/receipt remains unknown. |
| Bond forecasts | [Provider CSV](duration/provider_forecasts.csv), [institutional CSV](duration/institutional_quotes.csv), [coverage](duration/coverage_2018_2022.csv) | 4 original-table rows,3 separate quotes/references; only3/60 design months have provider tables and no original available-at is verified. |
| Signed SPX dealer book | [Access facts](spx_positions/vendor_access.json), [unsent intake](spx_positions/REQUEST_SPEC.md) | 0 raw position/book rows. One rounded retrospective public example is kept separately; it is not an input panel. |
| Manuscript access | [Receipt](manuscripts/source_access.json) | First two full papers still unacquired; the already-readable third PDF has no local byte hash. |

The primary macro CSV preserves scheduled-as-displayed, actual published-statement and secondary-date evidence as
different kinds. A release document's embargo/header is not proof of first calendar announcement or feed receipt.
The2019 BEA shutdown changed dates/estimate labels; canceled original plans and later revised schedules are retained
separately. Fed statement documents include unscheduled actions, not only scheduled rate meetings.

All builders are offline reproductions from retained facts; they do not silently fetch new data or compute returns:

    /workspace/venvs/thebeginning/bin/python analysis/codex_acquire_fx_calendar_20261029.py
    /workspace/venvs/thebeginning/bin/python analysis/codex_acquire_claims_calendar_20261029.py
    /workspace/venvs/thebeginning/bin/python analysis/codex_acquire_duration_free_data.py
    /workspace/venvs/thebeginning/bin/python analysis/codex_acquire_spx_positions_20261029.py --output analysis/outputs/codex_spx_positions_acquisition_20261029.json

The bundle inventory is listed in the final acquisition report/manifest. Do not fill missing
forecasts, unknown clocks, missing beginning inventory or unobserved returns. Hashes identify these retained facts,
not unread/undownloaded PDF bytes or independent economic verification. All three paper records remain NEEDS DATA.

Remaining public byte-download restrictions and exact normal-read resources are documented in
[NETWORK_PUBLIC_DOWNLOADS.md](NETWORK_PUBLIC_DOWNLOADS.md). This is an unapplied capability request; no environment
policy, account, licence, vendor request or payment was changed. Broader SPX history requires separately confirmed
vendor entitlement. Proprietary raw files must not be committed merely because this repository is private.
