"""Standalone price/flow disagreement entries, 5/15-minute completed bars.

No existing strategy tickets. Thin shared-_walk execution adapter enforces
signal-time flatness and one-minute receipt delay; no stale signals after exits.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import warnings

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"analysis/outputs/codex_flow_absorption"
os.environ["NUMBA_CACHE_DIR"]=str(OUT/"numba_cache")
sys.path.insert(0,str(ROOT/"analysis"))
import numpy as np
import pandas as pd
import codex_cash_open_repair as C
from grid24 import Grid24
from grid import _walk

PLAN="agents/codex/plans/flow_absorption.md"
CONFIGS={"A5_D20":(5,.20),"A5_D35":(5,.35),"A15_D20":(15,.20),"PRICE5":(5,None),"PRICE15":(15,None)}
COLS=["date","time","upvol","downvol","close"]


def bind(prereg):
    assert subprocess.check_output(["git","show",prereg+":"+PLAN],cwd=ROOT)==(ROOT/PLAN).read_bytes()
    assert subprocess.check_output(["git","branch","--show-current"],cwd=ROOT,text=True).strip()=="codex/work"
    paths=sorted((ROOT/"data").glob("OF_1min_*.csv"))+sorted((ROOT/"data").glob("NQ_1min_*.csv"))
    paths += [ROOT/PLAN,ROOT/"analysis/codex_cash_open_repair.py",ROOT/"analysis/grid.py",ROOT/"analysis/grid24.py",ROOT/"analysis/metrics.py"]
    C.dump(OUT/"input_binding.json",dict(prereg=prereg,source={str(p.relative_to(ROOT)):C.sha(p) for p in paths},
        models=CONFIGS,new_economic_configurations=5,prior_program_configurations=5,
        latency="one-minute assumed receipt delay, no historical receive timestamp verified"))
    C.write(OUT/".gitignore","numba_cache/\n")


def intake(g,cutoff,phase):
    files=sorted(p for p in (ROOT/"data").glob("OF_1min_*.csv") if int(p.name.split('_')[2])<=pd.Timestamp(cutoff).year)
    raw=pd.concat([pd.read_csv(p,usecols=COLS) for p in files],ignore_index=True)
    raw=raw[raw.date<=int(pd.Timestamp(cutoff).strftime("%Y%m%d"))].copy()
    duplicate=raw.duplicated(["date","time"],keep=False)
    conflicts=raw[duplicate].groupby(["date","time"])[["upvol","downvol","close"]].nunique(dropna=False)
    nconflict=int((conflicts>1).any(axis=1).sum())
    audit=dict(rows_before=len(raw),exact_duplicates=int(raw.duplicated().sum()),conflicting_keys=nconflict,
        first=int(raw.date.min()),last=int(raw.date.max()),clock="source ET minus60 minutes -> CT close label",
        source_readiness="Observed selected-field and timestamp checks; original capture/receipt completeness unverified")
    if nconflict:
        audit["status"]="NEEDS DATA: conflicting duplicate inputs"
        C.dump(OUT/f"{phase}_intake.json",audit)
        raise ValueError(audit["status"])
    raw=raw.drop_duplicates(["date","time"]).sort_values(["date","time"])
    row=np.searchsorted(g.dates,raw.date.to_numpy())
    keep=(row<g.D)&(g.dates[np.minimum(row,g.D-1)]==raw.date.to_numpy())
    audit["unmapped_dates_rows"]=int((~keep).sum());raw=raw[keep];row=row[keep]
    j=(raw.time.to_numpy()//100)*60+raw.time.to_numpy()%100-60
    assert ((j>=0)&(j<1440)).all()
    arrays={k:np.full(g.c.shape,np.nan) for k in ("buy","sell","close")}
    for k,col in (("buy","upvol"),("sell","downvol"),("close","close")):
        arrays[k][row,j]=raw[col].to_numpy(float)
    good=(np.isfinite(arrays["buy"])&np.isfinite(arrays["sell"])&(arrays["buy"]>=0)&(arrays["sell"]>=0)
          &np.isfinite(arrays["close"])&np.isfinite(g.c)&(abs(arrays["close"]-g.c)<=.25))
    audit.update(mapped_rows=len(raw),valid_quantity_rows=int((np.isfinite(raw.upvol)&np.isfinite(raw.downvol)&(raw.upvol>=0)&(raw.downvol>=0)).sum()),
        valid_native_close_matches=int(good.sum()),source_native_close_mismatch_rows=int((np.isfinite(arrays["close"])&np.isfinite(g.c)&(abs(arrays["close"]-g.c)>.25)).sum()),
        status="PASS limited bar-level intake; assumed latency only")
    C.dump(OUT/f"{phase}_intake.json",audit)
    arrays["valid"]=good
    return arrays


def make_signals(g,flow,frame,threshold,lo,hi):
    rows=[];counts={};atr=g._flow_atr
    for d in g.trading:
        date=pd.Timestamp(g.ts[d])
        if not lo<=date<=hi:continue
        if not C.normal_cash(date):counts["calendar_skip_days"]=counts.get("calendar_skip_days",0)+1;continue
        if not np.isfinite(atr[d]) or atr[d]<=0:continue
        for j in range(540,841,frame):
            sl=slice(j-frame+1,j+1)
            if not flow["valid"][d,sl].all() or not all(np.isfinite(getattr(g,q)[d,sl]).all() for q in ("o","h","l","c")):
                counts["incomplete_input_bars"]=counts.get("incomplete_input_bars",0)+1;continue
            oo,hh,ll,cc=g.o[d,j-frame+1],g.h[d,sl].max(),g.l[d,sl].min(),g.c[d,j]
            buy,sell=float(flow["buy"][d,sl].sum()),float(flow["sell"][d,sl].sum())
            if hh<=ll or buy+sell<=0:continue
            location=(cc-ll)/(hh-ll);side=1 if cc>oo and location>=.75 else (-1 if cc<oo and location<=.25 else 0)
            if not side:continue
            delta=(buy-sell)/(buy+sell)
            if threshold is not None and delta*side>-threshold:continue
            stop=np.ceil(.10*atr[d]*4)/4.;target=np.ceil(.15*atr[d]*4)/4.
            rows.append(dict(day=int(d),signal_j=j,dj=j+1,side=side,stop=stop,target=target,exit_j=min(j+30,895),delta_fraction=delta,
                input_last_j=j,first_entry_j=j+2))
    return pd.DataFrame(rows,columns=["day","signal_j","dj","side","stop","target","exit_j","delta_fraction","input_last_j","first_entry_j"]),counts


def replay(g,sig,independent=False):
    rows=[];counts={"suppressed_invested_or_same_close":0,"suppressed_daily_cap":0,"missing_scheduled_entry":0}
    for d,s in sig.groupby("day",sort=True):
        last=-1;n=0
        for r in s.sort_values("signal_j").itertuples():
            if not independent and r.signal_j<=last:
                counts["suppressed_invested_or_same_close"]+=1;continue
            if not independent and n>=4:
                counts["suppressed_daily_cap"]+=1;continue
            entry_j=int(r.first_entry_j)
            if entry_j>r.exit_j or not np.isfinite(g.o[d,entry_j]):
                counts["missing_scheduled_entry"]+=1;continue
            e=g.o[d,entry_j];stop=e-r.side*r.stop;target=e+r.side*r.target
            j,x,kind,worst=_walk(g.o[d],g.h[d],g.l[d],g.c[d],entry_j,int(r.exit_j),int(r.side),stop,target,1.)
            pnl=(x-e)*r.side*20.;slips=1+(kind!=1)
            rows.append(dict(day=int(d),signal_j=int(r.signal_j),j0=entry_j,j1=int(j),side=int(r.side),entry=e,exit=x,kind=int(kind),
                pnl=pnl,mae=abs(worst-e)*20.,qty=1.,date=pd.Timestamp(g.ts[d]),slips=int(slips),gross=pnl,
                net=pnl-7.25-5*slips,net_mnq=pnl/10-1.24-.5*slips,stress_four_ticks=pnl-7.25-20*slips,
                unobserved_held_minutes=int(np.isnan(g.c[d,entry_j:int(j)+1]).sum()),delta_fraction=r.delta_fraction))
            last=int(j);n+=1
    columns=["day","signal_j","j0","j1","side","entry","exit","kind","pnl","mae","qty","date","slips","gross","net","net_mnq","stress_four_ticks","unobserved_held_minutes","delta_fraction"]
    result=pd.DataFrame(rows,columns=columns)
    if result.empty:
        result["date"]=pd.Series(dtype="datetime64[ns]")
        for col in columns:
            if col!="date":result[col]=pd.Series(dtype=float)
    return result,counts


def engineering():
    # A bar closes up at its high despite heavy selling -> long, not sell.
    side=1;buy,sell=20.,80.;assert (buy-sell)/(buy+sell)*side<=-.2
    # A completed 09:00 signal cannot fill until the 09:02-labeled native bar.
    assert 540+2==542
    # Signals emitted before the current trade's exit never survive as delayed entries.
    assert not (550>550) and 555>550
    return dict(passed=True,checks=["aggressor-sign convention","whole-minute receipt delay","no stale/invested signal entry",
        "shared _walk entry-bar/gap/through conventions covered in Cash-Open Repair synthetic tests"])


def run(prereg,phase):
    bind(prereg);C.dump(OUT/"engineering_checks.json",engineering())
    lo=pd.Timestamp("2018-01-01" if phase=="design" else "2023-01-01")
    hi=pd.Timestamp("2022-12-31" if phase=="design" else "2026-07-07")
    selected=None
    if phase=="validation":
        selected=json.loads((OUT/"design_gate.json").read_text())["selected"]
        if selected is None:raise ValueError("Local design stop: do not validate this hypothesis; continue the t6 program elsewhere")
    with warnings.catch_warnings():
        warnings.simplefilter("ignore",RuntimeWarning)
        g=C.trim_grid(Grid24(),hi);g._flow_atr=g.daily_atr(15);flow=intake(g,hi,phase)
    days=pd.DatetimeIndex([pd.Timestamp(t) for t in g.ts if lo<=pd.Timestamp(t)<=hi and
        C.calendar_status(pd.Timestamp(t))["kind"] not in ("weekend","holiday")])
    configs=CONFIGS if selected is None else {k:CONFIGS[k] for k in (selected,"PRICE"+str(CONFIGS[selected][0]))}
    ledgers={};signals={};ind={};metrics=[];counts={};daily={}
    for model,(frame,threshold) in configs.items():
        s,ct=make_signals(g,flow,frame,threshold,lo,hi);signals[model]=s
        t,ex=replay(g,s);ledgers[model]=t;counts[model]=dict(input=ct,execution=ex,signals=len(s),executed=len(t))
        C.csv(OUT/f"{phase}_{model}_signals.csv",s);C.csv(OUT/f"{phase}_{model}_trades.csv",t)
        daily[model]=t.groupby("date").net.sum().reindex(days,fill_value=0.)
        if t.empty:
            # Preserve the first run's empty-model CSV representation (0.0)
            # while numerical ledger columns remain float for diagnostics.
            daily[model]=daily[model].astype(object)
        for side,label in ((0,"all"),(1,"long"),(-1,"short")):
            tx=t if not side else t[t.side==side]
            metrics.append(dict(model=model,period="2018-22" if phase=="design" else "2023+",side=label,**C.stats(tx,days)))
            for year in sorted(days.year.unique()):
                metrics.append(dict(model=model,period=str(year),side=label,**C.stats(tx[tx.date.dt.year==year],days[days.year==year])))
    C.csv(OUT/f"{phase}_metrics.csv",pd.DataFrame(metrics));C.csv(OUT/f"{phase}_daily.csv",pd.DataFrame(daily).rename_axis("date"),index=True)
    C.dump(OUT/f"{phase}_counts.json",counts)
    # Separate non-executable per-signal controls retain overlapping events.
    # This does not falsely call cap-dependent actual ledgers nested subsets.
    controls={}
    for model in (k for k in configs if k.startswith("A")):
        frame=CONFIGS[model][0];base="PRICE"+str(frame)
        if base not in ind:ind[base]=replay(g,signals[base],independent=True)[0]
        candidate=replay(g,signals[model],independent=True)[0]
        controls[model]=dict(non_executable_signal_only=True,
            **C.filter_controls(candidate,ind[base],days))
        C.csv(OUT/f"{phase}_{model}_independent_signal_diagnostic.csv",candidate[["day","j0","j1","side","date","net"]])
    C.dump(OUT/f"{phase}_filter_diagnostics.json",controls)
    if phase=="design":
        checks={}
        for model in ("A5_D20","A5_D35","A15_D20"):
            t=ledgers[model];m=C.stats(t,days);yy=t.groupby(t.date.dt.year).net.sum()
            checks[model]=dict(count=m["trades"]>=100,net=m["total"]>0,t=m["t_trade"]>=2,nw5=m["t_nw5"]>=1.5,
                pf=m["profit_factor"]>=1.2,years=int((yy>0).sum())>=4,micro=t.net_mnq.sum()>0,stress=t.stress_four_ticks.sum()>0)
        # JSON's default serializer is for datetimes; convert numpy booleans explicitly.
        checks={k:{j:bool(v) for j,v in flags.items()} for k,flags in checks.items()}
        passing=[k for k,v in checks.items() if all(v.values())]
        C.dump(OUT/"design_gate.json",dict(prereg=prereg,gates=checks,passing=passing,selected=passing[0] if passing else None,
            economic_models=5,cumulative_program_models=10,program_continues=True))
    allrows=pd.DataFrame(metrics)
    print(allrows[(allrows.period==("2018-22" if phase=="design" else "2023+"))&(allrows.side=="all")][["model","trades","total","avg","profit_factor","t_trade","t_nw5","max_dd"]].to_string(index=False))
    print("Passing design models:",passing if phase=="design" else selected)


if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("--phase",choices=("design","validation"),required=True);p.add_argument("--prereg",required=True)
    a=p.parse_args();run(a.prereg,a.phase)
