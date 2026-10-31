# Pension stress and municipal services: DON'T TEST as a trading strategy
Summary: Rao studies city pension underfunding, public services, social equity and employee benefits.
The dataset covers 1,842 city-sponsored pension plans over 1997–2018, primarily contracted CalPERS plans.
The author reports persistent fiscal spillovers, not a stock-return or pension-rebalancing strategy.
Monetary effect units are inconsistent across sections; no market direction, execution lesson or strategy test follows.

Source: Manita Rao, *Mitigating Pension Stress? The Impact of Public Pensions on Services, Equity, and Employees*,
cover date 01/11/2022, [SSRN 3980117](https://ssrn.com/abstract=3980117), user-uploaded PDF.
SHA256: `bf06c8511a0c59ef069df6359e5cc47c20aebd1aa91e6fd1329a8599c71b6a64`.
Reviewed 2026-10-29. Source-only findings, not independently reproduced. New return trials: **0**.
Repo context: codex/work `15988e292ae3edd3c7fb872a6f3fa0e2c1f742ad`.

## 1. What is it about?

How unfunded public pension obligations affect spending on city services and the generosity of public
employees' pension benefits. “Equity” means distributive/social equity, not equity-market returns.
The 1997–2018 dataset includes 1,842 city-sponsored plans covering firefighters, police and general employees.
Pension data obtained by public-records request from CalPERS are joined to municipal fiscal and demographic data.
This is not a study of trading by 1,842 independent investment managers: contracted plans share investment administration.

The author estimates dynamic fixed-effects models of future spending/benefit outcomes using pension asset values,
unfunded actuarial liabilities and interactions, alongside controls. Outcomes run over fiscal years, not intraday bars.

## 2. What does it find?

The author reports that pension underfunding spills over into lower public-service spending and employee benefits.
The categories include public safety, economic development and redistribution; effects can persist over later years.
Asset gains partially mitigate the fiscal pressure. Pension stress also changes the relationship between union
bargaining strength and employee benefit outcomes.

Two important qualifications:
- **Causal interpretation is conditional.** The author uses external investment shocks to motivate identification.
  Section 4.2 proxies asset shocks with market value of assets in the displayed fixed-effects specification.
  Common investment governance can limit local portfolio-choice confounding, but does not automatically rule out
  other channels linking markets, local revenue and spending. This source review does not independently validate
  the claimed causal interpretation or resolve identification concerns.
- **Reported monetary units conflict.** The introduction states 15–17 cents less services per additional pension
  dollar; the results/conclusion use “0.17 cents” and “0.15 to 0.17 cents.” Those differ by a factor of 100.
  Coefficient-to-percentage-point wording also needs reconciliation to the transformations.
  Do not choose a figure silently or reuse the precise dollar magnitude before checking the data/code.

References: abstract; introduction pp.3–5; data/strategy pp.14–17; results pp.19–21; discussion pp.29–31.
These are fiscal outcomes, not alpha, return forecasts, fill savings or a trader's success rate.

## 3. Why does it make money, if it does?

It does not demonstrate a money-making trade. The economic channel is budget pressure: funding pension
obligations competes with other expenditures, while investment gains can ease that pressure.
No tested stock/bond/futures trade, entry time, transaction costs, drawdown or net portfolio performance is reported.

An underfunded pension need not sell equities on a particular day. Contributions, benefit payments, asset
allocation, borrowing, governance and actuarial rules can lead to different responses.
Fiscal stress alone does not identify a signed market order, much less an exploitable ES/NQ price response.

## 4. Can we build on it?

It can inform public-finance or municipal-credit research, but there is no ready basis for our intraday strategies.
Even a municipal-credit application would need issuer/plan linkage, dated disclosures, bond prices/yields, liquidity
and issuance/credit controls; this paper does not establish that such a trade works.

For a pension-flow strategy we instead need allocation mandates, contemporaneous assets/weights, contribution/
benefit-payment calendars, actual execution constraints and netting/hedges. None is established as an executable
market signal by these fiscal regressions. Annual plan information cannot reconstruct timed rebalancing orders.

TIER_LIST already records separate pension/balanced-fund rebalancing tests with weak results. This paper neither
validates nor directly refutes them; it does not supply an incremental signal warranting another trial.
No exact SSRN match was identified in the inspected TIER_LIST, WATCHLIST or current TODO queue.

## Decision and retention

**DON'T TEST for the trading plans.** No new evidence-sheet candidate or strategy-queue entry is justified.
No distinctive execution method is established, so EXECUTION_REFERENCES is unchanged; do not pad it with an unrelated
fiscal study. The source and review remain available here if a future public-finance question arises.
No backtest, data acquisition, code, account change or live/VPS operation. No claim about payouts or diversification.

For Claude: `agents/codex/results/pension_fiscal_stress_review_20261029.md`.
