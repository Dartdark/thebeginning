# Watchdog stateful mismatch and today-only rejection proposal

Summary: Replace bar-label age and cumulative text counts with fresh-row state and dated order-failure events.
The proposed core clears resolved mismatches, requires fresh evidence across polls, and excludes older-day rejection lines.
It keeps unknown log formats visible and counts messages rather than claiming a number of rejected orders.
Draft only: no VPS, live file, scheduler, process, broker, notification or logger changes.
Claude must review and validate the PowerShell core and cursor/persistence adapter before any installation.

Review source: **59de62a**, `live/vps/watchdog.ps1` and `agents/codex/results/REVIEW_live_audit_free_data.md`.
Draft: [watchdog_stateful_draft.ps1](watchdog_stateful_draft.ps1). It defines functions only and sends nothing.
Plan: `agents/codex/plans/live_reconcile_followup.md`, **1ca38bb**. Research remains paused.

## Proposed behavior

Retain the existing read-only process/network checks and reviewed notification policy. Replace sections 2–3 with
the proposed core plus an adapter described below. Do not copy a topic, broker account, deployment tag list or secret
into this proposal. Do not install the draft as a scheduled job: it deliberately has no runtime adapter or alert sender.

Use UTC for elapsed time and `Central Standard Time` (DST-aware Windows zone) for the trading day. Verify each source
log is Central-local first. At startup validate state schema and clock. Explicit deployment metadata, reviewed against
the actual chart sets, supplies expected tags and account identity; tags discovered from old files are not that metadata.
No chart tag, process connection or POS sample proves an executed fill or the correct Apex account.

### Fresh append cursor and persistence adapter contract

The draft operates on complete newly appended rows, not `Get-Content` snapshots replayed on each poll. The adapter
is a required part of any later implementation, not assumed to exist in the current watchdog.

1. Open each file with shared read/write access. Identify its canonical source path, OS file identity/generation,
   byte offset, encoding and a prefix/tail hash. Read a bounded byte range from the committed offset; retain an
   incomplete final line for the next poll. Never advance past it. Validate actual CSV schema and numeric values.
2. Skip unchanged cursors. Replaying the same final row, reading a changed file mtime or finding an old mismatch
   does not create fresh evidence. Preserve every appended POS row in order, including repeated flat rows.
   `RecordId = generation:byte_offset` distinguishes actual appended evidence from replay.
3. On file replacement, truncation, prefix conflict, incompatible state schema, clock regression or missing state,
   rebaseline positions and cursor. Replay a complete current snapshot only to establish its terminal state; label
   startup freshness unknown. A mismatched baseline starts observation now, never at the old bar label.
   A partial read/parse failure leaves its cursor uncommitted and emits a monitoring diagnostic.
4. State schema v2 must contain per-source cursors, per-tag latest quantities/observation UTC and mismatch run,
   per-day seen rejection-event hashes and per-problem notification state. Recursively deserialize JSON dictionaries
   as hashtables for the supplied functions (PowerShell 5.1 `ConvertFrom-Json` alone does not do this).
5. Serialize with sufficient JSON depth to a temporary file in the same directory and atomically replace the state
   file only after successful processing. Use a named mutex so overlapping scheduler runs cannot consume/rewrite
   the same cursor. Do not reuse old `rej_count` state. Preserve today's rejection hashes across file rotation.
6. The adapter must recompute `CentralDay` from the same `NowUtc` supplied to all functions. It must reject malformed,
   unsupported-timezone, future-dated and out-of-day POS rows; diagnostics cannot be silently swallowed. A fresh append
   is newly observed data, not proof of feed freshness. A replay/copy with new file identity must rebaseline, not
   confirm persistence.

### Mismatch and heartbeat decision

Process every new POS row. A matching row immediately clears the pending mismatch, even if its chart bar HHMM is
identical to the preceding bad rows. A symbol change or observation gap exceeding the stale threshold starts a new
run. A mismatch is eligible for an alert only when the terminal row is bad, it appears in at least two distinct polls,
the observed run spans at least three minutes, and **this poll contains a fresh mismatched row**.

