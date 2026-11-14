"""Weekly scope, syntax and invented accounting fixtures; no market backtests.

Read the detached pinned Claude worktree. Do not import its side-effectful
research/monitoring modules or open its same-week review before the independent
assessment has been sealed. Writes only Codex research artifacts.
"""
from __future__ import annotations
import ast
import hashlib
import json
from pathlib import Path
import subprocess
from types import SimpleNamespace
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SOURCE = Path('/workspace/thebeginning_weekly_source_20261113')
HEAD = '7b0caeff98ead324ecc492375659b0b89db13d9f'
BASE = 'fe35af99aa90d7f31b91f8693859251bb44dd9ab'
OUT = ROOT / 'analysis/outputs/codex_weekly_cross_review_20261113'
INPUT = ROOT / 'agents/codex/inputs/weekly_cross_review_20261113'
HASHES = {}


def git(*args):
    return subprocess.check_output(['git', '-C', str(SOURCE), *args], text=True)


def read(path):
    raw = (SOURCE / path).read_bytes()
    frozen = subprocess.check_output(['git', '-C', str(SOURCE), 'show', f'{HEAD}:{path}'])
    assert raw == frozen, f'Source differs from review pin: {path}'
    HASHES[path] = hashlib.sha256(raw).hexdigest()
    return raw.decode('utf-8-sig')


def functions(path, names, env):
    tree = ast.parse(read(path), filename=path)
    selected = [n for n in tree.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name in names]
    assert {n.name for n in selected} == set(names)
    for node in selected:
        node.decorator_list = []
    code = ast.fix_missing_locations(ast.Module(body=selected, type_ignores=[]))
    exec(compile(code, str(SOURCE / path), 'exec'), env)
    return env


def finish_fixture():
    """Actual from-now helpers versus a documented integer2->1 finish sleeve.

    Start from a valid account state above156k, but below159k. A single DT
    target is100points: net198.775/MNQ at the benchmark's NQ/10 cost proxy
    (200 gross less.725RT commission and.50entry slippage). Other days flat.
    This is a policy counterexample, not a new account model or probability.
    """
    W = np.zeros((21, 1440)); R = W.copy()
    one_contract_net = 200. - .725 - .5
    W[0, -1] = R[0, -1] = 2*one_contract_net
    env = functions('analysis/eval_size_live.py', ['now'], {'np': np, 'D': 21, 'ok': np.ones(21, bool)})
    full, valid = env['now'](W, R, H=20, bal0=158750., fl0=154750., tgt=159000.)
    Wf, Rf = .5*W, .5*R
    documented, valid_finish = env['now'](Wf, Rf, H=20, bal0=158750., fl0=154750., tgt=159000.)
    assert valid[0] and valid_finish[0] and full[0] == 1. and documented[0] == 0.
    combo_env = functions('analysis/eval_size_combo.py', ['ev_all'], {'np': np})
    port = combo_env['ev_all'](W, R, 20, 158750., 154750., 159000., 4000., 2000., False)
    half_port = combo_env['ev_all'](Wf, Rf, 20, 158750., 154750., 159000., 4000., 2000., False)
    assert port[0] == 1. and half_port[0] == 0.
    dt = read('funded_strategies/NQ_Dual_Thrust.txt')
    assert 'UseFinish(true)' in dt and 'FinAt = 156000' in dt
    assert 'Floor(NumContracts * FinishMult + 0.5)' in dt
    return dict(actual_from_now_helper_result='PASS' if full[0] else 'TIME',
                actual_numba_port_result=float(port[0]),
                documented_integer_finish_result='PASS' if documented[0] else 'TIME',
                full_contracts=2, intended_finish_contracts=1, initial_equity=158750.,
                full_end_equity=158750.+2*one_contract_net, finish_end_equity=158750.+one_contract_net,
                cost_convention='NQ/10 benchmark proxy, not authenticated nativeMNQ cost',
                limitation='Invented valid near-target state with one DT100point target; no actual frequency, pass-rate delta or installed input state claim')


