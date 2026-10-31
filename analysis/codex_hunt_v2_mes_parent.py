"""H09 pure, literal CT five-minute ES MOC parent and affordability features.

No input/file/calendar schedule is read on import or by fixtures. Callers own
the frozen source inventory, expected-date calendar and whole-phase admission.
This helper computes no entry-to-exit return, stop path, trade profit or metric.
"""
from __future__ import annotations

from collections import defaultdict
from datetime import date, timedelta
from decimal import Decimal, InvalidOperation
from fractions import Fraction
import math
import re
import sys

sys.dont_write_bytecode = True
SOURCE_COMMIT = "d14dc9a153df128aafd3f48d4fea2aa78b88bb28"
SOURCE_PATH = "funded_strategies/ES_MOC_Follow.txt"
SOURCE_BLOB = "33e4a6a1c57dc0867d6ee9b26c310879ebd08f18"
SHARED_CALENDAR_DEPENDENCIES = ("analysis/codex_s03_calendar.py", "analysis/replica.py")
ATR_DAYS, REFERENCE_J, DECISION_J, ENTRY_J, EXIT_J = 15, 840, 890, 891, 900
TICK, POINT_VALUE, ROUND_TRIP_ALLOWANCE, SLICE = Fraction(1, 4), 5, Fraction(374, 100), 250
_NUMBER = re.compile(r"[+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[eE][+-]?[0-9]+)?\Z")


def number(value):
    """Finite decimal numeric input; negative/zero quotes are not repaired."""
    if isinstance(value, Fraction):
        return value
    text = str(value)
    if _NUMBER.fullmatch(text) is None:
        raise ValueError("Pure parent requires a finite ASCII decimal number.")
    try:
        result = Decimal(text)
    except InvalidOperation as error:
        raise ValueError("Invalid numeric value.") from error
    if not result.is_finite():
        raise ValueError("Nonfinite observation.")
    return Fraction(result)


def exact_text(value):
    value = number(value)
    return str(value.numerator) + "/" + str(value.denominator)


def civil_day(value):
    if not isinstance(value, str) or re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", value) is None:
        raise ValueError("Date must be a strict civil ISO date.")
    return date.fromisoformat(value)


def clock_key(day, minute):
    d = civil_day(day)
    if type(minute) is not int or not 0 <= minute < 1440:
        raise ValueError("Native minute must be an integer in0..1439.")
    return d.toordinal() * 1440 + minute


def split_clock(key):
    ordinal, minute = divmod(key, 1440)
    return date.fromordinal(ordinal).isoformat(), minute


def literal_early_close(day):
    """Exact UseHolidayTimes=true predicate from the pinned PL, with trace.

    This is a literal source predicate, not an authoritative cash calendar.
    Callers must also retain the independently bound shared calendar audit.
    """
    d = civil_day(day); mo, dom, yr = d.month, d.day, d.year
    dow = (d.weekday() + 1) % 7
    wk = 1 <= dow <= 5
    checks = {
        "JAN_NEWYEAR": mo == 1 and ((dom == 1 and wk) or (dom == 2 and dow == 1)),
        "JAN_THIRD_MONDAY": mo == 1 and dow == 1 and 15 <= dom <= 21,
        "FEB_THIRD_MONDAY": mo == 2 and dow == 1 and 15 <= dom <= 21,
        "MAY_LAST_MONDAY": mo == 5 and dow == 1 and dom >= 25,
        "JUNE_SOURCE_OBSERVANCE": mo == 6 and yr >= 2022 and ((dom == 19 and wk) or (dom == 18 and dow == 5) or (dom == 20 and dow == 1)),
        "JULY_SOURCE_OBSERVANCE": mo == 7 and (((dom == 3 or dom == 4) and wk) or (dom == 5 and dow == 1)),
        "SEPT_FIRST_MONDAY": mo == 9 and dow == 1 and dom <= 7,
        "NOV_THANKSGIVING": mo == 11 and dow == 4 and 22 <= dom <= 28,
        "NOV_FRIDAY": mo == 11 and dow == 5 and 23 <= dom <= 29,
        "DEC_SOURCE_OBSERVANCE": mo == 12 and (((dom == 24 or dom == 25) and wk) or (dom == 26 and dow == 1)),
    }
    return dict(is_early_close=any(checks.values()), matching_source_clauses=[key for key, value in checks.items() if value],
        source_powerlanguage_dow=dow, source_is_weekday=wk, source_blob=SOURCE_BLOB)


