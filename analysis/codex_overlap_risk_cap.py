"""Preregistered funded-plan overlap-cap study.

Plan: agents/codex/plans/overlap_risk_cap.md (commits b6fc8c0, 17baec8)
Output: analysis/outputs/codex_overlap_risk_cap/

Five trials only: current plan, ES MOC at 1 / 0 MES, NQ same-direction cap 2,
and cap 2 with ES MOC at 1 MES. Selection uses 2018-22 only; 2023+ is printed
and evaluated only after the design selection is fixed.
"""
from __future__ import annotations

import json
import pickle
import sys
import warnings
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")
sys.path.insert(0, "analysis")

import funded_bootstrap as FB
import funded_sim as F
import metrics as M
import resampling as R
from bridge_monday_confirm import load_bridge_mc
from build_lab import REPORTS
from funded_lab import with_slippage
from grid24 import jof
from portfolio import load_mc
import s_rank_es_round1_test as ER


SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
OUT = Path("analysis/outputs/codex_overlap_risk_cap")
SPLIT = pd.Timestamp("2023-01-01")
N_BOOT = 2000
N_RANDOM = 2000
HORIZON = 500
BLOCK = 20
SEED_DESIGN = 20261021
SEED_HOLDOUT = 20261022

VARIANTS = ["current", "moc_1", "moc_0", "cap_2", "cap_2_moc_1"]
LABELS = {
    "current": "Current plan (ES MOC 2)",
    "moc_1": "ES MOC 1",
    "moc_0": "ES MOC 0",
    "cap_2": "NQ cap 2 + ES MOC 2",
    "cap_2_moc_1": "NQ cap 2 + ES MOC 1",
}


def max_dd(x):
    x = np.asarray(x, float)
    eq = np.cumsum(x)
    peak = np.maximum.accumulate(np.maximum(eq, 0.0))
    return float(-(eq - peak).min())


def tstat(x):
    x = pd.Series(x, dtype=float).dropna()
    return float(x.mean() / x.std() * np.sqrt(len(x))) if len(x) > 1 and x.std() > 0 else np.nan


def moc_trades(sp=SP):
    ge = pickle.load(open(sp + "ge.pkl", "rb"))
    tr = ge.trading[pd.DatetimeIndex(ge.ts[ge.trading]) >= "2018-01-01"]
    atr = ge.daily_atr(15)[tr]
    cf = pd.Series(ge.c.ravel()).ffill().to_numpy()
    price = lambda t: cf[tr * 1440 + jof(t)]
    full = ge.last_j[tr] >= jof(1500)
    move = price(1450) - price(1400)
    take = full & (np.abs(move) >= 0.3 * atr) & (move != 0)
    return ER.trades(ge, tr[take], np.sign(move[take]).astype(int), jof(1451), jof(1500), 0.25 * atr[take]).reset_index(drop=True)


