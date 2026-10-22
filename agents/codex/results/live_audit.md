# Live execution audit: WATCH — missed fills confirmed; monitoring also produces false alarms
Summary: User confirms 10/20 VB did not fill; 10/21 VB filled on both accounts at -$575 each. Chart rows are not broker fills.
10/21 has 4 unique closed chart trades, 26 OPEN notifications for 4 entry keys, and 14 transient mismatch rows that resolve.
Current reports/raw data do not cover most live dates; no trustworthy live/backtest edge ratio or fill slippage can be computed.
Offline reconciliation prototype and evidence tables are provided; no live files, settings, orders, alerts or VPS were touched.
First obtain account execution exports, then repair monitoring with review and a controlled test; do not reset charts from stale flags alone.

Plan: `agents/codex/plans/live_audit.md`, d7b427b. Script: `analysis/codex_live_reconcile.py`.
Output: `analysis/outputs/codex_live_reconcile/`. Source: Claude **e097c0f**. Strategy research trials: **0**.

## Evidence standard and coverage

Three records must remain separate: chart-model trades, broker executions and the user's account confirmations.
`Apex_Trade_Logger.txt` uses `MarketPosition`, `EntryPrice`, `ExitPrice`, `TotalTrades` and `PositionProfit`.
Its real-time gate selects when it logs; it does **not** turn these chart values into exchange execution reports.
10/20 is a direct counterexample: two chart CLOSE losses exist even though the user says neither trade filled.
The current journal's heading describing these rows as live trades overstates what they establish.

Only two trade-log files (10/20, 10/21), one health CSV (10/21), four journal dates (10/17,19,20,21) and no
`live/*_live.xlsx` reports are in this source snapshot. Account 1's intended start is 10/12; account 2 begins 10/20.
The prototype exports all 40 weekday/account/strategy coverage rows for VB, ONB, EOS and Bridge Monday.
Funded LDF/RS/MOC etc. are not assumed deployed on these evaluation accounts.

| Live date | Account 1 evidence | Account 2 | Independent expected-trade status |
|---|---|---|---|
| 10/12 | Earlier setup notes say chart fills were Paper Trader/SIM, not verified Apex fills | Not active | VB/ONB reports already ended; Bridge report has no 10/12 entry |
| 10/13 | No trade log or daily journal | Not active | Bridge report covers part of day and has no entry; others stale |
| 10/14 | Setup history documents ONB stop-market rejection; no execution export | Not active | Expected entry/size/stop not independently reconstructed |
| 10/15 | No trade log or daily journal | Not active | Unknown, not zero trades |
| 10/16 | Setup history documents EOS stop rejections and incorrect continuous-symbol mapping | Not active | Scheduled expiry session; exact orders/fills unavailable |
| 10/17 | Saturday journal is a template/test, no trade facts | Not active | No weekday trade assumed |
| 10/18 | Manual Rithmic test order reported filled; separate from strategy evidence | Not active | Side, price, order ID and P&L unavailable |
| 10/19 | User journal: VB filled, Apex daily-loss liquidation; Bridge did not trade Sunday | Not active | Exact independent strategy replay unavailable |
| 10/20 | Chart VB loss exists, user confirms no fill | Same no-fill confirmation; chart log exists | Chart candidate only, not an independent fresh backtest |
| 10/21 | Two chart VB closes; user confirms filled day, -$575 | Same, -$575 | Chart candidates only; independent same-day backtest absent |

Absence of an ONB/EOS/Bridge CLOSE does not establish no opportunity, no position or correct execution. In particular,
zero POS at a sampled time is not continuous proof that no intrabar position existed.

### Existing backtests cannot settle the missing dates

| Strategy | Report Settings end | Last entry | Fit to deployed chart |
|---|---|---|---|
| VB v1 | 10/09 16:00 | 10/06 | One-NQ backtest; confirm actual code/inputs and MNQ settings |
| ONB v2 | 10/09 16:00 | 10/07 | **ADXMin 20**, unlike deployed ADX30; not interchangeable |
| EOS | 10/11 19:35 | 09/18 | Cannot evaluate 10/16 |
| Bridge Monday | 10/13 10:15 | 10/04 evening | Covers 10/12 with no entry, but not 10/18-19 |

