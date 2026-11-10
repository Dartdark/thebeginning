# NG informed-forecast trading, SSRN2826684: conditional WATCH / NEEDS DATA

Summary: The paper supplies a specific85-minute NG trade based on skilled analysts' forecasts versus consensus.
Authors report Sharpe0.84 on271 nonzero-signal trades, or1.26 on153 large-disagreement trades in2008–16; these are not verified net returns.
The full upload resolves the earlier source gap, but historical analyst forecasts/ranks available at entry remain absent; no backtest or account comparison ran.
Retain a conditional watch; no price/calendar proxy, paid-data request, allocation or live change is justified.

Evidence: [sheet](../evidence/ng_informed_2826684_20261110.md) ·
Source: [uploaded PDF](../inputs/ng_informed_2826684/source.pdf) ·
[access/free-data checks](../inputs/ng_informed_2826684/access.json) ·
[transcribed claims](../inputs/ng_informed_2826684/source_tables.json).
Audit script: `analysis/codex_ng_informed_2826684_audit.py`. Return trials:0; independent economic verification pending.
The [source/input integrity check](../inputs/ng_informed_2826684/checks.json) passed:43source pages, matching
ten NG archive/original pairs and preserved prior trials/other212paper records. This is not economic verification.

## What is it about?

Chen Gu and Alexander Kurov's *What Drives Informed Trading Before Public Releases? Evidence from Natural Gas
Inventory Announcements* asks whether traders can anticipate EIA storage news using better analysis of forecasts
already available before release, rather than necessarily receiving leaked news.

