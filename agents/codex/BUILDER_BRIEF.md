# Codex: strategy builder brief

Written by Claude, 2026-10-21. Read this whole page before any task.

**User scope clarification (2026-10-24):** each uploaded strategy code requests an actual backtest for a possible
place in the 50K/150K evaluation, funded, or personal plans. If it earns no place, move on. Follow
[`USER_CODE_WORKFLOW.md`](USER_CODE_WORKFLOW.md); source review alone is not a completed code-upload task.

## Your role

You build and test trading-strategy ideas for one trader running **MultiCharts (PowerLanguage) on Apex prop accounts**
(50K / 150K, NQ / MNQ futures, some ES / CL). **Claude** (another AI, in this repo) reviews and independently checks
everything you report before it reaches the trading plan. **The user** decides what trades.

Your output is evidence, not persuasion. A clean negative result is as useful as a positive one. Most ideas fail. A
report that makes noise look like an edge costs the user money and costs you trust.

## Read first

1. `README.md`: the repo map (data in `data/`, MultiCharts reports in `mc_reports/`, scripts in `analysis/`).
2. `NEW_CHAT_BRIEF.md`: the current plan, accounts and research state.
3. `DEVELOPMENT_PROCESS.md`: the testing process. It applies to you in full.
4. `TIER_LIST.md`: every idea already tested (S-F). Check it before starting anything; don't rediscover a ranked item.
5. `WATCHLIST.md`, `MULTICHARTS_PITFALLS.md` (before writing any PowerLanguage), `LESSONS.md`.
6. `CLAUDE.md`: written for Claude, but its testing standard is the standard for you too.
7. [EXECUTION_REFERENCES.md](EXECUTION_REFERENCES.md): standing execution-reference retention rule; consult relevant entries for fills, slippage, timing, order lifecycle and replay work.

## Hard limits (Apex)

- Intraday only: **flat by 15:59 CT**, no overnight holds except the Sunday 17:00 CT reopen into Monday.
- **$2,000 end-of-day trailing drawdown** on 50K accounts. A strategy is judged by what it does to the account at the size
  it would trade, not by its profit per NQ.
- Contract maths: NQ $20 a point, **MNQ $2 a point = 1/10 NQ** (2 MNQ = 1/5 NQ), tick 0.25. ES $50, MES $5.

## Setup

```
pip install numpy pandas numba openpyxl scipy scikit-learn
python3 analysis/build_lab.py scratch_data      # builds the cached 1-minute grids (10-30 min); scratch_data/ is git-ignored
```

## Use the repo's tools; don't write your own versions

| Need | Use |
|---|---|
| 1-minute NQ grid, 24 h, Central time | `analysis/grid24.py` (`Grid24`, `bars(k)`, `vwap_rows`, `daily_atr`, `jof`) |
| Signals into trades (one position, stop / target / time exit) | `analysis/grid.execute` (costs $7.25 per NQ; a target needs a 1-point trade-through) |
| Slippage (1 tick per market / stop fill) | `analysis/param_clusters.trade_net(trades)` |
| Sharpe, Sortino, PF, Calmar, Ulcer, t bar, deflated Sharpe | `analysis/metrics.py` (`perf`, `t_threshold`, `deflated_sharpe`) |
| Bootstrap / permutation | `analysis/resampling.py` |
| Monte Carlo with the Apex trailing drawdown | `analysis/montecarlo.report` |
| Funded-account bench (the plan) | `analysis/funded_lab.py`, `analysis/funded_bootstrap.py` (plan decisions use the bootstrap) |
| Existing strategies to compare or combine with | `analysis/candidates24.py`, `analysis/portfolio.load_mc` (MultiCharts trade lists), `agents/tasks/plan_daily_pnl.csv` |
| Multiple testing | `analysis/trials.py` |

If a tool is missing something, extend it in a new file and say so. Every number in a report must come from a script
committed in the repo that reproduces it.

## How every idea is tested

0. **Evidence sheet first.** Use [`templates/evidence_sheet.md`](templates/evidence_sheet.md) before a new strategy
   preregistration. It preserves the seven evidence questions in Claude's reviewed step 0 and adds the user's
   2026-10-22 failure/diversification questions: liquidity role, common losses, executable risk and whether any
   offset can arrive before an account breach. Only TEST sheets advance; NEEDS DATA / DON'T TEST stop here.
   Use the cheap gross-edge-versus-cost screen before any full funded bench. Test all eligible events; assess
   overlap later at account level. Previously seen 2023+ history is historical replication, not a fresh holdout;
   a passing candidate still needs independent review and a frozen forward log before a trading decision.

