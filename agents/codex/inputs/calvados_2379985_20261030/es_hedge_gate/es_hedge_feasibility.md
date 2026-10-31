# Calvados ES hedge: bounded no-return feasibility follow-up

2026-10-31. Scope: actual dated ES hedge inputs and roll-map availability only. Naked-design failure stands. No hedge signals, fitted hedge, candidate returns or new economic test were calculated.

**Result: public dated ES OHLC inputs found; exact-source hedge remains unverified.** Owned ES minute histories lack contract identities. A public archive lists the full2018–22quarterly ES chain plusESH2023, and three complete files were retrieved and audited for metadata. They supply potentially useful dated prices and overlapping contract intervals. They do not identify a vendor/timezone, contain official settlement marks, or establish exchange-native volume. A separately frozen intraday-price adaptation is possible in principle after resolving those inputs/protocols; no hedge economic test was run.

## Owned data examined first

`/workspace/thebeginning/data/ES_1min_2017.csv` through`ES_1min_2022.csv` were read only for file/header/row/date metadata. Both current Git trees inspected (`origin/codex/work` and cached latest Claude`a01be1b`) list these year files, with no dated ES/MES contract files or ES roll ledger. Workspace filename inventory found no additional dated ESH/M/U/Z2018–22price chain.

All six headers are`date,time,open,high,low,close,volume`: **no contract/symbol ID, expiry, settlement, roll flag, adjustment factor or old/new contract pair**. Detailed byte counts, SHA256s and first/last labels are in`owned_es_metadata.json`.2018–22row counts are346940/349251/348715/353073/353752. Repository briefing expressly describes its continuous contracts as unadjusted. A roll calendar inferred from a price jump would not establish both leg prices, trade-date conventions or executable roll cashflows; no such inference was made.

These owned bars remain useful for a separately labelled continuous-price hedge adaptation, but do not meet this task's exact dated-contract gate. No proxy return was run.

## Actual public/GitHub reads and rejected inputs

