"""Frozen OB v2 account comparisons; extends funded_sim without changing rules.

Finite-quantity acceleration: daily q=floor(base*f+1e-9), f clipped [.5,1],
stage all ones, has finitely many monotone q vectors. Precompute their exact
minute-path minima in the original sorted-key summation order, then preserve
funded_sim's account state machine verbatim. No minute interpolation, float32,
rounded risk sizes, approximate minima, changed DLL or payout rules are used.
Every production run checks all five original outputs on fixed paired histories.

Requires the separately passed 2018-22 design gate before loading any candidate
ledger or running historical account comparisons. Synthetic parity is independent.
"""
from __future__ import annotations

import argparse
import gc
import hashlib
import importlib
import json
import pickle
import sys
import time
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pandas as pd
from numba import njit

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "analysis"))
import funded_sim as F
from funded_lab import with_slippage
from portfolio import load_mc, paths

FUNDED_BASE = {"VB_N": 2, "VB_F": 1, "ONB_ML2_MC": ("risk", 400),
               "MON_MC": 1, "EOS": ("risk", 700), "LDF_MC": 2,
               "NFP_MC": ("risk", 500), "MON_BR_MC": 1, "CLS": 2,
               "MOC_MES": 2, "RS_L": 1}
EXTRA_COST = 1.275  # additional dollars per MNQ round trip, challenger only
FIELDS = ("paid", "payouts", "days", "blown", "first")
DEFAULT_OUT = ROOT / "analysis/outputs/codex_ob_v2_plan_test/accounts"
DEFAULT_LEDGERS = DEFAULT_OUT.parent / "replay"


def dump_json(path, value):
    Path(path).write_text(json.dumps(value, indent=2, allow_nan=True, default=str) + "\n")


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def cached_load(path):
    with open(path, "rb") as f:
        return pickle.load(f)


def safe_import(name, scratch):
    """Legacy modules read sys.argv at import; give their existing cache path.

    In particular build_lab's import creates OUT with exist_ok=True; OUT is the
    already-existing scratch directory, never a new research/cache directory.
    No helper __main__ block is executed.
    """
    previous = sys.argv
    try:
        sys.argv = [str(Path(__file__)), str(Path(scratch))]
        return importlib.import_module(name)
    finally:
        sys.argv = previous


def lab_metadata(scratch):
    """Read cache shapes/keys/calendar only, without computing new returns."""
    lab = cached_load(Path(scratch) / "lab.pkl")
    dates = pd.DatetimeIndex(lab.g.ts[lab.tr])
    return dict(days=lab.D, first=str(dates.min().date()), last=str(dates.max().date()),
                existing_keys=sorted(lab.W), missing_current_keys=sorted(set(FUNDED_BASE)-set(lab.W)),
                grid_rows=len(lab.g.ts), minute_columns=lab.W["VB"].shape[1],
                cache_files={p.name: dict(bytes=p.stat().st_size) for p in
                             (Path(scratch)/n for n in ("lab.pkl", "g24.pkl", "ge.pkl", "cl.pkl",
                                                      "s_rank_gap2.pkl", "single_print_sessions.pkl", "rs_trades.csv"))})