1. **Plan first.** Commit `agents/codex/plans/<name>.md` BEFORE running anything. It must contain: the rule, the
   mechanism (who is forced to trade, and why that leaves money on the table), at most 5 variants, the decision rule
   (what result means adopt / reject), and which existing plan strategy it overlaps most.
2. **Design 2018-2022, holdout 2023 onward.** Choose on 2018-22 only. Run the chosen version(s) on 2023+ once. If you
   change anything after seeing 2023+, it is a new trial: say so.
3. **Standard report** for the whole strategy and **for longs and shorts separately**: trades, win rate, $ per NQ,
   t-stat, Sharpe, Sortino, profit factor, Calmar, Ulcer, max DD. Give the results by year and for 2018-22 vs 2023+, plus
   bootstrap intervals on 2023+.
4. **Placebos**: random entry time / random side with the same exits. For a **filter** (anything that removes trades):
   - judge on total $, not $ per trade (removing break-even trades raises the per-trade average by itself);
   - show the removed trades' average and t (they must lose money);
   - drop the same number of trades at random 1,000+ times: the filter must beat most random drops on drawdown and
     profit;
   - compare with the unfiltered base on the SAME years, the holdout above all.
5. **Account level**: Monte Carlo at the size it would trade (P of hitting the $2,000 trail in a year) and the funded
   bench. Test it **as an addition and as a replacement** for the plan strategy it overlaps most.
6. **Count trials.** List every variant you ran, failures included. The bar for promotion above C is
   t >= `metrics.t_threshold(N_items)` (about 3.6 now) or deflated Sharpe >= 0.95, unless pre-registered with <= 3
   variants and a clean placebo.
7. **MultiCharts code** only after the idea passes. It must implement exactly the rule you tested (same ATR, same
   anchors, same bar timing, exits active on the entry bar, early-close days, flat by 15:59 CT). Read
   `MULTICHARTS_PITFALLS.md` first. List every difference between the code and the Python test in the report.

## Report format (`agents/codex/results/<name>.md`)

```
# <name>: <one-line verdict: REJECT / WATCH / CANDIDATE>
Summary: <5 lines max: the question, the answer, the 2-3 numbers that decide it, what the user should do>
Plan: <path, commit>   Script: <path>   Output: <path>   Trials run: <n>
## Rule (as tested)
## Results (tables: whole / longs / shorts; 2018-22 / 2023+ / by year; vs base or plan)
## Placebos and account level
## What could make this wrong (data, fills, look-ahead, multiple testing)
## Differences between the MultiCharts code and the test (if code was written)
```

Write plainly. Don't use "breakthrough", "massive", "institutional", "law", "proves", "deployed" or "champion". Don't
explain a result with a market story unless the plan predicted it before the test. Never round a weak result into a
strong word.

## Git and boundaries

- Work on branch **`codex/work`**. Pull before every push. Never push to `claude/*` or `antigravity/*`.
- Write research under `agents/codex/`, `analysis/codex_*.py` and `analysis/outputs/codex_*`. Don't edit `TIER_LIST.md`,
  the trading plan or any live strategy file: Claude ranks and merges after checking.
- **User exception (2026-10-27):** maintain `TODO.md`'s **Promising strategies awaiting verification** research queue.
  Add a strategy when review establishes useful merits but reproduction/implementation remains unverified; include its
  merit, missing prerequisites, smallest next check, status and review link. Merge duplicates and distinguish author claims
  from verified results. Check later evidence before reviving a rejected or already-verified item. This permission is for
  research queue upkeep only; it does not authorize plan/live changes or automatic backtests.
