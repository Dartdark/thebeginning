"""Frozen quarterly walk-forward experiments; no order-routing capability.

python analysis/codex_rl3690996_train.py stocks|futures [design|validation]
"""
from pathlib import Path
import argparse
import gc
import json
import os
import time
import hashlib
import subprocess
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
RUNTIME=Path(os.environ.get("RL3690996_RUNTIME",str(ROOT/"agents/codex/runtime/rl3690996")))
os.environ.setdefault("MPLCONFIGDIR",str(RUNTIME/"matplotlib"))
os.environ.setdefault("XDG_CACHE_HOME",str(RUNTIME/"cache"))
import torch
torch.set_num_threads(1)
from stable_baselines3 import PPO,A2C,DDPG
from stable_baselines3.common.noise import OrnsteinUhlenbeckActionNoise
from codex_rl3690996_core import StockBook,sha,DEFAULTS
from codex_rl3690996_env import StockEnv,FuturesEnv
import metrics as M

PLAN="30187666db966efde21fdbeb7e2c0bdc69927522"
ALGORITHMS={"PPO":PPO,"A2C":A2C,"DDPG":DDPG}
SEED=3690996


def dump(path,obj):
    def clean(x):
        if isinstance(x,dict):return {str(k):clean(v) for k,v in x.items()}
        if isinstance(x,(list,tuple)):return [clean(v) for v in x]
        if isinstance(x,np.generic):return clean(x.item())
        if isinstance(x,float) and not np.isfinite(x):return None
        return x
    Path(path).write_text(json.dumps(clean(obj),indent=2,default=str,allow_nan=False)+"\n")


def data_for(profile):
    return dict(np.load(RUNTIME/(profile+".npz"),allow_pickle=False))


def eligible(data,profile):
    ok=data["valid"].copy()
    if profile=="stocks":ok &= np.r_[False,data["valid"][:-1]]
    return np.flatnonzero(ok)


def make_env(profile,data,days,training=False,**kw):
    return (StockEnv if profile=="stocks" else FuturesEnv)(data,days,training=training,**kw)


def fit(profile,name,data,days,key):
    cache=RUNTIME/"models"/profile/("seed_"+str(SEED))/key
    cache.mkdir(parents=True,exist_ok=True)
    target=cache/name
    signature=dict(profile=profile,algorithm=name,seed=SEED,steps=8192,
        fit_first=int(data["dates"][days[0]]),fit_last=int(data["dates"][days[-1]]),
        data_sha256=sha(RUNTIME/(profile+".npz")),
        code={p:sha(ROOT/"analysis"/p) for p in ["codex_rl3690996_core.py","codex_rl3690996_env.py","codex_rl3690996_train.py"]})
    meta=target.with_suffix(".json")
    if meta.exists():
        assert json.loads(meta.read_text())==signature,"Cached model belongs to a different frozen experiment"
        return ALGORITHMS[name].load(str(target),device="cpu")
    env=make_env(profile,data,days,training=True)
    common=dict(env=env,seed=SEED,device="cpu",verbose=0,policy_kwargs=dict(net_arch=[64,64]),gamma=.99)
    if name=="PPO":
        model=PPO("MlpPolicy",n_steps=256,batch_size=64,n_epochs=5,learning_rate=.0003,gae_lambda=.95,**common)
    elif name=="A2C":
        model=A2C("MlpPolicy",n_steps=64,learning_rate=.0007,gae_lambda=.95,**common)
    else:
        dim=env.action_space.shape[0]
        noise=OrnsteinUhlenbeckActionNoise(np.zeros(dim),.1*np.ones(dim))
        model=DDPG("MlpPolicy",learning_rate=.001,buffer_size=50000,learning_starts=512,batch_size=64,
                   tau=.005,train_freq=(4,"step"),gradient_steps=1,action_noise=noise,**common)
    model.learn(total_timesteps=8192,progress_bar=False)
    model.save(str(target));dump(meta,signature);env.close()
    return model