This is repeated observed discrepancy, not proof that it remained continuously mismatched between samples. With
the existing five-minute scheduler, the earliest confirmed alert is normally the next poll, not three minutes later.
Multiple bad rows in one poll count as one observation. A bad row followed by a flat row in that same poll never
produces an unresolved-mismatch alert.

After 45 minutes without a newly observed POS append, report a logging-coverage/staleness problem, not a newly
confirmed mismatch. Track it per tag: another chart writing to the same file must not refresh this chart's heartbeat.
At first startup, old timestamps cannot establish actual write time. The core's baseline is only an observation anchor,
with an explicit freshness-unknown diagnostic; it can take a full stale interval to detect an already-frozen source.
Improving that latency requires a verified wall-clock/sequence field in the logger, which is **not part of this change**.
Existing process/network alarms still apply. Do not call all unmatched baseline samples healthy or turn off charts.

Only run position freshness checks inside a reviewed weekday/session schedule that accounts for holidays and actual
chart activation; do not infer an obligation to emit pre-activation or after early close. No schedule change is proposed.

### Today-only order failures

Parse each candidate line's embedded timestamp. The draft supports the observed `dd.MM.yyyy/HH:mm:ss.fff` style
(including a prefix such as `00-11F4-`) and explicit local ISO date/time. A file written today can contain old events:
its LastWriteTime is not the event day. Undated, unsupported, future-clock or DST-ambiguous events produce diagnostics.

Require both order context and rejection/invalid-order/account-lock language. Generic `not found`, indicator/storage
errors, routine cancellation and order-ID metadata alone are not rejection events. Keep unknown failure-like records
visible for manual format review; this parser is deliberately conservative and may miss unsupported multi-line formats.
Never inherit a date or rejection reason from an unrelated preceding record without a verified record schema.

Deduplicate today's exact normalized events by verified installation/profile scope and message content, even if a file
is copied or rescanned. Rotating a log must not clear today's seen-event set. **Distinct messages are not distinct
orders**: an order may emit multiple failures, and an order ID can be absent/zero. Any later order-count metric needs
reliable account/profile/order-ID/status parsing. Keep the original message, event time and source in a review record.

A new event should not be lost merely because the notification sender fails: keep it pending until a successful send
acknowledgment, record retry/error status, and commit the pending queue with cursors. A restart must preserve it.
Rate-limit and group pending events, retaining all details in the review log. Do not run the current cumulative
`REJECT_<count>` scheme in parallel with this parser. Do not label unknown-format diagnostics as broker rejections.

## Required replay and installation gates

| Fixture / transition | Expected result |
|---|---|
| 10/21-style same-bar bad → later 0/0 | Informational resolved transition; no unresolved mismatch |
| One bad row; subsequent polls read the same cursor | No persistence confirmation; eventual STALE |
| Fresh bad rows in two polls five minutes apart | One eligible discrepancy, subject to notification policy |
| Bad → flat → bad all in one poll | New pending run, not a confirmed old run |
| One tag writes, another stops | Only the first tag's freshness advances |
| Rotation/truncation, old rows copied, partial final line | Rebaseline or defer; no false fresh confirmation |
| Fresh file containing yesterday's `Invalid Market order parameters` | Excluded from today's order failures |
| Today `Influence PercentChange not found in storage!` | Not an order rejection |
| Today bare order-ID/IOG metadata | Not an order rejection |
| Today dated `Invalid Market order parameters: Buy 8 @MNQ.CME` | New order-failure event, retained with reason/time |
| Same failure in duplicate copies of the same profile log | One event, not multiple orders |
| Failure-like line without date, wrong zone or multi-line unknown format | Diagnostic; no invented date/order classification |
| DST/date change, backward clock, failed state write, overlapping runs | Explicit failure/rebaseline; no stale state accepted as fresh |
| Notification send failure and restart | Pending event survives for retry; no trade/order action |

PowerShell/pwsh is **not installed in this environment**. The draft has not been parsed or executed by PowerShell and
is not production-validated. Claude should run the functions and an adapter against fixture copies on a non-trading
Windows machine, then replay the saved 10/20–21 logs plus synthetic transitions above. This remains pending, not a pass.
Only after that review should the user consider a weekend integration; this task authorizes no VPS changes or sends.
