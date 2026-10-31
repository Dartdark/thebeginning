# Speculative Futures Trading under Mean Reversion: methods reference, no demonstrated trading edge

Summary: Leung, Jiao Li, Xin Li and Wang (November 25, 2015), SSRN 2695405, derive model-dependent futures entry/exit boundaries.
Two historical VIX curves are fitted; the paper reports no strategy backtest, net returns, Sharpe or out-of-sample validation.
Its useful lesson is to distinguish physical forecasts from pricing-measure expectations, including costs and the option to wait.
The uploaded version also has a conditional-sign omission and an apparent physical/pricing generator mismatch; neither is a verified finding about the authors' numerical code.
DON'T TEST as a current NQ/ES/Apex candidate. Retain methodology; no allocation, new return trial or live change.

Source: user's complete 22-page PDF, `ssrn-2695405.pdf`;
[SSRN record](https://ssrn.com/abstract=2695405).
PDF SHA-256: `dc5bd948d1eda42ac927d3e925ff9b7ee4d019e7d0266bfc4b214bc9a14acdae`.
Read as evidence, not operational instructions. Saved October 30, 2026, America/Los_Angeles.
Check script: `analysis/codex_leung_futures_2015_audit.py`;
output: `analysis/outputs/codex_leung_futures_2015/checks.json`.
Zero economic definitions/return trials; deterministic formula checks only.

## 1. What is it about?

The paper assumes spot follows Ornstein–Uhlenbeck (OU), Cox–Ingersoll–Ross (CIR),
or exponential OU (XOU) dynamics. It derives the corresponding dated-futures price
under the pricing measure Q, while evaluating trading opportunities under the
historical/physical measure P. The investor can wait to enter, enter long or short,
then wait to close. Coupled optimal-stopping problems produce entry/exit thresholds
as functions of spot and remaining time. The numerical method is Crank–Nicolson
with projected SOR, not a newly estimated predictive signal.

It also derives roll yield as `(change in futures price) - (change in spot price)`
(Eq 3.1, p9), in price units, and the cumulative decomposition across rolls.
This is not automatically a percentage investment return or a literal cash payment
when changing maturities. A futures ledger must reconcile multipliers, variation
margin, dated contracts, realized/open P&L and costs separately.

## 2. What does it find?

- OU/CIR futures prices share the same conditional-mean formula despite different
  distributions (pp3–4). XOU permits different curve shapes (pp6–8).
- Figure 1 fits observed VIX curves on November 20, 2008 and July 22, 2015. These are
  two pricing cross-sections, not trading-performance samples or forecast tests.
  A nearby paragraph says July 25; the figure/caption identify July 22.
- In the numerical examples, costs widen the waiting region, especially near the
  trading deadline. The ability to choose long or short delays entry relative to
  committing to a direction (pp14–18). These are conditional model results.
- Illustrations use a 22/252-year trading deadline and 66/252-year contract maturity
  (Figs 2–4), with cost parameters c = c-hat = 0.005 in price units. This is not a
  calibrated native-MNQ/VX execution-cost test.

No realized strategy-return table, walk-forward calibration, Sharpe, Sortino, profit
factor, Calmar, Ulcer, account survival or portfolio comparison is reported.
Missing numbers remain missing; numerical value functions are not verified profits.

## 3. Why would it make money?

Under the assumed physical process, the conditional future exit value can exceed
entry price plus costs. Trading only at selected boundaries exploits that modeled
expectation. The paper does not establish a forced flow, who pays the trader,
or persistent executable mispricing. Mean reversion is an assumption to validate.

For OU/CIR, the actual futures drift is proportional to
`mu_P*(theta_P-S) - mu_Q*(theta_Q-S)` (p5). Spot can tend to rise while the futures
has negative expected drift. If the measures coincide, the undiscounted futures
drift is zero. A risk-neutral curve is not a physical expected-return forecast.

Two implementation cautions in the uploaded version:

1. **Conditional inequality (p6, Eq 2.12).** The printed greater-than condition for
   positive XOU futures drift requires `mu_Q > mu_P`; it reverses when that
   coefficient is negative. Figure 4(b) instead uses 4.08 < 8.57. With its parameters,
   synthetic `log(S)=3.1` exceeds the printed threshold 3.002739, yet the futures
   drift is −3.023738 price units/year. An independent finite-difference Ito
   calculation gives −3.023739. This verifies the algebraic sign qualification,
   not historical profitability or the correctness of the authors' solver.
2. **Measure notation (pp12–14).** The objectives explicitly use physical P, but
   printed generators (4.2)–(4.4), visually checked on PDF p13, use tilde/Q drifts.
   A solver for the stated physical expectations must use the physical generator
   while retaining the Q-priced payoff. It may be a notation error; absent code,
   do not claim the figures were computed incorrectly or that the paper is invalid.

Discounted notional-price stopping objectives also need translation to an actual
futures margin/cash account before claiming executable P&L. The paper's stylized
problem does not implement Apex's intraday floor, consistency or payout rules.

## 4. Can we build on it?

**Methodology: yes. Current trading candidate: no.** It reinforces cost-aware
waiting and separate long/short analysis, but supplies no tested NQ/ES entry signal.
Price-level stationarity in VIX/commodities cannot simply be assumed for NQ/ES.

Owned-data inspection found daily VIX/VXN/VIX3M/VIXY series and continuous futures
bars; no identified dated VX curve panel with expiries. VIX3M is an index, VIXY is
an ETF; neither substitutes for the contract panel. Continuous NQ/CL history alone
does not identify the spot/Q-curve inputs for this source's replication.
No access failure or external acquisition was invented: owned inputs already fail
the exact-replication data gate, and this methods paper supplies no earned trading
hypothesis warranting a new acquisition/return search.

For a separately justified future project, the smallest next check is to reconcile
one timestamped spot/dated-futures curve and both measures' calibration, settle the
two equation cautions, and reconcile a single futures cash/margin ledger before
registering a chronological trading test with native costs. Parameters must be
estimated only from information available before each decision. An intraday Apex
adaptation would be a new strategy, not a replication of the paper's example.

TIER_LIST already contains the related 2016 regime-switching CIR paper (SSRN
2784215) with the same optimal-stopping/no-backtest limitation, plus rejected
NQ/ES OU/VWAP and intraday-pairs families. The 2015 paper is distinct; it does not
reopen those failures. No promising-strategy queue entry or tier promotion is earned.
Retained under the execution-reference library's E09 accounting/model follow-up.

For Claude: `agents/codex/results/leung_futures_2015_review.md`; methodology retained,
no new strategy, historical return replication or change to any of the five trading homes.
