# SPY auction-history vendor comparison: NEEDS DATA

Summary: Databento is the first SPY-only route to price, not a verified cheapest supplier.
BMLL is a coverage/quote alternative; SpiderRock's published start leaves the 2018 design year missing.
NYSE's standard design-history benchmark is $30,000; no alternative SPY quote was obtained.
Saved an estimate-only request specification; no accounts, keys, messages, purchases or return trials.

Date: 2026-10-25. Branch: `codex/work`; parent `c99e055`.
Evidence/data gate: `agents/codex/evidence/spy_close_imbalance.md` and `spy_close_imbalance_data_gate.md`.
Script: `analysis/codex_auction_quote_spec.py`.
Output: `analysis/outputs/codex_auction_vendor_comparison/quote_spec.json`.
Public reference collection: `analysis/codex_auction_source_documents.py` and
`analysis/outputs/codex_auction_sample_intake/reference_manifest.json`.
Return trials: 0. Acquisition/format work only; no strategy preregistration or performance selection.

## Comparison

| Route | Evidence of fit | Cost evidence | Decision / unresolved questions |
|---|---|---|---|
| **Databento ARCX.PILLAR / imbalance / SPY** | Official worked example explicitly requests SPY Arca auction data. Historical API supports symbol filtering and a metadata cost estimate. | Historical usage-based pricing; exact request price and applicable terms not obtained. | **First to price.** Verify per-schema history, SPY missing sessions and all-in cost. An advertised dataset start is not proof of imbalance history or SPY completeness. |
| **BMLL Auction Imbalance** | Public coverage groups ARCX with NYSE venues and lists a November 2015 group start; schema describes per-message records. | No SPY-only public price located in inspected material; quote required. | **Coverage alternative.** Group/product start does not verify SPY imbalance coverage in each design year. Confirm extract rights, minimum spend and field mapping. |
| **SpiderRock StockExchImbalance** | Historical dictionary explicitly lists Arca from February 11, 2019, with source and gateway timestamps. | No SPY-only public price located in inspected material; quote required. | **Lower priority for this design.** Cannot supply all of 2018 under the published coverage. Verify archival preservation of every update, not just final state. |
| **NYSE direct TAQ Arca Order Imbalances** | Original relevant product; both public samples have parsed SPY updates. | October 2026 standard commercial back-history list: $500 per content month; 60 design months = $30,000. | Keep the user's existing SPY-only quote pending. A filtered extract or different licence may be priced differently; neither a discount nor a full-package purchase is assumed. |

This ordering reflects how directly each route could answer our narrow request. **No verified cheaper offer exists yet.**
Quotes must include any minimums, data fees, subscription obligations, applicable licence and retention rights.
SPY auction results/corrections, SPY NBBO and ES quotes need separate coverage/cost lines.
The direct-exchange benchmark is imbalance history only, not the total research-data budget.

## Concrete Databento estimate request

The JSON specification contains unexecuted calls to documented metadata methods only:

1. `get_dataset_range(dataset="ARCX.PILLAR")`: inspect `schema.imbalance`, not only dataset start.
2. `get_dataset_condition`: inspect the design calendar; this is dataset-level quality, not a symbol event census.
3. `get_record_count` and `get_cost`: `symbols=["SPY"]`, `schema="imbalance"`, `stype_in="raw_symbol"`,
   start `2018-01-01T00:00:00Z`, exclusive end `2023-01-01T00:00:00Z`.
4. Separately estimate July 1-2, 2026, for a potential comparison with our existing public files. This is not permission to buy a sample.

Those estimate scopes include all SPY auction messages during each day. API schema selection does not by itself
filter to the closing auction. A cheaper intraday request, if supported, must be constructed per session with ET/DST
and early closes handled; discarding opening messages locally does not reduce a full-day acquisition bill.
The documentation cautions that cost/count estimates can over-report outside discrete ten-minute windows.
No missing interval may be silently clipped and then represented as complete 2018-22 coverage.