def evaluate(profile,data,days,policy,book=None,mult=1.,log=False):
    overlay=policy!="PASSIVE"
    rows=[];fills=[];trades=[]
    if profile=="stocks":
        book=book or StockBook(data["c"].shape[1],cost_multiplier=mult,log=log)
        env=StockEnv(data,days,book=book,overlay=overlay)
        obs,_=env.reset()
        for i in days:
            if isinstance(policy,str):
                if policy in ("PASSIVE","OVERLAY"):action=np.ones(env.n)/env.n
                else:
                    score=np.maximum(data["momentum"][i-1],0)
                    action=score/max(float(score.sum()),1e-12)
            else:action=policy.predict(obs,deterministic=True)[0]
            obs,_,done,_,info=env.step(action);rows.append(info)
        return rows,book.fills,book.closed,book
    for i in days:
        env=FuturesEnv(data,[i],cost_multiplier=mult,overlay=overlay,log=log)
        obs,_=env.reset()
        for k in range(77):
            if isinstance(policy,str):
                action=np.array([1. if policy in ("PASSIVE","OVERLAY") else np.sign(data["features"][i,k,1])])
            else:action=policy.predict(obs,deterministic=True)[0]
            obs,_,done,_,info=env.step(action)
        assert env.book.q==0
        if log:
            assert np.isclose(sum(t["net"] for t in env.book.trades),info["net"])
        rows.append(info);fills.extend(env.book.fills);trades.extend(env.book.trades)
    return rows,fills,trades,None


def returns(rows,profile):
    frame=pd.DataFrame(rows)
    if profile=="stocks":
        eq=frame.equity.to_numpy();prev=np.r_[10000.,eq[:-1]]
        # Validation starts flat; continuous-trade caller recomputes on complete joined series.
        return (eq-prev)/prev
    return frame.net.to_numpy()/10000.


def nw_t(x,lags=5):
    x=np.asarray(x,float);z=x-x.mean();n=len(x)
    variance=np.dot(z,z)/n
    for k in range(1,min(lags,n-1)+1):variance+=2*(1-k/(lags+1))*np.dot(z[k:],z[:-k])/n
    return float(x.mean()/np.sqrt(variance/n)) if variance>0 else 0.


