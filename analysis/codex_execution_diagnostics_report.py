"""Render the pinned entry-observation report and canonical input schema; no strategy evaluation."""
from pathlib import Path
import hashlib
import json
from importlib.metadata import version

import pandas as pd

import codex_execution_diagnostics as D

OUT=D.ROOT/'analysis/outputs/codex_execution_diagnostics'


def main():
    summary=json.loads((OUT/'diagnostics_summary.json').read_text())
    attempts=pd.read_csv(OUT/'entry_attempts.csv',keep_default_na=False)
    events=pd.read_csv(OUT/'market_events.csv')
    week=pd.read_csv(OUT/'weekly_coverage.csv')
    fixtures=json.loads((OUT/'fixture_checks.json').read_text())
    earlier=json.loads((D.ROOT/'analysis/outputs/codex_live_reconcile_followup/fixture_check_results.json').read_text())
    event_rows=[]
    for event,g in attempts.groupby('event_id',sort=True):
        prices=pd.to_numeric(g.fill_price,errors='coerce').dropna()
        price=('—' if prices.empty else f'{prices.min():,.2f}' if prices.min()==prices.max() else f'{prices.min():,.2f}–{prices.max():,.2f}')
        times=g.order_generated_time_raw.iloc[0][11:16]
        event_rows.append(f'| {g.trading_date.iloc[0]} | {times} | {len(g)} | {g.status.iloc[0]} | {price} | unresolved |')
    weekly_rows=[]
    for z in week.itertuples():
        context='observed; incomplete week' if z.observed_market_events else 'coverage unresolved; no zero-trade claim'
        weekly_rows.append(f'| {z.day} | {z.strategy} | {z.observed_market_events} | {z.filled_market_events} | {z.rejected_market_events} | {context} |')
    filled=attempts[attempts.status.eq('filled')];rejected=attempts[attempts.status.eq('rejected')]
    filled_ms=pd.to_numeric(filled.generated_to_status_ms);rejected_ms=pd.to_numeric(rejected.generated_to_status_ms)
    schema=dict(version=1,required_order_fields=list(D.REQUIRED),optional_order_fields={
      'order_generated_time_raw':'Original displayed tracker timestamp; never silently promoted to signal/submission time',
      'generated_time_utc':'Optional timezone-verified conversion; still not submission time',
      'broker_fill_time_raw':'Original filled-column timestamp, blank for unfilled orders',
      'status_time_raw':'Status transition time including rejection/cancellation, not inherently a fill',
      'coverage_verified':'Explicit true declaration needed to classify a supplied no-fill expected event as missed',
      'source':'Original export/source and row identity; preserve raw files and execution-leg details'},
      event_unit='Reviewed strategy signal ID shared across all account copies/retries; distinct IDs need not be statistically independent',
      order_statuses=['filled','partially_filled','rejected','cancelled','missed','unresolved'],
      time_rule='UTC fields must include Z or offset; raw tracker and chart timestamps remain separate',
      bar_fields=['bar_close_time_utc','symbol','actual_contract','open','high','low','close'],
      bar_rule='Exact minute close at or before anchor+offset; no nearest-future bar, interpolation or forward-fill',
      quote_fields=['attempt_id','basis','quote_time_utc','bid','ask','symbol','actual_contract','freshness_verified'],
      quote_rule='One reviewed same-contract quote, not after anchor and at most 1 second old; explicitly verified freshness; bid>0 and ask>bid',
      horizons=list(D.OFFSETS),proposal_schema=dict(columns=['schema','event','tag','chart_symbol','entry_date','entry_time',
      'chart_entry_price','exit_date','exit_time','chart_exit_price','bar_date','bar_time','pc_datetime_serial','bid','ask',
      'chart_close','quote_state','observation_role','pc_zone_label','contract_label','account_label'],
      role='Chart observation snapshots only; not accepted automatically as canonical signal/submission/fill quotes'))
    (OUT/'input_schema.json').write_text(json.dumps(schema,indent=2)+'\n')
    text=f'''# Execution diagnostics: WATCH — offline observations ready; price and quote evidence missing

Summary: Added read-only entry diagnostics for VB, evaluation ONB_ADX30 and Bridge Monday; entry rules stay fixed.
The October 20–21 tracker yields {len(events)} distinct market events across {len(attempts)} order rows: {summary['filled_market_events']} filled events and {summary['rejected_market_events']} rejected event.
Full account attribution, verified signal/submission clocks, weekly minute bars and contemporaneous quotes are missing.
No spread, signal-to-fill cost, nearby-price result or delayed-entry benefit is claimed; the week is incomplete.
Bid/ask logger change is an uncompiled proposal only; no live/VPS/logger deployment or strategy tests.

Plan: [`execution_diagnostics.md`](../plans/execution_diagnostics.md), **6d30acc**.
Task/source commit: **{summary['source_commit']}**; task and starting evidence preserved under
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
{chr(10).join(event_rows)}

Nominal generated-to-status differences in the displayed timestamps are {rejected_ms.min():.0f} ms for the rejected
rows and {filled_ms.min():.0f}–{filled_ms.max():.0f} ms for filled rows. These are arithmetic on the transcription,
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
{chr(10).join(weekly_rows)}

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
| Prices at −5/−2/−1/0/+1/+2/+5 min around signal/fill | {summary['window_observations']} observed samples | Latest close-stamped minute bars and verified anchors |
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
{','.join(D.REQUIRED)}
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
/workspace/venvs/thebeginning/bin/python analysis/codex_live_reconcile.py \\
  --execution-diagnostics --source {summary['source_commit']} \\
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

{fixtures['tests_run']} new engineering checks pass; {earlier['tests_run']} existing reconciliation checks also pass.
Coverage includes account-copy event counting, distinct signals, broker-ID-zero rejection retention, fractional
price parsing, unverified clocks, no-fill classifications, missed-coverage declarations, exact causal minute samples,
Sunday closures, quote decomposition and invalid/stale/future/wrong-contract quotes. No strategy returns, backtest,
funded bench, parameter search, timing variant or trading recommendation was computed. Friday's complete-week audit
remains pending the actual exports. Daily net confirmations cannot replace account-attributed execution evidence.

Tell Claude: review `agents/codex/results/execution_diagnostics.md` and the bid/ask logger proposal; observation only,
entry rules fixed, current evidence incomplete and market events counted once across account copies.
'''
    (D.ROOT/'agents/codex/results/execution_diagnostics.md').write_text(text)
    code=['analysis/codex_live_reconcile.py','analysis/codex_execution_diagnostics.py',
          'analysis/codex_execution_diagnostics_checks.py','analysis/codex_execution_diagnostics_report.py',
          'agents/codex/proposals/Apex_Trade_Logger_bidask.txt']
    reproduction=dict(plan_commit='6d30acc',source_commit=summary['source_commit'],strategy_trials=0,
      python_packages={p:version(p) for p in ['numpy','pandas','numba','openpyxl','scipy','scikit-learn']},
      file_sha256={p:hashlib.sha256((D.ROOT/p).read_bytes()).hexdigest() for p in code})
    (OUT/'reproduction.json').write_text(json.dumps(reproduction,indent=2)+'\n')


if __name__=='__main__':main()
