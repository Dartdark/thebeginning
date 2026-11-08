# Fast-alpha execution across the current books: no candidate earns advancement

Summary: Screened 24 frozen instrument/version streams spanning all five current book types; none passed design.
On all six fully resolved streams, delayed entry and combined entry/exit timing reduced net profit.
Positive conditional effects in VB/Kusho/NBL were weak and incomplete; S30/CL have especially limited path coverage.
No controls, 2023+ validation or account backtests were earned; no portfolio gain or live change is claimed.

Plan: [frozen protocol](../plans/fast_alpha_books_20261108.md), committed before returns at `d06d6eaeb069edc5c15fb8d44a9908661878936a`.
Clock-only amendment: `3b22c7e94e281dd79c45edc5ef75c08a44a3411b`; original attempt preserved.
[Evidence](../evidence/fast_alpha_books_20261108.md), [paper/five questions](fast_alpha_paper_20261108.md),
[runner](../../../analysis/codex_fast_alpha_books_20261108.py), [report/reconciliation code](../../../analysis/codex_fast_alpha_books_20261108_report.py).
Inputs and exact Claude roster source are in [config](../inputs/fast_alpha_books_20261108/config.json).

## What was tested

Design 2018-04-02–2022-12-30; owned 2017–22 raw one-minute NQ/ES/CL only. Each result is one native micro:
MNQ $2/point, MES $5/point, MCL $100/point. Main commission $1.24 RT plus one adverse native tick on market/stop
fills; stress $2.48/two ticks. MES/MCL commission is assumed. Targets need source-consistent trade-through.
No SPY fee/fractional-share or zero-slippage assumptions transferred to futures.

BASE preserves the original virtual parent's intended levels and state. ENTRY waits for the first complete
five-minute close-to-close return against the direction, then fills at the next executable minute open.
If the parent exits first, the entry is canceled; no hindsight-best fill or guaranteed price improvement.
BOTH adds favorable-countermove liquidation after a stop/discretionary exit request. Target/time/holiday exits
are preserved. Actual holdings can suppress subsequent parent entries. This is an explicitly specified
**fixed virtual-parent execution wrapper**, not a regenerated parent alpha with newly entry-anchored brackets.
Its source clocks/intent reconstruction and OHLC fills remain conditional until independent native review.

ENTRY−BASE isolates the entry policy; BOTH−ENTRY is the incremental exit policy conditional on those entries.
It is not a separate exit-only experiment. No 15/30/60-minute wait search, new streak, side filter or optimized stop.
All source tickets, missed orders and UNKNOWNs remain in the saved ledgers. Missing/changed-roll intervals
were not imputed. The old fast-alpha search and all parent selection histories remain in multiplicity.

## Fully resolved execution streams: every tested delay lost money

The following rows have no unresolved tickets across BASE/ENTRY/BOTH under this declared replay model.
Amounts are **total design-period net dollars per one micro**, not annual income, actual book sizing or payouts.

|Strategy|Tickets|Immediate BASE|Delayed entry|Entry + deferred exit|Combined change|
|---|---:|---:|---:|---:|---:|
|LDF|465|$3,229.40|$1,394.92|$1,949.92|$-1,279.48|
|NFP|42|$736.92|$469.92|$528.92|$-208.00|
|MOC|117|$2,433.69|$355.17|$336.65|$-2,097.04|
|TOS|218|$4,326.14|$819.17|$277.02|$-4,049.12|
|FC2B|425|$11,990.50|$9,477.48|$9,084.48|$-2,906.02|
|S47|367|$14,126.42|$12,731.90|$13,152.40|$-974.02|

These are direct negative execution comparisons, not failures caused only by absent data. LDF's fixed
14:00 flow and ES MOC's short window lose opportunities while waiting. The latter misses 77 of 117 tickets.
This timing explanation follows the frozen participant/time mechanism; it is not a new fitted time filter.
No claim of full native-platform or independent economic verification follows even for these clean paths.

## Every parent, including incomplete cases

This table uses the **same jointly resolved tickets** for all three profiles within each parent. It preserves
comparability but does not make the omitted observations ignorable. Qualified target fills/missing paths can
disproportionately remove winners. A negative conditional BASE does not establish that the adopted strategy lost
money. The full table must not be summed into a portfolio or scaled into payouts.

