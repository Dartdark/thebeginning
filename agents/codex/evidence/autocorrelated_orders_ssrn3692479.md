# Autocorrelated uninformed orders: DON'T TEST as a new alpha strategy

Summary: The source extends a Kyle-style theoretical market, not a public-data
trading rule. Its pricing update subtracts expected flow; autocorrelation alone
does not establish predictable returns. Private-signal model profits and numerical
liquidity shapes do not supply a calibrated NQ/ES execution or alpha policy.

Source: Vladislav Gounas, *Information in Noise: Strategic Trading under
Autocorrelated Uninformed Orders*, 2021-03-15, SSRN3692479.
PDF/hash: `agents/codex/inputs/ssrn3692479/`.
Review: `agents/codex/results/autocorrelated_orders_ssrn3692479.md`.
Return trials: **0**; no new strategy or parameter family.

## 1. Who trades and why?

Informed agents trade private asset-value signals; uninformed orders have an
assumed correlation structure. Target rebalancing/order splitting are motivations
and cited-model examples, not an identified institution's observed schedule or
measured demand. The paper's equilibrium market maker already anticipates the
predictable component. No new mispricing mechanism for our public-data trader.

## 2. Direction, size and information clock

In each batch auction agents submit quantities; the maker observes aggregate
flow, sets the clearing price, then price and flow become public. Full current
auction flow cannot be used to choose an earlier order at a previous quote.
Private signals arrive before trading and the terminal asset value is revealed
after the last round. Those are model information assumptions, not data we own.
No native contract, economic size or executable decision-to-fill clock is given.

## 3. Transmission

One stylized risky asset. There is no instrument-specific NQ/ES hedge, mandate,
dollar demand or account exposure. A model of information transmission is not
evidence of an unpriced CME flow at a particular time.

## 4. Data feasibility

The source supplies no empirical dataset, estimated latent informed/uninformed
labels, realized fundamental-value series, native quotes or order/fill ledger.
Our OF minute bars contain aggregate volume, delta and book features, not the
model's private signals or separately observed uninformed order process.
Autocorrelation is not a reliable identity label for a real trader. No external
acquisition or proxy backtest is justified by this source-only gate failure.

## 5. Costs and plan gaps

The model uses market orders in sequential batch auctions and competitive
conditional-expectation prices. It does not model a CME limit-order book,
queue/fill delays, explicit spread/commission or actual micro sizes. No positive
public-data gross edge, cost hurdle or eligible intraday opportunity window is
demonstrated. A lambda curve is a theoretical price-sensitivity parameter, not
measured cost per contract or a preferred execution hour.

## 6. Power

Numerical examples use three informed traders and ten model auctions; these are
not historical trades. No public-signal effect size, per-trade variance or
opportunity count exists for a return power calculation.

## 7. Existing evidence and falsifiers

No exact ID/title match before this review. Existing TIER_LIST order-flow
prediction results found no useful 5–30-minute NQ edge after costs. That does
not disprove all innovation features; it prevents relabeling failed raw-flow
predictors as new evidence. Execution references E25, E40 and E54 distinguish
flow predictability, price impact, risk and information clocks.
Any separately justified future innovation test must beat price-only and raw-flow
baselines with past-only forecasts and future executable outcomes after costs.
Failure does not authorize a parameter rescue or restarting failed families.

## 8. Failure and diversification

Wrong flow expectations, news shocks, rapid repricing and changing impact may
make timing worse. An estimated residual can reflect model error rather than
private information. Marketable orders can pay spread/adverse selection; no
tail hedge or offset before an account breach is demonstrated. Actual concurrent
losses and account contribution are unmeasured. Do not change orders or sizes.

## Decision

**DON'T TEST a new return strategy from this source.** Retain the market-impact
interpretation as an execution reference. Any future execution comparison must
have its own fixed parent signals, available-at clocks, quote/fill evidence,
native costs and paired original-timing control. No current research-budget,
promising-queue, plan or live change is earned by the theoretical model alone.