def build_inputs():
    lab = FB.plan_lab(SP)
    FB.add_moc_mes(lab, SP)
    rs = pd.read_csv(SP + "rs_trades.csv")
    rs["kind"] = rs.kind.map({"stop": 0, "target": 1, "flat": 2})
    rs = rs[rs.side > 0].reset_index(drop=True)
    lab.add("RS_L", rs)

    current = {**FB.PLAN, "VB_N": 2, "MOC_MES": 2, "RS_L": 1}
    names, base = lab._base(current)
    base_by_key = {k: base[i].copy() for i, k in enumerate(names)}

    dates = pd.DatetimeIndex(lab.g.ts[lab.tr]).normalize()
    day_to_row = pd.Series(np.arange(len(lab.tr)), index=lab.tr)
    flag = pd.read_pickle(SP + "single_print_sessions.pkl").flag.reindex(dates).fillna(False).to_numpy(bool)

    raw = {}
    for key in ("VB", "ONB_ML2_MC", "MON_MC", "EOS", "LDF_MC", "NFP_MC"):
        raw[key] = load_mc(lab.g, REPORTS[key][0]).reset_index(drop=True)
    raw["MON_BR_MC"] = load_bridge_mc(lab.g).reset_index(drop=True)
    raw["RS_L"] = rs

    rows = []
    for source, trades in raw.items():
        already_slipped = source == "MON_BR_MC"
        executed = trades.copy() if already_slipped else with_slippage(trades)
        executed["net_mnq"] = ((executed.exit - executed.entry) * executed.side * 20.0 - 7.25) / 10.0
        for i, r in trades.iterrows():
            if int(r.day) not in day_to_row.index:
                continue
            d = int(day_to_row.loc[int(r.day)])
            key = source
            if source == "VB":
                key = "VB_F" if flag[d] else "VB_N"
            raw_base = float(base_by_key[key][d])
            q = int(np.floor(raw_base + 1e-9))
            if q <= 0:
                continue
            rows.append({
                "source": source,
                "key": key,
                "src_i": int(i),
                "d": d,
                "date": dates[d],
                "j0": int(r.j0),
                "j1": int(r.j1),
                "side": int(r.side),
                "start": int(r.day) * 1440 + int(r.j0),
                "end": int(r.day) * 1440 + int(r.j1),
                "raw_base": raw_base,
                "q_orig": q,
                "net_mnq": float(executed.loc[i, "net_mnq"]),
                "already_slipped": already_slipped,
            })
    trades = pd.DataFrame(rows).sort_values(["start", "source", "src_i"]).reset_index(drop=True)

    q_cap = np.zeros(len(trades), dtype=int)
    active = []
    for start, ix in trades.groupby("start", sort=True).groups.items():
        active = [a for a in active if a["end"] >= start]
        pending = []
        for i in ix:
            r = trades.loc[i]
            other = [a for a in active if a["side"] == r.side and a["source"] != r.source]
            if other:
                used = sum(a["q"] for a in active if a["side"] == r.side)
                q = min(int(r.q_orig), max(0, 2 - used))
            else:
                q = int(r.q_orig)
            q_cap[i] = q
            if q > 0:
                pending.append({"end": int(r.end), "side": int(r.side), "source": r.source, "q": q})
        active.extend(pending)  # same-minute entries do not consume capacity from one another
    trades["q_cap"] = q_cap
    trades["removed"] = trades.q_orig - trades.q_cap

    components = {k: (lab.W[k], lab.C[k]) for k in current}
    cap_bases = {}
    for (key, q, reduced), grp in trades[trades.q_cap > 0].groupby(
        ["key", "q_cap", trades.q_cap < trades.q_orig], sort=True
    ):
        source = grp.source.iloc[0]
        sub = raw[source].loc[grp.src_i].reset_index(drop=True)
        comp = f"CAP__{key}__q{int(q)}__{'reduced' if reduced else 'normal'}"
        lab.add(comp, sub, slippage=not bool(grp.already_slipped.iloc[0]))
        components[comp] = (lab.W[comp], lab.C[comp])
        b = np.zeros(lab.D)
        for d in grp.d.unique():
            b[int(d)] = float(q) if reduced else float(base_by_key[key][int(d)])
        cap_bases[comp] = b

    zero = lambda: np.zeros(lab.D)
    configs = {}
    for variant in VARIANTS:
        b = {}
        capped = variant.startswith("cap_2")
        if capped:
            b.update({k: v.copy() for k, v in cap_bases.items()})
            b["CLS"] = np.full(lab.D, 2.0)
        else:
            for k, v in base_by_key.items():
                if k != "MOC_MES":
                    b[k] = v.copy()
        moc_n = 2 if variant in ("current", "cap_2") else 1 if variant in ("moc_1", "cap_2_moc_1") else 0
        if moc_n:
            b["MOC_MES"] = np.full(lab.D, float(moc_n))
        configs[variant] = b

    # Capped configs use their own NQ components but retain CL and MOC.
    for variant in ("cap_2", "cap_2_moc_1"):
        configs[variant]["CLS"] = np.full(lab.D, 2.0)
    return lab, dates, current, raw, trades, components, configs


