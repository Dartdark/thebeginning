"""Independent, pure E1/MO signal reconstruction from observed NQ bars.

Pinned source: d14dc9a:analysis/twin_continuation_test.py (MO only) and
analysis/high_winrate_test.py (E1). No old maker is imported/executed. Every
observed clock-bucket closure, including partial/midnight buckets, updates
EMA21 pivot/RMA14 true range/EMA3 oscillator. No orders, stops or P&L here.
"""
from __future__ import annotations

from datetime import date
import hashlib
import json
import math
from pathlib import Path
import re

REQUIRED = ("o", "h", "l", "c", "row", "j", "date")
ALPHA_PIVOT, ALPHA_OSC = 2 / 22, 2 / 4


def _day(value):
    text = str(value)
    if re.fullmatch(r"[0-9]{8}", text):
        day = date(int(text[:4]), int(text[4:6]), int(text[6:8]))
    elif re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", text):
        day = date.fromisoformat(text)
    else:
        raise ValueError("Observed dates must be YYYYMMDD or ISO YYYY-MM-DD.")
    return day


def source_half_day(value):
    day = _day(value)
    return ((day.month == 7 and day.day == 3) or (day.month == 12 and day.day == 24)
        or (day.month == 11 and day.weekday() == 4 and 23 <= day.day <= 29))


def _finite(value):
    return value is not None and math.isfinite(value)


def _json_float(value):
    return float(value) if _finite(value) else None


def _bar_valid(o, h, l, c):
    return all(math.isfinite(v) and v > 0 for v in (o, h, l, c)) and l <= min(o, c) and h >= max(o, c) and h >= l


