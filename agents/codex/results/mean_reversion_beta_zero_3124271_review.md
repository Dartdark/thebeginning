# Mean Reversion + Beta-Zero Targeting: retain the implementation lesson; DON'T TEST

Summary: This short Quantopian note buys recent stock losers, shorts winners and adds SPY/TLT hedges.
The author admits optimizing the parameters on backtests; the original ten-year Sharpe is 0.89 with −42.26% drawdown.
A one-year paper-trading screenshot reports +70.06%, but it does not validate the later corrected algorithm.
The code used a one-day liquidity lookback instead of the intended five; corrected backtest Sharpe is 0.85.
Retain the code-version and beta-risk cautions; no new return trial, promising-strategy queue item or allocation.

Source: Raj Krishnamurthy, *Mean Reversion + Beta-Zero Targeting*,
[SSRN 3124271](https://ssrn.com/abstract=3124271), uploaded seven-page note, fully read.
PDF creation metadata January 24, 2018; publication/revision history not independently verified.
[Archived PDF](../inputs/ssrn3124271/source.pdf), [extracted text](../inputs/ssrn3124271/source.txt).
PDF SHA-256: `d9a1fa63c071e935535007eb3f2d695ee487661e54c46038dd0317b5d4c83569`.
Figures inspected visually on pp. 3, 4, 6 and 7; archived renders of pp. 3, 6 and 7 preserve screenshot-only metrics.
All reported performance below is **the author's**, not independently reproduced. Return trials: **0**.

## 1. What is it about?

After Friday's close, select highly traded individual stocks by dollar volume, buy the prior week's losers and
short its winners on Monday at noon. The stated cutoffs are top 3% by liquidity, bottom 3.6% by weekly returns
for longs and top 0.4% for shorts. A one-year beta estimate guides additional SPY and/or TLT positions intended
to target zero beta to SPY (p. 3). The note explicitly says the colored parameters were data-mined for backtest results.

The correction is substantive: the code used one day of dollar volume, while five days was intended (p. 7).
The methodology on p. 3 describes the one-day version actually used; the corrected five-day version is a separate
strategy implementation. Their historical results and prospective evidence must remain separate.

## 2. What does it find?

| Version / period | Total return | Sharpe | Sortino | Beta | Maximum drawdown |
|---|---:|---:|---:|---:|---:|
| Original backtest, Jan. 2007–Jan. 2017, Fig. 1 | +1,303.51% | 0.89 | 1.44 | 0.29 | −42.26% |
| Paper trading, Jan. 23, 2017–Jan. 23, 2018, Fig. 3 | +70.06% | 2.40 | 4.20 | −0.04 | Not supplied in Fig. 3 |
| Corrected five-day-liquidity backtest, Fig. 4 | +1,144.09% | 0.85 | 1.37 | 0.25 | −37.23% |

The original prose reports a 30.23% annualized return against 6.81% for the benchmark (p. 4).
Those large returns do not remove the sizable drawdown or selection risk. Figure 1's historical beta is materially
positive despite the zero-beta target. The note's p. 5 −10.52% drawdown statement appears in the then-current
trading discussion and must not replace the −42.26% full-backtest drawdown shown in Figure 1.

The one-year update is a **paper-trading** report, not broker-verified funded live performance. Its headline
Sharpe is 2.40; some panel labels are dated January 18 while the performance panel is dated January 23, so not
all screenshot fields have established same-date parity. The author says the corrected version's future paper
performance remains to be seen (p. 7). No frozen code or trade ledger independently links versions to snapshots.

## 3. Why does it make money, if it does?

The proposed explanation is reversal in stock prices, with a market-beta hedge reducing broad equity exposure.
The cited long-horizon mean-reversion research does not itself establish this weekly tail-ranking rule, these
asymmetric cutoffs, a Monday-noon advantage or a return after borrow and turnover costs.

Liquidity provision after temporary price pressure is a plausible general explanation, but this note does not
identify a forced seller/buyer, measure order pressure or distinguish temporary mispricing from permanent news.
The author gives counterexamples: shorting pharmaceutical stocks after successful drug-trial news and buying
Equifax after its breach (p. 5). These are evidence of event/sector exposure, not proof that discretionary screening
would improve results. A proposed human veto has no frozen rule or independently tested record here.

Zero market beta also does not follow from the low-beta-stock anomaly cited on p. 2. A beta-neutral portfolio
can retain sector, volatility, short-squeeze, liquidity, funding and discontinuous news risks. TLT adds duration
exposure, and its equity beta can change. Neither an estimated beta nor a hedge prevents intraday account losses.

## 4. Can we build on it?

**Not enough evidence to justify rebuilding this version.** The original has a selected historical Sharpe below
one, large drawdown, undocumented search breadth and only a short paper-forward record. The five-day correction
has no reported prospective validation. Necessary implementation details are missing: the point-in-time stock
universe, exact percentile denominators/rounding, weights, gross/net leverage limits, liquidation/holding rule,
rebalancing policy, beta estimator/hedge solver, SPY-versus-TLT choice, locates, borrow, fees and slippage.
The figures' selected stock counts are not an executable definition of the tail-ranking procedure.

Some public daily S&P500 inputs were acquired for the earlier factor-beta-session project, but they do not
reproduce this broad stock universe, Monday-noon execution or short availability. That previous project's
failed net screens are related cautions, **not a replication or rejection of this exact stock rule**.
No additional acquisition is warranted for a candidate that fails this source/evidence gate; missing code/data
is not the only reason for stopping. Do not invent omitted settings or launch an NQ/ES reversal proxy.

The source does not provide an intraday-flat rule and depends on individual stocks and ETF hedges, so no place
in the 50K/150K evaluation or funded plans is established. A personal-account proposal would still need its own
credible specification, stronger independent forward evidence, costs, risk and current-portfolio comparisons.
No account benefit, diversification improvement or execution saving has been measured here.

## Retained lesson and disposition

Freeze the **implemented** code, input interpretation and data version before paper tracking. A forward result
from a one-day lookback cannot validate a revised five-day rule. Link code hashes, rebalance holdings and order
clocks to every report; inspect actual beta, gross exposure and joint losses instead of treating a zero-beta
objective as a risk guarantee. This extends execution reference E42 without changing any live workflow.

Checked SSRN identifier/author and related reversal/beta terms against TIER_LIST and Codex reports: no earlier
review of this exact note identified. Related individual-stock reversal and August-2007 quant-unwind work remains
relevant; stock-level associations do not automatically transfer to index futures. No promising queue entry is
added because the present evidence does not establish enough merit to prioritize this selected, incomplete rule.

**Verdict: DON'T TEST this source version.** Retain the review and implementation/risk lessons. No trading tier,
return result, independent verification, portfolio placement or plan change is claimed.

For Claude: `agents/codex/results/mean_reversion_beta_zero_3124271_review.md`.
