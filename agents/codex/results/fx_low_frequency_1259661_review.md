# Low-frequency FX momentum: retain for personal research; NEEDS DATA AND SOURCE CONVENTIONS

Summary: Harris and Yilmaz use monthly momentum in a recursively smoothed currency trend.
Their 1993–2008 basket Sharpe rises from 0.41 for MA(1,2) to 0.76 for HP and 0.80 for a parabolic kernel.
These are author results with carry included and transaction costs ignored, not our reproduced net returns.
A public spot-price panel was acquired, but source-matched carry, synthetic EUR history and basket conventions remain unresolved.
Retain a lower-priority personal lead; no return trial, Apex adaptation or allocation is earned at this gate.

Source: Richard D. F. Harris and Fatih Yilmaz, *A Momentum Trading Strategy Based on the Low Frequency Component
of the Exchange Rate*, University of Exeter paper 08/04, August 2008,
[SSRN 1259661](https://ssrn.com/abstract=1259661). Full uploaded 30-page PDF read, including Tables 1–7.
[PDF](../inputs/ssrn1259661/source.pdf), [extracted text](../inputs/ssrn1259661/source.txt).
PDF SHA-256: `215c1efbace467091b867acba38d801bda5580772ee407a44781a4d9aae1c36f`.
Gate script: `analysis/codex_fx_low_frequency_1259661_gate.py`;
receipt/data: `analysis/outputs/codex_fx_low_frequency_1259661_gate/`.
Return trials: **0**. Source numbers below are author-reported; no independent economic replication.

## 1. What is it about?

Extract a smooth trend from monthly spot FX levels, then go long when this month's fitted trend exceeds last
month's fitted trend and short when it falls: MA(1,2) applied to the estimated trend rather than raw spot.
The two smoothing families are Hodrick–Prescott (HP) and Nadaraya–Watson kernel regression (pp. 7–10).
The default monthly HP penalty is 14,400. Kernel variants are Gaussian, parabolic, triangular and cosine, with
default bandwidth one quarter of an interquartile range; the exact scaling convention needs clarification.

The source uses nine ex-USD G10 currencies versus USD: EUR, JPY, GBP, CHF, SEK, NOK, AUD, CAD and NZD.
Reuters end-of-month spot histories begin June 1986; Datastream money-market rates supply carry.
June 1986–May 1993 initializes the filters; June 1993–May 2008 is the reported recursive evaluation period,
also split into three five-year subperiods. Each month's smoother is estimated from its historical sample.

## 2. What does it find?

Author's equally weighted basket (EWP), June 1993–May 2008, Tables 2–4:

| Rule | Annualized return | Annualized Sharpe | Maximum drawdown | Directional accuracy |
|---|---:|---:|---:|---:|
| Raw-price MA(1,2) | 1.91% | 0.41 | 9.6% | 52.8% |
| Raw-price MA(2,6) | 2.32% | 0.45 | 16.2% | 55.6% |
| HP trend, penalty 14,400 | 4.49% | 0.76 | 7.7% | 60.6% |
| Parabolic-kernel trend | 4.62% | 0.80 | 9.8% | 62.8% |
| Triangular-kernel trend | 4.89% | 0.87 | 7.9% | 62.8% |

The triangular row is a reported alternative, not a version selected here after reviewing results.
The default HP basket's returns are 4.27%, 4.51% and 4.69% annualized over the three subperiods;
corresponding Sharpes are 0.89, 0.72 and 0.72 (Table 6). Parabolic-kernel basket Sharpes are
1.09, 0.64 and 0.74 (Table 7). Individual currencies are less consistent: HP's middle subperiod is negative
for JPY and NOK. Basket success is not uniform currency-level success or evidence of independent bets.

The paper includes interest carry but explicitly ignores trading costs (p. 11). Its claim that monthly FX
costs are negligible is an assumption, not an observed executable cost study. Figures 3–4 separately discuss
returns excluding carry, so those sensitivity plots should not be conflated with the main return tables.
Drawdown is described from the exchange rate in which the strategy is invested; exact cumulative net-NAV
accounting must be established before comparing this with our account drawdowns. No native trade ledger,
bootstrap uncertainty, multiple-testing correction or current-portfolio contribution is supplied.

## 3. Why does it make money, if it does?

The model assumes that the spot rate contains a persistent nonlinear trend plus serially uncorrelated noise.
Smoothing is intended to suppress noise-driven direction changes while retaining medium-term trends.
Footnote 4 cites noise-trader/central-bank interaction and nonlinear dependence as possible mechanisms;
the study does not identify a forced trader, predictable net flow or a modern causal source of FX profits.
Carry contributes separately to measured returns; this is not a pure spot-direction edge after funding costs.

The empirical recursive results support investigating the method, but do not establish that smoothing creates
predictability in arbitrary assets. Historical trends may decay, sharp reversals can lose, and all currencies
share USD exposure. Diversification versus today's personal book, conditional joint losses and margin needs
remain unmeasured. A monthly profitable basket is not evidence for a new intraday NQ/ES rule.

## 4. Can we build on it?

**Yes as a conditional, lower-priority personal-account lead.** It has a specific slow signal, a simple benchmark,
recursive evaluation and parameter-neighborhood evidence. It earns retention and feasibility work, not a trading
decision. Monthly multi-session positions do not fit any of the four Apex evaluation/funded homes as written.
Daily flatten/reopen, intraday bars or a futures-only single-currency implementation would be new adaptations.
The source only proposes higher-frequency research as future work (p. 16); it supplies no intraday results.

### Important filter and source conventions

- **No automatic look-ahead accusation:** Figures 1–2 use the whole sample for illustration; the authors explicitly
  disclose this (p. 5). Their trading evaluation is described as recursive (p. 10). Preserve that distinction.
- **Forecast vintages:** at decision t, fit only data available through t, then compare the intended fitted endpoints.
  The prior endpoint refitted with data through t and the old estimate stored at t−1 are different statistics.
  Resolve the intended convention and expanding versus fixed rolling history before returns. A single HP fit on
  the final dataset cannot supply historical trading signals. Freeze each dated signal before future observations.
- **Kernel units:** the regressor is time but the bandwidth discussion refers to an interquartile range for each
  series. Need exact time scaling, bandwidth units, estimation window and one-sided endpoint evaluation, rather
  than silently choosing a convenient implementation. The HP branch is more directly specified than this branch.
- **Instrument/basket definition:** establish FX quote direction, normalization/weights, whether the EWP signal
  is applied to one currency basket or aggregates separately traded signals, and how it is rebalanced. Raw levels
  in different quote units cannot simply be averaged as equal economic exposures. EUR before 1999 requires an
  identified predecessor/synthetic series. Neither quote conventions nor pre-euro splicing should be inferred
  from which implementation reproduces the best return.
- **Carry and execution:** identify money-market tenors, bid/ask/funding conventions, holiday/day counts, collateral,
  turnover and first executable post-signal prices. Policy rates are not executable deposit or forward carry.
  Futures substitutes need dated contracts and roll/variation-margin accounting, not spot carry added twice.

### Acquisition attempted and actual boundary

The no-return owned-file census found only 6E minute files, 2017–2026, among the inspected FX futures names.
Those do not reproduce the nine-currency source panel or its seven-year initial history.

Public FRED spot and BIS policy-rate-page requests returned proxy tunnel 403; no workaround was used.
The permitted GitHub mirror [datasets/exchange-rates](https://github.com/datasets/exchange-rates) supplied a
complete 7,648,466-byte daily CSV, 273,921 rows across its full universe, plus its README. Hashes and actual
country/date ranges are saved in the gate receipt; these are intake metadata, not tested trading outcomes.
The mirror says its source is the Federal Reserve and warns of mixed quote directions. This statement and
its licence declaration are provider claims, not independent verification of revisions or executable quotes.

Eight required non-euro countries have long advertised row-date coverage; the euro starts January 4, 1999.
Presence of dated rows does not certify valid values or end-of-month completeness. No return was scored.
The download does not contain the matched money-market carry or clarify source basket/kernel conventions.
Thus this is useful partial acquisition, not an exact Reuters/Datastream replication or an admitted net strategy.
Do not substitute a post-1999 basket, eight-currency subset or spot-only return screen without an explicitly
registered interpretation and source/data gates. Missing source settings are not silently chosen here.

**Decision: NEEDS DATA AND SOURCE CONVENTIONS.** Retain in the verification queue. When genuinely new matching
inputs or author rules arrive, first reconcile one dated month of prices, carry, weights and available-at clocks,
then establish a no-return design-period coverage/power census and commit a bounded HP-versus-raw-MA protocol.
Only passing design gates earn later validation and BASE/ADD/REPLACE/EMPTY portfolio tests at actual size/costs.
No market-return backtest, account simulation, independent verification, trading grade or plan change occurs now.

For Claude: `agents/codex/results/fx_low_frequency_1259661_review.md`.