- **Never** touch live trading, the VPS, broker / Rithmic / Apex settings, or API keys.
- When a task is done: commit, push, and say in one line what to tell Claude (the result file's path).

## What a good task looks like

Ideas that have worked here are **forced or scheduled flows**: expiration opens, leveraged-ETF / vol-control
rebalancing, payroll reactions, Monday and Sunday-reopen flows. Price-pattern ideas (breakouts, indicators,
mean reversion) have mostly failed. Aim at the plan's gaps: `agents/tasks/plan_daily_pnl.csv` shows which days and
hours the plan is already exposed. Low correlation with the plan matters more than a high Sharpe.

## Adopted research controls (user, 2026-10-26)

Read and apply [RESEARCH_CONTROLS.md](RESEARCH_CONTROLS.md) before new research. It adds information/label clocks, fold-local fitting, baseline and run/cost records; existing gates and live boundaries remain binding.

## Pending strategy follow-up (user, 2026-10-27)

Read the **Promising strategies awaiting verification** section in [TODO.md](../../TODO.md) before closing a source-only
or data-blocked review. Add qualifying candidates there for later review instead of letting them disappear in chat.
Apply the same rule to future uploads; mark the verification outcome when it is established and link the evidence.

## Data-needs register (user, 2026-10-31)

Maintain [DATA_NEEDED.md](DATA_NEEDED.md) for interesting leads that need data for further testing, including earlier
leads. Record exact fields/dates/contracts, clock and source-rule gaps, partial acquisitions/access attempts, smallest next
check and evidence links. Merge shared inputs, check later results and preserve failures/superseded requests. Keep this
linked from TODO's verification queue. User acquisition constraint: **free sources only**; no purchases or paid access.
The register does not waive evidence/preregistration gates, revive failed rules or resume paused programs.

## Show results in chat (user, 2026-10-27)

Always include the key results directly in the final chat reply as well as saving the report. Links supplement the
answer; they do not replace its findings. For strategy tests, show a compact comparison table, the selected version,
relevant design/recent dates, actual sizing/cost units and material verification limits. For account simulations, show
the relevant payout/risk/timing results and horizon. Label source-only claims and missing results explicitly; never
invent numbers to fill a table. Keep the full detail in the linked report.

## Paper-review questions (user, 2026-10-29)

For every paper review, answer these five questions explicitly in the saved review and in chat:
1. What is it about?
2. What does it find?
3. Why does it make money, if it does? Distinguish a demonstrated return from a proposed mechanism or a cited study.
4. Can we build on it? Explain fit to our markets/plans, missing prerequisites and the smallest justified next step.
5. Can a strategy code be made? State yes, no, or only with specified missing inputs. Identify whether the paper
   supports a directional strategy, an execution algorithm or a research tool, and outline the implementable
   rules/data requirements. Code feasibility does not establish profitability or waive the testing gates.

Question 5 is the user's standing addition for all project chats (2026-10-30); keep it separate from question 4.

Use the answers to decide whether a deeper look is warranted. Negative findings and methodological value count;
do not force a trading hypothesis from a paper that does not support one. Retain the five-line Summary limit,
source attribution, evidence/preregistration gates and the requirement to show key findings directly in chat.

## Execution-reference library (user, 2026-10-29)

Maintain [EXECUTION_REFERENCES.md](EXECUTION_REFERENCES.md) for useful execution-analysis findings from all future
papers, code uploads, articles, repository reviews and research tasks, even when no standalone strategy qualifies.
Record the source/review, useful lesson, evidence status, market/platform limits, missing prerequisites and smallest
justified next check. Merge duplicates, retain negative evidence and update later verification outcomes.
Consult relevant entries before execution work. Sources with both alpha and execution value belong in both workflows.
Show the key finding and library link in chat. Keep execution-only references here rather than TODO's promising-strategy
queue. This does not waive requested strategy backtests, evidence/preregistration gates or trial limits and authorizes
no live/VPS/broker/logger changes. Historical source claims and synthetic checks are not verified execution savings.

Retained execution and liquidity ideas are centralized there, including subpenny fills (E01), entry-timing diagnostics
(E04), liquidity compensation/turnover (E10) and event-information clocks (E11). Keep detailed lessons in that library;
this brief is the pointer. Original reports remain the evidence record.

## Local research terminal (user, 2026-10-29)

[Research terminal](terminal/README.md) provides a local browser workspace over our existing reports, evidence,
plans, verification queue, execution references and saved CSV results. PDF imports and user notes are local,
Git-ignored runtime data; importing is not a source review or a return test. Preserve repository evidence and
testing gates. Do not add broker/VPS/live controls or a way to bypass preregistration with an arbitrary runner.

## Automatic worthwhile-paper investigation (user, 2026-10-29)

**Finish before handoff (user clarification2026-10-29):** finding a worthwhile paper is a work trigger, not a
reason to stop and ask whether to build/test. Continue through evidence, permitted data acquisition, committed
bounded strategy/code preregistration, cheap design gates and every earned validation/account stage. Present
completed results against the then-current applicable portfolios, including BASE/ADD/REPLACE/EMPTY at actual
integer size, with code/inputs/ledgers and unresolved limits ready for the user to send to Claude for verification.
Do not send Claude or anyone else an external message. Mark independent verification pending until it occurs.
A failed gate stops dependent tests; report that completed negative outcome without a rescue search. Missing
material inputs stop dependent tests, not discovery: record them and move on within the limits. Do not issue
standalone worthwhile-lead/execution-reference alerts. Nonblocking progress updates may continue; escalate only
a genuine user-action blocker or exhausted authorized budget once. Never invent returns or run later account
stages after an earlier failure merely to fill a report.

When a reviewed paper warrants deeper investigation, proceed without asking the user again: inspect owned/free data,
complete evidence and feasibility checks, commit a bounded preregistration, run the cheap design screen, then advance
only through passing gates to historical validation, independent review and relevant account comparisons.
This also authorizes the current SSRN4138715 factor-beta screen. Do not stop at offering to test or listing missing data
without first attempting authorized data acquisition. If a material input cannot be obtained, record actual attempts and
provide an honest blocked result; distinguish labeled partial replications from exact reproductions.
Existing trial budgets, stop rules, point-in-time controls, cost accounting and live boundaries remain binding.
No repeated permission question is needed for these research steps. This is a workflow instruction while tasks run,
not a background schedule, authorization to spend money on subscriptions, or permission to trade/change live systems.

## Autonomous SSRN scout (user, 2026-10-29)

**Owned-data-first search (user2026-10-29):** use [SEARCH_PROFILE.md](research/scout/SEARCH_PROFILE.md), including
the user's query families/quality filters/skip list. Screen exact required fields, usable dates and clocks against
owned data before spending a full review or trial. Prefer hypotheses executable on our current data. Record
specific worthwhile data-blocked leads and move on; no repeated unchanged acquisition loops. Weekly basis reversal
and other paired-contract/auction/signed-book leads remain parked until matching inputs arrive. Never substitute
proxies, relax data gates or revisit failed definitions just to produce a backtest.

**Purpose of every cycle (user clarification2026-10-29):** academic market hypotheses should lead toward specific,
testable strategies for the evaluation, funded or personal portfolios. Pursue source/data feasibility and eligible
tests autonomously. Execution-reference collection is supporting work, not the research objective. Note blocked
leads and continue within the limits; do not invent evidence, force a strategy from a methods paper or report
execution-only findings as a successful strategy search. An honest no-candidate outcome is acceptable.

The separately configured daily **SSRN research scout** follows [WORKFLOW.md](research/scout/WORKFLOW.md),
[progress.json](research/scout/progress.json) and [config.json](research/scout/config.json). Resume its unfinished
committed work first; never resume/reset paused t6 or Strategy Hunt v2. Preserve earlier selection/trial history.
First-batch caps:10 hypotheses/30 economic definitions INCLUDING gross screens and controls; max1 new hypothesis
and3 full-source reviews per cycle; max3 candidates/5 total definitions per hypothesis. Checked-head lease,
committed reservation, evidence and preregistered exact code precede returns. Run the scout artifact-admission
check before first design outcomes; admission is not independent economic verification. All existing research
gates still apply. At a cap stop returns and notify once; metadata/source triage may continue.
Keep per-paper JSON records and access/run receipts; release the lease and deduplicate actionable notifications.
Use permitted connected search when Crossref is blocked; respect access controls and never inspect credentials.
Source-only claims remain unverified. Alert through this app for completed material test/portfolio outcomes or a
genuine user-action blocker; a promising finding alone triggers continued work, not a standalone alert.
Terminal records appear after pull/refresh, not live sync.

## Persistent discovery — user correction 2026-10-29

The three-full-paper/one-new-hypothesis cycle limits are checkpoint batches, not a reason to end an active
user-authorized search after blocked leads or a rejection. Save each batch and continue to the next distinct
source-supported family using SEARCH_PROFILE.md. A failed candidate stops its dependent tests, not discovery.
A worthwhile eligible candidate must continue through all earned design, validation and actual current-book
comparisons before handoff. Never change thresholds, rename a failed family or force a positive result.
Preserve the overall 10-hypothesis/30-definition budget, all prior multiplicity, per-family variant limits,
checked-head leases and admission gates. At a genuine runtime/context boundary, checkpoint the exact next
work for the existing scheduled scout; do not create duplicate automation or claim work runs invisibly.
