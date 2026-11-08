"""Frozen weekly NQ adaptation design screen. No later data is read by this entry point."""
from pathlib import Path
import hashlib
import json
import math
import subprocess

import numpy as np
import pandas as pd
import metrics as M
from resampling import max_dd

ROOT=Path(__file__).resolve().parents[1]
SOURCE=Path('/workspace/thebeginning/data')
OUT=ROOT/'analysis/outputs/codex_weekly_nq_adapt_20261108'
PLAN='agents/codex/plans/weekly_nq_adapt_20261108.md'
CODE='analysis/codex_weekly_nq_adapt_20261108.py'


def wilder_rsi(s,n=2):
    delta=s.diff().to_numpy(); result=np.full(len(s),np.nan)
    if len(s)<=n:return pd.Series(result,index=s.index)
    gain=np.maximum(delta[1:n+1],0).mean(); loss=np.maximum(-delta[1:n+1],0).mean()
    for i in range(n,len(s)):
        if i>n:
            gain=(gain*(n-1)+max(delta[i],0))/n
            loss=(loss*(n-1)+max(-delta[i],0))/n
        result[i]=50 if gain==loss==0 else 100 if loss==0 else 100-100/(1+gain/loss)
    return pd.Series(result,index=s.index)


def quarantine(friday):
    days=pd.date_range(friday-pd.Timedelta(days=4),friday)
    return any(d.month in (3,6,9,12) and 5<=d.day<=16 for d in days)


