# Read-only entry execution diagnostics

Task/source snapshot: Claude branch **37bcba975609607435fd5d28fef6512c7f9620d0**,
`agents/codex/TASK_execution_diagnostics.md`. Work on codex/work only. No strategy return trial.

1. Preserve the task, transcribed order tracker and current logger as review inputs under Codex paths. Read pinned
   chart CSVs through git blobs and record their hashes. Start from `live/orders_20261020_21.md`; retain all six
   individual entry-order rows, rejection status, exact source strings, missing reasons/account suffixes and clock
   uncertainty. Two accounts on one signal are one market event; never use broker ID 0 to merge rejections or use
   a chart OPEN as an execution. No market research, backtest, shared cache or live file changes.
2. Extend analysis/codex_live_reconcile.py with a separate offline diagnostics mode and Codex helper. Define an
   explicit canonical input schema for event IDs, accounts, contracts, side, size, signal/submission/fill clocks,
   status/reason and order IDs. Support verified minute-bar and contemporaneous quote inputs without inventing
   missing observations. Distinguish generated-time proxies, chart bar labels, broker fills and logger observation.
3. Emit one row per market event, individual order attempts, chart evidence, requested +/-1/2/5 and zero-minute
   windows around signal and fill, week/strategy coverage for October 19–23 with Sunday context, input hashes and
   a machine-readable summary. A missing file is unknown coverage; an absent fill is not a proven missed trade.
   NQ bars are only a price proxy for actual MNQ, never a reconstructed spread. Unverified tracker timezone prevents
   joining clocks. Sunday pre-reopen samples are unavailable even if an older quote/bar exists. Do not forward-fill.
4. Separate quoted spread, actual fill-vs-signal slippage and signed subsequent market movement. Calculate only
   with sufficient verified same-contract/time evidence. A bar close is not a point-in-time executable quote.
   Timestamp interval differences from the same tracker may be reported as nominal generated-to-status intervals,
   not network latency. No better-entry recommendation or timing selection follows this tiny observational sample.
5. Draft **agents/codex/proposals/Apex_Trade_Logger_bidask.txt** only, retaining existing legacy CSV/POS rows and
   adding a real-time OPEN/CLOSE quote sidecar. Include InsideBid, InsideAsk, Close and ComputerDateTime, tagged as
   chart-observation values, not submission/fill quotes. Do not enable intrabar order generation, alter entry/exit
   behavior, deploy, send messages or contact the VPS. Note same-bar trade omissions, stale/invalid quotes, chart
   continuous-vs-broker contract differences, PC timezone/precision limits and need for broker tracker timestamps.
   This environment cannot compile PowerLanguage; require Claude's review and non-trading compile validation.
6. Verify engineering behavior with meaningful synthetic fixtures: repeated account executions counted once per
   signal, distinct rejects with broker ID 0 retained, no-fill status, incomplete evidence, clock refusal, exact
   minute windows, causal bar-close selection, Sunday unavailable observations, crossed quotes and same-contract
   gates. Keep earlier reconciliation checks passing. Write execution_diagnostics.md with Summary <=5 lines,
   schema, first actual week table, measurable/unknown distinctions and exact weekly export requirements.

Commit/push only allowed Codex paths, pull before push. No live/VPS/logger/broker changes. No rule modification,
delay experiment, optimization, P&L forecast, scale recommendation or independent-event claim from account copies.
