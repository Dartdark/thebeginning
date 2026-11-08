"""Noise band (the Bridge noise-area rules, Zarattini / Aziz / Barbon) on CL and GC (user 2026-11-08, batch of 5, test 2).
PRE-REGISTERED (header committed before the first run; one variant per market, 2 ranked items). The Bridge's NQ RTH code, with its
clock moved to each market's regular hours and its point exits turned into % of price (NQ 50 / 25 pts ~ 0.35% / 0.175% at 2018-26 prices):
  15-min bars anchored to the open (CL 08:00-13:30 CT, GC 07:20-12:30 CT); TodayOpen = first RTH open, PrevClose = last RTH close of the
  previous trading day; slot = bar closing open + 30 .. close - 45; move = |close / TodayOpen - 1|; band = mean of that slot's previous
  20 moves; UB = max(open, prev close) x (1 + band), LB = min(...) x (1 - band); EMA20 of the RTH 15-min closes (continuous).
  On a slot bar, flat and bar close <= close - 60: close > UB and close > bar open -> buy next bar open; close < LB and < bar open -> short.
  Long: short signal (<= close - 60) -> reverse (if the day caps allow, else exit); else close < max(UB, EMA) -> exit next open. Mirror.
  Stop 0.35% / target 0.175% of the entry price (1-minute path, stop first), max 10 entries and 3 stops a day; flat at the open of the
  bar after close - 30 (CL 13:00 -> out 13:00, GC 12:00 -> out 12:00); CME early-close days skipped. Both sides (longs / shorts reported).
  CL $1,000 a point, tick 0.01; GC $100 a point, tick 0.10; $5 + 1 tick per market / stop fill (target = limit, no slip). Micros = 1/10.
Checks: per trade by period, by year, longs / shorts; placebo (same trades a day, random side and entry time, same bracket, 100 runs);
checker folder checks/candidates/noise_<mkt>/; daily corr with the plan; 150K evaluation (set + Twin 2 MNQ) + the market at Twin's
risk ($300 per stop) and half; funded 150K x 1.5 + Twin 2 + those sizes; personal book + the half size.
  tools/run_stamped.sh analysis/noise_markets_test.py CL > analysis/outputs/noise_markets_test_CL_output.txt   (GC alike)
"""
import sys, os, json, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from replica import is_early_close
import bench150 as BB

SPEC = {"CL": dict(op=480, cl=810, pv=1000.0, tick=0.01), "GC": dict(op=440, cl=750, pv=100.0, tick=0.10)}   # minutes after midnight CT
COMM, SL, TP, LOOK = 5.0, 0.0035, 0.00175, 20


def bars(g, op, cl):
    """RTH 15-min bars anchored to op: list per trading row of arrays (t_close, o, h, l, c)."""
    out = {}
    for r in g.trading:
        if is_early_close(pd.Timestamp(g.ts[r])): continue
        rows = []
        for t in range(op + 15, cl + 1, 15):
            js = np.arange(t - 14, t + 1); c = g.c[r, js]; ok = np.isfinite(c)
            if not ok.any(): continue
            rows.append((t, g.o[r, js][ok][0], np.nanmax(g.h[r, js]), np.nanmin(g.l[r, js]), c[ok][-1]))
        if len(rows) >= (cl - op) // 15 - 2: out[r] = np.array(rows)
    return out


