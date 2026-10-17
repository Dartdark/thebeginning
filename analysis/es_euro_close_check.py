"""Antigravity's new idea 'ESEuroCloseTrend' (branch antigravity/jesse, tasks/out_new_es, 2026-10-17), rebuilt on our data.

Rule (its Jesse code): 15-minute ES. At the close of the 10:15-10:30 CT bar (European close), if close - 08:30 open
>= 0.25 x ATR15 (daily TR, weekdays) AND close > VWAP from midnight AND ADX(14, 15-min bars) >= 20 -> long at that close;
mirror for shorts. Stop 0.30 ATR, target 0.75 ATR (2.5R), out at the close of the 15:00 bar; one trade a day; no early
closes. Its report: 844 trades 2018-2026, $59 a trade net at its costs, design 2018-22 weak ($32/trade), DD $22k per ES.
Costs here: $5 per ES + 1 tick ($12.50) per market / stop fill (the target is a limit). Stops / targets on 1-minute bars,
stop first when both are hit in one minute.
Also: the same rule decided at other times (placebo: is 10:30 special?), and without the ADX / VWAP conditions.
  python3 analysis/es_euro_close_check.py [SCRATCH_DIR]
"""
import sys; sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
import metrics as M

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
PV, TICK, COM = 50.0, 0.25, 5.0


# CME early-close days, as analysis/jesse/mcbase.py
def early_close(d):
    m, dd, dow, y = d.month, d.day, d.isoweekday() % 7, d.year      # dow: 0 = Sunday .. 6 = Saturday (MultiCharts)
    wk = 1 <= dow <= 5
    return ((m == 1 and ((dd == 1 and wk) or (dd == 2 and dow == 1)))
            or (m == 1 and dow == 1 and 15 <= dd <= 21) or (m == 2 and dow == 1 and 15 <= dd <= 21)
            or (m == 5 and dow == 1 and dd >= 25)
            or (m == 6 and y >= 2022 and ((dd == 19 and wk) or (dd == 18 and dow == 5) or (dd == 20 and dow == 1)))
            or (m == 7 and (((dd == 3 or dd == 4) and wk) or (dd == 5 and dow == 1)))
            or (m == 9 and dow == 1 and dd <= 7)
            or (m == 11 and dow == 4 and 22 <= dd <= 28) or (m == 11 and dow == 5 and 23 <= dd <= 29)
            or (m == 12 and (((dd == 24 or dd == 25) and wk) or (dd == 26 and dow == 1))))


c = np.load(SP + "jesse_es.npy")
m = pd.DataFrame(c[:, 1:], columns=["o", "c", "h", "l", "v"], index=pd.to_datetime(c[:, 0], unit="ms"))
b = m.resample("15min", label="left", closed="left").agg(dict(o="first", h="max", l="min", c="last", v="sum")).dropna()
b["end"] = b.index + pd.Timedelta(minutes=15)
b["date"] = b["end"].dt.normalize()            # date of the bar's close (as the Jesse code)
b["hhmm"] = b["end"].dt.hour * 100 + b["end"].dt.minute

# daily TR on weekdays, ATR15 known before the day
d = b.groupby("date").agg(h=("h", "max"), l=("l", "min"), c=("c", "last"))
pc = d["c"].shift(1)
tr = pd.concat([d["h"], pc], axis=1).max(axis=1) - pd.concat([d["l"], pc], axis=1).min(axis=1)
tr = tr[d.index.dayofweek < 5].iloc[1:]
atr = tr.rolling(15).mean().shift(1).reindex(d.index).ffill()

