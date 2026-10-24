"""S03 Noise Area v2: frozen 50K/150K evaluation and funded adapters.

Import, --prepare and --fixtures-only never read historical market data or
compute historical returns. --run requires the root's committed preregistration
and a passed, hash-bound design/implementation/calendar gate. Pinned Git blobs
are materialized with git show, so no prior task's unpublished runtime is needed.
"""
from __future__ import annotations

import argparse
import ast
import contextlib
import csv
import gc
import hashlib
import importlib
import importlib.util
import json
import math
import pickle
import subprocess
import sys
import time
import types
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CODEX_REF = "541d1117683294cc3949d13e7260272eba5a20b8"
CLAUDE_REF = "e4399c8e235ee26674c88a439d4c9926b5731af4"
OLD_REF = "a67035be4189b493098c80f1def979348520fd5d"
RUNTIME = ROOT / "agents/codex/runtime/s03_account_deps"
OUT = ROOT / "analysis/outputs/codex_s03_noisearea/accounts"
FEES = (1.04, 1.24)
COHORTS = {"2018_plus": ("2018-01-01", "2100-01-01"),
           "2023_plus": ("2023-01-01", "2100-01-01")}
FIFTY = {"VB_N": 2, "VB_F": 1, "ONB_ML2_MC": ("risk", 400),
         "MON_MC": 1, "EOS": ("risk", 700), "LDF_MC": 2,
         "NFP_MC": ("risk", 500), "MON_BR_MC": 1, "CLS": 2,
         "MOC_MES": 2, "RS_L": 1}
SEEDS = ("fc_2b_bench", "funded_bootstrap", "funded_lab", "funded_sim",
         "portfolio", "grid", "grid24", "relative_strength_test",
         "s_rank_es_round1_test", "cl_forced_flows_test", "funded_sim150",
         "plan_150k_test", "dual_thrust_test", "dual_thrust_bench")
WRAPPERS = ("codex_or_pullback_plan", "codex_anson_plan", "codex_anson_accounts",
            "codex_ob_v2_accounts", "codex_night_volume_switch_portfolio",
            "codex_r2vault_accounts")
CALENDAR_SOURCES = {"r2vault_calendar_metadata.md":"agents/codex/inputs/r2vault/calendar_metadata.md",
                    "codex_r2vault_replay.py":"analysis/codex_r2vault_replay.py",
                    "codex_anson_replay.py":"analysis/codex_anson_replay.py"}
INPUTS = {"RS_source.txt": "checks/candidates/relative_strength/RelStrength_v3.txt",
          "RS_reference.csv": "checks/candidates/relative_strength/trades.csv",
          "DT_reference.csv": "checks/candidates/dual_thrust/trades.csv",
          "DT_timed.csv": "checks/candidates/dual_thrust/trades_replica.csv",
          "funded_plan.md": "funded_strategies/FUNDED_PLAN.md",
          "new_chat_brief.md": "NEW_CHAT_BRIEF.md"}
REQUIRED_CACHES = ("lab.pkl", "g24.pkl", "ge.pkl", "cl.pkl", "s_rank_gap2.pkl",
                   "single_print_sessions.pkl")


def dump(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, default=str, allow_nan=True)+"\n", encoding="utf-8")


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for block in iter(lambda: f.read(1024*1024), b""):
            h.update(block)
    return h.hexdigest()


def git(*args):
    p = subprocess.run(["git", "-C", str(ROOT), *args], check=True,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return p.stdout


def _write_blob(ref, path, target):
    data = git("show", f"{ref}:{path}")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)
    return dict(repository_path=path, ref=ref,
                git_blob=git("rev-parse", f"{ref}:{path}").decode().strip(),
                sha256=hashlib.sha256(data).hexdigest(), bytes=len(data))


def _imports(data):
    result = set()
    for n in ast.walk(ast.parse(data.decode("utf-8-sig"))):
        if isinstance(n, ast.Import):
            result.update(x.name.split(".")[0] for x in n.names)
        elif isinstance(n, ast.ImportFrom) and n.module:
            result.add(n.module.split(".")[0])
    return result


def prepare(scratch=ROOT / "scratch_data", runtime=RUNTIME):
    """Stage exact sources and compare the old baseline pin to today's context.

    Cache presence/size only is inspected. No pickle, prices, trades or returned
    account results are read here. Missing Git objects are a hard prerequisite.
    """
    runtime, scratch = Path(runtime).resolve(), Path(scratch).resolve()
    if not runtime.is_relative_to(ROOT / "agents/codex/runtime"):
        raise ValueError("Source staging must remain in task runtime")
    try:
        for ref in (CODEX_REF, CLAUDE_REF, OLD_REF):
            git("cat-file", "-e", f"{ref}^{{commit}}")
    except subprocess.CalledProcessError:
        if (runtime / "manifest.json").is_file():
            verify_sources(runtime)
            return json.loads((runtime / "readiness.json").read_text())
        raise RuntimeError("Pinned Git objects unavailable; stage exact blobs through GitHub connector first") from None
    available = {Path(p).stem: p for p in git("ls-tree", "-r", "--name-only", CLAUDE_REF,
                 "analysis").decode().splitlines() if p.count("/") == 1 and p.endswith(".py")}
    pending, modules = list(SEEDS), {}
    while pending:
        name = pending.pop()
        if name in modules:
            continue
        path = available[name]
        target = runtime / "modules" / f"{name}.py"
        modules[name] = _write_blob(CLAUDE_REF, path, target)
        pending.extend(sorted(_imports(target.read_bytes()).intersection(available).difference(modules)))
    wrappers = {name: _write_blob(CODEX_REF, f"analysis/{name}.py",
                runtime / "published" / f"{name}.py") for name in WRAPPERS}
    inputs = {name: _write_blob(CLAUDE_REF, path, runtime / "modules" / name)
              for name, path in INPUTS.items()}
    calendar_sources = []
    for name,path in CALENDAR_SOURCES.items():
        meta = _write_blob(CODEX_REF,path,runtime/"published"/name)
        calendar_sources.append(dict(staged="published/"+name,**meta,
            url=f"https://github.com/Dartdark/thebeginning/blob/{CODEX_REF}/{path}"))
    dump(runtime/"calendar_source_provenance.json",dict(ref=CODEX_REF,sources=calendar_sources))
    raw_paths = git("ls-tree","-r","--name-only",CLAUDE_REF,"data").decode().splitlines()
    wanted = {f"data/NQ_1min_{prefix}{year}.csv" for year in range(2018,2027) for prefix in ("","ON_")}
    raw_meta = []
    for path in sorted(wanted.intersection(raw_paths)):
        blob = git("rev-parse",f"{CLAUDE_REF}:{path}").decode().strip()
        raw_meta.append(dict(path=path,sha=blob,size=int(git("cat-file","-s",blob)),
                             html_url=f"https://github.com/Dartdark/thebeginning/blob/{CLAUDE_REF}/{path}"))
    dump(runtime/"raw_csv_github_metadata.json",dict(ref=CLAUDE_REF,files=raw_meta))
    # Compare actual pinned blobs, including inputs; never assume unchanged.
    old_paths = {Path(p).stem: p for p in git("ls-tree", "-r", "--name-only", OLD_REF,
        "analysis").decode().splitlines() if p.count("/") == 1 and p.endswith(".py")}
    todo, legacy_names = list(SEEDS[:10]), []
    while todo:
        n = todo.pop()
        if n in legacy_names:
            continue
        legacy_names.append(n)
        todo.extend(sorted(_imports(git("show", f"{OLD_REF}:{old_paths[n]}")).intersection(old_paths)))
    checks = []
    for path in [f"analysis/{n}.py" for n in legacy_names] + [INPUTS["RS_source.txt"], INPUTS["RS_reference.csv"]]:
        a = git("rev-parse", f"{OLD_REF}:{path}").decode().strip()
        b = git("rev-parse", f"{CLAUDE_REF}:{path}").decode().strip()
        checks.append(dict(path=path, previous_blob=a, current_blob=b, unchanged=a == b))
    manifest = dict(ref=CLAUDE_REF, codex_ref=CODEX_REF, modules=modules, inputs=inputs,
                    wrappers=wrappers, previous_pin=OLD_REF, baseline_context_comparisons=checks,
                    changed_baseline_dependencies=[x for x in checks if not x["unchanged"]],
                    roster=funded_plans(), evaluation_sizes=evaluation_size_spec(),
                    historical_returns_computed=False)
    dump(runtime / "modules/manifest.json", manifest)
    dump(runtime / "manifest.json", manifest)
    missing = [n for n in REQUIRED_CACHES if not (scratch / n).is_file()]
    readiness = dict(ref=CLAUDE_REF, codex_ref=CODEX_REF, modules=len(modules),
                     wrappers=len(wrappers), baseline_comparisons=len(checks),
                     changed_baseline_dependencies=manifest["changed_baseline_dependencies"],
                     missing_caches=missing, caches={n: (scratch/n).stat().st_size
                     for n in REQUIRED_CACHES if (scratch/n).is_file()}, historical_returns_computed=False)
    dump(runtime / "readiness.json", readiness)
    return readiness