|Parent|Market|Resolved / source|Unknown|ENTRY change|BOTH change|Paired t ENTRY / BOTH|
|---|---|---:|---:|---:|---:|---:|
|VB|NQ|723/829|106|$1,081.38|$202.04|1.08 / 0.16|
|ONB30|NQ|342/350|8|$-1,267.82|$-1,830.32|-1.43 / -1.70|
|ONBML|NQ|176/178|2|$-815.50|$-1,031.50|-1.20 / -1.28|
|EOS|NQ|56/57|1|$-584.00|$-494.50|-1.21 / -0.92|
|LDF|NQ|465/465|0|$-1,834.48|$-1,279.48|-1.86 / -1.18|
|MON|NQ|242/243|1|$-1,525.50|$-1,111.50|-1.33 / -0.86|
|NFP|NQ|42/42|0|$-267.00|$-208.00|-0.87 / -0.62|
|BRIDGE|NQ|87/116|29|$-115.50|$-115.50|-0.98 / -0.98|
|CLS|CL|0/40|40|—|—|—|
|MOC|ES|117/117|0|$-2,078.52|$-2,097.04|-3.11 / -3.14|
|RS|NQ|564/578|14|$-2,924.24|$-3,227.19|-2.09 / -2.04|
|DT|NQ|820/853|33|$-2,806.92|$-2,626.42|-1.99 / -1.59|
|TOS|NQ|218/218|0|$-3,506.97|$-4,049.12|-2.70 / -3.15|
|OT|NQ|253/302|49|$-275.50|$-275.50|-0.56 / -0.56|
|FC2B|NQ|425/425|0|$-2,513.02|$-2,906.02|-2.32 / -2.23|
|ST|NQ|286/322|36|$-393.02|$-762.02|-0.42 / -0.64|
|PT|NQ|315/316|1|$-1,516.00|$-1,516.00|-1.85 / -1.85|
|S47|NQ|367/367|0|$-1,394.52|$-974.02|-1.51 / -0.96|
|KUSHO|NQ|1359/1738|379|$1,439.90|$761.84|1.20 / 0.42|
|S30_NQ|NQ|5/147|142|$26.50|$-6.50|0.68 / -0.22|
|S30_ES|ES|2/139|137|$-77.50|$-78.75|-1.12 / -1.20|
|TWIN|NQ|508/575|67|$-2,940.73|$-2,548.73|-2.74 / -2.21|
|TWIN_CAP1|NQ|552/592|40|$-2,362.86|$-1,686.71|-2.19 / -1.40|
|NBL|NQ|1063/1212|149|$646.68|$2,087.38|0.63 / 1.68|

VB's positive entry effect has t≈1.08; Kusho t≈1.20; NBL's combined effect t≈1.68. None approaches the
prespecified multiple-testing threshold (conservative 10,000 prior-definition floor plus 120 reserved and 58 older
fast-alpha looks), and their full path gates fail. NBL/Kusho conditional BASE remains negative on this restricted
subset. S30 has only 5 NQ / 2 ES resolved tickets; no inference is warranted. CL has zero jointly resolved paths:
its zero sum in machine output means **no identified result**, not a flat/no-trade/profitable strategy.

The source-clock checks fixed two adapters without changing rules: every Kusho date/index pair identifies
December 1, 2017 as its origin; PT next-bar market entries on five-minute reports map to the first constituent
minute OPEN, four minutes before the report stamp. Exact OPEN matching is required, not a favorable-price
search. The first attempt and diagnostics are retained; all 22 unaffected parent summaries reproduce exactly.
No additional economic variant or performance-based data relaxation was introduced.

## Stops, accounting and statistical limits

Deferring liquidation can extend loss beyond the original stop. Saved [deferred-exit risk](../../../analysis/outputs/codex_fast_alpha_books_20261108/deferred_exit_risk.csv)
reports paired observed adverse excursions and extra held minutes at one micro. These are conservative minute
measures (for example, Kusho added up to $660.50 adverse exposure and 60 held minutes), not verified tick chronology or account floor replay; no later rebound guarantees survival.
Market orders following pullbacks remain aggressive, and pending actual positions can suppress later intents.

