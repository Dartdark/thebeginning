# Execution diagnostics: WATCH — offline observations ready; price and quote evidence missing

Summary: Added read-only entry diagnostics for VB, evaluation ONB_ADX30 and Bridge Monday; entry rules stay fixed.
The October 20–21 tracker yields 3 distinct market events across 6 order rows: 2 filled events and 1 rejected event.
Full account attribution, verified signal/submission clocks, weekly minute bars and contemporaneous quotes are missing.
No spread, signal-to-fill cost, nearby-price result or delayed-entry benefit is claimed; the week is incomplete.
Bid/ask logger change is an uncompiled proposal only; no live/VPS/logger deployment or strategy tests.

Plan: [`execution_diagnostics.md`](../plans/execution_diagnostics.md), **6d30acc**.
Task/source commit: **37bcba975609607435fd5d28fef6512c7f9620d0**; task and starting evidence preserved under
`agents/codex/inputs/execution_diagnostics/`. Scripts: `analysis/codex_live_reconcile.py`,
`analysis/codex_execution_diagnostics.py`, `analysis/codex_execution_diagnostics_checks.py`,
`analysis/codex_execution_diagnostics_report.py`. Output: `analysis/outputs/codex_execution_diagnostics/`.
Strategy/return trials: **0**. Changes are offline Python and proposal/documentation files only.

## Rule (as observed)

No trading rule was evaluated or changed. Diagnose filled, rejected, cancelled and explicitly verified missed entries.
The sampling unit is a reviewed strategy signal, shared across account copies and retries. The six transcribed entry
rows form three observed decision events, not six independent samples. Distinct event IDs also do not establish
statistical independence between consecutive trades. Individual account execution records remain separate.

`Generated` in the tracker is a platform timestamp, not verified broker submission/receipt. Its `Filled / cancelled`
column is retained as a fill timestamp only on filled rows. On rejected rows it is a status-update timestamp.
The VPS clock's timezone is not explicitly verified by the screenshot; no conversion to CT/UTC is invented.
Full broker account suffixes were clipped. Dashboard day totals confirm separate accounts but do not identify which
order IDs belong to which account. Blank account fields are intentional, not an allocation between the two accounts.

## First observations: October 19–23

Start: `live/orders_20261020_21.md`, hand transcription, not a complete native broker execution file.
All entry rows are long market orders for eight MNQ; rejected rows use `@MNQ`, filled rows use `MNQZ6`.

| Day | Tracker generated slot (VPS zone unverified) | Entry-order rows | Status | Reported fill price/range | Account assignment |
|---|---|---:|---|---:|---|
| 2026-10-20 | 10:00 | 2 | rejected | — | unresolved |
| 2026-10-21 | 12:00 | 2 | filled | 30,069.00 | unresolved |
| 2026-10-21 | 12:30 | 2 | filled | 30,086.00–30,086.50 | unresolved |

Nominal generated-to-status differences in the displayed timestamps are 10 ms for the rejected
rows and 50–60 ms for filled rows. These are arithmetic on the transcription,
not network/broker latency, verified signal-to-fill delay or independently checked timestamp precision.
The second filled event has different entry prices across its two rows; that dispersion is observable, but does not
establish worse execution versus a contemporaneous signal or quote. Two broker-ID-zero rejections are retained as
separate order attempts within one signal event. Full rejection messages were not transcribed and remain unavailable;
the symbol-mapping explanation is reviewed context, not an invented full broker reason string.

The chart logger's entry labels are **10:30 on October 20**, and **12:30 / 13:00 on October 21**, whereas tracker
generation slots are **10:00**, and **12:00 / 12:30** respectively. They are different timestamp types. We do not
apply a 30-minute offset, treat a chart label as signal time, or assign chart prices to broker records. Chart duplicate
notifications are retained in the raw evidence and deduplicated separately; they never create extra broker fills.

