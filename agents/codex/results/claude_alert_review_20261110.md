# Claude alert and new-150K setup review: confirmed bugs; candidate fixes tested offline

Summary: The alert stack is not ready to rely on for the new 150K without corrections and acceptance checks.
New-account schema makes Python floor checks crash; the watchdog instead computes a zero-dollar floor.
Failed notifications are marked sent, and new/missing charts can evade checks; VB/ONB guard tags also differ.
All 19 isolated checks pass on the review patch; current routing matches the new account in the saved snapshot.
Patch staged only; Windows installation, phone delivery, scheduler resumption and current-book odds remain unverified.

Reviewed Claude branch `claude/nq-trading-strategy-params-5h9d20`, commit
`25ca95560627f94dc1d9850b823cb5bfe2f9dbc2`, November 10, 2026. Scope: alert publishing/relay/watchdog,
chart guard logging, account-floor helpers, pre-market/health checks, dashboard diagnostics and new evaluation setup.
This is a software and operational-readiness review, not a revalidation of every research study or strategy return.
The branch was refreshed before handoff and still pointed to the reviewed commit.
No live strategy, trading plan, VPS, broker, key, chart input, schedule or notification was changed.

Artifacts: [review patch and adoption notes](../code/alert_review_20261110/README.md),
[`analysis/codex_alert_review_20261110.py`](../../../analysis/codex_alert_review_20261110.py),
[check results](../../../analysis/outputs/codex_alert_review_20261110/checks.json),
[source/runtime manifest](../../../analysis/outputs/codex_alert_review_20261110/manifest.json),
[sanitized snapshot facts](../../../analysis/outputs/codex_alert_review_20261110/observed_status.json).
Economic trials: **0**. External notifications sent: **0**.

## Findings, ordered by urgency

### F1 — P1: the new evaluation has no functioning floor-check path

At the reviewed source, `live/expected_setup.json` registers account #5 as a live 150K evaluation with start 150,000,
trail 4,000 and `phase=evaluation`, but omits `lock` and `max_stop`. `analysis/live_guard.py:31–33` indexes both fields.
An invented valid balance row reproduces `KeyError: 'lock'`; adding only a lock reveals the next `max_stop` exception.
`premarket_check.check()` calls this helper without catching that exception, so the readiness check aborts.

`live/vps/watchdog.ps1:105–107` handles the same omission differently: `[double]$v.lock` becomes zero, so
`min(peak - trail, 0)` becomes a **$0 floor**. A synthetic equity of 145,900 therefore produces no account-failure alarm.
The missing maximum stop also makes the thin-cushion threshold zero. Silently adding a funded lock is not the repair:
evaluations continue trailing, whereas funded accounts lock under their different rule.

Candidate: phase-aware floors, normalized start dates and maximum-stop metadata of 2,750 from the existing setup.
An invented 156,000 prior peak gives evaluation floor 152,000; the funded control still gives 150,100. New-account
floor is 146,000. These are software fixtures and nominal rule arithmetic, not actual account balances or a new simulation.
**Remaining limit:** both legacy floor readers use the last daily-file balance as an EOD proxy. Reconcile true EOD
and the actual Apex threshold before treating the reconstructed floor as authoritative.

The original near-floor condition also waits for room below **half** a planned stop. Even with the schema repaired,
room of 2,000 versus a planned 2,750 stop remains silent. The candidate warns when room is at or below one full planned
stop, explicitly before costs/slippage. This is an alert threshold only; it neither caps orders nor guarantees a stop
fill before the account floor. The isolated thin-cushion case supplies complete original metadata to test this issue
separately from the missing-lock bug.

### F2 — P1: failed alerts are discarded or reported as queued

- `live/vps/claude_alert_relay.ps1:42–49` catches an HTTP failure but advances the cursor to the total line count.
  In an actual-script replay of three invented messages, the middle send fails, all three are attempted, cursor becomes
  3 and exit status is zero. That failed message is skipped thereafter. On a fresh cursor, line 37 also baselines all
  existing messages as sent without attempting delivery.
