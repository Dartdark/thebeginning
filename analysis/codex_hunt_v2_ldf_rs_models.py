"""H07 saved-parent financial adapter. Import and fixtures read no actual data.

FEATURES PASS -> immutable H01 raw gross -> gross PASS -> immutable protected
H01 BASE masks. No old maker, grid execution, native/workbook decoder, account,
validation or alternative rule is called. The failed H01 filter stays closed.
"""
from __future__ import annotations

import argparse
import ast
from contextlib import contextmanager
import csv
from datetime import date, datetime, timezone
import fcntl
from functools import lru_cache
import hashlib
import io
import json
from math import comb
from pathlib import Path
import re
import subprocess
import sys
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis/outputs/codex_hunt_v2_ldf_rs_open_loss"
PARENT = ROOT / "analysis/outputs/codex_hunt_v2_ldf_delta"
SCRIPT = "analysis/codex_hunt_v2_ldf_rs_models.py"
FEATURE_SCRIPT = "analysis/codex_hunt_v2_ldf_rs_features.py"
SOURCE_SCRIPT = "analysis/codex_hunt_v2_ldf_rs_open_loss.py"
SOURCE_HELPER = "analysis/codex_hunt_v2_ldf_rs_metadata.py"
PLAN = "agents/codex/plans/hunt_v2_ldf_rs_open_loss.md"
EVIDENCE = "agents/codex/evidence/hunt_v2_ldf_rs_open_loss.md"
ADDENDUM = "agents/codex/research/hunt_v2_ldf_rs_predata_adjudication.md"
H01_GROSS = "analysis/codex_hunt_v2_ldf_delta.py"
H01_DESIGN = "analysis/codex_hunt_v2_ldf_delta_design.py"
PREREG = "4c3612104c10f5e5eeb96e53d8cde6bc2a3f2b3d"
SOURCE_PIN = "7a9832725f1011ad554bd4da0efa92ca06ef70b2"
MODELS = ("BASE", "RS_OPEN_LOSS", "SAME_SIDE_OPEN", "PRICE_0901")
YEARS = tuple(range(2018, 2023))
SEEDS, SAMPLES, MAX_DRAWS = {"A": 2026102707, "B": 2026102708}, 1000, 100000
SHA_RE = re.compile(r"[0-9a-f]{64}\Z")
DATE_RE = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}\Z")
FEATURE_REQUIRED = ("features.csv", "features_gate.json", "features_input_binding.json",
                    "features_null_support_A.json", "features_null_support_B.json")
RAW_PHASE = "H07_RAW_GROSS_saved_parent"
DESIGN_PHASE = "H07_STOPPED_DESIGN_saved_parent"
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT / "analysis"))
import numpy as np
import pandas as pd
import metrics as M
import resampling as R


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""): digest.update(block)
    return digest.hexdigest()


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT)


def now():
    return datetime.now(timezone.utc).isoformat()


def safe(value):
    if isinstance(value, dict): return {str(k): safe(v) for k, v in value.items()}
    if isinstance(value, (tuple, list)): return [safe(v) for v in value]
    if isinstance(value, np.generic): return safe(value.item())
    if isinstance(value, float) and not np.isfinite(value): return None
    return value


def dump(name, value):
    with (OUT / name).open("x") as handle:
        json.dump(safe(value), handle, indent=2, allow_nan=False); handle.write("\n")


def csv_once(name, frame, index=False):
    with (OUT / name).open("x", newline="") as handle:
        frame.to_csv(handle, index=index, float_format="%.12g")


def relative_path(name):
    if not isinstance(name, str) or not name or "\\" in name:
        raise ValueError("Invalid bound relative path.")
    path = Path(name)
    if path.is_absolute() or ".." in path.parts or str(path) != name:
        raise ValueError("Bound path must stay in the repository:" + name)
    return ROOT / path


def digest_value(value):
    if not isinstance(value, str) or SHA_RE.fullmatch(value) is None:
        raise ValueError("Explicit lowercase SHA256 required.")
    return value


def committed_file(name, ref="HEAD"):
    current = sha(relative_path(name))
    if hashlib.sha256(git("show", ref + ":" + name)).hexdigest() != current:
        raise ValueError("Commit exact input/source before this phase:" + name)
    return current


def attach_hashes(binding, hashes):
    if not isinstance(hashes, dict): raise ValueError("Missing input hash map.")
    for name, expected in hashes.items():
        digest_value(expected)
        if sha(relative_path(name)) != expected: raise ValueError("Frozen input changed:" + name)
        prior = binding["hashes"].get(name)
        if prior is not None and prior != expected: raise ValueError("Conflicting binding:" + name)
        binding["hashes"][name] = expected