def build_current_lab(scratch):
    """Reuse lab.pkl plus only missing current roster pieces, matching FC bench.

    CLS retains the existing constant whole-Monday adverse path approximation;
    MOC_MES retains funded_bootstrap.add_moc_mes's close-based path approximation.
    These baseline limitations are explicitly preserved, not repaired here.
    """
    scratch = Path(scratch)
    lab = cached_load(scratch / "lab.pkl")
    dates = pd.DatetimeIndex(lab.g.ts[lab.tr])
    if "MON_BR_MC" not in lab.W:
        bridge = safe_import("bridge_monday_confirm", scratch)
        lab.add("MON_BR_MC", bridge.load_bridge_mc(lab.g), slippage=False)
    if "CLS" not in lab.W:
        from grid24 import jof
        cl = cached_load(scratch / "cl.pkl")
        frame = cached_load(scratch / "s_rank_gap2.pkl")["frames"]["CL"]
        op, hi = cl.o.ravel(), cl.h.ravel()
        close = pd.Series(cl.c.ravel()).ffill().to_numpy()
        pos = dict(zip(dates, range(len(dates))))
        wd, cd = np.zeros(lab.D), np.zeros(lab.D)
        for r in frame.itertuples():
            if not r.ok or not (r.gA >= 0.1):
                continue
            e_i = int(r.sun)*1440 + jof(1706)
            x_i = int(r.mon)*1440 + jof(900)
            if np.isnan(op[e_i]):
                continue
            entry = op[e_i] - .01
            px, stop, jx = close[x_i] + .01, entry + .75*r.atr, x_i
            hit = np.flatnonzero(hi[e_i:x_i+1] >= stop)
            if len(hit):
                jx = e_i + hit[0]
                px = (stop if jx == e_i or np.isnan(op[jx]) else max(op[jx], stop)) + .01
            net = (entry-px)*1000 - 7.25
            adverse = min((entry-np.nanmax(hi[e_i:jx+1]))*1000-7.25, net)
            d = pd.Timestamp(cl.ts[int(r.mon)])
            if d in pos:
                wd[pos[d]], cd[pos[d]] = min(adverse, net), net
        lab.W["CLS"] = wd[:, None]/10 * np.ones((1, lab.W["VB"].shape[1]))
        lab.C["CLS"] = cd/10
        del cl, close, op, hi
    flag = pd.read_pickle(scratch/"single_print_sessions.pkl").flag.reindex(dates).fillna(False).to_numpy(bool)
    for key, use in (("VB_F", flag), ("VB_N", ~flag)):
        if key not in lab.W:
            lab.W[key], lab.C[key] = lab.W["VB"]*use[:, None], lab.C["VB"]*use
    if "MOC_MES" not in lab.W:
        fb = safe_import("funded_bootstrap", scratch)
        fb.add_moc_mes(lab, str(scratch) + "/")
    if "RS_L" not in lab.W:
        rs = pd.read_csv(scratch/"rs_trades.csv")
        rs["kind"] = rs.kind.map({"stop": 0, "target": 1, "flat": 2})
        if rs.kind.isna().any():
            raise ValueError("Unexpected baseline RS exit kind")
        lab.add("RS_L", rs[rs.side > 0].reset_index(drop=True))
    return lab


def candidate_inputs(g, ledger_dir):
    ledger_dir = Path(ledger_dir)
    meta = pd.read_csv(ledger_dir/"daily_metadata.csv")
    if meta.day.duplicated().any():
        raise ValueError("Duplicate candidate daily metadata")
    if not np.array_equal(meta.day.to_numpy(int), np.arange(len(g.ts))):
        raise ValueError("Candidate metadata must cover exactly the cached grid calendar")
    if not np.array_equal(pd.to_datetime(meta.date).to_numpy(), pd.DatetimeIndex(g.ts).to_numpy()):
        raise ValueError("Candidate replay/grid calendar indices differ")
    stop = np.full(len(g.ts), np.nan)
    stop[meta.day.to_numpy(int)] = meta.stop_pts.to_numpy(float)
    ledgers = {}
    for name in ("OBV2", "BRIDGE100"):
        t = pd.read_csv(ledger_dir/f"{name}_full_trades.csv")
        if set(("day", "j0", "j1", "side", "entry", "exit", "kind", "net", "slips"))-set(t):
            raise ValueError("Missing standard trade columns")
        for col in ("day", "j0", "j1", "side", "kind", "slips"):
            t[col] = t[col].astype(int)
        if not (t.slips == 0).all():
            raise ValueError("Candidate must already contain all tick-slipped prices")
        if "qty" in t and not (t.qty == 1).all():
            raise ValueError("Expected per-one-NQ candidate ledgers")
        expected = (t.exit-t.entry)*t.side*20 - 7.25
        if not np.allclose(expected, t.net, rtol=0, atol=1e-7):
            raise ValueError("Candidate net does not match primary scaled-NQ costs")
        if not np.isfinite(stop[t.day.to_numpy(int)]).all() or not (stop[t.day.to_numpy(int)] > 0).all():
            raise ValueError("Missing or invalid candidate nominal stop distance")
        dates = pd.DatetimeIndex(g.ts[t.day.to_numpy()])
        if dates.min() < pd.Timestamp("2018-01-01") or dates.max() > pd.Timestamp("2026-10-09"):
            raise ValueError("Candidate outside frozen account date range")
        ledgers[name] = t
    return ledgers, stop, meta


