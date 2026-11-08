# UGL/GLL historical clocks: PARTIAL VERIFIED / PUBLICATION AND EXECUTION GAPS OPEN

Summary: Historical primary filings establish a material NAV/benchmark regime break in January 2019.
Before the change, gold NAV follows 15:00 London; from January 4 the normal clock is 13:30 ET.
Both funds first used BCOMGC for NAV on January 7, 2019; this is distinct from the clock change.
Preserved 15 primary documents and all acquired fund files; 2,518 additive policy rows, no invented availability.
Historical publication/vintage clocks, actual reset executions and dated exceptions remain blockers.

Scope: source acquisition and data QA only. Script: `analysis/codex_gold_clocks_20261108.py`.
Output: [immutable sources and receipts](../inputs/gold_clocks_20261108/README.md).
Trials run: **0**. No return/strategy/account test, trading or operational setting change.

## Verified policy and the transition

| Period | NAV valuation policy | Benchmark | AP order cutoff policy | Evidence boundary |
|---|---|---|---|---|
| 2018 through January 3, 2019 | 15:00 London, usually 10:00 ET; US/UK DST mismatch varies | LBMA Gold Price PM | 09:30 ET in 2018 sponsor filings | Typical policy, not day-specific receipts or executions; cutoff discrepancy below |
| January 4, 2019 | 13:30 ET under December 20 announcement | Transition mechanics unresolved | 13:00 ET | Clock change precedes first new-benchmark NAV; exclude from any homogeneous mapping until reconciled |
| January 7, 2019 onward, through 2022 | Normally 13:30 ET | Bloomberg Gold Subindex, BCOMGC, rolling COMEX futures | Normally 13:00 ET | Historical sources corroborate policy; early closes/fair valuation and actual reset timing remain unverified by date |