def run(g, S, placebo_rng=None, plan=None):
    op, cl, pv, tick = S["op"], S["cl"], S["pv"], S["tick"]; Bd = bars(g, op, cl)
    hist = {}; ema = None; a = 2 / 21; prev_close = None; trades = []
    for r in sorted(Bd):
        X = Bd[r]; topen = X[0, 1]; pos = 0; e = 0.0; j_in = 0; pend = None; ntr = nst = 0
        def close(px, j, kind):
            nonlocal pos, nst
            if (px - e) * pos <= -SL * e + 1e-12: nst += 1
            slips = 0 if kind == "target" else 2
            trades.append(dict(row=r, date=pd.Timestamp(g.ts[r]), side=pos, entry=e, exit=px, j0=j_in, j1=j, kind=kind,
                               net=(px - e) * pos * pv - COMM - slips * tick * pv, risk=SL * e * pv)); pos = 0
        for k in range(len(X)):
            t, o, h, l, c = X[k]; t = int(t)
            if pend is not None:                                    # market order at this bar's open (minute t - 14)
                if pend[0] in ("out", "rev") and pos != 0: close(o - pos * tick, t - 14, pend[2])
                if pend[0] in ("in", "rev"): pos = pend[1]; e = o + pos * tick; j_in = t - 14
                pend = None
            if pos != 0:
                for m in range(max(t - 14, j_in), t + 1):
                    if not np.isfinite(g.c[r, m]): continue
                    stp, tgt = e - pos * SL * e, e + pos * TP * e
                    if (g.l[r, m] <= stp) if pos > 0 else (g.h[r, m] >= stp):
                        close((min(g.o[r, m], stp) if pos > 0 else max(g.o[r, m], stp)) - pos * tick, m, "stop"); break
                    if (g.h[r, m] >= tgt) if pos > 0 else (g.l[r, m] <= tgt):
                        close(tgt, m, "target"); break
            ema = c if ema is None else ema + a * (c - ema)
            slot = (t - op) // 15 - 1                               # 1 = bar closing open + 30
            if 1 <= slot and t <= cl - 45 and prev_close is not None:
                mv = abs(c / topen - 1); hs = hist.setdefault(slot, [])
                if len(hs) >= LOOK:
                    avg = np.mean(hs[-LOOK:]); ub = max(topen, prev_close) * (1 + avg); lb = min(topen, prev_close) * (1 - avg)
                    can = ntr < 10 and nst < 3; ls = c > ub and c > o; ss = c < lb and c < o
                    if placebo_rng is not None and (ls or ss) and pos == 0:
                        if placebo_rng.random() < 0.5: ls, ss = ss, ls
                    if pos == 0 and can and t <= cl - 60:
                        if ls: pend = ("in", 1); ntr += 1
                        elif ss: pend = ("in", -1); ntr += 1
                    elif pos == 1:
                        if t <= cl - 60 and ss: pend = ("rev", -1, "reverse") if can else ("out", 0, "reverse exit"); ntr += can
                        elif c < max(ub, ema): pend = ("out", 0, "band/EMA exit")
                    elif pos == -1:
                        if t <= cl - 60 and ls: pend = ("rev", 1, "reverse") if can else ("out", 0, "reverse exit"); ntr += can
                        elif c > min(lb, ema): pend = ("out", 0, "band/EMA exit")
                hs.append(mv)
            if t == cl - 30 and pos != 0: pend = ("out", 0, "flat")
        if pos != 0: close(X[-1][4] - pos * tick, int(X[-1][0]), "last bar")
        prev_close = X[-1][4]
    return pd.DataFrame(trades)


