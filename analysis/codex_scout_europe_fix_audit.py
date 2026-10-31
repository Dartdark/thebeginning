"""Self-audit the saved single-definition ledger; opens no source return data.

Reproduces accounting/cost stress only. Not independent economic verification.
"""
import hashlib
import json
import subprocess
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'analysis/outputs/codex_scout_europe_fix'

def audit():
    t=pd.read_csv(OUT/'design_reference_ledger.csv')
    c=pd.read_csv(OUT/'endpoint_census.csv')
    r=json.loads((OUT/'result.json').read_text())
    m=json.loads((OUT/'manifest.json').read_text())
    assert len(t)==t.date.nunique()==1288
    assert t.date.between(20180101,20221231).all() and t.side.eq(-1).all()
    assert c.complete.sum()==len(t) and c.held_minutes.eq(360).all()
    assert abs(t.gross.sum()-t.commission.sum()-t.slippage.sum()-t.net.sum())<1e-7
    assert abs(t.net.sum()-r['metrics']['net_total'])<1e-7
    assert abs(sum(v['net_total'] for v in r['yearly'].values())-t.net.sum())<1e-7
    proposal=json.loads(subprocess.check_output(['git','show',m['claim']+
        ':agents/codex/research/scout/proposals/europe_fix.json'],cwd=ROOT,text=True))
    for p,h in proposal['artifact_sha256'].items():
        frozen=subprocess.check_output(['git','show',m['claim']+':'+p],cwd=ROOT)
        assert hashlib.sha256(frozen).hexdigest()==h
    assert hashlib.sha256((ROOT/'analysis/codex_scout_europe_fix.py').read_bytes()).hexdigest()==m['code_sha256']
    import codex_scout_europe_fix as screen
    for day,hour in [('2018-01-10',1),('2018-07-10',1),('2018-03-20',2),('2018-10-30',2)]:
        assert screen.clock(day,8).hour==hour and screen.clock(day,14).hour==hour+6
    checks=dict(accounting='PASS',clock_fixtures='PASS',frozen_artifact_commit_hashes='PASS',
        design_only=True,unique_ledger_dates=len(t),unknown_dates=int((~c.complete).sum()),
        unknown_returns_imputed=False,stress_net=float(t.gross.sum()-32.25*len(t)),
        stress_cost_per_round_trip=32.25,breakeven_total_cost=float(t.gross.mean()),
        gross_ticks=float(t.gross.mean()/6.25),cost_ticks=19.75/6.25,
        complete_fraction=len(t)/len(c),independent_verification=False)
    (OUT/'engineering_checks.json').write_text(json.dumps(checks,indent=2)+'\n')
    print(json.dumps(checks,indent=2))

if __name__=='__main__': audit()
