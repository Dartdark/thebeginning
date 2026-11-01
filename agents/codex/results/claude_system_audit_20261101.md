# Claude work audit: useful research platform; correct clocks and admission before trusting new results

Summary: Inventoried 80 Claude commits/133 changed paths and pinned 59 research/source/result artifacts at `3ad0b16`.
Eight disconnected checks reproduce six issue groups; source review adds a post-result protocol-change accounting concern.
The saved lab has six design rejections and six blocked/duplicate rows, no holdout openings or surviving candidate.
Inverse-volatility and firm-risk results are useful historical studies, with the source/accounting/selection limits below; no new returns were run here.
Interview lessons favor enforced admission, explicit permissions, reproducible inputs and review quality; no separate Claude interview response was available.

## Scope and reproducibility

Reviewed Claude branch `claude/nq-trading-strategy-params-5h9d20` at **`3ad0b16e7101ace22b870fe32dbf09fd4e2a80ee`**,
confirmed through the GitHub connector on 2026-11-01. Its two current mirrors matched that head at discovery.
Codex starting head: `f5f67a06558f74616e25e7e13820fe7962779d3a`. The branch comparison's merge base is
`86df2c0fa4b0e530b2c29caddd364830d12edab3`; 80 commits/133 paths are the comparison scope, not the entire repository history.
Git shell fetch was unavailable (configured proxy unreachable); connected GitHub reads supplied the checked remote state.
The branches diverge. No Claude branch was checked out, merged, reset or changed.

- [Source inventory and commit scope](../inputs/claude_audit_20261101/scope.json).
- [59 exact GitHub blob identities](../inputs/claude_audit_20261101/source_blobs.json); source text retained below `../inputs/claude_audit_20261101/3ad0b16/`.
- [Disconnected audit script](../../../analysis/codex_claude_audit_20261101.py).
- [Executed fixtures and source SHA-256 manifest](../../../analysis/outputs/codex_claude_audit_20261101/verification.json).
- [Interview assessment](jane_street_interview_review_20261101.md).

Run from repo root: `/workspace/venvs/thebeginning/bin/python analysis/codex_claude_audit_20261101.py`.
Eight synthetic scenario groups executed successfully. New historical strategy/account return tests: **zero**.
Tests import frozen research helpers with main blocks inactive; invented files, arrays and mocked setup/Git reads isolate them
from live data, broker connections, alerts and the VPS. No live-system acceptance or installed-copy parity is claimed.

This is a broad repository audit plus earlier audit-status reconciliation, not an independent rebuild of every historical
strategy or an assessment of inaccessible Claude conversations. The user was asked for Claude's separate interview response;
none was available when writing this report. Career drafts, unrelated branches, broker/VPS/installed execution and external
scheduler delivery are outside the code verification. The uploaded interview/audio was not published to GitHub.

## New material findings

### F1 — High: NG event selection uses information unavailable to the strategy

Frozen `analysis/lab_Q007.py:26` groups the entire week, prefers qualifying Thursday volume, otherwise chooses the larger
Wednesday/Friday 09:31 ratio. `analysis/lab_Q009.py:37` reuses this selector for an **08:00 entry and 09:29 exit**.
That same-day 09:31 observation is after Q009 has exited. Saying “volume only, never returns” does not make it causal.
For Q007, same-day 09:31 is before its 09:36 entry, but deciding whether a Wednesday event qualifies can depend on Thursday
or Friday observations that have not occurred yet.

Fixture: with Wednesday ratio 4 and Thursday ratio 1, Wednesday is selected. Change only future Thursday ratio to 4;
Wednesday disappears and Thursday is selected. A second fixture changes only a day's future 09:31 volume and changes Q009's
pre-report eligibility. The tests execute the frozen selector and confirm Q009 imports that exact function.

