# Primary-data transfer review: WATCH — integrity passes; signal admission pending

Summary:
Pulled local acquisition commit a5dec2d and independently verified all 1,170 compressed/original file hashes and sizes.
Five fund histories pass basic arithmetic; BOIL still has 1,178 identity failures in the original sponsor file.
New inputs include GVZ/OVX, longer Cboe histories, 844 Fed operations, 13,061 rate records and 233 buybacks.
The transfer is usable for source research; original information/benchmark clocks remain gates before strategy returns.

Source report: [`new_data_local_20261108.md`](new_data_local_20261108.md), source commit `a5dec2d`.
Script: `analysis/codex_primary_data_review_20261108.py`.
Output: `analysis/outputs/codex_primary_data_review_20261108.json`.
Trials run: **0**. This task checks new data; no economic outcomes, holdout or portfolio comparison was run.

## What was independently checked

The two transport manifests contain 1,170 unique gzip paths: **1,123,329,896 compressed bytes** and
**1,199,841,292 original bytes**. Every compressed and decompressed byte count/SHA256 matches. There are no
unlisted or missing gzip files. Windows path separators are interpreted portably without modifying the source
manifests. The 47 primary HTTP receipts also match their transported payloads. This verifies the delivery and
recorded source provenance; it does not independently recreate the publishers' historical public receipt times.

The new checker recomputes raw-to-normalized values from the original CSV/JSON/XML payloads. It does not call the
local acquisition script's audit functions, use its aggregate assertions as results, or execute external code.

| Input | Delivered and checked | Remaining limitation |
|---|---|---|
| UGL/GLL | 4,512 dates each, 2008-12-01–2026-11-06; exact NAV/shares match secondary; no arithmetic failures above 1% | Historical available-at vintages, mandate/benchmark weights, reset execution and creation/redemption offset |
| UCO/SCO | 4,516 dates each, 2008-11-24–2026-11-06; NAV/shares reconcile; no arithmetic failures above 1% | Current balanced-WTI benchmark is not historical front-month CL exposure |
| BOIL/KOLD | 3,796 dates each, 2011-10-04–2026-11-06 | **BOIL remains quarantined**; KOLD passes arithmetic only |
| VVIX/SKEW/VIX9D | 5,142 / 9,265 / 3,985 closes through 2026-11-06; all 11,862 old cached observations match | Original release/revision clocks and prelaunch status; SKEW gaps persist |
| GVZ/OVX | 4,309 closes each, 2009-09-18–2026-11-06 | New gold/oil implied-volatility states, not signed positions or tradeable options/futures quotes |
| NYFed | 844 unique operations with 37,359 nested security rows; 13,061 unique type/date rate records, 2017–2026 | Post-operation results and revised rates; original advance operation schedules/first receipts unresolved |
| Treasury buybacks | 233 operations / 6,369 security rows, 2000-03-09–2026-11-05; complete page/count checks | Historical programs/tests differ from the modern program; source event time is not verified public first receipt |

All normalized fund/index numbers match the original payloads, including previous NAV and NAV-change fields.
No row was filled. All new `available_at` values remain blank. Source NAV/shares match secondary values exactly;
the largest AUM discrepancy is **$0.00000022**, consistent with prior floating-point serialization.

**BOIL correction to the earlier hypothesis:** the sponsor original itself has the same 1,178 >1% NAV × shares/AUM
failures, 82 zero-share rows and 40 design-period failures. The secondary parser's rounding is not a sufficient
explanation or repair. Preserve the primary displayed precision and quarantine the history; do not infer shares
using AUM/NAV. Five passing fund identities do not certify matching historical adjustment bases or known-ahead flows.

All five index series contain unique positive closes. SKEW 2018-12-03 and 2019-07-05 are absent in the primary file
as well. Do not fill them automatically. Prelaunch/back-calculated observations must remain distinguishable; the
source package explicitly flags pre-October 2013 VIX9D. These are daily-close data, not intraday OHLC or dealer gamma.

All 20 annual NYFed datasets independently match the exact record multisets reconstructed from their disjoint
half-year raw queries. Normalized nested operations/rates match original JSON losslessly except the explicit blank
availability field. SOFR begins 2018-04-02. An operation's `releaseTime` or revised `lastUpdated` is not, by its label
alone, certification of when an executable historical announcement became public.

## Useful event-clock finding

All 1,089 supplemental receipt payloads match their recorded hashes/sizes. The document audit reproduces **521
well-formed XMLs**, **527 PDF signatures** and **520 operation-document clock rows**. PDF signatures are a content-type
check, not a full independent review of 527 documents. XML parsing likewise does not establish historical truth.

The 520 source operation-start timestamps use 376 `-04:00` and 144 `-05:00` offsets. Every normalized XML field matches
its original document; no filename or fixed year-round EST conversion substituted for the source time.

**None of the 520 documents supplies the parsed result-publication field.** All carry an announcement field before
the operation, including 172 documents labelled `Results` and 206 labelled `Released`. A result document retaining
an earlier `announcementDTM` does not mean its accepted amounts/prices were known then. Keep original announcement,
operation, result-content availability and later download clocks separate. This is retained in
[`EXECUTION_REFERENCES.md`](../EXECUTION_REFERENCES.md) under E11/E19; no execution saving was measured.

The buyback table has 174 entries from 2024 onward, including tests, and only seven operations in 2018–22. Those seven
are not a design sample for the regular modern program. The current future tentative schedule remains separate from
completed outcomes. No future operation/rate/buyback outcome was merged into the audited completed histories.

## What this enables next

**First source-feasibility priority remains UGL/GLL gold reset pressure (D15).** We now have primary-backed asset
history rather than a URL or secondary-only cache. The next decision is whether one historical fund-date can be
authenticated against its mandate, benchmark/contract weights and information/reset clocks. Fund assets alone do
not reveal the unoffset futures demand. No new threshold or trading window was selected from returns.

**Second, GVZ/OVX add actual new risk-state inputs for GC/CL research.** A separately justified hypothesis could use
lagged daily values after an explicit availability policy; a higher-volatility label is not automatically a price
direction signal. The existing rejected gold/oil rules and multiple-testing history remain unchanged.

**Treasury operations/buybacks now support better event-source work.** NYFed results cannot substitute for original
advance schedules. Modern buybacks need an openly declared recent/forward study design, not a fabricated 2018–22
modern-program sample or a new claim that 2023+ is unseen. No plan slot is earned by this data audit.

## Reproduction and scope

```bash
python analysis/codex_primary_data_review_20261108.py --output scratch_data/primary_data_review_new.json
python analysis/codex_new_data_20261108_check.py
```

The first command is fully offline, accepts Windows-generated manifest paths, verifies every transferred byte and
independently checks normalization/partition/document clocks. It refuses an existing output receipt. Only the audit
time varies. The earlier secondary archive's strict blob/integrity suite **passes on this Linux checkout**; the local
report honestly recorded its Windows CRLF failure rather than claiming a pass. That checkout issue does not justify
weakening raw-source hashes or rewriting either archived source.

No new strategy return, trial reservation, scout cycle, live/VPS/broker change or evaluation/funded/personal allocation.
Tell Claude: review `agents/codex/results/primary_data_review_20261108.md`; integrity/reconciliation passes,
BOIL stays quarantined and event-information admission remains conditional.
