"""One preregistered FOMC-minutes NQ screen; plan f1f720d.

Run with the configured Python: analysis/codex_fomc_minutes_screen.py scratch_data
--self-check runs synthetic execution/eligibility checks only.
No candidate holdout, placebo or account simulator is called by this script.
"""
from __future__ import annotations

import copy
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
import codex_sge_delivery_screen as OCC
from codex_overlap_risk_cap import tstat
from param_clusters import trade_net

OUT = Path("analysis/outputs/codex_fomc_minutes_screen")
SP = Path(sys.argv[1] if len(sys.argv) > 1 else "scratch_data")
START, SPLIT = pd.Timestamp("2018-01-01"), pd.Timestamp("2023-01-01")
ANCHOR, DECISION, EXIT = 13 * 60, 13 * 60 + 5, 13 * 60 + 30
ROUND_TRIP = 17.25


def design_grid(g):
    """Remove all post-2022 grid rows before calculating candidate inputs."""
    n = int((pd.DatetimeIndex(g.ts) < SPLIT).sum())
    out = copy.copy(g)
    for key in ("ts", "dates", "o", "h", "l", "c", "v", "last_j"):
        setattr(out, key, getattr(g, key)[:n])
    out.D = n
    out.trading = g.trading[g.trading < n]
    return out


def signals(g, dates, pos, releases, atr):
    lookup = pd.Series(np.arange(g.D), index=pd.DatetimeIndex(g.ts))
    sig, audit = [], []
    for date in releases:
        rec = {"date": date}
        assert START <= date < SPLIT
        if date not in dates:
            audit.append({**rec, "status": "not_trading_date"}); continue
        i, d = dates.get_loc(date), int(lookup.loc[date])
        if pos[i, DECISION] > 0:
            audit.append({**rec, "status": "existing_position", "open_lines": int(pos[i, DECISION])}); continue
        a, b = g.c[d, ANCHOR], g.c[d, DECISION]
        if not np.isfinite(a + b + atr[d]) or atr[d] <= 0:
            audit.append({**rec, "status": "missing_signal_or_ATR"}); continue
        side = int(np.sign(b - a))
        if not side:
            audit.append({**rec, "status": "unchanged"}); continue
        if any(not np.isfinite(getattr(g, k)[d, ANCHOR:EXIT + 1]).all() for k in ("o", "h", "l", "c")):
            audit.append({**rec, "status": "incomplete_window"}); continue
        stop = np.ceil(.25 * atr[d] / .25 - 1e-9) * .25
        sig.append(dict(day=d, dj=DECISION, side=side, stop=stop, target=np.inf, exit_j=EXIT))
        audit.append({**rec, "status": "signal", "side": side, "stop": stop})
    return pd.DataFrame(sig, columns=["day", "dj", "side", "stop", "target", "exit_j"]), pd.DataFrame(audit)


def execute(g, sig):
    t = grid.execute(g, sig, max_trades=1, name="FOMC minutes continuation")
    t["gross"] = t.pnl
    t["net"] = trade_net(t)
    t["cost"] = t.gross - t.net
    assert (t.date < SPLIT).all()
    assert ((t.j0 == DECISION + 1) & (t.j1 <= EXIT)).all()
    assert (t.kind != 1).all()
    np.testing.assert_allclose(t.cost, ROUND_TRIP)
    return t


def tables(t, dates):
    metrics, annual = [], []
    for name, side in (("whole", 0), ("long", 1), ("short", -1)):
        x = t if not side else t[t.side == side]
        daily = x.groupby("date").net.sum().reindex(dates, fill_value=0.)
        metrics.append(dict(side=name, gross_total=x.gross.sum(), cost_total=x.cost.sum(), total=x.net.sum(),
                            gross_avg=x.gross.mean(), t=tstat(x.net), **M.perf(daily, x.net)))
        for year in range(2018, 2023):
            q = x[x.date.dt.year == year]
            annual.append(dict(year=year, side=name, trades=len(q), gross=q.gross.sum(), net=q.net.sum(),
                               gross_avg=q.gross.mean(), net_avg=q.net.mean(), t=tstat(q.net)))
    return pd.DataFrame(metrics), pd.DataFrame(annual)


