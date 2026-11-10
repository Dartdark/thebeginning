# New data strategy batch: no qualified strategy from the first three tests

Summary: Actually tested three new NQ strategy arms from funding-rate and short-dated-volatility data.
Funding-stress short loses$476.50; morning fear rebound loses$920; pre-open fear rebound earns$1337at1MNQ.
The positive arm has t1.47, below the frozen2.5gate; all three fail design, so no2023+or account tests were run.
Screened two derived states against22strategy reference streams; the one flagged association repeats the knownOT/fear family.
No qualified evaluation/VB replacement or trading change. These are bounded negative/weak findings, not proof the data lack all value.

User request: November9,2026Pacific, test the newly owned data for a strategy. Folder names use the execution
host's November10UTC date. Strategy research is manually authorized; paused scout/lab/schedules stay paused.

Evidence: [`new_data_strategies_20261110.md`](../evidence/new_data_strategies_20261110.md).
Plan/code committed **382fb4d2**, before economic results.
Runner: `analysis/codex_new_data_strategies_20261110.py`; checker:
`analysis/codex_new_data_strategies_check_20261110.py`.
Outputs: `analysis/outputs/codex_new_data_strategies_20261110/`.
Trials run: **2hypotheses,3candidate arms,3price-only controls =6economic definitions;44reference-screen comparisons**.
Both conditional selected-parent null slots remain unused; all earlier project/Claude trials remain counted.

## Inventory, what was new and what was not repeated

Reviewed Claude **08544017**: its daily-series sweep, rejected-strategy rescue, Apex placebos, VB funded
re-slices and macro-surprise experiments are prior looks. Did not rerun them or rename a failed filter.
Current evaluation priority remains VB improvement/replacement in the book that already has Twin2,DT2and finish mode.

| Owned data | Disposition in this task |
|---|---|
| NYFed core rates | New funding-stress strategy; verified next-day publication/revision policy first |
| Official VIX9D + existing VIX | New delayed intraday rebound rule, with two frozen holding windows |
| Other volatility indices / macro daily proxies | Claude's existing broad sweep preserved; no duplicate grid |
| Macro actual/consensus panel | Original forecast/first-actual vintages still unverified; no full-history z-scaling or surprise-return rescue |
| Leveraged/inverse ETF NAV/AUM/shares | Available files retained; historical publication/reset/benchmark gaps still matter; BOIL remains quarantined |
| Treasury buybacks / NYFed operations | Results are post-operation information; modern buybacks do not provide a homogeneous2018–22design sample |
| Futures price history | Exact raw NQ snapshotfe35af99,2017warmup throughNov4,2026; new candidates evaluated only2018–22 |

The aim was new directional strategies, not another promise that smoothing VB's loss size improves passes.
Source mechanisms are hypotheses: funding pressure can persist as equity selling; short-term option fear
can precede a rebound after further overnight weakness. Neither participant flow is measured by these datasets.

## Publication clocks settled for the tested fields

Source notes/links: [`clock_evidence.md`](../inputs/new_data_strategies_20261110/sources/clock_evidence.md).
Direct container requests were blocked; the connected web reader accessed primary NYFed/ARRC/Cboe documents.
No purchase or external contact. Core rates are dated by the underlying transactions, published the next business
day, with same-day afternoon revisions. We use the **core percentRate only after3pmEastern on the following
rate business date**; no retrospective percentiles or volumes. Source dates/derived available times are saved.
This models policy timing with a buffer; it does not claim recovered feed receipt timestamps.

Fear uses the exact VIX9D/VIX close from **two completed NQ sessions earlier**. Missing exact source dates
remain unknown, notOFF; no data forward filling. VIX9D launched before the2018design period. These are historical
close-only official series, not intraday options/dealer inventory. Later historical restatements remain a limitation.
Original raw fields, including blank available_at, were not overwritten.

## Frozen rules and costs

- FUND_SHORT: delayed SOFR−EFFR≥5bp; short NQ09:01open→10:00closeCT.
- FEAR_EARLY: delayed VIX9D/VIX>1and07:30close below00:01open; long07:31→08:29CT.
- FEAR_MORNING: same fear/overnight condition; long09:01→10:00CT.

All:1integerMNQ,50point/$100nominal stop,100point/$200target,maximum1trade/day. Gap-open stop fills,
entry-minute brackets and canonical nearest-extreme OHLC convention; target requires1point through.
Known early-close and quarterly roll dates skipped equally in controls. Overnight features and scheduled
holding windows require observed prices; no replacements for missing minutes.

Assumed native fee **$1.25RT/MNQ**, one adverse tick on entry and stop/time exit; no extra target-limit exit slip.
Stress: fee$2.50RTand2ticks per market/stop leg. These are research cost assumptions, not confirmed invoices.
Stops do not guarantee the nominal loss during gaps. The price-only controls use the same clock/bracket,
available-data universe and overnight-decline condition where applicable, ignoring the new data gate.

