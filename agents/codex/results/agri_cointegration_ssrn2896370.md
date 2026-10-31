# Agricultural cointegration pairs: REJECT as a strategy foundation

Summary: The paper claims profitable cotton/coffee and cotton/cattle convergence trades.
Its trading-period evidence is only two and three completed trades, with costs ignored.
Trade-direction prose contradicts the profit formulas; native sizing and return denominators are unresolved.
Months-long holds do not fit Apex; the evidence also fails the personal-account research gate.
No return tests or plan changes; retain the execution/accounting lesson only.

Source: Cüneyt Ungever, *Pairs Trading to the Commodities Futures Market Using
Cointegration Method*, International Journal of Commerce and Finance 1(1),
2015, pp.25–38; [SSRN2896370](https://ssrn.com/abstract=2896370).
User PDF: `agents/codex/inputs/ssrn2896370/source.pdf`; SHA-256 in its manifest.
Evidence gate: `agents/codex/evidence/agri_cointegration_ssrn2896370.md`.
Return trials: **0**; all quoted performance below is author-reported, unverified.

## 1. What is it about?

Fit Johansen cointegration relations among ten agricultural futures, then fade
residual deviations of ±1.5 standard deviations until return to the mean.
The source screens 45 pairs over five alternative formation lengths. It chooses
the longest formation period (2004-12-01–2011-12-01, 1,765 observations) because
it finds the largest number of cointegrated pairs: seven. An AR(1) residual
criterion leaves coffee/cotton and cotton/live cattle (pp.28–30).

The trading period is 2011-12-02–2015-05-01, 859 daily observations. The data
are Bloomberg rolled nearby futures; holidays are forward-filled and positions
are described as $100,000 long/short values. It is a multi-month holding strategy,
not an intraday relative-strength rule.

## 2. What does it find?

| Author's trading-period result, p.33 | Coffee–cotton | Cotton–live cattle |
|---|---:|---:|
| Completed trades | 2 | 3 |
| Mean holding duration | 159 days | 142 days |
| Claimed total profit before costs | $48,909 | $372,343 |
| Claimed average annualized return | 17.4% | 358.5% |

These annualized figures are not independently verified portfolio CAGRs.
The paper calls returns statistically significant (p.34), but does not provide
a trade-return significance calculation supporting that claim. Cointegration
test significance is not a test of profitable trading.

Material reasons not to accept the headline:

- **Direction is internally inconsistent.** Page 30 says the upper-bound entry
  shorts cotton and buys coffee. Page 31's upper-bound profit equation instead
  earns cotton's price rise plus coffee's price fall: long cotton/short coffee.
  The lower-bound description/formula reverse each other too. This was checked
  in the rendered PDF, not inferred solely from extracted equations. We cannot
  silently choose the profitable interpretation.
- **Hedge and cash accounting are incomplete.** Log-price coefficients
  (coffee −0.6666×cotton; cotton −2.5023×cattle, p.29) are not native futures
  contract counts. Equal dollar legs, derivative exposure implied by those
  coefficients, and integer contracts are different portfolios. Contract
  multipliers, rebalance/roll cash flows, margin and the annualization denominator
  need a ledger before the reported hundreds-of-percent result is usable.
- **Costs are explicitly ignored** (p.27), despite a contradictory preceding
  nominal cost sentence. Each pair pays costs on both legs, including rolls.
- **Only five completed trading-period trades in total.** Correlated daily marks
  are not hundreds of independent trades. The two pairs also share cotton.
- **Selection and stability risk.** Forty-five pairs and five formation lengths
  were inspected; the chosen window maximizes discovered relationships. No
  multiplicity-adjusted trading evidence or rolling stability test is supplied.
  The source assumes the fitted relationship persists into trading.
- **Availability and data conventions are unresolved.** A signal using a daily
  close cannot assume a fill before that close is known. Holiday forward-fills
  are not tradable synchronized quotes; contract rolls/adjustment conventions
  can affect a fitted price-level relationship. The paper gives different
  trading-period spread means/deviations; their reporting alone does not prove
  look-ahead, but threshold fitting clocks are not demonstrated clearly enough
  for replication. No claim of a proven leak is made.

## 3. Why would it make money?

The proposed mechanism is convergence of a historically stationary residual.
No forced trader or economic linkage ensuring cotton converges with coffee or
cattle is established. The paper explicitly says it does not address the source
of profitability (p.34), then discusses volatility and mean reversion as possible
explanations. Those are hypotheses, not causal evidence or verified net alpha.

Cotton and cattle can respond differently to supply and demand shocks for long
periods. Cointegration in one selected sample is neither an arbitrage obligation
nor proof that losses remain small before eventual convergence.

## 4. Can we build on it?

**Not as a new trading foundation on this evidence.** Apex cannot hold these
positions for 142–159 days. Converting the rule into daily-flat NQ/ES trades would
change instruments, clock and mechanism; the repository already contains negative
index-pairs evidence. A personal account can hold multi-day positions, but that
permission does not repair the statistical and accounting shortcomings.

Local `data/` and Codex-input filename searches found no matching cotton/coffee/
cattle price histories. No external data purchase or proxy backtest is justified
for a source failing the earlier mechanism/specification gate. The paper was not
already recorded by SSRN ID; this review avoids reviving the distinct rejected
NQ/ES, NQ/YM and signature-pairs families. No promising-strategy queue entry is
earned; this is a rejection on source quality and fit, not merely NEEDS DATA.

The smallest action that could reopen it is an author/supplement ledger resolving
direction, contract quantities, roll returns, capital denominator and dated fills,
plus stronger independent net evidence. None is requested or assumed available.
If later supplied, a new bounded past-only protocol must precede any return test.

Useful retained lesson: turn fitted log-price coefficients into an explicit
integer futures hedge and full two-leg execution ledger before calling a spread
market neutral or interpreting its annualized return. See E44 in
`agents/codex/EXECUTION_REFERENCES.md`.

## Work completed and verification boundary

Read all 14 PDF pages; inspect the rendered p.31 equations; check exact-ID and
related-strategy repository hits; inspect available local instrument files.
Preserve the uploaded PDF and content hash. No source instruction was executed.
No strategy backtest, significance test, performance metrics, MC result,
placement comparison or tier is claimed. No PowerLanguage or live change.

For Claude: `agents/codex/results/agri_cointegration_ssrn2896370.md`.
