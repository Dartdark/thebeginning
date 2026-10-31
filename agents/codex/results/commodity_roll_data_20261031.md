# Commodity-index spread acquisition: WATCH / incomplete test inputs

Summary: Historical roll documentation and actual free multi-maturity wheat files were obtained/read.
The standard-wheat file selects December contracts, not the nearby pair required by the hypothesis.
Mini-wheat follows delivery months but has missing prices and uncertified clock/native-contract coverage.
No complete free 2018–22 test panel has been admitted; zero returns computed.
Use the saved source leads and request/export exact dated contracts before a preregistered screen.

Plan: metadata acquisition only. Script: `analysis/codex_commodity_roll_acquisition_20261031.py`.
Output: `analysis/outputs/codex_commodity_roll_acquisition_20261031/metadata.json`. New economic trials: zero.

## Acquired inputs and what they establish

Source repository: [pysystemtrade](https://github.com/pst-group/pysystemtrade), pinned commit
`164328bd76d2937d3dd61491377704c488283bc2`. Read its complete recursive tree, data documentation and roll
configuration; downloaded actual WHEAT and WHEAT_mini multiple-price CSVs, documentation and roll configuration.
Raw files remain `/workspace/commodity_roll_data/`, with URLs and hashes in committed input receipts.
These contain PRICE/CARRY/FORWARD prices and their actual maturity identifiers, a material improvement over a
single continuous series. They do not contain every dated contract's full history.

- Standard WHEAT: price maturity in design is December, with September carry and later December forward.
  Configuration explicitly selects annual December holdings. This cannot silently become the required nearby
  wheat spread merely because the file has multiple prices. CORN and winter CRUDE_W similarly select December.
- WHEAT_mini: configuration follows March/May/July/September/December. Actual files have missing prices and
  mixed intraday/end-of-day-labelled observations; vendor/clock conventions, genuine mini-versus-standard history,
  authoritative session census and paired executable marks remain unverified. A mini contract cannot silently
  inherit standard-contract fills, fees or liquidity. Counts of any paired observation do not establish full paths.
- Neither dataset was used to compute spreads, changes or returns. No missing price was filled or substituted.

## Roll documentation found

Read [February2018 S&P methodology, hosted by Daishin](https://etn.daishin.com/e5_data/mboard/etn_product/2018/06/9_00_methodology-sp-gsci-2x-zinc.pdf),
the [December2018 GSG prospectus](https://www.sec.gov/Archives/edgar/data/1332174/000143774918022622/gsg20181226_424b3.htm),
and [current S&P methodology](https://www.spglobal.com/spdji/en/documents/methodologies/methodology-sp-gsci.pdf).
The prospectus describes the standard fifth-through-ninth-business-day roll, 20% per day at reference settlements.
That documents a mandate; it does not establish net price pressure or a historical fill. Standard, enhanced and
pre-roll indices use different contracts/calendars, so do not mix them or apply the current PDF retrospectively.
Full2018–22 methodology/exception/calendar vintage coverage is not certified from these documents alone.

## Other actual access attempts

| Source | Actual result | Why it does not complete our input gate |
|---|---|---|
| [TurtleTrader archive](https://www.turtletrader.com/hpd/) | Read download page; attempted wheat ZIP, web tool rejects binary ZIP | Not an acquired modern panel; archive is not updated |
| [TFSMAG dataset](https://huggingface.co/datasets/Viharikvs/TFSMAG/blob/main/README.md) | Read schema/coverage; tree API and first-rows API inaccessible | Deep spreads end2004; modern spreads advertised2021–26; full design missing, no raw panel obtained |
| [HistoricalFuturesData](https://www.historicalfuturesdata.com/docs) | Read schema, tiers and wheat listings | Daily bars are adjusted continuous; per-contract ticks are distinct paid files; latest-month sample does not fill2018–22 |
| [FinzData](https://finzdata.com/datasets) | Read actual current coverage/tier page; wheat product URL inaccessible | Dated historical bars advertised behind paid/key access; free recent sample is not full history |
| [Portara wheat](https://portaracqg.com/futures/day/wha/) | Read individual/continuous options and delivery details | Full dated history sold; not downloaded or purchased |
| GitHub searches | WHEAT contract-price loader and docs found; exact ZWH2018 search mostly unrelated | Loader code and repository search hits are not a dated panel; successful multiple-price download audited separately above |

Some search snippets and vendor pages disagree about free coverage/prices; actual entitlement and delivery contents
must be checked before spending. No purchase, account creation, credential access or network-policy bypass occurred.
The permitted web connector read public documents; blocked binary/API calls were recorded, not rerouted.

## Smallest justified next steps

For the exact source-market test, obtain unadjusted individual CBOT ZW contracts for2018 onward, with both
members of each index roll present on the same dates. Need complete dated prices, actual session/settlement clocks,
volume/OI, expiry/delivery metadata and use rights; hourly/one-minute or listed-spread quotes improve fill checks.
An export through the user's existing historical feed might avoid a new purchase, but feed entitlement and depth
have not been verified here. Otherwise require a paired-contract sample from a vendor before buying history.

The public mini-wheat files are retained as a separate possible metadata lead, not an admitted strategy adaptation.
Resolve its identity, session/missingness and historical price source before any separately frozen mini protocol.
Do not choose contracts or change the source strategy to fit whichever prices happen to exist.

After the source/date/clock gate passes: complete evidence, commit one bounded protocol and code, cheap2018–22
gross-versus-cost screen, then only earned later validation and personal BASE/ADD/REPLACE/EMPTY comparisons.
Multiday source holdings still do not fit the four Apex homes. No profitability, diversification or account gain is established.
