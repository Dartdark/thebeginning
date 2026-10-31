# ES free-source triage — 2026-10-31

Bounded source and schema review only; zero candidate return tests.

## Result

A public archive has the full quarterly ES file-name chain for 2018–22 plus ESH2023, and actual bounded samples were retrieved. It does not establish a usable native daily-settlement chain: the files contain intraday OHLC with tick volume/volume/spread, no settlement column; timezone, vendor, session convention, and data-use rights are unspecified. Do not silently treat intraday closes or any continuous ES series as official dated daily settlements.

## Public dated archive actually checked

Repository: https://github.com/yakki-minati/US.Index.Futures.Data
Frozen commit/ref: 180fb127d0249827d415a3f5d298006a08ff7a31
README: https://github.com/yakki-minati/US.Index.Futures.Data/blob/180fb127d0249827d415a3f5d298006a08ff7a31/README.md
README says individual ES/NQ/YM contracts 2017–March2024. No vendor/source or license file observed in the complete recursive tree. Tree has all H/M/U/Z yearly ES contract files2018–22 and ESH2023, each approximately7–8.5MB.

Actual GET Range samples, HTTP206:
- https://raw.githubusercontent.com/yakki-minati/US.Index.Futures.Data/180fb127d0249827d415a3f5d298006a08ff7a31/ES/ESH2018.csv
  File size7474897bytes; Git blob a1ddd89703aa3dab2083bf5226777f0b36006d63.
  First timestamp2017.09.17 21:30:00; last2018.03.16 13:30:00.
- https://raw.githubusercontent.com/yakki-minati/US.Index.Futures.Data/180fb127d0249827d415a3f5d298006a08ff7a31/ES/ESZ2022.csv
  File size7831549bytes; Git blob2b968da7491d0170e985eeee35b6a036da6cc07a.
  First timestamp2022.03.20 22:00:00; last2022.12.16 14:29:00.

Tab-separated header:
<DATE> <TIME> <OPEN> <HIGH> <LOW> <CLOSE> <TICKVOL> <VOL> <SPREAD>

These resemble MetaTrader export fields. That resemblance is an inference, not provenance verification. ESH2018 early samples have VOL0 and large SPREAD values, so native volume/quote quality cannot be assumed. Only head/tail ranges were sampled; no complete-chain coverage audit, session aggregation, or returns were computed.

## Official CME check

https://www.cmegroup.com/market-data/daily-settlements.html
The official page explains daily marks and sends historical daily/final data to CME DataMine.

https://www.cmegroup.com/market-data/daily-bulletin.html
The public bulletin is previous trade date; historical bulletin link resolves to https://datamine.new.cmegroup.com/catalog?category=F001 (no readable rows in web tool). Current publication clocks: preliminary approximately00:00CT nextbusinessday, final10:00CT.

Attempted official historical URL:
https://www.cmegroup.com/CmeWS/mvc/Settlements/Futures/Settlements/138/FUT?tradeDate=01/02/2018&pageSize=500&isProtected=false
Result: inaccessible via web tool. No login, purchase, or access-control bypass attempted. Shell CME domains are outside current policy.

## Other screened paths

https://www.historicalfuturesdata.com/docs
Full CME daily history requires a free account; daily bars are expressly built from adjusted continuous ticks, while per-contract tick data is in paid access. No account created; unsuitable as an exact dated-settlement replacement.

https://finzdata.com/futures/es
Advertises88individualEScontracts2007+ with OHLCV/OI. Full history costs19USD and requireskey; freeperiodlast12months. No purchase or login.

https://github.com/stefan-jansen/machine-learning-for-trading/blob/main/data/futures/README.md
Individual ES download requires Databento API key, not a hosted public raw panel; inspected loader only. No key inspected or used.

https://github.com/carpethooligan/pa-sampledata/tree/master/data/ES
Only partial2022samples with root ES filenames; dated contract identity not established, unsuitable for complete2018–22chain.

## What remains needed

Official daily dated settlements or explicitly sourced daily OHLC at the strategy's historical decision/execution clocks; verified timezone/session labels and early-close handling; selected-contract roll rule and both legs' prices on roll date; full2018–22session census; provenance and applicable use rights. The raw public archive is a potential input lead, not a resolved data gate.

## Frozen commit and exact inventory

Commit: 180fb127d0249827d415a3f5d298006a08ff7a31 (2024-06-01T10:12:38Z).
Root Git tree: b2d6994c46b55595ed3a731653381a61dfc002df.

| File | Bytes | Git blob |
| --- | ---: | --- |
| ES/ESH2018.csv | 7474897 | a1ddd89703aa3dab2083bf5226777f0b36006d63 |
| ES/ESH2019.csv | 7460879 | bbbcef9cb00fb20b7d938ec781f48baf663837f1 |
| ES/ESH2020.csv | 7565113 | 1e4837d096ddc0cd49617ff9683376afb647a1ff |
| ES/ESH2021.csv | 7451033 | 963f7dd446eb6739a43aed4af0a48a91ebd942e0 |
| ES/ESH2022.csv | 7689867 | 5065447436f71a26542883af915165f7135a2441 |
| ES/ESH2023.csv | 7687115 | 3c93b42830154c1e3dfd36cd49001110fedb3f4f |
| ES/ESM2018.csv | 8159197 | 71a17dc9960628306210d2405f84dcc58eb7fa22 |
| ES/ESM2019.csv | 8100393 | 43b9f0d98ed0393156d62dff4014053c7567c749 |
| ES/ESM2020.csv | 8082564 | 7e061fc75cbd342fa00e5c3c04c7134415fea5e5 |
| ES/ESM2021.csv | 7494145 | 4523151be0f1f8cac0ff2a41f51a47b54e9fe30c |
| ES/ESM2022.csv | 8086803 | 4b749ac0fa582b5a305ba22ae66b9c7aac9195e4 |
| ES/ESU2018.csv | 7214455 | 1ec73e0e7eebcc445a037229c173c70dd92246bb |
| ES/ESU2019.csv | 7927928 | d19d4e878090eaaad688b1cdaef763bdd889e848 |
| ES/ESU2020.csv | 8521192 | a6855dc72ec39f4ff9c86a9a8819cea23fe52133 |
| ES/ESU2021.csv | 7421284 | 3df3cd05196090b7fe8d3dead088b904e0c25e92 |
| ES/ESU2022.csv | 8270687 | aed859d611a9b39253177c370e3504fe8309f622 |
| ES/ESZ2018.csv | 7625044 | dcf515bd31a2101d7a0721ef579d97629f9d5d92 |
| ES/ESZ2019.csv | 7947572 | c2209d7d5a74367edf2fdb382f8a9b2c4823175f |
| ES/ESZ2020.csv | 7988772 | 0f59561822857bba240c6edc71e33e333e3b096e |
| ES/ESZ2021.csv | 7469134 | 2bdee50bafe20d995c7026997a367d5b10b2b767 |
| ES/ESZ2022.csv | 7831549 | 2b968da7491d0170e985eeee35b6a036da6cc07a |

Combined listed file size: 163469623bytes. No full files downloaded; only1501-byte head/tail HTTP ranges per sampled file. Contract identity occurs in filenames only; sampled native rows have no contract column. Datetime separates DATE and TIME without timezone offset. No session/vendor/timezone claim beyond the README description was found.


