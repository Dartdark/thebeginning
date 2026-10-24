"""Frozen night-volume-switch joint accounts (preregistration affb482).

Consumes the separately audited replay; no signal search or cache rebuild.
The source's open entry holds its entry minute; open exits exclude that
minute's later range. All account allocations share the complete-session set.
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
import codex_or_pullback_plan as P
from codex_or_pullback_portfolio import dump, sha

PREREG = "affb482cf284f777b09b6116914d4fd2399284b0"
CONTEXT = "febc65f1573040abf9a697d1d3468e1bce48c4c0"
MODES = ("literal_delay", "immediate_stop")
OUT = ROOT / "analysis/outputs/codex_night_volume_switch/accounts"
REPLAY = OUT.parent / "replay"
BASE_MANIFEST = ROOT / "analysis/outputs/codex_or_pullback/baseline/current_plan_manifest.json"
COHORTS = {"2018_plus": ("2018-01-01", "2100-01-01"),
           "2018_22": ("2018-01-01", "2023-01-01"),
           "2023_plus": ("2023-01-01", "2100-01-01")}


def verify_context(cache):
    """Verify exact prepared-baseline dependencies, roster, and immutable cache."""
    P._git("cat-file", "-e", f"{PREREG}^{{commit}}")
    manifest = json.loads(BASE_MANIFEST.read_text(encoding="utf-8"))
    sources = manifest["sources"]
    comparisons = []
    for name, meta in sources["modules"].items():
        newer = P._git("rev-parse", f'{CONTEXT}:{meta["repository_path"]}').decode().strip()
        comparisons.append(dict(module=name, older=meta["git_blob"], newer=newer,
                                unchanged=meta["git_blob"] == newer))
    if len(comparisons) != 27 or not all(x["unchanged"] for x in comparisons):
        raise ValueError("Prepared current-plan dependencies changed; do not silently rebuild")
    for meta in sources["inputs"].values():
        if P._git("rev-parse", f'{CONTEXT}:{meta["repository_path"]}').decode().strip() != meta["git_blob"]:
            raise ValueError("Pinned RS source/reference changed")
    for name in ("real_fee_bench",):
        a = P._git("rev-parse", f"{P.PINNED_REF}:analysis/{name}.py").decode().strip()
        b = P._git("rev-parse", f"{CONTEXT}:analysis/{name}.py").decode().strip()
        if a != b:
            raise ValueError("Latest real-fee current plan changed")
        comparisons.append(dict(module=name, older=a, newer=b, unchanged=True))
    plan = {k: list(v) if isinstance(v, tuple) else v for k, v in P.CURRENT_PLAN.items()}
    if manifest["plan"] != plan or manifest["fee_per_micro_round_trip"] != 1.04:
        raise ValueError("Prepared plan roster or fees differ")
    cache_sha = sha(cache)
    if cache_sha != "699057ea248172f91ee64f7f3c4aad72347434063e64fab836576da53877067b":
        raise ValueError("Prepared baseline cache changed")
    result = dict(prepared_ref=P.PINNED_REF, current_context=CONTEXT,
                  unchanged_dependency_count=27, comparisons=comparisons,
                  rs_source_and_reference_unchanged=True, roster=plan,
                  prepared_cache_sha256=cache_sha, rebuilt=False,
                  baseline_manifest_sha256=sha(BASE_MANIFEST))
    dump(OUT / "context_reuse.json", result)
    return result


def candidate_paths(g, trades, fee=1.04):
    """Per-MNQ adverse and realized marks, with executable open/stop phases.

    Fee and entry slippage are visible at open entry. The exit slippage is
    visible at the fill. A filled stop caps its minute's range at the actual
    worse-gap/rounded-stop fill, not at the raw source bracket. Protection
    delay is already reflected by the immutable replay's exit and fill phase.
    """
    w, r = np.zeros(g.o.shape), np.zeros(g.o.shape)
    entry_cost = float(fee) + .5
    for x in trades.itertuples():
        d, e, z, side = int(x.day), int(x.entry_j), int(x.exit_j), int(x.side)
        if x.entry_phase != "open" or not (0 <= e <= z < g.o.shape[1]):
            raise ValueError("Expected same-date open-entry ledger")
        if side not in (-1, 1) or int(x.missing_held_minutes) or bool(x.cross_date):
            raise ValueError("Unknown candidate return included")
        net = (float(x.exit)-float(x.entry))*side*2.0-float(fee)-1.0
        end = z + int(x.exit_phase != "open")
        adverse = g.l[d, e:end] if side > 0 else g.h[d, e:end]
        if not np.isfinite(adverse).all():
            raise ValueError("Missing held minute OHLC")
        marks = (adverse-float(x.entry))*side*2.0-entry_cost
        if x.exit_phase != "open":
            if str(x.kind_label) != "stop":
                raise ValueError("Unexpected non-stop intrabar fill")
            # The final held minute terminates at the accepted stop fill.
            marks[-1] = net
        w[d, e:end] += marks
        w[d, z if x.exit_phase == "open" else z+1:] += net
        r[d, z:] += net
        if not np.isclose(net, float(x.gross_points)*2-float(fee)-1, rtol=0, atol=1e-7):
            raise ValueError("Replay gross and account net disagree")
    return w, r


def path_fixtures():
    from types import SimpleNamespace
    g = SimpleNamespace(o=np.full((1, 12), 100.), l=np.full((1, 12), 99.),
                        h=np.full((1, 12), 101.))
    g.l[0, 2], g.l[0, 5] = 10., 1.
    common = dict(day=0, entry_j=2, exit_j=5, side=1, entry=100.,
                  entry_phase="open", missing_held_minutes=0, cross_date=False)
    t = pd.DataFrame([dict(**common, exit=101., gross_points=1.,
                           exit_phase="open", kind_label="time")])
    w, r = candidate_paths(g, t)
    np.testing.assert_allclose(w[0, 2], -181.54)
    np.testing.assert_allclose(w[0, 3:5], -3.54)
    np.testing.assert_allclose(w[0, 5:], -.04)
    assert not r[0, :5].any()
    np.testing.assert_allclose(r[0, 5:], -.04)
    t = pd.DataFrame([dict(**common, exit=95., gross_points=-5.,
                           exit_phase="intrabar", kind_label="stop")])
    w, r = candidate_paths(g, t)
    np.testing.assert_allclose(w[0, 5:], -12.04)
    np.testing.assert_allclose(r[0, 5:], -12.04)
    # Stop-gap open fills exclude the later minute range, too.
    t.loc[0, ["exit", "gross_points", "exit_phase"]] = [90., -10., "open"]
    w, r = candidate_paths(g, t)
    np.testing.assert_allclose(w[0, 5:], -22.04)
    w2, r2 = candidate_paths(g, t, 1.24)
    np.testing.assert_allclose(w2[0, 2:]-w[0, 2:], -.2)
    np.testing.assert_allclose(r2[0, 5:]-r[0, 5:], -.2)
    return dict(open_entry_minute_held=True, unprotected_entry_range_retained=True,
                market_exit_later_OHLC_excluded=True, stop_minute_capped_at_fill=True,
                worse_gap_open_exit_range_excluded=True, fee_and_slippage_timing=True)


def read_replay(lab):
    ledgers, audits, eligible_sets, inputs = {}, {}, [], {}
    dates = pd.DatetimeIndex(lab.g.ts[lab.tr]).normalize()
    for mode in MODES:
        tp, ap = REPLAY / f"{mode}_trades.csv", REPLAY / f"{mode}_audit.csv"
        t, a = pd.read_csv(tp, parse_dates=["date"]), pd.read_csv(ap, parse_dates=["date"])
        if a.gridrow.duplicated().any():
            raise ValueError("Duplicate replay audit grid row")
        rows = a.gridrow.to_numpy(int)
        if not np.array_equal(a.date.to_numpy(), pd.DatetimeIndex(lab.g.ts[rows]).to_numpy()):
            raise ValueError("Replay audit calendar differs from prepared baseline")
        if not set(lab.tr).issubset(set(rows)):
            raise ValueError("Replay audit omits current-plan trading dates")
        if a.account_eligible.dtype != bool or (len(t) and t.cross_date.dtype != bool):
            raise ValueError("Expected explicit Boolean audit flags")
        eligible_sets.append(set(a.loc[a.account_eligible, "date"].dt.normalize()))
        ledgers[mode], audits[mode] = t, a
        inputs[str(tp.relative_to(ROOT))], inputs[str(ap.relative_to(ROOT))] = sha(tp), sha(ap)
    eligible_dates = set.intersection(*eligible_sets)
    eligible = dates.isin(eligible_dates)
    counts = {}
    for mode, t in ledgers.items():
        keep = t.date.dt.normalize().isin(eligible_dates)
        counts[mode] = dict(total_ledger_trades=len(t), account_eligible_trades=int(keep.sum()),
                            excluded_trades=int((~keep).sum()))
        ledgers[mode] = t.loc[keep].copy()
    dump(OUT / "account_calendar.json", dict(eligible=int(eligible.sum()), total=lab.D,
         excluded_dates=[str(x.date()) for x in dates[~eligible]], trade_counts=counts,
         funded_policy="identical common complete days, circular blocks after common restriction",
         evaluation_policy="complete real 21-day windows; calendar never compressed", inputs=inputs))
    return ledgers, eligible, inputs


def allocations(base, slot):
    empty = {k: v for k, v in base.items() if k != slot}
    plans = dict(BASE=dict(base), EMPTY_ONB=empty)
    for mode in MODES:
        plans[f"{mode}__ADD_1"] = {**base, mode: 1}
        plans[f"{mode}__ADD_2"] = {**base, mode: 2}
        plans[f"{mode}__REPLACE_ONB_2"] = {**empty, mode: 2}
    assert len(plans) == 8
    return plans


def funded_summary(results, acc, fee, cohort):
    rows, diffs = [], []
    for name, (a, b) in results.items():
        rows.append(dict(fee=fee, cohort=cohort, config=name,
            year1=a[:, 0].mean(), year1_p5=np.percentile(a[:, 0], 5),
            year1_p95=np.percentile(a[:, 0], 95), year2=b[:, 0].mean(),
            year2_p5=np.percentile(b[:, 0], 5), year2_p95=np.percentile(b[:, 0], 95),
            blown=b[:, 3].mean(), all6=(b[:, 1] == 6).mean(),
            days6=np.median(np.where(b[:, 1] == 6, b[:, 2], np.inf))))
        for ref in ("BASE", "EMPTY_ONB"):
            aa, bb = results[ref]
            for metric, delta in (("year1", a[:, 0]-aa[:, 0]),
                                  ("year2", b[:, 0]-bb[:, 0]),
                                  ("blown", b[:, 3]-bb[:, 3]),
                                  ("all6", (b[:, 1] == 6).astype(float)-(bb[:, 1] == 6))):
                lo, hi = acc.paired_ci(delta, seed=902, n=5000)
                diffs.append(dict(fee=fee, cohort=cohort, config=name, reference=ref,
                                  metric=metric, delta=delta.mean(), lo=lo, hi=hi))
    return rows, diffs


def run_funded(lab, fb, fs, fee, eligible):
    import codex_ob_v2_accounts as acc
    acc.F = fs
    histories = {}
    for cohort, start in (("2018_plus", "2018-01-01"), ("2023_plus", "2023-01-01")):
        boot = fb.Boot(lab, start=start)
        boot.days = boot.days[eligible[boot.days]]
        histories[cohort] = np.concatenate([boot._histories(250, 500, 20, s) for s in (1, 2, 3, 4)])
        np.save(OUT / f"funded_histories_{cohort}.npy", histories[cohort])
    all_results, checks, resources = {}, [], []
    for name, plan in allocations(P.CURRENT_PLAN, "ONB_ML2_MC").items():
        start = time.monotonic()
        keys = sorted(plan)
        w, c = np.stack([lab.W[k] for k in keys]), np.stack([lab.C[k] for k in keys])
        names, sizes = lab._base({k: plan[k] for k in keys})
        assert names == keys
        if not np.isfinite(w).all() or not np.isfinite(c).all():
            raise ValueError("Nonfinite account path")
        table = acc.make_table(w, c, sizes)
        checks.extend(acc.parity_check(w, c, table, histories["2018_plus"][[0, 1, 17, 333, 999]],
                                       f"{fee}/{name}"))
        for cohort, h in histories.items():
            all_results.setdefault(cohort, {})[name] = (acc.run_table(table, h, 250),
                                                        acc.run_table(table, h, 500))
        resources.append(dict(fee=fee, config=name, seconds=time.monotonic()-start,
                              max_quantity_states=int(table["counts"].max())))
        print(f"funded {fee:.2f} {name} {resources[-1]['seconds']:.1f}s", flush=True)
        del w, c, table
        gc.collect()
    rows, diffs = [], []
    for cohort, results in all_results.items():
        a, b = funded_summary(results, acc, fee, cohort)
        rows += a
        diffs += b
        np.savez_compressed(OUT / f"funded_results_{fee:.2f}_{cohort}.npz",
            **{f"{k}__{h}": results[k][i] for k in results for i, h in enumerate((250, 500))})
    dump(OUT / f"funded_parity_{fee:.2f}.json", checks)
    dump(OUT / f"funded_resources_{fee:.2f}.json", resources)
    return rows, diffs


def run_evaluation(lab, scratch, fee, ledgers, eligible):
    import codex_ob_v2_accounts as acc
    parts = P.evaluation_parts(scratch, preregistration_commit=PREREG,
                              authorized_returns=True, fee=fee, grid=lab.g)
    pp, q = parts.parts, parts.quantities
    bw = sum(pp[k][0]*q[k] for k in q)
    br = sum(pp[k][1]*q[k] for k in q)
    ew, er = bw-pp["ONB30"][0]*q["ONB30"], br-pp["ONB30"][1]*q["ONB30"]
    complete = np.array([i+parts.max_days <= lab.D and eligible[i:i+parts.max_days].all()
                         for i in range(lab.D)])
    raw, rows, diffs = {}, [], []
    base_sizes = {k: 1 for k in pp}
    for name, plan in allocations(base_sizes, "ONB30").items():
        start = time.monotonic()
        if name == "BASE":
            w, r = bw, br
        elif name == "EMPTY_ONB":
            w, r = ew, er
        else:
            mode = name.split("__")[0]
            n = plan[mode]
            cw, cr = candidate_paths(lab.g, ledgers[mode], fee)
            basew, baser = (ew, er) if "REPLACE" in name else (bw, br)
            w, r = basew+cw[lab.tr]*n, baser+cr[lab.tr]*n
            del cw, cr
        results = [parts.challenge(w, r, np.arange(s, min(s+parts.max_days, lab.D)),
                                   lambda p, c, n: 1.) for s in range(lab.D)]
        outcome = np.array([x[0] if x else "" for x in results])
        days = np.array([x[1] if x else 0 for x in results])
        raw[name] = (outcome, days)
        for cohort, (lo, hi) in COHORTS.items():
            mask = np.asarray((parts.dates >= lo) & (parts.dates < hi))
            ok = complete & mask
            rows.append(dict(fee=fee, cohort=cohort, config=name, starts=int(ok.sum()),
                passed=float((outcome[ok] == "pass").mean()),
                failed=float((outcome[ok] == "fail").mean()),
                timed_out=float((outcome[ok] == "time").mean()),
                median_pass_days=float(np.median(days[ok & (outcome == "pass")])),
                changed_vs_base=float((outcome[ok] != raw["BASE"][0][ok]).mean())))
            for ref in ("BASE", "EMPTY_ONB"):
                if ref not in raw:
                    continue
                for metric, label in (("passed", "pass"), ("failed", "fail"), ("timed_out", "time")):
                    # Keep the real chronological starts in each cohort: resample
                    # 20-start blocks, then omit ineligible starts inside draws.
                    delta = (outcome[mask] == label).astype(float)-(raw[ref][0][mask] == label)
                    valid = complete[mask]
                    ci = chronological_ci(delta, valid)
                    diffs.append(dict(fee=fee, cohort=cohort, config=name, reference=ref,
                        metric=metric, delta=float(delta[valid].mean()), lo=ci[0], hi=ci[1],
                        chronological_block=20, resamples=5000))
        print(f"evaluation {fee:.2f} {name} {time.monotonic()-start:.1f}s", flush=True)
        if name not in ("BASE", "EMPTY_ONB"):
            del w, r
    # BASE was evaluated before EMPTY_ONB existed; append its other paired control.
    for cohort, (lo, hi) in COHORTS.items():
        mask = np.asarray((parts.dates >= lo) & (parts.dates < hi))
        valid = complete[mask]
        for metric, label in (("passed", "pass"), ("failed", "fail"), ("timed_out", "time")):
            delta = (raw["BASE"][0][mask] == label).astype(float)-(raw["EMPTY_ONB"][0][mask] == label)
            ci = chronological_ci(delta, valid)
            diffs.append(dict(fee=fee, cohort=cohort, config="BASE", reference="EMPTY_ONB",
                              metric=metric, delta=float(delta[valid].mean()), lo=ci[0], hi=ci[1],
                              chronological_block=20, resamples=5000))
    frame = pd.DataFrame({f"{k}__{col}": v[i] for k, v in raw.items()
                          for i, col in enumerate(("outcome", "days"))}, index=parts.dates)
    frame["common_complete_21day_start"] = complete
    frame.to_csv(OUT / f"evaluation_starts_{fee:.2f}.csv", index_label="date")
    full = np.arange(lab.D)+parts.max_days <= lab.D
    o, d = raw["BASE"]
    reference = []
    for cohort, (lo, hi) in COHORTS.items():
        mask = np.asarray((parts.dates >= lo) & (parts.dates < hi)) & full
        reference.append(dict(fee=fee, cohort=cohort, starts=int(mask.sum()),
            passed=float((o[mask] == "pass").mean()), failed=float((o[mask] == "fail").mean()),
            timed_out=float((o[mask] == "time").mean()),
            median_pass_days=float(np.median(d[mask & (o == "pass")]))))
    dump(OUT / f"evaluation_full_calendar_BASE_{fee:.2f}.json", reference)
    return rows, diffs


def chronological_ci(delta, valid, seed=903, samples=5000, block=20):
    """Paired circular start blocks without compressing missing calendar starts."""
    delta, valid = np.asarray(delta), np.asarray(valid, bool)
    rng, means = np.random.default_rng(seed), np.empty(samples)
    length = len(delta)
    for start in range(0, samples, 100):
        n = min(100, samples-start)
        st = rng.integers(0, length, (n, int(np.ceil(length/block))))
        idx = ((st[:, :, None]+np.arange(block)) % length).reshape(n, -1)[:, :length]
        count = valid[idx].sum(axis=1)
        means[start:start+n] = (delta[idx]*valid[idx]).sum(axis=1)/count
    return np.percentile(means, [2.5, 97.5]).tolist()


def descriptive_overlap(lab, ledgers, eligible):
    dates = pd.DatetimeIndex(lab.g.ts[lab.tr])
    names, b = lab._base(P.CURRENT_PLAN)
    q = np.floor(b+1e-9)
    daily = sum(lab.C[k]*q[i] for i, k in enumerate(names))
    frame = pd.DataFrame({k: lab.C[k] for k in names}, index=dates)
    frame["PLAN_FULL_SIZE"] = daily
    rows = []
    for mode in MODES:
        cc = lab.C[mode]
        frame[mode] = cc
        for cohort, (lo, hi) in COHORTS.items():
            ok = eligible & np.asarray((dates >= lo) & (dates < hi))
            loss = ok & (daily < 0)
            rows.append(dict(mode=mode, cohort=cohort, eligible_days=int(ok.sum()),
                plan_loss_days=int(loss.sum()), joint_loss_days=int((loss & (cc < 0)).sum()),
                candidate_net_on_plan_loss_days=float(cc[loss].sum()),
                candidate_avg_on_plan_loss_days=float(cc[loss].mean()),
                correlation_with_plan=float(np.corrcoef(daily[ok], cc[ok])[0, 1])))
    frame.loc[eligible].to_csv(OUT / "daily_joint_pnl_1.04.csv", index_label="date")
    frame.loc[eligible].corr().to_csv(OUT / "daily_correlations_1.04.csv")
    pd.DataFrame(rows).to_csv(OUT / "daily_overlap_summary.csv", index=False)


def occupancy_report(lab, scratch, ledgers, eligible):
    """Reuse reviewed occupancy arithmetic; avoid loading a second large lab."""
    import codex_or_pullback_exposure as ex
    pf, build = importlib.import_module("portfolio"), importlib.import_module("build_lab")
    bridge = importlib.import_module("bridge_monday_confirm")
    dates, shape = pd.DatetimeIndex(lab.g.ts[lab.tr]), (lab.D, lab.g.o.shape[1])
    lookup = {int(d): i for i, d in enumerate(lab.tr)}
    flags = pd.read_pickle(scratch / "single_print_sessions.pkl").flag.reindex(dates).fillna(False).to_numpy(bool)
    raw = {k: pf.load_mc(lab.g, build.REPORTS[k][0])
           for k in ("VB", "ONB_ML2_MC", "MON_MC", "EOS", "LDF_MC", "NFP_MC")}
    raw["MON_BR_MC"] = bridge.load_bridge_mc(lab.g)
    rs = pd.read_csv(ROOT / "analysis/outputs/codex_or_pullback/baseline/baseline_rs_replay.csv")
    raw["RS_L"] = rs[rs.side > 0].copy()
    byrow = dict(zip(lab.tr, flags))
    vbflags = raw["VB"].day.map(byrow).fillna(False).to_numpy(bool)
    raw["VB_N"], raw["VB_F"] = raw["VB"].loc[~vbflags], raw["VB"].loc[vbflags]
    names, b = lab._base({k: P.CURRENT_PLAN[k] for k in ex.NQ_NAMES})
    q = np.floor(b+1e-9)
    current, metadata = {}, {}
    for i, name in enumerate(names):
        current[name] = ex.occupancy(raw[name], lookup, q[i], shape)
        count = np.bincount(raw[name].day.to_numpy(int), minlength=len(lab.g.ts))[lab.tr]
        np.testing.assert_array_equal(count, lab.N[name], err_msg=f"Occupancy ledger count {name}")
        metadata[name] = dict(**current[name][2], daily_trade_count_matches_cached_lab=True)
    total_long, total_short = sum(x[0] for x in current.values()), sum(x[1] for x in current.values())
    gross = total_long+total_short
    onb = current["ONB_ML2_MC"][0]+current["ONB_ML2_MC"][1]
    rows, legs = [], []
    for mode, t in ledgers.items():
        t = t.copy()
        t["j0"], t["j1"] = t.entry_j, t.exit_j-(t.exit_phase == "open").astype(int)
        cl, cs, _ = ex.occupancy(t, lookup, np.ones(lab.D), shape)
        held = cl+cs > 0
        same, opp = np.where(cl > 0, total_long, total_short), np.where(cl > 0, total_short, total_long)
        for cohort, (lo, hi) in COHORTS.items():
            daymask = eligible & np.asarray((dates >= lo) & (dates < hi))
            mask = held & daymask[:, None]
            n = int(mask.sum())
            if not n:
                continue
            fraction = lambda a: float((mask & a).sum()/n)
            maximum = lambda a: int(a[mask].max(initial=0))
            common = dict(mode=mode, cohort=cohort, candidate_held_minutes=n,
                candidate_held_days=int(mask.any(axis=1).sum()),
                any_current_nq_overlap_fraction=fraction(gross > 0),
                onb_overlap_fraction=fraction(onb > 0), same_side_overlap_fraction=fraction(same > 0),
                opposite_side_overlap_fraction=fraction(opp > 0),
                max_current_gross_mnq_while_candidate_held=maximum(gross))
            for size in (1, 2):
                rows.append(dict(**common, candidate_mnq=size,
                    max_gross_add_mnq=maximum(gross)+size,
                    max_gross_replace_onb_mnq=maximum(gross-onb)+size))
            for leg, (ll, ss, _) in current.items():
                legs.append(dict(mode=mode, cohort=cohort, leg=leg,
                    candidate_held_minutes=n, overlap_minutes=int((mask & (ll+ss > 0)).sum()),
                    overlap_fraction=fraction(ll+ss > 0),
                    same_side_fraction=fraction(np.where(cl > 0, ll, ss) > 0),
                    opposite_side_fraction=fraction(np.where(cl > 0, ss, ll) > 0)))
    pd.DataFrame(rows).to_csv(OUT / "occupancy_summary.csv", index=False)
    pd.DataFrame(legs).to_csv(OUT / "occupancy_per_leg.csv", index=False)
    dump(OUT / "occupancy_metadata.json", dict(legs=metadata,
        scope="full-size integer MNQ gross; opposite positions never netted; descriptive only",
        timing="candidate entry minute inclusive; open exit minute excluded; MC endpoints inclusive"))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--scratch", default=str(ROOT / "scratch_data"))
    ap.add_argument("--baseline-cache", default=str(ROOT / "agents/codex/runtime/or_pullback_current_lab.pkl"))
    ap.add_argument("--fixtures-only", action="store_true")
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    dump(OUT / "path_fixtures.json", path_fixtures())
    if args.fixtures_only:
        return
    started = time.monotonic()
    scratch, cache = Path(args.scratch).resolve(), Path(args.baseline_cache).resolve()
    context = verify_context(cache)
    with P.pinned_imports(P.DEFAULT_RUNTIME, scratch):
        fs, fb = importlib.import_module("funded_sim"), importlib.import_module("funded_bootstrap")
        with cache.open("rb") as handle:
            lab = pickle.load(handle)
        ledgers, eligible, inputs = read_replay(lab)
        fr, fd, er, ed = [], [], [], []
        for fee in (1.04, 1.24):
            if fee > 1.04:
                lab.real_fees(.20, list(P.CURRENT_PLAN))
            for mode, t in ledgers.items():
                w, r = candidate_paths(lab.g, t, fee)
                lab.W[mode], lab.C[mode] = w[lab.tr], r[lab.tr, -1]
                del w, r
            if fee == 1.04:
                descriptive_overlap(lab, ledgers, eligible)
                occupancy_report(lab, scratch, ledgers, eligible)
            a, b = run_funded(lab, fb, fs, fee, eligible)
            fr += a
            fd += b
            pd.DataFrame(fr).to_csv(OUT / "funded_summary.csv", index=False)
            pd.DataFrame(fd).to_csv(OUT / "funded_paired_differences.csv", index=False)
            a, b = run_evaluation(lab, scratch, fee, ledgers, eligible)
            er += a
            ed += b
            pd.DataFrame(er).to_csv(OUT / "evaluation_summary.csv", index=False)
            pd.DataFrame(ed).to_csv(OUT / "evaluation_paired_differences.csv", index=False)
    prior = ROOT / "analysis/outputs/codex_or_pullback_portfolio/baseline_reference.json"
    dump(OUT / "reproduction.json", dict(preregistration_commit=PREREG, context=context,
        paired_histories=1000, horizons=[250, 500], block=20, seeds=[1, 2, 3, 4],
        strategy_variants=2, fees=[1.04, 1.24], allocations_per_fee=8,
        eligible_days=int(eligible.sum()), seconds=time.monotonic()-started,
        replay_inputs=inputs, prepared_cache_sha256=sha(cache),
        scripts={name: sha(ROOT / "analysis" / name) for name in
                 (Path(__file__).name, "codex_ob_v2_accounts.py", "codex_or_pullback_plan.py",
                  "codex_or_pullback_exposure.py")},
        unrestricted_funded_reference=dict(path=str(prior.relative_to(ROOT)), sha256=sha(prior),
            result=json.loads(prior.read_text()), reused_without_rerun=True),
        limits=P.BASELINE_LIMITS + [
            "Small prepared-cache vs published full-calendar funded reference gap remains unresolved.",
            "Evaluation preserves inherited same-minute pass-before-breach priority.",
            "Descriptive daily P&L and occupancy do not establish pre-breach hedging.",
            "No broker acceptance, disconnect protection, or MultiCharts compilation is verified."]))
    print(f"completed {time.monotonic()-started:.1f}s", flush=True)


if __name__ == "__main__":
    main()
