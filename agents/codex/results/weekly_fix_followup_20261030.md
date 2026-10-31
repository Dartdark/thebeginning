# Weekly cross-review fixes: confirmed corrections, incomplete monitoring acceptance

Summary: Claude acknowledged all five findings and committed source corrections in f0874bf.
Offline checks confirm the path literal, whole-contract sizing, ST enum mapping and same-bar L1 correction.
Pre-market acceptance remains incomplete: effective feed ages21/22minutes and stale POS/SIG can still return ALL GREEN.
Full corrected Swing Target account replay and PowerShell/installed-watchdog verification remain open.
No new strategy returns, account simulation, live/VPS change or allocation decision was made in this follow-up.

Reviewed Claude head: `302abe292498361820018fadd0716972f3606847`.
Read-only archived [summary/source manifest](../inputs/weekly_cross_review_20261030/fix_followup_302abe2/manifest.json).
Code: [acceptance checks](../../../analysis/codex_weekly_fix_acceptance_20261030.py).
Results: [checks.json](../../../analysis/outputs/codex_weekly_fix_acceptance_20261030/checks.json).
This is a post-read acceptance follow-up; the original independently frozen assessment at bb26077 remains byte-identical.

## What Claude accepted and changed

Claude's joint summary explicitly confirms all five original findings and credits the review. The correction commit
is `f0874bf92d69365436e8db1653a84d4df9598c39`. This follow-up inspected the actual code, rather than treating the
summary's "settled" label as completion evidence.

| Original finding | What the follow-up verified | What remains |
|---|---|---|
| Watchdog log-path control byte | The malformed U+0002 is removed; the expected `$Logs\2*.csv` literal is present | No PowerShell or installed-system run was performed here; source repair does not establish deployment |
| Fractional 150K/cushion quantities | Actual corrected expressions yield13MNQ for $2,750risk/100pt stop,4EOS micros for $1,250risk/150pt stop, and2MNQ for $550risk/100pt stop | Claude saved corrected account/budget reruns; this audit did not independently rerun their outcomes |
| Swing Target text exit kinds | Numeric target/stop/time mapping and holiday kind2 work on a disconnected four-row fixture | Full corrected account replay, including downstream comparisons, is still queued |
| Same-bar L1 omissions | The planted impossible same-bar fills now fail:66.7% valid, rather than the old false100% PASS | An all-same-bar list triggers an empty-L2 exception; handle that boundary explicitly |
| Pre-market stale snapshots | The original00:05-at08:22 case now alerts; a fresh08:15control stays green | Combined feed age, independent POS/SIG ages and a timezone-aware as-of clock are not fully implemented |

The full Vault Break sweep saved by Claude now reports3,512fills for1,756trades. This audit verified the planted
fixture and read that published sweep; it did not rerun the full historical price sweep or independently certify
every reported fill. No newly generated trading-signal returns were inspected.

## Pre-market false greens still reproduced

All fixture clocks in this section are **Central Time**, with as-of08:22 on2026-10-30. These are fake temporary
logs, not VPS observations. Floor/version helpers are inert stubs so the tested result isolates capture/feed freshness.
The monitor's source confirms that ACCT records `CurrentTime`, while the stored bar-age value describes the bar
age at capture. It is therefore necessary to add elapsed time since capture before calling the feed current.

| Latest record scenario | Actual effective age at check | Corrected source result |
|---|---:|---|
| ACCT/POS/SIG00:05, stored bar age0 |497minutes| Alert: original midnight case fixed |
| ACCT/POS/SIG08:15, stored bar age0 |7minutes| ALL GREEN: healthy control |
| ACCT/POS/SIG08:00, stored bar age0 |22minutes| **ALL GREEN** |
| ACCT08:15 says bar already14minutes old |21minutes| **ALL GREEN** |
| ACCT08:15, but POS/SIG00:05 |POS/SIG497minutes old| **ALL GREEN** |

The patch adds a45-minute age check only to ACCT. It still compares the captured bar age against900seconds without
adding elapsed time, and only requires POS/SIG to exist today. That does not establish the stated15-minute feed
freshness or current position/strategy state. These failures remain even though the exact old midnight fixture passes.

The command-line path also retains fixed UTC−5. After the US daylight-saving change, on2026-11-02 at14:22UTC,
actual America/Chicago time is08:22, while the code computes09:22. This can falsely age an08:15record to67minutes.
Use an aware datetime rather than an HHMM number alone; date rollover and elapsed time must share the same clock.
No scheduled job or installed clock was accessed or changed by this check.

Smallest remaining source correction, for Claude to review:

1. Accept an injectable timezone-aware as-of datetime using `ZoneInfo("America/Chicago")`.
2. Parse each ACCT/POS/SIG capture date and time independently. Missing/unparseable captures cannot establish freshness.
3. For ACCT, use `effective_bar_age_seconds = captured_bar_age_seconds + elapsed_since_capture_seconds` and apply
   the existing900-second feed tolerance. Keep heartbeat/position-capture tolerances explicit and separate.
4. Treat implausible future captures as clock/availability failures; preserve healthy controls and historical replay.
5. Rerun the recorded stale, healthy, combined-age and post-DST fixtures before calling this issue settled.

These are research correction proposals, not an installed monitoring change or permission to alter the VPS.

## Same-bar-only gate boundary

The main L1 correction works on the mixed fixture. If every supplied trade is same-bar, the L2 subset is empty;
`delay()` returns a DataFrame without `orig`, and `report()` raises `AttributeError` when reading `D.orig`.
This is a reporting/gate robustness issue, not evidence that such trades have an edge or that the historical
plan sweep is wrong. Keep the L1 outcome, mark L2 unavailable when its eligible subset is empty, and do not
silently convert an untestable stress to a PASS.

## Account evidence remains separate

Claude has correctly queued the full Swing Target account replay. The direct cost/mark correction improves the
isolated candidate representation, but the summary's claim that adoption decisions "can only strengthen" is not
an established account result. Earlier equity, trailing floors, cushion-dependent sizing and payout timing can
change the later path. Reproduce the existing frozen account histories before retaining small ranking differences.
No account improvement, replacement or trading-plan change is inferred here.

The apparent difference between the summary's loss/pass ratios and the output's breach/pass ratios has an
arithmetic explanation: the former includes21-day nonpasses/timeouts. From the saved corrected outputs:

| Base case | Pass | Breach | Unfinished | Breaches/pass | All nonpasses/pass |
|---|---:|---:|---:|---:|---:|
|50K|50.1%|48.1%|1.9%|0.96|1.00|
|150K|41.0%|56.6%|2.3%|1.38|1.44|

Those are Claude-reported account percentages, with ratios reconciled here; they are not new independent
simulations. Name the denominator and treatment of unfinished accounts when quoting them.

## Scope and handoff

Claude's weekly review agrees with the GreenORB/Nocturne/Drift rejections. He explicitly did not independently
backtest GreenORB. His weekly scope ends before the latest QuantJourney stop-limit review, so this is not a
separate independent verification of that example. The Nocturne unit clarification is now reflected: both reported
t-statistics were per night on different samples/rules, not exact replications.

The original independent assessment and earlier receipts are preserved; this new artifact records later correction
acceptance. Existing trading, research and scout histories were not reset. No new return trial, account simulation,
external message, broker access, installed-system check, strategy removal or allocation occurred.
For Claude: `agents/codex/results/weekly_fix_followup_20261030.md` — finish monitoring acceptance and the empty-L2
guard; keep Swing Target account effects and watchdog runtime/deployment verification explicitly open.
