# Factor-beta sessions: restricted design screen FAIL; exact replication still incomplete
Summary: Tested two preregistered S&P500 market-beta baskets on 2018–22, with recent history unopened.
Price-covered overnight gross +3.93 bp/session becomes −0.66 bp after assumed costs; intraday +0.89 becomes −3.52 bp.
114–120 of 1,259 selected sessions remain unresolved, mainly after acquisitions; these are not filled with zero.
Neither candidate passes; stop before2023+, funded benches or timing/filter/sizing rescue. No plan allocation.

Plan: [factor_beta_sessions_test_20261029.md](../plans/factor_beta_sessions_test_20261029.md),
original c4dfa8035a2fad423bac8577a842eaaa657dabd4; corrected share-basis ratio before returns:
**f9f53157241d41725c93666c1930874b85be7f01**.
Scripts: analysis/codex_factor_beta_sessions.py, analysis/codex_factor_beta_acquire.py, analysis/codex_factor_beta_checks.py.
Outputs: analysis/outputs/codex_factor_beta_sessions/. Source/input record: agents/codex/inputs/factor_beta_sessions/source_manifest.json.
Return variants: **2** (overnight/intraday). Fractional/rounded quantity accounting and fixed cost stress are registered views,
not new tuned signals. Implementation reruns corrected JSON serialization and paired random-calendar accounting;
they did not change selections, trading parameters, gross or net basket returns.

## What was actually tested

