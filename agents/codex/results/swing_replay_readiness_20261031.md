# Swing Target replay: blocked baseline rebuild, cause identified

Summary: Read the latest requested brief and resumed the open corrected-exit-kind replay.
A clean baseline rebuild crashes on an ONB ML report's explicit `open` exit mark.
The research adapter excludes that mark and completes canonical paths for 343 closed ONB trades.
The ST enum correction matches its frozen 602-trade ledger; account effects remain uncomputed.
Do not treat the prior payout estimates as a completed corrected replay.

Plan: `agents/codex/plans/swing_replay_readiness_20261031.md`, commit 8f534a9.
Script: `analysis/codex_swing_replay_readiness_20261031.py`.
Output: `analysis/outputs/codex_swing_replay_readiness_20261031/checks.json`.
New strategy trials: 0. Account simulations: 0.

## Reproduced blocker and bounded correction

The documented fresh-session command, `python3 analysis/build_lab.py SCRATCH`,
creates the NQ/ES grids and adds VB, then fails in `portfolio.paths` at `adv[-1]`.
ONB ML's final report pair is trade 344: entry 2026-10-12 09:15, with exit signal
`open` and an export mark dated that day at midnight. `load_mc` treats it as a
closed market exit, yielding j0=546 and j1=0. This is an open-position valuation
mark, not evidence of a real midnight fill.

The proposed `load_closed_mc` helper excludes **only explicit open marks** and
rejects other unsupported cross-date or reversed paths. It preserves same-bar
closed trades. On the actual ONB report, all 343 remaining closed trades complete
the canonical path construction with finite values. This verifies parser/path
completion, not historical fill accuracy. Shared loader and live files were not edited.

The report audit also identifies five cross-date Overnight Drift backup trades.
They require explicit overnight-date handling; the adapter refuses to silently
delete them. OND is not an active funded-plan leg. Closed holidays must be handled
according to the documented strategy fixes, rather than by a generic j1<j0 filter.

## Swing Target and portfolio controls

The canonical fixed loader maps the frozen ledger's reasons exactly to numeric
kind: 264 targets, 82 protective exits and 256 time exits. Preserving its three
historical holiday repairs, eliminating the extra target tick changes total
closed cashflow by $132 per one MNQ across the ledger. This is existing-trade
accounting, not a new annual return or a measured live saving. Earlier independent
path reconciliation is in `weekly_cross_review_20261030` outputs.

The old bench repairs three holiday holds by exiting at the last available bar;
the traded v3 skips those dates. A corrected accounting replay must keep that
distinction visible and cannot automatically establish exact v3 results.

`plans50()` also represents the earlier RS-longs roster. The adopted plan now uses
T_ONESIDE instead. The existing replacement sweep lacks empty-slot controls.
Preserve a historical comparison for the accounting correction, then separately
compare the current roster with BASE/ADD/REPLACE/EMPTY at integer sizes, paired
histories, and the prescribed payout/risk/timing measures. More favorable isolated
cashflow does not itself prove a plan-level result under changing quantities,
trailing floors and payout caps.

## Remaining work and reproduction

NQ and ES grid rebuilds completed in `/workspace/swing_replay_cache`; the failed
baseline build did not produce `lab.pkl`. CL grid/gap frames, VB flags and RS trade
cache inputs also need rebuilding. The readiness JSON lists the precise missing
inputs. `swing_be.csv` is merely a staging copy of the committed frozen ledger.

Run from the repository root after installing the documented research dependencies:

```
python3 analysis/build_lab.py /workspace/swing_replay_cache
# Reproduces the shared loader's open-sentinel crash.
python3 analysis/codex_swing_replay_readiness_20261031.py /workspace/swing_replay_cache
# Audits all baseline reports and validates the bounded research adapter.
```

The check hashes source/report/ledger inputs and records versions. The first
command is expected to fail until the shared loader is corrected or a reviewed
research cache builder uses explicit closed-trade handling. No new payout, risk,
timing or strategy ranking is reported; the full corrected account replay remains
pending. No VPS, broker, account setting or live strategy change occurred.