def marker_proof(binding, directory, filename, expected_sha, phase, required, require_pass=True):
    digest_value(expected_sha)
    path = directory / filename
    rel = str(path.relative_to(ROOT))
    if sha(path) != expected_sha or committed_file(rel) != expected_sha:
        raise ValueError("Exact committed marker SHA required:" + rel)
    marker = json.loads(path.read_text())
    if marker.get("phase") != phase or (require_pass and marker.get("passed") is not True):
        raise ValueError("Wrong/failed stage marker:" + rel)
    artifacts = marker.get("artifacts_sha256")
    if not isinstance(artifacts, dict) or not set(required).issubset(artifacts):
        raise ValueError("Required stage artifacts are not hash-bound:" + rel)
    binding["hashes"][rel] = expected_sha
    for name, expected in artifacts.items():
        if not isinstance(name, str) or Path(name).name != name or "/" in name or "\\" in name or name in (".", ".."):
            raise ValueError("Stage artifact must be a safe basename.")
        attach_hashes(binding, {str((directory / name).relative_to(ROOT)): expected})
    return marker


def recheck(binding):
    attach_hashes(binding, dict(binding["hashes"]))


def verify_features(prereg, features_sha):
    if prereg != PREREG or git("rev-parse", "--verify", prereg + "^{commit}").decode().strip() != PREREG:
        raise ValueError("Use immutable original H07 preregistration.")
    if git("branch", "--show-current").decode().strip() != "codex/work": raise ValueError("Stay on codex/work.")
    subprocess.check_call(["git", "merge-base", "--is-ancestor", PREREG, "HEAD"], cwd=ROOT)
    bound = dict(prereg=PREREG, implementation_commit=git("rev-parse", "HEAD").decode().strip(),
        hashes={}, features_marker_sha256=features_sha, models=list(MODELS),
        versions=dict(python=sys.version.split()[0], numpy=np.__version__, pandas=pd.__version__),
        source_pin=SOURCE_PIN, no_parent_maker_or_engine_called=True, future_data_authorized=False)
    for name in (PLAN, EVIDENCE, H01_GROSS, H01_DESIGN):
        if git("show", PREREG + ":" + name) != relative_path(name).read_bytes():
            raise ValueError("Original frozen parent/protocol changed:" + name)
    for name in (SOURCE_SCRIPT, SOURCE_HELPER, ADDENDUM):
        if git("show", SOURCE_PIN + ":" + name) != relative_path(name).read_bytes():
            raise ValueError("Original SOURCE producer/addendum changed:" + name)
    for name in (SCRIPT, FEATURE_SCRIPT, SOURCE_SCRIPT, SOURCE_HELPER, PLAN, EVIDENCE, ADDENDUM,
                 H01_GROSS, H01_DESIGN, "analysis/metrics.py", "analysis/resampling.py"):
        bound["hashes"][name] = committed_file(name)
    marker = marker_proof(bound, OUT, "features_verified_execution.json", features_sha,
        "FEATURES_SUPPORT_only", FEATURE_REQUIRED)
    if marker.get("prereg") != PREREG or marker.get("raw_or_stopped_returns_calculated") is not False:
        raise ValueError("Feature proof has wrong prereg/outcome boundary.")
    if marker.get("script_sha256") != bound["hashes"][FEATURE_SCRIPT]: raise ValueError("Feature implementation differs.")
    inputs = json.loads((OUT / "features_input_binding.json").read_text())
    attach_hashes(bound, inputs["hashes"])
    source_sha = digest_value(marker.get("source_marker_sha256"))
    if inputs.get("source_marker_sha256") != source_sha: raise ValueError("SOURCE proof chain differs.")
    source = marker_proof(bound, OUT, "source_verified_execution.json", source_sha, "SOURCE_only",
        ("source_attempt.json", "source_parent_dates_only.json", "source_gate.json", "source_input_binding.json"))
    if source.get("prereg") != PREREG: raise ValueError("SOURCE prereg differs.")
    for name, expected in source.get("code_sha256", {}).items():
        if hashlib.sha256(git("show", SOURCE_PIN + ":" + name)).hexdigest() != expected:
            raise ValueError("SOURCE code is not bound to its immutable revision:" + name)
    for filename, phase, required in (
        ("gross_verified_execution.json", "gross", ("gross_events.csv",)),
        ("design_verified_execution.json", "design", ("design_BASE_trades.csv", "design_daily.csv"))):
        rel = str((PARENT / filename).relative_to(ROOT))
        if rel not in bound["hashes"]: raise ValueError("Missing original H01 marker binding.")
        old = marker_proof(bound, PARENT, filename, bound["hashes"][rel], phase, required, require_pass=False)
        maker = H01_GROSS if phase == "gross" else H01_DESIGN
        if old.get("script_sha256") != bound["hashes"][maker]: raise ValueError("Original H01 maker identity changed.")
    gate = json.loads((OUT / "features_gate.json").read_text())
    if not (gate.get("phase") == "FEATURES_SUPPORT_only" and gate.get("passed") is True):
        raise ValueError("Actual FEATURES support PASS required before raw outcomes.")
    return bound, gate


def parse_day(raw):
    if not isinstance(raw, str) or DATE_RE.fullmatch(raw) is None: raise ValueError("Exact ISO design date required.")
    day = date.fromisoformat(raw)
    if day.year not in YEARS: raise ValueError("No future/warmup financial conversion authorized.")
    return pd.Timestamp(day)


def integer(raw):
    if not isinstance(raw, str) or re.fullmatch(r"-?[0-9]+", raw) is None: raise ValueError("Exact integer field required.")
    return int(raw)