def placebo(g, S, T, n, seed=7):
    """Same number of trades a day, random side, entry at a random 15-min open (open + 30 .. close - 60), same bracket, out at the flat time."""
    rng = np.random.default_rng(seed); op, cl, pv, tick = S["op"], S["cl"], S["pv"], S["tick"]; res = []
    by = T.groupby("row").size()
    for run_ in range(n):
        for r, cnt in by.items():
            for _ in range(cnt):
                j0 = op + 30 + 15 * int(rng.integers(0, (cl - 60 - op - 30) // 15 + 1)); side = rng.choice([-1, 1])
                if not np.isfinite(g.o[r, j0 + 1]): continue
                e = g.o[r, j0 + 1] + side * tick; x = None; sl = 2
                for m in range(j0 + 1, cl - 29):
                    if not np.isfinite(g.c[r, m]): continue
                    if (g.l[r, m] <= e - SL * e) if side > 0 else (g.h[r, m] >= e + SL * e): x = e - side * SL * e - side * tick; break
                    if (g.h[r, m] >= e + TP * e) if side > 0 else (g.l[r, m] <= e - TP * e): x = e + side * TP * e; sl = 0; break
                if x is None:
                    cc = g.c[r, op:cl - 29]; x = cc[np.isfinite(cc)][-1] - side * tick
                res.append((run_, (x - e) * side * pv - COMM - sl * tick * pv))
    return pd.DataFrame(res, columns=["run", "net"])


def day_paths(g, T, pv):
    W = np.zeros(g.o.shape); R = np.zeros(g.o.shape); acc = {}
    for t in T.itertuples():
        cost = (t.exit - t.entry) * t.side * pv - t.net; js = np.arange(t.j0, t.j1 + 1)
        adv = ((g.l[t.row, js] if t.side > 0 else g.h[t.row, js]) - t.entry) * t.side * pv - cost; adv = np.nan_to_num(adv, nan=0.0)
        mark = np.nan_to_num((g.c[t.row, js] - t.entry) * t.side * pv - cost, nan=0.0)
        adv[-1] = min(adv[-1], t.net); mark[-1] = t.net
        base_r = acc.get(t.row, 0.0); acc[t.row] = base_r + t.net
        W[t.row, js] = base_r + np.minimum(adv, mark); R[t.row, js] = base_r + mark
        W[t.row, t.j1 + 1:] = base_r + t.net; R[t.row, t.j1 + 1:] = base_r + t.net
    return W, R


if __name__ == "__main__":
    mk = sys.argv[1]; S = SPEC[mk]; print(__doc__.split("\n")[0]); print(f"   market {mk}")
    gx = pickle.load(open(f"scratch_data/{mk.lower()}.pkl", "rb"))
    T = run(gx, S); T = T[T.date >= "2018-01-01"].reset_index(drop=True)
    tt = lambda x: x.mean() / x.std(ddof=1) * np.sqrt(len(x)) if len(x) > 2 else np.nan; a, b = T[T.date < "2023"].net, T[T.date >= "2023"].net
    print(f"   noise band on {mk}: n {len(T)} ${T.net.mean():.0f} t {tt(T.net):.2f} PF {T.net[T.net > 0].sum() / -T.net[T.net < 0].sum():.2f} | 2018-22 ${a.mean():.0f} (t {tt(a):.1f}) 2023+ ${b.mean():.0f} (t {tt(b):.1f}) | longs ${T[T.side > 0].net.mean():.0f} (t {tt(T[T.side > 0].net):.1f}, n {int((T.side > 0).sum())}) shorts ${T[T.side < 0].net.mean():.0f} (t {tt(T[T.side < 0].net):.1f}) | worst ${T.net.min():,.0f}")
    print(f"      by year $: {T.groupby(T.date.dt.year).net.sum().round(0).astype(int).to_dict()}")
    print(f"      exits: {T.kind.value_counts().to_dict()} | trade days {T.date.nunique()}")
    Pl = placebo(gx, S, T, 100); pm = Pl.groupby("run").net.mean()
    print(f"   placebo (random side and time, same bracket) ${pm.mean():.0f}, 95th ${np.percentile(pm, 95):.0f}; p {np.mean(pm >= T.net.mean()):.2f}", flush=True)
    cd = f"checks/candidates/noise_{mk.lower()}"; os.makedirs(cd, exist_ok=True)
    T.assign(date=T.date.dt.strftime("%Y-%m-%d"))[["date", "side", "net", "risk"]].to_csv(f"{cd}/trades.csv", index=False)
    Pl.to_csv(f"{cd}/placebo.csv", index=False)
    json.dump({"kind": "strategy", "pre_registered": True, "variants": 1}, open(f"{cd}/meta.json", "w"))
    open(f"{cd}/spec.md", "w").write(f"# Noise band on {mk} (Bridge noise-area rules on {mk}'s regular hours, 2026-11-08)\n" + __doc__.split("PRE-REGISTERED")[1].split("Checks:")[0] + "\n")
    ctx = BB.setup(); We, Re = day_paths(gx, T, S["pv"]); W1, R1 = BB.to_nq_days(ctx, gx, We / 10, Re / 10); dts, yr = ctx["dts"], ctx["yr"]
    lab = ctx["lab"]; dd = pd.Series(R1[:, -1], index=dts)
    C = pd.DataFrame({k: lab.C[k] for k in ("VB", "ONB_ML2_MC", "MON_MC", "EOS", "LDF_MC", "CLS", "TWIN")}, index=dts)
    print("   daily corr:", C[yr >= 2018].corrwith(dd[yr >= 2018]).round(2).to_dict())
    m23 = np.median(T.risk[T.date >= "2023"]) / 10; q = max(1, int(round(300 / m23))); sizes = sorted({q, max(1, q // 2)})
    print(f"   risk-matched size: {q} M{mk} (${q * m23:,.0f} per stop vs Twin 2 MNQ $300); sizes tested {sizes}\n")
    BB.eval_bench(ctx, {f"+ {mk} noise band {n} M{mk}": (n * W1, n * R1) for n in sizes})
    print()
    BB.funded_bench(ctx, {f"+ {mk} noise band {n} M{mk}": {**BB.BASE_FUNDED, "NBX": n} for n in sizes}, extra={"NBX": (W1, R1[:, -1])})
    print(f"\n   Personal book 1-year MC return / DD p95 (+ {sizes[0]} M{mk}):")
    BB.personal({f"+ {sizes[0]} M{mk}": pd.Series(sizes[0] * R1[:, -1], index=dts)})
