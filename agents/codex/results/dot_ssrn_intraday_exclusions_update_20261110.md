# dot: further intraday exclusions and updated overnight evidence
Author: dot. 2026-11-10. No return tests, deployments or strategy changes. These audits do not increase the numbered candidate count.

## Overnight drift: fresh negative evidence
[NY Fed July 1, 2026 author update](https://libertystreeteconomics.newyorkfed.org/2026/07/the-disappearing-overnight-drift/) revisits ES 02:00–03:00 Eastern. Approximately 3.7% annualized historical returns become approximately zero in January 2021–December 2025 (1,245 days); NQ/YM show similar disappearance. End-of-day signed-volume dispersion fell from 6.5% to 2.9%, and its relationship with subsequent returns weakened. The authors propose renewed dispersion might restore the effect, but the required future regime is not observed. **Do not treat a conditional rescue as established alpha.** The current blog is stronger freshness evidence than an old unconditional-drift abstract.

Assessment: this challenges the specific narrow-hour mechanism, not every overnight strategy or the user's independently specified designs. No new portfolio or source-rule change follows automatically.

## Opening-range breakout: bounded negative replication
[SSRN 7428398](https://ssrn.com/abstract=7428398), [public preregistration](https://github.com/mulhamfetna/trading-strategy-finder/blob/main/docs/WS-ORB-PREREGISTRATION.md), [report](https://github.com/mulhamfetna/trading-strategy-finder/blob/main/docs/WS-ORB-REPORT.md).
Nine futures, cash/pit/Globex anchors and four range lengths. First minute close outside range enters next minute open, one trade/session. Three registered exit families include opposite-range stops, ATR stops and targets; same-bar stop first, gaps filled at open. Confirmation 2018–24, exploration 2010–17, fresh 2025–August 2026. At a uniform $25 round trip, none of 225 cells clears all positive gates, although 39 net means remain positive. 138 cells are underpowered and only 28 powered-negative. Missing roll-day sensitivity and changing specifications remain admitted limitations.

Assessment: this is not universal proof every ORB fails. Resting breakout orders differ from close-confirmed entries. Grid aggregate losses are descriptive, costs are scenarios, and minute-path assumptions matter. Existing user's opening-range designs are not automatically identical.

## Event-free Friday ORB: revised evidence still weak
[SSRN 7589980](https://ssrn.com/abstract=7589980), indexed October 17, 2026 revision. QQQ pooled walk-forward +0.34R across 200 trades; DSR probabilities .67 walk-forward/.88 test, below .95. Six of seventeen instruments survive FDR; SPY, silver and NIFTY not established. NQ absent before 2018. Older summaries have different probe counts and DSR figures.

Full source unavailable through the permitted public routes checked. Exact futures net results, earnings information timestamps and fills remain unaudited. **Unnumbered source reserve, not a strong candidate.**

## NQ session-range prediction is not trading profit
Sodikov et al., DOI10.1016/j.finr.2026.100192. [Official public repository](https://github.com/ammaradolcevita/nq-volatility-forecasting); no verified SSRN identity.
The revised model predicts 09:30–11:00 Eastern high–low range using prior ranges, Asian/London behavior, opening gap and calendar/news variables. Train 2009–21, test 2022–25, chronological tuning. Revised test R²: HAR .245, HAR-X .356, Elastic Net .352, CatBoost .403. [Change log](https://github.com/ammaradolcevita/nq-volatility-forecasting/blob/main/docs/CHANGES.md) admits original future-to-past observations, full-sample regime selection and KFold problems, now corrected. Do not reuse the [thesis](https://essay.utwente.nl/essays/109422) .597 headline.

Independent inspection: midpoint hit rate 70.26% is range containment, without a payoff ledger. Start-stamped 16:00 bar closes 16:30, and inclusive 00:00 Asia bar extends to 00:30. Opening gap exists only at the opening print. These are material clock definitions. Licensed Kibot raw bars remain needed even though derived daily data are public. A sizing or stop-distance application needs its own frozen economic validation.

## Chinese one-minute cross-market forecasts: source gate
Guo/Zhu, DOI10.1016/j.jbankfin.2026.107834, [restricted full-text record](https://ideas.repec.org/a/eee/jbfina/v192y2026ics0378426626002086.html). Preview: 36 Chinese commodity futures, 2018–24, lagged cross-sectional returns and rolling linear/regularized forecasting; signal decays beyond one minute. Exact tuning, costs, execution and net robustness unavailable. No SSRN identity verified. Not a US one-contract adaptation or proof owned bars suffice.