def flag(raw):
    if raw not in ("0", "1"): raise ValueError("Frozen mask must be literal0/1.")
    return raw == "1"


def number(raw):
    value = float(raw)
    if not np.isfinite(value): raise ValueError("Nonfinite financial value.")
    return value


def read_features(handle):
    fields = ("event_id", "date", "year", "side", *("keep_" + m for m in MODELS),
              "source_known", "same_side_open", "price_sign", "stratum_A", "stratum_B")
    reader = csv.DictReader(handle)
    if not reader.fieldnames or not set(fields).issubset(reader.fieldnames): raise ValueError("Feature contract missing required columns.")
    rows = []
    for raw in reader:
        day = parse_day(raw["date"])
        row = dict(event_id=integer(raw["event_id"]), date=day, year=integer(raw["year"]), side=integer(raw["side"]))
        if row["year"] != day.year or row["side"] not in (-1, 1): raise ValueError("Feature date/year/side identity differs.")
        row.update({"keep_" + m: flag(raw["keep_" + m]) for m in MODELS})
        row["source_known"] = flag(raw["source_known"])
        row["same_side_open"] = None if raw["same_side_open"] == "" else flag(raw["same_side_open"])
        row["price_sign"] = raw["price_sign"]
        if row["price_sign"] not in ("NEGATIVE", "ZERO", "POSITIVE", "UNKNOWN"): raise ValueError("Unregistered price-sign category.")
        known, same, adverse = row["source_known"], row["same_side_open"], row["price_sign"] == "NEGATIVE"
        if (known and same is None) or (not known and same is not None): raise ValueError("Ambiguous known/open feature contract.")
        if not row["keep_BASE"] or row["keep_RS_OPEN_LOSS"] != (not (known and same and adverse)):
            raise ValueError("Primary mask no longer equals frozen interaction.")
        if row["keep_SAME_SIDE_OPEN"] != (not (known and same)) or row["keep_PRICE_0901"] != (not adverse):
            raise ValueError("Unselectable reference changed.")
        a = [row["year"], row["side"], row["price_sign"]]
        b = [row["year"], row["side"], known, same]
        for scheme, key in (("A", a), ("B", b)):
            if json.loads(raw["stratum_" + scheme]) != key: raise ValueError("Feature null stratum changed.")
            row["stratum_" + scheme] = json.dumps(key, separators=(",", ":"))
        rows.append(row)
    frame = pd.DataFrame(rows)
    if frame.empty or not np.array_equal(frame.event_id.to_numpy(), np.arange(len(frame))): raise ValueError("Original zero-based parent IDs/order required.")
    if frame.date.duplicated().any() or not frame.date.is_monotonic_increasing or set(frame.year) != set(YEARS):
        raise ValueError("Unique chronological five-year feature universe required.")
    return frame


def null_support(features, scheme):
    cells, count, variable = [], 1, 0
    for key, group in features.groupby("stratum_" + scheme, sort=True):
        pool = group[group.source_known]
        n, k = len(pool), int(pool.keep_RS_OPEN_LOSS.sum())
        choices = comb(n, k); count *= choices; variable += int(0 < k < n)
        cells.append(dict(stratum=json.loads(key), randomizable_n=n, randomizable_kept_k=k, exact_choices=str(choices),
            randomizable_event_ids=pool.event_id.tolist(), fixed_unknown_kept_event_ids=group.loc[~group.source_known, "event_id"].tolist()))
    return dict(scheme=scheme, exact_distinct_mask_count=str(count), variable_cells=variable,
                passed=count >= SAMPLES and variable > 0, cells=cells)


def verify_support(features, gate, reports):
    primary = features[features.keep_RS_OPEN_LOSS]; removed = features[~features.keep_RS_OPEN_LOSS]
    facts = dict(parent_events=len(features), known_state_events=int(features.source_known.sum()),
        primary_kept=len(primary), primary_removed=len(removed), primary_removed_years=sorted(removed.year.unique().tolist()),
        primary_kept_by_side={str(s): int((primary.side == s).sum()) for s in (-1, 1)})
    for name, value in facts.items():
        if gate.get(name) != value: raise ValueError("Feature support artifact/count mismatch:" + name)
    passed = (facts["known_state_events"] / len(features) >= .90 and len(primary) >= 100 and len(removed) >= 20
        and removed.year.nunique() >= 3 and min(facts["primary_kept_by_side"].values()) >= 10
        and gate.get("required_native_mark_reference_complete") is True)
    for scheme in ("A", "B"):
        actual = null_support(features, scheme); report = reports[scheme]
        if not actual["passed"] or report.get("passed") is not True:
            raise ValueError("Frozen pre-outcome matched-null support failed:" + scheme)
        for name in ("exact_distinct_mask_count", "variable_cells"):
            if report.get(name) != actual[name]: raise ValueError("Matched-null count proof changed:" + scheme)
    if not passed: raise ValueError("Frozen no-return support failed before outcomes.")