def _observed_buckets(observed_records):
    """Yield contiguous bucket occurrences; do not copy the whole bar history."""
    count = len(observed_records["c"])
    previous_coord, row_dates, bucket = None, {}, None
    for index in range(count):
        row_raw, j_raw = observed_records["row"][index], observed_records["j"][index]
        row, j = int(row_raw), int(j_raw)
        if row != row_raw or j != j_raw or row < 0 or not 0 <= j < 1440:
            raise ValueError("Observed row/minute must be exact valid nonnegative integers.")
        coord = (row, j)
        if previous_coord is not None and coord < previous_coord:
            raise ValueError("Observed records are not chronological; no sort/repair is allowed.")
        previous_coord = coord
        day = _day(observed_records["date"][index])
        if row in row_dates and row_dates[row] != day:
            raise ValueError("One Grid24 row maps to multiple calendar dates.")
        row_dates[row] = day
        key = (row, ((j - 1) % 1440) // 10)
        # Contiguous runs only: j0 and j1431..1439 on the same row have the
        # same label but are separate literal source bucket occurrences.
        if bucket is not None and bucket["key"] != key:
            yield bucket
            bucket = None
        if bucket is None:
            bucket = dict(key=key, items=[])
        values = tuple(float(observed_records[name][index]) for name in ("o", "h", "l", "c"))
        identifier = str(observed_records["source_id"][index]) if "source_id" in observed_records else f"row{row}:j{j}:observed{index}"
        global_id = int(observed_records["global_index"][index]) if "global_index" in observed_records else row * 1440 + j
        bucket["items"].append(dict(index=index, row=row, j=j, date=day, source_id=identifier,
            global_index=global_id, o=values[0], h=values[1], l=values[2], c=values[3],
            valid_source=_bar_valid(*values)))
    if bucket is not None:
        yield bucket


def reconstruct_mo(observed_records):
    """Aligned observed arrays -> (signal dicts, every closed-bucket dict).

    Input must be chronological by (row,j); equal coordinates are retained but
    flag duplicates and never make a full bucket. date is tied consistently to
    row. source_id/global_index, when supplied, are retained only as audit IDs.
    No date/outcome selection or new price data is performed by this function.
    """
    if not isinstance(observed_records, dict) or any(name not in observed_records for name in REQUIRED):
        raise ValueError("Expected aligned observed-record arrays:" + ",".join(REQUIRED))
    count = len(observed_records["c"])
    if any(len(observed_records[name]) != count for name in REQUIRED):
        raise ValueError("Observed input arrays have different lengths.")
    for optional in ("source_id", "global_index"):
        if optional in observed_records and len(observed_records[optional]) != count:
            raise ValueError("Optional source-ID array length differs.")
    signals, audit = [], []
    nb, prev_close, atrw, pivot, osc, previous_osc = 0, None, 0.0, 0.0, None, None
    traded_dates, unresolved_lineage = set(), []
    for occurrence, bucket in enumerate(_observed_buckets(observed_records), start=1):
        items = bucket["items"]; last = items[-1]
        highs, lows = items[0]["h"], items[0]["l"]
        for item in items[1:]:
            highs, lows = max(highs, item["h"]), min(lows, item["l"])
        close = last["c"]
        js = [item["j"] for item in items]
        bucket_id = f"MO_BUCKET_{occurrence:08d}_row{bucket['key'][0]}_k{bucket['key'][1]}"
        invalid_ids = [item["source_id"] for item in items if not item["valid_source"]]
        if invalid_ids:
            unresolved_lineage.append(bucket_id)
        nominal_end_j = (bucket["key"][1] + 1) * 10
        nominal_hhmm = (nominal_end_j // 60) * 100 + nominal_end_j % 60
        expected_js = list(range(bucket["key"][1] * 10 + 1, nominal_end_j + 1))
        expected_js = [minute % 1440 for minute in expected_js]
        full = len(items) == 10 and len(set(js)) == 10 and sorted(js) == sorted(expected_js)
        nb += 1
        if nb == 1:
            true_range = highs - lows; atrw = true_range; pivot = close
        else:
            true_range = max(highs - lows, abs(highs - prev_close), abs(lows - prev_close))
            atrw += (true_range - atrw) / 14
            pivot += (close - pivot) * ALPHA_PIVOT
        prev_close = close
        crossing, raw = 0, None
        if atrw > 0:
            raw = (close - pivot) / (3 * atrw) * 100
            if osc is None:
                osc = raw
            else:
                previous_osc = osc
                osc += (raw - osc) * ALPHA_OSC
                if osc > 100 and previous_osc <= 100:
                    crossing = 1
                elif osc < -100 and previous_osc >= -100:
                    crossing = -1
        day = last["date"]
        half = source_half_day(day.isoformat())
        in_window = 840 <= nominal_hhmm <= 930
        already = day in traded_dates
        qualifies = bool(crossing and in_window and full and not half and not already and nb >= 60)
        # Literal source state is retained even if invalid bars make it unsafe.
        # The caller must veto unresolved source/recursive lineage before returns.
        record = dict(bucket_id=bucket_id, bucket_occurrence=occurrence, bucket_row=bucket["key"][0],
            bucket_clock_index=bucket["key"][1], date=day.isoformat(), nb=nb,
            observed_bars=len(items), unique_observed_minutes=len(set(js)), observed_minutes=js,
            source_ids=[item["source_id"] for item in items], global_indices=[item["global_index"] for item in items],
            first_observed_index=items[0]["index"], last_observed_index=last["index"],
            first_observed_j=items[0]["j"], last_observed_j=last["j"],
            nominal_end_j=nominal_end_j, nominal_end_hhmm=nominal_hhmm, full=full, partial=not full,
            duplicate_observed_minutes=len(js) - len(set(js)), invalid_source_ids=invalid_ids,
            invalid_source=bool(invalid_ids), recursive_state_unresolved=bool(unresolved_lineage),
            recursive_unresolved_bucket_ids=list(unresolved_lineage),
            bucket_high=_json_float(highs), bucket_low=_json_float(lows), bucket_close=_json_float(close),
            true_range=_json_float(true_range), piv=_json_float(pivot), atrw=_json_float(atrw),
            raw=_json_float(raw), osc=_json_float(osc), prevOsc=_json_float(previous_osc),
            crossing_side=crossing, source_half_day=half, in_signal_window=in_window,
            date_already_signaled=already, minimum60_pass=nb >= 60, signal_emitted=qualifies)
        audit.append(record)
        if qualifies:
            traded_dates.add(day)
            signals.append(dict(date=int(day.isoformat().replace("-", "")), date_iso=day.isoformat(),
                date_id=int(day.isoformat().replace("-", "")), row=last["row"], j=last["j"],
                sigrow=last["row"], sigj=last["j"], sig_i=last["index"], global_index=last["global_index"],
                side=crossing, piv=_json_float(pivot), pivot=_json_float(pivot), atrw=_json_float(atrw), osc=_json_float(osc),
                prevOsc=_json_float(previous_osc), nb=nb, bucket_id=bucket_id,
                bucket_occurrence=occurrence, nominal_end_hhmm=nominal_hhmm,
                source_half_day=half, recursive_state_unresolved=bool(unresolved_lineage),
                source_ids=[item["source_id"] for item in items]))
    return signals, audit


def fixtures():
    def make(buckets, target_day="2020-01-02", target_close=1000.0, target_minutes=10, baseline=100.0):
        rows = []
        for bucket in range(buckets):
            for j in range(591 + bucket * 10, 601 + bucket * 10):
                rows.append((0, j, "2019-12-30", baseline))
        for j in range(511, 511 + target_minutes):
            rows.append((1, j, target_day, target_close))
        return arrays(rows)
    def arrays(rows):
        result = {key: [] for key in REQUIRED}
        result["source_id"] = []
        for index, (row, j, day, close) in enumerate(rows):
            for key, value in dict(o=close, h=close + .25, l=close - .25, c=close, row=row, j=j, date=day).items():
                result[key].append(value)
            result["source_id"].append(f"ARTIFICIAL_{index}")
        return result
    signals, audit = reconstruct_mo(make(59))
    assert len(signals) == 1 and signals[0]["side"] == 1 and signals[0]["nb"] == 60 and signals[0]["sigj"] == 520
    assert signals[0]["prevOsc"] <= 100 < signals[0]["osc"] and audit[0]["atrw"] == .5 and audit[0]["piv"] == 100
    short, _ = reconstruct_mo(make(59, target_close=100.0, baseline=1000.0))
    assert len(short) == 1 and short[0]["side"] == -1 and short[0]["osc"] < -100 <= short[0]["prevOsc"]
    immature, imm_audit = reconstruct_mo(make(58))
    assert not immature and imm_audit[-1]["crossing_side"] == 1 and imm_audit[-1]["nb"] == 59
    partial, partial_audit = reconstruct_mo(make(59, target_minutes=9))
    assert not partial and partial_audit[-1]["partial"] and partial_audit[-1]["nb"] == 60
    assert abs(partial_audit[-1]["piv"] - (100 + 900 * 2 / 22)) < 1e-10
    midnight = arrays([(0, 0, "2020-01-01", 100)] + [(0, j, "2020-01-01", 100) for j in range(1, 11)]
        + [(0, j, "2020-01-01", 100) for j in range(1431, 1440)] + [(1, 0, "2020-01-02", 100)])
    _, mid_audit = reconstruct_mo(midnight)
    assert [r["observed_bars"] for r in mid_audit] == [1, 10, 9, 1]
    assert [r["nominal_end_hhmm"] for r in mid_audit] == [2400, 10, 2400, 2400]
    assert [r["nb"] for r in mid_audit] == [1, 2, 3, 4]
    for day in ("2020-07-03", "2020-12-24", "2020-11-27"):
        blocked, buckets = reconstruct_mo(make(59, target_day=day))
        assert not blocked and buckets[-1]["source_half_day"] and buckets[-1]["crossing_side"] == 1
    assert not source_half_day("2020-11-26")  # Source Friday, shared Thanksgiving skip belongs to caller.
    duplicate = make(59)
    for key in duplicate:
        duplicate[key][-1] = duplicate[key][-2]
    blocked, duplicate_audit = reconstruct_mo(duplicate)
    assert not blocked and duplicate_audit[-1]["duplicate_observed_minutes"] == 1 and not duplicate_audit[-1]["full"]
    # Repeated same-date qualifying opposite cross must not emit another ticket.
    capped = make(59, target_close=1100.0, baseline=1000.0)
    for j in range(521, 571):
        for key, value in dict(o=1, h=1.25, l=.75, c=1, row=1, j=j, date="2020-01-02", source_id=f"ARTIFICIAL_EXTRA_{j}").items():
            capped[key].append(value)
    cap_signals, cap_audit = reconstruct_mo(capped)
    assert len(cap_signals) == 1 and any(r["crossing_side"] == -1 and r["date_already_signaled"] for r in cap_audit)
    invalid = make(59); invalid["h"][0] = 0
    _, bad_audit = reconstruct_mo(invalid)
    assert bad_audit[0]["invalid_source"] and bad_audit[-1]["recursive_state_unresolved"]
    assert reconstruct_mo({key: [] for key in REQUIRED}) == ([], [])
    json.dumps([signals, audit, mid_audit, bad_audit], allow_nan=False)
    return dict(passed=True, actual_market_MC_cache_CSV_rows_read=False, stopped_or_return_engine_executed=False,
        checks=["independentlong/shortcrossandfirstbucketinitialization", "60bucketminimumincludescurrentclosure",
            "partialbucketsupdateallrecursiveindicatorsbutcannotfire", "literalmidnight9+1bucketquirk",
            "sourceJul3/Dec24/ThanksgivingFRIDAYskip;Thursdaynotinliteralhalfday",
            "10uniqueobservedminutesrequired", "firstqualifyingsignalperdate/noBOorpositionmodel",
            "invalidsourceandrecursivelineageretained", "emptyarraysandJSONsafeaudit"],
        script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())


if __name__ == "__main__":
    result = fixtures()
    output = Path(__file__).resolve().parent / "outputs/codex_hunt_v2_highwin_confirmation" / f"signal_synthetic_checks_{result['script_sha256'][:12]}.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("x") as handle:
        json.dump(result, handle, indent=2, allow_nan=False); handle.write("\n")
    print(json.dumps(result, allow_nan=False))
