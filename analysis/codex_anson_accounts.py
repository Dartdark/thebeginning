"""Frozen Anson Apex placement: 50K/150K funded and evaluations (928c0ea).

Reuses exact finite-quantity minima, while parameterizing the account state
machine explicitly for both sizes. Original simulators verify all five outputs
for five fixed production histories at both horizons in every allocation/fee.
"""
from __future__ import annotations

import argparse
import gc
import importlib
import json
import pickle
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "agents/codex/runtime/or_pullback_python"))
sys.path.insert(0, str(ROOT / "analysis"))
import numpy as np
import pandas as pd
from numba import njit
import codex_anson_plan as A
import codex_ob_v2_accounts as acc
from codex_night_volume_switch_portfolio import chronological_ci

PREREG = "928c0eacf65627aea059c8961e8957c976f550ed"
OUT = ROOT / "analysis/outputs/codex_anson/accounts"
REPLAY = OUT.parent / "replay"
PREPARED = ROOT / "agents/codex/runtime/anson_plan.pkl"
MANIFEST = OUT.parent / "baseline/prepared_manifest.json"
COHORTS = {"2018_plus": ("2018-01-01", "2100-01-01"),
           "2018_22": ("2018-01-01", "2023-01-01"),
           "2018_24": ("2018-01-01", "2025-01-01"),
           "2023_plus": ("2023-01-01", "2100-01-01"),
           "2025_plus": ("2025-01-01", "2100-01-01")}


@njit(cache=True)
def lookup_one(low, close, sums, counts, base, hist, horizon,
               start, mll, lock, safety, qday, caps, ref, dllmode, mindays):
    """Original funded_sim sized state machine with explicit account constants."""
    bal, floor, cyc_start = start, start-mll, start
    best, qual, paid, n, first = 0., 0, 0., 0, -1
    end = min(len(hist), horizon)
    for d in range(end):
        source = hist[d]
        f = min(max((bal-floor)/ref, .5), 1.)
        total_q = 0
        for k in range(base.shape[0]):
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
            raise ValueError("Reachable daily quantity missing from exact lookup")
        if dllmode == 150:
            dll = 2000.
        else:
            profit = bal-start
            dll = 3000. if profit >= 6000. else 2000. if profit >= 3000. else 1000.
        lim = max(floor, bal-dll)
        if bal+low[source, left] <= lim:
            if floor >= bal-dll:
                return paid, n, d+1, 1, first
            pnl = -dll
        else:
            pnl = close[source, left]
        bal += pnl
        if pnl >= qday:
            qual += 1
        if pnl > best:
            best = pnl
        if floor < lock:
            floor = max(floor, min(bal-mll, lock))
        prof, room, cap = bal-cyc_start, bal-safety, caps[n]
        if qual >= mindays and room >= cap and prof > 0 and best < .5*prof:
            bal -= cap
            paid += cap
            n += 1
            if first < 0:
                first = d+1
            if n == 6:
                return paid, n, d+1, 0, first
            cyc_start, best, qual = bal, 0., 0
    return paid, n, end, 0, first


@njit(cache=True)
def lookup_many(low, close, sums, counts, base, histories, horizon,
                start, mll, lock, safety, qday, caps, ref, dllmode, mindays):
    out = np.zeros((len(histories), 5))
    for i in range(len(histories)):
        a, b, c, d, e = lookup_one(low, close, sums, counts, base, histories[i], horizon,
                                  start, mll, lock, safety, qday, caps, ref, dllmode, mindays)
        out[i, 0], out[i, 1], out[i, 2], out[i, 3], out[i, 4] = a, b, c, d, e
    return out


def rules(F, context):
    return (float(F.START), float(F.MLL), float(F.LOCK), float(F.SAFETY),
            float(F.MIN_DAY), np.asarray(F.CAPS), 3000. if context.startswith("150") else 1500.,
            150 if context.startswith("150") else 50, int(F.MIN_DAYS))


def run_table(table, histories, horizon, parameters):
    return lookup_many(table["low"], table["close"], table["sums"], table["counts"],
                       table["base"], np.ascontiguousarray(histories), horizon, *parameters)