The [February 2018 registration amendment](https://www.sec.gov/Archives/edgar/data/1415311/000119312518027791/d460791ds3a.htm)
and [2018 annual report](https://www.sec.gov/Archives/edgar/data/1415311/000119312519060564/d611404d10k.htm)
show the London-clock footnote. Do not assign fixed 10:00 ET to every 2018 date, or mechanically extend today's
13:30 policy backward. The annual report is retrospective evidence, not an available-before-trade vintage.

The [December 20, 2018 sponsor notice](https://www.sec.gov/Archives/edgar/data/1415311/000119312518354569/d677409dex991.htm)
announces January 4 NAV/cutoff changes and schedules the benchmark change on/about January 7.
The 2018 annual report's Note 9 confirms the **actual first new-benchmark NAV on January 7 for both funds**.
The [2019 annual report](https://www.sec.gov/Archives/edgar/data/1415311/000119312520056815/d816057d10k.htm)
and archived sponsor 2020 annual report corroborate the futures benchmark and normal clocks.
The [2021](https://www.sec.gov/Archives/edgar/data/1415311/000119312522054559/R18.htm)
and [2022](https://www.sec.gov/Archives/edgar/data/1415311/000119312523054105/R18.htm)
annual accounting-policy tables explicitly cover both funds. These use typical-time language; their
Eastern Standard Time shorthand is not authority to hard-code UTC-5 throughout the year.

**Cutoff discrepancy retained:** 2018 sponsor documents print 09:30 ET; the
[December 2018 exchange notice](https://www.govinfo.gov/content/pkg/FR-2018-12-27/html/2018-28007.htm)
cites 09:00 ET from older Amex releases. This investigation did not establish the intervening effective date
or all operational exceptions. The sidecar labels the printed sponsor policy and carries the conflict;
it does not silently treat the older-rule citation as the actual 2018 cutoff.

## A NAV clock is not a publication or executed-reset clock

The 2018 registration document describes typical rebalancing near NAV time. The
[March 2019 prospectus](https://www.sec.gov/Archives/edgar/data/1415311/000119312519090686/d702010d424b3.htm)
states daily rebalancing but permits its time and manner to vary at sponsor discretion. Daily objectives run
NAV-to-NAV. This supports a valuation anchor and a daily mandate, **not a synchronized executable GC order
at 13:30**, a fixed hedge window or known counterparty activity. Swaps and futures can transmit exposure
differently. An actual contract/weight and execution ledger remains absent.

The prospectus distinguishes frequently disseminated IOPV from actual once-daily NAV; the former commonly
starts from prior closing assets. IOPV is not a substitute for finalized daily NAV, net assets or shares.
Current sponsor pages have dated observations and generic market-return language; neither supplies original
2018-22 website releases or revisions. HTTP response Date/Last-Modified/ETag and today's retrieval time
describe the acquired object, not each historical row's first-publication time.

| Field or event | What is established | What remains unknown |
|---|---|---|
| NAV | Normal valuation clock and regime change | First public release/receipt, delays, revisions and dated exceptions |
| Net assets | Existing sponsor history retained and reconciled previously | Original vintage and field-specific public availability |
| Shares outstanding | Existing sponsor quantities retained | Public release clock; accounting recognition versus AP order/settlement date |
| Reset | Daily mandate; typical/variable timing disclosed | Orders, fills, execution window, netting and counterparty hedge timing |
| Contracts | Pre-2019 bullion benchmark versus later rolling futures index | Actual historical swap/futures weights, dated contracts/amendments and January 4 transition valuation |

**Publication gap remains open.** Bounded free primary-source discovery acquired no original per-day timestamped
NAV/AUM/shares-vintage panel. This is an acquisition limitation, not proof such records never existed. A date
label is not `available_at`. Applying an arbitrary next-day lag would be an assumption, not verification.
No same-day feature is admitted from these histories by this report.

## Creation, redemption and settlement offsets

The March 2019 prospectus's Creation and Redemption Transactions section establishes several distinct clocks:
valid pre-cutoff orders receive that order date; post-cutoff orders receive the next business date. Creation
payment uses order-date NAV plus fees. Normal cash creation delivery is T+1 by market close, with T+2 extension
or another agreed date; futures-transfer/block alternatives have separate provisions. Redemption units are
normally delivered by noon ET T+1, with extension provisions; proceeds normally follow by noon ET T+2, subject
to delivery and other conditions. These are historical terms, not today's settlement defaults.

The clauses do **not** establish a universal mapping from daily changes in published shares to an AP order,
cash settlement, sponsor hedge or a particular GC trade. Do not shift all share changes by a chosen number
of days, call net assets pure flows, or reconstruct unpublished shares by dividing AUM by NAV.

The historical index description gives a multi-day rolling convention, generally business days 6-10 with
approximately 20% per day. This is not an actual dated fund contract/weight ledger. The 2022 GLL prospectus
also contains an apparent silver/gold copy-text inconsistency in its roll paragraph, so no exact schedule
was reconstructed from that paragraph. The corroborating 2019 annual gold section identifies gold futures.

## Preservation, QA and review limits

- All **9 existing UGL/GLL source/normalized files** in the prior primary package have identical before/after
  SHA256 hashes. Existing exports and their empty `available_at` fields remain untouched.
- Archived **15 successful source responses**, verifying original and compressed byte counts/SHA256 and lossless
  decompression; one guessed sponsor annual-PDF URL returned **404**, preserved in its receipt. The actual
  2018 annual SEC filing was acquired successfully instead.
- Added **2,518 policy rows** covering the exact **1,259 existing 2018-22 dates per fund**: 253 pre-change,
  1 transition and 1,005 post-change dates per fund. These counts come from the script, not a synthetic calendar.
- All NAV/asset/share publication fields and actual reset-execution fields are blank; every holiday-exception
  flag remains unverified. Policy rows are an organizing sidecar, not daily observed timestamps or an exhaustive
  amendment history. Original quantities and prices were not repaired, filled or rebased.
- An acquired March 2021 registration amendment concerns VIX funds. It is retained but **excluded** from gold
  clock evidence; actual annual gold tables fill that source-scope gap. Search snippets alone are not admission.
- Relevant PDF pages were extracted in full with file-page locators. Raw originals retain layout authority;
  this was a text/clock audit, not a full financial-statement or PDF-layout review.

Reproduce `python -X utf8 analysis/codex_gold_clocks_20261108.py verify` from repository root.
See [evidence matrix](../inputs/gold_clocks_20261108/evidence_matrix.json),
[QA receipt](../inputs/gold_clocks_20261108/verification.json) and
[bounded discovery log](../inputs/gold_clocks_20261108/search_log.json).

## Smallest next check

Authenticate one existing contemporaneous NAV/net-assets/shares capture against its first receipt and revision
lineage, plus one actual reset/order/settlement record and dated early-close notice. Include a normal post-2019
session, a 2018 DST-mismatch session and January 4/7 transition evidence before expanding coverage. Preserve
unknowns if those records cannot be obtained free. Current holdings and a generic futures close cannot close
these gaps. No repeat blind endpoint crawl or purchase is justified by this result.

D15 remains **NEEDS DATA**; [data register](../DATA_NEEDED.md) and
[execution references](../EXECUTION_REFERENCES.md) updated. No profitability or strategy-code admission claimed.
