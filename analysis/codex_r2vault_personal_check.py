import sys, json, pickle
from pathlib import Path
sys.path.insert(0, 'agents/codex/runtime/or_pullback_python')
sys.path.insert(0, 'analysis')
import numpy as np
import pandas as pd

ROOT = Path('analysis/outputs/codex_r2vault')
with open('scratch_data/g24.pkl', 'rb') as f: g = pickle.load(f)
with open('agents/codex/runtime/anson_personal_baseline.pkl', 'rb') as f: baseline = pickle.load(f)
assert baseline.shape[1] == 14 and not baseline.isna().any().any()
days = pd.DatetimeIndex(baseline.index)
def near(a, b): np.testing.assert_allclose(a, b, rtol=0, atol=2e-7)
def stamp(row, j, phase):
    return pd.Timestamp(g.ts[int(row)]) + pd.Timedelta(minutes=int(j)-1, seconds=0 if phase=='open' else 30)
def book_day(s):
    target = s.normalize()+pd.Timedelta(days=int(s > s.normalize()+pd.Timedelta(hours=16)))
    return int(days.searchsorted(target))
def maxdd(v):
    c = np.r_[0., np.asarray(v).cumsum()]
    return float((np.maximum.accumulate(c)-c).max())

results=[]
for model in ['et_raw', 'ct_raw']:
    dest=ROOT/'personal'/model
    t=pd.read_csv(ROOT/'replay'/(model+'_trades.csv'))
    saved=pd.read_csv(dest/'candidate_daily.csv',parse_dates=['date']).set_index('date').iloc[:,0]
    out=np.zeros(len(days))
    for x in t.itertuples():
        start=stamp(x.entry_row,x.entry_j,x.entry_phase)
        end=stamp(x.exit_row,x.exit_j,x.exit_phase)
        assert end <= days[-1]+pd.Timedelta(hours=16)
        a,b=book_day(start),book_day(end)
        out[a]-=1.275+.5
        marks=[]
        for k in range(a,b):
            row=int(np.searchsorted(g.ts, np.datetime64(days[k])))
            if row==len(g.ts) or pd.Timestamp(g.ts[row]).normalize()!=days[k].normalize(): continue
            js=np.flatnonzero(np.isfinite(g.c[row,:961]))
            if len(js):
                j=int(js[-1]); s=pd.Timestamp(g.ts[row])+pd.Timedelta(minutes=j)
                if start<s<end: marks.append((k,float(g.c[row,j])))
        previous=x.entry
        for k,p in marks:
            out[k]+=(p-previous)*2
            previous=p
        out[b]+=(x.exit-previous)*2-(0. if x.kind==1 else .5)
    near(saved.to_numpy(),out)
    near(saved.sum(), (2*t.gross_points-1.775-np.where(t.kind==1,0.,.5)).sum())
    plans=pd.read_csv(dest/'daily_portfolios.csv',index_col=0,parse_dates=True)
    assert len(plans.columns)==21
    sets={
      'A':['TwinContinuation','OvernightBiasML','BridgeMondayLong','CLSundayFade_perMCL','NFPFade'],
      'B':['TwinContinuation','OvernightBiasML','BridgeMondayLong','CLSundayFade_perMCL','NFPFade','ExpirationOpenShort'],
      'C':['TwinContinuation','OvernightBiasML','BridgeMondayLong','CLSundayFade_perMCL','NFPFade','ExpirationOpenShort','VaultBreak'],
      'D':['TwinContinuation','OvernightBiasML','BridgeMondayLong','CLSundayFade_perMCL','NFPFade','ExpirationOpenShort','VaultBreak','RelativeStrength','ESMOCFollow_perMES'],
      'FULL':list(baseline)}
    for name in plans:
        group,allocation=name.split('__')
        v=baseline[sets[group]].sum(axis=1).to_numpy()
        if allocation in ['EMPTY_VB','REPLACE_VB_1']: v=v-baseline.VaultBreak.to_numpy()
        if allocation in ['ADD_1','REPLACE_VB_1']: v=v+out
        if allocation=='ADD_2': v=v+2*out
        near(plans[name],v)
    summary=pd.read_csv(dest/'mc_summary.csv'); effects=pd.read_csv(dest/'paired_effects.csv')
    ns=ne=nh=0
    for cohort,lo in [('2018_plus','2018-01-01'),('2025_plus_replication','2025-01-01')]:
        archive=np.load(dest/('paired_mc_'+cohort+'.npz'))
        ix=np.load(dest/('paired_histories_'+cohort+'.npy'))
        assert ix.shape==(5000,252)
        for row in summary[summary.cohort==cohort].itertuples():
            p,d=archive[row.config+'__profit'],archive[row.config+'__dd']
            vals=plans.loc[plans.index>=lo,row.config].to_numpy()[ix]
            c=vals.cumsum(axis=1)
            dd=(np.maximum.accumulate(np.c_[np.zeros(len(ix)),c],axis=1)[:,1:]-c).max(axis=1)
            near(p,c[:,-1]); near(d,dd)
            near([row.profit_p5,row.profit_p50,row.profit_p95,row.profit_mean,row.p_losing_year,row.dd_p50,row.dd_p95,row.capital_20pct],
                 [np.quantile(p,.05),np.median(p),np.quantile(p,.95),p.mean(),np.mean(p<=0),np.median(d),np.quantile(d,.95),np.quantile(d,.95)/.2])
            ns+=1
        for row in effects[effects.cohort==cohort].itertuples():
            p,d=archive[row.config+'__profit'],archive[row.config+'__dd']
            bp,bd=archive[row.reference+'__profit'],archive[row.reference+'__dd']
            scale=np.quantile(bd,.95)/np.quantile(d,.95)
            delta=(plans.loc[plans.index>=lo,row.config]-plans.loc[plans.index>=lo,row.reference]).to_numpy()
            near([row.profit_mean_delta,row.dd_mean_delta,row.profit_p50_delta,row.dd_p95_delta,row.capital_20pct_delta,row.paired_profit_delta_p5,row.paired_profit_delta_p50,row.paired_profit_delta_p95,row.p_paired_profit_delta_le_zero,row.historical_annual_mean_delta,row.same_dd95_continuous_scale,row.same_dd95_median_profit_delta,row.p_profit_beats_reference],
                 [(p-bp).mean(),(d-bd).mean(),np.median(p)-np.median(bp),np.quantile(d,.95)-np.quantile(bd,.95),(np.quantile(d,.95)-np.quantile(bd,.95))/.2,np.quantile(p-bp,.05),np.median(p-bp),np.quantile(p-bp,.95),np.mean(p<=bp),delta.mean()*252,scale,np.median(p)*scale-np.median(bp),np.mean(p>bp)+.5*np.mean(p==bp)])
            ne+=1
    periods={'2018_22':('2018-01-01','2023-01-01'),'2018_24_author_IS':('2018-01-01','2025-01-01'),'2023_plus':('2023-01-01','2100-01-01'),'2025_plus_replication':('2025-01-01','2100-01-01'),'2018_plus':('2018-01-01','2100-01-01')}
    periods.update({str(y):(str(y)+'-01-01',str(y+1)+'-01-01') for y in days.year.unique()})
    hist=pd.read_csv(dest/'historical_summary.csv')
    for row in hist.itertuples():
        lo,hi=periods[row.period]
        v=plans.loc[(plans.index>=lo)&(plans.index<hi),row.config].to_numpy()
        near([row.total,row.days,row.max_dd_including_start],[v.sum(),len(v),maxdd(v)])
        nh+=1
    results.append(dict(model=model,trades_booked=len(t),daily_mark_reconciliation=True,configurations=21,mc_summary_rows=ns,paired_effect_rows=ne,historical_rows=nh,net_micro=float(saved.sum())))
out=dict(status='PASS',baseline_legs=14,models=results,method='Independently recomputed saved daily booking and all saved paths; no new variant, history draw, or candidate price replay.',limitations='Does not certify author source parity or live stop residency; CI generation reviewed, not redrawn.')
(ROOT/'personal'/'saved_output_checks.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
