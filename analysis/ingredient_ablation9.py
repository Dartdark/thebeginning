"""Ingredient ablation, round 9 (user 2026-11-09: 'do the first batch'): Bridge Monday Long, ES MOC Follow, T one-side fade, the
three funded-plan pieces not yet taken apart. PRE-REGISTERED (header committed before the first run). Information only; ONE part
changed at a time; per contract after $7.25 (NQ) / $5 (ES) + 1 tick per market / stop fill (targets = limits, no slip); 2018-26,
both periods, total $ and max DD (ingredient_ablation3.line). A variant that beats its current version on t and in both periods
gets the two-bar check (its book bench) in a follow-up, not here.
  1. Bridge Monday Long (The Bridge's L644NQ; rebuild analysis/bridge_monday_long_test.py, MultiCharts 217/217): Sunday 19:00 CT
     close buy when the last regular session's ADX(7) is 10-50 and DI+ > DI-, target 100 points, no stop, out Monday 15:55.
     Variants: no ADX / DI filter / ADX range only / DI+ > DI- only / ADX(14) / no target / target 50 / target 150 / enter Monday
     08:30 instead / out Monday 12:00 / the same trade on Tuesday / Wednesday / Thursday / Friday (entry the evening before).
  2. ES MOC Follow (funded, MES; MultiCharts 199/199): full sessions, not early close; move = 14:50 close - 14:00 close; |move| >=
     0.30 x daily ATR15 -> follow at the 14:51 open, stop 0.25 ATR, out at the 15:00 close.
     Variants: threshold 0 (every day) / 0.2 / 0.5 / fade instead / no stop / stop 0.5 / move from 13:30 / move from 14:30 /
     out 14:55 / out 15:15 / longs only / shorts only / the same rule on NQ.
  3. T one-side fade (funded 50K; analysis/t_oneside_test.py, MultiCharts 348/358): heavy night (night volume > 1.4 x the median of
     the prior 20 valid nights) -> fade the night's move at 08:29:00 CT, out at 08:44:00, stop 0.40 x ATRd.
     Variants: every valid night (no volume filter) / quiet nights only / heavier nights (1.8) / lighter (1.2) / follow instead of
     fade / no stop / stop 0.8 / out 08:40 / out 09:00 / out 09:30 / enter at the bell (08:30:00) / longs only / shorts only.
  tools/run_stamped.sh analysis/ingredient_ablation9.py > analysis/outputs/ingredient_ablation9_output.txt
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import jof
from replica import is_early_close
from ingredient_ablation3 import line
import ingredient_ablation4 as IA4
import bridge_monday_long_test as BM
import t_oneside_test as TO


def moc(g, pv, tick, comm, k=0.30, fade=False, stop=0.25, ref=1400, dec=1450, out=1500, side_only=0):
    IA4.COMM = comm; atr = g.daily_atr(15); ts = pd.DatetimeIndex(g.ts); cf = pd.Series(g.c.ravel()).ffill().to_numpy(); rows = []
    for r in g.trading:
        d = ts[r]
        if d < pd.Timestamp("2018-01-01") or is_early_close(d) or np.isnan(atr[r]) or np.isnan(g.c[r, jof(1455):jof(1500) + 1]).all(): continue
        mv = cf[r * 1440 + jof(dec)] - cf[r * 1440 + jof(ref)]
        if mv == 0 or abs(mv) < k * atr[r]: continue
        s = int(np.sign(mv)) * (-1 if fade else 1)
        if side_only and s != side_only: continue
        x = IA4.walk(g, r * 1440 + jof(dec) + 1, r * 1440 + jof(out), s, None if stop is None else stop * atr[r], pv, tick)
        if x is not None: rows.append((d, s, x))
    return pd.DataFrame(rows, columns=["date", "side", "net"])


def tfade(g, D, fat=1.4, stop=0.40, j_in=830, j_out=845, follow=False, side_only=0, quiet=False, every=False):
    rows = []
    for x in D[D.valid & (D.med > 0) & D.atr.notna()].itertuples():
        heavy = x.vol > fat * x.med
        if every: pass
        elif quiet and heavy: continue
        elif not quiet and not heavy: continue
        s = -np.sign(x.ret) * (-1 if follow else 1)
        if s == 0 or (side_only and s != side_only) or pd.Timestamp(x.date) < pd.Timestamp("2018-01-01"): continue
        h = TO.hold(g, x.r, int(s), jof(j_in), jof(j_out), stop=stop * x.atr if stop else np.nan)
        if h: e, xp, j1, kind = h; rows.append((x.date, int(s), (xp - e) * s * 20.0 - 2 * 0.25 * 20.0 - 7.25))
    return pd.DataFrame(rows, columns=["date", "side", "net"])


if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    g = pickle.load(open("scratch_data/g24.pkl", "rb"))
    sh = lambda nm, T: print(line(T.net, T.date, nm), flush=True)
    # ---------------- 1. Bridge Monday
    print("\n1. Bridge Monday Long (check: MultiCharts 217 trades):")
    A7 = BM.bridge_adx(g, 7); A14 = BM.bridge_adx(g, 14)
    base = BM.bridge(g, A7); sh("as is", base)
    allm = BM.bridge(g, A7, filt=False); sh("no ADX / DI filter", allm)
    sig = {d: a for d, a in A7.items()}
    def sub(T, cond): return T[[cond(*sig[int(d) - 1]) for d in T.day]] if len(T) else T
    sh("ADX 10-50 only (any DI)", sub(allm, lambda a, di: 10 <= a < 50)); sh("DI+ > DI- only (any ADX)", sub(allm, lambda a, di: a >= 0 and di > 0))
    sh("ADX(14)", BM.bridge(g, A14)); sh("no target", BM.bridge(g, A7, target=0)); sh("target 50", BM.bridge(g, A7, target=50.0)); sh("target 150", BM.bridge(g, A7, target=150.0))
    sh("enter Monday 08:30 instead", BM.bridge(g, A7, rth_only=True)); sh("out Monday 12:00", BM.bridge(g, A7, exit_t=1200))
    for wd, nm in ((1, "Tuesday"), (2, "Wednesday"), (3, "Thursday"), (4, "Friday")): sh(f"same trade on {nm}", BM.bridge(g, A7, weekday=wd))
    # ---------------- 2. ES MOC
    print("\n2. ES MOC Follow (check: MultiCharts 199 trades; per ES):")
    ge = pickle.load(open("scratch_data/ge.pkl", "rb")); es = dict(pv=50.0, tick=0.25, comm=5.0)
    sh("as is", moc(ge, **es))
    for nm, kw in (("threshold 0 (every day)", dict(k=0.0)), ("threshold 0.2", dict(k=0.2)), ("threshold 0.5", dict(k=0.5)), ("fade instead", dict(fade=True)),
                   ("no stop", dict(stop=None)), ("stop 0.5", dict(stop=0.5)), ("move from 13:30", dict(ref=1330)), ("move from 14:30", dict(ref=1430)),
                   ("out 14:55", dict(out=1455)), ("out 15:15", dict(out=1515)), ("longs only", dict(side_only=1)), ("shorts only", dict(side_only=-1))):
        sh(nm, moc(ge, **es, **kw))
    sh("the same rule on NQ (per NQ)", moc(g, 20.0, 0.25, 7.25))
    # ---------------- 3. T fade
    print("\n3. T one-side fade (check: MultiCharts 348 fades from 2018):")
    D = TO.days(g)
    sh("as is", tfade(g, D))
    for nm, kw in (("every valid night (no volume filter)", dict(every=True)), ("quiet nights only", dict(quiet=True)), ("heavier nights (1.8)", dict(fat=1.8)),
                   ("lighter (1.2)", dict(fat=1.2)), ("follow instead of fade", dict(follow=True)), ("no stop", dict(stop=0)), ("stop 0.8", dict(stop=0.8)),
                   ("out 08:40", dict(j_out=840)), ("out 09:00", dict(j_out=900)), ("out 09:30", dict(j_out=930)), ("enter at the bell (08:30:00)", dict(j_in=831)),
                   ("longs only", dict(side_only=1)), ("shorts only", dict(side_only=-1))):
        sh(nm, tfade(g, D, **kw))
