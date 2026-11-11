"""Shared-walk adapter for frozen pressure studies; no inputs or returns on import.

Signals use completed-calendar-minute CT close labels. Signal close j becomes
an order after one complete minute of receipt allowance, at OPEN of label j+2.
The caller must bind its economic rules before using actual prices.
"""
from __future__ import annotations

import ast
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pandas as pd

from grid import _walk
import metrics as M

ROOT = Path(__file__).resolve().parents[1]
OHLC = ("o", "h", "l", "c")
LEDGER = ["day", "date", "signal_j", "j0", "j1", "side", "entry", "exit",
          "stop", "target", "stop_price", "target_price", "kind", "slips",
          "gross", "pnl", "commission", "slippage", "net", "net_mnq",
          "mnq_commission", "mnq_slippage", "net_mnq_fee150", "stress_four_ticks",
          "qty", "mae_shared_fullbar_proxy", "unobserved_held_minutes",
          "invalid_held_ohlc_minutes", "path_valid", "stop_first_net", "ambiguous_exit_bar", "time_exit_rewound"]


def _invalid_rows(grid, day, start, end):
    values = np.column_stack([getattr(grid, k)[day, start:end + 1] for k in OHLC])
    finite = np.isfinite(values).all(axis=1)
    valid = (finite & (values[:, 1] >= np.maximum(values[:, 0], values[:, 3]))
             & (values[:, 2] <= np.minimum(values[:, 0], values[:, 3]))
             & (values[:, 1] >= values[:, 2]))
    return int((~valid).sum()), int((~finite).sum())


