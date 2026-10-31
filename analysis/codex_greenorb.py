"""Frozen GreenORB rebuild on owned NQ bars, valued at one MNQ.

The uploaded Liqport class is archived, never imported. This extends Grid24
execution for source candle-colour paths and absolute OR stops/fill-anchored R.
Available-bar overnight VWAP is an explicit proxy, not native MNQ reproduction.
"""
from pathlib import Path
import argparse,hashlib,json,sys
import numpy as np
import pandas as pd
from numba import njit
from grid24 import Grid24
import metrics as M
import resampling as RES
import montecarlo as MC
ROOT=Path(__file__).resolve().parents[1]
INPUT=ROOT/'agents/codex/inputs/greenorb'
OUT=ROOT/'analysis/outputs/codex_greenorb'
SEED=30102026
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,x):Path(p).write_text(json.dumps(x,indent=2,default=str)+'\n')
def load(stage):
    # Separate split-specific readers; design cannot load recent prices.
    years=list(range(2018,2023)) if stage=='design' else list(range(2022,2027))
    files=[str(ROOT/f'data/NQ_1min_{y}.csv') for y in years]
    nights=[str(ROOT/f'data/NQ_1min_ON_{y}.csv') for y in years]
    # Input-only aliases keep split isolation and retain the previous calendar
    # night's warmup. Grid24 cannot otherwise accept a list of disjoint years.
    stage_dir=ROOT/'scratch_data/codex_greenorb'/stage
    stage_dir.mkdir(parents=True,exist_ok=True)
    for f in files+nights:
        p=Path(f);assert p.exists()
        alias=stage_dir/p.name
        if alias.exists():assert alias.resolve()==p.resolve()
        else:alias.symlink_to(p)
    expected={Path(p).name for p in files+nights}
    assert {p.name for p in stage_dir.glob('*.csv')}==expected
    g=Grid24(str(stage_dir/'NQ_1min_2???.csv'),str(stage_dir/'NQ_1min_ON_2???.csv'))
    if stage=='design':assert pd.Timestamp(g.ts[-1]).year==2022
    return g,files+nights

@njit(cache=True)
def walk(o,h,l,c,start,end,side,stop,target,entry,slip):
    """Source O-L-H-C for green/doji, O-H-L-C for red; target trade-through. End=time-exit OPEN."""
    worst=entry;collision=0
    for j in range(start,end+1):
        worst=min(worst,o[j]) if side==1 else max(worst,o[j])
        if j==end:return j,o[j]-side*slip,2,worst,collision
        if side*(o[j]-stop)<=0:return j,o[j]-side*slip,0,min(worst,o[j]) if side==1 else max(worst,o[j]),collision
        hit_s=side*(l[j]-stop)<=0 if side==1 else side*(h[j]-stop)<=0
        hit_t=h[j]>=target+.25 if side==1 else l[j]<=target-.25
        if hit_s and hit_t:collision+=1
        low_first=c[j]>=o[j]
        stop_first=low_first if side==1 else not low_first
        if hit_s and (not hit_t or stop_first):return j,stop-side*slip,0,stop,collision
        if hit_t:
            if stop_first:worst=min(worst,l[j]) if side==1 else max(worst,h[j])
            return j,target,1,worst,collision
        worst=min(worst,l[j]) if side==1 else max(worst,h[j])
    return end,np.nan,3,worst,collision

def vwap(g,d):
    # Reset17:00NY=16:00CT; there are no regular trades during16:00-17:00CT.
    prev=np.arange(961,1440);cur=np.arange(0,901)
    h=np.r_[g.h[d-1,prev],g.h[d,cur]];l=np.r_[g.l[d-1,prev],g.l[d,cur]]
    c=np.r_[g.c[d-1,prev],g.c[d,cur]];v=np.r_[g.v[d-1,prev],g.v[d,cur]]
    ok=np.isfinite(h+l+c+v)&(v>=0)
    pv=np.where(ok,(h+l+c)/3*v,0).cumsum();vv=np.where(ok,v,0).cumsum()
    a=np.divide(pv,vv,out=np.full(len(pv),np.nan),where=vv>0)
    # Zero computational increments for absent input bars do not assert zero
    # actual volume: missing prefix is counted as proxy uncertainty in audit.
    return a[len(prev):],ok[len(prev):]

