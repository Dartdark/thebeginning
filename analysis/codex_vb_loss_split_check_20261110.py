"""Verify saved split-stop ledgers/results without generating new return variants."""
from pathlib import Path
import hashlib
import json
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
P=ROOT/'analysis/outputs/codex_vb_loss_split_20261110'


def main():
    manifest=json.loads((P/'manifest.json').read_text())
    assert hashlib.sha256((ROOT/'analysis/codex_vb_loss_split_20261110.py').read_bytes()).hexdigest()==manifest['code_sha256']
    assert hashlib.sha256((ROOT/'agents/codex/plans/vb_loss_split_20261110.md').read_bytes()).hexdigest()==manifest['plan_sha256']
    a=pd.read_csv(P/'design_full_leg.csv',parse_dates=['date'])
    b=pd.read_csv(P/'design_shallow_leg.csv',parse_dates=['date'])
    assert (a.date.dt.year<=2022).all() and (b.date.dt.year<=2022).all()
    assert np.array_equal(a[['day','j0']],b[['day','j0']]) and (b.j1<=a.j1).all()
    for z in (a,b):
        assert np.allclose(z.native_net,z.native_gross-z.commission-z.slippage)
        assert np.allclose(z.native_net,(z.exit-z.entry)*2-1.25)
    r=pd.read_csv(P/'design_vb_metrics.csv')
    whole=r[r.year=='design'].set_index('model')
    expected={'BASE':15*a.native_net,'SPLIT':7*b.native_net+8*a.native_net,
              'REDUCED':11*a.native_net,'EMPTY':0*a.native_net}
    for name,x in expected.items():
        assert np.isclose(x.sum(),whole.loc[name,'net'])
        assert np.isclose(r[(r.model==name)&(r.year!='design')].net.sum(),x.sum())
    f=pd.read_csv(P/'design_trim_fate.csv')
    assert np.isclose(f.delta_normal_15mnq.sum(),expected['SPLIT'].sum()-expected['BASE'].sum())
    z=pd.read_csv(P/'design_start_outcomes.csv',parse_dates=['start'])
    assert (z.start+pd.Timedelta(days=30)<=pd.Timestamp('2023-01-01')).all()
    s=pd.read_csv(P/'design_accounts.csv')
    for row in s.itertuples():
        q=z[(z.model==row.model)&(z.protocol==row.protocol)]
        assert len(q)==1270 and np.isclose(q.outcome.eq(1).mean(),row.passed)
        assert np.isclose(row.passed+row.failed+row.expired,1)
    g=json.loads((P/'design_gate.json').read_text())
    assert not g['survives'] and not g['alternative_2023_outcomes_run']
    checks={'status':'passed','scope':'saved-ledger arithmetic; not independent execution verification',
            'source_and_plan_hashes':True,'entry_identity_and_exit_order':True,
            'native_costs_and_trade_totals':True,'annual_totals':True,'trim_fate_reconciles':True,
            'design_only_30_day_windows':True,'account_counts_and_rates':True,'failed_gate_stops_validation':True}
    (P/'saved_output_checks.json').write_text(json.dumps(checks,indent=2)+'\n')
    print(checks)


if __name__=='__main__':
    main()
