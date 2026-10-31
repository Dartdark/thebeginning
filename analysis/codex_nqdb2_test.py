"""Metrics, frozen gates and report inputs for the preregistered NQDB2 test.

Run after codex_nqdb2_run_profiles.py --design. This script does not replay
strategies or open 2023+ history. It only summarizes already authorized ledgers.
"""
import argparse
import hashlib
import json
import platform
from pathlib import Path

import numpy as np
import pandas as pd

from metrics import perf, deflated_sharpe, t_threshold

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis/outputs/codex_nqdb2_test"
PREREG = "eb7b8b07fd54e8083a13b04f25d1c5b59c68a00b"
PROFILES = ("S0", "S1", "A0", "A1", "E1")


def clean(v):
    if isinstance(v, dict):
        return {str(k): clean(x) for k, x in v.items()}
    if isinstance(v, (list, tuple)):
        return [clean(x) for x in v]
    if isinstance(v, (np.integer,)):
        return int(v)
    if isinstance(v, (np.floating, float)):
        return float(v) if np.isfinite(v) else None
    if isinstance(v, np.bool_):
        return bool(v)
    if isinstance(v, (pd.Timestamp, Path)):
        return str(v)
    return v


def dump(path, v):
    Path(path).write_text(json.dumps(clean(v), indent=2, allow_nan=False) + "\n")


