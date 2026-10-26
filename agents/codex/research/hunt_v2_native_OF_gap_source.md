# Native versus OF OHLC: a new input-quality question, no gap admission

Decision: **a bounded new non-return concordance intake is technically credible, but source provenance
does not yet authenticate replacement bars.** The owned OF export includes chart OHLC, not only flow
indicators. That warrants checking a second observed price stream for future distinct research. It
does not authorize filling any native gap, resurrecting H03/H04, changing their availability gates or
calculating another return. No new alpha hypothesis or TEST evidence decision is made here.

Source-only review,2026-10-26. Read only exporter/source/docs and existing saved metadata audits. No
actual native/OF CSV rows, MC workbook rows, new price values, position fields, trading ledgers or
returns were opened. No source module was imported/executed, input audit rerun or network request
attempted. This report adds **0 hypotheses,0 gross screens,0 economic evaluations**. Root reports H04
closed before raw endpoints; program checkpoint3/60economic evaluations,4/10hypotheses,2gross screens,
plus archived65t6evaluations. Root owns progress and any later intake registration.

## What each exporter actually writes

Pinned source inspected:7f0800ffc04d56bd878750369a4abc2316ee01d8. The working research implementation
when inspected was7784493258b793f98fd39a010d2fa6459e465bdf; no source/data file was changed.

|Source|Git blob at7f0800f|SHA256|
|---|---|---|
|tools/exporters/OFB_OrderFlow_Exporter.txt|0b18db89f6863b038fd2e23c5809bd14e079d3c3|5cdd6eba3feed00cce9f2707c6c43bb6f02f59c1ecb8d5d239fa7377c97ab62b|
|tools/exporters/NQ_Bar_Exporter.txt|2f42dade984ac41715fb7cc2322b2268f8568b91|f7c27c08265ab68df717f6e9a3e8cb8464fdf46a206d7ed018f702e67db2ce59|

**OF source:** the documentation instructs a1-minute ASCII chart built from The Bridge/MatFin's
`ofb_bars_NQ.csv`, chart close labels in Eastern. At `BarStatus(1)=2`, the exporter writes the chart's
`Date,Time,Open,High,Low,Close,Volume,UpTicks,DownTicks`. OHLC use two decimals. It then appends historical
DLL indicator slots and separately calculated VWAP/profile fields. The OHLC are therefore direct chart
values, not derived from cum-delta, big-print price, VWAP, an inferred path or the DLL slot values by
this exporter. The export window defaults09:30–16:15ET; optional Globex depends on how the upstream
data was built. Current owned-window coverage must not be assumed to be full Globex.

The exporter itself does not establish how upstream `ofb_bars_NQ.csv` was produced: trade versus quote
events, original contract IDs, roll selection, adjustments, empty-minute treatment, correction policy,
precision before rounding, tape completeness or the original build/version. Its comments describe MBO
history and an aggressor-exact split; those comments are not an authenticated raw-tape manifest.
No relevant upstream bar-builder source/manual or original per-date contract/build manifest was located
in this scoped filename/source search. That is a limited repository finding, not proof none exists.

**Native source:** the NQ bar exporter instructs a1-minute `@NQ` chart, Exchange/CT, defaults08:00–15:15,
and writes chart OHLC plus **Ticks** under the CSV column called`volume`. Prices use the configurable
Decimals(default2). Both exporters delete/rewrite outputs on recalculation. Neither embeds provider,
continuous-contract/roll map, export settings, original download/receipt time or revision vintage in
each CSV. A chart symbol example and file name do not bind the actual historical provider or contract.
Do not borrow an IQFeed/dxFeed name from another strategy or operating document as provenance for the
owned research CSV. The repository describes its continuous histories as not back-adjusted, with roll
jumps outside ordinary RTH; that general description does not prove OF uses the identical roll series.

Existing source studies establish that OF`volume` coincides with its buy/up-classified quantity and
`upvol+downvol` often agrees with native total volume. For a later intake retain this exact distinction:
OF`volume` alone is not native total. `Ticks`/UpTicks/DownTicks semantics also depend on the actual ASCII
mapping and upstream chart configuration. Zero values cannot automatically be classified as observed
no-trade minutes: the OF exporter explicitly documents zero as the bridge's missing-data convention
for indicator families, and upstream empty-price-bar construction remains unknown.

## What the retained audits establish, and what they do not

Saved H04 metadata reviewed, without opening its entry/trade CSV bodies:

- `analysis/outputs/codex_hunt_v2_rs_classified_support/gross_data_audit.json`: internally valid
  OHLCV rows and zero conflicting duplicate keys were reported for native NQ,ES and OF; source clocks
  are CT native and ET-minus60minutes OF. Receipt/execution was explicitly unverified.
- `pre_gross_gate.json` and immutable `pre_gross_verified_execution.json`:608parent entries,
  571unresolved-reference events,1166reference-decision days,9prefix days and1held-event day. No raw
  returns, stopped returns,2023+ or account test. These are the frozen H04 failure records, not a new
  source-quality test in this review.
- Root identifies the first persistent H04 EWMA fault as one missing NQ RTH minute on2018-04-30 while
  ES is complete. This is a parent-reported saved-audit finding; this reviewer did not inspect that
  native minute or the corresponding OF values. The unsupported MC entry-time parser is a separate
  engineering limitation and supplies no evidence for or against OF price authenticity.