def read_raw(handle, features):
    reader = csv.DictReader(handle)
    need = {"date", "year", "side", "decision_j", "entry_label_j", "exit_label_j", "atr", "entry_open", "exit_close", "gross_points", "gross_mnq", "unresolved_held_path", "invalid_or_missing_held_minutes"}
    if not reader.fieldnames or not need.issubset(reader.fieldnames): raise ValueError("Original H01 raw schema differs.")
    rows = []
    for event_id, raw in enumerate(reader):
        day = parse_day(raw["date"])
        y, s = integer(raw["year"]), integer(raw["side"])
        if event_id >= len(features): raise ValueError("Extra raw parent event.")
        f = features.iloc[event_id]
        if (day, y, s) != (f.date, f.year, f.side): raise ValueError("Raw parent ID/date/year/side differs before values.")
        if (integer(raw["decision_j"]), integer(raw["entry_label_j"]), integer(raw["exit_label_j"])) != (840, 841, 870):
            raise ValueError("Frozen raw clock changed.")
        if raw["unresolved_held_path"].lower() != "false" or integer(raw["invalid_or_missing_held_minutes"]) != 0:
            raise ValueError("Unresolved original held path.")
        entry, exit_, atr = (number(raw[name]) for name in ("entry_open", "exit_close", "atr"))
        points, gross = number(raw["gross_points"]), number(raw["gross_mnq"])
        if min(entry, exit_, atr) <= 0: raise ValueError("Invalid positive raw reference.")
        np.testing.assert_allclose([points, gross], [(exit_ - entry) * s, points * 2], rtol=0, atol=1e-7)
        rows.append(dict(event_id=event_id, date=day, year=y, side=s, entry_open=entry, atr=atr, gross_mnq=gross))
    result = pd.DataFrame(rows)
    if len(result) != len(features): raise ValueError("Missing raw parent event.")
    return result


def read_stopped(handle, features, raw_reference):
    reader = csv.DictReader(handle)
    metadata = ("event_id", "date", "year", "side", "entry_j", "exit_j", "kind", "invalid_held_minutes")
    financial = ("entry", "exit", "atr", "stop_points", "gross_points", "gross_mnq", "commission_mnq", "slippage_mnq",
                 "cost_mnq", "net_mnq", "cost_mnq_4tick", "net_mnq_4tick", "fill_count")
    if not reader.fieldnames or not set(metadata + financial).issubset(reader.fieldnames): raise ValueError("Immutable protected BASE schema differs.")
    strings = list(reader)
    # Every key/date passes before any stopped financial field conversion.
    for i, raw in enumerate(strings):
        day = parse_day(raw["date"])
        if i >= len(features) or (integer(raw["event_id"]), day, integer(raw["year"]), integer(raw["side"])) != (i, features.iloc[i].date, features.iloc[i].year, features.iloc[i].side):
            raise ValueError("Protected parent ledger IDs/dates/sides changed.")
    if len(strings) != len(features): raise ValueError("Protected ledger count differs.")
    rows = []
    for i, raw in enumerate(strings):
        values = {field: number(raw[field]) for field in financial}
        side = int(features.iloc[i].side); ej, xj, kind = (integer(raw[k]) for k in ("entry_j", "exit_j", "kind"))
        if ej != 841 or not ej <= xj <= 870 or kind not in (0, 2) or integer(raw["invalid_held_minutes"]) != 0:
            raise ValueError("Frozen active-protection/held/exit identity differs.")
        if kind == 2 and xj != 870: raise ValueError("Time exit not at fixed14:30.")
        if min(values["entry"], values["exit"], values["atr"], values["stop_points"]) <= 0: raise ValueError("Invalid protected reference.")
        expected_stop = np.ceil((.25 * values["atr"]) / .25) * .25
        np.testing.assert_allclose([values["entry"], values["atr"], values["stop_points"]], [raw_reference.iloc[i].entry_open, raw_reference.iloc[i].atr, expected_stop], rtol=0, atol=1e-7)
        points = (values["exit"] - values["entry"]) * side
        expected = [points, points * 2, 1.24, 1., 2.24, points * 2 - 2.24, 5.24, points * 2 - 5.24, 2.]
        names = ("gross_points", "gross_mnq", "commission_mnq", "slippage_mnq", "cost_mnq", "net_mnq", "cost_mnq_4tick", "net_mnq_4tick", "fill_count")
        np.testing.assert_allclose([values[name] for name in names], expected, rtol=0, atol=1e-7)
        rows.append(dict(event_id=i, date=features.iloc[i].date, year=int(features.iloc[i].year), side=side,
            entry_j=ej, exit_j=xj, kind=kind, **values))
    return pd.DataFrame(rows)


def read_axis(handle):
    reader = csv.DictReader(handle)
    if not reader.fieldnames or "date" not in reader.fieldnames: raise ValueError("Parent daily-date schema differs.")
    axis = pd.DatetimeIndex([parse_day(row["date"]) for row in reader])
    if axis.empty or axis.has_duplicates or not axis.is_monotonic_increasing or set(axis.year) != set(YEARS):
        raise ValueError("Original five-year cash-day axis required.")
    return axis