def verify_sources(runtime=RUNTIME):
    runtime = Path(runtime)
    m = json.loads((runtime / "manifest.json").read_text())
    if m["ref"] != CLAUDE_REF or m["codex_ref"] != CODEX_REF:
        raise ValueError("Frozen source revisions differ")
    for group, parent, suffix in (("modules", "modules", ".py"),
                                   ("inputs", "modules", ""), ("wrappers", "published", ".py")):
        for name, meta in m[group].items():
            if sha(runtime / parent / (name+suffix)) != meta["sha256"]:
                raise ValueError(f"Pinned source changed: {group}/{name}")
    if m["changed_baseline_dependencies"]:
        raise ValueError("Current baseline dependencies changed; explicit reconciliation required")
    return m


def funded_plans():
    onefifty = {k: (("risk", v[1]*1.5) if isinstance(v, tuple) else v*1.5)
                for k, v in FIFTY.items() if k != "RS_L"}
    onefifty.update(RS=1, DT=2)
    return {"50K_funded": dict(FIFTY), "150K_funded": onefifty}


def evaluation_size_spec():
    return {"50K_evaluation": dict(VB=8, ONB30_risk=1100, ONB30_stop_atr=.25,
             MON_BR=2, EOS_risk=500), "150K_evaluation": dict(VB=20,
             ONB30_risk=2750, ONB30_stop_atr=.25, MON_BR=5, EOS_risk=1250),
             "risk_quantity_rule": "floor(risk_dollars/(stop_points*2)); scale dollars before floor"}


def allocations(base, context):
    """Exactly four frozen configurations, preserving the entire VB slot size."""
    funded = context.endswith("funded")
    slots = ("VB_N", "VB_F") if funded else ("VB",)
    empty = {k: v for k, v in base.items() if k not in slots}
    replacement = {**empty, **{("S03_N" if k == "VB_N" else "S03_F" if k == "VB_F" else "S03"):base[k]
                               for k in slots}}
    return {"BASE": dict(base), "ADD_V2": {**base, "S03":2 if context.startswith("150") else 1},
            "EMPTY_VB": empty, "REPLACE_VB": replacement}


def require_gate(prereg, gate_path, ledger_path, audit_path, plan_path="agents/codex/plans/s03_noisearea.md"):
    if not prereg or not gate_path:
        raise PermissionError("Root preregistration and passed design gate are required")
    git("cat-file", "-e", f"{prereg}:{plan_path}")
    gate = json.loads(Path(gate_path).read_text())
    if gate.get("preregistration_commit") != prereg:
        raise ValueError("Account/design preregistrations differ")
    for k in ("design_gate_passed", "implementation_checks_clear", "account_run_authorized",
              "recent_net_positive", "full_calendar_complete"):
        if gate.get(k) is not True:
            raise PermissionError(f"Account prerequisite is not explicitly clear: {k}")
    for k in ("censored_positions", "unknown_account_days", "unknown_held_minutes", "apex_carry_violations"):
        if isinstance(gate.get(k), bool) or gate.get(k) != 0:
            raise PermissionError(f"Root must certify {k}=0")
    if gate.get("candidate") != "S03NoiseArea_v2":
        raise ValueError("Only the frozen primary S03NoiseArea_v2 enters accounts")
    if gate.get("candidate_ledger_sha256") != sha(ledger_path) or gate.get("candidate_audit_sha256") != sha(audit_path):
        raise ValueError("Candidate source files differ from the root gate")
    return gate


def source_calendar_audit(audit_path,runtime=RUNTIME,label="source"):
    """Read coverage metadata only, before opening any account-return gate."""
    a = pd.read_csv(audit_path,parse_dates=["date"])
    fields = {"day","date","calendar_kind","missing_cash_minutes","unknown_held_minutes",
              "delayed_orders","censored_positions","unmatched_orders"}
    if not fields.issubset(a) or a.day.duplicated().any():
        raise ValueError("Source day audit lacks complete unique coverage metadata")
    normal = a.calendar_kind.eq("normal")
    bad = a.loc[normal&a.missing_cash_minutes.gt(0)].copy()
    result = dict(source_audit=str(Path(audit_path).resolve().relative_to(ROOT)),
                  source_audit_sha256=sha(audit_path),calendar_rows=len(a),normal_cash_dates=int(normal.sum()),
                  normal_dates_missing_minutes=len(bad),missing_minutes=int(bad.missing_cash_minutes.sum()),
                  unknown_source_dates=bad.to_dict("records"),
                  held_unknown_minutes=int(a.unknown_held_minutes.sum()),
                  delayed_orders=int(a.delayed_orders.sum()),censored_positions=int(a.censored_positions.sum()),
                  unmatched_orders=int(a.unmatched_orders.sum()),
                  account_source_calendar_clear=False if a.loc[normal,"no_cash_data"].eq(True).any() or a[
                      ["unknown_held_minutes","censored_positions","unmatched_orders"]].to_numpy().any() else (None if len(bad) else True),
                  requires_native_interval_audit=bool(len(bad)),
                  interval_policy="Flat nondecision gaps may use observed-only VWAP as registered; missing scheduled checks/no-cash dates need resolution.",
                  known_halts_requiring_separate_documentation="R2's mask certifies no March2020 circuit-breaker interval.",
                  historical_account_or_baseline_returns_computed=False)
    dump(Path(runtime)/f"{label}_source_calendar_audit.json",result)
    return result


