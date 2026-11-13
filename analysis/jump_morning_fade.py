"""Morning jump fade: POST-HOC lead from analysis/jump_tuning_demo.py (found on the whole window, 4,368 versions looked at; not a
candidate). Fade a 5-min bar with |J| > 3 that closes 07:00-09:59 CT: enter against it at the next minute, stop 1.5 x the bar's
range, target 0.3 x the stop (0.45 x range), out after 240 min / 15:55. Costs $7.25 + 1 tick per market / stop fill, 1-min fills.
  tools/run_stamped.sh analysis/jump_morning_fade.py > analysis/outputs/jump_morning_fade_output.txt
"""
import sys; sys.path.insert(0,'analysis'); import warnings; warnings.filterwarnings('ignore')
import numpy as np, pandas as pd, jump_lib as L, jump_study as S
b=L.bars(); M=S.Mkt(); yr=b.ts.dt.year.to_numpy(); sgn=np.sign(b.r).fillna(0).to_numpy(); aJ=b.J.abs().to_numpy()
hr=((b.ts-pd.Timedelta(minutes=1)).dt.hour).to_numpy()   # hour of the entry minute ~ bar close hour
hc=b.ts.dt.hour.to_numpy()
ALL=yr>=2018
def L1(t,lab):
    if len(t)<5: print(lab,'n',len(t)); return
    x=t.net; y=pd.DatetimeIndex(t.ts).year
    f=lambda z: f"n {len(z):4d} win {np.mean(z>0):5.1%} ${z.mean():6.1f} PF {z[z>0].sum()/max(1,-z[z<0].sum()):4.2f} t {z.mean()/z.std()*np.sqrt(len(z)):5.2f}"
    print(f"{lab:<34} all {f(x)} | 18-22 {f(x[y<=2022])} | 23+ {f(x[y>=2023])} | R$ {t.R.mean()*20:5.0f}")
print('--- neighbours, with costs, one at a time')
for thr in (3,3.5,4):
    for k in (1.0,1.5,2.0):
        m=ALL&(aJ>thr)&np.isin(hc,[7,8,9])
        L1(S.trades(b,M,m,-sgn,'rng',k,tp=0.3,hold=240),f'fade J>{thr} k{k} h7-9')
print('--- base = fade J>3 k1.5; by entry hour (all hours)')
base=S.trades(b,M,ALL&(aJ>3),-sgn,'rng',1.5,tp=0.3,hold=240,one=False); base['h']=hc[base.q]; base['hm']=b.hhmm.to_numpy()[base.q]
for h,g in base.groupby('h'): L1(g,f'hour {h}')
print('--- inside 7-9: by bar close time')
g=base[base.h.isin([7,8,9])]
for a,c in ((700,729),(730,735),(736,829),(830,835),(836,859),(900,905),(906,959)): L1(g[(g.hm>=a)&(g.hm<=c)],f'{a}-{c}')
t=S.trades(b,M,ALL&(aJ>3)&np.isin(hc,[7,8,9]),-sgn,'rng',1.5,tp=0.3,hold=240)
y=pd.DatetimeIndex(t.ts).year
print('by year:',"  ".join(f"{k} ${v.net.sum():,.0f} ({len(v)}, {np.mean(v.net>0):.0%})" for k,v in t.groupby(y)))
L1(t[t.side>0],'longs'); L1(t[t.side<0],'shorts'); print('exit mix',t.why.value_counts().to_dict(),'avg mins',t.mins.mean().round(1), 'worst',t.net.min(), 'top5 share',t.net.nlargest(5).sum()/t.net.sum())
for tp in (0.2,0.3,0.5,1.0): L1(S.trades(b,M,ALL&(aJ>3)&np.isin(hc,[7,8,9]),-sgn,'rng',1.5,tp=tp,hold=240),f'tp {tp}')
for hold in (30,60,120): L1(S.trades(b,M,ALL&(aJ>3)&np.isin(hc,[7,8,9]),-sgn,'rng',1.5,tp=0.3,hold=hold),f'hold {hold}')
