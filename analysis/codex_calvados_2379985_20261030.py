"""Frozen cheap screen of the paper's unhedged Eq3 component,1dated VX.
No ES proxy/continuous futures, native-fill claim, leverage tuning or source-CAGR replication.
Shared intraday engine lacks multiday dated-contract switching: this small adapter
adds daily-open orders and settlement cash marks; metrics/resampling stay shared.
"""
from pathlib import Path
import argparse,hashlib,json,subprocess,sys,platform,importlib.metadata
import numpy as np
import pandas as pd
import metrics as M
import resampling as R
ROOT=Path(__file__).resolve().parents[1]
IN=ROOT/'agents/codex/inputs/calvados_2379985_20261030'
OUT=ROOT/'analysis/outputs/codex_calvados_2379985_20261030'
PLAN='agents/codex/plans/calvados_2379985_20261030.md'
PV,FEE,SLIP=1000.,5.,50.
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(p,x):
    def cast(z):
        if isinstance(z,(np.integer,np.bool_)):return z.item()
        if isinstance(z,np.ndarray):return z.tolist()
        if isinstance(z,(pd.Timestamp,Path)):return str(z)
        raise TypeError(type(z).__name__)
    Path(p).write_text(json.dumps(x,indent=2,default=cast)+'\n')
def committed():
    for p in [PLAN,Path(__file__).relative_to(ROOT).as_posix()]:
        subprocess.run(['git','cat-file','-e','HEAD:'+p],cwd=ROOT,check=True)
        subprocess.run(['git','diff','--exit-code','HEAD','--',p],cwd=ROOT,stdout=subprocess.DEVNULL,check=True)
def performance(d,t):
    p=M.perf(d,t,capital=500000.)
    # Include the initial capital peak when the first daily mark is a loss.
    p['max_dd']=R.max_dd(d)
    p['calmar']=p['annual']/p['max_dd'] if p['max_dd']>0 else np.inf
    eq=500000.+pd.Series(d).cumsum();peak=eq.cummax().clip(lower=500000.)
    p['ulcer']=float(np.sqrt(np.mean(((eq-peak)/peak*100.)**2)))
    p['ulcer_perf']=p['annual']/500000.*100./p['ulcer'] if p['ulcer']>0 else np.inf
    return p
def load():
    gate=json.loads((IN/'data_gate.json').read_text());manifest=json.loads((IN/'panel_manifest.json').read_text())
    if sha(IN/'cfe_calendar.csv')!=gate['calendar_sha256'] or sha(gate['spot_path'])!=gate['spot_sha256']:raise ValueError('Calendar/spot changed')
    cal=pd.DatetimeIndex(pd.read_csv(IN/'cfe_calendar.csv',parse_dates=['date']).date)
    days=cal[(cal>='2018-01-01')&(cal<='2022-12-31')]
    panel={}
    for x in manifest['files']:
        if sha(x['path'])!=x['sha256']:raise ValueError('Panel bytes changed')
        f=pd.read_csv(x['path']);f['date']=pd.to_datetime(f['Trade Date'])
        f=f[f.date<='2022-12-30'].set_index('date').sort_index()
        f['sigma']=np.sqrt(f.Settle.diff().pow(2).rolling(10,min_periods=10).mean())
        f['tts']=cal.searchsorted(pd.Timestamp(x['expiry']),side='right')-cal.searchsorted(f.index,side='right')
        panel[pd.Timestamp(x['expiry'])]=f
    spot=pd.read_csv(gate['spot_path'],parse_dates=['DATE']).set_index('DATE').CLOSE
    spot=spot[spot.index<='2022-12-30']
    return cal,days,panel,spot
def value(panel,e,d,col):
    z=float(panel[e].loc[d,col])
    if not np.isfinite(z) or z<=0:raise ValueError(f'Invalid {col} for {e} on {d}')
    return z