def native_coverage_audit(audit_path,orders_path,*,scratch=ROOT/"scratch_data",runtime=RUNTIME):
    """Narrow raw/cache timestamp audit: no signals, P&L, or account returns.

    Distinguish flat nondecision prefixes permitted by observed-only VWAP from
    an unobserved scheduled decision or an entirely missing normal cash date.
    R2's published closure mask has no March2020 circuit-breaker exception;
    those intervals are not relabeled known closures without source evidence.
    """
    runtime = Path(runtime)
    audit_paths = list(audit_path) if isinstance(audit_path,(tuple,list)) else [audit_path]
    orders_paths = list(orders_path) if isinstance(orders_path,(tuple,list)) else [orders_path]
    a = pd.concat([pd.read_csv(path,parse_dates=["date"]) for path in audit_paths],ignore_index=True)
    if a.day.duplicated().any():
        raise ValueError("Design/recent source coverage calendars overlap")
    bad = a.loc[a.calendar_kind.eq("normal")&a.missing_cash_minutes.gt(0)]
    selected = {pd.Timestamp(d).strftime("%Y%m%d"):str(pd.Timestamp(d).date()) for d in bad.date}
    raw,seen,versions = {d:[] for d in selected},{d:set() for d in selected},[]
    meta = json.loads((runtime/"raw_csv_github_metadata.json").read_text())
    if meta["ref"]!=CLAUDE_REF:
        raise ValueError("Raw CSV source metadata is not the frozen current revision")
    available = {x["path"]:x for x in meta["files"]}
    for year in sorted({d[:4] for d in selected}):
        for name in (f"NQ_1min_{year}.csv",f"NQ_1min_ON_{year}.csv"):
            path = ROOT/"data"/name
            key = str(path.relative_to(ROOT))
            expected = available[key]
            h = hashlib.sha1(b"blob "+str(path.stat().st_size).encode()+b"\0")
            with path.open("rb") as handle:
                for data in iter(lambda:handle.read(1024*1024),b""):
                    h.update(data)
            record = dict(expected,local_git_blob=h.hexdigest(),local_sha256=sha(path),
                          local_bytes=path.stat().st_size,exact_github_match=h.hexdigest()==expected["sha"])
            if not record["exact_github_match"]:
                raise ValueError(f"Local raw CSV differs from the frozen current Claude source: {key}")
            versions.append(record)
            with path.open(newline="") as handle:
                for number,row in enumerate(csv.DictReader(handle),2):
                    d = row["date"]
                    if d not in selected:
                        continue
                    hm = int(row["time"])
                    j = hm//100*60+hm%100
                    valid = all(math.isfinite(float(row[k])) for k in ("open","high","low","close","volume")) and float(row["volume"])>=0
                    if valid:
                        seen[d].add(j)
                    raw[d].append(dict(file=key,line=number,minute=j,native=valid))
    usecols = ["order_id","name","action","decision_day","decision_j","status","order_type",
               "activation_minute","fill_minute","delay_minutes"]
    orders = pd.concat([pd.read_csv(path,usecols=usecols) for path in orders_paths],ignore_index=True)
    rows = []
    p = helper(runtime)
    with p.pinned_imports(runtime/"modules",scratch):
        with (Path(scratch)/"g24.pkl").open("rb") as handle:
            g = pickle.load(handle)
        for compact,date in selected.items():
            d = int(np.flatnonzero(g.dates==int(compact))[0])
            native = np.logical_and.reduce([np.isfinite(getattr(g,k)[d]) for k in "ohlcv"])&(g.v[d]>=0)
            cached = set(np.flatnonzero(native))
            missing = sorted(set(range(511,901))-seen[compact])
            groups = np.split(missing,np.flatnonzero(np.diff(missing)>1)+1) if missing else []
            fmt = lambda x:f"{int(x)//60:02}:{int(x)%60:02}"
            checks = [j for j in range(540,871,30) if j not in seen[compact]]
            opening = [j+1 for j in range(540,871,30) if j+1 not in seen[compact]]
            order_mask = orders.order_type.eq("market")&orders.activation_minute.isin([d*1440+j for j in missing])
            source_row = bad.loc[bad.day==d].iloc[0]
            cash_count = len(set(range(511,901))&seen[compact])
            if cash_count==0:
                classification = "missing_entire_normal_cash_session"
            elif 511 not in seen[compact]:
                classification = "missing_frozen_cash_open_anchor"
            elif checks:
                classification = "missing_scheduled_decision_unclassified_closure"
            elif source_row.unknown_held_minutes or source_row.censored_positions or source_row.unmatched_orders:
                classification = "incomplete_execution_path"
            else:
                classification = "flat_nondecision_gap_observed_only_VWAP_allowed"
            rows.append(dict(date=date,day=d,classification=classification,
                missing_intervals=[dict(first=fmt(x[0]),last=fmt(x[-1]),minutes=len(x)) for x in groups],
                missing_scheduled_decisions=[fmt(j) for j in checks],
                missing_next_minute_entry_slots=[fmt(j) for j in opening],
                market_orders_activating_inside_missing=orders.loc[order_mask].to_dict("records"),
                missing_anchor_open=511 not in seen[compact],missing_1500_close=900 not in seen[compact],
                raw_native_cash_minutes=cash_count,cached_native_cash_minutes=int(native[511:901].sum()),
                raw_only_cash_minutes=sorted((seen[compact]-cached)&set(range(511,901))),
                cache_only_cash_minutes=sorted((cached-seen[compact])&set(range(511,901))),
                raw_cache_observed_masks_match=not ((seen[compact]^cached)&set(range(511,901))),
                is_canonical_baseline_trading_row=d in set(g.trading),
                raw_exports={key:dict(rows=sum(x["file"]==key for x in raw[compact]),
                    first_time=fmt(next((x["minute"] for x in raw[compact] if x["file"]==key),0)) if any(x["file"]==key for x in raw[compact]) else None,
                    last_time=fmt(next((x["minute"] for x in reversed(raw[compact]) if x["file"]==key),0)) if any(x["file"]==key for x in raw[compact]) else None,
                    cash_rows=sum(x["file"]==key and 511<=x["minute"]<=900 for x in raw[compact]))
                    for key in (f"data/NQ_1min_{compact[:4]}.csv",f"data/NQ_1min_ON_{compact[:4]}.csv")},
                unknown_held_minutes=int(source_row.unknown_held_minutes),delayed_orders=int(source_row.delayed_orders),
                censored_positions=int(source_row.censored_positions),unmatched_orders=int(source_row.unmatched_orders),
                verified_R2_known_closure_overlap_minutes=0,
                march2020_halt_candidate_unverified_in_R2_mask=date in ("2020-03-09","2020-03-12","2020-03-16","2020-03-18")))
    expected_dates = pd.bdate_range(a.date.min(),a.date.max())
    missing_dates = expected_dates.difference(pd.DatetimeIndex(a.date))
    closure_sources = json.loads((runtime/"calendar_source_provenance.json").read_text())
    for meta in closure_sources["sources"]:
        if sha(runtime/meta["staged"])!=meta["sha256"]:
            raise ValueError("Pinned known-closure source was edited")
    result = dict(ref=CLAUDE_REF,source_audits={str(Path(path).resolve().relative_to(ROOT)):sha(path) for path in audit_paths},
        source_orders={str(Path(path).resolve().relative_to(ROOT)):sha(path) for path in orders_paths},
        calendar_rows=len(a),normal_cash_dates=int(a.calendar_kind.eq("normal").sum()),
        expected_weekday_rows=len(expected_dates),omitted_weekday_dates=missing_dates.strftime("%Y-%m-%d").tolist(),
        grid_sha256=sha(Path(scratch)/"g24.pkl"),raw_versions=versions,days=rows,
        classification_counts=pd.Series([x["classification"] for x in rows]).value_counts().to_dict(),
        structural_audit_only=True,historical_account_or_baseline_returns_computed=False,
        account_gate_clear=not len(missing_dates) and not any(x["classification"]!="flat_nondecision_gap_observed_only_VWAP_allowed" for x in rows),
        known_closure_sources=closure_sources,
        no_cache_rebuild_or_price_imputation=True,
        criteria=["Flat gaps away from scheduled decisions are permitted by the frozen observed-only VWAP prefix when actual held/order paths remain complete.",
                  "A missing scheduled decision is unresolved unless an independently documented closure establishes there was no native bar.",
                  "An entirely absent normal cash session cannot silently become a zero-return date or be omitted from the baseline calendar.",
                  "A missing nominal next-minute slot is audited against actual queued market orders; next-observed execution is the registered rule.",
                  "Published R2 known_closed covers daily maintenance, weekends, early-close proxy and old15:16–15:30pause; it does not certify March2020 circuit breakers."])
    dump(runtime/"native_coverage_audit.json",result)
    return result


def _published_module(name, runtime=RUNTIME):
    """Execute exact published helper with its repository-relative __file__."""
    path = Path(runtime) / "published" / f"{name}.py"
    module = types.ModuleType("_s03_"+name)
    module.__file__ = str(ROOT / "analysis" / f"{name}.py")
    exec(compile(path.read_bytes(), module.__file__, "exec"), module.__dict__)
    return module


def helper(runtime=RUNTIME):
    verify_sources(runtime)
    p = _published_module("codex_or_pullback_plan", runtime)
    # Only the operational source context is replaced; the frozen functions and
    # current50K roster are unedited, and prepare has verified all old blobs.
    p.PINNED_REF = CLAUDE_REF
    p.DEFAULT_RUNTIME = Path(runtime) / "modules"
    if p.CURRENT_PLAN != FIFTY:
        raise ValueError("Published50K roster differs from the frozen adapter")
    return p


def engine(runtime=RUNTIME):
    """Compile only exact reviewed engine functions, avoiding research imports.

    Full original source files and hashes are staged. Function bodies are
    unchanged; disabling Numba's disk cache affects storage only. No main block,
    prior output, candidate, grid, or historical source ledger is imported.
    """
    from numba import njit
    module = types.ModuleType("_s03_account_engine")
    module.__dict__.update(np=np, pd=pd, njit=lambda **kw: njit(cache=False))
    selections = {"codex_ob_v2_accounts": ("quantity_states", "_table_minima", "make_table", "paired_ci"),
                  "codex_anson_accounts": ("lookup_one", "lookup_many", "rules", "run_table", "parity_check", "funded_summaries"),
                  "codex_r2vault_accounts": ("ChronologicalCI",)}
    for source, names in selections.items():
        path = Path(runtime) / "published" / f"{source}.py"
        tree = ast.parse(path.read_text(encoding="utf-8-sig"))
        nodes = [n for n in tree.body if isinstance(n, (ast.FunctionDef, ast.ClassDef)) and n.name in names]
        if {n.name for n in nodes} != set(names):
            raise ValueError(f"Canonical account engine functions missing: {source}")
        exec(compile(ast.Module(body=nodes, type_ignores=[]), str(path), "exec"), module.__dict__)
    module.acc = module
    return module


def candidate_paths(g, trades, fee=1.04, known_closed=None):
    """Raw geometry -> per1MNQ paths; reserve RT fee+entry tick at entry.

    Both protective stops and market exits pay one exit tick. Actual boundary
    extrema come from the replay; no pre-entry or post-exit excursion is used.
    Source net_NQ already includes baseline costs, so no second slippage layer
    is applied. Account fees replace .725 with1.04/1.24 per micro round trip.
    """
    w, r = np.zeros(g.o.shape), np.zeros(g.o.shape)
    for t in trades.itertuples():
        d, e, z, s = int(t.day), int(t.entry_j), int(t.exit_j), int(t.side)
        if s not in (-1, 1) or not 0 <= e <= z < g.o.shape[1]:
            raise ValueError("Invalid same-day S03 geometry")
        if t.entry_phase != "open" or t.exit_phase not in ("open", "intrabar"):
            raise ValueError("Unknown S03 executable phase")
        if bool(t.cross_date) or int(t.unknown_held_minutes) or int(t.kind) not in (0, 2):
            raise ValueError("Cross-date, unknown or non-frozen S03 exit")
        end = z+int(t.exit_phase != "open")
        price = np.array((g.l if s > 0 else g.h)[d, e:end], copy=True)
        if len(price):
            price[0] = float(t.entry_minute_adverse_px)
            if t.exit_phase != "open":
                price[-1] = float(t.exit_minute_adverse_px)
            if e == z and t.exit_phase != "open" and not np.isclose(
                    t.entry_minute_adverse_px, t.exit_minute_adverse_px, rtol=0, atol=1e-10):
                raise ValueError("Same-minute boundary extrema disagree")
            for offset in np.flatnonzero(~np.isfinite(price)):
                minute = e+int(offset)
                if known_closed is None or not known_closed[d, minute]:
                    raise ValueError("Unknown held-minute account price")
                previous = np.flatnonzero(np.isfinite(g.c[d, e:minute]))
                if not len(previous):
                    raise ValueError("No previous observed held Close during verified closure")
                price[offset] = g.c[d, e+previous[-1]]
        net = (float(t.raw_exit)-float(t.raw_entry))*s*2.-float(fee)-1.
        source_net = getattr(t, "net", getattr(t, "net_NQ", None))
        if source_net is None or not np.isclose(net+(fee-.725), float(source_net)/10., rtol=0, atol=1e-7):
            raise ValueError("S03 raw geometry/net/slippage convention differs")
        marks = (price-float(t.raw_entry))*s*2.-float(fee)-.5
        if len(marks) and t.exit_phase != "open":
            marks[-1] = min(marks[-1], net)
        w[d, e:end] += marks
        w[d, end:] += net
        r[d, z:] += net
    return w, r