The raw NQ daytime series in this source also ends 10/09. No new reconstruction was run on missing market data.
`analysis/live_vs_backtest.py` maps ONB_ML funded reports, but not the actual evaluation ONB ADX30 deployment.
Its live-min/max-date comparison can also omit expected trades on completely silent first/last dates. A daily audit
must use an explicit active calendar, complete expected coverage, correct version and account mapping.

## Every known trade or order episode

Times below are **chart labels**, not verified execution timestamps. VB's 30-minute bar labels cannot establish
within-bar delay or slippage; 10/19's documented 11:01:41 liquidation is a separately sourced clock time.

| Date / account | Strategy or episode | Chart entry → exit | Chart gross | Actual evidence and classification |
|---|---|---|---:|---|
| 10/12 / 1 | Paper/SIM fills, strategy unspecified | Not supplied | Unknown | Wrong route documented historically; cannot allocate to particular strategy trades |
| 10/14 / 1 | ONB entry-stop attempt | Price/time/size not supplied | Unknown | Invalid stop-market parameters documented; missed/stop status needs order history |
| 10/16 / 1 | EOS protective-stop attempts | Not supplied | Unknown | **Stop rejected** documented; exact position exposure/fills cannot be inferred |
| 10/18 / 1 | Manual test | Not supplied | Unknown | User reports actual fill; exclude from algorithm performance sample |
| 10/19 / 1 | VB long 8 MNQ | Entry 29950, chart 11:00; Apex liquidation 11:01:41 | About -$1,017 per journal notes | Real fill/forced liquidation; user balances 51,500.92→50,475.26, net -$1,025.66; planned stop would lose $1,200 |
| 10/20 / 1 | VB long 8 | 10:30 29870.25 →10:30 29795.25 | -$1,200 | **Missed, user-confirmed no fill**; chart P&L did not hit account |
| 10/20 / 2 | VB long 8 | Same | -$1,200 | **Missed, user-confirmed no fill** |
| 10/21 / 1 | VB long 8, first | 12:30 30069.50 →12:30 30109.50 | +$640 | Filled day/trades confirmed by user; individual actual fill prices/fees unknown |
| 10/21 / 2 | VB long 8, first | 12:30 30069.50 →12:30 30110.00 | +$648 | Same; the chart exit difference is not independently measured account slippage |
| 10/21 / 1 | VB long 8, second | 13:00 30085.75 →14:00 30010.75 | -$1,200 | Filled day/trades confirmed; no exported evidence of an actual rejected stop |
| 10/21 / 2 | VB long 8, second | Same | -$1,200 | Same |

The authoritative user confirmation for 10/21 is **-$575 on each account**. Account-label 1 chart gross is -$560,
label 2 -$552; residuals are -$15/-$23. These could include fees or fill differences; allocating them entirely to
fees, to one trade or to slippage would invent information. Actual size and individual execution details remain
unverified by a broker export. Tag VB-2 is an intended account label, not the actual Rithmic account identifier.

## Logger and health findings

