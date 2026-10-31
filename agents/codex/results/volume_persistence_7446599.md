# Post-announcement volume persistence: useful measurement research; no alpha test earned

Summary: European index futures remain unusually active after NFP, ISM and CPI; initial activity explains later volume.
The author reports pooled adjusted R² rising 0.130 -> 0.395 with activity; directional concentration adds about 0.06 percentage points.
This is a volume-outcome association, not a price-return forecast, profitable strategy or measured execution saving.
A fixed-five-minute numeric measurement kernel is feasible and built; full empirical replication needs licensed data.
No return trial, strategy promotion, promising-alpha queue entry, trading-plan or live change follows.

Source: *Trading Intensity, Forecast Disagreement, and Post-Announcement Volume Persistence in European Index Futures*,
[SSRN 7446599](https://ssrn.com/abstract=7446599), uploaded unreviewed preprint. The uploaded title page does not name
an author or give an explicit revision date; do not infer them. Review date: 2026-10-30.
Retained source: `agents/codex/inputs/volume_persistence_7446599/source.pdf`.
Script: `analysis/codex_volume_persistence_7446599.py`.
Audit/source claims: `analysis/outputs/codex_volume_persistence_7446599/`. Return trials: zero.
Document contents were treated as source material, not instructions from the user.

## 1. What is it about?

An empirical study of one-minute FTSE 100, DAX and CAC 40 futures around U.S. non-farm payroll, ISM manufacturing
and CPI announcements, from 2000 through July 3, 2025. The source has 306/307/260 available releases respectively;
usable counts vary by market and model. It measures the unusually high trading volume that persists after the initial
announcement response, and relates it to initial activity, tick-rule directional concentration and professional forecast dispersion.

Normal volume is the median log(volume+1) at the same local time across the preceding 20 eligible non-announcement
days, with at least ten comparison days required. NFP/CPI/ISM dates are excluded from that seasonal benchmark.
An estimated market/event-type boundary from the average first-15-minute response separates initial activity from
the following 120 minutes. A fixed-five-minute initial interval is also examined as a robustness check.

Initial activity is the log ratio of aggregate observed to aggregate typical initial volume (with +1 terms).
The main outcome, AUC120, sums only positive deviations of log volume from its seasonal baseline over the following
120 minutes; the regression target is log(1+AUC120). AUC therefore measures duration AND intensity, in log-volume
units—not contracts traded, price impact, liquidity resilience or dollars earned.

## 2. What does it find?

**Author-reported results; no independent empirical re-estimation.** Table 5, printed p.14, checked visually:

| Pooled model | Observations | Adjusted R² | Standardized activity coefficient |
|---|---:|---:|---:|
| Controls | 2,461 | 0.130 | — |
| Add initial activity | 2,461 | 0.395 | 0.350 |
| Add directional concentration | 2,460 | 0.396 | 0.357 |

The reported unrounded directional increment is 0.3953 -> 0.3959, or about 0.06 percentage points; its pooled
coefficient is 0.011 and insignificant. P3 loses one observation, so the printed difference is not a strictly identical-
sample ablation. Across the nine market/event combinations, all activity coefficients are positive and significant.
The markets share announcement dates; pooled standard errors appropriately cluster by date rather than treating
all cross-market observations as independent news events.

NFP has the largest and longest activity shift in each market. Greater forecast dispersion predicts **less** subsequent
NFP excess volume: coefficients -0.228 FTSE, -0.149 DAX, -0.074 CAC (Table 4, p.13). All survive Benjamini–Hochberg
adjustment; only FTSE/DAX survive Holm. ISM/CPI do not show a comparable common cross-market dispersion pattern.

Actual releases generate elevated activity relative to matched prior non-announcement periods. However, initial activity
also predicts later volume in the matched periods; a persistent-activity relation is not unique to news. The source reports
a stronger NFP activity slope in DAX/CAC but not a uniformly stronger slope across all nine settings (pp.10–11,15).

The reported R² values measure historical explanatory fit. They do not demonstrate a chronological out-of-sample
forecast, trade hit rate or account payoff. The dependent variable is future **volume**, not a price return. Directional
concentration uses absolute tick-rule signed volume; its weak coefficient for volume persistence does not establish
that all signed flow lacks predictive information for prices.

## 3. Why does it make money, if it does?

No money-making result is demonstrated. Portfolio repositioning, order splitting, liquidity transfer and inventory
redistribution are plausible mechanisms for continued volume after a rapid price adjustment. The regressions support
association with the initial activity scale; they do not identify individual participants' motives or establish these
mechanisms causally. The forecast-dispersion result is consistent with a signal-precision explanation, not proof of it.

The author explicitly warns on p.16 that persistent high volume need not imply poor liquidity or higher execution costs:
spreads/depth can improve while volume stays high. There are no uniform quotes/order books, native fill costs,
participation-rate savings, trading profits or strategy/account simulations. Do not turn the R² improvement into an alpha claim.

## 4. Can we build on it?

Yes, as execution-state measurement. It supplies a concrete activity statistic and an empirical reason to distinguish
initial volume scale from normalized one-sidedness. That could inform an independently justified capacity/participation
study, after measuring native spreads, depth, fills, adverse selection and missed-opportunity cost.

Two information-clock cautions matter:

- The primary contract is selected for the entire crossover date using that date's total volume, which is unavailable
  earlier that day. The paper acknowledges this and tests next-day activation. A causal replay must use a frozen known
  contract rule; it cannot use the primary same-day choice as a live input.
- The turning point is estimated from the average event path across the sample. Common across events is not the same
  as fitted only on past events. A future forecast must estimate timing/scalers on the design/past sample or use the
  source's fixed-five-minute boundary. Initial activity is available only after those minutes and their data arrive.
  AUC120, fitted half-life and eventual baseline duration are labels known later, not contemporaneous trade signals.

Our owned-data filename inspection found no FTSE/DAX/CAC transaction histories or matching professional forecast-
dispersion panel. NQ/ES OHLCV and minute-flow summaries cannot reproduce European venue results or the trade-level
tick rule exactly. Section 3 uses Bloomberg consensus/dispersion; the p.17 availability statement restricts redistribution
of commercially sourced raw transactions/announcement data and offers code/derived data on request subject to licensing.
No external contact, purchase or substitute-market return experiment was made.

For a later diagnostic study: first reconcile a dated native-contract event with a known-at-the-time calendar, at least ten
eligible prior seasonal days, source timestamp/bar conventions and independent quote/fill observations. A full source
regression additionally needs forecast vintages and sample definitions. No alpha data-shopping or return test is earned
from a volume outcome alone. This remains supporting execution work, not a new promising strategy.

## 5. Can a strategy code be made?

**Yes for a research/monitoring tool; no supported directional strategy.** A minimal measurement kernel is now in the
audit script: it takes a complete 125-minute event path and 10–20 prior aligned volume paths, uses the source's fixed-five-
minute robustness interval, and computes initial activity, AUC120/log outcome and a five-consecutive-minute return to
the 125% seasonal baseline. It reports both streak onset and when that streak can actually be confirmed, and explicitly
marks right-censored outcomes. Synthetic checks cover flat/high activity, later-outcome isolation, below-baseline volume,
late confirmation and invalid/missing inputs. These verify arithmetic only.

It is **not** a complete event loader, causal timing validator, fitted volume forecaster, turning-point estimator, transaction
tick-rule classifier, execution scheduler or backtester. Callers must supply audited dates/availability and contract mapping;
the numerical arrays alone do not prove observations preceded the event. No economic dataset is ingested by the script.
The kernel cannot decide buy/sell direction or a profitable wait/participation policy. Those require a separately justified
rule, complete costs/fills, committed test design and the ordinary validation gates.

For Claude: `agents/codex/results/volume_persistence_7446599.md`.
