"""Run a candidate's bench script and save its lab entries (W, C, stop) for the replacement sweep.
  python3 analysis/replacement_harvest.py SCRIPT KEY [KEY ...]   -> scratch_data/repl_<KEY>.pkl"""
import sys, io, contextlib, runpy, pickle, time, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
script, keys = sys.argv[1], sys.argv[2:]
t0 = time.time(); sys.argv = ["x", "scratch_data"]
with contextlib.redirect_stdout(io.StringIO()):
    ns = runpy.run_path(f"analysis/{script}.py", run_name="__main__")
lab = ns.get("lab")
for k in keys:
    if lab is None or k not in lab.W: print(f"{script}: {k} MISSING"); continue
    pickle.dump(dict(W=lab.W[k], C=lab.C[k], stop=lab.stop.get(k), dates=lab.g.ts[lab.tr]), open(f"scratch_data/repl_{k}.pkl", "wb"))
    print(f"{script}: {k} saved ({time.time() - t0:.0f}s)")
