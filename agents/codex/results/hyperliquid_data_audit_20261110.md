Author/origin: **dot**. Original bounded audit; published on codex/work November 10, 2026. Code path naming does not imply independent Codex authorship.

Publication note: raw JSON responses, matched observations and summary remain local at the output path below and are not included in Git because redistribution rights remain unresolved. Request/receipt metadata and raw hashes are retained in ../inputs/dot_trading_20261110/hyperliquid_receipts.json. A fresh clone cannot exactly reproduce the capture without those original local files. The original script can make new network requests when caches are missing; new captures are not immutable replay. No rerun was performed for publication.

# D32 Hyperliquid BTC funding data audit: PARTIAL ACQUISITION / NO TEST

Summary: The free public API supplied usable final BTC funding records and a matched one-day perpetual-price sample.
The 24 hourly events on 2026-11-08 have no duplicate timestamps or missing hourly bins; all match prior-minute candles.
History starts in the returned page on 2023-05-12, with an 8-hour to 1-hour cadence change on 2023-06-08; 2018-22 returned empty.
Archived pre-event forecasts, payment-time oracle prices, historical receipt clocks and executable hedge paths remain missing.
D32 stays NEEDS DATA; zero return tests, hypotheses or definitions added, and scout/lab pauses remain unchanged.

## Identity and reproduction

Task: bounded data feasibility audit requested 2026-11-10; not a strategy test or scout restart. Starting local research HEAD: `eebf2ceae1825e74e0014fedf95488cd3e4bf59a`, branch `codex/work`, desktop `DESKTOP-B5174BE`, checkout `C:\CodexRepo`. Local top-level brief is stale relative to the November 8 handoff; no operational state is inferred from it. `lab/STOP` is absent in this checkout, which does not lift the explicit pause.

Script: `analysis/codex_hyperliquid_data_audit.py`. Run from repository root: `python analysis/codex_hyperliquid_data_audit.py`. Python standard library only, tested with Python 3.7. The script reuses existing raw responses, so rerunning reproduces the captured audit rather than silently replacing snapshots. The initial acquisition was nine bounded public POST requests, plus one prior exploratory request of the same one-day funding sample. No authentication, user addresses, accounts, private keys or exchange/order endpoint was used.

Outputs: `analysis/outputs/codex_hyperliquid_audit_20261110/`. `receipts.json` records each exact request, HTTP status, request and receipt UTC, byte count and SHA256 of raw bytes. Nine original response JSON files, `matched_observations.csv`, and `summary.json` are retained. Receipts span 2026-11-10 05:25:32-05:25:36 UTC. No rate/price returns, t-statistics, forecasts of profit or account simulations were computed.

## Acquired observations

| Probe | Returned rows | Coverage / interpretation |
|---|---:|---|
| 2018-01-01 through 2023-01-01 | 0 | No existing design-era panel from this endpoint |
| 2023 full-year request | 500 | First returned 2023-05-12 00:00:00.048 UTC, last 2023-06-25 10:00:00.201 UTC; capped first page, not a complete year |
| 2024-01-01 | 24 | One UTC day only |
| 2025-01-01 | 24 | One UTC day only |
| 2026-01-01 | 24 | One UTC day only |
| 2026-11-08 | 24 | Complete observed UTC hourly bins; timestamps 1-70 ms after nominal hour |
| Recent BTC 1-minute candles | 1,444 | Nov 7 23:58 through Nov 9 00:01 UTC; no duplicate starts or missing minutes |
| Current predicted funding and asset context | One snapshot each | Forecast and current oracle/mark/OI, not historical vintages |

The initial historical page has 81 consecutive approximately eight-hour gaps followed by 418 approximately one-hour gaps. At 2023-06-08 00:00:00.254 UTC rate is `0.0001`; the next row at 01:00:00.054 is `0.0000125`. A uniform-hour parser would falsely classify 567 earlier hourly bins as missing. Preserve native settlement intervals and schema eras. Do not divide every row by eight or annualize early records as hourly. This is directly observed API behavior; historical rule documentation and complete-page reconciliation remain separate requirements.

## Units, settlement versus forecast, payment entitlement

