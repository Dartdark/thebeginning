"""Opposing-position overlap in the funded benches (Codex portfolio audit 2026-10-31). portfolio.paths marks each trade at its own
adverse extreme per minute (longs at the low, shorts at the high) and the benches sum them, so minutes with NQ longs AND shorts
open count the minority side's range twice. Measures how often and how much (min(long, short) MNQ x minute range x \$2).
Overnight Tick is excluded (stored as one day-level worst, not per minute).  python3 analysis/opposing_overlap_check.py"""
import sys; sys.argv=["x","scratch_data"]; sys.path.insert(0,"analysis")
import numpy as np, warnings; warnings.filterwarnings("ignore")
import funded_lab as FL, portfolio as PF
store={}
orig=FL.Lab.add
def add(self,name,trades,*a,**k):
    t=FL.with_slippage(trades) if k.get("slippage",True) else trades
    store[name]=t; return orig(self,name,trades,*a,**k)
FL.Lab.add=add
import overnight_tick_bench as OTB, swing_target_bench as STB
NQ={"VB","VB_N","VB_F","ONB_ML2_MC","MON_MC","EOS","LDF_MC","NFP_MC","MON_BR_MC","RS","RS_L","DT","ST"}
for which,plan in ((50,STB.plans50()["50K plan"]),(150,__import__("plan150_integer_test").plans()["all 1.5 -> 1"])):
    store.clear(); lab=OTB.lab_for(which); g=lab.g
    from build_lab import REPORTS; from portfolio import load_mc
    for k2,(f2,_) in REPORTS.items(): store.setdefault(k2, FL.with_slippage(load_mc(g,f2)))
    pass
    D,M=g.o.shape; pos=np.zeros((D,M)); lo=np.zeros((D,M)); sh=np.zeros((D,M))
    names,b=lab._base(plan)
    for k,bk in zip(names,b):
        src="VB" if k in("VB_N","VB_F") else k
        if k not in NQ or src not in store: continue
        t=store[src]; q=t["qty"].to_numpy() if "qty" in t else np.ones(len(t))
        for (d,j0,j1,s),qq in zip(t[["day","j0","j1","side"]].to_numpy(int),q):
            i=np.searchsorted(lab.tr,d); w=bk[i] if i<len(bk) and lab.tr[i]==d else np.nanmedian(bk)
            (lo if s>0 else sh)[d,j0:j1+1]+=qq*w
    print(which, "missing:", [k for k in names if k in NQ and ("VB" if k in ("VB_N","VB_F") else k) not in store])
    both=(lo>0)&(sh>0); rng=np.nan_to_num(g.h-g.l)
    over=np.minimum(lo,sh)*rng*2.0   # $2/pt per MNQ, minority side's double-counted range
    days=both.any(1)
    print(f"{which}K: minutes long+short at once {both.sum():,} on {days.sum()} of {len(lab.tr)} days; "
          f"overstated worst per such minute avg ${over[both].mean():.0f}, max ${over.max():,.0f}; worst day-max ${np.sort(over.max(1))[-5:].round(0)}")