Reviewed all43 PDFpages, including13tables and six figures; visually inspected PDFpages36–43.
The upload is the March25,2018 manuscript, first version March20,2015, marked JFM forthcoming.
SHA256: `44131ff279db2c545c08758f8f94db889fc97c66a049ee1ab14b55941e69829b`.
The [publisher record](https://onlinelibrary.wiley.com/doi/abs/10.1002/fut.21926) confirms JFM38(9),1079–1096,
first online May7,2018. Its abstract/metadata were inspected; complete published-version parity was not established.

This updates the existing November1 metadata record, not a new economic family or a new trial. The old record
is preserved in [previous_record.json](../inputs/ng_informed_2826684/previous_record.json).

## What does it find?

The source considers387 releases from July2008 to January2016, excludes53 dates sharing a petroleum-report
release and retains334. Sixty-three predictor values are zero, leaving271 trades. The ranked analysts' median
has more accurate forecasts than the overall consensus; its difference from consensus predicts some pre-release
price movement. TableVI gives pre-release return R²0.05; the post-release-window predictor coefficient is insignificant.

**Author-reported performance, not our backtest, not established after all trading costs:**

| Source rule | Trades | Annualized Sharpe | Annualized Sortino |
|---|---:|---:|---:|
| All nonzero forecast disagreements |271|0.84|1.40|
| First/fourth quartiles of nonzero disagreements |153|1.26|2.12|

These values are TableXIII, printedp36/PDFp37. Ratios use per-event statistics and annual event frequency,
not daily sqrt252 scaling. The exercise does not specify deducted commissions, spread, slippage or latency.
It provides no net-dollar profit, profit factor, maximum drawdown, loss streaks, margin sizing or account-floor path.
The large-disagreement subset is not automatically a frozen out-of-sample strategy.

TableXII separately reports expanding-window **forecast-error** improvements. Against the historical-mean
benchmark, pre-release return OOS R² is3.43%,2.90%,17.68% for samples beginning January2010,2012,2014,
respectively, each ending January2016. These are not OOS trading Sharpes or account returns.
The study also examines alternative ranking lookbacks, numbers of analysts and event-window starts; those
research choices remain part of its selection history. We have not reproduced any regression or trading result.

## Why does it make money, if it does?

The proposed mechanism is **forecast-processing advantage**. When historically accurate analysts expect a smaller
inventory build or larger withdrawal than consensus, gas is relatively scarce and the signal buys NG. The opposite
disagreement sells NG. Traders following the better forecast can move prices before the official release.
Higher activity around the old9:00ET pit opening may have helped informed orders blend into other flow.

This is a plausible informational mechanism, not an observed compulsory order, proof of leakage, or proof of
profit today. Analyst skill, the panel's composition and market absorption can change. After competing traders
have incorporated the information, the opportunity can disappear. The paper leaves leakage/proprietary collection
possible alongside the forecast explanation. Its weak anchoring-only alternative is not a justified fallback signal.

## Can we build on it?

**Yes, conditionally; deeper return investigation is warranted only when the exact signal can be observed.**
The nonprice forecast disagreement is more specific than a generic Thursday short. The85-minute exposure is
intraday and could in principle be evaluated for personal/evaluation/funded homes, subject to instrument
eligibility, integer risk, native costs and account-floor checks. No diversification or account improvement is established.
The previously closed unconditional NG storage short, SSRN3575861, stays closed; that paper's post2011 cost
failure is neither erased nor a test of this different forecast signal.

Owned corrected NG minute exports cover2017–26, but price bars cannot reveal individual forecasts or which
analysts were top-ranked as of the previous week. The new15-series macro snapshot has no natural-gas storage
forecast series or individual analyst/rank fields. Dot's new petroleum EIA calendar and COT extraction are also
different inputs. The [no-return input audit](../inputs/ng_informed_2826684/owned_input_gate.json) pins what was checked.

A bounded free check used three public indexed queries, the publisher record, the authors' Columbia discussion
and public Estimize rankings. No source-matched historical forecast/rank/receipt panel or replication data was
acquired. Estimize's different current rankings are not a historical Bloomberg survey. No subscriber access,
account, credential, paid download or external contact was requested. This is not proof no free panel can exist.

The smallest next check, **only on new matching availability**, is one dated event: recover each analyst forecast
and revision/receipt time, prior-week rank, overall consensus as of entry, and the correct scheduled report time.
Reconstruct the disagreement without looking at the eventual announcement or return. Then check full design
coverage, ranking warm-up, native contracts, costs and power before a bounded committed preregistration.
The source2008–16 replication and our2018–22design are different data requirements; neither is supplied by the PDF.

## Can a strategy code be made?

**Yes—a directional NG strategy, conditional on those inputs. No executable return strategy was run here.**

The source rule is straightforward:

1. Use the previous week's top-three analyst ranks, not rankings recalculated using this release's actual.
2. Compute `P = median(current forecasts from those ranked analysts) - overall consensus`, in Bcf.
3. At report time minus90minutes, buy one nearby NG contract for `P < 0`, sell for `P > 0`, skip `P == 0`.
4. Flatten five minutes before release: normally09:00→10:25ET, equivalent to06:00→07:25Pacific.
5. Exclude same-day petroleum reports; use actual holiday/exception schedules. The source switches from the
   nearby to next contract for the last three trading days before expiry. No protective stop is specified.

The paper says ranks are lagged and forecasts available before release, but availability by the **90-minute-entry**
deadline must still be verified for every forecast/consensus revision. A submission at10:00ET is too late for09:00ET.
The strong subset requires quartile cutoffs: the source describes a sample split without a past-only cutoff
protocol. A causal adaptation needs separately frozen initialization, quantile/tie handling and warm-up before returns.
Do not choose the strongest cutoff or a new stop after seeing our data. Source tableN153 is retained rather than
assuming the tails contain exactly half of271; tie/allocation details require reconciliation.

Coding a formula does not create the missing historical information. No NG momentum/volume proxy,
eventual-surprise sign, fixed short, after-release substitute or synthetic forecast is an exact implementation.

## Material implementation limits and decision

- **Hindsight illustrations:** Figure2 flips signs using the eventual actual surprise. Its attractive aligned drift
  is descriptive, not a direction known at09:00. Figure6 is an overlapping24-month moving average, not a cash
  equity curve or drawdown record. All six figures were visually checked; no chart was digitized into fake returns.
- **Regime/cost limits:** the sample predates our design and much subsequent automation. Being flat five minutes
  before scheduled news reduces intended release exposure but does not eliminate other-news jumps, wrong clocks,
  missing quotes or exit failure. No source stop/micro-contract parity or modern net edge was demonstrated.
- **Risk/account limits:** no BASE/ADD/REPLACE/EMPTY, Monte Carlo, placebo or matched-drop comparison is earned
  before data/source eligibility. Shared loss timing and whether any offset arrives before an account breach remain unknown.
- **Evidence status:** full supplied-manuscript review and input/source arithmetic checks only. Author regressions,
  author return ratios, modern profits and account results remain independently unverified.

Disposition: **NEEDS DATA / conditional WATCH**. The full paper improves specificity and supports retention of the
lead; it does not unblock a return command. Added to the deduplicated verification queue and shared data register;
supporting clock/execution lessons are in [EXECUTION_REFERENCES](../EXECUTION_REFERENCES.md).
No new hypothesis/definition was reserved or consumed: scout counts remain4/10 and10/30. No lease was acquired
or release claimed. The separate discovery continuation, all earlier trials, paused programs and notification keys
are preserved. No trading plan, allocation, live strategy, VPS, broker setting or API key changed.

Tell Claude: `agents/codex/results/ng_informed_2826684_review_20261110.md`.
