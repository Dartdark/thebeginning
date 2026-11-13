"""G13 invariance (analysis/invariance.py) on every existing candidate with >= 60 trades (2026-11-08), read-only:
  tools/run_stamped.sh analysis/invariance_survey.py > analysis/outputs/invariance_survey_output.txt
"""
import sys, os, json, re; sys.path.insert(0, "analysis")
import pandas as pd, invariance as INV
out = []
for c in sorted(os.listdir("checks/candidates")):
    d = f"checks/candidates/{c}"; tf = f"{d}/trades.csv"
    if not os.path.exists(tf): continue
    meta = json.load(open(f"{d}/meta.json")) if os.path.exists(f"{d}/meta.json") else {"kind": "strategy"}
    T = pd.read_csv(tf, parse_dates=["date"]); T = T[T.date >= "2018-01-01"]
    if meta.get("kind") == "filter" and "kept" in T: T = T[T.kept.astype(bool)]
    if len(T) < 60: continue
    v = "?"
    if os.path.exists(f"{d}/verdict.md"):
        m = re.search(r"(PASS WITH CONCERNS|PASS|FAIL)", open(f"{d}/verdict.md").read()); v = m.group(1) if m else "?"
    ok, txt, rows = INV.gate2(T[[k for k in ("date", "net", "risk", "symbol") if k in T]])
    r3, r2 = rows.get("P3 time (years)"), rows.get("P2 VIX regime (past-only median)")
    f = lambda r: f"{r['sis']:.3f}/{r['tau']:.3f} p{r['p_perm']:.2f}" if r else "n/a"
    print(f"{c:<32} n={len(T):5d} checker={v:<19} G13={'PASS' if ok else 'FAIL'} | years {f(r3)} | VIX {f(r2)}", flush=True)