def summarize(frame,trades,profile):
    frame=frame.copy();pnl=frame.net.to_numpy();eq=10000+np.cumsum(pnl)
    ret=pnl/np.r_[10000.,eq[:-1]]
    closed=pd.DataFrame(trades)
    z=M.perf(pnl,closed.net if len(closed) else None,capital=10000.)
    return_metrics=M.perf(ret,capital=1.)
    z.update(sharpe=return_metrics["sharpe"],sortino=return_metrics["sortino"])
    peak=np.maximum.accumulate(np.r_[10000.,eq])[1:]
    z.update(max_dd=float((peak-eq).max()),ulcer=float(np.sqrt(np.mean(((eq/peak-1)*100)**2))),
             net=float(pnl.sum()),ending_equity=float(eq[-1]),daily_return_pf=float(ret[ret>0].sum()/max(1e-12,-ret[ret<0].sum())),
             annual_return=float((eq[-1]/10000.)**(252/len(eq))-1) if eq[-1]>0 else None,
             max_dd_pct=float((1-eq/peak).max()),fees=float(frame.fee.sum()),slippage=float(frame.slippage.sum()),
             gross_on_executed_quantities=float(pnl.sum()+frame.fee.sum()+frame.slippage.sum()),
             sessions=len(frame),positive_years=int((frame.groupby(frame.date//10000).net.sum()>0).sum()),
             years=int(frame.date.floordiv(10000).nunique()),daily_NW5_t=nw_t(pnl),
             pf_basis="average-cost partial closures" if profile=="stocks" else "closed intraday round trips")
    z["calmar"]=z["annual"]/z["max_dd"] if z["max_dd"]>0 else None
    return z,ret


def run(profile,phase):
    subprocess.check_call(["git","-C",str(ROOT),"cat-file","-e",PLAN+":agents/codex/plans/rl3690996_build_20261030.md"])
    leaf=phase if SEED==3690996 else "confirmation_"+str(SEED)
    out=ROOT/"analysis/outputs/codex_rl3690996_build"/profile/leaf
    out.mkdir(parents=True,exist_ok=True)
    data=data_for(profile);ix=eligible(data,profile);dates=data["dates"]
    lo,hi=((20180101,20200101) if profile=="stocks" else (20180101,20230101))
    if phase=="validation":
        prior=out.parent/"design/gate.json"
        if not prior.exists() or not json.loads(prior.read_text())["primary_design_pass"]:
            raise PermissionError("Design gate did not earn reserved validation")
        for seed in (17,29):
            check=out.parent/("confirmation_"+str(seed))/"gate.json"
            if not check.exists() or not json.loads(check.read_text())["primary_design_pass"]:
                raise PermissionError("Reserved validation requires both declared seed confirmations")
        lo,hi=(20200101,20200818) if profile=="stocks" else (20230101,20261101)
    elif SEED!=3690996:
        check=out.parent/"design/gate.json"
        if not check.exists() or not json.loads(check.read_text())["primary_design_pass"]:
            raise PermissionError("Primary design did not earn extra training seeds")
    trading=ix[(dates[ix]>=lo)&(dates[ix]<hi)]
    quarters=pd.PeriodIndex(pd.to_datetime(dates[trading].astype(str)),freq="Q")
    candidates=["PPO","A2C","DDPG","SELECTOR","PASSIVE","OVERLAY","LINEAR","SELECTOR_2X_COST"]
    allrows={k:[] for k in candidates};allfills={k:[] for k in candidates};alltrades={k:[] for k in candidates}
    books={k:None for k in candidates}; selections=[]
    start=time.time()
    for quarter in quarters.unique():
        td=trading[quarters==quarter];before=ix[dates[ix]<dates[td[0]]]
        vd=before[-63:];fd=before[:-63]
        if len(vd)!=63 or len(fd)<60:raise ValueError("Insufficient predecision training/validation history")
        assert dates[fd[-1]]<dates[vd[0]]<=dates[vd[-1]]<dates[td[0]]
        models={};scores={}
        for name in ALGORITHMS:
            print(profile,quarter,name,"fit",len(fd),"validation",len(vd),flush=True)
            model=fit(profile,name,data,fd,str(quarter))
            vr,_,_,_=evaluate(profile,data,vd,model)
            rr=returns(vr,profile);scores[name]=float(rr.mean()/rr.std(ddof=1)*np.sqrt(252)) if rr.std()>0 else -1e9
            models[name]=model
        chosen=max(ALGORITHMS,key=lambda n:scores[n])
        selections.append(dict(quarter=str(quarter),fit_first=int(dates[fd[0]]),fit_last=int(dates[fd[-1]]),
            validation_first=int(dates[vd[0]]),validation_last=int(dates[vd[-1]]),trade_first=int(dates[td[0]]),
            trade_last=int(dates[td[-1]]),selected=chosen,**{k+"_validation_sharpe":v for k,v in scores.items()}))
        for label in candidates:
            name=chosen if label.startswith("SELECTOR") else label
            policy=models[name] if name in models else name
            r,f,t,book=evaluate(profile,data,td,policy,book=books[label],mult=2. if label=="SELECTOR_2X_COST" else 1.,log=True)
            for row in r:row.update(quarter=str(quarter),selected=name)
            allrows[label].extend(r)
            if profile=="stocks":
                # The external book owns its complete growing execution/realization ledger.
                allfills[label]=f;alltrades[label]=t;books[label]=book
            else:
                allfills[label].extend(f);alltrades[label].extend(t)
        pd.DataFrame(selections).to_csv(out/"selections.csv",index=False)
        dump(out/"progress.json",dict(quarter_complete=str(quarter),elapsed_seconds=time.time()-start))
        print(profile,quarter,"selected",chosen,"elapsed",round(time.time()-start),flush=True)
        del models;gc.collect()
    summaries={};rets={}
    for label in candidates:
        frame=pd.DataFrame(allrows[label]);frame.to_csv(out/(label+"_daily.csv"),index=False)
        pd.DataFrame(allfills[label]).to_csv(out/(label+"_fills.csv"),index=False)
        pd.DataFrame(alltrades[label]).to_csv(out/(label+"_closed.csv"),index=False)
        summaries[label],rets[label]=summarize(frame,alltrades[label],profile)
        frame.groupby(frame.date//10000).agg(net=("net","sum"),fee=("fee","sum"),slippage=("slippage","sum")).to_csv(out/(label+"_years.csv"))
        if profile=="futures":
            closed=pd.DataFrame(alltrades[label]);side={}
            for sign,nm in [(1,"long"),(-1,"short")]:
                t=closed[closed.side==sign] if len(closed) else closed
                daily=t.groupby("date").net.sum().reindex(frame.date,fill_value=0.) if len(t) else pd.Series(0.,index=frame.date)
                side[nm]=M.perf(daily,t.net if len(t) else [],capital=10000.)
            dump(out/(label+"_sides.json"),side)
    pd.DataFrame(summaries).T.to_csv(out/"summary.csv")
    diff=rets["SELECTOR"]-rets["OVERLAY"]
    checks=dict(net_positive=summaries["SELECTOR"]["net"]>0,
        mean_beats_overlay=float(diff.mean())>0,
        mean_beats_passive=float((rets["SELECTOR"]-rets["PASSIVE"]).mean())>0,
        incremental_NW5_ge2=nw_t(diff)>=2,
        doubled_cost_positive=summaries["SELECTOR_2X_COST"]["net"]>0,
        positive_years=summaries["SELECTOR"]["positive_years"]>=int(np.ceil(.75*summaries["SELECTOR"]["years"])))
    dump(out/"gate.json",dict(checks=checks,incremental_NW5_t=nw_t(diff),primary_design_pass=all(checks.values()),
        reserved_validation_run=phase=="validation",seed_confirmations_run=SEED!=3690996,new_economic_series=len(candidates),
        primary_seed=SEED,plan_commit=PLAN,limits=["conditional source/observed-grid research",
        "stock 2023+ history unavailable", "one primary seed; no seed selected after outcomes"]))
    dump(out/"manifest.json",dict(profile=profile,phase=phase,seed=SEED,steps_per_algorithm_quarter=8192,
        elapsed_seconds=time.time()-start,data_sha256=sha(RUNTIME/(profile+".npz")),
        code={p:sha(ROOT/"analysis"/p) for p in ["codex_rl3690996_core.py","codex_rl3690996_env.py","codex_rl3690996_train.py"]},
        plan_commit=PLAN,versions=dict(numpy=np.__version__,pandas=pd.__version__,torch=torch.__version__),
        definitions=candidates,source_preparation=json.loads((RUNTIME/"preparation.json").read_text())))
    print(pd.DataFrame(summaries).T[["annual_return","sharpe","sortino","profit_factor","calmar","ulcer","max_dd_pct","net"]].to_string(),flush=True)
    print("GATE",checks,"incremental NW5",nw_t(diff),flush=True)


if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("profile",choices=["stocks","futures"]);p.add_argument("phase",nargs="?",default="design",choices=["design","validation"])
    p.add_argument("--seed",type=int,choices=[3690996,17,29],default=3690996)
    args=p.parse_args();SEED=args.seed;run(args.profile,args.phase)
