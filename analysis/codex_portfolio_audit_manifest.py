"""Record final audit provenance without running economic calculations."""
from codex_portfolio_audit_config import *
from importlib.metadata import version
import subprocess

inputs=["NEW_CHAT_BRIEF.md","funded_strategies/FUNDED_PLAN.md","personal_strategies/PORTFOLIO.md",
        "analysis/personal_portfolio.py","analysis/portfolio.py","analysis/funded_sim.py","analysis/funded_sim150.py",
        "agents/tasks/plan_daily_pnl.csv","checks/candidates/fc_2b/trades.csv",
        "checks/candidates/twin_continuation/trades.csv","checks/candidates/dual_thrust/trades.csv",
        "checks/candidates/kusho/python_trades_v9_rolladj.csv","checks/candidates/s47_v2/python_trades_v2.csv",
        "checks/candidates/overnight_tick/trades.csv","checks/candidates/swing_target/mc_trades_v3.csv",
        "checks/candidates/papertrend/mc_trades_claude.csv","checks/candidates/s30_ibs/daily_nq_es_per_micro.csv",
        "checks/candidates/s30_ibs/python_trades_NQ.csv","checks/candidates/s30_ibs/python_trades_ES.csv"]
dump(OUT/"delivery_manifest.json",dict(source_commit=SOURCE_COMMIT,plan_commit=PLAN_COMMIT,
    source_inputs={p:dict(sha256=sha(SOURCE/p),bytes=(SOURCE/p).stat().st_size) for p in inputs},
    dependencies={k:version(k) for k in ["numpy","pandas","scipy","numba","openpyxl","matplotlib"]},
    audit_code={p.name:sha(p) for p in (ROOT/"analysis").glob("codex_portfolio_audit_*.py")},
    final_run_logical_identity="verified root outputs only; archived account preset failures are invalid150K evidence",
    output_files={str(p.relative_to(OUT)):dict(sha256=sha(p),bytes=p.stat().st_size)
                  for p in OUT.rglob("*") if p.is_file() and p.name!="delivery_manifest.json"},
    no_new_alpha_definitions=True,independent_review_pending=True))
print("DELIVERY MANIFEST SAVED")