| Flag or anomaly | Evidence | Classification and precise proposed change |
|---|---|---|
| MISMATCH VB at 14:00 | Strategy +8/broker 0 occurs twice; final same-bar row is 0/0 | Resolved sampling/chart-update mismatch, not evidence of a missed 10/21 trade. Evaluate ordered terminal state and repeated fresh samples, not last historical bad row |
| MISMATCH VB-2 at 14:00 | Same | Same; user confirms actual fills |
| Earlier mismatches at 12:30 | VB 8 bad rows, VB-2 2; both finish the bar 0/0 | Resolved, duration cannot be measured from HHMM bar labels. Preserve transition sequence, do not call persistence from bar age |
| OPEN duplication | 26 OPEN rows for 4 logical entries; VB first entry repeats 12 times, second 4; VB-2 repeats 5 and 5 | Duplicate notifications, **not extra fills**. Four unique CLOSEs cover the four keys; no unmatched logical OPEN remains |
| Exact duplicates | 65 identical rows in 10/21 file | Do not deduplicate all POS rows globally: a repeated final flat state can be erased and make an old mismatch look current |
| REJECTED (open), 29 lines | Last saved string is **10/20 19:50**, `Influence PercentChange not found in storage!` | Demonstrable stale/non-order false positive. Parse each line's event timestamp/type; file LastWriteTime and `not found` are insufficient |
| REJECTED (close), 33 lines | Saved last message is truncated order metadata, not a complete rejection reason | Unresolved line matches, not 33 proven rejected orders. Need raw lines, account/symbol/order ID and rejection status; do not label all genuine or all harmless |
| Rejection totals | 29 and 33 are cumulative scans | Do not add them into 62 orders; difference 4 is matching lines, not necessarily 4 orders. Use file-ID/offset cursors and unique order/status events |
| 10/20 heartbeat absence during RTH | POS rows appear only later; logger/update activation time not recorded | Coverage/installation gap, not proven frozen chart. Suppress no-coverage inference before a declared chart activation time |

`analysis/vps_health.py` picks the last **bad** row even after a good one follows; its EOD mismatch output is stale.
`live/vps/watchdog.ps1` uses bar HHMM as heartbeat wall-clock age and tests `age>=3` as mismatch persistence.
That can alert while reading a resolved/stale bar state; it does not measure elapsed time between fresh samples.
Default logger variables may also be reset by recalculation/reload or rolled back during intrabar updates; the
repeated OPENs are observed, but the exact runtime cause is not proven. Check lifecycle/persistence in a sandbox
before changing it. Do not attribute a confirmed fill to a failure just because a transient chart/broker row differs.

The health line reports MultiCharts running, disk 51.2 GB free and push_errors 0. These are useful process/push
checks, not evidence of correct broker account, valid symbol mapping, auto-trading state or order acceptance.
`GetSymbolName` logging `@MNQ` is expected feed notation; it does not reveal the resolved broker contract.

## 10/20 root-cause assessment

1. **Confirmed, strongest:** `MULTICHARTS_PITFALLS.md` records `Invalid Market order parameters: Buy 8 @MNQ.CME`
   on the VPS, both accounts, and confirms VPS mapping was `@MNQ→@MNQ` while the PC had the valid contract.
   Mapping is installation-specific. This directly explains real order rejection despite chart-model trades.
2. **Possible additional setup fault, not proven for these orders:** history describes new charts left on SIM 001,
   an incorrect broker profile, and account selection behind the Rithmic gear icon. Verify actual order account IDs;
   the tag suffix alone cannot settle which account received an order.
3. **Possible residual state after failures:** rejected-order auto-trading suspension or chart/model position after
   earlier rejections. The 10/19 Apex lock explains that day's repeated rejected exits; the user reported resetting
   to flat afterward, so it is weaker as the cause of both 10/20 accounts (account 2 was new).

No evidence establishes a new 10/21 mapping failure: its confirmed fills must be retained. A legitimate protective
stop rejection can coexist with successful entries; only the complete order lifecycle can settle that question.

## Numbered checks and fixes for the user, in priority order

These are proposals only. No VPS action has been performed. Inspect records first; change charts only after the
session, with actual broker positions/orders verified flat, and review the change with Claude.

1. **Export authoritative orders/executions for both accounts for 10/20 and 10/21**, plus 10/19 liquidation and
   10/12-16 attempts if available. Use Apex/Rithmic Order/Execution History; retain account ID, exchange contract,
   side/quantity, event timestamps with timezone, client/broker order IDs, fill prices, commissions and full rejection
   text. Include cancelled/rejected orders and partial fills. Redact credentials, not execution facts.