def opportunities(g,stage):
    lo,hi=('2018-01-01','2023-01-01') if stage=='design' else ('2023-01-01','2027-01-01')
    lookup={pd.Timestamp(d):i for i,d in enumerate(g.ts)};rows=[];sigs=[]
    for day in pd.bdate_range(lo,pd.Timestamp(hi)-pd.Timedelta(days=1)):
        if day>pd.Timestamp(g.ts[-1]):break
        d=lookup.get(day);row=dict(date=str(day.date()),day=d,status='unknown_day',night_missing=None)
        if d is None or d==0:rows.append(row);continue
        obs=np.isfinite(g.o[d]+g.h[d]+g.l[d]+g.c[d]+g.v[d])&(g.v[d]>=0)
        # Complete scan and possible held horizon for known-result days;
        # unknown data days are not treated as zero-strategy-return days.
        if not obs[511:900].all():
            row['status']='unknown_rth_path';rows.append(row);continue
        vv,_=vwap(g,d)
        pm=np.r_[np.isfinite(g.c[d-1,1021:]),np.isfinite(g.c[d,:526])]
        row.update(status='resolved',night_missing=int((~pm).sum()))
        rows.append(row)
        bars=[]
        for end in (515,520,525):bars.append((g.o[d,end-4],g.c[d,end]))
        bias=1 if all(b>a for a,b in bars) else -1 if all(b<a for a,b in bars) else 0
        oh=float(g.h[d,511:526].max());ol=float(g.l[d,511:526].min())
        for variant in ['primary','no_colour']:
            for j in range(530,661,5):
                c=g.c[d,j];side=1 if c>oh and c>vv[j] else -1 if c<ol and c<vv[j] else 0
                if not side or(variant=='primary' and side!=bias):continue
                stop=ol if side==1 else oh
                if side*(c-stop)/c>=.01:continue
                sigs.append(dict(date=str(day.date()),day=d,dj=j,side=side,stop_px=stop,bias=bias,variant=variant,
                                 signal_close=c,vwap=vv[j],night_missing=row['night_missing']))
                break
    return pd.DataFrame(sigs),pd.DataFrame(rows)

def execute(g,sigs,variant,random=None,slip_ticks=2,seed=SEED):
    rows=[];rng=np.random.default_rng(seed if random=='side' else seed+1)
    slip=.25*slip_ticks
    for s in sigs.itertuples(index=False):
        d=s.day;side=s.side;j=s.dj
        sp=s.stop_px
        if random=='side':side=int(rng.choice([-1,1]))
        if random=='time':j=int(rng.choice(np.arange(530,661,5)))
        entry=g.o[d,j+1]+side*slip
        risk=s.side*(g.o[d,s.dj+1]+s.side*.5-s.stop_px)
        if random is not None:sp=entry-side*risk
        else:risk=side*(entry-sp)
        if risk<=0:raise ValueError('Nonpositive fill-to-stop risk: requires source-engine resolution, not silent omission')
        raw=entry+side*1.5*risk
        target=(np.ceil(raw/.25-1e-9)if side==1 else np.floor(raw/.25+1e-9))*.25
        xj,px,kind,worst,col=walk(g.o[d],g.h[d],g.l[d],g.c[d],j+1,899,side,sp,target,entry,slip)
        # Gross references separate actual fill allowances from commissions.
        fill_charge=(1+(kind!=1))*slip*2
        gross_ref=(px-entry)*side*2 + fill_charge
        net=(px-entry)*side*2-1.24
        rows.append(dict(date=s.date,day=d,j0=j+1,j1=xj,side=side,entry=entry,exit=px,kind=kind,
            stop_px=sp,target_px=target,risk_pts=risk,signal_close=s.signal_close,bias=s.bias,
            variant=variant,gross=gross_ref,commission=1.24,slippage=fill_charge,net=net,
            author_fee_net=net+.20,fixed_ledger_stress_net=net-fill_charge,collision_bars=col,
            mae=abs(worst-entry)*2,night_missing=s.night_missing))
    return pd.DataFrame(rows)

