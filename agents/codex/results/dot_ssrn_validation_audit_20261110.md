# dot: independent validation and version audit
Author: dot. 2026-11-10. Companion to the 41-entry SSRN index; this does not add 41 viable strategies or reopen tests.

## Summary
- Commodity curve hypotheses remain interesting, but later implementations materially weaken the historical headline-return case.
- Commercial-position flow has later statistical support, without a demonstrated executable release-timed net portfolio.
- FX session evidence does not establish modern profitable 6E execution.
- Business-cycle FX evidence remains 2019/2020-era, despite a 2026 SSRN metadata date.
- No returns were computed and no strategy was promoted.

## Basis Momentum and Relative Basis: implementation sensitivity
**Fan and Zhang, Commodity Premia and Risk Management, JFM2024.** [Full publication](https://onlinelibrary.wiley.com/doi/full/10.1002/fut.22507), [institutional PDF](https://research-repository.griffith.edu.au/bitstreams/faa37914-895f-405d-847a-5d305455b127/download). SSRN identity not verified; included as independent validation, not an additional SSRN slot.

Source findings: §2/AppendixA/Table4 use 29 commodities, April1982–September2022, monthly equal-weight long/short halves. BM uses first-minus-second-nearby compounded 12-month returns; RB uses near minus far maturity-scaled log slopes. Traded outright contracts follow maximum OI, with the next maturity leading for three days before rolling. Gross-to-net annual BM is 2.6%→1.7% (net t2.2, Sharpe.32), RB2.0%→1.1% (t1.5, Sharpe.21). Costs assume full200% monthly turnover, $1.50 plus one tick per transaction. The paper describes dollar neutrality and100% collateralization without a simple leg-weight equation.

**Independent assessment:** These are not calendar-spread returns, but neither are they unchanged replications: basket, sample, half-sorts and OI contract choice differ from original BM's top/bottom-four and RB's terciles. Do not subtract these figures from original returns and call the difference measured decay, leverage-normalized loss or transaction costs. Their within-paper gross/net difference is the valid cost comparison. Stop-loss improvements are research hypotheses, not proof of account-survival protection.

## Basis Momentum: regime dependence
**Baba-Yara and Bondatti, Commodity Returns: Lost in Financialization, SSRN[4345427](https://ssrn.com/abstract=4345427).** Reviewed [January2023 EFMA full draft](https://www.efmaefm.org/0EFMAMEETINGS/EFMA%20ANNUAL%20MEETINGS/2023-UK/papers/EFMA%202023_stage-4455_question-Full%20Paper_id-318.pdf). [Author page](https://www.massimilianobondatti.com/research) lists March2026 revision; latest full text remains unverified.

Source findings: 32 commodities, March1986–August2021, standard12-month BM and top/bottom-four sorting. Outright returns use the second-shortest contract whose first-notice date clears the following month. Table1 reports gross BM18.77%/Sharpe.73 before2004 versus7.42%/.30 afterward; post2004 t1.08. No net-cost deduction. Across the factor panel, postpublication decay loses significance after controlling for the post2004 period.

**Independent assessment:** Strong reason not to treat original BM headline returns as a current expected return. Not an isolated postpublication holdout, not causal proof that financialization caused deterioration, and not the original21-market basket. Category: Personal evidence audit; no intraday or owned-data qualification.

## Commercial-position flow: support does not fix timing
**A Tale of Two Premiums Revisited, SSRN[3881922](https://ssrn.com/abstract=3881922), published2023.** [Full journal source](https://onlinelibrary.wiley.com/doi/full/10.1002/fut.22396).

Source findings: producer net-trading Q remains significant with fixed effects and disaggregated COT; smoothed hedging pressure AHP does not. Table7 extension labeled2007–2020 reports Q4.78(t3.81), AHP−.34(t−.84). Section3 uses Tuesday-to-Tuesday returns, without a Friday-release adjustment or net trading-cost portfolio. The data section and extension text disagree about January versus December2020 ending dates.

**Independent assessment:** Supports the liquidity-flow mechanism over the slow insurance component, not an executable Friday-afternoon strategy. Keep actual publication timestamps and postrelease prices as hard gates. This does not reopen the separately closed gold crowding screen: its38 entries and20.4% window coverage failed feasibility minima, not a gold-wide economic hypothesis.

## FX sessions: do not mix windows, instruments or costs
Existing **SSRN[3521370](https://ssrn.com/abstract=3521370)** [final2024 paper](https://onlinelibrary.wiley.com/doi/full/10.1111/jofi.13306) distinguishes fix-linked reversals from local-workday patterns. Its European strategy excludes the ECB-to-London-fix interval. Post-London is11:00–17:00ET, not the strict08:00–16:00NY rule. TableIII's June2006–December2019 CME basket mean is.64bp(t2.20), using midquotes. TableII's2014–2019 spot basket mean falls to.86bp(t1.62). TableX cost results concern AUD/GBP dealer-client spot, with postfix close16:00, and negative customer returns.

**Independent assessment:** Gross futures pattern persistence is not net profitability of our same-day6E hypothesis, while negative spot-customer results do not directly reject that exact futures rule. A17:00ET endpoint also fails applicable pre17:00 flatten requirements without modification. SSRN3069629 remains abstract-only; newer3138756 post2007 evidence remains full-source-gated. Neither is promoted.

## Business-cycle FX: newer timestamp, old evidence
**SSRN[2906600](https://ssrn.com/abstract=2906600)** shows July2026 revision metadata, but [author research page](https://www.stevenriddiough.com/research) still identifies September2019. A [December6,2019 accepted manuscript](https://www.repository.cam.ac.uk/bitstreams/a3531904-83e7-47ef-aac8-560c1e4b798c/download) retains December1999–January2016 real-time vintages and Table4 GAP-CS net3.46%, Sharpe.50 at50% quoted spreads. [City's version](https://openaccess.city.ac.uk/id/eprint/22867/1/BusCycleRisk.pdf) includes the appendix. Exact parity with inaccessible latest SSRN binary is unresolved. No author executable package or underlying dataset located on [Sarno's code page](https://sites.google.com/view/luciosarno/data-and-code).

**Independent assessment:** Preserve its causal-data strengths, but label2019/2020 evidence, not a verified2026 update. Manuscript CC BY-NC-ND licensing does not license underlying commercial data or any unlocated code. Personal category; broad vintages/forwards missing.

## Decision impact
The index's leading curve papers are priority **data-and-modern-validation gates**, not immediately buildable recommendations. COT flow is distinct but still needs a release-timed implementation. Read the [native-contract source audit](dot_ssrn_curve_data_feasibility_20261110.md) before treating a continuous series or public price webpage as adequate data. All next steps remain research-only unless separately authorized.
