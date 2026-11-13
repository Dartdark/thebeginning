"""Independent result arithmetic and saved-run consistency for ONB buffer tests."""
import hashlib
import json
import pickle
import sys
from pathlib import Path
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'analysis'))
import grid24

def main():
    g=pickle.load(open('C:/TradingVault/scratch_data/g24.pkl','rb'))
    base=pd.read_csv(ROOT/'analysis/outputs/codex_book_joint_losses/daily.csv',index_col='date',parse_dates=True)
    findings={};base_outcomes={}
    for family in ['codex_onb_heavy_night_fade','codex_onb_overnight_tick']:
        p=ROOT/'analysis/outputs'/family;alltrades=[]
        for period in ['design','recent']:
            t=pd.read_csv(p/f'trades_{period}_heavy.csv',parse_dates=['date'])
            assert np.allclose(t.gross-22.75,t.net)
            assert np.allclose((t.exit-t.entry)*t.side*20,t.gross)
            metrics=pd.read_csv(p/f'metrics_{period}.csv')
            m=metrics[(metrics.side=='ALL')&(metrics.variant=='heavy')].iloc[0]
            assert len(t)==m.trades and np.isclose(t.net.sum(),m.net)
            assert np.isclose(t.net.mean()/t.net.std()*np.sqrt(len(t)),m.t)
            alltrades.append(t)
        t=pd.concat(alltrades)
        c=pd.read_csv(p/'conditional_offsets.csv')
        for period,mask in [('2018-22',base.index.year<=2022),('2023+',base.index.year>=2023)]:
            ds=base.index[mask];onb_loss=ds[base.loc[ds,'ONB30']<0]
            expected=t[t.date.isin(onb_loss)].net.sum()/10
            actual=c[(c.period==period)&(c.state=='ONB loss')].candidate_total.iloc[0]
            assert np.isclose(expected,actual)
        table=pd.read_csv(p/'book_comparison.csv')
        for model in ['canonical','common_price','close_only']:
            for scenario in ['fresh','stress']:
                outcomes=pd.read_csv(p/f'outcomes_{model}_{scenario}.csv',parse_dates=['date'])
                k=(model,scenario)
                if k in base_outcomes:assert outcomes.base.equals(base_outcomes[k])
                else:base_outcomes[k]=outcomes.base
                for row in table[(table.model==model)&(table.scenario==scenario)].itertuples():
                    sel=(outcomes.date.dt.year<=2022) if row.period=='2018-22' else (outcomes.date.dt.year>=2023)
                    sel &= (outcomes.date<='2026-09-01')&(outcomes.base!='invalid')
                    assert int(sel.sum())==row.starts
                    assert np.isclose((outcomes.loc[sel,row.case]=='pass').mean(),row.pass_rate)
                    assert np.isclose(row.pass_rate+row.fail_rate+row.time_rate,1)
                    delta=(outcomes.loc[sel,row.case]=='pass').astype(int)-(outcomes.loc[sel,row.reference]=='pass').astype(int)
                    assert np.isclose(delta.mean(),row.pass_delta)
        findings[family]=dict(gross_cost_bridge=True,standalone_metrics=True,ONB_loss_attribution=True,
                              paired_outcome_tables=True,identical_base_between_candidates=True)
        if family=='codex_onb_overnight_tick':
            t=pd.concat([pd.read_csv(p/f'trades_{per}_heavy.csv',parse_dates=['entry_ts','exit_ts']) for per in ['design','recent']])
            origin=pd.Timestamp(g.ts[0]);i=((t.entry_ts-origin).dt.total_seconds()/60).astype(int)
            j=((t.exit_ts-origin).dt.total_seconds()/60).astype(int)
            assert np.allclose(g.o.ravel()[i],t.entry) and np.allclose(g.o.ravel()[j],t.exit)
            findings[family]['all_549_MC_fill_prices_match_minute_opens']=True
        (p/'validation.json').write_text(json.dumps(findings[family],indent=2))
    print(json.dumps(findings,indent=2))

if __name__=='__main__':main()
