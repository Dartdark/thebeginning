# SPY / Arca public sample intake: NEEDS DATA

Summary: Downloaded both official free Arca samples on the local research PC and verified SPY closing updates.
July 1/2 contain 3,385/3,494 SPY closing messages: two sessions, not 6,879 independent events.
Size, gzip, hashes and limited SPY format/order checks pass; history, receipt timing and quotes remain missing.
No ES returns, strategy parameters, trial account, purchase, vendor message or live change; return trials: 0.

Date: 2026-10-25. Branch: `codex/work`; continued from `0481412` after fetching and inspecting branch differences.
Evidence: `agents/codex/evidence/spy_close_imbalance.md` and its data gate.
Scripts: `analysis/codex_collect_auction_samples.py`, `analysis/codex_audit_arca_samples.py`,
`analysis/codex_auction_source_documents.py`, `analysis/codex_auction_intake_checks.py`.
Outputs: `analysis/outputs/codex_auction_sample_intake/` (sample audit, reference manifest, synthetic checks).

## Collected and parsed

The [official sample directory](https://ftp.nyse.com/Historical%20Data%20Samples/TAQ%20NYSE%20ARCA%20ORDER%20IMBALANCES/)
is accessible through this PC's normal network access. The earlier cloud 403 was not bypassed.
Compressed originals are read-only in `agents/codex/inputs/auction_data_sources_20261025/nyse_samples/`;
SPY-only CSV extracts are in the sibling `parsed/` folder. Originals and extracts remain local and git-ignored;
the committed audit records original/extract SHA256 hashes. No research caches were rebuilt.

| File date | Compressed bytes | All-symbol type-105 rows | SPY type-105 / closing rows | Closing source-time range |
|---|---:|---:|---:|---|
| 2026-07-01 | 115,017,342 | 3,786,073 | 8,010 / 3,385 | 15:00:01.054465149-15:59:59.063645971 |
| 2026-07-02 | 126,487,758 | 4,156,938 | 8,410 / 3,494 | 15:00:01.053494076-16:00:00.134319480 |

Both files passed expected size and complete gzip/CRC checks. Every type-105 row has 24 fields.
SPY fields passed decimal/integer, timestamp and supported-enum checks. Among SPY type-105 messages,
there were no duplicate feed/symbol sequence IDs, backwards sequences or backwards source times.
This checks observed SPY records, not numeric validity of every other symbol or missing-message completeness.
Sequence gaps are not treated as missing records: other message types can occupy intervening IDs.

Closing messages project 16:00 in both files. July 1 contains both sides and five nonzero-side changes;
July 2 contains sell-side updates throughout. Neither contains a zero total imbalance.
The first freeze flag appears at 15:59:00 on each day. Maximum observed gaps are about five/four seconds;
absence of an update need not mean missing data because the exchange publishes on changes.
July 2 has one closing message at/after projected auction time. Preserve it for audit, exclude it from
any future pre-close observation. No entry clock, threshold, signal denominator or delay has been selected.

Source times are consistent with an Eastern auction clock. The audit supplies explicitly assumed ET/CT/UTC
views using date-aware zones, while retaining original nanoseconds. This is not a verified customer receipt
clock. Sparse days, DST, early closes, delays and historical timezone conventions still require full intake.
Both samples have a normal 16:00 projected close; they do not test early-close behavior.
The file inventory contains mapping, status and imbalance messages only, with no auction execution print.

## Material schema issues

The downloaded [TAQ v2.4a specification](https://www.nyse.com/publicdocs/nyse/data/TAQ_XDP_Products_Client_Spec_v2.4a.pdf)
was visually checked on pages 25-28. Its numbering skips ordinal 4; in the samples Symbol is physical column 4,
not column 5. The parser uses the observed 24-field layout and rejects unknown widths. It retains total,
market and NYSE-only unpaired quantities separately. The side labels total imbalance only.

That specification still describes Arca quantities at indicative match price. The
[real-time v2.2n specification](https://www.ice.com/publicdocs/nyse/data/NYSE_Pillar_Order_Imbalances_Client_Specification_v2.2n.pdf),
page 11, corroborates [Databento's November 13, 2025 reference-price change](https://databento.com/docs/datasets/arcx-pillar).
The live-feed PDF was readable through web retrieval but its direct local download returned 403; no bypass was tried.
The sample's physical layout does not resolve whether TAQ documentation is stale or historical output differs.
**Quantity-definition era remains unvalidated; do not combine or normalize feeds on column names alone.**

## Further public-source search and collection

Downloaded reference documents/pages, the pinned DBN SDK fixture and its licence have hashes in `reference_manifest.json`.
The SDK fixture matches the earlier pinned hashes; it is format material, not an additional SPY session.
The official [2026 calendar](https://www.nyse.com/publicdocs/nyse/ICE_NYSE_2026_Yearly_Trading_Calendar.pdf)
was collected and visually checked. The collectors use named public URLs, bounded reads and exclusive creation;
they preserve existing originals. The sample downloader's error cleanup now supports the PC's Python 3.7.
The audit uses the already installed bundled Python 3.12 with timezone data. No packages were installed.

| Route | New finding / collection status | Remaining limitation |
|---|---|---|
| BMLL | Public auction schema PDF and sample-index HTML downloaded. Schema says one row per message and includes exchange sequence and UTC nanoseconds. | No directly downloadable auction-history sample was exposed on the inspected index; exact SPY years, rights and price unverified. |
| BMLL field mapping | Schema's Arca ReferencePrice maps to upstream IndicativeMatchingPrice. | It cannot be joined as though every vendor's reference-price name has the same meaning. |
| SpiderRock | Public historical dictionary downloaded; it lists Arca history from 2019-02-11, source and gateway timestamps. | Public docs still do not establish that all intraday updates survive archival storage. No historical files acquired. |
| Databento | Arca mapping documentation downloaded. | Symbol/schema history and quote still require authorized metadata access. No keys inspected or APIs called. |
| Massive NOI | Public documentation downloaded: describes a paid real-time WebSocket, history not applicable. | SPY/Arca entitlement unverified; this is not the missing downloadable design history. No connection or trial started. |

Sources: [BMLL schema](https://www.bmlltech.com/files/documents/BMLL-Auction-Imbalance.pdf),
[BMLL public documentation index](https://www.bmlltech.com/products/bmll-data-feed/documentation),
[SpiderRock historical dictionary](https://docs.spiderrockconnect.com/docs/HistoricalData/Data%20Dictionaries/StockExchImbalance/),
[Massive NOI](https://massive.com/docs/websocket/stocks/imbalances).
Search results offering stock bars, generic book imbalance, summaries or unrelated Nasdaq signals were not accepted as SPY auction updates.

## Gate and reproducibility

Limited sample-format gate: PASS on both samples. Complete study gate: **NEEDS DATA**.
Remaining: 2018-22 SPY coverage and event census, historical schemas/rules, quantity-definition confirmation,
receipt/lag evidence, auction results/corrections, synchronized SPY NBBO and ES quotes, licence/price and costs.
Two adjacent 2026 sessions cannot establish multi-year completeness, power or an edge. No P&L fields were generated.
Seventeen synthetic checks passed, including unknown widths/sides, bad quantities/prices/times and seasonal clock conversion.

From the research repo, set `$auctionPython` to the installed bundled Python path in `sample_audit.json`, then:

```powershell
& $auctionPython -B analysis/codex_auction_intake_checks.py
& $auctionPython -B analysis/codex_audit_arca_samples.py
```

To recollect on an allowed host, the original bounded command accepts both sample dates:
`python analysis/codex_collect_auction_samples.py --download-nyse --dates 20260701 20260702`.
It validates and reuses files already present. Raw downloads are not available from Git alone.
Reference collection defaults to a dry list; explicit `--download --names ...` collects selected references.
Next return work remains prohibited until the acceptance gate passes and a fixed preregistration is committed.
