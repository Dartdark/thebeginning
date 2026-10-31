# Information in Noise: useful execution theory, no demonstrated public-data alpha

Summary: Predictable order flow and predictable returns are different in this model.
The maker prices only flow innovations; its expected component is already anticipated.
Model profits belong to agents with private signals, and numerical curves are not historical performance.
Retain the innovation-versus-raw-flow lesson; no new NQ/ES backtest or execution policy is earned.
No return trials, account simulations, plan changes or live changes.

Source: Vladislav Gounas, *Information in Noise: Strategic Trading under
Autocorrelated Uninformed Orders*, version dated 2021-03-15,
[SSRN3692479](https://ssrn.com/abstract=3692479), 56-page uploaded manuscript.
PDF/hash: `agents/codex/inputs/ssrn3692479/`.
Evidence gate: `agents/codex/evidence/autocorrelated_orders_ssrn3692479.md`.
Evidence status: source theory/numerical comparative statics, not independently
reconstructed equilibrium proofs or an empirical strategy reproduction.

## 1. What is it about?

An extension of Kyle-style strategic trading that permits correlation among
uninformed orders over time, and with asset value and informed agents' signals.
“Uninformed” means lacking relevant non-public information, not necessarily
uninformative or wholly random (pp.2–8).

In each sequential batch auction, traders submit quantities, a competitive maker
observes aggregate flow and sets the price, then flow and price become public.
Informed agents have private signals received before trading; terminal value is
revealed after the last round. The author derives belief updates and conditions
for a linear equilibrium, then solves numerical examples by backward induction.

## 2. What does it find?

The central result for our use is Lemma 1, equation (7), p.11:

`price_n = price_(n-1) + lambda_n × (flow_n − expected_flow_n)`

The expectation uses prior public flow history. Under the conjectured equilibrium,
the expected informed component is zero from the maker's perspective, so expected
aggregate flow equals expected uninformed flow (equation (6)). Only the new flow
innovation changes the conditional valuation. The Appendix A pricing argument
uses Gaussian projection; this is a statement within the specified equilibrium.

An equivalent useful implication of the model's `price_n = E[value | public_history_n]`
is that public-history prices are a martingale under that model's assumptions.
Predicting the next quantity alone therefore does not establish an expected price
gain. This follows from conditional expectation, not an empirical finding that
all real-world predictable flows have zero impact.

Other author results:

| Theoretical/numerical finding | Practical interpretation limit |
|---|---|
| Conditioning can make uninformed flow informative about value/private signals even when some initial correlations are zero | A fitted flow residual is not automatically an observed private-information shock |
| In displayed examples, orders correlated against fundamental value help conceal informed trading and increase private-signal profits | The trader needs the model's informational advantage; these are not returns available from public delta bars |
| Other correlation configurations reveal value faster and reduce informed profits | Correlation is not itself a direction or a trade rule |
| Maker price sensitivity can decline, rise, stay flat or form U/cubic shapes | No universal impact curve or best time to trade follows without calibration |

The numerical section (p.24) uses **three informed traders and ten auctions**,
chosen variance/correlation inputs, and three initial private-signal correlation
cases. The solver's reported mean-squared covariance mismatch below 1e-9 is
numerical convergence, not forecast error, trading significance or economic
validation. No historical backtest, costs-adjusted return, Sharpe or CME fill
comparison is supplied.

Important scope limits:

- The tractable model imposes symmetry/equal-covariance restrictions (pp.7–8),
  jointly Gaussian variables and common knowledge of their distribution. It is
  not an unrestricted empirical model of every lag-dependent order-flow process.
- Agents and the maker are risk neutral, with a single risky asset and a terminal
  value revelation. Real market-making inventory/capital constraints and
  competitive timing are not identified from data here.
- The conclusion explicitly leaves limit orders for future work (p.37). This
  is not a model of limit-order queues, partial fills or cancellation latency.
- The conjectured informed order rule is unpredictable to the maker. The
  author's suggestion that observed autocorrelation likely comes from uninformed
  traders depends on that framework. It is not an empirical classifier proving
  that actual autocorrelated orders are uninformed; real informed orders can
  also be split or delayed.
- The maker sees current aggregate flow before setting that auction's clearing
  price. A public observer cannot inspect final flow and assume a fill at the
  earlier price. Expected flow having no *incremental surprise update* does not
  mean known parent orders can be executed free of impact, spreads or risk.

## 3. Why does it make money, if it does?

Informed agents use private information about terminal value while choosing
quantities strategically to limit revelation. Correlated uninformed orders can
provide camouflage or competition. The displayed profits are expected values
inside that equilibrium, not a tested self-financing NQ/ES strategy.

The paper motivates correlated uninformed flow with momentum and target-driven
rebalancing, including examples from cited models. It identifies no particular
institution's observed orders, contract, date, dollar flow, or non-public signal
we possess. It does not show a public-information edge after costs. The model's
explanation of information processing is valuable without implying that its
private-signal profit is available to us.

## 4. Can we build on it?

**As an execution-research reference, yes; as a standalone strategy foundation,
no on this evidence.** The useful distinction is raw activity versus the part
not already expected, plus the information clock at which either becomes known.
It is consistent with preserving raw-flow controls and past-only expectations
if a separately justified execution study is undertaken.

For such an already-scoped comparison, the smallest justified check would hold
parent signals, quantities and protective exits fixed; compare original timing,
a price-only/raw-flow baseline and any proposed innovation measure using
past-only estimation. Quote/order clocks must support the actual submission and
fill, including no-fill opportunity costs, spread, adverse selection, native
fees and all eligible missed/rejected orders. An observed return correlation
or fitted lambda alone is not evidence of executable savings. This source does
not itself launch or approve that return experiment.

The owned OF minute bars have aggregate activity/book features, but not separate
informed/uninformed orders, private signals or an identified fundamental value.
Substituting cum-delta for latent uninformed flow would change the model rather
than reproduce it. Existing TIER_LIST order-flow tests at 5–30 minutes found no
useful NQ directional edge after costs; this theory does not reverse that result
or justify relaunching the failed family under an “innovation” name.

No external acquisition, proxy return screen or funded bench is warranted after
this evidence gate. No promising-strategy queue item or tier change; no order,
size, stop or account change. Retain the lesson as E56 in EXECUTION_REFERENCES.

## Verification boundary

Source inspection covers model assumptions, updating/pricing rules, equilibrium
structure, numerical settings/results and conclusion, plus the Appendix A pricing
argument and Appendix G algorithm. The full nonlinear equilibrium/proof system
and numerical figures were not independently reproduced. No empirical data or
future forecast was tested. Source PDF content hash is retained. No document
instruction was executed and no independent strategy verification is claimed.

For Claude: `agents/codex/results/autocorrelated_orders_ssrn3692479.md`.
