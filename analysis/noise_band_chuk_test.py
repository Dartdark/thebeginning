"""Chuk (2026), 'Noise-Band Intraday Momentum in Nasdaq-100 Futures' (SSRN 7609644; Antigravity paper screen 2026_10_18_b,
5/5). Rebuilt from the paper's Table 1 (frozen rule), pre-registered, no parameter changes:
  sigma_t = mean over the prior 14 sessions of |P_t / O - 1| at the same minute of the regular session (8:30-15:00 CT);
  U_t = max(O, C_-1)(1 + sigma_t), L_t = min(O, C_-1)(1 - sigma_t); O = 8:30 open, C_-1 = prior 15:00 close; VWAP from 8:30.
  5-minute bars. Entry checks only at the :00 / :30 bar closes from 9:00 to 14:30 CT: long if close > U and > VWAP, short
  if close < L and < VWAP; fill at the next bar's open. Stop: trailing, the band or VWAP whichever is closer, set at each
  5-minute close, active from the next bar (checked first on each bar; a gap through fills at the bar open). Flat at the
  close of the 14:55 CT bar (paper: 'the 15:55 bar' ET). Several trades a day, one position at a time.
  (The paper's 'conflict lock' with its companion ORB rule is left out: we don't run that rule.)
Costs: our standard per NQ $14.50 + 1 tick per market / stop fill ($24.50 round trip); also the paper's own $2 per MNQ
with no slippage, to compare with its +$10.26 a day (2020 - Jul 2026). Daily P&L is the unit, as in the paper.
Then: correlation and overlap with Vault Break (our MC-matched Python trades, scratch_data/jesse_VaultBreak.csv).
  python3 analysis/noise_band_chuk_test.py [SCRATCH_DIR]
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import jof
import metrics as Mx

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
g = pickle.load(open(SP + "g24.pkl", "rb"))
J0, J1 = jof(831), jof(1500)                        # minute columns 8:31 .. 15:00 (close-stamped)
tr = g.trading; dts = pd.DatetimeIndex(g.ts[tr]).normalize()
C = np.array([pd.Series(g.c[r, J0:J1 + 1]).ffill().to_numpy() for r in tr])
O = g.o[tr, J0]; H = g.h[tr, J0:J1 + 1]; L_ = g.l[tr, J0:J1 + 1]; V = np.nan_to_num(g.v[tr, J0:J1 + 1])
OP = g.o[tr, J0:J1 + 1]
mv = np.abs(C / O[:, None] - 1)
sig = pd.DataFrame(mv).rolling(14).mean().shift(1).to_numpy()
pc = np.r_[np.nan, C[:-1, -1]]
tp = (H + L_ + C) / 3; vw = np.nancumsum(np.nan_to_num(tp) * V, 1) / np.maximum(np.cumsum(V, 1), 1)


def run_day(i, tick=0.25):
    """Returns a list of (side, entry, exit, how) in points for one session."""
    if np.isnan(O[i]) or np.isnan(pc[i]) or np.isnan(sig[i]).all(): return []
    U = max(O[i], pc[i]) * (1 + sig[i]); Lb = min(O[i], pc[i]) * (1 - sig[i])
    ends = np.arange(4, J1 - J0 + 1, 5)            # 5-min bar ends: 8:35 .. 15:00 (index of last minute)
    pos, e, stop, out, je = 0, 0.0, np.nan, [], 0
    for b in ends:
        hhmm = 830 + (b + 1) // 60 * 100 + (b + 1) % 60
        s0 = b - 4
        if pos and not np.isnan(stop):             # stop check on this bar against the level set at the last close
            bl, bh, bo = np.nanmin(L_[i, s0:b + 1]), np.nanmax(H[i, s0:b + 1]), OP[i, s0]
            if pos > 0 and bl <= stop: out.append((pos, e, min(stop, bo) if not np.isnan(bo) else stop, "stop", je, b)); pos = 0
            elif pos < 0 and bh >= stop: out.append((pos, e, max(stop, bo) if not np.isnan(bo) else stop, "stop", je, b)); pos = 0
        c = C[i, b]
        if hhmm == 1455:
            if pos: out.append((pos, e, c, "time", je, b)); pos = 0
            break
        if not pos and hhmm % 100 in (0, 30) and 900 <= hhmm <= 1430 and b + 1 <= J1 - J0:
            side = 1 if (c > U[b] and c > vw[i, b]) else (-1 if (c < Lb[b] and c < vw[i, b]) else 0)
            if side:
                nxt = OP[i, b + 1]
                if not np.isnan(nxt): pos, e, je = side, nxt, b + 1
        if pos:
            stop = max(U[b], vw[i, b]) if pos > 0 else min(Lb[b], vw[i, b])
    if pos: out.append((pos, e, C[i, -1], "time", je, J1 - J0))
    return out


rows = []
for i in range(len(tr)):
    if dts[i] < pd.Timestamp("2018-01-01"): continue
    for side, e, x, how, j0, j1 in run_day(i):
        rows.append(dict(date=dts[i], i=i, side=side, e=e, x=x, j0=j0, j1=j1, pts=side * (x - e), how=how))
T = pd.DataFrame(rows)
T["nq"] = (T.pts - 2 * 0.25) * 20 - 14.50           # our standard, per NQ
T["mnq_paper"] = T.pts * 2 - 2.0                    # the paper's costs, per MNQ
alld = pd.Index(dts[dts >= "2018-01-01"])


def show(col, nm, sub=None):
    t = T if sub is None else T[sub]
    d = t.groupby("date")[col].sum().reindex(alld, fill_value=0.0)
    for lo, hi, lab in (("2018", "2027", "2018-2026"), ("2020", "2027", "2020-2026 (paper)"), ("2018", "2020", "2018-19"),
                        ("2023", "2027", "2023-2026")):
        x = d[(d.index >= lo) & (d.index < hi)]; n = t[(t.date >= lo) & (t.date < hi)][col]
        tt = x.mean() / x.std() * np.sqrt(len(x))
        print(f"   {nm:<34} {lab:<18} ${x.mean():6.2f}/day  {len(n):5d} trades ${n.mean():6.1f}/trade  t {tt:4.1f}  "
              f"Sharpe {x.mean() / x.std() * np.sqrt(252):4.2f}")
    return d


if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    print(f"\nTrades {len(T)}, exits {T.how.value_counts().to_dict()}")
    show("mnq_paper", "1 MNQ, paper's $2 costs")
    d = show("nq", "1 NQ, our costs ($24.50)")
    show("nq", "  longs", T.side > 0); show("nq", "  shorts", T.side < 0)
    print("   by year (1 NQ):", d.groupby(d.index.year).sum().round(0).to_dict())
    print("   metrics 1 NQ daily 2018-2026:", Mx.summary(d) if hasattr(Mx, "summary") else "")
    vb = pd.read_csv(SP + "jesse_VaultBreak.csv", parse_dates=["entry_time"])
    vb["date"] = vb.entry_time.dt.normalize(); vb["net"] = (vb.points - 0.5) * 20 - 14.5
    vd = vb.groupby("date").net.sum().reindex(alld, fill_value=0.0)
    both = (d != 0) & (vd != 0)
    print(f"\nVault Break overlap: VB days {int((vd != 0).sum())}, noise-band days {int((d != 0).sum())}, both {int(both.sum())}; "
          f"daily corr all days {np.corrcoef(d, vd)[0, 1]:.2f}, on days both trade {np.corrcoef(d[both], vd[both])[0, 1]:.2f}")
    nb_vbday = d[vd != 0]; nb_novb = d[(vd == 0) & (d != 0)]
    print(f"   noise-band on VB days ${nb_vbday.mean():.1f}/day (n {len(nb_vbday)}), on days VB is out ${nb_novb.mean():.1f} (n {len(nb_novb)})")
    nl = T[T.side < 0].groupby("date").nq.sum().reindex(alld, fill_value=0.0)
    print(f"   noise-band SHORTS only: corr with VB {np.corrcoef(nl, vd)[0, 1]:.2f}")
    T.to_csv(SP + "noise_band_trades.csv", index=False)