def replay(signals, minute_frame=None, *, grid=None, max_trades=4,
           fill_through=1.0, independent=False):
    """Return (per-1-NQ ledger, diagnostics) using actual shared grid._walk.

    Required signal fields: signal_j, side, exit_j, plus day (grid row) or date.
    Brackets use stop/target distances OR stop_price/max_stop/target_R. The
    latter observes only the scheduled open as a quote proxy, checks risk before
    attempting entry, and rounds target distance up to a quarter point. Optional
    first_entry_j must equal signal_j+2. Duplicate decision signals raise.
    Independent=True is an overlapping signal diagnostic, never an account path.

    Missing actual held paths are RETAINED and flagged; they cannot be quietly
    removed or promoted. The caller must stop advancement if any are flagged.
    Native micro figures are NQ-price proxies, with their own assumed fees.
    """
    if grid is None:
        if minute_frame is None:
            raise ValueError("Pass minute_frame or grid")
        from codex_pressure_build_20261110_inputs import make_grid
        grid = make_grid(minute_frame)
    if max_trades < 1 or fill_through < 0:
        raise ValueError("Invalid execution policy")
    required = {"signal_j", "side", "exit_j"}
    anchored = "stop_price" in signals.columns
    required |= {"stop_price", "max_stop", "target_R"} if anchored else {"stop", "target"}
    if not required.issubset(signals.columns):
        raise ValueError(f"Missing signal columns: {required - set(signals.columns)}")
    s = signals.copy()
    if "day" not in s:
        if "date" not in s:
            raise ValueError("Signals require day or date")
        lookup = {pd.Timestamp(v).normalize(): i for i, v in enumerate(grid.ts)}
        s["day"] = pd.to_datetime(s.date).dt.normalize().map(lookup)
    if s[["day"] + sorted(required)].isna().any().any():
        raise ValueError("NaN signal field")
    if s.duplicated(["day", "signal_j"]).any():
        raise ValueError("More than one signal at a completed decision close")
    s = s.sort_values(["day", "signal_j"], kind="stable")
    counts = {"signals": len(s), "executed": 0, "suppressed_invested_or_same_close": 0,
              "suppressed_daily_cap": 0, "missing_scheduled_entry": 0,
              "quote_stop_wrong_side": 0, "quote_risk_above_maximum": 0,
              "unknown_held_path_trades": 0, "independent_nonexecutable": bool(independent)}
    rows = []
    for day, group in s.groupby("day", sort=True):
        d = int(day)
        if d != day or not 0 <= d < len(grid.ts):
            raise ValueError("Invalid grid day")
        last_exit, taken = -1, 0
        for r in group.itertuples(index=False):
            j = int(r.signal_j); end = int(r.exit_j); side = int(r.side)
            if j != r.signal_j or end != r.exit_j or side != r.side or side not in (-1, 1):
                raise ValueError("Noninteger minute/side or zero side")
            start = j + 2
            if hasattr(r, "first_entry_j") and r.first_entry_j != start:
                raise ValueError("Entry clock differs from frozen one-minute allowance")
            if not (0 <= j < start <= end < grid.o.shape[1]):
                raise ValueError("Invalid same-day decision/entry/exit order")
            bracket = [r.stop_price, r.max_stop, r.target_R] if anchored else [r.stop, r.target]
            if not np.isfinite(bracket).all() or min(bracket) <= 0:
                raise ValueError("Bracket inputs must be finite positive values")
            if not independent and j <= last_exit:
                counts["suppressed_invested_or_same_close"] += 1; continue
            if not independent and taken >= max_trades:
                counts["suppressed_daily_cap"] += 1; continue
            entry = float(grid.o[d, start])
            if not np.isfinite(entry):
                counts["missing_scheduled_entry"] += 1; continue
            if anchored:
                stop_px = float(r.stop_price)
                distance = side * (entry - stop_px)
                if distance <= 0:
                    counts["quote_stop_wrong_side"] += 1; continue
                if distance > r.max_stop:
                    counts["quote_risk_above_maximum"] += 1; continue
                target_distance = float(np.ceil(distance * r.target_R * 4.) / 4.)
            else:
                distance = float(r.stop); target_distance = float(r.target)
                stop_px = entry - side * distance
            if not np.allclose(np.array([distance, target_distance]) * 4., np.round(np.array([distance, target_distance]) * 4.), rtol=0, atol=1e-8):
                raise ValueError("Executable bracket distances must lie on quarter-point ticks")
            target_px = entry + side * target_distance
            out_j, out_px, kind, worst = _walk(grid.o[d], grid.h[d], grid.l[d], grid.c[d],
                                               start, end, side, stop_px, target_px, fill_through)
            rewound = bool(kind == 2 and out_j < end)
            invalid, missing = _invalid_rows(grid, d, start, end if kind == 2 else int(out_j))
            slips = 1 + int(kind != 1)
            gross = float((out_px - entry) * side * 20.)
            bh = (grid.l[d, int(out_j)] <= stop_px and grid.h[d, int(out_j)] >= target_px + fill_through) if side > 0 else (grid.h[d, int(out_j)] >= stop_px and grid.l[d, int(out_j)] <= target_px - fill_through)
            conservative_exit = (min(stop_px, grid.o[d, int(out_j)]) if side > 0 else max(stop_px, grid.o[d, int(out_j)])) if bh and kind == 1 else out_px
            conservative_slips = 2 if bh and kind == 1 else slips
            conservative_net = float((conservative_exit-entry)*side*20. - 7.25 - 5.*conservative_slips)
            row = dict(day=d, date=pd.Timestamp(grid.ts[d]), signal_j=j, j0=start, j1=int(out_j),
                       side=side, entry=entry, exit=float(out_px), stop=distance, target=target_distance,
                       stop_price=float(stop_px), target_price=float(target_px), kind=int(kind), slips=slips,
                       gross=gross, pnl=gross, commission=7.25, slippage=5. * slips,
                       net=gross - 7.25 - 5. * slips, net_mnq=gross / 10. - 1.24 - .5 * slips,
                       mnq_commission=1.24, mnq_slippage=.5 * slips,
                       net_mnq_fee150=gross / 10. - 1.50 - .5 * slips,
                       stress_four_ticks=gross - 7.25 - 20. * slips, qty=1.,
                       ambiguous_exit_bar=bool(bh), stop_first_net=conservative_net,
                       mae_shared_fullbar_proxy=float(abs(worst - entry) * 20.),
                       unobserved_held_minutes=missing, invalid_held_ohlc_minutes=invalid,
                       time_exit_rewound=rewound, path_valid=invalid == 0 and not rewound and np.isfinite(out_px))
            # Retain input features for audit without allowing overwrite of fills/cash.
            row.update({k: v for k, v in r._asdict().items() if k not in row})
            rows.append(row)
            counts["unknown_held_path_trades"] += int(not row["path_valid"])
            last_exit = int(out_j); taken += 1
    t = pd.DataFrame(rows) if rows else pd.DataFrame(columns=LEDGER)
    if t.empty:
        t["date"] = pd.Series(dtype="datetime64[ns]")
        for col in LEDGER:
            if col != "date": t[col] = pd.Series(dtype=float)
    counts["executed"] = len(t)
    counts["fill_rules"] = "shared _walk; entry-bar protection; worse stop gaps; 1-point target-through; shared both-hit path"
    counts["risk_limit"] = "shared worst is a full-bar proxy; not native intrabar extrema or an Apex account replay"
    counts["entry_guard"] = ("scheduled open is an assumed observable quote proxy; rejects wrong-side or oversized anchored stop before order; slippage is separately charged and may exceed nominal cap" if anchored else "fixed point-distance brackets")
    return t, counts


