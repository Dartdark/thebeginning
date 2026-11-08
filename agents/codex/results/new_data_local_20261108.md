# Local primary intake: acquired and reconciled; BOIL stays quarantined

Summary:
All 47 manifest jobs succeeded with normal local networking after 47 sandbox DNS failures.
Six sponsor NAV histories reconcile on NAV/shares; BOIL's original file still has 1,178 identity failures and 82 zero-share rows.
Five official Cboe histories extend through November 6, 2026; overlapping cached closes match exactly.
Acquired 844 NYFed operations, 13,061 rate records, both complete buyback tables and 1,089 supplemental requests.
No returns or portfolio changes; historical publication, reset-execution and benchmark-weight gates remain.

## Delivery and preservation

Task: `agents/codex/TASK_new_data_local_20261108.md`. Read AGENTS.md/BUILDER_BRIEF.md and the intake README; fast-forwarded `origin/codex/work` without discarding work. Existing source histories were read only, not rewritten. New package: `agents/codex/inputs/new_data_primary_local_20261108/`.

Scripts: existing `analysis/codex_new_data_20261108.py` and new `analysis/codex_new_data_local_20261108.py`. New package includes separate normalized files, all-date numeric difference ledgers, QA/disposition/clock flags, raw-source HTTP receipts, original and gzip byte counts/SHA256 manifests. Gzip round trips were checked byte-for-byte. `available_at` stays blank. The original sponsor text values, including thousands-of-shares precision, remain in compressed original CSVs; normalization uses Decimal multiplication by 1000 only.

Both initial commands failed every request in the sandbox with `<urlopen error [Errno 11001] getaddrinfo failed>`: 24 sponsor/index and 23 macro jobs. These exact failures are retained. The normal-network retry in fresh `_02` directories downloaded all 47 successfully. No network settings, credentials or access controls were changed; no purchase, account activation, external message, live/VPS/broker access or strategy backtest.

## Sponsor originals and BOIL