def parity_check(W, C, table, histories, F, parameters, name):
    records = []
    for i, h in enumerate(histories):
        for horizon in (250, 500):
            actual = run_table(table, h[None, :], horizon, parameters)[0]
            expected = np.asarray(F.run_pa_sized(np.ascontiguousarray(W[:, h, :]),
                np.ascontiguousarray(C[:, h]), np.ascontiguousarray(table["base"][:, h]),
                0, horizon, 0., True, .5, 1., parameters[6], np.ones(6)))
            np.testing.assert_array_equal(actual, expected, err_msg=f"Exact simulator parity {name}/{i}/{horizon}")
            records.append(dict(config=name, history=i, horizon=horizon,
                                original=expected.tolist(), lookup=actual.tolist(), exact=True))
    return records


def synthetic_checks(F50, F150):
    rng = np.random.default_rng(7714)
    K, D, M = 5, 40, 17
    C = rng.normal(28, 100, (K, D))
    W = np.minimum(rng.normal(-30, 100, (K, D, M)), C[:, :, None])
    base = rng.uniform(.1, 12, (K, D))
    base[:, 0] = [0., 1., 2., 3.999999999, 10.333333333]
    hist = rng.integers(0, D, (5, 500))
    records = []
    for context, F in (("50K_funded", F50), ("150K_funded", F150)):
        par = rules(F, context)
        tt = acc.make_table(W, C, base)
        records += parity_check(W, C, tt, hist, F, par, context+"/random_rounding")
        for label, close, low, qty in (("payout", 350., -10., 1.),
                                      ("trail", -500., -5000., 1.),
                                      ("dll", 100., -1100. if context.startswith("50") else -2100., 1.),
                                      ("no_quantity", 0., 0., 0.)):
            c, w, b = np.full((1, D), close), np.full((1, D, 3), low), np.full((1, D), qty)
            table = acc.make_table(w, c, b)
            records += parity_check(w, c, table, hist, F, par, context+"/"+label)
    A.dump(OUT / "synthetic_parity.json", dict(exact_records=len(records), records=records,
        contexts=["50K_ref1500", "150K_ref3000"], fixtures=["rounding", "payout", "trail", "dll", "zero_quantity"]))


def candidate_paths(g, trades, fee=1.04):
    """Per-MNQ marks; open entry holds its minute, open exit does not.

    Entry slippage0.50 is present from entry; round-trip fee and exit slippage
    are paid at exit. Every round trip pays, including multiple entries/day.
    Closed P&L remains zero until the trade closes, matching existing bench R.
    """
    w, r = np.zeros(g.o.shape), np.zeros(g.o.shape)
    for t in trades.itertuples():
        d, e, z, side = int(t.day), int(t.entry_j), int(t.exit_j), int(t.side)
        if t.entry_phase != "open" or t.exit_phase != "open" or not 0 <= e < z < g.o.shape[1]:
            raise ValueError("Apex ledger must contain same-day open entry/exit")
        if bool(t.cross_date) or int(t.missing_held_minutes):
            raise ValueError("Unknown held candidate minute")
        adverse = g.l[d, e:z] if side > 0 else g.h[d, e:z]
        if not np.isfinite(adverse).all():
            raise ValueError("Missing held OHLC")
        net = (t.exit-t.entry)*side*2.-fee-1.
        if not np.isclose(net, t.gross_points*2-fee-1, rtol=0, atol=1e-7):
            raise ValueError("Gross ledger mismatch")
        w[d, e:z] += (adverse-t.entry)*side*2.-.5
        w[d, z:] += net
        r[d, z:] += net
    return w, r


