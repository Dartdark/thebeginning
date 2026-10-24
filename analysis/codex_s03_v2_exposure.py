"""Both-side source/VaultBreak minute overlap, without new return trials.

Only the closest shared leg is measured here; this is not an estimate of
whole-account gross positions or of rescue before an actual account breach.
"""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"agents/codex/runtime/or_pullback_python"),str(ROOT/"analysis")]
import importlib
import json
import pickle
import numpy as np
import pandas as pd
import codex_s03_v2_replay as S
import codex_anson_plan as A
import codex_or_pullback_exposure as E
BASE=ROOT/"analysis/outputs/codex_s03_v2"


def main():
    S.authorize()
    with open(ROOT/"scratch_data/g24.pkl","rb") as f:g=pickle.load(f)
    dates=pd.DatetimeIndex(g.ts[g.trading]);shape=(len(dates),1440)
    lookup={int(row):i for i,row in enumerate(g.trading)}
    flags=pd.read_pickle(ROOT/"scratch_data/single_print_sessions.pkl").flag.reindex(dates).fillna(False).to_numpy(bool)
    common=pd.read_csv(BASE/"accounts/common_day_audit.csv").common_account_eligible.to_numpy(bool)
    with A.pinned_imports("scratch_data"):
        pf=importlib.import_module("portfolio");build=importlib.import_module("build_lab")
        source=ROOT/build.REPORTS["VB"][0]
        vb=pf.load_mc(g,str(source))
    sizes={"50K_funded":np.where(flags,1.,2.),"150K_funded":np.where(flags,1.,3.),
           "50K_evaluation":np.full(len(dates),8.),"150K_evaluation":np.full(len(dates),20.),
           "personal":np.ones(len(dates))}
    rows=[]
    for context,qty in sizes.items():
        vl,vs,_=E.occupancy(vb,lookup,qty,shape)
        for ver in("v2","v1"):
            model=ver+("_raw" if context=="personal" else"_apex")
            t=pd.read_csv(S.OUT/f"{model}_trades.csv")
            if context!="personal":t=t[t.date.isin(dates[common].strftime("%Y-%m-%d"))]
            t["j0"]=t.entry_j;t["j1"]=t.exit_j-(t.exit_phase=="open").astype(int)
            cl,cs,_=E.occupancy(t,lookup,np.ones(len(dates)),shape)
            assert (cl+cs).max()<=1
            for period,lo in(("2018_plus","2018-01-01"),("2023_plus","2023-01-01"),("2025_plus","2025-01-01")):
                day=np.asarray(dates>=lo)&(np.ones(len(dates),bool) if context=="personal" else common)
                held=((cl+cs)>0)&day[:,None];n=int(held.sum())
                same=((cl>0)&(vl>0))|((cs>0)&(vs>0))
                opp=((cl>0)&(vs>0))|((cs>0)&(vl>0))
                for amount in((1,2,4) if context.startswith("150") else(1,2)):
                    rows.append(dict(context=context,model=model,period=period,candidate_mnq=amount,
                        held_minutes=n,held_days=int(held.any(axis=1).sum()),
                        VB_overlap_fraction=float((held&((vl+vs)>0)).sum()/n),
                        same_side_fraction=float((held&same).sum()/n),opposite_side_fraction=float((held&opp).sum()/n),
                        maximum_VB_plus_candidate_gross=int((vl[held]+vs[held]+amount).max()),
                        scope="Closest leg only; full-size integer quantities before cushion reductions; MC endpoints inclusive"))
    pd.DataFrame(rows).to_csv(BASE/"minute_VB_overlap.csv",index=False)
    (BASE/"exposure_manifest.json").write_text(json.dumps(dict(source=str(source),sha256=S.sha(source),
        script_sha256=S.sha(__file__),new_strategy_returns=False,whole_account_exposure=False,
        breach_timing="joint minute account simulators govern risk; no actual breach-time rescue inferred"),indent=2)+"\n")
    print("Saved source/VB minute overlap",len(rows),flush=True)


if __name__=="__main__":main()
