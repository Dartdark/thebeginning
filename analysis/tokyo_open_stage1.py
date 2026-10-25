"""Stage 1 (look only) for the Tokyo-open idea card (checks/ideas/tokyo_open.md, 2026-10-25). NQ 2018-2022 ONLY (2023-26 is
kept for the stage-3 holdout). Tokyo opens at 09:00 JST = 00:00 UTC = 18:00 CT (US winter) / 19:00 CT (US summer).
  T = the open in CT on the evenings Sunday-Thursday. P15 = close(T+15) - close(T) (the first push); the reversal measure is
  sign(P15) x (close(T+H) - close(T+15)) for H = 75 / 135 minutes, in units of the daily ATR(15). Negative = the push reverses.
  Placebo: the same evenings at the OTHER clock hour (19:00 when Tokyo opens at 18:00 and vice versa): no open there.
  Gotobi (JST date's day in 5 / 10 / 15 / 20 / 25 / 30; weekend -> the Friday before; Japanese holidays ignored): NQ move from
  T to the 09:55 JST fix (T+55), gotobi vs ordinary nights. USD/JPY sanity check: Yahoo 60-minute JPY=X (recent ~2 years),
  the 00:00-01:00 UTC bar on gotobi vs ordinary days.
Output: analysis/outputs/tokyo_open_stage1_output.txt and analysis/outputs/tokyo_open_stage1.png
  python3 analysis/tokyo_open_stage1.py [SCRATCH_DIR]
"""
import sys, json, pickle, subprocess, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from grid24 import jof

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
g = pickle.load(open(SP + "g24.pkl", "rb")); C = pd.DataFrame(g.c).ffill(axis=1).to_numpy().ravel()   # ffill within the row
atr = g.daily_atr(15); TS = pd.DatetimeIndex(g.ts)
rows = []
for r, d in enumerate(TS):
    if d < pd.Timestamp("2018-01-01") or d > pd.Timestamp("2022-12-30") or d.dayofweek not in (6, 0, 1, 2, 3): continue
    t_open = pd.Timestamp(d.date(), tz="UTC") + pd.Timedelta(days=1)                     # 00:00 UTC of the next date
    hh = t_open.tz_convert("America/Chicago").hour                                         # 18 or 19
    a = atr[min(r + 1, len(atr) - 1)]
    if not np.isfinite(a) or a <= 0: continue
    jst = (d + pd.Timedelta(days=1))
    rows.append(dict(d=d, r=r, open_hh=hh, plac_hh=37 - hh, atr=a, jst=jst))
E = pd.DataFrame(rows)


def series(row, hh, lo=-60, hi=180):
    base = row * 1440 + hh * 60
    idx = np.arange(base + lo, base + hi + 1)
    x = C[idx]; return x - C[base]


def measure(hh_col):
    out = []
    for e in E.itertuples():
        s = series(e.r, getattr(e, hh_col))
        p = s[60 + 15]
        if not np.isfinite(p) or p == 0 or np.isnan(s).any(): continue
        sg = np.sign(p)
        out.append(dict(d=e.d, p=p / e.atr, r60=sg * (s[60 + 75] - s[60 + 15]) / e.atr, r120=sg * (s[60 + 135] - s[60 + 15]) / e.atr,
                        path=sg * s / e.atr, atr=e.atr, gross60=sg * (s[60 + 75] - s[60 + 15]) * 20))
    return pd.DataFrame(out)


def tst(x): x = pd.Series(x).dropna(); return x.mean() / x.std() * np.sqrt(len(x))