def path_fixtures():
    from types import SimpleNamespace
    g = SimpleNamespace(o=np.full((1, 12), 100.), l=np.full((1, 12), 99.), h=np.full((1, 12), 101.))
    g.l[0, 2], g.l[0, 5], g.h[0, 7], g.h[0, 10] = 10., 1., 190., 250.
    t = pd.DataFrame([dict(day=0, entry_j=2, exit_j=5, side=1, entry=100., exit=101.,
        gross_points=1., entry_phase="open", exit_phase="open", cross_date=False, missing_held_minutes=0),
        dict(day=0, entry_j=7, exit_j=10, side=-1, entry=100., exit=101.,
        gross_points=-1., entry_phase="open", exit_phase="open", cross_date=False, missing_held_minutes=0)])
    w, r = candidate_paths(g, t)
    np.testing.assert_allclose(w[0, 2], -180.5)
    np.testing.assert_allclose(w[0, 3:5], -2.5)
    np.testing.assert_allclose(w[0, 5:7], -.04)
    np.testing.assert_allclose(w[0, 7], -180.54)
    np.testing.assert_allclose(w[0, 10:], -4.08)
    np.testing.assert_allclose(r[0, 10:], -4.08)
    ws, rs = candidate_paths(g, t, 1.24)
    np.testing.assert_allclose(ws[0, 2:5]-w[0, 2:5], 0.)
    np.testing.assert_allclose(ws[0, 5:10]-w[0, 5:10], -.2)
    np.testing.assert_allclose(ws[0, 10:]-w[0, 10:], -.4)
    np.testing.assert_allclose(rs[0, 10:]-r[0, 10:], -.4)
    return dict(open_entry_extreme_included=True, open_exit_later_range_excluded=True,
                shorts_and_multiple_trades=True, per_trade_fee_at_exit=True, entry_slip_at_entry=True)


def allocations(base, vb_keys, context):
    empty = {k: v for k, v in base.items() if k not in vb_keys}
    result = dict(BASE=dict(base), EMPTY_VB=empty, ADD1={**base, "ANSON": 1},
                  ADD2={**base, "ANSON": 2})
    if context.startswith("150"):
        result["ADD4"] = {**base, "ANSON": 4}
    result["REPLACE_VB2"] = {**empty, "ANSON": 2}
    return result


def read_replay(lab):
    path, audit_path = REPLAY / "intended_apex_trades.csv", REPLAY / "intended_apex_audit.csv"
    t, a = pd.read_csv(path, parse_dates=["date"]), pd.read_csv(audit_path, parse_dates=["date"])
    if a.gridrow.duplicated().any() or a.account_eligible.dtype != bool:
        raise ValueError("Invalid source audit")
    if not np.array_equal(a.date.to_numpy(), pd.DatetimeIndex(lab.g.ts[a.gridrow.to_numpy(int)]).to_numpy()):
        raise ValueError("Source/calendar grid mismatch")
    if not set(lab.tr).issubset(set(a.gridrow)):
        raise ValueError("Incomplete audit trading calendar")
    dates = pd.DatetimeIndex(lab.g.ts[lab.tr])
    eligible_dates = set(a.loc[a.account_eligible, "date"])
    eligible = dates.isin(eligible_dates)
    keep = t.date.isin(eligible_dates)
    A.dump(OUT / "account_calendar.json", dict(total=lab.D, eligible=int(eligible.sum()),
        excluded_dates=dates[~eligible].strftime("%Y-%m-%d").tolist(),
        raw_trades=len(t), common_eligible_trades=int(keep.sum()),
        policies=dict(funded="common complete-day universe before circular20day blocks; changed adjacency disclosed",
                      evaluation="same real complete21day windows; calendar never compressed"),
        inputs={str(path.relative_to(ROOT)):A.file_sha(path), str(audit_path.relative_to(ROOT)):A.file_sha(audit_path)}))
    return t.loc[keep].copy(), eligible


def funded_summaries(results, fee, context, cohort):
    rows, paired = [], []
    for name, (a, b) in results.items():
        rows.append(dict(fee=fee, context=context, cohort=cohort, config=name,
            year1=a[:, 0].mean(), year1_p5=np.percentile(a[:, 0], 5), year1_p95=np.percentile(a[:, 0], 95),
            year2=b[:, 0].mean(), year2_p5=np.percentile(b[:, 0], 5), year2_p95=np.percentile(b[:, 0], 95),
            blown=b[:, 3].mean(), all6=(b[:, 1] == 6).mean(),
            days6=np.median(np.where(b[:, 1] == 6, b[:, 2], np.inf))))
        for ref in ("BASE", "EMPTY_VB"):
            aa, bb = results[ref]
            for metric, delta in (("year1", a[:, 0]-aa[:, 0]), ("year2", b[:, 0]-bb[:, 0]),
                                  ("blown", b[:, 3]-bb[:, 3]),
                                  ("all6", (b[:, 1] == 6).astype(float)-(bb[:, 1] == 6))):
                lo, hi = acc.paired_ci(delta, seed=902, n=5000)
                paired.append(dict(fee=fee, context=context, cohort=cohort, config=name, reference=ref,
                                   metric=metric, delta=delta.mean(), lo=lo, hi=hi))
    return rows, paired


