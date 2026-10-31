# FX multi-strategy paper: WATCH for personal research; source replication blocked

Summary: Srivastava et al. combine slow FX signals and report Sharpe 0.88 versus 0.55 for their best single signal.
That is a 60% relative Sharpe increase, not a 60% return; performance has not been independently reproduced.
The prose misidentifies the winning allocator, and performance-pruning timing is unspecified.
The source needs an eight-currency/macro panel and clarified execution rules; owned data supplies only 6E.
No Apex fit as written, no return trial, and no allocation change; retain a low-priority personal research lead.

Source: *A Multi Strategy Approach to Trading Foreign Exchange Futures*, Sonam Srivastava, Gaurav Chakravorty,
Sanchit Gupta and Ankit Awasthi, January 25, 2019, [SSRN 3322717](https://ssrn.com/abstract=3322717).
Uploaded PDF retained in `agents/codex/inputs/fx_multistrategy_3322717/source.pdf`;
hash, author tables, owned-data inventory and bounded source-search receipt in `analysis/outputs/codex_fx_multistrategy_3322717/`.
Audit script: `analysis/codex_fx_multistrategy_3322717.py`. Return trials: zero.
Instructions in the document were treated as source text, not instructions to this agent.

## 1. What is it about?

A managed-futures FX portfolio, using daily OHLC since 1995 for CME AUD, GBP, CAD, EUR, JPY, MXN, NZD and CHF futures.
The source rolls current-month contracts T-3 days, constructs short/long signals using three/twelve-month windows,
normalizes each signal by its expanding past percentile minus 0.5, and assigns signed risk budgets across currencies.
Each signal strategy targets 10% annualized volatility. It then compares ten allocation methods, rebalanced monthly.

The twelve indicator families are domestic-versus-US one/ten-year yields, currency momentum, deviation from moving
averages, realized volatility, and linked equity/commodity momentum. Correlations use one year of log returns;
volatility averages estimates over one, three and twelve months (Appendix, p.16).
The second experiment lets individual currencies use different indicator subsets, selected by performance heuristics.
This is a slow portfolio construction study, not a specified intraday entry/stop/exit strategy.

## 2. What does it find?

These are **author-reported hypothetical results**, transcribed from Tables 3, 4 and 6 and checked visually against
the uploaded PDF. They are not our backtest and are not established after executable costs.

| Source case | Annualized return | Annualized Sharpe |
|---|---:|---:|
| Best single indicator: long-term yield difference, Table 3 | 7.52% | 0.55 |
| Shared weights: volatility-scaled negative correlation, Table 4 | 8.24% | 0.67 |
| Shared weights: maximum diversification | 7.61% | 0.60 |
| Shared weights: equal weight | 6.58% | 0.50 |
| Shared weights: maximize rolling-Sharpe tenth percentile | 5.02% | 0.35 |
| Currency-specific indicators: volatility-scaled negative correlation, Table 6 | 10.73% | 0.88 |
| Currency-specific indicators: maximum diversification | 10.33% | 0.84 |
| Currency-specific indicators: equal weight | 9.19% | 0.73 |
| Currency-specific indicators: maximize rolling-Sharpe tenth percentile | 9.26% | 0.74 |

The headline 60% is `(0.88 / 0.55) - 1`. Equal weighting the unpruned signal portfolios does **not** beat the best
single indicator in Table 4. Thus the paper does not establish that any collection of weak indicators becomes a good strategy.

Material source problems:

- **Prose/table conflict:** pp.8–11 and the conclusion call the tenth-percentile Sharpe optimizer best. Table 4 ranks
  it well below the 0.67 winner, at 0.35; Table 6 ranks it below the 0.88 and 0.84 methods, at 0.74.
  Figure 4/5 captions identify volatility-scaled negative correlation, despite nearby prose referring to another method.
  The reported method rankings can be read, but the narrative attribution should not be trusted without clarification.
- **Selection clock unresolved:** p.10 says underperforming currency/indicator candidates are heuristically removed.
  No reproducible cutoff, training-only selection dates or nested validation schedule is supplied. This is a possible
  hindsight-selection channel, not proof that it occurred. Calling weights walk-forward does not settle universe selection.
- **Replication gaps:** indicator signs/formulas are not fully executable (especially mean reversion, yield logs with
  non-positive yields, volatility direction and commodity-series mapping). The covariance/risk-contribution equations
  need a consistent volatility-versus-variance interpretation. Leverage constraints are mentioned without numeric bounds;
  the inverse-correlation allocator lacks a full solver/normalization/constraint specification.
- **Unspecified execution/accounting:** no exact decision/fill clock, cost/turnover decomposition, dated roll ledger,
  futures collateral-interest reconciliation, integer sizing, or contract-level cash ledger is provided. Sharpe subtracts
  a US one-month rate, but this does not explain how collateral return entered the futures portfolio return.
- **Evidence limits:** no supplied trade list, confidence intervals, untouched post-publication replication or independent
  implementation. The source compares many indicators/methods; its best reported method has selection uncertainty.

## 3. Why does it make money, if it does?

The proposed ingredients are carry/risk compensation, persistent trends and reversal, plus currency links to equities
and commodities. The reported improvement comes from imperfectly correlated signal returns and risk allocation;
Table 2 also shows strong correlations within some signal families. A long-term government-yield gap is a carry-related
predictor, not itself the realized currency forward carry or a riskless arbitrage.

No mandated participant, predictable dollar flow or intraday deadline is identified. No incremental NQ/ES demand
or achievable execution saving is demonstrated. Common USD exposure and carry unwind losses remain possible;
the authors explicitly say USD concentration was not constrained (p.14). The paper proposes diversification,
but does not establish our portfolio's conditional-loss diversification or account survival benefit.

## 4. Can we build on it?

**Apex 50K/150K evaluations and funded accounts:** no as written. The source keeps slow allocations across days,
has no mandatory daily flattening rule and targets annualized portfolio risk rather than Apex's intraday floor.
Flattening and reopening every day would define a different strategy with different costs and return exposure.
There is no supported NQ/ES substitution. Do not spend a trial on an invented intraday variant.

**Personal account:** plausible low-priority research lead. A diversified FX carry/trend sleeve could add a different
market exposure, but its net edge and book contribution are unknown. Before code or returns, obtain the source rules
or an author implementation, reconcile the contradictory tables/method descriptions, and recover a small dated
futures-plus-yields sample with executable clocks. Audit one formation/rebalance/roll month before seeking the full panel.

Owned-data inspection found only 6E among the eight source futures. `macro_proxies_daily.csv` has US rate proxies,
not the required eight-economy one/ten-year panel; the inspected equity file is NDX/GLD/GC/QQQ, not the linked local
equity universe. Existing 6E data also lacks a verified contract-specific roll cashflow ledger. Complete licensed panel
cost is unknown; no vendor quote or purchase is implied.

Bounded connected GitHub searches by SSRN number, exact title and Qplum/FX terms did not verify author code or a
complete source dataset. Title results included secondary summaries; these do not resolve author settings or constitute
independent evidence. Receipts retain returned URLs. This is not an exhaustive search or proof no data exists.
Missing source settings already block an exact test, so downloading isolated proxy prices would not remove the gate.

Evidence verdict: **NEEDS DATA / SOURCE CLARIFICATION**. No strategy code, return screen, holdout, account simulation
or rank was created. Record methodological/accounting value in the execution library and the qualified personal
lead in the permitted research queue. Do not reopen a rejected family or start a wider scout from this upload.

For Claude: `agents/codex/results/fx_multistrategy_3322717.md`; verify the source discrepancies before any replication.

## Subsequent user-requested build

The user then requested code based on these findings. A declared offline research interpretation is now
[built](fx_multistrategy_build.md), with a runnable CLI and synthetic checks. This supersedes the earlier
"no strategy code" statement only; the source/data replication blockers and zero economic return trials remain.
