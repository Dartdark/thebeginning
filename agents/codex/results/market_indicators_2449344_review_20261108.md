# Technical market indicators: retain negative evidence; no strategy admitted

Summary: Broad historical test finds little economic value in 93 breadth/sentiment indicators.
Main OLS funnel:93 examined →30 initially significant →10 stable across halves →8 stable in rolling signs →0 economically outperforming.
Several regime/robust-model exceptions exist, but are weak selected results, not independently verified opportunities.
Sharpe columns are scaled by 10^-2; the robust short-sales result is 0.0247 per week, not annual Sharpe 2.47.
Do not start a breadth/sentiment or NQ regime-filter search from this source; retain the evidence and clock/unit cautions.

Source: Jiali Fang, Yafeng Qin and Ben Jacobsen, *Technical Market Indicators: An Overview*, SSRN2449344,
user-uploaded64-page manuscript. Review date November 8,2026, America/Los_Angeles.
No explicit manuscript date established; PDF creation October 23,2014 is metadata, not authenticated publication date.
[Owned PDF](../inputs/market_indicators_2449344/paper.pdf), [text](../inputs/market_indicators_2449344/paper.txt).
Scope: main narrative §§1–7, selected methods/results tables and Appendix 4 inspected; Table 13 visually checked.
Not every table, figure, appendix cell or cited study independently audited; no empirical reproduction.
[Audit script](../../../analysis/codex_market_indicators_2449344_audit.py),
[source/unit receipt](../../../analysis/outputs/codex_market_indicators_2449344/source_audit.json).

## Five questions

1. **What is it about?** Whether93 market-wide indicators predict S&P500 returns:50 sentiment and43 strength
   measures,65 raw plus28 transformed. Includes breadth, new highs/lows, short-sales activity, survey sentiment,
   put/call activity, volatility, fund balances and margin statistics. Tests annual/monthly/weekly/daily horizons,
   with differing samples mostly ending2010/2011, an average length of 54 years and some much older series.
2. **What does it find?** Thirty indicators initially pass a10% significance threshold, ten remain significant
   in both sample halves and eight maintain comparatively stable signs. None of those eight significantly
   outperforms buy-and-hold in the main OLS economic tests after assumed 0.10% switching costs. Business-cycle,
   sentiment and alternative-estimator checks are broadly negative, with the exceptions explicitly listed below.
   These are author results, not independently reproduced findings for our futures book.
3. **Why does it make money, if it does?** Broad profitability is not established. Technical stories rely on
   sentiment extremes, informed/uninformed activity and trend breadth; several fitted signs contradict those stories.
   No specific compelled trade at a known time is identified. Marginal selected gains under an alternative estimator
   do not establish a stable exploitable premium after native costs and information delays.
4. **Can we build on it?** As negative evidence against a broad indicator search and as a warning to separate
   regression significance, sign stability and economic value. The positive exceptions fail our source/evidence gate:
   weak selected tests, no clearly specified compelled flow, uncertain available-at inputs, and no demonstrated
   independent post-selection validation. Keep them documented rather than promote them to the promising queue.
   No new data acquisition or return test is justified. Reopen only on materially stronger independent evidence
   with a specific causal mechanism and matching historical clocks; a new model alone is insufficient.
5. **Can a strategy code be made?** **Yes, conditionally:** the paper specifies a research long-market/cash rule.
   Fit return-on-lagged-indicator-change regression on the first half; forecast the next period; hold the market
   when forecast return exceeds the corresponding T-bill return, otherwise cash; refit each period and charge0.10%
   when switching. Exact reproduction needs original indicator definitions/histories, expanding-versus-fixed
   refit-window clarification, available-at dates, cash-yield conversion, executable fills and price/dividend treatment.
   Its daily/weekly/monthly exposure is primarily a personal-stock timing experiment, not an intraday Apex rule.
   Code feasibility does not establish a profitable strategy or authorize an invented overnight-free adaptation.

## Positive exceptions, without hiding selection or units