def run():
    committed();OUT.mkdir(parents=True,exist_ok=True);cal,days,panel,spot=load()
    cash=0.;held=None;target=None;entry=None;trades=[];daily=[];decisions=[];marks=[]
    previous_equity=0.
    for d in days:
        # Targets came from the preceding session's fully available close/settle.
        if d==days[-1]:target=None       # frozen terminal liquidation at last design Open
        if target!=held:
            if held is not None:
                px=value(panel,held,d,'Open');gross=(entry['entry_ref']-px)*PV
                cash+=gross-(FEE+SLIP)
                trades.append({**entry,'exit_date':d,'exit_ref':px,'gross':gross,'fees':2*FEE,'slippage':2*SLIP,
                               'net':gross-2*(FEE+SLIP),'stress_net':gross-2*(FEE+2*SLIP)})
                held=None;entry=None
            if target is not None:
                px=value(panel,target,d,'Open');cash-=FEE+SLIP;held=target
                entry=dict(entry_date=d,expiry=held,entry_ref=px,entry_decision=decisions[-1]['date'],
                    entry_score=decisions[-1]['chosen_score'],side=-1,qty=1)
        mark=(entry['entry_ref']-value(panel,held,d,'Settle'))*PV if held is not None else 0.
        eq=cash+mark
        # Daily settlement marks, not a chronology-preserving intraday margin path.
        daily.append(dict(date=d,net=eq-previous_equity,equity=eq,held_expiry=held,spot_available=d in spot.index))
        marks.append(dict(date=d,expiry=held,unrealized=mark,closed_cash=cash))
        previous_equity=eq
        if d==days[-1]:continue
        eligible=[];own_score=np.nan
        if d in spot.index:
            v=float(spot.loc[d]);assert np.isfinite(v) and v>0
            for e,f in panel.items():
                if d not in f.index:continue
                r=f.loc[d];tt=int(r.tts)
                score=(float(r.Settle)-v)/(float(r.sigma)*tt) if tt>0 and float(r.sigma)>0 else np.nan
                if e==held:own_score=score
                if 15<=tt<=93:
                    if not np.isfinite(score):raise ValueError('Missing candidate sigma')
                    eligible.append((score,e))
            eligible.sort(key=lambda x:(-x[0],x[1]))
            if not eligible:raise ValueError('No eligible monthly futures')
            exit_needed=held is not None and (int(panel[held].loc[d,'tts'])<10 or own_score<.10)
            if held is not None and not np.isfinite(own_score):raise ValueError('Missing held-contract score')
            if held is None or exit_needed:
                target=eligible[0][1] if eligible[0][0]>.12 else None
            else:target=held
            score=eligible[0][0] if target is not None and target!=held else own_score
        else:
            # No stale spot basis decisions on the exceptional2018-12-05VX session.
            target=held
            if held is not None and int(panel[held].loc[d,'tts'])<10:target=None
            score=np.nan
        decisions.append(dict(date=d,current_expiry=held,next_expiry=target,chosen_score=score,own_score=own_score,
                              fresh_spot=d in spot.index))
    assert held is None
    cols=['entry_date','expiry','entry_ref','entry_decision','entry_score','side','qty','exit_date','exit_ref','gross','fees','slippage','net','stress_net']
    t=pd.DataFrame(trades,columns=cols);t['exit_date']=pd.to_datetime(t.exit_date)
    d=pd.DataFrame(daily).set_index('date');z=pd.DataFrame(decisions)
    t.to_csv(OUT/'design_trades.csv',index=False);d.to_csv(OUT/'design_daily.csv');z.to_csv(OUT/'design_decisions.csv',index=False)
    pd.DataFrame(marks).to_csv(OUT/'design_marks.csv',index=False)
    if not np.isclose(t.net.sum(),d.net.sum()):raise AssertionError('Trade/marked daily cash mismatch')
    result=performance(d.net,t.net)
    result.update(total=float(d.net.sum()),daily_t=float(d.net.mean()/d.net.std()*np.sqrt(len(d))),
        trade_t=float(t.net.mean()/t.net.std()*np.sqrt(len(t))),max_dd=R.max_dd(d.net),
        gross=float(t.gross.sum()),fees=float(t.fees.sum()),slippage=float(t.slippage.sum()),stress_total=float(t.stress_net.sum()))
    years=d.net.groupby(d.index.year).sum();yr=[]
    for y in years.index:
        dd=d[d.index.year==y];tt=t[t.exit_date.dt.year==y]
        p=performance(dd.net,tt.net);p.update(year=int(y),total=float(dd.net.sum()),daily_t=float(dd.net.mean()/dd.net.std()*np.sqrt(len(dd))))
        yr.append(p)
    pd.DataFrame(yr).to_csv(OUT/'design_years.csv',index=False)
    rng=np.random.default_rng(2379985);gross=t.gross.to_numpy();null=[]
    for i in range(1000):
        x=gross*rng.choice([-1,1],len(t))-t.fees.to_numpy()-t.slippage.to_numpy()
        null.append(dict(draw=i,total=float(x.sum())))
    pside=float((1+sum(x['total']>=result['total'] for x in null))/1001)
    pd.DataFrame(null).to_csv(OUT/'design_random_side.csv',index=False)
    boot=R.bootstrap(d.net,n=5000,block=10,seed=2379986,capital=500000.);boot.to_csv(OUT/'design_bootstrap.csv')
    # Bootstrap annual profit is an identical positive-mean test under fixed T.
    gates=dict(at_least20_closed_trades=len(t)>=20,positive_net=result['total']>0,daily_t_at_least2=result['daily_t']>=2,
               four_positive_years=int((years>0).sum())>=4,stress_positive=result['stress_total']>0,
               block_annual_p5_positive=float(boot.loc['annual','p5'])>0,random_side_p_le05=pside<=.05)
    output=dict(component='Naked Eq3/4 only,1VX, next-session dailyOpen references',period='2018-2022',
        metrics=result,year_net={str(k):float(v) for k,v in years.items()},random_side_p=pside,gates=gates,
        passed=all(gates.values()),preferred_hedged_tested=False,account_comparisons_run=False,
        code_sha256=sha(__file__),plan_sha256=sha(ROOT/PLAN),
        input_sha256={x.name:sha(x) for x in IN.iterdir() if x.is_file()},
        spot_sha256=sha(json.loads((IN/'data_gate.json').read_text())['spot_path']),
        shared_code_sha256={x:sha(ROOT/'analysis'/x) for x in ['metrics.py','resampling.py']},
        versions={x:importlib.metadata.version(x) for x in ['numpy','pandas','numba','openpyxl','scipy','scikit-learn']},
        python=sys.version,platform=platform.platform(),seeds=dict(side=2379985,bootstrap=2379986),
        plan_commit=subprocess.check_output(['git','log','-1','--format=%H','--',PLAN],cwd=ROOT,text=True).strip())
    dump(OUT/'design_result.json',output);print(json.dumps(output,indent=2))
def synthetic():
    # Hedge algebra verification only, not a hedged strategy return study.
    n=20.;s=1100.;tts=17.;b=-.6+.006*tts;es=n*1000*b/(.01*s*50)
    vx_delta=-n*1000*b;es_delta=es*.01*s*50
    assert np.isclose(vx_delta+es_delta,0) and es<0
    assert np.isclose(-500000*.6/(15*1000),-20)
    sigma=np.sqrt(np.mean(np.square(np.arange(1,11,dtype=float))))
    assert sigma>np.std(np.arange(1,11,dtype=float))
    print(json.dumps(dict(hedge_signed_es=es,synthetic_total_linear_delta=vx_delta+es_delta,rms_example=sigma,checks=3)))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('phase',choices=['synthetic','design']);a=p.parse_args()
    synthetic() if a.phase=='synthetic' else run()