def _shared_stats():
    """Bind existing pure C.stats/nw/tstat without its unrelated import side effects."""
    path = ROOT / "analysis/codex_cash_open_repair.py"
    tree = ast.parse(path.read_text())
    selected = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in {"stats", "nw", "tstat"}]
    if len(selected) != 3:
        raise ValueError("Shared metric interface changed")
    namespace = {"np": np, "pd": pd, "M": M}
    exec(compile(ast.Module(body=selected, type_ignores=[]), str(path), "exec"), namespace)
    return namespace["stats"]


def metrics_summary(trades, calendar_dates, column="net", *, allow_unknown=False):
    """Shared initial-zero daily metrics and trade/NW t; preserve explicit zero days."""
    if not allow_unknown and len(trades) and (trades.invalid_held_ohlc_minutes > 0).any():
        raise ValueError("Unknown held OHLC path; descriptive outcomes cannot advance")
    t = trades.copy()
    if column.startswith("net_mnq"):
        t["pnl"] = t.gross / 10.
    return _shared_stats()(t, pd.DatetimeIndex(calendar_dates), column=column)


def metrics_table(trades, calendar_dates, column="net", *, allow_unknown=False):
    """Whole/long/short, pooled and by year; no selection or gate inside helper."""
    days = pd.DatetimeIndex(calendar_dates)
    rows = []
    for side, label in [(0, "all"), (1, "long"), (-1, "short")]:
        t = trades if side == 0 else trades[trades.side == side]
        periods = [("all", days)] + [(str(y), days[days.year == y]) for y in sorted(set(days.year))]
        for period, cal in periods:
            sub = t if period == "all" else t[pd.DatetimeIndex(t.date).year == int(period)]
            rows.append(dict(period=period, side=label, units=column,
                             **metrics_summary(sub, cal, column, allow_unknown=allow_unknown)))
    return pd.DataFrame(rows)


def minute_close_marks(grid, trades, *, instrument="NQ", allow_unknown=False):
    """Return day/minute close-mark P&L; reconcile EOD to ledger, not an account simulator.

    Entry half-commission + market slippage are charged at entry. Remaining costs
    are charged at exit. OHLC intraminute floor touches are not represented here.
    A negative P&L at an earlier intraminute extreme must use a separate event tape.
    """
    if instrument not in {"NQ", "MNQ"}: raise ValueError("Instrument must be NQ or MNQ")
    if not allow_unknown and len(trades) and (trades.invalid_held_ohlc_minutes > 0).any():
        raise ValueError("Unknown held path")
    marks = np.zeros_like(grid.c, dtype=float)
    pv, fee, slip, column = (20., 7.25, 5., "net") if instrument == "NQ" else (2., 1.24, .5, "net_mnq")
    for r in trades.itertuples():
        d, a, b = int(r.day), int(r.j0), int(r.j1)
        marks[d, a:b] += (grid.c[d, a:b] - r.entry) * r.side * pv - fee / 2. - slip
        marks[d, b:] += getattr(r, column)
    totals = trades.groupby("day")[column].sum()
    for d, total in totals.items():
        np.testing.assert_allclose(marks[int(d), -1], total, rtol=0, atol=1e-8)
    return marks


