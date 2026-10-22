"""London FX fixing reversal: two preregistered 6E rules, plan aed463d.

python -u -B analysis/codex_fx_fix_reversal.py scratch_data
Uses repository execution, metrics, resampling, Monte Carlo and funded-account tools.
All rule/slot selection uses 2018-22; only the selected rule is opened on 2023+.
"""
from __future__ import annotations

import json
import pickle
import sys
import warnings
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pandas as pd
from numba import njit

sys.path.insert(0, "analysis")
import codex_overlap_risk_cap as O
import codex_marginal_contribution as CM
import funded_sim as F
import grid
import metrics as M
import montecarlo as MC
import resampling as R
from grid24 import Grid24
from portfolio import paths

warnings.filterwarnings("ignore", category=RuntimeWarning)
SP = Path(sys.argv[1] if len(sys.argv) > 1 else "scratch_data")
OUT = Path("analysis/outputs/codex_fx_fix_reversal")
SPLIT = pd.Timestamp("2023-01-01")
PV, TICK, COMM = 125000.0, 0.00005, 7.25
N_PLACEBO, N_ACCOUNT = 1000, 2000
HOLDS = (30, 60)
SEEDS = {"side": 4101, "time": 4102, "design_account": 4201, "holdout_account": 4202}


def save_json(name, obj):
    (OUT / name).write_text(json.dumps(obj, indent=2, default=str, allow_nan=True) + "\n")


def load_fx():
    p = SP / "6e.pkl"
    if p.exists():
        return pickle.load(p.open("rb"))
    g = Grid24("data/6E_1min_20*.csv", night_pattern="")
    with p.open("wb") as f:
        pickle.dump(g, f, protocol=4)
    return g


def clock_minutes(dates, hour=16, minute=3):
    local = (pd.DatetimeIndex(dates).normalize() + pd.Timedelta(hours=hour, minutes=minute))
    ct = local.tz_localize("Europe/London").tz_convert("America/Chicago")
    return np.asarray(ct.hour * 60 + ct.minute, dtype=int)


def make_signals(g, dates, hold, design, wrong_clock=False):
    pos = pd.Series(np.arange(g.D), index=pd.DatetimeIndex(g.ts))
    use = dates[dates < SPLIT] if design else dates[dates >= SPLIT]
    djs = np.full(len(use), 603, dtype=int) if wrong_clock else clock_minutes(use)
    atr = g.daily_atr(15)
    sig, audit = [], []
    for date, dj in zip(use, djs):
        if date not in pos.index:
            audit.append({"date": date, "status": "missing_date"})
            continue
        d = int(pos.loc[date]); start = int(dj - 33)
        a, b = g.c[d, start], g.c[d, dj]
        if not np.isfinite(a + b + atr[d]) or atr[d] <= 0:
            audit.append({"date": date, "status": "missing_signal_or_atr"})
            continue
        side = -int(np.sign(b - a))
        if side == 0:
            audit.append({"date": date, "status": "unchanged"})
            continue
        stop = np.ceil(0.25 * atr[d] / TICK - 1e-9) * TICK
        sig.append(dict(day=d, dj=int(dj), side=side, stop=stop,
                        target=np.inf, exit_j=int(dj + hold)))
        audit.append({"date": date, "status": "signal", "dj": int(dj), "side": side,
                      "stop": stop, "missing_entry": not np.isfinite(g.o[d, dj + 1]),
                      "missing_exit": not np.isfinite(g.c[d, dj + hold]),
                      "truncated": bool(g.last_j[d] < dj + hold)})
    return pd.DataFrame(sig), pd.DataFrame(audit)


def execute_fx(g, sig):
    t = grid.execute(g, sig, max_trades=1, name="FX fix reversal")
    # grid.execute's path walker is instrument-independent; its hard-coded NQ dollar columns are replaced.
    t["gross"] = (t.exit - t.entry) * t.side * PV
    t["commission"] = COMM
    t["slippage"] = 2 * TICK * PV
    t["net"] = t.gross - COMM - 2 * TICK * PV
    t["stop_pts"] = t.day.map(sig.set_index("day").stop)
    t["dj"] = t.j0 - 1
    assert (t.j0 == t.dj + 1).all()
    assert (t.j1 < 15 * 60 + 59).all()
    assert (t.j1 >= t.j0).all()
    return t