`get_cost` is an estimate, not the download method. The saved script only generates JSON; it imports no vendor SDK,
reads no credentials and makes no network calls. No authenticated metadata request was executed.
The public pricing UI was readable, but browser interaction failed before a usable custom estimate appeared.
An authenticated metadata result or a user-visible completed portal estimate is still needed for a numerical quote.
Generic subscription cards and promotional credits are not a price for this historical SPY request.

## Data-quality checks before spending

- Databento's public tracker lists an issue titled **ARCX.PILLAR/XNYS.PILLAR/XASE.PILLAR - Imbalance Auction Timestamp
  reported in localtime instead of UTC prior to 2025-11-02**, under fix in progress when inspected.
  This names the auction-time field; it does not establish that every event or receive timestamp is wrong.
  Confirm correction status, affected field/version and clock behavior before parsing design years.
- The previously documented November 13, 2025 quantity-definition change remains a separate issue.
- BMLL's Arca price-field mapping and SpiderRock archival-update completeness remain open from the prior intake.
- Vendor capture time is not the user's historical receipt time. Execution delay still needs defensible reconstruction.
- Inspect missing/zero states, publication order and auction results without ES forward returns. No signal parameters are selected here.

## Routes that do not currently solve this request

Massive's inspected NOI page describes real-time access, with history not applicable; it is not a verified historical
SPY source. dxFeed's public June 2026 auction-imbalance announcement is for **Nasdaq TotalView**; it does not establish
historical SPY/Arca coverage. Nasdaq/QQQ remains a separate NQ hypothesis.
Stock bars, generic order-book imbalance indicators and auction summaries do not replace original pre-close updates.

## Sources and saved evidence

- Databento [SPY/QQQ worked example](https://databento.com/docs/examples/equities/auction-imbalance),
  [historical pricing](https://databento.com/pricing),
  [cost estimate](https://databento.com/docs/api-reference-historical/metadata/metadata-get-cost),
  [per-schema history](https://databento.com/docs/api-reference-historical/metadata/metadata-get-dataset-range),
  [record count](https://databento.com/docs/api-reference-historical/metadata/metadata-get-record-count),
  [dataset conditions](https://databento.com/docs/api-reference-historical/metadata/metadata-get-dataset-condition).
- Databento [auction-time issue](https://issues.databento.com/roadmap/arcxpillarxnyspillarxasepillar-imbalance-auction-timestamp-reported-in-localtime-instead-of-utc-prior-to-2025-11-02).
  Web retrieval showed the issue tracker index/title/status, not a complete technical incident analysis.
- BMLL [coverage](https://www.bmlltech.com/bmll-data-and-analytics),
  [auction product](https://www.bmlltech.com/products/bmll-data-feed/auction-imbalance).
- SpiderRock [historical imbalance dictionary](https://docs.spiderrockconnect.com/docs/HistoricalData/Data%20Dictionaries/StockExchImbalance/).
- NYSE [October 2026 historical pricing](https://www.nyse.com/publicdocs/nyse/data/NYSE_Historical_Market_Data_Pricing.pdf), page 4.
- dxFeed [Nasdaq imbalance announcement](https://dxfeed.com/dxfeed-adds-order-imbalance-data-for-nasdaq-totalview/).
- Massive [NOI documentation](https://massive.com/docs/websocket/stocks/imbalances).

Selected public pages were downloaded as local reference snapshots with hashes, under the existing ignored auction
input folder. The pricing-page HTML snapshot is an application shell; pricing text was inspected through web retrieval
and the rendered browser page instead. The reference manifest distinguishes download successes from failures. No additional market history
was acquired in this comparison; the two NYSE sessions remain the only parsed SPY auction samples.
Research status stays **NEEDS DATA**. The next step is obtaining a narrow, coverage-verified price estimate, then
applying the existing acceptance gate before any purchase or returns.
