"""Frozen OB v2 / common-warm-up Bridge replay (preregistration 7d7714b).

Usage: configured-python analysis/codex_ob_v2_replay.py --phase design
Recent/full phases require an explicit --authorize-recent CLI flag. The public
functions leave phase authorization to the caller. No input cache is modified.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import pickle
from pathlib import Path
import sys
from types import SimpleNamespace
import warnings

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "analysis"))
from grid24 import jof
from candidates24 import _continuous_adx
from bridge_onb_orb_test import rth_atr
from replica import is_early_close

PV, TICK, COMMISSION, THROUGH = 20.0, 0.25, 7.25, 1.0
OUT = ROOT / "analysis/outputs/codex_ob_v2_plan_test/replay"
WARMUP = ROOT / "agents/codex/inputs/ob_v2_bench/NQ_1min_2017.csv"
WARMUP_HASH = "b4005cfcd7ea021174b1eb14534b473ee5d2e4014319f991e9c34b0619bfde8d"
COLS = ["day", "date", "side", "j0", "j1", "entry", "exit", "kind", "slips", "net",
        "raw_entry", "raw_exit", "gross", "cost", "commission", "entry_fills", "slip_fills",
        "trade_stop_pts", "stop_pts", "signal_j", "signal_close", "stop_price", "target_price",
        "atr15", "atr100", "ratio", "earlyclose", "attempt", "flat_unexecutable",
        "entry_delay_minutes", "exit_label"]


def build_context():
    """Return original cached grid and prior-only features with 2017 RTH seed.

    All public array rows and ledger day numbers keep the original g24 indices.
    Only temporary copies receive the warm-up export; the pickle is read-only.
    """
    digest = hashlib.sha256(WARMUP.read_bytes()).hexdigest()
    if digest != WARMUP_HASH:
        raise ValueError(f"Warm-up input hash differs from preregistration: {digest}")
    with (ROOT / "scratch_data/g24.pkl").open("rb") as f:
        g = pickle.load(f)
    data = pd.read_csv(WARMUP)
    first = pd.to_datetime(str(int(data.date.min())))
    prefix = pd.date_range(first, pd.Timestamp(g.ts[0]) - pd.Timedelta(days=1), freq="D")
    offset = len(prefix)
    warm = copy.copy(g)
    warm.ts = np.r_[prefix.to_numpy(), g.ts]
    warm.dates = pd.DatetimeIndex(warm.ts).strftime("%Y%m%d").astype(int).to_numpy()
    warm.D = len(warm.ts)
    rows = np.searchsorted(warm.dates, data.date.to_numpy())
    cols = jof(data.time.to_numpy())
    for full, short in (("open", "o"), ("high", "h"), ("low", "l"), ("close", "c"), ("volume", "v")):
        a = np.full((warm.D, 1440), np.nan)
        a[offset:] = getattr(g, short)
        a[rows, cols] = data[full].to_numpy(float)
        setattr(warm, short, a)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        full_b = warm.bars(15)
        atr15 = rth_atr(warm, 15)
        atr100 = rth_atr(warm, 100)
        adx = _continuous_adx(full_b, 16)
    rr = pd.Series((full_b["h"] - full_b["l"]).ravel())
    have = rr.notna()
    av = pd.Series(np.nan, index=rr.index)
    av[have] = rr[have].rolling(20).mean().shift(1).to_numpy()
    avgr = av.to_numpy().reshape(full_b["c"].shape)
    # OR reference is updated after testing today's range, as in the source.
    band = np.zeros(warm.D, bool)
    bias = np.zeros(warm.D, np.int8)
    on_high = np.full(warm.D, np.nan)
    on_low = np.full(warm.D, np.nan)
    or_ref = np.full(warm.D, np.nan)
    ema, count = 0.0, 0
    i830, i845 = int(jof(830) // 15), int(jof(845) // 15)
    for d in range(warm.D):
        if np.isnan(full_b["c"][d, i845]):
            continue
        hi, lo = full_b["h"][d, i845], full_b["l"][d, i845]
        or_ref[d] = ema if ema else np.nan
        band[d] = ema == 0 or (hi - lo) <= 2.0 * ema
        ema = hi - lo if ema == 0 else ema + 2.0 / 21.0 * (hi - lo - ema)
        count += 1
        if count < 20:
            band[d] = True
        hs, ls = full_b["h"][d, :i830 + 1], full_b["l"][d, :i830 + 1]
        if np.isnan(hs).all():
            continue
        on_high[d], on_low[d] = np.nanmax(hs), np.nanmin(ls)
        if on_high[d] > on_low[d]:
            loc = (full_b["o"][d, i845] - on_low[d]) / (on_high[d] - on_low[d])
            bias[d] = 1 if loc >= .67 else (-1 if loc <= .33 else 0)
    ctx = {"b": {k: (v[offset:].copy() if k != "j" else v.copy()) for k, v in full_b.items()},
           "adx": adx[offset:].copy(), "avgr": avgr[offset:].copy(),
           "atr15": atr15[offset:].copy(), "atr100": atr100[offset:].copy(),
           "band": band[offset:].copy(), "bias": bias[offset:].copy(),
           "on_high": on_high[offset:].copy(), "on_low": on_low[offset:].copy(),
           "or_ref": or_ref[offset:].copy()}
    ctx["ratio"] = ctx["atr15"] / ctx["atr100"]
    ts = pd.DatetimeIndex(g.ts)
    trading = np.isin(np.arange(g.D), g.trading)
    warm_ok = np.isfinite(ctx["atr100"]) & (ctx["atr100"] > 0) & np.isfinite(ctx["atr15"]) & (ctx["atr15"] > 0)
    early = np.array([is_early_close(x) for x in ts], dtype=bool)
    ctx["daily_metadata"] = pd.DataFrame(dict(day=np.arange(g.D), date=ts, trading=trading,
        atr15=ctx["atr15"], atr100=ctx["atr100"], ratio=ctx["ratio"], warmup_ok=warm_ok,
        ratio_ok=(ctx["ratio"] >= .6) & (ctx["ratio"] <= 1.2),
        eligible=trading & warm_ok & (ts.year >= 2018), earlyclose=early,
        stop_pts=.30 * ctx["atr15"], bias=ctx["bias"], or_band_ok=ctx["band"],
        or_high=ctx["b"]["h"][:, i845], or_low=ctx["b"]["l"][:, i845],
        on_high=ctx["on_high"], on_low=ctx["on_low"], or_reference=ctx["or_ref"]))
    ctx["input_audit"] = dict(warmup_sha256=digest, warmup_rows=len(data),
        warmup_dates=int(data.date.nunique()), warmup_first=str(int(data.date.min())),
        warmup_last=str(int(data.date.max())), added_prefix_calendar_rows=offset,
        cached_first=str(ts[0].date()), cached_last=str(ts[-1].date()),
        cached_calendar_rows=g.D, cached_trading_rows=len(g.trading),
        native_multicharts_parity_verified=False,
        data_assumption="User assumes matching data; native platform parity not established.")
    return g, ctx


def _in_period(year, period):
    if period == "design":
        return 2018 <= year <= 2022
    if period == "recent":
        return year >= 2023
    if period == "full":
        return year >= 2018
    raise ValueError("period must be design, recent or full")


def _replay_day(g, ctx, d, scheduled=None):
    """Shared one-position replay; scheduled events bypass signal-selection gates."""
    b, adx, avgr = ctx["b"], ctx["adx"], ctx["avgr"]
    meta = ctx["daily_metadata"].iloc[d]
    sp = float(meta.stop_pts)
    early = bool(meta.earlyclose)
    flat_j = int(jof(1130 if early else 1430))
    last_j = int(jof(1100 if early else 1200))
    diag = dict(day=int(d), date=str(pd.Timestamp(g.ts[d]).date()), earlyclose=early,
                attempts=0, filled=0, scheduled_collisions=0, unfilled=0,
                delayed_entries=0, delayed_flats=0, flat_unexecutable=0,
                partial_native_bars=0, both_exit_minute=0, entry_minute_gap_stop=0)
    out, pos, pending, flat_pending = [], None, None, False
    schedule = {} if scheduled is None else {int(x["signal_j"]): x for x in scheduled}

    def finish(m, raw_exit, kind, label, invalid=False):
        nonlocal pos, flat_pending
        side = pos["side"]
        exit_price = raw_exit if kind == 1 else raw_exit - side * TICK
        gross = (raw_exit - pos["raw_entry"]) * side * PV
        net = (exit_price - pos["entry"]) * side * PV - COMMISSION
        out.append(dict(day=d, date=pd.Timestamp(g.ts[d]), side=side, j0=pos["j0"], j1=int(m),
            entry=pos["entry"], exit=exit_price, kind=kind, slips=0, net=net,
            raw_entry=pos["raw_entry"], raw_exit=raw_exit, gross=gross, cost=gross-net,
            commission=COMMISSION, entry_fills=1, slip_fills=1 + int(kind != 1),
            trade_stop_pts=pos["stop_pts"], stop_pts=pos["stop_pts"],
            signal_j=pos["signal_j"], signal_close=pos["signal_close"],
            stop_price=pos["stop"], target_price=pos["target"], atr15=float(meta.atr15),
            atr100=float(meta.atr100), ratio=float(meta.ratio), earlyclose=early,
            attempt=pos["attempt"], flat_unexecutable=invalid,
            entry_delay_minutes=pos["j0"]-pos["signal_j"]-1, exit_label=label))
        pos, flat_pending = None, False

    # Native bar close decisions are evaluated even if the exact boundary minute
    # is absent: Grid24.bars supplies the last observed close of that native bar.
    for i in range(int(jof(900) // 15), int(jof(1500) // 15) + 1):
        j = i * 15
        minutes = np.flatnonzero(np.isfinite(g.o[d, j-14:j+1])) + j - 14
        if not len(minutes):
            continue
        first = int(minutes[0])
        if np.isnan(g.c[d, j]):
            diag["partial_native_bars"] += 1
        if pending is not None:
            s, anchor = int(pending["side"]), float(pending["signal_close"])
            dist = float(pending.get("stop_pts", sp))
            raw_entry = float(g.o[d, first])
            pos = dict(side=s, raw_entry=raw_entry, entry=raw_entry+s*TICK,
                stop=anchor-s*dist, target=anchor+s*3.0*dist, stop_pts=dist,
                j0=first, signal_j=int(pending["signal_j"]), signal_close=anchor,
                attempt=int(pending["attempt"]))
            diag["filled"] += 1
            if first != pos["signal_j"] + 1:
                diag["delayed_entries"] += 1
            pending = None
        if pos is not None and flat_pending:
            if first != flat_j + 1:
                diag["delayed_flats"] += 1
            finish(first, float(g.o[d, first]), 2, "scheduled_flat")
        if pos is not None:
            s = pos["side"]
            for m in minutes:
                m = int(m)
                if m < pos["j0"]:
                    continue
                stop_hit = g.l[d, m] <= pos["stop"] if s > 0 else g.h[d, m] >= pos["stop"]
                target_hit = g.h[d, m] >= pos["target"] + THROUGH if s > 0 else g.l[d, m] <= pos["target"] - THROUGH
                if stop_hit and target_hit:
                    diag["both_exit_minute"] += 1
                if stop_hit:
                    # Adverse opening gaps apply on the entry minute, too.
                    raw_exit = min(g.o[d, m], pos["stop"]) if s > 0 else max(g.o[d, m], pos["stop"])
                    if m == pos["j0"] and raw_exit != pos["stop"]:
                        diag["entry_minute_gap_stop"] += 1
                    finish(m, float(raw_exit), 0, "stop")
                    break
                if target_hit:
                    raw_exit = max(g.o[d, m], pos["target"]) if s > 0 else min(g.o[d, m], pos["target"])
                    finish(m, float(raw_exit), 1, "target")
                    break
        c = b["c"][d, i]
        if np.isnan(c):
            continue
        if scheduled is not None:
            event = schedule.get(j)
            if event is not None:
                diag["attempts"] += 1
                if pos is not None or pending is not None:
                    diag["scheduled_collisions"] += 1
                else:
                    pending = {**event, "attempt": diag["attempts"]}
        elif pos is None and pending is None and diag["attempts"] < 4:
            time_ok = j < last_j if early else j <= last_j
            if time_ok and adx[d, i] >= 20:
                avg = avgr[d, i]
                range_ok = np.isnan(avg) or avg == 0 or b["h"][d, i] - b["l"][d, i] <= 2.5 * avg
                brk = 1 if c > meta.or_high else (-1 if c < meta.or_low else 0)
                if brk == int(meta.bias) and brk != 0 and range_ok:
                    diag["attempts"] += 1
                    pending = dict(side=brk, signal_close=float(c), signal_j=j,
                                   stop_pts=sp, attempt=diag["attempts"])
        if pos is not None and j >= flat_j:
            flat_pending = True
    if pending is not None:
        diag["unfilled"] += 1
    if pos is not None:
        # Explicit invalid-model fallback, never an ordinary scheduled fill.
        # Its conservative terminal mark lets all risk remain visible; any such
        # event is flagged for review and blocks a native-parity claim.
        seen = np.flatnonzero(np.isfinite(g.c[d, :int(jof(1500))+1]))
        m = int(seen[-1])
        diag["flat_unexecutable"] += 1
        finish(m, float(g.c[d, m]), 2, "INVALID_terminal_mark_no_next_bar", True)
    return out, diag


def run(g, ctx, filtered=True, period="design", rand_side_seed=None, random_time_seed=None):
    """Replay one frozen ledger; no return-dependent parameter selection."""
    if rand_side_seed is not None or random_time_seed is not None:
        base = run(g, ctx, filtered=filtered, period=period)
        return replay_events(g, ctx, base, rand_side_seed=rand_side_seed, random_time_seed=random_time_seed)
    rows, audit = [], []
    for m in ctx["daily_metadata"].itertuples(index=False):
        if not _in_period(pd.Timestamp(m.date).year, period):
            continue
        if not m.eligible or not m.or_band_ok or m.bias == 0 or (filtered and not m.ratio_ok):
            continue
        trades, diag = _replay_day(g, ctx, int(m.day))
        rows.extend(trades)
        audit.append(diag)
    out = pd.DataFrame(rows, columns=COLS)
    # Keep attrs JSON-compatible: a DataFrame in attrs breaks pandas concat/
    # groupby metadata comparisons when it asks whether attrs are equal.
    out.attrs["diagnostics"] = audit
    out.attrs["rule"] = "OBV2" if filtered else "BRIDGE100"
    out.attrs["period"] = period
    return out


def replay_events(g, ctx, base_events, rand_side_seed=None, random_time_seed=None):
    """Diagnostic nulls on fixed observed event days/count and stop distances.

    Entry-time null draws distinct native signal bars uniformly on each event
    day (09:00..12:00, or09:00..10:45 early). It preserves original event sides,
    anchors each new bracket on that bar's close and bypasses entry filters.
    Event ordering is maintained by assigning the sorted times to the original
    event order. One-position collisions reduce effective count and are logged.
    With neither seed this exactly replays the base ledger's event schedule.
    """
    sides = np.random.default_rng(rand_side_seed) if rand_side_seed is not None else None
    times = np.random.default_rng(random_time_seed) if random_time_seed is not None else None
    rows, audits = [], []
    for d, group in base_events.sort_values(["day", "signal_j"]).groupby("day", sort=True):
        d = int(d)
        events = group.to_dict("records")
        if times is not None:
            early = bool(ctx["daily_metadata"].iloc[d].earlyclose)
            candidates = np.arange(int(jof(900)), int(jof(1045 if early else 1200)) + 1, 15)
            candidates = candidates[np.isfinite(ctx["b"]["c"][d, candidates // 15])]
            count = min(len(events), len(candidates))
            selected = np.sort(times.choice(candidates, size=count, replace=False))
            events = events[:count]
            for event, j in zip(events, selected):
                event["signal_j"] = int(j)
                event["signal_close"] = float(ctx["b"]["c"][d, int(j) // 15])
        for event in events:
            event["stop_pts"] = float(event["trade_stop_pts"])
            if sides is not None:
                event["side"] = int(sides.choice([-1, 1]))
        trades, diag = _replay_day(g, ctx, d, scheduled=events)
        diag["original_events"] = len(group)
        diag["time_slots_unavailable"] = len(group)-len(events)
        rows.extend(trades)
        audits.append(diag)
    out = pd.DataFrame(rows, columns=COLS)
    out.attrs["diagnostics"] = audits
    out.attrs["original_events"] = len(base_events)
    return out


def cheap_summary(t):
    if len(t) == 0:
        return dict(n=0, pass_gate=False)
    yearly = t.groupby(t.date.dt.year).net.sum().reindex(range(2018, 2023), fill_value=0)
    negative = -float(t.loc[t.net < 0, "net"].sum())
    pf = float(t.loc[t.net > 0, "net"].sum()) / negative if negative else float("inf")
    checks = dict(at_least_100=len(t) >= 100, total_net_positive=float(t.net.sum()) > 0,
        gross_1_5x_costs=float(t.gross.mean()) >= 1.5 * float(t.cost.mean()),
        pf_1_15=pf >= 1.15, three_positive_years=int((yearly > 0).sum()) >= 3)
    return dict(n=len(t), total_net=float(t.net.sum()), mean_net=float(t.net.mean()),
        mean_gross=float(t.gross.mean()), mean_cost=float(t.cost.mean()), pf=pf,
        positive_years=int((yearly > 0).sum()), year_net={str(k): float(v) for k, v in yearly.items()},
        sides={str(s): dict(n=len(z), mean_net=float(z.net.mean()), total_net=float(z.net.sum()))
               for s, z in t.groupby("side")}, checks=checks, pass_gate=all(checks.values()))


def execution_selfcheck():
    """Synthetic checks for material execution branches; no historical rerun."""
    def scenario(points):
        g = SimpleNamespace(ts=np.array([np.datetime64("2020-01-02")]))
        for key in ("o", "h", "l", "c"):
            setattr(g, key, np.full((1, 1440), np.nan))
        b = {key: np.full((1, 96), np.nan) for key in ("o", "h", "l", "c")}
        for minute, o, h, l, c in [(540, 100, 100, 100, 100), *points]:
            for key, value in zip(("o", "h", "l", "c"), (o, h, l, c)):
                getattr(g, key)[0, minute] = value
                b[key][0, (minute+14)//15] = value
        metadata = pd.DataFrame([dict(stop_pts=10., earlyclose=False, atr15=100/3,
            atr100=100/3, ratio=1., bias=1, or_high=99., or_low=90.)])
        ctx = dict(b=b, adx=np.full((1, 96), 25.), avgr=np.full((1, 96), 10.), daily_metadata=metadata)
        return _replay_day(g, ctx, 0, scheduled=[dict(signal_j=540, signal_close=100., side=1, stop_pts=10.)])

    cases = {}
    trades, audit = scenario([(541, 80, 85, 79, 82)])
    cases["entry_minute_adverse_gap_stop"] = trades[0]["raw_exit"] == 80 and trades[0]["net"] == -17.25 and audit["entry_minute_gap_stop"] == 1
    trades, audit = scenario([(541, 100, 130, 99, 129), (542, 129, 131, 128, 130)])
    cases["target_touch_waits_for_one_point_through"] = trades[0]["j1"] == 542 and trades[0]["raw_exit"] == 130
    trades, audit = scenario([(541, 100, 131, 89, 110)])
    cases["stop_first_when_both_possible"] = trades[0]["kind"] == 0 and trades[0]["raw_exit"] == 90 and audit["both_exit_minute"] == 1
    trades, audit = scenario([(541, 132, 133, 131, 132)])
    cases["entry_minute_target_open_improvement"] = trades[0]["kind"] == 1 and trades[0]["raw_exit"] == 132
    trades, audit = scenario([(541, 100, 101, 99, 100), (870, 100, 101, 99, 100), (871, 102, 103, 101, 102)])
    cases["flat_decision_then_next_bar_open"] = trades[0]["j1"] == 871 and trades[0]["raw_exit"] == 102 and not trades[0]["flat_unexecutable"]
    trades, audit = scenario([(541, 100, 101, 99, 100), (870, 100, 101, 99, 100)])
    cases["missing_flat_open_flagged_invalid"] = trades[0]["flat_unexecutable"] and audit["flat_unexecutable"] == 1
    if not all(cases.values()):
        raise AssertionError(cases)
    return cases


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--phase", choices=("design", "recent", "full"), default="design")
    parser.add_argument("--authorize-recent", action="store_true")
    parser.add_argument("--selfcheck", action="store_true", help="Synthetic execution checks only; no historical replay")
    args = parser.parse_args()
    if args.selfcheck:
        checks = execution_selfcheck()
        OUT.mkdir(parents=True, exist_ok=True)
        (OUT / "execution_selfcheck.json").write_text(json.dumps(checks, indent=2)+"\n")
        print(json.dumps(checks, indent=2))
        return
    if args.phase != "design" and not args.authorize_recent:
        parser.error("Recent returns require root authorization and --authorize-recent")
    OUT.mkdir(parents=True, exist_ok=True)
    g, ctx = build_context()
    ctx["daily_metadata"].to_csv(OUT / "daily_metadata.csv", index=False)
    pd.DataFrame({"day": g.trading, "date": pd.DatetimeIndex(g.ts[g.trading])}).to_csv(
        OUT / "trading_days.csv", index=False)
    (OUT / "input_audit.json").write_text(json.dumps(ctx["input_audit"], indent=2)+"\n")
    results = {}
    for name, filtered in (("OBV2", True), ("BRIDGE100", False)):
        t = run(g, ctx, filtered=filtered, period=args.phase)
        t.to_csv(OUT / f"{name}_{args.phase}_trades.csv", index=False)
        pd.DataFrame(t.attrs["diagnostics"]).to_csv(OUT / f"{name}_{args.phase}_execution_audit.csv", index=False)
        if args.phase == "recent":
            # Concatenate the already frozen design ledger; do not rerun past
            # returns merely to produce a full-sample account input file.
            design = pd.read_csv(OUT / f"{name}_design_trades.csv", parse_dates=["date"])
            recent_plain = t.copy()
            recent_plain.attrs = {}
            pd.concat([design, recent_plain], ignore_index=True).to_csv(
                OUT / f"{name}_full_trades.csv", index=False)
            design_audit = pd.read_csv(OUT / f"{name}_design_execution_audit.csv")
            pd.concat([design_audit, pd.DataFrame(t.attrs["diagnostics"])], ignore_index=True).to_csv(
                OUT / f"{name}_full_execution_audit.csv", index=False)
        if args.phase == "design":
            results[name] = cheap_summary(t)
        else:
            results[name] = dict(n=len(t), total_net=float(t.net.sum()), mean_net=float(t.net.mean()))
    (OUT / f"{args.phase}_summary.json").write_text(json.dumps(results, indent=2)+"\n")
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