def daily(t, dates, side=0):
    sub = t if not side else t[t.side == side]
    return sub.groupby("date").net.sum().reindex(dates, fill_value=0.0)


def metric_rows(t, dates, label):
    rows = []
    masks = {"design": dates < SPLIT, "holdout": dates >= SPLIT, "full": np.ones(len(dates), bool)}
    for period, mask in masks.items():
        ds = dates[mask]
        if not len(ds):
            continue
        tt = t[t.date.isin(ds)]
        for side_name, side in (("whole", 0), ("long", 1), ("short", -1)):
            sub = tt if not side else tt[tt.side == side]
            x = daily(sub, ds)
            rows.append({"rule": label, "period": period, "side": side_name,
                         "total": sub.net.sum(), "gross": sub.gross.sum(),
                         "commissions": sub.commission.sum(), "slippage": sub.slippage.sum(),
                         "t": O.tstat(sub.net), **M.perf(x, sub.net)})
    return rows


@njit
def control_tables(o, h, l, c, day_ix, stops, real_dj, hold):
    """Replay both sides with repository _walk, then randomize; never flip realized stop exits."""
    n = len(day_ix)
    actual_sides = np.full((n, 2), np.nan)
    time_net = np.full((n, 301), np.nan)
    for i in range(n):
        d, sp, dj = day_ix[i], stops[i], real_dj[i]
        for si in range(2):
            side = 1 if si == 0 else -1
            entry = o[d, dj + 1]
            target = np.inf if side > 0 else -np.inf
            j1, px, kind, worst = grid._walk(o[d], h[d], l[d], c[d], dj + 1, dj + hold,
                                          side, entry - side * sp, target, 1.0)
            actual_sides[i, si] = (px - entry) * side * PV - COMM - 2 * TICK * PV
        for z in range(301):
            q = 480 + z
            if abs(q - dj) <= 90:
                continue
            a, b, entry = c[d, q - 33], c[d, q], o[d, q + 1]
            if not (np.isfinite(a) and np.isfinite(b) and np.isfinite(entry) and
                    np.isfinite(c[d, q + hold])) or b == a:
                continue
            side = -1 if b > a else 1
            target = np.inf if side > 0 else -np.inf
            j1, px, kind, worst = grid._walk(o[d], h[d], l[d], c[d], q + 1, q + hold,
                                          side, entry - side * sp, target, 1.0)
            time_net[i, z] = (px - entry) * side * PV - COMM - 2 * TICK * PV
    return actual_sides, time_net


def placebos(g, t, hold, label):
    side_values, time_values = control_tables(
        g.o, g.h, g.l, g.c, t.day.to_numpy(int), t.stop_pts.to_numpy(float), t.dj.to_numpy(int), hold
    )
    real_col = np.where(t.side.to_numpy() > 0, 0, 1)
    np.testing.assert_allclose(side_values[np.arange(len(t)), real_col], t.net, atol=1e-8)
    rng_side = np.random.default_rng(SEEDS["side"])
    rng_time = np.random.default_rng(SEEDS["time"])
    random_side = side_values[np.arange(len(t))[None, :], rng_side.integers(0, 2, (N_PLACEBO, len(t)))]
    random_time = np.empty_like(random_side)
    for i in range(len(t)):
        values = time_values[i, np.isfinite(time_values[i])]
        if not len(values):
            raise ValueError(f"No valid placebo times on {t.date.iloc[i]}")
        random_time[:, i] = rng_time.choice(values, N_PLACEBO)
    summary, samples = [], []
    for kind, z in (("side", random_side), ("time", random_time)):
        sums = z.sum(axis=1)
        actual = float(t.net.sum())
        summary.append({"rule": label, "kind": kind, "actual_total": actual,
                        "random_p5": np.percentile(sums, 5), "random_p50": np.median(sums),
                        "random_p95": np.percentile(sums, 95),
                        "p_ge_actual": (1 + np.sum(sums >= actual)) / (N_PLACEBO + 1)})
        samples.extend({"rule": label, "kind": kind, "run": i, "total": float(s)} for i, s in enumerate(sums))
    return summary, samples


