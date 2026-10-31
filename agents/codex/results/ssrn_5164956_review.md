# Overnight/intraday disagreement: a possible feature, no verified futures or plan edge

Source: user-uploaded SSRN5164956, Overnight vs. Intraday Returns: Investor Disagreement,
Information Uncertainty, and Future Stock Returns; RichardD.F.Harris,NanLi,NickTaylor.
Text/model/methods/results/Table3/Table11/conclusion inspected. Zero new strategy trials,
backtests or account comparisons. All statistics below are author-reported, not our replication.

## 1. What is it about?

US common stocks,CRSP codes10/11,NYSE/AMEX/NASDAQ,August1992–December2022; exclude stock
months with missing trading days and prices below1USD, adjust delistings where applicable.
Month-end rank stocks by a prior-month price-based disagreement measure, long highest decile,
short lowest, hold the following month. This is stock cross-sectional selection, not a rule
predicting tomorrow's NQ direction or trading against yesterday's overnight move.

Section4.2/Eq16: Dis = monthly MEAN of (|intraday simple return|+|overnight simple return|)
divided by same-month close-to-close return STANDARD DEVIATION. Abstract/conclusion say
variance, but the explicit equation and definition say SD. Preserve this ambiguity for source
parity; do not choose a denominator on results. Overnight return inferred multiplicatively
from total return and open-to-close price return; equity adjustment/dividend conventions
matter. Only previous completed month is available for next month's decisions.

## 2. What does it find?

Table3: equal-weight H−L raw1.177%monthly,t7.46;4factoralpha1.394%,t7.41.
Value-weight H−L0.355%monthly,t2.10;4factoralpha0.413%,t2.25.
Table11: post2000equalweight1.127%,t5.92;valueweight0.264%,t1.31 (insignificant).
Table11pre2000valueweight0.638%,t2.12; section7.2prose incorrectly attaches7.46 to
that0.638%figure. Use the table, retain discrepancy. These t's are heteroskedasticity-robust
as described, not automatically our daily NW5, dependence/selection-corrected promotion t.

Table3PanelC attributes predictive spread mainly to subsequent intraday components:
3.214%monthly,t16.70,overnight−0.194%,t−1.49. Do not add these mechanically to reproduce
1.177%total: exact aggregation/compounding/rebalancing/sampling and adjustment conventions
must be reconciled using ledgers. No result is independently authenticated from the PDF.
No explicit executable transaction/borrow-cost model located; share-size/liquidity/turnover
and opening/closing auction fill frictions remain. Larger equal-vs-valueweight performance,
illiquidity concentration and post2000valueweight weakness limit relevance to large indexfutures.

## 3. Why would it make money, if it does?

Authors propose compensation for INFORMATION UNCERTAINTY: groups process public information
differently; holding less-transparent stocks may require higher expected returns. Higher scores
are associated with uncertainty proxies and subsequent earnings-announcement returns. This
supports a risk-premium interpretation, not an identified compulsory order or causal proof.
Do not infer individual retail/institutional trading from index close/open alone. Factor-alpha
survival does not eliminate every mispricing, liquidity or omitted-variable explanation.

Absolute-leg sum does not require overnight/intraday returns to have opposite signs. The
close-to-close SD denominator can interact with cancellation of the two return legs. Distinguish
this feature from plain volatility, lagged returns and known overnight-reversal families.

## 4. Can we build on it?

Yes as a NEW, UNTESTED price-derived feature. NQ/ES existing minute histories can support a
cash-clock proxy from completed prior months, without buying an analyst feed. The index's
cross-sectional stock variation is not an aggregate time-series timing effect; transfer is
an independent hypothesis. Broad equity original replication needs a point-in-time common-
stock universe with adjusted opens/closes/delistings and executable costs; our index futures
files do not reproduce that universe. No burden to ask the user to verify those facts.

Recommended cheapest follow-up: bounded test of the frozen prior-month score as a FILTER on
one existing independently defined NQ/ES book leg, before any new signal/size search. Preregister
exact cash close/open clocks, denominator, lag and threshold on2018–22; compare volatility-only,
lagged return/overnight-price controls and total base/kept/removed profit with1000matched subsets.
Only if design passes move to current personal BASE/ADD/REPLACE/EMPTY, then selected historical
validation and full dependence/selection checks. An approval to review this PDF is not a
preregistration or result for this proposed filter; no economic experiment started here.

Prior research: TIER_LIST's Overnight-Intraday Reversal Everywhere family was rejected on
synchronized7market clocks. This paper's monthly absolute-return score differs, but merely
renaming that reversal is not new. No current failed CHoCH/HP family was retuned.

## Five homes

Personal: research-feature WATCH only; no earned addition, stock-selection replication or
measured diversification.50Kfunded/150Kfunded: original monthlystockspread outside adopted
intraday futures implementation, no eligible addition established.50Kevaluation/150Kevaluation:
same, no joint pass-rate evidence. A new causal intraday filter could be evaluated for all five
homes; none of those tests was run. No measured account improvement or harm claimed.

Verdict: worth a small bounded feature test, lower conviction than its equalweight headline.
No plan allocation/ranking/live changes; stopped programs remain stopped. No pending verified-
strategy queue entry: this is a feature lead, not an executable validated candidate.
