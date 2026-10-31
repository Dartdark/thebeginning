"""Current 17-piece personal portfolio comparison for the frozen S03 v2 review.

Import, source staging, and synthetic fixtures never read market data. Historical
loading/benchmarking requires the root preregistration hash and a passed DESIGN
gate. The published reference and the corrected accounting are separate outputs.
No live action, quantity search, or strategy parameter selection is implemented.
"""
from __future__ import annotations

import argparse
import contextlib
from dataclasses import dataclass
import hashlib
import importlib.util
import json
from pathlib import Path
import pickle
import subprocess
import sys

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PIN = "e4399c8e235ee26674c88a439d4c9926b5731af4"
RUNTIME = ROOT / "agents/codex/runtime/s03_personal_deps"
SOURCES = RUNTIME / "claude"
OUT = ROOT / "analysis/outputs/codex_s03_noisearea/personal"
FEES = (1.04, 1.24)
SEED, N, BLOCK, HORIZON = 20261024, 1000, 20, 252
PLAN_COLUMNS = (
    "VaultBreak", "OvernightBiasML", "MondayLong", "ExpirationOpenShort",
    "LateDayFlow", "NFPFade", "BridgeMondayLong", "CLSundayFade_perMCL",
    "ESMOCFollow_perMES", "RelativeStrength",
)
EXTRA_COLUMNS = ("FC2B", "TwinContinuation", "OvernightAnomaly", "DualThrust", "Kusho", "S47", "S30")
COLUMNS = PLAN_COLUMNS + EXTRA_COLUMNS
PLAN_LAB_MAP = dict(VB="VaultBreak", ONB_ML2_MC="OvernightBiasML", MON_MC="MondayLong", EOS="ExpirationOpenShort",
                    LDF_MC="LateDayFlow", NFP_MC="NFPFade", MON_BR_MC="BridgeMondayLong", CLS="CLSundayFade_perMCL",
                    MOC_MES="ESMOCFollow_perMES", RS="RelativeStrength")
START_A = ("TwinContinuation", "OvernightBiasML", "BridgeMondayLong", "CLSundayFade_perMCL", "NFPFade")
START_B = START_A + ("ExpirationOpenShort",)
START_C = START_B + ("VaultBreak",)
START_D = START_C + ("RelativeStrength", "ESMOCFollow_perMES")
CORE = tuple(k for k in COLUMNS if k != "S30")
INPUTS = (
    "analysis/personal_portfolio.py", "analysis/forward_log_plans_test.py",
    "personal_strategies/PORTFOLIO.md", "agents/tasks/plan_daily_pnl.csv",
    "checks/candidates/fc_2b/trades.csv", "checks/candidates/twin_continuation/trades.csv",
    "checks/candidates/overnight_anomaly/trades.csv", "checks/candidates/dual_thrust/trades.csv",
    "checks/candidates/kusho/python_trades_v9_rolladj.csv", "checks/candidates/s47_v2/python_trades_v2.csv",
    "checks/candidates/s30_ibs/daily_nq_es_per_micro.csv", "checks/candidates/s30_ibs/python_trades_NQ.csv",
    "checks/candidates/s30_ibs/python_trades_ES.csv", "analysis/montecarlo.py", "analysis/metrics.py",
    "analysis/resampling.py", "analysis/grid24.py", "analysis/outputs/personal_portfolio_output.txt",
    "analysis/kusho_bench.py", "analysis/s30_ibs_test.py", "analysis/kusho_test.py",
    "analysis/overnight_round.py", "analysis/overnight_anomaly_test.py", "checks/candidates/twin_continuation/spec.md",
    "analysis/twin_continuation_test.py",
)
LIMITATIONS = [
    "Historical replication of already observed strategies, not an untouched holdout.",
    "Personal risk is measured on synchronized daily 16CT marks; intraday margin/liquidation risk is not a daily-MC result.",
    "Current canonical Twin is the v1 checker ledger, not an exact v2.1 ledger; its original rules and raw-roll exposure are preserved.",
    "Kusho/S30 roll corrections inherit the source's inferred continuous-contract switch convention, not a broker roll ledger.",
    "Closed baseline ledgers do not certify that no terminal position exists; terminal position inventory must be attested separately.",
    "Quantities are fixed in native micro equivalents; the Core10 row does not assume cheaper mini commissions.",
]


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for b in iter(lambda: f.read(1024 * 1024), b""):
            h.update(b)
    return h.hexdigest()


def dump(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, default=str) + "\n")


@dataclass(frozen=True)
class Authorization:
    prereg_path: str
    prereg_sha256: str
    design_path: str
    design_sha256: str


def authorize(prereg, prereg_sha256, design_gate):
    """Validate root's concrete hash and gate before historical work."""
    prereg, design_gate = Path(prereg).resolve(), Path(design_gate).resolve()
    if len(str(prereg_sha256)) != 64 or sha(prereg) != prereg_sha256:
        raise PermissionError("Root preregistration SHA256 does not match")
    gate = json.loads(design_gate.read_text())
    status = str(gate.get("status", gate.get("decision", ""))).upper()
    linked = gate.get("prereg_sha256", gate.get("root_prereg_sha256"))
    if status not in ("PASS", "PASSED") or linked != prereg_sha256 or gate.get("allow_personal") is not True:
        raise PermissionError("A passed linked DESIGN gate with allow_personal=true is required")
    return Authorization(str(prereg), prereg_sha256, str(design_gate), sha(design_gate))


def require_authorization(auth):
    if not isinstance(auth, Authorization):
        raise PermissionError("Historical work requires root preregistration and DESIGN authorization")
    if sha(auth.prereg_path) != auth.prereg_sha256 or sha(auth.design_path) != auth.design_sha256:
        raise PermissionError("Authorization artifact changed")


def prepare_sources(source_repo=ROOT, runtime=SOURCES):
    """Fresh-clone reproducibility: exact pinned git-show bytes, without checkout/reset."""
    runtime, source_repo = Path(runtime).resolve(), Path(source_repo).resolve()
    if not runtime.is_relative_to(RUNTIME.resolve()):
        raise ValueError("Personal staging is limited to its owned runtime directory")
    manifest = dict(reference=PIN, retrieval="git show from explicit source_repo", files={})
    for rel in INPUTS:
        data = subprocess.check_output(["git", "-C", str(source_repo), "show", PIN + ":" + rel])
        blob = subprocess.check_output(["git", "-C", str(source_repo), "rev-parse", PIN + ":" + rel]).decode().strip()
        dest = runtime / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)
        manifest["files"][rel] = dict(git_blob=blob, sha256=sha(dest), bytes=len(data))
    dump(runtime / "manifest.json", manifest)
    return manifest


def verify_sources(runtime=SOURCES):
    runtime = Path(runtime)
    manifest = json.loads((runtime / "manifest.json").read_text())
    if manifest["reference"] != PIN or set(manifest["files"]) != set(INPUTS):
        raise ValueError("Incomplete or stale personal17 source inventory")
    for rel, meta in manifest["files"].items():
        data = (runtime / rel).read_bytes()
        blob = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
        if blob != meta["git_blob"] or sha(runtime / rel) != meta["sha256"]:
            raise ValueError("Edited pinned source: " + rel)
    return manifest