def candidate_component(g, t, lab, dates):
    """Extend native path support using portfolio.paths via an exact price-unit conversion.

    Multiply 6E prices by PV/20 so existing NQ dollar arithmetic yields 6E dollars.
    This changes units only. No fake NQ costs or 1/10 sizing remains in the component.
    """
    pos = pd.Series(np.arange(g.D), index=pd.DatetimeIndex(g.ts))
    ix = pos.reindex(dates).to_numpy()
    factor = PV / 20.0
    arrays = {}
    for name in ("o", "h", "l", "c"):
        arr = np.full((len(dates), 1440), np.nan)
        valid = np.isfinite(ix)
        arr[valid] = getattr(g, name)[ix[valid].astype(int)] * factor
        arrays[name] = arr
    proxy = SimpleNamespace(**arrays)
    tx = t.copy()
    date_pos = pd.Series(np.arange(len(dates)), index=dates)
    tx["day"] = tx.date.map(date_pos).astype(int)
    tx["entry"] = tx.entry * factor
    tx["exit"] = (tx.exit - tx.side * 2 * TICK) * factor
    w, realized = paths(proxy, tx)
    expected = daily(t, dates).to_numpy()
    np.testing.assert_allclose(realized[:, -1], expected, atol=1e-7)
    assert np.isfinite(w).all()
    return w, realized[:, -1]


def account_run(components, configs, pool, seed):
    keys = sorted({k for cfg in configs.values() for k in cfg})
    change = np.zeros(1440, bool); change[-1] = True
    for k in keys:
        w = components[k][0]
        change[0] |= np.any(w[:, 0] != 0)
        change[1:] |= np.any(np.diff(w, axis=1) != 0, axis=0)
    w = np.stack([components[k][0][:, change] for k in keys])
    c = np.stack([components[k][1] for k in keys])
    d = len(c[0])
    bases = {nm: np.stack([cfg.get(k, np.zeros(d)) for k in keys]) for nm, cfg in configs.items()}
    rng = np.random.default_rng(seed)
    start = rng.integers(0, len(pool), (N_ACCOUNT, 25))
    histories = pool[((start[:, :, None] + np.arange(20)) % len(pool)).reshape(N_ACCOUNT, 500)]
    results = {nm: np.zeros((N_ACCOUNT, 7)) for nm in configs}
    for h, ix in enumerate(histories):
        wh, ch = np.ascontiguousarray(w[:, ix]), np.ascontiguousarray(c[:, ix])
        for nm in configs:
            bh = np.ascontiguousarray(bases[nm][:, ix])
            a = F.simulate_sized(wh, ch, bh, horizon=250, starts=[0], fmin=0.5, fmax=1.0, ref=1500.)
            b = F.simulate_sized(wh, ch, bh, horizon=500, starts=[0], fmin=0.5, fmax=1.0, ref=1500.)
            results[nm][h] = [a["paid"][0], b["paid"][0], a["blown"][0], b["blown"][0],
                              b["payouts"][0], b["days"][0], b["first"][0]]
        if (h + 1) % 500 == 0:
            print(f"  account histories {h + 1}/{N_ACCOUNT}", flush=True)
    return results


def account_summary(results, period):
    rows = []
    for nm, z in results.items():
        t6 = np.where(z[:, 4] == 6, z[:, 5], np.inf)
        row = {"period": period, "config": nm, "y1": z[:, 0].mean(), "y2": z[:, 1].mean(),
               "blown_y1": z[:, 2].mean(), "blown_y2": z[:, 3].mean(),
               "all6": np.mean(z[:, 4] == 6), "days6": np.median(t6),
               "days6_completers": np.median(z[z[:, 4] == 6, 5])}
        rows.append(row)
    diffs = []
    for nm, base in (("addition", "current"), ("replacement", "current"), ("replacement", "empty")):
        z, b = results[nm], results[base]
        row = {"period": period, "config": nm, "versus": base,
               "diff_blown_y1": np.mean(z[:, 2] - b[:, 2]), "diff_blown_y2": np.mean(z[:, 3] - b[:, 3])}
        for year, j in ((1, 0), (2, 1)):
            x = z[:, j] - b[:, j]
            se = x.std(ddof=1) / np.sqrt(len(x))
            row.update({f"diff_y{year}": x.mean(), f"mean_ci_lo_y{year}": x.mean() - 1.645 * se,
                        f"mean_ci_hi_y{year}": x.mean() + 1.645 * se,
                        f"path_p5_y{year}": np.percentile(x, 5), f"path_p95_y{year}": np.percentile(x, 95)})
        diffs.append(row)
    return rows, diffs


