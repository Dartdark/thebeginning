"""Independent source/engine review fixtures; never loads research history.

This verifies the parent's execution helper on deterministic synthetic arrays.
It is not a separate strategy implementation, raw-data replication, parity
check, return trial, account bench or promotion decision.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scratch_data/codex_deps'))
sys.path.insert(0, str(ROOT / 'analysis'))
import numpy as np
import codex_swing_engine as engine

OUT = ROOT / 'analysis/outputs/codex_swing_target/independent_engine_review.json'
REPORT = ROOT / 'agents/codex/results/swing_target_engine_review.md'
SOURCE = ROOT / 'agents/codex/inputs/swing_target/Swing_Target_NQ.txt'
PAPER = 'https://ssrn.com/abstract=6350238'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def short_fixtures():
    arrays = [np.full((1, 1440), np.nan) for _ in range(4)]
    o, h, l, c = arrays
    signal = np.array([[0, 526, -1, 20.]], dtype=float)
    schedule = np.array([20.])
    # Short100: prior average20 gives BE trigger94 and target93. The low93.5
    # arms BE without target+through92; the later bounce exits at100. The
    # initial high101 occurs before that trigger, so it still counts as MAE.
    o[0,526], h[0,526], l[0,526], c[0,526] = 100., 101., 93.5, 100.
    result = engine._market_many.py_func(o,h,l,c,signal,schedule,True,1.,0)
    assert len(result) == 1
    be = dict(zip(engine.COLUMNS, result[0].tolist()))
    assert be['entry'] == 100. and be['exit'] == 100.
    assert be['reason_code'] == 3 and be['mae'] == 20.
    assert be['entry_minute_adverse_px'] == 101.
    # Same entry, ordinary first minute. The next open120 exceeds the old
    # protective stop114. Fill at120 and record400/NQ adverse excursion.
    o[0,526], h[0,526], l[0,526], c[0,526] = 100., 101., 99., 100.
    o[0,527], h[0,527], l[0,527], c[0,527] = 120., 121., 119., 120.
    result = engine._market_many.py_func(o,h,l,c,signal,schedule,False,1.,0)
    assert len(result) == 1
    gap = dict(zip(engine.COLUMNS, result[0].tolist()))
    assert gap['entry'] == 100. and gap['exit'] == 120.
    assert gap['reason_code'] == 0 and gap['mae'] == 400.
    assert gap['exit_phase_code'] == 0 and gap['exit_minute_adverse_px'] == 120.
    return dict(short_causal_be=True, short_pretrigger_adverse_not_erased=True,
                short_gap_stop_uses_worse_open=True, short_gap_mae_reconciles=True,
                synthetic_short_be_trade=be, synthetic_short_gap_trade=gap)


def main():
    source_hash, engine_hash = sha(SOURCE), sha(Path(engine.__file__))
    source = SOURCE.read_text(encoding='utf-8')
    assert 'SetProfitTarget' in source and 'SetStopLoss' in source
    assert 'SetBreakEven' not in source and 'Breakeven' not in source
    parent_suite = engine.synthetic_checks()
    assert all(parent_suite.values())
    independent = short_fixtures()
    result = dict(status='PASS: limited source/engine/synthetic review',
                  source_sha256=source_hash, engine_sha256=engine_hash,
                  review_script_sha256=sha(Path(__file__)),
                  provided_synthetic_suite=parent_suite,
                  independent_short_fixtures=independent,
                  research_history_loaded=False, return_outputs_inspected=False,
                  independent_full_raw_data_replication=False, multicharts_parity_established=False,
                  new_economic_trials=0, account_or_promotion_verdict=False,
                  limitation='Minute paths, unrounded distances and chart-template proxy remain assumptions.',
                  placebo_terminal_state_note='replay_market omits unclosed terminal signals; parent must reconcile requested/closed counts.',
                  paper=dict(url=PAPER, abstract_verified=True, full_pdf_access='403; no bypass',
                             supports='ES value-area breakout events in first30min weaker; not NQ prior2day or15min validation'))
    assert sha(SOURCE) == source_hash and sha(Path(engine.__file__)) == engine_hash
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2, allow_nan=False) + '\n', encoding='utf-8')
    REPORT.write_text(f'''# Swing Target source and engine review: PASS WITH LIMITS

Summary: No material causal execution blocker found against the frozen plan.
The supplied deterministic suite and two independent short-side BE/gap fixtures pass.
Uploaded source omits the prose's breakeven rule and has exact-boundary/holiday limitations.
This is an execution-helper review, not independent raw-data replication, MC parity, return validation or promotion.

Scope: source `agents/codex/inputs/swing_target/Swing_Target_NQ.txt`, engine `analysis/codex_swing_engine.py`,
plan `agents/codex/plans/swing_target.md`. Script: `analysis/codex_swing_engine_review.py`.
Output: `analysis/outputs/codex_swing_target/independent_engine_review.json`. New economic trials: **0**.
Reviewed engine SHA256: `{engine_hash}`. Source SHA256: `{source_hash}`.

## Source/prose discrepancies

- **Breakeven absent:** source lines78–83 only set target/stop. No BE trigger or exit exists, so the uploaded code cannot
  itself produce the prose's31 BE exits. The separately frozen CODE_BE version addresses only this discrepancy.
- **Minute labels:** lines73–75 submit at08:45 into the bar labeled08:46; on the close-stamped proxy its open is normally
 08:45 wall time. Inclusive14:29 submission permits the14:30-labeled bar. Lines86–88 submit a market exit at14:59,
  filling at the open of the15:00-labeled bar, normally14:59 wall time. Labels must not be presented as verified broker clocks.
- **Exact session boundaries:** reset requires08:31 (46–59), storage/termination requires15:00 (92–95). Missing boundary
  bars and early closes can omit stored sessions or carry a position. Recomputing AvgRng at a later08:31 can change that carried bracket.
- **Execution:** header line18 admits level-price Python fills despite possible gap-through stops. Both directions are
  submitted together (73–75), so the parent's OCO/path treatment is a declared proxy, not source-proven MC behavior.
- **Prior searches:** header lines4–5 state several start times were inspected in both periods. Author trial count is
  unknown;2023+ is previously examined historical validation. No supporting MC trade export was supplied for the584-trade claim.

## What the engine checks establish

The parent's synthetic suite verifies post-entry path/MAE, causal BE, early disarming, worse-open entries, one entry/day,
inclusive last submission, next-native-bar orders, unrepaired missing15:00 carry, one-point target-through and fixed path sensitivity.
Independent additional fixtures verify short100 → low93.5 → bounce100 exits at BE, while the earlier high101 remains in MAE;
and a short stop nominally114 fills at a worse next open120, with400/NQ MAE.
Read-through found protective range updates occur after the08:31 close, and BE affects subsequent adverse movement.
No research-history cache or strategy return output was opened for this review.

`replay_market` omits a signal still open at dataset end. The parent must reconcile requested/closed placebo counts and disclose
unresolved signals, rather than silently count them as no-event zeros. This review does not independently verify those run-level counts.
The parent wrapper separately flags cross-date and late exits; finite-held-minute counts alone would not prove flat-deadline compliance.

## Howard reference

The [primary SSRN abstract]({PAPER}) describes ES volume-profile value-area breakout events during January2025–January2026.
It reports weaker first30-minute events and an economically insignificant unfiltered continuation signal. That supports an early-session
timing concern in its own setting. It does not establish this NQ prior-two-day price-level rule, a15-minute cutoff, or0DTE causation.
The full PDF returned403; no access bypass was attempted. Only the primary indexed abstract was verified.

## Limits

This uses the parent's helper plus synthetic fixtures, not a second end-to-end implementation or native tick replay.
It does not verify the reported trade count/PF, raw-history completeness, tick rounding, chart-template parity, broker fills,
portfolio benefit or account survival. Those remain the parent audit's separate tests and independent-review requirements.
No source, engine, live/VPS/broker configuration or key was modified. Only this review script, JSON and report were created.
''', encoding='utf-8')
    print(json.dumps(dict(status=result['status'], parent_suite_pass=True,
                          independent_short_be_and_gap_pass=True, output=str(OUT)), indent=2))


if __name__ == '__main__':
    main()
