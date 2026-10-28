# Shared Target Guard v1 — research setup and review

Status: **built, Python checks pass; PowerLanguage compilation, Windows file API and paper-order behavior NOT verified. No installation performed.** This replaces repeated daily balance edits with one manually confirmed per-account file update. It does not obtain broker balances or provide account-wide profit accounting.

## Files

- `analysis/codex_shared_target_guard.py`: manual publisher; no trading/network APIs.
- `agents/codex/code/Apex_Target_Guard_Shared_RESEARCH.txt`: separate exit-only PowerLanguage draft. `EnableOrders=false` and `ConfirmChicagoClock=false` by default.
- `analysis/codex_shared_target_guard_checks.py`: disconnected verification.
- `analysis/outputs/codex_shared_target_guard_20261028/verification.json`: measured test results and explicit unverified flags.

The existing `apex_strategies/Apex_Target_Guard.txt` is unchanged. Do not add two order-enabled guards to the same chart. Do not install this draft on a live account based on Python tests.

## Paper/research workflow

These examples are for a separate local paper/research workspace with no live broker connection. Commands assume the repository root and Python 3.9+ with Chicago timezone data. On Windows, `py -3` can be used instead of `python`; if `zoneinfo` reports missing timezone data, that Python environment needs `tzdata` before the writer will run. No package is installed by this script.

Create a new account alias once (use a non-sensitive alias, not a real account number):

```powershell
python analysis/codex_shared_target_guard.py --state-dir C:\TradingResearch\TargetGuard init --account PAPER50_A --size 50000
```

The writer prints the token and fixed target. Record these in the **paper** chart's guard settings once:

| Input | Example / meaning |
|---|---|
| StateFile | `C:\TradingResearch\TargetGuard\PAPER50_A.ini` — absolute local path, identical on all this account's charts |
| ExpectedAccountToken | Integer printed by `init`; per-account namespace check, NOT a broker credential |
| EvaluationSize | `50000` or `150000`, matching the configured account |
| BufferDollars | `50` by default, matching the writer's one-time `--buffer` |
| ConfirmChicagoClock | Only set true in paper testing after verifying both Windows and chart use Chicago time |
| EnableOrders | **Leave false** for initial verification |

`init` fixes $53,050 for 50K or $159,050 for 150K with the default buffer. It refuses to overwrite an existing account configuration. A target is not recalculated from that day's balance. Use a different alias for a separate test account; never recycle a passed account's file/token into a new account.

After verifying **all account positions are flat**, reconcile the actual balance, including posted fees and manual trades. Enter it once:

```powershell
python analysis/codex_shared_target_guard.py --state-dir C:\TradingResearch\TargetGuard update --account PAPER50_A --flat-confirmed
```

The script prompts for the balance and atomically replaces that account's INI. Every chart configured to read it sees the same snapshot on its next real-time calculation. There is no need to edit daily chart inputs. `--balance 51480.25` is also supported. The flat flag is a human assertion; the tool cannot verify it against a broker.

Use a distinct alias, generated token and file for each account. Set up a 150K paper alias with `--size 150000`; it retains its own fixed $159,050 target. Do not commit runtime balance/configuration files to Git or place them in a synced data feed folder.

The command can publish for the upcoming session during 16:00–17:00 CT on normal weekdays and Sunday from 16:00 CT. An active guard accepts the snapshot starting at 17:00 CT. A snapshot prepared after 17:00 has the next calendar date as session label. Midnight is not a reset. Weekend publishing/trading windows are rejected as coded; the tool does not implement a CME holiday calendar. Native strategies must retain their early-close/no-entry/time-exit rules.

## What the file contains and what is checked

One integer-only `[Guard]` section contains schema, generated token, monotone revision, Chicago session label, as-of date/time, balance cents, fixed target cents, flat confirmation and an arithmetic checksum. Atomic same-directory replacement avoids partially written files. An exclusive writer lock prevents two updates for the same alias. A failed replacement preserves the old file and reports failure; it does not claim that the requested balance was published. A lock left by a crashed process requires review with all writers stopped; never delete a lock just to race another writer.

