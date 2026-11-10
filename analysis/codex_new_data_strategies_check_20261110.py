"""Check the saved new-data design batch; no new strategy returns."""
from pathlib import Path
import hashlib
import json
import numpy as np
import pandas as pd
import codex_new_data_strategies_20261110 as A


def main():
    p=A.OUT;m=json.loads((p/'manifest.json').read_text())
    assert hashlib.sha256(Path(A.__file__).read_bytes()).hexdigest()==m['code_sha256']
    assert A.sha(A.ROOT/A.PLAN)==m['plan_sha256']
    f=pd.read_csv(p/'design_feature_clocks.csv',parse_dates=['date','source_date','fear_source_date'])
    available=pd.to_datetime(f.available_at,utc=True);decision=pd.to_datetime(f.decision_at,utc=True)
    known=f.fund_state.notna()
    assert (available[known]<=decision[known]).all()
    assert (f.source_date[known]<f.date[known]).all()
    fear=f.fear_state.notna()
    assert (f.fear_source_date[fear]<f.date[fear]).all()
    assert (f.date<'2023-01-01').all()
    table=pd.read_csv(p/'design_metrics.csv')
    ledgers={}
    for name,(_,side,j0,jend,_) in A.MODELS.items():
        t=pd.read_csv(p/(name+'_design_trades.csv'),parse_dates=['date'])
        ledgers[name]=t
        assert not t.date.duplicated().any()
        assert t.date.between('2018-01-01','2022-12-31').all()
        assert t.side.eq(side).all() and t.j0.eq(j0).all() and t.j1.le(jend).all()
        assert np.allclose(t.gross,(t.exit-t.entry)*t.side*2)
        assert np.allclose(t.net,t.gross-1.25-.5*(1+t.kind.ne(1)))
        assert np.allclose(t.stress_net,t.gross-2.50-1.*(1+t.kind.ne(1)))
        row=table[(table.model==name)&(table.period=='design')&(table.side=='all')].iloc[0]
        assert len(t)==row.trades and np.isclose(t.net.sum(),row.net)
        annual=table[(table.model==name)&(table.period!='design')&(table.side=='all')]
        assert np.isclose(annual.net.sum(),row.net)
    gates=json.loads((p/'design_gate.json').read_text())
    for name,control in A.CANDIDATES.items():
        t,c=ledgers[name],ledgers[control]
        paired=t.merge(c,on='date',suffixes=('_candidate','_control'),validate='one_to_one')
        assert len(paired)==len(t) and np.allclose(paired.net_candidate,paired.net_control)
        row=next(x for x in gates['candidates'] if x['candidate']==name)
        removed=c[~c.date.isin(t.date)]
        assert np.isclose(removed.net.sum(),row['removed_net'])
        assert np.isclose(c.net.sum(),t.net.sum()+removed.net.sum())
        assert row['cheap_pass']==all(row['tests'].values())
    assert not gates['survivors'] and not gates['alternative_2023_outcomes_run']
    assert gates['conditional_null_definitions']==0
    screen=pd.read_csv(p/'reference_screen_design.csv')
    assert len(screen)==44 and screen.piece.nunique()==22
    receipt={'passed':True,'scope':'saved-output accounting, chronology and gate checks; not independent alpha verification',
             'costs_and_trade_gross':True,'annual_totals':True,'candidate_control_subset_identity':True,
             'unknown_state_and_publication_fixtures':A.clock_checks(),'source_clock_order':True,
             'all_new_candidates_design_only':True,'failed_gate_stops_validation':True}
    (p/'saved_output_checks.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(receipt)


if __name__=='__main__':main()