def synthetic_fixtures(runtime=RUNTIME):
    g = SimpleNamespace(o=np.full((1,12),100.), h=np.full((1,12),101.),
                        l=np.full((1,12),99.), c=np.full((1,12),100.))
    row = dict(day=0, entry_j=2, exit_j=5, side=1, raw_entry=100., raw_exit=140.,
               entry_phase="open", exit_phase="open", kind=2, net=782.75,
               entry_minute_adverse_px=99., exit_minute_adverse_px=140.,
               cross_date=False, unknown_held_minutes=0)
    g.l[0,5] = 1.  # post-open-exit excursion must be excluded
    w,r = candidate_paths(g,pd.DataFrame([row]))
    np.testing.assert_allclose(w[0,2:5],-3.54)
    np.testing.assert_allclose(w[0,5:],77.96)
    np.testing.assert_allclose(r[0,5:],77.96)
    row.update(side=-1, raw_exit=60., entry_minute_adverse_px=101., exit_minute_adverse_px=60.)
    ws,rs = candidate_paths(g,pd.DataFrame([row]))
    np.testing.assert_array_equal(ws,w)
    np.testing.assert_array_equal(rs,r)
    row.update(side=1, raw_exit=90., kind=0, exit_phase="intrabar", net=-217.25,
               entry_minute_adverse_px=99., exit_minute_adverse_px=90.)
    w,r = candidate_paths(g,pd.DataFrame([row]))
    np.testing.assert_allclose(w[0,5:],-22.04)
    row.update(exit_j=2, entry_minute_adverse_px=90.)
    w,r = candidate_paths(g,pd.DataFrame([row]))
    np.testing.assert_allclose(w[0,2:],-22.04)
    twice = pd.DataFrame([row,dict(row,entry_j=7,exit_j=9,entry_minute_adverse_px=99.)])
    w,r = candidate_paths(g,twice)
    wh,rh = candidate_paths(g,twice,1.24)
    np.testing.assert_allclose(r[0,-1],-44.08)
    np.testing.assert_allclose(rh[0,-1]-r[0,-1],-.4)
    g.l[0,8] = np.nan
    try:
        candidate_paths(g,twice)
    except ValueError:
        pass
    else:
        raise AssertionError("Unknown held bar accepted")
    a = allocations(funded_plans()["150K_funded"],"150K_funded")
    assert set(a) == {"BASE","ADD_V2","EMPTY_VB","REPLACE_VB"}
    assert a["REPLACE_VB"]["S03_N"] == 3 and a["REPLACE_VB"]["S03_F"] == 1.5
    # Synthetic data exercise engine enumeration without historical returns.
    b = engine(runtime)
    q,_ = b.quantity_states(np.array([1.5,3.,8.]))
    assert (q>=0).all() and (np.diff(q,axis=0)>=0).all()
    return dict(long_short_symmetry=True, post_open_exit_extreme_excluded=True,
                stop_boundary_extreme=True, same_minute_stop=True, each_reentry_pays_fee=True,
                stress_each_reentry_pays_increment=True, unknown_held_bar_blocked=True,
                replacement_preserves_normal_flag_sizes=True, historical_returns_computed=False)


def canonical_engine_fixtures(runtime=RUNTIME, scratch=ROOT / "scratch_data"):
    """Compare both account engines using invented data only."""
    p, b = helper(runtime), engine(runtime)
    records = []
    with p.pinned_imports(Path(runtime)/"modules", scratch):
        for context, name in (("50K_funded","funded_sim"),("150K_funded","funded_sim150")):
            f = importlib.import_module(name)
            rng = np.random.default_rng(7714)
            k,d,m = 5,40,17
            c = rng.normal(28,100,(k,d))
            w = np.minimum(rng.normal(-30,100,(k,d,m)),c[:,:,None])
            base = rng.uniform(.1,12,(k,d))
            base[:,0] = [0.,1.,2.,3.999999999,10.333333333]
            hist = rng.integers(0,d,(5,500))
            for label, ww, cc, bb in [("random_rounding",w,c,base)] + [
                (tag,np.full((1,d,3),low),np.full((1,d),close),np.full((1,d),qty))
                for tag,close,low,qty in (("payout",350.,-10.,1.),("trail",-500.,-5000.,1.),
                ("dll",100.,-1100. if context.startswith("50") else -2100.,1.),("zero_quantity",0.,0.,0.))]:
                table = b.make_table(ww,cc,bb)
                records += b.parity_check(ww,cc,table,hist,f,b.rules(f,context),context+"/"+label)
    return dict(exact_records=len(records),records=records,historical_returns_computed=False)


def _exact_other_fee_metadata(lab, scratch):
    """Recover exact CLS/MOC event counts directly from canonical source rules.

    This executes only after the return gate. Unlike a nonzero-day count, it
    includes zero-net trades and records the exact source event inventory.
    """
    fb, er = importlib.import_module("funded_bootstrap"), importlib.import_module("s_rank_es_round1_test")
    # Capture the exact existing MOC generator's trade ledger without altering
    # its path calculation. Temporarily intercept its pure trades() return.
    saved, captured = er.trades, []
    def capture(*args, **kwargs):
        t = saved(*args, **kwargs)
        captured.append(t.copy())
        return t
    er.trades = capture
    oldw, oldc = lab.W["MOC_MES"], lab.C["MOC_MES"]
    try:
        fb.add_moc_mes(lab,str(Path(scratch).resolve())+"/")
        if len(captured) != 1:
            raise ValueError("Canonical MOC trade inventory not captured exactly once")
        t = captured[0]
        idx = pd.Index(lab.g.ts).get_indexer(pd.to_datetime(t.date).dt.normalize())
        if (idx<0).any():
            raise ValueError("MOC dates missing in NQ calendar")
        n = np.bincount(idx,minlength=len(lab.g.ts))[lab.tr]
        np.testing.assert_allclose(oldc,lab.C["MOC_MES"]-(1.04-.5)*n,rtol=0,atol=1e-7)
        first = np.full(len(lab.g.ts),1440)
        np.minimum.at(first,idx,t.j0.to_numpy(int))
        lab.N["MOC_MES"],lab.J0["MOC_MES"] = n,first[lab.tr]
    finally:
        er.trades = saved
        lab.W["MOC_MES"],lab.C["MOC_MES"] = oldw,oldc
    # CLS: the canonical fast_plan_lab source admits each eligible Sunday once,
    # booked on Monday, provided its entry Open exists. No return inference.
    with (Path(scratch)/"cl.pkl").open("rb") as handle:
        cl = pickle.load(handle)
    with (Path(scratch)/"s_rank_gap2.pkl").open("rb") as handle:
        fr = pickle.load(handle)["frames"]["CL"]
    dates = []
    for row in fr.itertuples():
        if row.ok and row.gA >= .1 and np.isfinite(cl.o[int(row.sun),1026]):
            dates.append(pd.Timestamp(cl.ts[int(row.mon)]))
    idx = pd.Index(lab.g.ts).get_indexer(dates)
    idx = idx[idx>=0]
    n = np.bincount(idx,minlength=len(lab.g.ts))[lab.tr]
    counted_before = ((lab.C["CLS"]!=0)|(np.abs(lab.W["CLS"]).max(axis=1)>0)).astype(int)
    np.testing.assert_array_equal(counted_before,n,err_msg="Canonical CLS fee inference differs from exact event count")
    lab.N["CLS"],lab.J0["CLS"] = n,np.where(n>0,0,1440)
    return dict(MOC_MES=int(lab.N["MOC_MES"].sum()),CLS=int(n.sum()),
                count_source="canonical emitted MOC ledger / exact CLS admission events",zero_net_events_retained=True)