The draft uses Windows `GetPrivateProfileIntA` from `kernel32.dll`, with the same `DefineDLLFunc` declaration style used by repo exporters. It reads the revision before and after fields and checks the checksum, token, size/target, time and session. This helps reject inconsistent snapshots; it is not authenticated broker/account binding, a security boundary or a transactional account feed. Windows profile caching, DLL declaration/bitness compatibility and concurrent-reader behavior still require actual Windows/MultiCharts testing.

The PC clock, chart timezone, account selection, file alias and expected token are **manual setup checks**. A correctly matching file/token cannot detect a chart attached to the wrong broker account. The signal is real-time only and does not consume today's file during historical replay. It checks that the chart's date matches the PC's current date, but cannot certify healthy market-data latency. No timer is installed to force recalculation when ticks/bars stop.

Status messages appear in the PowerLanguage output log on status, revision or candidate-limit changes, including parsed balance/target cents. Monitor-only mode calculates a candidate limit for an open chart position without issuing it; a flat chart logs zero as the no-candidate value:

| Code | Meaning |
|---|---|
| 1 | Historical calculations disabled |
| 2 | Clock/account/size confirmation missing |
| 3 | Closed window or chart date mismatch |
| 4 | Missing, stale, wrong-account/target, inconsistent or otherwise invalid snapshot |
| 5 | Valid manual snapshot, monitor-only |
| 6 | Snapshot balance already meets/exceeds target; review and stop further trading externally |
| 7 | Valid snapshot and order generation explicitly enabled for a reviewed paper test |

No missing-file or previous-session cached-balance fallback is used. Invalid data suppresses **new guard-order generation**; it does not block the main strategy's entries, flatten the account or guarantee immediate withdrawal of already-working orders. Native stops/exits remain responsible for protection. Do not interpret this behavior as a safe-to-trade indicator. Check stale-order withdrawal in the paper platform before considering any real use.

## Preserved limits — read before reviewing results

- Balance is a manually reconciled **flat-account snapshot**, not current equity. Subsequent realized profits/losses, late fees, manual trades and other charts' floating P&L are not incorporated automatically. A second update requires all positions flat and another manual reconciliation. Once-a-day entry does not solve same-day account-wide accounting.
- Each chart still computes its own limit from `(TargetCents - BalanceCents) / (100 * BigPointValue * CurrentContracts)`. It does not sum open positions across charts or allocate the remaining target between them. Concurrent charts can still pass the target before either guard fires.
- Example: $51,480.25 toward $53,050 leaves $1,569.75. Eight MNQ require 98.109375 points before tick rounding. At entry 20,000, the limit is 20,098.25 long or 19,901.75 short. Commissions/slippage are not predicted; the configured buffer is not a guarantee.
- As in the original, next-bar limits do not protect the entry bar. Fill-through, fills, cancellation timing, rejected orders and strategy/broker position synchronization must be verified in MultiCharts. Reaching the evaluation target is not automatically verified with Apex and entries are not disabled after a pass.
- It is an evaluation utility. No funded payout controller or personal account target policy is supplied. There is no alpha, economic trial, new plan allocation or claimed pass/payout improvement.

## Required next check: independent Claude review and disconnected paper compile

1. Claude reviews writer/INI contract, Chicago clocks, target arithmetic and failure behavior against the existing guard.
2. Compile the draft in the **research/home-PC** installation with no live broker connection. Verify the native API declaration, integer return handling and `CurrentDate`/EL-date conversion. Do not claim compilation from the Python result.
3. Leave `EnableOrders=false`. Verify valid/missing/wrong-token/wrong-target/corrupt/stale/future snapshots and the fixed target across two charts for each paper account. Confirm unrelated account files do not change either chart. Confirm the platform actually refreshes replaced INIs.
4. Exercise 16:00, 17:00, midnight, restart and a Chicago DST weekend using a suitable controlled test environment. Do not change a live PC's clock. Historical backtests cannot validate the real-time file branch.
5. In a separate paper test only, verify long/short limits at MNQ and NQ sizes; partial exits/size changes, limit withdrawal after stale state and chart reloads; verify original stops remain active. Record compile output, settings, status logs and order traces.
6. Only after review and evidence, decide whether to authorize installation. Any later automatic account-balance reader is a separate project: first monitor its readings against the real ledger through fees, manual trades, restarts and session boundaries.

Recommended next step is the independent review/paper compile above. No production settings or live files were changed in building this package.
