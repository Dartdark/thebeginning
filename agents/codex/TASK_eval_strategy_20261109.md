# Evaluation-first strategy development: active manual research task

Summary: Develop a strategy that improves the evaluation books within 30 calendar days; prioritize other markets.
User steering November9,2026Pacific: seek diversification outside the NQ-heavy book; changing/replacing VB is allowed.
Immediate focus is gold's participants/mechanism and a hypothesis first; crude, FX and Treasuries follow.
The completed new-data NQ batch qualified no strategy; do not repeat its failed funding/fear definitions.
No market's low correlation or account benefit is assumed, and no live or scheduled program changes.

User request, 2026-11-09: evaluation is the priority; develop a strategy to strengthen it, “all hands on deck.” This task does not create schedules or authorize external messages, broker/VPS/orders or portfolio changes. Work only on codex/work and preserve other work.

## Latest direction: other markets first (user, November9,2026Pacific)

The user explicitly wants the research focus moved to other markets because of potential low correlation with
the existing book. Apply that direction to subsequent manual research; another NQ variant is no longer the default.
This is a research-priority change, not authorization to trade, relax evidence gates, or resume paused programs.

Prioritize **GC/MGC and CL/MCL**, then **6E and ZN** where native costs, sizing and source data permit.
The repository has2018/2022/2026minute files for all four, with broader2017–26annual histories previously inventoried;
file presence does not certify every session, roll, executable contract, micro feed or historical signal input.
Use the market's own documented participants/flows and a genuinely new admitted hypothesis. Preserve old failures
in gold breakouts/filters, commodity releases/settlement, FX fixes and Treasury month-end families.
Do not relabel a failed NQ rule by changing the ticker. ES/YM remain eligible for a specific distinct mechanism,
but have lower priority as sources of a different risk exposure than US equity-index trading.

Separate three questions:
1. Does the strategy have an edge after its actual contract costs and execution assumptions?
2. Does its **strategy P&L**, including losses on VB/ONB stop days and common macro shocks, diversify the book?
3. At integer size, does it improve passes/fees/time before the30-day deadline and before an intraday breach?

