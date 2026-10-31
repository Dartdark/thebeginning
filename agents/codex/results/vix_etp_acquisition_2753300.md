# VIX ETP acquisition: futures restored, partial XIV found, full replay still blocked

Summary: Downloaded and hashed the pinned VX archive: 240 monthly files, 43,573 native rows, 2005–2025 observations.
Recovered a 364-row public XIV OHLCV snapshot spanning 2016-09-07–2018-02-15, including its last trading days.
Downloaded a VXX CSV, but it begins 2018-01-25 and is not admitted as the original 2009 VXX history.
The paper's vendor says its XIV open/high/low package stops August 2017; a purchase alone would not fix a next-open replay.
Full original-product/synthetic histories and causal input/fill clocks remain missing. Zero new economic trials.

User request: obtain the inputs missing from [the paper review](vix_etp_2753300.md).
Script: `analysis/codex_vix_etp_acquisition_2753300.py`.
Outputs: `analysis/outputs/codex_vix_etp_acquisition_2753300/summary.json`, `vx_file_census.csv`, `access_receipt.json`.
Raw third-party files: `/workspace/vix2753300_acquisition/`, scratch-only, not redistributed to Git.
This intake is not an economic preregistration, strategy result, source-exact certification or permission to trade.

## Acquired, not merely located

| Input | Actual acquisition | Admission limit |
|---|---|---|
| Dated monthly VX | Pinned Pustak-007/ml_risk_overlay archive; 240 native CSVs, 43,573 rows | Reference archive; not yet certified for source-era units, expiry/roll identity, publication time or official-byte equality |
| XIV | 364 converted public-table OHLCV observations, 2016-09-07–2018-02-15 | Partial secondary snapshot, not full inception-to-termination panel or native exchange file |
| VXX | Pinned xjcarter/data CSV; 1,215 rows, 2018-01-25–2022-11-18 | Starts at newer-product era; does not establish original 2009-series identity/history |
| Spot VIX | Existing owned daily file | Remains available; not a futures-price or product-price substitute |

The VX archive URL is [pinned at 7a8df408](https://codeload.github.com/Pustak-007/ml_risk_overlay/zip/7a8df4089664c339de9a4c5900cecdbe9d5b954e).
Archive SHA256 is `71dc39799b8290e608b1fca8c62b55e6c58fc1d9975ad4ba41a34f42d4fe330b`.
This restores the same acquisition identified by the earlier Calvados work, plus earlier source-era files not
included in that study's selected 66-file panel. The complete raw archive contains observations from May 23,
2005 to October 1, 2025; this is a file-range statement, not proof of continuous monthly/front-contract coverage.

Metadata audit found 356 nonpositive settlement rows, 2,135 nonpositive opens and 407 high-below-low rows
across the unfiltered archive. These include illiquid/untraded portions; counts are not strategy exclusions.
Six 2013 files have a CFE disclaimer line before their real header. The parser recognizes that exact header
and preserves original bytes; it does not treat the disclaimer as a market record.
Early files contain values such as Jan-2006 Settle=134.50. Their historical scale/multiplier must be verified
against primary documentation before joining spot VIX. No guessed factor-of-ten correction or basis was calculated.

The [public XIV table](https://chartexchange.com/symbol/nasdaq-xiv/historical/) exposes observations through
February 15, 2018 and identifies the product as inactive. A converted snapshot was saved from the inspected
table portions, deduplicated by date, and hashed. It includes actual reported O/H/L/C rather than a replacement
ETP. It does not by itself establish exchange provenance, adjustment conventions, full trading-day coverage,
redemption cashflows or executable open fills. No candidate P&L was calculated from it.

The [VXX CSV at its pinned commit](https://raw.githubusercontent.com/xjcarter/data/7d705ada2d3ca483700eb695772e7de9cfc75cbc/VXX.csv)
was downloaded and date/schema audited. Its 2018 start is insufficient for original VXX/XIV source replication;
it was kept as an explicitly unadmitted candidate, not spliced onto a synthetic or renamed into the old product.

## Attempted sources and the purchase trap

- Public `systematicinvestor/SIT` was downloaded at `f9b1185036d9a97764e8c5e12f091b8338926190`: no XIV/VXX
  named data members were found; no source code was executed. The formerly referenced SIT.test was unavailable.
- Original Dropbox TXT links and ordinary share/download forms remained inaccessible through connected web.
  GitHub searches largely found loader scripts, not a verified original-product panel. No embedded example
  API credentials were used, and no blocked shell domain or alternate proxy was attempted.
- The [source vendor's OHLC documentation](https://www.sixfigureinvesting.com/2014/09/simulating-open-high-low-vxx-vixy-tvix-uvxy-xiv-svxy/)
  explicitly says **XIV open/high/low only goes through August 2017**. It also says futures opens ceased being
  synchronized with ETP opens as futures trading hours expanded, and that futures intraday extremes need not
  occur simultaneously. Thus a synthetic futures Open cannot simply become an ETP next-session Open.
- Its [closing-history offer](https://www.sixfigureinvesting.com/2013/09/backtests-for-volatility-etn-etf/) describes
  purchasable indicative backtests, including original XIV. That is not a downloaded package or confirmation of
  original market-price fields through the termination event. The inspected shop did not expose a usable current
  price/checkout quotation. No purchase, subscription, account creation or message to the vendor was made.
- The vendor separately offers free modern SVIX/UVIX simulations. Those are different product objectives and
  terms; no substitution was chosen just because the files are free.

The original review's description of the local VX scratch absence is now superseded by this actual restoration.
Its broader claim that an exact ETP replay remains blocked still holds. The new public XIV snapshot partly
closes the post-August-2017 observation gap, but does not supply the earlier original ETP panel.

## Precisely what is still needed

For the original 2006–14 historical replication: source-era synthetic indicative values, original postlaunch
XIV/VXX market prices with split/adjustment conventions, matching front-VX settlements/rolls and spot, and a
known availability/fill protocol. A later-execution adaptation is feasible in code but is not exact source replay.
For a termination-aware archived continuation: complete original XIV/VXX market O/H/L/C or an explicitly frozen
later-close protocol, issuer redemption treatment, correct adjustment eras and event clocks through February2018.
The public snapshot and the new-product VXX file do not jointly satisfy these requirements.

Current-product substitution would require its own product specification; no perpetual XIV, SVXY or short-VIXY
adaptation is implicitly admitted. The 240-file archive is reference material, not a finished continuous front
contract series. No same-close fill uses after-close information, and no economic gate was weakened.

This is a completed partial acquisition with a reproducible census. No new returns, plan benches, tier changes,
live actions or independent-verification claims. The next useful evidence is a complete matching original-product
panel or a vendor-confirmed exact field/date package; an unverified purchase is not yet a concrete solution.
