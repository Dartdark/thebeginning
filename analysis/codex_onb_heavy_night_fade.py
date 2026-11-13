"""Frozen heavy-night T fade: staged standalone tests before current-book replay.
python analysis/codex_onb_heavy_night_fade.py design|recent
"""
import hashlib
import json
import pickle
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'analysis/outputs/codex_onb_heavy_night_fade'
MODE=sys.argv[1] if len(sys.argv)>1 else 'design'
sys.argv=[sys.argv[0],str(OUT/'_cache')]
sys.path.insert(0,str(ROOT/'analysis'))
import t_oneside_test as source
import metrics as mt
import resampling as rs
import montecarlo as mc

SEED=20261113
FEE_NQ=12.75 # 1.275 per MNQ, plus .5 per fill micro slippage
GRID=Path('C:/TradingVault/scratch_data/g24.pkl')


def code():return subprocess.check_output(['git','rev-parse','HEAD'],text=True,cwd=ROOT).strip()


def simulate(g,events,variant='heavy',flip=False):
    out=[]
    for x in events.itertuples():
        if variant!='all' and x.ratio<=1.4:continue
        side=-int(np.sign(x.ret))
        if flip:side=-side
        if not side:continue
        j0=511 if variant=='delay' else 510
        entry=g.o[x.r,j0];exit_=g.o[x.r,525]
        if not np.isfinite(entry) or not np.isfinite(exit_):continue
        if not np.isfinite(g.c[x.r,j0:525]).all():continue
        stop=entry-side*.4*x.atr
        j1=524;kind=2;px=exit_
        for j in range(j0,525):
            if (side>0 and g.l[x.r,j]<=stop) or (side<0 and g.h[x.r,j]>=stop):
                px=min(g.o[x.r,j],stop) if side>0 else max(g.o[x.r,j],stop)
                j1=j;kind=0;break
        gross=(px-entry)*side*20
        out.append(dict(date=x.date,day=x.r,j0=j0,j1=j1,side=side,entry=entry,exit=px,
                        kind=kind,ratio=x.ratio,atr=x.atr,gross=gross,commission=FEE_NQ,
                        slippage=10.,net=gross-FEE_NQ-10.,variant=variant))
    return pd.DataFrame(out)


def summary(t,dates,period):
    rows=[]
    for side,sub in [('ALL',t),('LONG',t[t.side>0]),('SHORT',t[t.side<0])]:
        daily=sub.groupby('date').net.sum().reindex(dates,fill_value=0)
        r=mt.perf(daily,sub.net,capital=150000)
        r.update(period=period,side=side,gross=sub.gross.sum(),commission=sub.commission.sum(),
                 slippage=sub.slippage.sum(),net=sub.net.sum(),
                 t=sub.net.mean()/sub.net.std()*np.sqrt(len(sub)) if len(sub)>1 else np.nan)
        rows.append(r)
    return pd.DataFrame(rows)


def placebo(g,events,t,variant):
    opposite=simulate(g,events,variant,flip=True).set_index('date')
    a=t.set_index('date');common=a.index.intersection(opposite.index)
    assert len(common)==len(t)
    x=a.loc[common,'net'].to_numpy();y=opposite.loc[common,'net'].to_numpy()
    rng=np.random.default_rng(SEED)
    draws=np.where(rng.random((1000,len(x)))<.5,x[None,:],y[None,:]).mean(1)
    p=(1+int((draws>=x.mean()).sum()))/(len(draws)+1)
    return dict(actual_mean=x.mean(),random_mean=draws.mean(),p=p),draws


