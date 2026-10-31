# I04 CME collector: one-file timestamp/identity intake, no margin values

Mechanism before data: `agents/codex/evidence/hunt_v2_new_primary_nomination.md` (NEEDS DATA).
Source pins/limitations: `agents/codex/research/hunt_v2_new_primary_nomination.md`.
This is a new non-return input-quality intake, not H05 or a trading TEST. Commit plan/code/review
before acquisition/CSV interpretation. Running3/60economic evaluations,4/10hypotheses,2gross screens;
archived t6=65. I04 adds0to each. H01–H04/I01–I03 remain closed or completed under original definitions.

## Single immutable acquisition and binding

Only source: BrunoProgramming/cme_margin commit
`93cc090bd7f680292436012b13c4e6fb44fc411f`, `data/cme_margin.csv`, exactly26,989,907bytes,
Git blob `21c9202c0918bd2ea017fa80baeb1e467e10241c`.
URL: `https://raw.githubusercontent.com/BrunoProgramming/cme_margin/93cc090bd7f680292436012b13c4e6fb44fc411f/data/cme_margin.csv`.
No second CSV, origin/fork concatenation, current endpoint or replacement source after inspection.
The modern dashboard metadata check found no historical CSV and is not an acquisition candidate.

The GitHub app identified this oversized UTF-8 archive; its pinned raw file may be downloaded once
through the permitted GitHub host into the isolated ignored Codex output cache. Bind size, Git-blob
SHA1 and newly computed SHA256 before CSV interpretation; never execute remote code. A403, access
error, wrong object or partial attempt is retained and stops this intake without retry/bypass.
Do not contact CME, buy data, create accounts or change network policy. Keep raw CSV local/ignored:
the collector's MIT software license does not establish CME-data redistribution rights. Save source
identifiers/hash/header and factual metadata ledgers, not the raw full margin-value table in Git.

## Schema and strictly permitted fields

Code-derived required-column subset, not yet a verified header/order:
`Time,Exchange,Asset Class,Product Name,Product Code,Start Period,End Period,Maintenance,Currency,Maint. Vol. Scan`.
Require exact names and unambiguous header; extra index columns may remain uninterpreted. Save full
header and its raw-line SHA before records. Do not guess renamed columns or infer header from values.

Interpret only Time,Exchange,Asset Class,Product Name,Product Code,Start Period,End Period,Currency
and original CSV record ID. Maintenance/Maint. Vol. Scan and every other numeric field remain opaque
and unconverted. No maintenance levels, changes, averages, thresholds, first-increase events, prices,
signals, returns, t/DSR, correlations, placebos or account outcome. Period labels remain exact strings;
they are contract buckets, never effective dates. No new numeric stage is authorized here.

Time is the collector's poll timestamp, not announcement/effective/receipt time. Require a real ISO
calendar timestamp with explicit UTC offset(Z or+00:00); accept space or T separator and0–9fractional
second digits without rewriting the raw value. Retain raw timestamp/precision and normalized UTC
date; no naive-timezone assumption, epoch guess, repair or forward-fill. Invalid/ambiguous metadata
stays unresolved with source IDs. All file dates may be inventoried as metadata, including outside
2018–26; no financial field at those dates may be inspected or converted.

## Fixed inventory and target scope

Inventory ALL product-code/name/exchange/asset-class/currency identity combinations and poll-time
coverage, with row counts and first/last valid timestamp/by-UTC-year. This is an identity/coverage
inventory, not product admission. Preserve leading zeros/case/raw strings; surrounding ASCII whitespace
may be stripped for separate normalized labels while retaining originals. No product numeric conversion.

Before data, target labels are exactly NQ,MNQ,ES,MES. For each report exact observed raw identity pairs,
source-row counts, unique UTC poll timestamps/dates and per-year coverage. If these labels are absent,
report absent; do not pick a different code/name after values. Even an apparent product-name match
needs original CME mapping before trading. Save all target metadata rows and duplicate metadata-key
IDs (Time+exchange+asset+code+periods+currency). Without inspecting Maintenance, duplicates cannot be
called equivalent/conflicting margin values. Retain original sequence and flag nonmonotone times.

The collector saves selected changes rather than every unchanged poll. A missing target row/day
does not prove no change, no requirement or uninterrupted availability. Do not count observations as
genuine increases, infer event independence, generate a usable daily margin state or silently fill
missing2018–19/2021–26. The six-hour workflow is intended cadence, not an authenticated run log.

## Result, run identity and retention

Output only `analysis/outputs/codex_hunt_v2_cme_margin_metadata/`; proposed script
`analysis/codex_hunt_v2_cme_margin_metadata.py`. Runtime cache/partial download/locks stay there.
Require codex/work, committed exact code/plan/evidence/source/dependencies, exclusive run lock,
write-once attempt/artifacts, fixed directory and complete/partial attempt guard. No unchanged retry
or alternate output directory. Bind download/code/input/artifact hashes and versions; recheck after
interpretation. Retain exceptions with actual stage and no economic claim. Large ledgers can be
deterministic gzip with all records/IDs retained; no sampling based on favorable coverage.

Synthetic checks must cover schema ambiguity, ISO/UTC/precision and invalid/naive timestamps,
leading-zero product identities, absent targets, duplicate metadata IDs/nonmonotone sequence and
poisoned Maintenance/numeric cells proving they are never accessed/converted. Import/fixtures must
not fetch/open actual source. No price/grid/strategy/account engine or remote scraper may be imported.

Completion remains DIAGNOSTIC_ONLY_NEEDS_PRIMARY_CLOCK_AND_HISTORY, regardless of apparent coverage.
Report actual covered dates/products, missing required periods, unresolved metadata, poll semantics,
licensing/provenance limits and unchanged budgets. If invalid schema/hash/download stops first,
retain the specific failure instead. Neither a2020commit nor current collector Time authenticates
historical exchange announcements or collateral deadlines. A later source-complete TEST and separate
<=5configuration economic preregistration would still be required for H05. No old-source repair,
trading/PowerLanguage, book change, external message, watcher change or program pause follows.
