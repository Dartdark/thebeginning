# dot: SSRN continuation, pass 10
Author: dot. 2026-11-10. Research-method audit only. No training, backtests, code execution or portfolio changes.

## 48. Enhancing Time Series Momentum Strategies Using Deep Neural Networks
**Lim, Zohren and Roberts, SSRN [3369195](https://ssrn.com/abstract=3369195).** Reviewed [arXiv 1904.04912v3, September 27, 2020](https://arxiv.org/html/1904.04912v3), later than SSRN's January 2020 revision.

Daily bounded LSTM positions use normalized returns over 1/21/63/126/252 days and three MACD features, with 60-day EWM volatility targeting at 15%. Pinnacle supplies 88 ratio-adjusted continuous series, filtered from 98 by missingness. Expanding tests cover 1995–2015, retrained every five years; training/validation is chronological 90/10, with 50 random hyperparameter trials and 63-step trajectories. Raw gross Sharpe is 2.804 versus 1.192 for 12-month sign-return momentum. At 10 bp costs, turnover-regularized LSTM Sharpe is 0.912 versus 0.861; drawdowns are 37.1% versus 37.3%. Unregularized LSTM Sharpe becomes −5.313. Ordinary LSTM superiority lasts only around 2–3 bp.

**Assessment:** A distinct modeling method, not a new economic mechanism or demonstrated improvement to the user's portfolio. The dramatic gross headline becomes a small incremental net advantage at the illustrated higher cost. Meaningful expanding OOS does not eliminate architecture/objective selection across the overall experiment. No reviewed post-2015 validation.

**Tags:** Personal method lead; no intraday/no-overnight fit; no exact current-data qualification. Existing-bar subset adaptation would change universe and training design. Before any later build, require a native-contract return ledger, executable signal/fill clock, realistic costs and simple cost-aware baselines. No such test is authorized by this report.

## Slow Momentum with Fast Reversion: non-SSRN supplement
[Full arXiv 2105.13727v3, December 20, 2021](https://arxiv.org/html/2105.13727v3), [publication](https://doi.org/10.3905/jfds.2021.1.081). SSRN identifier not verified; not another SSRN count.

Adds Gaussian-process online changepoint features to the neural model. Uses 50 Pinnacle futures, expanding five-year OOS blocks across 1995–2020, chronological 90/10 validation, 50 random trials and candidate changepoint windows of 10/21/63/126/252 days. Reported Sharpe 2.16 versus LSTM 1.62 is an **average of five-year window Sharpes**, not one pooled historical ratio. Rescaled 9.88% maximum drawdown is also window-averaged, not the full-history worst loss. Main results are gross; Appendix C says classical-method superiority deteriorates beyond roughly 2 bp.

**Assessment:** More complexity and tuning without demonstrated robust high-cost improvement. Fast reversion does not mean intraday flat. No reviewed post-2020 validation. [Author code](https://github.com/kieranjwood/slow-momentum-fast-reversion) is MIT, but its current 100-ticker Quandl/CHRIS example is not the paper's 50-contract Pinnacle universe. Software licensing does not license market data.

## Breaking Bad Trends: simpler comparator, known family
**SSRN [3594888](https://ssrn.com/abstract=3594888).** Reviewed [published November 20, 2023 paper](https://people.duke.edu/~charvey/Research/Published_Papers/P167_Breaking_bad_trends.pdf), not the older working version.

43 Barchart futures, monthly 1990–2022. Blends 12- and 2-month signals with separate correction/rebound weights, re-estimated every 30 months from prior history, at least 12 observations per state, clipped to [0,1]. Front contracts roll at expiration-month start. Gross Sharpe is 0.80 versus 0.64 for 12-month trend; returns 4.7% versus 4.2%, drawdown −13.2% versus −18.8%, annual turnover 399% versus 229%. During 2009–2022 its Sharpe is only 0.22. Performance excludes trading/roll costs. An estimated 29 bp break-even relative-cost threshold is not a verified net execution result.

**Assessment:** Useful simple comparator, not permission to reopen the already-failed local Turning Points family (SSRN 3489539). Personal overnight only; exact current inputs unverified.

## Common execution and survival gates
- Next-day return targets establish logical lagging, not an executable common cutoff or fill protocol. Publication delays of settlements and post-signal execution remain unresolved. The cross-market asynchronous-close finding from Network Momentum must not automatically be attributed to own-history models.
- The 88 series include overlapping pit/electronic and index variants, not 88 independent risks. [Pinnacle documentation](https://pinnacledata2.com/clc.html) describes session alternatives and fixed roll schedules; ratio-adjusted histories do not themselves provide a tradable contract ledger.
- A 15% annual volatility target does not limit intraday trailing drawdown, overnight gaps, margin calls, contract rounding or account failure.
- No paper establishes better payouts, loss-limit survival or incremental utility for this user's current book.
- Preserve existing repository results: six-market weekly TSM net Sharpe 0.46, daily trend blocks 0/32 passing, and failed NQ Turning Points states. No exact neural-method entry was found in the reviewed indexes, but that does not turn the broader trend family into a new validated edge.

## Licensing
Public arXiv access is not a general Creative Commons reuse grant. MIT code does not grant Pinnacle/Barchart/Nasdaq data rights. No data entitlement or redistribution permission was established. Only concise research summaries are published here.
