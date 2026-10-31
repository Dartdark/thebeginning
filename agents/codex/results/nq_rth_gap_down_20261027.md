# NQ gap-down long: REJECT — fixed reconstruction does not establish an edge

The written rule is testable without the missing author code. An independent
reconstruction on owned NQ one-minute data produced947resolved trades from
2018-01-02through2026-10-09: **$10,014.22net perMNQ, trade t1.189,
dailyNewey–West(5)t1.265, Sharpe0.403**. Design2018–22 was nearly flat after
costs. Random-sidep0.127fails. This piece is not eligible for book promotion.
These are coverage-conditioned results: unresolved dates/outcomes are retained,
not fabricated zeros. The supplied $602k result was not reproduced.

Original local preregistration: `6e9cb69083d792649001e0f757af96ff6691f1b3`.
First implementation: `2466106`; scope amendment before stopped results:
`eaa296f`; unchanged validation selection: `b4da22f`; financial diagnostics:
`c0175ef`. See the [plan](../plans/nq_rth_gap_down_20261027.md),
[evidence](../evidence/nq_rth_gap_down_20261027.md) and
[disclosed post-gross scope correction](../research/nq_rth_gap_down_replication_scope.md).
These commits were made locally before their respective new outcomes. Shell Git
authentication was unavailable. Automatic approval review also rejected exporting
the original post/README without specific source-export authorization. Those two
files and the `preregistration_history.bundle` containing them stay LOCAL ONLY.
Connected-app publication includes derived code/results and a metadata manifest
of original commit IDs/timestamps/hashes; it does not export the source payload.
Do not describe the later server publication as a publicly timestamped predata
registration or a fresh out-of-sample test.

Scripts: `analysis/codex_nq_rth_gap_down.py`,
`analysis/codex_nq_rth_gap_down_diagnostics.py`,
`analysis/codex_nq_rth_gap_down_checks.py`.
Outputs: `analysis/outputs/codex_nq_rth_gap_down_20261027/`.
Own trial history: **3economic price paths,5frozen economic/cost definitions**;
2,000same-exit placebo paths and1,000matched-subset paths retained as diagnostics.
Author side/stop/threshold/regime trial count is UNKNOWN. Existing related
gap/reversal failures remain selection history. Hunt v2 remains completed at
10hypotheses/5economic evaluations/4grossscreens, plus archived65t6evaluations.
No hunt counters, notifications, automations, rankings or plan allocations changed.

## What was actually tested

- Signal instrumentNQ, one-minute timeframe; economics at one nativeMNQ.
  Buy only if the RTH opening print is below the previous cash-session close.
  No gap threshold, volatility filter, shorts, target, reentry or parameter sweep.
- Source session09:30–16:00NewYork maps to08:30–15:00Chicago. Native bars are
  stamped at their CLOSE. Observe the first opening price from OPEN08:31,
  wait one minute and fill OPEN08:32, physically08:31CT. The already-observed
  opening print is never used as the executable primary entry.
- Stop100NQpoints below the raw entry reference; active on the entry bar.
  A touch triggers. A later opening through it fills at the worse open.
  No target, so no favorable stop/target ordering assumption.
- Preplanned normal exit CLOSE15:00CT; scheduled early-close exit12:00CT.
  Full cash holidays/weekends do not trade. Previous early cash-session close
  is used as that day's reference, an explicit interpretation of missing source
  holiday handling. No overnight holds or exits after15:59CT.
- Native fee1.24USD/MNQroundtrip plus one0.25point adverse tick at EACH fill
  (.50USDperfill): **2.24USDnominal roundtrip cost**. This is the repo's research
  fee assumption, not a newly verified broker quote. The normal stopped loss
  is202.24USD/MNQ; gaps/liquidity can make it worse.

Always-long RTH uses the same delayed entry, stop, exit and costs on the identical
known calendar. The source-cost diagnostic uses0.5point/fill and no commission
perNQ; severe native costs use1.5points/fill plus3extra points on stops and native
commission. The same-opening-print source benchmark is labelled NONEXECUTABLE
after observing its condition. The unspecified VWAP engine was not invented or
combined with this strategy.