@lru_cache(maxsize=1)
def legacy_helpers():
    """Execute only four pinned pure functions; never import a maker/cache/engine."""
    env = dict(np=np, pd=pd, M=M, R=R)
    for script, names in ((H01_GROSS, ("tstat",)), (H01_DESIGN, ("nw_t", "daily_values", "performance"))):
        tree = ast.parse((ROOT / script).read_text())
        nodes = [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name in names]
        if {node.name for node in nodes} != set(names): raise ValueError("Pinned pure metric helper missing.")
        exec(compile(ast.Module(body=nodes, type_ignores=[]), script, "exec"), env)
        if script == H01_GROSS: env["G"] = SimpleNamespace(tstat=env["tstat"])
    return env


def summary_groups(base, features, field):
    rows = []; tstat = legacy_helpers()["tstat"]
    for model in MODELS:
        mask = features["keep_" + model].to_numpy(bool)
        for group, selected in (("base", base), ("kept", base[mask]), ("removed", base[~mask])):
            for period in ("2018-22", *map(str, YEARS)):
                part = selected if period == "2018-22" else selected[selected.year == int(period)]
                for side, value in (("both", None), ("long", 1), ("short", -1)):
                    q = part if value is None else part[part.side == value]
                    x = q[field].to_numpy(float); sd = x.std(ddof=1) if len(x) > 1 else np.nan
                    rows.append(dict(model=model, group=group, period=period, side=side, field=field, events=len(x),
                        total=float(x.sum()), mean=float(x.mean()) if len(x) else None, SD=sd,
                        SE=sd / np.sqrt(len(x)) if len(x) else None, t=tstat(x)))
    return pd.DataFrame(rows)


def all_metrics(tickets, axis):
    h = legacy_helpers(); rows = []
    for model, trades in tickets.items():
        for period in ("2018-22", *map(str, YEARS)):
            days = axis if period == "2018-22" else axis[axis.year == int(period)]
            part = trades if period == "2018-22" else trades[trades.year == int(period)]
            for side, s in (("all", None), ("long", 1), ("short", -1)):
                q = part if s is None else part[part.side == s]
                for basis, field, cost in (("MNQ", "net_mnq", "cost_mnq"), ("MNQ_4tick", "net_mnq_4tick", "cost_mnq_4tick")):
                    daily = h["daily_values"](q, field, days)
                    rows.append(dict(model=model, period=period, side=side, basis=basis,
                        gross=float(q.gross_mnq.sum()), cost=float(q[cost].sum()), **h["performance"](daily, q[field].to_numpy(float))))
    return pd.DataFrame(rows)


def unique_masks(features, scheme, samples=SAMPLES, max_draws=MAX_DRAWS):
    report = null_support(features, scheme)
    if int(report["exact_distinct_mask_count"]) < samples or report["variable_cells"] < 1:
        raise ValueError("Insufficient distinct matched-null support before draws.")
    rng = np.random.default_rng(SEEDS[scheme]); fixed = ~features.source_known.to_numpy(bool)
    pools = [(np.asarray(cell["randomizable_event_ids"], int), cell["randomizable_kept_k"]) for cell in report["cells"]]
    masks, seen, attempts = [], set(), 0
    while len(masks) < samples and attempts < max_draws:
        mask = fixed.copy(); attempts += 1
        for ids, keep in pools:
            if keep: mask[rng.choice(ids, size=keep, replace=False)] = True
        signature = np.packbits(mask).tobytes()
        if signature in seen: continue
        seen.add(signature); masks.append(mask)
    if len(masks) != samples: raise ValueError("Unable to obtain1000unique frozen masks; no seed/stratum retry.")
    return np.asarray(masks, dtype=bool), dict(report, seed=SEEDS[scheme], draws=attempts, distinct_masks=len(masks))


def null_statistics(base, features, axis, masks, scheme):
    day_index = axis.get_indexer(base.date)
    if (day_index < 0).any() or len(np.unique(day_index)) != len(base): raise ValueError("Exact one-ticket/day mapping required.")
    values = base.net_mnq.to_numpy(float); paths = np.zeros((len(masks), len(axis)))
    paths[:, day_index] = masks * values[None, :]
    primary = features.keep_RS_OPEN_LOSS.to_numpy(bool)
    actual = np.zeros(len(axis)); actual[day_index] = values * primary
    totals = paths.sum(1); dds = np.array([R.max_dd(path) for path in paths])
    total, dd = float(actual.sum()), R.max_dd(actual)
    profit_fail, dd_fail = totals >= total, dds <= dd
    failures = profit_fail | dd_fail
    diagnostics = dict(scheme=scheme, samples=len(masks), actual_total=total, actual_maxDD=dd,
        joint_failure_count=int(failures.sum()), joint_p=(1 + int(failures.sum())) / (len(masks) + 1),
        profit_p=(1 + int(profit_fail.sum())) / (len(masks) + 1), DD_p=(1 + int(dd_fail.sum())) / (len(masks) + 1),
        strict_joint_wins=int((~failures).sum()), passed=int(failures.sum()) <= 49,
        definition="failure=nullprofit>=actual OR nullDD<=actual;tiesfail", diagnostic_paths_not_executable_portfolios=True)
    table = pd.DataFrame(dict(scheme=scheme, run=np.arange(len(masks)), total_net=totals, maxDD=dds,
        profit_at_least_actual=profit_fail, DD_at_most_actual=dd_fail, joint_failure=failures))
    ids = base.event_id.to_numpy(np.int32)
    selected_ids = np.vstack([ids[mask] for mask in masks])
    return diagnostics, table, {scheme + "_masks": masks, scheme + "_selected_event_ids": selected_ids, scheme + "_daily_paths": paths}