For the recent sample, `fundingRate=0.0000125` is a dimensionless fraction per hourly payment: 0.00125 percent or 0.125 basis points. All 24 recent rows have that rate; a single day of constant rates establishes no economic edge. Positive rates debit longs and credit shorts. The payment uses position quantity times payment-time oracle price times rate, rather than mark price. The five-second premium observations feed the hourly calculation. [Funding specification](https://hyperliquid.gitbook.io/hyperliquid-docs/trading/funding).

The native BTC contract is linear, one unit of the underlying, USDC-margined with the usual crypto oracle denominated in USDT, without an automatic USDC/USDT conversion. A USD-labelled Coinbase spot bar is therefore not an exact oracle or settlement-currency substitute. [Contract specifications](https://hyperliquid.gitbook.io/hyperliquid-docs/trading/contract-specifications).

`fundingHistory` returns historical funding, whereas `predictedFundings` supplies current predictions with next payment times. Our BTC prediction includes an explicit `fundingIntervalHours` of 1 for HlPerp and 8 for the two other venues; raw rates across venues are not directly comparable. Neither endpoint establishes historical pre-payment forecast vintages. The returned historical fields are only coin, fundingRate, premium and time; they do not supply publication or revision times. [Perpetual endpoint specification](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/info-endpoint/perpetuals).

A position must be eligible at the settlement event to receive/pay funding. Candle proximity alone does not establish the order of fill, position update and funding within that block. No account ledger was queried. A real payment reconciliation still needs eligible signed position, exact oracle and cash debit/credit. The timestamp milliseconds are observed event offsets, NOT measured publication latency.

## Matched prices and information clocks

All 24 events have a preceding completed perpetual candle. For the first event (00:00:00.070 UTC), the previous candle ends at 23:59:59.999 and closes at 75,850; the next minute opens at 75,851 and closes at 75,827. These are observations, not executable bid/ask fills. The event-minute close is future information relative to settlement. No return was calculated from these prices.

The matched CSV deliberately leaves `available_at_historical` and `oracle_at_payment` empty. The receipt in our manifest is when this historical response was obtained today, not when a trader could originally know it. Contemporary oracle and mark from today's snapshot cannot fill historical oracle gaps. A conservative later-research contract would keep event_time, source publication, local receipt, nextFundingTime, decision and earliest executable fill separate; unknown original availability must remain unknown, not assigned the settlement timestamp.

The API provides only the latest 5,000 candles per interval, and time-range endpoints cap responses at 500 elements. A one-minute API backfill therefore does not supply years of aligned price history; pagination requires timestamp overlap handling and deduplication. [Info endpoint](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/info-endpoint).

## Owned holdings and remaining source gaps

Local data includes `BTC_1min_2018.csv` through 2026 and `BTCUSD_spot_1min_2018.csv` through 2026, plus `ETHUSDT_perp_30m.csv`. BTC and spot headers are date,time,open,high,low,close,volume. ETH has timestamp/OHLC/volume, not funding. A scoped filename inventory found no pre-existing Hyperliquid/funding file; this is not a global absence proof. The existing D32 source gate identifies continuous CME BTC and Coinbase spot, not matched Hyperliquid prices or a dated expiring CME contract.

The local 2026 CME file ends October 13 05:24 and spot file October 23 19:00 in their unverified local label convention. Neither reaches this November 8 sample. Do not relabel these clocks as UTC or claim the new sample is matched to CME/spot. Historical overlap may exist for earlier dates, but timezone, native instrument, rolls, executable hedge prices and settlement-currency basis still need audit. CME expiry-basis D32 is untouched.

Official bulk archives include historical contexts/books but are requester-pays, may have missing data and are not guaranteed timely. They were not accessed because the task is free-only. [Historical data](https://hyperliquid.gitbook.io/hyperliquid-docs/historical-data). The public documentation establishes an accessible read API, not an unrestricted redistribution license. The [official interface terms](https://app.hyperliquid.xyz/terms) were attempted but yielded no readable text in the source tool. No license grant or jurisdictional trading eligibility is certified; retain the sample in this private project, and check terms before redistribution or any trading integration. No paid archive, new vendor contact, signup or terms acceptance occurred.

## Disposition and smallest next check

D32 advances from documentation-only to a reproducible partial final-rate/price acquisition. It does NOT advance to TEST. Before a pre-payment hypothesis: obtain an authorized free archived forecast/context sample with authentic observation/receipt timestamps and matched payment oracle, audit historical rule eras and reconcile one signed position/payment independently. Without that, a lagged-final-rate design is a different hypothesis requiring its own evidence and preregistration, not a repair of the original missing input. No such design is registered here.

Even a complete funding ledger would not prove directional pressure in CME or diversification from VB/ONB. Carry can coexist with price, basis, collateral and venue losses. New strategy returns, allocation, promotion, schedule changes and live/VPS/broker changes remain outside this audit.