def baseline_source_inventory(runtime=SOURCES):
    """Audit the published ledger contract and endpoint metadata, without returns.

    The canonical portfolio is a closed-ledger research reconstruction. Balanced
    emitted entry/exit events establish that scope; they do not claim knowledge
    of unexported simulator state or broker positions. A known cutoff-spanning
    ledger trade is separately rejected by corrected_baseline.
    """
    verify_sources(runtime)
    runtime=Path(runtime)
    dates=pd.read_csv(runtime/"agents/tasks/plan_daily_pnl.csv",usecols=["date"])
    days=validate_days(pd.to_datetime(dates.date))
    ledger_specs=(
        ("FC2B","fc_2b/trades.csv","date","date"),
        ("TwinContinuation","twin_continuation/trades.csv","entry_date","date"),
        ("OvernightAnomaly","overnight_anomaly/trades.csv","entry_date","date"),
        ("DualThrust","dual_thrust/trades.csv","date","date"),
        ("Kusho","kusho/python_trades_v9_rolladj.csv","date","exit_date"),
        ("S47","s47_v2/python_trades_v2.csv","date","date"),
        ("S30_NQ","s30_ibs/python_trades_NQ.csv","date","exit_date"),
        ("S30_ES","s30_ibs/python_trades_ES.csv","date","exit_date"),
    )
    inventory={}
    unresolved=known_open=0
    for piece,rel,entry,exit_ in ledger_specs:
        t=pd.read_csv(runtime/("checks/candidates/"+rel),usecols=list(dict.fromkeys([entry,exit_])))
        en,ex=pd.to_datetime(t[entry]),pd.to_datetime(t[exit_])
        invalid=en.isna()|ex.isna()|(ex<en)
        crossing=(en<=days[-1])&(ex>days[-1])
        unresolved+=int(invalid.sum());known_open+=int(crossing.sum())
        inventory[piece]=dict(rows=len(t),entry_events=len(en),exit_events=len(ex),
            first_entry=str(en.min().date()),last_entry=str(en.max().date()),last_exit=str(ex.max().date()),
            invalid_event_rows=int(invalid.sum()),known_cutoff_spanning_rows=int(crossing.sum()),
            original_path="checks/candidates/"+rel,ledger_sha256=sha(runtime/("checks/candidates/"+rel)))
    return dict(reference=PIN,complete=unresolved==0,pieces=list(COLUMNS),open_positions=known_open,
        unresolved_positions=unresolved,scope="published_closed_ledger_portfolio",
        plan_first_date=str(days[0].date()),plan_last_date=str(days[-1].date()),plan_dates=len(days),
        standalone_ledgers=inventory,source_contract="analysis/personal_portfolio.py at exact pinned commit",
        terminal_state_limitation="Unexported simulator terminal state is not inferred from closed ledgers; benchmark reproduces all known source positions only",
        native_plan_endpoint_check="exact current native-unit exports must cover every canonical date before corrected returns")


@contextlib.contextmanager
def pinned_modules(runtime=SOURCES):
    """Keep exact legacy module identities for pickles and helper imports."""
    runtime = Path(runtime)
    prior_path, prior_argv = sys.path[:], sys.argv[:]
    names = ("grid24", "metrics", "montecarlo", "resampling", "overnight_round")
    previous = {n: sys.modules.pop(n) for n in names if n in sys.modules}
    sys.path.insert(0, str(runtime / "analysis"))
    sys.argv = [str(__file__), str(ROOT / "scratch_data")]
    try:
        # Legacy scripts insert the working analysis/ directory at position0.
        # Preload exact modules so those imports cannot bind stale local files.
        for name in names:
            module = import_file("s03_pinned_" + name, runtime / ("analysis/" + name + ".py"))
            sys.modules[name] = module
        yield
    finally:
        for n in names:
            sys.modules.pop(n, None)
        sys.modules.update(previous)
        sys.path[:] = prior_path
        sys.argv[:] = prior_argv