def design_gate(tickets, metrics, nulls):
    primary = tickets["RS_OPEN_LOSS"]
    p = metrics[(metrics.model == "RS_OPEN_LOSS") & (metrics.period == "2018-22") & (metrics.side == "all") & (metrics.basis == "MNQ")].iloc[0]
    years = primary.groupby("year").net_mnq.sum().reindex(YEARS, fill_value=0)
    total = float(primary.net_mnq.sum()); base = float(tickets["BASE"].net_mnq.sum())
    removed = tickets["BASE"][~tickets["BASE"].event_id.isin(primary.event_id)]
    gates = dict(at_least100=len(primary) >= 100, positive_net=total > 0,
        trade_t_at_least2=pd.notna(p.t_trade) and p.t_trade >= 2,
        dailyNW5_at_least1_5=pd.notna(p.t_nw5) and p.t_nw5 >= 1.5,
        PF_at_least1_2=p.profit_factor >= 1.2, positive4of5years=int((years > 0).sum()) >= 4,
        positive_excluding_every_year=bool(((total - years) > 0).all()),
        positive4tick=float(primary.net_mnq_4tick.sum()) > 0,
        kept_total_strictly_gt_BASE=total > base,
        removed_total_negative=float(removed.net_mnq.sum()) < 0,
        removed_mean_negative=len(removed) > 0 and float(removed.net_mnq.mean()) < 0,
        primary_strictly_gt_overlap=total > float(tickets["SAME_SIDE_OPEN"].net_mnq.sum()),
        primary_strictly_gt_price=total > float(tickets["PRICE_0901"].net_mnq.sum()),
        matched_A_pass=nulls["A"]["passed"] is True, matched_B_pass=nulls["B"]["passed"] is True)
    passed = bool(all(gates.values()))
    return dict(phase=DESIGN_PHASE, passed=passed, primary="RS_OPEN_LOSS", gates=gates,
        primary_metrics=p.to_dict(), year_net=years.to_dict(), configurations_evaluated=list(MODELS),
        counted_evaluations=4, repeated_parent_and_controls_counted=True,
        original_H01_filter_stays_closed=True, parent_execution_replays=0,
        next_stage="immediate_current_personal19_design_bench" if passed else "close_H07",
        validation_or_bench_run=False, selection_frozen_for2023=False)


def ensure_no_attempt(phase):
    for directory in (ROOT / "analysis/outputs").glob("codex_hunt_v2_ldf_rs_open_loss*"):
        if any((directory / (phase + suffix)).exists() for suffix in ("_attempt.json", "_verified_execution.json")):
            raise ValueError("Retained financial attempt exists; no automatic/alternate-directory retry.")


@contextmanager
def lock():
    OUT.mkdir(parents=True, exist_ok=True)
    with (OUT / "financial.lock").open("a") as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB); yield


def feature_inputs(prereg, features_sha):
    bound, gate = verify_features(prereg, features_sha)
    with (OUT / "features.csv").open(newline="") as handle: features = read_features(handle)
    reports = {s: json.loads((OUT / ("features_null_support_" + s + ".json")).read_text()) for s in ("A", "B")}
    verify_support(features, gate, reports)
    return bound, features


def gross(prereg, features_sha):
    with lock():
        bound, features = feature_inputs(prereg, features_sha); ensure_no_attempt("gross")
        dump("gross_attempt.json", dict(started_utc=now(), **bound))
        dump("gross_pre_outcome_binding.json", bound)
        with (PARENT / "gross_events.csv").open(newline="") as handle: base = read_raw(handle, features)
        summary = summary_groups(base, features, "gross_mnq")
        primary = base[features.keep_RS_OPEN_LOSS.to_numpy(bool)].gross_mnq
        gate = dict(phase=RAW_PHASE, passed=bool(len(primary) >= 100 and primary.mean() >= 4.48),
            primary="RS_OPEN_LOSS", primary_kept=len(primary), primary_gross_mean=float(primary.mean()),
            primary_gross_t=legacy_helpers()["tstat"](primary), native_RT_cost=2.24, gross_hurdle=4.48,
            gross_screens=1, counted_evaluations=0, costs_subtracted=False, stopped_returns_read=False,
            models=list(MODELS), original_H01_filter_stays_closed=True, no_parent_execution=True)
        csv_once("gross_parent_events.csv", base); csv_once("gross_summary.csv", summary)
        dump("gross_input_binding.json", bound); dump("gross_gate.json", gate)
        recheck(bound)
        names = ("gross_attempt.json", "gross_pre_outcome_binding.json", "gross_parent_events.csv", "gross_summary.csv", "gross_input_binding.json", "gross_gate.json")
        marker = dict(**gate, prereg=PREREG, implementation_commit=bound["implementation_commit"], script_sha256=sha(ROOT / SCRIPT),
            features_marker_sha256=features_sha, artifacts_sha256={n: sha(OUT / n) for n in names}, completed_utc=now())
        dump("gross_verified_execution.json", marker)
        return gate


