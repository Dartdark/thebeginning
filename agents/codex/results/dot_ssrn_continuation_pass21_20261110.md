# dot: SSRN continuation, pass 21
Author: dot. November 10, 2026. Research only.

## 62. Wisdom of Crowds and Commodity Pricing
[SSRN 4104888](https://ssrn.com/abstract=4104888); [published full paper](https://onlinelibrary.wiley.com/doi/full/10.1002/fut.22393), January 2023; [author conference manuscript](https://acfr.aut.ac.nz/__data/assets/pdf_file/0011/686747/2a-John-H-Fan.pdf). Published version is preferred.

**Source:** Commodity-keyword Twitter Academic API corpus, 2009–2020. Clean text; Loughran–McDonald word scores +1 positive, −.15 negative. Take tweet score sign, average daily then monthly; rank monthly sentiment changes. Equal-weight long upper half, short lower half of 28 commodity BCOM excess-return indexes, monthly rebalance, described as 50% collateralized. January 2010–December 2020 gross annual mean 7.2%, volatility 9.6%, Sharpe .75, t=2.9, maximum drawdown −12.2%. Uniform modeled round-trip cost .086%, turnover approximately 1.3 monthly; exact net Sharpe is plotted, not numerically verified. Footnote 6 addresses GMT/exchange-close timing and reports unchanged results dropping tweets after day 25. No untouched modern validation established.

**Assessment:** Distinct personal monthly signal based on language, not COT positions. No exact title/ID match in current index, TIER_LIST or DATA_NEEDED. Does not reopen existing failed sentiment or crowding tests.

Credit the day-25 timing robustness; do not falsely describe an unaddressed simple month-end lookahead. Remaining prerequisites are immutable posting/collection receipts, query/preprocessing/dictionary versions, deleted-tweet and sparse-day treatment, missing-month/tie conventions, and formation-to-fill timing. Later engagement counts must not be backdated.

BCOM index returns require native-contract roll replication, exchange-specific costs, sizing and cash/margin reconciliation. A uniform cost assumption is not a fill ledger. Do not infer a precise net Sharpe from a graph or transfer the broad cross-section to CL/GC alone. Different source information is not proof of incremental portfolio diversification.

**Rights/data:** [Official dictionary terms](https://sraf.nd.edu/loughranmcdonald-master-dictionary/) distinguish free academic research from commercial licensing and provide word addition/removal-year metadata. [X full-archive documentation](https://docs.x.com/x-api/posts/search/introduction) requires pay-per-use or Enterprise access. Bloomberg/Refinitiv index inputs remain restricted. No complete lawful free corpus verified; no purchase or outreach. Not currently owned-data testable, not no-overnight.

## Existing D51 macro-surprise source correction
[SSRN 1920401](https://ssrn.com/abstract=1920401) is already parked in DATA_NEEDED, not a new entry. [Earlier three-index draft](https://www.academia.edu/18131980/Information_Driven_Price_Jumps_and_Trading_Strategy_Evidence_from_Stock_Index_Futures) used actual-minus-consensus direction, first transaction after 10:01 Eastern to one minute later. This trading rule is separate from its retrospective whole-day jump classifier. Tick-cost-adjusted figures are cumulative return sums, not annualized account returns; no untouched strategy holdout.

The [published S&P-only version](https://www.academia.edu/17999424/S_and_P_500_index_futures_price_jumps_and_macroeconomic_news), [DOI 10.1002/fut.21627](https://onlinelibrary.wiley.com/doi/abs/10.1002/fut.21627), changes to Lee–Mykland analysis and reports the response concentrated in the initial minute, with later means near zero. It omits the draft trading-profit experiment.

Assessment: this weakens reliance on draft continuation profits, but is not a modern exact-rule failed replication. Full-size SP cannot silently become ES. Fičura #29's detected-jump strategy is different. Preserve D51's parked status: initial releases, timestamped consensus, concurrent events and attainable first-after-minute fills remain missing. The audit inspected available full HTML text, not visually verified original PDF equations.

## Disposition
62 numbered entries, not 62 validated strategies. No new existing-data admission. No tests, account actions, code changes, data purchases or paused experiment resumption.
