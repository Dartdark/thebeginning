"""Reproduce engineering receipts only; no market-return or account simulation."""
import hashlib
import json
import platform
import subprocess
import sys
import unittest
from pathlib import Path

import codex_delta_straddle_strategy as strategy

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / 'analysis/outputs/codex_delta_straddle_build'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    suite = unittest.defaultTestLoader.discover(str(ROOT / 'agents/codex'),
                                               pattern='test_delta_straddle_strategy.py')
    result = unittest.TextTestRunner(verbosity=1).run(suite)
    if not result.wasSuccessful():
        raise SystemExit(1)
    packet = strategy.demo_packet()
    demo = strategy.plan(packet)
    # These receipts describe invented mechanics, never strategy profits.
    demo['input_sha256'] = hashlib.sha256(json.dumps(packet, sort_keys=True, allow_nan=False).encode()).hexdigest()
    demo['code_sha256'] = digest(Path(strategy.__file__))
    manifest = {'scope': 'SYNTHETIC ENGINEERING ONLY; NOT A HISTORICAL BACKTEST',
        'plan_commit': subprocess.check_output(['git', 'rev-parse', '04dbfaee'], cwd=ROOT, text=True).strip(),
        'python_version': platform.python_version(), 'external_dependencies': [],
        'tests_run': result.testsRun, 'failures': len(result.failures), 'errors': len(result.errors),
        'skipped': len(result.skipped), 'financial_trials': 0,
        'test_source_sha256': digest(ROOT / 'agents/codex/test_delta_straddle_strategy.py'),
        'code_sha256': demo['code_sha256'], 'input_sha256': demo['input_sha256'],
        'recorder_sha256': digest(Path(__file__)),
        'random_seed': None, 'synthetic_sessions': len(packet['sessions']),
        'synthetic_market_count': len(strategy.WEIGHTS),
        'source_choices': {'horizons': strategy.HORIZONS, 'decay': strategy.DECAY,
                           'risk_target': strategy.RISK_TARGET, 'band': strategy.BAND},
        'preregistration': 'agents/codex/plans/delta_straddle_4677166_build.md',
        'preregistration_sha256': digest(ROOT / 'agents/codex/plans/delta_straddle_4677166_build.md'),
        'data_gate_sha256': digest(ROOT / 'agents/codex/inputs/delta_straddle_4677166/free_data_gate.md')}
    for name, data in [('test_receipt.json', manifest), ('synthetic_plan.json', demo),
                       ('account_admission.json', strategy.admission())]:
        (OUTPUT / name).write_text(json.dumps(data, indent=2, allow_nan=False) + '\n')
    print(json.dumps({'tests': result.testsRun, 'financial_trials': 0, 'output': str(OUTPUT)}))


if __name__ == '__main__':
    main()
