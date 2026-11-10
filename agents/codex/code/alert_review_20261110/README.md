# Alert reliability review candidate

Review: [findings and acceptance limits](../../results/claude_alert_review_20261110.md).
Patch: [reliability.patch](reliability.patch), against Claude source
`25ca95560627f94dc1d9850b823cb5bfe2f9dbc2`.

The patch is staged for review. It has not been applied to the project production files or installed on the VPS.
It changes the alert publisher, relay, watchdog, floor helper, pre-market routing/heartbeat checks, journal wording,
and the new evaluation's missing maximum-stop metadata. It changes no strategy order, sizing or account decision.

Reproduction from a research checkout containing the pinned Claude Git objects:

```sh
/workspace/venvs/thebeginning/bin/python analysis/codex_alert_review_20261110.py --pwsh /workspace/review_tools/pwsh/pwsh
```

The script reads pinned Git objects and applies the exported patch only inside a temporary directory. The Python
helpers use invented files and mocked Git results. The actual PowerShell scripts execute on Linux with a temporary
`C:` drive and mocked Git, HTTP, clock, processes, connections and child PowerShell calls. No live notification,
kill-switch operation, broker call or scheduled-task change occurs. Outputs contain synthetic test values.

PowerShell 7.6.9's official archive is separately installed under `/workspace/review_tools`; its SHA256 is recorded
in the run manifest. Python requires the project's pandas/numpy environment. The runtime/archive are not committed.
Linux PowerShell results do not establish Windows PowerShell 5.1 or installed-copy acceptance.

Important adoption details:

- Review the patch against the then-current Claude branch; `git apply --check` against the pinned source passed.
- Preserve the existing relay cursor. On a missing cursor the candidate replays existing queue entries instead of
  discarding them; that can replay historical alerts. Review bootstrap policy before installation.
- Previously failed messages that the old relay already marked sent need separate log reconciliation; installing
  this patch cannot identify or recover those messages automatically.
- Delivery is at least once. A successful HTTP request followed by a failed cursor write can produce a duplicate.
  Queue truncation, concurrent relay instances and cursor-file atomicity remain outside these checks.
- Resolve VB/ONB Tag and HeartbeatTag against `expected_setup.json`; the patch does not guess or change chart inputs.
- Confirm the Claude pre-market and journal/dashboard schedules are enabled for the new evaluation. The repository
  still describes them as paused; this review has no direct access to those scheduler settings.
- The watchdog's existing RTH schedule/conditions remain. Late-session coverage and the Sunday Bridge window need
  a deliberate session policy and Windows acceptance; continuously running today's RTH checks would create noise.
- Dashboard pass odds/drift still need the current six-strategy book, evaluation floor and portal expiry date.
- Check the floor's input history against Apex's actual threshold. The minimal patch corrects account phase and
  missing fields; it does not certify the existing last-row-per-calendar-day balance reconstruction as true EOD.

Before calling the system accepted, the operating owner must verify the installed Windows copies, all six strategy
versions/heartbeat tags, routing/positions, deliberate missing-chart and delivery-failure behavior, and an acknowledged
notification on the phone. A task result of zero alone does not establish delivery or successful monitoring.
