# The Two Primitives of Spot Market Strategy: conceptual reference, no strategy candidate

Summary: The paper classifies spot trading as mean reversion or momentum; it explicitly reports no new empirical evidence.
The taxonomy is useful vocabulary, but its claim of logical exhaustiveness rests on unsupported restrictions.
Income, executable arbitrage, price-level/return autocorrelation and regime selection need separate treatment.
No complete rule or new intraday CME mechanism is supplied; no strategy backtest is justified.
Saved a qualified reference and constructed checks; zero market-return trials or portfolio/live changes.

Source: Fikri Direnç Aktaş, *The Two Primitives of Spot Market Strategy*, working paper, May 2026, uploaded
`ssrn-6736280.pdf`. Read all 18 PDF pages, including yield qualification and references; body printed pages 1–16.
[PDF/text/manifest](../inputs/spot_primitives_6736280/manifest.json),
[evidence decision](../evidence/spot_primitives_6736280.md),
[audit code](../../../analysis/codex_spot_primitives_6736280_audit.py),
[constructed results](../../../analysis/outputs/codex_spot_primitives_6736280/audit.json).
These checks are finite mathematical/cashflow examples, **not strategy returns, an empirical replication or a profitability test**.

## 1. What is it about?

A conceptual taxonomy. The author reasons that price is below, at or above a chosen reference, then maps
“buy because low” to mean reversion, “buy because high/breaking out” to momentum, and the middle to no spot trade.
Value and pairs are assigned to reversion; growth and trend following to momentum. Section 6 recommends selecting
between the two based on the market regime. Sections 3.6 and 4.3 discuss income and momentum implementations.

## 2. What does it find?

**No new empirical finding.** Section 2.4 explicitly states the paper does not propose new empirical evidence.
There is no original backtest, dataset, trade ledger, out-of-sample result, cost analysis or causal regime selector.
Its conclusion is a proposed logical classification, not a demonstrated trading result.