def run_funded(lab, fb, fee, eligible, F50, F150):
    histories = {}
    for cohort, start in (("2018_plus", "2018-01-01"), ("2025_plus", "2025-01-01")):
        boot = fb.Boot(lab, start=start)
        boot.days = boot.days[eligible[boot.days]]
        histories[cohort] = np.concatenate([boot._histories(250, 500, 20, s) for s in (1, 2, 3, 4)])
        np.save(OUT / f"funded_histories_{cohort}.npy", histories[cohort])
    rows, paired, checks, resources = [], [], [], []
    for context, F in (("50K_funded", F50), ("150K_funded", F150)):
        base, parameters = A.funded_plans()[context], rules(F, context)
        results = {}
        for name, plan in allocations(base, ("VB_N", "VB_F"), context).items():
            started = time.monotonic()
            keys = sorted(plan)
            w, c = np.stack([lab.W[k] for k in keys]), np.stack([lab.C[k] for k in keys])
            names, size = lab._base({k: plan[k] for k in keys})
            assert names == keys
            if not np.isfinite(w).all() or not np.isfinite(c).all():
                raise ValueError("Nonfinite account input")
            table = acc.make_table(w, c, size)
            checks += parity_check(w, c, table, histories["2018_plus"][[0, 1, 17, 333, 999]],
                                   F, parameters, f"{fee}/{context}/{name}")
            for cohort, hist in histories.items():
                results.setdefault(cohort, {})[name] = (run_table(table, hist, 250, parameters),
                                                        run_table(table, hist, 500, parameters))
            resources.append(dict(fee=fee, context=context, config=name,
                seconds=time.monotonic()-started, max_quantity_states=int(table["counts"].max())))
            print(f"funded {fee:.2f} {context} {name} {resources[-1]['seconds']:.1f}s", flush=True)
            del w, c, table
            gc.collect()
        for cohort, result in results.items():
            a, b = funded_summaries(result, fee, context, cohort)
            rows += a
            paired += b
            np.savez_compressed(OUT / f"funded_results_{fee:.2f}_{context}_{cohort}.npz",
                **{f"{k}__{h}": result[k][i] for k in result for i, h in enumerate((250, 500))})
    A.dump(OUT / f"funded_parity_{fee:.2f}.json", checks)
    A.dump(OUT / f"funded_resources_{fee:.2f}.json", resources)
    return rows, paired