This is a **partial screen** inspired by SSRN4138715, not its full CRSP/FF5-conditional study.
No owned stock panel was available. Acquired a public, third-party point-in-time S&P500 membership/price archive:
[Johnbrick123/sp500-data](https://github.com/Johnbrick123/sp500-data).
All five downloaded file sizes/digests match the release metadata, including 235,298,311-byte prices.parquet.
The provider's quality claims are not an independent source audit by us.
No API keys, purchased subscriptions or broker access were used.
A pinned public FF5 mirror was also inspected but ends2020-04-30; it was not used in the return screen.
Using old FF5 data for only favorable dates would not be a valid full-period test.

Fixed 20 high- and 20 low-beta stocks, equal-dollar, from the historical S&P500 membership at formation.
OLS single-market beta uses prior252 sessions against SPY total returns, minimum200 common observations.
Fit/eligibility end at the penultimate prior-month session. Prices at that anchor must be >=$5,
with prior20 usable open/close sessions. No full-sample fitted ranking.
Overnight longs high-beta and shorts low-beta; intraday reverses the legs. Monthly ranks stay frozen.
The first overnight session ending in a new month retains the previous month's weights; no same-close refit.
Warm-up2017; actual selection/outcomes2018–22 only. No2023+ book returns were read or scored.

Reference capital$100,000, $50,000 long/$50,000 short, gross1x. Fixed$2,500 per name.
Costs: **2 bp per one-way execution, 4 bp per round trip on actual notional**, plus short borrow3% annual.
Overnight borrow uses calendar elapsed days; intraday charges a full day. No credit for short proceeds,
no cash-funded-long financing; actual locates, auction fills and minimum fees remain unknown.
Stress10bp round trip. This is a cost assumption, not an observed broker tariff.

## Results: complete-price diagnostic days only

A bp is0.01% of reference capital; at$100,000,1bp=$10.
These conditional results omit unresolved sessions; they are **not a continuous executable equity ledger**.

| Basket / sizing | Covered sessions | Gross bp/session | Trading cost bp | Borrow bp | Net bp/session | HAC t | Net90% block interval, bp |
|---|---:|---:|---:|---:|---:|---:|---|
| Overnight fractional |1,139|3.93|4.00|0.59|−0.66|−0.31|[−4.15,+3.13]|
| Overnight rounded shares |1,139|3.92|3.92|0.58|−0.58|−0.28|[−4.03,+3.19]|
| Intraday fractional |1,145|0.89|4.00|0.41|−3.52|−1.34|[−7.76,+0.84]|
| Intraday rounded shares |1,145|0.86|3.92|0.40|−3.47|−1.35|[−7.63,+0.81]|

Overnight fractional net is −$6.64 per observed session; intraday −$35.17.
Breakeven total round-trip execution charge, after the assumed borrow cost, is only3.34bp overnight and0.48bp intraday.
At the prespecified10bp round-trip stress, means are −6.66bp overnight and −9.52bp intraday.
No alternative cheaper cost model was selected after results. A lower-cost policy could behave differently;
these results do not prove every implementation or the full paper is unprofitable.

### Whole / long / short metrics, fractional reference

Metrics use fixed$100,000 and **covered days**; “trades” below are daily basket observations, not individual fills.
DD and all other measures are conditional and cannot represent the missing acquisition sessions.

| Basket component | Days | Win | Mean$ | Sharpe | Sortino | PF | Calmar | Ulcer | MaxDD$ |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Overnight whole|1,139|49.9%|−6.64|−0.14|−0.21|0.974|−0.060|8.54|28,012|
| Overnight long|1,139|53.2%|23.47|0.43|0.61|1.093|0.236|4.04|25,074|
| Overnight short|1,139|35.6%|−30.11|−1.72|−2.97|0.649|−0.220|19.21|34,557|
| Intraday whole|1,145|48.2%|−35.17|−0.54|−0.75|0.913|−0.188|21.93|47,071|
| Intraday long|1,145|49.1%|−6.08|−0.20|−0.29|0.963|−0.091|6.14|16,817|
| Intraday short|1,145|46.9%|−29.08|−0.48|−0.67|0.921|−0.151|23.68|48,484|

### By year, fractional conditional net$

| Year | Overnight | Intraday |
|---|---:|---:|
|2018|−5,024|−3,418|
|2019|−7,008|−12,568|
|2020|17,317|−2,207|
|2021|5,164|−12,147|
|2022|−18,007|−9,924|

Overnight positive2/5 years; intraday0/5. The profitable long-only overnight component does not authorize
dropping the short leg after seeing these results or opening a third return trial.

## Controls, power and stop

Market-adjusted gross conditional means remain positive: overnight1.18bp, intraday1.41bp.
A random20/20 basket comparison uses1,000 monthly draws, paired on the same valid calendar within each draw,
with matching costs and share accounting. Fractional one-sided descriptive p values: overnight0.001,
intraday0.173. **These do not pass the registered random-data gate**: only33 overnight/47 intraday null paths
cover every observed candidate day, while the plan requires all1,000 complete. The overnight relative ranking
can look better than random while its own net mean is negative.

HAC lag20 and2,000 circular20-session block-bootstrap draws use daily book observations.
The naive t≈2 mean hurdle is4.54bp overnight and6.09bp intraday; mean dependence and missing events limit
interpretation. Thousands of individual constituent observations are not independent sessions.
Random and bootstrap seeds are frozen in the manifest.

Both candidates fail net mean, t, confidence lower bound, four-positive-years, stress and completeness gates.
Rounded accounting does not rescue either. No selected winner; no2023+ evaluation or recent intervals,
funded/account bench, deployment code or additional optimization follows.

## Missing executions and data limitations

The screen has1,259 potential design sessions. Overnight120 and intraday114 are unresolved
(9.5% and9.1%). Names include MON-201806, AGN, NBL, TIF, XLNX, CERN and CTXS.
They were selected before their later acquisition/removal; prices cease while the frozen monthly basket still
references them. The archive also contains no-trade and exit-gap flags; available execution is never inferred
from a carried mark. We do not know a reviewed replacement/cash/settlement ledger for these positions.

Those days stay in unresolved.csv and the gate denominator. They are not coded as zero, filled at a stale quote
or replaced with stocks that subsequently performed well. The complete-day summaries are selection-conditional
diagnostics, not a corrected full-account result or a rigorous proof of economic rejection.

The public archive mixes Yahoo, Tiingo, CRSP and other sources. Historical “close” conventions differ:
Yahoo closes can already reflect later splits. The fixed$5 eligibility and rounded-share calculations use
the supplied price basis; this can embed subsequent split information and is a further implementation/data
limitation, not a verified native-share backtest. Corporate-action metadata and original raw prices must be
reconciled before any future exact replication.
The rounded overnight entry reference follows the registered total-return adjustment ratio, not actual
broker records; quantity chosen at idealized recorded prices is optimistic and lacks pre-auction uncertainty.
No current or historical stock-borrow availability was verified.

The FF5-conditional all-U.S.-stock study remains unreplicated. Point-in-time S&P membership and clock discipline
reduce some biases, but do not turn a revised archive into exact historical information availability.
No paid/futures native costs are inferred from stock backtests.

## Reproduction and engineering checks

Configured Python3.12 with numpy/pandas/scipy; pyarrow installed to read the acquired archive.
No source repository code was executed. Public data were downloaded into scratch_data/factor_sessions/.
Acquire validates sizes and SHA256 digests and stops if a mutable release changes. Source metadata and URLs are committed;
the full mixed-vendor raw dataset is not redistributed. Preserve the verified local snapshot for reproducibility.

Commands:
```bash
/workspace/venvs/thebeginning/bin/python analysis/codex_factor_beta_acquire.py
/workspace/venvs/thebeginning/bin/python analysis/codex_factor_beta_sessions.py
/workspace/venvs/thebeginning/bin/python analysis/codex_factor_beta_checks.py
```

Seven engineering checks pass, including eight independent OLS spot checks, prior-month fit clocks, disjoint
basket legs, exact cost/leg identities, daily-to-year reconciliation, no recent outcome evaluation and fail-closed
missing-price handling. These are implementation checks, not independent evidence of an edge.

## Decision and standing workflow

**STOP / no allocation from this screen.** Exact replication remains NEEDS DATA/native implementation.
Update the TODO entry with these results; no repeated parameter/size search or full-bench run is justified.
The standing instruction to investigate worthwhile future papers automatically is saved in BUILDER_BRIEF:
data/evidence → committed preregistration → cheap screen → only passing later stages, without asking again.
This changes research workflow, not live trading or authorization to purchase subscriptions.

For Claude: agents/codex/results/factor_beta_sessions_test_20261029.md.