def run_accounts(lab, components, configs, pool, n, block, seed):
    keys = sorted({k for cfg in configs.values() for k in cfg})
    chg = np.zeros(1440, dtype=bool)
    for k in keys:
        w = components[k][0]
        chg[-1] = True
        chg[0] |= np.any(w[:, 0] != 0)
        chg[1:] |= np.any(np.abs(np.diff(w, axis=1)) > 0, axis=0)
    W = np.stack([components[k][0][:, chg] for k in keys])
    C = np.stack([components[k][1] for k in keys])
    bases = {nm: np.stack([cfg.get(k, np.zeros(lab.D)) for k in keys]) for nm, cfg in configs.items()}

    rng = np.random.default_rng(seed)
    nb = int(np.ceil(HORIZON / block))
    starts = rng.integers(0, len(pool), (n, nb))
    hist = pool[((starts[:, :, None] + np.arange(block)) % len(pool)).reshape(n, -1)[:, :HORIZON]]
    results = {nm: np.zeros((n, 5)) for nm in configs}
    year1 = {nm: np.zeros(n) for nm in configs}
    for h, ix in enumerate(hist):
        wh = np.ascontiguousarray(W[:, ix]); ch = np.ascontiguousarray(C[:, ix])
        for nm in configs:
            bh = np.ascontiguousarray(bases[nm][:, ix])
            r2 = F.simulate_sized(wh, ch, bh, horizon=HORIZON, starts=[0], fmin=0.5, fmax=1.0, ref=1500.0)
            r1 = F.simulate_sized(wh[:, :250], ch[:, :250], bh[:, :250], horizon=250, starts=[0], fmin=0.5, fmax=1.0, ref=1500.0)
            results[nm][h] = [r2["paid"][0], r2["payouts"][0], r2["days"][0], r2["blown"][0], r2["first"][0]]
            year1[nm][h] = r1["paid"][0]
    return results, year1, int(chg.sum())


def account_table(results, year1, period):
    base = results["current"]
    rows = []
    for nm in results:
        r = results[nm]
        paid, payouts, days, blown = r[:, 0], r[:, 1], r[:, 2], r[:, 3]
        done_days = days[payouts == 6]
        diff = paid - base[:, 0]
        rows.append({
            "period": period,
            "variant": nm,
            "label": LABELS[nm],
            "y1_mean": year1[nm].mean(),
            "y2_mean": paid.mean(),
            "y2_p5": np.percentile(paid, 5),
            "y2_p95": np.percentile(paid, 95),
            "blown": blown.mean(),
            "all6": np.mean(payouts == 6),
            "days6": np.median(done_days) if len(done_days) else np.inf,
            "diff_y2": diff.mean(),
            "diff_y2_p5": np.percentile(diff, 5),
            "diff_y2_p95": np.percentile(diff, 95),
            "diff_blown": blown.mean() - base[:, 3].mean(),
            "beats_base": np.mean(diff > 0) + 0.5 * np.mean(diff == 0),
        })
    return pd.DataFrame(rows)


def choose_design(tab):
    b = tab[tab.variant == "current"].iloc[0]
    eligible = tab[(tab.variant != "current") & (tab.y2_mean >= b.y2_mean) &
                   (tab.blown <= b.blown + 0.005) & (tab.days6 <= b.days6 + 5) &
                   ((tab.y2_mean >= b.y2_mean + 250) | (tab.blown <= b.blown - 0.01))].copy()
    if not len(eligible):
        return "current", []
    eligible = eligible.sort_values(["y2_mean", "blown"], ascending=[False, True])
    top = eligible.iloc[0]
    within = eligible[eligible.y2_mean >= top.y2_mean - 100].sort_values(["blown", "variant"])
    return str(within.iloc[0].variant), eligible.variant.tolist()


def full_size_daily(components, configs, dates):
    out = {}
    for nm, cfg in configs.items():
        d = np.zeros(len(dates))
        for k, b in cfg.items():
            d += np.floor(b + 1e-9) * components[k][1]
        out[nm] = pd.Series(d, index=dates)
    return out


def directional_daily(trades, moc, lab, dates, variant):
    qcol = "q_cap" if variant.startswith("cap_2") else "q_orig"
    rows = trades.assign(pnl=trades.net_mnq * trades[qcol]).groupby(["d", "side"]).pnl.sum()
    ans = {1: np.zeros(len(dates)), -1: np.zeros(len(dates))}
    for (d, side), value in rows.items():
        ans[int(side)][int(d)] += value
    moc_n = 2 if variant in ("current", "cap_2") else 1 if variant in ("moc_1", "cap_2_moc_1") else 0
    date_pos = pd.Series(np.arange(len(dates)), index=dates)
    for r in moc.itertuples():
        d = pd.Timestamp(r.date).normalize()
        if d in date_pos.index:
            ans[int(r.side)][int(date_pos.loc[d])] += float(r.net) / 10.0 * moc_n
    ans[-1] += lab.C["CLS"] * 2  # CL Sunday fade is short-only
    return {"long": pd.Series(ans[1], index=dates), "short": pd.Series(ans[-1], index=dates)}


