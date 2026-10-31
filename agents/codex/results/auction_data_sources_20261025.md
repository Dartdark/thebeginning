# Auction-data source search: NEEDS DATA — useful routes found, history not acquired

Summary: Found free NYSE Arca sample links and several commercial auction-message routes.
Databento ARCX.PILLAR is the first targeted SPY/ES route to price; Nasdaq/QQQ is a separate NQ study.
Collected a small public SDK format fixture and its licence locally; no usable SPY history acquired.
NYSE sample downloads fail with the cloud proxy's 403; a bounded local-PC downloader is included.
No purchases, account creation, vendor messages, return tests or live-system changes.

Date: 2026-10-25. Scope: current auction-imbalance need and supporting prices/timestamps.
**Later local-PC update:** both named NYSE samples were downloaded and parsed successfully.
See `auction_sample_intake_20261025.md`; the cloud-access findings below remain a record of that earlier environment.
Evidence parent: `agents/codex/evidence/spy_close_imbalance.md`.
A web page, advertised start date, public example and an acquired multi-year dataset are different levels of evidence.

## Best paths, in order

1. **Free NYSE Arca samples:** official directory [S1] lists two gzip files for 2026-07-01 and 2026-07-02, at 115,017,342 and 126,487,758 bytes. These are genuine product sample links, but their contents and SPY coverage have NOT been inspected. They can check format, symbol presence and message ordering; two days cannot validate an edge.
2. **Databento ARCX.PILLAR:** primary documentation describes SPY-compatible Arca auction imbalances, auction-result statistics and feed timestamps [S2,S3]. Its public SPY/QQQ worked example supports the exact dataset/symbol route [S4]. Obtain metadata and a SPY-only historical estimate before any order; no verified personal price or full-history entitlement obtained.
3. **NYSE direct historical product:** relevant source for old Arca history [S5]. Existing quote request remains unanswered. Earlier recorded full-market list pricing is not a current SPY-only quote. Do not purchase the broad package for an untested hypothesis.
4. **SpiderRock StockExchImbalance:** explicit NYSE/Arca start 2019-02-11 and historical delivery 04:00 CT T+1 [S6]. Preserves source and gateway timestamp fields. Verify that historical files retain the sequence of intraday updates rather than only the last state. T+1 packaging alone does not invalidate replay of originally live messages; a final snapshot alone would.
5. **BMLL:** advertises auction imbalance data from 2017, with side/size, indicative/reference prices and time fields; API/S3/SFTP options [S7]. Global product start is NOT proof of SPY/Arca coverage in 2018. Price, symbol coverage and access require verification; no sample/trial account opened.
6. **Nasdaq through Databento XNAS.ITCH:** primary worked example uses QQQ [S4]. Appropriate for a separately documented QQQ/NQ hypothesis, not a substitute for missing SPY/Arca data.

AlgoSeek's public SIP/TAQ material did not establish auction-message availability in this search. Do not infer NOII from an ordinary trades/NBBO product.

## Material schema and timing findings

Databento's Arca field mapping [S2] identifies a definition break on **2025-11-13**: paired and imbalance quantities switch their reference from indicative match price to reference price. Preserve both prices and audit comparisons across this boundary.
A pre-2025 model may otherwise appear to change when the measurement changed. Do not rescale regimes after inspecting returns.
The documentation also identifies a March 2019 protocol-field addition, requiring explicit unavailable-field handling.

Databento captures `ts_recv`; it is receipt at the vendor's server, not receipt on the user's computer. Add client transport/order latency before an executable fill. Source/exchange timestamps alone do not prove availability.
Auction-result messages belong to a different schema from imbalance updates. A research order must include any normalization inputs, symbol definitions and necessary quote data, rather than only the imbalance file.

The ARCX.PILLAR advertised start **2018-05-01** appears in indexed vendor material/API examples [S8]; the opened catalog page's dynamically rendered specification did not expose a per-schema coverage table. Treat that date as a lead until authenticated metadata verifies the imbalance schema and SPY specifically. It would leave early 2018 missing if confirmed. Register a shorter design period openly; do not fabricate those months.
No numerical XNAS.ITCH start or price is asserted here.