def read_owned(name, manifest):
    p=SOURCE/name; raw=p.read_bytes()
    expected=subprocess.check_output(['git','rev-parse','HEAD:data/'+name],cwd=ROOT,text=True).strip()
    actual=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
    if actual!=expected:raise RuntimeError('owned input differs from current branch: '+name)
    manifest[name]={'git_blob':actual,'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw)}
    return pd.read_csv(p)


def prepare():
    manifest={}; pieces=[]
    for year in range(2017,2023):
        x=read_owned(f'NQ_1min_{year}.csv',manifest)
        if x.duplicated(['date','time']).any():raise RuntimeError('duplicate minute bars')
        x=x[(x.time>=800)&(x.time<=1515)]
        x['session']=pd.to_datetime(x.date.astype(str),format='%Y%m%d')
        for d,g in x.groupby('session',sort=True):
            if d.dayofweek>=5:continue
            g=g.sort_values('time'); en=g[g.time>=801].head(1)
            if len(en)!=1:raise RuntimeError('no executable observed bar: '+str(d))
            pieces.append({'date':d,'open':float(en.open.iloc[0]),'close':float(g.close.iloc[-1]),
                           'execution_bar':int(en.time.iloc[0]),'last_bar':int(g.time.iloc[-1]),'bars':len(g)})
    daily=pd.DataFrame(pieces).set_index('date').sort_index()
    if daily.index.duplicated().any():raise RuntimeError('duplicate sessions')
    daily['week']=daily.index+pd.to_timedelta(4-daily.index.dayofweek,unit='D')
    weekly=daily.groupby('week').agg(close=('close','last'),last_session=('close',lambda s:s.index[-1]))
    v=read_owned('VIX_daily.csv',manifest)
    v['date']=pd.to_datetime(v.DATE);v=v.set_index('date').sort_index()
    v=v.loc[:'2022-12-30']
    for w in weekly.index:
        available=v[v.index<=w]
        if len(available):
            dt=available.index[-1]
            weekly.loc[w,'vix_date']=dt
            weekly.loc[w,'vix']=float(available.CLOSE.iloc[-1]) if (w-dt).days<=7 else np.nan
    if not np.isfinite(daily[['open','close']]).all().all():raise RuntimeError('nonfinite prices')
    for n in (5,25):weekly[f'ema{n}']=weekly.close.ewm(span=n,adjust=False,min_periods=n).mean()
    weekly['ema_up']=(weekly.ema5>weekly.ema5.shift())&(weekly.ema25>weekly.ema25.shift())
    weekly['ratio']=weekly.close/weekly.vix
    for n in (12,5):weekly[f'ratio_ema{n}']=weekly.ratio.ewm(span=n,adjust=False,min_periods=n).mean()
    weekly['rsi2']=wilder_rsi(weekly.close)
    weekly['base_entry']=(weekly.close>weekly.ema5)&weekly.ema_up
    weekly['full_entry']=weekly.base_entry&(weekly.ratio>weekly.ratio_ema12)&(weekly.rsi2<75)&(weekly.vix<40)
    weekly['quarantine']=list(map(quarantine,weekly.index))
    return daily,weekly,manifest


def run_rule(daily,weekly,rule):
    d=daily.loc['2018-01-01':'2022-12-30']; position=False; prior_week=None
    entry=entry_date=last_mark=None; trades=[]; ledger=[]
    for date,r in d.iterrows():
        gross=commission=slippage=0.; exits=False; week=r.week
        if week!=prior_week:
            prev=week-pd.Timedelta(days=7)
            f=weekly.loc[prev] if prev in weekly.index else None
            eligible=f is not None and pd.notna(f.ema25)
            valid_vix=eligible and pd.notna(f.vix) and pd.notna(f.ratio_ema12)
            unsafe=quarantine(week)
            if position:
                signal_exit=(not valid_vix or f.ratio<f.ratio_ema5) if rule=='full' else (not eligible or f.close<f.ema5)
                risk_exit=eligible and f.close<.95*entry
                if unsafe or signal_exit or risk_exit:
                    exit_px=float(r.open); gross+=(exit_px-last_mark)*2
                    commission+=.625;slippage+=.5
                    trades.append({'entry_date':entry_date,'exit_date':date,'entry':entry,'exit':exit_px,
                                   'side':1,'gross':(exit_px-entry)*2,'commission':1.25,'slippage':1.,
                                   'net':(exit_px-entry)*2-2.25,
                                   'reason':'roll_quarantine' if unsafe else 'weekly_5pct' if risk_exit else 'signal'})
                    position=False;exits=True
            if not position and not exits and not unsafe and eligible and (valid_vix if rule=='full' else True):
                if bool(f.full_entry if rule=='full' else f.base_entry):
                    position=True;entry=float(r.open);entry_date=date;last_mark=entry
                    commission+=.625;slippage+=.5
        if position:
            gross+=(float(r.close)-last_mark)*2;last_mark=float(r.close)
            if date==d.index[-1]:
                commission+=.625;slippage+=.5
                trades.append({'entry_date':entry_date,'exit_date':date,'entry':entry,'exit':last_mark,'side':1,
                               'gross':(last_mark-entry)*2,'commission':1.25,'slippage':1.,
                               'net':(last_mark-entry)*2-2.25,'reason':'design_end'})
                position=False
        ledger.append({'date':date,'gross':gross,'commission':commission,'slippage':slippage,
                       'net':gross-commission-slippage,'position_at_close':int(position)})
        prior_week=week
    t=pd.DataFrame(trades,columns=['entry_date','exit_date','entry','exit','side','gross','commission','slippage','net','reason'])
    l=pd.DataFrame(ledger).set_index('date')
    for col in ('gross','commission','slippage','net'):
        if abs(l[col].sum()-t[col].sum())>.005:raise RuntimeError('cash ledger mismatch: '+col)
    # Fixed two-tick-per-leg stress, with unchanged orders and separate costs.
    l['stress_net']=l.net-l.slippage
    l['reference_nq_net']=l.gross*10-l.commission*(7.25/1.25)-l.slippage*10
    t['stress_net']=t.net-t.slippage
    t['reference_nq_net']=t.gross*10-17.25
    return t,l


def stats(t,l):
    s=M.perf(l.net,t.net,capital=50000)
    s['max_dd']=max_dd(l.net)
    s['calmar']=s['annual']/s['max_dd'] if s['max_dd'] else None
    s['total']=float(l.net.sum());s['gross']=float(l.gross.sum())
    s['commission']=float(l.commission.sum());s['slippage']=float(l.slippage.sum())
    s['stress_total']=float(l.stress_net.sum());s['reference_nq_avg']=float(t.reference_nq_net.mean())
    s['t_trade']=float(t.net.mean()/t.net.std(ddof=1)*np.sqrt(len(t))) if len(t)>1 and t.net.std()>0 else None
    s['by_year']={str(y):float(x) for y,x in l.net.groupby(l.index.year).sum().items()}
    s['short_trades']=0
    return s


def main():
    for name in (PLAN,CODE):
        if subprocess.check_output(['git','show','HEAD:'+name],cwd=ROOT)!=(ROOT/name).read_bytes():
            raise RuntimeError('commit exact plan/script before returns')
    # Formula and causality assertions before real outcomes.
    a=pd.Series([100.,101,102,101,103,104])
    assert wilder_rsi(a).iloc[:4].equals(wilder_rsi(a.iloc[:4]))
    assert wilder_rsi(pd.Series([100.,101,102])).iloc[-1]==100
    assert quarantine(pd.Timestamp('2020-03-13')) and not quarantine(pd.Timestamp('2020-02-14'))
    d,w,manifest=prepare();OUT.mkdir(parents=True,exist_ok=True)
    d.to_csv(OUT/'daily_inputs.csv');w.to_csv(OUT/'weekly_features.csv')
    results={}
    for name in ('full','baseline'):
        t,l=run_rule(d,w,name);t.to_csv(OUT/f'{name}_trades.csv',index=False);l.to_csv(OUT/f'{name}_daily.csv')
        results[name]=stats(t,l)
    f,b=results['full'],results['baseline']
    gates={'trades_ge20':f['trades']>=20,'gross_positive':f['gross']>0,'net_positive':f['total']>0,
           'trade_t_ge2':f['t_trade'] is not None and f['t_trade']>=2,'sharpe_ge0_5':f['sharpe']>=.5,
           'positive_years_ge3':sum(v>0 for v in f['by_year'].values())>=3,
           'cost_stress_positive':f['stress_total']>0,'sharpe_beats_baseline_0_1':f['sharpe']>=b['sharpe']+.1,
           'calmar_ge_baseline':f['calmar'] is not None and b['calmar'] is not None and f['calmar']>=b['calmar']}
    result={'stage':'2018-22 design only','definition':'assumed weekly NQ/VIX adaptation, not exact source replication',
            'results':results,'gates':gates,'design_passed':all(gates.values()),'economic_definitions':2,
            'execution_stresses':2,'holdout_read':False,'portfolio_tests_run':False,
            'data_dates':[str(d.index.min()),str(d.index.max())],
            'weekly_formation_rows':len(w),'first_valid_ema25_week':str(w.ema25.first_valid_index()),
            'quarantine_weeks_design':int(w.loc['2018':'2022'].quarantine.sum()),
            'delayed_execution_sessions':{str(dt.date()):int(row.execution_bar) for dt,row in d[d.execution_bar>801].iterrows()},
            'inputs':manifest,'preregistration_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
            'code_sha256':hashlib.sha256((ROOT/CODE).read_bytes()).hexdigest(),
            'plan_sha256':hashlib.sha256((ROOT/PLAN).read_bytes()).hexdigest(),
            'limitations':['RTH daily marks omit overnight intraperiod adverse excursions',
                           'continuous contract identities/actual rolls not authenticated; fixed calendar quarantine',
                           'assumed formulas and Monday08:00 execution differ from paper',
                           'no financing, collateral, margin sufficiency or portfolio certification']}
    (OUT/'results.json').write_text(json.dumps(result,indent=2,allow_nan=True)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='inputs'},indent=2))


if __name__=='__main__':main()
