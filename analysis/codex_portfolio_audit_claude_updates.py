"""Verify Claude's three audit updates; metadata and synthetic checks only.

No historical strategy rerun, new return selection or change to trading code.
"""
from pathlib import Path
import hashlib
import importlib
import json
import os
import subprocess
import sys
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
SOURCE=Path(sys.argv[1] if len(sys.argv)>1 else "/workspace/scratch/claude_audit_updates").resolve()
REF="d654fda13d43f3b481441168336586bb89bd9d9e"
OUT=ROOT/"analysis/outputs/codex_portfolio_audit_claude_updates_20261030"
OUT.mkdir(parents=True,exist_ok=True)
os.environ.setdefault("NUMBA_CACHE_DIR",str(ROOT/"agents/codex/runtime/audit_updates_numba"))
sys.dont_write_bytecode=True
head=subprocess.check_output(["git","-C",str(SOURCE),"rev-parse","HEAD"],text=True).strip()
assert head==REF,"Review belongs to the pinned three audit-update commits"
sys.path.insert(0,str(SOURCE/"analysis"));sys.argv=[__file__,"/workspace/scratch","library"]
os.chdir(SOURCE)
P=importlib.import_module("plan150_integer_test")
ST=importlib.import_module("swing_target_bench")
F=importlib.import_module("funded_sim")

plans=P.plans();chosen=plans["all 1.5 -> 1"]
assert all(isinstance(v,tuple) or float(v).is_integer() for v in chosen.values())
assert {k:chosen[k] for k in P.HALF}=={k:1 for k in P.HALF}
assert chosen["DT"]==2 and "ST" not in chosen
size_checks=[]
for f in [.5,.75,1.]:
    size_checks.append(dict(cushion_factor=f,
        old={k:int(np.floor(plans["old x 1.5 (fractional)"][k]*f)) for k in P.HALF},
        new={k:int(np.floor(chosen[k]*f)) for k in P.HALF}))

# A common conservative path error can affect two plans differently at a floor.
# Both reach balance50500/floor50100 before their last day. DLL is below that floor.
close=np.array([2100.,0.,-600.,100.])
case={}
for label,low in [("A",np.array([-1.,-1100.,-600.,-390.])),
                  ("B",np.array([-1.,-1100.,-600.,-370.]))]:
    actual=np.asarray(F.run_pa(low,close,0,4,0.,False,True)).tolist()
    biased=np.asarray(F.run_pa(low-20.,close,0,4,0.,False,True)).tolist()
    case[label]=dict(original=actual,common_20_dollar_adverse_bias=biased)
assert case["A"]["original"][3]==0 and case["A"]["common_20_dollar_adverse_bias"][3]==1
assert case["B"]["original"][3]==case["B"]["common_20_dollar_adverse_bias"][3]==0

legacy50=ST.plans50()["50K plan"]
assert "RS_L" in legacy50 and not any(k in legacy50 for k in ["T","TOS","TOS_T"])
personal=(SOURCE/"analysis/personal_portfolio.py").read_text()
ladder=(SOURCE/"analysis/personal_ladder.py").read_text()
overlap=(SOURCE/"analysis/opposing_overlap_check.py").read_text()
assert 'FWD = ["FC2B", "Kusho", "S47", "S30"]' in ladder
assert 'if c not in FWD' in ladder and 'ladder(P, FWD, start=ch)' in ladder
assert 'swing_target_bench' in overlap and 'STB.plans50()["50K plan"]' in overlap
assert 'w=bk[i]' in overlap and 'np.floor' not in overlap
assert "Twin: no v2.1 ledger exists" in personal
assert 'assign(date=k21.exit_date)' in personal
assert 'P = runpy.run_path("analysis/personal_portfolio.py", run_name="__main__")["P"]' in ladder

paths=["analysis/plan150_integer_test.py","analysis/outputs/plan150_integer_test_output.txt",
       "analysis/opposing_overlap_check.py","analysis/outputs/opposing_overlap_check_output.txt",
       "analysis/personal_ladder.py","analysis/outputs/personal_ladder_output.txt",
       "analysis/personal_portfolio.py","analysis/funded_sim.py","analysis/funded_sim150.py",
       "analysis/overnight_tick_bench.py","analysis/swing_target_bench.py",
       "funded_strategies/FUNDED_PLAN.md","personal_strategies/PORTFOLIO.md","TODO.md"]
out=dict(source_commit=head,code_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    independent_historical_return_reruns=0,new_alpha_definitions=0,
    verified_updates=dict(explicit150K_integer_chart_inputs=True,integer_sizing_fixtures=size_checks,
        DT2_retained_ST_not_reintroduced=True,current19_label_ladder_refreshed=True,
        four_forward_only_sleeves_remain_separate=True),
    qualifications=dict(
        overlap50_roster=legacy50,
        overlap50_roster_is_historical_RS_long_not_current_TOS=True,
        overlap_uses_fractional_risk_bases_without_executable_floor=True,
        overlap_excludes_overnight_tick=True,
        no_full_shared_price_account_replay_in_three_updates=True,
        common_bias_can_change_relative_failure_outcomes=case,
        greedy_cleared_subset_comparisons=sum(range(1,16)),
        greedy_forward_subset_comparisons=sum(range(1,5)),
        greedy_ranking_uses_same_historical_assembly_and_bootstrap_for_selection=True,
        new_independent_validation_in_personal_ladder=False,
        four_piece_capital_threshold_from_saved_output=10935,
        four_piece_DD_p95_from_saved_output=2187,
        DD_fraction_of_10000=2187/10000,
        inherited_Twin_v1_Kusho_exit_day_OT_cutoff_limits_unchanged=True),
    sources={p:hashlib.sha256((SOURCE/p).read_bytes()).hexdigest() for p in paths},
    evidence_boundary="Source/settings verification and synthetic account counterexample; Claude saved performance numbers are not independently rerun here")
(OUT/"verification.json").write_text(json.dumps(out,indent=2,default=str)+"\n")
print(json.dumps({"source_commit":head,"integer_inputs_verified":True,
    "synthetic_counterexample_passed":True,"greedy_subset_comparisons":130,
    "overlap50_uses_historical_roster":True,"independent_historical_return_reruns":0},indent=2))