**Impact:** Q009 is not an executable pre-release study as specified. Q007 is not a causal weekly holiday-release selector.
Both saved verdicts are FAIL, so this does not establish an overlooked winner or a reason to trade them. It limits the scope
of claims that the economic mechanisms were ruled out. Do not promote or repeatedly retest them under the same definition.
Use dated official release calendars, with verified time changes, for any separately justified future event study. If those
inputs are unavailable, record the blocker and move on. Q012's volume-labelled “ECB days” likewise require actual calendar
validation; its ledger already acknowledges contamination by ADP.

### F2 — High: a missing time-exit/holding path still produces a trade return

`analysis/lab_Q007.py:56` skips missing high bars and, if no observed stop hit exists, exits at the **last finite close** in
the intended window (`:61`). Q009, Q012 and Q016 repeat this pattern. It can silently move a scheduled exit earlier and treat
an unobserved holding path as if no stop was hit.

Fixture: a synthetic Q007 follow trade has an entry and last observed close at 09:37; all subsequent bars and the scheduled
10:30 exit are missing. The helper still books **+$975 net per synthetic NG**, at its $25 round-trip cost. That is an invented
fixture demonstrating mechanics, not a historical profit. Missing exit prices/path cannot justify that fill or stop survival.

**Required correction:** distinguish a valid known early-close protocol from unexpected missing bars. Reject/quarantine
unresolved paths, retain counts and exact times, and reconcile identical eligible samples before any already-authorized
rerun. Do not fill, drop silently, or carry prices to fabricate returns. The frequency/economic impact in actual data was
not measured here.

### F3 — High: the lab's claimed holdout/gate enforcement occurs too late or accepts declarations

`analysis/lab_tools.py:92` checks STOP, completed daily rows and whether an idea is runnable. It does not reserve a holdout
look or verify preregistration, exact code, prior-stage receipts or a checked-head lease. The quarterly check is in
`log()` at line117, which the skill invokes **after testing**. Candidate scripts accept `--holdout` without consuming a
reservation or recording a once-only opening before reading results.

Fixture: 40 looks already recorded earlier in the same quarter; `can_run()` returns **OK**. Only trying to log look41 is
rejected. Another fixture logs a stage5 PASS with `looks:0`, empty receipt arrays and no preregistration/result files.
Receipt key presence is enforced; evidence truth and stage progression are not. The `tier_check`/`who_pays` checks similarly
validate declaration presence/category, not the search's accuracy or a named payer.

**Impact:** the platform is a partially enforced workflow, not the fully automatic gatekeeper described in
`portfolio/SYSTEM.md`. No actual overspend/false promotion is demonstrated: the saved ledger reports zero holdout looks
and no PASS. Add atomic pre-execution admission/reservation with per-hypothesis consumed-look identity and verified
code/source/input/gate hashes, and fail closed before returns. Keep the existing budgets; do not restart counts.
The Codex scout's checked-head lease and admission design is a reference, not proof Claude's separate lab already uses it.
A dashboard state of “running” currently means STOP absent, not proof a worker or schedule is executing.

### F4 — Medium: Git failure can be reported as a successful pre-push/synchronization check

`tools/prepush_check.py:18` discards subprocess exit status. An empty `rev-list` result does not fail `before()`; in
`after()`, two empty `rev-parse` results compare equal. The synthetic Git stub returns empty strings for failed reads:
both checks return an empty error list, which the CLI would print as **PREPUSH: OK**.

Check return codes, require well-formed commit IDs and a successful remote read, and use an expected parent at mutation.
Do not equate a stale remote-tracking ref with current remote state. No push, hook execution or remote write was performed
by this fixture; this report is published only to codex/work through an independently checked non-force parent update.

### F5 — Medium: the provenance stamp is not an exact content/run identity

`analysis/provenance.py:25` hashes names and file sizes, not file contents. A same-length historical price edit changes the
file's true SHA-256 while leaving the printed fingerprint **identical**; the synthetic test reproduces this. The “dirty”
label does not encode a patch, and `lab_tools.log()` stamps at logging time rather than binding code/inputs before execution.
Cache pickle versions, MC tickets and fitted artifacts are not identified by the CSV name/size fingerprint.