def import_file(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def validate_days(days):
    days = pd.DatetimeIndex(days)
    if not len(days) or days.has_duplicates or not days.is_monotonic_increasing or not (days == days.normalize()).all():
        raise ValueError("Expected nonempty ordered unique normalized daily calendar")
    return days


def session_index(days, stamp):
    stamp = pd.Timestamp(stamp)
    date = stamp.normalize()
    date += pd.Timedelta(days=int(stamp > date + pd.Timedelta(hours=16)))
    k = int(days.searchsorted(date))
    if k >= len(days):
        raise ValueError("Event is after the benchmark cutoff; terminal valuation is required")
    return k


def fill_stamp(g, date, j, price, *, phase=None):
    """Resolve source minute stamps against their actual open/gap convention.

    Intrabar timestamps encode only ordering relative to the minute open and
   16CT boundary; the30seconds is not a claimed tick timestamp. The source's
    max/min(open,order) fill at the open is identifiable from its fill price.
    """
    date = pd.Timestamp(date).normalize(); j = int(j)
    lookup = {pd.Timestamp(d).normalize(): i for i, d in enumerate(g.ts)}
    row = lookup[date]
    if phase is None:
        phase = "open" if np.isclose(price, g.o[row,j], rtol=0, atol=1e-9) else "intrabar"
    if phase == "close":
        return date + pd.Timedelta(minutes=j)
    return date + pd.Timedelta(minutes=j-1,seconds=0 if phase=="open" else 30)


def book_daily(values, dates, days, *, strict=True):
    days = validate_days(days)
    dates = pd.DatetimeIndex(dates).normalize()
    ix = days.searchsorted(dates)
    if strict and ((ix >= len(days)).any() or (dates < days[0]).any()):
        raise ValueError("Daily booking outside benchmark interval")
    if not strict:
        ix = np.minimum(ix, len(days) - 1)  # canonical reference only
    out = np.zeros(len(days))
    np.add.at(out, ix, np.asarray(values, float))
    return pd.Series(out, index=days)


def ledger_net_micro(t, fee, commission=7.25):
    """Replace only commission; source net already contains the source slippage."""
    comm = np.asarray(t["comm"] if "comm" in t else commission, float)
    return t.net.to_numpy(float) / 10 + comm / 10 - float(fee)


def fixed_ladders():
    def allocation(keys, core=1, s30=0):
        q = {k: int(core) for k in keys}
        if s30:
            q["S30"] = int(s30)
        return q
    return {
        "A": (allocation(START_A), 1), "B": (allocation(START_B), 1),
        "C": (allocation(START_C), 1), "D": (allocation(START_D), 1),
        "13_NO_DT": (allocation([k for k in CORE if k not in ("DualThrust", "Kusho", "S47")]), 1),
        "14_NO_KUSHO_S47": (allocation([k for k in CORE if k not in ("Kusho", "S47")]), 1),
        "CORE16": (allocation(CORE), 1), "FULL17": (allocation(CORE, s30=1), 1),
        "CORE2_S30_1": (allocation(CORE, core=2, s30=1), 2),
        "CORE4_S30_1": (allocation(CORE, core=4, s30=1), 4),
        "CORE10_S30_3": (allocation(CORE, core=10, s30=3), 10),
    }


def configurations(frame, candidate):
    if set(frame) != set(COLUMNS) or not frame.index.equals(candidate.index):
        raise ValueError("Expected synchronized current17 baseline and candidate")
    if not np.isfinite(frame.to_numpy()).all() or not np.isfinite(candidate.to_numpy()).all():
        raise ValueError("Missing portfolio values cannot be zero-imputed")
    plans, meta = {}, {}
    for group, (quantity, add_unit) in fixed_ladders().items():
        base = sum(frame[k] * n for k, n in quantity.items())
        vb = int(quantity.get("VaultBreak", 0))
        empty = base - frame.VaultBreak * vb
        choices = dict(BASE=base, ADD_S03=base + candidate * add_unit,
                       EMPTY_VB=empty, REPLACE_VB=empty + candidate * vb)
        for label, value in choices.items():
            name = group + "__" + label
            plans[name] = value
            meta[name] = dict(group=group, allocation=label, baseline_quantities=quantity,
                              add_s03_units=add_unit, replace_s03_units=vb,
                              replacement_applicable=bool(vb), quantities_frozen_before_returns=True)
    return plans, meta


def reject_incomplete_candidate(trades, audit):
    """Inspect complete replay audit, including censored entries absent from CSV."""
    if not isinstance(audit, dict) or audit.get("complete") is not True:
        raise ValueError("Complete candidate replay audit is required")
    if audit.get("personal_path_eligible") is not True:
        raise ValueError("Replay audit blocks personal paths/Monte Carlo")
    if audit.get("all_native_dates_covered") is not True or int(audit.get("calendar_unknown_native_minutes", -1)) != 0:
        raise ValueError("Unobserved native/no-trade dates block personal Monte Carlo")
    for key in ("unknown_held_minutes", "unknown_held_trades", "censored_trades", "unresolved_positions", "unpriced_positions"):
        if key not in audit:
            raise ValueError("Candidate audit omits " + key)
        if int(audit[key]) != 0:
            raise ValueError("Candidate audit contains unresolved held data: " + key)
    for key in ("unknown_held_minutes", "unknown_heldmins", "censored", "cross_date"):
        if key in trades and trades[key].fillna(1).astype(float).ne(0).any():
            raise ValueError("Candidate ledger contains " + key)
    if not {"date", "net"}.issubset(trades) or not np.isfinite(trades.net.to_numpy(float)).all():
        raise ValueError("Candidate ledger lacks finite date/net")


def candidate_daily(trades, days, audit, fee=1.04):
    reject_incomplete_candidate(trades, audit)
    out = book_daily(ledger_net_micro(trades, fee), pd.to_datetime(trades.date), days)
    np.testing.assert_allclose(out.sum(), ledger_net_micro(trades, fee).sum(), rtol=0, atol=1e-8)
    return out.rename("S03")


def load_reference(*, auth, scratch=ROOT / "scratch_data", runtime=SOURCES):
    """Exact current canonical17 accounting; never run canonical __main__/MC."""
    require_authorization(auth)
    manifest = verify_sources(runtime)
    runtime = Path(runtime)
    p = pd.read_csv(runtime / "agents/tasks/plan_daily_pnl.csv", parse_dates=["date"]).set_index("date")
    if set(p) != set(PLAN_COLUMNS):
        raise ValueError("Personal plan source no longer has its ten canonical columns")
    days = validate_days(p.index)
    p = p - .55 * (p != 0)
    def from_trades(rel, name, exit_date="date"):
        t = pd.read_csv(runtime / rel)
        date = pd.to_datetime(t[exit_date])
        t = t.loc[date <= days[-1]]
        return book_daily(t.net.to_numpy() / 10 - .55, date.loc[t.index], days, strict=False).rename(name)
    pieces = [p]
    for rel, name in (("fc_2b/trades.csv", "FC2B"), ("overnight_anomaly/trades.csv", "OvernightAnomaly"),
                      ("dual_thrust/trades.csv", "DualThrust"), ("s47_v2/python_trades_v2.csv", "S47")):
        pieces.append(from_trades("checks/candidates/" + rel, name))
    pieces.append(from_trades("checks/candidates/kusho/python_trades_v9_rolladj.csv", "Kusho", "exit_date"))
    with pinned_modules(runtime):
        src = import_file("s03_current_personal_reference", runtime / "analysis/personal_portfolio.py")
        pieces.append(src.twin_marked(days, path=str(runtime / "checks/candidates/twin_continuation/trades.csv"), sp=str(Path(scratch).resolve()) + "/"))
    s30 = pd.read_csv(runtime / "checks/candidates/s30_ibs/daily_nq_es_per_micro.csv", index_col=0, parse_dates=True).iloc[:, 0]
    pieces.append(s30.reindex(days, fill_value=0.).rename("S30"))
    frame = pd.concat(pieces, axis=1).loc[:, list(COLUMNS)]
    if not np.isfinite(frame.to_numpy()).all():
        raise ValueError("Canonical17 reference has missing values")
    return frame, manifest


def reprice_plan(raw_plan, counts, commission_credit, fee):
    """Exact daily counts/credits must come from canonical current timed ledgers."""
    for value in (raw_plan, counts, commission_credit):
        if set(value) != set(PLAN_COLUMNS) or not value.index.equals(raw_plan.index):
            raise ValueError("Personal ten-piece fee inputs do not align")
        if not np.isfinite(value.to_numpy()).all():
            raise ValueError("Missing plan daily/count/commission input")
    if (counts.to_numpy() < 0).any() or not np.equal(counts.to_numpy(), np.floor(counts.to_numpy())).all():
        raise ValueError("Plan counts must include every whole native-unit trade")
    if (commission_credit.to_numpy() < 0).any():
        raise ValueError("Negative original commission credit")
    return raw_plan + commission_credit - float(fee) * counts


def align_plan_export(frame, days):
    """Map exact current account-lab unit exports to personal canonical names."""
    frame = frame.rename(columns=PLAN_LAB_MAP)
    if not set(PLAN_COLUMNS).issubset(frame):
        raise ValueError("Account export omits a current personal plan piece")
    out = frame.reindex(validate_days(days)).loc[:, list(PLAN_COLUMNS)]
    if not np.isfinite(out.to_numpy()).all():
        raise ValueError("Account export omits personal benchmark dates")
    return out


def reconcile_plan_native(raw_plan, plan_native_daily, counts, commission_credit, source_fee=1.04):
    reconstructed = plan_native_daily + source_fee * counts - commission_credit
    delta = raw_plan - reconstructed
    worst = float(np.abs(delta.to_numpy()).max())
    return dict(exact_within_tolerance=worst <= 1e-6, maximum_absolute_daily_difference=worst,
                tolerance=1e-6, source_fee=source_fee,
                per_piece_maximum_difference={k:float(delta[k].abs().max()) for k in PLAN_COLUMNS})


def roll_jump_series(g, symbol, runtime=SOURCES):
    """Use exact current source convention; only called after parent authorization."""
    with pinned_modules(runtime):
        helper = import_file("s03_current_roll_helper", Path(runtime) / "analysis/overnight_round.py")
        addresses = np.sort(helper.roll_minutes(g, symbol))
    c = g.c.ravel()
    jumps = {}
    for j in addresses:
        prior = np.flatnonzero(np.isfinite(c[:j]))
        if not len(prior) or not np.isfinite(c[j]):
            raise ValueError("Roll adjustment lacks observed prices")
        jumps[int(j)] = float(c[j] - c[prior[-1]])
    return jumps


def marked_ledger(g, trades, days, *, fee, point_value=2., entry_slip=0., jumps=None, name="piece"):
    """Synchronized16CT marks with exact source-net reconciliation.

    Trades have entry_stamp/exit_stamp, raw-or-already-slipped entry/exit,
    source mini net and comm. The source's slip convention is preserved: entry
    slip is reserved explicitly, residual source execution cost is paid at exit.
    Known roll jumps are removed at their own mark interval, not only at exit.
    No future price, global forward fill, silent missing mark, or exit clamp.
    """
    days = validate_days(days)
    lookup = {pd.Timestamp(d).normalize(): i for i, d in enumerate(g.ts)}
    out, records, expected = np.zeros(len(days)), [], 0.
    jumps = {} if jumps is None else jumps
    for no, t in enumerate(trades.to_dict("records")):
        et, xt = pd.Timestamp(t["entry_stamp"]), pd.Timestamp(t["exit_stamp"])
        if xt < et:
            raise ValueError("Exit before entry")
        a, b = session_index(days, et), session_index(days, xt)
        e, x, side = float(t["entry"]), float(t["exit"]), int(t.get("side", 1))
        if not np.isfinite([e, x]).all() or side not in (-1, 1):
            raise ValueError("Invalid source ledger fill")
        ei = int(t.get("entry_address", -1)); xi = int(t.get("exit_address", -1))
        held_jumps = {j: v for j, v in jumps.items() if ei < j <= xi}
        jump_net = sum(held_jumps.values()) * side * point_value
        source_net = float(t["net"]) / 10
        original_fee = float(t.get("comm", 7.25)) / 10
        residual = (x - e) * side * point_value - jump_net - source_net - original_fee - entry_slip
        if residual < -1e-6:
            raise ValueError("Source net/roll/entry-slippage accounting cannot reconcile: " + name)
        residual = max(0., residual)
        out[a] -= fee + entry_slip
        previous = e
        removed = set()
        for k in range(a, b):
            date = days[k]
            row = lookup.get(date)
            if row is None:
                raise ValueError("Held baseline session lacks calendar row")
            js = np.flatnonzero(np.isfinite(g.c[row, :961]))
            if not len(js):
                raise ValueError("Held baseline session lacks observed mark at/before16CT")
            j = int(js[-1]); stamp = date + pd.Timedelta(minutes=j)
            if stamp <= et:
                raise ValueError("No observed held mark after entry")
            price = float(g.c[row, j]); address = row * 1440 + j
            remove = {q for q in held_jumps if q <= address and q not in removed}
            pnl = (price - previous) * side * point_value - sum(held_jumps[q] for q in remove) * side * point_value
            removed.update(remove)
            out[k] += pnl
            records.append(dict(piece=name, trade=no, date=date, mark_j=j, minutes_before16=960-j,
                                price=price, mark_pnl=pnl, removed_rolls=len(remove), source="observed_same_date_close"))
            previous = price
        out[b] += (x - previous) * side * point_value - residual - sum(v for j, v in held_jumps.items() if j not in removed) * side * point_value
        expected += source_net + original_fee - fee
    np.testing.assert_allclose(out.sum(), expected, rtol=0, atol=1e-6)
    return pd.Series(out, index=days, name=name), pd.DataFrame(records), dict(trades=len(trades), net_sum=float(out.sum()), expected_net=expected, fee=fee)


def corrected_baseline(*, auth, scratch, counts, commission_credit, plan_native_daily, terminal_inventory, runtime=SOURCES, fee=1.04):
    """Keep17 fixed rules; repair commissions and overnight daily accounting."""
    require_authorization(auth)
    verify_sources(runtime)
    if (terminal_inventory.get("complete") is not True or terminal_inventory.get("unresolved_positions", 1) != 0
            or terminal_inventory.get("reference") != PIN or set(terminal_inventory.get("pieces", [])) != set(COLUMNS)):
        raise ValueError("Complete baseline terminal-position inventory is required")
    if terminal_inventory.get("open_positions") != 0:
        raise ValueError("Open baseline positions require explicit terminal marks; closed-only benchmark blocked")
    runtime, scratch = Path(runtime), Path(scratch)
    raw = pd.read_csv(runtime / "agents/tasks/plan_daily_pnl.csv", parse_dates=["date"]).set_index("date")
    days = validate_days(raw.index)
    counts = align_plan_export(counts, days)
    commission_credit = align_plan_export(commission_credit, days)
    plan_native_daily = align_plan_export(plan_native_daily, days)
    reconciliation = reconcile_plan_native(raw, plan_native_daily, counts, commission_credit)
    if not reconciliation["exact_within_tolerance"]:
        raise ValueError("Current canonical personal plan and native-unit lab differ: " + json.dumps(reconciliation))
    frame = reprice_plan(raw, counts.loc[:, list(PLAN_COLUMNS)], commission_credit.loc[:, list(PLAN_COLUMNS)], fee)
    manifest, mark_tables = dict(fee=fee, reference=PIN, pieces={}, limitations=LIMITATIONS,
                                 price_caches={k:sha(scratch/k) for k in ("g24.pkl","ge.pkl")},
                                 terminal_inventory=terminal_inventory, plan_reconciliation=reconciliation), []
    def read(rel):
        return pd.read_csv(runtime / ("checks/candidates/" + rel))
    def closed_window(t):
        cutoff = days[-1] + pd.Timedelta(hours=16)
        if ((t.entry_stamp <= cutoff) & (t.exit_stamp > cutoff)).any():
            raise ValueError("A source trade spans the cutoff; terminal marks must be supplied")
        return t.loc[(t.entry_stamp <= cutoff) & (t.exit_stamp <= cutoff)].copy()
    for rel, name in (("fc_2b/trades.csv", "FC2B"), ("overnight_anomaly/trades.csv", "OvernightAnomaly"),
                      ("dual_thrust/trades.csv", "DualThrust"), ("s47_v2/python_trades_v2.csv", "S47")):
        t = read(rel); t = t.loc[pd.to_datetime(t.date) <= days[-1]].copy()
        frame[name] = book_daily(ledger_net_micro(t, fee), t.date, days)
        manifest["pieces"][name] = dict(trades=len(t),source_fee_credit=.725,booking="source exit date",source_slippage_preserved=True)
    with pinned_modules(runtime):
        with (scratch / "g24.pkl").open("rb") as f:
            g = pickle.load(f)
        with (scratch / "ge.pkl").open("rb") as f:
            ge = pickle.load(f)
    t = read("twin_continuation/trades.csv")
    t["entry_stamp"] = [fill_stamp(g,r.entry_date,int(r.entry_time_ct)//100*60+int(r.entry_time_ct)%100,r.entry,
                                   phase="open" if r.setup=="MO" else None) for r in t.itertuples()]
    t["exit_stamp"] = [fill_stamp(g,r.date,int(r.exit_time_ct)//100*60+int(r.exit_time_ct)%100,r.exit) for r in t.itertuples()]
    t = closed_window(t)
    frame["TwinContinuation"], marks, money = marked_ledger(g, t, days, fee=fee, entry_slip=.5, name="TwinContinuation")
    manifest["pieces"]["TwinContinuation"] = money; mark_tables.append(marks)
    t = read("kusho/python_trades_v9_rolladj.csv")
    # Source exit_date maps Sunday exits to Monday; fm/xm retain actual chronology.
    t["entry_stamp"] = [fill_stamp(g,r.date,int(r.fm)%1440,r.entry) for r in t.itertuples()]
    exit_day = pd.to_datetime(t.date) + pd.to_timedelta(t.xm // 1440 - t.fm // 1440, unit="D")
    t["exit_stamp"] = [fill_stamp(g,d,int(r.xm)%1440,r.exit+(0.25*r.side if r.kind!="target" else 0.),
                                  phase="open" if r.kind=="eod" else None) for d,r in zip(exit_day,t.itertuples())]
    t = closed_window(t)
    date_rows = {pd.Timestamp(d).normalize(): i for i, d in enumerate(g.ts)}
    # Roll membership follows the source's inclusive close-stamped addresses,
    # independently of wall-clock open/intrabar timestamps used for sessions.
    t["entry_address"] = [date_rows[pd.Timestamp(r.date).normalize()]*1440+int(r.fm)%1440 for r in t.itertuples()]
    t["exit_address"] = [date_rows[pd.Timestamp(r.date).normalize()+pd.Timedelta(days=int(r.xm)//1440-int(r.fm)//1440)]*1440+int(r.xm)%1440 for r in t.itertuples()]
    frame["Kusho"], marks, money = marked_ledger(g, t, days, fee=fee, jumps=roll_jump_series(g, "NQ", runtime), name="Kusho")
    manifest["pieces"]["Kusho"] = money; mark_tables.append(marks)
    frame["S30"] = 0.
    for symbol, grid, pv in (("NQ", g, 2.), ("ES", ge, 5.)):
        t = read("s30_ibs/python_trades_" + symbol + ".csv")
        t["entry_stamp"] = pd.to_datetime(t.date) + pd.Timedelta(hours=15)
        t["exit_stamp"] = pd.to_datetime(t.exit_date) + pd.Timedelta(hours=15)
        t = closed_window(t)
        t["entry"], t["exit"] = t.e_px, t.x_px  # already contain the source's market slippage
        date_rows = {pd.Timestamp(d).normalize(): i for i, d in enumerate(grid.ts)}
        t["entry_address"] = [date_rows[x.normalize()] * 1440 + 901 for x in t.entry_stamp]
        t["exit_address"] = [date_rows[x.normalize()] * 1440 + 901 for x in t.exit_stamp]
        x, marks, money = marked_ledger(grid, t, days, fee=fee, point_value=pv, jumps=roll_jump_series(grid, symbol, runtime), name="S30_" + symbol)
        frame["S30"] += x
        manifest["pieces"]["S30_" + symbol] = money; mark_tables.append(marks)
    if set(frame) != set(COLUMNS) or not np.isfinite(frame.to_numpy()).all():
        raise ValueError("Corrected baseline is not the complete finite17-piece roster")
    return frame.loc[:, list(COLUMNS)], pd.concat(mark_tables, ignore_index=True), manifest


def histories(length, n=N, horizon=HORIZON, block=BLOCK, seed=SEED):
    if length < block:
        raise ValueError("Insufficient cohort for frozen20-day blocks")
    rng = np.random.default_rng(seed)
    starts = rng.integers(0, length, (n, int(np.ceil(horizon / block))))
    return ((starts[:, :, None] + np.arange(block)) % length).reshape(n, -1)[:, :horizon]


def simulate_daily(values, idx):
    daily = np.asarray(values, float)[idx]
    if not np.isfinite(daily).all():
        raise ValueError("Unknown values block personal Monte Carlo")
    eq = daily.cumsum(axis=1)
    peak = np.maximum.accumulate(np.c_[np.zeros(len(eq)), eq], axis=1)[:, 1:]
    dd = (peak - eq).max(axis=1)
    sd = daily.std(axis=1, ddof=1)
    sharpe = np.divide(daily.mean(axis=1) * np.sqrt(252), sd, out=np.full(len(sd), np.nan), where=sd > 0)
    return dict(profit=eq[:, -1], dd=dd, sharpe=sharpe)


def annual_interval(delta):
    """Paired90% finite-history CI; circular20-day blocks over full cohort."""
    delta = np.asarray(delta, float)
    ix = histories(len(delta), horizon=len(delta))
    return np.quantile(delta[ix].mean(axis=1) * 252, [.05, .95])


def paired_mean_interval(values, n=N, seed=SEED):
    """90% precision CI for paired per-history outcomes, conditional on history."""
    values=np.asarray(values,float)
    rng=np.random.default_rng(seed)
    samples=np.empty(n)
    for start in range(0,n,100):
        size=min(100,n-start)
        ix=rng.integers(0,len(values),(size,len(values)))
        samples[start:start+size]=values[ix].mean(axis=1)
    return np.quantile(samples,[.05,.95])


def joint_losses(frame,candidate):
    rows=[]
    for period,start in (("2018_plus","2018-01-01"),("2023_plus","2023-01-01")):
        mask=frame.index>=start
        c=candidate[mask]
        for group,(quantities,_) in fixed_ladders().items():
            b=sum(frame[k][mask]*q for k,q in quantities.items())
            joint=(b<0)&(c<0)
            rows.append(dict(period=period,group=group,days=len(b),candidate_correlation=b.corr(c),
                candidate_covariance=b.cov(c),baseline_negative_days=int((b<0).sum()),
                candidate_negative_days=int((c<0).sum()),joint_negative_days=int(joint.sum()),
                candidate_sum_on_baseline_negative=float(c[b<0].sum()),candidate_sum_on_joint_negative=float(c[joint].sum()),
                baseline_sum_on_joint_negative=float(b[joint].sum()),
                scope="synchronized16CTdaily PnL; no assertion of offset before an intraday margin event"))
    return pd.DataFrame(rows)


def max_dd(x):
    e = np.r_[0., np.asarray(x, float).cumsum()]
    return float((np.maximum.accumulate(e) - e).max())


def historical_metrics(x):
    x = np.asarray(x, float)
    profit, loss = x[x > 0].sum(), -x[x < 0].sum()
    downside = np.sqrt(np.mean(np.minimum(x, 0.) ** 2))
    dd, ann = max_dd(x), x.mean() * 252
    eq = np.r_[0., x.cumsum()]
    dollar_ulcer = np.sqrt(np.mean((np.maximum.accumulate(eq) - eq) ** 2))
    return dict(days=len(x), total=x.sum(), annual=ann, sharpe=x.mean()/x.std(ddof=1)*np.sqrt(252) if x.std(ddof=1)>0 else np.nan,
                sortino=x.mean()/downside*np.sqrt(252) if downside else np.nan,
                pf=profit/loss if loss else np.nan, max_dd=dd, calmar=ann/dd if dd else np.nan,
                ulcer_dollars=dollar_ulcer, metrics_unit="daily portfolio observations; not per-trade t/PF")


def benchmark(frame, candidate, *, auth, audit, fee, out=OUT):
    require_authorization(auth)
    reject_incomplete_candidate(pd.DataFrame(columns=["date", "net"]), audit)
    out = Path(out); out.mkdir(parents=True, exist_ok=True)
    plans, metadata = configurations(frame, candidate)
    days = validate_days(frame.index)
    rows, effects, historical = [], [], []
    ci_cache = {}
    periods = {"2018_22": ("2018-01-01", "2023-01-01"), "2023_plus": ("2023-01-01", "2100-01-01"),
               "2018_plus": ("2018-01-01", "2100-01-01")}
    periods.update({str(y): (str(y)+"-01-01", str(y+1)+"-01-01") for y in sorted(days.year.unique())})
    for name, x in plans.items():
        for period, (lo, hi) in periods.items():
            sub = x[(days >= lo) & (days < hi)]
            if len(sub):
                historical.append(dict(config=name, period=period, fee=fee, **historical_metrics(sub)))
    for cohort, start in (("2018_plus", "2018-01-01"), ("2023_plus", "2023-01-01")):
        mask = days >= start; ix = histories(int(mask.sum()))
        np.save(out / (cohort + "_paired_indices.npy"), ix)
        results, summaries = {}, {}
        for name, x in plans.items():
            result = results[name] = simulate_daily(x[mask], ix)
            pnl, dd, sp = result["profit"], result["dd"], result["sharpe"]
            dd95 = float(np.quantile(dd, .95))
            summary = dict(cohort=cohort, config=name, fee=fee, group=metadata[name]["group"], allocation=metadata[name]["allocation"],
                           pnl_mean=pnl.mean(), pnl_p5=np.quantile(pnl,.05), pnl_p50=np.median(pnl), pnl_p95=np.quantile(pnl,.95),
                           p_losing_year=np.mean(pnl <= 0), dd_p50=np.median(dd), dd_p95=dd95,
                           capital_20pct=dd95/.2, return_over_p95dd=np.median(pnl)/dd95 if dd95 else np.nan,
                           sharpe_p50=np.nanmedian(sp), histories=N, horizon=HORIZON, seed=SEED, block=BLOCK,
                           replacement_applicable=metadata[name]["replacement_applicable"])
            summaries[name] = summary; rows.append(summary)
        for name, result in results.items():
            group = metadata[name]["group"]
            refs = [group + "__BASE"]
            if metadata[name]["replacement_applicable"]:
                refs.append(group + "__EMPTY_VB")
            for reference in refs:
                base = results[reference]
                delta = (plans[name][mask] - plans[reference][mask]).to_numpy()
                ci_key = hashlib.sha256(delta.tobytes()).hexdigest()
                if ci_key not in ci_cache:
                    ci_cache[ci_key] = annual_interval(delta)
                lo, hi = ci_cache[ci_key]
                pr = summaries[name]["return_over_p95dd"]
                br = summaries[reference]["return_over_p95dd"]
                # This is the distribution of paired annual outcomes, not a
                # confidence interval for a future edge or MC mean precision.
                dd_reduction = base["dd"] - result["dd"]
                dlo, dhi = np.quantile(dd_reduction, [.05,.95])
                ddlo,ddhi=paired_mean_interval(dd_reduction)
                annual_mean_change=float((result["profit"]-base["profit"]).mean())
                effect = dict(cohort=cohort, config=name, reference=reference, fee=fee,
                              historical_annual_delta=delta.mean()*252, annual_delta_ci90_lo=lo, annual_delta_ci90_hi=hi,
                              annual_ci_scope="finite historical mean; circular20-day full-cohort paired bootstrap",
                              paired_year_profit_delta_p5=np.quantile(result["profit"]-base["profit"],.05),
                              paired_year_profit_delta_p50=np.median(result["profit"]-base["profit"]),
                              paired_year_profit_delta_p95=np.quantile(result["profit"]-base["profit"],.95),
                              paired_year_dd_reduction_p5=dlo, paired_year_dd_reduction_p95=dhi,
                              dd_reduction_scope="paired annual-outcome quantiles; not a finite-history confidence interval",
                              mean_per_history_dd_reduction=float(dd_reduction.mean()),
                              mean_per_history_dd_reduction_ci90_lo=ddlo,mean_per_history_dd_reduction_ci90_hi=ddhi,
                              mean_per_history_dd_reduction_ci_scope="paired bootstrap over1000 MC histories; conditional simulation precision",
                              paired_annual_return_mean_change=annual_mean_change,
                              sharpe_p50_delta=summaries[name]["sharpe_p50"]-summaries[reference]["sharpe_p50"],
                              return_over_p95dd_delta=pr-br, dd_p95_delta=summaries[name]["dd_p95"]-summaries[reference]["dd_p95"],
                              capital_20pct_delta=summaries[name]["capital_20pct"]-summaries[reference]["capital_20pct"],
                              joint_profit_risk_criterion=bool(lo>0 and pr>=br),
                              joint_dd_return_criterion=bool(ddlo>0 and annual_mean_change>=0),
                              no_automatic_rejection_of_user_selected_S30_risk_tradeoff=True)
                effects.append(effect)
        np.savez_compressed(out / (cohort + "_paired_paths.npz"), **{name+"__"+kind: value for name,r in results.items() for kind,value in r.items()})
    pd.DataFrame(rows).to_csv(out / "mc_summary.csv", index=False)
    effect_frame=pd.DataFrame(effects)
    effect_frame.to_csv(out / "paired_effects.csv", index=False)
    decisions=[]
    for (cohort,name),sub in effect_frame.groupby(["cohort","config"],sort=False):
        m=metadata[name];label=m["allocation"]
        applicable=label=="ADD_S03" or (label=="REPLACE_VB" and m["replacement_applicable"])
        references=[m["group"]+"__BASE"]
        if label=="REPLACE_VB" and m["replacement_applicable"]:
            references.append(m["group"]+"__EMPTY_VB")
        compared=sub[sub.reference.isin(references)]
        satisfied=bool(applicable and len(compared)==len(references) and
                       (compared.joint_profit_risk_criterion|compared.joint_dd_return_criterion).all())
        decisions.append(dict(cohort=cohort,config=name,fee=fee,applicable=applicable,
            required_references=references,demonstrated_material_place=satisfied,
            interpretation="frozen statistical comparison only; no live or automatic allocation change"))
    pd.DataFrame(decisions).to_csv(out/"placement_criteria.csv",index=False)
    pd.DataFrame(historical).to_csv(out / "historical_summary.csv", index=False)
    joint_losses(frame,candidate).to_csv(out/"joint_losses.csv",index=False)
    pd.DataFrame(plans).to_csv(out / "daily_portfolios.csv", index_label="date")
    dump(out / "manifest.json", dict(reference=PIN, authorization=auth.__dict__, fee=fee, configurations=metadata,
         script_sha256=sha(__file__), n=N, horizon=HORIZON, seed=SEED, block=BLOCK, block_convention="circular",
         annual_CI=.90, source_manifest_sha256=sha(SOURCES / "manifest.json"), limitations=LIMITATIONS,
         candidate_audit=audit, decision="Report all11 fixed ladder rows; no winning quantity selection"))
    return pd.DataFrame(rows), effect_frame, pd.DataFrame(historical)


def fixtures():
    """Invented values only; validates cost, chronology, unknown-data and ladder invariants."""
    from types import SimpleNamespace
    days = pd.DatetimeIndex(["2026-10-02", "2026-10-05"])
    g = SimpleNamespace(ts=pd.date_range(days[0], days[-1], freq="D").to_numpy(), c=np.full((4,1440),np.nan),o=np.full((4,1440),100.))
    g.c[0,960], g.c[0,961] = 105., 999.
    t = pd.DataFrame([dict(entry_stamp="2026-10-02 09:00", exit_stamp="2026-10-05 09:00", entry=100., exit=110., side=1, net=182.75)])
    x, marks, money = marked_ledger(g,t,days,fee=1.04,entry_slip=.5)
    np.testing.assert_allclose(x,[8.46,9.5],atol=1e-12)
    assert marks.iloc[0].price == 105. and marks.iloc[0].mark_j == 960
    xstress,_,_ = marked_ledger(g,t,days,fee=1.24,entry_slip=.5)
    np.testing.assert_allclose(xstress-x,[-.2,0.],atol=1e-12)
    assert session_index(days,fill_stamp(g,days[0],961,100.))==0
    assert session_index(days,fill_stamp(g,days[0],961,99.))==1
    assert session_index(days,fill_stamp(g,days[0],960,99.,phase="close"))==0
    # A roll basis is removed in the same daily interval in which it arrives.
    t = pd.DataFrame([dict(entry_stamp="2026-10-02 09:00", exit_stamp="2026-10-05 09:00", entry=100., exit=210., side=1, net=192.75,
                         entry_address=540, exit_address=3*1440+540)])
    g.c[0,960] = 205.
    x,_,_ = marked_ledger(g,t,days,fee=1.04,jumps={900:100.})
    np.testing.assert_allclose(x,[8.96,10.],atol=1e-12)
    try:
        session_index(days,pd.Timestamp("2026-10-05 16:01"))
    except ValueError:
        pass
    else:
        raise AssertionError("Future exit was clamped")
    bad = dict(complete=True,personal_path_eligible=True,all_native_dates_covered=True,calendar_unknown_native_minutes=0,
               unknown_held_minutes=0,unknown_held_trades=0,censored_trades=1,unresolved_positions=0,unpriced_positions=0)
    try:
        candidate_daily(pd.DataFrame(columns=["date","net"]),days,bad)
    except ValueError:
        pass
    else:
        raise AssertionError("Censored omitted trade did not block Monte Carlo")
    good = {**bad,"censored_trades":0}
    t = pd.DataFrame(dict(date=[days[0],days[0]],net=[-17.25,182.75]))
    x = candidate_daily(t,days,good)
    np.testing.assert_allclose(x.iloc[0],t.net.sum()/10+2*.725-2*1.04)
    frame = pd.DataFrame({k:np.arange(25,dtype=float) for k in COLUMNS},index=pd.date_range("2020-01-01",periods=25))
    cand = pd.Series(np.ones(25),index=frame.index)
    plans, meta = configurations(frame,cand)
    assert len(plans)==44 and len(fixed_ladders())==11
    for group,units in (("A",1),("CORE2_S30_1",2),("CORE4_S30_1",4),("CORE10_S30_3",10)):
        np.testing.assert_allclose(plans[group+"__ADD_S03"]-plans[group+"__BASE"],units)
    for group in ("A","B"):
        np.testing.assert_array_equal(plans[group+"__BASE"],plans[group+"__REPLACE_VB"])
        assert not meta[group+"__REPLACE_VB"]["replacement_applicable"]
    ix=histories(25,n=4,horizon=25)
    assert ix.shape==(4,25) and ((ix>=0)&(ix<25)).all()
    r=simulate_daily(np.zeros(25),ix)
    np.testing.assert_array_equal(r["dd"],0.)
    assert max_dd([-10.,5.])==10.
    return dict(invented_data_only=True,exact_source_net_fee_repricing=True,every_reentry_pays_fee=True,
                fee_reserved_at_entry=True,no_after16_price_peek=True,roll_removed_at_actual_interval=True,
                no_future_exit_clamp=True,censored_candidate_blocks_all_personal_MC=True,
                complete17_pieces_11_ladder_rows_44_choices=True,scaled_add_units_fixed=True,
                A_B_replacement_NA=True,circular_paired_indices=True,starting_zero_drawdown_included=True)


def write_blocked_manifest(candidate_gate, out=OUT):
    """Record unrun destinations using source hashes; calculate no historical paths."""
    candidate_gate=Path(candidate_gate).resolve()
    gate=json.loads(candidate_gate.read_text())
    if (gate.get("account_run_authorized") is not False or gate.get("allow_personal") is not False
            or not str(gate.get("status","")).upper().startswith("BLOCKED")):
        raise PermissionError("Blocked-only requires an explicit blocked candidate gate denying personal runs")
    prereg=ROOT/"agents/codex/plans/s03_noisearea.md"
    prereg_sha=sha(prereg)
    linked=[gate[k] for k in ("prereg_sha256","root_prereg_sha256","preregistration_sha256") if k in gate]
    if isinstance(gate.get("preregistration"),dict) and "sha256" in gate["preregistration"]:
        linked.append(gate["preregistration"]["sha256"])
    if not linked or any(value!=prereg_sha for value in linked):
        raise PermissionError("Blocked candidate gate must match this S03 preregistration SHA256")
    source_manifest=verify_sources()
    fixture=fixtures()
    rows=[]
    for group,(quantity,add_unit) in fixed_ladders().items():
        vb=int(quantity.get("VaultBreak",0))
        empty={k:q for k,q in quantity.items() if k!="VaultBreak"}
        choices=dict(BASE=dict(quantity),ADD_S03={**quantity,"S03":add_unit},EMPTY_VB=empty,
                     REPLACE_VB={**empty,**({"S03":vb} if vb else {})})
        for label,allocation in choices.items():
            rows.append(dict(config=group+"__"+label,ladder=group,allocation=label,
                quantities=allocation,add_s03_units=add_unit,replace_s03_units=vb,
                replacement_applicable=bool(vb),placement_applicable=label=="ADD_S03" or (label=="REPLACE_VB" and bool(vb)),
                status="BLOCKED_DATA",performance_computed=False,baseline_return_runs=0,candidate_return_runs=0,monte_carlo_runs=0,
                condition="Root candidate gate denies account/personal paths; no missing values dropped or imputed"))
    if len(rows)!=44 or len(fixed_ladders())!=11:
        raise AssertionError("Frozen blocked inventory must retain11 ladder rows and44 choices")
    manifest=dict(status="BLOCKED_DATA",scope="Current17-piece personal portfolio; all11 frozen ladder rows",
        account_run_authorized=False,allow_personal=False,baseline_return_runs=0,candidate_return_runs=0,monte_carlo_runs=0,
        historical_performance_computed=False,performance_gain_claim=None,baseline_source_pin=PIN,
        baseline_pieces=list(COLUMNS),baseline_piece_count=len(COLUMNS),ladder_rows=11,fixed_configurations=44,
        configurations=rows,planned_fees=list(FEES),planned_cohorts=["2018_plus","2023_plus"],
        planned_bootstrap=dict(histories=N,block_days=BLOCK,horizon_days=HORIZON,seed=SEED,convention="circular"),
        source_data_condition=gate,candidate_gate_path=str(candidate_gate.relative_to(ROOT)) if candidate_gate.is_relative_to(ROOT) else str(candidate_gate),
        candidate_gate_sha256=sha(candidate_gate),preregistration_path="agents/codex/plans/s03_noisearea.md",
        preregistration_sha256=prereg_sha,source_manifest_sha256=sha(SOURCES/"manifest.json"),
        source_inventory=source_manifest,script_sha256=sha(__file__),fixtures=fixture,
        fixture_scope="Invented prices, fee/mark arithmetic, circular index and allocation invariants only; no observed baseline or candidate returns",
        no_raw_baseline_csv_exported=True,limitations=LIMITATIONS,
        conclusion="Personal portfolio gain and capital effects are unassessed because the preregistered data gate failed")
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    dump(out/"blocked_manifest.json",manifest)
    compact=[{**r,"quantities":json.dumps(r["quantities"],sort_keys=True)} for r in rows]
    pd.DataFrame(compact).to_csv(out/"blocked_configurations.csv",index=False)
    return manifest


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("command",nargs="?",choices=("fixtures","prepare","verify","inventory","run"))
    ap.add_argument("--blocked-only",action="store_true",help="Write the unrun frozen portfolio inventory from an explicit blocking gate")
    ap.add_argument("--candidate-gate",help="Root candidate gate JSON; required with --blocked-only")
    ap.add_argument("--source-repo",default=str(ROOT))
    ap.add_argument("--scratch",default=str(ROOT/"scratch_data"))
    ap.add_argument("--prereg"); ap.add_argument("--prereg-sha256"); ap.add_argument("--design-gate")
    ap.add_argument("--ledger"); ap.add_argument("--audit"); ap.add_argument("--counts"); ap.add_argument("--commission-credit")
    ap.add_argument("--plan-native-daily")
    ap.add_argument("--terminal-inventory"); ap.add_argument("--out",default=str(OUT))
    args=ap.parse_args()
    if args.blocked_only:
        if not args.candidate_gate:
            ap.error("--blocked-only requires --candidate-gate")
        manifest=write_blocked_manifest(args.candidate_gate,args.out)
        print(json.dumps({k:manifest[k] for k in ("status","baseline_piece_count","ladder_rows","fixed_configurations","baseline_return_runs","candidate_return_runs","monte_carlo_runs")}))
        return
    if args.command is None:
        ap.error("choose a command or --blocked-only")
    if args.command=="fixtures":
        print(json.dumps(fixtures(),indent=2)); return
    if args.command=="prepare":
        m=prepare_sources(args.source_repo); print(json.dumps(dict(reference=m["reference"],files=len(m["files"])))); return
    if args.command=="verify":
        m=verify_sources(); print(json.dumps(dict(reference=m["reference"],files=len(m["files"]),ladders=fixed_ladders()))); return
    if args.command=="inventory":
        print(json.dumps(baseline_source_inventory(),indent=2));return
    required=("prereg","prereg_sha256","design_gate","ledger","audit","counts","commission_credit","plan_native_daily")
    for key in required:
        if not getattr(args,key):
            ap.error("run requires --"+key.replace("_","-"))
    auth=authorize(args.prereg,args.prereg_sha256,args.design_gate)
    fixture=fixtures()
    out=Path(args.out); out.mkdir(parents=True,exist_ok=True)
    audit=json.loads(Path(args.audit).read_text()); ledger=pd.read_csv(args.ledger)
    reject_incomplete_candidate(ledger,audit)  # before any baseline path calculation
    counts=pd.read_csv(args.counts,index_col=0,parse_dates=True)
    credits=pd.read_csv(args.commission_credit,index_col=0,parse_dates=True)
    plan_daily=pd.read_csv(args.plan_native_daily,index_col=0,parse_dates=True)
    terminal=json.loads(Path(args.terminal_inventory).read_text()) if args.terminal_inventory else baseline_source_inventory()
    dump(out/"baseline_source_inventory.json",terminal)
    reference,sources=load_reference(auth=auth,scratch=args.scratch)
    reference.to_csv(out/"canonical_reference17.csv",index_label="date")
    dump(out/"sources.json",sources)
    for fee in FEES:
        dest=out/("fee_"+str(fee)); dest.mkdir(exist_ok=True)
        baseline,marks,manifest=corrected_baseline(auth=auth,scratch=args.scratch,counts=counts,commission_credit=credits,plan_native_daily=plan_daily,terminal_inventory=terminal,fee=fee)
        candidate=candidate_daily(ledger,baseline.index,audit,fee)
        baseline.to_csv(dest/"baseline17.csv",index_label="date")
        (baseline-reference).to_csv(dest/"accounting_changes_vs_canonical.csv",index_label="date")
        marks.to_csv(dest/"baseline_marks.csv",index=False)
        candidate.to_csv(dest/"candidate_daily.csv",index_label="date")
        manifest.update(fixtures=fixture,ledger_sha256=sha(args.ledger),audit_sha256=sha(args.audit),counts_sha256=sha(args.counts),commission_credit_sha256=sha(args.commission_credit),plan_native_daily_sha256=sha(args.plan_native_daily),terminal_inventory_sha256=sha(out/"baseline_source_inventory.json"))
        dump(dest/"accounting_manifest.json",manifest)
        benchmark(baseline,candidate,auth=auth,audit=audit,fee=fee,out=dest)
    print("Current17 personal benchmark complete at real and stress fees")


if __name__=="__main__":
    main()
