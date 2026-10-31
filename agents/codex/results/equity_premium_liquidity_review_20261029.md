# Equity premium and endogenous trading: WATCH as theory; no strategy established
Summary: Swan proposes a liquidity-preference explanation of the equity premium, not an executable trading strategy.
Historical model fits are not after-cost excess returns from following a signal.
NYSE dividend-yield adjusted R² is 36.38% for 1955–98; the cited 60%+ figures concern selected subperiods.
Useful context on liquidity compensation and turnover; no new strategy test or verification-queue entry recommended.

Source: Peter L. Swan, *Can “Illiquidity” Explain the Equity Premium Puzzle? The Value of Endogenous Market Trading*,
version dated June 17, 2002, [SSRN 251399](https://ssrn.com/abstract=251399), user-uploaded PDF.
SHA256: `b20a93d906149c5e21e7c24113efb1524d13c391ca63ce25ae38d04212a75bbb`.
Review date: 2026-10-29. Source-only review; findings not independently replicated.
New return trials: **0**. No backtest plan/script applicable.
Repo context: codex/work `1caf201f38ec94ad030e3f31a9aed4a65261434c`.

## 1. What is it about?

Why stocks historically earned substantially more than Treasury bills, beyond what simple consumption-risk models explain.
The author incorporates the benefits investors obtain from trading/liquidity into preferences and allows turnover
to respond to transaction costs. Liquidity is proxied principally by turnover; trading benefits are model-implied,
not directly measured survey responses or a prespecified signal.

The model contrasts equity and Treasury securities and estimates relationships using historical U.S. and Australian
data. It is not an intraday mean-reversion, momentum, market-making or scheduled-flow strategy.

## 2. What does it find?

| Source result | Meaning / limit |
|---|---|
| Introduction reports a 6.07% annual historical NYSE equity premium over bills, 1900–98. | Historical market compensation being explained; not a new strategy's annual alpha or a promised future return. |
| Table 1 / introduction: 1980–2000 average annual turnover about 13.9 for Treasury bonds/bills versus 0.575 for NYSE equity; mean relative ratio 24.58. | Historical measures across different assets/market structures; turnover is not interchangeable with bid/ask spread, depth or execution resilience. |
| Australian analysis uses approximately 576 stocks and 24,350 monthly observations, 1994–98, with spreads, taxes and assumed brokerage (section VI). | The fitted model links costs, turnover and returns; it is not a trade ledger showing exploitable net profit. The conclusion inconsistently says 1994–99. |
| Table 6: NYSE dividend-yield fit has adjusted R² 0.3638 over 1955–98; 0.6424 over 1955–74 and 0.6783 over 1975–88. | The conclusion's 60%+ emphasis is not the full-sample fit. The dependent variable is dividend yield, not next-day trading return. |
| Table 6 implies equity transaction costs 3.476% for the full sample and 0.958% for 1989–98. | Model-implied historical costs, not current observed spreads or suitable NQ/ES/micro commission inputs. |

References: abstract; introduction pp.2–3; empirical sections VI and IX; conclusion pp.37–39; Table 6 p.52.
Section IX predicts daily turnover from the preceding twenty days before fitting the dividend-yield equation.
That timing choice does not establish causal identification or a successful chronological return-forecasting strategy.

The author argues the framework accounts for the premium and related volatility puzzle. This review treats
those as model-dependent claims. In-sample fit, high parameter t-statistics and rejection of a nested restriction
do not establish that liquidity uniquely explains the premium rather than risk, information or alternative specifications.
There is no independently reproduced modern out-of-sample strategy performance here.

## 3. Why does it make money, if it does?

The proposed compensation is for giving up liquidity benefits: investors require a higher expected return
to hold less liquid equity relative to more liquid Treasury assets. Endogenous turnover magnifies the model's
premium beyond simply multiplying spread by turnover.

This is an equilibrium explanation, not a free arbitrage. A high expected return may compensate for trading
frictions, inability to exit cheaply and exposure to adverse states. Holding something less liquid can also produce
losses, especially if liquidity deteriorates when the investor needs cash.
A liquidity premium is distinct from a directional prediction and from profits earned by supplying liquidity intraday.

The framework does not mean that trading more automatically increases financial wealth. Utility from trading,
model-implied investor surplus and after-cost cash P&L are separate quantities.

## 4. Can we build on it?

**For hypothesis discipline and liquidity-risk context, yes. As a ready foundation for an ES/NQ strategy, no.**

Useful applications: distinguish compensation for illiquidity from alpha; measure spread, depth, impact and
turnover separately; and recognize that observed volume responds to trading costs and market conditions.
High volume is not automatically high executable liquidity, nor is low volume a directional buy signal.

A new strategy would still need a participant, information available before entry, net directional transmission,
fixed trade horizon and a plausible gross edge versus costs. This paper supplies no forced-flow schedule,
entry threshold, stop, exit, size or timing evidence. Its historical equity-versus-bill comparison does not
establish a futures opportunity. A personal account removes the intraday holding restriction, but not the need
for predictive evidence and sufficient capital through liquidity stress.

A direct replication would need historical equity returns/dividends, shares outstanding and turnover, Treasury
yields, and the paper's spread/tax/brokerage assumptions; stock-level Australian replication additionally needs
the relevant SIRCA inputs. Ownership, current access and licence costs were not checked.
No modern empirical update or external data was obtained.

## Decision

**DON'T TEST as a new strategy from this paper alone.** Keep it as theoretical background.
TIER_LIST, WATCHLIST and the current TODO queue were inspected at the pinned head. No exact source match was found;
existing FOMC liquidity-filter tests are separate hypotheses and are not validated by this paper.
No promising-strategy queue addition because no particular executable candidate establishes useful merits.
No return tests, MultiCharts code, account simulations, trading allocations or live/VPS changes were performed.
Portfolio benefit, payout impact, execution edge and current profitability are unmeasured.

For Claude: `agents/codex/results/equity_premium_liquidity_review_20261029.md`.