- `live/vps/watchdog.ps1:157–160` swallows HTTP errors, writes `ALERT` and records the hourly suppression timestamp.
  A failed send is thus suppressed for the next hour. Scheduled-task success can coexist with failed notification.
- `analysis/send_alert.py:15–24` ignores failed pull/add/commit operations and prints `queued for the phone` even
  when every push fails. A failed pull can still be followed by a file append and subsequent Git operations.
- `analysis/vps_health.py:155` describes every watchdog log entry as an alarm sent, including muted entries.

Candidate: checked publishing operations, bounded HTTP waits, a relay cursor advanced after each accepted message,
stop/retry at the first failed message, failed watchdog sends left eligible for retry, and truthful log wording.
The middle-failure fixture stops at cursor 1 with error status; a healthy retry sends only the remaining two messages
and reaches cursor 3. The watchdog failure fixture leaves no sent timestamp and returns an error.
HTTP acceptance is still not confirmation of phone receipt. See candidate notes for replay/duplicate/concurrency limits.

### F3 — P1: a new or never-started chart/strategy can evade monitoring

`watchdog.ps1:51–67,113–123` discovers charts from historical POS/SIG rows. An expected chart that has never written
those rows is absent from the discovered set and receives no missing-chart alarm. Conversely, the SIG set is not
filtered to live configured charts, so retired strategy tags can keep generating warnings.
`premarket_check.py:50` and `vps_health.monitor_check():56` likewise waive the missing strategy heartbeat until the
strategy has already been seen. A helper can look healthy while its actual strategy heartbeat is absent.
ACCT auto-off/feed loops also include retired tags, despite the POS loop's configuration filter.

Candidate: build required POS/SIG sets from the registered live charts, filter routine retired-chart noise and identify
unknown tags on a live account explicitly. Invented never-seen charts are now flagged. The candidate's stricter checks
will correctly flag incomplete tag/heartbeat installation; align tags before judging the new setup accepted.

### F4 — P1 setup mismatch observed: two guard tags disagree with configuration

The main-branch daily trade log available at the pin ended at 15:14 CT and had no new-account POS/ACCT rows. That was
not the latest operating evidence. The separately read `vps-status` snapshot at **2026-11-10 16:25 CT** shows six guards
writing ACCT/POS rows after a MultiCharts restart. All six latest ACCT rows have auto-trading=1 and their
**route_account field (column 9, GetAccountID)** matches the registered new account. The typed monitor account agrees too.
This establishes snapshot routing, not strategy compilation, order/fill correctness or continuing availability.

| Configured guard tag | Observed guard tag | Result |
|---|---|---|
| VB150-5 | VB-5 | mismatch |
| ONB150-5 | ONB-5 | mismatch |
| EOS150-5 | EOS150-5 | matches |
| MON_BR150-5 | MON_BR150-5 | matches |
| TW150-5 | TW150-5 | matches |
| DT150-5 | DT150-5 | matches |

VB/ONB monitoring cannot join the intended chart by tag reliably. Reconcile the guard's `Tag`, the strategy's
`HeartbeatTag`, and the configuration together. Do not infer a wrong-account route from this tag mismatch. The 200-row
snapshot tail contains Twin/DT SIG rows but cannot establish all six strategies' complete heartbeat/version history.
The patch deliberately does not guess a chart input change or silently relabel configuration to hide the discrepancy.

### F5 — P1: the pre-market check can miss wrong order routing

`premarket_check.py:74–78` compares the monitor account but omits the distinct routed-account column. An explicitly
typed `AccountName` can be correct while the chart gear routes elsewhere. The isolated fixture supplies a correct
monitor account and a different routed account: the source emits no routing warning; the candidate does.
Missing route data is also reported as unknown. **No wrong route was observed in the six-row snapshot above.**

