# CL Legacy net-short state support: bounded non-return intake

Mechanism BEFORE position rows: `agents/codex/evidence/hunt_v2_owned_flow_nomination.md` (NEEDS DATA).
Source note: `agents/codex/research/hunt_v2_owned_flow_nomination.md`.
This plan is a cheap NEW state-frequency intake, not an economic preregistration or TEST override.
It does not register H04. Root must COMMIT this plan and the auditor BEFORE opening position rows.

## Question, fixed predicate and stop

The possible later filter would remove an existing CL Sunday up-gap SHORT only if the last genuinely
published Legacy noncommercial CL cohort is net short. Covering pressure is a hypothesis; actual Sunday
inventory/stops/margins are unobserved. The existing CL base, gap, exit, stop, size and availability are
not changed by this intake. No return test or trading protocol is authorized now.

FIRST ask the cheaper necessary question: are there at least **20 distinct negative as-of report weeks
in2018–22**, using `Noncommercial Positions-Long (All) - Noncommercial Positions-Short (All) < 0`?
This is a minimum source-support gate, not a fitted trading threshold, power proof, or number of trades.
If fewer than20, close this proposed sign-state filter as NOT_TESTABLE_SUPPORT before any publication
bridge, NQ chart/TFF inspection or price/P&L. No rank/percentile, sign inversion, category switch, altered
threshold or broader year range may rescue it. Retain absence/failures and counts in source history.
If20or more, the result remains NEEDS_PUBLICATION_DATA: neither TEST nor a strategy pass. Actual known
Sunday opportunities, release mapping and power would still require a separate committed later intake.

## Pre-intake inspection actually performed

Source code/docs, annual ZIP directory metadata and the first header line ONLY were inspected.
No report/position rows, raw prices, trade lists or P&L were opened; no strategy code ran.
Every owned2017–22 Legacy ZIP contains one `annual.txt` with the same129-field header. Selected columns:

|Exact header|Zero-based position|
|---|---:|
|Market and Exchange Names|0|
|As of Date in Form YYYY-MM-DD|2|
|CFTC Contract Market Code|3|
|Open Interest (All)|7|
|Noncommercial Positions-Long (All)|8|
|Noncommercial Positions-Short (All)|9|

Exact header-line SHA256 for all six files:
`e4605b0ce9a5dbe7e13b592cc07e53e83df25193a074256e9ac4c1e79d59e6ba`.

Pre-row codec clarification: this digest binds the raw first-line bytes, including the existing line
ending. Decode CSV text with Latin-1 to preserve source bytes; selected dates, codes and counts must
still meet their strict ASCII grammars. Contract codes may strip surrounding ASCII whitespace, then
must contain exactly six ASCII digits, with leading zeros retained. Counts may strip surrounding ASCII whitespace, then must be
ASCII digits only: no thousands-separator removal, decimal conversion or rounding. Any unexpected
representation stops as unresolved. Bind the six constants below directly in the committed auditor;
no unbound alternative input manifest or output-directory override is permitted. Complete the identity
and date metadata pass for ALL six years before converting ANY target position count.

**Identity caveat before data:** no owned source-code/document definition of067651 was found by the
scoped source search. The header itself cannot confirm a contract-code value. Therefore067651 is the
declared target to VERIFY during this first committed parse, not a previously admitted mapping.
Require exact corresponding market name
`CRUDE OIL, LIGHT SWEET - NEW YORK MERCANTILE EXCHANGE`
after stripping surrounding whitespace; do not accept another code, E-mini, Brent, natural gas or a
substring-only oil match. If absent/mismatched, stop as NOT_TESTABLE_IDENTITY before numeric positions.
Report raw name/code identity metadata; do not silently repair them to the expected pair.

## Immutable source allowlist

Only `data/cot/deacot2017.zip` through `data/cot/deacot2022.zip`, member `annual.txt`, are allowed.
No wildcard may admit2023+ZIPs. All other contracts and fields are outside the input scope.
ZIP bytes were hashed without parsing position rows. Bind these values before parsing:

|Year|ZIP bytes|ZIP SHA256|Member bytes|Member CRC32|
|---|---:|---|---:|---|
|2017|1711091|5e910b93b5af5e1c8f4006eaeee10109754ee5dd2c7f9d04520bd9770c8ece2b|14109048|dd333f32|
|2018|1900546|adaecbfadf54f117308cc8a135cd9ba827deac3eb1489a5febc642c403728527|15365481|00e5b4e8|
|2019|1904592|3f2707b5fcab1491329684c82cc03759ab66899839f533e09ff0a5dcf517b0c5|15419216|57125e9d|
|2020|1838852|8c83c820e5f6fd193a0923aa02cfe520d20dbe74bba571a576c92baf7a186317|15038669|de73f504|
|2021|1882568|423d20412ec3fb629500fcbfbaa7b6973c5868965000d13963e9b63700c90952|15251600|de161a75|
|2022|1983765|206364f467eb0013b0a5f8e9526426cc6fcfc5bad4e4f91b25e00311a0184cfa|16277791|bffae737|