2. **Inspect this VPS's mapping:** File → Broker Profiles → Rithmic → Symbol Mapping; verify the feed alias maps to
   the actual current contract recorded by the accepted test order (MNQZ6 for this October setup). Confirm both chart
   sets use that profile. Do not infer routing from the logger's `@MNQ` symbol field or blindly change a working mapping.
3. **Inspect each chart's actual destination:** Strategy Properties → Auto Trading → Rithmic → gear icon → correct
   Apex account; Chart Trading's broker/account selectors must not be SIM. Verify auto-trading state and rejection
   stop status; ensure the copier is off while account 2 runs its own signals. Keep existing inputs/sizes unchanged.
4. **Replace alarm semantics after review:** separate `chart_state`, `broker_position_snapshot` and `execution` records;
   record account ID, resolved contract, process/run ID, monotonic sequence and real UTC observation timestamp plus
   bar timestamp. Persist emission IDs across intrabar updates/restarts without replaying historical trades.
5. **Use stateful mismatch checks:** evaluate the latest ordered observation, account for pending orders and netting
   across same-account strategies, require repeated fresh mismatched samples with elapsed wall time, and emit a
   resolution event. Keep historical incidents separately. Never automatically flatten/reset from a stale mismatch.
6. **Repair rejection parsing:** consume only new file bytes, handle rotation/truncation, parse the log's event date,
   filter actual order rejection statuses, keep full reasons/IDs and deduplicate by lifecycle event. Separate feed/
   indicator errors from order errors. Apply the same parser to the summary and watchdog so they do not disagree.
7. **Collect the missing performance evidence:** export the actual live chart reports and refreshed same-date
   backtests for the deployed versions, especially evaluation ONB **ADX30**, plus the corresponding new minute
   data if a Python rebuild is desired. Include account labels/settings and known bar timestamp convention.
   Use broker fills for execution comparison; a live-chart Strategy Performance Report alone is still insufficient.
8. **Dry-run daily reconciliation before connecting the journal job.** Run the prototype offline and compare with
   the exported order history. Verify one genuine missing fill, one ordinary fill, one partial fill/size mismatch,
   one resolved transient mismatch and one old error. Only then propose wiring its outputs into the 16:40 CT job.

## Offline daily reconciliation prototype and validation

`analysis/codex_live_reconcile.py` reads git snapshots and optional canonical `--expected`/`--broker` round-trip CSVs;
it writes only `analysis/outputs/codex_*`. It never calls a broker, edits the journal or sends alerts. The default
audit explicitly pins e097c0f. It produces per-trade chart audit, all-day coverage, mismatch transitions, report
coverage/settings, actual-user day totals, health summaries and source hashes.

The canonical input schema is documented at the top of the script. Broker partial executions must first be
aggregated by actual order/position identity; duplicate timestamp keys are refused. Symbol/account mapping and
timestamp precision must be established by the input provider. The comparator extends the existing report-matcher
logic to retain completely missed days and account/strategy scope; unsupported coverage produces UNKNOWN, not
zero P&L or invented missed trades. `--coverage-complete` must be a justified input assertion.

Matched records report adverse entry/exit slippage in ticks, time difference, wrong size and broker/expected gross
P&L. Gross P&L comparisons are not after-fee edge estimates. This is a prototype, not a deployed journal replacement;
reversal, scale-in/out, uncertain bar timestamps and strategy attribution need additional explicit adapters.

Synthetic validation passed for a fully missed date, incomplete-coverage safeguards, wrong size, tick arithmetic
and point multipliers. Audit reproduction gives six chart CLOSEs, four unique 10/21 OPEN keys and no unresolved
terminal mismatch groups. No live/backtest ratio or drift alarm was manufactured from missing data.

Tell Claude: review `agents/codex/results/live_audit.md` — 10/20 real missed fills, 10/21 confirmed -$575/account,
resolved mismatch noise and stale/non-order rejection matches; prototype offline only; live files unchanged.
