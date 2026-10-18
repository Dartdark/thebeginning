# Antigravity's reading of López de Prado, *Advances in Financial Machine Learning* (2018) — Claude's review (2026-10-18)

Source: antigravity/jesse `tasks/out_book_prado_afml/` (19 ideas, shortlist of 3). Format followed well (quotes, pages, Apex fit).

**Verdict: no trade to test. The book is a methods book; its one market mechanism is already tested.**

- **The only real forced flow in it** (idea 1: dealers sell off-the-run Treasuries before auctions, p. 180) is an
  illustrative example with no evidence. We already tested the intraday version thoroughly (TIER_LIST,
  `analysis/treasury_auction_test.py`, Fleming-Liu-Nguyen 2026): the pre-auction ZN dip is real (t 2.3 gross) but about a
  third of the round-trip cost; net negative.
- **Shortlist #1-2 (SADF explosiveness, symmetric CUSUM):** in the book these are a bubble-detection test and an
  event-SAMPLING filter (when to ask the ML model for a label), not trade rules. The "book's mechanism" text for SADF
  (margin-call cascades) is not Prado's; it should have been labelled "my inference" (brief rule 0). As trade rules they
  are generic intraday trend triggers with free thresholds; that family (ORB, gap momentum, intraday trend models) has
  failed on NQ / ES repeatedly. Not tested: no stated forced trader, and choosing h / the critical value is a parameter search.
- **Shortlist #3 (Optimal Trading Rules on an OU process):** an exit-optimisation method, not an edge; our exits come
  from each strategy's mechanism, and OU-based filters were F.

**Already in our process (the book's real value):** triple-barrier labels = our target / stop / time exits; meta-labeling
(tested on VB and LDF: F); deflated Sharpe and probability of backtest overfitting (`analysis/metrics.py`: `deflated_sharpe`,
`pbo`, used for every promotion); bet sizing from a probability ≈ our cushion sizing question.