def metric_tables(daily, directions, dates):
    periods = {
        "full": np.ones(len(dates), dtype=bool),
        "design": dates < SPLIT,
        "holdout": dates >= SPLIT,
    }
    rows, years = [], []
    for nm in VARIANTS:
        sides = {"whole": daily[nm], **directions[nm]}
        for side, series in sides.items():
            for period, mask in periods.items():
                x = series[mask]
                p = M.perf(x)
                active = x[x != 0]
                rows.append({"variant": nm, "side": side, "period": period, "total": x.sum(),
                             "t": tstat(active), **p})
        for year, value in daily[nm].groupby(dates.year).sum().items():
            years.append({"variant": nm, "year": int(year), "total": value})
    return pd.DataFrame(rows), pd.DataFrame(years)


def holdout_bootstrap(daily):
    rows = []
    for i, nm in enumerate(VARIANTS):
        x = daily[nm][daily[nm].index >= SPLIT]
        b = R.bootstrap(x, n=5000, block=10, seed=3100 + i)
        for metric, r in b.iterrows():
            rows.append({"variant": nm, "metric": metric, **r.to_dict()})
        rows.append({"variant": nm, "metric": "P(Sharpe<=0)", "actual": np.nan,
                     "p5": np.nan, "p50": b.attrs["p_sharpe_le_0"], "p95": np.nan})
    return pd.DataFrame(rows)


def removed_table(trades):
    rows = []
    cut = trades[trades.removed > 0].copy()
    cut["period"] = np.where(cut.date < SPLIT, "design", "holdout")
    for (period, key), g in cut.groupby(["period", "key"]):
        x = np.repeat(g.net_mnq.to_numpy(), g.removed.to_numpy(int))
        rows.append({"period": period, "key": key, "entries": len(g), "units": len(x),
                     "total": x.sum(), "avg": x.mean(), "t": tstat(x),
                     "long_units": int(g.loc[g.side > 0, "removed"].sum()),
                     "short_units": int(g.loc[g.side < 0, "removed"].sum())})
    for period, g in cut.groupby("period"):
        x = np.repeat(g.net_mnq.to_numpy(), g.removed.to_numpy(int))
        rows.append({"period": period, "key": "ALL", "entries": len(g), "units": len(x),
                     "total": x.sum(), "avg": x.mean(), "t": tstat(x),
                     "long_units": int(g.loc[g.side > 0, "removed"].sum()),
                     "short_units": int(g.loc[g.side < 0, "removed"].sum())})
    return pd.DataFrame(rows)


def random_drop_placebo(trades, daily):
    units = []
    for r in trades.itertuples():
        for _ in range(int(r.q_orig)):
            units.append({"period": "design" if r.date < SPLIT else "holdout", "key": r.key,
                          "d": int(r.d), "net": float(r.net_mnq)})
    units = pd.DataFrame(units)
    cuts = trades.assign(period=np.where(trades.date < SPLIT, "design", "holdout")).groupby(["period", "key"]).removed.sum()
    rng = np.random.default_rng(4444)
    rows = []
    for period, mask in (("design", daily["current"].index < SPLIT), ("holdout", daily["current"].index >= SPLIT)):
        loc = np.where(mask)[0]
        pos = {d: i for i, d in enumerate(loc)}
        base = daily["current"].to_numpy()[loc]
        actual = daily["cap_2"].to_numpy()[loc]
        profits, dds = np.zeros(N_RANDOM), np.zeros(N_RANDOM)
        groups = []
        for key in cuts.loc[period].index if period in cuts.index.get_level_values(0) else []:
            ncut = int(cuts.loc[(period, key)])
            pool = units[(units.period == period) & (units.key == key)].index.to_numpy()
            groups.append((pool, ncut))
        for run in range(N_RANDOM):
            x = base.copy()
            for pool, ncut in groups:
                if ncut <= 0:
                    continue
                for u in rng.choice(pool, ncut, replace=False):
                    rr = units.loc[u]
                    x[pos[int(rr.d)]] -= float(rr.net)
            profits[run] = x.sum()
            dds[run] = max_dd(x)
        rows.append({
            "period": period,
            "actual_profit": actual.sum(),
            "random_profit_p5": np.percentile(profits, 5),
            "random_profit_p50": np.percentile(profits, 50),
            "random_profit_p95": np.percentile(profits, 95),
            "p_random_profit_ge_actual": np.mean(profits >= actual.sum()),
            "actual_max_dd": max_dd(actual),
            "random_dd_p5": np.percentile(dds, 5),
            "random_dd_p50": np.percentile(dds, 50),
            "random_dd_p95": np.percentile(dds, 95),
            "p_random_dd_le_actual": np.mean(dds <= max_dd(actual)),
        })
    return pd.DataFrame(rows)