| Day | Strategy | Observed events | Filled events | Rejected events | Coverage interpretation |
|---|---|---:|---:|---:|---|
| 2026-10-19 | VB | 0 | 0 | 0 | coverage unresolved; no zero-trade claim |
| 2026-10-19 | ONB_ADX30 | 0 | 0 | 0 | coverage unresolved; no zero-trade claim |
| 2026-10-19 | MON_BR | 0 | 0 | 0 | coverage unresolved; no zero-trade claim |
| 2026-10-20 | VB | 1 | 0 | 1 | observed; incomplete week |
| 2026-10-20 | ONB_ADX30 | 0 | 0 | 0 | coverage unresolved; no zero-trade claim |
| 2026-10-20 | MON_BR | 0 | 0 | 0 | coverage unresolved; no zero-trade claim |
| 2026-10-21 | VB | 2 | 2 | 0 | observed; incomplete week |
| 2026-10-21 | ONB_ADX30 | 0 | 0 | 0 | coverage unresolved; no zero-trade claim |
| 2026-10-21 | MON_BR | 0 | 0 | 0 | coverage unresolved; no zero-trade claim |
| 2026-10-22 | VB | 0 | 0 | 0 | coverage unresolved; no zero-trade claim |
| 2026-10-22 | ONB_ADX30 | 0 | 0 | 0 | coverage unresolved; no zero-trade claim |
| 2026-10-22 | MON_BR | 0 | 0 | 0 | coverage unresolved; no zero-trade claim |
| 2026-10-23 | VB | 0 | 0 | 0 | coverage unresolved; no zero-trade claim |
| 2026-10-23 | ONB_ADX30 | 0 | 0 | 0 | coverage unresolved; no zero-trade claim |
| 2026-10-23 | MON_BR | 0 | 0 | 0 | coverage unresolved; no zero-trade claim |

Zero in this table means **no observed event in the available entry evidence**, not no trade or a verified missed
trade. Chart CSVs exist for October 20–22; October 18 Sunday context, October 19 and October 23 files are absent in
the pinned snapshot. ONB/Bridge entry evidence is insufficient. A POS heartbeat or a file's presence does not prove
the entry ledger is complete. There is no full-week coverage declaration; Friday export remains pending.

## What is measurable

| Component | Current result | Required evidence |
|---|---|---|
| Actual entry status/quantity/prices | Transcribed six order rows; account suffixes unresolved | Native account-attributed order/execution CSV |
| Full rejection reason | Unavailable in transcription | Dated broker/platform order reason, retained verbatim |
| Signal → submission → broker-fill delay | Unavailable; generation/status proxy preserved separately | Actual signal and submission timestamps plus verified clock mapping |
| Quoted spread at submission/fill | Unavailable | Fresh same-contract bid/ask captured at those instants |
| Effective fill cost versus fill-time midpoint | Unavailable | Actual fill plus fresh same-contract contemporaneous quote |
| Fill versus signal benchmark | Unavailable | Verified signal clock and fresh same-contract signal quote |
| Prices at −5/−2/−1/0/+1/+2/+5 min around signal/fill | 0 observed samples | Latest close-stamped minute bars and verified anchors |
| Post-entry adverse/favorable movement | Unavailable | Verified fill clock and comparable price windows; descriptive only |
| Benefit of waiting a minute | Not tested | Separate frozen strategy/execution experiment, including missed trades and exits |

Both owned 2026 NQ day and overnight files end **2026-10-09**; their date coverage and hashes were inspected without
building a grid or research cache. NQ continuous minute closes can later be labeled as a price proxy for MNQ, but
cannot reconstruct the actual MNQ spread or an executable fill. Same-contract minute data is preferred. At a fractional
minute anchor, use the last completed minute close, record its lag and never use the next minute's future close.
No missing minutes are carried forward. Sunday observations before 17:00 CT are unavailable, including apparent
pre-open values in a supplied file; a Friday quote is never used as Sunday's pre-entry observation.

## Schema and calculations

Machine-readable schema: `input_schema.json`. Canonical order CSV has the required columns below; preserve original
order IDs, original timestamps and raw exports alongside it. This is a reviewed normalization, not a claim that a
native MultiCharts export already uses these column names.