def prior_closures():
    """Check old floor/tie/cost fixes without rerunning historical returns."""
    env = functions('analysis/plan_150k_test.py', ['evaluation'], {'np': np})
    W = np.zeros((21, 2)); R = W.copy()
    R[0, -1] = W[0, -1] = 7000.
    W[1, 0] = -4500.
    r = dict(st=150000., dd=4000., dll=1e9, tgt=9000., lock=150100.)
    assert env['evaluation'](W, R, 0, 21, r) == ('fail', 2)
    # Equality must give adverse-touch priority.
    W2, R2 = W.copy(), R.copy()
    W2[0, 0] = -4000.; R2[0, 0] = 9000.
    assert env['evaluation'](W2, R2, 0, 21, r) == ('fail', 1)
    j0, j1, je = 1, 3, 2
    arrays = [np.full((202, 1440), 100.) for _ in range(4)]
    g = SimpleNamespace(trading=np.arange(202), ts=pd.date_range('2020-01-01', periods=202),
                        o=arrays[0], h=arrays[1], l=arrays[2], c=arrays[3])
    lg = functions('analysis/long_after_green_test.py', ['one', 'run'],
                   {'np': np, 'pd': pd, 'J0': j0, 'J1': j1, 'JE': je, 'TICK': .25})
    be = functions('analysis/daily_reversal_bertola_test.py', ['trades'],
                   {'np': np, 'pd': pd, 'J0': j0, 'J1': j1, 'JE': je})
    cost = {}
    for symbol, pv, fee in [('NQ', 20., 7.25), ('ES', 50., 5.)]:
        expected = -.5*pv-fee
        green = float(lg['run'](g, pv, fee, [200], mode='full', sl=.005).net.iloc[0])
        bertola = float(be['trades'](g, pv, fee, .25, 'A', 'always_long').net.iloc[0])
        assert green == bertola == expected
        cost[symbol] = dict(green=green, bertola=bertola, expected=expected)
    return dict(continuing_eval_floor='PASS', simultaneous_target_risk_touch='FAIL_AS_REQUIRED',
                single_round_trip_commission=cost,
                still_open='General UNKNOWN held-path state is not supplied by the two daily helpers; 21-session expiry and DLL snapping remain inherited evaluation limits')


def main():
    assert git('rev-parse', 'HEAD').strip() == HEAD
    rows = [line.split('\t', 1) for line in git('diff', '--name-status', BASE, HEAD).splitlines()]
    scoped = [(st, p) for st, p in rows if not p.startswith('career/')]
    commits = git('rev-list', f'{BASE}..{HEAD}').splitlines()
    parsed, errors = [], []
    for _, path in scoped:
        if not path.endswith('.py') or not (SOURCE / path).is_file(): continue
        try: ast.parse(read(path), filename=path); parsed.append(path)
        except SyntaxError as exc: errors.append(dict(path=path, line=exc.lineno, error=str(exc)))
    INPUT.mkdir(parents=True, exist_ok=True); OUT.mkdir(parents=True, exist_ok=True)
    (INPUT / 'changed_paths.tsv').write_text('status\tpath\n'+'\n'.join(f'{s}\t{p}' for s,p in scoped)+'\n')
    scope = dict(base=BASE, source_head=HEAD, week='2026-11-07 through 2026-11-13 close',
                 base_definition='Last first-parent commit before2026-11-07T00:00:00Z, after previous Friday review',
                 reachable_new_commits=len(commits), changed_paths_total=len(rows), trading_process_inventory_paths=len(scoped),
                 excluded_nontrading_career_paths=len(rows)-len(scoped), commits=commits,
                 independent_first=True, same_week_claude_review_read=False,
                 coverage='Whole change inventory, risk-based material source and saved-result review; not a replication of every historical result')
    (INPUT / 'scope.json').write_text(json.dumps(scope, indent=2)+'\n')
    checks = dict(source_head=HEAD, syntax_only_python_files=len(parsed), syntax_errors=errors,
                  finish_mode_omission=finish_fixture(), previous_week_closures=prior_closures(),
                  no_real_market_or_account_simulation=True, no_live_or_notification_action=True)
    assert not errors
    (INPUT / 'source_manifest.json').write_text(json.dumps(HASHES, indent=2, sort_keys=True)+'\n')
    (OUT / 'core_checks.json').write_text(json.dumps(checks, indent=2)+'\n')
    print(json.dumps({k: scope[k] for k in ['reachable_new_commits','changed_paths_total','trading_process_inventory_paths']}, indent=2))
    print(json.dumps(checks, indent=2))


if __name__ == '__main__': main()