### F6 — coverage and scheduler gaps need operating-owner verification

`push_trade_logs.ps1:28` installs the watchdog weekdays at 08:15 with a seven-hour duration: its final regular run is
around 15:15. Several internal chart checks stop at 15:00. This misses the later part of the permitted session and the
Bridge strategy's Sunday 19:00 CT entry window. ONB's name alone is not evidence of an overnight position.
The candidate does not invent a 24-hour session policy or change Windows tasks; those need chart-specific active windows,
holiday/session handling and an installed-machine test.

`CLAUDE.md` / `NEW_CHAT_BRIEF.md` still describe the Claude pre-market and 16:40 journal/dashboard jobs as paused until
accounts resume, while the configuration now declares #5 live. Changing the JSON's status only unmutes the VPS watchdog
after the local config reaches it; it does not itself enable Claude's scheduled jobs. Their actual scheduler state was
not available here. Confirm both are enabled for the new evaluation. Do not resume the unrelated paused research lab/scout.

The status snapshot lists relay and log-push task results of zero; that is not end-to-end delivery evidence given F2.
The status task's 267009 value is the Windows task-running code, not by itself a failure. Earlier saved watchdog lines
were all marked MUTED while no account was live; do not describe their count as phone notifications delivered.

### F7 — P2: dashboard odds/drift do not describe the current six-chart evaluation

`analysis/live_panels.py:40–48` still builds the old VB/ONB/Bridge/EOS book and scales it by 2.5, which gives VB 20 rather
than the current 15 and omits Twin/DT. Its live-vs-backtest and silence panels use hard-coded `-2` tags at line 84,
so they monitor the old closed account instead of the new one.
`account_tools.py:24,91–101` leaves the new deadline `None`, substitutes 60 business days and retains the funded-style
floor lock in pass odds. The expiry alarm cannot fire without a date. `dashboard_data.py:21,68–69` also retains a fixed
initial floor rather than refreshing the trailing threshold.

Do not use those panels as new-account odds, drift or remaining-cushion evidence. Rebuild them on the exact current
six-strategy book, unlocked evaluation floor, actual portal expiry and causal cost/path accounting. No replacement odds
or economic tests are invented here. This repair is outside the minimal alert patch.

### F8 — P2: fixed UTC−5 timestamps are wrong in Chicago's winter

`send_alert.py:14` labels UTC−5 as CT year-round. On November 10 an invented 21:00 UTC event is stamped 16:00 CT instead
of 15:00 CST. The candidate publisher uses `America/Chicago` and passes the frozen-clock check. Fixed-offset date logic
also remains in `account_tools.today()` and `vps_health`'s default/current-day selection; include those in dashboard/date
cleanup. The already-zone-aware pre-market clock is a different code path and is not regressed by this patch.

## Completed validation and handoff

All **19 candidate checks pass**. The original source fails 18 scenarios; the funded-floor control already passes.
These are deliberately related engineering scenarios, not 19 independent economic findings. Python uses invented
fixtures and mocked Git failures. The actual PowerShell relay/watchdog execute with all external/Windows operations
mocked and all filesystem writes confined to a temporary mapped drive. The exported patch was applied in a separate
temporary tree and its resulting files exactly matched the tested candidates.

An initial harness result read the outer PowerShell process status instead of the called watchdog's exit code; the
wrapper now captures the actual script exit status. This was a harness correction, not a second production patch or an
economic trial. PowerShell 7.6.9/Linux is not Windows PowerShell 5.1, MultiCharts compilation or installed-copy acceptance.

Claude handoff: review the candidate patch; reconcile both tag inputs on all six charts; verify real account floor
and all six versioned strategy heartbeats; confirm paused operational checks are enabled; resolve monitoring windows;
and update the dashboard model/expiry. Then perform the authorized Windows/phone acceptance check with an explicit
receipt. Preserve existing relay cursor and local/remote kill latches. No live changes were made by this review.