```text
attempt_id,event_id,trading_date,strategy,account,instrument,actual_contract,side,qty,filled_qty,order_type,status,reason,order_id,fill_price,signal_time_utc,submission_time_utc,fill_time_utc
```

`attempt_id` is a unique input-record identity; `event_id` is a reviewed common signal ID across accounts. Do not
group arbitrary fills merely because their times are close, merge different signals by minute, or deduplicate all
rejections with broker ID zero. `trading_date` is the reviewed session date, so Sunday's Bridge entry belongs to
Monday's session while retaining its actual Sunday timestamp. Account and actual contract may be empty only when
explicitly unknown; they are never inferred from a clipped prefix or chart tag. ONB must be `ONB_ADX30`, not ambiguous
`ONB` or the funded ML key. `side` is +1/−1; quantities are whole contracts. UTC clock fields require an explicit
timezone offset or Z. Missing clocks remain blank. A declared missed entry needs reviewed complete coverage;
otherwise it is `unresolved_no_fill`. Cancellation is a separate status. Partial fills require retained execution-leg
detail and reviewed price/time aggregation; a final status timestamp alone does not establish every leg's fill time.

Minute bars: `bar_close_time_utc,symbol,actual_contract,open,high,low,close`.
Quotes: `attempt_id,basis,quote_time_utc,bid,ask,symbol,actual_contract,freshness_verified`;
`basis` is signal/submission/fill. Require one attributed same-contract quote no later than its anchor and at most
one second old, plus explicit freshness verification. Crossed, locked, nonpositive, stale, ambiguous or wrong-contract
quotes remain unusable. This is a frozen data-quality guard, not a strategy spread filter. A chart observation
snapshot is not automatically a verified fill/submission quote.

For NQ/MNQ tick 0.25 and direction s=+1 long/−1 short:

- quoted spread ticks = (ask−bid)/0.25;
- effective fill cost versus fill-time mid = s×(fill−fill_mid)/0.25;
- signed market move during signal-to-fill interval = s×(fill_mid−signal_mid)/0.25;
- total fill-versus-signal-mid difference = sum of the last two components.

Effective cost versus midpoint includes more than the spread itself; do not name the entire number “spread paid.”
Post-entry movement uses signed differences between comparable observed minute closes at zero and +1/+2/+5 minutes,
with an explicit same-contract/proxy label. It is descriptive and is never reported as delayed-strategy P&L. No missing
component is replaced by zero. Each order can have price/quote observations, but summaries count market events once.

## Logger proposal for Claude

[`Apex_Trade_Logger_bidask.txt`](../proposals/Apex_Trade_Logger_bidask.txt) is a complete **proposal**, based on the
pinned original logger, with additive OPEN/CLOSE real-time snapshots to a separate `quotes/` subfolder as `YYYYMMDD_chart_quotes_v1.csv`.
It records InsideBid, InsideAsk, Close and raw ComputerDateTime, plus the chart event identity and explicit metadata
labels. The legacy fourteen-column trade/POS output is unchanged. The offline legacy audit now accepts exact `YYYYMMDD.csv`
names only. All other consumers and later push/sync treatment still need review. FileAppend cannot create the
quotes subfolder; its existence must be checked in the separate non-trading compile/replay environment. Manual metadata labels
must have no commas/newlines and do not verify account, actual contract or timezone on their own.

The quote belongs to the **charted symbol** and the instant the logger runs. With existing bar-close calculation,
that can be much later than submission/fill; same-bar OPENs can be absent. Recovered CLOSE records see current quotes,
not historical exit quotes. Quote source freshness is unknown. The PC serial clock has no UTC offset, and decimal
formatting adds no verified timing precision. The proposal deliberately does not change calculation cadence, enable
intrabar order generation, retrieve broker identity, add event subscriptions or claim exact broker callbacks.
It therefore cannot alone supply the requested submission/fill quotes or rejected/missed-order observations.