The daily series is **closed-ticket, common-complete contribution**, not full MTM equity. Overnight marking,
unresolved trades, aggregate netting and current account quantities prevent using it as a funded/eval proxy.
Source-ticket quantities are normalized to one micro only for this cheap diagnostic. Actual book sizes,
inverse-vol weights and signal-time funded cushion sizing were not fabricated from these curves.

All gross−fee−slippage totals reconcile to net and daily contributions. Original standard_metrics.csv counts
resolved opportunities, including canceled orders; [actual-fill metrics](../../../analysis/outputs/codex_fast_alpha_books_20261108/actual_fill_metrics.csv)
separately reports actual trade count/win/average/t, whole/long/short and every design year. Total paired effects
retain zero missed-trade contributions; dropping profitable unfilled tickets is not called a higher average edge.
Sharpe/Sortino/PF/Calmar/Ulcer/DD are in the CSVs, with the same conditional, closed-ticket limitation.

Cheap gates required at least 30 complete tickets, no unresolved paths, positive total/stressed net and incremental
total, adjusted paired t, DSR >= .95 and 4/5 positive years. **No candidate passed.** Significance is not inferred
from a favorable average or source paper, and the conservative selection floor is not a complete census of
unknown author trials. Conditional effect estimates and repeated/overlapping strategy streams are dependent.

## All five placement homes

|Home|Mapped streams|Passed|BASE/ADD/REPLACE/EMPTY outcome|
|---|---:|---:|---|
|evaluation_50|4|0|Not earned; no demonstrated overlay allocation|
|evaluation_150|5|0|Not earned; no demonstrated overlay allocation|
|funded_50|10|0|Not earned; no demonstrated overlay allocation|
|funded_150|13|0|Not earned; no demonstrated overlay allocation|
|personal|21|0|Not earned; no demonstrated overlay allocation|

The source personal roster has 20 named pieces but 21 instrument legs because S30 includes NQ and ES. The latest
150K evaluation/funded rosters add capped Twin separately from personal Twin. Shared parents were tested once,
then mapped to every book that uses them. The exact five-home coverage is in [book_placement.csv](../../../analysis/outputs/codex_fast_alpha_books_20261108/book_placement.csv).

None earned random-delay/drop controls, 2023+ historical validation, independent raw-spec review or native account
comparisons. Those stages were **not run**, rather than manufactured after a failed design. This is not a
measured claim that every possible portfolio-risk metric worsens or that the current plans are optimal.
Current source roster/cushion inconsistencies and earlier account-model defects also remain binding limits.

## Five paper questions and decision

1. **About:** fast SPY mean reversion as a timing overlay on slower ATR intraday breakouts.
2. **Findings:** authors report about 200 bp CAGR gain and Sharpe 0.86 (body) / 0.87 (abstract) to 0.99; commissions included,
   zero slippage. Our 24-stream futures design finds no passing overlay, with six fully resolved negative comparisons.
3. **Why money:** possible better execution of slow alpha without standalone fast turnover; missed exposure and
   deferred-stop risk can outweigh it. Neither the paper nor these conditional screens establishes live savings.
4. **Build on it:** the requested bounded execution question is tested; no profile earns deeper/account work.
   Retain the negative evidence, not a new waiting-window rescue or an unverified strategy queue candidate.
5. **Can strategy code be made:** yes, the committed Python execution wrapper exists. It is research code,
   not installed MultiCharts signals or broker-tested native execution. No passing rule is available to deploy.

**Recommendation: keep existing execution timing.** This project establishes no approved change in any book.
Independent economic/native verification remains pending. No root tier/trading plan, allocation, live strategy,
VPS, broker setting or API key changed. The autonomous scout/paused programs and their budgets were preserved.

For Claude: `agents/codex/results/fast_alpha_books_20261108.md`; verify the fixed-parent interpretation, source
clock amendments, native costs, path/target qualification and all negative/incomplete dispositions before any reuse.

To regenerate these tables from the saved ledgers, run
`/workspace/venvs/thebeginning/bin/python analysis/codex_fast_alpha_books_20261108_report.py`.
This reads no raw market data and creates no new economic definition. The original design commands and checked
commits are recorded in run.json and progress.json; a new design execution requires the frozen code/inputs,
a valid committed lease and checked remote head. The completed project's lease is released, so merely
rerunning its design command from the final commit is intentionally not permitted by the admission guard.