# VWAP from midnight (typical price), ADX(14) Wilder on 15-min bars
tp = (b["h"] + b["l"] + b["c"]) / 3
b["vwap"] = (tp * b["v"]).groupby(b["date"]).cumsum() / b["v"].groupby(b["date"]).cumsum().replace(0, np.nan)
up, dn = b["h"].diff(), -b["l"].diff()
pdm = np.where((up > dn) & (up > 0), up, 0.0); ndm = np.where((dn > up) & (dn > 0), dn, 0.0)
trb = pd.concat([b["h"] - b["l"], (b["h"] - b["c"].shift()).abs(), (b["l"] - b["c"].shift()).abs()], axis=1).max(axis=1)
w = lambda x: pd.Series(x, index=b.index).ewm(alpha=1 / 14, adjust=False).mean()
atrb = w(trb); pdi = 100 * w(pdm) / atrb; ndi = 100 * w(ndm) / atrb
b["adx"] = w((100 * (pdi - ndi).abs() / (pdi + ndi)).fillna(0))
sopen = b[b["hhmm"] == 845].set_index("date")["o"]

mc = m["c"].to_numpy(); mh = m["h"].to_numpy(); ml = m["l"].to_numpy(); mt = m.index


def run(dec=1030, k=0.25, use_vwap=True, use_adx=True, stop=0.30, tgt=0.75, ex=1500):
    rows = []
    sig = b[(b["hhmm"] == dec)]
    for t, r in sig.iterrows():
        dt = r["date"]
        if dt < pd.Timestamp("2018-01-02") or dt.dayofweek >= 5 or early_close(dt.date()) or dt not in sopen.index:
            continue
        a = atr.get(dt, np.nan)
        if not a > 0: continue
        disp = r["c"] - sopen[dt]
        side = 0
        if disp >= k * a and (not use_vwap or r["c"] > r["vwap"]) and (not use_adx or r["adx"] >= 20): side = 1
        elif disp <= -k * a and (not use_vwap or r["c"] < r["vwap"]) and (not use_adx or r["adx"] >= 20): side = -1
        if not side: continue
        e = r["c"]; s_px = e - side * stop * a; t_px = e + side * tgt * a
        i0 = mt.searchsorted(r["end"]); i1 = mt.searchsorted(dt + pd.Timedelta(hours=ex // 100, minutes=ex % 100))
        x, how = mc[i1 - 1], "time"
        for i in range(i0, i1):
            if (side > 0 and ml[i] <= s_px) or (side < 0 and mh[i] >= s_px): x, how = s_px, "stop"; break
            if (side > 0 and mh[i] >= t_px) or (side < 0 and ml[i] <= t_px): x, how = t_px, "target"; break
        slip = TICK * (1 if how == "target" else 2)
        rows.append(dict(date=dt, side=side, pts=(x - e) * side, how=how,
                         net=((x - e) * side - slip) * PV - COM))
    return pd.DataFrame(rows)


def line(x, nm):
    n = x["net"]; yrs = n.groupby(x["date"].dt.year).sum()
    t = n.mean() / n.std() * np.sqrt(len(n)) if len(n) > 2 else np.nan
    gp, gl = n[n > 0].sum(), -n[n < 0].sum()
    a = n[x["date"] < "2023"]; h = n[x["date"] >= "2023"]
    print(f"{nm:<44} n={len(n):4d} ${n.mean():6.0f} PF {gp / gl if gl else np.inf:4.2f} t {t:4.1f} "
          f"yrs+ {(yrs > 0).sum()}/{len(yrs)} | 18-22 ${a.mean():5.0f} 23+ ${h.mean():5.0f}")


if __name__ == "__main__":
    base = run()
    line(base, "ESEuroCloseTrend as written (10:30)")
    print("   by year:", base.groupby(base["date"].dt.year)["net"].sum().round(0).to_dict())
    print("   exits:", base["how"].value_counts().to_dict())
    line(base[base.side > 0], "   longs"); line(base[base.side < 0], "   shorts")
    daily = base.groupby("date")["net"].sum()
    print("   metrics:", M.perf(daily, base["net"]) if hasattr(M, "perf") else "")
    print("\nWhat carries it:")
    line(run(use_adx=False), "no ADX filter")
    line(run(use_vwap=False), "no VWAP filter")
    line(run(use_adx=False, use_vwap=False), "displacement only")
    print("\nPlacebo: same rule decided at other times (exit 15:00):")
    for dec in (930, 1000, 1100, 1130, 1200, 1230, 1300):
        line(run(dec=dec), f"decide at {dec}")
