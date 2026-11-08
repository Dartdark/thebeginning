# Claude ingredient/ES review: fixed synthetic verification

Summary: Review pinned Claude7fb1ff5branch work, without running strategy backtests or changing it.
Retain exact source files/ref, commit this plan/script before synthetic checks.
No economic variants, market returns, plan/live changes or external messages.

Check1: AST-extract literal grids()from retained twin_continuation_bench.py, execute only that inspected
function with fake tc.PV=20and a single invented ES trade entry100exit110, net470, low99. Require copied
function's realizedterminal470matchesinput; compare its adversemark with multiplier-correct50$/point.
Record whether its worstpath differs even when terminal P&L agrees. Do not import author module/top-level code.
Check2: AST-inspect bridge_noise_15m_test.run's tp=sl*rrassignment, and ingredient ablation's "no stop"
kwargs sl=1e6,rr=1.0. Evaluate only numeric bindings: originalstop50,target25 vs assumedno-stopboth1e6.
Classify as a coupled intervention, not empirical isolated stop value. No candidate return reruns.

Pass for fixtures means source findings reproduced, not strategies/cash paths validated. Report confirmed
issues and untested consequences separately; no new ES performance or claims of changed account odds.
Process advice: design-only drop-one tests with trial ledger; already-seen2023+is historical/post-selection,
not a fresh validation. Report source account comparisons as Claude's results, not independent reproductions.
