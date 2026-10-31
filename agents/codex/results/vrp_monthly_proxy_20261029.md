# Monthly VRP proxy: REJECT this adaptation; exact paper replication unresolved
Summary: An actual preregistered 2018–22 monthly endpoint diagnostic tested positive-VRP equity exposure.
One MES-equivalent:31 selected months net$8,322.81, versus$9,614.12 for37 matched constant-exposure months.
The filter loses$1,291.31 versus base, monthly trade t1.79; skipped months average+$215.22.
Stop: no2023+returns or account bench. Source-data parity and one missing daily mark remain unresolved.

Original plan: [vrp_monthly_proxy_20261029.md](../plans/vrp_monthly_proxy_20261029.md),
commit `1f444c660ced79409834dbe8187b4589409ab910`.
Effective pre-return amendments: [primary-only availability scope](../research/vrp_monthly_proxy_pre_return_amendment.md)
and [terminal endpoint scope](../research/vrp_monthly_proxy_endpoint_scope.md), committed before first outcomes.
Executed implementation commit: `a3d7d11c36fa6c81ecb3344d194c7a22c69f7587`; script SHA256 `be61f0c91cd63f20f2096b1c99740bd6d046a21bf2990ddfe747b554de152b60`.
Script: [runner](../../../analysis/codex_vrp_monthly_proxy.py),
[independent ledger checks](../../../analysis/codex_vrp_monthly_proxy_checks.py),
[report renderer](../../../analysis/codex_vrp_monthly_proxy_report.py).
Outputs: [endpoint metrics](../../../analysis/outputs/codex_vrp_monthly_proxy_20261029/primary_endpoints/endpoint_metrics.csv),
[monthly ledger](../../../analysis/outputs/codex_vrp_monthly_proxy_20261029/primary_endpoints/monthly_ledger.csv),
[filter controls](../../../analysis/outputs/codex_vrp_monthly_proxy_20261029/primary_endpoints/endpoint_controls.json),
[run manifest](../../../analysis/outputs/codex_vrp_monthly_proxy_20261029/primary_endpoints/manifest.json).
Trials: **1 candidate definition P + 1 nonselectable constant-exposure control B return-tested**.
H/I/R were defined but financially unexecuted; no prior research trial history is reset.

## 1. What is the paper about?

