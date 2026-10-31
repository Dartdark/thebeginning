# FOMC VX data acquisition — blocked pending access

Checked 2026-10-31 for the user's request to obtain the data needed by SSRN2544445.
**No matching raw data acquired; no return test run.** Availability and prices below are provider claims, not validation of delivered coverage or quality.

## Actual access results

- Existing repository inputs provide daily VX/index/ETF data, not the required dated intraday contract panel. See [original data gate](../inputs/fomc_vx_2544445/data_gate.md).
- Connected web reader could inspect provider pages but rejected the FirstRate/Cboe binary ZIP sample formats. A separate shell download of `https://frd001.s3.us-east-2.amazonaws.com/frd_sample_futures_VX.zip` with normal environment proxy failed with HTTP403. A diagnostic HEAD returned `CONNECT tunnel failed, response 403` from the environment proxy before a vendor response. No sample bytes acquired. No proxy bypass attempted.
- Public/GitHub searches found daily collections and downloaders, not a verified free full-history intraday panel. Plugin searches for historical futures providers found no relevant connected provider.
- [Public third-party evaluation sample](https://huggingface.co/datasets/lynx1231/historical-futures-data-sample/tree/main), inspected through its README, source notice and file catalogue: VX minute contracts VXX25, VXZ25, VXF26, VXG26 and VXH26, with minute coverage starting in2025. This cannot supply2010–14 replication or2018–22 design. No Parquet payload downloaded. Its README describes Chicago wall-clock milliseconds rather than true UTC and no exact expiry metadata; catalogue coverage alone would not admit it.

## Available paid paths, not purchased

| Provider | Advertised offer inspected | Material qualification |
|---|---|---|
| [FinzData shop](https://finzdata.com/shop) / [futures catalogue](https://finzdata.com/futures-data) | US$49 for one futures market, full history, individual contracts plus continuous, all bar sizes including1minute; catalogue lists VX from2008 | Cheapest located listing, not a verified dataset. Optional daily updates US$19.95/month are added by default and can be removed before checkout. Free tier is only30days of daily futures. Provider documents Eastern local time/DST and start-of-bar labels. No quotes/ticks included in this bar product. |
| [Portara pricing](https://portaracqg.com/pricing/) / [VX product](https://portaracqg.com/futures/int/vx/) | US$220 special (usual$330) per commodity, full-history individual1minute **or** continuous1minute, formatting included; VX product advertises history from2004 | Pricing now inspected on the actual pricing page, superseding the earlier search-snippet-only status. Choose individual contracts. Delivery advertised by FTP; no final order, file or coverage validation. |
| [Cboe current trades](https://datashop.cboe.com/cfe-futures-trades) / [legacy trades and quotes](https://datashop.cboe.com/cfe-vix-volatility-index-futures-trades-quotes) | Current product March2018 onward; legacy April2004–February2018 | Potential source for quotes/trades and exact historical replication. Price not established; two historical product eras and timestamp conventions require reconciliation. |

No purchase, subscription, account creation, credential inspection or external contact was performed. No suitable authenticated provider connection was available. Public sample failures do not establish that the paid data are unavailable elsewhere.

## Exact delivery/export request

1. **Instrument:** CFE VX standard monthly futures, each dated contract separately, raw unadjusted prices; retain contract codes, delivery months and actual expiration dates. Continuous back-adjusted prices are insufficient. Preserve weekly series separately if delivered.
2. **Coverage:**2010–2014 inclusive for source replication and2018–2022 inclusive for modern design. Prefer full available history; keep2023+ reserved until an earned validation gate. Include contracts spanning the start/end of each interval, not merely contracts whose delivery month falls inside it.
3. **Bars:**1minute OHLC and actual traded volume across the full available session, including the11:00 entry through at least35minutes after each statement. Retain vendor's original timestamps and documentation of timezone, DST, start/end labels, session breaks, empty bars and corrections. No forward-filled synthetic trade volume.
4. **Execution:** bid/ask or trade tape if available, plus tick/contract specification history. One-minute bars can support a limited conservative screen only after explicit fill/stop assumptions; they do not reveal spread or intra-minute execution order.
5. **Packaging:** CSV or Parquet with provider provenance, field dictionary and license terms. Keep originals in ignored `scratch_data/codex_vx_acquisition/`; do not commit licensed bulk data. No account credentials needed in the repository or chat.

First admission check after files arrive: identify a known scheduled FOMC date, reconcile its exact contract/expiry and price levels, map vendor timestamps against the scheduled statement clock, check OHLC/volume integrity and missing minutes, and confirm both required year ranges. Stop on missing event windows or unexplained clock discrepancies. This check is data validation, not a return test.

Source specification still needs an explicit resolution of chart-only `min-Maturity=5`, the11:00 timezone/DST convention and the printed leverage sign. Receiving bars does not resolve these automatically. Evidence and committed bounded preregistration must precede strategy returns.

## Resume condition

**User decision2026-10-31: free sources only.** Do not pursue paid access or repeat the purchase question. Paid listings above are historical discovery records, not next actions. No matching free full-history panel was obtained in the completed search. Resume only when a distinct, legitimately free source or matching already-owned export becomes available; do not repeat unchanged acquisition paths. The environment's vendor-host restriction separately prevents the attempted direct sample download. No source-equivalent backtest is currently possible with the acquired inputs.

Tell Claude: `agents/codex/results/fomc_vx_data_acquisition.md` — acquisition blocked, no new empirical strategy evidence.