def candidate_paths(g, trades, extra_cost=0.0):
    """Per-MNQ paths; extra stress fees are charged throughout open AND closed paths.

    portfolio.paths includes the primary commission in adverse open equity from
    entry, and realizes it at exit. Mirror those timings for the additional fee.
    A multi-entry day pays one round-trip fee per trade, never just once per day.
    """
    w, r = paths(g, trades)
    w /= 10
    r /= 10
    if extra_cost:
        for t in trades.itertuples():
            w[t.day, t.j0:] -= extra_cost
            r[t.day, t.j1:] -= extra_cost
    return w, r


def add_candidates(lab, ledgers, stop):
    for name, trades in ledgers.items():
        w, r = candidate_paths(lab.g, trades)
        lab.W[name], lab.C[name] = w[lab.tr], r[lab.tr, -1]
        lab.stop[name] = np.nan_to_num(stop[lab.tr], nan=1e12)
        # Extra fee is visible during each trade, not only at the closing mark.
        for t in trades.itertuples():
            w[t.day, t.j0:] -= EXTRA_COST
            r[t.day, t.j1:] -= EXTRA_COST
        lab.W[name+"_STRESS"], lab.C[name+"_STRESS"] = w[lab.tr], r[lab.tr, -1]
        lab.stop[name+"_STRESS"] = lab.stop[name]


def funded_plans(stress=False):
    base = dict(FUNDED_BASE)
    empty = {k: v for k, v in base.items() if k != "ONB_ML2_MC"}
    suffix = "_STRESS" if stress else ""
    return {"BASE": base, "EMPTY_ONB": empty,
            "REPLACE_OBV2": {**empty, "OBV2"+suffix: ("risk", 400)},
            "ADD_OBV2": {**base, "OBV2"+suffix: 1},
            "REPLACE_BRIDGE100": {**empty, "BRIDGE100"+suffix: ("risk", 400)}}


def quantity_states(base):
    """All exact q vectors at endpoints, integer crossings, neighbors, intervals.

    base >=0 and f monotonically increasing imply q is componentwise monotone;
    two distinct reachable vectors therefore have distinct integer sums. The
    sum is an exact index, not a hash or an approximate substitute for q.
    """
    base = np.asarray(base, dtype=np.float64)
    if not np.isfinite(base).all() or (base < 0).any():
        raise ValueError("Only finite, nonnegative fixed/risk quantities supported")
    cuts = [.5, 1.0]
    for b in base[base > 0]:
        lo = int(np.floor(b*.5 + 1e-9))
        hi = int(np.floor(b + 1e-9))
        if hi-lo > 10000:
            raise ValueError("Unexpectedly large quantity-state table")
        for m in range(lo+1, hi+1):
            x = (m-1e-9)/b
            for y in (np.nextafter(x, -np.inf), x, np.nextafter(x, np.inf)):
                if .5 <= y <= 1:
                    cuts.append(float(y))
    cuts = np.unique(cuts)
    probes = np.unique(np.r_[cuts, cuts[:-1] + np.diff(cuts)/2])
    q = np.floor(probes[:, None]*base[None, :] + 1e-9)
    q = q[np.r_[True, np.any(np.diff(q, axis=0) != 0, axis=1)]]
    sums = q.sum(axis=1).astype(np.int64)
    if len(sums) > 1 and not (np.diff(sums) > 0).all():
        raise AssertionError("Non-monotone finite quantity-state enumeration")
    return q, sums


@njit(cache=True)
def _table_minima(W, C, Q, counts):
    K, D, M = W.shape
    lo = np.zeros((D, Q.shape[1]))
    close = np.zeros_like(lo)
    for d in range(D):
        for s in range(counts[d]):
            low = 0.0
            for j in range(M):
                x = 0.0
                for k in range(K):
                    q = Q[d, s, k]
                    if q > 0:
                        x += q*W[k, d, j]
                if x < low:
                    low = x
            lo[d, s] = low
            pnl = 0.0
            for k in range(K):
                pnl += Q[d, s, k]*C[k, d]
            close[d, s] = pnl
    return lo, close