Zhou (2018), [SSRN1783624](https://ssrn.com/abstract=1783624), reviews variance risk premium (VRP) and
monthly asset-return predictability. See the [source-only review](variance_risk_premium_review_20261029.md)
for all four source-review answers and table-level citations.

## 2. What does it find, and what did we independently find?

**Author finding:** monthly SPX VRP predicts later equity excess returns, with strongest fit around a quarter;
Table1 reports three-month adjusted R²9.61% and overlap-robust t7.22 for1990–2016.
That is a forecasting regression, not a costed allocation result.

**Our verified diagnostic:** the frozen positive-VRP ES proxy earns positive dollars in a rising equity
sample but earns less than the same-universe constant-exposure control. This rejects this particular filter
as a useful addition under the registered screen. It does **not** falsify the paper's exact monthly SPX model,
its three-month regression or every possible VRP allocation.

## Rule and information clock

Feature at each completed month-end: `(VIX/100)^2/12 - RV`, where RV sums ES five-minute cash-session log-return
squares and overnight cash-close-to-open returns. Known early closes shorten the session. Shared causal-prefix
roll detection adjusts completed feature paths only; it is not verified vendor roll provenance.
Conservatively available17:00 CT, then enter at the next month's first cash-session08:30 boundary using the
exact close-labelled08:31 bar OPEN. Exit at the following month's first cash open.
Long one MES-equivalent iff VRP>0. No short, stop, target, leverage change or parameter selection.
Calendar-excluded target months: March, June, September, December, to avoid carrying unverified contract switches.
This is our one-month/no-roll-month ES adaptation, not the author's SPX strategy or a three-month replication.
Overnight holding makes it structurally personal-only; it is not an Apex intraday rule.

### Data gates and pre-return changes, all retained

1. Original no-return audit:16 of40 target months had current feature plus complete12-month median history,
   below30 required. The optional H/I/R common-universe protocol is closed; no history threshold relaxed.
2. Separately committed primary-only audit:37 target months had known IV/RV, enough for the primary P rule;
   three unknown signal months remain excluded from this conditional diagnostic and visible in eligibility.csv.
3. One daily cash-close risk mark was absent,2020-11-30. All37 scheduled entry/exit opens exist.
   The full daily-risk data gate remains FAILED. The differently labelled daily file was not used as a repair.
4. A second pre-return amendment authorized only the terminal endpoint-return diagnostic, retaining that missing
   daily mark. No joint profit/daily-DD gate,2023+test, MC or account simulation follows from these results.

The amendments respond to observed availability BEFORE any target P&L, not to financial performance. They make
this a data-informed diagnostic rather than an untouched original preregistration. Both audits, coverage holes,
feature inputs and amendments are saved. Missing daily risk was never filled with zero or reconstructed from
SPY/cash-index prices. Target endpoints were not deleted after outcomes.

## Design results: 2018–2022, identical37-month universe

Dollar units: fixed **one MES-equivalent** ($5/ES point), using ES prices. This is not verified native MES
execution; the pre-MES part is counterfactual. Assumed round trip: $1.24 commission plus one adverse tick each
side ($2.50), total$3.74. Stress: four ticks each side plus commission, total$11.24. No spread double-counting.

| Rule | Months held | Win | Gross | Costs | Net | Net/held month | Trade t | Four-tick stress net |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| VRP > 0 | 31 | 71.0% | $8,438.75 | $115.94 | $8,322.81 | $268.48 | 1.79 | $8,090.31 |
| Constant exposure | 37 | 73.0% | $9,752.50 | $138.38 | $9,614.12 | $259.84 | 1.80 | $9,336.62 |

All trades are long; all=long. Short count is0 and short performance ratios are undefined, not positive evidence.
The full side/year table is retained in endpoint_metrics.csv.

| Year | P months | P net | B months | B net |
|---|---:|---:|---:|---:|
| 2018 | 6 | $61.31 | 8 | $858.83 |
| 2019 | 6 | $-148.69 | 8 | $1,522.58 |
| 2020 | 6 | $2,077.56 | 7 | $2,986.32 |
| 2021 | 7 | $4,472.57 | 7 | $4,472.57 |
| 2022 | 6 | $1,860.06 | 7 | $-226.18 |

### Risk statistics: endpoint-only diagnostics, not daily risk certification

The statistics below use the37 observed allocation opportunities, including known flat P months. Annualization
uses37/5 opportunities/year; the quarters and three unknown feature months are not treated as independently
observed trading outcomes. They do not estimate complete daily/overnight risk or a capital requirement.
Initial equity reference$50,000 is used for Ulcer only. Full daily Sharpe/Sortino/Calmar/Ulcer/DD are unavailable.

| Rule | Opportunity Sharpe | Opportunity Sortino | Trade PF | Endpoint Calmar | Endpoint Ulcer | Endpoint DD |
|---|---:|---:|---:|---:|---:|---:|
| P | 0.79 | 1.42 | 2.21 | 0.65 | 2.06 | $2,556.16 |
| B | 0.80 | 1.28 | 2.07 | 0.57 | 1.94 | $3,396.23 |

Endpoint DD can understate within-month losses severely. No claim of better daily drawdown follows from P's
lower endpoint DD. No margin call, liquidation, financing/dividend return or live account path is simulated.

## Controls and stop decision

- P-minus-B net: **$-1,291.31**, paired monthly NW3 t-0.44.
- The6 removed months average **+$215.22**, t0.45; they did not lose money.
- In1000 exactly-count-matched random month-drop comparisons, **39.4%**
  earned at least P's total. The selector is not an unusual improvement over random removal.
- Gross mean$272.22 exceeds the$7.48 economic cost hurdle, but net t1.79 misses2,
  total net is lower than base, and the removed-trade gate fails. Profitable exposure is not incremental alpha.
- Joint profit/daily-DD dominance is **unavailable**, not a passing placebo. The daily data gate stays failed.

**REJECT this proxy filter. No2023+returns, full funded/personal bench, promotion or rescue search.**
No independent raw-spec strategy-checker or MultiCharts parity was requested because the diagnostic already fails.

## 3. Why does it make money, if it does?

The source proposes compensation for uncertainty risk. Our long equity exposure makes positive dollars,
but constant exposure makes more in the same observed months. These results do not identify a separate VRP
timing premium or establish a causal return mechanism. Continuing to change thresholds after seeing this
result would be a new trial, not verification of this result.

## 4. Can we build on it?

Not as an allocation from this test. Exact source replication remains separate and unverified.
The [author homepage](https://sites.google.com/site/haozhouspersonalhomepage/) advertises IV/RV throughDec2024,
but its Google Drive download was denied by the current network policy. The
[official older Fed table](https://www.federalreserve.gov/econresdata/researchdata/feds200711_1.html)
endsDec2008 and cannot supply our design period. No alternate host was used to bypass the denied download.
Existing data/SPY_daily.csv contains index/futures-scale values, not verified SPY ETF prices; no shared file was edited.

| Home | Verdict |
|---|---|
| Personal | No place established: proxy filter underperforms base, t<2, daily risk unverified; no portfolio contribution measured. |
| 50K funded | Structurally ineligible for the frozen overnight rule; no payout test. |
| 150K funded | Structurally ineligible; no result inferred from50K. |
| 50K evaluation | Structurally ineligible; no pass-rate or completion-time test. |
| 150K evaluation | Structurally ineligible; no account comparison inferred. |

The promising-strategy queue retains source-parity status with this negative proxy result attached, not an
instruction to rerun thresholds. Execution library E12 retains the data/measurement lesson.
No plan allocation, ranking, PowerLanguage, live/VPS/broker/API-key or notification change.

## Verification and reproduction

Nineteen synthetic calendar/causality/roll/cost/accounting checks passed before outcomes.
Independent checker verified all37 scheduled raw entry/exit opens, costs/stress, P feature decisions,
aggregate/year/side reconciliation, unchanged input hashes and the stop before validation.
That is a mechanical ledger check, not independent promotion review or actual MES fill confirmation.
Only2017–22 ES files were loaded;2017 supplies warm-up. VIX source bytes include later dates but values were
filtered to<=2022 before feature calculations. No2023+target returns were evaluated.

Run once at the recorded implementation commit in a separate clean checkout (outputs are exclusive):

    /workspace/venvs/thebeginning/bin/python analysis/codex_vrp_monthly_proxy.py synthetic
    /workspace/venvs/thebeginning/bin/python analysis/codex_vrp_monthly_proxy.py audit
    /workspace/venvs/thebeginning/bin/python analysis/codex_vrp_monthly_proxy.py audit --primary-only
    /workspace/venvs/thebeginning/bin/python analysis/codex_vrp_monthly_proxy.py endpoints --primary-only
    /workspace/venvs/thebeginning/bin/python analysis/codex_vrp_monthly_proxy_checks.py
    /workspace/venvs/thebeginning/bin/python analysis/codex_vrp_monthly_proxy_report.py

Do not run design/validation as a workaround for the retained failed data gate.
For Claude: `agents/codex/results/vrp_monthly_proxy_20261029.md`.
