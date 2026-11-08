"""Archive receipt and printed coefficient interpretation, not an empirical replication."""
from pathlib import Path
import hashlib
import json
import subprocess

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'agents/codex/inputs/nasdaq_fragmentation_1941956'
OUT = ROOT / 'analysis/outputs/codex_nasdaq_fragmentation_1941956'


def main():
    assert subprocess.check_output(['pdftotext', '-layout', str(SOURCE/'paper.pdf'), '-']) == (SOURCE/'paper.txt').read_bytes()
    # Manually transcribed printed Tables 9/10; Table 10 visually inspected.
    years = list(range(2002, 2011))
    spread = [-.40, -.09, -.08, -.11, -.01, .23, -.18, -.20, .06]
    seconds = [-98.78, -48.34, -65.84, -100.21, -136.14, 123.12, 147.26, 167.38, 198.80]
    assert all(x < 0 for x in seconds[:5]) and all(x > 0 for x in seconds[5:])
    files = [SOURCE/name for name in ['paper.pdf', 'paper.txt', 'table10.png', 'table12.png']] + [Path(__file__)]
    result = {
        'title': 'Exchange Entrances, Mergers and the Evolution of Order Flow on NASDAQ 1993-2010',
        'authors': ['Robert H. Battalio', 'Jared F. Egginton', 'Bonnie F. Van Ness', 'Robert A. Van Ness'],
        'source_draft': 'October 5, 2011', 'review_date': '2026-11-07 America/Los_Angeles',
        'source_file_id': 'file_0000000064a881fdaaa917cd47989b95', 'pages': 34,
        'scope': 'Main narrative and key tables reviewed; Tables10/12 visually inspected; chart-only pages29-34 not independently audited; no empirical replication',
        'hashes': {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in files},
        'table9_fragmentation_spread_coefficients': dict(zip(years, spread)),
        'table10_fragmentation_seconds_coefficients': dict(zip(years, seconds)),
        'interpretation': 'Holding controls fixed, negative seconds coefficient means shorter delay; positive means longer delay. Prose speed interpretation is reversed relative to printed units.',
        'table12_reported_2010_cancellation_pct': {'NASD': 82.8, 'NASDAQ': 16.3, 'ARCA': 92.1, 'AMEX': 52.8, 'ISE': 97.0, 'BATS': 40.8},
        'table2_reported_NASDAQ_volume_share_pct': {'1993': 100.0, '2010': 37.0},
        'new_economic_trials': 0, 'strategy_returns_computed': False,
        'verdict': 'EXECUTION_REFERENCE_NO_STANDALONE_STRATEGY',
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT/'source_audit.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps({'source_integrity': 'PASS', 'table10_sign_change': 'CONFIRMED', 'return_trials': 0}))


if __name__ == '__main__':
    main()
