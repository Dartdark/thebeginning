"""BTC ADX ensemble, APEX-LEGAL INTRADAY version on MBT (user 2026-11-13: 'is there an intraday apex legal version? break it into
ingredients, data sweep, give me the best result'). Spot signals (Coinbase, 24/7 indicators as in analysis/btc_adx_ensemble_test.py),
every fill copied onto CME Micro Bitcoin (MBT) at the same 15m close; resting stop on MBT at the spot stop distance.
Apex rules applied: every book out at the 15:30-15:45 CT candle close (flat before 15:59 CT); no new entries from 14:45 CT to the
17:00 CT reopen or while CME is shut (Fri 15:45 -> Sun 17:00); books may open after 17:00 and hold to 15:45 next day (one Apex
trading day). Costs per MBT $2.50 round trip + 1 tick (5 points) a fill. Rolls removed by ratio.
Variants fixed before running (10; the pick rule is the highest DAILY t of V0-V8, then the data sweep on that one):
 V0 as coded (both sides, books ADX 40 / 50, all gates, resting stop) | V1 longs only | V2 no ADX gate | V3 no Bollinger width
 V4 no vol ratio | V5 no SuperTrend | V6 single book ADX>40 | V7 single book ADX>50 | V8 no resting stop | V9 = V0 shorts (slice)
Not modelled: CME holiday early closes (a book may be held through one), margin, Apex's own contract limits for MBT.
  tools/run_stamped.sh analysis/btc_adx_intraday_test.py > analysis/outputs/btc_adx_intraday_test_output.txt
"""
import sys, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
import btc_adx_ensemble_test as P
print(__doc__.split("\n")[0])
MULT, TICK, COMM = 0.1, 5.0, 2.5
src = open("analysis/btc_adx_futures_test.py", encoding="utf-8").read().split("\nm = load_fut()")[0].split("import btc_adx_ensemble_test as P")[1].split("\n", 2)[2]
ns = {"np": np, "pd": pd, "glob": __import__("glob")}; exec(src, ns)
f = ns["load_fut"](); f15 = P.rs(f, "15min"); fac = f.f.resample("15min", label="left", closed="left").last().reindex(f15.index).to_numpy()
FT = f15.index.to_numpy(); FO, FH, FL, FC = (f15[k].to_numpy() for k in ("open", "high", "low", "close"))
ctx = P.setup(); m15 = ctx[0]
ce = (m15.index + pd.Timedelta(minutes=15)).tz_localize("UTC").tz_convert("America/Chicago")      # candle CLOSE time, CT
hm = ce.hour * 100 + ce.minute; wd = ce.dayofweek
flat = np.asarray(hm == 1545)
shut = ((wd == 4) & (hm >= 1545)) | (wd == 5) | ((wd == 6) & (hm < 1700))
noent = np.asarray(shut | ((hm >= 1445) & (hm < 1700)))


def mirror(S, resting=True):
    rows = []
    for k in S.itertuples():
        ie = np.searchsorted(FT, np.datetime64(k.t)); ix = np.searchsorted(FT, np.datetime64(k.tx))
        if ix >= len(FT) or ie >= ix: continue
        s = k.side; pe = FC[ie] + s * TICK; real = pe / fac[ie]; stop = pe * (1 - s * k.R)
        ih = min(max(np.searchsorted(FT, np.datetime64(k.th)), ie), ix) if pd.notna(k.th) else None
        exit_px, why, half_px = FC[ix] - s * TICK, k.why, (FC[ih] if ih is not None else None)
        if resting:
            seg = np.flatnonzero((FL[ie + 1:ix + 1] <= stop) if s == 1 else (FH[ie + 1:ix + 1] >= stop))
            if len(seg):
                j = ie + 1 + seg[0]; px = (min(stop, FO[j]) if s == 1 else max(stop, FO[j])) - s * TICK
                if ih is None or j <= ih: half_px = None
                exit_px, why = px, "mbt stop"
        ret = s * ((exit_px - pe) / pe if half_px is None else 0.5 * (half_px - pe) / pe + 0.5 * (exit_px - pe) / pe)
        usd = ret * real * MULT - COMM - (COMM / 4 if half_px is not None else 0)
        rows.append((FT[ie], FT[ix], s, k.book, usd, k.R * real * MULT, why))
    d = pd.DataFrame(rows, columns=["t", "tx", "side", "book", "usd", "risk", "why"])
    d["r"] = d.usd / d.risk; d["yr"] = pd.DatetimeIndex(d.t).year
    d["day"] = (pd.DatetimeIndex(d.tx).tz_localize("UTC").tz_convert("America/Chicago") + pd.Timedelta(hours=7)).normalize().tz_localize(None)  # Apex day (17:00 CT start)
    return d


