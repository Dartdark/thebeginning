"""Rating of the funded set (2026-10-12): per-strategy stats at funded sizes, payout distribution,
how accounts blow up, leave-one-out, cushion sizing / staged sizing / payout buffer, slippage stress.
Blocks rate1..rate4; expects the pickled funded lab from a scratch run. Record of the test."""

# ======================= rate1
# import sys,pickle,warnings;warnings.filterwarnings('ignore');sys.path.insert(0,'analysis')
# import numpy as np,pandas as pd
# import funded_sim as F
# SP='/tmp/claude-0/-home-user-thebeginning/7f50794d-c1bb-567e-997c-15fdea9b8719/scratchpad/'
# lab=pickle.load(open(SP+'lab.pkl','rb'))
# plan={"VB":3,"ONB_ML_MC":("risk",300),"OND_MC":("risk",500),"EOS":("risk",500)}
# names,b=lab._base(plan); b=np.floor(b+1e-9)
# dates=pd.DatetimeIndex(lab.g.ts[lab.tr]); yr=dates.year
# P=pd.DataFrame({k:lab.C[k]*b[i] for i,k in enumerate(names)},index=dates)   # $ per day at funded sizes (with slippage)
# P["ALL"]=P.sum(1)
# print("== per strategy at funded size ($/day series, 2018-2026)")
# for k in names+["ALL"]:
#     x=P[k]; t=x[x!=0]; eq=x.cumsum(); dd=(eq-eq.cummax()).min()
#     print(f"{k:<10} trade days/yr {len(t)/8.8:5.0f}  win {np.mean(t>0):.0%}  avg/trade ${t.mean():5.0f}  PF {t[t>0].sum()/-t[t<0].sum():.2f}  total/yr ${x.sum()/8.8:7,.0f}  maxDD ${dd:8,.0f}  worst day ${x.min():6,.0f}  avg contracts {np.mean(b[names.index(k)][x!=0]) if k!='ALL' else 0:.1f}")
# print("\nyearly $ (funded sizes):"); print(P.groupby(yr).sum().round(0).astype(int).T.to_string())
# m=P.ALL.resample("ME").sum(); print("\nmonths negative:",(m<0).mean().round(2),"worst month",m.min().round(),"best",m.max().round(), "avg",m.mean().round())
# x=P.ALL; print("days with trade",(x!=0).mean().round(2),"daily mean",x.mean().round(1),"sd",x.std().round(1),"days >= $250",(x>=250).mean().round(3),"per year",((x>=250).sum()/8.8).round())
# eq=x.cumsum(); dd=eq-eq.cummax(); print("portfolio maxDD",dd.min().round(),"on",dd.idxmin().date(),"; rolling 20-day worst",x.rolling(20).sum().min().round())
# print("\ncorrelation of daily P&L:"); print(P[names].corr().round(2).to_string())
# # payout distribution
# W=np.stack([lab.W[k] for k in names]); C=np.stack([lab.C[k] for k in names])
# for h in (250,500):
#     st=np.arange(0,lab.D-h); r=F.simulate_sized(W,C,lab._base(plan)[1],horizon=h,starts=st)
#     n=r["payouts"]; bl=r["blown"].astype(bool)
#     print(f"\n== horizon {h} days: expected ${r['paid'].mean():,.0f}; median ${np.median(r['paid']):,.0f}; blown {bl.mean():.0%}")
#     print("   payouts count distribution:",{i:f"{np.mean(n==i):.0%}" for i in range(7)})
#     print(f"   blown accounts: median day blown {np.median(r['days'][bl]):.0f}, paid before blowing ${r['paid'][bl].mean():,.0f}, blown with 0 payouts {np.mean(bl&(n==0)):.0%}")
#     print(f"   not blown: avg ${r['paid'][~bl].mean():,.0f}; days to first payout median {np.median(r['first'][r['first']>0]):.0f}")
#     print("   by start year:",pd.Series(r['paid']).groupby(yr[st]).mean().round().astype(int).to_dict())
#     print("   blown by start year:",pd.Series(bl).groupby(yr[st]).mean().round(2).to_dict())
# pickle.dump((P,names,b),open(SP+'rateP.pkl','wb'))