def evaluate(lab, scratch, fee, candidate, eligible):
    bundle = A.evaluation_parts(scratch, preregistration_commit=PREREG,
                               authorized_returns=True, fee=fee, grid=lab.g)
    cw, cr = candidate_paths(lab.g, candidate, fee)
    cw, cr = cw[lab.tr], cr[lab.tr]
    complete = np.array([s+21 <= lab.D and eligible[s:s+21].all() for s in range(lab.D)])
    rows, paired, references = [], [], []
    for context, part in bundle.contexts.items():
        pp, q = part.parts, part.quantities
        bw, br = sum(pp[k][0]*q[k] for k in q), sum(pp[k][1]*q[k] for k in q)
        ew, er = bw-pp["VB"][0]*q["VB"], br-pp["VB"][1]*q["VB"]
        raw = {}
        for name, plan in allocations({k:1 for k in pp}, ("VB",), context).items():
            start = time.monotonic()
            if name == "BASE":
                w, r = bw, br
            elif name == "EMPTY_VB":
                w, r = ew, er
            else:
                w0, r0 = (ew, er) if "REPLACE" in name else (bw, br)
                w, r = w0+cw*plan["ANSON"], r0+cr*plan["ANSON"]
            if context.startswith("50"):
                result = [part.challenge(w, r, np.arange(s, min(s+21, lab.D)), lambda p,c,n:1.)
                          for s in range(lab.D)]
            else:
                result = [part.challenge(w, r, s, lab.D, part.rules) for s in range(lab.D)]
            o = np.array([x[0] if x else "" for x in result])
            d = np.array([x[1] if x else 0 for x in result])
            raw[name] = (o, d)
            for cohort, (lo, hi) in COHORTS.items():
                ok = complete & np.asarray((bundle.dates >= lo) & (bundle.dates < hi))
                rows.append(dict(fee=fee, context=context, cohort=cohort, config=name,
                    starts=int(ok.sum()), passed=float((o[ok] == "pass").mean()),
                    failed=float((o[ok] == "fail").mean()), timed_out=float((o[ok] == "time").mean()),
                    median_pass_days=float(np.median(d[ok & (o == "pass")])),
                    changed_vs_base=float((o[ok] != raw["BASE"][0][ok]).mean())))
            if name not in ("BASE", "EMPTY_VB"):
                del w, r
            print(f"evaluation {fee:.2f} {context} {name} {time.monotonic()-start:.1f}s", flush=True)
        for name, (o, d) in raw.items():
            for cohort, (lo, hi) in COHORTS.items():
                mask = np.asarray((bundle.dates >= lo) & (bundle.dates < hi))
                valid = complete[mask]
                for ref in ("BASE", "EMPTY_VB"):
                    for metric, label in (("passed", "pass"), ("failed", "fail"), ("timed_out", "time")):
                        delta = (o[mask] == label).astype(float)-(raw[ref][0][mask] == label)
                        lo_ci, hi_ci = chronological_ci(delta, valid, seed=903, samples=5000, block=20)
                        paired.append(dict(fee=fee, context=context, cohort=cohort, config=name,
                            reference=ref, metric=metric, delta=float(delta[valid].mean()), lo=lo_ci, hi=hi_ci))
        frame = pd.DataFrame({f"{k}__{col}":v[i] for k,v in raw.items()
                              for i,col in enumerate(("outcome","days"))}, index=bundle.dates)
        frame["common_complete_21day_start"] = complete
        frame.to_csv(OUT / f"evaluation_starts_{fee:.2f}_{context}.csv", index_label="date")
        full = np.arange(lab.D)+21 <= lab.D
        for cohort, (lo, hi) in COHORTS.items():
            ok = full & np.asarray((bundle.dates >= lo) & (bundle.dates < hi))
            o, d = raw["BASE"]
            references.append(dict(fee=fee, context=context, cohort=cohort, starts=int(ok.sum()),
                passed=float((o[ok] == "pass").mean()), failed=float((o[ok] == "fail").mean()),
                timed_out=float((o[ok] == "time").mean()), median_pass_days=float(np.median(d[ok & (o == "pass")]))))
    A.dump(OUT / f"evaluation_full_calendar_BASE_{fee:.2f}.json", references)
    return rows, paired


