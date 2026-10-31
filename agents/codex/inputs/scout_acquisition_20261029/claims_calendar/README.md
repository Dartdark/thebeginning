# Weekly initial-claims release calendar: sourced dates, partial verified clocks

Acquired2026-10-29 for SSRN5207418 research. This packet defines no trading rule and computes no returns.

- `claims_calendar_2018_2022.csv`:261 distinct sourced release dates; each has an official date corroboration.
- `primary_embargo_headers.csv`:249 individually corroborated08:30 Eastern embargo-header facts:223 direct PDF parses,
  26 indexed official headers. Twelve2018 dates have official date-only evidence and retain blank time/UTC fields.
- `coverage_2018_2022.csv`:52/52/53/52/52 sourced dates by year and the verified/unknown clock counts.
- `secondary_dates.json`:259 date facts from a pinned public research calendar. Two wrongly omitted2019 dates were
  restored using actual primary evidence: January3 and October17. No weekday-date rule generated any row.
- `primary_*.json`: per-source facts, exact URLs, reader references, failures and indexed-versus-PDF methods.
- `manifest.json`: source/output hashes, counts, unknown knowledge clocks and explicit evidence limits.

Rebuild from the repository:

    /workspace/venvs/thebeginning/bin/python analysis/codex_acquire_claims_calendar_20261029.py

The source-date universe begins with the public Midas calendar at commit
`f9e756cbbca3a0576178412a48e1e374c9c76cfe`, then separately corroborates official dates/headers and repairs omissions.
This is not proof that an official complete archive export was acquired or that no unlisted publication exists.

Printed embargo times are distinct from original advance schedule publication and actual transmission/receipt.
Those latter clocks remain unknown for every row. No general Thursday or08:30 rule fills missing facts.
All `return_eligible` flags remain false; the paper's exact universe/window and pre-entry availability remain unverified.
No unemployment level, surprise, return, position size, account P&L or hypothesis variant was computed.

Only source calendar/header facts are retained. No local PDF bytes or PDF hashes are claimed. An indexed header
is labeled as such, including when the current direct source URL is unavailable. Public federal facts and minimal
factual extraction are retained, rather than copying third-party code or full narrative documents.
