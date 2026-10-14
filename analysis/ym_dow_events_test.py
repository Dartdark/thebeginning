"""YM's own events (2026-10-14): Dow heavyweight earnings and the 10-year (ZN), 2018-2026, 1 YM ($5 a point, tick 1),
$5 + 1 tick a fill = $15 a round trip (ES $30, NQ $17.25 for comparisons).
The Dow is price-weighted: GS, CAT, HD, UNH, AXP, JPM (data/dow_heavy_earnings.csv, Alpha Vantage; AMGN / V missing).
Pre-specified (before looking):
  A1 event session (pre-market report: that day; post-market: next day): follow / fade YM's 15:00 -> 8:30 move, 8:30 -> 15:00
  A2 Dow-specific part: rel = YM overnight return - ES overnight return; follow / fade sign(rel) in YM 8:30 -> 15:00
  A3 bank days (JPM or GS reporting): A1 and A2 on those alone
  B1 ZN overnight (15:00 -> 8:30) return z >= 1.5 in size: long YM if ZN up (yields down), short if down, 8:30 -> 15:00;
     same rule on ES and NQ (is YM special?), and the opposite sign
  B2 1-minute and 5-minute lead-lag 8:30-15:00: corr(ZN return over the last k min, YM return over the next k min) vs ES
  B3 ZN 5-min move >= 3 sd (rolling 20 days of 5-min moves) 8:35-14:30: YM in the implied direction for 30 min; also fade
  python3 analysis/ym_dow_events_test.py [SCRATCH_DIR]
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import jof
from co_oc_reversal_test import load, line

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
SPECS = {"YM": (5.0, 15.0), "ES": (50.0, 30.0), "NQ": (20.0, 17.25)}


def frame(g, hh=(830, 1500)):
    cf = pd.Series(g.c.ravel()).ffill().to_numpy(); tr = g.trading; idx = pd.DatetimeIndex(g.ts[tr])
    ok = ~np.isnan(g.c[tr, jof(830):jof(1500) + 1]).all(1)
    D = pd.DataFrame({h: cf[tr * 1440 + jof(h)] for h in hh}, index=idx)[ok]
    D["prev"] = D[1500].shift(1); return D[D.index >= "2018-01-01"]


if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    G = {s: (pickle.load(open(SP + "gy.pkl", "rb")) if s == "YM" else pickle.load(open(SP + "ge.pkl", "rb")) if s == "ES"
             else pickle.load(open(SP + "g24.pkl", "rb"))) for s in ("YM", "ES", "NQ")}
    zn = load("ZN")
    F = {s: frame(g) for s, g in G.items()}; FZ = frame(zn)
    idx = F["YM"].index.intersection(F["ES"].index).intersection(F["NQ"].index).intersection(FZ.index)
    for s in F: F[s] = F[s].loc[idx]
    FZ = FZ.loc[idx]
    day = {s: (F[s][1500] - F[s][830]) * SPECS[s][0] for s in F}
    on = {s: np.log(F[s][830] / F[s].prev) for s in F}; onz = np.log(FZ[830] / FZ.prev)
    E = pd.read_csv("data/dow_heavy_earnings.csv"); E["d"] = pd.to_datetime(E.reportedDate); E = E[E.d >= "2017-12-15"]
    def sess(r):
        k = idx.searchsorted(r.d) if r.reportTime == "pre-market" else idx.searchsorted(r.d, side="right")
        return idx[k] if k < len(idx) else pd.NaT
    E["sess"] = E.apply(sess, axis=1); E = E.dropna(subset=["sess"])
    ev = pd.Series(idx.isin(E.sess.unique()), index=idx)
    bank = pd.Series(idx.isin(E[E.ticker.isin(["JPM", "GS"])].sess.unique()), index=idx)
    c = SPECS["YM"][1]
    print(f"event sessions {ev.sum()} ({ev.sum() / len(idx) * 252:.0f} a year), bank days {bank.sum()}")
    print(f"|YM overnight| event {on['YM'][ev].abs().mean() * 1e4:.0f} bp vs other {on['YM'][~ev].abs().mean() * 1e4:.0f}; "
          f"|YM - ES overnight| event {(on['YM'] - on['ES'])[ev].abs().mean() * 1e4:.1f} bp vs other {(on['YM'] - on['ES'])[~ev].abs().mean() * 1e4:.1f}")
    rel = on["YM"] - on["ES"]
    for nm, m in (("A1/A2 all event sessions", ev), ("A3 bank days", bank)):
        print(f"\n{nm}")
        for lab, sig in (("follow YM overnight", np.sign(on["YM"])), ("fade YM overnight", -np.sign(on["YM"])),
                         ("follow Dow-specific (YM - ES)", np.sign(rel)), ("fade Dow-specific (YM - ES)", -np.sign(rel))):
            x = sig * day["YM"] - c
            print(line(x[m], lab, 36)); 
            if nm.startswith("A1"): print(line(x[~ev], "   placebo (other days)", 36))
    print("\nB1 big ZN overnight move: trade the index in the yields-down = long direction, 8:30 -> 15:00")
    zz = (onz.abs() - onz.abs().rolling(60).mean().shift(1)) / onz.abs().rolling(60).std().shift(1)
    big = zz >= 1.5
    for s in ("YM", "ES", "NQ"):
        x = np.sign(onz) * day[s] - SPECS[s][1]; print(line(x[big], f"{s} with ZN (n big {int(big.sum())})", 36))
        print(line(-np.sign(onz)[big] * day[s][big] - SPECS[s][1], f"{s} against ZN", 36))
    print("\nB2 lead-lag 8:30-15:00 (pooled minutes)")
    def mins(g, k):
        tr = g.trading; idx_g = pd.DatetimeIndex(g.ts[tr]); keep = idx_g.isin(idx)
        a = pd.DataFrame(g.c[tr[keep], jof(830):jof(1500) + 1]).ffill(axis=1).to_numpy(); return np.log(a[:, k::k][:, :] ) if False else np.log(a)
    Lz, Ly, Le = mins(zn, 1), mins(G["YM"], 1), mins(G["ES"], 1)
    n = min(len(Lz), len(Ly), len(Le)); Lz, Ly, Le = Lz[-n:], Ly[-n:], Le[-n:]
    for k in (1, 5):
        rz = Lz[:, k::k] - Lz[:, :-k:k][:, :Lz[:, k::k].shape[1]]
        ry = Ly[:, k::k] - Ly[:, :-k:k][:, :rz.shape[1]]; re = Le[:, k::k] - Le[:, :-k:k][:, :rz.shape[1]]
        a, b, e_ = rz[:, :-1].ravel(), ry[:, 1:].ravel(), re[:, 1:].ravel()
        ok = ~np.isnan(a) & ~np.isnan(b) & ~np.isnan(e_)
        same = np.corrcoef(rz[:, 1:].ravel()[ok], ry[:, 1:].ravel()[ok])[0, 1]
        print(f"   k={k} min: corr(ZN last k, YM next k) {np.corrcoef(a[ok], b[ok])[0, 1]:+.4f}, (ZN, ES next) {np.corrcoef(a[ok], e_[ok])[0, 1]:+.4f}; same-bar ZN-YM {same:+.3f}")
    print("\nB3 ZN 5-min shock (>= 3 sd) 8:35-14:30: YM 30 min in the implied direction (yields down = long)")
    out = []
    rz5 = Lz[:, 5:] - Lz[:, :-5]; sd = pd.DataFrame(np.abs(rz5)).stack().std()
    dates = idx[-n:]
    for i in range(n):
        s_ = pd.Series(rz5[i]).rolling(1).mean().to_numpy()
        for j in range(0, rz5.shape[1] - 30):
            if abs(rz5[i, j]) >= 3 * np.nanstd(rz5[max(0, i - 20):i].ravel()) if i >= 20 else False:
                m = j + 5
                if m > jof(1430) - jof(830): break
                y0, y1 = np.exp(Ly[i, m]), np.exp(Ly[i, m + 30])
                out.append((dates[i], np.sign(rz5[i, j]), (y1 - y0) * 5.0)); break
    o = pd.DataFrame(out, columns=["d", "s", "mv"]).set_index("d")
    print(line(o.s * o.mv - c, "YM follow ZN shock, 30 min", 36)); print(line(-o.s * o.mv - c, "YM fade, 30 min", 36))