The reviewed H03/H04 classifier source checks source/native OHLC validity **internally**, source-volume
aliases, exact up+down versus native total and close agreement within.25. It does **not** require
cross-source open/high/low agreement. A valid OHLC tuple can contain a wrong high/low and still satisfy
all those checks. Broad historical close-match percentages, a valid geometry or a matching adjacent
minute do not authenticate an OF price at a key absent from native data. A missing native print can
also reflect an actual halt, session/contract difference or export omission; do not infer its cause
from which treatment produces an executable strategy.

## Smallest new committed non-return intake proposal

This is a proposal, **not an executed intake plan**. Root must first freeze/commit a separate finite
input-quality plan, code, schemas/clock mapping, source hashes and synthetic review. No unchanged
general-validity audit or closed strategy module should be rerun. Reuse immutable input bindings and
saved aggregate audits where applicable, while clearly identifying the genuinely new key/OHLC joins.

**Stage A — missing-key inventory, metadata only.** Allow only explicit native NQ DAY2018–22 annual
files and OF2018–22 annual parts already bound in the saved input manifest; no wildcard2023+, ES,
workbook, parent signal/order or P&L input. Hash original bytes without changing them. Read date/time
strings and source row IDs only; bind all other columns as unread price fields at this stage. Freeze
native close labels and the documented ET-minus60minutes map, without a timestamp-offset search.
Inventory all expected RTH keys511..900 on a frozen calendar, separately retaining normal, exceptional
and nontrading classifications. Report BOTH/native-only/OF-only/NEITHER presence, duplicate-key status,
source-row IDs and missing-key lists. Do not restrict the inventory to H03/H04 tickets or select keys
using their outcomes. Closed-study metadata may supply context but not a favorable key universe.

Stage A can answer whether the second stream even contains keys missing from the first. Presence does
not establish an observed trade, OHLC fidelity, genuine exchange availability or an executable fill.
If no potentially relevant additional keys exist, stop this intake before inspecting new prices.
If a required original timestamp/symbol mapping is contradicted or ambiguous, report NEEDS PROVENANCE
and stop numeric admission; do not choose a different mapping after seeing price agreement.

**Stage B — separately authorized fixed-key concordance, no returns.** If Stage A warrants it, the
same preregistration must already fix the complete common-key universe and missing-key probe policy.
Before probing missing-native OHLC, examine **all** common RTH keys in the fixed2018–22scope, not a
hand-picked well-matching sample. Convert only OHLC and native total/OFup+down/volume-alias fields.
Report exact open/high/low/close equality, per-field absolute errors in native ticks, quantization,
geometry, totals, zero/invalid states and disagreements by fixed year/calendar/source strata. Retain
all mismatching IDs and sequence discontinuities. The old close-within-one-tick metric may be shown
as a diagnostic; it is not an automatic new OHLC acceptance rule. No fitted level offsets, date shifts,
volatility thresholds, most-favorable field selection or post-result roll/era deletions.

Then inspect only the prebound Stage-A OF-only key set for field validity, coverage and source IDs,
without computing price differences across time, returns, hypothetical stop hits, signals or P&L.
Separate zero/absent OHLC, genuine positive-trade quantity and unresolved source states. A valid OF
bar remains a second-source observation, not a fabricated native print. Do not interpolate either
feed, extend OHLC across gaps, manufacture a native volume, infer a high/low path, or insert the row
into a native grid. Retain original datasets and a standalone diagnostic ledger; no repaired price
dataset, order engine, account engine or strategy list is an output of this intake.

Stage B should end with **DIAGNOSTIC ONLY / NEEDS PROVENANCE**, unless a precommitted independent
primary-source gate also establishes the actual upstream symbol/contract/roll/session/adjustment and
bar-construction/correction provenance. Common-key concordance alone cannot prove what happened at
the very key absent from one feed. Primary evidence might make a future OF-as-independent-price-feed
study legitimate; it must not silently certify a spliced series as the original native history.

All artifacts must bind input/code/plan/dependency hashes, versions, original IDs, calendars and exact
clock rules with write-once outputs, an exclusive lock, retained failed attempts, hash rechecks and a
verified non-return marker. Synthetic checks should cover ET/CT date mapping, duplicate conflicts,
missing keys, OHLC field mismatches despite identical closes, zero/unknown fields and forbidden-return
paths. Source quality is not statistical multiplicity erasure: retain the source-intake history and
add0hypotheses/screens/economic evaluations only while no economic signal or return was evaluated.

## What remains outside scope

This2018–22RTH question cannot certify2017warmup, full Globex,2023+ history, ES, MNQ quotes/fills,
historical receipt, market halts or original contract-month identities. It supplies no strategy t/DSR,
placebo, correlation or book-improvement result. Broader scope needs its own prior plan; no expansion
to repair a disappointing intake after values are seen. A later distinct strategy would require its
own honest mechanism, source admission and economic preregistration, preserving every earlier failed
family. H03/H04 stay CLOSED under their original source definitions even if this new intake finds
additional observations. No generic OF-filter retuning, trading, broker/VPS action, purchase, external
message, t6 resumption, watcher change or automatic v2 pause follows from this report.
