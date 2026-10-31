"""Reconcile saved experimental ledgers independently of the broker engines."""
from pathlib import Path
import argparse
import hashlib
from importlib.metadata import version
import json
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"analysis/outputs/codex_rl3690996_build"
RUNTIME=ROOT/"agents/codex/runtime/rl3690996"
verification={}
parser=argparse.ArgumentParser()
parser.add_argument("--profile",choices=["stocks","futures"])
args=parser.parse_args()
profiles=[args.profile] if args.profile else ["stocks","futures"]


def table(path):
    try:return pd.read_csv(path)
    except pd.errors.EmptyDataError:return pd.DataFrame()


for profile in profiles:
    folder=OUT/profile/"design"
    if not (folder/"summary.csv").exists():
        continue
    summary=pd.read_csv(folder/"summary.csv",index_col=0)
    selection=pd.read_csv(folder/"selections.csv")
    assert ((selection.fit_last<selection.validation_first)&
            (selection.validation_last<selection.trade_first)).all()
    for row in selection.itertuples():
        scores={a:getattr(row,a+"_validation_sharpe") for a in ["PPO","A2C","DDPG"]}
        assert row.selected==max(scores,key=scores.get)
    data=dict(np.load(RUNTIME/(profile+".npz"),allow_pickle=False))
    lookup={int(d):i for i,d in enumerate(data["dates"])}
    checks={}
    for label in summary.index:
        daily=table(folder/(label+"_daily.csv"));fills=table(folder/(label+"_fills.csv"));closed=table(folder/(label+"_closed.csv"))
        mult=2 if label=="SELECTOR_2X_COST" else 1
        assert daily.date.is_unique and daily.date.is_monotonic_increasing
        assert np.isfinite(daily[["net","fee","slippage"]]).all().all()
        assert np.isclose(daily.net.sum(),summary.loc[label,"net"])
        assert np.isclose(daily.fee.sum(),summary.loc[label,"fees"])
        assert np.isclose(daily.slippage.sum(),summary.loc[label,"slippage"])
        if len(fills):
            assert np.isclose(fills.fee.sum(),daily.fee.sum())
            assert np.isclose(fills.slippage.sum(),daily.slippage.sum())
            assert (fills.qty.astype(int)==fills.qty).all()
        if profile=="stocks":
            cash=10000.;q=np.zeros(len(data["tickers"]),dtype=int);last_equity=10000.
            for day in daily.itertuples():
                idx=lookup[int(day.date)]
                # Frozen design has no split in the admitted28-name panel. Fail if that changes.
                assert np.allclose(data["split"][idx],1)
                z=fills[fills.fill_date==day.date] if len(fills) else fills
                for f in z.itertuples():
                    assert f.decision_date<f.fill_date and f.cash_after>=-1e-7
                    assert np.isclose(f.price,data["o"][idx,int(f.asset)]*(1+f.side*.0005*mult))
                    assert np.isclose(f.fee,f.qty*f.price*.001*mult)
                    cash-=f.side*f.qty*f.price+f.fee;q[int(f.asset)]+=f.side*f.qty
                    assert np.isclose(cash,f.cash_after) and q[int(f.asset)]==f.holdings_after
                equity=cash+q@data["c"][idx]
                assert np.isclose(equity,day.equity) and np.isclose(equity-last_equity,day.net)
                assert cash>=-1e-7 and (q>=0).all()
                last_equity=equity
        else:
            for day in daily.itertuples():
                z=fills[fills.date==day.date] if len(fills) else fills
                t=closed[closed.date==day.date] if len(closed) else closed
                if len(z):
                    assert z.qty.sum()==0 and np.abs(z.qty.cumsum()).max()<=1
                    assert (z.minute>z.decision_minute).all() and z.minute.max()<=896
                    assert np.allclose(z.price,z.raw_price+np.sign(z.qty)*.25*mult)
                    assert np.allclose(z.fee,abs(z.qty)*.62*mult)
                    assert np.allclose(z.slippage,abs(z.qty)*.5*mult)
                if len(t):
                    assert np.allclose(t.net,(t.exit-t.entry)*t.side*t.qty*2-t.fee)
                    assert np.allclose(t.net,t.gross-t.fee-t.slippage)
                    assert np.isclose(t.net.sum(),day.net)
                else:assert np.isclose(day.net,0)
                assert day.adverse<=min(day.net,0)+1e-6
            if len(closed):
                assert np.isclose(closed.groupby("side").net.sum().sum(),daily.net.sum())
        checks[label]=dict(sessions=len(daily),fills=len(fills),closed_realizations=len(closed),
                           clock_cash_fee_position_reconciliation=True)
    verification[profile]=dict(chronological_folds_and_pretrade_selection=True,policies=checks,
                               all_checks_passed=True)
    manifest=json.loads((folder/"manifest.json").read_text())
    models=[]
    for path in sorted((RUNTIME/"models"/profile/"seed_3690996").glob("*/*.zip")):
        signature=json.loads(path.with_suffix(".json").read_text())
        assert signature["code"]==manifest["code"]
        assert signature["data_sha256"]==manifest["data_sha256"]
        models.append(dict(path=str(path.relative_to(RUNTIME)),sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                           bytes=path.stat().st_size,signature=signature))
    assert len(models)==len(selection)*3
    (folder/"model_receipts.json").write_text(json.dumps(models,indent=2)+"\n")

if len(verification)!=len(profiles):
    raise RuntimeError("Requested profile results must finish before reconciliation")
verification["all_checks_passed"]=True
verification["dependencies"]={name:version(name) for name in ["torch","stable-baselines3","gymnasium","numpy","pandas","scipy","matplotlib"]}
name="ledger_verification"+("_"+args.profile if args.profile else "")+".json"
(OUT/name).write_text(json.dumps(verification,indent=2)+"\n")
print(json.dumps(verification,indent=2))
