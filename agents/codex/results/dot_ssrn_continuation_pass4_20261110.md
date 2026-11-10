# dot: SSRN continuation, pass 4
Author: dot. Date: 2026-11-10. Research only, on codex/work.

## Summary
The strongest new full-paper research in this pass is factor-based intraday equity prediction, requiring a separate data stack.
Three appealing timing papers fail important execution, statistical or point-in-time checks.
Recovered MOM–TOM source reveals a calendar mismatch in an existing indexed adaptation; no tests were reopened.
These are research classifications, not strategy approvals.

## 28. Intraday Return Predictability in the Crude Oil Market: The Role of EIA Inventory Announcements
Wen, Indriawan, Lien and Xu. [SSRN 3822093](https://ssrn.com/abstract=3822093).
[Accepted Energy Journal manuscript](https://digital.library.adelaide.edu.au/server/api/core/bitstreams/aee73b81-111e-4bef-9e0e-7b1164f368a1/content), pages 7–8, 21–24 and 43.

**Source evidence:** USO one-minute observations span April 10, 2006–July 31, 2019, covering 3,240 days. On 591 actual Wednesday 10:30 Eastern EIA release days, measure the 10:30–11:00 log return. Buy at 15:30 if nonnegative, otherwise short, and close at 16:00. Non-Wednesday releases are excluded. This bare rule needs no inventory-surprise input. Table 6 reports annual mean 4.14%, t=1.88, standard deviation 0.21 and a reported Sharpe of 19.54. Predictability is absent during 2014–2016. Rolling five-year coefficient estimates do not provide untouched forward strategy P&L. No strategy trading-cost adjustment was found.

**dot assessment:** Intraday personal ETF hypothesis, not an Apex futures replication. Existing data: native USO minute history not verified. CL substitution or changing the exit to the futures settlement window is a new adaptation. Existing project CL EIA follow-through tests are weak and cannot be ignored.
Do not promote the reported Sharpe: the annualized mean divided by the displayed half-hour standard deviation approximately produces that number, without consistent annualization. The reported mean t-statistic also misses conventional two-sided 5% significance. Before any authorized test, confirm return definitions, zero-exposure days, USO splits, quoted spreads, actual release calendar and causal fills. Mechanism attribution uses richer trade/quote data unavailable in simple OHLCV; basic signal generation does not. Useful source audit, not a strong replacement for the original intraday reserves.

## 29. Profitability of Trading in the Direction of Asset Price Jumps
Fičura. [SSRN 2903629](https://ssrn.com/abstract=2903629).
[Full Prague Economic Papers article](https://pep.vse.cz/pdfs/pep/2019/04/01.pdf).

**Source evidence:** A Lee–Mykland standardized-return jump trigger follows the detected jump's sign. Confidence thresholds and 1–24-bar holding horizons are chosen on the first half of each series and frozen on the second. The data include spot FX through June 2015 and CL/ES/VX through December 2015, with weekend and rollover gaps cleaned. Costs are one pip for FX and a one-tick futures spread plus $2.20 commission. EUR/USD 15-minute results use 90% confidence and a nine-bar hold, with 674 OOS trades and t=2.828; the 30-minute version holds four bars, with 414 trades and t=2.590. None of 21 futures OOS cells reaches 5% significance. ES 15-minute cumulative OOS profit is negative $16,735 per contract and CL negative $37,192.

**dot assessment:** Reject as a new ES/CL strategy. A spot-FX signal translated to 6E is unvalidated, not an existing-data replication. Price-only estimation is conceptually possible, but exact session, gap, roll and volatility-window treatment matters. A fixed intraday exit is not established by a simple bar-horizon rule. Multiple markets/frequencies and holding-period dependence limit the strength of the isolated positive FX cells. Do not interpret drawdown-scaled performance as unlevered return.

## 30. Investor Inattention and the Market Impact of Summary Statistics
Gilbert, Kogan, Lochstoer and Ozyildirim. [SSRN 1108050](https://ssrn.com/abstract=1108050).
[Published Management Science paper](https://business.columbia.edu/sites/default/files-efs/pubfiles/3200/investor_inattention.pdf).

**Source evidence:** The sample contains 116 LEI events during February 1997–February 2009, excluding 30 simultaneous-announcement dates. Signal is original-release LEI minus Bloomberg consensus. The equity rule follows its sign at 10:00 New York time on the previous trading day, reverses at 10:05 on release day and closes at 16:00 the next day. Bond direction is opposite, with weaker evidence. Exit horizon was chosen ex post, as footnote 15 states. Futures execution costs were unavailable; a 14-basis-point SPY spread proxy supports the claimed roughly 6% net annual return. The prominent 65.2-basis-point result is a standardized-surprise regression coefficient, not a separately documented signed-strategy realized mean. No clean OOS strategy test was established.

**dot assessment:** Personal overnight hypothesis only; not current-data testable. The release may be reconstructible from public components, but the paper does not establish a complete pre-entry reconstruction backtest. Required inputs include original vintages, contemporaneous component weights, estimated missing components, entry-time consensus and exact calendars. Revised historical LEI is not an ex-ante signal.
The [author appendix](https://faculty.washington.edu/gilbertt/docs/Gilbert_Kogan_Lochstoer_Ozyildirim_Investor%20Inattention%20and%20the%20LEI_Appendix_2011.pdf) describes construction. [Current methodology](https://www.conference-board.org/data/bci/index.cfm?id=2154) includes major 2012 component changes, while [March 2026 technical notes](https://www.conference-board.org/pdf_free/press/US%20LEI%20Technical%20Notes-Mar%202026.pdf) describe revised weights and data timing. An intraday-only variant would be a new hypothesis, not the published strategy.

## 31. The MOM–TOM Effect: Detecting the Market Impact of CTA Trading
Van Hemert. [SSRN 2515900](https://ssrn.com/abstract=2515900).
[Full 2014 manuscript mirror](https://www.followingthetrend.com/?mdocs-file=2592), pages 4–9.

**Source evidence:** Turn of month means the final TWO business days of a month and FIRST day of the next. A replication portfolio spans 52 futures, with average returns divided by variance, then covariance-based scaling to 10% annual volatility. A 100-day lookback is chosen for strongest correlation with the Newedge trend index among 20–320-day candidates. Volatility combines roughly two-month and four-year exponentially weighted estimates; correlations use about one year. Evidence emphasizes January 2000–March 2014, with weaker earlier effects and a reversal in late 2013. Fees are omitted. Table 2's TOM information ratio of 3.23 annualizes only selected-day returns using square root of 250. Equity-index evidence is weaker than commodities, currencies and rates.

**dot assessment:** Existing-family source correction, not fresh alpha. Personal: close-to-close hypothesis. Intraday: not proven. Existing data: original 52-contract replication unavailable; subset adaptations already exist.
The [indexed Q017 preregistration at commit 4dfc4b](https://github.com/Dartdark/thebeginning/blob/4dfc4b1777d55fab345487b702b5efec918dd058/checks/candidates/lab_Q017/PREREG.md) instead uses the final ONE session plus first TWO sessions, and 63/252-day sign momentum with intraday entries/exits. Its failure is not an exact-paper replication verdict. This path was not found on codex/work; the comparison is explicitly to the indexed default-branch snapshot. No existing files or test conclusions were changed.
Selected-day annualization does not equal a cash-on-other-days strategy Sharpe. Need proper calendar returns, attainable fills, native rolls and complete specification before any later authorized replication. The calendar mismatch is not permission to rerun or reopen paused work.

## 32. Intraday Market Return Predictability Culled from the Factor Zoo
Aleti, Bollerslev and Siggaard. [SSRN 4388560](https://ssrn.com/abstract=4388560).
[Published 2025 Management Science paper](https://public.econ.duke.edu/~boller/Papers/MS_2025.pdf); [online appendix](https://econ.duke.edu/~boller/Papers/HFML_Sup_App.pdf).
SSRN 3726765 is a different paper, not an earlier version.

**Source evidence:** Lagged intraday/daily returns for 272 equity portfolios predict the next 15-minute market return and trade SPY. Data span 1996–2020; OOS covers 2004–2020. Expanding samples use chronological 80/20 training/validation, with annual refits for most models and five-year refits for nonlinear models. Nine forecasts form an ensemble. The preferred target filters jumps using past information. S-Sign uses ±100% exposure with a no-trade region based on lagged quoted half-spreads. Costs apply to ETF turnover, with 2% annualized short borrowing; supplemental results model market impact. Reported intraday net Sharpe is 1.37. Default overnight exposure remains +100%, although overnight returns are excluded from that headline statistic. Factors are predictors, not holdings, so factor-level trade netting is irrelevant.

**dot assessment:** Stronger research design than most new intraday screens, but conditional personal-equity research, not a ready futures strategy. The published appendix already supplies a separately costed flat-overnight implementation. Existing-data replication: no, cross-sectional factor histories and quoted spreads are missing from futures OHLCV.
The [author's data page](https://www.sakethaleti.com/data) links historical factor returns; live availability, synchronization, licensing and latency remain open. Printed threshold equations appear inconsistent with the stated no-trade region; intended symmetric positive/negative cutoffs are an interpretation, not code-verified. The [official replication page](https://pubsonline.informs.org/doi/suppl/10.1287/mnsc.2023.01657) lists 13 parts, but attempted file access failed. No need to acquire data or implement before these gates are resolved.
This is a separate data-intensive candidate, not evidence that the current few-futures predictor set should work.

### Independent full-appendix correction
Appendix OA.7.5, Table OA.12 (printed pages 61–62), explicitly sets overnight exposure to zero. Its Cts,All–Ensemble–S-Sign row reports transaction-cost-adjusted annual intraday return 19.89%, Sharpe 1.37 and alpha 19.98% (t=5.75), for 2004–2020. The main paper also flags this robustness check in footnote 17. This corrects the earlier implication that eliminating overnight exposure was an unstudied adaptation. It does not establish a futures implementation, current data access, live predictor delivery, modern untouched holdout or portfolio benefit. The table was checked in the rendered full appendix; no return test was run.

## Research status
No new candidate in this pass clears every source, data, cost, holdout and portfolio-fit gate. Source audits add useful hypotheses and prevent false promotion. Continue research without changing live strategy books or re-running prior experiments.