def calendar_audit(day, shared_status):
    """Audit an explicitly supplied shared cash-calendar result; no schedule I/O."""
    literal = literal_early_close(day)
    if not isinstance(shared_status, dict) or shared_status.get("kind") not in {"normal", "early", "holiday", "weekend"}:
        raise ValueError("Caller must provide the fixed shared cash-calendar audit.")
    allowed = shared_status["kind"] == "normal" and not literal["is_early_close"]
    return dict(literal=literal, shared_cash_calendar=dict(shared_status), calendar_entry_allowed=allowed,
        disposition="ELIGIBLE" if allowed else "SKIP_KNOWN_CALENDAR", future_price_membership_used=False)


def affordability(atr):
    """Fixed whole-contract feature only; this is not a hard dollar risk cap."""
    atr = number(atr)
    if atr <= 0:
        raise ValueError("Parent ATR must be strictly positive.")
    raw_distance = atr / 4
    stop_points = math.ceil(raw_distance / TICK) * TICK
    planned_one = stop_points * POINT_VALUE + ROUND_TRIP_ALLOWANCE
    extra = 2 * planned_one <= SLICE
    return dict(stop_points=float(stop_points), stop_points_exact=exact_text(stop_points),
        raw_stop_points=float(raw_distance), planned_risk_per_mes=float(planned_one),
        planned_two_mes_risk=float(2 * planned_one), extra_affordable=extra, qty_extra=int(extra),
        qty_policy=1 + int(extra), fixed_slice_usd=SLICE, native_RT_allowance_usd=float(ROUND_TRIP_ALLOWANCE),
        baseline_one_mes_always_retained=True, hard_loss_cap_claimed=False)