| Source | Author-reported exception | Qualification |
|---|---|---|
| §5.1/Table 5, printedp39 | Expansion-only mutual-fund redemptions improve Sharpe; NYSE net new highs have positive alpha | Selected among many indicators/states; NBER expansion labels are retrospective. Net-new-highs alpha t=1.84 is marginal. Introduction says “new highs”; table/body specify net new highs. |
| §6.2/Table 13, printedp50/PDFp52 | Robust-fit weekly NYSE total short sales: Sharpe-difference t 1.89; alpha t 1.99;1788 observations | Sharpe is 2.47×10^-2=0.0247 per week versus−0.17×10^-2=−0.0017 for buy-and-hold. Not an annual Sharpe of 2.47. Does not outperform under main OLS or GARCH tests. |
| §6.3/Appendix 4, printedp55 | Robust-fit weekly NYSE advances: t 2.16 for Sharpe difference, alpha t 2.31 | Added after relaxing the both-halves selection criterion. Sharpe 3.54×10^-2=0.0354 weekly. |
| §6.3/Appendix 4, printedp55 | Robust-fit weekly NYSE net new highs: t 2.42 for Sharpe difference, alpha t 2.57 | Also selected after relaxing the gate. Sharpe 4.35×10^-2=0.0435 weekly. No family-wise correction establishes admission. |

The numerical audit transcribes these selected source rows; it does not generate returns, reproduce the paper,
or establish that modern fees would erase or preserve any result. No annualization is needed for the verdict.
The study covers many correlated indicators, estimators, states and robustness variants;93 is not a complete
trial count. Its10% individual-test cutoff and longest-history strategy do not eliminate selection risk.

## Methods, data and applicability limits

- The core regression is next-period return on the prior-period percentage change in an indicator. Equations use
  lag notation, but adjacent prose confusingly says “one period ahead.” Exact row alignment needs source/code
  reconciliation before implementation; a lagged reference date alone is not proof the release was available.
- Economic evaluation starts in the second sample half and refits chronologically, but the candidate shortlist
  was chosen using full-sample/both-half significance and rolling-sign inspection. This is not an untouched
  holdout for the whole selection procedure. The paper's iid-normal assumptions for Sharpe testing also need
  scrutiny for dependent trading returns; White corrections alone do not fix every serial-dependence issue.
- NBER dates are known retrospectively. CFNAI is released in real time, but the paper's claim that this makes it
  free of hindsight bias is too strong without actual release dates and original vintages. Historical values can
  be revised. Prior-year sentiment also needs availability and PCA-estimation-vintage checks.
- Data are from Global Financial Data. Long premodern “S&P500” histories are reconstructed/index-predecessor
  histories, not a continuously live500-stock product. State the era, price versus total return and investable
  benchmark before any reproduction. The cash-yield units and assumed switching fee are not our MNQ cost model.
- Table 1 notes weekly NYSE short-sales series end in 2008, followed by daily reporting with changed participant
  categories. FINRA daily short volume, short interest and modern 6E/NQ/ES volume are different inputs; no silent
  splice or proxy is an exact reproduction. A bounded local filename inventory found no named matching NYSE
  breadth/short-sales history; this is not proof every archived file was exhaustively searched.
- The source does not evaluate our exact intraday rules, costed integer futures positions, drawdown floors or
  payout paths. It does not invalidate volatility as a risk measurement, all possible technical rules, or existing
  independently tested portfolio exposures. No current VXN gate, sizing or allocation changes follow.

## Decision

**DON'T TEST** on supplied evidence. The explicit exceptions were screened and rejected for advancement, not
overlooked. No eligible new hypothesis, market-return trial, model fit, account simulation or PowerLanguage
strategy was run. No new TODO candidate or data-register item: this is a failed source/evidence gate rather
than a promising strategy blocked only by data. No online data acquisition was warranted after that decision.

Source/units verified by committed code; empirical results and economic value remain independently unverified.
Retain the clock, selection and switching-cost lessons in [EXECUTION_REFERENCES.md](../EXECUTION_REFERENCES.md).

For Claude: `agents/codex/results/market_indicators_2449344_review_20261108.md`.
