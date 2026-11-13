"""Paired current-book replay for the frozen heavy-night fade; no live actions.
Canonical bench-compatible adverse paths plus a common-price session sensitivity.
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
sys.path.insert(0,str(ROOT/'analysis'));sys.argv=[sys.argv[0],str(OUT/'_cache')]
from portfolio import paths
from plan_150k_test import evaluation,R150

SEED=20261113
BASE=ROOT/'analysis/outputs/codex_book_joint_losses'
LABEL='fade'
CANDIDATE_KEY='FADE'


def candidate(variant='heavy',size=1):
    t=pd.concat([pd.read_csv(OUT/f'trades_{p}_{variant}.csv',parse_dates=['date']) for p in ['design','recent']],ignore_index=True)
    t['strategy']='FADE';t['qty']=float(size);t['net']*=size/10
    t['entry_ts']=t.date+pd.to_timedelta(t.j0,unit='m')
    t['exit_ts']=t.date+pd.to_timedelta(t.j1,unit='m')
    return t


def canonical(g,t,days):
    pieces={}
    for k,tt in t.groupby('strategy',sort=False):
        if k not in ['TWIN','JF','OT']:
            rr=tt.copy()
            rr['day']=np.searchsorted(g.ts,rr.date.to_numpy())
            rr['j0']=rr.entry_ts.dt.hour*60+rr.entry_ts.dt.minute
            rr['j1']=rr.exit_ts.dt.hour*60+rr.exit_ts.dt.minute
            rr['kind']=rr.kind.astype(str).map({'0':0,'1':1,'2':2,'stop':0,'target':1,'tgt':1}).fillna(2).astype(int)
            if k=='MON_BR':
                rr['j0']=0
                rr.loc[rr.exit_ts.dt.normalize()<rr.date,'j1']=0
                rr['entry']+=.25
            rr['exit']=rr.entry+rr.side*(rr.net*10/rr.qty+7.25)/20
            rr['qty']/=10
            w,r=paths(g,rr)
            pieces[k]=(w[days],r[days])
            continue
        w=np.zeros(g.c.shape);r=np.zeros(g.c.shape)
        for x in tt.itertuples():
            i=int((x.entry_ts-pd.Timestamp(g.ts[0])).total_seconds()/60)
            j=int((x.exit_ts-pd.Timestamp(g.ts[0])).total_seconds()/60)
            idx=np.arange(i,j+1)
            if k in ['TWIN','OT']:idx=idx[np.isfinite(g.c.ravel()[idx])]
            row,js=idx//1440,idx%1440;last=row[-1]
            net=x.net;fee=.55*x.qty if k=='JF' else 0.
            cost=(x.exit-x.entry)*x.side*2*x.qty-(net+fee)
            extreme=g.l.ravel()[idx] if x.side>0 else g.h.ravel()[idx]
            adv=(extreme-x.entry)*x.side*2*x.qty-cost
            is_target=str(x.kind) in ['1','tgt','target']
            if k in ['TWIN','OT']:adv[-1]=(net+fee) if str(x.kind)=='0' else min(adv[-1],net+fee)
            else:adv[-1]=(net+fee) if is_target else min(adv[-1],net+fee)
            logical=int(np.searchsorted(g.ts,x.date.to_datetime64()))
            if last!=logical:
                # Sunday cash flows must survive weekday row selection. The
                # old shared grid leaves these on Sunday and drops them.
                assert k=='TWIN' and last<logical
                w[logical,0]+=min(float(adv.min()),net)
                w[logical,1:]+=net;r[logical,:]+=net
                continue
            m=row==last;a=adv[m].copy()
            if (~m).any():a[0]=min(a[0],adv[~m].min())
            w[last,js[m]]+=a;w[last,js[-1]+1:]+=net+fee;r[last,js[-1]:]+=net+fee
            w[last]-=fee;r[last]-=fee
        pieces[k]=(w[days],r[days])
    return pieces


def physical(g,t,days,close_only=False):
    """Shared-price conservative bound; all trades in a minute share high/low.
    Final exit fills also checked. Trade lifecycle inside a minute is unknown.
    Model is a sensitivity, not proof of executable simultaneous marks.
    Aggregate on actual 17:00-16:00 sessions; pad maintenance with the final P&L.
    """
    n=g.D*1440
    q=np.zeros(n+1);a=np.zeros(n+1);qi=np.zeros(n+1);ai=np.zeros(n+1);cash=np.zeros(n+1)
    origin=pd.Timestamp(g.ts[0])
    for x in t.itertuples():
        i=int((x.entry_ts-origin).total_seconds()/60);j=int((x.exit_ts-origin).total_seconds()/60)
        signed=x.side*2*x.qty;cost=(x.exit-x.entry)*signed-x.net
        intercept=-x.entry*signed-cost
        q[i]+=signed;q[j]-=signed;a[i]+=intercept;a[j]-=intercept
        qi[i]+=signed;qi[j+1]-=signed;ai[i]+=intercept;ai[j+1]-=intercept;cash[j]+=x.net
    q=np.cumsum(q[:-1]);a=np.cumsum(a[:-1]);qi=np.cumsum(qi[:-1]);ai=np.cumsum(ai[:-1]);c=np.cumsum(cash[:-1])
    close=pd.Series(g.c.ravel()).ffill().to_numpy()
    marked=c+q*close+a
    priorcash=c-cash[:-1]
    low=np.where(np.isfinite(g.l.ravel()),g.l.ravel(),close)
    high=np.where(np.isfinite(g.h.ravel()),g.h.ravel(),close)
    worst=np.minimum(np.minimum(priorcash+qi*low+ai,priorcash+qi*high+ai),marked)
    worst=np.nan_to_num(worst);marked=np.nan_to_num(marked)
    w=np.empty((len(days),1440));r=np.empty_like(w)
    for k,d in enumerate(days):
        lo=(d-1)*1440+1021;hi=d*1440+961
        base=c[lo-1]
        ww=marked[lo:hi] if close_only else worst[lo:hi]
        w[k,:1380]=ww-base;r[k,:1380]=c[lo:hi]-base
        w[k,1380:]=w[k,1379];r[k,1380:]=r[k,1379]
    return w,r


def run_eval(w,r,stress=False):
    rules={**R150,'tgt':9050.}
    n=len(w);h=20 if stress else 21
    outcome=np.full(n,'invalid',dtype=object);duration=np.full(n,np.nan)
    for start in range(n-h+1):
        if not stress:
            ans=evaluation(w,r,start,n,rules)
        else:
            # Same existing engine, translated balance/floor by changing start,
            # trail room and target while restoring the ongoing $4k floor trail.
            bal=147998.08;floor=146000.;ans=('time',h)
            for count,d in enumerate(range(start,start+h),1):
                lim=max(floor,bal-2000.)
                hit=np.flatnonzero(bal+w[d]<=lim);win=np.flatnonzero(bal+r[d]>=159050.)
                jb=hit[0] if len(hit) else 1440;jp=win[0] if len(win) else 1440
                if jp<jb:ans=('pass',count);break
                if jb<1440:
                    if lim==floor:ans=('fail',count);break
                    bal=lim
                else:bal+=r[d,-1]
                floor=max(floor,bal-4000.)
        outcome[start],duration[start]=ans
    return outcome,duration


def band(delta):
    rng=np.random.default_rng(SEED);n=len(delta);st=rng.integers(0,n,(2000,int(np.ceil(n/60))))
    samples=delta[((st[:,:,None]+np.arange(60))%n).reshape(2000,-1)[:,:n]].mean(1)
    return np.percentile(samples,[5,95]).tolist()


def offsets(t,base,dates):
    fade=t.groupby('date').net.sum().reindex(dates,fill_value=0)
    onb=base[base.strategy=='ONB30'].groupby('date').net.sum().reindex(dates,fill_value=0)
    book=pd.read_csv(BASE/'daily.csv',index_col='date',parse_dates=True).BOOK.reindex(dates)
    crossings=pd.read_csv(BASE/'dll_crossings.csv',parse_dates=['date'])
    rows=[]
    for per,mask in [('2018-22',dates.year<=2022),('2023+',dates.year>=2023)]:
        ds=dates[mask];a=fade.loc[ds];o=onb.loc[ds];b=book.loc[ds]
        for state,sel in [('all',np.ones(len(ds),bool)),('ONB loss',o<0),('ONB win',o>0),('ONB inactive',o==0),('book tail5',b.rank(method='first')<=np.ceil(len(ds)*.05))]:
            x=a.loc[sel]
            rows.append(dict(period=per,state=state,days=len(x),candidate_active=int((x!=0).sum()),
                             candidate_total=x.sum(),mean_per_day=x.mean(),positive=int((x>0).sum()),negative=int((x<0).sum())))
        c=crossings[crossings.date.isin(ds)].copy();at=c.date+pd.to_timedelta(c.minute,unit='m')
        early=[]
        for day,clock in zip(c.date,at):
            early.append(t[(t.date==day)&(t.exit_ts<=clock)].net.sum())
        c['fade_before_base_crossing']=early;c['period']=per
        c.to_csv(OUT/f'early_offsets_{per.replace("+","on")}.csv',index=False)
    pd.DataFrame(rows).to_csv(OUT/'conditional_offsets.csv',index=False)


def main():
    assert json.loads((OUT/'gate_recent.json').read_text())['pass']
    g=pickle.load(open('C:/TradingVault/scratch_data/g24.pkl','rb'))
    base=pd.read_csv(BASE/'trades.csv',parse_dates=['date','entry_ts','exit_ts'])
    daily=pd.read_csv(BASE/'daily.csv',index_col='date',parse_dates=True)
    dates=daily.index;days=np.searchsorted(g.ts,dates.to_numpy())
    fade=candidate();lag=candidate('delay');offsets(fade,base,dates)
    # Find design overlap without reading P&L to choose replacement.
    counts={}
    for k in base.strategy.unique():
        n=0;b=base[(base.strategy==k)&(base.date.dt.year<=2022)]
        for x in fade[fade.date.dt.year<=2022].itertuples():
            for y in b[(b.entry_ts<=x.exit_ts)&(b.exit_ts>=x.entry_ts)].itertuples():
                n+=int((min(x.exit_ts,y.exit_ts)-max(x.entry_ts,y.entry_ts)).total_seconds()/60)+1
        counts[k]=n
    replace=max(counts,key=counts.get)
    print('design overlap',counts,'replacement',replace,flush=True)
    bp=canonical(g,base,days);fp=canonical(g,fade,days)[CANDIDATE_KEY];lp=canonical(g,lag,days)[CANDIDATE_KEY]
    for k,(w,r) in bp.items():assert np.allclose(r[:,-1],daily[k]),k
    w0=sum(v[0] for v in bp.values());r0=sum(v[1] for v in bp.values())
    wc,rc=bp[replace]
    streams={'base':(w0,r0),f'+{LABEL}1':(w0+fp[0],r0+fp[1]),f'+{LABEL}2':(w0+2*fp[0],r0+2*fp[1]),
             'empty_slot':(w0-wc,r0-rc),'replacement1':(w0-wc+fp[0],r0-rc+fp[1]),
             '+delay1':(w0+lp[0],r0+lp[1])}
    results=[];decisions=[]
    # Paired primary engine; common-price and close-only are fixed sensitivities.
    for model in ['canonical','common_price','close_only']:
        print('model',model,flush=True)
        if model!='canonical':
            cases={'base':base,f'+{LABEL}1':pd.concat([base,fade],ignore_index=True),
                   f'+{LABEL}2':pd.concat([base,candidate(size=2)],ignore_index=True),
                   'empty_slot':base[base.strategy!=replace],
                   'replacement1':pd.concat([base[base.strategy!=replace],fade],ignore_index=True),
                   '+delay1':pd.concat([base,lag],ignore_index=True)}
            streams={k:physical(g,v,days,close_only=model=='close_only') for k,v in cases.items()}
        for stress in [False,True]:
            cache={k:run_eval(w,r,stress) for k,(w,r) in streams.items()}
            raw=pd.DataFrame({'date':dates})
            for k,(o,duration) in cache.items():raw[k]=o;raw[k+'_days']=duration
            raw.to_csv(OUT/f'outcomes_{model}_{"stress" if stress else "fresh"}.csv',index=False)
            b=cache['base'][0]
            for per,mask in [('2018-22',dates.year<=2022),('2023+',dates.year>=2023)]:
                valid=mask&(b!='invalid')&(dates<=pd.Timestamp('2026-09-01'))
                for k,(o,duration) in cache.items():
                    for reference in (['base','empty_slot'] if k=='replacement1' else ['base']):
                        ref=cache[reference][0]
                        delta=(o[valid]=='pass').astype(float)-(ref[valid]=='pass').astype(float)
                        lo,hi=band(delta)
                        row=dict(model=model,scenario='stress' if stress else 'fresh',period=per,case=k,reference=reference,
                                 starts=int(valid.sum()),pass_rate=float(np.mean(o[valid]=='pass')),
                                 fail_rate=float(np.mean(o[valid]=='fail')),time_rate=float(np.mean(o[valid]=='time')),
                                 pass_delta=float(delta.mean()),band05=lo,band95=hi,
                                 median_days_pass=float(np.median(duration[valid&(o=='pass')])) if (valid&(o=='pass')).any() else None)
                        results.append(row)
                        if reference=='base':print(per,stress,k,f"pass {row['pass_rate']:.3%} diff {row['pass_delta']:+.3%} [{lo:+.3%},{hi:+.3%}]",flush=True)
    table=pd.DataFrame(results);table.to_csv(OUT/'book_comparison.csv',index=False)
    p=table[(table.model=='canonical')&(table.case==f'+{LABEL}1')&(table.reference=='base')]
    passbook=bool((p[p.period=='2018-22'].pass_delta>=0).all() and (p[p.period=='2023+'].band05>0).all())
    manifest=dict(code=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
                  primary_book_gate=passbook,overlap_minutes_design=counts,replacement=replace,
                  audit_trades_sha256=hashlib.sha256((BASE/'trades.csv').read_bytes()).hexdigest(),
                  base_daily_reconciliation=True,target=159050.,stressed_start=147998.08,
                  note='Stressed start is a historical scenario, not verified current balance; no trading changes.')
    (OUT/'book_gate.json').write_text(json.dumps(manifest,indent=2))
    print('BOOK GATE',passbook,flush=True)


if __name__=='__main__':main()
