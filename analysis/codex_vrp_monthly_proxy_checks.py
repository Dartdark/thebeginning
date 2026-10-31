"""Independent raw-open/ledger checks; no new trading rule or return variant."""
from pathlib import Path
import hashlib
import json
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'analysis/outputs/codex_vrp_monthly_proxy_20261029'
DEST=OUT/'primary_endpoints'


def main():
    events=pd.read_csv(DEST/'monthly_ledger.csv')
    features=pd.read_csv(DEST/'features.csv',index_col='month')
    manifest=json.loads((DEST/'manifest.json').read_text())
    controls=json.loads((DEST/'endpoint_controls.json').read_text())
    metrics=pd.read_csv(DEST/'endpoint_metrics.csv')
    raw={}
    for year in range(2018,2023):
        x=pd.read_csv(ROOT/f'data/ES_1min_{year}.csv')
        opens=x[x.time==831]
        assert not opens.duplicated(['date','time']).any()
        raw.update({str(pd.to_datetime(str(r.date)).date()):r.open for r in opens.itertuples()})
    checks={}
    for e in events.itertuples():
        assert np.isclose(raw[e.entry_date],e.entry) and np.isclose(raw[e.exit_date],e.exit)
        assert np.isclose((raw[e.exit_date]-raw[e.entry_date])*5,e.gross)
        assert np.isclose(e.gross-3.74,e.net)
        assert np.isclose(e.gross-11.24,e.stress_net)
        assert bool(e.P)==bool(features.loc[str(pd.Period(e.month)-1),'vrp']>0)
        assert pd.Period(e.month).month not in (3,6,9,12)
        assert pd.Timestamp(e.entry_date).year<=2022 and pd.Timestamp(e.exit_date).year<=2022
    checks['raw_open_and_feature_checks']=len(events)
    checks['rt_cost_and_stress_checks']=len(events)
    p=events.loc[events.P,'net'];removed=events.loc[~events.P,'net']
    assert np.isclose(p.sum()+removed.sum(),events.net.sum())
    assert np.isclose(p.sum(),controls['candidate_net'])
    assert np.isclose(events.net.sum(),controls['base_net'])
    assert controls['candidate_net']<controls['base_net'] and controls['candidate_monthly_t']<2
    assert controls['removed_avg']>0
    checks['aggregate_reconciliation']=True
    for name in ['P','B']:
        totals=metrics[(metrics.name==name)&(metrics.side=='all')]
        assert np.isclose(totals.loc[totals.year!='all','net'].sum(),float(totals.loc[totals.year=='all','net'].iloc[0]))
        assert (metrics[(metrics.name==name)&(metrics.side=='short')].trades==0).all()
    checks['year_and_side_rows']=True
    assert not controls['validation_authorized'] and not controls['daily_mark_gate_passed']
    assert controls['joint_profit_daily_dd_dominance'] is None
    assert not (OUT/'validation').exists() and not (OUT/'primary_validation').exists()
    assert manifest['return_ledgers_evaluated']==2
    checks['stop_gate_and_no_validation']=True
    for path,info in manifest['files'].items():
        assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==info['sha256']
    checks['input_hashes_match']=True
    result=dict(passed=True,checks=checks,new_economic_trials=0,
                note='Independent raw input/ledger reconciliation, not a promotion checker or native MES parity')
    (OUT/'verification.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result))


if __name__=='__main__':main()
