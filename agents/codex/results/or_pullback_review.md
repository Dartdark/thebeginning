# ORPullback: WATCH as research, no current-plan addition justified yet

Summary: The supplied evidence does not yet justify adding ORPullback to the current plan or replacing a leg.
Its author reports $12.64 per MNQ and PF 1.23 after 2020, but the separate test/holdout t-statistics are only 1.54/1.86.
One-MNQ closed-equity drawdown is $1,868; the code's first post-entry bar lacks generated explicit brackets under its stated ordinary IOG-off setup.
There is no exact-source parity export or paired current-plan addition/replacement result; its LucidFlex simulation is a different comparison.
Keep the current plan unchanged; original ledgers and source execution reconciliation are the next evidence, not a forced ONB contest.

User scope: **put it against the current plan overall**. ONB is not a compulsory competitor or replacement.
Scope record: `agents/codex/plans/or_pullback_source_review.md`; evidence: `agents/codex/evidence/or_pullback.md`.
Input archive: `agents/codex/inputs/or_pullback/{source.txt,report.pdf,report_extracted.txt}` (unchanged originals, hashes in output).
Script/output: `analysis/codex_or_pullback_review.py`, `analysis/outputs/codex_or_pullback_review/{summary.json,reported_periods.csv}`.
Context: Codex `e0277c3bca8cdb7a8bd2c1361c9183bfeb015694`; latest Claude `a67035be4189b493098c80f1def979348520fd5d`.
New strategy-return trials / account simulations: **0 / 0**. Author's search count and freeze registry: not supplied.

## What this would contribute

Five-minute bars; first fifteen-minute regular opening range. A close beyond an edge arms a side. The first **later**
counter-colour bar still closing beyond that edge triggers a close entry. Normal configuration has a 50-point stop,
100-point target, at most two triggers/trades and two losing trades per day, one open position at a time.

Correctly configured in CT: OR 08:30-08:45, earliest possible trigger 08:55 (08:50 earliest arm, then a later bar),
entry cutoff 14:30 and normal flat 14:55. It is an intraday continuation candidate with potentially different entry timing
from the existing legs. The rule does not have to beat ONB alone to earn a place; it could add useful portfolio returns
or replace whichever slot it actually overlaps. Neither useful diversification nor high correlation is established yet.

Its one-MNQ nominal bracket is $100 risk / $200 target, with two nominal stop distances totaling $200 before costs and
adverse fills. One **NQ** instead is $1,000 / $2,000, with two stop distances totaling the nominal $2,000 initial trail.
These are arithmetic amounts, not guaranteed loss caps. The file has fixed quantity, not the funded plan's cushion controller.

## Reported evidence, not independently reconstructed returns

The research note, PDF p. 3, reports these values on **one MNQ**, net of a two-dollar round-trip allowance:

| Period | Trades | PF | Mean net | Total net | Closed-equity DD | t |
|---|---:|---:|---:|---:|---:|---:|
| 2021-23 selection | 902 | 1.25 | $13.35 | $12,046 | $1,540 | 3.04 |
| 2024-July 2025 test | 477 | 1.17 | $9.58 | $4,568 | $1,868 | 1.54 |
| August 2025-July 2026 claimed sealed holdout | 286 | 1.27 | $15.51 | $4,434 | $1,428 | 1.86 |
| All 2021-26 | 1,665 | 1.23 | $12.64 | $21,048 | $1,868 | 3.83 |
| Longs, all 2021-26 | 883 | 1.24 | $13.06 | $11,530 | $1,344 | 2.93 |
| Shorts, all 2021-26 | 782 | 1.21 | $12.17 | $9,518 | $1,876 | 2.48 |

Counts and totals reconcile across periods and sides, and the reported stop/target/time exit counts sum to the trade
count. That is an arithmetic check, not proof of the underlying trades, statistical validity or code parity.

Positive separate periods and positive long/short means are useful evidence. However, the headline t=3.83 includes the
selection sample. The separate test t=1.54 and claimed sealed-holdout t=1.86 are modest, and neither alone clears the
usual t=2 reference. This is not a claim that the author set and failed those exact gates, or that a combined validation
statistic must be below two; the original daily ledger would be needed for the declared independent test.
The structured search's variant count, DSR, placebo evidence in the profitable period and independent freeze chronology
are absent. The required repo 2018-22/2023+ split is also not supplied. Six positive recent years do not remove selection risk.

The note reports 2,693 trades in 2010-20 with PF 0.94, -$1.4/MNQ and t=-1.1 (p. 4). Its price-scaling check, ES/GC
checks and lack of an options-expiry fingerprint acknowledge limits; they do not identify a durable cause for the recent
edge. A negative old period does not itself establish that the exact 2018-22 design slice is negative. The disclosed
random-direction control concerns 2010-20; it does not establish that the profitable 2021+ pullback beats matched random
side, immediate-breakout or simple delayed-entry controls.

## Put against the current plan

Latest saved real-fee benchmark at Claude `a67035b`, `analysis/outputs/real_fee_bench_output.txt`:

| Account objective | Current plan, published baseline | Current plan plus ORPullback |
|---|---|---|
| 50K Apex evaluation pass rate | 49.8% at the assumed actual micro fee | Not measured |
| Funded expected payouts, year 1 / year 2 | $9,180 / $11,982 | Not measured |
| Funded blown / median days to six payouts | 7.6% / 263 days | Not measured |