def self_check():
    a = np.full((1, 1440), 100.)
    g = SimpleNamespace(o=a.copy(), h=a.copy(), l=a.copy(), c=a.copy(), D=1,
                        ts=np.array(["2020-01-02"], dtype="datetime64[ns]"), last_j=np.array([1439]))
    sig = pd.DataFrame([dict(day=0, dj=DECISION, side=1, stop=2., target=np.inf, exit_j=EXIT)])
    g.c[0, EXIT] = g.h[0, EXIT] = 101.
    np.testing.assert_allclose(execute(g, sig).net, [2.75])
    g.l[0, DECISION + 1] = 97.
    t = execute(g, sig)
    assert t.j1.iloc[0] == DECISION + 1 and t.kind.iloc[0] == 0
    np.testing.assert_allclose(t.net, [-57.25])
    g.l[0, DECISION + 1] = 100.
    g.o[0, DECISION + 2] = g.l[0, DECISION + 2] = 95.
    np.testing.assert_allclose(execute(g, sig).net, [-117.25])
    g.o[:] = g.l[:] = g.c[:] = g.h[:] = 100.
    sig["side"] = -1
    g.c[0, EXIT] = g.l[0, EXIT] = 99.
    np.testing.assert_allclose(execute(g, sig).net, [2.75])
    g.o[0, DECISION + 2] = g.h[0, DECISION + 2] = 105.
    np.testing.assert_allclose(execute(g, sig).net, [-117.25])
    # Eligibility depends on current exposure, not future exposure or daily P&L.
    g.o[:] = g.l[:] = g.c[:] = g.h[:] = 100.
    g.c[0, DECISION] = g.h[0, DECISION] = 101.
    dates = pd.DatetimeIndex(g.ts)
    pos = np.zeros((1, 1440), dtype=np.uint16)
    pos[0, DECISION] = 1
    s, audit = signals(g, dates, pos, dates, np.array([10.]))
    assert s.empty and audit.status.iloc[0] == "existing_position"
    pos[:] = 0; pos[0, DECISION + 10] = 1
    s, audit = signals(g, dates, pos, dates, np.array([10.]))
    assert len(s) == 1 and s.stop.iloc[0] == 2.5
    try:
        signals(g, dates, pos, pd.DatetimeIndex(["2023-01-01"]), np.array([10.]))
    except AssertionError:
        pass
    else:
        raise AssertionError("Holdout event was not blocked")
    print("PASS: NQ costs, next-bar entry, entry-bar stop, adverse gap stop, decision-only occupancy, holdout guard")