Low covariance can let a modest positive edge contribute more than another correlated equity rule. It does not
create an edge or guarantee better first-passage outcomes. Trading frequency, loss timing, executable maximum
exposure and contract granularity still matter. Measure correlations across matched dates, eras and stress
episodes; underlying market return correlation is not a substitute for the strategy/account comparison.
General context, not a measured result for this book:
[CME on changing cross-asset correlations](https://www.cmegroup.com/articles/2025/exploring-diversification-within-commodity-markets.html).

Completed records to retain: [new-data strategy batch](results/new_data_strategies_20261110.md),
[direct VB split-stop rejection](results/vb_loss_split_20261110.md). No candidate from those batches earned adoption.
The earlier source lanes below remain historical leads/data gates; they do not override this new market priority.

## Read and synchronize

Latest completion after user said "do it": [gold crowding feasibility](results/gold_crowding_feasibility_20261110.md).
Committed no-return census `44df28eb`: 38 crowded entries in 2018–22; only 20.4% of 30-calendar-day windows contain one.
Event-count and opportunity-coverage gates fail. Free Managed Money data partially reconciled; original vintages and
native execution remain unverified. Zero economic returns, no recent/account stage. Close this implementation without
retuning; the prior data-gate next step below is historical, not an instruction to rerun the failed candidate.

Latest user step, November 9, 2026 Pacific: explain why gold moves, who trades it and formulate a hypothesis before
returns. Completed [market map / crowded-long liquidation hypothesis](results/gold_market_hypothesis_20261110.md)
and [source/evidence sheet](evidence/gold_crowded_longs_20261110.md). Status NEEDS DATA / untested, 0 new returns;
the key next check is disaggregated gold Managed Money fields plus actual publication exceptions, then a
no-return frequency/power census. Existing local Legacy COT is not a substitute. No immediate strategy
test or revived failed clock rule is implied; exact future parameters/code must be committed before returns.

Read AGENTS, the entire Codex builder brief, RESEARCH_CONTROLS, current Claude NEW_CHAT_BRIEF, DEVELOPMENT_PROCESS, TIER_LIST, WATCHLIST, LESSONS and this task. Current inspected Claude head: `3e08d56` (evaluation diagnosis and builder). Refresh before continuing. Keep the paused lab/scout/t6/Hunt programs paused.

Completed phase A: `agents/codex/results/eval_focus_baseline_20261109.md`.
Frozen plan/code commit: `5815ed6`.
Existing diagnosis: `analysis/eval_failure_diag.py` on Claude; capped-set builder `analysis/eval_set_builder.py`.

## What the new strategy has to do

The objective is paired **pass probability before the actual deadline**, with time-outs counted as lost attempts, at real integer size and native costs. A higher win rate, smoother standalone equity curve or lower trail failure rate is insufficient. Do not optimize for funded payout caps; this study concerns evaluations.

Preferred target: a source-supported, recurring return stream with sufficiently frequent opportunities, modest standalone risk, and weak common-loss exposure to VB/ONB. Seek a meaningful pass improvement (a practical research ambition is +5 percentage points) without using that aspiration to loosen the registered acceptance rule. For comparison, improving 150K pass 37% to 42% would lower the idealized fees-per-pass index by about 12%; that is an illustration, not a forecast.

The candidate must enter early enough for its profit/risk effect to matter on the account's actual path. Money earned after a trail breach or DLL pause cannot rescue that day. Screen hours actually unoccupied by open positions, not only dates with zero booked P&L. A different symbol can retain the same macro direction/risk.

The 150K book is the first research target because it is the current expansion focus; also report the unchanged 50K book. Do not assume membership or size from old top-level README tables.

## Proposed division of work for user-forwarded coordination

These assignments are a review packet, not a claim that other assistants have received it or begun work.

| Role | Concrete work | Deliverable / boundary |
|---|---|---|
| Codex | Build source/data-admitted hypotheses; commit exact code/rules, run cheap design gates and every earned native-calendar account comparison | Reproducible rule, trial ledger, paired BASE/ADD/REPLACE/EMPTY tables; no live edits |
| Claude | Independently check the baseline, risk-rounding discrepancy, account clocks and minute/DLL/Bridge/Twin path assumptions; independently develop a distinct economic family if assigned by the user | Review findings first; exact preregistration before new returns; no assumed agreement |
| Dot | Inventory current tasks and retrieve permitted free source/availability evidence for missing inputs; prepare complete task packets | Source URLs, hashes, coverage, availability/vintage limits; preserve pauses and do not duplicate scout |

## Candidate lanes and gates

1. **Macro surprise rather than the first-minute price move.** Existing source SSRN1920401's earlier draft Section VI concerns initial actual-minus-consensus direction one minute after release for a one-minute hold; prior price-response tests do not reproduce it. A newly acquired free panel includes historical CPI/core CPI/payroll/claims/retail actuals and forecasts. This is a genuinely new *input lead*, not a tested edge. Before any returns, resolve the documented timestamp error, first-actual/revision provenance, exact pre-release forecast identity, source-version rule and publication-to-entry delay. `D51` in DATA_NEEDED retains the original source-specific requirements. If those cannot be cleared, keep it parked; do not substitute revised FRED values, assume a median, or change the hold to produce a new result.
2. **Direct opening/closing auction information.** Existing registered source/data gates remain binding. Need actual historical messages and clocks; SPY Arca and NYSE stocks are different products. No price-only auction proxy or paid acquisition. This lane is already known and data-blocked; it is not a new trial or permission to rerun the old MOC definition.
3. **A distinct, source-supported inventory/hedge flow in an owned contract.** Avoid the rejected CL/NG release and generic roll/fix/indicator families. The new Dow opening-reversal abstract is only a feasibility lead: exact rules are withheld/inaccessible in the inspected materials, and an unobserved 0DTE dealer inventory cannot be inferred from a green candle. Do not invent a paper replication. Seek complete primary rules/data or another distinct admissible family.

These are source-feasibility lanes, not three approved backtests. Keep the batch at at most three distinct source/evidence evaluations; do not reset scout/program/global multiplicity. A new return trial requires its own evidence TEST verdict, exact committed plan/code and an explicit within-family variant/control count (at most five; stricter source/task limits apply).

## Before any new account promotion claim

- Verify risk rounding is **floor(total risk / per-contract stop dollars)** at the frozen account quantity, not a multiple of already floored $250 units. Review the source discrepancy in the baseline report before comparing a candidate to “the current set.”
- Reconcile trades and daily/native minute paths, identify all report coverage gaps, and resolve or bound missing observations. Bridge Sunday booking and Twin midnight carry conventions need explicit treatment; the existing baseline is conditional on those helpers.
- Do not use a perfect fill at the DLL as an execution fact. Retain a registered adverse/liquidation stress and distinguish a one-minute bound from tick-level replay.
- Freeze the candidate and selection on 2018–22; already-seen 2023+ is historical replication. If a proposed mechanism only begins in 2023, register a defensible alternative chronological design before touching its returns rather than silently calling older years suitable.
- Earn each stage: cheap net-edge/cost screen, controls, recent replication, paired native-calendar BASE/ADD/REPLACE/EMPTY, then independent/native/forward review. Freeze the replace/empty slot before opening recent results.
- Candidate acceptance: positive recent paired pass-rate improvement with a prespecified interval excluding zero, surviving the prespecified execution/cost stress, plus all registered edge/risk gates. No post hoc ranking, repeated recent looks or “best size” promotion.

## Checkpoint and output

The baseline and source-feasibility intake are completed; **strategy development remains open**. No new strategy return test or promotion occurred in phase A. Next work is the macro panel's no-return source/clock/vintage admission check and a distinct eligible source lane, plus independent verification of the baseline findings. This task file does not claim background execution after a chat ends.

User correction / progress, same day: the price history, macro actual/forecast panel and saved official calendars are already owned. [Reconciliation](results/eval_owned_data_reconciliation_20261109.md) confirms the calendar matches and resolves the payroll clock error in a derived sidecar. Do not request duplicate acquisition; continue validation of forecast/initial-actual vintages and decision-time availability. Source values and return-admission flags remain unchanged.

Reports begin with Summary (at most five lines), identify source/plan/code/input refs, disclose all economic trials and show key results directly in chat. Produce the exact report path for the user to forward to Claude. Never send external messages automatically.
