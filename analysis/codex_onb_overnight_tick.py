"""Frozen MC Overnight Tick/VIX re-bench, staged and native-costed.
python analysis/codex_onb_overnight_tick.py design|recent|book
"""
import hashlib
import json
import pickle
import subprocess
import sys
from pathlib import Path
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'analysis/outputs/codex_onb_overnight_tick'
MODE=sys.argv[1] if len(sys.argv)>1 else 'design';sys.argv=[sys.argv[0],str(OUT/'_cache')]
sys.path.insert(0,str(ROOT/'analysis'))
import codex_onb_heavy_night_fade as helpers
import codex_onb_fade_book as book
import overnight_round as overnight
import resampling as rs
import montecarlo as mc

REP=ROOT/'mc_reports/Backtesting Strategy Performance Report _ @NQ - 5 Minutes Overnight Tick VIX.xlsx'


def load(g,recent):
    raw=pd.read_excel(REP,sheet_name='List of Trades',header=2)
    en=raw[raw.Type.astype(str).str.startswith('Entry')].reset_index(drop=True)
    ex=raw[raw.Type.astype(str).str.startswith('Exit')].reset_index(drop=True)
    assert len(en)==len(ex)
    a=pd.DataFrame(dict(entry_ts=pd.to_datetime(en.Date)-pd.Timedelta(minutes=4),
                        exit_ts=pd.to_datetime(ex.Date)-pd.Timedelta(minutes=4),
                        entry=en.Price.to_numpy(float),exit=ex.Price.to_numpy(float),
                        exit_signal=ex.Signal.astype(str)))
    a['date']=a.exit_ts.dt.normalize();a=a[a.date.between('2023-01-01','2026-10-12')] if recent else a[a.date.between('2018-03-01','2022-12-31')]
    rolls=overnight.roll_minutes(g,'NQ');origin=pd.Timestamp(g.ts[0]);out=[];excluded=[]
    for x in a.itertuples():
        i=int((x.entry_ts-origin).total_seconds()/60);j=int((x.exit_ts-origin).total_seconds()/60)
        reason=None
        if x.exit_signal.strip().lower()=='open':reason='open report trade'
        elif i<0 or j>=g.D*1440:reason='outside grid'
        elif not(np.isfinite(g.o.ravel()[i]) and np.isfinite(g.o.ravel()[j])):reason='missing endpoint'
        elif ((rolls>=i)&(rolls<=j)).any():reason='roll switch'
        if reason:
            excluded.append(dict(date=str(x.date.date()),reason=reason));continue
        for variant in ['heavy','delay']:
            entry=x.entry if variant=='heavy' else g.o.ravel()[i+1]
            if not np.isfinite(entry):
                excluded.append(dict(date=str(x.date.date()),reason='missing delayed endpoint'));continue
            gross=(x.exit-entry)*20
            out.append(dict(date=x.date,entry_ts=x.entry_ts+pd.Timedelta(minutes=variant=='delay'),
                            exit_ts=x.exit_ts,entry=entry,exit=x.exit,side=1,kind=2,
                            gross=gross,commission=12.75,slippage=10.,net=gross-22.75,
                            variant=variant,strategy='OT',qty=1.,j0=i%1440,j1=j%1440))
    return pd.DataFrame(out),dict(report_rows_in_period=len(a),exclusions=excluded,
                                 report_sha256=hashlib.sha256(REP.read_bytes()).hexdigest())


def candidate(variant='heavy',size=1):
    t=pd.concat([pd.read_csv(OUT/f'trades_{p}_{variant}.csv',parse_dates=['date','entry_ts','exit_ts']) for p in ['design','recent']],ignore_index=True)
    t['qty']=size;t['net']*=size/10
    return t


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    if MODE=='book':
        book.OUT=OUT;book.LABEL='OT';book.CANDIDATE_KEY='OT';book.candidate=candidate;book.main();return
    if MODE=='recent':assert json.loads((OUT/'gate_design.json').read_text())['pass']
    g=pickle.load(open('C:/TradingVault/scratch_data/g24.pkl','rb'))
    recent=MODE=='recent';t,provenance=load(g,recent)
    dates=pd.DatetimeIndex(g.ts[g.trading]);dates=dates[dates.to_series().between('2023-01-01' if recent else '2018-03-01','2026-10-12' if recent else '2022-12-31').to_numpy()]
    rows=[];randoms={};rng=np.random.default_rng(20261113)
    for variant in ['heavy','delay']:
        sub=t[t.variant==variant].copy();sub.to_csv(OUT/f'trades_{MODE}_{variant}.csv',index=False)
        m=helpers.summary(sub,dates,MODE);m['variant']=variant;rows.append(m)
        actual=sub.net.mean();draws=np.where(rng.random((1000,len(sub)))<.5,sub.gross.to_numpy(),-sub.gross.to_numpy()).mean(1)-22.75
        p=(1+(draws>=actual).sum())/1001
        randoms[variant]=dict(actual_mean=actual,random_mean=draws.mean(),p=p)
        pd.DataFrame(dict(mean_net=draws)).to_csv(OUT/f'placebo_{MODE}_{variant}.csv',index=False)
        sub.groupby(sub.date.dt.year).agg(n=('net','size'),gross=('gross','sum'),net=('net','sum')).to_csv(OUT/f'yearly_{MODE}_{variant}.csv')
        print(MODE,variant,m[['side','trades','avg','t','sharpe','profit_factor']].to_string(index=False),flush=True)
        print('random side',randoms[variant],flush=True)
        if variant=='heavy':
            primary=m.iloc[0];daily=sub.groupby('date').net.sum().reindex(dates,fill_value=0)
            if recent:
                rs.bootstrap(daily,n=2000,block=20,seed=20261113,capital=150000).to_csv(OUT/'bootstrap_recent.csv')
                (OUT/'permutation_recent.json').write_text(json.dumps(rs.permutation(daily,n=2000,seed=20261113),default=float,indent=2))
                for size in [1,2]:
                    result=dict(trades=mc.trade_mc(sub.net*size/10,n=2000,seed=20261113),
                                daily=mc.daily_mc(daily*size/10,n=2000,block=20,seed=20261113))
                    (OUT/f'mc_recent_{size}mnq.json').write_text(json.dumps(result,indent=2,default=float))
    pd.concat(rows,ignore_index=True).to_csv(OUT/f'metrics_{MODE}.csv',index=False)
    passed=bool(primary.avg>0 and primary.t>=2 and randoms['heavy']['p']<.05)
    manifest=dict(**{'pass':passed},code=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
                  net_mean=primary.avg,t=primary.t,random_sides=randoms,provenance=provenance)
    (OUT/f'gate_{MODE}.json').write_text(json.dumps(manifest,indent=2))
    print('GATE',MODE,'PASS' if passed else 'FAIL',flush=True)


if __name__=='__main__':main()
