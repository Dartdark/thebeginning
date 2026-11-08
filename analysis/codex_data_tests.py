"""Three tests on Codex's 2026-11-08 data (user 2026-11-08: 'do it'). PRE-REGISTERED (header committed before the first run).
Data copied from codex/work (agents/codex/inputs/new_data_primary_local_20261108/normalized/) to data/codex_20261108/.
  T1 LETF-flow fade on CL and GC (2nd replication of WATCHLIST #31; frozen rule, only the clock moved to each market's settlement):
     UCO +2 / SCO -2 (crude) on CL, UGL +2 / GLL -2 (gold) on GC; exposure flow X_D = sum L x (AUM_D - AUM_{D-1} x NAV_D / NAV_{D-1});
     Z = X_{D-1} / past-60-day sd; |Z| >= 1 -> trade AGAINST sign(Z) over the last 30 minutes before settlement (CL 13:01 -> 13:30 CT,
     GC 12:01 -> 12:30 CT), stop 0.25 x ATR15; $5 + 1 tick per fill (CL $1,000 / pt, tick 0.01; GC $100 / pt, tick 0.10). 2 items.
     Success = t >= 2 in at least one market and the same sign in the other.
  T2 VIX9D / VIX inversion as a risk-off filter on the 150K plan (2 variants): yesterday's VIX9D close / VIX close >= 1.0 (near-term fear
     above 30-day) -> A skip the whole plan that day / B half size. Per-day split of the plan's P&L (inverted vs normal) first; then the
     150K evaluation (set + Twin 2 MNQ) and the funded 150K x 1.5 + Twin 2 with the multiplier on every piece.
  T3 Treasury buyback days on ZN (scheduled official buying): modern program operations from 2024-04 (operation 13:40 -> 14:00 ET =
     12:40 -> 13:00 CT; final announcement 11:00 ET same day), nominal-coupon operations whose maturity bucket covers 7-10 years;
     A long ZN 10:01 -> 13:00 CT (from the final announcement to the operation close); B long ZN 12:31 -> 13:00 CT. No stop; $5 + 1 tick
     per fill ($1,000 / pt, tick 1/64). Control: the same windows on all other 2024-26 days (random-day longs, same count, 500 runs).
     POWER WARNING: ~2.5 years of operations.
Checker on T1 (each market) and T3 A / B; placebo = random side (T1), random days (T3).
  tools/run_stamped.sh analysis/codex_data_tests.py > analysis/outputs/codex_data_tests_output.txt
"""
import sys, os, json, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import jof
from replica import is_early_close
import letf_flow_test as LF
import bench150 as BB

CD = "data/codex_20261108/"


def fund(f):
    d = pd.read_csv(CD + f"{f}.csv", parse_dates=["date"]).set_index("date").sort_index()
    return d.net_assets_usd.astype(float), d.nav_usd_source_basis.astype(float)


def flow(funds):
    out = {}
    for f, L in funds.items():
        aum, nav = fund(f); out[f] = L * (aum - aum.shift(1) * nav / nav.shift(1))
    return pd.DataFrame(out).dropna().sum(axis=1)


def signal(X, days):
    Zf = (X / X.rolling(60).std().shift(1)).dropna(); out = {}
    for d, z in Zf.items():
        later = days[days > d]
        if len(later) and abs(z) >= 1.0: out.setdefault(later[0], z)
    return pd.Series(out).sort_index()


def save(name, T, pl, variants, pre=True):
    cd = f"checks/candidates/{name}"; os.makedirs(cd, exist_ok=True)
    T.assign(date=pd.DatetimeIndex(T.date).strftime("%Y-%m-%d"))[["date", "side", "net"]].to_csv(f"{cd}/trades.csv", index=False)
    pd.DataFrame(pl, columns=["run", "net"]).to_csv(f"{cd}/placebo.csv", index=False)
    json.dump({"kind": "strategy", "pre_registered": pre, "variants": variants}, open(f"{cd}/meta.json", "w"))
    open(f"{cd}/spec.md", "w").write(f"# {name} (2026-11-08)\nSee analysis/codex_data_tests.py header.\n")


def window_trade(g, d, t0, t1, side=1):
    pos = pd.Series(np.arange(len(g.ts)), index=pd.DatetimeIndex(g.ts))
    if d not in pos.index: return None
    r = int(pos[d]); js, jx = jof(t0) + 1, jof(t1)
    if np.isnan(g.o[r, js]) or np.isnan(g.c[r, jx]): return None
    e = g.o[r, js] + side * LF.TICK; x = g.c[r, jx] - side * LF.TICK
    return (x - e) * side * LF.PV - LF.COMM


