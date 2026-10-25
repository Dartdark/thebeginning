"""Frozen six-sleeve historical composition. Research only; never submits orders.

Run design, validation, diagnostics in that order, passing committed --prereg.
Uses original MC ledgers, not independent source-signal replication. All output
creation is exclusive; original workbooks, prices and existing caches are read only.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import warnings

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "analysis"))
import metrics as M
import montecarlo as MC
import resampling as R
from grid24 import Grid24
from portfolio import load_mc
from trials import parse_tier_list

OUT = ROOT / "analysis/outputs/codex_nq_day_flow6"
PLAN = "agents/codex/plans/nq_day_flow6.md"
SEED = 20261025
REPORTS = {
    "VB": "Backtesting Strategy Performance Report VB v1.xlsx",
    "ONB": "Backtesting Strategy Performance Report _ @NQ - 15 Minutes Overnight Bias ML (funded) v2.xlsx",
    "MON": "Backtesting Strategy Performance Report _ @NQ - 5 Minutes NQ Monday Longs.xlsx",
    "EOS": "Backtesting Strategy Performance Report EOS v1.xlsx",
    "LDF": "Backtesting Strategy Performance Report _ @NQ - 5 Minutes Late Day Flow.xlsx",
    "NFP": "Backtesting Strategy Performance Report _ @NQ - 5 Minutes NFP Fade.xlsx",
}
SOURCES = {
    "VB": "apex_strategies/NQ_Vault_Break.txt",
    "ONB": "funded_strategies/NQ_Overnight_Bias_ML.txt",
    "MON": "funded_strategies/NQ_Monday_Long.txt",
    "EOS": "funded_strategies/NQ_Expiration_Open_Short.txt",
    "LDF": "funded_strategies/NQ_Late_Day_Flow.txt",
    "NFP": "funded_strategies/NQ_NFP_Fade.txt",
}
PERSONAL = ROOT / "analysis/outputs/codex_rebound/personal19/UNIFORM/fee_1.24/baseline_daily19.csv"
MATCH = {"VB": "VaultBreak", "ONB": "OvernightBiasML", "MON": "MondayLong",
         "EOS": "ExpirationOpenShort", "LDF": "LateDayFlow", "NFP": "NFPFade"}


class VirtualSleeves:
    """Reference target-position accounting, not an order sender or signal engine.

    Opposite virtual sleeves coexist while actual net exposure can be zero.
    A sleeve's protective exit must update that sleeve alone, then reconcile
    the account to the resulting net target. Do not run uncoordinated charts.
    """
    def __init__(self):
        self.position = {k: 0 for k in REPORTS}

    def target(self, sleeve, desired):
        if sleeve not in self.position or desired not in (-1, 0, 1):
            raise ValueError("Unknown sleeve or non-unit virtual target")
        old = sum(self.position.values())
        self.position[sleeve] = int(desired)
        return sum(self.position.values()) - old


def engineering_checks():
    b = VirtualSleeves()
    assert b.target("ONB", -1) == -1
    assert b.target("VB", 1) == 1 and sum(b.position.values()) == 0
    assert b.target("ONB", 0) == 1  # VB remains intended long, so restore actual long.
    assert b.target("ONB", 0) == 0  # A duplicate stale exit cannot add a new position.
    assert b.target("VB", 0) == -1
    assert sum(b.position.values()) == 0
    for key in REPORTS:
        b.target(key, 1)
    assert sum(b.position.values()) == 6
    for key in REPORTS:
        b.target(key, 0)
    assert sum(b.position.values()) == 0
    try:
        b.target("VB", .5)
        raise AssertionError("Fractional quantity accepted")
    except ValueError:
        pass
    assert R.max_dd([-10., 5.]) == 10.
    # Do not inflate daily evidence by treating duplicated simultaneous tickets
    # as independent observations. Daily aggregation is the primary safeguard.
    x = np.array([-2., 1., 4., 2., -1.])
    np.testing.assert_allclose(tstat(2*x), tstat(x))
    assert tstat(np.repeat(x, 2)) > tstat(x)
    y = np.arange(1., 9.)
    np.testing.assert_allclose(nw_t(y, 0), tstat(y)*np.sqrt(len(y)/(len(y)-1)))
    save_json(OUT / "engineering_checks.json", dict(passed=True,
        checks=["opposing virtual sleeves preserve ownership", "exit restores residual target",
                "duplicate exit gives zero delta", "unit/integer sizing", "six-contract cap",
                "flatten all", "initial-zero drawdown", "ticket splitting vs daily evidence",
                "NW zero-lag convention"]))


def digest(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def save_bytes(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if path.read_bytes() != data:
            raise ValueError(f"Refuse to overwrite different existing artifact: {path}")
        return
    with path.open("xb") as f:
        f.write(data)


def save_json(path, obj):
    save_bytes(path, (json.dumps(obj, indent=2, default=str, allow_nan=True) + "\n").encode())


def save_csv(path, frame, index=False):
    save_bytes(path, frame.to_csv(index=index, float_format="%.12g").encode())


def tstat(x):
    x = np.asarray(x, dtype=float)
    return float(x.mean() / x.std(ddof=1) * np.sqrt(len(x))) if len(x) > 1 and x.std(ddof=1) else np.nan


def nw_t(x, lags=5):
    """Intercept-only Newey-West, Bartlett weights, same convention as plan_alpha_test."""
    x = np.asarray(x, dtype=float)
    e = x - x.mean()
    s = float(e @ e)
    for lag in range(1, min(lags, len(x)-1) + 1):
        s += 2 * (1 - lag / (lags + 1)) * float(e[lag:] @ e[:-lag])
    return float(x.mean() / (np.sqrt(max(s, 0.)) / len(x))) if s > 0 else np.nan


def day_series(t, days, column="net_micro", side=0):
    selected = t if not side else t[t.side == side]
    return selected.groupby("date")[column].sum().reindex(days, fill_value=0.)


def stats(t, days, side=0):
    selected = t if not side else t[t.side == side]
    d = day_series(t, days, side=side)
    x = selected.net_micro
    m = M.perf(d, x)
    # Metrics use real observations; initial zero only corrects DD/Ulcer bookkeeping.
    eq = 50000. + np.r_[0., d.to_numpy().cumsum()]
    dd = eq - np.maximum.accumulate(eq)
    m["max_dd"] = float(-dd.min())
    m["ulcer"] = float(np.sqrt(np.mean((dd[1:] / np.maximum.accumulate(eq)[1:] * 100.)**2)))
    m["calmar"] = m["annual"] / m["max_dd"] if m["max_dd"] else np.nan
    m["ulcer_perf"] = m["annual"] / 50000. * 100. / m["ulcer"] if m["ulcer"] else np.nan
    m.update(days=len(d), total=float(d.sum()), t_trade=tstat(x), t_daily=tstat(d),
             t_nw5=nw_t(d), t_nw20=nw_t(d, 20), gross=float(selected.gross_micro.sum()),
             costs=float(selected.cost_micro.sum()), daily_pf=M.perf(d)["profit_factor"])
    if selected.empty:
        for key in ("win", "avg", "profit_factor", "sharpe", "sortino", "calmar", "ulcer_perf"):
            m[key] = np.nan
    return m


def verify_prereg(prereg):
    subprocess.check_call(["git", "-C", str(ROOT), "cat-file", "-e", f"{prereg}:{PLAN}"])
    committed = subprocess.check_output(["git", "-C", str(ROOT), "show", f"{prereg}:{PLAN}"])
    assert committed == (ROOT / PLAN).read_bytes(), "Preregistered plan changed"
    branch = subprocess.check_output(["git", "-C", str(ROOT), "branch", "--show-current"], text=True).strip()
    assert branch == "codex/work"
    inputs = [ROOT / "mc_reports" / p for p in REPORTS.values()]
    inputs += [ROOT / p for p in SOURCES.values()]
    inputs += sorted((ROOT / "data").glob("NQ_1min_20*.csv"))
    inputs += sorted((ROOT / "data").glob("NQ_1min_ON_*.csv"))
    inputs += [PERSONAL, ROOT / PLAN, ROOT / "analysis/metrics.py", ROOT / "analysis/portfolio.py",
               ROOT / "analysis/grid24.py", ROOT / "analysis/resampling.py", ROOT / "analysis/montecarlo.py"]
    binding = dict(prereg=prereg, inputs={str(p.relative_to(ROOT)): digest(p) for p in inputs},
                   python=sys.version, versions={n: importlib.metadata.version(n) for n in
                       ("numpy", "pandas", "numba", "openpyxl", "scipy", "scikit-learn")},
                   new_economic_variants=1, selected_weights={k: 1 for k in REPORTS})
    save_json(OUT / "source_binding.json", binding)
    return binding


def prepare_window(g, lo, hi, phase):
    """Window first, arithmetic second. The shared loader sees only this window."""
    rows, audit, exclusions = [], [], []
    OUT.mkdir(parents=True, exist_ok=True)
    for name, file in REPORTS.items():
        path = ROOT / "mc_reports" / file
        raw = pd.read_excel(path, sheet_name="List of Trades", header=2)
        entries = raw[raw.Type.astype(str).str.startswith("Entry")].reset_index(drop=True)
        exits = raw[raw.Type.astype(str).str.startswith("Exit")].reset_index(drop=True)
        assert len(entries) == len(exits)
        et, xt = pd.to_datetime(entries.Date), pd.to_datetime(exits.Date)
        keep = (et >= lo) & (xt <= hi + pd.Timedelta(days=1) - pd.Timedelta(microseconds=1))
        ens, exs = entries[keep].reset_index(drop=True), exits[keep].reset_index(drop=True)
        settings = pd.read_excel(path, sheet_name="Settings", header=None)
        setting_map = dict(zip(settings.iloc[:, 0].astype(str), settings.iloc[:, 1].astype(str)))
        assert "Enabled1 Minute" == setting_map.get("Bar Magnifier"), name
        report_bar = int(setting_map["Compression"].split()[0])
        # MC entry stamps can label the end of a 30-minute chart bar while
        # the magnified stop exit carries its earlier native minute label.
        causal_labels = xt >= et - pd.Timedelta(minutes=report_bar-1)
        assert causal_labels[keep].all(), name
        # The temporary report is our windowed derivative, never an existing user input.
        selected_rows = pd.concat([ens, exs], ignore_index=True)
        with tempfile.TemporaryDirectory(prefix="codex_flow6_", dir=OUT) as td:
            filtered = Path(td) / "window.xlsx"
            with pd.ExcelWriter(filtered, engine="openpyxl") as writer:
                selected_rows.to_excel(writer, sheet_name="List of Trades", startrow=2, index=False)
                settings.to_excel(writer, sheet_name="Settings", index=False, header=False)
            t = load_mc(g, str(filtered))
        assert len(t) == len(ens), "Shared loader must not silently drop candidate trades"
        t["source_entry_stamp"] = pd.to_datetime(ens.Date).to_numpy()
        t["source_exit_stamp"] = pd.to_datetime(exs.Date).to_numpy()
        t["date"] = pd.to_datetime(exs.Date).dt.normalize().to_numpy()
        t["sleeve"] = name
        t["source_contracts"] = ens.Contracts.to_numpy(float)
        t["slips"] = 1 + (t.kind != 1).astype(int)
        t["gross_micro"] = (t.exit-t.entry) * t.side * 2.
        t["cost_micro"] = 1.24 + .5 * t.slips
        t["net_micro"] = t.gross_micro - t.cost_micro
        np.testing.assert_allclose(t.pnl / 10., t.gross_micro, rtol=0., atol=1e-7)
        assert (pd.to_datetime(ens.Date).dt.normalize().to_numpy() == t.date.to_numpy()).all(), "Cross-date MC trade"
        assert (t.j1 >= t.j0).all()
        held_missing = entry_unmapped = exit_unmapped = ambiguous_bar = 0
        for r in t.itertuples():
            held_missing += int(np.isnan(g.c[r.day, r.j0:r.j1+1]).sum())
            entry_unmapped += not (g.l[r.day, r.j0] <= r.entry <= g.h[r.day, r.j0])
            exit_unmapped += not (g.l[r.day, r.j1] <= r.exit <= g.h[r.day, r.j1])
            ambiguous_bar += (r.j1 < r.j0 + report_bar and r.kind != 2)
        t["date"] = pd.to_datetime(t.date)
        rows.append(t)
        for i in np.where((et <= pd.Timestamp("2026-10-09 23:59:59")) & ~keep)[0]:
            # Log dates only; do not calculate other-window returns.
            exclusions.append(dict(sleeve=name, entry_stamp=str(et.iloc[i]), exit_stamp=str(xt.iloc[i]),
                                   reason="outside requested phase window"))
        audit.append(dict(sleeve=name, source_tickets=len(entries), phase_tickets=len(t),
            malformed_time_pairs_outside_phase=int((~causal_labels & ~keep).sum()),
            first_stamp=str(et.min()), last_stamp=str(xt.max()), bar_minutes=report_bar,
            source_start=setting_map.get("Start Date"), source_end=setting_map.get("End Date"),
            bar_magnifier=setting_map.get("Bar Magnifier"),
            limit_policy={k:v for k,v in setting_map.items() if "limit" in k.lower() or "time zone" in k.lower()},
            observed_held_missing_minutes=held_missing, entry_price_unmapped=int(entry_unmapped),
            exit_price_unmapped=int(exit_unmapped), same_chart_bar_entries_exits=int(ambiguous_bar)))
    trades = pd.concat(rows, ignore_index=True).sort_values(["date", "j1", "sleeve", "j0"]).reset_index(drop=True)
    days = pd.DatetimeIndex(g.ts[g.trading])
    days = days[(days >= lo) & (days <= hi)]
    assert set(trades.date).issubset(set(days)), "Trade exits missing from daily calendar"
    daily = pd.DataFrame({name: day_series(trades[trades.sleeve == name], days) for name in REPORTS})
    daily["total"] = daily.sum(axis=1)
    daily.index.name = "date"
    np.testing.assert_allclose(daily.total.sum(), trades.net_micro.sum(), atol=1e-6)
    save_csv(OUT / f"{phase}_trades.csv", trades)
    save_csv(OUT / f"{phase}_daily.csv", daily, index=True)
    save_json(OUT / f"{phase}_audit.json", audit)
    save_csv(OUT / f"{phase}_outside_dates.csv", pd.DataFrame(exclusions))
    return trades, daily


def metrics_rows(t, days, period):
    return [dict(period=period, side=label, **stats(t, days, side))
            for side, label in ((0, "all"), (1, "long"), (-1, "short"))]


def run_design():
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        g = Grid24()
    t, d = prepare_window(g, pd.Timestamp("2018-01-01"), pd.Timestamp("2022-12-31"), "design")
    m = stats(t, d.index)
    positive_years = int((d.total.groupby(d.index.year).sum() > 0).sum())
    gates = dict(tickets=m["trades"] >= 300, positive=m["total"] > 0,
                 daily_t=m["t_daily"] >= 3., nw5_t=m["t_nw5"] >= 2.5,
                 pf=m["profit_factor"] >= 1.2, years=positive_years >= 4)
    result = dict(metrics=m, positive_years=positive_years, gates=gates, passed=all(gates.values()))
    save_json(OUT / "design_gate.json", result)
    save_csv(OUT / "design_metrics.csv", pd.DataFrame(metrics_rows(t, d.index, "2018-22")))
    print(json.dumps(result, indent=2))


def read_phase(phase):
    return pd.read_csv(OUT / f"{phase}_trades.csv", parse_dates=["date", "source_entry_stamp", "source_exit_stamp"]), \
        pd.read_csv(OUT / f"{phase}_daily.csv", index_col=0, parse_dates=True)


def run_validation():
    gate = json.loads((OUT / "design_gate.json").read_text())
    assert gate["passed"], "Design failure: stop before validation"
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        g = Grid24()
    t, d = prepare_window(g, pd.Timestamp("2023-01-01"), pd.Timestamp("2026-10-09"), "validation")
    dt, dd = read_phase("design")
    full_t, full_d = pd.concat([dt, t], ignore_index=True), pd.concat([dd, d])
    rows = metrics_rows(dt, dd.index, "2018-22") + metrics_rows(t, d.index, "2023+")
    rows += metrics_rows(full_t, full_d.index, "full")
    for year, dx in full_d.groupby(full_d.index.year):
        rows += metrics_rows(full_t[full_t.date.dt.year == year], dx.index, str(year))
    metrics = pd.DataFrame(rows)
    save_csv(OUT / "metrics.csv", metrics)
    sensitivity = []
    for label, fee, ticks in (("primary", 1.24, 1), ("fee_1.04", 1.04, 1), ("four_ticks", 1.24, 4)):
        for period, tx, dx in (("2018-22", dt, dd), ("2023+", t, d), ("full", full_t, full_d)):
            z = tx.copy()
            z["cost_micro"] = fee + .5 * ticks * z.slips
            z["net_micro"] = z.gross_micro - z.cost_micro
            sensitivity.append(dict(case=label, period=period, **stats(z, dx.index)))
    save_csv(OUT / "cost_sensitivity.csv", pd.DataFrame(sensitivity))
    m = stats(full_t, full_d.index)
    target = {k: m[k] >= 6 for k in ("t_trade", "t_daily", "t_nw5")}
    result = dict(metrics=m, target_tests=target, t6_target_passed=all(target.values()),
                  historical_validation_only=True, new_composite_variants=1)
    save_json(OUT / "target_result.json", result)
    print(json.dumps(result, indent=2))


def diagnostics():
    engineering_checks()
    assert json.loads((OUT / "design_gate.json").read_text())["passed"]
    dt, dd = read_phase("design")
    vt, vd = read_phase("validation")
    t, d = pd.concat([dt, vt], ignore_index=True), pd.concat([dd, vd])
    boot_rows, risk, placebo = [], [], []
    tier = subprocess.check_output(["git", "-C", str(ROOT), "show", "94a1627:TIER_LIST.md"], text=True)
    with tempfile.TemporaryDirectory(prefix="codex_trials_", dir=OUT) as td:
        tier_path = Path(td) / "tier.txt"
        tier_path.write_text(tier)
        prior_trials = parse_tier_list(tier_path)
    item_count = len(prior_trials)
    save_json(OUT / "trial_accounting.json", dict(prior_ranked_items=item_count,
        parsed_prior_variants=int(prior_trials.variants.sum()), new_composite_variants=1,
        actual_prior_searches="Unknown; includes constituent selection, unreported work and repeated portfolio comparisons",
        dsr_sensitivity_trials=10000, n10000_is_not_complete_census=True))
    significance = []
    for period, tx, dx in (("full", t, d), ("2023+", vt, vd)):
        for side, label in ((0, "all"), (1, "long"), (-1, "short")):
            daily = day_series(tx, dx.index, side=side)
            x = tx.net_micro if not side else tx.loc[tx.side == side, "net_micro"]
            # Reuse repo stats and resampled paths, prepend zero only inside path statistics.
            b = R.bootstrap(daily, n=5000, block=10, seed=SEED)
            eqpaths = R.fan_paths(daily, n=5000, block=10, seed=SEED)
            bootdds = np.max(np.maximum.accumulate(np.c_[np.zeros(len(eqpaths)), eqpaths], axis=1)[:, 1:] - eqpaths, axis=1)
            b.loc["max_dd", ["actual", "p5", "p50", "p95"]] = [R.max_dd(daily), *np.percentile(bootdds, [5, 50, 95])]
            annuals = eqpaths[:, -1] / (len(daily) / 252.)
            b.loc["calmar", ["actual", "p5", "p50", "p95"]] = [stats(tx, dx.index, side)["calmar"], *np.percentile(annuals / bootdds, [5, 50, 95])]
            equity = 50000. + np.c_[np.zeros(len(eqpaths)), eqpaths]
            peaks = np.maximum.accumulate(equity, axis=1)
            ulcers = np.sqrt(np.mean(((equity[:,1:]-peaks[:,1:])/peaks[:,1:]*100.)**2, axis=1))
            b.loc["ulcer", ["actual", "p5", "p50", "p95"]] = [stats(tx, dx.index, side)["ulcer"], *np.percentile(ulcers, [5,50,95])]
            ulcer_perf = annuals / 50000. * 100. / ulcers
            # _stats does not return ulcer performance, so keep its additional
            # corrected distribution explicitly in the same result table.
            b.loc["ulcer_perf", ["actual", "p5", "p50", "p95"]] = [stats(tx, dx.index, side)["ulcer_perf"], *np.percentile(ulcer_perf,[5,50,95])]
            for metric, r in b.iterrows():
                boot_rows.append(dict(period=period, side=label, metric=metric, **r.to_dict()))
            risk.append(dict(period=period, side=label, kind="permutation", **R.permutation(daily, n=5000, seed=SEED)))
            risk.append(dict(period=period, side=label, kind="trade_bootstrap_descriptive", **MC.trade_mc(x, n=10000, seed=SEED)))
            for trail in (2000., 4000.):
                risk.append(dict(period=period, side=label, kind="EOD_only_year", trail=trail,
                                 **MC.daily_mc(daily, n=5000, block=10, seed=SEED, trail=trail)))
            for trials in (item_count+1, 10000):
                significance.append(dict(period=period, side=label, trial_lower_bound=trials,
                    dsr_daily=M.deflated_sharpe(daily, trials), dsr_tickets=M.deflated_sharpe(x, trials),
                    required_t=M.t_threshold(trials)))
        gross = day_series(tx, dx.index, "gross_micro").to_numpy()
        costs = day_series(tx, dx.index, "cost_micro").to_numpy()
        rng = np.random.default_rng(SEED)
        null = (rng.choice([-1., 1.], (2000, len(gross))) * gross - costs).sum(axis=1)
        actual = float((gross-costs).sum())
        placebo.append(dict(period=period, null="session_gross_sign_flip_not_execution_placebo", runs=2000,
            actual=actual, null_mean=float(null.mean()), null_p95=float(np.percentile(null,95)),
            p_ge_actual=float((1+np.sum(null >= actual))/(len(null)+1))))
    save_csv(OUT / "bootstrap.csv", pd.DataFrame(boot_rows))
    save_json(OUT / "risk.json", risk)
    save_json(OUT / "placebo.json", placebo)
    save_csv(OUT / "significance.csv", pd.DataFrame(significance))
    personal_comparison(t, d)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        g = Grid24()
    exposure, daily_exposure = [], []
    for date, tx in t.groupby("date"):
        net = np.zeros(1441); gross = np.zeros(1441)
        for r in tx.itertuples():
            net[int(r.j0)] += r.side; net[int(r.j1)+1] -= r.side
            gross[int(r.j0)] += 1; gross[int(r.j1)+1] -= 1
        net, gross = net.cumsum(), gross.cumsum()
        daily_exposure.append(dict(date=str(date.date()), max_net=float(abs(net).max()), max_gross=float(gross.max()),
                                   offset_minutes=int(np.sum(gross > abs(net)))))
        assert net[-1] == gross[-1] == 0
    exposure = dict(max_virtual_gross=max(r["max_gross"] for r in daily_exposure),
                    max_net=max(r["max_net"] for r in daily_exposure),
                    sessions_with_opposing_sleeves=sum(r["offset_minutes"]>0 for r in daily_exposure),
                    note="Inclusive minute-grid proxy; exact intraminute fill ordering remains unverified")
    save_json(OUT / "exposure.json", exposure)
    save_csv(OUT / "exposure_by_day.csv", pd.DataFrame(daily_exposure))
    save_csv(OUT / "component_totals.csv", t.groupby("sleeve").agg(tickets=("net_micro","size"), gross=("gross_micro","sum"), costs=("cost_micro","sum"), net=("net_micro","sum")).reset_index())
    print(json.dumps(dict(exposure=exposure, placebo=placebo), indent=2))


def personal_comparison(t, d):
    p = pd.read_csv(PERSONAL, index_col=0, parse_dates=True)
    selected = list(MATCH.values())
    # Do not remap missing dates forward silently: preserve and inventory them.
    missing = d.index.difference(p.index)
    missing_rows = d.loc[missing]
    save_csv(OUT / "personal_calendar_residual.csv", missing_rows, index=True)
    common = p.index.intersection(d.index)
    p = p.loc[common]; t = t[t.date.isin(common)]
    cand = day_series(t, common)
    starters = {
        "A": ["TwinContinuation","OvernightBiasML","BridgeMondayLong","CLSundayFade_perMCL","NFPFade"],
        "B": ["TwinContinuation","OvernightBiasML","BridgeMondayLong","CLSundayFade_perMCL","NFPFade","ExpirationOpenShort"],
        "C": ["TwinContinuation","OvernightBiasML","BridgeMondayLong","CLSundayFade_perMCL","NFPFade","ExpirationOpenShort","VaultBreak"],
        "D": ["TwinContinuation","OvernightBiasML","BridgeMondayLong","CLSundayFade_perMCL","NFPFade","ExpirationOpenShort","VaultBreak","RelativeStrength","ESMOCFollow_perMES"],
        "FULL": list(p.columns),
    }
    rows = []
    histories = {}
    for period in ("full", "2023+"):
        ix = np.arange(len(p)) if period == "full" else np.where(p.index.year >= 2023)[0]
        rng = np.random.default_rng(SEED)
        nb = int(np.ceil(252/10))
        starts = rng.integers(0, len(ix)-10+1, (1000, nb))
        h = ix[(starts[:,:,None]+np.arange(10)).reshape(1000,-1)[:,:252]]
        histories[period] = h.tolist()
        for cohort, cols in starters.items():
            replaced = [name for name in selected if name in cols]
            base = p[cols].sum(axis=1)
            empty = base - p[replaced].sum(axis=1)
            contrast = {"BASE": base, "ADD": base+cand, "EMPTY": empty, "REPLACE": empty+cand}
            base_mean = base.to_numpy()[h].sum(axis=1)
            for mode, series in contrast.items():
                z = series.to_numpy()[h]; e = np.c_[np.zeros(len(z)), z.cumsum(axis=1)]
                dd95 = float(np.percentile(np.max(np.maximum.accumulate(e,axis=1)-e,axis=1),95))
                sums = z.sum(axis=1); diff = sums-base_mean
                rows.append(dict(period=period, cohort=cohort, contrast=mode,
                    mean_year=float(sums.mean()), median_year=float(np.median(sums)), dd95=dd95,
                    median_profit_dd95=float(np.median(sums)/dd95), incremental_mean=float(diff.mean()),
                    paired_increment_p5=float(np.percentile(diff,5)), paired_increment_p95=float(np.percentile(diff,95)),
                    correlation=float(base.iloc[ix].corr(cand.iloc[ix])),
                    candidate_on_book_loss=float(cand.iloc[ix][base.iloc[ix]<0].sum()),
                    replacing=",".join(replaced)))
    save_json(OUT / "personal_histories.json", histories)
    save_csv(OUT / "personal_comparison.csv", pd.DataFrame(rows))
    save_json(OUT / "personal_limits.json", dict(unmapped_dates=len(missing),
        unmapped_net=float(missing_rows.total.sum()), comparison="Common dates only; no forward date remapping",
        baseline="afde088 common-scale 19-leg snapshot, inherited fee/booking approximations",
        duplication="Six composite constituents already occur in FULL. ADD increases their exposure.",
        apex={context:"LIMITED: no causal joint current overnight baseline paths; EOD-only risk is not placement evidence"
              for context in ("50K evaluation","150K evaluation","50K funded","150K funded")}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--phase", choices=["design", "validation", "diagnostics"], required=True)
    parser.add_argument("--prereg", required=True)
    args = parser.parse_args()
    verify_prereg(args.prereg)
    {"design": run_design, "validation": run_validation, "diagnostics": diagnostics}[args.phase]()
