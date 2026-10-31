# Overnight versus intraday tail risk: WATCH as a risk reference; no new strategy test
Summary: Riedel and Wagner separate predictable volatility from residual extreme-loss risk in four equity indices.
Their historical overnight innovations have heavier downside tails despite lower ordinary volatility.
NASDAQ illustrated 99.9% VaR: overnight4.951% versus intraday4.586%; overnight VaR is lower at the other reported levels.
Retain the risk/execution lesson; no demonstrated profitable rule, new backtest, queue candidate or allocation.

Source: Christoph Riedel and Niklas Wagner, *Is Risk higher during Non-Trading Periods? The Risk Trade-Off for
Intraday versus Overnight Market Returns*,18 May2015, [SSRN2494387](https://ssrn.com/abstract=2494387), uploaded PDF.
SHA256: `39ab51157018225eecd97e60f9cc29ebbbbed1ef2b1342f90d438cfdcc3f83fa`.
Review date:2026-10-29. Repository snapshot:`da216431c31c2435088082992dc53130c1ff495b`.
Evidence: source findings, not independently reproduced; Table9 was also checked against the rendered PDF page.
New return trials: **0**. No trading rule or new return calculation was introduced.

## 1. What is it about?

Whether overnight holdings are riskier than intraday holdings, and whether volatility alone answers that question.
The source separates cash-index close-to-close log returns into close-to-next-open and open-to-close components.
It fits an AR(2)-TGARCH/GJR volatility model, then a Generalized Pareto Distribution (GPD) to upper/lower
tails of standardized innovations. The key distinction is **time-varying volatility versus remaining tail shape**.

Markets: NASDAQ Composite, CAC40 and DAX30, September1988–July2010; TOPIX, August1990–July2010 (pp.8–9).
NASDAQ Composite is not the Nasdaq-100. These are historical cash indices, not ES/NQ futures or executable ETF fills.
Overnight includes weekends/holidays; the cash exchange's non-trading period is not the same as a futures-market closure.

## 2. What does it find?

| Source result | Scope / interpretation |
|---|---|
| Table1,p.25: NASDAQ sample standard deviation0.007454 overnight versus0.013196 intraday. | Raw log-return volatility is lower overnight; this is not a comparison of tail losses or risk per clock-hour. |
| Table7,p.27: NASDAQ lower-tail innovation GPD shape xi0.183618 overnight (SE0.0442855), versus0.0441602 intraday (SE0.0382567). | Source rejects zero shape overnight but not intraday under its estimator/test. Positive xi means a heavier Pareto-type tail, not a profit signal. |
| Table7: significant positive lower-tail overnight shape for all four markets. | Conditional tail result after the fitted volatility model; not proof that every current overnight strategy has the same tail. |
| Table7: TOPIX upper intraday tail is also significantly positive. | The abstract's broad “intraday innovations do not” statement has this reported exception. |
| Table9,p.34: NASDAQ model-implied volatility1.058% intraday and0.858% overnight. | These are fitted-model unconditional volatility levels used in an illustration, not Table1's sample standard deviations. |

### The VaR trade-off is confidence-level dependent

Table9 sets conditional mean to zero and conditional volatility equal to fitted unconditional levels.
These are **illustrative model loss quantiles**, not observed trade losses or an out-of-sample VaR backtest.

| Confidence level | Intraday VaR | Overnight VaR |
|---|---:|---:|
|95%|1.804%|1.328%|
|97.5%|2.263%|1.796%|
|99%|2.891%|2.513%|
|99.5%|3.383%|3.142%|
|99.9%|4.586%|4.951%|

Thus heavier **standardized** overnight tails do not imply higher **total loss VaR at every level**.
The overnight tail outweighs its lower volatility only at99.9% among the displayed NASDAQ examples.
The source's prose calls the97.5% overnight innovation quantile higher, but Table9 shows2.092 overnight versus
2.138 intraday; follow the table rather than repeat that generalization. VaR also says nothing directly about
average loss beyond its cutoff; it is not expected shortfall or a worst-case guarantee.

### What remains unverified

- AR/TGARCH and GPD estimates depend on model specification, stationary-tail assumptions, index quote construction
  and threshold choice. The thresholds use about7–10% of innovations plus visual stability assessment (pp.11–12).
- Failure to reject xi=0 does not establish normally distributed innovations or prove that intraday tail risk is absent.
  An uncorrelated residual is not automatically independent or correctly calibrated in its extremes.
- Reported likelihood-ratio/tail tests and estimated risk parameters were not independently recreated here.
  The economic interpretation of overnight illiquidity is plausible, but these historical return distributions do not
  causally isolate liquidity, information accumulation, opening-price effects or any particular trader's behavior.
- Extreme-quantile extrapolation remains uncertain; a nominal one-in1000 probability is not a scheduled event once
  every1000 days, nor a guarantee against clusters or larger losses. No historical-vintage or walk-forward calibration
  test is supplied by the Table9 illustration.

## 3. Why does it make money, if it does?

**The paper establishes no money-making strategy.** It studies risk composition.
Its descriptive means include a positive historical NASDAQ overnight mean and a negative intraday mean, but it
does not turn that split into a costed, executable rule, establish a risk-adjusted alpha or measure account payouts.
Bearing overnight tail risk could require compensation; this paper does not demonstrate an exploitable net premium
available to us. Avoiding the night can change risk and return together, rather than create free profits.

The proposed risk mechanism is limited trading/liquidity while information accumulates, with adjustment at the open.
ES/NQ trade through much of that cash-market night, so their order availability, spread, depth, maintenance breaks,
Sunday reopen, halts and liquidation prices require separate measurements. A stop need not fill at its trigger price.

## 4. Can we build on it?

**Yes for risk and execution assessment; no new alpha test is warranted from this source.**
The smallest useful future application is to an already-frozen overnight/personal strategy: retain its chronological
mark-to-market path and actual session exposures, distinguish regular nights from weekends/holidays/reopens, and
assess downside exceedances alongside volatility. Compare like-for-like native contract data and include actual
fees, spreads, stop-gap behavior and margin/liquidation timing before making sizing claims.

If a GARCH/GPD risk model is later proposed, preregister windows, tail thresholds and benchmark first; fit using only
past information, test calibration on later matured observations, and compare with simpler empirical tail/volatility
baselines. More elaborate fitting is not justified by a source-only review alone. No new VaR model or sizing overlay
was fitted, and none is recommended for immediate installation.

Relevant existing evidence, not rerun:
- [Session attribution review](overnight_intraday_knuteson_review_20261029.md): separate return patterns from causal
  stories and reconcile cash-session attribution to the executable strategy ledger.
- `analysis/overnight_round.py` and the related repository overnight-family findings already address simple overnight
  long/trend ideas; a risk paper provides no new directional input to reopen them.
- [Monthly VRP proxy diagnostic](vrp_monthly_proxy_20261029.md): known monthly entry/exit profits did not certify
  daily/overnight risk when a daily mark was missing. This paper reinforces that distinction; it does not validate
  those endpoint drawdowns or change that negative filter result.

TIER_LIST, WATCHLIST, TODO and prior results were checked at the pinned head; no exact SSRN/title match found.
Retained in [EXECUTION_REFERENCES.md](../EXECUTION_REFERENCES.md), E15, as an overnight liquidity/tail-risk reference.
No TODO strategy-queue entry: there is no specific new profitable candidate with documented merits.

### Placement and decision

Personal: useful risk reference, **no new strategy allocation**. Both funded sizes and both evaluation sizes:
**no new eligible strategy**; no intraday signal is defined, and ordinary overnight holds conflict with our Apex remit.
No account bench ran, so no payout/pass-rate improvement or measured harm to any of the five homes is claimed.
Deeper investigation is warranted only when a concrete overnight candidate or risk-model decision makes it relevant;
there is no basis for a standalone strategy backtest from the paper alone.

For Claude: `agents/codex/results/overnight_tail_risk_review_20261029.md`.
