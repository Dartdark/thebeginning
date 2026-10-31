"""Saved-ledger self-audit only; no new return data or economic definitions."""
from pathlib import Path
import hashlib,json
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'analysis/outputs/codex_scout_fomc_cycle'
def run():
    t=pd.read_csv(OUT/'design_reference_ledger.csv');r=json.loads((OUT/'result.json').read_text())
    c=pd.read_csv(OUT/'coverage.csv');n=pd.read_csv(OUT/'calendar_null.csv')
    assert len(t)==t.date.nunique()==484 and t.event.all()
    assert t.date.between(20180101,20221231).all()
    assert abs(t.gross.sum()-t.commission.sum()-t.slippage.sum()-t.net.sum())<1e-8
    assert abs(t.net.sum()-r['metrics']['total'])<1e-8
    assert abs(sum(x['total'] for x in r['yearly'].values())-t.net.sum())<1e-8
    assert ((1+(n.net_total>=t.net.sum()).sum())/1001)==r['calendar_null_p']
    assert c.loc[c.event,'complete'].all()
    assert c.loc[~c.complete,'date'].tolist()==[20201130]
    a=(ROOT/'analysis/codex_scout_fomc_cycle.py').read_text()
    b=(ROOT/'analysis/codex_scout_fomc_cycle_retry.py').read_text()
    assert a.replace("t.drop(columns='match').to_csv(OUT/'design_reference_ledger.csv',index=False)",
                     "t.to_csv(OUT/'design_reference_ledger.csv',index=False)")==b
    m=json.loads((OUT/'manifest.json').read_text())
    assert hashlib.sha256(b.encode()).hexdigest()==m['code_sha256']
    checks=dict(ledger_accounting='PASS',calendar_null='PASS',design_only='PASS',candidate_coverage='484/484',
                unknown_non_event_dates=[20201130],retry_diff='one output-only line; no financial rule change',
                independent_economic_verification=False,economic_definitions=3,engineering_replay_extra_definitions=0)
    (OUT/'self_audit.json').write_text(json.dumps(checks,indent=2)+'\n');print(json.dumps(checks,indent=2))
if __name__=='__main__':run()