Official references checked for the proposal: [InsideBid](https://www.multicharts.com/trading-software/index.php?title=InsideBid),
[InsideAsk](https://www.multicharts.com/trading-software/index.php?title=InsideAsk),
[ComputerDateTime](https://www.multicharts.com/trading-software/index.php?title=ComputerDateTime).
Inside quotes are current chart-symbol quote fields and cannot be referenced historically; ComputerDateTime is a
computer-local serial date/time. PowerLanguage is not available to compile/run this draft here. Claude must review it
and validate compilation, CSV field counts, real-time-only behavior and unchanged trade/POS behavior on a separate
non-trading environment before any later integration. No VPS/live file, logger, scheduler, alert or broker was changed.

## Weekly exports and commands

1. Export the full **Order and Position Tracker** for each account as `live/orders/YYYYMMDD_orders.csv`, including
   full account IDs, actual contracts, entry and protective/exit orders, generated/submitted/status/fill times with
   timezone/precision, quantities, prices, IDs and full reasons. Retain partial-fill executions, cancelled/rejected
   attempts and daily logs. Clarify which timestamp columns are actually available; unavailable submission time stays
   unknown. An execution export with fees is needed separately for net round-trip reconciliation.
2. Export updated **NQ day AND overnight minute bars**, including Sunday context through Friday. Also provide actual
   traded MNQ contract minute data where available. Preserve exporter timestamp convention, timezone and contract-roll
   metadata; no guessed NQ→MNQ quote equivalence. Supply reviewed normalized UTC close stamps for `--bars-input`.
3. Preserve `live/trades/YYYYMMDD.csv` and chart live/backtest reports for deployed VB, ONB_ADX30 and Bridge versions,
   including Settings, exact inputs and account activation/session coverage. These identify expected signals/model
   differences, not broker fills. Include Sunday October 18 context for Monday October 19.
4. Confirm VPS clock/timezone and the full chart-tag/account/actual-contract mapping. Retain raw source times even
   after UTC conversion. The first native CSV needs a reviewed column mapping to the canonical schema. If the logger
   proposal is later approved and installed by the responsible operator, export its sidecar separately; it still
   does not replace broker-timestamped quotes. No installation is requested or performed in this task.

Reproduce the current partial-week observations:

```bash
/workspace/venvs/thebeginning/bin/python analysis/codex_live_reconcile.py \
  --execution-diagnostics --source 37bcba975609607435fd5d28fef6512c7f9620d0 \
  --start 2026-10-19 --end 2026-10-23 --output analysis/outputs/codex_execution_diagnostics
/workspace/venvs/thebeginning/bin/python analysis/codex_execution_diagnostics_checks.py
/workspace/venvs/thebeginning/bin/python analysis/codex_execution_diagnostics_report.py
```

For a later reviewed weekly dataset, use a **new** Codex output folder and add `--orders-input CANONICAL_ORDERS.csv`,
`--bars-input CANONICAL_MINUTES.csv` and `--quotes-input VERIFIED_QUOTES.csv` as available. Missing inputs remain
unknown. `--tracker-timezone America/Chicago` is an explicit verification declaration for the hand transcription;
do not supply it merely to make bars join. A generated timestamp still does not become a submission or signal time.
This mode is separate from existing expected-vs-broker round-trip comparison and refuses mixed comparison flags.

## Checks and limits

16 new engineering checks pass; 15 existing reconciliation checks also pass.
Coverage includes account-copy event counting, distinct signals, broker-ID-zero rejection retention, fractional
price parsing, unverified clocks, no-fill classifications, missed-coverage declarations, exact causal minute samples,
Sunday closures, quote decomposition and invalid/stale/future/wrong-contract quotes. No strategy returns, backtest,
funded bench, parameter search, timing variant or trading recommendation was computed. Friday's complete-week audit
remains pending the actual exports. Daily net confirmations cannot replace account-attributed execution evidence.

Tell Claude: review `agents/codex/results/execution_diagnostics.md` and the bid/ask logger proposal; observation only,
entry rules fixed, current evidence incomplete and market events counted once across account copies.
