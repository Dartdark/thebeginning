# Calvados dated VX acquisition and metadata audit

2026-10-31. Zero strategy signals or candidate returns were calculated. Raw data remains scratch-only and is not authorized for redistribution to Git.

## Acquired archival data

Downloaded the pinned [Pustak-007/ml_risk_overlay archive](https://codeload.github.com/Pustak-007/ml_risk_overlay/zip/7a8df4089664c339de9a4c5900cecdbe9d5b954e), commit `7a8df4089664c339de9a4c5900cecdbe9d5b954e`, through the inherited proxy on an allowed GitHub domain. The download succeeded after enabling network access for that bounded tool command. No source credentials or authentication were used. Initial sandbox-only attempt returned Operation not permitted; no alternate proxy or route was used.

Archive: `/workspace/calvados_data_prior/ml_risk_overlay_7a8df408.zip`, 4,240,816 bytes. Extracted **66 individual monthly VX files from December2017 through May2023**, 1,060,105 bytes, into `/workspace/calvados_data_prior/archive_7a8df408/data/raw/vix_futures_data/`. The archive itself contains monthly files2014–2025; only the requested design/warm-up/beyond-year-end expiry set was extracted. No strategy source or notebook was executed.

`downloaded_panel_manifest.json` preserves the archive SHA256, per-file raw URL, bytes, SHA256 and Git blob SHA. Each extracted file's Git blob hash was recomputed from its bytes. The acquisition notebook explicitly attributes scraping to Cboe historical and archive pages; see [notebook](https://github.com/Pustak-007/ml_risk_overlay/blob/7a8df4089664c339de9a4c5900cecdbe9d5b954e/Notebooks/01_Data_Acquisition_and_EDA.ipynb). This is useful thirdparty provenance. Equality to the official originals is not verified. No explicit repository/data license was observed; original Cboe rights remain applicable.

Native header: `Trade Date,Futures,Open,High,Low,Close,Settle,Change,Total Volume,EFP,Open Interest`. Actual expiry is encoded in the filename and month label, not a dedicated CSV column. Both monthly and weekly products use the official VX download path; this archive's set is monthly. Inspect and preserve every identity instead of substituting a continuous front/second-month series.

## Metadata-only gate

Audit code: `audit_panel.py`; detailed output: `panel_metadata_audit.json`; per-date identity census: `candidate_identity_coverage.csv`.

Calendar base: pandas_market_calendars5.5.0 CFE valid-day implementation plus **2018-12-05**, which primary Cboe documentation proves was a VX business day. The package ignores extended hours and has outdated clock definitions, so its times were never used. Other historical calendar details remain secondary implementations, although every raw row and lifecycle date matches this corrected date set.

TTS in this audit counts CFE dates strictly after the observation through expiry inclusive. Root must freeze the intended source/adaptation convention before returns.

| Metadata property | Observation |
|---|---:|
| Design CFE dates2018-01-02–2022-12-30 | 1,260 |
| Monthly candidate rows with15–93TTS | 4,740 |
| Missing expected candidate identities | 0 |
| Duplicate contract/date rows | 0 |
| Candidate rows with nonpositive Open or Settle | 0 |
| Candidate rows with High<Low or nonpositive volume | 0 |
| Candidate dates missing11settlements for10daily differences | 0 |
| Candidate rows lacking positive next-session Open | 0 |
| Dates with3 /4eligible monthly identities | 300 /960 |
| Missing lifecycle dates across66files | 0 |

These are data observations, not fill quality, official equality, strategy results or economic verification. The full raw66file set has270nonpositiveOpen observations and241High<Low observations, all outside the audited eligible15–93TTS range. They remain unaltered. The four invalid-row CSV reports are present even when empty.

Owned spot includes every ordinary CFE design date but has **no2018-12-05 VIX index observation**. It includes five2022US cash-holiday dates that have no VX daily-settlement row: May30, Jun20, Jul4, Sep5, Nov24. Use the explicit VX session/mark calendar; do not silently forward-fill these joins. The missing spot is a source-availability issue, while actual VX marks exist on the shortened2018-12-05session. A frozen adaptation can forbid a fresh spot-based decision that day, preserve pending orders/held marks, and state the treatment explicitly; this agent did not choose or test an economic protocol.

## Primary clock/calendar evidence

- [Cboe C2020101500](https://cdn.cboe.com/resources/release_notes/2020/Update-Adjustment-of-Daily-Marking-and-Settlement-Price-Ref-Time-for-Prop-Index-Prods-.pdf), directly read: effective2020-10-26 VX/VXM daily-settlement reference moved15:15CT to15:00CT, noon on early closes. Confirmed prices disseminate after Trade Desk confirmation, generally before15:15. Non-TAS trading hours did not change. A settlement is not known at the beginning of its calculation interval; align signal/fill clocks or use a later session.
- [Cboe2018-12-05 mourning schedule](https://cdn.cboe.com/resources/schedule_update/2018/Cboe-to-Observe-National-Day-of-Mourning-on-Wednesday-December-5-2018.pdf): nonexpiring VX traded17:00CT Tuesday to08:30CT Wednesday, with daily settlement at08:30CT. RTH was closed. Therefore a generic NYSE/full-session calendar would wrongly omit a real VX mark and alter TTS. Nine monthly records exist that day.
- [Cboe March2019 expiry reminder](https://cdn.cboe.com/resources/product_update/2019/Reminder-CFE-VX-Mar-19-SetDate.pdf) confirms Tuesday2019-03-19 because Good Friday affects the following month's option expiry. The archive includes this date and Tuesday2022-03-15. [Contract specifications](https://www.cboe.com/tradable_products/vix/vix_futures/specifications) explain the30-days-before-third-Friday rule and holiday adjustment; reconcile all filenames before certifying source exactness.
- [Official2020futures calendar](https://cdn.cboe.com/resources/aboutcboe/Cboe2020FUTURESCalendar.pdf) is an additional primary calendar source; no manual reinterpretation of its graphic dates was used in the metadata audit.

## Official acquisition attempts and rights

[CFE history](https://www.cboe.com/markets/us/futures/market-statistics/historical-data/futures/) advertises2013–current detail and VX+VXT including TAS. Post2013official dated files follow `https://cdn.cboe.com/data/us/futures/market_statistics/historical_data/VX/VX_{expiry-date}.csv`, as corroborated by inspected [downloader source](https://github.com/dougransom/vix_utils/blob/main/src/vix_utils/download_vix_futures.py), blob `45f7ae3ec7aca055cf58a9474633a5f8c3f84525`. Its code/schema evidence is secondary, not an official payload.

[VIX history](https://www.cboe.com/tradable-products/vix/vix-historical-data) advertises spot1990–present; its CSV currently redirects to `https://cdn-api.cboe.com/api/global/us_indices/daily_prices/VIX_History.csv`. Attempts through the web tool at this CSV, VX2022-06-01sample and [final-settlement archive](https://cdn.cboe.com/resources/futures/archive/volume-and-price/CFE_FinalSettlement_Archive.csv) returned unsupported text/csv; monthly2018-01-17and2022-12-21 samples were inaccessible through that tool. Cboe domains are absent from shell network policy, so no shell Cboe fetch or access bypass was attempted. Ordinary archival GitHub acquisition above succeeded separately.

[Cboe terms](https://www.cboe.com/terms) discuss personal noncommercial downloads with notices; [use-of-content](https://www.cboe.com/use-of-content) describes broader approval/licensing. Public download availability and an unlicensed thirdparty GitHub copy do not establish unrestricted redistribution rights. Keep raw research inputs scratch-only, attribution explicit, and provenance limitations attached to any future results. This is an availability/provenance record, not a legal conclusion or an automatic reason to abandon authorized personal research.