def require_gross(bound, gross_sha, features_sha):
    marker = marker_proof(bound, OUT, "gross_verified_execution.json", gross_sha, RAW_PHASE,
        ("gross_parent_events.csv", "gross_summary.csv", "gross_input_binding.json", "gross_gate.json"))
    if marker.get("prereg") != PREREG or marker.get("features_marker_sha256") != features_sha or marker.get("script_sha256") != sha(ROOT / SCRIPT):
        raise ValueError("Exact same-code/same-features gross PASS required before stopped fields.")
    gate = json.loads((OUT / "gross_gate.json").read_text())
    if gate.get("passed") is not True or gate.get("phase") != RAW_PHASE or gate.get("models") != list(MODELS):
        raise ValueError("Gross gate does not authorize frozen four definitions.")
    prior = json.loads((OUT / "gross_input_binding.json").read_text())
    attach_hashes(bound, prior["hashes"])
    bound["gross_marker_sha256"] = gross_sha


def design(prereg, features_sha, gross_sha):
    with lock():
        bound, features = feature_inputs(prereg, features_sha)
        require_gross(bound, gross_sha, features_sha); ensure_no_attempt("design")
        dump("design_attempt.json", dict(started_utc=now(), **bound)); dump("design_pre_outcome_binding.json", bound)
        with (PARENT / "gross_events.csv").open(newline="") as handle: raw = read_raw(handle, features)
        with (PARENT / "design_BASE_trades.csv").open(newline="") as handle: base = read_stopped(handle, features, raw)
        with (PARENT / "design_daily.csv").open(newline="") as handle: axis = read_axis(handle)
        if not base.date.isin(axis).all(): raise ValueError("Stopped events outside immutable daily axis.")
        tickets = {m: base[features["keep_" + m].to_numpy(bool)].copy() for m in MODELS}
        metrics = all_metrics(tickets, axis); diagnostics, arrays, names = {}, {}, []
        for scheme in ("A", "B"):
            masks, sampling = unique_masks(features, scheme)
            diagnostic, table, values = null_statistics(base, features, axis, masks, scheme)
            diagnostics[scheme] = dict(diagnostic, sampling=sampling); arrays.update(values)
            name = "design_null_" + scheme + ".csv"; csv_once(name, table); names.append(name)
        arrays.update(event_ids=base.event_id.to_numpy(np.int32), dates=axis.strftime("%Y-%m-%d").to_numpy(dtype="U10"))
        with (OUT / "design_null_paths.npz").open("xb") as handle: np.savez_compressed(handle, **arrays)
        names.append("design_null_paths.npz")
        gate = design_gate(tickets, metrics, diagnostics)
        for model, trades in tickets.items():
            name = "design_" + model + "_trades.csv"; csv_once(name, trades); names.append(name)
        for suffix, field in (("", "net_mnq"), ("_4tick", "net_mnq_4tick")):
            daily = pd.DataFrame({m: legacy_helpers()["daily_values"](t, field, axis) for m, t in tickets.items()})
            name = "design_daily" + suffix + ".csv"; csv_once(name, daily.rename_axis("date"), index=True); names.append(name)
        csv_once("design_metrics.csv", metrics); csv_once("design_base_kept_removed.csv", summary_groups(base, features, "net_mnq"))
        dump("design_null_diagnostics.json", diagnostics); dump("design_input_binding.json", bound); dump("design_gate.json", gate)
        names += ["design_metrics.csv", "design_base_kept_removed.csv", "design_null_diagnostics.json", "design_input_binding.json", "design_gate.json", "design_attempt.json", "design_pre_outcome_binding.json"]
        recheck(bound)
        marker = dict(**gate, prereg=PREREG, implementation_commit=bound["implementation_commit"], script_sha256=sha(ROOT / SCRIPT),
            features_marker_sha256=features_sha, gross_marker_sha256=gross_sha,
            artifacts_sha256={name: sha(OUT / name) for name in names}, completed_utc=now())
        dump("design_verified_execution.json", marker)
        return gate