def make_table(W, C, base):
    states = [quantity_states(base[:, d]) for d in range(base.shape[1])]
    counts = np.array([len(x[1]) for x in states], dtype=np.int64)
    Q = np.zeros((base.shape[1], counts.max(), base.shape[0]))
    sums = np.full(Q.shape[:2], -1, dtype=np.int64)
    for d, (q, sm) in enumerate(states):
        Q[d, :len(q)], sums[d, :len(q)] = q, sm
    low, close = _table_minima(W, C, Q, counts)
    return dict(sums=sums, counts=counts, low=low, close=close, Q=Q,
                base=np.ascontiguousarray(base))


@njit(cache=True)
def _lookup_one(low, close, sums, counts, base, hist, horizon):
    """funded_sim.run_pa_sized state machine, exact f=.5..1/ref1500/stage=1."""
    bal = F.START
    floor = F.START-F.MLL
    cyc_start = F.START
    best = 0.0
    qual = 0
    paid = 0.0
    n = 0
    first = -1
    end = min(len(hist), horizon)
    K = base.shape[0]
    for d in range(end):
        source = hist[d]
        f = min(max((bal-floor)/1500.0, .5), 1.0)
        total_q = 0
        for k in range(K):
            total_q += int(np.floor(base[k, source]*f+1e-9))
        if total_q == 0:
            continue
        left, right = 0, counts[source]
        while left < right:
            mid = (left+right)//2
            if sums[source, mid] < total_q:
                left = mid+1
            else:
                right = mid
        if left >= counts[source] or sums[source, left] != total_q:
            raise ValueError("Reachable daily quantity is missing from exact lookup")
        dll = F._dll(bal)
        lim = max(floor, bal-dll)
        if bal+low[source, left] <= lim:
            if floor >= bal-dll:
                return paid, n, d+1, 1, first
            pnl = -dll
        else:
            pnl = close[source, left]
        bal += pnl
        if pnl >= F.MIN_DAY:
            qual += 1
        if pnl > best:
            best = pnl
        if floor < F.LOCK:
            floor = max(floor, min(bal-F.MLL, F.LOCK))
        prof = bal-cyc_start
        room = bal-F.SAFETY
        cap = F.CAPS[n]
        if qual >= F.MIN_DAYS and room >= cap and prof > 0 and best < .5*prof:
            bal -= cap
            paid += cap
            n += 1
            if first < 0:
                first = d+1
            if n == 6:
                return paid, n, d+1, 0, first
            cyc_start = bal
            best = 0.0
            qual = 0
    return paid, n, end, 0, first


@njit(cache=True)
def _lookup_many(low, close, sums, counts, base, histories, horizon):
    out = np.zeros((len(histories), 5))
    for i in range(len(histories)):
        a, b, c, d, e = _lookup_one(low, close, sums, counts, base, histories[i], horizon)
        out[i, 0], out[i, 1], out[i, 2], out[i, 3], out[i, 4] = a, b, c, d, e
    return out


def run_table(table, histories, horizon):
    return _lookup_many(table["low"], table["close"], table["sums"], table["counts"],
                        table["base"], np.ascontiguousarray(histories), horizon)


def parity_check(W, C, table, histories, name):
    records = []
    for i, hist in enumerate(histories):
        for horizon in (250, 500):
            actual = run_table(table, hist[None, :], horizon)[0]
            expected = F.run_pa_sized(np.ascontiguousarray(W[:, hist, :]),
                                     np.ascontiguousarray(C[:, hist]),
                                     np.ascontiguousarray(table["base"][:, hist]),
                                     0, horizon, 0.0, True, .5, 1.0, 1500.0, np.ones(6))
            if not np.array_equal(actual, np.array(expected)):
                raise AssertionError(f"Exact original-simulator parity failed {name}/{i}/{horizon}: {actual}/{expected}")
            records.append(dict(plan=name, history=i, horizon=horizon,
                                original=list(expected), lookup=actual.tolist(), exact=True))
    return records