def overlap(lab, t, eligible):
    dates = pd.DatetimeIndex(lab.g.ts[lab.tr])
    rows = []
    for context, base in A.funded_plans().items():
        names, sizes = lab._base(base)
        quantity = np.floor(sizes+1e-9)
        daily = sum(lab.C[k]*quantity[i] for i,k in enumerate(names))
        candidate = lab.C["ANSON"]
        for cohort, (lo, hi) in COHORTS.items():
            ok = eligible & np.asarray((dates >= lo) & (dates < hi))
            loss = ok & (daily < 0)
            rows.append(dict(context=context, cohort=cohort, eligible_days=int(ok.sum()),
                correlation=float(np.corrcoef(daily[ok], candidate[ok])[0,1]),
                plan_loss_days=int(loss.sum()), joint_loss_days=int((loss & (candidate < 0)).sum()),
                candidate_net_on_plan_loss_days=float(candidate[loss].sum())))
        pd.DataFrame(dict(PLAN_FULL_SIZE=daily, ANSON_1=candidate), index=dates).loc[eligible].to_csv(
            OUT / f"daily_joint_pnl_{context}.csv", index_label="date")
    pd.DataFrame(rows).to_csv(OUT / "overlap_daily.csv", index=False)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--scratch", default="scratch_data")
    ap.add_argument("--fixtures-only", action="store_true")
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    A.authorize(PREREG, True)
    A.dump(OUT / "path_fixtures.json", path_fixtures())
    started = time.monotonic()
    with A.pinned_imports(args.scratch):
        F50, F150 = importlib.import_module("funded_sim"), importlib.import_module("funded_sim150")
        fb = importlib.import_module("funded_bootstrap")
        synthetic_checks(F50, F150)
        if args.fixtures_only:
            return
        provenance = json.loads(MANIFEST.read_text())
        if provenance["expanded_cache_sha256"] != A.file_sha(PREPARED) or provenance["fee"] != 1.04:
            raise ValueError("Expanded plan cache differs from saved current baseline")
        with PREPARED.open("rb") as f:
            lab = pickle.load(f)
        t, eligible = read_replay(lab)
        fr, fd, er, ed = [], [], [], []
        fee_totals = {}
        for fee in (1.04, 1.24):
            if fee > 1.04:
                fee_totals = lab.real_fees(.20, list(set(A.P.CURRENT_PLAN) | {"RS", "DT"}))
            w, r = candidate_paths(lab.g, t, fee)
            lab.W["ANSON"], lab.C["ANSON"] = w[lab.tr], r[lab.tr, -1]
            del w, r
            if fee == 1.04:
                overlap(lab, t, eligible)
            a,b = run_funded(lab, fb, fee, eligible, F50, F150)
            fr += a
            fd += b
            pd.DataFrame(fr).to_csv(OUT / "funded_summary.csv", index=False)
            pd.DataFrame(fd).to_csv(OUT / "funded_paired_differences.csv", index=False)
            a,b = evaluate(lab, args.scratch, fee, t, eligible)
            er += a
            ed += b
            pd.DataFrame(er).to_csv(OUT / "evaluation_summary.csv", index=False)
            pd.DataFrame(ed).to_csv(OUT / "evaluation_paired_differences.csv", index=False)
    A.dump(OUT / "reproduction.json", dict(preregistration=PREREG, pin=A.PIN,
        prepared_cache_sha256=A.file_sha(PREPARED), prepared_manifest_sha256=A.file_sha(MANIFEST),
        scripts={p:A.file_sha(ROOT/"analysis"/p) for p in (Path(__file__).name,"codex_anson_plan.py","codex_ob_v2_accounts.py")},
        funded=dict(contexts=2, allocations={"50K":5,"150K":6}, fees=[1.04,1.24],
            horizons=[250,500], paired_histories=1000, seeds=[1,2,3,4], circular_block=20,
            production_parity_expected=220, fixed_history_indices=[0,1,17,333,999]),
        evaluation=dict(real_full_windows=21, chronological_CI_block=20, resamples=5000,
            tie_handling={"50K":"pass first","150K":"breach first"}),
        sensitivity_extra_fee_totals_per_micro=fee_totals, seconds=time.monotonic()-started,
        limits=A.P.BASELINE_LIMITS+[
            "Prior50Kpreparedcache has a small unresolved gap against the published funded reference.",
            "150Kbaseline retains fractional pre-cushion sizes from the published bench.",
            "Corrected150Kevaluation uses actual integer quantities after dollar-risk scaling; old41.6% is not the same input baseline.",
            "Shared eligibility omits missing/stress days; funded resampling changes adjacency.",
            "Candidate reserves entry slippage while open and pays RTcommission at exit; inherited Apex baseline reserves full RTcommission from entry. Closed totals match but fee-mark timing is asymmetric.",
            "No candidate protective stop exists; open-position risks use observed minute extremes.",
            "Daily overlap cannot establish an offset before breach."]))
    print(f"completed {time.monotonic()-started:.1f}s", flush=True)


if __name__ == "__main__":
    main()
