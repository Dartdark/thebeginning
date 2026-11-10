# dot: Unbiased Trading representative review

Summary: Useful material concerns executable costs/fills and concentrated portfolio risk.
Data/tool leads include Hyperliquid funding and SEC filing access, with substantial permissions and timing limits.
No verified VB replacement or older CME minute-data source was found.
This is a representative review, not an exhaustive channel audit or independently replicated creator performance.

Author/origin: **dot**. Review delivered November 10, 2026; saved here afterward at the user's request.
Creator/source claims remain separate from dot's assessment. Some transcripts used in the original review were mirrors; creator simulations were not independently verified. No new source re-review or test occurred during this branch publication.

## Five review questions
1. **What is it about?** @UnbiasedTradingGoshawk trading-method, portfolio, data and tooling discussions. Representative [video](https://www.youtube.com/watch?v=elPKLu9cj_I) and [interview](https://zencastr.com/z/O06ZQkmC).
2. **What does it find?** The useful takeaways are checking costs and executable fills, avoiding concentrated/shared losses, and distinguishing useful data access from a ready strategy. These are methodological lessons, not verified returns from this review.
3. **Why does it make money, if it does?** No independently demonstrated profitable rule was established here. Funding is a contractual cashflow but price, hedge, basis, collateral and venue risks can outweigh it.
4. **Can we build on it?** Yes, as a source/feasibility reference. Existing execution and parameter work should not be repeated merely because the channel discusses it. The subsequently completed [Hyperliquid audit](hyperliquid_data_audit_20261110.md) stays NEEDS DATA. The [loss map](dot_vb_onb_loss_map_20261110.md) relates shared-risk lessons to documented account paths without promising a fix.
5. **Can a strategy code be made?** Conditional on exact signal, timing, executable instruments/costs and admitted data. A funding parser/auditor is implementable and exists; a historically valid pre-payment strategy still lacks forecast receipt history, oracle/payment reconciliation and hedge paths. No complete profitable CME rule follows from this review.

## Data and tools
- **Hyperliquid:** venue-specific historical settled funding is a D32 feasibility lead, not CME data. [API](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/info-endpoint/perpetuals). Latest 5,000 candles limit long minute history; deeper [archives](https://hyperliquid.gitbook.io/hyperliquid-docs/historical-data) are requester-paid and were not used. Public accessibility does not certify reuse rights.
- **Binance:** public trades/candles and taker-buy volume are not permission for the intended use. [Terms](https://github.com/binance/binance-public-data/blob/master/TERMS_AND_CONDITIONS.md) impose noncommercial-research restrictions and prohibit live proprietary-trading execution without licensing. No download occurred.
- **AskEdgar:** keyed/credit-based, with documented focus largely on smaller companies. **SEC APIs were dot's alternative suggestion**, not attributed to the creator: [SEC EDGAR APIs](https://www.sec.gov/search-filings/edgar-application-programming-interfaces). Narrative guidance still requires source-document extraction and authentic availability times.
- Portfolio mathematics and indicator ensembles are educational references, not independent edges. Earlier VB timeframe-ensemble work already underperformed its single-timeframe comparison; no repeat study is requested here.

No return tests, portfolio changes, paid access, external contact or scout/lab restart. For all five portfolio homes, no new eligible strategy addition is established by this source review.