if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    # ---------------- T1
    print("\nT1 LETF-flow fade on CL / GC (frozen rule):")
    for mk, grid, funds, (t0, t1), cost in (("CL", "scratch_data/cl.pkl", {"UCO": 2, "SCO": -2}, (1300, 1330), (1000.0, 0.01, 5.0)),
                                            ("GC", "scratch_data/gc.pkl", {"UGL": 2, "GLL": -2}, (1200, 1230), (100.0, 0.10, 5.0))):
        LF.PV, LF.TICK, LF.COMM = cost; g = pickle.load(open(grid, "rb")); days = pd.DatetimeIndex(g.ts[g.trading])
        aum, _ = fund(list(funds)[0]); print(f"   {mk}: {list(funds)[0]} median assets $bn by year", {y: round(aum[aum.index.year == y].median() / 1e9, 2) for y in range(2018, 2027)})
        S = signal(flow(funds), days); kw = dict(t0=t0, t1=t1, stop=0.25)
        T = LF.trades(g, S, lambda d, z: -int(np.sign(z)), **kw); Tf = LF.trades(g, S, lambda d, z: int(np.sign(z)), **kw)
        print(LF.line(T.net, T.date, f"{mk} fade")); print(LF.line(Tf.net, Tf.date, f"{mk} follow"))
        print(f"      by year $: {T.groupby(T.date.dt.year).net.sum().round(0).astype(int).to_dict()}")
        rng = np.random.default_rng(37); pl = []
        for run in range(200):
            sides = {d: int(rng.choice([-1, 1])) for d in S.index}; Tp = LF.trades(g, S, lambda d, z: sides[d], **kw); pl += [(run, x) for x in Tp.net]
        pm = pd.DataFrame(pl, columns=["run", "net"]).groupby("run").net.mean()
        print(f"   random side ${pm.mean():.0f}, 95th ${np.percentile(pm, 95):.0f}; real ${T.net.mean():.0f}; p {np.mean(pm >= T.net.mean()):.3f}", flush=True)
        save(f"letf_fade_{mk.lower()}", T, pl, 1)
    # ---------------- T2
    print("\nT2 VIX9D / VIX inversion filter on the 150K plan:")
    v9 = pd.read_csv(CD + "VIX9D.csv", parse_dates=["date"]).set_index("date").close_index_points
    vx = pd.read_csv("data/VIX_daily.csv", parse_dates=["DATE"]).set_index("DATE").CLOSE
    ratio = (v9 / vx).dropna().sort_index()
    ctx = BB.setup(); dts = ctx["dts"]; yr = ctx["yr"]
    inv = np.array([bool((ratio[ratio.index < d] >= 1.0).iloc[-1]) if (ratio.index < d).any() else False for d in dts])
    print(f"   inverted days (2018+): {inv[yr >= 2018].mean():.0%} of trading days")
    lab = ctx["lab"]; base = BB.BASE_FUNDED
    pday = sum((v if not isinstance(v, tuple) else 1.0) * lab.C[k] for k, v in base.items() if not isinstance(v, tuple))
    for nm, m_ in (("inverted", inv), ("normal", ~inv)):
        x = pd.Series(pday[m_ & (yr >= 2018)]); print(f"   plan (fixed-size pieces) $ a day on {nm} days: ${x.mean():.0f} (n {len(x)}, t {x.mean() / x.std() * np.sqrt(len(x)):.2f}; worst ${x.min():,.0f})")
    for tag, mult in (("A skip", 0.0), ("B half", 0.5)):
        m = np.where(inv, mult, 1.0)
        print(); BB.eval_bench(ctx, {f"{tag} on inverted days": (ctx["Wb"] * (m - 1)[:, None], ctx["Rb"] * (m - 1)[:, None])})
    for tag, mult in (("A", 0.0), ("B", 0.5)):
        m = np.where(inv, mult, 1.0)
        for k in list(base):
            lab.W[k + tag] = lab.W[k] * m[:, None]; lab.C[k + tag] = lab.C[k] * m
            if k in lab.stop: lab.stop[k + tag] = lab.stop[k]
    print(); BB.funded_bench(ctx, {"A skip on inverted days": {k + "A": v for k, v in base.items()}, "B half on inverted days": {k + "B": v for k, v in base.items()}})
    # ---------------- T3
    print("\nT3 Treasury buyback days on ZN:")
    LF.PV, LF.TICK, LF.COMM = 1000.0, 1 / 64, 5.0; gz = pickle.load(open("scratch_data/zn.pkl", "rb"))
    b = pd.read_csv(CD + "buybacks_operations.csv", parse_dates=["operation_date"]); b = b[(b.operation_date >= "2024-04-01") & (b.security_type == "Nominal Coupons")]
    def covers(s):
        try:
            a, z = s.replace("Mo", "M").split(" to "); f = lambda t: float(t[:-1]) / (12 if t.endswith("M") else 1); return f(a) <= 10 and f(z) >= 7
        except Exception: return False
    b = b[b.maturity_bucket.map(covers) & (b.operation_start_time_est == "01:40 PM")]
    opd = sorted(set(b.operation_date)); print(f"   qualifying operations {len(b)} on {len(opd)} days ({opd[0].date()} -> {opd[-1].date()}); buckets {b.maturity_bucket.value_counts().to_dict()}")
    zd = pd.DatetimeIndex(gz.ts[gz.trading]); zd = zd[(zd >= "2024-04-01") & (zd <= pd.Timestamp(gz.ts[gz.trading][-1]))]
    for tag, (t0, t1) in (("A 10:01 -> 13:00", (1000, 1300)), ("B 12:31 -> 13:00", (1230, 1300))):
        real = [(d, window_trade(gz, d, t0, t1)) for d in opd]; real = [(d, x) for d, x in real if x is not None]
        others = [window_trade(gz, d, t0, t1) for d in zd if d not in set(opd) and not is_early_close(d)]; others = np.array([x for x in others if x is not None])
        xs = np.array([x for _, x in real]); tt = xs.mean() / xs.std(ddof=1) * np.sqrt(len(xs))
        rng = np.random.default_rng(41); pm = np.array([rng.choice(others, len(xs), replace=False).mean() for _ in range(500)])
        print(f"   {tag}: n {len(xs)} ${xs.mean():.0f} t {tt:.2f} | other days ${others.mean():.0f} | random days 95th ${np.percentile(pm, 95):.0f}; p {np.mean(pm >= xs.mean()):.3f}")
        T = pd.DataFrame({"date": [d for d, _ in real], "side": 1, "net": xs}); save(f"zn_buyback_{tag[0].lower()}", T, [(i, x) for i in range(50) for x in rng.choice(others, len(xs), replace=False)], 2)
