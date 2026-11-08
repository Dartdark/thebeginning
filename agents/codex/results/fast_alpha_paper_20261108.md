# Fast alphas: source review and current-book test specification

Summary: The paper's SPY timing improvement is an author backtest, not evidence it works on ES or every parent.
Its reported Sharpe is0.86in the body/0.87in the abstract, versus0.99with the overlay; CAGR gain approximately2points.
Commissions are included, but slippage is explicitly zero; one five-minute return is measured close-to-close.
The requested24-parent execution study has a frozen design; its outcomes will be reported separately.

Source: Carlo Zarattini and Alberto Pagani, *Improving Performance with Fast Alphas*, Concretum QuanTips2,
February2026,7-page owned upload. [Source](../inputs/fast_alpha_books_20261108/paper.pdf),
[text/version receipt](../inputs/fast_alpha_books_20261108/access.json).

1. **What is it about?** Using short-horizon SPY mean reversion as execution information for a slower intraday
   ATR breakout, rather than trading the reversal at extremely high turnover. Sample January2007–January2026.
2. **What does it find?** Authors report roughly200bp more annualized return and Sharpe0.86/0.87to0.99. The
   baseline is session open±0.5ATR14, decisions every15minutes, stop at session open, EOD flat, daily2%vol targeting.
   Cost assumptions: IBKR tiered0.0035/share, doubled sell charge, zero slippage, fractional shares, no minimum fee.
   No author code/raw IQFeed/Norgate replication or fresh unseen validation was supplied here.
3. **Why does it make money, if it does?** Proposed short-lived reversal improves execution around a slower
   favorable move without standalone fast-alpha turnover. It can also miss the profitable first minutes, buy
   at a worse price despite a down bar, or increase losses while postponing a stop. The source's claim that
   the trigger is unchanged does not preserve its loss cap. A market order after a pullback remains aggressive.
4. **Can we build on it?** Yes: the user explicitly requests a common-policy comparison across current books.
   Preserve prior negative NQ overlay history and include every frozen parent, cancellations, extra risk and
   matched delay/drop nulls. SPY tracking the S&P500 does not establish ES transfer, equivalent costs or fills.
   The [evidence](../evidence/fast_alpha_books_20261108.md) and [preregistration](../plans/fast_alpha_books_20261108.md)
   define the bounded experiment and all earned account stages.
5. **Can a strategy code be made?** **Yes, a research execution wrapper**, with causal original intents,
   full five-minute signals, next-minute fills, target/stop/time priority, native fees and path accounting.
   The committed Python runner is a fixed virtual-parent ticket replay, not production MultiCharts code or
   proof of exact original intent reconstruction. Any survivor must earn that independent reconstruction
   and actual-size account comparisons; no live modification follows from this review.

The earlier `analysis/fast_alpha_test.py` tested seven older NQ streams, generally losing on delays. Its
six wait/fallback profiles per parent, full-sample/recent views and paper-breakout tests remain prior selection.
That replay used forward-filled prices and unchanged realized exits, so its reported negatives are qualified
historical evidence, not a complete current-book rerun. This task neither erases them nor silently rescues them.
