"""Synthetic source checks only; no market data or strategy returns.

Pinned Claude source: b007bc42fdc991e3cc8fe8c3423f177eb10411d8.
Run with the configured Python from the repository root.
"""
import ast
import json
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'agents/codex/inputs/claude_more_20261024/mnq_sharedcap_test.py.txt'


def main():
    tree = ast.parse(SOURCE.read_text())
    functions = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in {'netted', 'realize'}]
    env = {'np': np, 'C': np.array([[100, 90, 90, 100] + [100] * 386]), 'C1501': [100], 'PV': 2.0}
    exec(compile(ast.Module(body=functions, type_ignores=[]), str(SOURCE), 'exec'), env)
    events = {'ON': [(0, -3, 100), (30, 3, 95)], 'NA': [(10, 2, 101), (40, -2, 104)], 'TOTM': []}
    replay = env['netted'](events)
    phantom = [e for e in replay if e[0] == 30]
    assert phantom == [(30, 3, 95)], replay
    # A full round trip loses $20, beyond a $15 cap. The next entry must be blocked.
    # Current implementation tests the cap only with a nonzero position.
    cap_events = [(0, 1, 100), (1, -1, 90), (2, 1, 90), (3, -1, 100)]
    got, fills = env['realize'](cap_events, 0, 1.0, cap=15)
    assert got == -24.0 and fills == 4, (got, fills)
    # Documented first eligible close is 09:00 (b=0), but can requires b >= 1.
    clocks = [900 + 100 * (b // 2) + 30 * (b % 2) for b in range(13)]
    eligible = [clocks[b] for b in range(12) if 1 <= b <= 12]
    assert eligible[0] == 930
    result = {
        'source_commit': 'b007bc42fdc991e3cc8fe8c3423f177eb10411d8',
        'kind': 'synthetic implementation checks; not a backtest',
        'sharedcap_stale_exit': {'actual_event': phantom[0], 'expected': 'ignore ON exit after reversal closed ON'},
        'sharedcap_flat_breach': {'actual_pnl': got, 'actual_contract_fills': fills, 'expected_pnl': -22.0, 'expected_contract_fills': 2, 'cost_per_fill': 1.0},
        'intraday_first_signal_close': {'code': eligible[0], 'documentation': 900},
    }
    out = ROOT / 'analysis/outputs/codex_claude_more_review'
    out.mkdir(parents=True, exist_ok=True)
    (out / 'synthetic_checks.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