def synthetic_parity(out):
    rng = np.random.default_rng(7714)
    K, D, M = 5, 40, 17
    C = rng.normal(28, 100, (K, D))
    W = np.minimum(rng.normal(-30, 100, (K, D, M)), C[:, :, None])
    base = rng.uniform(.1, 12, (K, D))
    # Include exact integer, half-integer, zero, near-integer and risk quantities.
    base[:, 0] = [0, 1, 2, 3.999999999, 10.333333333]
    table = make_table(W, C, base)
    histories = rng.integers(0, D, (12, 500))
    records = parity_check(W, C, table, histories, "synthetic")
    # Exercise cash-generating payout, trail breach, daily stop, no-quantity paths.
    for fixture, value, adverse in (("payout", 350., -10.), ("breach", -500., -2200.),
                                     ("dll", 100., -1100.), ("no_quantity", 0., 0.)):
        cc = np.full((1, 40), value)
        ww = np.full((1, 40, 3), adverse)
        bb = np.full((1, 40), 0. if fixture == "no_quantity" else 1.)
        tt = make_table(ww, cc, bb)
        records.extend(parity_check(ww, cc, tt, histories[:3] % 40, fixture))
    edge_checks = 0
    for d in range(D):
        edges = [.5, 1.]
        for b in base[:, d]:
            if b <= 0:
                continue
            for m in range(int(np.floor(.5*b+1e-9))+1, int(np.floor(b+1e-9))+1):
                crossing = (m-1e-9)/b
                edges.extend(x for x in (np.nextafter(crossing, -np.inf), crossing,
                                         np.nextafter(crossing, np.inf)) if .5 <= x <= 1.)
        for f in np.r_[edges, rng.uniform(.5, 1, 500)]:
            q = np.floor(base[:, d]*f+1e-9)
            ix = np.searchsorted(table["sums"][d, :table["counts"][d]], int(q.sum()))
            if not np.array_equal(q, table["Q"][d, ix]):
                raise AssertionError("Quantity-state parity failed")
            edge_checks += 1
    result = dict(exact_original_five_output_checks=len(records), quantity_checks=edge_checks,
                  records=records, settings=dict(fmin=.5, fmax=1., ref=1500., stage=[1]*6,
                                                 rounding="floor(base*f+1e-9)"))
    # Independent fee timing fixture: two trades on one day, with an idle gap.
    # Open equity pays at entries 1/5; realized equity pays at exits 3/6.
    grid = SimpleNamespace(o=np.full((1, 8), 10.), l=np.full((1, 8), 9.), h=np.full((1, 8), 11.))
    trades = pd.DataFrame(dict(day=[0, 0], j0=[1, 5], j1=[3, 6], side=[1, -1],
                               entry=[10., 10.], exit=[10., 10.], kind=[2, 2]))
    plain_w, plain_r = candidate_paths(grid, trades)
    stress_w, stress_r = candidate_paths(grid, trades, EXTRA_COST)
    expected_w = -EXTRA_COST*np.array([[0, 1, 1, 1, 1, 2, 2, 2]])
    expected_r = -EXTRA_COST*np.array([[0, 0, 0, 1, 1, 1, 2, 2]])
    np.testing.assert_allclose(stress_w-plain_w, expected_w, rtol=0, atol=1e-12)
    np.testing.assert_allclose(stress_r-plain_r, expected_r, rtol=0, atol=1e-12)
    result["two_trade_extra_fee_timing_fixture"] = dict(passed=True, extra_MNQ_RT=EXTRA_COST,
                                                        open_delta=expected_w.tolist(), realized_delta=expected_r.tolist())
    dump_json(Path(out)/"synthetic_parity.json", result)
    return result


def paired_ci(delta, seed=902, n=5000, block=None):
    delta = np.asarray(delta, dtype=float)
    if not len(delta):
        return [np.nan, np.nan]
    rng = np.random.default_rng(seed)
    means = np.empty(n)
    for start in range(0, n, 100):
        batch = min(100, n-start)
        if block is None:
            idx = rng.integers(0, len(delta), (batch, len(delta)))
        else:
            starts = rng.integers(0, len(delta), (batch, int(np.ceil(len(delta)/block))))
            idx = ((starts[:, :, None]+np.arange(block)) % len(delta)).reshape(batch, -1)[:, :len(delta)]
        means[start:start+batch] = delta[idx].mean(axis=1)
    return np.percentile(means, [2.5, 97.5]).tolist()