def moc_evidence(moc, raw_ldf, dates):
    rows, yearly = [], []
    for side_name, side in (("whole", 0), ("long", 1), ("short", -1)):
        t = moc if side == 0 else moc[moc.side == side]
        for period, use in (("full", np.ones(len(t), bool)), ("design", t.date < SPLIT), ("holdout", t.date >= SPLIT)):
            tt = t[use]
            dl = tt.groupby(pd.to_datetime(tt.date).dt.normalize()).net.sum().reindex(dates[dates < SPLIT] if period == "design" else dates[dates >= SPLIT] if period == "holdout" else dates, fill_value=0.0)
            rows.append({"side": side_name, "period": period, "total": tt.net.sum(), "t": tstat(tt.net), **M.perf(dl, tt.net)})
    for year, g in moc.groupby(pd.to_datetime(moc.date).dt.year):
        yearly.append({"year": int(year), "trades": len(g), "total": g.net.sum(), "avg": g.net.mean(), "t": tstat(g.net)})

    ldf = raw_ldf.copy()
    ldf["date"] = pd.to_datetime(ldf.date).dt.normalize()
    mm = moc[["date", "side", "net"]].copy()
    mm["date"] = pd.to_datetime(mm.date).dt.normalize()
    shared = mm.merge(ldf[["date", "side"]], on="date", suffixes=("_moc", "_ldf"))
    md = mm.groupby("date").net.sum().reindex(dates, fill_value=0.0)
    le = with_slippage(ldf)
    le["net"] = (le.exit - le.entry) * le.side * 20 - 7.25
    ld = le.groupby("date").net.sum().reindex(dates, fill_value=0.0)
    overlap = {
        "moc_days": int(mm.date.nunique()),
        "ldf_days": int(ldf.date.nunique()),
        "shared_days": int(shared.date.nunique()),
        "same_direction_days": int(shared.loc[shared.side_moc == shared.side_ldf, "date"].nunique()),
        "daily_correlation_all_days": float(md.corr(ld)),
        "daily_correlation_shared_days": float(md[md.index.isin(shared.date)].corr(ld[ld.index.isin(shared.date)])),
    }
    return pd.DataFrame(rows), pd.DataFrame(yearly), overlap


def sensitivity(lab, components, configs, selected, dates):
    rows = []
    sub = {k: configs[k] for k in ("current", selected)}
    pool = np.where(dates >= SPLIT)[0]
    for block in (10, 60):
        res, y1, _ = run_accounts(lab, components, sub, pool, N_BOOT, block, SEED_HOLDOUT + block)
        rows.append(account_table(res, y1, f"holdout_L{block}"))
    return pd.concat(rows, ignore_index=True)