def fixtures():
    checks = []
    assert R.max_dd([-10., 0., 5., 0.]) == 10.
    perf = legacy_helpers()["performance"](pd.Series([-10., 0., 5., 0.]), np.array([-10., 5.]))
    assert perf["max_dd"] == 10. and perf["sessions"] == 4 and perf["total"] == -5.
    checks.append("sharedH01puremetrics_initialzeroDD_dailyzeros_noengineimport")
    for bad in ("True", "False", "", "2"):
        try: flag(bad)
        except ValueError: pass
        else: raise AssertionError("Ambiguous mask admitted")
    assert flag("0") is False and flag("1") is True
    checks.append("literal0_1_masks")
    # One variable cell plus a fixed unknown row; values are invented.
    rows = []
    for i in range(14):
        known = i < 13
        rows.append(dict(event_id=i, date=pd.Timestamp("2020-01-02") + pd.Timedelta(days=i), year=2020, side=1,
            source_known=known, keep_RS_OPEN_LOSS=(i < 6 or not known),
            stratum_A='[2020,1,"NEGATIVE"]', stratum_B='[2020,1,true,true]'))
    artificial = pd.DataFrame(rows)
    assert int(null_support(artificial.iloc[:12], "A")["exact_distinct_mask_count"]) == 924
    assert int(null_support(artificial, "A")["exact_distinct_mask_count"]) == 1716
    masks, sampling = unique_masks(artificial, "A")
    assert masks.shape == (1000, 14) and masks[:, 13].all() and np.all(masks.sum(1) == 7)
    assert len({np.packbits(mask).tobytes() for mask in masks}) == 1000
    checks.append("exactcomb_924fails1716supports1000_unique_masks_unknownfixed")
    base = pd.DataFrame(dict(event_id=range(14), date=artificial.date, net_mnq=np.arange(14) - 6.))
    d, table, arrays = null_statistics(base, artificial, pd.DatetimeIndex(artificial.date), masks, "A")
    np.testing.assert_allclose(arrays["A_daily_paths"].sum(1), table.total_net)
    actual = base.net_mnq.to_numpy() * artificial.keep_RS_OPEN_LOSS.to_numpy()
    failures = (table.total_net.to_numpy() >= actual.sum()) | (table.maxDD.to_numpy() <= R.max_dd(actual))
    assert d["joint_failure_count"] == int(failures.sum()) and d["joint_p"] == (1 + failures.sum()) / 1001
    assert (1 + 49) / 1001 <= .05 and (1 + 50) / 1001 > .05
    checks.append("matched_paths_reconcile_OR_failure_ties_49versus50")
    try: parse_day("2023-01-02")
    except ValueError: pass
    else: raise AssertionError("Future financial date admitted")
    poison = io.StringIO("date,year,side,decision_j,entry_label_j,exit_label_j,atr,entry_open,exit_close,gross_points,gross_mnq,unresolved_held_path,invalid_or_missing_held_minutes\n2023-01-02,2023,1,840,841,870,POISON,POISON,POISON,POISON,POISON,False,0\n")
    try: read_raw(poison, pd.DataFrame())
    except ValueError as error: assert "future/warmup" in str(error)
    else: raise AssertionError("Future poison converted")
    checks.append("date_before_financial_poison")
    # Exact protected-ledger bridge, never raw no-stop gross as stopped gross.
    fs = pd.DataFrame(dict(event_id=[0, 1], date=pd.to_datetime(["2020-01-02", "2020-01-03"]), year=[2020, 2020], side=[1, -1]))
    rr = pd.DataFrame(dict(entry_open=[100., 100.], atr=[100., 100.]))
    records = []
    for i, (side, exit_, points) in enumerate(((1, 110., 10.), (-1, 110., -10.))):
        records.append(dict(event_id=i, date=fs.iloc[i].date.date().isoformat(), year=2020, side=side, entry_j=841, exit_j=870, kind=2, invalid_held_minutes=0,
            entry=100., exit=exit_, atr=100., stop_points=25., gross_points=points, gross_mnq=points * 2, commission_mnq=1.24, slippage_mnq=1., cost_mnq=2.24,
            net_mnq=points * 2 - 2.24, cost_mnq_4tick=5.24, net_mnq_4tick=points * 2 - 5.24, fill_count=2))
    buffer = io.StringIO(); pd.DataFrame(records).to_csv(buffer, index=False); buffer.seek(0)
    protected = read_stopped(buffer, fs, rr)
    np.testing.assert_allclose(protected.net_mnq, [17.76, -22.24]); np.testing.assert_allclose(protected.net_mnq_4tick, [14.76, -25.24])
    records[0]["commission_mnq"] += .01
    buffer = io.StringIO(); pd.DataFrame(records).to_csv(buffer, index=False); buffer.seek(0)
    try: read_stopped(buffer, fs, rr)
    except AssertionError: pass
    else: raise AssertionError("Corrupt saved cost accepted")
    checks.append("native_saved_stopped_cost_bridge_corruption_rejection")
    return dict(passed=True, checks=checks, script_sha256=sha(ROOT / SCRIPT),
        actual_features_raw_stopped_native_workbook_or_marker_values_read=False, actual_financial_phases_run=False)


def main():
    parser = argparse.ArgumentParser(); parser.add_argument("--phase", required=True, choices=("fixtures", "gross", "design"))
    parser.add_argument("--prereg", default=PREREG); parser.add_argument("--features-sha"); parser.add_argument("--gross-sha")
    args = parser.parse_args()
    if args.phase == "fixtures": result = fixtures()
    else:
        if not args.features_sha: parser.error("Financial stage requires exact committed FEATURES PASS SHA.")
        if args.phase == "gross": result = gross(args.prereg, args.features_sha)
        else:
            if not args.gross_sha: parser.error("Stopped design additionally requires exact committed gross PASS SHA.")
            result = design(args.prereg, args.features_sha, args.gross_sha)
    print(json.dumps(safe(result), allow_nan=False))


if __name__ == "__main__": main()
