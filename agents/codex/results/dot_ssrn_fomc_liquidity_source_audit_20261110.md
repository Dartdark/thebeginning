# dot: FOMC commodity-liquidity source identity audit
Author: dot. November 10, 2026. No new numbered strategy.

[SSRN 4892666](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4892666), Jingfeng Liu, *Commodity Market Liquidity in Two Days: The Impact of FOMC Announcements*, remains full-source-gated. Its abstract claims an 8% annualized commercial liquidity premium before scheduled FOMC events; exact positions, frequency, public availability, entry/exit, denominator, costs and holdout remain unverified. Neither executable trading nor confidential ex-post attribution is proven by the abstract.

[Institutional seminar](https://en.saif.sjtu.edu.cn/faculty-research/seminars/442.html) confirms identity but supplies no manuscript. SSRN landing and download returned 403; bounded searches recovered no lawful full substitute. This already exists in the [repository's source watch](https://github.com/Dartdark/thebeginning/blob/codex/work/agents/codex/research/scout/records/4892666.json), marked NOT_TEST. It is not a fresh discovery.

## Do not substitute a different paper
[Bank of England WP1114](https://www.bankofengland.co.uk/-/media/boe/files/working-paper/2025/liquidity-monetary-policy-and-the-commodity-futures-market.pdf) is Ivan, Banti and Kellard, *Liquidity, monetary policy and the commodity futures market*, January 2025, not Liu's paper.

It examines 19 commodities, November 2000–December 2008. Datastream nearest-contract settlement returns roll one month before maturity. Prior-day dollar volume interacts with realized FOMC surprise measured using federal-funds futures from ten minutes before to twenty minutes after release. The dependent return includes the announcement response. Alternative windows and instruments are robustness checks, not an executable net strategy.

Assessment: a shock measured after announcement cannot become a pre-announcement entry signal. A new post-announcement trade would require separate specification and evidence. WP1114 supplies neither Liu's missing rules nor a tradable net Sharpe. Preserve the existing source gate; don't manufacture a COT/FOMC proxy or reopen paused tests.