def print_account(tab, title):
    print(f"\n{title}")
    cols = ["label", "y1_mean", "y2_mean", "blown", "all6", "days6", "diff_y2", "diff_blown", "diff_y2_p5", "diff_y2_p95"]
    print(tab[cols].to_string(index=False, formatters={
        "y1_mean": "${:,.0f}".format, "y2_mean": "${:,.0f}".format, "blown": "{:.1%}".format,
        "all6": "{:.1%}".format, "days6": "{:.0f}".format, "diff_y2": "{:+,.0f}".format,
        "diff_blown": "{:+.1%}".format, "diff_y2_p5": "{:+,.0f}".format, "diff_y2_p95": "{:+,.0f}".format,
    }))


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    lab, dates, current, raw, trades, components, configs = build_inputs()
    moc = moc_trades()
    print(__doc__.splitlines()[0])
    print(f"Current plan keys: {current}")
    print(f"NQ entries considered: {len(trades):,}; overlap cap reduces {(trades.removed > 0).sum():,} entries / {trades.removed.sum():,} MNQ units")

    design_pool = np.where(dates < SPLIT)[0]
    holdout_pool = np.where(dates >= SPLIT)[0]
    design_res, design_y1, nmin = run_accounts(lab, components, configs, design_pool, N_BOOT, BLOCK, SEED_DESIGN)
    design = account_table(design_res, design_y1, "design")
    selected, eligible = choose_design(design)
    print_account(design, f"DESIGN 2018-22: {N_BOOT:,} paired 20-day-block histories ({nmin} decision minutes)")
    print(f"\nDESIGN SELECTION FIXED BEFORE HOLDOUT: {LABELS[selected]}; eligible alternatives: {eligible or 'none'}")

    print("\n--- HOLDOUT OPENED: 2023 onward ---")
    hold_res, hold_y1, _ = run_accounts(lab, components, configs, holdout_pool, N_BOOT, BLOCK, SEED_HOLDOUT)
    holdout = account_table(hold_res, hold_y1, "holdout")
    print_account(holdout, f"HOLDOUT 2023+: {N_BOOT:,} paired 20-day-block histories")

    b = holdout[holdout.variant == "current"].iloc[0]
    s = holdout[holdout.variant == selected].iloc[0]
    adoption = selected != "current" and s.y2_mean >= b.y2_mean and s.blown <= b.blown and s.days6 <= b.days6
    verdict = "CANDIDATE" if adoption else "REJECT" if selected == "current" or (s.y2_mean < b.y2_mean and s.blown >= b.blown) else "WATCH"

    daily = full_size_daily(components, configs, dates)
    directions = {nm: directional_daily(trades, moc, lab, dates, nm) for nm in VARIANTS}
    for nm in VARIANTS:
        np.testing.assert_allclose(daily[nm], directions[nm]["long"] + directions[nm]["short"], atol=1e-8)
    np.testing.assert_allclose(
        (daily["current"] - daily["cap_2"]).sum(),
        (trades.net_mnq * trades.removed).sum(),
        atol=1e-8,
    )
    np.testing.assert_allclose(
        daily["current"] - daily["moc_1"],
        daily["cap_2"] - daily["cap_2_moc_1"],
        atol=1e-8,
    )
    metrics, yearly = metric_tables(daily, directions, dates)
    boot = holdout_bootstrap(daily)
    removed = removed_table(trades)
    random_drop = random_drop_placebo(trades, daily)
    moc_metrics, moc_yearly, overlap = moc_evidence(moc, raw["LDF_MC"], dates)
    sens = sensitivity(lab, components, configs, selected, dates)

    account = pd.concat([design, holdout], ignore_index=True)
    account.to_csv(OUT / "account_results.csv", index=False)
    metrics.to_csv(OUT / "portfolio_metrics.csv", index=False)
    yearly.to_csv(OUT / "portfolio_by_year.csv", index=False)
    boot.to_csv(OUT / "holdout_bootstrap.csv", index=False)
    removed.to_csv(OUT / "removed_units.csv", index=False)
    random_drop.to_csv(OUT / "random_drop_placebo.csv", index=False)
    moc_metrics.to_csv(OUT / "es_moc_metrics.csv", index=False)
    moc_yearly.to_csv(OUT / "es_moc_by_year.csv", index=False)
    sens.to_csv(OUT / "block_sensitivity.csv", index=False)
    trades.to_csv(OUT / "nq_overlap_entries.csv", index=False)
    decision = {
        "trials": 5,
        "design_selected": selected,
        "eligible_design": eligible,
        "holdout_adoption_pass": bool(adoption),
        "verdict": verdict,
        "es_moc_ldf_overlap": overlap,
        "seeds": {"design": SEED_DESIGN, "holdout": SEED_HOLDOUT},
    }
    (OUT / "decision.json").write_text(json.dumps(decision, indent=2) + "\n")

    print("\nRemoved marginal NQ units")
    print(removed.to_string(index=False, formatters={"total": "${:,.0f}".format, "avg": "${:,.1f}".format, "t": "{:.2f}".format}))
    print("\nRandom-removal placebo")
    print(random_drop.to_string(index=False))
    print("\nES MOC / Late-Day Flow overlap:", overlap)
    print("\nBlock sensitivity for selected rule")
    print(sens[["period", "label", "y2_mean", "blown", "all6", "days6", "diff_y2", "diff_blown"]].to_string(index=False))
    print(f"\nVERDICT: {verdict}; design selected {LABELS[selected]}; holdout adoption pass {adoption}")
    print(f"Outputs: {OUT}/")


if __name__ == "__main__":
    main()
