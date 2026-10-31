"""S03v2 all-plan placement by extending reviewed generic account adapters.

Reuses R2Vault/Anson finite-quantity accounting, original simulator parity,
real21-session evaluation windows and full14-piece personal benchmarks.
New path builder handles both sides and sigma stops rather than R2 long-only.
"""
from pathlib import Path
import argparse
import importlib
import json
import pickle
import sys
import time
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"agents/codex/runtime/or_pullback_python"),str(ROOT/"analysis")]
import numpy as np
import pandas as pd
import codex_s03_v2_replay as S
import codex_r2vault_accounts as C
import codex_r2vault_personal as Q
import codex_anson_personal as P
import codex_anson_plan as A
import codex_anson_accounts as B
BASE=ROOT/"analysis/outputs/codex_s03_v2"
MODES=("v2_apex","v1_apex")


def candidate_paths(g,trades,fee=1.04,known_closed=None):
    """Signed exposure with causal boundary extrema and all-market/stop costs."""
    w,r=np.zeros(g.o.shape),np.zeros(g.o.shape)
    for t in trades.itertuples():
        d,e,z,side=int(t.day),int(t.entry_j),int(t.exit_j),int(t.side)
        if side not in(-1,1) or t.cross_date or t.unknown_held_minutes or not 0<=e<=z<1440:
            raise ValueError("Invalid Apex candidate path")
        end=z+int(t.exit_phase!="open")
        price=np.array((g.l if side>0 else g.h)[d,e:end],copy=True)
        if len(price):
            price[0]=t.entry_minute_adverse_px
            if t.exit_phase!="open":price[-1]=t.exit_minute_adverse_px
            for offset in np.flatnonzero(~np.isfinite(price)):
                minute=e+int(offset)
                if known_closed is None or not known_closed[d,minute]:raise ValueError("Unknown held quote")
                prior=np.flatnonzero(np.isfinite(g.c[d,e:minute]))
                if not len(prior):raise ValueError("No causal prior close")
                price[offset]=g.c[d,e+prior[-1]]
        net=(t.exit-t.entry)*side*2-fee-1.
        marks=(price-t.entry)*side*2-fee-.5
        if len(marks) and t.exit_phase!="open":marks[-1]=min(marks[-1],net)
        w[d,e:end]+=marks;w[d,end:]+=net;r[d,z:]+=net
    return w,r


def path_fixtures():
    from types import SimpleNamespace
    g=SimpleNamespace(o=np.full((1,1440),100.),h=np.full((1,1440),101.),l=np.full((1,1440),99.),c=np.full((1,1440),100.))
    t=pd.DataFrame([dict(day=0,entry_j=2,exit_j=4,side=-1,entry=100.,exit=104.,entry_phase="open",
        exit_phase="intrabar",entry_minute_adverse_px=101.,exit_minute_adverse_px=104.,cross_date=False,unknown_held_minutes=0)])
    g.h[0,4]=900. # Post-stop high mustnot enter the account path.
    w,r=candidate_paths(g,t)
    np.testing.assert_allclose(w[0,2:5],[-3.54,-3.54,-10.04]);np.testing.assert_allclose(r[0,4:],-10.04)
    t.loc[0,["exit_j","exit_phase","exit","exit_minute_adverse_px"]]=[2,"intrabar",104.,104.]
    t.loc[0,"entry_minute_adverse_px"]=104.
    w,r=candidate_paths(g,t);np.testing.assert_allclose(w[0,2:],-10.04)
    return dict(short_boundary=True,entry_fee_reserved=True,stop_clips_adverse=True,same_minute_stop=True)


def personal():
    S.authorize();out=BASE/"personal";out.mkdir(parents=True,exist_ok=True)
    with open(ROOT/"agents/codex/runtime/anson_personal_baseline.pkl","rb") as f:frame=pickle.load(f)
    reference=P.baseline_reference(frame)
    if not reference["rounding_match"]:raise ValueError("Personal baseline differs")
    with open(ROOT/"scratch_data/g24.pkl","rb") as f:g=pickle.load(f)
    manifest=dict(preregistration=S.PREREG,baseline=reference,models={},fees=1.275,
        history_rule="5000 paired252day20dayblocks seed1; full/2025+;21configs each",limits=P.LIMITATIONS,
        scripts={p:S.sha(ROOT/"analysis"/p) for p in (Path(__file__).name,"codex_r2vault_personal.py","codex_anson_personal.py")})
    for model in("v2_raw","v1_raw"):
        dest=out/model;dest.mkdir(exist_ok=True)
        path=S.OUT/f"{model}_trades.csv"
        t=pd.read_csv(path);opened=pd.read_csv(S.OUT/f"{model}_open_positions.csv")
        daily,marks,money=Q.candidate_daily(g,t,frame.index,fee=1.275,open_positions=opened)
        daily=daily.rename(model);daily.to_csv(dest/"candidate_daily.csv",index_label="date")
        marks.to_csv(dest/"marks.csv",index=False)
        Q.joint_losses(frame,daily).to_csv(dest/"joint_losses.csv",index=False)
        money["ledger_sha256"]=S.sha(path);manifest["models"][model]=money
        print("personal starting",model,flush=True)
        P.benchmark(frame,daily,dest)
        print("personal complete",model,flush=True)
    (out/"manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")