def stats(t,calendar):
    x=t.net;days=pd.to_datetime(calendar.date);daily=t.groupby(pd.to_datetime(t.date)).net.sum().reindex(days,fill_value=0.)
    m=M.perf(daily,x)
    # Include initial capital in the peak: the first losing trade is a drawdown.
    m['max_dd']=RES.max_dd(daily);m['calmar']=m['annual']/m['max_dd'] if m['max_dd'] else None
    m.update(total=float(x.sum()),t=float(x.mean()/x.std(ddof=1)*np.sqrt(len(x)))if len(x)>1 else None,
        gross=float(t.gross.sum()),commission=float(t.commission.sum()),slippage=float(t.slippage.sum()),
        fixed_ledger_stress_total=float(t.fixed_ledger_stress_net.sum()),author_fee_total=float(t.author_fee_net.sum()))
    prior=pd.read_csv(ROOT/'TRIALS.csv')
    m.update(historical_trial_items=len(prior),historical_trial_variants=int(prior.variants.sum()),
             trials_t_bar=M.t_threshold(len(prior)+1),dsr=M.deflated_sharpe(x,len(prior)+1))
    assert np.isclose(daily.sum(),x.sum())
    assert np.isclose(t.gross.sum()-t.commission.sum()-t.slippage.sum(),x.sum())
    return m,daily

def filter_checks(base,kept,calendar):
    removed=base[~base.date.isin(kept.date)]
    bs,_=stats(base,calendar);ks,kd=stats(kept,calendar);rs,_=stats(removed,calendar)
    rng=np.random.default_rng(SEED+2);profits=[];dds=[]
    for _ in range(1000):
        z=base.iloc[np.sort(rng.choice(len(base),len(kept),replace=False))]
        m,_=stats(z,calendar);profits.append(m['total']);dds.append(m['max_dd'])
    profits=np.array(profits);dds=np.array(dds)
    p_profit=float((1+(profits>=ks['total']).sum())/1001)
    p_dd=float((1+(dds<=ks['max_dd']).sum())/1001)
    # Strict source-filter admission: total net improves, removed trades lose,
    # and both profit and DD beat95% of same-size random subsets.
    passed=ks['total']>bs['total'] and rs['avg']<0 and p_profit<=.05 and p_dd<=.05
    return dict(base=bs,kept=ks,removed=rs,p_profit=p_profit,p_dd=p_dd,
        random_drop_profit=profits.tolist(),random_drop_dd=dds.tolist(),pass_filter=bool(passed))

