"""Measure first-payout timing for the frozen, adopted 2026-10-26 stacks.

Reuses pinned repository loaders, account rules, block histories and exact
quantity tables. No strategy search and no live/account access.
"""
from __future__ import annotations

import argparse
import contextlib
import gc
import hashlib
import importlib
import importlib.abc
import importlib.util
import importlib.metadata
import json
import math
import pickle
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from numba import njit

ROOT = Path(__file__).resolve().parents[1]
SNAP = ROOT / "agents/codex/inputs/current_payout_timing_20261026"
OUT = ROOT / "analysis/outputs/codex_current_payout_timing_20261026"
RUNTIME = ROOT / "agents/codex/runtime/current_payout_timing_20261026"
PREREG = "43528dc94c13d9340ceee582fc48a8386245dd12"
HORIZON = 500
CHECKPOINTS = (21, 42, 63, 84, 105, 126, 252, 500)


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for b in iter(lambda: f.read(1024 * 1024), b""):
            h.update(b)
    return h.hexdigest()


def dump(path, value):
    Path(path).write_text(json.dumps(value, indent=2, default=str, allow_nan=False) + "\n")


class PinnedFinder(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        p = SNAP / "analysis" / (fullname + ".py")
        if "." not in fullname and p.is_file():
            return importlib.util.spec_from_file_location(fullname, p)


@contextlib.contextmanager
def pinned(scratch):
    old_argv = sys.argv
    finder = PinnedFinder()
    sys.argv = [str(Path(__file__)), str(scratch), "library"]
    sys.meta_path.insert(0, finder)
    try:
        yield
    finally:
        sys.meta_path.remove(finder)
        sys.argv = old_argv


@njit(cache=True)
def lookup(low, close, sums, counts, base, hist, account, ref):
    """Canonical funded state machine using exact daily quantity minima.

    account = [START, MLL, LOCK, SAFETY, MIN_DAY, MIN_DAYS, SIZE].
    Timing and payouts match run_pa_sized; cap requests occur at the close.
    """
    start, mll, lock, safe, qday, mindays, size = account
    caps = (np.array([1500., 1500., 2000., 2500., 2500., 3000.]) if size == 50
            else np.array([2500., 3000., 3000., 3000., 4000., 5000.]))
    bal = start
    floor = start - mll
    cyc_start = start
    best, qual, paid, n, first = 0., 0, 0., 0, -1
    for d in range(len(hist)):
        source = hist[d]
        f = min(max((bal - floor) / ref, .5), 1.)
        total = 0
        for k in range(base.shape[0]):
            total += int(np.floor(base[k, source] * f + 1e-9))
        if total == 0:
            continue
        left, right = 0, counts[source]
        while left < right:
            mid = (left + right) // 2
            if sums[source, mid] < total:
                left = mid + 1
            else:
                right = mid
        if left >= counts[source] or sums[source, left] != total:
            raise ValueError("Missing reachable quantity state")
        dll = 2000.
        if size == 50:
            profit = bal - start
            dll = 3000. if profit >= 6000. else 2000. if profit >= 3000. else 1000.
        lim = max(floor, bal - dll)
        if bal + low[source, left] <= lim:
            if floor >= bal - dll:
                return paid, n, d + 1, 1, first
            pnl = -dll
        else:
            pnl = close[source, left]
        bal += pnl
        if pnl >= qday:
            qual += 1
        best = max(best, pnl)
        if floor < lock:
            floor = max(floor, min(bal - mll, lock))
        profit = bal - cyc_start
        if qual >= mindays and bal - safe >= caps[n] and profit > 0 and best < .5 * profit:
            bal -= caps[n]
            paid += caps[n]
            n += 1
            if first < 0:
                first = d + 1
            if n == 6:
                return paid, n, d + 1, 0, first
            cyc_start, best, qual = bal, 0., 0
    return paid, n, len(hist), 0, first


def run_lookup(table, hist, account, ref):
    return np.array(lookup(table["low"], table["close"], table["sums"], table["counts"],
                           table["base"], np.ascontiguousarray(hist), account, ref))


def event_quantile(first, p):
    values = np.sort(np.where(np.asarray(first) > 0, first, np.inf))
    x = float(values[max(0, math.ceil(p * len(values)) - 1)])
    return x if np.isfinite(x) else None


def timing(first):
    first = np.asarray(first)
    recipients = first[first > 0]
    return dict(n=len(first), received_share=float((first > 0).mean()),
                no_payout_share=float((first <= 0).mean()),
                p10_days=event_quantile(first, .1), median_days=event_quantile(first, .5),
                p90_days=event_quantile(first, .9),
                recipient_only_median_days=float(np.median(recipients)) if len(recipients) else None,
                **{f"p_by_{d}": float(((first > 0) & (first <= d)).mean()) for d in CHECKPOINTS})


def fixtures(acc, f50, f150):
    """Meaningful parity on funded payout, DLL, trailing breach and integer sizes."""
    records = []
    rng = np.random.default_rng(20261026)
    for which, mod, ref in ((50, f50, 1500.), (150, f150, 3000.)):
        account = np.array([mod.START, mod.MLL, mod.LOCK, mod.SAFETY,
                            mod.MIN_DAY, mod.MIN_DAYS, which], dtype=float)
        for scenario in ("mixed", "steady_profit", "trailing_breach", "dll_then_recovery"):
            k, d, m = 3, 80, 7
            base = np.repeat(np.array([1., 2.5, 4.1])[:, None], d, axis=1)
            c = rng.normal(15, 70, (k, d))
            w = np.minimum(rng.normal(-20, 90, (k, d, m)), c[:, :, None])
            if scenario == "steady_profit":
                c[:] = 100.; w[:] = 0.
            if scenario == "trailing_breach":
                c[:] = 0.; w[:] = -3000.
            if scenario == "dll_then_recovery":
                c[:] = 150.; w[:] = 0.; w[:, 4, :] = -400.
            table = acc.make_table(w, c, base)
            h = np.arange(d)
            got = run_lookup(table, h, account, ref)
            exp = np.array(mod.run_pa_sized(w, c, base, 0, d, 0., True, .5, 1., ref, np.ones(6)))
            np.testing.assert_array_equal(got, exp)
            records.append(dict(account=which, scenario=scenario, exact=True, output=got.tolist()))
    return records


def build_lab(scratch):
    import fc_2b_bench as fc
    import funded_bootstrap as fb
    import overnight_tick_bench as ot
    import swing_target_bench as st
    lab = fc.fast_plan_lab(str(scratch) + "/")
    fb.add_moc_mes(lab, str(scratch) + "/")
    rs = pd.read_csv(scratch / "rs_trades.csv")
    rs["kind"] = rs.kind.map(fc.KIND)
    if rs.kind.isna().any():
        raise ValueError("Unknown RS exit kind")
    lab.add("RS_L", rs[rs.side > 0].reset_index(drop=True))
    lab.add("RS", rs)
    ots = pd.read_csv(SNAP / "checks/candidates/overnight_tick/python_trades.csv", parse_dates=["date"])
    ot.add_ot(lab, ots.set_index("date"))
    # Canonical ST loader expects this name in SP; never modify shared scratch.
    RUNTIME.mkdir(parents=True, exist_ok=True)
    (RUNTIME / "swing_be.csv").write_bytes((SNAP / "checks/candidates/swing_target/codex_be_trades.csv").read_bytes())
    st.SP = str(RUNTIME) + "/"
    trades = st.pt_trades(lab.g)
    lab.add("ST", trades)
    plans = {50: st.plans50()["VB 2/1 -> 1/1 + ST 1"],
             150: st.plans150()["DT 2 -> ST 2"]}
    dates = pd.DatetimeIndex(lab.g.ts[lab.tr])
    use = np.asarray((dates >= "2018-01-01") & (dates <= "2026-07-07"))
    needed = set().union(*(set(p) for p in plans.values()))
    for attr in ("W", "C", "stop", "N", "J0"):
        old = getattr(lab, attr)
        setattr(lab, attr, {k: np.ascontiguousarray(v[use]) for k, v in old.items() if k in needed})
    lab.tr = lab.tr[use]
    lab.D = len(lab.tr)
    lab.yr = dates[use].year
    return lab, plans, ots, trades


def evaluation_paths(lab, fee):
    import portfolio as pf
    import funded_lab as fl
    import build_lab as bl
    import bridge_monday_confirm as bridge
    import combine_levers_test as cl
    g, tr = lab.g, lab.tr
    atr = g.daily_atr(15)[tr]
    trades = {"VB": fl.with_slippage(pf.load_mc(g, bl.REPORTS["VB"][0])),
              "ONB30": fl.with_slippage(pf.load_mc(g, cl.ONB30)),
              "MON_BR": bridge.load_bridge_mc(g),
              "EOS": fl.with_slippage(pf.load_mc(g, bl.REPORTS["EOS"][0]))}
    old = pf.COST
    pf.COST = fee * 10
    try:
        parts = {k: tuple(a[tr] / 10 for a in pf.paths(g, t)) for k, t in trades.items()}
    finally:
        pf.COST = old
    result = {}
    for which, risk_onb, risk_eos, vb, br in ((50, 1100., 500., 8., 2.),
                                            (150, 2750., 1250., 20., 5.)):
        risk = lambda dollars, m: np.floor(dollars / (np.nan_to_num(m * atr, nan=1e12) * 2))[:, None]
        q = {"VB": vb, "ONB30": risk(risk_onb, .25), "MON_BR": br,
             "EOS": risk(risk_eos, bl.REPORTS["EOS"][1])}
        result[which] = (sum(parts[k][0] * q[k] for k in q),
                         sum(parts[k][1] * q[k] for k in q))
    return result


def pipeline(table, histories, account, ref, eval_paths, which):
    """Keep phase transitions and retries inside the same market history."""
    import combine_levers_test as cl
    import plan_150k_test as p150
    w, r = eval_paths
    rows = []
    for number, hist in enumerate(histories):
        # Only this one history is expanded; no giant history x day x minute cube.
        wh, rh = w[hist], r[hist]
        offset, attempts, funded = 0, 0, 0
        first = -1
        while offset < len(hist):
            if which == 50:
                outcome = cl.challenge(wh, rh, np.arange(offset, min(offset + 21, len(hist))),
                                       lambda profit, cushion, day: 1.)
            else:
                outcome = p150.evaluation(wh, rh, offset, len(hist), p150.R150)
            attempts += 1
            if outcome is None:
                break
            status, days = outcome
            offset += days
            if status != "pass" or offset >= len(hist):
                continue
            funded += 1
            rr = run_lookup(table, hist[offset:], account, ref)
            if rr[4] > 0:
                first = offset + int(rr[4])
                break
            offset += int(rr[2])
            if not rr[3]:
                break
        rows.append(dict(history=number, first=first, evaluation_attempts=attempts,
                         funded_accounts_started=funded))
    return pd.DataFrame(rows)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--scratch", type=Path, default=ROOT / "scratch_data")
    ap.add_argument("--fixtures-only", action="store_true")
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    started = time.monotonic()
    sys.path.insert(0, str(ROOT / "analysis"))
    with pinned(args.scratch.resolve()):
        import codex_ob_v2_accounts as acc
        import funded_sim as f50
        import funded_sim150 as f150
        import funded_bootstrap as fb
        checked = fixtures(acc, f50, f150)
        dump(OUT / "synthetic_parity.json", checked)
        print("Synthetic parity: 8/8 exact", flush=True)
        if args.fixtures_only:
            return
        print("Building fixed current roster from existing caches", flush=True)
        lab, plans, ot, st = build_lab(args.scratch.resolve())
        dates = pd.DatetimeIndex(lab.g.ts[lab.tr])
        hist = np.concatenate([fb.Boot(lab)._histories(250, HORIZON, 20, s) for s in (1, 2, 3, 4)])
        np.save(OUT / "histories.npy", hist)
        summary, parity = [], []
        print(f"Coverage: {dates.min().date()} .. {dates.max().date()}, {len(dates)} sessions", flush=True)
        for fee_label, fee in (("legacy_bench", .725), ("real_1.04", 1.04), ("stress_1.24", 1.24)):
            if fee_label != "legacy_bench":
                previous = .725 if fee == 1.04 else 1.04
                for name in lab.C:
                    baseline = .5 if name == "MOC_MES" and fee == 1.04 else previous
                    lab.real_fees(fee - baseline, [name])
            # The legacy evaluation uses $.725 for every NQ-based leg.
            ep = evaluation_paths(lab, fee)
            for which, mod, ref in ((50, f50, 1500.), (150, f150, 3000.)):
                label = f"{which}K/{fee_label}"
                print(f"{label}: building exact quantity table", flush=True)
                keys = sorted(plans[which])
                names, base = lab._base({k: plans[which][k] for k in keys})
                assert names == keys
                w, c = np.stack([lab.W[k] for k in keys]), np.stack([lab.C[k] for k in keys])
                table = acc.make_table(w, c, base)
                account = np.array([mod.START, mod.MLL, mod.LOCK, mod.SAFETY,
                                    mod.MIN_DAY, mod.MIN_DAYS, which], dtype=float)
                if fee == 1.04:
                    for ix in (0, 17, 333, 999):
                        for horizon in (250, 500):
                            h = hist[ix, :horizon]
                            got = run_lookup(table, h, account, ref)
                            exp = np.array(mod.run_pa_sized(np.ascontiguousarray(w[:, h]),
                                np.ascontiguousarray(c[:, h]), np.ascontiguousarray(base[:, h]),
                                0, horizon, 0., True, .5, 1., ref, np.ones(6)))
                            np.testing.assert_array_equal(got, exp)
                            parity.append(dict(account=which, history=ix, horizon=horizon, exact=True,
                                               canonical=exp.tolist(), lookup=got.tolist()))
                    print(f"{label}: direct historical parity exact", flush=True)
                del w, c
                gc.collect()
                raw = np.stack([run_lookup(table, h, account, ref) for h in hist])
                frame = pd.DataFrame(raw, columns=["paid", "payouts", "days", "blown", "first"])
                frame.to_csv(OUT / f"funded_{which}_{fee_label}.csv", index_label="history")
                a = dict(account=which, fee=fee_label, clock="from_funding", **timing(raw[:, 4]),
                         blown=float(raw[:, 3].mean()), all6=float((raw[:, 1] == 6).mean()),
                         year2_paid=float(raw[:, 0].mean()),
                         median_days6=event_quantile(np.where(raw[:, 1] == 6, raw[:, 2], -1), .5))
                summary.append(a)
                print(f"{label}: funded first median {a['median_days']} sessions", flush=True)
                pipe = pipeline(table, hist, account, ref, ep[which], which)
                pipe.to_csv(OUT / f"pipeline_{which}_{fee_label}.csv", index=False)
                a = dict(account=which, fee=fee_label, clock="from_first_evaluation", **timing(pipe['first']))
                summary.append(a)
                print(f"{label}: evaluation-to-first median {a['median_days']} sessions", flush=True)
                dump(OUT / "summary.json", summary)
                pd.DataFrame(summary).to_csv(OUT / "summary.csv", index=False)
                del table
                gc.collect()
            del ep
            gc.collect()
        dump(OUT / "historical_parity.json", parity)
        paths = sorted(SNAP.rglob("*"))
        cache_names = ("lab.pkl", "g24.pkl", "ge.pkl", "cl.pkl", "s_rank_gap2.pkl",
                       "single_print_sessions.pkl", "rs_trades.csv")
        import build_lab as bl
        import bridge_monday_confirm as bridge
        import combine_levers_test as cl
        reports = {bl.REPORTS[k][0] for k in ("VB", "ONB_ML2_MC", "EOS", "LDF_MC", "NFP_MC")}
        reports.update((bridge.F, cl.ONB30))
        manifest = dict(preregistration=PREREG, source_ref=json.loads((SNAP / "source_manifest.json").read_text())["source_ref"],
            script_sha256=sha(__file__), accelerator_sha256=sha(ROOT / "analysis/codex_ob_v2_accounts.py"),
            histories_sha256=sha(OUT / "histories.npy"),
            history_publication="Numpy history array retained locally; reconstruct exactly from four seeds and 20-day blocks. Account CSVs are published.",
            sources={str(p.relative_to(ROOT)):sha(p) for p in paths if p.is_file() and "__pycache__" not in p.parts},
            caches={name:sha(args.scratch / name) for name in cache_names},
            reports={p:sha(ROOT / p) for p in sorted(reports)},
            coverage=dict(first=str(dates.min().date()), last=str(dates.max().date()), sessions=len(dates),
                          dropped_after_cutoff="OT signals unavailable after 2026-07-07; all strategies truncated together"),
            ot_ledger_rows=len(ot), st_ledger_rows=len(st), plans=plans, histories=1000, seeds=[1,2,3,4],
            block=20, horizon=500, months_definition="21 sessions", fees=[.725,1.04,1.24],
            timing="Full-cap payout request at qualifying close; bank/approval/activation lag excluded",
            pipeline="Fresh evaluation slot; retries retain the same market history; not conditioned on current live balances",
            limitations=["Historic bootstrap assumes the sampled edge and dependence persist.",
                "Existing CL/OT constant daily-adverse and MOC close-path approximations retained.",
                "50K evaluation gives pass priority on a same-minute tie; 150K requires pass strictly before breach.",
                "Canonical ST loader and its extra slippage/holiday exits retained.",
                "Inherited real_fees fallback counts one round trip per active day where cache trade counts are absent.",
                "No new strategy variants or independent holdout claim; fixed adopted roster only."],
            versions={"python":sys.version,"numpy":np.__version__,"pandas":pd.__version__,
                **{n:importlib.metadata.version(n) for n in ("numba","openpyxl","scipy","scikit-learn")}},
            output_checks=dict(synthetic_exact=len(checked), historical_exact=len(parity), summary_reconciliations=len(summary)),
            seconds=time.monotonic()-started)
        dump(OUT / "manifest.json", manifest)
        print(pd.DataFrame(summary)[["account","fee","clock","p10_days","median_days","p90_days","p_by_63","p_by_126"]].to_string(index=False), flush=True)


if __name__ == "__main__":
    main()