Official source: [ProShares UGL page](https://www.proshares.com/our-etfs/leveraged-and-inverse/ugl), equivalents for all six funds, and their linked accounts.profunds.com NAV/holdings downloads. Acquired full histories, six current holdings snapshots, six fund pages and split history. Also retained two linked current statutory prospectuses and an annual report; read receipts identify inspected NAV/rebalancing passages. These documents describe current arrangements, not authenticated historical mandates.

| Fund | Rows | First date | Last date | Primary identity failures >1% |
|---|---:|---|---|---:|
| UGL | 4,512 | 2008-12-01 | 2026-11-06 | 0 |
| GLL | 4,512 | 2008-12-01 | 2026-11-06 | 0 |
| UCO | 4,516 | 2008-11-24 | 2026-11-06 | 0 |
| SCO | 4,516 | 2008-11-24 | 2026-11-06 | 0 |
| BOIL | 3,796 | 2011-10-04 | 2026-11-06 | **1,178** |
| KOLD | 3,796 | 2011-10-04 | 2026-11-06 | 0 |

Every overlapping date's NAV and shares match the secondary copy numerically. Exact-decimal AUM differences occur on GLL144/UCO1,686/SCO405/BOIL1,102/KOLD1,380 rows; maximum absolute difference across them is $0.00000022, consistent with binary-float serialization, not a material fund revision. UGL has no differences. Difference ledgers retain every nonzero decimal difference rather than silently applying a tolerance.

**BOIL remains quarantined as a whole dataset.** The original sponsor download still contains 82 zero-share rows and the same 1,178 >1% NAV×shares/AUM failures, including 40 in 2018–22. Thus the earlier secondary-collector rounding explanation alone does not resolve the defect: the available sponsor history itself lacks enough displayed historical share precision. No shares were inferred from AUM/NAV. This finding does not establish erroneous economics at the sponsor; split-restatement and displayed-precision basis remain unresolved.

Five other funds pass the arithmetic check but are not admitted as historical reset-pressure inputs. Original publication/revision vintages, creation/redemption offsets, historical mandate changes, dated benchmark contracts/roll weights and actual reset execution remain missing. Current prospectuses warn rebalancing time/manner can vary; current holdings and NAV conventions must not be projected backward into 2018–22.

## Official Cboe daily closes

Source: [Cboe historical data](https://www.cboe.com/tradable_products/vix/vix_historical_data) official CDN downloads, exact URLs in acquisition receipts.

| Index | Rows | First | Last |
|---|---:|---|---|
| VVIX | 5,142 | 2006-03-06 | 2026-11-06 |
| SKEW | 9,265 | 1990-01-02 | 2026-11-06 |
| VIX9D | 3,985 | 2011-01-04 | 2026-11-06 |
| GVZ | 4,309 | 2009-09-18 | 2026-11-06 |
| OVX | 4,309 | 2009-09-18 | 2026-11-06 |

All 3,955/3,951/3,956 overlapping VVIX/SKEW/VIX9D closes match exactly. SKEW **2018-12-03 and 2019-07-05 are also absent in the primary file**; left unfilled. Dates are unique and closes positive. Only daily closes were normalized; synthetic secondary OHLC/volume were not imported. Pre-October2013 VIX9D remains back-calculated per the retained original intake methodology review. Other prelaunch/revision statuses were not newly certified; explicit clock flags preserve that uncertainty. No signed dealer position or intraday fill data follows.

## NYFed operations and funding

Saved the official [API documentation](https://markets.newyorkfed.org/static/docs/markets-api.html) and YAML specification. The specification verifies `/api/tsy/{operation}/results/{include}/search` and `/api/rates/all/search`, allowed path values, and inclusive start/end dates. These search endpoints document no pagination/record-limit parameter; the separate `last/{number}` endpoint's cap was not applied to search.

Annual 2017–2026 queries contain **844 unique operation-ID/date records, 37,359 nested security-detail rows and 13,061 reference-rate records**. Independently downloaded disjoint inclusive half-year queries: all **20 annual datasets match the exact record multisets of their halves**. This verifies query consistency and absence of that form of annual truncation, not completeness against an independent exchange/event registry. Retain results as post-operation outcomes.

Rate records preserve all original fields (rates, percentiles, volume, revision indicators, targets and SOFR averages/index where present), plus blank availability. SOFR/TGCR/BGCR each start **2018-04-02**, 2,148 observations each; no 2017 SOFR was invented. EFFR/OBFR each have 2,473 rows from 2017-01-03; SOFRAI has 1,671 from 2020-03-02. Queries end 2026-11-08; latest regular rate effective date is November5 and SOFRAI November6. Separate original operation announcement/schedule archives and public first-release clocks were not recovered from the inspected current pages; raw current pages and attempts are retained. No result was reclassified as advance-known scheduled demand.

## Treasury buybacks and document clocks

Source: [TreasuryDirect buybacks](https://treasurydirect.gov/auctions/buy-backs/) and the two official Fiscal Data endpoints. Operations **233 rows**, security details **6,369 rows**, each one page matching reported total-count/total-pages. Coverage 2000-03-09–2026-11-05 includes historical programs and tests, not one homogeneous modern sample. There are 174 operations dated2024 onward, beginning with April2024 test operations. The seven2018–22 entries are not a regular modern-program design sample.

Followed the official page's year/filename link construction to fetch all referenced modern preliminary/final announcements, results and special notices. Supplemental batch: **1,089 successful requests**, including **521 well-formed XML and 527 PDF payloads**, the current tentative calendar, NYFed half-year query checks and current reference page. Retained the linked XSD and May2025 XML-change notice separately. No malformed XML/non-PDF body was found in the supplemental document checks. A successful HTTP HTML response is retained as a document, not treated as a historical operation announcement.

Normalized **520 operation-document clock rows** separately from the data tables. XML operation-start timestamps explicitly carry **376 `-04:00` and 144 `-05:00` offsets**, so fixed year-round EST is inappropriate. Source `announcementDTM`, operation start/close and settlement are retained separately; absent result-publication fields stay blank. An announcement field carried on a result document is not automatically the result-release clock. Example source XML: April3,2024 announcement11:00−04:00 and operation13:40–14:00−04:00; filename174000 encodes a different clock. Filename time was not used as announcement time. Original actual public first receipt remains unknown.

The saved November2026 tentative schedule covers November12,2026–February9,2027; it is a dated current snapshot, separate from completed results capped November8. No future operations were merged into results or historical 2018–22 formation data.

## Checks and research disposition

Primary content checks, Decimal reconciliation, unique dates, positive index closes, buyback page/count checks, duplicate NYFed operation-ID/date checks, exact annual/half-year record equality, XML parsing/PDF signatures and compression round-trip hashes passed. The existing `codex_new_data_20261108_check.py` stopped at `Changed source blob: raw/daggerok/LICENSE`: verified Windows CRLF versus committed LF contents are identical after newline normalization. That pre-existing strict Git-blob check was not reported as passing and the old archive was not rewritten. New primary files have their own byte-exact transport hashes.

This makes primary-backed gold/oil asset histories, five close-only risk indices, funding histories and documented modern buyback events available for further source/clock work. It does not admit BOIL, prove historical known-ahead reset flows, revive failed strategies or authorize returns. Trials run: **0**. Tell Claude: review this report and `agents/codex/inputs/new_data_primary_local_20261108/qa_summary.json`, `supplement_qa.json` and transport manifests.