def build_five_minute_bars(minutes):
    """Observed native close labels -> midnight-aligned chart bars, no ffill.

    Each input is {date:ISO,minute:0..1439,open,high,low,close,volume,
    source_id}. Identical numeric duplicate observations collapse with every ID;
    contradictions are a whole-source error. Bucket00:00 belongs to the NEW day
    and contains prior-date23:56..23:59 plus native00:00 when observed.
    """
    selected = {}; duplicate_groups = []
    for index, row in enumerate(minutes):
        key = clock_key(row["date"], row["minute"])
        values = tuple(number(row[field]) for field in ("open", "high", "low", "close", "volume"))
        op, high, low, close, volume = values
        if any(value % TICK for value in values[:4]) or high < max(op, close, low) or low > min(op, close, high) or volume < 0:
            raise ValueError("Invalid native tick grid/OHLC/volume observation.")
        source_id = str(row.get("source_id", "synthetic_or_caller_row:" + str(index)))
        if key in selected:
            if selected[key]["values"] != values:
                raise ValueError("Contradictory duplicate native key; no first-row selection.")
            selected[key]["source_ids"].append(source_id)
            continue
        selected[key] = dict(values=values, source_ids=[source_id])
    buckets = defaultdict(list)
    for key, row in sorted(selected.items()):
        end = ((key + 4) // 5) * 5
        buckets[end].append((key, row))
        if len(row["source_ids"]) > 1:
            day, minute = split_clock(key)
            duplicate_groups.append(dict(date=day, minute=minute, source_ids=row["source_ids"]))
    bars = []
    for end, observations in sorted(buckets.items()):
        day, minute = split_clock(end); seen = {key for key, _ in observations}
        missing = [dict(date=split_clock(key)[0], minute=split_clock(key)[1]) for key in range(end - 4, end + 1) if key not in seen]
        bars.append(dict(date=day, minute=minute, open=float(observations[0][1]["values"][0]),
            high=float(max(row["values"][1] for _, row in observations)), low=float(min(row["values"][2] for _, row in observations)),
            close=float(observations[-1][1]["values"][3]), volume=float(sum(row["values"][4] for _, row in observations)),
            bar_id=day + ":C" + str(minute), observed_native_keys=[dict(date=split_clock(key)[0], minute=split_clock(key)[1]) for key, _ in observations],
            source_ids=[source_id for _, row in observations for source_id in row["source_ids"]],
            native_count=len(observations), missing_native_keys=missing, complete_five_minutes=not missing,
            exact_native_close_present=end in seen, first_observed_key=split_clock(observations[0][0]),
            last_observed_key=split_clock(observations[-1][0])))
    return dict(bars=bars, identical_duplicate_groups=duplicate_groups, input_rows=sum(len(row["source_ids"]) for row in selected.values()),
        unique_native_keys=len(selected), missing_buckets_filled=False, future_day_membership_used=False)


def reconstruct_parent(five_bars, *, calendar_auditor):
    """Literal observed-chart state and decision audits, with no trade outcomes.

    calendar_auditor(dayISO) MUST be the preregistered shared calendar callback.
    Fixtures pass an artificial callback; this module never imports a schedule.
    Output candidates are provisional until the caller admits every expected
    normal date, exact C1400/C1450/O1451 and held path through C1500. Missing
    observed dates cannot be discovered from observed bars alone.
    """
    bars = list(five_bars)
    keys = [clock_key(bar["date"], bar["minute"]) for bar in bars]
    if keys != sorted(set(keys)):
        raise ValueError("Five-minute bars must have unique chronological keys.")
    current = None; hi = low = close = None; previous_close = Fraction(0); previous_close_origin = None; reference = None
    day_bars = []; stored = []; tr_records = []; decisions = []; candidates = []; observed_dates = []; chart_presence = {}
    for bar in bars:
        day, minute = bar["date"], bar["minute"]
        if minute % 5 or any(field not in bar for field in ("bar_id", "complete_five_minutes", "exact_native_close_present", "source_ids")):
            raise ValueError("Use explicit audited midnight-aligned five-minute bars.")
        op, bh, bl, bc = (number(bar[field]) for field in ("open", "high", "low", "close"))
        if bh < max(op, bc, bl) or bl > min(op, bc, bh):
            raise ValueError("Invalid chart-bar OHLC.")
        if day != current:
            if current is not None and close > 0:
                if civil_day(current).weekday() < 5:
                    tr = max(hi, previous_close) - min(low, previous_close) if previous_close > 0 else hi - low
                    record = dict(reference_id="CT5M_TR:" + current, date=current, tr=float(tr), tr_exact=exact_text(tr),
                        previous_observed_date_close=float(previous_close), day_close=float(close),
                        previous_close_source=previous_close_origin,
                        chart_bar_ids=[item["bar_id"] for item in day_bars], chart_bars=len(day_bars),
                        partial_chart_bar_ids=[item["bar_id"] for item in day_bars if not item["complete_five_minutes"]],
                        complete_independent_daily_range_verified=False, ideal_1440_minute_history_inferred=False)
                    tr_records.append(record); stored.append((tr, record)); stored = stored[-ATR_DAYS:]
                # The DayClose>0 guard wraps THIS update too, including Sunday.
                previous_close = close
                previous_close_origin = dict(date=current, bar_id=day_bars[-1]["bar_id"], source_ids=day_bars[-1]["source_ids"])
            current = day; observed_dates.append(day); hi, low = bh, bl; reference = None; day_bars = []
            chart_presence[day] = dict(date=day, reference_state="NO_BAR", decision_state="NO_BAR",
                reference_exact_native_close_present=False, decision_exact_native_close_present=False)
        else:
            hi, low = max(hi, bh), min(low, bl)
        close = bc; day_bars.append(bar)
        atr = sum((value for value, _ in stored), Fraction(0)) / ATR_DAYS if len(stored) == ATR_DAYS else None
        if minute == REFERENCE_J:
            reference = bar
            chart_presence[day].update(reference_state="COMPLETE_EXACT" if bar["complete_five_minutes"] and bar["exact_native_close_present"] else "PARTIAL",
                reference_exact_native_close_present=bar["exact_native_close_present"])
        if minute != DECISION_J:
            continue
        chart_presence[day].update(decision_state="COMPLETE_EXACT" if bar["complete_five_minutes"] and bar["exact_native_close_present"] else "PARTIAL",
            decision_exact_native_close_present=bar["exact_native_close_present"])
        cal = calendar_audit(day, calendar_auditor(day))
        ref = number(reference["close"]) if reference is not None else None
        move = bc - ref if ref is not None else None
        # Literal guards RefPx>0 and ATRv>0; finite nonpositive native quotes
        # otherwise remain observed source state rather than a repair/deletion.
        literal_qualified = bool(not cal["literal"]["is_early_close"] and ref is not None and ref > 0 and atr is not None and atr > 0
            and abs(move) >= Fraction(3, 10) * atr)
        flags = []
        if reference is None: flags.append("MISSING_OBSERVED_REFERENCE_CHART_BAR_C1400")
        elif not reference["complete_five_minutes"] or not reference["exact_native_close_present"]: flags.append("PARTIAL_REFERENCE_OR_MISSING_EXACT_NATIVE_C1400")
        if not bar["complete_five_minutes"] or not bar["exact_native_close_present"]: flags.append("PARTIAL_DECISION_OR_MISSING_EXACT_NATIVE_C1450")
        if atr is None: flags.append("FEWER_THAN_15_STORED_WEEKDAY_CHART_TRS")
        audit = dict(date=day, decision_j=DECISION_J, dj=DECISION_J, entry_label_j=ENTRY_J, exit_j=EXIT_J,
            reference_close=float(ref) if ref is not None else None, decision_close=float(bc),
            move_points=float(move) if move is not None else None, atr=float(atr) if atr is not None else None,
            atr_exact=exact_text(atr) if atr is not None else None, atr_reference_ids=[record["reference_id"] for _, record in stored],
            atr_reference_source_limit_ids=[record["reference_id"] for _, record in stored if record["partial_chart_bar_ids"]],
            source_limit_complete_independent_ATR_ranges_unverified=True, literal_parent_qualified=literal_qualified,
            calendar=cal, source_flags=flags, reference_bar_id=reference["bar_id"] if reference is not None else None,
            reference_exact_native_close_present=reference["exact_native_close_present"] if reference is not None else False,
            decision_exact_native_close_present=bar["exact_native_close_present"],
            reference_source_ids=reference["source_ids"] if reference is not None else [], decision_bar_id=bar["bar_id"],
            decision_source_ids=bar["source_ids"], required_native_keys=[dict(date=day, minute=j) for j in (REFERENCE_J, DECISION_J, *range(ENTRY_J, EXIT_J + 1))],
            financial_source_admission_passed=False, exact_endpoint_or_held_prices_interpreted=False,
            one_consumed_decision_per_day=True, future_full_day_membership_used=False)
        if literal_qualified:
            audit.update(side=1 if move > 0 else -1, **affordability(atr))
        decisions.append(audit)
        if literal_qualified and cal["calendar_entry_allowed"]:
            candidates.append(audit)
    return dict(candidates=candidates, decision_audit=decisions, stored_TR_audit=tr_records, observed_dates=observed_dates,
        observed_date_coverage=list(chart_presence.values()),
        source_parameters=dict(commit=SOURCE_COMMIT, path=SOURCE_PATH, blob=SOURCE_BLOB, ATR_days=ATR_DAYS,
            decision_j=DECISION_J, reference_j=REFERENCE_J, entry_j=ENTRY_J, exit_j=EXIT_J,
            shared_calendar_dependencies=list(SHARED_CALENDAR_DEPENDENCIES)),
        expected_normal_date_coverage_is_callers_mandatory_gate=True, source_or_count_gate_passed=False,
        raw_stopped_or_account_returns_computed=False, economic_evaluations=0, gross_screen_runs=0)


def fixtures():
    """Invented observations only; no actual schedule/calendar/source values."""
    normal = lambda day: dict(kind="normal", cash_close_j=900, reason="ARTIFICIAL_FIXTURE_CALLBACK")
    def native(day, minute, op=100, high=101, low=99, close=100, source_id="artificial"):
        return dict(date=day, minute=minute, open=op, high=high, low=low, close=close, volume=1, source_id=source_id)
    rows = [native("2000-01-03", j) for j in range(1436, 1440)] + [native("2000-01-04", 0)]
    grouped = build_five_minute_bars(rows)
    assert len(grouped["bars"]) == 1 and grouped["bars"][0]["date"] == "2000-01-04" and grouped["bars"][0]["minute"] == 0
    assert grouped["bars"][0]["complete_five_minutes"] and grouped["bars"][0]["native_count"] == 5
    partial = build_five_minute_bars(rows[:-1])["bars"][0]
    assert not partial["complete_five_minutes"] and not partial["exact_native_close_present"] and partial["close"] == 100
    duplicate = build_five_minute_bars(rows + [dict(rows[0], source_id="second-identical")])
    assert len(duplicate["identical_duplicate_groups"]) == 1 and duplicate["unique_native_keys"] == 5
    try: build_five_minute_bars(rows + [dict(rows[0], close=100.25)])
    except ValueError: pass
    else: raise AssertionError("Conflicting duplicate accepted.")
    checks = ["newdate00bucket/prior2356to2359+00/noffill/partialflags/identicalduplicatesandconflictveto"]
    def five(day, minute, close=100, high=101, low=99, op=100):
        return dict(date=day, minute=minute, open=op, high=high, low=low, close=close, volume=5,
            bar_id=day + ":ART_C" + str(minute), complete_five_minutes=True, exact_native_close_present=True,
            source_ids=[day + ":ART" + str(minute)])
    # Artificial sparse observed bars deliberately do not claim full daily range.
    days = [date(2000, 2, 1) + timedelta(days=i) for i in range(40)]
    bars = [five(day.isoformat(), 600) for day in days]
    result = reconstruct_parent(bars, calendar_auditor=normal)
    assert all(civil_day(record["date"]).weekday() < 5 for record in result["stored_TR_audit"])
    assert all(not record["complete_independent_daily_range_verified"] for record in result["stored_TR_audit"])
    # A prior observed Sunday close changes Monday's TR previous-close baseline.
    sunday = date(2000, 2, 6)
    small = [five("2000-02-04", 600), five(sunday.isoformat(), 600, close=105, high=106, low=104, op=105),
        five("2000-02-07", 600), five("2000-02-08", 600)]
    tr = reconstruct_parent(small, calendar_auditor=normal)["stored_TR_audit"]
    assert tr[-1]["date"] == "2000-02-07" and tr[-1]["tr"] == 6 and tr[-1]["previous_observed_date_close"] == 105
    assert tr[-1]["previous_close_source"]["date"] == "2000-02-06"
    guarded = [five("2000-02-04", 600), five("2000-02-06", 600, close=-5, high=-4, low=-6, op=-5),
        five("2000-02-07", 600), five("2000-02-08", 600)]
    gtr = reconstruct_parent(guarded, calendar_auditor=normal)["stored_TR_audit"]
    assert gtr[-1]["previous_observed_date_close"] == 100 and gtr[-1]["tr"] == 2
    checks.append("weekday15TRobservedhistory/SundayPrevClose/DayClosePositiveguardwrapsPrevClose/noidealrangeclaim")
    # Warmup is entirely in the past; changing future same-date bars cannot size today's entry.
    decision_day = "2000-03-15"
    history = [five(day.isoformat(), 600) for day in days if day.isoformat() < decision_day]
    decision = [five(decision_day, 840), five(decision_day, 890, close=101, high=102)]
    out = reconstruct_parent(history + decision, calendar_auditor=normal)
    assert len(out["candidates"]) == 1 and out["candidates"][0]["side"] == 1 and out["candidates"][0]["atr"] == 2
    with_future = reconstruct_parent(history + decision + [five(decision_day, 1200, close=500, high=501, low=499, op=500)], calendar_auditor=normal)
    assert with_future["candidates"] == out["candidates"]
    short = reconstruct_parent(history + [five(decision_day, 840), five(decision_day, 890, close=99, low=98)], calendar_auditor=normal)
    assert short["candidates"][0]["side"] == -1
    missing_ref = reconstruct_parent(history + decision[1:], calendar_auditor=normal)
    assert not missing_ref["candidates"] and "MISSING_OBSERVED_REFERENCE_CHART_BAR_C1400" in missing_ref["decision_audit"][0]["source_flags"]
    partial_decision = dict(decision[-1], complete_five_minutes=False, exact_native_close_present=False)
    provisional = reconstruct_parent(history + [decision[0], partial_decision], calendar_auditor=normal)
    assert provisional["candidates"] and provisional["candidates"][0]["source_flags"] and not provisional["candidates"][0]["financial_source_admission_passed"]
    assert provisional["observed_date_coverage"][-1]["decision_state"] == "PARTIAL"
    assert result["observed_date_coverage"][-1]["decision_state"] == "NO_BAR"
    boundary_history = [five(day.isoformat(), 600, high=101, low=98.5) for day in days if day.isoformat() < decision_day]
    boundary = reconstruct_parent(boundary_history + [five(decision_day, 840), five(decision_day, 890, close=100.75)], calendar_auditor=normal)
    assert boundary["candidates"][0]["atr_exact"] == "5/2" and boundary["candidates"][0]["move_points"] == .75
    checks.append("Ref1400/Decision1450followbothsides/OPEN1451+C1500keys/futurebarinvariance/missingref+partialdecisionunresolved")
    skipped = reconstruct_parent(history + decision, calendar_auditor=lambda day: dict(kind="holiday", cash_close_j=None, reason="ARTIFICIAL"))
    assert not skipped["candidates"] and skipped["decision_audit"][0]["calendar"]["disposition"] == "SKIP_KNOWN_CALENDAR"
    assert literal_early_close("2000-11-24")["matching_source_clauses"] == ["NOV_FRIDAY"]
    assert not literal_early_close("2000-11-22")["is_early_close"]
    checks.append("literalholidaytrace+separateinjectedcashcalendar/noactualschedulegeneration")
    assert affordability(1)["stop_points"] == .25 and affordability(Fraction(1001, 1000))["stop_points"] == .5
    assert affordability(97)["qty_policy"] == 2 and affordability(Fraction(9701, 100))["qty_policy"] == 1
    assert affordability(1000)["qty_policy"] == 1 and not affordability(1000)["hard_loss_cap_claimed"]
    checks.append("quartertickconservativeceil/250fixedextraaffordability/1or2wholeMES/q1fallbacknotriskcap")
    return dict(passed=True, groups=len(checks), checks=checks, actual_input_header_schema_rows_or_schedule_accessed=False,
        raw_stopped_or_account_returns_computed=False, economic_evaluations=0, gross_screen_runs=0)


if __name__ == "__main__":
    import json
    if sys.argv[1:] != ["--fixtures"]:
        raise SystemExit("Pure SOURCE/SYNTHETIC helper only: use --fixtures; no actual-data command exists.")
    print(json.dumps(fixtures(), allow_nan=False))
