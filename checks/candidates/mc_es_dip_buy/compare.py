"""Compare the ES replica with the reference analysis/spy_dip_filter_settle.py (spy('ES'), session dating, 'drop trades' = shadow version).
Run from repo root after replica.py."""
import sys, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
OUT = "checks/candidates/mc_es_dip_buy/"
src = open("analysis/spy_dip_filter_settle.py", encoding="utf-8").read().split("\nSPEC = ")[0]
G = {"__name__": "ref", "__doc__": "x\n"}; exec(compile(src, "spy_dip_ref", "exec"), G)
pd_, np_ = G["pd"], G["np"]
b, sig, plan, mg = G["spy"]("ES")
T0 = G["simulate"](b, sig, plan, manage=mg)
entry_t = b.index + pd.Timedelta(hours=1); ses = pd.DatetimeIndex((entry_t + pd.Timedelta(hours=7)).normalize())
rise = G["prior"](G["SR"]["VIX/VIX3M (term structure)"], ses, G["RULES"]["rising"]) == 1
bi = np.searchsorted(b.index.values, T0.t.values)
usd = lambda t: (t.ret * t.e * 50.0 - 5.0 - 12.5 - np.where(t.why == "target", 0.0, 12.5)) / 10 - 0.55
T0 = T0.assign(usd=usd(T0), kept=~rise[bi], t_close=T0.t + pd.Timedelta(hours=1))
jx = np.searchsorted(b.index.values, T0.tx.values) + 1; T0["x_close"] = b.index[np.minimum(jx, len(b) - 1)] + pd.Timedelta(hours=1)   # simulate labels tx one candle before the exit candle
T0.to_csv(OUT + "ref_trades_unfiltered.csv", index=False)
K = T0[T0.kept].reset_index(drop=True); K.to_csv(OUT + "ref_trades_session_drop.csv", index=False)
blk = pd.read_csv("scratch_data/spy_dip_ES_session_signal.csv", parse_dates=["t", "tx"])
lines = []
def pr(*a):
    s = " ".join(str(x) for x in a); print(s); lines.append(s)
yrs = lambda t: (t.max() - t.min()).days / 365.25
tt = lambda x: x.mean() / x.std(ddof=1) * np.sqrt(len(x))
pr(f"reference: unfiltered {len(T0)} trades ${T0.usd.sum():,.0f}; session+drop {len(K)} trades ${K.usd.sum():,.0f} (${K.usd.sum() / yrs(K.t):,.0f}/yr, t {tt(K.usd):.2f}); block-signals file {len(blk)} trades")
for st in ("1h", "1min"):
    S = pd.read_csv(OUT + f"shadow_{st}.csv", parse_dates=["t", "tx", "ses"]); R = pd.read_csv(OUT + f"real_{st}.csv", parse_dates=["entry_time", "exit_time", "shadow_t"])
    m = T0.merge(S, left_on=["t_close", "side"], right_on=["t", "side"], how="outer", suffixes=("_ref", "_rep"), indicator=True)
    bo = m[m._merge == "both"]
    pr(f"\n=== stops on {st} bars ===")
    pr(f"shadow vs reference unfiltered: ref {len(T0)}, replica {len(S)}, same entry bar+side {len(bo)} ({len(bo) / len(T0):.1%} of ref, {len(bo) / len(S):.1%} of replica); "
       f"same exit bar {np.mean(bo.x_close == bo.tx_rep):.1%}; same exit kind {np.mean(bo.why_ref == bo.why_rep):.1%}; filter flag agrees {np.mean(bo.kept_ref == bo.kept_rep):.1%}")
    pr(f"  shadow P&L corr per matched trade {np.corrcoef(bo.usd_ref, bo.usd_rep)[0, 1]:.4f}; matched ref ${bo.usd_ref.sum():,.0f} vs replica shadow ${bo.usd_rep.sum():,.0f}")
    pr("  unmatched ref:", m[m._merge == "left_only"][["t_close", "side"]].astype(str).values.tolist()[:6], " unmatched replica:", m[m._merge == "right_only"][["t_rep", "side"]].astype(str).values.tolist()[:6])
    # real vs reference session + drop trades
    R = R[R.entry_time >= "2017-06-01"]
    mr = K.merge(R, left_on="t_close", right_on="shadow_t", how="outer", indicator=True); br = mr[mr._merge == "both"]
    pr(f"real vs ref session+drop: ref {len(K)} ${K.usd.sum():,.0f}, replica real {len(R)} ${R.usd.sum():,.0f} (${R.usd.sum() / yrs(R.entry_time):,.0f}/yr, t {tt(R.usd):.2f}); "
       f"matched by shadow entry {len(br)} ({len(br) / len(K):.1%} of ref); P&L corr {np.corrcoef(br.usd_x, br.usd_y)[0, 1]:.3f}")
    pr(f"  matched: ref ${br.usd_x.sum():,.0f} vs replica ${br.usd_y.sum():,.0f}; difference per trade mean ${(br.usd_y - br.usd_x).mean():+.2f}; "
       f"unmatched ref {(mr._merge == 'left_only').sum()} ${mr[mr._merge == 'left_only'].usd_x.sum():,.0f}, unmatched replica {(mr._merge == 'right_only').sum()} ${mr[mr._merge == 'right_only'].usd_y.sum():,.0f}")
    br = br.assign(d=br.usd_y - br.usd_x, gap=(br.entry_time - br.t_close) > pd.Timedelta(hours=1))
    pr(f"  entries filled after the 16:00-17:00 break / weekend (fill bar not the next hour): {int(br.gap.sum())}, P&L diff on them ${br.d[br.gap].sum():+,.0f}; others ${br.d[~br.gap].sum():+,.0f}")
    pr(f"  exits: replica {R.how.value_counts().to_dict()}; ref {K.why.value_counts().to_dict()}")
    for y in range(2017, 2027):
        a_ = K[K.t.dt.year == y].usd.sum(); c_ = R[R.entry_time.dt.year == y].usd.sum()
        pr(f"   {y}: ref ${a_:+8,.0f}  replica ${c_:+8,.0f}")
    if st == "1h":
        S.assign(date=S.tx.dt.normalize().dt.date, net=S.usd)
        fl = R.assign(entry_time=R.entry_time, exit_time=R.exit_time)[["entry_time", "exit_time", "side", "entry", "exit", "usd"]]
        fl.to_csv(OUT + "real_for_gates.csv", index=False)
open(OUT + "compare_output.txt", "w").write("\n".join(lines) + "\n")