1. [bgithub1/volgrid cash/futures ES CSV](https://github.com/bgithub1/volgrid/blob/bec1dad61be58036c1f778fc1c2d20e5fa314572/volgrid/df_cash_futures_ES.csv) was successfully fetched through the connected GitHub tool. Pinned commit`bec1dad61be58036c1f778fc1c2d20e5fa314572`, blob`96cc7a154845bd8c2ed6ef558ed1aca595dd9105`. It has2741rows2010-09-01–2021-07-26, header`symbol,settle_date,contract_num,open,high,low,close,adj_close,volume,open_interest`. Every symbol is`ESZ99`; contract_num values6/7/13/14 do not supply actual dated-contract identities.897rowsfall2018–22and2022is absent. Not admitted as a dated2018–22chain.
2. [ettiennehugo/MultiCharts.Net roll calendar](https://github.com/ettiennehugo/MultiCharts.Net/blob/98136a356c2e31ee009f6ec4d41aae10cb6447b2/tools/m-event/out/roll_splices_2016_2024.csv) was successfully fetched. Pinned commit`98136a356c2e31ee009f6ec4d41aae10cb6447b2`, blob`1605cd575d24454d3ac19ea8dc1e01da46754c66`. It lists actual quarterly contract IDs/expiry/rule-roll dates2016–24, but **all observed_splice and offset_sessions fields are blank**. It is a secondary calendar template, not the owned export's verified roll map or paired roll prices. Its changing roll convention (Thursday before expiry throughMarch2022; Monday expiry week afterward) also requires source attribution rather than automatic adoption.
3. Recursive GitHub trees for those two pinned repositories were successfully fetched. Their visible data artifacts did not supply a complete matched dated ES daily chain. Other global GitHub searches(`ESH18 ESM18`, `ESH18.csv`, `ESM18.csv`, `ESH22.csv`, ES expiry names with Settle/Open/Close) returned downloader code, roll metadata, unrelated text or no relevant file. Search indexing and partial-word matching are imperfect; negative search results are not proof of nonexistence.

## Missing material inputs

Need actual quarterly ES identities covering all hedge holdings2018–22plus the relevant end-of-period/warm-up contracts; dated daily opens and settlement/close marks with clocks; expiry calendars; and both old/new contract prices on a frozen roll date/time. Contract choice, hedge-rebalance interval, integer sizing, cash/variation-margin accounting and the manuscript's hedge-equation ambiguity must be frozen in a separate preregistration before any hedge economic test. Source prescription of an SPX hedge ratio does not provide historical ES roll fills.

## Actual dated archive discovered and sampled

[yakki-minati/US.Index.Futures.Data](https://github.com/yakki-minati/US.Index.Futures.Data/tree/180fb127d0249827d415a3f5d298006a08ff7a31/ES), confirmed commit`180fb127d0249827d415a3f5d298006a08ff7a31`,2024-06-01; root tree`b2d6994c46b55595ed3a731653381a61dfc002df`. [README](https://github.com/yakki-minati/US.Index.Futures.Data/blob/180fb127d0249827d415a3f5d298006a08ff7a31/README.md) says individual ES/NQ/YM contracts2017–March2024. Recursive tree lists every H/M/U/Z ES contract2018–22plusESH2023,21files163,469,623bytes. Expected per-file Git hashes/sizes/URLs are in`es_dated_inventory.json` and`es_public_notes.md`. No source vendor, timezone/bar convention, adjustment policy or explicit repository/data license was found in its README or recursive tree. Contract identity is in filenames only.

GitHub Contents reads of the large files returned empty content. Raw-GitHub HTTP206head/tail requests succeeded, followed by three bounded complete-file HTTP200reads for the following audit. Each complete sample's recomputed Git blob hash matched the frozen tree; SHA256/access records are in`es_sample_metadata.json`.

| Sample file | Rows | First naive label | Last naive label | Zero VOL rows | Invalid OHLC / duplicate timestamps |
|---|---:|---|---|---:|---:|
| ESH2018.csv |119216|2017-09-17 21:30|2018-03-16 13:30|5743|0 /0|
| ESM2018.csv |130303|2017-12-17 22:30|2018-06-15 13:30|6622|0 /0|
| ESZ2022.csv |123822|2022-03-20 22:00|2022-12-16 14:29|49|0 /0|

The actual TSV schema is`<DATE>,<TIME>,<OPEN>,<HIGH>,<LOW>,<CLOSE>,<TICKVOL>,<VOL>,<SPREAD>`. These resemble MetaTrader export fields; that is an inference, not an authenticated vendor/source attribution. All three samples have strictly increasing unique timestamps and positive, coherent OHLC; all volume fields are nonnegative. ESM2018has120zeroTICKVOLrows. Early ESH2018andESM2018dates have full days withVOL0butpositiveTICKVOL. SPREAD is frequently positive, its units unspecified. Tick volume cannot silently replace actual exchange trade volume. No settlement field is present.

Adjacent ESH2018/ESM2018intervals overlap2017-12-17through2018-03-16, so this is more useful than a renamed front-month continuous series: both contracts' price histories may be present at a chosen roll. The21-file identity chain is complete by filenames; **only three full intervals were audited**, and absence of an entire session or required clock cannot be certified across the uninspected chain. One-minute observations have many gaps; a calendar/session census must distinguish no ticks, holidays and acquisition gaps before any daily aggregation.

Timezone/bar-label evidence, kept separate from source claims: a metadata-only comparison of sampled front-contract closes to the owned CT-labelled ES export strongly favors **UTC bar-open labels, converted to CT and advanced one minute**. For Jan2–Jan9,2018,8013of8078paired close values match exactly under that hypothesis, versus3337of8004without the minute shift. For Nov1–Nov9,2022,8497of9593match versus1160of9586without the shift. Treating raw labels as CT gives only144of7309and31of8934matches. This is clock-alignment evidence, not independent timestamp provenance; the2022residuals also require explanation. Expiry tail labels13:30UTC inMarch2018and14:29UTC inDecember2022are consistent with that hypothesis. Do not silently certify a timezone, adopt quote-side prices as trades, or call these official settlements from this comparison.

The three raw samples remain scratch-only. A wider download had just begun before root's instruction to stop at three samples arrived; it was terminated promptly. Eighteen files had reached scratch by then, including the three reused samples; the additional files were not read or audited. No full-chain completeness claim follows and no raw files are copied into tracked inputs.

## Official/vendor acquisition attempts

- [CME daily settlements](https://www.cmegroup.com/market-data/daily-settlements.html), successfully read, directs historical daily/final data to CME DataMine. Actual attempted historical endpoint`https://www.cmegroup.com/CmeWS/mvc/Settlements/Futures/Settlements/138/FUT?tradeDate=01/02/2018&pageSize=500&isProtected=false` was inaccessible through the web tool. No historical rows were obtained. Shell CME domains are outside current policy; no bypass attempted.
- [CME daily bulletin](https://www.cmegroup.com/market-data/daily-bulletin.html), successfully read, supplies previous trade date and links historical bulletins to`https://datamine.new.cmegroup.com/catalog?category=F001`; that catalog yielded no readable historical rows. The current bulletin publication clocks do not establish2018–22availability or executable fills.
- [HistoricalFuturesData docs](https://www.historicalfuturesdata.com/docs), read: full daily access requires a free account and the daily bars are adjusted continuous; per-contract ticks are paid. No account created; this does not fill the dated-contract gate.
- [FinzData ES](https://finzdata.com/futures/es), read: advertises88individual contracts2007+, but full history costs$19andrequiresakey; free last12months does not cover2018–22. No purchase or key use.
- [stefan-jansen futures loader](https://github.com/stefan-jansen/machine-learning-for-trading/blob/main/data/futures/README.md), read: individual-contract download needs a Databento key; no hosted free raw panel established. [carpethooligan sample directory](https://github.com/carpethooligan/pa-sampledata/tree/master/data/ES) contains partial2022root-ES samples, not a complete dated2018–22chain.

## Concrete gate conclusion

**Usable now for further metadata inspection:** individual-contract-labelled OHLC files, verified raw access for three complete examples, months of roll overlap, a complete advertised quarterly filename set, and strong evidence for UTC start labels. These are more concrete inputs than the owned continuous export. Raw paths/sample hashes and coverage/volume reports are preserved for root to inspect.

**Still required before a hedge test:** verify actual instrument/vendor/price-side and clock conventions; audit the full date/clock census and paired roll marks; obtain official settlements if exact daily-settlement reproduction is claimed, otherwise explicitly preregister an intraday-price adaptation; freeze ES contract selection, roll date/time, dynamic hedge adjustment and integer rounding. One VX often implies less than one ES hedge at small capital: fractional ES, silently scaling capital, or backfilling MES would change the rule. Use actual native ES prices and multipliers; no MES substitution was made.

No purchase, registration, login, credential discovery, endpoint bypass, hedge signals/returns or raw-data redistribution was performed. The exact preferred-source hedge remains unverified; this does not imply that no free chain exists or reopen the failed naked definition.
