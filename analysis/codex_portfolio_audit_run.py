"""Fixed current-book diagnostics and conditional account baselines. No allocation search."""
import sys
sys.dont_write_bytecode=True
from codex_portfolio_audit_config import *
import gc
import pickle
from types import SimpleNamespace
import numpy as np
import pandas as pd

os.environ.setdefault("NUMBA_CACHE_DIR",str(RUNTIME/"numba"))
os.environ.setdefault("MPLCONFIGDIR",str(RUNTIME/"matplotlib"))
os.environ.setdefault("XDG_CACHE_HOME",str(RUNTIME/"cache"))
sys.path.insert(0,str(SOURCE/"analysis"))
os.chdir(SOURCE)
sys.argv=[__file__,str(SCRATCH),"library"]
import funded_sim as F50
import funded_sim150 as F150
import funded_bootstrap as FB
import portfolio as PF
import metrics as M
import montecarlo as MC
import codex_ob_v2_accounts as TABLE
import codex_anson_accounts as ENGINE

meta=dict(np.load(RUNTIME/"dates_atr.npz"));dates=pd.to_datetime(meta["dates"].astype(str))
rows=[];account_rows=[];parity=[];admission=[]


def perf(x):
    x=np.asarray(x,float);z=M.perf(x,capital=10000.)
    eq=10000.+np.cumsum(x);pk=np.maximum.accumulate(np.r_[10000.,eq])[1:]
    z.update(net=float(x.sum()),max_dd=float((pk-eq).max()),
             ulcer=float(np.sqrt(np.mean(((eq/pk-1)*100)**2))))
    z["calmar"]=z["annual"]/z["max_dd"] if z["max_dd"]>0 else None
    return z


def quantity(plan):
    result=[]
    for k,v in plan.items():
        result.append(v[1]/(meta["atr"]*v[2]*2) if isinstance(v,list) else np.full(len(dates),v))
    return np.asarray(result)


def diagnostics(home,keys,unit,base,fee,ticks,scenario):
    q=np.floor(base+1e-9)
    valid=np.logical_and.reduce([u["known"] for u in unit])&np.isfinite(base).all(0)
    complete=np.logical_and.reduce([u["valid"] for u in unit])&valid
    C=np.asarray([u["G"]-fee*u["N"]-ticks*u["S"][:,-1] for u in unit])
    gross=sum(q[i]*u["G"] for i,u in enumerate(unit))
    fees=sum(q[i]*fee*u["N"] for i,u in enumerate(unit))
    slips=sum(q[i]*ticks*u["S"][:,-1] for i,u in enumerate(unit))
    components=pd.DataFrame((q*C).T,index=dates,columns=keys)
    d=components.sum(axis=1).to_numpy()
    assert np.allclose(d,gross-fees-slips)
    frame=components.copy();frame["net"]=d;frame["gross"]=gross;frame["fees"]=fees;frame["slippage"]=slips;frame["admitted"]=valid;frame["complete_minute_paths"]=complete
    frame.index.name="date";frame.to_csv(OUT/f"{home}_{scenario}_daily.csv")
    for cohort,mask in [("all",valid),("2018_22",valid&(dates.year<2023)),("2023_plus",valid&(dates.year>=2023))]:
        z=perf(d[mask]);z.update(home=home,scenario=scenario,cohort=cohort,sessions=int(mask.sum()),
            gross=float(gross[mask].sum()),fees=float(fees[mask].sum()),slippage=float(slips[mask].sum()),
            first=dates[mask].min(),last=dates[mask].max(),sizing="full-size daily integer lots, before account pauses/cushion")
        rows.append(z)
    if scenario=="main":
        components[valid].corr().to_csv(OUT/f"{home}_correlations.csv")
        sums=components[valid].sum(axis=1);worst=sums.nsmallest(max(1,int(np.ceil(.05*len(sums))))).index
        attr=[]
        for k in keys:
            x=components.loc[valid,k];others=components.loc[valid].drop(columns=k).sum(axis=1)
            attr.append(dict(component=k,net=x.sum(),annual=x.mean()*252,rest_correlation=x.corr(others),
                net_on_worst5pct=components.loc[worst,k].sum(),losing_days=int((x<0).sum()),
                joint_loss_with_rest=int(((x<0)&(others<0)).sum()),
                loss_when_rest_loses=float(x[others<0].sum())))
        pd.DataFrame(attr).to_csv(OUT/f"{home}_contributions.csv",index=False)
        frame.loc[worst].to_csv(OUT/f"{home}_worst5pct_days.csv")
        frame.loc[valid].groupby(frame.index[valid].year)[["gross","fees","slippage","net"]].sum().to_csv(OUT/f"{home}_years.csv")
        # Exposure uses recorded, inferred trade minutes; no new rule is selected from this map.
        asset={k:pd.read_csv(OUT/f"{k}_unit_ledger.csv",nrows=1).market.iloc[0] for k in keys}
        per_asset={a:np.zeros_like(unit[0]["Q"]) for a in set(asset.values())}
        gross_asset={a:np.zeros_like(unit[0]["Q"]) for a in set(asset.values())}
        for i,k in enumerate(keys):
            per_asset[asset[k]]+=q[i,:,None]*unit[i]["Q"]
            gross_asset[asset[k]]+=q[i,:,None]*abs(unit[i]["Q"])
        exp=[]
        for a,Q in per_asset.items():
            G=gross_asset[a];mixed=G>abs(Q)+1e-8
            exp.append(dict(market=a,sessions=int(valid.sum()),active_session_share=float((G[valid].max(1)>0).mean()),
                max_gross_contracts=float(G[valid].max()),max_abs_net_contracts=float(abs(Q[valid]).max()),
                opposite_position_minutes=int(mixed[valid].sum()),
                active_minutes=int((G[valid]>0).sum()),
                days_with_opposite_positions=int(mixed[valid].any(1).sum()),
                maximum_locked_opposite_contracts=float(((G[valid]-abs(Q[valid]))/2).max())))
            # 24-hour session minute0 closes17:01CT of the preceding date.
            pd.DataFrame(dict(session_minute=np.arange(1440),civil_close_minute=(np.arange(1440)+1021)%1440,
                active_share=(G[valid]>0).mean(0),mean_gross=G[valid].mean(0),mean_net=Q[valid].mean(0))).to_csv(OUT/f"{home}_{a}_occupancy.csv",index=False)
        pd.DataFrame(exp).to_csv(OUT/f"{home}_exposure.csv",index=False)
        del per_asset,gross_asset
    return valid,C