if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    A, Pl = measure("open_hh"), measure("plac_hh")
    print(f"\n1. NQ 2018-2022, {len(A)} Tokyo opens (evenings Sun-Thu). Reversal = sign(first 15-min push) x the next move, in ATR:")
    for nm, X in (("Tokyo open", A), ("placebo: same evenings, the other clock hour", Pl)):
        print(f"   {nm:<46} next 60 min {X.r60.mean():+.4f} ATR (t {tst(X.r60):+.1f}, ${-X.gross60.mean():+.1f} a fade gross per NQ) | "
              f"next 120 min {X.r120.mean():+.4f} (t {tst(X.r120):+.1f})")
    q = pd.qcut(A.p.abs(), 3, labels=["small", "mid", "big"])
    print("   by push size (Tokyo):", {k: f"{v.r60.mean():+.4f} ATR (t {tst(v.r60):+.1f}, n {len(v)}, fade ${-v.gross60.mean():+.0f})" for k, v in A.groupby(q)})
    qp = pd.qcut(Pl.p.abs(), 3, labels=["small", "mid", "big"])
    print("   by push size (placebo):", {k: f"{v.r60.mean():+.4f} ATR (t {tst(v.r60):+.1f}, fade ${-v.gross60.mean():+.0f})" for k, v in Pl.groupby(qp)})
    print("   by year (Tokyo, 60 min):", {y: f"{v.r60.mean():+.4f} (t {tst(v.r60):+.1f})" for y, v in A.groupby(A.d.dt.year)})
    print("   by season (Tokyo at 18:00 vs 19:00 CT):", {h: f"{A[E.set_index('d').open_hh.reindex(A.d).values == h].r60.mean():+.4f}" for h in (18, 19)})
    # gotobi
    j = E.jst
    gd = j.dt.day.isin([5, 10, 15, 20, 25, 30])
    fri_shift = (j.dt.dayofweek == 4) & ((j + pd.Timedelta(days=1)).dt.day.isin([5, 10, 15, 20, 25, 30]) | (j + pd.Timedelta(days=2)).dt.day.isin([5, 10, 15, 20, 25, 30]))
    E["gotobi"] = gd | fri_shift
    mv = []
    for e in E.itertuples():
        base = e.r * 1440 + e.open_hh * 60
        mv.append((C[base + 55] - C[base]) / e.atr if np.isfinite(C[base + 55]) and np.isfinite(C[base]) else np.nan)
    E["to_fix"] = mv
    gg_, oo = E[E.gotobi].to_fix.dropna(), E[~E.gotobi].to_fix.dropna()
    print(f"\n2. Gotobi: NQ from the Tokyo open to the 09:55 JST fix, in ATR: gotobi {gg_.mean():+.4f} (t {tst(gg_):+.1f}, n {len(gg_)}), "
          f"ordinary {oo.mean():+.4f} (t {tst(oo):+.1f}, n {len(oo)}); difference t "
          f"{(gg_.mean() - oo.mean()) / np.sqrt(gg_.var() / len(gg_) + oo.var() / len(oo)):+.1f}")
    try:
        r = subprocess.run(["curl", "-sS", "-m", "60", "-A", "Mozilla/5.0",
                            "https://query1.finance.yahoo.com/v8/finance/chart/JPY=X?range=730d&interval=60m"], capture_output=True, text=True)
        jj = json.loads(r.stdout)["chart"]["result"][0]
        fx = pd.Series(jj["indicators"]["quote"][0]["close"], index=pd.to_datetime(jj["timestamp"], unit="s")).dropna()
        fo = pd.Series(jj["indicators"]["quote"][0]["open"], index=pd.to_datetime(jj["timestamp"], unit="s")).reindex(fx.index)
        b = fx[fx.index.hour == 0] / fo[fo.index.hour == 0] - 1
        dd = b.index.normalize(); got = dd.day.isin([5, 10, 15, 20, 25, 30]) | ((dd.dayofweek == 4) & ((dd + pd.Timedelta(days=1)).day.isin([5, 10, 15, 20, 25, 30]) | (dd + pd.Timedelta(days=2)).day.isin([5, 10, 15, 20, 25, 30])))
        bg, bo = b[got] * 1e4, b[~got] * 1e4
        print(f"   USD/JPY sanity (Yahoo 60-min, {b.index[0].date()} .. {b.index[-1].date()}): 00:00-01:00 UTC bar gotobi {bg.mean():+.1f} bp "
              f"(t {tst(bg):+.1f}, n {len(bg)}) vs ordinary {bo.mean():+.1f} bp (t {tst(bo):+.1f})")
    except Exception as ex:
        print("   USD/JPY sanity check failed:", ex)
    # figure
    t = np.arange(-60, 181)
    fig, ax = plt.subplots(figsize=(9, 4.8), facecolor="#fcfcfb"); ax.set_facecolor("#fcfcfb")
    for X, nm, col in ((A, "Tokyo open", "#2a78d6"), (Pl, "Placebo (other clock hour)", "#eb6834")):
        m = np.mean(np.stack(X.path.values), axis=0); ax.plot(t, m, color=col, lw=2, label=nm)
        ax.text(t[-1] + 3, m[-1], nm, color="#52514e", fontsize=9, va="center")
    ax.axvline(0, color="#b5b4ad", lw=1); ax.axvline(15, color="#b5b4ad", lw=1, ls=":")
    ax.axhline(0, color="#b5b4ad", lw=1)
    ax.set_xlabel("minutes from the Tokyo open (09:00 JST)", color="#52514e"); ax.set_ylabel("NQ move, signed by the first 15-min push (ATR)", color="#52514e")
    ax.set_title("NQ around the Tokyo open, 2018-2022: does the first push reverse?", color="#0b0b0b", fontsize=11, loc="left")
    for s in ("top", "right"): ax.spines[s].set_visible(False)
    for s in ("left", "bottom"): ax.spines[s].set_color("#b5b4ad")
    ax.tick_params(colors="#52514e"); ax.legend(frameon=False, loc="upper left", fontsize=9); ax.set_xlim(-60, 230)
    fig.tight_layout(); fig.savefig("analysis/outputs/tokyo_open_stage1.png", dpi=150)
    print("\n   figure: analysis/outputs/tokyo_open_stage1.png")
