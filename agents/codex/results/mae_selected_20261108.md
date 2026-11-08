# Selected-book 0.25% pullback limits — no profile earns advancement

Summary: Tested the user's requested MAE price-offset policy on Vault Break, FC 2B and S47.
With complete design paths, FC2B and S47 lost net dollars versus immediate entry in every year.
Vault Break's conditional subset improved weakly but remained negative; 106 unknown paths prevent a full estimate.
Nine economic definitions executed; six reserved null definitions unused. No controls, 2023+ or account stage earned.
Keep original execution timing; no allocation/live change or independent economic verification is established.

Protocol/evidence/exact code were committed and published before returns at
`6e2b55417b737d33018eb4972f3addd06b81fe12` (initial protocol commit `a766d9e7824839f2da71fba2010a24d41f145b35`).
[Plan](../plans/mae_selected_20261108.md) · [Evidence](../evidence/mae_selected_20261108.md) ·
[Frozen runner](../../../analysis/codex_mae_selected_20261108.py) ·
[Saved-ledger report code](../../../analysis/codex_mae_selected_20261108_report.py) ·
[Input/source snapshots](../inputs/mae_selected_20261108/config.json) ·
[Original five-question paper review](ssrn7063478_review_20261108.md).

## Rule and scope

This is a new explicit user request following the source-only review, not a revision erasing the earlier decision.
Selected before new returns: VB's sustained intraday breakout, FC2B's opening-drive exposure and S47's Europe/NY
agreement. Do not delay short scheduled-flow windows such as MOC/NFP. No threshold, side or holding-window search.

Design **2018-04-02–2022-12-30**, owned 2017–22 NQ raw only, Central clocks. One MNQ ($2/point, .25 tick).
Modeled commission **$1.24 RT**; one adverse tick per market/stop fill. Passive entry requires **one tick through**,
not a touch; zero modeled passive entry slippage. Marketable-gap fills use observed OPEN plus adverse cost capped
at the limit. Stress: **$2.48 RT / two market-stop ticks**, same fills. Source target qualification is unchanged.
The commission is a frozen research assumption from the book's micro-cost convention, not a newly verified broker tariff.

Long limit is original entry minus 0.25%, rounded down to tick; short limit is plus 0.25%, rounded up. It activates
one minute after the original event and cancels before the entire original exit minute. No original-entry-bar
excursion, fallback market entry, favorable-date selection or missing-price imputation is allowed. Untaken
opportunities remain zero child contributions, with the original opportunity/calendar denominator.

**Original virtual-parent state, bracket levels and exit intents stay fixed.** This directly tests the paper's
unchanged-original-exit interpretation. It is not a full regenerated native strategy with brackets re-anchored
to the new fill. A native implementation needs separate intent/risk reconstruction. Fills and risk use the
existing common OHLC path convention, not verified tick/queue chronology. No account-floor result is inferred.

## Results — total design-period dollars per one MNQ

FC2B/S47 are complete under the declared source/path model. VB is a **selected common-complete subset**, not its
full strategy or book. In particular its negative BASE below does not mean the adopted full VB lost money.

|Parent|Resolved/source|Immediate net|Limit net|Net change|Limit fills / missed|Paired daily t|
|---|---:|---:|---:|---:|---:|---:|
|VB|723/829|$-1,281.02|$-191.34|$1,089.68|341 / 382|0.66|
|FC2B|425/425|$11,990.50|$1,358.38|$-10,632.12|238 / 187|-3.89|
|S47|367/367|$14,126.42|$6,228.92|$-7,897.50|217 / 150|-2.82|

These are totals over the design period, not annual income, actual full-book sizing or payout forecasts.
The main and higher-cost results are both recorded; baseline replay totals match the previous frozen study.

|Complete parent|BASE → limit Sharpe|BASE → limit profit factor|BASE → limit closed-ticket drawdown|
|---|---:|---:|---:|
|FC2B|1.55 → 0.28|1.59 → 1.11|$894.38 → $1,949.86|
|S47|1.58 → 0.92|1.70 → 1.54|$1,582.80 → $1,635.24|

These drawdowns are closed-ticket daily statistics, **not native intraday account drawdowns**. Full metrics,
actual fill counts, win/average/trade t, Sharpe/Sortino/PF/Calmar/Ulcer/DD for whole/long/short and every year
are in [metrics.csv](../../../analysis/outputs/codex_mae_selected_20261108/metrics.csv).

## Why better entry prices did not improve the strategies

|Parent|Price improvement on filled trades|Foregone BASE net from missed trades|Missed BASE average|Missed BASE t|
|---|---:|---:|---:|---:|
|VB|$18,655.00|$17,733.82|$46.42|22.61|
|FC2B|$12,476.50|$23,225.62|$124.20|11.64|
|S47|$11,878.50|$19,883.00|$132.55|9.29|