## Original gross rejection and the scope amendment

The first2018–22 raw delayed-entry-to-close screen measured546down-gap dates,
mean **−8.558608USD/MNQ**, t−0.676752, before any costs, versus the4.48USDgross
hurdle. The original `design/completed.json` remains **REJECT_GROSS**.

The maker initially applied the hunt's stop-after-gross process too broadly to
this separate user request for the stated STOPPED replication. Raw time-exit
returns do not mathematically determine a fixed-stop rule's returns. After seeing
the negative screen, an explicit scope correction was committed BEFORE the first
stopped outcomes, allowing source reconstruction only under the unchanged rule.
This is disclosed post-screen work, not a clean initial gate pass, a rescued
family or an alternative selected on later returns. Stopped design also failed.
The unchanged later period was committed before its one historical reconstruction.

## Native MNQ results on resolved common coverage

|Period|Trades|NetUSD|Trade t|DailyNW5t|Sharpe|MaxDDUSD|
|---|---:|---:|---:|---:|---:|---:|
|2018–22|542|216.92|0.041|0.043|0.018|3,501.94|
|2023–2026-10-09|405|9,797.30|1.495|1.612|0.773|4,227.08|
|Full|947|10,014.22|1.189|1.265|0.403|4,227.08|
|Source window2020-12through2025-11|561|9,798.86|1.317|1.418|0.591|3,397.30|
|Source window excluding2025|473|3,580.48|0.633|0.666|0.314|3,397.30|

Full five metrics: **Sharpe0.403, Sortino0.824, PF1.114, Calmar0.273,
Ulcer2.534%** at the shared50,000USDreference capital. Win44.24%; average
net10.5747USD/MNQ. All947trades are long; shorts0by definition, not a newly
validated short-side rejection. Daily Sharpe includes known no-trade dates.
Shared equity metrics are seeded at initial equity; time-series statistics use
the actual known-date series. All cost views and five metrics/year are retained
in `diagnostics/full_metrics.csv`.

|Year|Trades|NetUSD/MNQ|Trade t|
|---|---:|---:|---:|
|2018|110|339.10|0.195|
|2019|99|548.24|0.441|
|2020|90|702.90|0.349|
|2021|103|724.78|0.330|
|2022|140|−2,098.10|−0.547|
|2023|121|5,397.96|2.086|
|2024|102|−408.98|−0.174|
|2025|98|6,748.48|1.387|
|2026through10-09|84|−1,940.16|−0.741|

The current source ranking basisN326gives tbar3.609533. FullDSR atN326is0.0304;
an explicitly hypotheticalN1000sensitivity is0.0127. Both fail; neither count
certifies the unknown author's selection history. A positive year or selected
2023/2025 result does not substitute for full/history significance or design.
The shared20-dayblock bootstrap gives full Sharpe90%interval **−0.127to0.841**.

## Source charts do not reproduce

Even the favorable same-opening-print benchmark, source0.5point/fill costs and
no commission produced **$110,960perNQ over561resolved trades** in the stated
2020-12through2025-11window, versus the post's approximately$602k/742trades.
The delayed source-cost version earned$99,335. Therefore entry delay alone
does not explain most of the discrepancy. No original code/data exists for a
parity diagnosis, and this does not establish which source convention caused it.

The headline combined curves also use an unspecified VWAP strategy and sizing;
their MC charts cannot validate this gap leg. The post's per-year statements,
stop/gap sweeps, ES/gold transfer and volatility correlations remain author
claims, not replications performed by this task. Do not claim the source author
used our exact clock, early-close treatment or continuous contract construction.

## Controls, execution costs and risk

|Full-history view|NetUSD/MNQ|Trade t|MaxDDUSD/MNQ|
|---|---:|---:|---:|
|Gap primary|10,014.22|1.189|4,227.08|
|Always-long matched RTH|15,833.14|1.357|6,062.12|
|Gap severe execution costs|2,891.22|0.341|6,070.04|

