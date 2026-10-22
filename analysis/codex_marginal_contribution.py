"""Paired leave-one-out contribution study for every current funded-plan line.

Plans (commit f0629aa): agents/codex/plans/marginal_{core,calendar,other}.md
Output: analysis/outputs/codex_marginal_contribution/
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, "analysis")

import codex_overlap_risk_cap as O
import metrics as M
import resampling as R


OUT = Path("analysis/outputs/codex_marginal_contribution")
SPLIT = pd.Timestamp("2023-01-01")
N_BOOT = 2000
N_DAILY_BOOT = 5000
BLOCK = 20
SEEDS = {"full": 20261023, "design": 20261024, "holdout": 20261025}

ROSTER = {
    "Vault Break": ["VB_N", "VB_F"],
    "Overnight Bias ML v2": ["ONB_ML2_MC"],
    "Monday Long": ["MON_MC"],
    "Expiration Open Short": ["EOS"],
    "Late-Day Flow": ["LDF_MC"],
    "NFP Fade": ["NFP_MC"],
    "Bridge Monday Long": ["MON_BR_MC"],
    "CL Sunday Gap Fade": ["CLS"],
    "ES MOC Follow": ["MOC_MES"],
    "Relative Strength longs": ["RS_L"],
}

BATCHES = {
    "core": ["Vault Break", "Overnight Bias ML v2", "Late-Day Flow", "Relative Strength longs"],
    "calendar": ["Monday Long", "Expiration Open Short", "NFP Fade", "Bridge Monday Long"],
    "other": ["CL Sunday Gap Fade", "ES MOC Follow"],
}

SOURCE = {
    "Vault Break": "VB",
    "Overnight Bias ML v2": "ONB_ML2_MC",
    "Monday Long": "MON_MC",
    "Expiration Open Short": "EOS",
    "Late-Day Flow": "LDF_MC",
    "NFP Fade": "NFP_MC",
    "Bridge Monday Long": "MON_BR_MC",
    "Relative Strength longs": "RS_L",
}


def tstat(x):
    x = pd.Series(x, dtype=float).dropna()
    return float(x.mean() / x.std() * np.sqrt(len(x))) if len(x) > 1 and x.std() > 0 else np.nan


def variant_name(strategy):
    return "drop__" + strategy.lower().replace(" ", "_").replace("-", "_")


def account_table(results, year1, period):
    base = results["current"]
    rows = []
    for nm, r in results.items():
        paid, payouts, days, blown = r[:, 0], r[:, 1], r[:, 2], r[:, 3]
        done = days[payouts == 6]
        diff = paid - base[:, 0]
        rows.append({
            "period": period,
            "variant": nm,
            "removed": "" if nm == "current" else next(s for s in ROSTER if variant_name(s) == nm),
            "y1_mean": year1[nm].mean(),
            "y2_mean": paid.mean(),
            "y2_p5": np.percentile(paid, 5),
            "y2_p95": np.percentile(paid, 95),
            "blown": blown.mean(),
            "all6": np.mean(payouts == 6),
            "days6": np.median(done) if len(done) else np.inf,
            "diff_y2": diff.mean(),
            "diff_y2_p5": np.percentile(diff, 5),
            "diff_y2_p95": np.percentile(diff, 95),
            "diff_blown": blown.mean() - base[:, 3].mean(),
            "beats_base": np.mean(diff > 0) + 0.5 * np.mean(diff == 0),
        })
    return pd.DataFrame(rows)


def print_account(tab, title):
    print(f"\n{title}")
    z = tab.copy()
    z["name"] = np.where(z.variant == "current", "Current plan", "Without " + z.removed)
    cols = ["name", "y1_mean", "y2_mean", "blown", "all6", "days6", "diff_y2", "diff_blown",
            "diff_y2_p5", "diff_y2_p95"]
    print(z[cols].to_string(index=False, formatters={
        "y1_mean": "${:,.0f}".format, "y2_mean": "${:,.0f}".format,
        "blown": "{:.1%}".format, "all6": "{:.1%}".format, "days6": "{:.0f}".format,
        "diff_y2": "{:+,.0f}".format, "diff_blown": "{:+.1%}".format,
        "diff_y2_p5": "{:+,.0f}".format, "diff_y2_p95": "{:+,.0f}".format,
    }))


def strategy_paths(lab, dates, trades, moc):
    daily = {}
    sides = {}
    trade_pnl = {}
    trade_side = {}
    for strategy, source in SOURCE.items():
        t = trades[trades.source == source].copy()
        t["pnl"] = t.net_mnq * t.q_orig
        x = t.groupby("d").pnl.sum().reindex(range(len(dates)), fill_value=0.0).to_numpy()
        daily[strategy] = pd.Series(x, index=dates)
        sides[strategy] = {}
        for side, label in ((1, "long"), (-1, "short")):
            xx = t[t.side == side].groupby("d").pnl.sum().reindex(range(len(dates)), fill_value=0.0).to_numpy()
            sides[strategy][label] = pd.Series(xx, index=dates)
        trade_pnl[strategy] = t.pnl.to_numpy(float)
        trade_side[strategy] = t.side.to_numpy(int)

    # Current plan holds two MES; moc.net is the native one-ES research P&L.
    mm = moc.copy()
    mm["date"] = pd.to_datetime(mm.date).dt.normalize()
    mm["pnl"] = mm.net / 5.0
    daily["ES MOC Follow"] = mm.groupby("date").pnl.sum().reindex(dates, fill_value=0.0)
    sides["ES MOC Follow"] = {
        label: mm[mm.side == side].groupby("date").pnl.sum().reindex(dates, fill_value=0.0)
        for side, label in ((1, "long"), (-1, "short"))
    }
    trade_pnl["ES MOC Follow"] = mm.pnl.to_numpy(float)
    trade_side["ES MOC Follow"] = mm.side.to_numpy(int)

    cl = pd.Series(lab.C["CLS"] * 2.0, index=dates)
    daily["CL Sunday Gap Fade"] = cl
    sides["CL Sunday Gap Fade"] = {"long": cl * 0.0, "short": cl.copy()}
    trade_pnl["CL Sunday Gap Fade"] = cl[cl != 0].to_numpy(float)
    trade_side["CL Sunday Gap Fade"] = -np.ones(len(trade_pnl["CL Sunday Gap Fade"]), dtype=int)

    return daily, sides, trade_pnl, trade_side


def metric_tables(daily, sides, trade_pnl, trade_side, dates):
    periods = {"full": np.ones(len(dates), bool), "design": dates < SPLIT, "holdout": dates >= SPLIT}
    rows, years = [], []
    for strategy in ROSTER:
        series = {"whole": daily[strategy], **sides[strategy]}
        for side, x in series.items():
            for period, mask in periods.items():
                d = x[mask]
                # Trade dates are not retained for CL, so standard daily observations are used uniformly.
                active = d[d != 0]
                p = M.perf(d, active)
                rows.append({"strategy": strategy, "side": side, "period": period, "total": d.sum(),
                             "t": tstat(active), **p})
        for year, value in daily[strategy].groupby(dates.year).sum().items():
            years.append({"strategy": strategy, "year": int(year), "total": value})
    return pd.DataFrame(rows), pd.DataFrame(years)


def holdout_bootstrap(daily):
    rows = []
    for i, strategy in enumerate(ROSTER):
        x = daily[strategy][daily[strategy].index >= SPLIT]
        b = R.bootstrap(x, n=N_DAILY_BOOT, block=10, seed=3500 + i)
        for metric, r in b.iterrows():
            rows.append({"strategy": strategy, "metric": metric, **r.to_dict()})
        rows.append({"strategy": strategy, "metric": "P(Sharpe<=0)", "actual": np.nan,
                     "p5": np.nan, "p50": b.attrs["p_sharpe_le_0"], "p95": np.nan})
    return pd.DataFrame(rows)


def decisions(design, holdout):
    db = design[design.variant == "current"].iloc[0]
    hb = holdout[holdout.variant == "current"].iloc[0]
    rows = []
    for strategy in ROSTER:
        nm = variant_name(strategy)
        d = design[design.variant == nm].iloc[0]
        h = holdout[holdout.variant == nm].iloc[0]
        eligible = (d.y2_mean >= db.y2_mean and d.blown <= db.blown and d.days6 <= db.days6 + 5 and
                    (d.y2_mean >= db.y2_mean + 250 or d.blown <= db.blown - 0.01))
        hpass = eligible and h.y2_mean >= hb.y2_mean and h.blown <= hb.blown and h.days6 <= hb.days6
        if hpass:
            verdict = "CANDIDATE"
        elif eligible or (d.diff_y2 > 0 and d.diff_blown <= 0) or (h.diff_y2 > 0 and h.diff_blown <= 0):
            verdict = "WATCH"
        else:
            verdict = "KEEP"
        rows.append({
            "strategy": strategy,
            "design_eligible": bool(eligible),
            "holdout_pass": bool(hpass),
            "verdict": verdict,
            "design_strategy_paid_value": -d.diff_y2,
            "design_strategy_blowup_cost": -d.diff_blown,
            "design_days_faster": d.days6 - db.days6,
            "holdout_strategy_paid_value": -h.diff_y2,
            "holdout_strategy_blowup_cost": -h.diff_blown,
            "holdout_days_faster": h.days6 - hb.days6,
        })
    return pd.DataFrame(rows)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    lab, dates, current, raw, trades, components, prior_configs = O.build_inputs()
    moc = O.moc_trades()
    current_cfg = prior_configs["current"]
    configs = {"current": {k: v.copy() for k, v in current_cfg.items()}}
    for strategy, keys in ROSTER.items():
        configs[variant_name(strategy)] = {k: v.copy() for k, v in current_cfg.items() if k not in keys}

    print("Current funded roster confirmed for the marginal-contribution study:")
    print(current)
    print("ES MOC Follow status: ACTIVE at 2 MES")

    # Reproduce the exact current baseline over all available dates.
    all_pool = np.arange(len(dates))
    full_res, full_y1, nmin = O.run_accounts(
        lab, components, {"current": configs["current"]}, all_pool, N_BOOT, BLOCK, SEEDS["full"]
    )
    full = account_table(full_res, full_y1, "full")
    print_account(full, f"FULL BASELINE: {N_BOOT:,} paired 20-day-block histories ({nmin} decision minutes)")

    design_pool = np.where(dates < SPLIT)[0]
    design_res, design_y1, _ = O.run_accounts(
        lab, components, configs, design_pool, N_BOOT, BLOCK, SEEDS["design"]
    )
    design = account_table(design_res, design_y1, "design")
    print_account(design, f"DESIGN 2018-22: {N_BOOT:,} paired histories")
    db = design[design.variant == "current"].iloc[0]
    eligible = []
    for strategy in ROSTER:
        d = design[design.variant == variant_name(strategy)].iloc[0]
        if (d.y2_mean >= db.y2_mean and d.blown <= db.blown and d.days6 <= db.days6 + 5 and
                (d.y2_mean >= db.y2_mean + 250 or d.blown <= db.blown - 0.01)):
            eligible.append(strategy)
    print(f"\nDESIGN ELIGIBILITY FIXED BEFORE HOLDOUT: {eligible or 'none'}")

    print("\n--- HOLDOUT OPENED: 2023 onward ---")
    hold_pool = np.where(dates >= SPLIT)[0]
    hold_res, hold_y1, _ = O.run_accounts(
        lab, components, configs, hold_pool, N_BOOT, BLOCK, SEEDS["holdout"]
    )
    holdout = account_table(hold_res, hold_y1, "holdout")
    print_account(holdout, f"HOLDOUT 2023+: {N_BOOT:,} paired histories")

    daily, sides, trade_pnl, trade_side = strategy_paths(lab, dates, trades, moc)
    # Exact identity against the benchmark components at full size.
    expected = {}
    for strategy, keys in ROSTER.items():
        z = np.zeros(len(dates))
        for key in keys:
            z += np.floor(current_cfg[key] + 1e-9) * components[key][1]
        expected[strategy] = pd.Series(z, index=dates)
        np.testing.assert_allclose(daily[strategy], expected[strategy], atol=1e-8)
        np.testing.assert_allclose(daily[strategy], sides[strategy]["long"] + sides[strategy]["short"], atol=1e-8)

    metrics, yearly = metric_tables(daily, sides, trade_pnl, trade_side, dates)
    boot = holdout_bootstrap(daily)
    corr = pd.DataFrame(daily).corr()
    decision = decisions(design, holdout)
    account = pd.concat([full, design, holdout], ignore_index=True)

    account.to_csv(OUT / "account_results.csv", index=False)
    decision.to_csv(OUT / "decisions.csv", index=False)
    metrics.to_csv(OUT / "standalone_metrics.csv", index=False)
    yearly.to_csv(OUT / "standalone_by_year.csv", index=False)
    boot.to_csv(OUT / "holdout_bootstrap.csv", index=False)
    corr.to_csv(OUT / "daily_correlation.csv")
    status = {
        "baseline": {"VB_N": 2, "VB_F": 1, "ONB_ML2_MC_risk": 400, "MON_MC": 1,
                     "EOS_risk": 700, "LDF_MC": 2, "NFP_MC_risk": 500, "MON_BR_MC": 1,
                     "CLS_MCL": 2, "MOC_MES": 2, "RS_L_MNQ": 1, "cushion_ref": 1500},
        "es_moc_active": True,
        "batches": BATCHES,
        "trials": {"core": 5, "calendar": 5, "other": 3},
        "seeds": SEEDS,
        "design_eligible": eligible,
    }
    (OUT / "baseline_status.json").write_text(json.dumps(status, indent=2) + "\n")

    print("\nMARGINAL DECISIONS")
    print(decision.to_string(index=False, formatters={
        "design_strategy_paid_value": "${:+,.0f}".format,
        "design_strategy_blowup_cost": "{:+.1%}".format,
        "design_days_faster": "{:+.0f}".format,
        "holdout_strategy_paid_value": "${:+,.0f}".format,
        "holdout_strategy_blowup_cost": "{:+.1%}".format,
        "holdout_days_faster": "{:+.0f}".format,
    }))
    print(f"\nOutputs: {OUT}/")


if __name__ == "__main__":
    main()