def self_checks():
    """Deterministic execution checks on synthetic prices; never read market returns."""
    dates = pd.DatetimeIndex(["2018-01-15", "2018-03-15", "2018-07-15", "2018-10-30"])
    assert clock_minutes(dates).tolist() == [603, 663, 603, 663]
    a = np.full((1, 1440), 1.1)
    g = SimpleNamespace(D=1, o=a.copy(), h=a.copy(), l=a.copy(), c=a.copy(),
                        ts=np.array(["2020-01-02"], dtype="datetime64[ns]"), last_j=np.array([1439]))
    g.c[0, 633] = g.h[0, 633] = 1.101
    sig = pd.DataFrame([dict(day=0, dj=603, side=1, stop=.002, target=np.inf, exit_j=633)])
    t = execute_fx(g, sig)
    np.testing.assert_allclose(t.net, [105.25], atol=1e-8)
    w, c = candidate_component(g, t, None, pd.DatetimeIndex(g.ts))
    np.testing.assert_allclose(c, [105.25], atol=1e-8)
    g.l[0, 604] = 1.097
    t = execute_fx(g, sig)
    assert t.kind.iloc[0] == 0 and t.j1.iloc[0] == 604
    np.testing.assert_allclose(t.net, [-269.75], atol=1e-8)
    g.l[0, 604] = 1.1
    g.o[0, 605] = g.h[0, 605] = g.c[0, 605] = 1.096
    g.l[0, 605] = 1.095
    t = execute_fx(g, sig)
    assert t.kind.iloc[0] == 0 and t.j1.iloc[0] == 605
    np.testing.assert_allclose(t.net, [-519.75], atol=1e-8)
    print("PASS: DST, native 6E dollar paths, costs, entry-bar stops and gap-through fills", flush=True)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    print("Loading confirmed funded roster and 6E data", flush=True)
    lab, dates, current, raw, nq, components, prior = O.build_inputs()
    fx = load_fx()
    base = prior["current"]
    design_dates = dates[dates < SPLIT]
    design_trades, design_metrics, audit_all = {}, [], []
    placebo_summary, placebo_samples = [], []
    for hold in HOLDS:
        sig, audit = make_signals(fx, dates, hold, design=True)
        t = execute_fx(fx, sig)
        design_trades[hold] = t
        design_metrics.extend(metric_rows(t, design_dates, f"hold_{hold}"))
        audit_all.append(audit.assign(period="design", rule=f"hold_{hold}"))
        ps, runs = placebos(fx, t, hold, f"design_{hold}")
        placebo_summary.extend(ps); placebo_samples.extend(runs)
    dm = pd.DataFrame(design_metrics)
    pick_rows = dm[(dm.period == "design") & (dm.side == "whole")].set_index("rule")
    a, b = pick_rows.loc["hold_30"], pick_rows.loc["hold_60"]
    selected = 60 if b.calmar > a.calmar * 1.1 else 30
    # Ensure 'exceeds by 10%' behaves as intended when both Calmars are negative.
    if a.calmar < 0 and b.calmar <= a.calmar + abs(a.calmar) * .1:
        selected = 30
    chosen = design_trades[selected]
    ps = [r for r in placebo_summary if r["rule"] == f"design_{selected}"]
    selrow = pick_rows.loc[f"hold_{selected}"]
    design_pass = bool(selrow.avg > 0 and selrow.t >= 2 and all(r["p_ge_actual"] <= .05 for r in ps))

    # Replacement slot selected on design correlation only, before holdout is constructed.
    moc = O.moc_trades()
    roster_daily, roster_sides, tp, ts = CM.strategy_paths(lab, dates, nq, moc)
    cd = daily(chosen, design_dates)
    correlations = {s: float(cd.corr(x.reindex(design_dates))) for s, x in roster_daily.items()}
    slot = sorted(correlations, key=lambda s: (-abs(correlations[s]), s))[0]
    frozen = {"plan_commit": "aed463d", "variants": 2, "selected_hold": selected,
              "design_pass": design_pass, "replacement_slot": slot, "design_correlations": correlations,
              "seeds": SEEDS, "note": "Frozen before any selected-rule holdout trades or outputs are constructed."}
    save_json("design_selection.json", frozen)
    dm.to_csv(OUT / "design_metrics.csv", index=False)
    print("DESIGN METRICS", flush=True)
    print(pick_rows[["total", "trades", "avg", "t", "calmar"]].to_string(), flush=True)
    print(f"SELECTION FIXED: hold {selected}; design pass {design_pass}; replacement slot {slot}", flush=True)

    # Construct both design account configs and all required controls; no new rule search.
    full_candidate = chosen.copy()
    cx = "FX_FIX"
    # Design component contains zeros outside design, so design evaluation never reads holdout candidate P&L.
    components[cx] = candidate_component(fx, full_candidate, lab, dates)
    empty = {k: v.copy() for k, v in base.items() if k not in CM.ROSTER[slot]}
    configs = {"current": base, "addition": {**base, cx: np.ones(lab.D)},
               "empty": empty, "replacement": {**empty, cx: np.ones(lab.D)}}
    dr = account_run(components, configs, np.where(dates < SPLIT)[0], SEEDS["design_account"])
    ar, ad = account_summary(dr, "design")
    print(pd.DataFrame(ar).to_string(index=False), flush=True)

    print("--- HOLDOUT OPENED ON SELECTED RULE ONLY ---", flush=True)
    sig, audit = make_signals(fx, dates, selected, design=False)
    ht = execute_fx(fx, sig)
    audit_all.append(audit.assign(period="holdout", rule=f"hold_{selected}"))
    t = pd.concat([chosen, ht], ignore_index=True).sort_values("date").reset_index(drop=True)
    pd.DataFrame(metric_rows(t, dates, f"hold_{selected}")).to_csv(OUT / "selected_metrics.csv", index=False)
    t.to_csv(OUT / "selected_trades.csv", index=False)
    yr = t.groupby([t.date.dt.year, "side"]).agg(trades=("net", "size"), total=("net", "sum"), avg=("net", "mean"))
    yr.to_csv(OUT / "by_year_side.csv")
    ps, runs = placebos(fx, ht, selected, "holdout_selected")
    placebo_summary.extend(ps); placebo_samples.extend(runs)
    pd.DataFrame(placebo_summary).to_csv(OUT / "placebo_summary.csv", index=False)
    pd.DataFrame(placebo_samples).to_csv(OUT / "placebo_runs.csv", index=False)

    components[cx] = candidate_component(fx, t, lab, dates)
    hr = account_run(components, configs, np.where(dates >= SPLIT)[0], SEEDS["holdout_account"])
    rr, dd = account_summary(hr, "holdout"); ar.extend(rr); ad.extend(dd)
    ac = pd.DataFrame(ar); diff = pd.DataFrame(ad)
    ac.to_csv(OUT / "account_results.csv", index=False)
    diff.to_csv(OUT / "account_differences.csv", index=False)
    # Raw paired outcomes permit independent confidence calculations without another backtest.
    for period, result in (("design", dr), ("holdout", hr)):
        for nm, z in result.items():
            np.savez_compressed(OUT / f"accounts_{period}_{nm}.npz", outcomes=z)

    boot_rows, perm_rows, mc_rows = [], [], []
    for period, mask in (("full", np.ones(len(dates), bool)), ("holdout", dates >= SPLIT)):
        ds = dates[mask]
        for name, side in (("whole", 0), ("long", 1), ("short", -1)):
            sub = t[t.date.isin(ds)]
            if side:
                sub = sub[sub.side == side]
            x = daily(sub, ds)
            bt = R.bootstrap(x, n=5000, block=10, seed=5001)
            for metric, r in bt.iterrows():
                boot_rows.append({"period": period, "side": name, "metric": metric, **r.to_dict()})
            boot_rows.append({"period": period, "side": name, "metric": "P(Sharpe<=0)",
                              "p50": bt.attrs["p_sharpe_le_0"]})
            perm_rows.append({"period": period, "side": name, **R.permutation(x, n=5000, seed=5002)})
            mc_rows.append({"period": period, "side": name, "type": "trades", **MC.trade_mc(sub.net, n=10000, seed=5003)})
            mc_rows.append({"period": period, "side": name, "type": "one_year", **MC.daily_mc(x, n=5000, seed=5004)})
    pd.DataFrame(boot_rows).to_csv(OUT / "bootstrap.csv", index=False)
    pd.DataFrame(perm_rows).to_csv(OUT / "permutation.csv", index=False)
    pd.DataFrame(mc_rows).to_csv(OUT / "monte_carlo.csv", index=False)
    boot = pd.DataFrame(boot_rows)
    ci = boot[(boot.period == "holdout") & (boot.side == "whole") & (boot.metric == "annual")].iloc[0]
    hmetric = metric_rows(ht, dates[dates >= SPLIT], "holdout")[0]
    hold_pass = bool(hmetric["avg"] > 0 and hmetric["t"] >= 2 and ci.p5 > 0 and
                     all(r["p_ge_actual"] <= .05 for r in ps))

    # Wrong fixed CT clock on DST-mismatch dates is a control, never an alternative rule.
    wrong = []
    for isdesign in (True, False):
        ss, _ = make_signals(fx, dates, selected, design=isdesign, wrong_clock=True)
        wrong.append(execute_fx(fx, ss))
    wt = pd.concat(wrong, ignore_index=True)
    mismatch_dates = dates[clock_minutes(dates) != 603]
    clock_rows = []
    for period, ds in (("design", mismatch_dates[mismatch_dates < SPLIT]),
                       ("holdout", mismatch_dates[mismatch_dates >= SPLIT])):
        for label, tt in (("London_clock", t), ("fixed_1003_CT", wt)):
            z = tt[tt.date.isin(ds)]
            clock_rows.append({"period": period, "clock": label, "dates": len(ds), "trades": len(z),
                               "net": z.net.sum(), "avg": z.net.mean(), "t": O.tstat(z.net)})
    pd.DataFrame(clock_rows).to_csv(OUT / "dst_clock_control.csv", index=False)
    pd.concat(audit_all, ignore_index=True).to_csv(OUT / "data_audit.csv", index=False)

    plan_csv = pd.read_csv("agents/tasks/plan_daily_pnl.csv", parse_dates=["date"]).set_index("date")
    gapdates = plan_csv.index[(plan_csv.drop(columns=[], errors="ignore") == 0).all(axis=1)]
    gaps = t[t.date.isin(gapdates)]
    intraday = []
    # Identify NQ slot overlap from actual entry/exit minutes, rather than daily correlation.
    if slot in CM.SOURCE:
        sn = nq[nq.source == CM.SOURCE[slot]]
        joined = t.merge(sn[["date", "j0", "j1", "side"]], on="date", suffixes=("_fx", "_slot"))
        active = joined[(joined.j0_fx <= joined.j1_slot) & (joined.j1_fx >= joined.j0_slot)]
        intraday = active.date.dt.strftime("%Y-%m-%d").unique().tolist()
    allocation_pass = {}
    for nm in ("addition", "replacement"):
        good = True
        for period in ("design", "holdout"):
            a = ac[(ac.period == period) & (ac.config == nm)].iloc[0]
            b = ac[(ac.period == period) & (ac.config == "current")].iloc[0]
            good &= a.y1 >= b.y1 and a.y2 >= b.y2 and a.blown_y1 <= b.blown_y1 + .01 and a.days6 <= b.days6
            if nm == "replacement":
                e = ac[(ac.period == period) & (ac.config == "empty")].iloc[0]
                good &= a.y1 > e.y1 and a.y2 > e.y2
        allocation_pass[nm] = bool(good)
    if design_pass and hold_pass and any(allocation_pass.values()):
        verdict = "CANDIDATE"
    elif selrow.avg > 0 and hmetric["avg"] > 0:
        verdict = "WATCH"
    else:
        verdict = "REJECT"
    ni = len(pd.read_csv("TRIALS.csv"))
    decision = {**frozen, "holdout_statistical_pass": hold_pass, "allocation_pass": allocation_pass,
                "verdict": verdict, "repository_items": ni, "t_threshold": M.t_threshold(ni),
                "deflated_sharpe": M.deflated_sharpe(t.net, ni),
                "candidate_dates_on_zero_plan_days": len(gaps), "candidate_net_on_zero_plan_days": float(gaps.net.sum()),
                "gap_dates_total": len(gapdates), "slot_intraday_overlap_dates": len(intraday),
                "fix_decision_minutes_CT": {str(k): int(v) for k, v in pd.Series(clock_minutes(dates)).value_counts().items()}}
    save_json("decision.json", decision)
    print("ACCOUNT RESULTS", flush=True)
    print(ac.to_string(index=False), flush=True)
    print("PLACEBOS", flush=True)
    print(pd.DataFrame(placebo_summary).to_string(index=False), flush=True)
    print("DECISION", json.dumps(decision, indent=2), flush=True)


if __name__ == "__main__":
    if "--self-check" in sys.argv:
        self_checks()
    else:
        main()