def funded_summary(res, y1):
    rows, differences = [], []
    for name, r in res.items():
        days6 = np.where(r[:, 1] == 6, r[:, 2], np.inf)
        rows.append(dict(config=name, year1=y1[name].mean(), year1_p5=np.percentile(y1[name], 5),
                         year1_p95=np.percentile(y1[name], 95), year2=r[:, 0].mean(),
                         year2_p5=np.percentile(r[:, 0], 5), year2_p95=np.percentile(r[:, 0], 95),
                         blown=r[:, 3].mean(), all6=(r[:, 1] == 6).mean(), days6=np.median(days6)))
        for reference in ("BASE", "EMPTY_ONB"):
            for metric, delta in (("year1", y1[name]-y1[reference]),
                                  ("year2", r[:, 0]-res[reference][:, 0]),
                                  ("blown", r[:, 3]-res[reference][:, 3])):
                ci = paired_ci(delta)
                differences.append(dict(config=name, reference=reference, metric=metric,
                                        delta=delta.mean(), lo=ci[0], hi=ci[1]))
    return pd.DataFrame(rows), pd.DataFrame(differences)


def run_funded(lab, scratch, out, n=1000):
    out = Path(out)
    fb = safe_import("funded_bootstrap", scratch)
    histories = fb.Boot(lab)._histories(n, 500, 20, 1)
    np.save(out/"funded_histories.npy", histories)
    all_plans = {f"{regime}__{name}": p for regime in ("primary", "stress")
                 for name, p in funded_plans(regime == "stress").items()}
    keys = sorted({k for p in all_plans.values() for k in p})
    W = np.stack([lab.W[k] for k in keys])
    C = np.stack([lab.C[k] for k in keys])
    if not np.isfinite(W).all() or not np.isfinite(C).all():
        raise ValueError("Nonfinite account paths")
    # The existing bootstrap also removes unchanged minutes. Use all minutes:
    # exact same minima and addition order; no full-stack np.diff temporary.
    parity, resources, results, year1 = [], [], {}, {}
    shared = {}
    fixed = histories[np.unique([0, min(1, n-1), min(17, n-1), min(333, n-1), n-1])]
    for name, plan in all_plans.items():
        canonical = json.dumps(plan, sort_keys=True)
        if canonical in shared:
            previous = shared[canonical]
            results[name], year1[name] = results[previous], year1[previous]
            continue
        started = time.monotonic()
        base = np.zeros((len(keys), lab.D))
        names, sizes = lab._base(plan)
        for k, b in zip(names, sizes):
            base[keys.index(k)] = b
        table = make_table(W, C, base)
        parity.extend(parity_check(W, C, table, fixed, name))
        results[name] = run_table(table, histories, 500)
        year1[name] = run_table(table, histories, 250)[:, 0]
        resources.append(dict(config=name, seconds=time.monotonic()-started,
                              states=int(table["counts"].sum()), max_daily_states=int(table["counts"].max())))
        shared[canonical] = name
        print(f"funded {name}: exact parity passed, {resources[-1]['seconds']:.1f}s", flush=True)
        del table
    np.savez_compressed(out/"funded_raw.npz", **{k: v for k, v in results.items()},
                        **{k+"__year1": v for k, v in year1.items()})
    for regime in ("primary", "stress"):
        r = {k.split("__", 1)[1]: v for k, v in results.items() if k.startswith(regime+"__")}
        y = {k.split("__", 1)[1]: v for k, v in year1.items() if k.startswith(regime+"__")}
        summary, diffs = funded_summary(r, y)
        summary.to_csv(out/f"funded_{regime}_summary.csv", index=False)
        diffs.to_csv(out/f"funded_{regime}_paired_differences.csv", index=False)
    dump_json(out/"real_funded_parity.json", parity)
    dump_json(out/"funded_resources.json", resources)
    return results, year1