for home,plan in ROSTERS.items():
    print("HOME",home,flush=True)
    keys=list(plan);base=quantity(plan)
    units=[dict(np.load(RUNTIME/(k+".npz"))) for k in keys]
    for scenario,(fee,ticks) in SCENARIOS.items():
        print(home,scenario,"diagnostics",flush=True)
        valid,C=diagnostics(home,keys,units,base,fee,ticks,scenario)
        W=np.asarray([u["W"]-fee*u["F"]-ticks*u["S"] for u in units])
        R=np.asarray([u["R"]-fee*u["F"]-ticks*u["S"] for u in units])
        assert np.allclose(W[:,:,-1],C) and np.allclose(R[:,:,-1],C)
        # Keep every chronological window's original calendar positions. A missing day invalidates that window.
        if home.startswith("evaluation"):
            rules=dict(PF.RULES)
            if home.endswith("150"):
                rules.update(start=150000.,target=9000.,mll=4000.,dll=2000.)
            q=np.floor(base+1e-9);w=np.einsum("kd,kdm->dm",q,W);r=np.einsum("kd,kdm->dm",q,R)
            results=[]
            for start in range(len(dates)-20):
                if not valid[start:start+21].all():continue
                outcome,used=PF.challenge(w,r,np.arange(start,start+21),rules)
                results.append(dict(start=dates[start],outcome=outcome,days=used))
            result=pd.DataFrame(results);result.to_csv(OUT/f"{home}_{scenario}_accounts.csv",index=False)
            for name,mask in [("all",np.ones(len(result),bool)),("2018_22",pd.to_datetime(result.start).dt.year<2023),
                              ("2023_plus",pd.to_datetime(result.start).dt.year>=2023)]:
                t=result[mask];passed=t[t.outcome=="pass"]
                account_rows.append(dict(home=home,scenario=scenario,cohort=name,n=len(t),
                    pass_rate=(t.outcome=="pass").mean(),failure_rate=(t.outcome=="fail_mll").mean(),
                    timeout_rate=(t.outcome=="fail_time").mean(),median_pass_days=passed.days.median(),
                    basis="conditional historical21-session starts; overlapping windows, no independence claim"))
            del q,w,r
        else:
            # Native timing is improved; remaining price-inference/per-strategy-extrema limits remain explicit.
            use=np.flatnonzero(valid);B=np.ascontiguousarray(base[:,use]);Wv=W[:,use,:];Cv=C[:,use]
            chg=np.zeros(W.shape[2],bool);chg[-1]=True;chg[0]=True
            chg[1:]|=(np.diff(Wv,axis=2)!=0).any(axis=(0,1))
            Wv=np.ascontiguousarray(Wv[:,:,chg]);Cv=np.ascontiguousarray(Cv)
            f=F50 if home.endswith("50") else F150
            params=ENGINE.rules(f,"50K_funded" if f is F50 else "150K_funded")
            # Canonical synchronized20-day block history generator; same seed/allocation/scenario pairing.
            dummy=SimpleNamespace(g=SimpleNamespace(ts=dates[use].to_numpy()),tr=np.arange(len(use)))
            hist=FB.Boot(dummy,start=START)._histories(500,500,20,20261031)
            np.save(OUT/f"{home}_{scenario}_history_dates.npy",meta["dates"][use][hist])
            table=TABLE.make_table(Wv,Cv,B)
            parity+=ENGINE.parity_check(Wv,Cv,table,hist[:2],f,params,f"{home}/{scenario}")
            result=ENGINE.run_table(table,hist,500,params);y1=ENGINE.run_table(table,hist,250,params)[:,0]
            t=pd.DataFrame(result,columns=["paid","payouts","days","blown","first"]);t["y1"]=y1
            t.to_csv(OUT/f"{home}_{scenario}_accounts.csv",index=False)
            t6=np.where(t.payouts==6,t.days,np.inf)
            account_rows.append(dict(home=home,scenario=scenario,cohort="all",n=len(t),
                y1=y1.mean(),y1_p5=np.percentile(y1,5),y2=t.paid.mean(),y2_p5=np.percentile(t.paid,5),
                failure_rate=t.blown.mean(),all6_rate=(t.payouts==6).mean(),median_sixth_days=float(np.median(t6)),
                basis="conditional synchronized20-day blocks/500 sessions;500 paired histories; inferred OHLC adverse bounds"))
            del Wv,Cv,table,B
        admission.append(dict(home=home,scenario=scenario,total_sessions=len(dates),admitted_sessions=int(valid.sum()),
                              excluded_sessions=int((~valid).sum()),native_fee_RT=fee,ticks_per_market_stop_fill=ticks,
                              complete_minute_path_sessions=int((np.logical_and.reduce([u["valid"] for u in units])&valid).sum()),
                              certification="conditional recorded-ledger/sparse-bar path model; missing adverse observations and actual/current-version fills unverified"))
        del W,R;gc.collect()
        pd.DataFrame(rows).to_csv(OUT/"baseline_metrics.csv",index=False)
        pd.DataFrame(account_rows).to_csv(OUT/"account_summary.csv",index=False)
        dump(OUT/"simulator_parity.json",parity)
        pd.DataFrame(admission).to_csv(OUT/"admission.csv",index=False)
        print(home,scenario,"complete",flush=True)
    del units;gc.collect()


