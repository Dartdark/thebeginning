"""Source receipt and elementary moment illustration; no market-data reads or return tests."""
from pathlib import Path
import hashlib
import json
import subprocess

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'agents/codex/inputs/infinite_factor_7596842'
OUT = ROOT / 'analysis/outputs/codex_infinite_factor_7596842'


def main():
    pdf = SOURCE / 'paper.pdf'
    text = subprocess.check_output(['pdftotext', '-layout', str(pdf), '-'])
    assert text == (SOURCE / 'paper.txt').read_bytes()
    info = subprocess.check_output(['pdfinfo', str(pdf)], text=True)
    pages = int(next(x.split(':', 1)[1] for x in info.splitlines() if x.startswith('Pages:')))
    # A scalar zero-mean unit-variance shock loads on (1,0) in state A and (0,1)
    # in state B. Equiprobable states: conditional ranks1, unconditional rank2.
    # This finite example is our illustration, not a replication of the infinite-rank theorem.
    conditional_a = [[1.0, 0.0], [0.0, 0.0]]
    conditional_b = [[0.0, 0.0], [0.0, 1.0]]
    pooled = [[(conditional_a[i][j]+conditional_b[i][j])/2 for j in range(2)] for i in range(2)]
    det = lambda x: x[0][0]*x[1][1]-x[0][1]*x[1][0]
    assert det(conditional_a) == det(conditional_b) == 0
    assert det(pooled) == 0.25
    record = dict(title='Infinite Factor Structure in Conditional Asset Pricing',
                  authors=['Mikhail Chernov','Bryan Kelly','Semyon Malamud','Johannes Schwab'],
                  source_version='October11,2026', review_date='2026-11-07', pages=pages,
                  source_permission='owned_upload', source_file_id='file_000000001e8881f69209dbd822c4e29e',
                  hashes={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
                          for p in [pdf,SOURCE/'paper.txt',Path(__file__)]},
                  scope='Focused source review: introduction, setup/assumptions, Theorem1, conditional-stock setup, Section5 illustrations/pricing/covariance and conclusion; no independent audit of all appendix proofs.',
                  illustration=dict(conditional_a=conditional_a,conditional_b=conditional_b,pooled=pooled,
                                    zero_means=True,pooled_rank=2,scope='Finite algebra only; no return simulation, no profitable strategy, no proof certification'),
                  new_economic_trials=0, strategy_returns_computed=False,
                  verdict='METHOD_REFERENCE_NO_STRATEGY_ADMITTED')
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/'source_audit.json').write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps(dict(pages=pages,finite_rank_illustration='PASS',return_trials=0)))


if __name__ == '__main__':
    main()