These are existing plan outputs, not a fresh rerun or a performance forecast. ORPullback is absent from that run. Its
standalone $21,048 over the selected recent sample cannot be added to the plan's capped funded payouts or compared
directly with those figures. The note's 35-44% pass-within-sixty-days figures are for **standalone two-MNQ LucidFlex-style
rules** (p. 5), not the current combined Apex evaluation. They are not a valid head-to-head against 49.8%.

The candidate's NQ exposure can coincide with several current morning/afternoon positions. No actual overlap map,
conditional-loss analysis or paired account history is provided. The relevant hurdle is a gain on the **whole plan** after
costs/cushion sizing/netting and intraday risk: addition, a justified replacement and the empty-slot control. Moving profits
between legs or improving standalone PF is not enough. A $1,868 one-MNQ closed-equity drawdown is close to the nominal
trail but is not an annual blow-up probability or proof of certain account failure; actual cushion, trail lock, withdrawals,
other legs and minute paths determine that result.

Fees are not the main objection. The note's one-point-per-MNQ allowance is $2 round trip, near the latest assumed
$1.04 fee plus two $0.50 market/stop slippage ticks = $2.04. Target executions have a different fill/cost path and need the
actual ledger. Two additional ticks **each side** cost another $2/MNQ, about 16% of the reported mean; close execution,
target trade-through and first-bar protection matter more than alleging a large fee mismatch.

## Source/report parity and readiness

1. **Initial protection is delayed under the declared ordinary setup.** Close entries at lines 92-93 are issued while flat;
   the MarketPosition exit branches at 98/105 are skipped at that calculation. At the following five-minute close the
   source observes the position and generates **next-bar** brackets. The first full post-entry bar therefore lacks these
   explicit orders. IOG off plus one-minute Bar Magnifier does not pre-generate them. Exact broker-event settings can
   affect live sequencing, so verify a first-fill/stop-submission trace. The note's minute-fill description does not document
   that same unprotected interval; parity must be demonstrated rather than assumed. No resulting loss is quantified here.
   [MultiCharts IOG/Magnifier behavior](https://www.multicharts.com/trading-software/index.php?title=Why_is_Data_Playback_strategy_performance_different_from_Backtesting_results%3F).
2. **Close fills require evidence.** Knowing a completed close before submitting an order does not establish a fill at that
   historical close. Both entries and the normal time exit use close orders. The syntax is supported; the assumption
   needs timestamped executable reconciliation, not an unsupported claim that all such orders are backtest-only.
   [MultiCharts calculation/order lifecycle](https://www.multicharts.com/trading-software/index.php?title=How_Scripts_Work).
3. **Holiday handling is incomplete.** Time>=tFlat gives an ordinary late-bar fallback, but no early-close calendar or early
   flatten exists. SetExitOnClose follows configured sessions and is documented as backtesting-only, with rejection risk
   at the final session tick; it is not a verified live holiday safeguard. No actual overnight carry is established here.
   [Official SetExitOnClose documentation](https://www.multicharts.com/trading-software/index.php?title=SetExitOnClose).
4. **The proposed regime switch is absent.** The note's rolling-six-month profit/DD switch-off/resume rule is not in the
   supplied source. Its old-loss reduction and recent-profit sacrifice are author-reported sensitivity results. They do
   not validate an independently frozen regime detector; its norm, checkpoints, execution timing and shadow tracking
   when off would need definition. Do not attribute those filtered results to the delivered default or adopt the overlay.

Other source details are coherent: OR bars close at 09:35/09:40/09:45 ET; reset at the first RTH bar works on appropriate
full-session or RTH charts; loss counting uses MultiCharts currency P&L. Brackets are anchored to **EntryPrice**, not the
prior uploaded file's signal-close levels. Default ChartIsCentral=false is an explicit NY/Bridge preset; Chicago feeds need
true, as the source says. This is a configuration dependency, not an unconditional timezone bug. PriceScaled=false is the
delivered rule; optional scaling results are a different configuration.

Arming persists after a return inside the range. A later eligible counter-colour close outside can still trigger, so the rule
does not prove uninterrupted breakout defence or a better entry price. A trigger blocked by a guard intentionally consumes
that side, consistent with both code and note. Those are rule definitions rather than accidental counter errors.

## Decision and next evidence

**WATCH as a candidate; keep the current plan unchanged.** There is positive reported recent evidence, but no verified
incremental portfolio gain or exact-code execution reconciliation. This does not prove ORPullback loses, and it does not
require it to compete specifically with ONB. No new grade is assigned for Claude.

Smallest next evidence: original timestamped trades/daily paths, search/freeze provenance, and a current-source MultiCharts
export with settings and a first-fill bracket trace. Resolve the execution/holiday specification before a separately
preregistered exact-rule or corrected-rule replication and any paired account bench. Evaluate all eligible events, then
assess overlap; do not cherry-pick only times the existing plan is flat. Promotion still needs the latest independent
statistical and account gates. The note's trading instructions and switch-off proposal were not adopted.

Validation here: all PDF pages extracted/rendered and material tables visually checked; reported arithmetic/source defaults
checked by the audit script; independent read-only source and plan-context reviews. No new price returns, optimizer,
account simulation, compile, source change, plan edit, cache rebuild, live access or PR action occurred. Latest real-fee and
Twin daily-mark checks are closed in the current brief; they are not carried forward as open items by this review.
