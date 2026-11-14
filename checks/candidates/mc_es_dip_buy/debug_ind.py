"""Debug: replica indicator values vs the reference's at every 1h close (run from repo root)."""
import sys, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd, importlib.util as iu
sp = iu.spec_from_file_location("esr", "checks/candidates/mc_es_dip_buy/replica.py"); RP = iu.module_from_spec(sp); sp.loader.exec_module(RP)
src = open("analysis/spy_dip_filter_settle.py", encoding="utf-8").read().split("\nSPEC = ")[0]
G = {"__name__": "ref", "__doc__": "x\n"}; exec(compile(src, "spy_dip_ref", "exec"), G)
E = G["E"]; atr, dmi, ema, htf_at = E["atr"], E["dmi"], E["ema"], E["htf_at"]
mm, bb = RP.load()
m1 = mm.copy(); m1.index = m1.index - pd.Timedelta(minutes=1)
agg = {"open": "first", "high": "max", "low": "min", "close": "last"}
b = m1.resample("1h", label="left", closed="left").agg(agg).dropna(); h4 = m1.resample("4h", label="left", closed="left").agg(agg).dropna()
C = b.close.to_numpy()
ref = pd.DataFrame({"ST4": htf_at(b, h4, G["supertrend"](h4, 22, 2.0)), "A4": htf_at(b, h4, atr(h4)), "ADX4": htf_at(b, h4, dmi(h4)[2]),
                    "E18": ema(C, 18), "A1": atr(b)}, index=b.index + pd.Timedelta(hours=1))
dbg = []; RP.run(mm, bb, dbg=dbg)
D = pd.DataFrame(dbg, columns=["T", "ST4", "A4", "ADX4", "E18", "A1", "N4"]).set_index("T")
j = ref.join(D, rsuffix="_rep")
for c in ("ST4", "A4", "ADX4", "E18", "A1"):
    d = (j[c] - j[c + "_rep"]).abs(); late = j.index >= "2017-09-01"
    print(f"{c}: max abs diff after 2017-09 {d[late].max():.6f}; share of bars differing > 1e-6: {np.mean(d[late] > 1e-6):.2%}")
d = (j.A4 - j.A4_rep).abs(); x = j[(d > 1e-6) & (j.index >= "2017-09-01")]
print(x.head(12).to_string())
print("4h candles: ref", len(h4), "replica N4 at end", D.N4.iloc[-1])
