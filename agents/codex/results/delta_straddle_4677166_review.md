# Robust delta-straddle trend following: conditional personal WATCH / NEEDS DATA AND SPECIFICATION

Summary: A concrete slow, diversified trend-following design merits retention, not an NQ-only proxy test.
Author reports9.27%annual return, Sharpe1.03 and13.60%drawdown over the historical multi-asset simulation.
The fast4/8/16-day version changes from+7.85%gross to−3.23%after modeled costs.
Matching41-market returns/roll/carry and execution/accounting conventions remain unadmitted after owned/free checks.
No new strategy-return trial, current allocation or Apex intraday implementation.

Source: Dobromir Tzotchev, J.P.Morgan Securities plc, *Designing robust trend-following system: Behind the scenes of trend-following*, February6,2018. SSRN4677166 posted January17,2024 per [primary metadata](https://ssrn.com/abstract=4677166). Reviewed November8,2026(America/Los_Angeles).
[Upload](../inputs/delta_straddle_4677166/ssrn-4677166.pdf) · [full extracted text](../inputs/delta_straddle_4677166/full_text.txt).
Scope: focused review of signal construction, analytical implications, empirical portfolio/risk/cost sections, universe and selected mathematical appendix derivations. Not an independent verification of every formula. The57-page upload contains the2018report and later disclosure material; the disclosure/SSRN dates do not establish later out-of-sample performance. Printedp.4footnote4 visually checked.
Plan: source/mechanics/data gate only; evidence not TEST. [Evidence](../evidence/delta_straddle_4677166.md) · [actual free-data/specification gate](../inputs/delta_straddle_4677166/free_data_gate.md).
Script: [source audit and invented fixtures](../../../analysis/codex_delta_straddle_4677166_audit.py) · [claims/universe/receipt/hashes](../../../analysis/outputs/codex_delta_straddle_4677166/source_audit.json). Financial-return trials: zero; independent empirical verification pending.

## Five questions

1. **What is it about?** Designing a systematic trend portfolio using a smooth signal `2*Phi(sqrt(T)*mean_return/volatility)−1`, averaging several horizons, allocating across markets and scaling risk. It connects that signal to straddle delta under stated model conventions, derives trend/autocorrelation/cost effects, and discusses no-trade bands, carry and risk budgeting.
2. **What does it find?** Author's historical simulation reports9.27%annual return,9.04%volatility, Sharpe1.03 and−13.60%maximum drawdown for the benchmark. A short4/8/16-day system loses after costs(Table19). The0.25no-trade band has reported Sharpe1.03versus0.92without it(Table18). Those are author backtests, not independently reproduced results or our portfolio contribution. Parameters, cost caps, allocations and variants were examined on the historical sample; no clean modern holdout is established.
3. **Why does it make money, if it does?** Sustained upward or downward trends can persist long enough for a lagged position to participate; spreading risk across different assets and horizons can diversify whipsaws. This is a price-persistence hypothesis, not a measured forced participant. Turnover and running costs can consume short-horizon gross gains. The straddle analogy is conditional model geometry, not ownership of an option or guaranteed crisis protection; sudden reversals and a long position before a crash can still lose.
4. **Can we build on it?** Yes, conditionally for a diversified personal-account research sleeve, with the exact source universe and native cash/roll costs. Worth retaining because the rule, long historical post-modeled-cost result and horizon/cost comparisons are explicit. It is lower priority than owned-data-compatible leads. It does not overturn our failed daily entry blocks, fast trend rules or single-market NQ/ES studies. Smallest next check: one correctly timed formation/rebalance/roll and whole-universe coverage/cost/margin audit after genuinely new matching inputs arrive. Free-source discovery completed without a matching panel.
5. **Can a strategy code be made?** **Yes, an offline research implementation is feasible once the listed choices and data are fixed.** It would compute lagged horizon signals, aggregate them, translate risk weights to native integer positions, maintain last held quantities through the no-trade band, and book fills/carry/rolls/collateral. Exact replication is not presently established, and no MultiCharts trading implementation is earned. Code feasibility is separate from profitability and account suitability.

## Baseline rule described, not run

- Average smooth signed signals over32,64,126,252,504trading days. A signal stays between−1and+1, but inverse-volatility position size need not be bounded.
- Appendixp.36 contains41instruments:10equity futures,7FX total-return indices,10commodities and14rate futures. Allocate25%risk to each asset class, using stated liquidity-based market weights. These are indicator/volatility-scaled exposures, not equal contract counts. The table's asset weights already include class allocation; do not multiply by25%again.
- Use EWMA volatility with decay0.94for position forecasts. Position is proportional to aggregate signal×risk weight/volatility. Portfolio risk targeting uses an expanding-window adjustment targeting average10%annual volatility, not a hard loss cap. Initialization, decision/fill timing, leverage and integer implementation are not fully specified.
- Skip target adjustments below a0.25/volatility threshold. Exact interaction with changing volatility, portfolio scaling and the last executed holding must be frozen; a comparison only against yesterday's desired signal can produce a different strategy.
- Execution costs scale with changes in positions; running costs with absolute held exposure. Source Table6cost assumptions differ by era; modern asset-class averages and gradual historical multipliers are not our broker fees, spreads or native roll/financing evidence. Base results include collateral interest and exclude manager/performance fees; later comparisons add separate fee scenarios.
- Source positions are multiday, including overnight risk. Flat-by15:59CT would substantially change the economics and is not an implementation detail.

## Source evidence and limitations

| Item | Evidence / implication |
|---|---|
| Model foundations | Gaussian/i.i.d. and AR(1) analytical cases explain cost/horizon trade-offs. Persistent real trends, volatility estimation and changing distributions need empirical validation; the normal CDF score is not a posterior trend probability or trade win rate. |
| Horizon diversification | Theoretical P&L correlation `6/pi*asin(0.5*sqrt(T1/T2))` is about0.69016whenT2/T1=2. Our arithmetic matches. This is conditional on the model; horizon ratios matter, but the actual rounded horizon list is not exactly geometric and equal weights are not a universal optimal portfolio. |
| Risk scaling | A bounded signal plus inverse volatility can still produce excessive leverage, especially in quiet markets. Positive daily covariance offsets are uncertain. Integer sizes, margin, gap losses and borrow/financing must reconcile before account claims. |
| Rebalancing band | Turnover control is explicit and useful, but the0.25choice was selected after examining alternatives. It is not independent out-of-sample evidence and must not be tuned on our validation years. |
| Short-horizon source result | Fast-signal net losses are negative evidence. The optional cost caps and more complex risk budgets are separately searched variants, not automatic rescues. More responsive March2009plots do not establish general superiority. |
| Return/carry construction | Bloomberg continuous futures tickers do not determine executed roll P&L; FX`*USDCR`is total return, not spot. Liquidity-weight vintages, collateral series and inception/missing-history treatment need authentication. `YM1`in the source is Australian3Ybonds, not Dow futures. ED4is not automatically modern SOFR. |
| Negative/zero prices | Any log-return implementation needs an explicit native contract/roll/negative-price policy; the2020WTIevent cannot be silently removed or repaired. This matters in the proposed modern design years. |
| Statistical correction | Footnote4/p.4 multiplies the naive t-statistic by`sqrt((1+rho)/(1−rho))`. Under its marginal-return-volatility convention, positive AR(1) dependence raises mean-estimation variance and requires the reciprocal correction asymptotically. An exact finite-window covariance fixture confirms the direction. This is a printed issue, not proof that unavailable empirical code made it. |
| Accounting red flag | Table19reports−156.18%maximum drawdown for the fast net variant. Its NAV/drawdown convention needs reconciliation; do not read it as an investable positive-equity peak-to-trough loss or an acceptable10%-volatility account path. We do not claim a corrected return series. |
| Benchmark scope | Strong backtest diversification versus hypothetical long-only portfolios and a CTA index is not marginal contribution to our current personal book. Source equities Sharpe0.35is weaker than the aggregate1.03; the universe and cross-asset diversification are material. |

The AR(1) counterexample, CDF symmetry/bounds and horizon-correlation checks are deterministic mechanics, not new economic variants. No historical price signals, returns, filter deletions, holdout, placebos or account paths were calculated in this review.

## Acquisition and next gate

Owned input filenames and bounded public author/title/replication/GitHub/Bloomberg-series searches were checked. Found manuscript metadata and secondary adaptations, not an authenticated source-equivalent free constituent panel or author engine. No raw panel admitted. The monthly performance table is not a daily trade/roll/cash ledger. See the [acquisition receipt](../inputs/delta_straddle_4677166/free_data_gate.md); no purchase, registration, external contact or credentials used.

Require a full causal return/carry panel with504-session warm-up before design2018–22, matching calendar/instruments, exact execution and weighting choices, and native integer cash/margin accounting. Reconcile one complete rebalance/roll interval without returns, then coverage/power/cost feasibility. Evidence must advance to TEST and a separately committed bounded protocol before any financial-return screen. No continuous-spot subset or intraday NQ adaptation may inherit the author's results.

## Placement and retained lessons

**WATCH / NEEDS DATA AND SPECIFICATION, low-priority conditional personal lead.** No allocation earned. All four Apex funded/evaluation homes are ineligible as described because of overnight/multiday holdings; no daily-flat conversion justified by this review. Gross/net long/short performance, by-year design/validation, account simulations and current-book BASE/ADD/REPLACE/EMPTY are **not run**, not zeros or implicit passes.

Retained in TODO and [DATA_NEEDED.md](../DATA_NEEDED.md) with missing prerequisites; deduplicate with broad diversified trend research rather than reopening a failed single-market family. [Execution library](../EXECUTION_REFERENCES.md) retains actual-position turnover versus held-exposure costs and the limits of no-trade bands/crisis convexity. No schedules, trade orders, risk-setting changes or live work authorized by paper contents.

For Claude: `agents/codex/results/delta_straddle_4677166_review.md` — concrete diversified trend lead, source claims only; free-data/specification gate unresolved, zero financial-return trials.