The gap filter removes **$5,818.92of profitable trades**, average4.685USD,
t0.720. Smaller DD alone is not incremental alpha. In1,000year-matched subsets,
28.9%earned at least the selected filter's profit; it beat both profit and DD
in62.9%of comparisons. Sampled event IDs/masks/net paths are retained.

Same-exit random-side test: **p0.126873**,1,000complete paths: FAIL.
Random-time test:664complete/336unknown paths; conservative p bounds
**0.004995to0.340659**. The favorable lower bound is NOT a pass; unknown paths
were not redrawn away. Total and mean use identical fixed event counts.
Random entries/sides and every net path are retained in compressed artifacts;
these are statistical nulls, not executable combined portfolios.

One-MNQ standalone5,000-path20-dayblock bootstrap over252known trading dates:
medianprofit$1,009.56,5–95%range−$2,979.65to$5,647.92, P(loss)33.38%,
DD95$4,514.86. The shared standalone EOD$2,000trail diagnostic hits48.7%.
This is conditional on incomplete selected history, not a forecast, an intraday
liquidation model, or a funded/evaluation account blow rate. Full-length trade
bootstrap also has11.44%losing paths, so no reproduced100%profit claim.

## Calendar/data/execution limits

The design intake audited628,741source rows, zero duplicate/conflicting keys and
zero invalid observed candles. Missing observations still matter. Across both
periods there are2,205expected cash dates; statistics use2,189common resolved
dates. Four signal dates are UNKNOWN:2020-03-16,2020-11-30,2020-12-01(the missing
prior reference),2021-09-17. Twelve always-long paths are unresolved, including
eight known gap-long paths. Unknown returns were not set to zero or accepted
from the shared walker's missing-bar skip/time fallback.

The unresolved gap paths include **2020-03-09,03-12and03-18**, precisely material
stress dates, plus2018-07-26,2024-10-09,2025-06-02,2025-11-14and2026-08-06.
Missingness is not safely assumed random; reported risk can be understated.
Absent bars may reflect halts or feed gaps; neither is silently repaired.
No complete-history return, maximum-loss guarantee or safe account size follows.

Native export close labels follow the existing repository contract. Author
timestamp parity, original instrument/continuous roll identity and historical
spreads/latency remain unverified. No retrospective roll-jump adjustment,
low-vol filter or source-price rescaling was introduced to improve the result.

Shared execution and nine invented edge-case checks cover entry-active stops,
touches, adverse gap fills, pre-entry lows, early closes and unknown paths.
Retained-ledger invariants cover every resolved always-long path, cost arithmetic,
first stop touch and exact scheduled time exits. This is implementation QA,
not a fresh independent raw-spec financial promotion check. No promotion was
attempted. An audit-only performance retry and cache-location correction changed
no financial result; those are retained administrative details.

## Account placement and final disposition

|Requested home|Disposition|
|---|---|
|Current personal19|No eligible candidate: failed gross/design/significance/placebo gates. No promotion bench; current daily-book source also has the known2020-11-30gap and inherited marking/fee limits.|
|50Kfunded|Not promoted; no valid joint-account improvement claimed. Standalone daily trail risk is not the account bench.|
|150Kfunded|Not promoted; no paired joint intraday paths/bootstrap gain supplied or inferred.|
|50Kevaluation|Not promoted; no valid joint DLL/target/trailing path or pass-rate gain claimed.|
|150Kevaluation|Not promoted; no inference from the50Kor daily proxy.|

No indicated design pass existed to unlock the promotion benches. Failed gates
were not rescued with new size, stops, gap thresholds, volatility filters or
favorable years. No PowerLanguage draft, installation, live trading, purchase,
account trial, external message or phone-delivery claim.

**Verdict: the available data support a reproducible REJECT for promotion of
this fixed reconstruction, with the coverage limits above. The attractive source
headline remains unverified; a genuinely different source export/convention
would need reconciliation before any new bounded replication.**

Publication note: the compressed sampled-path archives and rendered PNG remain in the execution workspace; source code, CSV summaries/ledgers and hashes are published. Original attachments and private history bundle remain local under the approval boundary.
