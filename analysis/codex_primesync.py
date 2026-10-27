"""Frozen PrimeSync reconstruction: design-only comparison before any recent returns."""
from __future__ import annotations
import argparse, hashlib, json, math, pickle, sys
from pathlib import Path
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'analysis'))
from candidates import adx
from codex_s03_calendar import calendar_status
import metrics as M

OUT=ROOT/'analysis/outputs/codex_primesync'
PLAN='ac08941890778a751039490a38a8fa5abd1def38'
PARAMS=dict(ma=150,volume_n=20,volume_mult=1.5,range_n=20,range_mult=1.2,
            adx_n=14,adx_min=20.,atr_n=14,atr_mult=1.5,cooldown=4,
            risk=500.,reserve=5.,max_qty=30,tick=.25,fee=1.04,through=1.)


def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()


def dump(p,x):
    Path(p).write_text(json.dumps(x,indent=2,default=str,allow_nan=True)+'\n')


def qty_for(risk_points,pv):
    return 3*(min(30,int(500/(risk_points*pv+5)))//3)


def walk(g,day,j0,side,risk,qty,pv,mode,adverse_first=False):
    """Extend the repo's OHLC path convention to staged stops/partial targets.
    All prices are observed one minute at a time. A missing held minute remains unresolved.
    """
    tick=.25; entry_raw=float(g.o[day,j0]); entry=entry_raw+side*tick
    targets=np.ceil(risk*np.array([1.5,2.5,4.5])/tick-1e-10)*tick
    stop_u=-risk; stage=0; left=qty; fills=[]; ambiguous=0
    def fill(j,quantity,raw,kind):
        actual=raw if kind=='target' else raw-side*tick
        fills.append(dict(j=j,quantity=int(quantity),raw=float(raw),price=float(actual),kind=kind))
    unresolved=False; exit_j=900
    for j in range(j0,901):
        o,h,l,c=(float(getattr(g,k)[day,j]) for k in 'ohlc')
        if not np.isfinite([o,h,l,c]).all():
            unresolved=True;exit_j=j;break
        fav=(h-entry)*side if side>0 else (l-entry)*side
        adv=(l-entry)*side if side>0 else (h-entry)*side
        if adv<=stop_u and fav>=targets[min(stage,2)]:ambiguous+=1
        if adverse_first:
            order=(o,l,h,c) if side>0 else (o,h,l,c)
        else:
            order=(o,h,l,c) if h-o<=o-l else (o,l,h,c)
        for point,px in enumerate(order):
            u=side*(px-entry)
            if u<=stop_u:
                raw=px if point==0 else entry+side*stop_u
                fill(j,left,raw,'stop');left=0;exit_j=j;break
            if mode==0:
                if u>=targets[1]:stage=max(stage,2);stop_u=max(stop_u,targets[0])
                elif u>=targets[0]:stage=max(stage,1);stop_u=max(stop_u,0.)
                if u>=targets[2]+1.:
                    fill(j,left,entry+side*targets[2],'target');left=0;exit_j=j;break
            else:
                while stage<3 and u>=targets[stage]+1.:
                    amount=qty//3 if stage<2 else left
                    fill(j,amount,entry+side*targets[stage],'target');left-=amount;stage+=1
                    if stage==1:stop_u=max(stop_u,0.)
                    elif stage==2:stop_u=max(stop_u,targets[0])
                    if not left:exit_j=j;break
                if not left:break
        if not left:break
        if j==900:
            fill(j,left,c,'time');left=0;exit_j=j
    if unresolved:
        return dict(exit_j=exit_j,unresolved=True,net=np.nan,gross=np.nan,
                    commission=np.nan,slippage=np.nan,entry=entry,ambiguous=ambiguous,fills=fills)
    gross=sum(f['quantity']*side*(f['raw']-entry_raw)*pv for f in fills)
    price_pnl=sum(f['quantity']*side*(f['price']-entry)*pv for f in fills)
    commission=qty*1.04
    assert sum(f['quantity'] for f in fills)==qty and left==0
    return dict(exit_j=exit_j,unresolved=False,net=price_pnl-commission,gross=gross,
                commission=commission,slippage=gross-price_pnl,entry=entry,ambiguous=ambiguous,fills=fills)


def fixtures():
    from types import SimpleNamespace
    def make(values):
        a={k:np.full((1,901),100.) for k in 'ohlc'}
        for j,vals in values.items():
            for k,v in zip('ohlc',vals):a[k][0,j]=v
        return SimpleNamespace(**a)
    cases=[]
    # Entry is100.25, R2, T1=103.25/T2=105.25/T3=109.25.
    g=make({899:(100,110.5,100,110),900:(110,110,110,110)})
    for mode in (0,1):
        x=walk(g,0,899,1,2.,3,2.,mode)
        assert not x['unresolved'] and all(f['kind']=='target' for f in x['fills'])
        expected=(3*9*2 if mode==0 else (3+5+9)*2)-3*1.04
        assert np.isclose(x['net'],expected)
        cases.append(dict(name='three_targets_or_full_target',mode=mode,passed=True))
    # Touch T1 but no trade-through; milestones stop changes, partial stop does not.
    g=make({899:(100,103.25,99,100),900:(100,100,97,98)})
    a=walk(g,0,899,1,2.,3,2.,0);b=walk(g,0,899,1,2.,3,2.,1)
    assert a['net']>b['net'] and b['fills'][0]['kind']=='stop'
    cases.append(dict(name='touch_not_partial_fill',passed=True))
    # Entry-bar initial protection, later gap-through executable price.
    g=make({899:(100,100,97,99)})
    x=walk(g,0,899,1,2.,3,2.,0);assert x['exit_j']==899 and x['fills'][0]['price']==98.
    g=make({899:(100,101,99,100),900:(95,96,94,95)})
    x=walk(g,0,899,1,2.,3,2.,0);assert x['fills'][0]['price']==94.75
    cases.append(dict(name='entry_stop_and_gap_through',passed=True))
    # Short symmetry and unknown held-minute detection.
    g=make({899:(100,100,89.5,90),900:(90,90,90,90)})
    x=walk(g,0,899,-1,2.,3,2.,1);assert len(x['fills'])==3 and x['net']>0
    g=make({899:(100,101,99,100),900:(np.nan,np.nan,np.nan,np.nan)})
    assert walk(g,0,899,1,2.,3,2.,0)['unresolved']
    assert qty_for(1000,2)==0 and qty_for(10,2)%3==0
    cases.append(dict(name='short_unknown_and_integer_risk',passed=True))
    g=make({899:(100,106.5,99,106),900:(104,104,102,103)})
    for mode in (0,1):
        x=walk(g,0,899,1,2.,3,2.,mode)
        assert x['exit_j']==900 and x['fills'][-1]['kind']=='stop'
        assert x['fills'][-1]['raw']==103.25 and x['fills'][-1]['price']==103.
        assert len(x['fills'])==(1 if mode==0 else 3)
    cases.append(dict(name='tp2_then_original_tp1_stop',passed=True))
    OUT.mkdir(parents=True,exist_ok=True);dump(OUT/'fixtures.json',cases)
    print(f'Execution fixtures PASS ({len(cases)} cases)',flush=True)


def roll_dates(index):
    result=np.zeros(len(index),bool)
    for y in sorted(set(index.year)):
        for mo in (3,6,9,12):
            fridays=pd.date_range(f'{y}-{mo:02d}-01',periods=31,freq='D')
            fridays=fridays[(fridays.month==mo)&(fridays.dayofweek==4)]
            start=fridays[2]-pd.Timedelta(days=8)
            result|=(index>=start)&(index<=start+pd.Timedelta(days=1))
    return result


def features(g,k,lo,hi):
    b=g.bars(k);per=1440//k
    valid=np.logical_and.reduce([np.isfinite(b[x]) for x in 'ohlcv'])
    ids=np.flatnonzero(valid.ravel()); h,l,c,v=(b[x].ravel()[ids] for x in 'hlcv')
    ma=pd.Series(c).rolling(150).mean().to_numpy()
    pc=np.r_[c[0],c[:-1]]
    tr=np.maximum(h-l,np.maximum(abs(h-pc),abs(l-pc)))
    atr=pd.Series(tr).rolling(14).mean().to_numpy()
    ax=adx(h,l,c,14)
    av=pd.Series(v).rolling(20).mean().shift(1).to_numpy()
    ar=pd.Series(h-l).rolling(20).mean().shift(1).to_numpy()
    full={x:np.full(valid.size,np.nan) for x in ('ma','atr','adx','vbase','rbase','ordinal','roll')}
    ixdates=pd.DatetimeIndex(g.ts[ids//per])
    contaminated=pd.Series(roll_dates(ixdates)).rolling(150,min_periods=1).max().to_numpy(bool)
    for name,data in (('ma',ma),('atr',atr),('adx',ax),('vbase',av),('rbase',ar),
                       ('ordinal',np.arange(len(ids))),('roll',contaminated)):
        full[name][ids]=data
    crosses=np.zeros(valid.size,int)
    good=np.arange(len(ids))>=300
    lg=(c>ma)&(pc<=np.r_[np.nan,ma[:-1]])&good
    sh=(c<ma)&(pc>=np.r_[np.nan,ma[:-1]])&good
    crosses[ids]=lg.astype(int)-sh.astype(int)
    vw=g.vwap_rows(b,start_j=511)
    has=np.isfinite(g.c).astype(int).ravel()
    pad=k-1;tail=(-(len(has)+pad))%k
    counts=np.r_[np.zeros(pad,int),has,np.zeros(tail,int)].reshape(-1,k).sum(1)[:valid.size].reshape(valid.shape)
    rth_good=np.isfinite(g.c[:,511:901]).cumprod(axis=1).astype(bool)
    rows=[];audit=dict(candidate_crosses=0,signal_buckets_incomplete=0,vwap_history_incomplete=0,
                      zero_or_bad_volume_baselines=0,eligible_signals=0)
    start,end=pd.Timestamp(lo),pd.Timestamp(hi)
    for d in np.flatnonzero((g.ts>=start.to_datetime64())&(g.ts<end.to_datetime64())):
        if calendar_status(g.ts[d])['kind']!='normal':continue
        for bi,j in enumerate(b['j']):
            if not 510<j<870:continue
            f=d*per+bi;side=crosses[f]
            if not side:continue
            audit['candidate_crosses']+=1
            if counts[d,bi]!=k:audit['signal_buckets_incomplete']+=1;continue
            if not rth_good[d,j-511]:audit['vwap_history_incomplete']+=1;continue
            if not full['vbase'][f]>0 or not full['rbase'][f]>0:
                audit['zero_or_bad_volume_baselines']+=1;continue
            if not (side*(b['c'][d,bi]-vw[d,bi])>0 and b['v'][d,bi]>1.5*full['vbase'][f]
                and b['h'][d,bi]-b['l'][d,bi]>1.2*full['rbase'][f] and full['adx'][f]>=20):continue
            risk=math.ceil(full['atr'][f]*1.5/.25-1e-10)*.25
            if not risk>0:continue
            rows.append(dict(day=int(d),dj=int(j),ordinal=int(full['ordinal'][f]),side=int(side),risk=risk,
                             roll_flag=bool(full['roll'][f]),date=pd.Timestamp(g.ts[d])))
    audit['eligible_signals']=len(rows)
    return pd.DataFrame(rows),audit,ids


def execute(g,signals,ids,k,pv,mode,adverse=False):
    rows=[];fills=[];last_exit_ord=-100000;flat_global=-1
    idx_to_min=(ids//(1440//k))*1440+(ids%(1440//k))*k
    missing_entry=0;minimum_lot_skip=0
    for x in signals.itertuples():
        minute=x.day*1440+x.dj
        if minute<flat_global or x.ordinal-last_exit_ord<4:continue
        q=qty_for(x.risk,pv)
        if q<3:minimum_lot_skip+=1;continue
        if not np.isfinite(g.o[x.day,x.dj+1]):missing_entry+=1;continue
        z=walk(g,x.day,x.dj+1,x.side,x.risk,q,pv,mode,adverse)
        flat_global=x.day*1440+(900 if z['unresolved'] else z['exit_j'])
        last_exit_ord=int(np.searchsorted(idx_to_min,flat_global,side='left'))
        fs=z.pop('fills');trade_id=len(rows)
        for f in fs:fills.append(dict(trade=trade_id,date=x.date,side=x.side,entry=z['entry'],**f))
        rows.append(dict(date=x.date,side=x.side,entry_j=x.dj+1,qty=q,risk=x.risk,
                         roll_flag=x.roll_flag,net_per_mini=z['net']/q*10,**z))
    columns=['date','side','entry_j','qty','risk','roll_flag','net_per_mini','exit_j',
             'unresolved','net','gross','commission','slippage','entry','ambiguous']
    return pd.DataFrame(rows,columns=columns),pd.DataFrame(fills),dict(missing_entry=missing_entry,minimum_lot_skip=minimum_lot_skip)


def describe(t,days):
    resolved=t.loc[~t.unresolved.astype(bool)]
    daily=resolved.groupby('date')['net'].sum().reindex(days,fill_value=0.)
    x=resolved.net.to_numpy(float);r=M.perf(daily,x)
    r.update(net=float(x.sum()),gross=float(resolved.gross.sum()),commission=float(resolved.commission.sum()),
             slippage=float(resolved.slippage.sum()),unresolved=int(t.unresolved.sum()),
             t=float(x.mean()/x.std(ddof=1)*np.sqrt(len(x))) if len(x)>1 and x.std()>0 else np.nan,
             daily_t=float(daily.mean()/daily.std()*np.sqrt(len(daily))) if daily.std()>0 else np.nan,
             mean_per_mini=float(resolved.net_per_mini.mean()) if len(resolved) else np.nan)
    return r,daily


def ci(x,n=2000):
    rng=np.random.default_rng(2701);out=[];x=np.asarray(x,float)
    for _ in range(n):
        starts=rng.integers(0,len(x),math.ceil(len(x)/20));ix=((starts[:,None]+np.arange(20))%len(x)).ravel()[:len(x)]
        out.append(x[ix].sum())
    return np.percentile(out,[5,95]).tolist()


def run_period(period,mode_only=None):
    lo,hi=('2018-01-01','2023-01-01') if period=='design' else ('2023-01-01','2027-01-01')
    days=pd.bdate_range(max(lo,'2018-01-02'),min(pd.Timestamp(hi)-pd.Timedelta(days=1),pd.Timestamp('2026-10-09')))
    rows=[];scores={};audits={};ledgers={}
    for market,cache,pv in (('NQ','g24.pkl',2.),('ES','ge.pkl',5.)):
        with (ROOT/'scratch_data'/cache).open('rb') as f:g=pickle.load(f)
        if period=='design':
            n=int(np.searchsorted(g.ts,np.datetime64('2023-01-01')))
            for name in ('o','h','l','c','v','ts','dates','last_j'):setattr(g,name,getattr(g,name)[:n])
            g.D=n;g.trading=g.trading[g.trading<n]
        for k in (15,30):
            context=f'{market}_{k}'
            sig,a,ids=features(g,k,lo,hi);sig.to_csv(OUT/f'{period}_{context}_signals.csv',index=False)
            audits[context]=a
            for mode in ((0,1) if mode_only is None else (mode_only,)):
                name=f'{context}_exit{mode}'
                t,ff,extra=execute(g,sig,ids,k,pv,mode)
                t.to_csv(OUT/f'{period}_{name}_trades.csv',index=False)
                ff.to_csv(OUT/f'{period}_{name}_fills.csv',index=False)
                ledgers[name]=t
                for label,part in [('whole',t),('long',t[t.side>0]),('short',t[t.side<0])]:
                    r,daily=describe(part,days);rows.append(dict(context=context,mode=mode,side=label,**r))
                    if label=='whole':scores[name]=daily
                years=[]
                for year,yy in t.groupby(t.date.dt.year):
                    r,_=describe(yy,days[days.year==year]);years.append(dict(year=int(year),**r))
                pd.DataFrame(years).to_csv(OUT/f'{period}_{name}_years.csv',index=False)
                audits[name]=dict(**extra,unresolved=int(t.unresolved.sum()),ambiguous_minutes=int(t.ambiguous.sum()),
                                 roll_flagged=int(t.roll_flag.sum()),positions=len(t))
                print(period,name,'trades',len(t),'net',round(t.net.sum(),2),'unresolved',int(t.unresolved.sum()),flush=True)
        del g
    pd.DataFrame(rows).to_csv(OUT/f'{period}_metrics.csv',index=False)
    pd.DataFrame(scores).to_csv(OUT/f'{period}_daily.csv',index_label='date')
    dump(OUT/f'{period}_audit.json',audits)
    return pd.DataFrame(rows),pd.DataFrame(scores),ledgers


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--fixtures-only',action='store_true');args=ap.parse_args()
    fixtures()
    if args.fixtures_only:return
    m,daily,ledgers=run_period('design')
    score={mode:daily[[c for c in daily if c.endswith(f'exit{mode}')]].mean(axis=1) for mode in (0,1)}
    difference=score[1]-score[0];bounds=ci(difference)
    relative=int(score[1].sum()>score[0].sum())
    conclusive=bounds[0]>0 or bounds[1]<0
    chosen=relative if conclusive else 0
    chosen_m=m[(m['mode']==chosen)&(m.side=='whole')]
    z=score[chosen];dt=float(z.mean()/z.std()*np.sqrt(len(z))) if z.std()>0 else float('nan')
    gate=dict(net_positive=bool(z.sum()>0),daily_t_at_least_2=bool(dt>=2),
        three_contexts_positive=int((chosen_m.net>0).sum())>=3,
        total_positions_at_least_100=int(chosen_m.trades.sum())>=100,
        thirty_positions_per_context=bool((chosen_m.trades>=30).all()),
        all_paths_resolved=int(chosen_m.unresolved.sum())==0)
    clean=sum(t.loc[~t.roll_flag.astype(bool),'net'].sum() for n,t in ledgers.items() if n.endswith(f'exit{chosen}'))/4
    gate['positive_excluding_roll_flags']=bool(clean>0)
    # Execute only the frozen chosen style under the preregistered adverse-path diagnostic.
    adverse_rows=[]
    for market,cache,pv in (('NQ','g24.pkl',2.),('ES','ge.pkl',5.)):
        with (ROOT/'scratch_data'/cache).open('rb') as f:g=pickle.load(f)
        n=int(np.searchsorted(g.ts,np.datetime64('2023-01-01')))
        for name in ('o','h','l','c','v','ts','dates','last_j'):setattr(g,name,getattr(g,name)[:n])
        g.D=n;g.trading=g.trading[g.trading<n]
        for k in (15,30):
            sig,_,ids=features(g,k,'2018-01-01','2023-01-01');t,ff,extra=execute(g,sig,ids,k,pv,chosen,True)
            t.to_csv(OUT/f'design_{market}_{k}_adverse_trades.csv',index=False)
            adverse_rows.append(dict(context=f'{market}_{k}',net=float(t.net.sum()),unresolved=int(t.unresolved.sum())))
        del g
    gate['positive_adverse_first']=sum(x['net'] for x in adverse_rows)>0
    selection=dict(preregistration=PLAN,two_protocols_eight_context_cells=True,
        selection_statistic='equal-context design net; paired20-day90% difference interval',
        design_totals={k:float(v.sum()) for k,v in score.items()},partial_minus_milestone_90_ci=bounds,
        relative_higher_net=relative,conclusive_exit_difference=conclusive,chosen_exit=chosen,
        chosen_design_daily_t=dt,net_excluding_roll_flags=clean,adverse_diagnostic=adverse_rows,
        gate=gate,design_pass=all(gate.values()),recent_returns_computed=False,
        native_micro_price_volume_parity=False)
    dump(OUT/'selection.json',selection)
    if selection['design_pass']:
        run_period('recent',chosen);selection['recent_returns_computed']=True;dump(OUT/'selection.json',selection)
    manifest=dict(plan_commit=PLAN,parameters=PARAMS,script_sha256=sha(__file__),
        helpers={p:sha(ROOT/'analysis'/p) for p in ['grid24.py','candidates.py','metrics.py','codex_s03_calendar.py','replica.py']},
        caches={p:sha(ROOT/'scratch_data'/p) for p in ['g24.pkl','ge.pkl']},
        versions=dict(python=sys.version,numpy=np.__version__,pandas=pd.__version__),
        trial_count=dict(exit_protocols=2,contexts=4,design_cells=8,adverse_cells=4,
                         recent_cells=4 if selection['recent_returns_computed'] else 0),
        limitations=['Assumed entry settings, not author parity.','Mini-price/volume, micro quantity/cost proxy.',
            'Intraminute ordering inferred, not tick verified.','Unadjusted continuous rolls only broadly flagged.',
            'Unknown paths retained; resolved-only metrics cannot qualify unresolved data.'])
    dump(OUT/'manifest.json',manifest);print(json.dumps(selection,indent=2),flush=True)


if __name__=='__main__':main()
