"""One preregistered 2018-22 GC screen, plan a161117; no funded bench or holdout on failure.

python -u -B analysis/codex_sge_delivery_screen.py scratch_data
python -B analysis/codex_sge_delivery_screen.py --self-check

Existing open positions come from trade intervals, never accumulated P&L paths.
"""
from __future__ import annotations

import json
import pickle
import sys
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pandas as pd

sys.path.insert(0, "analysis")
import grid
import metrics as M
import codex_overlap_risk_cap as OLD
from grid24 import Grid24

OUT = Path("analysis/outputs/codex_sge_delivery_screen")
SP = Path(sys.argv[1] if len(sys.argv) > 1 else "scratch_data")
PV, TICK, COMM = 100.0, 0.1, 7.25
ROUND_TRIP = COMM + 2 * TICK * PV
SPLIT = pd.Timestamp("2023-01-01")


def shanghai_minute(dates, hour, minute):
    wall = pd.DatetimeIndex(dates).normalize() + pd.Timedelta(hours=hour, minutes=minute)
    ct = wall.tz_localize("Asia/Shanghai").tz_convert("America/Chicago")
    assert (ct.tz_localize(None).normalize() == pd.DatetimeIndex(dates).normalize()).all()
    return np.asarray(ct.hour * 60 + ct.minute, dtype=int)


