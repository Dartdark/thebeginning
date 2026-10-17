"""Task 09 (ES MOC Follow) blind check, 2026-10-17: Antigravity's trades are one minute early. This rebuilds the rule on our
1-minute ES (jesse_es.npy, bar-open stamps) with the clock as is (= MultiCharts) and shifted one minute late (= reading
the close-stamped CSV as open-stamped), and matches each against Antigravity's tasks/out_09/trades.csv and the MC report.
  python3 analysis/jesse/task09_shift_check.py [SCRATCH_DIR]
"""
import sys, io, subprocess; sys.path.insert(0, "analysis/jesse")
import numpy as np, pandas as pd
SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
sys.argv = sys.argv[:1]
import compare as C

src = open("analysis/es_euro_close_check.py").read()
exec(src[src.index("def early_close"):src.index("\n\n\n", src.index("def early_close"))])   # same CME early-close rule


def rule(shift_min):
    c = np.load(SP + "jesse_es.npy")
    m = pd.DataFrame(c[:, 1:], columns=["o", "c", "h", "l", "v"], index=pd.to_datetime(c[:, 0], unit="ms") + pd.Timedelta(minutes=shift_min))
    b = m.resample("5min").agg(dict(o="first", h="max", l="min", c="last")).dropna()
    b["end"] = b.index + pd.Timedelta(minutes=5); b["date"] = b["end"].dt.normalize()
    d = b.groupby("date").agg(h=("h", "max"), l=("l", "min"), c=("c", "last")); pc = d["c"].shift(1)
    tr = (pd.concat([d["h"], pc], axis=1).max(axis=1) - pd.concat([d["l"], pc], axis=1).min(axis=1))[d.index.dayofweek < 5].iloc[1:]
    atr = tr.rolling(15).mean().shift(1).reindex(d.index).ffill()
    e = b.set_index("end")
    rows = []
    for dt in d.index[d.index >= "2018-01-02"]:
        if dt.dayofweek >= 5 or early_close(dt.date()): continue
        t0, t1, t2 = dt + pd.Timedelta("14h"), dt + pd.Timedelta("14h50min"), dt + pd.Timedelta("15h")
        if t0 not in e.index or t1 not in e.index: continue
        a = atr.get(dt, np.nan); mv = e.at[t1, "c"] - e.at[t0, "c"]
        if not a > 0 or abs(mv) < 0.30 * a or mv == 0: continue
        s = 1 if mv > 0 else -1; w = m.loc[t1:t2 - pd.Timedelta("1min")]
        if not len(w): continue
        en = w["o"].iloc[0]; sp = en - s * 0.25 * a; x = w["c"].iloc[-1]
        hit = (w["l"] <= sp) if s > 0 else (w["h"] >= sp)
        if hit.any(): x = sp
        rows.append(dict(entry_time=t1, side=s, entry=en, exit=x, points=(x - en) * s))
    return pd.DataFrame(rows)


def cmp(a, b, nm):
    for d in (a, b): d["day"] = d.entry_time.dt.normalize()
    mm = a.merge(b, on="day", how="outer", suffixes=("_a", "_b"), indicator="src"); both = mm[mm.src == "both"]
    print(f"{nm:<44} both {len(both):3d}, only rebuild {(mm.src == 'left_only').sum():3d}, only other {(mm.src == 'right_only').sum():3d}, "
          f"same side {(both.side_a == both.side_b).mean():.0%}, entry within 1 tick {((both.entry_a - both.entry_b).abs() <= 0.25).mean():.0%}")


if __name__ == "__main__":
    raw = subprocess.check_output(["git", "show", "origin/antigravity/jesse:tasks/out_09/trades.csv"]).decode()
    ag = pd.read_csv(io.StringIO(raw)); ag["entry_time"] = pd.to_datetime(ag.date + " " + ag.entry_time_ct)
    ag["side"] = np.where(ag.side == "long", 1, -1); ag = ag.rename(columns={"entry_price": "entry"})
    mc = C.mc_trades(C.REPORTS["ESMOCFollow"][0])
    hi = mc.entry_time.max().normalize() + pd.Timedelta(days=1)
    for sh in (0, 1):
        r = rule(sh); r = r[r.entry_time < hi]
        cmp(r.copy(), mc.copy(), f"rebuild, clock shifted {sh} min, vs MultiCharts"); cmp(r.copy(), ag[ag.entry_time < hi].copy(), f"rebuild, clock shifted {sh} min, vs Antigravity")
        print(f"   rebuild gross $ per ES trade: {r.points.mean() * 50:.0f} (n {len(r)})")