def parity(t):
    p=ROOT/'mc_reports/Backtesting Strategy Performance Report _ @NQ - 1 Minute T_ONESIDE v2.xlsx'
    raw=pd.read_excel(p,sheet_name='List of Trades',header=2)
    en=raw[raw.Type.astype(str).str.startswith('Entry')].reset_index(drop=True)
    ex=raw[raw.Type.astype(str).str.startswith('Exit')].reset_index(drop=True)
    print('MC entry signal labels',en.Signal.value_counts().to_dict(),flush=True)
    # Actual export names the opening fade OFlg/OFsh, not T.
    sel=en.Signal.astype(str).isin(['OFlg','OFsh'])
    assert sel.any(), 'unrecognized MC fade labels; cannot assert parity'
    en,en_ex=en[sel].copy(),ex[sel].copy()
    en['date']=pd.to_datetime(en.Date).dt.normalize()
    en['side']=np.where(en.Type.str.contains('Long'),1,-1)
    en['exit']=en_ex.Price.to_numpy()
    en=en[en.date.between('2023-01-01','2026-10-12')]
    m=t.merge(en[['date','side','Price','exit']],on=['date','side'],suffixes=('','_mc'))
    return dict(source=str(p.relative_to(ROOT)),fade_mc_count=len(en),matched=len(m),
                candidate_count=len(t),same_entry=int(np.isclose(m.entry,m.Price).sum()),
                same_exit=int(np.isclose(m.exit,m.exit_mc).sum()))


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    if MODE=='recent':
        old=json.loads((OUT/'gate_design.json').read_text())
        assert old['pass'],'design gate failed; recent stays unopened'
    g=pickle.load(open(GRID,'rb'))
    events=source.days(g)
    events=events[events.valid&(events.med>0)&events.atr.notna()]
    recent=MODE=='recent'
    events=events[(events.date>='2023-01-01')&(events.date<='2026-10-12')] if recent else events[(events.date>='2018-03-01')&(events.date<='2022-12-31')]
    dates=pd.DatetimeIndex(g.ts[g.trading]);dates=dates[(dates>=(events.date.min()))&(dates<=('2026-10-12' if recent else '2022-12-31'))]
    allrows=[];results={}
    for variant in ['heavy','delay','all']:
        t=simulate(g,events,variant)
        t.to_csv(OUT/f'trades_{MODE}_{variant}.csv',index=False)
        m=summary(t,dates,MODE);m['variant']=variant;allrows.append(m)
        pl,draws=placebo(g,events,t,variant)
        pd.DataFrame({'mean_net':draws}).to_csv(OUT/f'placebo_{MODE}_{variant}.csv',index=False)
        results[variant]=pl
        print('\n',MODE,variant,m[['side','trades','avg','t','gross','net','sharpe','profit_factor']].to_string(index=False),flush=True)
        print('random-side placebo',pl,flush=True)
        t.groupby(t.date.dt.year).agg(n=('net','size'),gross=('gross','sum'),net=('net','sum')).to_csv(OUT/f'yearly_{MODE}_{variant}.csv')
        if variant=='heavy':
            primary=m.iloc[0]
            daily=t.groupby('date').net.sum().reindex(dates,fill_value=0)
            # Gross sum - net sum = exact bridge (no double-counted ticks).
            assert np.isclose(t.gross.sum()-t.commission.sum()-t.slippage.sum(),t.net.sum())
            if recent:
                rs.bootstrap(daily,n=2000,block=20,seed=SEED,capital=150000).to_csv(OUT/'bootstrap_recent.csv')
                (OUT/'permutation_recent.json').write_text(json.dumps(rs.permutation(daily,n=2000,seed=SEED),indent=2,default=float))
                for size in [1,2]:
                    val=dict(trades=mc.trade_mc(t.net*size/10,n=2000,seed=SEED),
                             daily=mc.daily_mc(daily*size/10,n=2000,block=20,seed=SEED))
                    (OUT/f'mc_recent_{size}mnq.json').write_text(json.dumps(val,indent=2,default=float))
                (OUT/'mc_parity.json').write_text(json.dumps(parity(t),indent=2))
    metrics=pd.concat(allrows,ignore_index=True);metrics.to_csv(OUT/f'metrics_{MODE}.csv',index=False)
    p=results['heavy']['p'];passed=bool(primary.avg>0 and primary.t>=2 and p<.05)
    gate=dict(pass_=passed,**{'pass':passed},period=MODE,net_mean=float(primary.avg),t=float(primary.t),
              placebo=results,code=code(),events=len(events),heavy_events=int((events.ratio>1.4).sum()),
              trades=int(primary.trades),excluded_heavy_events=int((events.ratio>1.4).sum())-int(primary.trades),
              grid_sha256=hashlib.sha256(GRID.read_bytes()).hexdigest(),
              source_sha256=hashlib.sha256((ROOT/'analysis/t_oneside_test.py').read_bytes()).hexdigest(),
              versions=dict(numpy=np.__version__,pandas=pd.__version__))
    (OUT/f'gate_{MODE}.json').write_text(json.dumps(gate,indent=2))
    print('GATE',MODE,'PASS' if passed else 'FAIL',flush=True)


if __name__=='__main__':main()