def digest(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def tstat(x):
    x = np.asarray(x, float)
    return float(x.mean() / x.std(ddof=1) * np.sqrt(len(x))) if len(x) > 1 and x.std(ddof=1) > 0 else np.nan


def daily_mtm(g, t, slip_ticks):
    """Calendar-close MTM, with actual entry/exit fill costs, including carries.

    Missing dates have no fabricated price. Any open holding retains its prior
    mark until the next observed close; its global interval remains in ledger.
    Each closed trade's allocated marks and costs reconcile to final net.
    """
    out = np.zeros(g.D)
    details = []
    for row in t.itertuples():
        d0, d1 = int(row.day), int(row.exit_day)
        previous = float(row.raw_entry)
        one = []
        for day in range(d0, d1 + 1):
            if day == d1:
                mark = float(row.raw_exit)
            elif g.last_j[day] >= 0:
                mark = float(g.c[day, g.last_j[day]])
            else:
                mark = previous
            value = (mark - previous) * int(row.side) * 20.0
            if day == d0:
                value -= 3.625 + 5.0 * slip_ticks
            if day == d1:
                value -= 3.625 + (5.0 * slip_ticks if int(row.kind) != 1 else 0)
            out[day] += value
            previous = mark
            one.append(value)
        if not np.isclose(sum(one), float(row.net), atol=1e-7):
            raise AssertionError("Daily MTM / closed trade net mismatch")
        details.append(dict(global_entry=int(row.global_entry), global_exit=int(row.global_exit),
                            allocated_net=sum(one), ledger_net=float(row.net)))
    if not np.isclose(out.sum(), t.net.sum(), atol=1e-6):
        raise AssertionError("Aggregate daily/trade mismatch")
    return pd.Series(out, index=pd.DatetimeIndex(g.ts)), pd.DataFrame(details)


def summarize(g, period, out=OUT):
    first, last = (2018, 2022) if period == "design" else (2023, 2026)
    rows, yearly, audits = [], [], {}
    # Account trading dates plus any source exposure outside that calendar.
    trading = set(map(int, g.trading))
    ledgers = {}
    for profile in PROFILES:
        p = out / f"{period}_{profile}.csv"
        t = pd.read_csv(p)
        ledgers[profile] = t
        trading.update(t.day.astype(int))
        trading.update(t.exit_day.astype(int))
    days = np.array(sorted(d for d in trading if first <= pd.Timestamp(g.ts[d]).year <= last))
    idx = pd.DatetimeIndex(g.ts[days])
    for profile, t in ledgers.items():
        auditpath = out / f"{period}_{profile}_audit.json"
        audits[profile] = json.loads(auditpath.read_text()) if auditpath.exists() else {}
        daily, reconciliation = daily_mtm(g, t, 3 if profile == "E1" else 1)
        d = daily.reindex(idx, fill_value=0.0)
        d.rename("net_NQ").to_csv(out / f"{period}_{profile}_daily.csv", index_label="date")
        reconciliation.to_csv(out / f"{period}_{profile}_reconciliation.csv", index=False)
        for side, sub in (("whole", t), ("long", t[t.side == 1]), ("short", t[t.side == -1])):
            dd = d if side != "short" else d * 0
            m = perf(dd, sub.net)
            m.update(profile=profile, side=side, period=period, net=float(sub.net.sum()),
                     t=tstat(sub.net), gross=float(sub.pnl.sum()),
                     commission=7.25 * len(sub), slippage=float(sub.slippage_usd.sum()),
                     carry_trades=int(sub.carry.sum()))
            rows.append(m)
        dates = pd.to_datetime(t.date)
        for year in range(first, last + 1):
            sub = t[dates.dt.year == year]
            dd = d[d.index.year == year]
            m = perf(dd, sub.net)
            m.update(profile=profile, year=year, net=float(sub.net.sum()), t=tstat(sub.net),
                     mtm_net=float(dd.sum()), carry_trades=int(sub.carry.sum()))
            yearly.append(m)
    frame, years = pd.DataFrame(rows), pd.DataFrame(yearly)
    frame.to_csv(out / f"{period}_metrics.csv", index=False)
    years.to_csv(out / f"{period}_yearly.csv", index=False)
    if period == "design":
        primary = ledgers["A1"]
        ya = years[years.profile == "A1"]
        # Audit format from replay retains censored list; accept zero only.
        a = audits["A1"]
        censor = a.get("censored", [])
        if not isinstance(censor, list):
            censor = a.get("censored_positions", [])
        n_censored = len(censor) if isinstance(censor, list) else int(censor)
        checks = dict(minimum_100_trades=len(primary) >= 100,
                      positive_net=float(primary.net.sum()) > 0,
                      t_at_least_2=tstat(primary.net) >= 2,
                      three_positive_years=int((ya.net > 0).sum()) >= 3,
                      stress_positive=float(ledgers["E1"].net.sum()) > 0,
                      zero_primary_censoring=n_censored == 0)
        gate = dict(prereg_sha=PREREG, preregistration_commit=PREREG,
                    candidate="apex_safe_veto1", checks=checks,
                    statistical_conditions_passed=all(checks.values()),
                    implementation_checks_clear=False,
                    passed=False, design_gate_passed=False,
                    note="Root must attach independent replay/null parity audit before opening recent history.",
                    censored_positions=n_censored,
                    candidate_ledger_sha256=digest(out / "design_A1.csv"))
        dump(out / "design_gate.json", gate)
    dump(out / f"{period}_summary.json", dict(preregistration=PREREG,
         metrics=rows, yearly=yearly, replay_audits=audits,
         note="Daily MTM totals equal final cost-adjusted ledgers; whole equals long; no shorts."))
    return frame, years


def final_statistics(out=OUT, *, run_mc=False):
    """Only previously computed ledgers; no additional signal/return trials."""
    from resampling import bootstrap
    import scipy, numba, openpyxl, sklearn
    context = json.loads((ROOT / "agents/codex/inputs/nqdb2/test_context.json").read_text())
    counts = (context["ranked_items_before_test"] + 1,
              context["ranked_items_before_test"] + 5)
    whole, trials = [], []
    for profile in PROFILES:
        frames, days = [], []
        for period in ("design", "recent"):
            t = pd.read_csv(out / f"{period}_{profile}.csv")
            d = pd.read_csv(out / f"{period}_{profile}_daily.csv", index_col=0, parse_dates=True).iloc[:, 0]
            frames.append(t)
            days.append(d)
            trials.append(dict(profile=profile, period=period, returns_opened=True,
                               trades=len(t), net=t.net.sum(), preregistration=PREREG,
                               selectable=profile == "A1", rule_changed_after_returns=False))
            row = perf(d, t.net)
            row.update(profile=profile, period=period, net=t.net.sum(), t=tstat(t.net),
                       dsr_ranked=deflated_sharpe(t.net, counts[0]),
                       dsr_profile_sensitivity=deflated_sharpe(t.net, counts[1]),
                       multiple_test_t=t_threshold(counts[0]))
            whole.append(row)
        t, d = pd.concat(frames, ignore_index=True), pd.concat(days).sort_index()
        row = perf(d, t.net)
        row.update(profile=profile, period="full", net=t.net.sum(), t=tstat(t.net),
                   dsr_ranked=deflated_sharpe(t.net, counts[0]),
                   dsr_profile_sensitivity=deflated_sharpe(t.net, counts[1]),
                   multiple_test_t=t_threshold(counts[0]))
        whole.append(row)
    pd.DataFrame(whole).to_csv(out / "all_period_metrics.csv", index=False)
    pd.DataFrame(trials).to_csv(out / "trial_ledger.csv", index=False)
    recent = pd.read_csv(out / "recent_A1.csv")
    daily = pd.read_csv(out / "recent_A1_daily.csv", index_col=0, parse_dates=True).iloc[:, 0]
    bs = bootstrap(daily, n=3000, block=20, seed=20261024)
    bs.to_csv(out / "recent_A1_bootstrap.csv", index_label="metric")
    # Same block model, including all zero-trade dates, for trade PF / total.
    gp = recent.assign(date=pd.to_datetime(recent.date), positive=recent.net.clip(lower=0)).groupby("date").positive.sum().reindex(daily.index, fill_value=0).to_numpy()
    gl = recent.assign(date=pd.to_datetime(recent.date), negative=(-recent.net).clip(lower=0)).groupby("date").negative.sum().reindex(daily.index, fill_value=0).to_numpy()
    rng = np.random.default_rng(20261024)
    pf_values, total_values = [], []
    length, block = len(daily), 20
    for _ in range(30):
        starts = rng.integers(0, length - block + 1, (100, int(np.ceil(length / block))))
        ix = (starts[:, :, None] + np.arange(block)).reshape(100, -1)[:, :length]
        pf_values.extend((gp[ix].sum(1) / gl[ix].sum(1)).tolist())
        total_values.extend(daily.to_numpy()[ix].sum(1).tolist())
    dump(out / "recent_A1_bootstrap_extra.json", dict(draws=3000, block=20, seed=20261024,
         interval="5th/50th/95th percentiles; daily calendar blocks retain all trade signs",
         trade_profit_factor_p5_p50_p95=np.percentile(pf_values, [5, 50, 95]).tolist(),
         net_total_p5_p50_p95=np.percentile(total_values, [5, 50, 95]).tolist()))
    dump(out / "environment.json", dict(python=platform.python_version(),
         numpy=np.__version__, pandas=pd.__version__, scipy=scipy.__version__,
         numba=numba.__version__, openpyxl=openpyxl.__version__, sklearn=sklearn.__version__,
         interpreter="/workspace/venvs/thebeginning/bin/python", packages_installed_by_task=False,
         caches_rebuilt=False))
    if run_mc:
        import montecarlo as MC
        gate = json.loads((out / "accounts_gate.json").read_text())
        if not gate.get("account_run_authorized") or gate.get("apex_carry_violations") != 0:
            raise PermissionError("Monte Carlo requires the same complete legal-account gate")
        t = pd.concat([pd.read_csv(out / f"{p}_A1.csv") for p in ("design", "recent")])
        d = pd.concat([pd.read_csv(out / f"{p}_A1_daily.csv", index_col=0, parse_dates=True).iloc[:, 0]
                       for p in ("design", "recent")]).sort_index()
        # Here the standard research commission is $0.725/MNQ. The account
        # adapter separately recomputes $1.04/$1.24, so do not conflate these.
        results = []
        for label, mask in (("2018_plus", np.ones(len(d), bool)), ("2023_plus", d.index.year >= 2023)):
            tt = t if label == "2018_plus" else t[pd.to_datetime(t.date).dt.year >= 2023]
            for size in (0.1, 0.2):
                dm = MC.daily_mc(d.iloc[np.flatnonzero(mask)] * size, horizon=252,
                                 n=5000, block=20, seed=20261024)
                results.append(dict(cohort=label, MNQ=size * 10, **dm))
        dump(out / "standalone_monte_carlo.json", dict(seed=20261024, draws=5000,
             cost_note="Standard research $7.25/NQ plus slippage; account tables use actual micro fees",
             risk_note="EOD-only trailing probability; funded engine separately checks intraday excursion",
             results=results))
    print(pd.DataFrame(whole)[["profile", "period", "trades", "net", "avg", "t", "dsr_ranked", "max_dd"]].to_string(index=False))


def mdtable(headers, rows):
    return "| " + " | ".join(headers) + " |\n|" + "|".join("---" for _ in headers) + "|\n" + "\n".join(
        "| " + " | ".join(str(x) for x in row) + " |" for row in rows)


def write_report(out=OUT):
    m = pd.read_csv(out / "all_period_metrics.csv")
    yy = pd.concat([pd.read_csv(out / f"{p}_yearly.csv") for p in ("design", "recent")])
    ds = {p: json.loads((out / f"diagnostics_{p}/summary.json").read_text()) for p in ("design", "recent")}
    gate = json.loads((out / "accounts_gate.json").read_text())
    audit = json.loads((out / "accounts/candidate_full_audit.json").read_text())
    extra = json.loads((out / "recent_A1_bootstrap_extra.json").read_text())
    bs = pd.read_csv(out / "recent_A1_bootstrap.csv", index_col=0)
    a = m[m.profile == "A1"].set_index("period")
    money = lambda x: f"${float(x):,.0f}"
    report = ["# NQDB2 / DriftBreak v2: REJECT for plan promotion",
        "Summary: The fixed proxy earns money, but does not meet the validation requirements.",
        f"Apex-safe design: {int(a.loc['design','trades'])} trades, {money(a.loc['design','avg'])}/NQ, t={a.loc['design','t']:.2f}; recent: {int(a.loc['recent','trades'])}, {money(a.loc['recent','avg'])}/NQ, t={a.loc['recent','t']:.2f}.",
        f"The drift veto fails its required tests; full-sample DSR {a.loc['full','dsr_ranked']:.3f} is below 0.95.",
        f"Two original-data held-price gaps block the registered funded/evaluation/Monte Carlo stage; no account simulation ran.",
        "Keep the current trading plan. This is a proxy result, not an exact MultiCharts validation.",
        "", f"Plan: `agents/codex/plans/nqdb2_test.md`, `{PREREG}`.",
        "Script: `analysis/codex_nqdb2_run_profiles.py`, `_replay.py`, `_diagnostics.py`, `_test.py`, `_accounts.py`.",
        "Output: `analysis/outputs/codex_nqdb2_test/`. Trials run: **one idea, five fixed return streams**, both registered periods; no retuning.",
        "", "## Rule (as tested)", "",
        "Long NQ above the calendar-open noise band (0.30 times the previous 15 positive Date high-low ranges) and 30-minute VWAP. "
        "Default veto rejects a four-valid-bar return <=-0.10%. Decisions 10:00-14:00 CT inclusive, next-bar market, maximum two submitted attempts/date. "
        "Prearmed 40-point target/75-point stop; exit after seven closes below VWAP or next bar after 15:30. Literal rollover/EOC behavior is preserved.",
        "",
        "S0/S1 are the literal-source proxy with veto off/on. A0/A1 apply the same fixed existing VB early-close calendar: entries before11:00, observed11:30 close exit. "
        "A1 was the primary candidate before returns. E1 is A1 at three ticks slippage. No alternative modes, thresholds, bar sizes, timings or sizes were searched.",
        "",
        "Assumptions: full-session, midnight-aligned close-stamped30-minute bars, IOG off, total-volume-weighted typical price; "
        "MC `Volume` may be up-volume. Previous positive Date ranges include Sunday partials. Existing Grid24 and shared one-minute `grid._walk` are reused. "
        "$7.25/NQ commission plus one tick on market/stop fills; target requires1point trade-through. E1 uses three ticks. "
        "Account scaling would preserve the NQ40/75-point geometry, dividing dollars by10 per MNQ. No unmodified $800/$1500 brackets on an MNQ chart.",
        "", "## Results", "", "All dollars below are **per one NQ**, after stated research costs. 2026 ends2026-10-09; 2023+ is seen historical replication.", ""]
    rows = []
    for profile in PROFILES:
        d = m[(m.profile == profile) & (m.period == "design")].iloc[0]
        r = m[(m.profile == profile) & (m.period == "recent")].iloc[0]
        rows.append([profile, int(d.trades), money(d.net), money(d.avg), f"{d.t:.2f}", int(r.trades), money(r.net), money(r.avg), f"{r.t:.2f}"])
    report += [mdtable(["Rule", "2018-22 n", "Net", "$/trade", "t", "2023+ n", "Net", "$/trade", "t"], rows),
        "", "A1 whole-strategy metrics (identical for longs; **zero shorts**, all short metrics N/A):", ""]
    rows = []
    for period in ("design", "recent", "full"):
        x = a.loc[period]
        rows.append([period, int(x.trades), f"{x.win:.1%}", money(x.avg), f"{x.t:.2f}", f"{x.sharpe:.2f}", f"{x.sortino:.2f}",
                     f"{x.profit_factor:.2f}", f"{x.calmar:.2f}", f"{x.ulcer:.2f}", money(x.max_dd)])
    report += [mdtable(["Period", "n", "Win", "$/trade", "t", "Sharpe", "Sortino", "PF", "Calmar", "Ulcer%", "Daily maxDD"], rows),
        "", "Daily mark-to-market includes actual fill costs and reconciles to trade net to the cent. All profiles' long/short and annual rows are in the CSVs. "
        "Ulcer uses the standard repository $50,000 reference equity; these statistics are not account payout results.", ""]
    rows = []
    for x in yy[yy.profile == "A1"].itertuples():
        rows.append([int(x.year), int(x.trades), money(x.net), money(x.avg), f"{x.t:.2f}", f"{x.profit_factor:.2f}"])
    report += [mdtable(["Year", "A1 trades", "A1 net", "$/trade", "t", "PF"], rows), ""]
    vbpath = out / "baselineall_metrics.csv"
    if not vbpath.exists():
        vbpath = out / "design_current_vb_metrics.csv"
    vb = pd.read_csv(vbpath)
    report += ["Current VB comparator comes from its existing canonical MultiCharts report, with standardized research costs applied once. "
               "It uses different range, volume, cap and clock rules; this is not an isolated drift-veto test or account replacement result.", ""]
    comparable = vb[vb.period.astype(str).isin(["2018_22", "2023_plus", "full", "2023+", "2018_plus"])]
    report += [mdtable(["Current VB period", "n", "Net", "$/trade", "t", "PF", "Daily maxDD"],
        [[x.period, int(x.trades), money(x.net), money(x.avg), f"{x.t:.2f}", f"{x.profit_factor:.2f}", money(x.max_dd)] for x in comparable.itertuples()]),
        "", "## Placebos and account level", "", "The design strategy gate passed, so the same five streams were opened once on2023+. "
        "The independent compiled outcome/scheduler checks match all five full replays and12 selected null reruns in each period. "
        "No source rule was changed after either period was opened.", "", "**Default veto: fails.** Re-entry changes are counted, not treated as simple deletions.", ""]
    rows = []
    for period in ("design", "recent"):
        f = ds[period]["A_filter"]
        rows.append([period, f["removed"]["trades"], money(f["removed"]["avg"]), f"{f['removed']['t']:.2f}",
                     f["new_reentries"]["trades"], money(f["new_reentries"]["total"]),
                     money(f["base"]["max_daily_dd"]), money(f["filtered"]["max_daily_dd"])])
    report += [mdtable(["Period", "Removed n", "Removed mean", "Removed t", "New reentries", "New net", "A0 maxDD", "A1 maxDD"], rows),
        "", "The removed trades must lose and t<=-2; neither period passes. Recent removed trades actually win. "
        "Each family/period has1,000 matched-count trade-drop draws, a gross-removal sensitivity and1,000 decision-mask reruns permitting re-entry. "
        "A1 must beat95% on profit and drawdown, not merely raise its average trade.", ""]
    rows = []
    for period in ("design", "recent"):
        f, s = ds[period]["A_filter"], ds[period]["A_signal_null"]
        for label, summary in (("matched trade drops", f["matched_net_count"]["summary"]), ("signal-mask reruns", s["summary"])):
            rows.append([period, label, f"{summary['p_profit_ge']:.4f}", f"{summary['fraction_observed_beats_dd']:.1%}"])
    report += [mdtable(["Period", "Null", "Profit p", "Share null DD beaten"], rows),
        "", "Random-side controls have100 draws per period. Count-preserving random-time controls also have100; all exceed A1 profit in both periods. "
        "That time control conditions on A1's active dates/counts and **future occupancy feasibility** so schedules can actually submit the matched count. "
        "It is a conditional timing diagnostic, not an unconditional executable strategy or proof that the whole long-NQ edge is zero. "
        "The initial time sampler incorrectly matched proposed instead of actual submissions; those outputs are marked invalid and retained separately. "
        "The corrected sampler is checked against full replay; strategy ledgers never changed.", "",
        f"2023+ bootstrap:3,000 20-day blocks, seed20261024. 90% trade-PF interval "
        f"{extra['trade_profit_factor_p5_p50_p95'][0]:.3f}-{extra['trade_profit_factor_p5_p50_p95'][2]:.3f}; "
        f"net-total interval {money(extra['net_total_p5_p50_p95'][0])} to {money(extra['net_total_p5_p50_p95'][2])}. "
        f"Sharpe interval {bs.loc['sharpe','p5']:.2f}-{bs.loc['sharpe','p95']:.2f}; maxDD interval "
        f"{money(bs.loc['max_dd','p5'])}-{money(bs.loc['max_dd','p95'])}. These bounds do not demonstrate a reliably positive recent edge.", "",
        "**Funded/evaluation/Monte Carlo: not run; registered path-quality gate blocked.** "
        f"All{audit['trades']:,} A1 rows were retained; no censored holdings or illegal carries, and full native/no-trade-date coverage passed. "
        f"The held-path audit separately records{audit['recurring_halt_pattern_trades']} recurring legacy15:16-15:30 gap-pattern trades and two unexplained held-day gaps:", ""]
    report += [mdtable(["Date", "Missing CT minutes", "Original CSV"],
        [[x["date"], x["first_missing_time"] + ("-" + x["last_missing_time"] if x["missing_minutes"] > 1 else ""),
          "data/NQ_1min_" + x["date"][:4] + ".csv"] for x in audit["unexplained_gaps"]]),
        "", "The raw daytime files skip those rows; overnight files provide no replacements. "
        "The shared observed-bar replay skips missing OHLC, so it cannot observe an intervening stop/target/account breach. "
        "No bars were imputed, trades dropped or unofficial bounding variants run. The account gate is false, with zero account simulations. "
        "No payout, blow-up, pass-rate or replacement-gain claim is made. The one-addition/one-replacement/current/empty-slot adapter remains reproducible for a later authorized data-complete study.",
        "", "Account-scope refresh: while this task ran, `USER_CODE_WORKFLOW.md` was published at concurrent Codex commit `fe84522` "
        "(blob `11d532bd92264f6ecb00774ffc34e5ac2ab995e7`). Its broader scope is recorded below. These are limiting conditions, "
        "not simulated findings or inferred results at another account size.", "",
        mdtable(["Destination", "Result / limiting condition"], [
            ["50K evaluation", "Not scored: two unexplained held-price gaps fail the registered account-path gate."],
            ["150K evaluation", "Not scored: the same candidate path is incomplete; no 50K-to-150K performance inference."],
            ["50K funded", "Not scored: complete intraday paths and canonical baseline parity are prerequisites."],
            ["150K funded", "Not scored: incomplete candidate paths; no distinct 150K bootstrap was run."],
            ["Personal ladder/full portfolio", "Not scored: no registered personal comparison opened; source-volume/path uncertainty and failed validation remain. Portfolio contribution is unknown."]]),
        "", "None earns a placement from this evidence. The data gate and failed validation end this trial; no size search or open-ended rescue test follows.",
        "", "## What could make this wrong", "",
        "- **Source parity:** chart session/IOG and native up-volume history are unverified. Total volume and midnight chart/session choices are declared proxy assumptions. "
        "Literal S1 has three cross-date trades across both periods; A1 has none. The original code has no verified holiday liquidation policy.",
        "- **Data/fills:** unexplained intratrade gaps limit even the standalone proxy. One-point limit trade-through and shared OHLC ordering are fixed assumptions; no exact-version MC export was supplied.",
        f"- **Multiple testing:**291 existing ranked items plus this idea gives t bar{a.loc['full','multiple_test_t']:.3f}. "
        f"A1 full t{a.loc['full','t']:.3f} clears that bar, but DSR{a.loc['full','dsr_ranked']:.3f} fails. "
        f"Recent t{a.loc['recent','t']:.3f} misses2; both t and DSR are required, plus clean checks and plan gain. +5-profile sensitivity is in all_period_metrics.csv.",
        "- **Selection/history:** the upload's original development/selection record is unknown and2023+ is already seen. No parameters were chosen on those returns here. "
        "Positive pooled profit does not validate the added drift filter, diversification or account risk.",
        "- **Account baseline:** the independent review notes an unresolved small prior prepared-cache versus published canonical-funded discrepancy. "
        "No new account comparison was reached, so it is neither explained away as rounding nor used to support a candidate.",
        "", "## Differences between the MultiCharts code and the test", "",
        "No new MC code or live file was written. Differences: total-volume surrogate; declared full-session/midnight grid and IOG off; "
        "one-minute path/one-point target fill convention; A-profile early-close safeguard; research costs; explicit endpoint/data-gap auditing. "
        "The independent review is `agents/codex/results/nqdb2_independent_review.md`: implementation arithmetic passes inspection, source/data validation remains WITH CONCERNS.",
        "", "## Reproduce", "", "Use the configured Python environment; existing caches are inputs, never rebuilt. From the repository root:", "", "```bash",
        "export PYTHONPATH=analysis", "PY=/workspace/venvs/thebeginning/bin/python",
        f"$PY analysis/codex_nqdb2_run_profiles.py --design --prereg-sha {PREREG}",
        "$PY analysis/codex_nqdb2_test.py --period design",
        f"$PY analysis/codex_nqdb2_diagnostics.py --design --prereg-sha {PREREG}",
        "$PY analysis/codex_nqdb2_test.py --certify-design",
        f"$PY analysis/codex_nqdb2_run_profiles.py --recent --prereg-sha {PREREG} --gate-file analysis/outputs/codex_nqdb2_test/design_gate.json",
        "$PY analysis/codex_nqdb2_test.py --period recent",
        f"$PY analysis/codex_nqdb2_diagnostics.py --recent --prereg-sha {PREREG} --gate-file analysis/outputs/codex_nqdb2_test/design_gate.json",
        f"$PY analysis/codex_nqdb2_accounts.py --audit-only --root-authorized --preregistration-commit {PREREG}",
        f"$PY analysis/codex_nqdb2_accounts.py --baseline-all-existing --preregistration-commit {PREREG} --out analysis/outputs/codex_nqdb2_test",
        "$PY analysis/codex_nqdb2_test.py --finalize", "$PY analysis/codex_nqdb2_test.py --report", "```", "",
        "Do not use --run or --mc against a false account gate. Full generated feature pickles and redundant null samples can be regenerated; "
        "published ledgers, metrics, audits and source/cache hashes identify this run. No plan, ranking, live, VPS or broker setting changed.", ""]
    content = "\n".join(report)
    for old, new in {
        "before11:00": "before 11:00", "observed11:30": "observed 11:30",
        "close-stamped30": "close-stamped 30", "requires1point": "requires 1 point",
        "NQ40/75": "NQ 40/75", "by10": "by 10", "ends2026": "ends 2026",
        "on2023+": "on 2023+", "and12": "and 12", "has1,000": "has 1,000",
        "and1,000": "and 1,000", "beat95%": "beat 95%", "have100": "have 100",
        "bootstrap:3,000": "bootstrap: 3,000", "seed20261024": "seed 20261024",
        "All1,534": "All 1,534", "records222": "records 222", "legacy15:16": "legacy 15:16",
        "testing:**291": "testing:** 291", "bar3.581": "bar 3.581", "t3.994": "t 3.994",
        "DSR0.855": "DSR 0.855", "t1.727": "t 1.727", "misses2": "misses 2",
        "and2023+": "and 2023+"
    }.items():
        content = content.replace(old, new)
    (ROOT / "agents/codex/results/nqdb2_test.md").write_text(content)
    print("Wrote agents/codex/results/nqdb2_test.md")


def certify_design(out=OUT):
    p = out / "design_gate.json"
    gate = json.loads(p.read_text())
    diagnostic = out / "diagnostics_design/summary.json"
    audit = json.loads(diagnostic.read_text())
    if gate["prereg_sha"] != PREREG or audit["prereg_sha"] != PREREG:
        raise ValueError("Preregistration mismatch")
    if not all(gate["checks"].values()):
        raise PermissionError("Frozen statistical conditions fail")
    if set(audit["profile_parity"]) != set(PROFILES) or not all(
            x["exact_event_match"] for x in audit["profile_parity"].values()):
        raise PermissionError("Replay parity fails")
    if len(audit["selected_null_parity"]) < 12:
        raise PermissionError("Selected null parity checks incomplete")
    gate.update(implementation_checks_clear=True, passed=True, design_gate_passed=True,
                note="All frozen design statistics and independent event/net parity pass. Veto/time controls fail separately; no rule retuning.",
                independent_audit="diagnostics_design/summary.json", independent_audit_sha256=digest(diagnostic))
    dump(p, gate)
    print("Certified frozen design gate; no returns computed")


def main():
    import pickle
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--period", choices=("design", "recent"), default="design")
    ap.add_argument("--scratch", type=Path, default=ROOT / "scratch_data")
    ap.add_argument("--out", type=Path, default=OUT)
    ap.add_argument("--finalize", action="store_true")
    ap.add_argument("--mc", action="store_true")
    ap.add_argument("--report", action="store_true")
    ap.add_argument("--certify-design", action="store_true")
    args = ap.parse_args()
    if args.certify_design:
        certify_design(args.out)
        return
    if args.report:
        write_report(args.out)
        return
    if args.finalize:
        final_statistics(args.out, run_mc=args.mc)
        return
    with (args.scratch / "g24.pkl").open("rb") as f:
        g = pickle.load(f)
    frame, years = summarize(g, args.period, args.out)
    print(frame[frame.side == "whole"][["profile", "trades", "win", "avg", "net", "t", "profit_factor", "max_dd", "carry_trades"]].to_string(index=False))
    print(years.pivot(index="year", columns="profile", values="net").to_string())
    if args.period == "design":
        print((args.out / "design_gate.json").read_text())


if __name__ == "__main__":
    main()
