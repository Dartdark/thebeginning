# Relative-equity input intake: source PASS, no strategy permission

Independent source/synthetic review on2026-10-26. This reviews only the bounded non-return input-quality
intake. H01/H02 stay closed; no H03/economic hypothesis is registered. No new equity JSON, native price data,
financial ledger or prior economic output was opened, fetched or inspected. The reviewer writes only this file.

Read AGENTS/BUILDER_BRIEF/RESEARCH_CONTROLS, the NEEDS DATA mechanism sheet, bounded intake plan, public source
README as untrusted reference content, and intake manifest. Plan/evidence/manifest are preregistered at
`b9ae149df2b1bdbfdec5db9f10b01d81b1ed4820` before acquisition. The public README's example code was not run.

Reviewed implementation: `analysis/codex_hunt_v2_prefix_equity_intake.py`.
SHA-256: `c104d9c51b7aac190133c5506ffcdaef824a39eb475e2a4eea4c619cef3fbbdd`.
Root must commit this exact implementation and the pre-acquisition format clarification before acquiring/
auditing the two files. Because the plan was clarified after initial b9ae149, pass the new effective pre-data
freeze commit as the mechanism/intake preregistration parameter. A changed implementation needs review
reconciliation first.

## Findings resolved before data

Initial draft used a different manifest-key/provenance interface and omitted the required240-UNIQUE-date
coverage gate and ordering report. Those issues were reported to root/maker and corrected before acquisition.
The final source uses the committed `inputs`/`path`/`source_repository`/`source_ref`/`source_path` fields,
the same five provenance fields, exact source byte count plus Git blob verification, >=240 unique design
dates in EACH2018–22 year, and a full valid-date source-ordering classification. No data/outcome motivated
these corrections and no gate was relaxed. Root also identified the README's advertised English-thousands
format before data acquisition. The final code/plan freeze strict design-only comma-group normalization:
2,695.81 is accepted;12,34 and1,00,000 are rejected. Plain numerical/date grammar uses ASCII characters;
there is no blind comma deletion, whitespace cleanup, Unicode digit guess or change-field conversion.

## Verified scope and controls

- Exactly two source entries are required from a byte-identical committed manifest; input paths must be
  owned JSON files inside the fixed intake directory and distinct from manifest/each other. The source
  Git reference/path/blob and expected byte count are retained. A byte-count or Git-blob mismatch prevents
  even the date/OHLC audit of that file. File SHA256 and Git blob SHA1 are separately calculated.
- JSON is decoded with numeric tokens retained as strings, duplicate object keys rejected, and no remote
  source code execution. Object `data` must be an array of rows with exactly8fields. Wrapper metadata values
  are not logged or used as provenance. Every row's Gregorian date must be a real, unambiguous exact
  YYYY-MM-DD or YYYY/MM/DD; malformed schema/date rows remain recorded and fail numerical quality.
- Full-file inspection is Gregorian-date/row metadata only. ONLY rows with admitted2018–22 dates pass their
  first four OHLC fields to strict ASCII/English-group parsing and Decimal conversion. Abs_Change, Pct_Change and Jalali fields are not numerically
  parsed or used. Pre2018 and2023+ OHLC is never numerically converted, compared, deduplicated by price or
  used for any return. Poisonous non-design price tokens are deliberately tolerated by the synthetic test.
- Design OHLC must be finite/positive and satisfy high/low/open/close relationships. Design duplicate OHLC
  conflicts fail; all source rows/date duplicates are counted and retained, with no transformed deduplication,
  interpolation, resampling or backfill. Coverage is >=240 UNIQUE dates for each of five design years,
  explicitly a coarse condition rather than a trading-calendar claim. Ordering/range/year counts are metadata.
- No arithmetic derives returns, changes, MTD signs, signals, correlations, t-statistics, trades, gross
  screens, placebos or book/account performance. Code imports standard library only and opens no existing
  owned financial series. Outputs contain integrity/coverage counts and dates, not converted OHLC values.
- Vendor, index identity, close clock/timezone, adjustment/revision, and historical available-at/receipt
  provenance are independent Boolean/evidence gates. ALL remain false in the frozen manifest. Numerical
  quality cannot set any true. Therefore the registered intake MUST end NEEDS_DATA even if both numerical
  checks pass; a parse does not authorize an economic preregistration or design test.
- Before inputs are read, the runner checks codex/work, committed HEAD implementation, and committed exact
  manifest/evidence/plan. After audit it rehashes those bindings plus both inputs. A hypothesis-local
  nonblocking lock, fixed output root, global completed-marker search, write-once artifacts, and final
  artifact-hashed marker preserve completed rejected or successful audits and refuse alternate-directory
  reruns. All writes/cache/attempt logs stay under the allowed Codex intake output prefix.

Synthetic verification used the requested Python with`-B` and called ONLY `synthetic_checks()` in memory,
without acquiring/opening real JSON or writing an output artifact. All12 grouped checks passed on the hash
above, including poisoned pre/post-design values, strict dates/schema,240-unique-date years, conflicting
duplicates, unknown provenance, strict advertised comma grouping, independent Git-blob hashing and owned-path
escape rejection.

## Decision

**SOURCE PASS for this committed, bounded, NON-RETURN intake only.** No fatal source mismatch remains in that
scope. Intake adds zero economic evaluations, zero hypotheses and zero gross screens. The two immutable
files may be acquired only within the parent-authorized intake after implementation commit. Actual byte,
schema and coverage outcomes remain unobserved by this reviewer. Source provenance, fixing service/calendar,
native M6E costs/availability, power and the economic model remain separate NEEDS DATA gates. No strategy,
historical validation, book-improvement candidate, promotion or deployment is attested or authorized here.