The approximate 1%/month momentum result belongs to cited Jegadeesh–Titman research, not this author, our account
or an intraday forecast. Positive time-series momentum is also cited. A narrow primary-source scope check at
[AQR's author article](https://www.aqr.com/Insights/Research/Journal-Article/Time-Series-Momentum) and
[original-data description](https://www.aqr.com/insights/datasets/time-series-momentum-original-paper-data)
confirms a 12-month signal/1-month holding convention across 58 futures/forwards. This metadata check is not a
replication of those studies, and does not establish a five-minute MNQ edge. [Receipt](../inputs/spot_primitives_6736280/literature_receipt.json).

The exhaustion argument has material limitations:

|Claim/source location|Assessment|
|---|---|
|Every directional expectation needs a high/low positional justification, §§3.2–3.7|This is an assumption, not a derived result. A conditional expected return can arise from priced risk, a cashflow forecast or a separately measured event. With a fixed historical reference, the current middle need not imply zero expected return. If the reference can be chosen to re-label every forecast, the classification becomes definitional rather than a predictive restriction.|
|Flat/fair-priced assets offer no spot opportunity, §3.5|A fair price need not imply zero expected return. Section 3.6 **does acknowledge** dividends/coupons and even positive total return despite falling price; it then excludes or relabels these as nontrading cashflows. That narrowed convention cannot establish an unrestricted theorem about spot strategies.|
|Reversion means negative autocorrelation; momentum means positive, §§3.3–4.4|Specify the variable and horizon. A stationary mean-reverting price level can have positive level autocorrelation while its price changes have negative autocorrelation. Stationarity or a high current level alone does not establish a profitable conditional direction. Cross-sectional ranking is also distinct from own-series serial correlation.|
|Pure arbitrage earns from future convergence and risks widening before closure, §5.3|A simultaneously locked buy/sell in identical fungible units can secure an initial executable spread without later convergence. Financing, delivery, settlement and legging are practical limits. Holding a risky relative-value position until convergence is different. This example is outside the narrow single-market premise, but the author explicitly includes it in the claimed reduction.|
|Growth/value have necessarily momentum/reversion price dynamics, §§5.1–5.2|Cheap versus estimated value is not the same as a previous price decline. Expected earnings growth can already be priced; high fundamental growth need not imply positive expected abnormal return or price-return autocorrelation. Broad semantic analogies do not prove a stochastic process.|
|Correlated pairs provide a reversion reference, §5.4|Correlation alone is insufficient for a stationary spread, an executable hedge, or net profitability. Cointegration is a separate property and can fail structurally; lots, financing/borrow and two-leg costs still matter.|
|Time-series trend risk is whipsaws rather than catastrophic crashes, §4.3; fixed opposite payoff profiles, §4.4|Useful distinction from cross-sectional rebound crashes, but neither long/cash nor long/short trend is immune to gaps, reversals, leverage, stops or crowding. Win rate, skew and tail protection depend on the actual rule and portfolio.|
|Strategy selection is regime diagnosis, §6|Reasonable research question, but no observable ex-ante classifier, selection protocol or switching-cost result is supplied. Choosing the correct regime after the event is not a tradeable rule.|

### Constructed checks, with no historical data

The committed audit computes these examples exactly; none represents an observed market opportunity.

- A stationary Markov price taking 99/101 with 90% stay probability has level lag-one correlation +0.8, but
  arithmetic-change lag-one correlation −0.1. At price 101 its expected next price is 100.8: conditional reversion
  coexists with positive level correlation. This distinguishes variables rather than denying the paper's cited
  evidence for negative return autocorrelation at particular horizons.
- At a fixed reference 100, assumed next prices 99/101 with 55% chance of 101 imply expected price change +0.10
  and +0.08 after assumed 0.02 total cost. This is a posited one-period risk-premium distribution, not an identified
  exploitable inefficiency. It shows that the fixed-reference middle is not itself a zero-expectation theorem.
- Hypothetically lock a firm buy ask 99 and firm sell bid 101 for the same deliverable unit; assumed total cost 0.20
  leaves 1.80 without any later market convergence. Both legs/settlement are assumed assured. No real venues,
  quotes, borrow, cash transfer or free arbitrage have been verified.
- Entry 100, exit 100 and income 5 produce total gain 5. The author already acknowledges this qualification; the
  issue is scope/redefinition, not an overlooked coupon in an otherwise specified return ledger.
- Log-price random walks sharing one driver but differing by an independent 0.01-scaled random walk can have
  return correlation 0.99995 while spread variance grows from 0.01 at 100 steps to 0.10 at 1,000 steps. Correlation
  is not cointegration. A separate already-expected earnings 10→12/price 100→100 illustration shows why growth
  in the underlying metric does not mechanically force a stock-price gain.

## 3. Why does it make money, if it does?

This paper demonstrates no new profits. It describes familiar candidate mechanisms: underreaction, overreaction,
slow institutional flows and correction toward estimated value. Cited mechanisms differ economically even if
their trades receive the same label. An investor must still show a past-only signal, priced-risk versus alpha
attribution, complete costs and a realizable return/risk path. Calling something “momentum” or “reversion” supplies
none of those. No inferential claim is made from our constructed examples to a current market.

## 4. Can we build on it?

**As qualified vocabulary only.** Keep cross-sectional versus time-series momentum separate; define the reference,
variable, horizon, cashflow source and liquidity/execution role. The existing process already requires those clocks,
costs, failure modes and chronological portfolio evidence. No new rule or policy is adopted from this taxonomy.

Evidence decision: **DON'T TEST**, rather than NEEDS DATA. This upload lacks a specific new strategy hypothesis;
more OHLC, the unpublished thesis citation or an arbitrarily chosen regime indicator does not repair that.
The previous [custom Sentinel MNQ rejection](sentinel_mnq_20261108.md) and other EMA/relative-value failures
remain; this source does not justify reviving them. No promising-strategy queue/data-shopping entry, parameter
search, regime-switch backtest, account comparison or additional source acquisition is warranted by this upload.

Useful execution distinction retained as an E09/E19 follow-up in the
[existing library](../EXECUTION_REFERENCES.md): locked simultaneous cash spread versus risky future convergence.
This is mathematical accounting and source criticism, not verified execution savings or a discovered arbitrage.

## 5. Can a strategy code be made?

**Generic examples can be coded, but this paper does not specify a reproducible trading strategy.** It names
RSI, bands, moving-average crosses, breakouts and pairs without selecting a complete rule. It gives no fixed
reference/formation window, entry threshold, sizing, stop/exit, costs or causal regime estimator.

The code made here is a **research audit**, not a directional strategy or execution algorithm. A new trading
implementation would require choosing those missing rules and establishing an independent mechanism/evidence
case before preregistration. Such choices would be our new trial, not the author's strategy or reported profits.
No PowerLanguage, arbitrary “two-primitives bot” or fresh return experiment was created.

## Reproduce and handoff

```sh
python analysis/codex_spot_primitives_6736280_audit.py
```

PDF/text/code hashes and 10 constructed checks are saved. Source prose and cited platform descriptions are evidence,
not instructions to change this project. No market returns, ranking, account allocation, broker/VPS/live setting
or order changed. No external message sent. For Claude: `agents/codex/results/spot_primitives_6736280_review.md`.