def eval_plans(stress=False):
    base = {"VB": 8, "ONB30": ("risk", 1100), "MON_BR": 2, "EOS": ("risk", 500)}
    empty = {k: v for k, v in base.items() if k != "ONB30"}
    suffix = "_STRESS" if stress else ""
    return {"BASE": base, "EMPTY_ONB": empty,
            "REPLACE_OBV2": {**empty, "OBV2"+suffix: ("risk", 1100)},
            "ADD_OBV2": {**base, "OBV2"+suffix: 1},
            "REPLACE_BRIDGE100": {**empty, "BRIDGE100"+suffix: ("risk", 1100)}}


def evaluation_summary(raw, dates):
    rows, diffs = [], []
    for period, mask in (("full", np.ones(len(dates), bool)), ("2018_22", dates.year < 2023),
                         ("2023_plus", dates.year >= 2023)):
        for name, r in raw.items():
            x = r[mask]
            passed, blown, timeout = x[:, 0] == 1, x[:, 0] == -1, x[:, 0] == 0
            rows.append(dict(period=period, config=name, n=len(x), pass_rate=passed.mean(),
                             blown=blown.mean(), timeout=timeout.mean(),
                             median_pass_days=np.median(x[passed, 1]) if passed.any() else np.nan))
            for reference in ("BASE", "EMPTY_ONB"):
                for metric, code in (("pass_rate", 1), ("blown", -1), ("timeout", 0)):
                    delta = (x[:, 0] == code).astype(float)-(raw[reference][mask, 0] == code)
                    ci = paired_ci(delta, seed=903, block=60)
                    diffs.append(dict(period=period, config=name, reference=reference, metric=metric,
                                      delta=delta.mean(), lo=ci[0], hi=ci[1]))
    return pd.DataFrame(rows), pd.DataFrame(diffs)