Keep the cheap stamp as an inventory hint, and add content hashes/cached verified manifests for every actually consumed
input and exact code/dirty patch, with start/end run receipts. Do not describe the present stamp as enough to recreate an
exact run. This audit's frozen blobs and SHA-256 manifest are independent of that helper.

### F6 — Medium: undefined edge crashes the advisory buy gate and can suppress the morning digest

`analysis/buy_gate.py:40` checks `edge is None` but then formats it with `:.0%`. With40 recorded live trades and no positive
backtest denominator, the source raises `TypeError: unsupported format string passed to NoneType.__format__` instead of
returning PLAN ONLY. `morning_brief.brief()` calls this function without catching that exception.

This was reproduced using invented in-memory dashboard/setup records; **no live/setup files were opened**. Missing edge
needs an explicit UNKNOWN/insufficient-evidence explanation. Saved dashboard inputs also need their own freshness/coverage
checks before a favorable advisory status. This is source behavior, not evidence a real morning brief failed or a purchase
was automatically authorized.

### F7 — Medium: the Q016 amended universe must remain a separate post-result protocol look

`checks/candidates/lab_Q016/PREREG.md` initially requires a 09:01 volume confirmation although entry is08:59.
Its amendment removes that confirmation **after the first run**, which had returned V2 +$184/trade, t1.49 on10 trades and
placebo p0.12. The amendment records these numbers, which is good, but calls the change “day selection only, not a variant.”
Removing an eligibility condition changes the economic protocol/sample; under the user's information-clock and multiplicity
rules it is not an unchanged confirmation. The ledger has one Q016 study row/zero looks, not an explicit definition ledger
for both three-rule universes. Preserve both examined protocols and all outcomes; do not erase the earlier look or invoke
the <=3-variant exception as if only three economic definitions had been examined.

The revised design also fails (best t0.76), so no holdout/account rescue or promotion is justified. This audit does not
request reopening it. The process lesson applies before the next distinct candidate.

## What Claude did well, and what remains qualified

### Reconciled older defects: do not reopen completed work

- The 10/24 SharedCap stale-exit/loss-latch, IntradayMomentum first decision and VWAP Drift date-window findings have
  documented corrections/reruns in `agents/cross_review/2026-10-25_claude_response_to_codex.md`.
- Weekly integer-sizing, leak-check same-bar coverage and Chicago/DST corrections have dated follow-up checks.
  Installed PowerShell/runtime acceptance is separate and was not investigated here.
- The claim that improved Swing Target accounting “can only strengthen” adoption was withdrawn. The corrected saved
  account replay reports essentially ties: two-year change **-$7** for50K VB reduction+ST and **-$7** for150K DT->ST;
  Claude/user reverted the funded swaps. This is a good example of letting replay override an appealing explanation.
  These legacy-source outputs do not certify today's exact integer/native-fee/current-roster configuration.
- Current integer inputs, current-roster overlap sensitivity and chronological ladder checks were already completed in
  [the final portfolio follow-up](portfolio_audit_final_followup_20261030.md). That independent check found **0/500**
  paired funded histories changed for either size under its narrowly specified overlap correction. Do not request their
  first implementation again. Literal-version ledgers, intraday marks, margin and future edge remain qualified.
- PAPERTREND's discretionary placement does not turn its earlier statistical checker FAIL into PASS. MC ticket/source
  parity and the existing qualification remain relevant; no new full replication was performed here.

### Current lab outcome: honest negatives, narrower economic conclusions

At the pinned head `lab/ledger.json` contains12 rows: **six design tests failed**, five duplicate skips and one data-blocked
NG expiry idea. The six design best t-statistics, as reported by Claude, are NG reaction -0.04, 6E fix0.85, NG pre-report0.36,
6E month-end0.17, ECB0.40 and ES/ZN pre-release0.76. Holdout looks:0; candidates surviving stage1:0. Twelve rows do not mean
12 newly executed backtests. The clocks and incomplete-path issues above qualify the affected mechanism-wide conclusions;
negative outputs should be retained, not promoted or silently reset.

