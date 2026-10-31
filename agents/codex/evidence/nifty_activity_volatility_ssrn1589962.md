# Nifty activity/volatility: DON'T TEST as a trading strategy

Summary: Source studies same-day cash-index variance against futures activity,
not a profitable strategy or verified future forecast. Daily surprise activity
is not available before that activity occurs. Printed model arithmetic also
weakens the claimed persistence result. Preserve a risk-feature caution only.

Source: Sakthivel & Kamaiah, SSRN1589962, user PDF in
`agents/codex/inputs/ssrn1589962/`; review in
`agents/codex/results/nifty_activity_volatility_ssrn1589962.md`.
Return trials: **0**. Arithmetic audit is not a strategy trial or return test.

## 1. Who trades and why?

The source hypothesizes joint information arrival behind unexpected futures
volume/open interest and cash volatility. No forced trader, exploitable demand
imbalance or causal identification is established. Its own method is not a test
discriminating the information theories discussed (p.3).

## 2. Direction, size, timing and information clock

No return direction, order size or trade rule is supplied. ARMA(5,5) decomposes
daily activity into expected and residual components. Full-day actual volume
cannot be known at the start of the day; official open-interest availability
requires a separate publication/receipt clock. The displayed variance regressions
include contemporaneous activity components. No rolling, past-only fit or
future-period forecast evaluation is shown. They cannot be assumed to be
pre-trade risk signals merely because one component is called unexpected.

## 3. Contract transmission

Nifty near-month futures and Nifty spot, July 2000–February 2008; no NQ/ES order
transmission or return evidence. Transfer to CME would require a new hypothesis,
contract/session treatment and fitted model rather than copying coefficients.

## 4. Data feasibility

Required exact inputs: Nifty daily close, dated near-month contract volume/OI,
roll/expiry mapping, transformations and publication clocks. The paper cites
NSE but provides no raw panel or forecast ledger. Local filename search finds
no Nifty or dated daily contract-OI price panel. The owned OF minute files have
volume/order-book fields, not a substitute for this Indian futures-OI sample.
No external acquisition is justified after the earlier no-strategy/clock gate;
missing data is not the sole reason for rejection.

## 5. Costs and intraday fit

No entries, exits, expected move, commission, spread, slippage or liquidity model.
No actual plan gap or native integer size is established. Volatility association
alone supplies neither a trading side nor a net gain from a filter. A risk feature
would need forecast loss and paired strategy/account outcomes before use.

## 6. Power

No trade count, per-trade return distribution or effect size exists to justify
a profitability power calculation. The number of daily observations does not
convert coefficient significance into economically useful trade opportunities.

## 7. Existing work and falsifiers

No exact SSRN1589962 review found before this one. Related TIER_LIST results:
VVG volatility/volume/gap classifier F and Donchian/LWTI/volume volatility-filter
variant D. Those do not disprove all activity-risk features, but cannot be
overturned by this different market's contemporaneous covariance result.
Future feature falsifiers: no out-of-sample forecast improvement over lagged
realized-volatility/ATR; no incremental paired net benefit; stale OI available
only after a decision; failure of variance validity/stability checks.

## 8. Failure and diversification

Unexpected activity can accompany widening spreads or price impact rather than
provide cheap liquidity. OI is outstanding contracts, not order-book depth or
signed buying pressure. A risk feature is not a hedge, and gives no demonstrated
offset before an Apex floor breach. Joint losses, actual order type, execution
and fail-safe behavior are unmeasured. Do not alter size, stop or entry filters.

## Decision and next gate

**DON'T TEST a return strategy from this paper.** Useful methodological caution,
not a promising strategy queue entry. A separately justified risk-forecast project
would need publication clocks, past-only estimation, valid variance parameters,
lagged price-only baselines and out-of-sample forecast gains before account tests.
No new strategy, portfolio, live setting, PowerLanguage or tier change.