At runtime, before CSV interpretation, compute and retain each uncompressed member SHA256, validate
ZIP CRC/size/header/name against this registration, and bind member bytes to the already pinned ZIP.
This byte hashing is not a position statistic. Do not extract members into shared directories.
Record exact code/plan/evidence/dependency hashes and runtime version before rows, and recheck all bindings
afterwards. Never execute ZIP content or remote code. All outputs/cache stay in allowed Codex paths.

## Strict non-return parser and permitted calculations

Use CSV strings; preserve leading zeros in contract codes. Inspect code/name/as-of metadata first.
Only067651 rows with the exact expected name can advance to numeric selected-field conversion.
Require an unambiguous real `YYYY-MM-DD` as-of date. Dates are AS-OF metadata, never publication dates.
Do not force Tuesdays: holiday or exception dates remain explicit instead of guessed/relabelled.
For2017 record source/calendar metadata only; **do not convert2017 positions**, since the sign-state
support question needs no rank warm-up. Only2018–22 target rows may convert the three count fields.
No pre2017 or2023+position field may be converted. Out-of-file-year dates are retained/flagged, not
silently discarded; any as-of date outside2017–22 blocks source admission.

Counts must be finite, nonnegative integers; OI>0 and long<=OI,short<=OI. No absolute-value correction,
missing-to-zero conversion, rounding or position interpolation. Invalid target fields remain unresolved
and block the support decision. Other-contract numeric fields must never be converted.
Compute only selected net sign/counts and as-of support. No price series is admitted or read.

Key by contract/as-of date. Exact selected-field duplicates may collapse ONCE with original IDs/counts
retained; contradictory selected counts for a key are fatal. Do not select a latest vintage or the row
that yields a desired sign. Preserve which ZIP/member/source row supplied each observation.
For the fixed20-week support gate, count distinct ISO(asof-year,asof-week) keys with a negative net
and as-of date in2018–22. Also report distinct negative as-of dates and any multiple reports per ISOweek;
multiple conflicting-sign reports in one week are unresolved, not independently counted support.

Permitted outputs: identity/header/hash audit; total/valid/unresolved target row counts; as-of date range;
per-year unique reports, negative/zero/positive states and distinct negative ISOweeks; selected as-of
date/sign flags and original row IDs; support-gate decision. Position totals may be retained in a bound
source ledger if needed for reconciliation, but no exposure-to-price/dollar-flow calculation is allowed.

## Explicit exclusions

No `COT_NQ.csv`, TFF archive, NQ chart, release/exported-rank field, release/calendar mapping or Friday
assumption; no CL/NQ/ES or other raw price file; no MC workbook/trade list/current-book P&L; no percentage
return, gross/net strategy return, t-stat, correlation, resampling, placebo, economic signal replay,
held-window audit, daily/account simulation or performance-derived parameter. No later-year outcome.
As-of signs must not be turned into hypothetical Sunday keep/drop rows during this intake.

## Execution identity, retention and interpretation

Proposed code `analysis/codex_hunt_v2_cl_cot_state_intake.py` and outputs
`analysis/outputs/codex_hunt_v2_cl_cot_state_intake/`. Commit code plus this plan/evidence before rows;
use a branch/prereg/code-hash gate, exclusive run lock, immutable artifacts and a verified marker
binding all outputs/inputs. Retain incomplete attempts. Do not repeat a completed intake unchanged in
alternate directories. Synthetic fixtures may exercise metadata, integer validation, duplicate conflicts,
sign boundaries, ISOweek counts and the19vs20 support threshold; synthetic rows are not source evidence.

Program checkpoint before this plan:3/60 counted evaluations,3/10 registered hypotheses,2gross screens;
prior t6 archived65. This intake adds0 economic evaluations,0hypotheses and0gross screens. Parent/root
owns progress updates and commits. A failed state-support gate stops this proposed filter, not v2.
No point-in-time admission, TEST, H04 nomination, trading approval or user-action blocker follows from
any support result. Even a passing20-week gate still needs independent publication/batch/vintage proof,
an updated TEST evidence sheet, a separate economic preregistration and all ordinary v2 gates.
