"""Frozen research audit configuration, not live trading inputs."""
from pathlib import Path
import hashlib
import json
import os

ROOT = Path(__file__).resolve().parents[1]
SOURCE = Path(os.environ.get("PORTFOLIO_AUDIT_SOURCE", "/workspace/scratch/portfolio_audit_source"))
SCRATCH = Path(os.environ.get("PORTFOLIO_AUDIT_SCRATCH", "/workspace/scratch"))
RUNTIME = ROOT / "agents/codex/runtime/portfolio_audit_20261031"
OUT = ROOT / "analysis/outputs/codex_portfolio_audit_20261031"
SOURCE_COMMIT = "c3126aa01796133f3aecb368e688726931dea440"
PLAN_COMMIT = "671f7f1"
START, END = "2018-04-02", "2026-07-07"
SCENARIOS = {"main": (1.04, 1), "fee_124": (1.24, 1), "stress": (2.08, 2)}
MARKETS = {"NQ": (2., .25), "ES": (5., .25), "CL": (100., .01)}
ROSTERS = {
    "evaluation_50": {"VB": 8, "ONB30": ["risk", 1100, .25], "EOS": ["risk", 500, .30], "BRIDGE": 2},
    "evaluation_150": {"VB": 20, "ONB30": ["risk", 2750, .25], "EOS": ["risk", 1250, .30], "BRIDGE": 5},
    "funded_50": {"VB_N": 2, "VB_F": 1, "ONBML": ["risk", 400, .30], "OT": 1,
                  "EOS": ["risk", 700, .30], "LDF": 2, "NFP": ["risk", 500, .50],
                  "BRIDGE": 1, "CLS": 2, "MOC": 2, "TOS": 1},
    "funded_150": {"VB_N": 3, "VB_F": 1.5, "ONBML": ["risk", 600, .30], "MON": 1.5,
                   "EOS": ["risk", 1050, .30], "LDF": 3, "NFP": ["risk", 750, .50],
                   "BRIDGE": 1.5, "CLS": 3, "MOC": 3, "RS": 1, "DT": 2, "OT": 2},
}
PERSONAL_CORE = {"VaultBreak": "VB", "OvernightBiasML": "ONBML", "MondayLong": "MON",
                 "ExpirationOpenShort": "EOS", "LateDayFlow": "LDF", "NFPFade": "NFP",
                 "BridgeMondayLong": "BRIDGE", "CLSundayFade_perMCL": "CLS",
                 "ESMOCFollow_perMES": "MOC", "RelativeStrength": "RS"}


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for block in iter(lambda: f.read(1024*1024), b""): h.update(block)
    return h.hexdigest()


def dump(path, obj):
    import numpy as np
    def clean(x):
        if isinstance(x, dict): return {str(k): clean(v) for k, v in x.items()}
        if isinstance(x, (tuple, list)): return [clean(v) for v in x]
        if isinstance(x, np.generic): return clean(x.item())
        if isinstance(x, float) and not np.isfinite(x): return None
        return x
    Path(path).write_text(json.dumps(clean(obj), indent=2, default=str, allow_nan=False)+"\n")
