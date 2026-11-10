# dot: free-input acquisition, partial data gates closed
Author: dot. 2026-11-10. Data acquisition and structural validation only; no signals, returns, backtests or scout/lab changes.

## Summary
Acquired 72 advance FOMC schedule dates, a 1,007-row commodity-positioning sample and 14 EIA holiday exceptions.
These are usable source artifacts, not complete point-in-time strategy inputs.
API actuals/Bloomberg consensus, native curves, executable prices and historical release vintages remain blocked.
No purchases, accounts, external messages, live access or restricted/large raw files were put in git.

## Delivered files
All compact artifacts: [input directory](../inputs/dot_free_input_acquisition_20261110/).
- [FOMC advance schedules](../inputs/dot_free_input_acquisition_20261110/fomc_advance_schedule.csv): 72 tentative meeting-end dates across 2018–2026, eight per year, from eight dated official notices. Every row retains its notice URL and declared publication timestamp. This supplements, and does not modify, the existing scout calendar with null advance-notice fields.
- [Federal Reserve source excerpts](../inputs/dot_free_input_acquisition_20261110/fomc_source_excerpts.md): retained text from the dated notices.
- [COT commodity sample](../inputs/dot_free_input_acquisition_20261110/cot2018_commodity_sample.csv): 1,007 distinct market/date records, 19 market codes, January 2–December 31, 2018, extracted from the official 13,410-row legacy futures-only archive. Fields: market identity/code, position date, total OI, commercial long/short positions and trader counts, contract units. Codes retain leading zeros.
- [EIA current schedule snapshot](../inputs/dot_free_input_acquisition_20261110/eia_schedule_snapshot.json): 14 listed exceptions for 2025–2026, including November 12, 2026 at noon Eastern. This is a snapshot, not a historical advance calendar.
- [Source hashes and row checks](../inputs/dot_free_input_acquisition_20261110/acquisition_manifest.json).
- [Reproduction script](../inputs/dot_free_input_acquisition_20261110/build_supplement.py): Python standard library plus curl. Run from an empty scratch directory. It downloads official sources, normalizes reviewed FOMC date transcription, parses COT and EIA, and records fresh hashes. No strategy code. Raw HTML/ZIP stay local and should not be staged.

## What each acquisition actually resolves
### #53 FOMC reversal
The previous audit located advance notices but the saved event JSON did not retain their publication timestamps. The supplement now retains those fields and extends through 2026, explicitly including October 28, 2026. Schedule dates were transcribed from and checked against the official notice text. The 2025–2026 notice expressly states 14:00 Eastern statement releases; that clock field remains blank for earlier notices rather than importing later knowledge.

The 72 rows are NOT 72 completed regular announcements: March 18, 2020 is marked cancelled and December 9, 2026 future/tentative. Emergency March 3 and March 15, 2020 actions are not inserted into regular schedules. Their separate treatment remains necessary. The [March 15 official page](https://www.federalreserve.gov/monetarypolicy/fomcpresconf20200315.htm) identifies a 17:00 release.

These are current retrievals of historical dated notices, not contemporaneously captured website versions or feed receipts. The notice publication time is not the later statement time. No blanket historical release-clock admission is granted. Original-calendar revisions, cancellation timing, exact ES observations, contract continuity and execution quotes/costs remain unresolved.

### #24 COT commercial positioning
The free [2018 legacy archive](https://www.cftc.gov/files/dea/history/deacot2018.zip) is genuinely downloadable and parseable. The existing D50 register already records owned 2018–2022 legacy archives and CL/GC/NG coverage. This pass does not claim to discover a new archive: its retained 19-market extraction broadens the checked sample beyond those three markets. It is a bounded sample, not the paper's exact full universe or full history. It does not provide native maturity prices.

Current archives can contain revisions. Position dates are not release dates. The 53 position observations per market include holiday Monday observations; never assume every row is Tuesday or available three days later. The January 29, 2019 [CFTC catch-up notice](https://www.cftc.gov/PressRoom/PressReleases/7864-19) says December 24, 2018 data were expected to be released February 1, 2019, after the shutdown. This is a planned release date, not proof of receipt.

The [official exception/revision record](https://www.cftc.gov/MarketReports/CommitmentsofTraders/HistoricalSpecialAnnouncements/index.htm) also documents:
- June 15, 2021 observations delayed to June 21, 2021.
- December 21, 2020 observations published December 28, 2020.
- 2023 ION delays: originally February 3 report issued February 24; February 10 on March 3; February 17 on March 8; February 24 on March 10; March 3 on March 14; March 10 on March 16; March 17 on March 21.
- March 26 and October 15, 2019 positions corrected after their original releases.
These make naive Friday joins and revised-as-original values unsafe. Actual release vintages/times, prior-week OI treatment, broad contract matching and executable returns remain missing.

### #58 API/EIA
The EIA schedule snapshot improves holiday awareness but does not recover the historical API actuals or Bloomberg EIA consensus required by the source strategy. [API's official access page](https://www.api.org/energy-insights/statistics/wsb) limits its WSB reports to subscription distributors; normal release is approximately Tuesday 16:30 Eastern, with exceptions. No subscription or account was opened. Targeted paper/consensus searches did not yield a verified lawful free historical Bloomberg consensus panel with receipt timestamps. This is a bounded unsuccessful search, not proof none can exist.

EIA government actuals are different from market consensus. The retained current calendar cannot establish every past pre-event schedule. Do not backfill holiday events using a generic Wednesday 10:30 assumption, and do not label a price-only adaptation an exact paper replication.

### #1/#2 native commodity curves
The earlier [native-contract feasibility audit](dot_ssrn_curve_data_feasibility_20261110.md) remains controlling: no lawful free comprehensive native maturity panel was established. This pass did not repeat paid-provider discovery or scrape restricted CME pages. COT is positioning, not a substitute curve.

## Provenance, rights and limits
Federal Reserve data/text: [public-domain policy](https://www.federalreserve.gov/disclaimer.htm), with source attribution and exceptions for third-party material. CFTC: [public-domain policy](https://www.cftc.gov/WebPolicy/index.htm), with attribution. EIA: [copyright/reuse policy](https://www.eia.gov/about/copyrights_reuse.php), with attribution. No logos/photos or vendor data copied into the compact artifacts.

Raw source hashes describe bytes retrieved now. File verification timestamps are retrieval/normalization observations, not historical knowledge times. The manifest records successful public-source bytes, not invented first-release vintages.

## Handoff
Tell Claude: agents/codex/results/dot_free_input_acquisition_20261110.md.
This closes parts of acquisition feasibility only. No candidate is promoted, no modern profitability is established, and no paused research resumes.