def run_evaluation(g, ledgers, stop, scratch, out):
    out = Path(out)
    cl = safe_import("combine_levers_test", scratch)
    reports = safe_import("build_lab", scratch).REPORTS
    bridge = safe_import("bridge_monday_confirm", scratch)
    tr = g.trading
    dates = pd.DatetimeIndex(g.ts[tr])
    atr = g.daily_atr(15)[tr]
    pieces, stops = {}, {}
    baseline_trades = {"VB": with_slippage(load_mc(g, reports["VB"][0])),
                       "ONB30": with_slippage(load_mc(g, cl.ONB30)),
                       "MON_BR": bridge.load_bridge_mc(g),
                       "EOS": with_slippage(load_mc(g, reports["EOS"][0]))}
    for name, t in baseline_trades.items():
        w, r = paths(g, t)
        pieces[name] = w[tr]/10, r[tr]/10
    stops.update(ONB30=np.nan_to_num(.25*atr, nan=1e12),
                 EOS=np.nan_to_num(reports["EOS"][1]*atr, nan=1e12))
    for name, t in ledgers.items():
        for suffix, fee in (("", 0.), ("_STRESS", EXTRA_COST)):
            w, r = candidate_paths(g, t, fee)
            pieces[name+suffix] = w[tr], r[tr]
            stops[name+suffix] = np.nan_to_num(stop[tr], nan=1e12)
    starts = np.arange(len(tr)-cl.MAXD+1)
    starts = starts[dates[starts] >= pd.Timestamp("2018-01-01")]
    start_dates = dates[starts]
    one = lambda p, c, n: 1.0
    results, shared, convention = {}, {}, []
    for regime in ("primary", "stress"):
        raw = {}
        for name, plan in eval_plans(regime == "stress").items():
            canonical = json.dumps(plan, sort_keys=True)
            if canonical in shared:
                raw[name] = shared[canonical]
                continue
            W = np.zeros_like(next(iter(pieces.values()))[0])
            R = np.zeros_like(W)
            for key, value in plan.items():
                q = np.floor(value[1]/(stops[key]*2))[:, None] if isinstance(value, tuple) else value
                W += pieces[key][0]*q
                R += pieces[key][1]*q
            codes = {"pass": 1, "fail": -1, "time": 0}
            res = [cl.challenge(W, R, np.arange(s, s+cl.MAXD), one) for s in starts]
            if any(x is None for x in res):
                raise AssertionError("A full-length evaluation start returned no result")
            raw[name] = np.array([(codes[x[0]], x[1]) for x in res])
            shared[canonical] = raw[name]
            # Existing scripts included truncated tail windows that hit pass/fail
            # before data ended. They are excluded here by preregistration.
            tail = [cl.challenge(W, R, np.arange(s, len(tr)), one)
                    for s in range(max(0, len(tr)-cl.MAXD+1), len(tr))]
            convention.append(dict(regime=regime, config=name, full_starts=len(starts),
                                   truncated_tail_pass=sum(x is not None and x[0] == "pass" for x in tail),
                                   truncated_tail_fail=sum(x is not None and x[0] == "fail" for x in tail),
                                   truncated_tail_no_result=sum(x is None for x in tail)))
            print(f"evaluation {regime} {name}: {len(starts)} full starts", flush=True)
            del W, R
        summary, diffs = evaluation_summary(raw, start_dates)
        summary.to_csv(out/f"evaluation_{regime}_summary.csv", index=False)
        diffs.to_csv(out/f"evaluation_{regime}_paired_differences.csv", index=False)
        np.savez_compressed(out/f"evaluation_{regime}_raw.npz", starts=starts,
                            dates=start_dates.to_numpy(), **raw)
        results[regime] = raw
    dump_json(out/"evaluation_end_window_convention.json", convention)
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", choices=("prepare", "synthetic-parity", "funded", "evaluation", "all"), required=True)
    parser.add_argument("--scratch", type=Path, default=ROOT/"scratch_data")
    parser.add_argument("--ledger-dir", type=Path, default=DEFAULT_LEDGERS)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--gate-passed", action="store_true", help="Only after root confirms frozen cheap design gate")
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    if args.stage == "prepare":
        dump_json(args.out/"cache_metadata.json", lab_metadata(args.scratch))
        return
    if args.stage == "synthetic-parity":
        print(json.dumps({k: v for k, v in synthetic_parity(args.out).items() if k != "records"}, indent=2))
        return
    if not args.gate_passed:
        raise SystemExit("Historical account testing blocked: --gate-passed is required after the frozen design gate passes")
    started = time.monotonic()
    lab = build_current_lab(args.scratch)
    ledgers, stop, meta = candidate_inputs(lab.g, args.ledger_dir)
    if args.stage in ("funded", "all"):
        add_candidates(lab, ledgers, stop)
        run_funded(lab, args.scratch, args.out)
    if args.stage in ("evaluation", "all"):
        g = lab.g
        del lab
        gc.collect()
        run_evaluation(g, ledgers, stop, args.scratch, args.out)
    manifest = dict(seconds=time.monotonic()-started, script_sha256=sha(Path(__file__)),
                    inputs={p.name: sha(p) for p in args.ledger_dir.glob("*full_trades.csv")},
                    baseline_cache_sha256={p.name: sha(p) for p in
                        (args.scratch/name for name in ("lab.pkl", "ge.pkl", "cl.pkl", "s_rank_gap2.pkl",
                                                       "single_print_sessions.pkl", "rs_trades.csv"))},
                    metadata_sha256=sha(args.ledger_dir/"daily_metadata.csv"),
                    historical_gate_explicitly_confirmed=True,
                    funded=dict(n=1000, H=500, L=20, seed=1, fmin=.5, fmax=1, ref=1500,
                                CI_resamples=5000, CI_seed=902, original_five_output_parity_required=True),
                    evaluation=dict(window=21, full_length_starts_only=True, CI_block=60, CI_resamples=5000, CI_seed=903),
                    limitations=["Combined open-position tier cap is not enforced by existing account simulators; no new cap introduced",
                                 "Existing CL constant-daily adverse and MOC close-path approximations retained",
                                 "Scaled-NQ commission is .725/MNQ primary; extra challenger-only stress 1.275/MNQ",
                                 "Existing combine_levers target/breach same-minute priority retained"])
    dump_json(args.out/f"{args.stage}_manifest.json", manifest)


if __name__ == "__main__":
    main()