## Free alternatives that do not fill the same need

- **NYSE public auction viewer** [S9]: exchange announcement describes trailing three-month history for large NYSE auctions, displayed as minute averages. Helpful for inspecting mechanics; not proven original Arca/SPY message history. A minute average is known only after that minute completes, not at its start.
- **Mendeley ClosingAuction replication** [S10]: landing page describes replication code using exchange data merged with CRSP/TAQ. It does not establish that the licensed raw input data are downloadable. No files acquired.
- **Bogousslavsky/Muravyev public research data** [S11]: 2010–2018 stock-level auction volumes and deviations, not a pre-close signed SPY message stream. Relevant background, unsuitable as the proposed trading input.
- **Databento open-source DBN fixture** [S12]: downloaded 5,554-byte binary plus licence from a pinned official repository. Format-development material only; neither its symbol/auction coverage nor its market representativeness has been verified. It is NOT research-ready history. Local files and SHA256 hashes are in the acquisition manifest; data bytes are kept local rather than republished as a licensed exchange-history bundle.

## Collection status and network limitation

The web connector could inspect public pages. A shell request first lacked network access; a supported additional-network request then reached the normal proxy and received **403 Forbidden** for ftp.nyse.com.
No proxy bypass, alternate mirror of the denied host, secret inspection or credential workaround was attempted.
Consequently, the large NYSE gzip files are located but not downloaded. This is an environment restriction, not evidence NYSE requires payment for those samples.

`analysis/codex_collect_auction_samples.py` defaults to listing the two exact public URLs. On a computer with permitted access, `--download-nyse --dates 20260701` downloads only the selected free sample, limits size, writes an original compressed file, checks gzip integrity and creates a SHA256 manifest. No credentials, brokerage connections or trading changes.
Use a research checkout/output folder. Do not run it against a live strategy directory. It neither scrapes arbitrary websites nor evades vendor controls.

The user can instead allow ftp.nyse.com through the cloud environment's supported network configuration and run the same script there. This report does not change that configuration.

## Local computer integration

Official OpenAI CLI documentation [S13] supports running Codex against local files and commands. A local app/CLI session pointed at the research clone can use local download access, subject to its permissions.
This cloud chat is not itself attached to the user's PC; creating files here does not install anything there or grant remote control.
Keep research in codex/work and preserve the existing prohibition on VPS, broker settings, API keys and live trading files.

## Next step

Inspect one official free Arca sample when networking permits. Verify SPY closing messages and schema eras without future returns.
Then obtain Databento metadata/quote (requires an authorized account/key supplied through the normal supported setup, never pasted into chat). Request a narrow sample first; no billable data endpoint is called by our downloader.
Research status remains NEEDS DATA. No S-rank or profitability claim follows from these sources.

## Source register — inspected 2026-10-25

S1: https://ftp.nyse.com/Historical%20Data%20Samples/TAQ%20NYSE%20ARCA%20ORDER%20IMBALANCES/
S2: https://databento.com/docs/datasets/arcx-pillar
S3: https://databento.com/datasets/ARCX.PILLAR
S4: https://databento.com/docs/examples/equities/auction-imbalance
S5: https://www.nyse.com/market-data/historical/taq-order-imbalances
S6: https://docs.spiderrockconnect.com/docs/HistoricalData/Data%20Dictionaries/StockExchImbalance/
S7: https://www.bmlltech.com/products/bmll-data-feed/auction-imbalance
S8: https://databento.com/docs/api-reference-historical (indexed API examples; not a completed metadata request)
S9: https://www.nyse.com/data-insights/nyse-introduces-closing-auction-imbalance-analysis-tool and https://www.nyse.com/nyse-auction-data
S10: https://data.mendeley.com/datasets/dcrnzrmfxy/1
S11: https://bogousslavsky.github.io/data/
S12: https://github.com/databento/dbn/tree/82f76c1de6f5c8a1f4b3711fac423f88a3f91d67/tests/data
S13: https://help.openai.com/en/articles/11096431 (redirected to current official CLI documentation)