### Inverse-volatility personal sizing: useful, not independent evidence of future income

`personal_invvol_confirm.book()` estimates each year's volatility from earlier years; no current-year volatility is read
when selecting that year's weights. This is a useful chronological sensitivity check. The source also explores equal,
uncapped/capped weights,15/19 sleeves and several integer sizes on already familiar history. “2023+ never seen” is incorrect
as a research-history claim: the strategies and earlier allocations have been studied on those years. A walk-forward
calculation can be causal while its reported method is selected after seeing that same history.

Claude's saved **15 cleared pieces, approximately2 micros per sleeve,2023+** comparison:

| Method | Median252-session P&L | Daily DD p95 | P&L / DD p95 | DD-p95/20% capital |
| --- | ---: | ---: | ---: | ---: |
| Equal | $70,329 | $11,529 | 6.10 | $57,647 |
| Yearly past-only inverse-vol, cap2x | $48,243 | $6,272 | 7.69 | $31,360 |

The source shows lower absolute P&L and lower modeled risk, with a better ratio; this is not an equal-capital incremental
P&L result. Independent rounding does not preserve total lots exactly (the initial15-sleeve1x comparison uses15 versus18
lots); the output discloses this but prose says “same total micros.” Compare actual rounded vectors, fees and margin at the
same capital before interpreting deployable superiority. Static2026 chart vectors and a yearly reweighted historical path
are distinct protocols; do not treat one path's statistics as exact validation of the other.

This audit did not rerun that historical book: matching cached paths are unavailable locally. Earlier source-version,
report-cutoff, exit-day accounting, margin and marked-open-position limits carry forward. Capital=DDp95/20% is a
conditional risk rule, not guaranteed sufficient capital or a stop on losses. User adoption recorded in Claude's docs
is not independent economic verification or installation confirmation. No allocation is changed by this review.

### Firm-level risk: useful dependence check; preserve the sample/uncertainty

Saved study: four150K evaluations started one/day versus one/week, historical start dates2018–2023-08, same account engine.
One/day reports pass/fail correlation0.73, all-four-fail45.4%, no-passes48.3%; weekly spacing reports0.29,25.9%,28.8%.
Mean passes are1.58 for both. Distinguishing correlated failures from number of expected passes is useful.
These are overlapping historical batches, without an independent confidence assessment/new holdout in this audit;
“~one year apart” is a comparison, not proof of statistical independence. Legacy micro-fee/path assumptions remain.
Do not turn “about halves” into a future failure guarantee or infer20 copied funded accounts diversify one market path.

### Additional work reviewed at source/report level

- RollZone: Good Friday holding defect identified, negative Apex comparisons and C/expansion-only disposition; no promotion.
- GC USA->Asia: time-zone dependence, weakening continuation attribution, filter/stop failures and D disposition. Its source
  review correctly avoids adding a filter merely because recent risk improves. Chart-clock ambiguity remains material;
  the supplied report is not matched trade by trade here.
- Scout/queue/lesson/receipt records and modular runbooks improve continuity. They do not prove schedules actually ran,
  that an external alert arrived or that private sessions are visible to this app. No external messages were sent.

## Recommended order for Claude's next review

1. Correct event-information clocks and quarantine incomplete-price paths; retain the failed outcomes and prior definitions.
2. Enforce admission/look reservations before execution; bind stage evidence, exact inputs/code and checked parent.
3. Make Git checks fail closed, provenance content-based, and unknown advisory edge non-crashing; prove each with fixtures.
4. Reconcile the inverse-vol plan's static vectors versus yearly protocol, actual costs/margin and already-seen history.
5. Keep interview-inspired changes small and testable; measure fewer invalid runs and better reproducibility before adding
   more agents or schedules. Current missing data and researcher selection are not fixed by more throughput.

No trading-plan/size decision, live strategy, VPS, broker configuration, schedule or external notification was changed.
For Claude: `agents/codex/results/claude_system_audit_20261101.md`.