def accounts():
    S.authorize();out=BASE/"accounts";out.mkdir(parents=True,exist_ok=True)
    inv=json.loads((BASE/"context.json").read_text())
    if inv["changed"]:raise ValueError("Changed baseline inputs")
    base=json.loads(C.BASE_MANIFEST.read_text())
    if S.sha(C.PREPARED)!=base["expanded_cache_sha256"]:raise ValueError("Prepared cache changed")
    (out/"path_fixtures.json").write_text(json.dumps(path_fixtures(),indent=2)+"\n")
    C.OUT=out;C.REPLAY=S.OUT;C.MODES=MODES
    started=time.monotonic()
    with A.pinned_imports("scratch_data"):
        F50,F150=importlib.import_module("funded_sim"),importlib.import_module("funded_sim150")
        fb=importlib.import_module("funded_bootstrap")
        old=B.OUT
        try:B.OUT=out;B.synthetic_checks(F50,F150)
        finally:B.OUT=old
        with open(C.PREPARED,"rb") as f:lab=pickle.load(f)
        ledgers,eligible,inputs=C.read_inputs(lab)
        known=np.load(ROOT/"analysis/outputs/codex_r2vault/replay/known_closed.npy")
        fr=[];fp=[];er=[];ep=[]
        for fee in(1.04,1.24):
            if fee>1.04:lab.real_fees(.20,list(set(A.P.CURRENT_PLAN)|{"RS","DT"}))
            paths={}
            for mode,t in ledgers.items():
                w,r=candidate_paths(lab.g,t,fee,known)
                paths[mode]=(w[lab.tr],r[lab.tr])
                lab.W[mode],lab.C[mode]=paths[mode][0],paths[mode][1][:,-1]
                del w,r
            if fee==1.04:C.overlap(lab,eligible)
            a,b=C.funded(lab,fb,F50,F150,fee,eligible);fr+=a;fp+=b
            pd.DataFrame(fr).to_csv(out/"funded_summary.csv",index=False)
            pd.DataFrame(fp).to_csv(out/"funded_paired_differences.csv",index=False)
            a,b=C.evaluation(lab,"scratch_data",fee,paths,eligible,S.PREREG);er+=a;ep+=b
            pd.DataFrame(er).to_csv(out/"evaluation_summary.csv",index=False)
            pd.DataFrame(ep).to_csv(out/"evaluation_paired_differences.csv",index=False)
    manifest=dict(preregistration=S.PREREG,context=inv["reference"],prepared_sha256=base["expanded_cache_sha256"],
        fees=[1.04,1.24],models=list(MODES),whole21sessionwindows=True,paired_histories=1000,block=20,
        horizons=[250,500],seeds=[1,2,3,4],all_five_cohorts=list(C.COHORTS),production_parity=360,synthetic_parity=100,
        inputs=inputs,seconds=time.monotonic()-started,
        code_hashes={p:S.sha(ROOT/"analysis"/p) for p in(Path(__file__).name,"codex_r2vault_accounts.py","codex_anson_accounts.py")},
        limitations=A.P.BASELINE_LIMITS+["Baseline prepared cache and inherited known-closure entry-price marks preserved.",
            "Both50/150evaluation minute tie conventions preserved; personal daily marks do not measure margin liquidation."])
    (out/"manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
    print("accounts complete",time.monotonic()-started,flush=True)


if __name__=="__main__":
    ap=argparse.ArgumentParser();ap.add_argument("--phase",choices=["personal","accounts","fixtures"],required=True);a=ap.parse_args()
    if a.phase=="personal":personal()
    elif a.phase=="accounts":accounts()
    else:print(path_fixtures())
