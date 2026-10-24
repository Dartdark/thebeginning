"""Frozen NQDB2 account adapter; importing this file computes no returns.

--prepare checks sources/cache presence only. --fixtures-only uses invented bars.
--run requires the root's committed preregistration and passed design-gate JSON.
Only the explicitly preregistered Apex-safe Veto1 proxy enters account scoring.
Literal-source carries remain in its standalone ledger and are never repaired here.

Reuses codex_or_pullback_plan's current roster/fees, the existing exact funded
quantity-state accelerator, and the reviewed chronological paired bootstrap.
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

ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / "agents/codex/runtime/nqdb2_plan_analysis"
OUT = ROOT / "analysis/outputs/codex_nqdb2_test/accounts"
CONTEXT = "e34d71cd3537a9f019d2521e280fc92f3ffdb4c6"
FEES = (1.04, 1.24)
COHORTS = {"2018_plus": ("2018-01-01", "2100-01-01"),
           "2018_22": ("2018-01-01", "2023-01-01"),
           "2023_plus": ("2023-01-01", "2100-01-01")}


def dump(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, default=str, allow_nan=True) + "\n")


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def prepare(scratch, runtime=RUNTIME):
    """Materialize exact Git sources if absent; never deserialize/read prices.

    A fresh complete clone needs no unpublished runtime: the existing pinned
    helper traverses transitive imports using git show. Only that source
    materializer is called; no research module or its main block is imported.
    """
    runtime, scratch = Path(runtime), Path(scratch)
    import codex_or_pullback_plan as P
    if not (runtime / "manifest.json").is_file():
        P.prepare_sources(runtime)
    manifest = json.loads((runtime / "manifest.json").read_text())
    if not (runtime / "current_context.json").is_file():
        paths = [meta["repository_path"] for meta in manifest["modules"].values()]
        paths += [meta["repository_path"] for meta in manifest["inputs"].values()]
        paths += ["analysis/real_fee_bench.py"]
        comparisons = [dict(path=path,
            pinned=P._git("rev-parse", f'{manifest["ref"]}:{path}').decode().strip(),
            current=P._git("rev-parse", f"{CONTEXT}:{path}").decode().strip()) for path in paths]
        dump(runtime / "current_context.json", dict(pinned=manifest["ref"], current=CONTEXT, comparisons=comparisons))
    context = json.loads((runtime / "current_context.json").read_text())
    if context["current"] != CONTEXT or context["pinned"] != manifest["ref"]:
        raise ValueError("Unexpected frozen baseline context")
    if not all(x["pinned"] == x["current"] for x in context["comparisons"]):
        raise ValueError("Baseline dependencies changed")
    for group, suffix in (("modules", ".py"), ("inputs", "")):
        for name, meta in manifest[group].items():
            path = runtime / (name + suffix)
            if sha(path) != meta["sha256"]:
                raise ValueError(f"Pinned source changed: {path}")
    required = ("lab.pkl", "g24.pkl", "ge.pkl", "cl.pkl", "s_rank_gap2.pkl",
                "single_print_sessions.pkl")
    missing = [str(scratch / name) for name in required if not (scratch / name).is_file()]
    if missing:
        raise FileNotFoundError("Existing caches missing; never rebuild automatically: " + str(missing))
    return dict(source_ref=manifest["ref"], current_context=CONTEXT,
                verified_modules=len(manifest["modules"]), verified_inputs=len(manifest["inputs"]),
                sources_sha256=sha(runtime / "manifest.json"),
                context_sha256=sha(runtime / "current_context.json"),
                existing_caches={n: (scratch / n).stat().st_size for n in required},
                returns_computed=False)


def require_gate(prereg, gate_path, ledger_path):
    """Root writes this artifact only after its frozen 2018--22 decision."""
    if not prereg or not gate_path:
        raise PermissionError("Root preregistration and design gate are required")
    gate = json.loads(Path(gate_path).read_text())
    if gate.get("design_gate_passed") is not True:
        raise PermissionError("2018--22 design gate did not pass; account work stops")
    if gate.get("preregistration_commit") != prereg:
        raise ValueError("Account and gate preregistrations differ")
    if gate.get("candidate") != "apex_safe_veto1":
        raise ValueError("Only the frozen Apex-safe Veto1 proxy may enter accounts")
    for field in ("account_run_authorized", "implementation_checks_clear", "recent_net_positive"):
        if gate.get(field) is not True:
            raise PermissionError(f"Account prerequisite is not explicitly clear: {field}")
    for field in ("censored_positions", "unknown_account_days", "apex_carry_violations"):
        if gate.get(field) != 0 or isinstance(gate.get(field), bool):
            raise ValueError(f"Root must certify a complete Apex-safe replay: {field}=0")
    if gate.get("candidate_ledger_sha256") != sha(ledger_path):
        raise ValueError("Candidate ledger was not frozen by the root gate")
    return gate


def audit_candidate_bundle(scratch, runtime, out, prereg, authorize=False):
    """Join already frozen ledgers; inspect prices/calendar, never replay rules."""
    out, scratch = Path(out), Path(scratch)
    source = out.parent
    out.mkdir(parents=True, exist_ok=True)
    prepare(scratch, runtime)
    design_gate = json.loads((source / "design_gate.json").read_text())
    if not all(design_gate.get(k) is True for k in ("design_gate_passed", "implementation_checks_clear")):
        raise PermissionError("Design prerequisites not clear")
    if design_gate["preregistration_commit"] != prereg:
        raise ValueError("Design preregistration differs")
    audits, parts, parity, input_hashes = {}, [], {}, {}
    for period in ("design", "recent"):
        path = source / f"{period}_A1.csv"
        a = json.loads((source / f"{period}_A1_audit.json").read_text())
        if a["prereg_sha"] != prereg or a["ledger_sha256"] != sha(path):
            raise ValueError(f"{period} ledger hash/preregistration mismatch")
        if a["parameters"] != dict(apex_safe=True, veto_mode=1, slip_ticks=1.0):
            raise ValueError("Unfrozen account parameters")
        if a["censored_positions"] or a["censored"]:
            raise ValueError("Censored positions cannot enter accounts")
        diagpath = source / f"diagnostics_{period}" / "summary.json"
        diag = json.loads(diagpath.read_text())
        profiles = diag.get("profile_parity", {})
        if set(profiles) != {"S0", "S1", "A0", "A1", "E1"} or not all(
                x.get("exact_event_match") is True for x in profiles.values()):
            raise ValueError(f"{period} independent replay parity is not clear")
        parity[period] = dict(path=str(diagpath.relative_to(ROOT)), sha256=sha(diagpath),
                              all_five_profiles_exact=True, selected_null_parity=len(diag.get("selected_null_parity", [])))
        input_hashes[period] = dict(ledger=sha(path), audit=sha(source / f"{period}_A1_audit.json"),
                                   features=sha(source / f"{period}_features.pkl"))
        audits[period] = a
        part = pd.read_csv(path)
        years = pd.to_datetime(part.date).dt.year
        if not ((years.between(2018, 2022)) if period == "design" else years.ge(2023)).all():
            raise ValueError("Design/recent ledgers overlap or contain wrong years")
        parts.append(part)
    if audits["recent"]["total_net"] <= 0:
        raise PermissionError("Recent net is not positive")
    t = pd.concat(parts, ignore_index=True).sort_values("global_entry", kind="stable").reset_index(drop=True)
    if t.global_entry.duplicated().any() or not (t.global_entry.to_numpy()[1:] > t.global_exit.to_numpy()[:-1]).all():
        raise ValueError("Duplicate or overlapping candidate positions")
    combined = source / "candidate_A1.csv"
    t.to_csv(combined, index=False)
    import codex_or_pullback_plan as P
    with P.pinned_imports(runtime, scratch):
        replica = importlib.import_module("replica")
        with (scratch / "g24.pkl").open("rb") as handle:
            g = pickle.load(handle)
        t = audit_ledger(g, g.trading, t, out)
        cache_hash = sha(scratch / "g24.pkl")
        if any(a["cache_sha256"] != cache_hash for a in audits.values()):
            raise ValueError("Frozen replay and account grid differ")
        date = pd.DatetimeIndex(t.date)
        early = np.array([replica.is_early_close(d) for d in date])
        early_violation = early & ((t.decision_j >= 660) | (t.j0 >= 660) | (t.j1 > 690))
        chronology_violation = ~(t.global_entry > t.global_decision)
        raw_entry = g.o.ravel()[t.global_entry.to_numpy(int)]
        price_violation = ~np.isclose(raw_entry, t.raw_entry, rtol=0, atol=1e-7)
        price_violation |= ~np.isclose(t.entry, t.raw_entry+t.side*.25, rtol=0, atol=1e-7)
        price_violation |= ~np.isclose(t.exit, t.raw_exit-t.side*.25*(t.kind != 1), rtol=0, atol=1e-7)
        for phase, field in (("open", "o"), ("close", "c")):
            use = t.exit_phase == phase
            price_violation |= use & ~np.isclose(getattr(g, field).ravel()[t.global_exit.to_numpy(int)], t.raw_exit, rtol=0, atol=1e-7)
        invalid = early_violation | chronology_violation | price_violation
        t.loc[invalid].to_csv(out / "candidate_timing_price_violations.csv", index=False)
        if invalid.any():
            raise ValueError("Candidate early-close/timing/raw-fill audit failed")
        # Completeness covers every valid native 30m bar, including Sundays and
        # holidays, rather than treating an absent emitted trade as zero.
        with np.errstate(all="ignore"):
            bars = g.bars(30)
        d, j = np.nonzero(np.isfinite(bars["c"]))
        expected = d*1440+j*30
        yy = pd.DatetimeIndex(g.ts[d]).year
        unknown_days = 0
        coverage = {}
        for period, condition in (("design", (yy >= 2018) & (yy <= 2022)), ("recent", yy >= 2023)):
            f = pd.read_pickle(source / f"{period}_features.pkl")
            fy = pd.DatetimeIndex(f.date).year
            mask = ((fy >= 2018) & (fy <= 2022)) if period == "design" else fy >= 2023
            actual = f.loc[mask, "global_close"].to_numpy(int)
            if not np.array_equal(actual, expected[condition]):
                raise ValueError(f"{period} saved features omit or reorder native bars")
            canonical = g.trading[(pd.DatetimeIndex(g.ts[g.trading]).year >= (2018 if period == "design" else 2023))
                                  & (pd.DatetimeIndex(g.ts[g.trading]).year <= (2022 if period == "design" else 9999))]
            missing = set(canonical)-set(f.loc[mask, "day"].astype(int))
            unknown_days += len(missing)
            coverage[period] = dict(native_bars=len(actual), canonical_days=len(canonical), missing_account_days=sorted(map(int, missing)))
            del f
        del bars
        if unknown_days:
            raise ValueError("Unknown/no-feature account dates remain")
        gaps = []
        for row_index, x in enumerate(t.itertuples()):
            end = int(x.j1) if x.exit_phase == "open" else int(x.j1)+1
            held = np.arange(int(x.j0), end)
            missing = ~np.logical_and.reduce([np.isfinite(getattr(g, field)[int(x.day), held])
                                              for field in ("o", "h", "l", "c")])
            positions = held[missing]
            if not len(positions):
                continue
            chunks = np.split(positions, np.flatnonzero(np.diff(positions) > 1)+1)
            for chunk in chunks:
                lo, hi = int(chunk[0]), int(chunk[-1])
                before = np.flatnonzero(np.isfinite(g.c[int(x.day), :lo]))
                after = np.flatnonzero(np.isfinite(g.o[int(x.day), hi+1:]))
                prev_j = int(before[-1]) if len(before) else -1
                next_j = hi+1+int(after[0]) if len(after) else -1
                date_string = str(pd.Timestamp(g.ts[int(x.day)]).date())
                recurring_halt = lo >= 916 and hi <= 930 and date_string <= "2021-06-24"
                gaps.append(dict(ledger_row=row_index, date=date_string,
                    period="design" if date_string < "2023-01-01" else "recent",
                    first_missing_j=lo, last_missing_j=hi, missing_minutes=len(chunk),
                    first_missing_time=f"{lo//60:02}:{lo%60:02}", last_missing_time=f"{hi//60:02}:{hi%60:02}",
                    classification="historical_recurring_1516_1530_halt_pattern" if recurring_halt else "unexplained_intraday_data_gap",
                    entry_j=int(x.j0), exit_j=int(x.j1), entry_time=f"{int(x.j0)//60:02}:{int(x.j0)%60:02}",
                    exit_time=f"{int(x.j1)//60:02}:{int(x.j1)%60:02}", exit_why=x.why, side=int(x.side),
                    raw_entry=float(x.raw_entry), raw_exit=float(x.raw_exit),
                    stop_points=75., target_points=40., raw_stop=float(x.raw_entry)-int(x.side)*75.,
                    raw_target=float(x.raw_entry)+int(x.side)*40.,
                    previous_observed_j=prev_j, previous_observed_close=float(g.c[int(x.day), prev_j]) if prev_j >= 0 else None,
                    next_observed_j=next_j, next_observed_open=float(g.o[int(x.day), next_j]) if next_j >= 0 else None,
                    net_NQ_observed_proxy=float(x.net), cross_date=bool(x.day != x.exit_day)))
        gap_frame = pd.DataFrame(gaps)
        gap_frame.to_csv(out / "candidate_held_data_gaps.csv", index=False)
        if len(gap_frame):
            unknown = gap_frame[gap_frame.classification == "unexplained_intraday_data_gap"]
            unknown_days = int(unknown.date.nunique())
            raw_evidence = []
            for gap in unknown.to_dict("records"):
                compact_date = int(gap["date"].replace("-", ""))
                first, last = gap["first_missing_j"], gap["last_missing_j"]
                files = []
                for name in (f"NQ_1min_{str(compact_date)[:4]}.csv", f"NQ_1min_ON_{str(compact_date)[:4]}.csv"):
                    path = ROOT / "data" / name
                    observed, found = [], []
                    with path.open() as handle:
                        for line_number, line in enumerate(handle, 1):
                            fields = line.rstrip("\r\n").split(",")
                            if len(fields) < 2 or fields[0] != str(compact_date):
                                continue
                            hhmm = int(fields[1])
                            minute = hhmm//100*60+hhmm%100
                            if first-2 <= minute <= last+2:
                                observed.append(dict(line_number=line_number, raw_row=line.rstrip("\r\n")))
                            if first <= minute <= last:
                                found.append(dict(line_number=line_number, minute=minute, raw_row=line.rstrip("\r\n")))
                    files.append(dict(path=str(path.relative_to(ROOT)), sha256=sha(path),
                                      missing_interval_rows_found=found, neighboring_rows=observed))
                if any(x["missing_interval_rows_found"] for x in files):
                    raise ValueError("Raw observed bar exists outside cache; stop for cache/data reconciliation")
                raw_evidence.append(dict(date=gap["date"], first_missing_time=gap["first_missing_time"],
                                         last_missing_time=gap["last_missing_time"], raw_export_files=files,
                                         conclusion="Absent in both current day and overnight raw CSV exports; not a cache omission"))
            dump(out / "candidate_raw_gap_evidence.json", raw_evidence)
            audit = dict(trades=len(t), censored_positions=0, unknown_account_days=unknown_days,
                apex_carry_violations=0, early_close_trades=int(early.sum()),
                early_close_timing_violations=0, chronology_violations=0, raw_fill_price_violations=0,
                all_rows_retained=True, source_ledgers=input_hashes, full_native_calendar_coverage=coverage,
                grid_sha256=cache_hash, independent_parity=parity,
                held_gap_spans=len(gap_frame), held_gap_trades=int(gap_frame.ledger_row.nunique()),
                recurring_halt_pattern_trades=int(gap_frame[gap_frame.classification != "unexplained_intraday_data_gap"].ledger_row.nunique()),
                unexplained_gaps=unknown.to_dict("records"), account_path_completeness=False,
                raw_gap_evidence_sha256=sha(out / "candidate_raw_gap_evidence.json"),
                action="STOP account scoring; no imputation, trade removal, bounds simulation, or alternative variant",
                proxy_concern="Standalone frozen research replay skips absent one-minute bars; an intervening stop/target or account breach is unobserved.")
            dump(out / "candidate_full_audit.json", audit)
            gate = dict(design_gate_passed=True, preregistration_commit=prereg, candidate="apex_safe_veto1",
                account_run_authorized=False, implementation_checks_clear=True, recent_net_positive=True,
                recent_net=audits["recent"]["total_net"], censored_positions=0, unknown_account_days=unknown_days,
                apex_carry_violations=0, candidate_ledger_sha256=sha(combined),
                candidate_audit_sha256=sha(out / "candidate_full_audit.json"), design_gate_sha256=sha(source / "design_gate.json"),
                independent_parity=parity, account_path_completeness=False, account_simulations_run=0,
                blocked_reason="Unexplained held-minute data gaps; preregistration requires zero unknown account days")
            dump(source / "accounts_gate.json", gate)
            dump(out / "run_launcher.json", dict(status="blocked_before_simulation", account_simulations_run=0,
                gate_sha256=sha(source / "accounts_gate.json"), ledger_sha256=sha(combined),
                script_sha256=sha(__file__), reason=gate["blocked_reason"]))
            print(json.dumps(gate, indent=2))
            return gate
        w, r = candidate_paths(g, t, 1.04)
        expected_daily = np.bincount(t.day.to_numpy(int), weights=t.net.to_numpy()/10-(1.04-.725), minlength=g.D)
        error = float(np.max(np.abs(r[:, -1]-expected_daily)))
        if error > 1e-7:
            raise ValueError("Candidate net/path reconciliation failed")
        del w, r
        audit = dict(trades=len(t), first_entry=str(date.min().date()), last_exit=str(pd.to_datetime(t.exit_date).max().date()),
            censored_positions=0, unknown_account_days=unknown_days, apex_carry_violations=0,
            early_close_trades=int(early.sum()), early_close_timing_violations=int(early_violation.sum()),
            chronology_violations=int(chronology_violation.sum()), raw_fill_price_violations=int(price_violation.sum()),
            all_rows_retained=True, source_ledgers=input_hashes, full_native_calendar_coverage=coverage,
            candidate_net_path_max_abs_error=error, grid_sha256=cache_hash, independent_parity=parity,
            source_proxy_limit="Independent parity validates the frozen declared Python proxy; MC up-volume parity is unavailable.")
        dump(out / "candidate_full_audit.json", audit)
    gate = dict(design_gate_passed=True, preregistration_commit=prereg, candidate="apex_safe_veto1",
        account_run_authorized=bool(authorize), implementation_checks_clear=True, recent_net_positive=True,
        recent_net=audits["recent"]["total_net"], censored_positions=0, unknown_account_days=0, apex_carry_violations=0,
        candidate_ledger_sha256=sha(combined), candidate_audit_sha256=sha(out / "candidate_full_audit.json"),
        design_gate_sha256=sha(source / "design_gate.json"), independent_parity=parity,
        authorization="Root explicitly authorized account run contingent on zero violations" if authorize else "Await root go-ahead")
    dump(source / "accounts_gate.json", gate)
    print(json.dumps(gate, indent=2))
    return gate


def allocations(base):
    """One add, same VB normal/flag slots, and empty-slot control; no search."""
    empty = {k: v for k, v in base.items() if k not in ("VB_N", "VB_F")}
    return {"BASE": dict(base), "EMPTY_VB": empty,
            "ADD_DB1": {**base, "DB": 1},
            "REPLACE_VB_DB2_1": {**empty, "DB_N": 2, "DB_F": 1}}


def baseline_design(scratch, runtime, out, prereg, include_recent=False):
    """Existing canonical VB report only; no candidate or account simulation.

    load_mc supplies raw report prices. with_slippage is applied once and
    standardized net is recomputed from those prices, as portfolio.paths does.
    The default writes 2018--22 only. include_recent summarizes the same
    already-scored canonical report for 2018--22, 2023+, and all years.
    Funded sizes are descriptive, with no account simulation.
    """
    if not prereg:
        raise PermissionError("Committed root preregistration identifier required")
    sources = prepare(scratch, runtime)
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    import codex_or_pullback_plan as P
    with P.pinned_imports(runtime, scratch):
        pf = importlib.import_module("portfolio")
        fl = importlib.import_module("funded_lab")
        build = importlib.import_module("build_lab")
        metrics = importlib.import_module("metrics")
        with (Path(scratch) / "g24.pkl").open("rb") as handle:
            g = pickle.load(handle)
        report = ROOT / build.REPORTS["VB"][0]
        raw = pf.load_mc(g, str(report))
        all_rows = len(raw)
        date = pd.to_datetime(raw.date)
        raw = raw.loc[(date >= "2018-01-01") & ((date < "2023-01-01") if not include_recent else True)].copy()
        raw["raw_entry"], raw["raw_exit"] = raw.entry, raw.exit
        t = fl.with_slippage(raw)
        t["pnl"] = (t.raw_exit-t.raw_entry)*t.side*20.0
        t["slippage_usd"] = t.slips*5.0
        t["net"] = (t.exit-t.entry)*t.side*20.0-7.25
        np.testing.assert_allclose(t.net, t.pnl-7.25-t.slippage_usd, rtol=0, atol=1e-7)
        t["exit_day"] = t.day
        t["entry_date"], t["exit_date"] = t.date, t.date
        t["global_entry"], t["global_exit"] = t.day*g.o.shape[1]+t.j0, t.day*g.o.shape[1]+t.j1
        t["cost_slip_fills"] = t.slips
        t["slips"] = 0  # prices now contain the one-time standardized slippage
        t["commission_NQ"] = 7.25
        flags = pd.read_pickle(Path(scratch) / "single_print_sessions.pkl").flag
        t["funded_flag"] = flags.reindex(pd.DatetimeIndex(t.date)).fillna(False).to_numpy(bool)
        t["funded_full_size_MNQ"] = np.where(t.funded_flag, 1, 2)
        t["funded_full_size_net"] = t.net/10*t.funded_full_size_MNQ
        prefix = "baselineall" if include_recent else "design_current_vb"
        t.to_csv(out / f"{prefix}.csv", index=False)
        tr_dates = pd.DatetimeIndex(g.ts[g.trading])
        days = tr_dates[(tr_dates >= "2018-01-01") & ((tr_dates < "2023-01-01") if not include_recent else True)]
        daily = t.groupby("date").net.sum().reindex(days, fill_value=0.0)
        daily.rename("net_NQ").to_csv(out / f"{prefix}_daily.csv", index_label="date")
        rows = []
        periods = [("2018_22", t, daily)] if not include_recent else [
            ("2018_plus", t, daily),
            ("2018_22", t[pd.to_datetime(t.date).dt.year <= 2022], daily[daily.index.year <= 2022]),
            ("2023_plus", t[pd.to_datetime(t.date).dt.year >= 2023], daily[daily.index.year >= 2023])]
        for label, part, d in periods+[
                (str(year), t[pd.to_datetime(t.date).dt.year == year], daily[daily.index.year == year])
                for year in range(2018, int(days.year.max())+1)]:
            result = metrics.perf(d, part.net)
            x = part.net.to_numpy(float)
            closed = np.r_[0., np.cumsum(x)]
            result.update(period=label, net=float(x.sum()),
                t=float(x.mean()/x.std(ddof=1)*np.sqrt(len(x))) if len(x)>1 and x.std(ddof=1)>0 else np.nan,
                max_dd_closed_trade=float(np.max(np.maximum.accumulate(closed)-closed)),
                commission=float(7.25*len(part)), slippage=float(part.slippage_usd.sum()))
            rows.append(result)
        pd.DataFrame(rows).to_csv(out / f"{prefix}_metrics.csv", index=False)
        meta = dict(preregistration_commit=prereg, baseline="Current canonical VB, existing MC report",
            source_report=str(report.relative_to(ROOT)), report_sha256=sha(report),
            report_rows_all_history=all_rows, rows_summarized=len(t), evaluated_period="2018 onward, with design/recent/full rows" if include_recent else "2018-2022 only",
            sources=sources, cache_inputs={name: sha(Path(scratch)/name) for name in ("g24.pkl", "single_print_sessions.pkl")},
            standardization="Raw report prices; once-only 1 tick entry and 1 tick stop/market exit, target exit no slip; $7.25/NQ RT",
            net_reconciliation_passed=True, NQ_point_value=20, funded_VB_normal_MNQ=2, funded_VB_flagged_MNQ=1,
            flagged_trades=int(t.funded_flag.sum()),
            funded_full_size_columns="Descriptive fixed size only; no cushion sizing or account results",
            daily_drawdown="Existing metrics.perf on canonical trading dates including zero-trade dates",
            closed_trade_drawdown="Includes initial zero equity peak; each yearly row resets equity",
            NQDB2_returns_computed=False, account_simulations_run=0,
            script_sha256=sha(__file__), helper_sha256=sha(ROOT / "analysis/codex_or_pullback_plan.py"),
            ledger_sha256=sha(out / f"{prefix}.csv"), metrics=rows)
        dump(out / f"{prefix}_metadata.json", meta)
        print(pd.DataFrame(rows)[["period", "trades", "net", "avg", "t", "profit_factor", "max_dd"]].to_string(index=False))
        return meta


def audit_ledger(g, trading, trades, out):
    """Audit every row before indexing; never erase a Sunday/holiday/carry."""
    required = {"day", "j0", "j1", "exit_day", "side", "entry", "exit", "kind", "net", "slips",
                "entry_phase", "exit_phase", "global_entry", "global_exit"}
    if required - set(trades):
        raise ValueError(f"Missing account ledger fields: {sorted(required-set(trades))}")
    t = trades.copy()
    for col in ("day", "exit_day", "j0", "j1", "side", "kind", "slips", "global_entry", "global_exit"):
        values = t[col].to_numpy(float)
        if not np.isfinite(values).all() or not np.equal(values, values.astype(int)).all():
            raise ValueError(f"Noninteger ledger field: {col}")
        t[col] = values.astype(int)
    if ((t.day < 0) | (t.exit_day >= len(g.ts)) | (t.exit_day < t.day)).any():
        raise ValueError("Candidate calendar rows out of range")
    if not ((t.j0 >= 0) & (t.j0 < g.o.shape[1]) & (t.j1 >= 0) & (t.j1 < g.o.shape[1])).all():
        raise ValueError("Candidate minute out of range")
    if not np.array_equal(t.global_entry, t.day*g.o.shape[1]+t.j0):
        raise ValueError("Candidate global entry mapping differs")
    if not np.array_equal(t.global_exit, t.exit_day*g.o.shape[1]+t.j1):
        raise ValueError("Candidate global exit mapping differs")
    if not (t.global_exit >= t.global_entry).all():
        raise ValueError("Exit precedes entry")
    if not t.side.isin((-1, 1)).all() or not t.kind.isin((0, 1, 2)).all() or not (t.slips == 0).all():
        raise ValueError("Unknown side/kind or double-counted slippage")
    if not (t.entry_phase == "open").all() or not t.exit_phase.isin(("open", "intrabar", "close")).all():
        raise ValueError("Unknown candidate execution phase")
    if "qty" in t and not (t.qty == 1).all():
        raise ValueError("Account ledgers must be per-one-NQ normalized geometry")
    expected = (t.exit-t.entry)*t.side*20.0-7.25
    if not np.allclose(expected, t.net, rtol=0, atol=1e-7):
        raise ValueError("Candidate ledger fees/slipped prices differ")
    violations = t.loc[(t.day != t.exit_day) | ~t.day.isin(trading) | ~t.exit_day.isin(trading)
                       | (t.j1 > 15*60+59)].copy()
    violations.to_csv(Path(out) / "candidate_calendar_violations.csv", index=False)
    dump(Path(out) / "candidate_calendar_audit.json", dict(total_rows=len(t),
         cross_date=int((t.day != t.exit_day).sum()),
         outside_baseline_calendar=int((~t.day.isin(trading) | ~t.exit_day.isin(trading)).sum()),
         after_1559_exit=int((t.j1 > 15*60+59).sum()),
         excluded_rows=0, repaired_rows=0,
         policy="All rows retained; unsupported calendar/carry blocks the account comparison"))
    if len(violations):
        raise ValueError("Apex-safe ledger contains carry/non-account-date trades; inspect full violations, never drop them")
    return t


def candidate_paths(g, trades, fee=1.04):
    """One-MNQ adverse/closed paths, from actual slipped prices and entry fees.

    Entry is the minute open, so that minute's range is held. An open exit
    excludes later OHLC. The stop minute terminates at its executable fill.
    Bracket ambiguity uses the unchanged reviewed adverse-before-target rule.
    Cross-date trades must first be rejected by the explicit calendar audit.
    """
    w, r = np.zeros(g.o.shape), np.zeros(g.o.shape)
    for x in trades.itertuples():
        d, e, z, side = int(x.day), int(x.j0), int(x.j1), int(x.side)
        if int(x.exit_day) != d or x.entry_phase != "open" or not 0 <= e <= z < g.o.shape[1]:
            raise ValueError("Unsupported candidate calendar or entry phase")
        net = (float(x.exit)-float(x.entry))*side*2.0-float(fee)
        end = z if x.exit_phase == "open" else z+1
        adverse = g.l[d, e:end] if side > 0 else g.h[d, e:end]
        if not np.isfinite(adverse).all():
            raise ValueError("Unknown held-minute price; never replace missing OHLC by entry")
        marks = (adverse-float(x.entry))*side*2.0-float(fee)
        if len(marks) and int(x.kind) == 0 and x.exit_phase != "open":
            marks[-1] = net
        elif len(marks) and x.exit_phase != "open":
            marks[-1] = min(marks[-1], net)
        w[d, e:end] += marks
        w[d, z if x.exit_phase == "open" else z+1:] += net
        r[d, z:] += net
    return w, r


def fixtures():
    g = SimpleNamespace(o=np.full((1, 9), 100.), l=np.full((1, 9), 99.), h=np.full((1, 9), 101.))
    g.l[0, 5] = 1.
    t = pd.DataFrame([dict(day=0, exit_day=0, j0=2, j1=5, side=1,
        entry=100.25, exit=100.75, kind=2, entry_phase="open", exit_phase="open")])
    w, r = candidate_paths(g, t)
    np.testing.assert_allclose(w[0, 2:5], -3.54)
    np.testing.assert_allclose(w[0, 5:], -.04)
    assert not r[0, :5].any()
    np.testing.assert_allclose(r[0, 5:], -.04)
    t.loc[0, ["exit", "kind", "exit_phase"]] = [95., 0, "intrabar"]
    w, r = candidate_paths(g, t)
    np.testing.assert_allclose(w[0, 5:], -11.54)
    w2, r2 = candidate_paths(g, t, 1.24)
    np.testing.assert_allclose(w2[0, 2:]-w[0, 2:], -.2)
    np.testing.assert_allclose(r2[0, 5:]-r[0, 5:], -.2)
    t.loc[0, "exit_day"] = 1
    try:
        candidate_paths(g, t)
    except ValueError:
        pass
    else:
        raise AssertionError("Cross-date trade was silently truncated")
    return dict(entry_fee_and_slip_visible=True, held_entry_range=True,
                open_exit_later_range_excluded=True, executable_stop_cap=True,
                stress_fee_timing=True, cross_date_never_truncated=True)


def frozen_histories(lab, fb, out):
    """Exactly the reviewed four seeds, reused across every fee/allocation."""
    result = {}
    for cohort, start in (("2018_plus", "2018-01-01"), ("2023_plus", "2023-01-01")):
        boot = fb.Boot(lab, start=start)
        result[cohort] = np.concatenate([boot._histories(250, 500, 20, s) for s in (1, 2, 3, 4)])
        np.save(Path(out) / f"funded_histories_{cohort}.npy", result[cohort])
    return result


def funded(lab, bundle, histories, fee, out):
    """One allocation stack at a time; no K*D*M diff temporary."""
    import codex_ob_v2_accounts as acc
    acc.F = bundle.funded_sim
    results, parity, resources = {}, [], []
    for name, plan in allocations(bundle.base).items():
        started = time.monotonic()
        keys = sorted(plan)
        w, c = np.stack([lab.W[k] for k in keys]), np.stack([lab.C[k] for k in keys])
        names, sizes = lab._base({k: plan[k] for k in keys})
        assert names == keys
        if not np.isfinite(w).all() or not np.isfinite(c).all():
            raise ValueError("Nonfinite account path")
        table = acc.make_table(w, c, sizes)
        parity += acc.parity_check(w, c, table, histories["2018_plus"][[0, 1, 17, 333, 999]], f"{fee}/{name}")
        for cohort, h in histories.items():
            results.setdefault(cohort, {})[name] = (acc.run_table(table, h, 250), acc.run_table(table, h, 500))
        resources.append(dict(fee=fee, config=name, seconds=time.monotonic()-started,
                              max_quantity_states=int(table["counts"].max())))
        print(f"funded {fee:.2f} {name} {resources[-1]['seconds']:.1f}s", flush=True)
        del w, c, table
        gc.collect()
    rows, differences = [], []
    for cohort, records in results.items():
        for name, (a, b) in records.items():
            rows.append(dict(fee=fee, cohort=cohort, config=name, year1=a[:, 0].mean(),
                year1_p5=np.percentile(a[:, 0], 5), year1_p95=np.percentile(a[:, 0], 95),
                year2=b[:, 0].mean(), year2_p5=np.percentile(b[:, 0], 5), year2_p95=np.percentile(b[:, 0], 95),
                blown=b[:, 3].mean(), all6=(b[:, 1] == 6).mean(),
                days6=np.median(np.where(b[:, 1] == 6, b[:, 2], np.inf))))
            for reference in ("BASE", "EMPTY_VB"):
                aa, bb = records[reference]
                for metric, delta in (("year1", a[:, 0]-aa[:, 0]), ("year2", b[:, 0]-bb[:, 0]),
                                      ("blown", b[:, 3]-bb[:, 3])):
                    lo, hi, lo95, hi95 = paired_intervals(delta)
                    differences.append(dict(fee=fee, cohort=cohort, config=name, reference=reference,
                                            metric=metric, delta=delta.mean(), lo=lo, hi=hi,
                                            confidence=.90, lo95=lo95, hi95=hi95))
        np.savez_compressed(Path(out) / f"funded_raw_{fee:.2f}_{cohort}.npz",
            **{f"{k}__{h}": records[k][i] for k in records for i, h in enumerate((250, 500))})
    dump(Path(out) / f"funded_parity_{fee:.2f}.json", parity)
    dump(Path(out) / f"funded_resources_{fee:.2f}.json", resources)
    return rows, differences


def paired_intervals(delta, seed=902, samples=5000):
    """Fixed paired account-history resampling; report both prereg90% and95%."""
    delta = np.asarray(delta, dtype=float)
    rng, means = np.random.default_rng(seed), np.empty(samples)
    for start in range(0, samples, 100):
        n = min(100, samples-start)
        idx = rng.integers(0, len(delta), (n, len(delta)))
        means[start:start+n] = delta[idx].mean(axis=1)
    return np.percentile(means, [5, 95, 2.5, 97.5]).tolist()


def chronological_ci(delta, valid, seed=903, samples=5000, block=20, confidence=.90):
    """Reviewed paired chronological start blocks; calendar is not compressed."""
    delta, valid = np.asarray(delta), np.asarray(valid, bool)
    if not valid.any():
        return [np.nan, np.nan]
    rng, means = np.random.default_rng(seed), np.empty(samples)
    length = len(delta)
    for start in range(0, samples, 100):
        n = min(100, samples-start)
        st = rng.integers(0, length, (n, int(np.ceil(length/block))))
        idx = ((st[:, :, None]+np.arange(block)) % length).reshape(n, -1)[:, :length]
        count = valid[idx].sum(axis=1)
        means[start:start+n] = np.divide((delta[idx]*valid[idx]).sum(axis=1), count,
                                         out=np.full(n, np.nan), where=count > 0)
    tail = (1-confidence)*50
    return np.nanpercentile(means, [tail, 100-tail]).tolist()


def evaluation(lab, scratch, P, prereg, fee, ledger, out, runtime):
    """Canonical four-leg real_fee_bench baseline; same engine and 21-day rule."""
    parts = P.evaluation_parts(scratch, preregistration_commit=prereg, authorized_returns=True,
                               runtime=runtime, fee=fee, grid=lab.g)
    pp, q = parts.parts, parts.quantities
    if set(q) != {"VB", "ONB30", "MON_BR", "EOS"} or q["VB"] != 8.0:
        raise ValueError("Documented current evaluation roster differs")
    base_w = sum(pp[k][0]*q[k] for k in q)
    base_r = sum(pp[k][1]*q[k] for k in q)
    empty_w, empty_r = base_w-pp["VB"][0]*8, base_r-pp["VB"][1]*8
    del pp
    cw, cr = candidate_paths(lab.g, ledger, fee)
    cw, cr = cw[lab.tr], cr[lab.tr]
    configs = (("BASE", False, 0), ("EMPTY_VB", True, 0),
               ("ADD_DB1", False, 1), ("REPLACE_VB_DB8", True, 8))
    raw = {}
    full = np.arange(lab.D)+parts.max_days <= lab.D
    for name, empty, n in configs:
        w, r = (empty_w, empty_r) if empty else (base_w, base_r)
        if n:
            w, r = w+cw*n, r+cr*n
        res = [parts.challenge(w, r, np.arange(s, min(s+parts.max_days, lab.D)), lambda p, c, n: 1.)
               for s in range(lab.D)]
        raw[name] = (np.array([x[0] if x else "" for x in res]), np.array([x[1] if x else 0 for x in res]))
        print(f"evaluation {fee:.2f} {name}", flush=True)
        if n:
            del w, r
    rows, differences = [], []
    for name, (outcomes, days) in raw.items():
        for cohort, (lo, hi) in COHORTS.items():
            mask = np.asarray((parts.dates >= lo) & (parts.dates < hi))
            valid = full & mask
            passed = valid & (outcomes == "pass")
            rows.append(dict(fee=fee, cohort=cohort, config=name, starts=int(valid.sum()),
                passed=float((outcomes[valid] == "pass").mean()), failed=float((outcomes[valid] == "fail").mean()),
                timed_out=float((outcomes[valid] == "time").mean()),
                median_pass_days=float(np.median(days[passed])) if passed.any() else np.nan,
                changed_vs_base=float((outcomes[valid] != raw["BASE"][0][valid]).mean())))
            for reference in ("BASE", "EMPTY_VB"):
                for metric, label in (("passed", "pass"), ("failed", "fail"), ("timed_out", "time")):
                    delta = (outcomes[mask] == label).astype(float)-(raw[reference][0][mask] == label)
                    lo_ci, hi_ci = chronological_ci(delta, full[mask])
                    lo95, hi95 = chronological_ci(delta, full[mask], confidence=.95)
                    differences.append(dict(fee=fee, cohort=cohort, config=name, reference=reference, metric=metric,
                        delta=float(delta[full[mask]].mean()), lo=lo_ci, hi=hi_ci, confidence=.90,
                        lo95=lo95, hi95=hi95, block=20, resamples=5000))
    frame = pd.DataFrame({f"{k}__{c}": v[i] for k, v in raw.items() for i, c in enumerate(("outcome", "days"))}, index=parts.dates)
    frame["complete_21day_start"] = full
    frame.to_csv(Path(out) / f"evaluation_starts_{fee:.2f}.csv", index_label="date")
    return rows, differences


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--scratch", type=Path, default=ROOT / "scratch_data")
    ap.add_argument("--runtime", type=Path, default=RUNTIME)
    ap.add_argument("--out", type=Path, default=OUT)
    ap.add_argument("--preregistration-commit")
    ap.add_argument("--gate", type=Path)
    ap.add_argument("--ledger", type=Path)
    ap.add_argument("--root-authorized", action="store_true", help="Only after root's explicit contingent account authorization")
    modes = ap.add_mutually_exclusive_group(required=True)
    modes.add_argument("--prepare", action="store_true")
    modes.add_argument("--fixtures-only", action="store_true")
    modes.add_argument("--baseline-design-only", action="store_true")
    modes.add_argument("--baseline-all-existing", action="store_true")
    modes.add_argument("--audit-only", action="store_true")
    modes.add_argument("--run", action="store_true")
    args = ap.parse_args()
    if args.prepare:
        print(json.dumps(prepare(args.scratch, args.runtime), indent=2))
        return
    if args.fixtures_only:
        print(json.dumps(fixtures(), indent=2))
        return
    if args.baseline_design_only:
        baseline_design(args.scratch, args.runtime, args.out, args.preregistration_commit)
        return
    if args.baseline_all_existing:
        baseline_design(args.scratch, args.runtime, args.out, args.preregistration_commit, include_recent=True)
        return
    if args.audit_only:
        audit_candidate_bundle(args.scratch, args.runtime, args.out, args.preregistration_commit, args.root_authorized)
        return
    if not args.ledger:
        raise ValueError("Frozen Apex-safe candidate ledger required")
    gate = require_gate(args.preregistration_commit, args.gate, args.ledger)
    sources = prepare(args.scratch, args.runtime)
    args.out.mkdir(parents=True, exist_ok=True)
    cache_inputs = {name: sha(args.scratch / name) for name in sources["existing_caches"]}
    dump(args.out / "baseline_cache_inputs.json", cache_inputs)
    import codex_or_pullback_plan as P
    started = time.monotonic()
    bundle = P.build_current_plan(args.scratch, preregistration_commit=args.preregistration_commit,
        authorized_returns=True, runtime=args.runtime, audit_dir=args.out / "baseline", fee=1.04)
    lab = bundle.lab
    t = audit_ledger(lab.g, lab.tr, pd.read_csv(args.ledger), args.out)
    dates = pd.DatetimeIndex(lab.g.ts[lab.tr])
    flags = pd.read_pickle(args.scratch / "single_print_sessions.pkl").flag.reindex(dates).fillna(False).to_numpy(bool)
    fr, fd, er, ed = [], [], [], []
    with P.pinned_imports(args.runtime, args.scratch):
        build = importlib.import_module("build_lab")
        bridge = importlib.import_module("bridge_monday_confirm")
        combine = importlib.import_module("combine_levers_test")
        reports = {build.REPORTS[k][0] for k in ("VB", "ONB_ML2_MC", "MON_MC", "EOS", "LDF_MC", "NFP_MC")}
        reports.update((bridge.F, combine.ONB30))
        report_inputs = {name: sha(ROOT / name) for name in sorted(reports)}
        dump(args.out / "baseline_report_inputs.json", report_inputs)
        histories = frozen_histories(lab, bundle.bootstrap, args.out)
        for fee in FEES:
            if fee > 1.04:
                lab.real_fees(.20, list(bundle.base))
            w, r = candidate_paths(lab.g, t, fee)
            lab.W["DB"], lab.C["DB"] = w[lab.tr], r[lab.tr, -1]
            for name, use in (("DB_F", flags), ("DB_N", ~flags)):
                lab.W[name], lab.C[name] = lab.W["DB"]*use[:, None], lab.C["DB"]*use
            del w, r
            a, b = funded(lab, bundle, histories, fee, args.out)
            fr += a; fd += b
            pd.DataFrame(fr).to_csv(args.out / "funded_summary.csv", index=False)
            pd.DataFrame(fd).to_csv(args.out / "funded_paired_differences.csv", index=False)
            a, b = evaluation(lab, args.scratch, P, args.preregistration_commit, fee, t, args.out, args.runtime)
            er += a; ed += b
            pd.DataFrame(er).to_csv(args.out / "evaluation_summary.csv", index=False)
            pd.DataFrame(ed).to_csv(args.out / "evaluation_paired_differences.csv", index=False)
            gc.collect()
    dump(args.out / "reproduction.json", dict(preregistration_commit=args.preregistration_commit,
        gate=gate, gate_sha256=sha(args.gate), ledger_sha256=sha(args.ledger), sources=sources,
        script_sha256=sha(__file__), helper_sha256=sha(ROOT / "analysis/codex_or_pullback_plan.py"),
        accelerator_sha256=sha(ROOT / "analysis/codex_ob_v2_accounts.py"),
        baseline_cache_inputs=cache_inputs, baseline_report_inputs=report_inputs,
        fees=FEES, paired_histories=1000, block=20, horizons=[250, 500],
        seeds=[1, 2, 3, 4], funded_plan=bundle.base, evaluation_plan={"VB": 8, "ONB30": ["risk", 1100], "MON_BR": 2, "EOS": ["risk", 500]},
        evaluation_days=21, seconds=time.monotonic()-started,
        limits=P.BASELINE_LIMITS+["Candidate is an Apex-safe total-volume Python proxy, not literal source parity.",
            "Evaluation inherits same-minute pass-before-breach priority from combine_levers_test.",
            "Calendar/carry violations block scoring; no candidate data is silently dropped."]))


if __name__ == "__main__":
    main()