# ======================= rate2
# import sys,pickle,warnings;warnings.filterwarnings('ignore');sys.path.insert(0,'analysis')
# import numpy as np,pandas as pd
# import funded_sim as F
# SP='/tmp/claude-0/-home-user-thebeginning/7f50794d-c1bb-567e-997c-15fdea9b8719/scratchpad/'
# lab=pickle.load(open(SP+'lab.pkl','rb'))
# plan={"VB":3,"ONB_ML_MC":("risk",300),"OND_MC":("risk",500),"EOS":("risk",500)}
# def sc(p,**kw):
#     a=lab.score(p,250,**kw); b=lab.score(p,500,**kw)
#     return f"1y ${a['expected']:6,.0f} (2023+ ${a['s2023_on']:5,.0f}) blown {a['blown']:.0%} 1st payout {a['days_to_1st']:.0f}d | 2y ${b['expected']:6,.0f} (2023+ ${b['s2023_on']:5,.0f}) blown {b['blown']:.0%}"
# print("Current                                  ",sc(plan))
# print("-- leave one out")
# for k in plan:
#     p=dict(plan); p.pop(k); print(f"  without {k:<32}",sc(p))
# print("-- cushion sizing: size x clip((balance - drawdown floor)/ref, fmin, fmax)")
# for ref,fmin,fmax in ((2000,0.5,1.0),(2000,0.5,1.5),(3000,0.5,1.5),(4000,0.5,2.0),(2000,0.25,1.0),(2500,0.5,1.25)):
#     print(f"  ref {ref} f in [{fmin},{fmax}]{'':<14}",sc(plan,fmin=fmin,fmax=fmax,ref=ref))
# print("-- stage: size multiplier by number of payouts made [0,1,2,...]")
# for st in ((0.5,1,1,1,1,1),(0.7,1,1,1,1,1),(0.7,1.3,1.3,1.3,1.3,1.3),(1,1.3,1.5,1.5,1.5,1.5),(0.5,1,1.5,1.5,1.5,1.5)):
#     print(f"  stage {st}{'':<5}",sc(plan,stage=np.array(st,float)))
# print("-- keep a buffer above safety net before requesting (keep $)")
# for kp in (500,1000):
#     print(f"  keep {kp}{'':<31}",sc(plan,keep=float(kp)))

# ======================= rate3
# exec(open("/tmp/claude-0/-home-user-thebeginning/7f50794d-c1bb-567e-997c-15fdea9b8719/scratchpad/rate2.py").read().split('print("Current')[0])
# cs=dict(fmin=0.5,fmax=1.0,ref=2000)
# print("Cushion sizing (ref 2000, [0.5,1])          ",sc(plan,**cs))
# p=dict(plan); p.pop("OND_MC"); print("  ... without Overnight Drift               ",sc(p,**cs))
# for k,v in (("VB",4),("ONB_ML_MC",("risk",400)),("EOS",("risk",700))):
#     p=dict(plan); p[k]=v; print(f"  ... {k} -> {v}{'':<20}"[:46],sc(p,**cs))
# p=dict(plan); p["VB"]=4; p["ONB_ML_MC"]=("risk",400); p["OND_MC"]=("risk",700); p["EOS"]=("risk",700); print("  ... all ~1.35x bigger                       ",sc(p,**cs))
# print("  ... + keep $500                            ",sc(plan,keep=500.0,**cs))
# # stress: 1 extra tick per fill ($0.50 per MNQ per fill, 2 fills)
# for k in plan:
#     tr=lab.C[k]!=0; lab.C[k]=lab.C[k]-1.0*tr; lab.W[k]=lab.W[k]-1.0*tr[:,None]
# print("Stress +1 tick/fill: current                 ",sc(plan))
# print("Stress +1 tick/fill: cushion sizing          ",sc(plan,**cs))

# ======================= rate4
# exec(open("/tmp/claude-0/-home-user-thebeginning/7f50794d-c1bb-567e-997c-15fdea9b8719/scratchpad/rate2.py").read().split('print("Current')[0])
# cs=dict(fmin=0.5,fmax=1.0,ref=2000)
# for lbl,p in (("VB3 ONB400 OND500 EOS700",{"VB":3,"ONB_ML_MC":("risk",400),"OND_MC":("risk",500),"EOS":("risk",700)}),
#               ("VB3 ONB400 EOS700 (no OND)",{"VB":3,"ONB_ML_MC":("risk",400),"EOS":("risk",700)}),
#               ("VB2 ONB400 OND500 EOS700",{"VB":2,"ONB_ML_MC":("risk",400),"OND_MC":("risk",500),"EOS":("risk",700)}),
#               ("VB3 ONB400 OND300 EOS700",{"VB":3,"ONB_ML_MC":("risk",400),"OND_MC":("risk",300),"EOS":("risk",700)})):
#     print(f"{lbl:<30} cushion",sc(p,**cs))