def stat(d):
    tt = lambda x: x.mean() / x.std(ddof=1) * np.sqrt(len(x)) if len(x) > 2 else np.nan
    x = d.usd; dd = d.groupby("day").usd.sum(); eq = dd.cumsum()
    a, z = d[d.yr <= 2022], d[d.yr >= 2023]
    return dict(n=len(d), win=np.mean(x > 0), usd=x.mean(), pf=x[x > 0].sum() / -x[x < 0].sum(), R=d.r.mean(), t=tt(d.r), td=tt(dd),
                t_a=tt(a.r), t_z=tt(z.r), yrs=int((d.groupby("yr").usd.sum() > 0).sum()), ny=d.yr.nunique(), per_yr=x.sum() / ((d.t.max() - d.t.min()).days / 365.25),
                mdd=(eq - eq.cummax()).min(), worst_day=dd.min(), L=d.r[d.side == 1].mean(), S=d.r[d.side == -1].mean(), tL=tt(d.r[d.side == 1]), tS=tt(d.r[d.side == -1]))


def line(nm, s):
    print(f"{nm:<30} n {s['n']:4d} win {s['win']:.0%} ${s['usd']:6.1f}/MBT PF {s['pf']:4.2f} R {s['R']:+.3f} t {s['t']:5.2f} daily t {s['td']:5.2f} | 2019-22 t {s['t_a']:5.2f} 2023+ t {s['t_z']:5.2f} "
          f"| {s['yrs']}/{s['ny']} yrs | ${s['per_yr']:,.0f}/yr per MBT, DD ${s['mdd']:,.0f} | longs {s['L']:+.3f}R (t {s['tL']:.2f}) shorts {s['S']:+.3f}R (t {s['tS']:.2f})")


G = ("adx", "bbw", "vol", "st")
V = {"V0 as coded": dict(), "V1 longs only": dict(longs_only=True), "V2 no ADX gate": dict(gates=("bbw", "vol", "st")),
     "V3 no Bollinger width": dict(gates=("adx", "vol", "st")), "V4 no vol ratio": dict(gates=("adx", "bbw", "st")),
     "V5 no SuperTrend": dict(gates=("adx", "bbw", "vol")), "V6 single book ADX>40": dict(books=(40,)), "V7 single book ADX>50": dict(books=(50,))}
res = {}; trades = {}
print("\nAPEX-LEGAL INTRADAY (flat 15:45 CT), spot signals -> MBT, per MBT per book:")
for nm, kw in V.items():
    S = P.run(ctx, flat=flat, noent=noent, **kw); S = S[(S.t >= FT[0]) & (S.tx <= FT[-1])]
    d = mirror(S); res[nm] = stat(d); trades[nm] = d; line(nm, res[nm])
    if nm == "V0 as coded":
        d8 = mirror(S, resting=False); res["V8 no resting stop"] = stat(d8); trades["V8 no resting stop"] = d8
        print(f"  (V0 exits: {d.why.value_counts().to_dict()}; spot book trades {len(S)}, mirrored {len(d)}; hold hours median {((d.tx - d.t) / np.timedelta64(1, 'h')).median():.1f})")
line("V8 no resting stop", res["V8 no resting stop"])
d9 = trades["V0 as coded"]; d9 = d9[d9.side == -1]; line("V9 V0 shorts (slice)", stat(d9))
best = max([k for k in res if not k.startswith("V9")], key=lambda k: res[k]["td"])
print(f"\nBEST by the fixed rule (highest daily t of V0-V8): {best}")
B = trades[best]
print("  by year $ per MBT: " + "  ".join(f"{y} {g.usd.sum():+,.0f} ({len(g)})" for y, g in B.groupby("yr")))
print(f"  worst trade {B.r.min():.2f}R (${B.usd.min():,.0f}), worst Apex day ${B.groupby('day').usd.sum().min():,.0f}; stop $ per MBT median {B.risk.median():.0f} (2025+ {B.risk[B.yr >= 2025].median():.0f})")
for acct_trail, size in ((4000, None),):
    pass
B.assign(date=B.day.dt.date, net=B.usd).to_csv("scratch_data/btc_adx_intraday_best_trades.csv", index=False)
open("scratch_data/btc_adx_intraday_best.txt", "w").write(best)
