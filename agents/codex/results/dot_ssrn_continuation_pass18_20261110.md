# dot: dividend-payment flows and FX returns
Author: dot. 2026-11-10. Research only; no return tests or trading.

## 57. Dividend Flows and the Foreign Exchange Rate
**Personal daily/overnight; conditional data-gated foundation, not intraday or currently test-ready.**

[SSRN 6415558](https://ssrn.com/abstract=6415558). Full inspected source: Chapter 1 of Jingtao Zheng's [official June 2024 dissertation](https://knowledge.uchicago.edu/records/b5epc-yqe79), printed pp.1–85; Table1.5 visually checked. [PDF](https://knowledge.uchicago.edu/records/b5epc-yqe79/files/Zheng_uchicago_0330D_17368.pdf?download=1), matching MD5 eb6046dbf8edb77a0cc1d98747e4909b. The indexed SSRN posting is April2026, 67 pages: **parity with that manuscript is unverified**.

### Compact source specification
Across nine non-USD G10 currencies, short a currency versus USD for one day when prior two-day aggregate cash dividends exceed its rolling one-year95th percentile. One-dollar positions per triggered currency are summed. Sample January2001–June2023. Table1.5: annual gross/net4.4%/3.6%, Sharpe.68/.56, net t2.66; no positions75% of days. Net assumes constant1bp institutional spreads; forwards approximate spot plus three-month rate differential/365. Compustat Global/CRSP dividends use primary listings, payment dates and weekend adjustment. WMR hourly fixings sampled around local closes supply FX. Repatriation and international reinvestment provide the mechanism. No frozen OOS found. Event-study top5% within full calendar-year is ex-post; **only the trading rule's rolling-year threshold is causal in principle**.

### Independent implementation assessment
The return denominator is not a documented fixed-capital or margin account: simultaneous dollar positions vary. Do not compare3.6% directly with funded portfolio returns. Exact dividend aggregation/share counts, payment currency, primary-listing changes, publication receipts and corrections must be reconciled. Japan has qualifications about when exact amounts are confirmed. Known-beforehand schedules are not automatically point-in-time archived data.

Exact trailing-window endpoint, percentile interpolation/ties, holidays and warm-up are insufficiently specified. Historical study close conventions vary by currency; actual tradable order and financing timestamps must be reconstructed. Approximated one-day forwards are not observed executable retail rollover or futures P&L. Commissions, holiday accrual, ticket minima, collateral, spread stress and integer sizing are absent from the simple cost model.

All positions share a long-USD side. A cash-flow mechanism is distinct from carry or fixing seasonality, but portfolio diversification and account-survival benefit are unproven. Stress-related intermediary constraints may worsen fills. No source stop, target or risk cap is established. Adding risk limits or same-day flattening creates a changed strategy rather than replicating these results.

### Data, rights and dedup
Current TIER_LIST, DATA_NEEDED and scout progress inspection found no matching title,6415558, Zheng or dividend-repatriation entry. The separate scout inventory and this research index have different counts; neither establishes exhaustive uniqueness. Existing failed European-fixing3521370 is a different mechanism and remains failed.

[S&P Compustat](https://www.marketplace.spglobal.com/en/datasets/compustat-financials-%288%29) and [LSEG WMR](https://www.lseg.com/en/ftse-russell/benchmarks/wmr-fx-benchmarks) describe licensed data services. Public dissertation access does not grant dataset rights; no complete open matching panel was located. Existing6E bars cannot reproduce nine-currency dividend/FX inputs. Futures substitution changes financing and universe.

**Next gate:** reconcile SSRN/dissertation versions, then audit one complete dividend interval with as-of records, aggregation, quotation direction and executable financing. No data acquisition or return test is authorized by this report.
