"""Pure evaluation-policy selection and paired uncertainty helpers.

No data files are read, no trades are generated and no account replay is run.
Run this module with --selftest for synthetic observations only.

Design nomination is descriptive selection on already observed 2018--22 history,
not economic verification or proof of global optimality. Candidate definitions,
the common start calendar, input admission and the search budget must be frozen
by the caller before outcomes. All rates retain expired and unknown starts.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from collections import defaultdict
from collections.abc import Mapping
from statistics import median

import numpy as np

STATUSES = ("pass", "fail", "expire", "unknown")
DESIGN_YEARS = (2018, 2019, 2020, 2021, 2022)
ALIASES = {
    "pass": "pass", "passed": "pass", "success": "pass",
    "fail": "fail", "failed": "fail", "failure": "fail", "blown": "fail", "breach": "fail",
    "expire": "expire", "expired": "expire", "timeout": "expire", "time_out": "expire",
    "timed_out": "expire", "time": "expire",
    "unknown": "unknown", "missing": "unknown", "unresolved": "unknown", "incomplete": "unknown",
    "open": "unknown", "still_open": "unknown", "unfinished": "unknown", "censored": "unknown", "": "unknown",
}


def _status(value, status_map=None):
    if status_map is not None and value in status_map:
        value = status_map[value]
    if value is None:
        return "unknown"
    if not isinstance(value, str):
        raise ValueError("Numeric status codes need an explicit status_map; no code meaning is inferred.")
    key = value.strip().lower().replace("-", "_").replace(" ", "_")
    if key not in ALIASES:
        raise ValueError(f"Unrecognized outcome status: {value!r}")
    return ALIASES[key]


def _start_id(value):
    if value is None:
        return None
    if isinstance(value, tuple) and len(value) == 2 and value[0] in ("number", "text"):
        # Internal normalized records are also accepted by public summary helpers.
        return value
    if isinstance(value, (int, np.integer)) and not isinstance(value, (bool, np.bool_)):
        return ("number", int(value))
    if isinstance(value, (float, np.floating)):
        if not np.isfinite(value):
            raise ValueError("Start ID is not finite")
        return ("number", float(value))
    return ("text", str(value))


def _records(outcomes, status_key="status", time_key="time", start_key="start", status_map=None):
    if hasattr(outcomes, "to_dict") and not isinstance(outcomes, Mapping):
        outcomes = outcomes.to_dict("records")
    elif isinstance(outcomes, np.ndarray) and outcomes.dtype.names:
        outcomes = [{key: row[key] for key in outcomes.dtype.names} for row in outcomes]
    result = []
    for item in outcomes:
        if isinstance(item, Mapping):
            flags = []
            for name in STATUSES:
                if name in item:
                    value = item[name]
                    if value not in (0, 1, False, True):
                        raise ValueError("Outcome indicator flags must be boolean/zero/one")
                    if bool(value):
                        flags.append(name)
            if len(flags) > 1:
                raise ValueError("Contradictory outcome flags")
            if status_key in item:
                status = _status(item[status_key], status_map)
                if any(name in item for name in STATUSES) and flags != [status]:
                    raise ValueError("Status disagrees with outcome flags")
            else:
                status = flags[0] if flags else "unknown"
            time = item.get(time_key, item.get("days", item.get("trading_days")))
            start = item.get(start_key)
            if start is None:
                start = next((item[k] for k in ("start_id", "start_date", "start_index") if k in item), None)
        elif isinstance(item, (tuple, list)) and len(item) == 2:
            status, time = _status(item[0], status_map), item[1]
            start = None
        else:
            status, time, start = _status(item, status_map), None, None
        if time is not None:
            time = float(time)
            if not np.isfinite(time) or time < 0:
                raise ValueError("Outcome time must be finite and nonnegative, or None")
        result.append(dict(status=status, time=time, start_id=_start_id(start)))
    starts = [r["start_id"] for r in result]
    if any(x is not None for x in starts):
        if any(x is None for x in starts):
            raise ValueError("A partial start calendar cannot be silently completed")
        if len(starts) != len(set(starts)):
            raise ValueError("Duplicate start IDs")
        if len({x[0] for x in starts}) > 1:
            raise ValueError("Mixed numeric/text start IDs are not a certified chronology")
    return result


def _calendar(records):
    ids = [r["start_id"] for r in records]
    if not ids or any(x is None for x in ids):
        return None, None
    ids = sorted(ids)
    encoded = json.dumps(ids, separators=(",", ":"), ensure_ascii=True).encode()
    return hashlib.sha256(encoded).hexdigest(), ids


def summarize_outcomes(outcomes, *, status_key="status", time_key="time", start_key="start",
                       candidate_id=None, account=None, year=None, status_map=None):
    """Summarize final outcomes without hiding expiry/censoring in denominators.

    Input accepts status strings, (status,time) tuples, mapping records, structured
    arrays or a dataframe. None/open/unfinished are UNKNOWN; explicit timeout/time
    means EXPIRE. Numeric codes require status_map. Time statistics are conditional
    on actual passing starts, never all-account funding speed. A calendar fingerprint
    is returned only when every observation supplies a unique start ID.
    """
    records = _records(outcomes, status_key, time_key, start_key, status_map)
    n = len(records)
    counts = {s: sum(r["status"] == s for r in records) for s in STATUSES}
    rates = {s: counts[s] / n if n else None for s in STATUSES}
    pass_times = [r["time"] for r in records if r["status"] == "pass" and r["time"] is not None]
    calendar_hash, ids = _calendar(records)
    result = dict(n=n, counts=counts, rates=rates,
        pass_lower=rates["pass"], pass_upper=(counts["pass"] + counts["unknown"]) / n if n else None,
        fail_lower=rates["fail"], fail_upper=(counts["fail"] + counts["unknown"]) / n if n else None,
        expire_rate=rates["expire"], unknown_share=rates["unknown"],
        conditional_pass_median_time=median(pass_times) if pass_times else None,
        conditional_pass_mean_time=float(np.mean(pass_times)) if pass_times else None,
        pass_times=pass_times, passed_with_time=len(pass_times),
        pass_time_coverage=len(pass_times) / counts["pass"] if counts["pass"] else None,
        calendar_hash=calendar_hash, start_ids=ids,
        interpretation="Unknown stays separate from observed failures. Bounds allow unknown outcomes to be pass/fail.")
    for k, value in (("candidate_id", candidate_id), ("account", account), ("year", year)):
        if value is not None:
            result[k] = value
    return result


def _counts(row):
    values = row.get("counts", row.get("status_counts"))
    if values is None:
        values = {}
        for s in STATUSES:
            keys = (s + "_count", "n_" + s, s + "es" if s == "pass" else s + "s", s)
            found = next((row[k] for k in keys if k in row), None)
            if found is None:
                raise ValueError("Annual rows need all four outcome counts, not rounded rates")
            values[s] = found
    clean = {}
    for s in STATUSES:
        value = values.get(s)
        if value is None or not np.isfinite(value) or int(value) != value or value < 0:
            raise ValueError(f"Invalid {s} count")
        clean[s] = int(value)
    raw_n = row.get("n", sum(clean.values()))
    if not np.isfinite(raw_n) or int(raw_n) != raw_n:
        raise ValueError("Denominator must be a finite integer")
    n = int(raw_n)
    if n < 0 or n != sum(clean.values()):
        raise ValueError("Counts must sum exactly to the unconditional denominator")
    return n, clean


def _metadata(metadata, account, candidate):
    if isinstance(metadata, Mapping):
        for key in ((account, candidate), candidate):
            if key in metadata:
                return dict(metadata[key])
        if account in metadata and candidate in metadata[account]:
            return dict(metadata[account][candidate])
    else:
        hits = [m for m in metadata if str(m.get("candidate_id")) == candidate and str(m.get("account", account)) == account]
        if len(hits) == 1:
            return dict(hits[0])
    raise ValueError(f"Candidate metadata missing for {account}/{candidate}")


def _dominates(a, b):
    # Four explicit objectives retain the speed/survival/expiry tradeoff. Fast time
    # is conditional on success and is labeled as such throughout the interface.
    at = a["conditional_pass_median_time"]
    bt = b["conditional_pass_median_time"]
    av = (-a["pass_score"], a["fail_upper"], a["expire_rate"], at if at is not None else math.inf)
    bv = (-b["pass_score"], b["fail_upper"], b["expire_rate"], bt if bt is not None else math.inf)
    return all(x <= y + 1e-12 for x, y in zip(av, bv)) and any(x < y - 1e-12 for x, y in zip(av, bv))


def _frontier(candidates):
    return [c for c in candidates if not any(_dominates(other, c) for other in candidates if other is not c)]


def _objective(c, role):
    speed = c["conditional_pass_median_time"]
    speed = speed if speed is not None else math.inf
    if role == "risk_first":
        return (c["fail_upper"], -c["pass_score"], c["expire_rate"], speed, c["candidate_id"])
    if role == "fast_pass":
        return (speed, -c["pass_score"], c["fail_upper"], c["candidate_id"])
    return (-c["pass_score"], c["fail_upper"], c["expire_rate"], speed, c["candidate_id"])


def _family_medoids(pool, normalization_pool, role, top_fraction, radius):
    groups = defaultdict(list)
    all_groups = defaultdict(list)
    for c in normalization_pool:
        all_groups[c["family_group"]].append(c)
    for c in pool:
        groups[c["family_group"]].append(c)
    medoids, audits = [], []
    for group in sorted(groups):
        members = sorted(groups[group], key=lambda c: _objective(c, role))
        reference = all_groups[group]
        keys = sorted(reference[0]["exposure_vector"])
        if any(sorted(c["exposure_vector"]) != keys for c in reference):
            raise ValueError("All candidates in a book/family need explicit matching vector keys; missing is not zero")
        x = np.array([[c["exposure_vector"][k] for k in keys] for c in reference], dtype=float)
        low, high = x.min(0), x.max(0)
        scale = np.where(high > low, high - low, 1.)
        target_n = max(1, math.ceil(len(members) * top_fraction))
        # Include primary-objective ties at the cutoff, so candidate-ID order does
        # not remove equally good neighborhood points before medoid selection.
        cutoff = _objective(members[target_n - 1], role)[0]
        top = [c for c in members if _objective(c, role)[0] <= cutoff + 1e-12]
        z = (np.array([[c["exposure_vector"][k] for k in keys] for c in top]) - low) / scale
        dist = np.sqrt(np.mean((z[:, None] - z[None, :]) ** 2, axis=2)) if keys else np.zeros((len(top), len(top)))
        unseen, components = set(range(len(top))), []
        while unseen:
            stack = [min(unseen)]; component = []
            while stack:
                i = stack.pop()
                if i not in unseen:
                    continue
                unseen.remove(i); component.append(i)
                stack.extend(j for j in sorted(unseen) if dist[i, j] <= radius + 1e-12)
            components.append(sorted(component))
        components.sort(key=lambda ix: (-len(ix), min(_objective(top[i], role) for i in ix), tuple(top[i]["candidate_id"] for i in ix)))
        chosen = components[0]
        mean_distance = {i: float(dist[i, chosen].mean()) for i in chosen}
        smallest = min(mean_distance.values())
        ties = [i for i in chosen if abs(mean_distance[i] - smallest) <= 1e-12]
        selected = min(ties, key=lambda i: _objective(top[i], role))
        representative = dict(top[selected])
        representative["medoid_role"] = role
        representative["neighborhood_members"] = [top[i]["candidate_id"] for i in chosen]
        representative["neighborhood_supported"] = len(chosen) >= 2
        representative["medoid_mean_normalized_distance"] = mean_distance[selected]
        medoids.append(representative)
        audits.append(dict(family_group=group, role=role, candidate_count=len(members),
            top_count=len(top), top_fraction=top_fraction, cutoff=cutoff, normalized_rms_radius=radius,
            vector_keys=keys, normalization_low=low.tolist(), normalization_high=high.tolist(),
            components=[[top[i]["candidate_id"] for i in ix] for ix in components],
            medoid=representative["candidate_id"], neighborhood_supported=len(chosen) >= 2))
    return sorted(medoids, key=lambda c: _objective(c, role)), audits


def rank_design(summary_rows, *, candidate_metadata, max_nominees=3, top_fraction=.20,
                pass_tolerance=.02, max_unknown_share=.01, neighborhood_radius=.35,
                design_years=DESIGN_YEARS, min_fast_passes=5):
    """Nominate <=3 policies/account from finite, predeclared candidate families.

    Metadata: family_id, exposure_vector (all explicit finite numeric keys), optional
    book_id and eligible. Without book_id, differing nonzero supports are separate
    books. This never clusters books solely on an overall size multiplier.

    Score = equal-year mean unconditional pass - .25 * population SD(yearly pass).
    Year coverage and common yearly start calendars are required. A policy with
    unknown_share>1% is not certifiable. Risk ordering uses the *upper bound* on
    failures; unknown is never renamed an observed failure. No missing starts are
    dropped or imputed here. If no policy passes data gates, only a provisional
    frontier is returned and nominees is empty.

    Top20% medoids are constructed separately by family/book and objective. The
    risk pool is formed FIRST from the inclusive2pp pass-score band; a pass-only
    trimming step cannot remove every safer policy in that band. A fixed normalized
    RMS-distance graph chooses its largest connected elite neighborhood and its
    medoid. Singleton neighborhoods are flagged, not claimed stable.
    """
    if not 0 <= max_nominees <= 3 or not 0 < top_fraction <= 1 or pass_tolerance < 0:
        raise ValueError("Invalid nomination settings")
    years = tuple(sorted(set(int(y) for y in design_years)))
    if not years or any(y not in DESIGN_YEARS for y in years):
        raise ValueError("Selection years must be within2018--22")
    if not 0 <= max_unknown_share <= 1 or neighborhood_radius < 0:
        raise ValueError("Invalid data/neighbor gate")
    if hasattr(summary_rows, "to_dict"):
        summary_rows = summary_rows.to_dict("records")
    grouped, excluded = defaultdict(dict), []
    calendars = defaultdict(set)
    for source in summary_rows:
        row = dict(source)
        year = row.get("year")
        if isinstance(year, str) and len(year) == 4 and year.isdigit():
            year = int(year)
        if not isinstance(year, (int, np.integer)) or int(year) not in years:
            excluded.append(dict(candidate_id=row.get("candidate_id", row.get("candidate")), year=str(year), reason="outside_design_years"))
            continue
        candidate = str(row.get("candidate_id", row.get("candidate", row.get("name", ""))))
        account = str(row.get("account", "default"))
        if not candidate:
            raise ValueError("Annual row needs candidate_id")
        key = (account, candidate)
        if int(year) in grouped[key]:
            raise ValueError("Duplicate candidate/account/year row")
        n, counts = _counts(row)
        row.update(n=n, counts=counts)
        grouped[key][int(year)] = row
        if row.get("calendar_hash"):
            calendars[(account, int(year))].add((row["calendar_hash"], n))
    candidates = []
    for (account, candidate), annual in sorted(grouped.items()):
        meta = _metadata(candidate_metadata, account, candidate)
        vector = meta.get("exposure_vector", meta.get("exposures"))
        if not isinstance(vector, Mapping) or not vector:
            raise ValueError("Every candidate needs explicit exposure/risk-coefficient vector")
        vector = {str(k): float(v) for k, v in vector.items()}
        if not all(np.isfinite(v) for v in vector.values()):
            raise ValueError("Exposure vector contains unavailable/nonfinite coefficients")
        family_value = meta.get("family_id", meta.get("family"))
        if family_value is None:
            raise ValueError("Every candidate needs an economic family_id; unrelated books cannot share an inferred family")
        family = str(family_value)
        book = str(meta.get("book_id", "support:" + ",".join(sorted(k for k, v in vector.items() if v != 0))))
        counts = {s: sum(r["counts"][s] for r in annual.values()) for s in STATUSES}
        n = sum(r["n"] for r in annual.values())
        pass_rates = [annual[y]["counts"]["pass"] / annual[y]["n"] for y in years if y in annual and annual[y]["n"]]
        rates = {s: counts[s] / n if n else None for s in STATUSES}
        times = [float(t) for r in annual.values() for t in r.get("pass_times", [])]
        if any(not np.isfinite(t) or t < 0 for t in times):
            raise ValueError("Invalid conditional pass times")
        if any(len(r.get("pass_times", [])) > r["counts"]["pass"] for r in annual.values()):
            raise ValueError("More passing times than actual passing starts")
        reasons = []
        if set(annual) != set(years) or len(pass_rates) != len(years):
            reasons.append("missing_or_empty_design_years")
        if not n or rates["unknown"] > max_unknown_share + 1e-12:
            reasons.append("unknown_share_above_gate_or_empty")
        for y in years:
            if y not in annual or not annual[y].get("calendar_hash"):
                reasons.append("start_calendar_unverified")
            elif len(calendars[(account, y)]) != 1:
                reasons.append("different_start_calendars_or_denominators")
        if not meta.get("eligible", True):
            reasons.append("caller_input_admission_failed")
        mean = float(np.mean(pass_rates)) if pass_rates else -math.inf
        sd = float(np.std(pass_rates, ddof=0)) if pass_rates else math.inf
        candidates.append(dict(candidate_id=candidate, account=account, family_id=family, book_id=book,
            family_group=family + "::" + book, exposure_vector=vector, n=n, counts=counts, rates=rates,
            pass_lower=rates["pass"], pass_upper=(counts["pass"] + counts["unknown"]) / n if n else None,
            fail_lower=rates["fail"], fail_upper=(counts["fail"] + counts["unknown"]) / n if n else math.inf,
            expire_rate=rates["expire"] if n else math.inf, unknown_share=rates["unknown"],
            yearly_pass={str(y): annual[y]["counts"]["pass"] / annual[y]["n"] if annual[y]["n"] else None for y in sorted(annual)},
            calendar_hashes={str(y): annual[y].get("calendar_hash") for y in sorted(annual)},
            pass_year_mean=mean, pass_year_sd=sd, pass_score=mean - .25 * sd,
            conditional_pass_median_time=median(times) if times else None,
            conditional_pass_mean_time=float(np.mean(times)) if times else None,
            passed_with_time=len(times), pass_time_coverage=len(times) / counts["pass"] if counts["pass"] else None,
            certifiable_ranking=not reasons, data_gate_reasons=sorted(set(reasons))))
    accounts = {}
    for account in sorted({c["account"] for c in candidates}):
        all_rows = [c for c in candidates if c["account"] == account]
        eligible = [c for c in all_rows if c["certifiable_ranking"]]
        finite = [c for c in all_rows if np.isfinite(c["pass_score"]) and c["n"]]
        frontier_all = _frontier(finite)
        frontier = _frontier(eligible)
        chosen, medoid_audits, role_pools = [], [], {}
        if eligible:
            best = max(c["pass_score"] for c in eligible)
            pools = {
                "robust_pass": eligible,
                "risk_first": [c for c in eligible if c["pass_score"] >= best - pass_tolerance - 1e-12],
                "fast_pass": [c for c in frontier if c["counts"]["pass"] >= min_fast_passes
                              and c["passed_with_time"] == c["counts"]["pass"]
                              and c["conditional_pass_median_time"] is not None],
            }
            for role in ("robust_pass", "risk_first", "fast_pass"):
                representatives, audit = _family_medoids(pools[role], eligible, role, top_fraction, neighborhood_radius)
                medoid_audits.extend(audit)
                role_pools[role] = [c["candidate_id"] for c in representatives]
                selected_ids = {c["candidate_id"] for c in chosen}
                pick = next((c for c in representatives if c["candidate_id"] not in selected_ids), None)
                if pick is not None and len(chosen) < max_nominees:
                    chosen.append(dict(pick, nomination_role=role))
        accounts[account] = dict(candidates=all_rows,
            pareto_all=frontier_all, pareto_certifiable=frontier,
            frontier=frontier if eligible else frontier_all,
            frontier_status="certifiable_ranking_only" if eligible else "provisional_no_candidate_passed_data_gates",
            nominees=chosen, role_medoid_candidates=role_pools, family_medoid_audit=medoid_audits,
            selection_status="finite_design_nomination_not_global_optimum" if eligible else "no_certifiable_nomination")
    return dict(design_years=list(years), excluded_rows=excluded, accounts=accounts,
        settings=dict(max_nominees=max_nominees, top_fraction=top_fraction, pass_tolerance=pass_tolerance,
                      max_unknown_share=max_unknown_share, normalized_rms_neighborhood_radius=neighborhood_radius,
                      score="equal-year unconditional-pass mean minus0.25populationSD", min_fast_passes=min_fast_passes),
        limits="Selection, data-gate ranking and conditional historical uncertainty only. No global optimum, live safety or independent economic verification is established.")


def _aligned(candidate, baseline, *, status_key, time_key, start_key, status_map, assume_aligned):
    a = _records(candidate, status_key, time_key, start_key, status_map)
    b = _records(baseline, status_key, time_key, start_key, status_map)
    if len(a) != len(b):
        raise ValueError("Candidate/baseline must retain the identical start universe, including unknowns")
    if not a:
        raise ValueError("No paired starts")
    a_ids = [r["start_id"] for r in a]; b_ids = [r["start_id"] for r in b]
    if all(i is not None for i in a_ids) and all(i is not None for i in b_ids):
        if set(a_ids) != set(b_ids):
            raise ValueError("Candidate/baseline start IDs differ; no intersection-only comparison")
        amap = {r["start_id"]: r for r in a}; bmap = {r["start_id"]: r for r in b}
        ids = sorted(amap)
        return [amap[i] for i in ids], [bmap[i] for i in ids], ids, "matched_unique_start_ids"
    if any(i is not None for i in a_ids + b_ids) or not assume_aligned:
        raise ValueError("Supply unique matching start IDs or explicitly set assume_aligned=True for positional arrays")
    return a, b, list(range(len(a))), "caller_asserted_positional_chronology"


def paired_block_bootstrap(candidate, baseline, *, block_starts=4, n_reps=5000, seed=20261104,
                           quantiles=(.05, .95), status_key="status", time_key="time", start_key="start",
                           status_map=None, assume_aligned=False):
    """Paired noncircular moving-block bootstrap of weekly-start outcome differences.

    Blocks are4or8 *start observations*, not independently shuffled trades/days.
    Every bootstrap draw uses identical contiguous indices for both policies and
    retains unknowns. Bounds are reported alongside known-state differences.
    The caller must supply the frozen chronological weekly-start calendar.
    """
    if not isinstance(block_starts, (int, np.integer)) or block_starts < 1:
        raise ValueError("block_starts must be positive integer")
    if not isinstance(n_reps, (int, np.integer)) or n_reps < 1:
        raise ValueError("n_reps must be positive integer")
    if len(quantiles) != 2 or not 0 <= quantiles[0] < quantiles[1] <= 1:
        raise ValueError("Invalid interval quantiles")
    a, b, ids, alignment = _aligned(candidate, baseline, status_key=status_key, time_key=time_key,
        start_key=start_key, status_map=status_map, assume_aligned=assume_aligned)
    n = len(a)
    if n < block_starts:
        raise ValueError("Insufficient paired starts for requested block length; no IID fallback")
    x = np.array([[int(r["status"] == s) for s in STATUSES] for r in a], dtype=float)
    y = np.array([[int(r["status"] == s) for s in STATUSES] for r in b], dtype=float)
    known = x - y
    delta = np.column_stack([known, x[:, 0] - y[:, 0] - y[:, 3],
        x[:, 0] + x[:, 3] - y[:, 0], x[:, 1] - y[:, 1] - y[:, 3], x[:, 1] + x[:, 3] - y[:, 1]])
    names = ["pass", "fail", "expire", "unknown", "pass_difference_lower", "pass_difference_upper",
             "fail_difference_lower", "fail_difference_upper"]
    rng = np.random.default_rng(seed)
    draws = np.empty((n_reps, len(names)))
    nb = math.ceil(n / block_starts); offsets = np.arange(block_starts)
    digest = hashlib.sha256()
    for first in range(0, n_reps, 250):
        last = min(first + 250, n_reps)
        starts = rng.integers(0, n - block_starts + 1, size=(last - first, nb))
        index = (starts[:, :, None] + offsets).reshape(last - first, -1)[:, :n]
        digest.update(index.astype("<i8", copy=False).tobytes())
        draws[first:last] = delta[index].mean(axis=1)
    assert np.allclose(draws[:, :4].sum(axis=1), 0.)
    intervals = np.quantile(draws, quantiles, axis=0)
    point = dict(zip(names, map(float, delta.mean(axis=0))))
    ci = {key: [float(intervals[0, i]), float(intervals[1, i])] for i, key in enumerate(names)}
    return dict(n=n, block_starts=int(block_starts), n_reps=int(n_reps), seed=int(seed),
        quantiles=list(quantiles), alignment=alignment, start_calendar_hash=hashlib.sha256(json.dumps(ids).encode()).hexdigest(),
        resample_index_sha256=digest.hexdigest(), point_delta=point, ci=ci,
        identified_effect_ci=dict(pass_difference=[ci["pass_difference_lower"][0], ci["pass_difference_upper"][1]],
                                  fail_difference=[ci["fail_difference_lower"][0], ci["fail_difference_upper"][1]]),
        candidate=summarize_outcomes(a, start_key="start_id"), baseline=summarize_outcomes(b, start_key="start_id"),
        limits="Conditional on empirical paired chronology and fixed policies. Blocks are weekly-start observations; interval precision is not future edge or calibrated live-account risk.")


def paired_block_bootstrap_sensitivity(candidate, baseline, *, blocks=(4, 8), **kwargs):
    """Return both prespecified block sensitivities; do not claim monotone widths."""
    return {str(block): paired_block_bootstrap(candidate, baseline, block_starts=block, **kwargs) for block in blocks}


def selftest():
    s = summarize_outcomes([dict(status=k, time=2, start=i) for i, k in enumerate(STATUSES)])
    assert s["n"] == 4 and s["rates"] == dict.fromkeys(STATUSES, .25)
    assert s["pass_lower"] == .25 and s["pass_upper"] == .5 and s["fail_upper"] == .5
    assert summarize_outcomes([])["rates"]["fail"] is None
    assert summarize_outcomes([None, "open", "unfinished"])["counts"]["unknown"] == 3
    for bad in ([dict(status="pass", fail=True)], [dict(status="pass", start=1), dict(status="fail", start=1)]):
        try:summarize_outcomes(bad)
        except ValueError:pass
        else:raise AssertionError("Contradictory/duplicate data accepted")
    def annual(cid, statuses, year, account="50K"):
        return summarize_outcomes([dict(status=k, time=(i % 7) + 1, start=i) for i, k in enumerate(statuses)],
            candidate_id=cid, year=year, account=account)
    rows = []
    meta = {}
    for cid, npass, nfail in [("best", 60, 35), ("safer", 59, 20), ("outside", 57, 0), ("unknown", 59, 0)]:
        statuses = ["pass"] * npass + ["fail"] * nfail + ["expire"] * (100 - npass - nfail)
        if cid == "unknown":statuses[-41:] = ["unknown"] * 41
        rows.extend(annual(cid, statuses, y) for y in DESIGN_YEARS)
        meta[cid] = dict(family_id=cid, book_id=cid, exposure_vector={"VB": 1., "ONB": 1.})
    r = rank_design(rows, candidate_metadata=meta)
    a = r["accounts"]["50K"]
    assert a["nominees"][0]["candidate_id"] == "best"
    assert next(x for x in a["nominees"] if x["nomination_role"] == "risk_first")["candidate_id"] == "safer"
    assert not next(x for x in a["candidates"] if x["candidate_id"] == "unknown")["certifiable_ranking"]
    assert [c["candidate_id"] for c in rank_design(list(reversed(rows)), candidate_metadata=meta)["accounts"]["50K"]["nominees"]] == [c["candidate_id"] for c in a["nominees"]]
    boundary_rows = rows + [annual("boundary", ["pass"] * 58 + ["fail"] * 5 + ["expire"] * 37, y) for y in DESIGN_YEARS]
    boundary_meta = dict(meta, boundary=dict(family_id="boundary", exposure_vector={"VB":1., "ONB":1.}))
    boundary = rank_design(boundary_rows, candidate_metadata=boundary_meta)["accounts"]["50K"]
    assert next(c for c in boundary["nominees"] if c["nomination_role"] == "risk_first")["candidate_id"] == "boundary"
    gate_rows = []
    gate_meta = {}
    for cid, unknown in (("at_gate", 1), ("above_gate", 2)):
        gate_rows.extend(annual(cid, ["pass"] * 60 + ["fail"] * (40 - unknown) + ["unknown"] * unknown, y) for y in DESIGN_YEARS)
        gate_meta[cid] = dict(family_id=cid, exposure_vector={"VB":1.})
    gate = rank_design(gate_rows, candidate_metadata=gate_meta)["accounts"]["50K"]
    assert next(c for c in gate["candidates"] if c["candidate_id"] == "at_gate")["certifiable_ranking"]
    assert not next(c for c in gate["candidates"] if c["candidate_id"] == "above_gate")["certifiable_ranking"]
    mismatched = [dict(r) for r in rows]
    mismatched[0]["calendar_hash"] = "different_calendar"
    mismatch = rank_design(mismatched, candidate_metadata=meta)["accounts"]["50K"]
    assert not mismatch["nominees"] and all(not c["certifiable_ranking"] for c in mismatch["candidates"])
    partial = rank_design(rows[1:5], candidate_metadata=meta)["accounts"]["50K"]
    assert not partial["nominees"] and "missing_or_empty_design_years" in partial["candidates"][0]["data_gate_reasons"]
    # Pure parameter/score fixtures: a dense elite neighborhood beats an isolated
    # single maximum; multiplying parameter units cannot change its medoid.
    points = []
    for i in range(20):
        exposure = [1., .10, .11, .12][i] if i < 4 else (i - 4) / 1000
        points.append(dict(candidate_id=f"p{i:02d}", family_group="family::book", exposure_vector={"VB":exposure},
            pass_score=.90 - i / 100 if i < 4 else .40 - i / 1000,
            fail_upper=.1, expire_rate=.1, conditional_pass_median_time=4))
    medoids, audit = _family_medoids(points, points, "robust_pass", .2, .35)
    assert medoids[0]["candidate_id"] == "p02" and medoids[0]["neighborhood_supported"]
    scaled = [dict(p, exposure_vector={"VB":p["exposure_vector"]["VB"] * 100}) for p in points]
    assert _family_medoids(scaled, scaled, "robust_pass", .2, .35)[0][0]["candidate_id"] == "p02"
    separated = [dict(points[0], family_group="a::book"), dict(points[1], family_group="b::other_book")]
    assert len(_family_medoids(separated, separated, "robust_pass", .2, .35)[0]) == 2
    extended = rows + [annual("outside", ["pass"] * 100, 2023)]
    assert [c["candidate_id"] for c in rank_design(extended, candidate_metadata=meta)["accounts"]["50K"]["nominees"]] == [c["candidate_id"] for c in a["nominees"]]
    bad = [annual("x", ["unknown"] * 100, y) for y in DESIGN_YEARS]
    b = rank_design(bad, candidate_metadata={"x":dict(family_id="x", exposure_vector={"VB":1.})})["accounts"]["50K"]
    assert not b["nominees"] and b["frontier_status"].startswith("provisional")
    same = [dict(status=("pass" if i < 16 else "fail"), start=i, time=5) for i in range(32)]
    boot = paired_block_bootstrap(same, list(reversed(same)), block_starts=8, n_reps=5000)
    assert all(v == [0., 0.] for v in boot["ci"].values())
    assert boot["resample_index_sha256"] == paired_block_bootstrap(same, same, block_starts=8, n_reps=5000)["resample_index_sha256"]
    allpass = [dict(status="pass", start=i, time=1) for i in range(32)]
    allfail = [dict(status="fail", start=i, time=1) for i in range(32)]
    known = paired_block_bootstrap(allpass, allfail, block_starts=4, n_reps=5000)
    assert known["ci"]["pass"] == [1., 1.] and known["ci"]["fail"] == [-1., -1.]
    try:paired_block_bootstrap(same[:-1], same, n_reps=5)
    except ValueError:pass
    else:raise AssertionError("Mismatched calendar accepted")
    shifted = [dict(r, start=r["start"] + 100) for r in same]
    try:paired_block_bootstrap(shifted, same, n_reps=5)
    except ValueError:pass
    else:raise AssertionError("Intersection-only calendar accepted")
    dependent = [dict(status=("pass" if i < 32 else "fail"), start=i, time=1) for i in range(64)]
    baseline = [dict(status="fail", start=i, time=1) for i in range(64)]
    iid = paired_block_bootstrap(dependent, baseline, block_starts=1, n_reps=5000)
    blocked = paired_block_bootstrap_sensitivity(dependent, baseline, n_reps=5000)
    assert blocked["8"]["ci"]["pass"][1] - blocked["8"]["ci"]["pass"][0] > iid["ci"]["pass"][1] - iid["ci"]["pass"][0]
    assert all(sum(b["point_delta"][s] for s in STATUSES) == 0 for b in blocked.values())
    print("PASS: synthetic denominators/bounds, unknown/calendar/year gates, inclusive risk band, elite medoid/unit invariance, book separation, design/row-order isolation, provisional frontier, strict paired alignment, reproducibility and5,000-draw dependent-block checks; no market data read.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args()
    if args.selftest:
        selftest()
    else:
        parser.error("Import this pure helper, or use --selftest; no market-data runner is provided.")
