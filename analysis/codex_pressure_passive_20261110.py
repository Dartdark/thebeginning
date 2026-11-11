"""Frozen pressure-event execution extension; import and self-check are outcome-free.

L1/L2 are resting-limit hypotheses on the original frozen RESID2 event file;
MARKET is an unselectable, independently executed control. Real outcomes require
the exact plan/evidence/code Git commit. No source signal regeneration occurs.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
from types import SimpleNamespace

import numpy as np
import pandas as pd

import codex_pressure_build_20261110_inputs as I
import codex_pressure_build_20261110_replay as E
from codex_s03_calendar import calendar_status

ROOT = Path(__file__).resolve().parents[1]
PLAN = "agents/codex/plans/pressure_passive_20261110.md"
EVIDENCE = "agents/codex/evidence/pressure_passive_20261110.md"
SOURCE_REF = "c852212a"
SOURCE = "analysis/outputs/codex_pressure_build_20261110/batch1_design_qa2/RESID2_signals.csv.gz"
CODE = "analysis/codex_pressure_passive_20261110.py"
OUT = ROOT / "analysis/outputs/codex_pressure_build_20261110/passive_design"
MODELS = ("L1", "L2", "MARKET")
TRADE_COLUMNS = ["day", "date", "signal_j", "j0", "j1", "side", "entry", "exit", "kind",
    "stop", "target", "stop_price", "target_price", "gross", "pnl", "commission", "slippage",
    "net", "net_mnq", "net_entry_tick_stress", "net_mnq_entry_tick_stress", "qty",
    "unobserved_held_minutes", "invalid_held_ohlc_minutes", "unknown_exposure", "path_valid"]
ORDER_COLUMNS = ["model", "day", "date", "signal_j", "activation_j", "ttl_last_j", "side",
                 "limit_price", "stop_price", "risk", "target_price", "status", "release_j", "fill_j", "exit_j"]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write(path, data):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(data, str): data = data.encode()
    if path.exists():
        if path.read_bytes() != data: raise ValueError(f"Refuse different artifact overwrite: {path}")
    else:
        with path.open("xb") as stream: stream.write(data)


def dump(path, value):
    write(path, json.dumps(value, indent=2, default=str, allow_nan=True) + "\n")


def valid_bar(grid, d, j):
    if not 0 <= j < grid.o.shape[1]: return False
    o, h, l, c = [getattr(grid, k)[d, j] for k in ("o", "h", "l", "c")]
    return bool(np.isfinite([o, h, l, c]).all() and l <= min(o, c) <= max(o, c) <= h)


def _exit(grid, d, fill_j, last_j, side, stop, target, certified_fillbar_target=True,
          entry_at_open=False):
    """Stop-first with entry-time-aware target knowledge.

    A MARKET entry occurs at the known minute open, so its later high/low through
    target is usable even in that minute. An intraminute passive fill requires a
    post-fill closing trade through target instead. Both assume an immediately
    active bracket. The no-fillbar-target stress disables both first-minute cases.
    """
    for j in range(fill_j, last_j + 1):
        if not valid_bar(grid, d, j):
            return dict(unknown=True, at=j, j1=np.nan, exit=np.nan, kind=-1)
        o, h, l, c = [float(getattr(grid, k)[d, j]) for k in ("o", "h", "l", "c")]
        gap = o <= stop if side > 0 else o >= stop
        stop_hit = l <= stop if side > 0 else h >= stop
        target_hit = h >= target + 1. if side > 0 else l <= target - 1.
        if gap:
            return dict(unknown=False, at=j, j1=j, exit=o, kind=0)
        if stop_hit:
            return dict(unknown=False, at=j, j1=j, exit=stop, kind=0)
        certified = c >= target + 1. if side > 0 else c <= target - 1.
        first_minute_target = target_hit if entry_at_open else certified
        if (j > fill_j and target_hit) or (j == fill_j and certified_fillbar_target and first_minute_target):
            return dict(unknown=False, at=j, j1=j, exit=target, kind=1)
        if j == last_j:
            return dict(unknown=False, at=j, j1=j, exit=c, kind=2)
    raise AssertionError("Unreachable exit path")


def _trade(grid, model, d, decision, side, fill_j, entry, stop, target, outcome):
    market = model == "MARKET"
    unknown = bool(outcome["unknown"])
    exit_price, kind = outcome["exit"], int(outcome["kind"])
    gross = np.nan if unknown else float((exit_price - entry) * side * 20.)
    exit_ticks = np.nan if unknown else int(kind != 1)
    entry_ticks = int(market)
    slip = np.nan if unknown else 5. * (entry_ticks + exit_ticks)
    return dict(day=d, date=pd.Timestamp(grid.ts[d]), signal_j=decision, j0=fill_j, j1=outcome["j1"],
        side=side, entry=entry, exit=exit_price, kind=kind, stop=side * (entry - stop),
        target=side * (target - entry), stop_price=stop, target_price=target,
        gross=gross, pnl=gross, commission=7.25, slippage=slip,
        net=gross - 7.25 - slip,
        net_mnq=gross / 10. - 1.24 - slip / 10.,
        net_entry_tick_stress=gross - 7.25 - 5. * (1 + exit_ticks),
        net_mnq_entry_tick_stress=gross / 10. - 1.24 - .5 * (1 + exit_ticks), qty=1.,
        unobserved_held_minutes=int(unknown), invalid_held_ohlc_minutes=int(unknown),
        unknown_exposure=unknown, path_valid=not unknown)


def replay(signals, grid, model, max_submitted=4, *, certified_fillbar_target=True):
    """Use frozen events independently for each model; no selection on future fills.

    A viable decision reserves the only slot immediately and counts as submitted,
    including eventual activation cancellation or TTL expiry. Inactive latency
    has no live order, so only active-pending and held OHLC are exposure-relevant.
    Any unknown exposure halts further submissions that day and blocks advancement.
    """
    if model not in MODELS: raise ValueError(model)
    required = {"day", "signal_j", "side", "stop_price", "max_stop"}
    if not required.issubset(signals.columns): raise ValueError(f"Missing fields: {required - set(signals.columns)}")
    if signals[list(required)].isna().any().any(): raise ValueError("NaN source event")
    if signals.duplicated(["day", "signal_j"]).any(): raise ValueError("Duplicate source decision")
    orders, trades = [], []
    counts = dict(source_events=len(signals), submitted=0, fills=0, ttl_expired=0,
        activation_not_passive=0, decision_risk_rejected=0, activation_risk_rejected=0,
        suppressed_reserved_or_same_close=0, suppressed_daily_cap=0,
        unknown_active_pending=0, unknown_held=0, days_halted_unknown=0,
        suppressed_unknown_day=0, model=model, certified_fillbar_target=bool(certified_fillbar_target))
    for day, group in signals.sort_values(["day", "signal_j"], kind="stable").groupby("day", sort=True):
        d = int(day)
        if d != day or not 0 <= d < len(grid.ts): raise ValueError("Invalid source day")
        release, submitted, halted = -1, 0, False
        for r in group.itertuples(index=False):
            t, side = int(r.signal_j), int(r.side)
            if t != r.signal_j or side != r.side or side not in (-1, 1): raise ValueError("Invalid minute or side")
            active, expires = t + 6, t + 10
            if t < 0 or expires >= grid.o.shape[1] or active > 895: raise ValueError("Invalid activation window")
            if hasattr(r, "date") and pd.Timestamp(r.date).normalize() != pd.Timestamp(grid.ts[d]).normalize():
                raise ValueError("Source grid day/date mapping changed")
            if halted:
                counts["suppressed_unknown_day"] += 1; continue
            if t <= release:
                counts["suppressed_reserved_or_same_close"] += 1; continue
            if submitted >= max_submitted:
                counts["suppressed_daily_cap"] += 1; continue
            close = float(grid.c[d, t]); stop = float(r.stop_price)
            if not np.isfinite([close, stop, r.max_stop]).all() or r.max_stop <= 0:
                raise ValueError("Invalid frozen source state")
            if model == "L1": q = close - side * .25
            elif model == "L2":
                midpoint = (close + stop) / 2.
                q = np.floor(midpoint * 4.) / 4. if side > 0 else np.ceil(midpoint * 4.) / 4.
            else: q = np.nan
            risk = side * (q - stop) if model != "MARKET" else np.nan
            target = q + side * (np.ceil(.3 * risk * 4.) / 4.) if model != "MARKET" else np.nan
            order = dict(model=model, day=d, date=pd.Timestamp(grid.ts[d]), signal_j=t, activation_j=active,
                ttl_last_j=expires, side=side, limit_price=q, stop_price=stop, risk=risk,
                target_price=target, status=None, release_j=None, fill_j=np.nan, exit_j=np.nan)
            if model != "MARKET" and (risk <= 0 or risk > r.max_stop):
                counts["decision_risk_rejected"] += 1
                order.update(status="DECISION_RISK_REJECTED", release_j=t); orders.append(order); continue
            submitted += 1; counts["submitted"] += 1
            if not np.isfinite(grid.o[d, active]):
                order.update(status="UNKNOWN_ACTIVATION", release_j=active)
                counts["unknown_active_pending"] += 1; halted = True
                orders.append(order); continue
            activation_open = float(grid.o[d, active])
            if model == "MARKET":
                risk = side * (activation_open - stop)
                if risk <= 0 or risk > r.max_stop:
                    counts["activation_risk_rejected"] += 1
                    release = active; order.update(status="ACTIVATION_RISK_REJECTED", release_j=release)
                    orders.append(order); continue
                fill_j, entry = active, activation_open
                target = entry + side * (np.ceil(.3 * risk * 4.) / 4.)
                order.update(risk=risk, target_price=target)
            else:
                passive = q < activation_open if side > 0 else q > activation_open
                if not passive:
                    counts["activation_not_passive"] += 1
                    release = active; order.update(status="NOT_PASSIVE_CANCELLED", release_j=release)
                    orders.append(order); continue
                fill_j = None
                for j in range(active, expires + 1):
                    if not valid_bar(grid, d, j):
                        order.update(status="UNKNOWN_PENDING", release_j=j)
                        counts["unknown_active_pending"] += 1; halted = True; break
                    hit = grid.l[d, j] <= q - 1. if side > 0 else grid.h[d, j] >= q + 1.
                    if hit:
                        fill_j = j; break
                if halted:
                    orders.append(order); continue
                if fill_j is None:
                    counts["ttl_expired"] += 1
                    release = expires; order.update(status="TTL_EXPIRED", release_j=release)
                    orders.append(order); continue
                entry = float(q)
            counts["fills"] += 1
            last = min(int(fill_j) + 29, 895)
            outcome = _exit(grid, d, int(fill_j), last, side, stop, target,
                            certified_fillbar_target, entry_at_open=model == "MARKET")
            row = _trade(grid, model, d, t, side, int(fill_j), entry, stop, target, outcome)
            trades.append(row)
            order.update(fill_j=fill_j, exit_j=outcome["j1"], release_j=outcome["at"],
                         status="UNKNOWN_HELD" if outcome["unknown"] else "FILLED_CLOSED")
            if outcome["unknown"]:
                counts["unknown_held"] += 1; halted = True
            release = int(outcome["at"]); orders.append(order)
        counts["days_halted_unknown"] += int(halted)
    tf = pd.DataFrame(trades, columns=TRADE_COLUMNS)
    if tf.empty:
        tf["date"] = pd.Series(dtype="datetime64[ns]")
        for col in TRADE_COLUMNS:
            if col != "date": tf[col] = pd.Series(dtype=float)
    of = pd.DataFrame(orders, columns=ORDER_COLUMNS)
    counts["unknown_exposure"] = bool(counts["unknown_active_pending"] or counts["unknown_held"])
    counts["native_queue_verified"] = False
    return tf, of, counts


def bind(prereg):
    if subprocess.check_output(["git", "branch", "--show-current"], cwd=ROOT, text=True).strip() != "codex/work":
        raise ValueError("Research branch required")
    paths = [PLAN, EVIDENCE, CODE, "analysis/codex_pressure_build_20261110_inputs.py",
             "analysis/codex_pressure_build_20261110_replay.py"]
    for path in paths:
        if subprocess.check_output(["git", "show", f"{prereg}:{path}"], cwd=ROOT) != (ROOT / path).read_bytes():
            raise ValueError(f"Unfrozen protocol: {path}")
    original = subprocess.check_output(["git", "show", f"{SOURCE_REF}:{SOURCE}"], cwd=ROOT)
    frozen = subprocess.check_output(["git", "show", f"{prereg}:{SOURCE}"], cwd=ROOT)
    if original != frozen or original != (ROOT / SOURCE).read_bytes():
        raise ValueError("Original frozen source events changed")
    return dict(prereg=prereg, source_commit=subprocess.check_output(["git", "rev-parse", SOURCE_REF], cwd=ROOT, text=True).strip(), source_path=SOURCE,
        source_blob=subprocess.check_output(["git", "rev-parse", f"{SOURCE_REF}:{SOURCE}"], cwd=ROOT, text=True).strip(),
        source_sha256=hashlib.sha256(original).hexdigest(), code={p: sha(ROOT / p) for p in paths},
        dependencies={p: sha(ROOT / p) for p in ["analysis/codex_cash_open_repair.py", "analysis/metrics.py", "analysis/codex_s03_calendar.py", "agents/codex/inputs/bridge_native_2018_22_20261108/transfer_manifest.json"]},
        models=list(MODELS), selectable=["L1", "L2"], unselectable=["MARKET"],
        historical_validation_read=False, new_economic_definitions=3,
        execution="NQ OHLC conditional proxy; 1pointthrough is not native queue acceptance; no rebates; full RT fees; immediate bracket, stopfirst; passive fillbar TP requires closingtrade through target+1, MARKET entry at known open may use its later high/low through target",
        execution_stress="full independent-policy replay with no fillbar target credit for all three models; unselectable",
        missing_policy="unknown activepending/held exposure halts day and blocks all advancement")


def run(prereg, out=None):
    dest = Path(out) if out is not None else OUT
    binding = bind(prereg)
    if (dest / "results.json").exists(): raise ValueError("Results exist; do not overwrite")
    dump(dest / "binding.json", binding)
    minute = I.load_design_native(); grid = I.make_grid(minute)
    dump(dest / "input_audit.json", minute.attrs.get("input_audit", {}))
    signals = pd.read_csv(ROOT / SOURCE, parse_dates=["date"])
    calendar = pd.DatetimeIndex([d for d in pd.to_datetime(grid.ts)
        if calendar_status(d)["kind"] == "normal" and (d.month, d.day) not in ((7, 3), (12, 24))])
    stats, metrics, all_counts = {}, [], {}
    for model in MODELS:
        t, orders, counts = replay(signals, grid, model)
        write(dest / f"{model}_trades.csv", t.to_csv(index=False))
        write(dest / f"{model}_orders.csv", orders.to_csv(index=False))
        all_counts[model] = counts
        strict, strict_orders, strict_counts = replay(signals, grid, model, certified_fillbar_target=False)
        write(dest / f"{model}_no_fillbar_target_trades.csv", strict.to_csv(index=False))
        write(dest / f"{model}_no_fillbar_target_orders.csv", strict_orders.to_csv(index=False))
        all_counts[model + "_NO_FILLBAR_TP"] = strict_counts
        if counts["unknown_exposure"]:
            stats[model] = dict(status="BLOCKED_UNKNOWN_EXPOSURE", counts=counts)
            continue
        summary = E.metrics_summary(t, calendar)
        micro = E.metrics_summary(t, calendar, "net_mnq")
        stress = E.metrics_summary(t, calendar, "net_entry_tick_stress")
        micro_stress = E.metrics_summary(t, calendar, "net_mnq_entry_tick_stress")
        table = E.metrics_table(t, calendar); table["model"] = model; metrics.append(table)
        daily = t.groupby("date").net.sum().reindex(calendar, fill_value=0.)
        write(dest / f"{model}_daily.csv", daily.to_csv(header=["net"]))
        stats[model] = dict(summary=summary, micro=micro, entry_tick_stress=stress,
            micro_entry_tick_stress=micro_stress, counts=counts,
            no_fillbar_target=(dict(status="BLOCKED_UNKNOWN_EXPOSURE", counts=strict_counts) if strict_counts["unknown_exposure"] else
                dict(summary=E.metrics_summary(strict, calendar), micro=E.metrics_summary(strict, calendar, "net_mnq"),
                     entry_tick_stress=E.metrics_summary(strict, calendar, "net_entry_tick_stress"), counts=strict_counts)),
            positive_years=int((daily.groupby(daily.index.year).sum() > 0).sum()),
            long_trades=int((t.side == 1).sum()), short_trades=int((t.side == -1).sum()))
    if metrics: write(dest / "metrics.csv", pd.concat(metrics, ignore_index=True).to_csv(index=False))
    result = dict(prereg=prereg, stats=stats, execution=all_counts,
        any_unknown_exposure=any(c["unknown_exposure"] for c in all_counts.values()),
        selected=None, gate_complete=False, validation_allowed=False, new_economic_definitions=3)
    dump(dest / "results.json", result)
    print(json.dumps(result, indent=2, default=str), flush=True)
    return result


def self_check():
    def fresh():
        a = np.full((1, 1440), 100.)
        return SimpleNamespace(o=a.copy(), h=a.copy(), l=a.copy(), c=a.copy(), ts=np.array([np.datetime64("2020-01-02")]))
    def sig(times=(540,), **kw):
        rows = []
        for t in times:
            r = dict(day=0, signal_j=t, side=1, stop_price=95., max_stop=10.)
            r.update(kw); rows.append(r)
        return pd.DataFrame(rows)
    checks = {}
    g = fresh(); g.l[0, 541:546] = 90.; g.l[0, 546] = 98.75
    t, o, _ = replay(sig(), g, "L1")
    checks["one_full_five_minute_latency"] = bool(t.j0.iloc[0] == 546 and t.entry.iloc[0] == 99.75)
    g = fresh(); g.l[0, 546:551] = 99.
    t, o, _ = replay(sig(), g, "L1")
    checks["one_point_through_not_touch"] = bool(t.empty and o.status.iloc[0] == "TTL_EXPIRED")
    g = fresh(); g.l[0, 550] = 98.75
    t, o, _ = replay(sig(), g, "L1")
    checks["ttl_includes_last_minute"] = bool(t.j0.iloc[0] == 550)
    g = fresh(); g.l[0, 551] = 98.
    t, o, _ = replay(sig(), g, "L1")
    checks["no_fill_after_ttl"] = bool(t.empty and o.status.iloc[0] == "TTL_EXPIRED")
    g = fresh(); g.o[0, 546] = 99.75; g.l[0, 546] = 99.
    t, o, _ = replay(sig(), g, "L1")
    checks["strict_passivity_cancels_equal_open"] = bool(t.empty and o.status.iloc[0] == "NOT_PASSIVE_CANCELLED")
    g = fresh(); g.l[0, 546] = 94.; g.h[0, 546] = 110.
    t, _, _ = replay(sig(), g, "L1")
    checks["fillbar_stop_wins"] = bool(t.kind.iloc[0] == 0 and t.exit.iloc[0] == 95.)
    g = fresh(); g.l[0, 546] = 98.; g.h[0, 546] = 110.; g.h[0, 547] = 110.
    t, _, _ = replay(sig(), g, "L1")
    checks["high_only_fillbar_target_forbidden"] = bool(t.j1.iloc[0] == 547 and t.kind.iloc[0] == 1)
    g = fresh(); g.l[0, 546] = 98.; g.h[0, 546] = 103.; g.c[0, 546] = 102.25
    t, _, _ = replay(sig(), g, "L1")
    strict, _, _ = replay(sig(), g, "L1", certified_fillbar_target=False)
    checks["only_certified_close_fillbar_target"] = bool(t.j1.iloc[0] == 546 and t.kind.iloc[0] == 1 and strict.j1.iloc[0] > 546)
    g = fresh(); g.h[0, 546] = 101.25; g.l[0, 546] = 97.; g.c[0, 546] = 97.75
    t, _, _ = replay(sig(side=-1, stop_price=105.), g, "L1")
    checks["short_certified_close_symmetric"] = bool(t.j1.iloc[0] == 546 and t.kind.iloc[0] == 1)
    g = fresh(); g.l[0, 546] = 98.; g.h[0, 547] = 110.; g.l[0, 547] = 94.
    t, _, _ = replay(sig(), g, "L1")
    checks["later_ambiguity_stopfirst"] = bool(t.kind.iloc[0] == 0)
    g = fresh(); g.l[0, 546] = 98.; g.o[0, 547] = 93.; g.h[0, 547] = 94.; g.l[0, 547] = 92.; g.c[0, 547] = 93.
    t, _, _ = replay(sig(), g, "L1")
    checks["worse_open_gap_stop"] = bool(t.exit.iloc[0] == 93.)
    g = fresh(); g.o[0, 547] = 93.; g.h[0, 547] = 94.; g.l[0, 547] = 92.; g.c[0, 547] = 93.
    t, _, _ = replay(sig(), g, "L1")
    checks["pending_gap_fill_Q_no_improvement_then_worse_stop"] = bool(t.j0.iloc[0] == 547 and t.entry.iloc[0] == 99.75 and t.exit.iloc[0] == 93.)
    g = fresh(); g.l[0, 546] = 98.
    t, _, _ = replay(sig(), g, "L1")
    checks["thirty_minute_time_exit_from_fill"] = bool(t.j1.iloc[0] == 575 and t.kind.iloc[0] == 2)
    g = fresh(); g.l[0, 876] = 98.
    t, _, _ = replay(sig((870,)), g, "L1")
    checks["flat_by_1455"] = bool(t.j1.iloc[0] == 895 and t.kind.iloc[0] == 2)
    g = fresh(); g.l[0, 546:551] = 98.75; g.h[0, 546:551] = 100.25
    t, o, ct = replay(sig((540, 545, 550, 555, 565, 575, 585)), g, "L1")
    checks["pending_reserves_and_sameclose_suppressed"] = bool(ct["suppressed_reserved_or_same_close"] > 0)
    g = fresh()
    t, o, ct = replay(sig((540, 555, 570, 585, 600)), g, "L1")
    checks["cap_counts_unfilled_submissions"] = bool(ct["submitted"] == 4 and ct["suppressed_daily_cap"] == 1)
    g = fresh(); g.o[0, 547] = np.nan
    t, o, ct = replay(sig((540, 555)), g, "L1")
    checks["unknown_pending_blocks_day"] = bool(ct["unknown_exposure"] and ct["suppressed_unknown_day"] == 1 and o.status.iloc[0] == "UNKNOWN_PENDING")
    g = fresh(); g.l[0, 546] = 98.; g.o[0, 547] = np.nan
    t, o, ct = replay(sig(), g, "L1")
    checks["unknown_held_retained"] = bool(len(t) == 1 and bool(t.unknown_exposure.iloc[0]) and pd.isna(t.net.iloc[0]))
    g = fresh()
    t, o, ct = replay(sig(), g, "MARKET")
    checks["market_not_conditioned_on_limit_fills"] = bool(len(t) == 1 and t.j0.iloc[0] == 546)
    g = fresh(); g.h[0, 546] = 103.; g.l[0, 546] = 99.
    t, _, _ = replay(sig(), g, "MARKET")
    strict, _, _ = replay(sig(), g, "MARKET", certified_fillbar_target=False)
    checks["market_open_entry_can_use_later_target_high"] = bool(t.j1.iloc[0] == 546 and t.kind.iloc[0] == 1 and t.exit.iloc[0] == 101.5 and strict.j1.iloc[0] > 546)
    g = fresh(); g.l[0, 546] = 98.; g.h[0, 547] = 110.
    t, _, _ = replay(sig(), g, "L1")
    checks["full_fees_and_entry_cost_stress"] = bool(np.isclose(t.net.iloc[0] - t.net_entry_tick_stress.iloc[0], 5.) and np.isclose(t.net_mnq.iloc[0] - t.net_mnq_entry_tick_stress.iloc[0], .5) and t.commission.iloc[0] == 7.25)
    g = fresh(); g.l[0, 546] = 96.5
    t, o, _ = replay(sig(stop_price=95.25), g, "L2")
    checks["L2_midpoint_long_floor"] = bool(t.entry.iloc[0] == 97.5 and o.limit_price.iloc[0] == 97.5)
    g = fresh(); g.h[0, 546] = 103.5
    t, o, _ = replay(sig(side=-1, stop_price=104.75), g, "L2")
    checks["L2_midpoint_short_ceil"] = bool(t.entry.iloc[0] == 102.5 and o.limit_price.iloc[0] == 102.5)
    if not all(checks.values()): raise AssertionError(checks)
    return checks


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-check", action="store_true")
    parser.add_argument("--prereg")
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    if args.self_check:
        print(json.dumps(dict(synthetic_only=True, checks=self_check()), indent=2))
    elif args.prereg:
        run(args.prereg, args.out)
    else:
        parser.error("Choose --self-check or --prereg")