def build_baseline(scratch, *, preregistration_commit, gate, runtime=RUNTIME, out=OUT):
    """Build current canonical paths only after the passed root account gate.

    Recreates the50K source adapter from ordinary scratch caches; adds current
    RS-both and DT exactly as the published Anson adapter. No prior task cache
    or saved account return is required.
    """
    if gate.get("account_run_authorized") is not True or gate.get("design_gate_passed") is not True:
        raise PermissionError("Account/baseline return gate is closed")
    runtime,out,scratch = Path(runtime),Path(out),Path(scratch).resolve()
    p,b = helper(runtime),engine(runtime)
    baseline_out = out/"baseline"
    bundle = p.build_current_plan(scratch,preregistration_commit=preregistration_commit,
        authorized_returns=True,runtime=runtime/"modules",audit_dir=baseline_out,fee=1.04)
    with p.pinned_imports(runtime/"modules",scratch):
        lab = bundle.lab
        # P reprices the two funded VB partitions, while its auxiliary whole
        # VB path remains at the old fee. Reprice that auxiliary personal/
        # inventory column explicitly; funded configurations use the splits.
        lab.real_fees(1.04-.725,["VB"])
        np.testing.assert_allclose(lab.C["VB"],lab.C["VB_N"]+lab.C["VB_F"],rtol=0,atol=1e-7)
        rs = pd.read_csv(baseline_out/"baseline_rs_replay.csv",parse_dates=["date"])
        rs["kind"] = rs.kind.map({"stop":0,"target":1,"flat":2})
        if rs.kind.isna().any():
            raise ValueError("Unexpected RS exit kind")
        lab.add("RS",rs)
        lab.real_fees(1.04-.725,["RS"])
        expected = np.bincount(rs.day.to_numpy(int),weights=rs.net.to_numpy()/10-.315,
                               minlength=len(lab.g.ts))[lab.tr]
        np.testing.assert_allclose(lab.C["RS"],expected,rtol=0,atol=1e-7)
        # Use the published reconciliation function, without importing its
        # unrelated cache loader or research helpers.
        source = runtime/"published/codex_anson_plan.py"
        node = next(n for n in ast.parse(source.read_text()).body
                    if isinstance(n,ast.FunctionDef) and n.name=="_dt_reconcile")
        ns = dict(np=np,pd=pd)
        exec(compile(ast.Module(body=[node],type_ignores=[]),str(source),"exec"),ns)
        dt = pd.read_csv(runtime/"modules/DT_timed.csv",parse_dates=["date"])
        dt,audit,mismatch = ns["_dt_reconcile"](dt,runtime/"modules/DT_reference.csv",
            pd.DatetimeIndex(lab.g.ts[lab.tr]).max())
        mismatch.to_csv(baseline_out/"dt_mismatches.csv",index=False)
        if audit["mismatch_rows"]:
            raise ValueError("Current DT committed timed ledger differs from reference")
        ent,sig = dt.entry_time.to_numpy(int),dt.sig_time.to_numpy(int)
        np.testing.assert_array_equal(ent//100*60+ent%100,sig//100*60+sig%100+1)
        dmodule = importlib.import_module("dual_thrust_test")
        lab.add("DT",dmodule.lab_trades(lab.g,dt))
        lab.real_fees(1.04-.725,["DT"])
        idx = pd.Index(lab.g.ts).get_indexer(dt.date)
        expected = np.bincount(idx,weights=dt.net.to_numpy()/10-.315,minlength=len(lab.g.ts))[lab.tr]
        np.testing.assert_allclose(lab.C["DT"],expected,rtol=0,atol=1e-7)
        exact = _exact_other_fee_metadata(lab,scratch)
        needed = set().union(*(set(x) for x in funded_plans().values())) | {"VB","RS"}
        for field in ("W","C","N","J0"):
            data = getattr(lab,field)
            for name in list(data):
                if name not in needed:
                    del data[name]
        if any(n not in lab.N for n in needed):
            raise ValueError("A baseline leg lacks exact per-day trade counts")
        for name in needed:
            if not np.isfinite(lab.W[name]).all() or not np.isfinite(lab.C[name]).all():
                raise ValueError(f"Nonfinite canonical baseline path: {name}")
        dates = pd.DatetimeIndex(lab.g.ts[lab.tr])
        counts = pd.DataFrame({k:lab.N[k] for k in needed},index=dates)
        counts.to_csv(baseline_out/"exact_trade_counts.csv",index_label="date")
        credits = counts.mul(pd.Series({k:.5 if k=="MOC_MES" else .725 for k in needed}))
        credits.to_csv(baseline_out/"original_commission_credit.csv",index_label="date")
        pd.DataFrame({k:lab.C[k] for k in needed},index=dates).to_csv(
            baseline_out/"daily_values_1.04.csv",index_label="date")
        metadata = dict(ref=CLAUDE_REF,codex_ref=CODEX_REF,fee=1.04,
            preregistration_commit=preregistration_commit,plans=funded_plans(),
            dt_reconciliation=audit,rs_reconciliation=bundle.source_manifest["rs_reconciliation"],
            exact_other_fee_counts=exact,counts_sha256=sha(baseline_out/"exact_trade_counts.csv"),
            source_manifest_sha256=sha(runtime/"manifest.json"),baseline_limits=p.BASELINE_LIMITS,
            baseline_cache_rebuilt_from_canonical_sources=True,original_scratch_caches_rewritten=False)
        dump(baseline_out/"manifest.json",metadata)
        return SimpleNamespace(lab=lab,p=p,engine=b,metadata=metadata,
            funded50=importlib.import_module("funded_sim"),funded150=importlib.import_module("funded_sim150"),
            bootstrap=importlib.import_module("funded_bootstrap"))


def read_candidate(lab, ledger_path, audit_path, out):
    """Enforce whole canonical calendar; unknown rows never become zero P&L."""
    t = pd.read_csv(ledger_path,parse_dates=["date"])
    t = t.rename(columns={k:v for k,v in (("j0","entry_j"),("j1","exit_j")) if v not in t})
    required = {"day","entry_j","exit_j","side","raw_entry","raw_exit","net","kind",
                "entry_phase","exit_phase","entry_minute_adverse_px","exit_minute_adverse_px",
                "cross_date","unknown_held_minutes","execution_complete"}
    if not required.issubset(t):
        raise ValueError("Candidate ledger missing fields: "+str(sorted(required-set(t))))
    if not t.execution_complete.eq(True).all() or t.cross_date.ne(False).any() or t.unknown_held_minutes.ne(0).any():
        raise ValueError("Incomplete or non-Apex-safe candidate trade")
    if "qty" in t and not t.qty.eq(1).all():
        raise ValueError("Candidate ledger must be per-one-NQ geometry")
    for col,expected in (("entry",t.raw_entry+t.side*.25),("exit",t.raw_exit-t.side*.25)):
        if col in t:
            np.testing.assert_allclose(t[col],expected,rtol=0,atol=1e-7)
    intrastop = t.kind.eq(0)&t.exit_phase.eq("intrabar")
    if intrastop.any():
        if "stop" not in t:
            raise ValueError("Protective stop geometry missing")
        np.testing.assert_allclose(t.loc[intrastop,"raw_exit"],t.loc[intrastop,"stop"],rtol=0,atol=1e-7)
    if t.empty:
        raise ValueError("Gate passed but candidate ledger is empty")
    if not t.day.isin(lab.tr).all():
        raise ValueError("Candidate trade dates are outside canonical trading calendar")
    date = pd.DatetimeIndex(lab.g.ts[t.day.to_numpy(int)]).normalize()
    if not np.array_equal(date.to_numpy(),t.date.dt.normalize().to_numpy()):
        raise ValueError("Candidate source dates/grid rows differ")
    ge = t.day.to_numpy(int)*1440+t.entry_j.to_numpy(int)
    gx = t.day.to_numpy(int)*1440+t.exit_j.to_numpy(int)
    if len(t)>1:
        sequential = (ge[1:]>gx[:-1]) | ((ge[1:]==gx[:-1]) & (t.exit_phase.to_numpy()[:-1]=="open"))
        if not sequential.all():
            raise ValueError("Candidate ledger reordered, duplicated, or overlapping")
    np.testing.assert_allclose(lab.g.o.ravel()[ge],t.raw_entry,rtol=0,atol=1e-7)
    for phase,field in (("open","o"),):
        use = t.exit_phase.eq(phase)
        np.testing.assert_allclose(getattr(lab.g,field).ravel()[gx[use]],t.loc[use,"raw_exit"],rtol=0,atol=1e-7)
    audit = pd.read_csv(audit_path,parse_dates=["date"])
    key = "day" if "day" in audit else "gridrow"
    if key not in audit or audit[key].duplicated().any():
        raise ValueError("Full-calendar day audit lacks unique gridrow")
    scope = lab.tr[pd.DatetimeIndex(lab.g.ts[lab.tr]).year>=2018]
    detail = audit.set_index(key).reindex(scope)
    if detail.date.isna().any():
        raise ValueError("Candidate audit omits canonical trading dates; no account scoring")
    if not np.array_equal(pd.to_datetime(detail.date).dt.normalize().to_numpy(),
                          pd.DatetimeIndex(lab.g.ts[scope]).normalize().to_numpy()):
        raise ValueError("Candidate day-audit dates differ from canonical grid")
    for col in ("unknown_held_minutes","censored_positions","unmatched_orders"):
        if col not in detail or detail[col].isna().any() or detail[col].ne(0).any():
            raise ValueError(f"Candidate full-calendar audit incomplete: {col}")
    if "account_eligible" not in detail or not detail.account_eligible.eq(True).all():
        raise ValueError("Candidate incomplete calendar cannot be narrowed after returns")
    if not {"calendar_kind","missing_cash_minutes"}.issubset(detail):
        raise ValueError("Full source-minute coverage audit is required")
    # Observed-only cumulative VWAP is the frozen rule. Missing minutes while
    # flat, away from scheduled decisions, do not by themselves make that
    # reconstruction incomplete. Require all normal-date decision/anchor bars
    # and do not let g.trading's missing whole date hide the source omission.
    all_normal = audit.loc[audit.calendar_kind.eq("normal")&audit.date.ge("2018-01-01")].copy()
    normal_rows = all_normal[key].to_numpy(int)
    native = np.logical_and.reduce([np.isfinite(getattr(lab.g,k)[normal_rows]) for k in "ohlcv"])
    native &= lab.g.v[normal_rows]>=0
    checks = np.arange(540,871,30)
    source_unknown = ~native[:,checks].all(axis=1)|~native[:,511]|~native[:,511:901].any(axis=1)
    all_normal.loc[source_unknown].to_csv(Path(out)/"unknown_source_calendar_rows.csv",index=False)
    if source_unknown.any():
        raise ValueError("A normal source date lacks anchor/decision coverage; resolve documented closures or whole-date data omission")
    detail.to_csv(Path(out)/"common_day_audit.csv",index_label="gridrow")
    dump(Path(out)/"calendar.json",dict(canonical_days=len(scope),retained_days=len(scope),
         excluded_days=0,ledger_rows=len(t),unknown_held_minutes=0,censored_positions=0,
         no_calendar_compression=True,source_ledger_sha256=sha(ledger_path),source_audit_sha256=sha(audit_path)))
    return t


def histories(lab, bootstrap, out):
    dates = pd.DatetimeIndex(lab.g.ts[lab.tr])
    result = {}
    for cohort,(lo,hi) in COHORTS.items():
        boot = bootstrap.Boot(lab,start=lo)
        boot.days = boot.days[np.asarray(dates[boot.days]<hi)]
        if not len(boot.days):
            raise ValueError("No canonical days in requested account cohort")
        result[cohort] = np.concatenate([boot._histories(250,500,20,seed) for seed in (1,2,3,4)])
        np.save(Path(out)/f"funded_histories_{cohort}.npy",result[cohort])
    return result


def paired_intervals(delta,seed=902,n=5000):
    """Same reviewed IID paired draws; report both preregistered CI levels."""
    delta = np.asarray(delta,dtype=float)
    rng,means = np.random.default_rng(seed),np.empty(n)
    for start in range(0,n,100):
        size = min(100,n-start)
        idx = rng.integers(0,len(delta),(size,len(delta)))
        means[start:start+size] = delta[idx].mean(axis=1)
    a,bb,c,d = np.percentile(means,[2.5,5,95,97.5])
    return dict(lo=float(a),hi=float(d),lo95=float(a),hi95=float(d),lo90=float(bb),hi90=float(c))


def chronological_intervals(ci,delta):
    delta = np.asarray(delta,float)
    values = delta[ci.idx]
    np.multiply(values,ci.take_valid,out=values)
    mean = values.sum(axis=1)/ci.denominator
    a,bb,c,d = np.percentile(mean,[2.5,5,95,97.5])
    return dict(lo=float(a),hi=float(d),lo95=float(a),hi95=float(d),lo90=float(bb),hi90=float(c))


def funded_comparisons(bundle, fee, hist, out):
    lab,b = bundle.lab,bundle.engine
    rows,paired,parity,resources = [],[],[],[]
    for context,f in (("50K_funded",bundle.funded50),("150K_funded",bundle.funded150)):
        results = {cohort:{} for cohort in hist}
        for name,plan in allocations(funded_plans()[context],context).items():
            started = time.monotonic()
            keys = sorted(plan)
            w,c = np.stack([lab.W[k] for k in keys]),np.stack([lab.C[k] for k in keys])
            names,base = lab._base({k:plan[k] for k in keys})
            if names!=keys:
                raise ValueError("Canonical summation order changed")
            table = b.make_table(w,c,base)
            # BASE is always checked and scored before any candidate plan.
            parity += b.parity_check(w,c,table,hist["2018_plus"][[0,1,17,333,999]],f,b.rules(f,context),
                                     f"{fee}/{context}/{name}")
            for cohort,h in hist.items():
                values=[]
                for horizon in (250,500):
                    # Chunk histories; never allocate all1,000 original
                    # strategy-minute histories simultaneously.
                    values.append(np.concatenate([b.run_table(table,h[i:i+100],horizon,b.rules(f,context))
                                                   for i in range(0,len(h),100)]))
                results[cohort][name] = tuple(values)
            resources.append(dict(context=context,config=name,fee=fee,
                                  seconds=time.monotonic()-started,max_quantity_states=int(table["counts"].max())))
            print(f"funded {fee:.2f} {context} {name}",flush=True)
            del w,c,table
            gc.collect()
        for cohort,result in results.items():
            a,bb = b.funded_summaries(result,fee,context,cohort)
            for row in a:
                one,two = result[row["config"]]
                row["year1_breached"] = float(one[:,3].mean())
                row["year1_all6"] = float((one[:,1]==6).mean())
                row["days_first_median"] = float(np.median(two[two[:,4]>0,4])) if (two[:,4]>0).any() else np.inf
            for row in bb:
                one,two = result[row["config"]]
                a0,b0 = result[row["reference"]]
                delta = {"year1":one[:,0]-a0[:,0],"year2":two[:,0]-b0[:,0],
                         "blown":two[:,3]-b0[:,3],"all6":(two[:,1]==6).astype(float)-(b0[:,1]==6)}[row["metric"]]
                interval = paired_intervals(delta)
                np.testing.assert_allclose([row["lo"],row["hi"]],[interval["lo"],interval["hi"]],rtol=0,atol=1e-12)
                row.update(interval)
            rows += a
            paired += bb
            np.savez_compressed(Path(out)/f"funded_results_{fee:.2f}_{context}_{cohort}.npz",
                **{f"{k}__{h}":result[k][i] for k in result for i,h in enumerate((250,500))})
    dump(Path(out)/f"funded_parity_{fee:.2f}.json",parity)
    dump(Path(out)/f"funded_resources_{fee:.2f}.json",resources)
    return rows,paired


def evaluation_comparisons(bundle,scratch,prereg,fee,paths,out,runtime=RUNTIME):
    lab,p,b = bundle.lab,bundle.p,bundle.engine
    base = p.evaluation_parts(scratch,preregistration_commit=prereg,authorized_returns=True,
                             runtime=Path(runtime)/"modules",fee=fee,grid=lab.g)
    ev150,build = importlib.import_module("plan_150k_test"),importlib.import_module("build_lab")
    atr = lab.g.daily_atr(15)[lab.tr]
    risk = lambda dollars,m:np.floor(dollars/(np.nan_to_num(m*atr,nan=1e12)*2.))[:,None]
    q150 = dict(VB=20.,ONB30=risk(2750,.25),MON_BR=5.,EOS=risk(1250,build.REPORTS["EOS"][1]))
    specs = {"50K_evaluation":(base.quantities,base.challenge),"150K_evaluation":(q150,ev150.evaluation)}
    last = np.full(lab.D,np.datetime64("NaT"),dtype="datetime64[ns]")
    last[:lab.D-20] = base.dates[20:].to_numpy()
    complete = np.arange(lab.D)+21<=lab.D
    masks = {k:np.asarray((base.dates>=lo)&(base.dates<hi)&(last<np.datetime64(hi)))
             for k,(lo,hi) in COHORTS.items()}
    intervals = {k:b.ChronologicalCI(complete[mask]) for k,mask in masks.items()}
    rows,paired = [],[]
    for context,(q,challenge) in specs.items():
        pp = base.parts
        bw,br = sum(pp[k][0]*q[k] for k in q),sum(pp[k][1]*q[k] for k in q)
        ew,er = bw-pp["VB"][0]*q["VB"],br-pp["VB"][1]*q["VB"]
        raw = {}
        for name,plan in allocations(q,context).items():
            if name=="BASE":
                w,r = bw,br
            elif name=="EMPTY_VB":
                w,r = ew,er
            else:
                w0,r0 = (ew,er) if name=="REPLACE_VB" else (bw,br)
                cw,cr = paths
                w,r = w0+cw*plan["S03"],r0+cr*plan["S03"]
            if context.startswith("50"):
                values = [challenge(w,r,np.arange(s,min(s+21,lab.D)),lambda p,c,n:1.) for s in range(lab.D)]
            else:
                values = [challenge(w,r,s,lab.D,ev150.R150) for s in range(lab.D)]
            outcome = np.array([x[0] if x else "" for x in values])
            days = np.array([x[1] if x else 0 for x in values])
            raw[name] = outcome,days
            for cohort,mask in masks.items():
                ok = complete&mask
                rows.append(dict(context=context,fee=fee,cohort=cohort,config=name,starts=int(ok.sum()),
                    passed=float((outcome[ok]=="pass").mean()),failed=float((outcome[ok]=="fail").mean()),
                    timed_out=float((outcome[ok]=="time").mean()),
                    median_pass_days=float(np.median(days[ok&(outcome=="pass")]))))
            print(f"evaluation {fee:.2f} {context} {name}",flush=True)
            if name not in ("BASE","EMPTY_VB"):
                del w,r
        for name,(o,d) in raw.items():
            for cohort,mask in masks.items():
                for ref in ("BASE","EMPTY_VB"):
                    for metric,label in (("passed","pass"),("failed","fail"),("timed_out","time")):
                        delta = (o[mask]==label).astype(float)-(raw[ref][0][mask]==label)
                        paired.append(dict(context=context,fee=fee,cohort=cohort,config=name,reference=ref,
                                           metric=metric,delta=float(delta[complete[mask]].mean()),
                                           **chronological_intervals(intervals[cohort],delta)))
        frame = pd.DataFrame({f"{k}__{c}":v[i] for k,v in raw.items()
                              for i,c in enumerate(("outcome","days"))},index=base.dates)
        frame["complete_21session_start"],frame["window_last_date"] = complete,last
        for cohort,mask in masks.items():
            frame[cohort+"__whole_window_inside"] = mask
        frame.to_csv(Path(out)/f"evaluation_starts_{fee:.2f}_{context}.csv",index_label="date")
        del bw,br,ew,er
        gc.collect()
    return rows,paired


def concurrent_exposure(bundle,trades,scratch,out,runtime=RUNTIME):
    """NQ gross exposure, separating same/opposite sides without netting.

    Baseline MC minute endpoints are inclusive; candidate open exits are
    exclusive. The inherited Bridge Sunday-to-Monday booking approximation is
    retained and disclosed. Quantities are full-size integer bounds; actual
    funded cushion quantities vary by bootstrap history.
    """
    lab = bundle.lab
    pf,build = importlib.import_module("portfolio"),importlib.import_module("build_lab")
    bridge,dt = importlib.import_module("bridge_monday_confirm"),importlib.import_module("dual_thrust_test")
    dates = pd.DatetimeIndex(lab.g.ts[lab.tr])
    lookup = {int(row):i for i,row in enumerate(lab.tr)}
    shape = lab.D,lab.g.o.shape[1]
    flags = pd.read_pickle(Path(scratch)/"single_print_sessions.pkl").flag.reindex(dates).fillna(False).to_numpy(bool)
    raw = {name:pf.load_mc(lab.g,build.REPORTS[name][0])
           for name in ("VB","ONB_ML2_MC","MON_MC","EOS","LDF_MC","NFP_MC")}
    raw["MON_BR_MC"] = bridge.load_bridge_mc(lab.g)
    rs = pd.read_csv(Path(out)/"baseline/baseline_rs_replay.csv")
    raw["RS"],raw["RS_L"] = rs,rs.loc[rs.side>0]
    timed = pd.read_csv(Path(runtime)/"modules/DT_timed.csv",parse_dates=["date"])
    timed = timed[timed.date<=dates.max()]
    raw["DT"] = dt.lab_trades(lab.g,timed)
    flagged = raw["VB"].day.map(dict(zip(lab.tr,flags))).fillna(False).to_numpy(bool)
    raw["VB_N"],raw["VB_F"] = raw["VB"].loc[~flagged],raw["VB"].loc[flagged]

    def occupancy(ledger,quantity,candidate=False):
        long,short = np.zeros(shape,dtype=np.int32),np.zeros(shape,dtype=np.int32)
        for t in ledger.itertuples():
            d = lookup.get(int(t.day))
            if d is None or quantity[d]<=0:
                continue
            e = int(t.entry_j if candidate else t.j0)
            z = int(t.exit_j if candidate else t.j1)+1
            if candidate and t.exit_phase=="open":
                z -= 1
            (long if t.side>0 else short)[d,e:z] += int(quantity[d])
        return long,short

    cl,cs = occupancy(trades,np.ones(lab.D),True)
    held = cl+cs>0
    rows,legs,timing = [],[],[]
    for context,plan in funded_plans().items():
        names,base = lab._base({k:plan[k] for k in plan if k in raw})
        qty = np.floor(base+1e-9)
        long,short = np.zeros(shape,dtype=np.int32),np.zeros(shape,dtype=np.int32)
        vbgross = np.zeros(shape,dtype=np.int32)
        for i,name in enumerate(names):
            ll,ss = occupancy(raw[name],qty[i])
            long += ll
            short += ss
            if name.startswith("VB_"):
                vbgross += ll+ss
            for cohort,(lo,hi) in COHORTS.items():
                use = held&np.asarray((dates>=lo)&(dates<hi))[:,None]
                total = int(use.sum())
                if total:
                    legs.append(dict(context=context,cohort=cohort,leg=name,candidate_held_minutes=total,
                        overlap_minutes=int((use&(ll+ss>0)).sum()),
                        same_side_minutes=int((use&(np.where(cl>0,ll,ss)>0)).sum()),
                        opposite_side_minutes=int((use&(np.where(cl>0,ss,ll)>0)).sum())))
            del ll,ss
        gross = long+short
        same,opposite = np.where(cl>0,long,short),np.where(cl>0,short,long)
        add = 2 if context.startswith("150") else 1
        normal,flagged_size = plan["VB_N"],plan["VB_F"]
        replace = np.floor(np.where(flags,flagged_size,normal)+1e-9).astype(int)
        for cohort,(lo,hi) in COHORTS.items():
            use = held&np.asarray((dates>=lo)&(dates<hi))[:,None]
            total = int(use.sum())
            if not total:
                continue
            rows.append(dict(context=context,cohort=cohort,candidate_held_minutes=total,
                current_nq_overlap_fraction=float((use&(gross>0)).sum()/total),
                same_side_fraction=float((use&(same>0)).sum()/total),
                opposite_side_fraction=float((use&(opposite>0)).sum()/total),
                max_current_gross_mnq=int(gross[use].max(initial=0)),
                max_ADD_V2_gross_mnq=int((gross+add)[use].max(initial=0)),
                max_REPLACE_VB_gross_mnq=int((gross-vbgross+replace[:,None])[use].max(initial=0))))
        # Show the candidate at BASE's full-size adverse minute. This is a
        # descriptive timing diagnostic, not a claim of a pre-breach hedge.
        keys,bases = lab._base({k:plan[k] for k in sorted(plan)})
        w = np.zeros(shape)
        for i,name in enumerate(keys):
            w += lab.W[name]*np.floor(bases[i]+1e-9)[:,None]
        j = w.argmin(axis=1)
        for cohort,(lo,hi) in COHORTS.items():
            use = np.asarray((dates>=lo)&(dates<hi))
            cand = lab.W["S03"][np.arange(lab.D),j]*add
            loss = use&(w[np.arange(lab.D),j]<0)
            timing.append(dict(context=context,cohort=cohort,baseline_adverse_days=int(loss.sum()),
                candidate_positive_at_baseline_adverse_minute=int((loss&(cand>0)).sum()),
                candidate_negative_at_baseline_adverse_minute=int((loss&(cand<0)).sum()),
                candidate_net_mark_sum_at_baseline_adverse_minute=float(cand[loss].sum())))
        del long,short,gross,vbgross,same,opposite,w
        gc.collect()
    pd.DataFrame(rows).to_csv(Path(out)/"concurrent_nq_exposure.csv",index=False)
    pd.DataFrame(legs).to_csv(Path(out)/"concurrent_nq_by_leg.csv",index=False)
    pd.DataFrame(timing).to_csv(Path(out)/"candidate_at_baseline_adverse_minute.csv",index=False)
    dump(Path(out)/"concurrent_exposure_metadata.json",dict(
        scope="NQ/MNQ gross; ES/CL excluded; full-size integer quantities before history-specific funded cushion",
        same_opposite_separate=True,opposite_positions_never_netted=True,
        baseline_endpoints="inclusive MC bars; Bridge retains Monday booking of Sunday exposure",
        candidate_endpoints="entry inclusive; open exit exclusive; intrabar stop exit inclusive",
        causal_protection_before_account_breach_established=False))


def run(args):
    """Entrypoint reserved for explicit root authorization after design passes."""
    gate = require_gate(args.prereg,args.gate,args.ledger,args.audit,args.plan_path)
    runtime,out = Path(args.runtime),Path(args.out)
    out.mkdir(parents=True,exist_ok=True)
    prepare(args.scratch,runtime)
    bundle = build_baseline(args.scratch,preregistration_commit=args.prereg,gate=gate,runtime=runtime,out=out)
    lab,p = bundle.lab,bundle.p
    started = time.monotonic()
    with p.pinned_imports(runtime/"modules",args.scratch):
        t = read_candidate(lab,args.ledger,args.audit,out)
        hist = histories(lab,bundle.bootstrap,out)
        dates = pd.DatetimeIndex(lab.g.ts[lab.tr])
        flags = pd.read_pickle(Path(args.scratch)/"single_print_sessions.pkl").flag.reindex(dates).fillna(False).to_numpy(bool)
        fr,fp,er,ep = [],[],[],[]
        for fee in FEES:
            if fee>1.04:
                lab.real_fees(.20,list(set().union(*(set(p) for p in funded_plans().values()))))
            w,r = candidate_paths(lab.g,t,fee)
            paths = w[lab.tr],r[lab.tr]
            lab.W["S03"],lab.C["S03"] = paths[0],paths[1][:,-1]
            for name,mask in (("S03_N",~flags),("S03_F",flags)):
                lab.W[name],lab.C[name] = paths[0]*mask[:,None],paths[1][:,-1]*mask
            del w,r
            if fee==1.04:
                concurrent_exposure(bundle,t,args.scratch,out,runtime)
            a,bb = funded_comparisons(bundle,fee,hist,out)
            fr += a
            fp += bb
            pd.DataFrame(fr).to_csv(out/"funded_summary.csv",index=False)
            pd.DataFrame(fp).to_csv(out/"funded_paired_differences.csv",index=False)
            a,bb = evaluation_comparisons(bundle,args.scratch,args.prereg,fee,paths,out,runtime)
            er += a
            ep += bb
            pd.DataFrame(er).to_csv(out/"evaluation_summary.csv",index=False)
            pd.DataFrame(ep).to_csv(out/"evaluation_paired_differences.csv",index=False)
    dump(out/"reproduction.json",dict(preregistration_commit=args.prereg,gate_sha256=sha(args.gate),
        source_manifest_sha256=sha(runtime/"manifest.json"),script_sha256=sha(__file__),
        current_context=CLAUDE_REF,published_wrappers=CODEX_REF,fees=FEES,configs=4,
        funded=dict(paired_histories=1000,horizons=[250,500],block=20,seeds=[1,2,3,4],chunk=100),
        evaluation=dict(real_sessions=21,whole_window_cohort=True,CI_block=20,CI_samples=5000,
                        tie_policy={"50K":"pass first","150K":"breach first"}),
        calendar_exclusions=0,candidate_cost="raw geometry; RTfee+entrytick reserved at entry; exitmarket/stoptick",
        limits=p.BASELINE_LIMITS+["Minute OHLC cannot prove tick order.",
             "Daily P&L correlation cannot establish protection before an account breach."],
        seconds=time.monotonic()-started))


def audit_only(args):
    """Publish a data-limited result for every Apex destination, without P&L.

    Only source coverage/order metadata, raw CSV row timestamps, and finite
    cached OHLCV masks are inspected. No baseline is built and no account
    simulator or candidate path/return calculation is called.
    """
    if args.run:
        raise ValueError("--audit-only and --run are mutually exclusive")
    out,runtime = Path(args.out).resolve(),Path(args.runtime).resolve()
    source = out.parent
    audits = [source/"design_V2_day_audit.csv",source/"recent_V2_day_audit.csv"]
    orders = [source/"design_V2_orders.csv",source/"recent_V2_orders.csv"]
    held_path = Path(args.held_gaps).resolve() if args.held_gaps else source/"recent_V2_unknown_held_minutes.csv"
    detail = native_coverage_audit(audits,orders,scratch=args.scratch,runtime=runtime)
    out.mkdir(parents=True,exist_ok=True)
    dump(out/"native_coverage_audit.json",detail)
    held = pd.read_csv(held_path,parse_dates=["date"])
    date_values = set(held.date.dt.strftime("%Y%m%d"))
    raw_rows = {d:[] for d in date_values}
    for year in sorted({d[:4] for d in date_values}):
        for prefix in ("","ON_"):
            path = ROOT/"data"/f"NQ_1min_{prefix}{year}.csv"
            with path.open(newline="") as handle:
                for number,row in enumerate(csv.DictReader(handle),2):
                    if row["date"] not in date_values:
                        continue
                    hm = int(row["time"])
                    native = all(math.isfinite(float(row[k])) for k in ("open","high","low","close"))
                    raw_rows[row["date"]].append(dict(path=str(path.relative_to(ROOT)),line=number,
                        j=hm//100*60+hm%100,close_time=f"{hm//100:02}:{hm%100:02}",native_OHLC=native))
    gap_rows = []
    for x in held.itertuples():
        compact = pd.Timestamp(x.date).strftime("%Y%m%d")
        rows = raw_rows[compact]
        matches = [r for r in rows if r["j"]==int(x.j)]
        day_detail = next(y for y in detail["days"] if y["day"]==int(x.day))
        gap_rows.append(dict(date=str(pd.Timestamp(x.date).date()),day=int(x.day),j=int(x.j),
            close_time=f"{int(x.j)//60:02}:{int(x.j)%60:02}",entry_order_id=int(x.entry_order_id),
            raw_rows_at_missing_minute=matches,
            neighboring_raw_rows=[r for r in rows if abs(r["j"]-int(x.j))<=2],
            raw_source_minute_absent=not any(r["native_OHLC"] for r in matches),
            raw_cache_observed_masks_match=day_detail["raw_cache_observed_masks_match"],
            classification="unknown_native_OHLC_while_candidate_held",
            account_effect="Possible stop crossing inside an unobserved held minute cannot be determined."))
    proof = dict(source_held_gap_audit=str(held_path.relative_to(ROOT)),held_gap_sha256=sha(held_path),
        current_claude_ref=CLAUDE_REF,held_minutes=len(held),held_dates=held.date.dt.strftime("%Y-%m-%d").unique().tolist(),
        rows=gap_rows,raw_versions=[x for x in detail["raw_versions"] if any(y in x["path"] for y in {d[:4] for d in date_values})],
        raw_files_match_latest_pinned_repository=all(x["exact_github_match"] for x in detail["raw_versions"]),
        cache_omission_detected=any(not x["raw_cache_observed_masks_match"] for x in gap_rows),
        no_imputation_no_exclusion_no_grid_rebuild=True,historical_account_or_baseline_returns_computed=False)
    dump(out/"held_gap_raw_proof.json",proof)
    blockers = []
    if len(held):
        blockers.append(dict(code="UNKNOWN_HELD_PATH",minutes=len(held),
            dates=proof["held_dates"],evidence="held_gap_raw_proof.json",
            criterion="Registered Stage3 requires zero unknown held-minute OHLC paths."))
    for x in detail["days"]:
        if x["classification"]!="flat_nondecision_gap_observed_only_VWAP_allowed":
            blockers.append(dict(code=x["classification"],date=x["date"],
                intervals=x["missing_intervals"],missing_decisions=x["missing_scheduled_decisions"],
                evidence="native_coverage_audit.json"))
    if detail["omitted_weekday_dates"]:
        blockers.append(dict(code="OMITTED_SOURCE_WEEKDAYS",dates=detail["omitted_weekday_dates"]))
    inputs = {str(Path(x).resolve().relative_to(ROOT)):sha(x) for x in [*audits,*orders,held_path]}
    for value in (args.ledger,args.gate):
        if value:
            path = Path(value).resolve()
            if not path.is_file():
                raise FileNotFoundError(path)
            inputs[str(path.relative_to(ROOT))] = sha(path)
    record = dict(candidate="V2",status="BLOCKED_DATA" if blockers else "AUDIT_CLEAR_NOT_AUTHORIZED",
        script_path=str(Path(__file__).resolve().relative_to(ROOT)),script_sha256=sha(__file__),
        preregistration_commit=args.prereg or "d9ef177df4f2a788dc4e9d108c4cdc1fbc4880ad",
        current_claude_ref=CLAUDE_REF,published_account_model_ref=CODEX_REF,
        account_or_baseline_returns_computed=False,baseline_built=False,account_simulations_run=False,
        blocks=blockers,inputs=inputs,fees_planned=list(FEES),
        finding="Account contribution is unknown because required source paths are incomplete; this does not establish no gain.",
        destinations=[dict(destination=name,status="BLOCKED_DATA" if blockers else "NOT_AUTHORIZED",
            baseline_built=False,comparisons_run=False,reason="Zero unknown held-path gate fails; no addition/replacement value is estimated.",
            frozen_configurations=list(allocations(plan,name)),baseline_specification=plan)
            for name,plan in [*funded_plans().items(),
                ("50K_evaluation",dict(VB=8,ONB30=("risk",1100),MON_BR=2,EOS=("risk",500))),
                ("150K_evaluation",dict(VB=20,ONB30=("risk",2750),MON_BR=5,EOS=("risk",1250)))]],
        policy="No prices imputed, no source date excluded, no rescue variant, no extra data feed, no baseline/account simulator invoked.")
    dump(out/"blocked_destinations.json",record)
    return dict(status=record["status"],held_minutes=len(held),held_dates=proof["held_dates"],
                source_calendar_classifications=detail["classification_counts"],destinations=4,
                account_or_baseline_returns_computed=False,
                outputs=[str((out/name).relative_to(ROOT)) for name in
                         ("native_coverage_audit.json","held_gap_raw_proof.json","blocked_destinations.json")])


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--scratch", default=str(ROOT / "scratch_data"))
    ap.add_argument("--runtime", default=str(RUNTIME))
    ap.add_argument("--out", default=str(OUT))
    ap.add_argument("--prepare", action="store_true")
    ap.add_argument("--fixtures-only", action="store_true")
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--prereg")
    ap.add_argument("--plan-path", default="agents/codex/plans/s03_noisearea.md")
    ap.add_argument("--gate")
    ap.add_argument("--ledger")
    ap.add_argument("--audit")
    ap.add_argument("--audit-calendar",action="store_true")
    ap.add_argument("--audit-only",action="store_true")
    ap.add_argument("--held-gaps")
    args = ap.parse_args()
    if args.audit_only and args.run:
        ap.error("--audit-only and --run are mutually exclusive")
    if args.prepare:
        print(json.dumps(prepare(args.scratch,args.runtime)),flush=True)
    if args.fixtures_only:
        result = synthetic_fixtures(args.runtime)
        if (Path(args.runtime)/"manifest.json").is_file():
            canonical = canonical_engine_fixtures(args.runtime,args.scratch)
            dump(Path(args.runtime)/"canonical_engine_synthetic.json",canonical)
            result["exact_canonical_account_engine_checks"] = canonical["exact_records"]
        dump(Path(args.runtime)/"synthetic_fixtures.json", result)
        print(json.dumps(result),flush=True)
    if args.run:
        require_gate(args.prereg,args.gate,args.ledger,args.audit,args.plan_path)
        run(args)
    if args.audit_only:
        print(json.dumps(audit_only(args),default=str),flush=True)
    if args.audit_calendar:
        if not args.audit:
            ap.error("--audit-calendar requires --audit")
        result = source_calendar_audit(args.audit,args.runtime)
        print(json.dumps({k:v for k,v in result.items() if k!="unknown_source_dates"},default=str),flush=True)
    if not any((args.prepare,args.fixtures_only,args.run,args.audit_calendar,args.audit_only)):
        ap.print_help()


if __name__ == "__main__":
    main()