def synthetic_checks():
    """Only planted arrays; no real prices, signals or economic outcomes."""
    def fresh():
        a = np.full((1, 1440), 100.)
        return SimpleNamespace(o=a.copy(), h=a.copy(), l=a.copy(), c=a.copy(),
                               ts=np.array([np.datetime64("2020-01-02")]))
    def signal(j=540, **extra):
        return dict(day=0, signal_j=j, side=1, stop=2., target=2., exit_j=j + 10, **extra)
    checks = {}
    g = fresh(); g.o[0, 541] = 110.; g.h[0, 541] = 111.; g.l[0, 541] = 109.; g.c[0, 541] = 110.
    t, _ = replay(pd.DataFrame([signal()]), grid=g)
    checks["whole_minute_delay"] = bool(t.j0.iloc[0] == 542 and t.entry.iloc[0] == 100.)
    g = fresh(); g.l[0, 542] = 97.
    t, _ = replay(pd.DataFrame([signal()]), grid=g)
    checks["entry_bar_stop_and_cash"] = bool(t.kind.iloc[0] == 0 and t.j1.iloc[0] == 542 and np.isclose(t.net.iloc[0], -57.25) and np.isclose(t.net_mnq.iloc[0], -6.24))
    g = fresh(); g.o[0, 543] = 95.; g.h[0, 543] = 96.; g.l[0, 543] = 94.; g.c[0, 543] = 95.
    t, _ = replay(pd.DataFrame([signal()]), grid=g)
    checks["worse_gap_stop"] = bool(t.exit.iloc[0] == 95. and t.kind.iloc[0] == 0)
    g = fresh(); g.h[0, 542] = 102.5; g.h[0, 543] = 103.
    t, _ = replay(pd.DataFrame([signal()]), grid=g)
    checks["target_through_one_point"] = bool(t.j1.iloc[0] == 543 and t.exit.iloc[0] == 102. and t.kind.iloc[0] == 1)
    marks = minute_close_marks(g, t); micro = minute_close_marks(g, t, instrument="MNQ")
    checks["close_marks_reconcile"] = bool(np.isclose(marks[0, -1], t.net.sum()) and np.isclose(micro[0, -1], t.net_mnq.sum()))
    g = fresh(); g.h[0, 542] = 105.; g.l[0, 542] = 97.
    t, _ = replay(pd.DataFrame([signal()]), grid=g)
    checks["shared_both_hit_stop_path"] = bool(t.kind.iloc[0] == 0)
    g = fresh(); g.h[0, 542] = 103.; g.l[0, 542] = 95.
    t, _ = replay(pd.DataFrame([signal()]), grid=g)
    checks["shared_both_hit_target_path"] = bool(t.kind.iloc[0] == 1)
    g = fresh()
    s = pd.DataFrame([signal(540), signal(545), signal(550), signal(555)])
    t, ct = replay(s, grid=g)
    checks["invested_and_same_close_suppressed"] = bool(t.signal_j.tolist() == [540, 555] and ct["suppressed_invested_or_same_close"] == 2)
    g = fresh(); g.o[0, 542] = np.nan
    t, ct = replay(pd.DataFrame([signal()]), grid=g)
    checks["missing_scheduled_open_not_retimed"] = bool(t.empty and ct["missing_scheduled_entry"] == 1)
    g = fresh()
    for k in OHLC: getattr(g, k)[0, 543] = np.nan
    t, ct = replay(pd.DataFrame([signal()]), grid=g)
    checks["unknown_held_path_retained"] = bool(len(t) == 1 and t.invalid_held_ohlc_minutes.iloc[0] == 1 and ct["unknown_held_path_trades"] == 1)
    try:
        metrics_summary(t, [pd.Timestamp("2020-01-02")])
    except ValueError:
        checks["unknown_path_blocks_metrics_advancement"] = True
    else:
        checks["unknown_path_blocks_metrics_advancement"] = False
    g = fresh()
    anchored = dict(day=0, signal_j=540, side=1, stop_price=98., max_stop=3., target_R=.3, exit_j=552)
    t, _ = replay(pd.DataFrame([anchored]), grid=g)
    checks["anchored_quote_risk_and_rounded_target"] = bool(t.stop.iloc[0] == 2. and t.target.iloc[0] == .75 and t.stop_price.iloc[0] == 98.)
    g = fresh(); g.o[0, 542] = 97.; g.h[0, 542] = 98.; g.l[0, 542] = 96.; g.c[0, 542] = 97.
    t, ct = replay(pd.DataFrame([anchored]), grid=g)
    checks["wrong_side_anchored_stop_skips"] = bool(t.empty and ct["quote_stop_wrong_side"] == 1)
    g = fresh(); g.o[0, 542] = 102.; g.h[0, 542] = 103.; g.l[0, 542] = 101.; g.c[0, 542] = 102.
    t, ct = replay(pd.DataFrame([anchored]), grid=g)
    checks["quote_risk_cap_skips"] = bool(t.empty and ct["quote_risk_above_maximum"] == 1)
    g = fresh()
    for key in OHLC: getattr(g,key)[0,549:551]=np.nan
    t,ct=replay(pd.DataFrame([dict(day=0,signal_j=540,side=1,stop=2.,target=10.,exit_j=550)]),grid=g)
    checks['missing_exit_tail_not_hidden']=bool(t.time_exit_rewound.iloc[0] and t.unobserved_held_minutes.iloc[0]==2 and not t.path_valid.iloc[0])
    empty=pd.DataFrame(columns=['day','signal_j','side','stop','target','exit_j'])
    t,_=replay(empty,grid=fresh())
    checks['zero_trade_stress_summary']=metrics_summary(t,[pd.Timestamp('2020-01-02')],column='stop_first_net')['total']==0
    if not all(checks.values()): raise AssertionError(checks)
    return checks


if __name__ == "__main__":
    import json
    print(json.dumps({"synthetic_only": True, "checks": synthetic_checks()}, indent=2))
