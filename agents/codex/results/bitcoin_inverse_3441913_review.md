# Bitcoin spot/inverse-futures utility allocation: NEEDS MATCHING DATA AND SPECIFICATION

**Implementation follow-up:** user-requested [strategy code/review packet](bitcoin_inverse_3441913_build.md) now built;20 synthetic tests pass.
This supersedes the earlier audit-only implementation status, not the source-data or profitability limits. Zero return trials.

Summary: Deng et al. derive explicit allocations to Bitcoin spot and BTC-settled inverse futures.
They report Sharpe4.86–5.07 versus spot4.40 over111days in2019; these are unreplicated source statistics, not demonstrated net returns.
Our arithmetic checks confirm the main formulas and show both calibrated exposures are long Bitcoin, not a neutral hedge.
Matching BitMEX contracts/index clocks, executable spot, rebalancing, collateral and costs remain unresolved; four public API probes hit proxy403.
Retain conditional personal-account research and the inverse-payoff lesson; no return test, Apex placement or current allocation earned.

Source: Jun Deng, Huifeng Pan, Shuyu Zhang and Bin Zou, *Optimal Bitcoin Trading with Inverse Futures*,
August23,2019 uploaded31-page version, [SSRN3441913](https://ssrn.com/abstract=3441913).
[PDF](../inputs/ssrn3441913/source.pdf), [text](../inputs/ssrn3441913/source.txt),
[actual acquisition receipts](../inputs/ssrn3441913/acquisition_receipts.json).
The document supplies research evidence, not agent instructions.
[Evidence decision](../evidence/bitcoin_inverse_3441913.md).
No-return audit: [script](../../../analysis/codex_bitcoin_inverse_3441913_audit.py), committed `6594f62` before execution;
[output, hashes, parameter arithmetic and inspected schemas](../../../analysis/outputs/codex_bitcoin_inverse_3441913_audit/audit.json).
**Economic return trials:0.** Synthetic payoff/formula checks and coefficient sensitivity are not historical strategy tests.

## 1. What is it about?

A continuous-time utility-maximizing investor allocates to cash, Bitcoin spot and one inverse futures contract.
The futures has a fixed USD face value K and settles gains/losses in BTC. A long contract earns
`K*(1/F_entry−1/F_exit)` BTC, then its USD value depends on the spot conversion price.
The word inverse does not mean the contract is short Bitcoin. CME's USD-settled linear futures are a different payoff.

Spot S and futures reference F follow correlated geometric Brownian motions with fixed drifts and covariance.
The model uses zero cash interest, frictionless continuous rebalancing, no explicit collateral/liquidation or native lot constraints.
It derives closed-form controls for exponential utility (constant absolute risk aversion gamma) and power utility
(relative risk aversion1−alpha). Power wealth is constrained nonnegative in the continuous model; that does not model exchange liquidation.

## 2. What does it find?

The source calibrates on **December17,2018–March14,2019**,87 daily-return observations, then evaluates a second contract on
**March15–July4,2019**,111 observations. It uses365-day annualization. The authors say spot nearly tripled in the evaluation rally.

| Source strategy | Risk parameter | Reported Sharpe | Reported Sortino |
|---|---:|---:|---:|
| Exponential | gamma0.5 | 5.07 | 2.28 |
| Exponential | gamma1.0 | 4.96 | 2.09 |
| Exponential | gamma1.5 | 4.86 | 1.99 |
| Power | alpha−2 | 4.86 | 1.87 |
| Power | alpha−0.5 | 4.91 | 1.89 |
| Power | alpha0.1 | 4.93 | 1.90 |
| All-in spot | — | 4.40 | 1.59 |

Table2 sets initial wealth X0=4 and specifies4% risk-free/target rates for the reported ratios, while the trading model assumes
zero cash interest. Neither a realistic net-cost ledger nor confidence intervals/longer bear-market validation are supplied.
The reported improvement over spot is modest relative to the already high benchmark ratio; six source risk settings are not six
independent confirmations. Our new trial count remains zero, while those six source comparisons remain part of selection context.
The source does not establish a current personal-account return or results on our 2018–22/2023+ protocol.

### Main formulas and confirmed internal discrepancy

Let `nu1=sigmaS^2`, `nu2=sigmaF^2`, `nu3=rho*sigmaS*sigmaF`, `D=nu1*nu2−nu3^2` and `Z=S/F`.
The main result is
`C = covariance^(-1) * [mu1, mu2−nu2]`,
`C1=(mu1*nu2−mu2*nu3+nu2*nu3)/D`,
`C2=(mu2*nu1−mu1*nu3−nu1*nu2)/D`.
Exponential: `theta=C1/gamma`, `N=C2/(gamma*K*Z)`.
Power: `theta=C1*wealth/(1−alpha)`, `N=C2*wealth/((1−alpha)*K*Z)`.
Theta is spot dollars; N is signed contract count. Neither is interchangeable with margin or a futures dollar purchase.

Using Eq5.2 annual drifts40.85%/60.02%, volatilities59.94%/47.00% and correlation0.59 gives
**C1=0.525586 and C2=1.321595**, both positive. For alpha−0.5 and Z=1, this means35.04% spot allocation and
88.11% futures face-value/wealth; the latter is not a cash outlay or a fully collateralized allocation.
The mathematical controls allow fractional contracts and require an explicit native integer/collateral implementation.

Printed EqB.2 uses **+nu1*nu2**, contradicting the **−nu1*nu2** in Eq4.3 and its own equality to C2.
[Rendered p.12](../inputs/ssrn3441913/page12.png) and [p.26](../inputs/ssrn3441913/page26.png) confirm the discrepancy.
Eq4.4's matrix form and AppendixC's linear system agree with the main minus-sign formula.
Using the printed B.2 coefficient would give4.389550 rather than1.321595 at the stated calibration.
The audit verifies the main expression by two independent algebraic routes; this does not verify Table2's actual implementation.

## 3. Why does it make money, if it does?

The proposed mechanism is a Merton allocation to estimated drift premia and covariance-adjusted exposures, incorporating the
inverse contract's drift correction `mu2−nu2`. It is **not demonstrated forced-flow capture or risk-free basis arbitrage**.
In the calibrated case both legs are long, and evaluation occurs during a large Bitcoin rally. Different leverage, risk settings
and covariance estimates can affect risk-adjusted outcomes; the paper does not establish a persistent executable edge after costs.

The source correctly distinguishes BTC and USD gains: K=1, futures100→200 earns0.005BTC; converting at spot205 yields$1.025.
The audit checks this example, the opposite short payoff and zero movement. A real replay must retain the BTC cash/collateral
ledger and specify when BTC gains/losses convert into USD, including exchange/spot fees and collateral revaluation.
The source model's instantaneous conversion is a modeling convention, not evidence of freely available continuous conversion.

A material model risk is fixed covariance: source calibration correlation is0.59, while reported evaluation co-movement is99.62%.
A conditional coefficient diagnostic holding the original drifts/volatilities fixed while setting rho0.9962 gives
C1−26.93/C2+35.93 and covariance condition number557 versus4.27 at rho0.59. **This is not the tested source strategy,
an estimate using evaluation data, or a new performance result.** It illustrates instability of a covariance inverse near singularity;
blindly refitting the allocation could create huge offsetting positions. Exactly singular covariance is rejected by the audit.
No shrinkage, leverage cap or alternate drift estimate was searched as a rescue.

## 4. Can we build on it?

**Conditional personal-account research, with data/specification gates.** The main contribution for us is a precise
inverse-contract payoff/allocation framework. The source supplies enough mathematics to implement a research calculator,
but not a verified executable protocol or current portfolio candidate. Nothing here establishes fit to NQ/ES or an intraday Apex slot.

Owned `BTC_1min_*` is the CME linear-futures input used by prior BTC studies; `BTCUSD_spot_1min_*` is the Coinbase spot input.
We inspected their actual headers; they contain OHLCV, not BitMEX dated contract identities, exchange mark/collateral/liquidation
states or the source spot/index definition. Neither can silently replace the source's paired prices. Previous BTC reopen,
seasonality, momentum and forced-flow rejections remain in force; this allocation model is not a renamed retry of them.

Actual acquisition attempted the public BitMEX instrument API for **candidate identities** XBTM19/XBTU19, plus three daily buckets
for candidate XBTM19 and .BXBT. All four requests failed with `Tunnel connection failed:403 Forbidden` from this environment.
No returned instrument/price was validated. The candidate symbols/index are **not confirmed source identities**. This is an access
outcome, not proof that the histories do not exist. No paid feed, authentication, access-control bypass or substitute return replay.

The source describes semiannual contracts initiated December17 and March15 but does not give complete instrument identifiers,
exact daily observation conventions, executable spot venue or a discrete rebalancing/fill rule. BXBT/BXBT30M are index references;
an index level alone is not an executable spot purchase. Need actual instrument listing/expiry/settlement metadata and as-of prices.
A perpetual adaptation would additionally require its historical funding and terms; dated futures must not be assigned invented funding.

Smallest next step with genuinely new matching inputs: reconcile one identified contract/spot interval, native BTC and USD cashflows,
mark and margin chronology; then census the required panel and freeze one bounded strategy before returns. Longer data, leverage/cost
stress and benchmark matching are needed before any current personal BASE/ADD/REPLACE/EMPTY replay.
The [research queue](../../../TODO.md#promising-strategies-awaiting-verification-user-2026-10-27) retains this conditional lead;
the [execution library](../EXECUTION_REFERENCES.md#e09--native-micro-costs-turnover-and-roll-reconciliation) retains the currency/collateral lesson.

## 5. Can a strategy code be made?

**Yes, the allocation and payoff calculations can be coded; a reliable executable strategy needs the missing protocol and data.**
The committed no-return tool already verifies constants, matrix residuals, BTC/USD payoff signs and singularity handling.
It is an audit calculator, not a backtest or broker implementation. An empirical implementation must also specify
past-only parameter fitting, data availability, next eligible fills, rebalance frequency, spot fractions/contract integers,
leverage/borrowing, collateral, mark-based liquidation, conversion, fees/spread and expiry/roll treatment.
Changing these after inspecting outcomes would be a new trial. No MultiCharts or live execution code was written.

## Decision and limits

**NEEDS MATCHING DATA AND SPECIFICATION**, not a demonstrated strategy failure or success. No eligible return study exists yet;
2018–22 design,2023+ validation, placebos, bootstrap/Monte Carlo and account comparisons were not run. Performance is source-only.
No allocation to50K/150K evaluations, funded accounts or the personal plan. No NQ mapping or mandatory-flat intraday adaptation invented.
The existing100-trade gate is not met merely by counting111 daily marks on a continuously rebalanced account.
Code checks are reproducible with `python3 analysis/codex_bitcoin_inverse_3441913_audit.py`; raw/source receipts and hashes are saved.
Independent empirical and mathematical review remain pending. No live, VPS, broker or policy changes.