## Design2018–22 results, after costs

All dollar results at **oneMNQ**, not oneNQ, not an account or scaled multi-contract book.

| Candidate | Trades | Win | Net | Net/trade | t | PF | EOD DD | Stress net | Verdict |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| Funding short |104|47.1%|−$476.50|−$4.58|−0.78|0.82|$851.50|−$710.50|REJECT|
| Pre-open fear rebound |150|52.7%|+$1337.00|+$8.91|1.47|1.41|$562.75|+$1004.50|Fails statistical gate|
| Morning fear rebound |150|42.7%|−$920.00|−$6.13|−0.74|0.87|$1480.00|−$1250.50|REJECT|

| Candidate | Sharpe | Sortino | Calmar | Ulcer | Direction |
|---|---:|---:|---:|---:|---|
| Funding short |−0.35|−0.47|−0.11|1.22|Short only; long0/N/A|
| Pre-open fear rebound |0.65|1.18|0.46|0.40|Long only; short0/N/A|
| Morning fear rebound |−0.33|−0.50|−0.12|1.60|Long only; short0/N/A|

Whole-strategy metrics equal the populated side. Full side/year rows are saved in `design_metrics.csv`.
These DD/ratios are standalone daily closed equity, with initial zero and no omitted zero-trade weekdays;
they do not establish intraday account survival. Ulcer uses the repository's$50Kreference capital.

| Year | Funding short trades/net | Pre-open rebound trades/net | Morning rebound trades/net |
|---|---:|---:|---:|
|2018|38 / +$165.50|41 / −$289.75|41 / −$933.25|
|2019|61 / −$130.75|27 / +$179.75|27 / −$111.75|
|2020|5 / −$511.25|27 / +$1043.75|27 / +$788.25|
|2021|0 / $0|10 / +$492.50|10 / −$378.50|
|2022|0 / $0|45 / −$89.25|45 / −$284.75|

Funding signals concentrate in2018–20, with no2021–22trade; no later threshold was substituted to improve frequency.
The pre-open rule earns most of its money in2020–21 and loses in2018/2022. It has not demonstrated a stable edge.

## Controls and filter accounting

| Pair | Price-only pool trades/net | Data-gated trades/net | Removed trades mean | Removed t |
|---|---:|---:|---:|---:|
| Funding short |1166 / +$1129.00|104 / −$476.50|+$1.51|0.50|
| Pre-open rebound |523 / +$584.25|150 / +$1337.00|−$2.02|−0.73|
| Morning rebound |523 / −$2872.25|150 / −$920.00|−$5.23|−1.18|

The early fear gate improves this price-only pool's total net by removing weak entries, but its own t1.47
fails the committed2.5criterion. The later rule merely loses less than its control. Neither result earns
selected-parent random-drop/random-side testing or2023+replication under the frozen cheap-screen gate.
No best-window/threshold rescue or flip of the funding trade's direction was run after these outcomes.

## Standing screen across existing strategies

Two derived states×22strategy reference streams=44design-only comparisons, corrected threshold|t|≥3.052.
One flag: archived OvernightTick earns$71.63per active day in the delayed fear state versus$6.78outside,
t3.56,100/214active known-state days;8active days have unknown state and are excluded, not classifiedOFF.
This repeats the existing OT/fear family explored by Claude, not an independent new strategy or a new evaluation hedge.
The44-test threshold does not erase Claude's1,190-plus prior comparisons and selection history.

The reference panel has19archived source versions plus frozen FINRA/ZT125and evaluationONB30. It spans
strategy names but is **not a reconstruction of every current sizing/version**, and has mixed inherited cost
conventions. It therefore supplies associations only; no current-book improvement follows. Every new strategy
would still need consistent native costs, original source clocks, held-path coverage and causal account replay.

## Verification, limits and final disposition

Clock-prefix/unknown-state fixtures and gap/target/entry-minute tests passed before economic results.
Saved-output checks verify raw-to-net costs, annual totals, candidate/control trade identity, removed totals,
source-before-decision clocks and failed-gate stopping. No prospective trade has an unresolved scheduled holding
window in the tested outputs. Fear controls reject8days with absent required overnight point prices;31design
dates lack the exact delayed index input; funding has65unknown prelaunch/publication-window dates.
Eligibility calendars and derived-clock ledgers are saved separately.

The runner uses NQ observations as an MNQ execution proxy. One-minute sequencing, historical index vintages,
policy-based receipt assumptions and current strategy reference versions remain limitations. These are our
reproducible research outputs, not independent native platform validation. No MultiCharts compile/fill claim.

**No candidate survives the cheap gate.** No new2023+strategy returns, bootstrap/payout/account comparison,
MonteCarlo, alternative size, native code or plan adoption was earned. This is why no evaluation-pass uplift
is reported. Actual strategy code can be made—the research implementations are committed—but profitability
and a place in the updated evaluation book have not been established by this batch.
