"""US100 Donchian trend (Wong 2026, SSRN 6722841; author's MQL5 'US100_Turtle_Donchian_Trend_EA'), run on NQ by Claude because Codex's
executor was blocked (user 2026-11-08). Codex's frozen plan (codex/work agents/codex/plans/us100_donchian_6722841_build_20261108.md):
  15-min bars (24h, from 1-min), decisions at each new bar from completed bars only. Long only, one position, no target.
  entry: last close > high of the preceding 160 bars (excluding the last bar); channel exit: last close < low of the preceding 60 bars
  ATR(80) Wilder on 15-min true range; initial stop 1.5 ATR; trailing stop = max(stop, last close - 2 ATR), updated at each new bar.
  Stop active intrabar (15-min high / low; fill at the worse of open / stop). Market entries / exits at the new bar's open.
  SOURCE arm: holds across sessions / weekends (personal only; continuous contract: roll jumps are in the P&L, a stated limit).
  APEX arm: flat at the open of the 15:45 CT bar (11:45 on CME early-close days), no entries from then until the 17:00 reopen.
  Costs per NQ: $7.25 + 1 tick per market / stop fill. Gate (Codex's): 2018-22 net > 0 and daily t >= 2, else stop; 2023+ only after.
  tools/run_stamped.sh analysis/us100_donchian_test.py > analysis/outputs/us100_donchian_test_output.txt
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
import metrics as M
from replica import is_early_close

PV, TICK, COMM = 20.0, 0.25, 7.25


def bars15(g):
    out = []
    for r in range(g.D):
        c = g.c[r]
        if np.isnan(c).all(): continue
        for s in range(0, 1440, 15):
            seg = slice(s, s + 15); cc = c[seg]; ok = ~np.isnan(cc)
            if not ok.any(): continue
            out.append((r, s, g.o[r, seg][ok][0], np.nanmax(g.h[r, seg]), np.nanmin(g.l[r, seg]), cc[ok][-1]))
    return pd.DataFrame(out, columns=["row", "s", "o", "h", "l", "c"])


def run(g, B, apex, entry_window=None):
    # entry_window (2026-11-08, user, POST HOC from the entry-time split): (hhmm_from, hhmm_to) new entries only in that CT window
    o, h, l, c = (B[k].to_numpy() for k in "ohlc"); rows = B.row.to_numpy(); s = B.s.to_numpy(); n = len(B)
    hhmm = (s // 60) * 100 + s % 60
    dates = pd.DatetimeIndex(g.ts[rows]); early = np.array([is_early_close(d) for d in dates]) if apex else np.zeros(n, bool)
    cut = np.where(early, 1145, 1545)
    tr = np.r_[h[0] - l[0], np.maximum(h[1:], c[:-1]) - np.minimum(l[1:], c[:-1])]
    atr = np.full(n, np.nan); atr[79] = tr[:80].mean()
    for i in range(80, n): atr[i] = atr[i - 1] + (tr[i] - atr[i - 1]) / 80
    hi160 = pd.Series(h).rolling(160).max().shift(1).to_numpy(); lo60 = pd.Series(l).rolling(60).min().shift(1).to_numpy()
    trades = []; pos = False; e = st = 0.0; i0 = 0
    for i in range(162, n):
        blocked = apex and (hhmm[i] >= cut[i]) and hhmm[i] < 1700
        if pos:
            # stop at the open / inside bar i
            if o[i] <= st: trades.append((i0, i, e, o[i] - TICK, "stop")); pos = False
            elif l[i] <= st: trades.append((i0, i, e, st - TICK, "stop")); pos = False
        if pos:
            k = i - 1
            if apex and blocked: trades.append((i0, i, e, o[i] - TICK, "flat")); pos = False
            elif c[k] < lo60[k]: trades.append((i0, i, e, o[i] - TICK, "channel")); pos = False
            else:
                st = max(st, c[k] - 2 * atr[k])
                if o[i] <= st: trades.append((i0, i, e, o[i] - TICK, "stop")); pos = False   # (already handled above)
        if not pos and not blocked and (entry_window is None or entry_window[0] <= hhmm[i] < entry_window[1]):
            k = i - 1
            if np.isfinite(atr[k]) and np.isfinite(hi160[k]) and c[k] > hi160[k]:
                e = o[i] + TICK; st = e - 1.5 * atr[k]; i0 = i; pos = True
                if l[i] <= st: trades.append((i0, i, e, min(o[i], st) - TICK, "stop")); pos = False
    T = pd.DataFrame(trades, columns=["i0", "i1", "entry", "exit", "kind"])
    T["net"] = (T.exit - T.entry) * PV - COMM; T["date"] = pd.DatetimeIndex(g.ts[rows[T.i1]]); T["edate"] = pd.DatetimeIndex(g.ts[rows[T.i0]])
    T["bars"] = T.i1 - T.i0
    return T


def report(T, nm):
    T = T[T.edate >= "2018-01-01"]; tt = lambda x: x.mean() / x.std(ddof=1) * np.sqrt(len(x)) if len(x) > 2 else np.nan
    idx = pd.date_range("2018-01-01", T.date.max(), freq="B"); d = T.groupby("date").net.sum().reindex(idx, fill_value=0.0)
    a, b = T[T.edate < "2023"], T[T.edate >= "2023"]; da, db = d[d.index < "2023"], d[d.index >= "2023"]
    print(f"\n{nm}: {len(T)} trades, ${T.net.mean():.0f} a trade, PF {T.net[T.net > 0].sum() / -T.net[T.net < 0].sum():.2f}, win {np.mean(T.net > 0):.0%}, median hold {T.bars.median():.0f} bars, worst ${T.net.min():,.0f}")
    print(f"   2018-22 (design): n {len(a)} net ${a.net.sum():,.0f} (${a.net.mean():.0f} a trade), daily t {tt(da):.2f} -> {'PASS' if a.net.sum() > 0 and tt(da) >= 2 else 'FAIL'} gate")
    print(f"   by year $: {T.groupby(T.edate.dt.year).net.sum().round(0).astype(int).to_dict()}")
    print(f"   exits: {T.kind.value_counts().to_dict()}")
    return a.net.sum() > 0 and tt(da) >= 2, d, b, db


if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    g = pickle.load(open("scratch_data/g24.pkl", "rb")); B = bars15(g)
    print(f"   15-min bars: {len(B)} ({pd.Timestamp(g.ts[B.row.iloc[0]]).date()} .. {pd.Timestamp(g.ts[B.row.iloc[-1]]).date()})")
    for apex, nm in ((False, "SOURCE arm (holds across sessions)"), (True, "APEX arm (flat 15:45 / 11:45 early close)")):
        T = run(g, B, apex); ok, d, b, db = report(T, nm)
        if ok:
            tt = lambda x: x.mean() / x.std(ddof=1) * np.sqrt(len(x))
            print(f"   2023+ (seen-history replication, not a holdout): n {len(b)} net ${b.net.sum():,.0f} (${b.net.mean():.0f}), daily t {tt(db):.2f}")
            print(M.table({nm[:10] + " 2018+": (d, T[T.edate >= '2018'].set_index('date').net)}))
        else:
            print("   design gate failed: 2023+ not examined (Codex plan rule 6)")
    nt = len([1 for l_ in open("TIER_LIST.md") if l_.startswith("| ") and "---" not in l_]) + 2
    print(f"\n   t needed for promotion (N = {nt}): {M.t_threshold(nt):.2f}")