def run(stage):
    OUT.mkdir(parents=True,exist_ok=True)
    if stage=='recent':
        assert json.loads((OUT/'design_result.json').read_text())['later_stages_earned'], 'Design gate has not earned recent data'
    g,paths=load(stage);sig,audit=opportunities(g,stage)
    sig.to_csv(OUT/f'{stage}_signals.csv',index=False)
    resolved=audit[audit.status=='resolved']
    by={v:execute(g,sig[sig.variant==v],v) for v in ['primary','no_colour']}
    # Nested colour-filter control: same first no-colour entry, unchanged exits.
    b=by['no_colour'];by['nested_colour']=b[b.side==b.bias].copy()
    results={};ds={}
    for k,t in by.items():
        t.to_csv(OUT/f'{stage}_{k}_trades.csv',index=False)
        results[k]={};ds[k]={}
        for side,label in [(0,'whole'),(1,'long'),(-1,'short')]:
            z=t if not side else t[t.side==side]
            if len(z):results[k][label],ds[k][label]=stats(z,resolved)
        results[k]['yearly']={str(y):stats(z,resolved[pd.to_datetime(resolved.date).dt.year==y])[0]
            for y,z in t.groupby(pd.to_datetime(t.date).dt.year)}
        results[k]['yearly_sides']={str(y):{label:stats(z[z.side==side],resolved[pd.to_datetime(resolved.date).dt.year==y])[0]
            for side,label in [(1,'long'),(-1,'short')] if (z.side==side).any()}
            for y,z in t.groupby(pd.to_datetime(t.date).dt.year)}
    t=by['primary'];s=results['primary']['whole']
    stress=execute(g,sig[sig.variant=='primary'],'primary_4tick',slip_ticks=4)
    stress.to_csv(OUT/f'{stage}_primary_4tick_trades.csv',index=False)
    stress_stats,_=stats(stress,resolved)
    f=filter_checks(b,by['nested_colour'],resolved)
    save(OUT/f'{stage}_filter.json',f)
    daily=ds['primary']['whole']
    daily.to_csv(OUT/f'{stage}_primary_daily.csv',index_label='date',header=['net'])
    mc=dict(trade=MC.trade_mc(t.net,n=10000,seed=SEED),
            daily=MC.daily_mc(daily,n=5000,seed=SEED,trail=2000))
    save(OUT/f'{stage}_montecarlo.json',mc)
    RES.bootstrap(daily,n=5000,block=10,seed=SEED).to_csv(OUT/f'{stage}_bootstrap.csv')
    # Stage1 gate: no controls needed to disqualify an insufficient primary.
    gross_pass=len(resolved)>=1000 and len(t)>=80 and s['total']>0 and s['t']>=2 and stress_stats['total']>0
    result=dict(stage=stage,primary_gross_gate=bool(gross_pass),metrics=results,
        data=dict(total_weekdays=len(audit),resolved_days=len(resolved),unknown_days=int((audit.status!='resolved').sum()),
                  proxy_overnight_missing_days=int((resolved.night_missing>0).sum())),
        financial_scope='NQ observed-bar VWAP proxy at1MNQ prices/costs, not nativeMNQ/Liqport match',
        later_stages_earned=False,definition_ids_executed=['GO_PRIMARY','GO_NO_COLOUR','GO_NESTED_COLOUR'],
        exact_4tick_stress=stress_stats,filter_gate=f['pass_filter'],
        gross_breakeven_extra_cost_per_trade=s['total']/len(t),
        dependency_versions=dict(numpy=np.__version__,pandas=pd.__version__),code_sha256=sha(__file__))
    result['engine_hashes']={str(p.relative_to(ROOT)):sha(p) for p in
        [ROOT/'analysis'/name for name in ['grid24.py','metrics.py','resampling.py','montecarlo.py']]}
    audit.to_csv(OUT/f'{stage}_coverage.csv',index=False)
    save(OUT/f'{stage}_result.json',result)
    save(OUT/f'{stage}_inputs.json',[dict(path=str(Path(p).relative_to(ROOT)),sha256=sha(p))for p in paths])
    print(json.dumps(result,indent=2,default=str))
    print('Monte Carlo diagnostic at1MNQ, not a funded-account test:',json.dumps(mc,default=str))
    if not gross_pass:
        print('STOP: failed preregistered primary cheap gate; no recent or account tests.')
        return
    # Only after the primary cheap gate: random-side/time with identical horizon
    # and inherited stop distances,1000replications per control family.
    # No alternate strategy is selected from these diagnostics.
    null={}
    for mode in ['side','time']:
        values=[]
        # Stable source seed, explicit offset per draw. No strategy selected.
        for k in range(1000):
            z=execute(g,sig[sig.variant=='primary'],'null_'+mode,random=mode,seed=SEED+100*k)
            values.append(float(z.net.sum()))
        null[mode]=dict(totals=values,p=(1+sum(v>=s['total'] for v in values))/1001)
    save(OUT/f'{stage}_placebo.json',null)
    result['definition_ids_executed']+=['GO_RANDOM_SIDE','GO_RANDOM_TIME']
    result['later_stages_earned']=bool(f['pass_filter'] and all(v['p']<=.05 for v in null.values()))
    result['placebo_p']={k:v['p'] for k,v in null.items()}
    save(OUT/f'{stage}_result.json',result)
    print(json.dumps({k:v['p'] for k,v in null.items()}))

def synthetic():
    # Entry-bar protection, gap stops, colour collision, trade-through, time OPEN.
    o=np.array([100.,100.,101.]);h=np.array([103.,103.,102.]);l=np.array([97.,97.,100.]);c=np.array([102.,98.,101.])
    assert walk(o,h,l,c,0,2,1,98.,102.,100.,.5)[2]==0
    c[0]=98.;assert walk(o,h,l,c,0,2,1,98.,102.,100.,.5)[2]==1
    h[:]=102.;l[:]=99.;c[:]=101.;assert walk(o,h,l,c,0,2,1,98.,102.,100.,.5)[2]==2
    o[1]=97.;assert walk(o,h,l,c,0,2,1,98.,110.,100.,.5)[1]==96.5
    assert walk(o,h,l,c,0,0,-1,110.,90.,100.,.5)[1]==100.5
    print('PASS: entry-bar stop, candle-colour ordering, strict target trade-through, adverse gap, time-open exit')
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('stage',choices=['synthetic','design','recent']);a=ap.parse_args()
    synthetic() if a.stage=='synthetic' else run(a.stage)