On FC2B/S47 the missed opportunities earned substantially more than entry concessions saved. Fees/slippage
savings are included separately in the [opportunity bridge](../../../analysis/outputs/codex_mae_selected_20261108/opportunity_bridge.csv);
price gain + filled-trade cost saving − foregone BASE net reconciles exactly to the total change. A more favorable
fill is not a profitable execution policy when it misses the main trend days. This failure mechanism was stated
in the preregistration. The missed population need not consist exclusively of winners; its aggregate here is positive.

|Parent|Stressed BASE net|Stressed limit net|Stressed change|Positive incremental design years|
|---|---:|---:|---:|---:|
|VB|$-2,774.04|$-758.18|$2,015.86|3/5|
|FC2B|$11,038.50|$942.26|$-10,096.24|0/5|
|S47|$13,304.34|$5,850.34|$-7,454.00|0/5|

FC2B and S47 lose relative to BASE in **all five design years**. VB's increment has paired t≈0.66, far below the
preregistered 4.42 threshold, and both main/stressed child totals are negative. Of 829 VB tickets, 105 fail the
existing target trade-through qualification and one has a source path/fill gap. These 106 are UNKNOWN, not
no-trade days. Missing winners/targets can bias its common-complete subset, so its small positive difference
is **not evidence of a full-VB benefit**. No data gate, target rule or offset was relaxed to rescue it.

[Year totals](../../../analysis/outputs/codex_mae_selected_20261108/year_comparison.csv) and all BASE/LIMIT tickets,
missed BASE tickets and conditional daily files remain in the output folder. No unknown returns are filled with zero.

## Gates, trials and placement

All three fail design. Primary gates included positive total/stress net and increments, zero UNKNOWNs, 30 actual
fills, paired daily t, DSR≥.95 and year stability. The conservative selection count is 10,253, retaining the
10,000 prior floor, earlier timing/limit looks, author selection and all 15 current reservations.
Nine definitions ran: BASE, fixed limit and cost-stress per parent. Six random-time/random-drop definitions
were reserved but **not run** because no parent earned them. No additional offset or selected long/short rescue.

|Home|Selected parents in source book|Placement outcome|
|---|---|---|
|50K evaluation|VB|No qualifying overlay; VB evidence is incomplete/weak; no account test earned|
|150K evaluation|VB|Same gate result; no account improvement inferred from 50K|
|50K funded|VB|No qualifying overlay; no payout/breach comparison earned|
|150K funded|VB|No qualifying overlay; no payout/breach comparison earned|
|Personal|VB, FC2B, S47|Complete FC2B/S47 tests worse; no qualified VB benefit; no portfolio comparison earned|

Exact account BASE/ADD/REPLACE/EMPTY, Monte Carlo, 2023+ historical validation and independent raw-spec review
were not earned and **were not run**. A stopped design is not a measured assertion that every possible portfolio
risk metric worsens or that the current plans are optimal. Source funded cushion/roster and earlier account-engine
limitations remain binding. The source personal FC2B/S47 entries retain their forward-log qualifications.

## Five paper questions after this test

1. **About:** use original whole-trade MAE to evaluate adverse-offset resting entries on a slower parent.
2. **Findings:** author's Nifty Sharpe 1.38→3.33 remains unverified; our selected NQ replay finds no qualifying improvement.
3. **Why money:** retained entries gain price mechanically, but the tested missed-trade opportunity costs dominate
   for FC2B/S47. The source's proposed conviction effect is not established by these results.
4. **Build on it:** the requested bounded test is complete; retain the negative evidence, not a new threshold search.
5. **Can code be made:** yes, the committed causal fixed-parent research wrapper exists. No native MultiCharts
   signal or broker parity is certified; no positive rule earns deployment.

## Reproducibility and limits

The nine invented pre-execution clock/fill/accounting tests passed without market data. The guard confirmed exact
published code/spec/input hashes and the checked-head project lease before the executed design command. See
[run receipt](../../../analysis/outputs/codex_mae_selected_20261108/run.json) and
[project ledger](../inputs/mae_selected_20261108/progress.json). Original source files/static parent CSVs may contain
already-seen 2023+ rows; raw prices loaded for this test were 2017–22 only, and no new 2023+ outcome was calculated.
The closed-ticket series is conditional and omits interim MTM, netting and current integer/cushion account state.

Regenerate these report tables from saved ledgers with
`/workspace/venvs/thebeginning/bin/python analysis/codex_mae_selected_20261108_report.py`.
The completed lease is released; a new market design run is intentionally guarded. No stopped scout/lab/eval
program was restarted. No trading plan, allocation, live strategy, VPS, broker setting or API key changed.
Independent economic/native verification remains pending; all numbers are research-model results.

For Claude: `agents/codex/results/mae_selected_20261108.md`; inspect first-passage/expiry assumptions, fixed-parent
exits, cost/opportunity accounting and VB's missing-target selection before any reuse. No execution change is proposed.
