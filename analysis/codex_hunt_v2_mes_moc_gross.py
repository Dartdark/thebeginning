"""H09 raw MES closing-flow screen, gated on committed SOURCE/support PASS.

Import and --fixtures read no owned source, marker, schedule or price values.
Only --gross may load the six previously admitted ES files, after checking the
exact committed marker/review/artifact/code/input chain. There are no stops,
fees, execution walks, account tests or 2023+ inputs in this raw screen.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
from datetime import date, datetime, timezone
import fcntl
from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path
import re
import subprocess
import sys
import traceback

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "analysis"))
import numpy as np
import pandas as pd
from grid24 import Grid24
from codex_hunt_v2_ldf_delta import tstat

OUT = ROOT / "analysis/outputs/codex_hunt_v2_mes_affordability"
SCRIPT = "analysis/codex_hunt_v2_mes_moc_gross.py"
PLAN = "agents/codex/plans/hunt_v2_mes_moc_affordability.md"
EVIDENCE = "agents/codex/research/hunt_v2_mes_moc_affordability_nomination.md"
SOURCE_REVIEW = "agents/codex/reviews/hunt_v2_mes_source_admission.json"
PREREG = "1a8087f7358901e08fa7e284ded7a6913b58568b"
PARENT_COMMIT = "d14dc9a153df128aafd3f48d4fea2aa78b88bb28"
PARENT_PATH = "funded_strategies/ES_MOC_Follow.txt"
PARENT_BLOB = "33e4a6a1c57dc0867d6ee9b26c310879ebd08f18"
YEARS = tuple(range(2018, 2023))
NATIVE = tuple(f"data/ES_1min_{year}.csv" for year in range(2017, 2023))
SOURCE_MARKER = "source_verified_execution.json"
SOURCE_REQUIRED = (
    "source_attempt.json", "source_pre_value_binding.json", "source_native_audit.json",
    "source_grid_audit.json", "source_parent_features.json", "source_decision_audit.json",
    "source_TR_audit.json", "source_expected_dates.json", "source_calendar_contradictions.json",
    "source_held_path_audit.json", "source_null_support.json", "source_counts.csv",
    "source_features.csv", "source_gate.json", "source_input_binding.json",
)
SOURCE_CODE = (
    "analysis/codex_hunt_v2_mes_moc_admit.py", "analysis/codex_hunt_v2_mes_parent.py",
    "analysis/grid24.py", "analysis/codex_s03_calendar.py", "analysis/replica.py", PLAN, EVIDENCE,
)
DEPENDENCIES = (*SOURCE_CODE, SCRIPT, "analysis/codex_hunt_v2_ldf_delta.py")
SHA_RE = re.compile(r"[0-9a-f]{64}\Z")
POINT_VALUE, RT_COST, HURDLE = 5., 3.74, 7.48


def now():
    return datetime.now(timezone.utc).isoformat()


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT)


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def json_once(name, value):
    with (OUT / name).open("x") as handle:
        json.dump(value, handle, indent=2, allow_nan=False)
        handle.write("\n")


def csv_once(name, records):
    with (OUT / name).open("x") as handle:
        pd.DataFrame(records).to_csv(handle, index=False, float_format="%.17g")


def read_json(name):
    with (OUT / name).open() as handle:
        return json.load(handle)


def committed_current(path):
    path = Path(path)
    relative = str(path.relative_to(ROOT))
    current = path.read_bytes()
    if git("show", "HEAD:" + relative) != current:
        raise ValueError("Commit exact artifact/dependency before gross phase:" + relative)
    return hashlib.sha256(current).hexdigest()


def code_binding(prereg):
    if prereg != PREREG or git("rev-parse", "--verify", prereg + "^{commit}").decode().strip() != prereg:
        raise ValueError("Use the exact original full H09 preregistration SHA.")
    if git("branch", "--show-current").decode().strip() != "codex/work":
        raise ValueError("H09 stays on codex/work.")
    subprocess.check_call(["git", "merge-base", "--is-ancestor", prereg, "HEAD"], cwd=ROOT)
    hashes = {name: committed_current(ROOT / name) for name in DEPENDENCIES}
    for name in (PLAN, EVIDENCE):
        if git("show", prereg + ":" + name) != (ROOT / name).read_bytes():
            raise ValueError("Original H09 plan/evidence changed:" + name)
    if git("rev-parse", PARENT_COMMIT + ":" + PARENT_PATH).decode().strip() != PARENT_BLOB:
        raise ValueError("Pinned parent source differs.")
    return dict(prereg=prereg, implementation_commit=git("rev-parse", "HEAD").decode().strip(),
        code_sha256=hashes, runtime_versions=dict(python=sys.version.split()[0], numpy=np.__version__, pandas=pd.__version__),
        parent_source=dict(commit=PARENT_COMMIT, path=PARENT_PATH, blob=PARENT_BLOB))


def source_header(marker, prereg):
    """Pure fail-closed header check, before any artifact/input financial load."""
    if marker.get("phase") != "SOURCE_SUPPORT_only" or marker.get("passed") is not True:
        raise ValueError("SOURCE/support must PASS; failed source cannot open raw endpoints.")
    if marker.get("prereg") != prereg or marker.get("raw_stopped_or_account_returns_computed") is not False:
        raise ValueError("Wrong prereg or SOURCE already interpreted returns.")
    if marker.get("gross_screen_runs") != 0 or marker.get("economic_evaluations") != 0:
        raise ValueError("SOURCE phase economic/gross count is not zero.")
    if set(marker.get("artifacts_sha256", {})) != set(SOURCE_REQUIRED):
        raise ValueError("SOURCE artifact inventory differs from the fixed successful protocol.")
    if set(marker.get("code_sha256", {})) != set(SOURCE_CODE):
        raise ValueError("SOURCE code inventory differs from the fixed protocol.")


def source_binding(prereg, expected_marker_sha, current):
    if not SHA_RE.fullmatch(expected_marker_sha):
        raise ValueError("Explicit exact SOURCE marker SHA256 is mandatory.")
    marker_path = OUT / SOURCE_MARKER
    if sha(marker_path) != expected_marker_sha:
        raise ValueError("SOURCE marker SHA differs before input access.")
    marker = read_json(SOURCE_MARKER)
    source_header(marker, prereg)
    if (OUT / "source_exception.json").exists():
        raise ValueError("Retained SOURCE exception prevents raw returns.")
    if committed_current(marker_path) != expected_marker_sha:
        raise ValueError("Commit reviewed SOURCE marker first.")
    artifact_hashes = marker["artifacts_sha256"]
    for name, expected in artifact_hashes.items():
        if not SHA_RE.fullmatch(expected) or committed_current(OUT / name) != expected:
            raise ValueError("SOURCE artifact changed:" + name)
    gate = read_json("source_gate.json")
    checks = gate.get("checks", {})
    if gate.get("phase") != "SOURCE_SUPPORT_only" or gate.get("passed") is not True or not checks or not all(value is True for value in checks.values()):
        raise ValueError("All frozen SOURCE/support gates must pass.")
    if gate.get("raw_stopped_or_account_returns_computed") is not False or gate.get("gross_screen_runs") != 0 or gate.get("economic_evaluations") != 0:
        raise ValueError("SOURCE gate has a prior financial interpretation.")
    source = read_json("source_input_binding.json")
    if source.get("prereg") != prereg or source.get("implementation_commit") != marker.get("implementation_commit"):
        raise ValueError("SOURCE marker/binding identity differs.")
    for name in SOURCE_CODE:
        expected = marker["code_sha256"][name]
        if expected != source.get("code_sha256", {}).get(name) or expected != current["code_sha256"][name]:
            raise ValueError("SOURCE dependency changed after admission:" + name)
    parent = source.get("parent_source", {})
    if (parent.get("commit"), parent.get("path"), parent.get("blob")) != (PARENT_COMMIT, PARENT_PATH, PARENT_BLOB):
        raise ValueError("SOURCE parent binding differs.")
    if not SOURCE_REVIEW.startswith("agents/codex/reviews/"):
        raise ValueError("Invalid fixed independent-review destination.")
    review_sha = committed_current(ROOT / SOURCE_REVIEW)
    with (ROOT / SOURCE_REVIEW).open() as handle:
        review = json.load(handle)
    if review.get("passed") is not True or review.get("raw_screen_authorized") is not True or not review.get("reviewer"):
        raise ValueError("Independent source admission review did not authorize raw screen.")
    if review.get("source_marker_sha256") != expected_marker_sha or review.get("source_gate_sha256") != artifact_hashes["source_gate.json"]:
        raise ValueError("Independent source review is not bound to this marker/gate.")
    inventory = source.get("native_inventory", [])
    if [item.get("path") for item in inventory] != list(NATIVE):
        raise ValueError("Only the original explicit six ES2017--22 files are allowed.")
    # Hash ALL six regular original inputs before Grid24 opens any header/value.
    for item in inventory:
        path = ROOT / item["path"]
        if not path.is_file() or path.is_symlink() or type(item.get("bytes")) is not int or not SHA_RE.fullmatch(item.get("sha256", "")):
            raise ValueError("Invalid admitted original native source:" + item["path"])
        if path.stat().st_size != item["bytes"] or sha(path) != item["sha256"]:
            raise ValueError("Admitted native input changed:" + item["path"])
    return dict(source_marker_sha256=expected_marker_sha, source_marker=marker,
        source_artifact_sha256=artifact_hashes, native_inventory=inventory,
        independent_review=dict(path=SOURCE_REVIEW, sha256=review_sha, reviewer=review["reviewer"]),
        source_gate=gate)


def validate_features(features, gate):
    """Pure consistency check on committed pre-entry records, no price inputs."""
    if not isinstance(features, list):
        raise ValueError("SOURCE parent feature ledger must be a list.")
    previous = None
    for index, row in enumerate(features):
        day = date.fromisoformat(row["date"])
        if day.isoformat() != row["date"] or day.year not in YEARS or day.weekday() >= 5 or row.get("year") != day.year:
            raise ValueError("Parent feature date outside frozen design universe.")
        if row.get("event_id") != index or (previous is not None and day <= previous):
            raise ValueError("Parent event IDs/dates must be unique and chronological.")
        previous = day
        if type(row.get("side")) is not int or row["side"] not in (-1, 1):
            raise ValueError("Invalid frozen parent direction.")
        if type(row.get("qty_extra")) is not int or row["qty_extra"] not in (0, 1) or row.get("qty_policy") != 1 + row["qty_extra"]:
            raise ValueError("EXTRA/POLICY must preserve whole-contract parent quantities.")
        if type(row.get("source_known")) is not bool or (not row["source_known"] and row["qty_extra"]):
            raise ValueError("Unknown EXTRA state cannot gain a contract.")
        if row.get("qty_BASE_Q1") != 1 or row.get("qty_CONST_Q2") != 2:
            raise ValueError("Frozen constant-size controls changed.")
        exact_atr = Fraction(row["atr_exact"])
        if exact_atr <= 0:
            raise ValueError("Invalid prior ATR in frozen parent feature.")
        stop = Fraction(math.ceil(exact_atr), 4)
        affordable = 2 * (stop * 5 + Fraction(374, 100)) <= 250
        if row["source_known"] and row["qty_extra"] != int(affordable):
            raise ValueError("Quantity differs from frozen rounded native affordability.")
        if abs(float(stop) - float(row["stop_points"])) > 1e-10:
            raise ValueError("Frozen protective distance differs from exact ATR.")
    extra = [row for row in features if row["qty_extra"]]
    if len(features) != gate.get("parent_events") or len(extra) != gate.get("extra_events"):
        raise ValueError("SOURCE gate and feature counts differ.")
    if len(features) < 100 or len(extra) < 50 or len({row["year"] for row in extra}) < 3:
        raise ValueError("Frozen minimum parent/EXTRA/year support did not pass.")
    if min(sum(row["side"] == side for row in extra) for side in (-1, 1)) < 10:
        raise ValueError("Frozen EXTRA side support did not pass.")
    return features


def raw_records(grid, features, outcome_state):
    """Interpret terminal quotes only for pre-admitted frozen event IDs."""
    axes = [str(pd.Timestamp(value).date()) for value in grid.ts]
    if len(axes) != len(set(axes)):
        raise ValueError("Shared native grid date axis is not unique.")
    lookup = {day: index for index, day in enumerate(axes)}
    rows = []
    for feature in features:
        if feature["date"] not in lookup:
            raise ValueError("Admitted parent date absent from bound shared grid.")
        day = lookup[feature["date"]]
        quotes = [float(grid.o[day, 891]), float(grid.c[day, 900])]
        if not all(math.isfinite(value) and value > 0 and abs(value * 4 - round(value * 4)) <= 1e-7 for value in quotes):
            raise ValueError("Exact admitted native O891/C900 invalid; no endpoint fallback.")
        entry, close = [round(value * 4) / 4 for value in quotes]
        # This is the first financial subtraction in the raw phase.
        gross = feature["side"] * (close - entry) * POINT_VALUE
        outcome_state["raw_return_subtractions"] += 1
        rows.append(dict(event_id=feature["event_id"], date=feature["date"], year=feature["year"],
            side=feature["side"], source_known=feature["source_known"], qty_BASE_Q1=1, qty_CONST_Q2=2,
            qty_EXTRA=feature["qty_extra"], qty_POLICY=feature["qty_policy"], qty_OMITTED_EXTRA=1-feature["qty_extra"],
            causal_atr_exact=feature["atr_exact"], stop_points=feature["stop_points"],
            entry_j=891, exit_j=900, raw_input_OPEN1451=quotes[0], raw_input_CLOSE1500=quotes[1],
            native_OPEN1451=entry, native_CLOSE1500=close, gross_per_mes=gross,
            gross_BASE_Q1=gross, gross_CONST_Q2=2*gross, gross_EXTRA=feature["qty_extra"]*gross,
            gross_POLICY=feature["qty_policy"]*gross, gross_OMITTED_EXTRA=(1-feature["qty_extra"])*gross,
            raw_no_stop=True, fees_or_slippage_deducted=False))
    return rows


def summarize(records):
    output = []
    for model in ("BASE_Q1", "CONST_Q2", "EXTRA", "POLICY", "OMITTED_EXTRA"):
        for period in ("2018-22", *map(str, YEARS)):
            for side in ("both", "long", "short"):
                chosen = [row for row in records if (period == "2018-22" or row["year"] == int(period))
                    and (side == "both" or row["side"] == (1 if side == "long" else -1))]
                active = [row for row in chosen if row["qty_"+model] > 0]
                values = np.asarray([row["gross_"+model] for row in active], dtype=float)
                if not np.isfinite(values).all():
                    raise ValueError("Raw summary may not omit nonfinite outcomes.")
                contracts = sum(row["qty_"+model] for row in active)
                n = len(values)
                sd = float(values.std(ddof=1)) if n >= 2 else None
                output.append(dict(model=model, period=period, side=side, parent_tickets=len(chosen),
                    active_tickets=n, whole_contracts=contracts, total_gross=float(values.sum()),
                    mean_gross_per_ticket=float(values.mean()) if n else None,
                    mean_gross_per_contract=float(values.sum()/contracts) if contracts else None,
                    SD_gross_per_ticket=sd, SE_gross_per_ticket=sd/math.sqrt(n) if sd is not None else None,
                    trade_t=tstat(values), costs_deducted=False, stopped_or_account_return=False))
    return output


def cost_gate(summaries):
    extra = next(row for row in summaries if (row["model"],row["period"],row["side"]) == ("EXTRA","2018-22","both"))
    mean = extra["mean_gross_per_contract"]
    passed = mean is not None and mean >= HURDLE
    return dict(phase="RAW_GROSS_DESIGN_only", passed=passed, incremental_candidate="EXTRA",
        extra_active_events=extra["active_tickets"], extra_total_gross=extra["total_gross"],
        extra_mean_gross_per_mes=mean, extra_trade_t=extra["trade_t"], native_mes_point_value=POINT_VALUE,
        native_RT_cost=RT_COST, twice_native_RT_hurdle=HURDLE,
        costs_basis="1.24RTcommission+1.25permarket_or_stopfill; no costs deducted from raw endpoints",
        raw_stop_or_fee_optimization=False, raw_endpoint_returns_computed=True,
        gross_screen_runs=1, economic_evaluations=0, new_hypothesis_registered=False,
        stopped_validation_account_placebo_or_PL_run=False,
        next_action="Commit/review raw results, then only frozen stopped designs" if passed else
            "Close H09 at raw cost gate; no stopped/validation/account tests or retuning")


def recheck(binding):
    for name, expected in binding["code_sha256"].items():
        if sha(ROOT/name) != expected:
            raise ValueError("Gross phase code/dependency changed:"+name)
    source = binding.get("source", {})
    for name, expected in source.get("source_artifact_sha256", {}).items():
        if sha(OUT/name) != expected:
            raise ValueError("SOURCE artifact changed during raw screen:"+name)
    if source and sha(OUT/SOURCE_MARKER) != source["source_marker_sha256"]:
        raise ValueError("SOURCE marker changed during raw screen.")
    for item in source.get("native_inventory", []):
        if (ROOT/item["path"]).stat().st_size != item["bytes"] or sha(ROOT/item["path"]) != item["sha256"]:
            raise ValueError("Bound native input changed during raw screen:"+item["path"])


@contextmanager
def lock():
    OUT.mkdir(parents=True, exist_ok=True)
    with (OUT/"source.lock").open("a") as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        yield


def gross(prereg, source_marker_sha):
    binding = code_binding(prereg)
    with lock():
        for directory in (ROOT/"analysis/outputs").glob("codex_hunt_v2_mes_affordability*"):
            if any((directory/name).exists() for name in ("gross_attempt.json", "gross_verified_execution.json")):
                raise ValueError("Retained H09 raw attempt exists; no unchanged retry/alternate output directory.")
        started = now()
        json_once("gross_attempt.json", dict(started_utc=started, **binding,
            requested_source_marker_sha256=source_marker_sha, retry_authorized=False))
        names = ["gross_attempt.json"]
        outcome_state = dict(raw_return_subtractions=0)
        stage = "SOURCE_marker_gate_review_and_all_bindings_before_price_values"
        try:
            binding["source"] = source_binding(prereg, source_marker_sha, binding)
            features = validate_features(read_json("source_parent_features.json"), binding["source"]["source_gate"])
            json_once("gross_pre_value_binding.json", binding)
            names.append("gross_pre_value_binding.json")
            stage = "shared_grid_exact_six_preexisting_source_links"
            cache = OUT/"cache/native_design"
            links = {f"day_{year}.csv":ROOT/name for year,name in zip(range(2017,2023),NATIVE)}
            if {path.name for path in cache.iterdir()} != set(links):
                raise ValueError("Exact pre-admitted six-file shared-grid cache inventory differs.")
            for name, target in links.items():
                path = cache/name
                if not path.is_symlink() or path.resolve() != target.resolve():
                    raise ValueError("Shared-grid cache link differs from admitted original input.")
            grid = Grid24(str(cache/"day_*.csv"), night_pattern="")
            stage = "raw_frozen_parent_endpoint_returns_no_stops_or_costs"
            records = raw_records(grid, features, outcome_state)
            del grid
            summaries = summarize(records)
            csv_once("gross_events.csv", records)
            csv_once("gross_summary_side_year.csv", summaries)
            names += ["gross_events.csv", "gross_summary_side_year.csv"]
            gate = cost_gate(summaries)
        except Exception as error:
            gate = dict(phase="RAW_GROSS_DESIGN_only", passed=False, status="SOURCE_OR_IMPLEMENTATION_BLOCKED",
                stage=stage, exception_type=type(error).__name__, exception_message=str(error),
                raw_endpoint_returns_computed=bool(outcome_state["raw_return_subtractions"]),
                gross_screen_runs=int(bool(outcome_state["raw_return_subtractions"])), economic_evaluations=0,
                stopped_validation_account_placebo_or_PL_run=False, retry_authorized=False)
            json_once("gross_exception.json", dict(gate, traceback=traceback.format_exc()))
            names.append("gross_exception.json")
        try:
            recheck(binding)
        except Exception as error:
            gate.update(passed=False, final_binding_recheck_failed=str(error))
        gate["raw_return_subtractions"] = outcome_state["raw_return_subtractions"]
        json_once("gross_gate.json", gate)
        json_once("gross_input_binding.json", binding)
        names += ["gross_gate.json", "gross_input_binding.json"]
        marker = dict(started_utc=started, completed_utc=now(), phase="RAW_GROSS_DESIGN_only",
            passed=gate["passed"], prereg=prereg, implementation_commit=binding["implementation_commit"],
            source_marker_sha256=source_marker_sha, code_sha256=binding["code_sha256"],
            artifacts_sha256={name:sha(OUT/name) for name in names},
            raw_endpoint_returns_computed=gate["raw_endpoint_returns_computed"],
            raw_return_subtractions=outcome_state["raw_return_subtractions"], gross_screen_runs=gate["gross_screen_runs"],
            economic_evaluations=0, new_hypothesis_registered=False, retry_authorized=False,
            stopped_validation_account_placebo_or_PL_run=False)
        json_once("gross_verified_execution.json", marker)
        return gate


def fixtures():
    """Invented arrays/dictionaries only; no file, marker or schedule read."""
    from types import SimpleNamespace
    checks = []
    fake = dict(phase="SOURCE_SUPPORT_only", passed=True, prereg=PREREG,
        raw_stopped_or_account_returns_computed=False, gross_screen_runs=0, economic_evaluations=0,
        artifacts_sha256={name:"a"*64 for name in SOURCE_REQUIRED}, code_sha256={name:"b"*64 for name in SOURCE_CODE})
    source_header(fake,PREREG)
    for change in (dict(passed=False),dict(prereg="0"*40),dict(raw_stopped_or_account_returns_computed=True),
                   dict(gross_screen_runs=1),dict(economic_evaluations=1),dict(artifacts_sha256={})):
        try:
            source_header(dict(fake,**change),PREREG)
        except ValueError:
            pass
        else:
            raise AssertionError("Failed/mismatched SOURCE header admitted.")
    checks.append("pure_SOURCE_failure_and_identity_veto_before_any_price_loader")
    dates = ["2018-01-02","2018-01-03","2019-01-02","2020-01-02"]
    signs, closes, masks = [1,-1,1,-1],[101,102,100,97],[1,0,0,1]
    g = SimpleNamespace(ts=np.array(dates,dtype="datetime64[D]"),
        o=np.full((4,1440),np.nan),c=np.full((4,1440),np.nan))
    g.o[:,891] = 100;g.c[:,900] = closes
    features = [dict(event_id=i,date=day,year=int(day[:4]),side=signs[i],source_known=True,
        qty_extra=masks[i],qty_policy=1+masks[i],atr_exact="4/1",stop_points=1.) for i,day in enumerate(dates)]
    state = dict(raw_return_subtractions=0)
    rows = raw_records(g,features,state)
    assert [row["gross_per_mes"] for row in rows] == [5.,-10.,0.,15.]
    assert state["raw_return_subtractions"] == 4
    summary = summarize(rows)
    pick = lambda model: next(r for r in summary if (r["model"],r["period"],r["side"]) == (model,"2018-22","both"))
    assert pick("BASE_Q1")["total_gross"] == 10 and pick("CONST_Q2")["total_gross"] == 20
    assert pick("EXTRA")["total_gross"] == 20 and pick("POLICY")["total_gross"] == 30
    assert pick("OMITTED_EXTRA")["total_gross"] == -10
    assert pick("EXTRA")["active_tickets"] == 2 and pick("EXTRA")["trade_t"] == 2
    assert cost_gate(summary)["passed"] and cost_gate(summary)["economic_evaluations"] == 0
    checks.append("bothside_raw_endpoints_exact_native_cash_and_zero_return_tickets_kept")
    checks.append("all_extra_omitted_constant_and_policy_profit_conservation_and_cost_hurdle")
    failed = [dict(row,qty_EXTRA=1 if row["event_id"] in (0,1) else 0,
        gross_EXTRA=row["gross_per_mes"] if row["event_id"] in (0,1) else 0) for row in rows]
    assert not cost_gate(summarize(failed))["passed"]
    for key in (891,900):
        bad = SimpleNamespace(ts=g.ts,o=g.o.copy(),c=g.c.copy())
        (bad.o if key == 891 else bad.c)[0,key] = np.nan
        try:
            raw_records(bad,features,dict(raw_return_subtractions=0))
        except ValueError:
            pass
        else:
            raise AssertionError("Missing exact endpoint was repaired.")
    checks.append("raw_fail_stops_and_missing_endpoints_have_no_fallback")
    return dict(passed=True,groups=len(checks),checks=checks,actual_input_marker_header_schema_rows_or_calendar_accessed=False,
        actual_market_returns_computed=False,economic_evaluations=0,gross_screen_runs=0)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--fixtures",action="store_true")
    mode.add_argument("--gross",action="store_true")
    parser.add_argument("--prereg")
    parser.add_argument("--source-marker-sha")
    arguments = parser.parse_args()
    if arguments.fixtures:
        print(json.dumps(fixtures(),allow_nan=False))
    else:
        if not arguments.prereg or not arguments.source_marker_sha:
            parser.error("--gross requires exact --prereg and --source-marker-sha")
        print(json.dumps(gross(arguments.prereg,arguments.source_marker_sha),allow_nan=False))
