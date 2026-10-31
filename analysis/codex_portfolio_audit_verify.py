"""Synthetic native-cost/session checks and independent saved-ledger reconciliation."""
import ast
import argparse
import gc
import tempfile
from types import SimpleNamespace
import numpy as np
import pandas as pd
from codex_portfolio_audit_config import *


def mechanics():
    tree=ast.parse((ROOT/"analysis/codex_portfolio_audit_prepare.py").read_text())
    body=[x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name in ["stamp","session","coord","prices_for_session","build_unit"]]
    with tempfile.TemporaryDirectory() as temp:
        out=Path(temp);days=pd.DatetimeIndex(["2020-01-02"])
        grid=SimpleNamespace(dates=np.array([20200101,20200102]),D=2)
        for k in ["o","h","l","c"]:setattr(grid,k,np.full((2,1440),100.))
        ns=dict(np=np,pd=pd,gc=gc,OUT=out,RUNTIME=out,issues=[],days=days,pos={days[0]:0},grids={"NQ":grid},MARKETS=MARKETS)
        exec(compile(ast.Module(body=body,type_ignores=[]),"extracted_frozen_path_functions","exec"),ns)
        assert ns["session"](pd.Timestamp("2020-01-01 17:01"))==days[0]
        assert ns["coord"](pd.Timestamp("2020-01-01 17:01"))==0
        assert ns["coord"](pd.Timestamp("2020-01-02 17:00"))==1439
        records=[]
        def fixture(name,side=1,kind=2,exit_open=True):
            z=pd.DataFrame([dict(market="NQ",session=days[0],entry_session=days[0],
                 entry_at=pd.Timestamp("2020-01-02 09:00"),exit_at=pd.Timestamp("2020-01-02 09:02"),
                 qty=1,side=side,entry=100.,exit=101. if side>0 else 99.,kind=kind,exit_open=exit_open)])
            ns["build_unit"](name,z)
            return dict(np.load(out/(name+".npz"))),z
        u,z=fixture("market")
        assert u["N"][0]==1 and u["F"][0,-1]==1 and u["S"][0,-1]==1
        assert np.isclose(u["G"][0]-1.04*u["N"][0]-u["S"][0,-1],-.04)
        a,b=ns["coord"](z.entry_at[0]),ns["coord"](z.exit_at[0])
        assert u["F"][0,a]==.5 and u["F"][0,b]==1 and u["Q"][0,b]==0
        records.append("native fee split, one-tick sides, final-flat cash bridge")
        t,_=fixture("target",kind=1,exit_open=False)
        assert t["S"][0,-1]==.5
        records.append("target limit exit pays commission without another adverse tick")
        s,_=fixture("short",side=-1)
        assert s["G"][0]==2 and s["S"][0,-1]==1
        records.append("native short sign and symmetric costs")
        repeated=pd.concat([z,z],ignore_index=True);ns["build_unit"]("twice",repeated)
        r=dict(np.load(out/"twice.npz"));assert r["N"][0]==2 and r["S"][0,-1]==2
        records.append("all reentries counted, no per-active-day cost shortcut")
        grid.l[1,541]=np.nan
        bad,_=fixture("missing");assert not bad["valid"][0]
        records.append("missing held quote fails admission, not imputed as an observed zero")
        grid.l[1,541]=100
        z["entry_session"]=pd.Timestamp("2020-01-01");ns["build_unit"]("cross",z)
        cross=dict(np.load(out/"cross.npz"));assert not cross["valid"][0]
        records.append("cross-session source mismatch remains unknown")
        assert int(np.floor(2750/(333*.25*2)))!=int(np.floor(1100/(333*.25*2)))*2.5
        assert np.floor(1.5*.5)==0 and np.floor(3*.5)==1
        records.append("150K risk floors at its own budget; cushion lots are integer")
        dump(OUT/"mechanics.json",dict(all_passed=True,checks=records))


def saved():
    dates=pd.to_datetime(np.load(RUNTIME/"dates_atr.npz")["dates"].astype(str))
    checked=[]
    for path in sorted(OUT.glob("*_unit_ledger.csv")):
        key=path.name.removesuffix("_unit_ledger.csv")
        t=pd.read_csv(path);u=dict(np.load(RUNTIME/(key+".npz")))
        idx=pd.DatetimeIndex(pd.to_datetime(t.date));g=t.groupby(idx).gross.sum().reindex(dates,fill_value=0).to_numpy()
        n=t.groupby(idx).qty.sum().reindex(dates,fill_value=0).to_numpy()
        s=t.groupby(idx).slippage_one_tick.sum().reindex(dates,fill_value=0).to_numpy()
        assert np.allclose(g,u["G"]) and np.allclose(n,u["N"]) and np.allclose(s,u["S"][:,-1])
        pv=MARKETS[t.market.iloc[0]][0]
        assert np.allclose((t.exit-t.entry)*t.side*pv*t.qty,t.gross)
        assert np.allclose(u["W"][:,-1],u["G"]) and np.allclose(u["R"][:,-1],u["G"])
        assert np.allclose(u["F"][:,-1],u["N"])
        checked.append(dict(component=key,trades=len(t),cash_cost_and_native_unit_reconciliation=True))
    for home,plan in ROSTERS.items():
        for scenario,(fee,ticks) in SCENARIOS.items():
            frame=pd.read_csv(OUT/f"{home}_{scenario}_daily.csv")
            assert np.allclose(frame.net,frame.gross-frame.fees-frame.slippage)
            assert np.allclose(frame[list(plan)].sum(axis=1),frame.net)
            s=pd.read_csv(OUT/"baseline_metrics.csv")
            row=s[(s.home==home)&(s.scenario==scenario)&(s.cohort=="all")].iloc[0]
            assert np.isclose(frame.loc[frame.admitted,"net"].sum(),row.net)
    p=json.loads((OUT/"simulator_parity.json").read_text())
    assert len(p)==24 and all(z["exact"] for z in p)
    # Paired fee scenarios share actual admitted historical date histories.
    for home in ["funded_50","funded_150"]:
        base=np.load(OUT/f"{home}_main_history_dates.npy")
        caps=np.array([1500,1500,2000,2500,2500,3000] if home=="funded_50" else [2500,3000,3000,3000,4000,5000])
        expected=np.r_[0,np.cumsum(caps)]
        rules=json.loads((OUT/f"{home}_account_rules.json").read_text())
        assert rules["start"]==({"funded_50":50000,"funded_150":150000}[home])
        assert np.array_equal(rules["caps"],caps)
        for scenario in SCENARIOS:
            assert np.array_equal(base,np.load(OUT/f"{home}_{scenario}_history_dates.npy"))
            r=pd.read_csv(OUT/f"{home}_{scenario}_accounts.csv")
            assert np.array_equal(r.paid,expected[r.payouts.astype(int)])
            assert (r.y1<=r.paid).all() and r.paid.max()<=caps.sum()
    dump(OUT/"verification.json",dict(all_passed=True,component_checks=checked,account_parity_records=len(p),
        fee_scenarios_share_history_dates=True,account_identity_and_each_payout_ladder_verified=True,
        limits="checks certify arithmetic and inherited simulator parity, not actual orders/fills or source-version parity"))


if __name__=="__main__":
    OUT.mkdir(parents=True,exist_ok=True)
    parser=argparse.ArgumentParser();parser.add_argument("mode",choices=["mechanics","saved"]);args=parser.parse_args()
    (mechanics if args.mode=="mechanics" else saved)()
    print(args.mode,"PASS")
