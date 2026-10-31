"""Read-only accounting / exit-minute adapter audit. No signals, strategy backtest or account simulation.
Exact source + trade ledger: Claude SHA 16145ab15c09fa9489a58ef651f5711c1ef2599f.
Writes only own scratch report JSON.
"""
import ast, io, json, pathlib, subprocess, types
import numpy as np
import pandas as pd
REPO=pathlib.Path(__file__).resolve().parents[1]
OUT=REPO/'analysis/outputs/codex_weekly_cross_review_20261030'
OUT.mkdir(parents=True,exist_ok=True)
SHA='16145ab15c09fa9489a58ef651f5711c1ef2599f'
def source(path): return subprocess.check_output(['git','show',f'{SHA}:{path}'],cwd=REPO)
ns={'np':np,'POINT_VALUE':20.,'COST':7.25,'SLIP':.25}
for f,names in [('analysis/funded_lab.py',['with_slippage']),('analysis/portfolio.py',['paths'])]:
    m=ast.parse(source(f)); code=ast.Module(body=[n for n in m.body if isinstance(n,ast.FunctionDef) and n.name in names],type_ignores=[]); exec(compile(code,f,'exec'),ns)
g=types.SimpleNamespace(o=np.array([[100.,100.]]),l=np.array([[99.,80.]]),h=np.array([[101.,101.]]))
fixtures=[]
for kind in ['stop',0,'target',1]:
    t=pd.DataFrame([dict(day=0,j0=0,j1=1,side=1,entry=100.,exit=90. if kind in ['stop',0] else 110.,kind=kind)])
    slipped=ns['with_slippage'](t)
    fixture_g=g if kind in ['stop',0] else types.SimpleNamespace(o=np.array([[100.,109.]]),l=np.array([[99.,108.]]),h=np.array([[101.,111.]]))
    w,r=ns['paths'](fixture_g,slipped)
    fixtures.append(dict(kind=kind,slips=int(slipped.slips.iloc[0]),exit=float(slipped.exit.iloc[0]),exit_minute_worst_per_MNQ=float(w[0,1]/10),close_per_MNQ=float(r[0,-1]/10)))
t=pd.read_csv(io.BytesIO(source('checks/candidates/swing_target/codex_be_trades.csv')),parse_dates=['date'])
old=ns['with_slippage'](t.assign(kind=t.reason)); corrected=ns['with_slippage'](t)
res={'sha':SHA,'fixtures':fixtures,'ledger_rows':len(t),'kind_counts':t.kind.value_counts().to_dict(),'reason_counts':t.reason.value_counts().to_dict(),
     'extra_cost_string_vs_numeric_per_NQ':float(((corrected.exit-old.exit)*t.side*20).sum()),
     'string_kind_net_minus_ledger_net_per_NQ':float((((old.exit-old.entry)*old.side*20-7.25)-t.net).sum())}
# Reconstruct the existing recorded paths only, using bars and holiday repair from this SHA.
# No entry/exit decisions are generated here.
t['raw_date']=t.date.dt.strftime('%Y%m%d').astype(int)
g=types.SimpleNamespace(**{k:np.full((len(t),1440),np.nan) for k in ['o','h','l','c']})
lookup={d:i for i,d in enumerate(t.raw_date)}
for year in sorted(t.date.dt.year.unique()):
    bar=pd.read_csv(io.BytesIO(source(f'data/NQ_1min_{year}.csv')),usecols=['date','time','open','high','low','close'])
    bar=bar[bar.date.isin(lookup)]
    rows=bar.date.map(lookup).to_numpy(int); cols=((bar.time//100)*60+bar.time%100).to_numpy(int)
    for key,col in [('o','open'),('h','high'),('l','low'),('c','close')]: getattr(g,key)[rows,cols]=bar[col].to_numpy(float)
old=t.assign(day=np.arange(len(t)),kind=t.reason).copy(); corrected=t.assign(day=np.arange(len(t))).copy()
repairs=[]
for i in np.flatnonzero(t.apex_flat_violation):
    last=np.where(np.isfinite(g.c[i,:901]))[0].max()
    for x in [old,corrected]: x.loc[i,['j1','exit','kind']]=[last,g.c[i,last],2]
    repairs.append(str(t.date[i].date()))
wo,ro=ns['paths'](g,ns['with_slippage'](old)); wc,rc=ns['paths'](g,ns['with_slippage'](corrected))
low_o=wo.min(axis=1); low_c=wc.min(axis=1); delta=(low_c-low_o)/10
res['frozen_recorded_daily_paths']={'holiday_repair_dates':repairs,'corrected_minus_original_close_per_MNQ_total':float((rc[:,-1]-ro[:,-1]).sum()/10),
    'daily_min_changed_days':int((np.abs(delta)>1e-8).sum()),'daily_min_lift_max_per_MNQ':float(delta.max()),
    'daily_min_lift_max_date':str(t.date[delta.argmax()].date()),
    'examples':pd.DataFrame({'date':t.date.astype(str),'reason':t.reason,'original_daily_low_per_MNQ':low_o/10,'corrected_daily_low_per_MNQ':low_c/10,'difference':delta}).sort_values('difference',ascending=False).head(6).to_dict('records')}
# Match recorded same-day protective exits to their exit-minute raw bars.
z=t[(t.kind==0)&~t.apex_flat_violation].copy(); row=z.index.to_numpy(); minute=z.j1.to_numpy()
z['slipped_exit']=z.exit-z.side*.5
z['raw_time']=(z.j1//60)*100+z.j1%60
z['low']=g.l[row,minute]; z['high']=g.h[row,minute]; assert z.low.notna().all()
z['bar_adverse_px']=np.where(z.side>0,z.low,z.high)
z['excess_adverse_per_MNQ']=np.maximum(0,(z.slipped_exit-z.bar_adverse_px)*z.side*2)
cols=['date','reason','side','entry','exit','slipped_exit','raw_time','low','high','excess_adverse_per_MNQ']
res['protective_exit_bar_check']={'matched':len(z),'with_excess_adverse':int((z.excess_adverse_per_MNQ>0).sum()),'max_excess_per_MNQ':float(z.excess_adverse_per_MNQ.max()),
 'examples':z.sort_values('excess_adverse_per_MNQ',ascending=False)[cols].head(6).assign(date=lambda x:x.date.astype(str)).to_dict('records')}
(OUT/'kind_adapter_audit.json').write_text(json.dumps(res,indent=2)+'\n')
print(json.dumps(res,indent=2))
