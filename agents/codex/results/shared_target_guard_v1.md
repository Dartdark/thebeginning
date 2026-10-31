# Shared Target Guard v1: built for review, not installed

User approved a per-account shared manual balance input. Built the publisher, separate monitor-first PowerLanguage draft, reference checks and [setup/review guide](../code/SHARED_TARGET_GUARD_SETUP.md). Existing Target Guard and all live/settings files are unchanged.

## Delivered behavior

Initialize an evaluation alias/token and fixed target once. For each session, confirm the whole account is flat and enter its reconciled balance once. The writer publishes a cent-precise, session-labelled INI for all that account's chart guards. Account files are separate. Targets default to $53,050 / $159,050; they do not need daily edits. Revisions/checksum, atomic replacement and exclusive writer locks support consistent reading. Incorrect/stale inputs do not fall back to guessed balances.

This reduces manual chart edits. It preserves the original **per-chart** calculation and does not infer broker balances, aggregate P&L across charts, account-wide flattening, entry blocking or pass verification. A session-start snapshot becomes inaccurate for this purpose after additional realized activity unless manually reconciled again with all positions flat. Monitoring a future broker-balance reader was not implemented because none has been verified.

## Verification

Command: `/workspace/venvs/thebeginning/bin/python -B analysis/codex_shared_target_guard_checks.py`.

Result: **14 tests passed**, zero failures/errors. Tests cover cent precision/nonfinite inputs; fixed targets; account and checksum mismatches; session rollover, maintenance, midnight, weekends and DST; stale/future/mixed revisions; missing/malformed fields; restart persistence; writer exclusion and interrupted replacement; already-met targets; whole-contract long/short tick calculations including MNQ/NQ and negative price rounding; and draft default/date-conversion checks.

Results: [`verification.json`](../../../analysis/outputs/codex_shared_target_guard_20261028/verification.json).
Writer/reference: [`codex_shared_target_guard.py`](../../../analysis/codex_shared_target_guard.py).
Tests: [`codex_shared_target_guard_checks.py`](../../../analysis/codex_shared_target_guard_checks.py).
Draft: [`Apex_Target_Guard_Shared_RESEARCH.txt`](../code/Apex_Target_Guard_Shared_RESEARCH.txt).

**Not verified:** MultiCharts compilation, native Windows profile API/bitness/cache behavior, actual file refresh across charts, broker account binding, tick/event latency, resting-order cancellation or paper/live order results. Python verification is not PowerLanguage execution. Date conversion follows the repo's EL date convention (`Date + 19000000`); no shared pitfalls file was edited.

## Placement and next step

For 50K and 150K evaluations this is a conditional operational convenience, pending independent review and paper compilation. Funded 50K/150K and personal plans are outside this evaluation utility's policy. No financial/account bench or claimed return/DD, pass-rate or payout improvement; zero economic trials. No research programs or automations restarted.

**Recommendation:** Claude independently reviews the package, then compile and exercise it on disconnected paper charts with orders disabled. The exact checklist is in the setup guide. Installation and any account-wide automated controller need separate approval after that evidence.

Current connected source reviewed: Claude-branch `apex_strategies/Apex_Target_Guard.txt`, blob `f96ae8c85ec6ef3274711f7f26445dbf86373d33`. Work is on `codex/work` only, with concurrent/untracked work preserved. No external messages, purchases, live/VPS/broker/API changes or root TODO edits.
