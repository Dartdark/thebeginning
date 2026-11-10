# Gold crowding source and clock admission

User authorized implementation/testing November 9, 2026 Pacific. No economic outcomes inspected at this checkpoint.

## Acquisition and identity

Official free binary URL attempted: https://www.cftc.gov/files/dea/history/fut_disagg_txt_2018.zip .
Default sandbox curl could not reach its inherited proxy; approved retry returned HTTP 403. This is an access
failure, not an automatic-approval rejection. Official HTML is accessible through the connected web tool.

Free mirror inspected at commit `69e9c4e7268906e711f594adf17eb4066819ae89`:
https://github.com/tsingshuizhang/gold-cot-tracker . Only the design-period positioning slice is retained here;
the mirror's price histories, indicators, claims and executable code are not research inputs. Its normalizer and
fetch code were read statically: gold code 088691, Disaggregated futures-only annual ZIP fallback, Managed Money
long/short/spreading and OI. Its simplified release calendar is NOT imported. The mirror omits original row-level
receipts and contract identity, so source identity needs independent reconciliation. Hashes are in acquisition_manifest.json.

Official sampled source, code 088691, futures-only, 100 troy ounces:
https://www.cftc.gov/sites/default/files/files/dea/cotarchives/2018/futures/other_lf071718.htm .
Gold July 17, 2018: OI 528278; Managed Money long 107775, short 134224, spreading 51880; all match the mirror.
These are source cells, not strategy performance. Full overlapping OI/date reconciliation against owned Legacy
ZIPs is performed by the data script; equality of OI is not a check of every Managed Money cell or original vintage.

## Official publication and correction evidence

- Normal convention, Tuesday positions released Friday 15:30 Eastern:
  https://www.cftc.gov/MarketReports/CommitmentsofTraders/index.htm .
- Historical exceptions/corrections:
  https://www.cftc.gov/MarketReports/CommitmentsofTraders/HistoricalSpecialAnnouncements/index.htm .
  June 15, 2021 report moved from June 18 to June 21. December 21, 2020 observations were released December 28.
  Tuesday holidays can cause Monday observations. April 3, 2019 notice explicitly includes gold code 088691
  among March 26, 2019 observations corrected after their March 29 publication.
- January 29, 2019 shutdown recovery notice:
  https://www.cftc.gov/PressRoom/PressReleases/7864-19 . Last report December 21, 2018; December 24 positions
  expected February 1, 2019, then twice-weekly catch-up. This is a planned schedule, not all actual receipts.

## Conservative research subset, fixed before opportunity counts

Use only Tuesday observations from weeks without a US federal holiday or Good Friday; also omit the December 5,
2018 national-mourning week. Omit observations December 24, 2018 through March 26, 2019 inclusive. Omit that last
gold report permanently, including ranking history, to avoid its known revision. Exclude trading December 22, 2018
through March 31, 2019 inclusive. The deliberately wider blackout avoids fabricating catch-up receipts.

For remaining reports use documented ordinary Friday 15:30 Eastern publication plus a one-hour processing buffer;
first use is the next eligible US morning. Require observation age at most 14 calendar days. Omitted reports never
enter the rank, and missing releases do not become zero positions. Rank each new report against the last 52 eligible
earlier published reports, never against future observations or a full-history distribution. This is an intentionally
reduced published-state test, not reconstruction of every report that investors could have used.

The current mirror is not an original-vintage archive. Known affected gold rows are excluded, one official row and
all overlapping OI values can be reconciled; undetected revisions remain a limitation. This admits at most a
conditional historical falsification screen. A passing result would still require wider original-report/vintage,
contract/roll and native MGC quote/fee review; it cannot be promoted or called independently verified from this panel.

The census inspects 2017–22 owned GC bars only for available inputs, predecision breaks and planned-path missingness.
No forward return, trade P&L, stopped outcome or 2023+ GC prices is computed during that stage.