def add_interval(positions, dates, start, end):
    """Inclusive minute occupancy, including positions carried across midnight."""
    start, end = pd.Timestamp(start), pd.Timestamp(end)
    assert end >= start
    for d in dates[(dates >= start.normalize()) & (dates <= end.normalize())]:
        i = dates.get_loc(d)
        a = max(0, int((start - d).total_seconds() // 60))
        b = min(1439, int((end - d).total_seconds() // 60))
        positions[i, a:b + 1] += 1


def read_mc_intervals(path, zone, entry_back=0):
    r = pd.read_excel(path, sheet_name="List of Trades", header=2)
    en = r[r.Type.astype(str).str.startswith("Entry")].reset_index(drop=True)
    ex = r[r.Type.astype(str).str.startswith("Exit")].reset_index(drop=True)
    assert len(en) == len(ex)
    starts = pd.DatetimeIndex(pd.to_datetime(en.Date)).tz_localize(zone).tz_convert("America/Chicago").tz_localize(None)
    ends = pd.DatetimeIndex(pd.to_datetime(ex.Date)).tz_localize(zone).tz_convert("America/Chicago").tz_localize(None)
    return [(a - pd.Timedelta(minutes=entry_back), b) for a, b in zip(starts, ends)]


def roster_occupancy(dates):
    positions = np.zeros((len(dates), 1440), dtype=np.uint16)
    counts = {}
    # This accepted table already contains ATR-sized integer quantities at the current planned maximum.
    nq = pd.read_csv("analysis/outputs/codex_overlap_risk_cap/nq_overlap_entries.csv", parse_dates=["date"])
    nq = nq[(nq.q_orig > 0) & (nq.source != "MON_BR_MC") & nq.date.isin(dates)]
    for source, t in nq.groupby("source"):
        counts[source] = len(t)
        for r in t.itertuples():
            add_interval(positions, dates, r.date + pd.Timedelta(minutes=int(r.j0)),
                         r.date + pd.Timedelta(minutes=int(r.j1)))
    # Synthetic Monday bookkeeping is not actual overnight exposure; use the source report instead.
    bridge = read_mc_intervals(
        "mc_reports/Backtesting Strategy Performance Report _ @NQ - 5 Minutes Bridge Monday Longs.xlsx",
        "America/Chicago",
    )
    cl = read_mc_intervals(
        "mc_reports/Backtesting Strategy Performance Report _ CL - 5 Minutes CL Sunday Gap.xlsx",
        "America/New_York", entry_back=4,
    )
    for name, pairs in (("MON_BR_MC_actual", bridge), ("CLS_actual", cl)):
        n = 0
        for a, b in pairs:
            if b.normalize() >= dates.min() and a.normalize() <= dates.max():
                add_interval(positions, dates, a, b)
                n += 1
        counts[name] = n
    # Existing, accepted ES MOC rule, no account scoring or new strategy search.
    moc = OLD.moc_trades(str(SP) + "/")
    moc = moc[moc.date.isin(dates)]
    for r in moc.itertuples():
        add_interval(positions, dates, r.date + pd.Timedelta(minutes=int(r.j0)),
                     r.date + pd.Timedelta(minutes=int(r.j1)))
    counts["MOC_MES"] = len(moc)
    return positions, counts


def occupancy_tables(pos, dates):
    rows, hours = [], []
    for weekday in range(5):
        use = dates.dayofweek == weekday
        opened = pos[use] > 0
        p = opened.mean(axis=0)
        for j in range(1440):
            rows.append({"weekday": weekday, "day":
                         ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"][weekday],
                         "minute": j, "hhmm": f"{j // 60:02}:{j % 60:02}", "dates": int(use.sum()),
                         "any_open_fraction": p[j], "mean_open_lines": pos[use, j].mean()})
        for h in range(24):
            x = opened[:, h * 60:(h + 1) * 60]
            hours.append({"weekday": weekday, "hour_ct": h, "dates": int(use.sum()),
                          "fraction_minutes_flat": float((~x).mean()),
                          "fraction_whole_hours_flat": float((~x).all(axis=1).mean())})
    return pd.DataFrame(rows), pd.DataFrame(hours)


def chinese_calendar():
    snapshot = OUT / "shanghai_sessions_2018_22.csv"
    if snapshot.exists():
        sessions = pd.DatetimeIndex(pd.read_csv(snapshot, parse_dates=["date"]).date)
        version = "committed_calendar_snapshot"
    else:
        import exchange_calendars as xc
        version = xc.__version__
        c = xc.get_calendar("XSHG", start="2018-01-01", end="2022-12-31")
        sessions = pd.DatetimeIndex(c.sessions).tz_localize(None).normalize()
        pd.DataFrame({"date": sessions}).to_csv(snapshot, index=False)
    # Exact SGE daytime closures for 2022 from official notice 10000677; weekends are always closed.
    intervals = [("2022-01-01", "2022-01-03"), ("2022-01-31", "2022-02-06"),
                 ("2022-04-03", "2022-04-05"), ("2022-04-30", "2022-05-04"),
                 ("2022-06-03", "2022-06-05"), ("2022-09-10", "2022-09-12"),
                 ("2022-10-01", "2022-10-07")]
    weekdays = pd.date_range("2022-01-01", "2022-12-31", freq="B")
    expected = weekdays
    for a, b in intervals:
        expected = expected[~((expected >= a) & (expected <= b))]
    assert set(sessions[sessions.year == 2022]) == set(expected), "XSHG differs from the official SGE 2022 notice"
    return sessions, version


def make_signals(g, dates, positions, sessions):
    rows = pd.Series(np.arange(g.D), index=pd.DatetimeIndex(g.ts))
    atr = g.daily_atr(15)
    start = shanghai_minute(dates, 15, 0)
    decision = shanghai_minute(dates, 15, 15)
    end = shanghai_minute(dates, 15, 30)
    sig, audit = [], []
    for i, date in enumerate(dates):
        rec = {"date": date, "dj": int(decision[i]), "exit_j": int(end[i])}
        if date not in sessions:
            audit.append({**rec, "status": "Shanghai_closed"}); continue
        if positions[i, decision[i]] > 0:
            audit.append({**rec, "status": "existing_position"}); continue
        if date not in rows.index:
            audit.append({**rec, "status": "missing_GC_date"}); continue
        d = int(rows.loc[date]); j = int(decision[i]); jx = int(end[i]); a = g.c[d, start[i]]; b = g.c[d, j]
        if not np.isfinite(a + b + atr[d]) or atr[d] <= 0:
            audit.append({**rec, "status": "missing_signal_or_ATR"}); continue
        side = int(np.sign(b - a))
        if not side:
            audit.append({**rec, "status": "unchanged"}); continue
        if not np.isfinite(g.o[d, j + 1]):
            audit.append({**rec, "status": "missing_next_open"}); continue
        stop = np.ceil(.25 * atr[d] / TICK - 1e-9) * TICK
        sig.append(dict(day=d, dj=j, side=side, stop=stop, target=np.inf, exit_j=jx))
        audit.append({**rec, "status": "signal", "side": side, "stop": stop,
                      "missing_exit": not np.isfinite(g.c[d, jx])})
    return pd.DataFrame(sig), pd.DataFrame(audit)


def execute_gc(g, sig):
    t = grid.execute(g, sig, max_trades=1, name="SGE delivery continuation")
    t["gross"] = (t.exit - t.entry) * t.side * PV
    t["cost"] = ROUND_TRIP
    t["net"] = t.gross - t.cost
    assert (t.date < SPLIT).all(), "Holdout must not be executed in the screen"
    assert (t.j1 < 15 * 60 + 59).all()
    return t


def tables(t, dates):
    rows, years = [], []
    for side_name, side in (("whole", 0), ("long", 1), ("short", -1)):
        sub = t if not side else t[t.side == side]
        daily = sub.groupby("date").net.sum().reindex(dates, fill_value=0.0)
        rows.append({"side": side_name, "gross_total": sub.gross.sum(), "cost_total": sub.cost.sum(),
                     "total": sub.net.sum(), "gross_avg": sub.gross.mean(), "round_trip": ROUND_TRIP,
                     "t": OLD.tstat(sub.net), **M.perf(daily, sub.net)})
        for year in range(2018, 2023):
            q = sub[sub.date.dt.year == year]
            years.append({"year": year, "side": side_name, "trades": len(q), "gross": q.gross.sum(),
                          "net": q.net.sum(), "net_avg": q.net.mean(), "t": OLD.tstat(q.net)})
    return pd.DataFrame(rows), pd.DataFrame(years)


def self_checks():
    dates = pd.DatetimeIndex(["2020-01-02", "2020-07-02"])
    assert shanghai_minute(dates, 15, 15).tolist() == [75, 135]
    # Overnight position ends on Sunday: it must not appear on Monday.
    ds = pd.DatetimeIndex(["2020-01-06", "2020-01-07"])
    p = np.zeros((2, 1440), dtype=np.uint16)
    add_interval(p, ds, "2020-01-05 19:00", "2020-01-05 23:00")
    assert not p.any()
    add_interval(p, ds, "2020-01-05 19:00", "2020-01-06 02:00")
    assert (p[0, :121] == 1).all() and not p[0, 121:].any() and not p[1].any()
    a = np.full((1, 1440), 1500.)
    g = SimpleNamespace(o=a.copy(), h=a.copy(), l=a.copy(), c=a.copy(), ts=np.array(["2020-01-02"], dtype="datetime64[ns]"), last_j=np.array([1439]))
    g.c[0, 90] = g.h[0, 90] = 1501.
    sig = pd.DataFrame([dict(day=0, dj=75, side=1, stop=2., target=np.inf, exit_j=90)])
    t = execute_gc(g, sig)
    np.testing.assert_allclose(t.net, [72.75])
    g.l[0, 76] = 1497.
    t = execute_gc(g, sig)
    assert t.kind.iloc[0] == 0 and t.j1.iloc[0] == 76
    np.testing.assert_allclose(t.net, [-227.25])
    print("PASS: Shanghai/Chicago DST, midnight interval boundaries, native GC costs, entry-bar stop")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    nq = pickle.load((SP / "g24.pkl").open("rb"))
    dates = pd.DatetimeIndex(nq.ts[nq.trading])
    dates = dates[(dates >= "2018-01-01") & (dates < SPLIT)]
    print("Mapping actual design-period roster intervals; no account simulator is called", flush=True)
    positions, counts = roster_occupancy(dates)
    minute, hour = occupancy_tables(positions, dates)
    minute.to_csv(OUT / "roster_minute_occupancy.csv", index=False)
    hour.to_csv(OUT / "roster_hour_occupancy.csv", index=False)
    print(hour[(hour.hour_ct.isin([1, 2, 7, 10, 15]))].to_string(index=False), flush=True)
    # The occupancy output is frozen before any candidate P&L is calculated.
    sessions, version = chinese_calendar()
    print("SGE 2022 official-calendar cross-check passed", flush=True)
    cache = SP / "gc.pkl"
    g = pickle.load(cache.open("rb")) if cache.exists() else Grid24("data/GC_1min_20*.csv", night_pattern="")
    sig, audit = make_signals(g, dates, positions, sessions)
    t = execute_gc(g, sig)
    metrics, annual = tables(t, dates)
    t.to_csv(OUT / "design_trades.csv", index=False)
    audit.to_csv(OUT / "design_audit.csv", index=False)
    metrics.to_csv(OUT / "design_metrics.csv", index=False)
    annual.to_csv(OUT / "design_by_year_side.csv", index=False)
    overlaps = []
    for r in t.itertuples():
        i = dates.get_loc(r.date)
        assert positions[i, r.j0 - 1] == 0
        x = positions[i, r.j0:r.j1 + 1] > 0
        overlaps.append({"date": r.date, "minutes": len(x), "overlap_minutes": int(x.sum())})
    overlap = pd.DataFrame(overlaps)
    overlap.to_csv(OUT / "candidate_position_overlap.csv", index=False)
    flat_fraction = 1 - overlap.overlap_minutes.sum() / overlap.minutes.sum()
    row = metrics[metrics.side == "whole"].iloc[0]
    positive_years = int((annual[annual.side == "whole"].net > 0).sum())
    gate = {"at_least_100_trades": bool(len(t) >= 100), "gross_at_least_1_5_cost": bool(row.gross_avg >= 1.5 * ROUND_TRIP),
            "net_positive": bool(row.total > 0), "net_t_at_least_2": bool(row.t >= 2),
            "at_least_3_positive_years": bool(positive_years >= 3), "at_least_95_percent_unoccupied": bool(flat_fraction >= .95)}
    decision = {"plan_commit": "a161117", "trials": 1, "period": "2018-22 only", "gate_checks": gate,
                "design_pass": bool(all(gate.values())), "holdout_opened": False, "funded_bench_run": False,
                "verdict": "DESIGN_PASS" if all(gate.values()) else "REJECT", "round_trip_per_GC": ROUND_TRIP,
                "gross_hurdle_per_GC": 1.5 * ROUND_TRIP, "unoccupied_position_fraction": float(flat_fraction),
                "roster_interval_counts": counts, "calendar": "XSHG daytime proxy; exact SGE 2022 cross-check passed",
                "calendar_package_version": version, "audit_counts": audit.status.value_counts().to_dict(),
                "position_minutes": int(overlap.minutes.sum()), "overlap_minutes": int(overlap.overlap_minutes.sum())}
    (OUT / "decision.json").write_text(json.dumps(decision, indent=2) + "\n")
    print("DESIGN SCREEN", flush=True)
    print(metrics.to_string(index=False), flush=True)
    print("DECISION", json.dumps(decision, indent=2), flush=True)
    if not all(gate.values()):
        print("STOP: design failure; no holdout, placebo, Monte Carlo or funded bench", flush=True)


if __name__ == "__main__":
    if "--self-check" in sys.argv:
        self_checks()
    else:
        main()