# Personal source assembly, stopped before its printing, MonteCarlo or allocation sweeps.
# This preserves the published component identities; known version/marking limits are audited, not hidden.
source=(SOURCE/"analysis/personal_portfolio.py").read_text()
prefix=source[:source.index("    names = {")]
prefix=prefix.replace('sp="scratch_data/"', 'sp='+repr(str(SCRATCH)+"/"))
ns={"__name__":"__main__","__file__":str(SOURCE/"analysis/personal_portfolio.py")}
exec(compile(prefix,str(SOURCE/"analysis/personal_portfolio.py"),"exec"),ns)
published=ns["P"].loc[(ns["P"].index>=START)&(ns["P"].index<=END)].copy()
published.to_csv(OUT/"personal_published_daily.csv")
personal_rows=[]
for scenario,(fee,ticks) in SCENARIOS.items():
    P=published.copy();valid=pd.Series(True,index=P.index)
    for col,key in PERSONAL_CORE.items():
        u=dict(np.load(RUNTIME/(key+".npz")))
        x=pd.Series(u["G"]-fee*u["N"]-ticks*u["S"][:,-1],index=dates)
        P[col]=x.reindex(P.index);valid&=pd.Series(u["known"],index=dates).reindex(P.index,fill_value=False)
        del u
    # Published extras use per-NQ7.25 commission plus .55 extra per micro trade =1.275RT.
    for col,path,exit_col in [
        ("FC2B","checks/candidates/fc_2b/trades.csv","date"),
        ("TwinContinuation","checks/candidates/twin_continuation/trades.csv","date"),
        ("DualThrust","checks/candidates/dual_thrust/trades.csv","date"),
        ("Kusho","checks/candidates/kusho/python_trades_v9_rolladj.csv","exit_date"),
        ("S47","checks/candidates/s47_v2/python_trades_v2.csv","date"),
        ("OvernightTick","checks/candidates/overnight_tick/trades.csv","date"),
        ("SwingTarget","checks/candidates/swing_target/mc_trades_v3.csv","date"),
        ("PaperTrend","checks/candidates/papertrend/mc_trades_claude.csv","date")]:
        t=pd.read_csv(SOURCE/path);d=pd.to_datetime(t[exit_col])
        ix=P.index.searchsorted(d);keep=ix<len(P)
        # Counts outside this audit window cannot be clipped into its first or last session.
        keep&=(d>=P.index.min())&(d<=P.index.max())
        counts=pd.Series(1.,index=P.index[ix[keep]]).groupby(level=0).sum().reindex(P.index,fill_value=0)
        P[col]+=(1.275-fee)*counts
        # Extra adverse tick per market/stop fill; source-kind ambiguity is retained as a stress approximation.
        if ticks>1:
            kinds=t.get("kind",pd.Series("unknown",index=t.index)).astype(str).str.lower()
            nsides=1+(~kinds.isin(["target","profit target"])).astype(int)
            extra=pd.Series(nsides[keep].to_numpy()*.5*(ticks-1),index=P.index[ix[keep]]).groupby(level=0).sum().reindex(P.index,fill_value=0)
            P[col]-=extra
    # S30 contains two separate native-contract sleeves and a daily marked ledger. Debit its actual exit counts.
    for sym,oldfee in [("NQ",.725),("ES",.5)]:
        t=pd.read_csv(SOURCE/f"checks/candidates/s30_ibs/python_trades_{sym}.csv")
        d=pd.to_datetime(t.exit_date);ix=P.index.searchsorted(d);keep=(d>=P.index.min())&(d<=P.index.max())&(ix<len(P))
        counts=pd.Series(1.,index=P.index[ix[keep]]).groupby(level=0).sum().reindex(P.index,fill_value=0)
        # Existing daily S30 ledger already contains full-size commissions/10, not the .55 personal add-on.
        P["S30"]-=(fee-oldfee)*counts
        if ticks>1:P["S30"]-=2*(.5 if sym=="NQ" else 1.25)*(ticks-1)*counts
    P["admitted"]=valid;P.to_csv(OUT/f"personal_{scenario}_components.csv")
    V=P.drop(columns="admitted").loc[valid];d=V.sum(axis=1)
    for name,m in [("all",np.ones(len(V),bool)),("2018_22",V.index.year<2023),("2023_plus",V.index.year>=2023)]:
        z=perf(d[m]);z.update(home="personal",scenario=scenario,cohort=name,sessions=int(m.sum()),
            first=d[m].index.min(),last=d[m].index.max(),sizing="documented19-sleeve one-micro ledger proxy; not margin-certified")
        rows.append(z)
    dm=MC.daily_mc(d.to_numpy(),horizon=252,n=5000,block=20,seed=20261031,trail=1e12)
    # Source MC utility's DD omits the starting-zero peak; retain its result and independently correct that below.
    personal_rows.append(dict(scenario=scenario,**dm,capital_at20pct_rule=dm["dd_p95"]/.2,
                              evidence="conditional source ledgers, Twin v1 and Kusho exit-day/roll limits"))
    if scenario=="main":
        V.corr().to_csv(OUT/"personal_correlations.csv");worst=d.nsmallest(int(np.ceil(.05*len(d)))).index
        att=[]
        for k in V:
            other=d-V[k]
            att.append(dict(component=k,net=V[k].sum(),annual=V[k].mean()*252,
                rest_correlation=V[k].corr(other),net_on_worst5pct=V.loc[worst,k].sum(),
                joint_loss_with_rest=int(((V[k]<0)&(other<0)).sum()),loss_when_rest_loses=V.loc[other<0,k].sum()))
        pd.DataFrame(att).to_csv(OUT/"personal_contributions.csv",index=False)
        pd.DataFrame(dict(net=d)).groupby(d.index.year).sum().to_csv(OUT/"personal_years.csv")
        core=d-V["S30"]
        dump(OUT/"personal_ladder_diagnostic.json",dict(documented_piece_count=len(V.columns),
             actual_contract_sleeves=len(V.columns)+1,description="S30 combines MNQ+MES; the printed ladder still names an older16-piece core",
             no_S30_current18_sleeve_metrics=perf(core),
             no_S30_current18_sleeve_MC=MC.daily_mc(core.to_numpy(),horizon=252,n=5000,block=20,seed=20261031,trail=1e12),
             source_sizing_floor="personal_portfolio.py max(1,floor(...)) always prints at least1x even when the20% risk budget cannot fund1x"))
pd.DataFrame(rows).to_csv(OUT/"baseline_metrics.csv",index=False)
pd.DataFrame(personal_rows).to_csv(OUT/"personal_bootstrap.csv",index=False)
dump(OUT/"run_manifest.json",dict(source_commit=SOURCE_COMMIT,plan_commit=PLAN_COMMIT,rosters=ROSTERS,
    scenarios=SCENARIOS,seed=20261031,bootstrap_histories=500,block_days=20,personal_draws=5000,
    code={p.name:sha(p) for p in (ROOT/"analysis").glob("codex_portfolio_audit_*.py")},
    backend={p:sha(ROOT/"analysis"/p) for p in ["codex_ob_v2_accounts.py","codex_anson_accounts.py"]},
    decisions="audit only; no allocations selected, retired or changed"))
print("ALL AUDIT OUTPUTS COMPLETE",flush=True)