def verify_saved_trades():
    """Independent scalar replay of the saved rule, not another strategy trial."""
    g = design_grid(pickle.load((SP / "g24.pkl").open("rb")))
    t = pd.read_csv(OUT / "design_trades.csv", parse_dates=["date"])
    atr = g.daily_atr(15)
    for r in t.itertuples():
        d, side = int(r.day), int(r.side)
        assert side == np.sign(g.c[d, DECISION] - g.c[d, ANCHOR])
        entry = g.o[d, DECISION + 1]
        stop = entry - side * np.ceil(.25 * atr[d] / .25 - 1e-9) * .25
        j1, px, kind = EXIT, g.c[d, EXIT], 2
        for j in range(DECISION + 1, EXIT + 1):
            hit = g.l[d, j] <= stop if side == 1 else g.h[d, j] >= stop
            if hit:
                j1, kind = j, 0
                px = min(g.o[d, j], stop) if side == 1 else max(g.o[d, j], stop)
                break
        assert r.j1 == j1 and r.kind == kind
        np.testing.assert_allclose([r.entry, r.exit, r.net], [entry, px, side * (px - entry) * 20 - ROUND_TRIP])
    msg = f"PASS: all {len(t)} saved trades independently replayed; side, entry, stop/time exit and net match"
    (OUT / "verification.txt").write_text(msg + "\n")
    print(msg)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    g = design_grid(pickle.load((SP / "g24.pkl").open("rb")))
    dates = pd.DatetimeIndex(g.ts[g.trading])
    dates = dates[(dates >= START) & (dates < SPLIT)]
    cal = pd.read_csv(OUT / "release_calendar_2018_22.csv", parse_dates=["date"])
    releases = pd.DatetimeIndex(cal.date)
    assert len(releases) == 40 and releases.is_unique and releases.is_monotonic_increasing
    assert cal.groupby(cal.date.dt.year).size().eq(8).all()
    pos, counts = OCC.roster_occupancy(dates)
    occ = pd.DataFrame({"date": releases, "open_at_decision": [int(pos[dates.get_loc(d), DECISION]) for d in releases]})
    occ.to_csv(OUT / "event_occupancy_before_returns.csv", index=False)
    print("Calendar/occupancy frozen before candidate returns:", occ.open_at_decision.eq(0).sum(), "of 40 events flat", flush=True)
    sig, audit = signals(g, dates, pos, releases, g.daily_atr(15))
    t = execute(g, sig)
    metrics, annual = tables(t, dates)
    overlaps = []
    for r in t.itertuples():
        i = dates.get_loc(r.date)
        assert pos[i, DECISION] == 0
        x = pos[i, r.j0:r.j1 + 1] > 0
        overlaps.append(dict(date=r.date, minutes=len(x), overlap_minutes=int(x.sum())))
    overlap = pd.DataFrame(overlaps, columns=["date", "minutes", "overlap_minutes"])
    minutes, overlapped = int(overlap.minutes.sum()), int(overlap.overlap_minutes.sum())
    flat_fraction = 1 - overlapped / minutes if minutes else 0.
    whole = metrics[metrics.side == "whole"].iloc[0]
    positive_years = int((annual[annual.side == "whole"].net > 0).sum())
    gate = dict(at_least_20_trades=bool(len(t) >= 20), gross_at_least_1_5_cost=bool(whole.gross_avg >= 1.5 * ROUND_TRIP),
                net_positive=bool(whole.total > 0), net_t_at_least_2=bool(whole.t >= 2),
                at_least_3_positive_years=bool(positive_years >= 3), at_least_95_percent_unoccupied=bool(flat_fraction >= .95))
    decision = dict(plan_commit="f1f720d", trials=1, period="2018-22 only", gate_checks=gate,
                    design_pass=bool(all(gate.values())), verdict="DESIGN_PASS" if all(gate.values()) else "REJECT",
                    holdout_opened=False, placebos_run=False, monte_carlo_run=False, funded_bench_run=False,
                    round_trip_per_NQ=ROUND_TRIP, gross_hurdle_per_NQ=1.5 * ROUND_TRIP,
                    unoccupied_position_fraction=flat_fraction, position_minutes=minutes, overlap_minutes=overlapped,
                    roster_interval_counts=counts, audit_counts=audit.status.value_counts().to_dict())
    for name, table in (("design_trades", t), ("design_audit", audit), ("design_metrics", metrics),
                        ("design_by_year_side", annual), ("candidate_position_overlap", overlap)):
        table.to_csv(OUT / f"{name}.csv", index=False)
    pd.DataFrame([dict(trial=1, rule="follow 13:00-13:05 minutes reaction; out 13:30; stop .25 ATR; flat roster",
                       design="2018-22", plan="f1f720d", verdict=decision["verdict"])]).to_csv(OUT / "trials.csv", index=False)
    (OUT / "decision.json").write_text(json.dumps(decision, indent=2) + "\n")
    print(metrics.to_string(index=False), flush=True)
    print(annual[annual.side == "whole"].to_string(index=False), flush=True)
    print(json.dumps(decision, indent=2), flush=True)
    print("STOP: design failed; no holdout, placebos or account bench" if not all(gate.values())
          else "DESIGN PASS: rule frozen; validation required before promotion", flush=True)


if __name__ == "__main__":
    if "--self-check" in sys.argv:
        self_check()
    elif "--verify-saved" in sys.argv:
        verify_saved_trades()
    else:
        main()
