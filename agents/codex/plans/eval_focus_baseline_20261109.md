# Evaluation-first research: baseline protocol and candidate admission

Summary: The user requests a strategy specifically to strengthen evaluations, with the deadline treated as binding.
Freeze the present 50K and 150K stacks; first isolate calendar, native-fee and DLL-fill assumptions.
Do not optimize the stack, change entries, resume a schedule or alter plans/live systems.
New alpha needs a separate evidence sheet and exact committed implementation before its returns.
This phase produces a reproducible baseline and a concrete evaluation-specific research mandate.

## Authorization and sources

User, 2026-11-09: switch focus to evaluations and develop a strategy to bolster them. This is an active manual research task; lab/scout schedules remain paused. Read AGENTS, builder brief, research controls, current Claude process/tier/watch/lessons, and the new evaluation diagnosis/set-builder before running.

Pinned reviewed branch: `3e08d56e4e0a3761bd622cf17dfcab7c018d4e18`.
Read-only source copies/manifest: `agents/codex/inputs/eval_focus_20261109/`.
Script: `analysis/codex_eval_focus_baseline_20261109.py`.
Outputs: `analysis/outputs/codex_eval_focus_20261109/`.
Source raw files: existing `/workspace/thebeginning/data`, pinned per file before outcomes; preserve existing histories and recorded trials.

## Freeze the current account books

| Book | Start / target / EOD trailing distance / DLL | Frozen sizing |
|---|---|---|
| 50K | $50,000 / $3,000 / $2,000 / $1,000 | VB 8 MNQ; ONB ADX30 risk $1,100 at 0.25 x prior ATR15; Bridge Monday 2 MNQ; EOS risk $500 at 0.30 x ATR15 |
| 150K | $150,000 / $9,000 / $4,000 / $2,000 | VB 20 MNQ; ONB ADX30 risk $2,750; Bridge Monday 5 MNQ; EOS risk $1,250; Twin cap1 v2.1 2 MNQ |

Risk-sized quantities are floored to integer MNQ. Existing entry/exit lists and source target/slippage conventions remain frozen. Evaluation floor keeps trailing; never apply the funded PA lock. Prop/legal and source/native readiness questions remain visible.

## Four fixed engineering protocols, not a search for a new strategy

1. **LEGACY_21:** corrected evaluation floor, 21 trading sessions, source per-NQ net divided by ten, exact DLL clipping. Reproduce existing modelling conventions as a reference.
2. **CALENDAR_30:** replace the 21-session clock with calendar dates in `[start_date, start_date + 30 days)`. Same costs and DLL approximation. A start is first available NQ trading date; purchase before that date is not modelled. No outcome is admitted unless the whole calendar window is covered, even if it would terminate early.
3. **NATIVE_30:** same actual clock; change commissions from $0.725 to $1.25 per MNQ round trip. Preserve the existing one-tick slippage bridge. Per-trade difference is $0.525 times the actual integer quantity.
4. **NATIVE_30_ADVERSE_DLL:** same as 3, but if the first minute crosses the daily limit without a simultaneously detected account-floor touch, book that minute's combined adverse mark rather than a perfect fill at the limit. If this mark breaches the account floor, fail. This is a deliberately conservative one-minute execution bound, not tick-exact broker liquidation.

All four are predeclared accounting/clock comparisons on the same frozen strategy portfolios. Zero new alpha definitions and no size/entry/filter selection in this phase. They still count as four disclosed account-protocol looks; do not erase the prior trials.

## Information, marks and source boundaries

Use owned one-minute close-stamped Chicago bars and the existing MultiCharts loaders. Past-only ATR15 determines quantities. Twin source simulator uses `max_stop_mult=1.0, v21=True` exactly, and its holiday rules. Pin input hashes and report latest dates before outcomes. Compare starts 2018-01-02 through 2026-09-01, matching the latest Claude diagnostic's starting-date scope; omit incomplete windows consistently.

The source `paths` helper sums adverse extrema within a minute. Simultaneous extrema of multiple positions need not be jointly attainable. DLL clipping and adverse-minute liquidation are modelling bounds, not actual fills. The Bridge loader books Sunday entries to Monday and omits an exact Sunday equity path; this limitation must remain explicit. Twin's existing path helper carries pre-midnight adverse risk to the exit date rather than maintaining exact calendar marks; reproduce and disclose this convention, record calendar/session crossings and do not confuse them. No final deployment claim can be based on these approximate paths.

Keep all missing held bars/excluded records visible; do not treat missing observed P&L as a strategy permission to enter. No fresh signal uses future clock or current-day realized outcomes. Diagnostic conditioning on a failed account is descriptive and never a tradable filter.

## Outputs and metrics

Return a ledger for every fully covered start; record account, protocol, start/deadline, outcome (pass / trail fail / time-out), trading days, elapsed calendar days and DLL pauses. Output full, 2018–22 and 2023+ tables, by year and paired changes. Only include design starts whose entire window ends before 2023. Later history is already seen historical replication. Common start coverage is required for protocol differences.

Report unconditional pass/fail/time-out rates; median trading/calendar time conditional on passing; implied fee per pass using the actual separately identified fee or report `fee / p_pass` symbolically if a price is unverified. Do not confuse that long-run expectation with independent concurrent account attempts or guaranteed spending. Overlapping start windows are dependent; use paired 60-start moving-block intervals, 2,000 draws, seed 20261109. Do not claim significance from the raw number of daily starts.

Separate source diagnosis from newly reproduced measurements. Report each piece's unconditional daily P&L, correlation and concurrent risk windows only as diagnostics. A later gain cannot rescue an already breached account.

## Checks before real outcomes

Meaningful synthetic account checks: (a) floor continues trailing beyond the PA lock level; (b) target after calendar expiry cannot pass; (c) DLL pauses only the day, trail touch fails; (d) adverse-DLL booking can fail where perfect clipping would survive; (e) a target and adverse floor touch in the same minute use adverse-first; (f) fractional quantities are not introduced by accounting conversion; (g) completed trade nets and path tails reconcile. Stop on a failed fixture or source mismatch; amend implementation transparently without changing economic settings.

## Candidate admission after baseline

Read the latest TIER_LIST/WATCHLIST before any economic proposal. Prefer recurring source-supported flows or a direct hedge in owned markets, with a return window that can help before common breaches. A claim of low daily correlation is not enough. Opening/DLL-time exposure and performance during the actual sequence matter. No account-state recovery bet or after-stop re-entry is authorized by this plan.

Maximum initial source-feasibility packet: three distinct hypotheses; no new return trial unless a source/evidence gate permits an exact rule and a second plan/code commit freezes it. Published historical claims are not new local backtests. Missing proprietary rules or auction/inventory data are blockers; do not invent a replication.

Before any candidate's return test, freeze a cheap 2018–22 net-edge/cost gate, at most five definitions including controls, passed-only recent historical replication and paired current-book comparisons. Both ADD and REPLACE must be checked against EMPTY; choose the overlapped slot on design only. A strategy earns an evaluation candidacy only if recent paired pass improvement is positive with an interval excluding zero under a fixed calendar/native-cost protocol, and the improvement survives execution stress. Lower trail failures with offsetting time-outs do not pass. Independently verify and forward track before a user decision.

No live/VPS/broker/key/order changes, plan edits, schedule changes, external messages or paid data. Save a Summary of at most five lines and show key results in chat. Commit and normally push only codex/work; provide the report path for Claude.
