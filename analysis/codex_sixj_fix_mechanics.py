"""Synthetic mechanics only; no price/data/network input and no edge estimator."""
from datetime import date, datetime, time, timedelta, timezone
from decimal import Decimal, localcontext
from hashlib import sha256
import json
from pathlib import Path
from zoneinfo import ZoneInfo


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "agents/codex/research/sixj_fix_mechanics_test_plan.md"
OUT = ROOT / "analysis/outputs/codex_sixj_fix_mechanics/synthetic_checks.json"
D = Decimal


def reciprocal_change(spot_before, spot_after):
    """Toy inverse quotes only; actual futures include carry/basis and tick grids."""
    if spot_before <= 0 or spot_after <= 0:
        raise ValueError("positive quotes required")
    with localcontext() as ctx:
        ctx.prec = 45
        return D(1) / spot_after - D(1) / spot_before


def shifted_fixture_event(nominal, known_open):
    """Three-state, FICTIONAL bank calendar, not a Japanese holiday engine."""
    cursor = nominal
    while True:
        state = known_open.get(cursor)
        if state is None:
            return None
        if state:
            return cursor
        cursor -= timedelta(days=1)


def known_next_open(available_at, exact_opens):
    """No fabricated price: require a supplied exact open after availability."""
    return min((t for t in exact_opens if t > available_at), default=None)


def conditional_cost(fee, tick_value, adverse_ticks_per_fill):
    if fee < 0 or tick_value <= 0 or adverse_ticks_per_fill < 0:
        raise ValueError("invalid hypothetical execution assumptions")
    friction = 2 * tick_value * adverse_ticks_per_fill
    return fee + friction


def run_checks():
    records = []

    def check(name, predicate, detail):
        if not predicate:
            raise AssertionError(name)
        records.append({"name": name, "pass": True, "detail": detail})

    up = reciprocal_change(D("150"), D("151"))
    down = reciprocal_change(D("150"), D("149"))
    check("quote_inversion", up < 0 < down and
          reciprocal_change(D("150"), D("150")) == 0,
          "Toy USDJPY rise means USD-per-JPY falls: pre-fix premise SHORT6J.")
    try:
        reciprocal_change(D("0"), D("150"))
    except ValueError:
        invalid_rejected = True
    else:
        invalid_rejected = False
    check("invalid_quote", invalid_rejected, "Nonpositive quotes rejected.")

    # Arbitrary order units, not measured positions or a fitted impact model.
    residual = lambda imports, exports, prehedge: imports - exports - prehedge
    check("offsets_and_prehedging", residual(100, 100, 0) == 0 and
          residual(100, 0, 100) == 0 and residual(100, 120, 0) < 0,
          "Commercial purchases can coexist with zero/opposite residual demand.")
    check("no_necessary_reversal", (110 - 110) == 0 and (100 - 110) < 0,
          "Invented pressure index 100->110->110 has no reversal; 100->110->100 does.")

    clock_rows = []
    for tokyo_date, expected_ct, expected_zone in [
        ("2024-01-08", "2024-01-07T18:55:00-06:00", "CST"),
        ("2024-07-08", "2024-07-07T19:55:00-05:00", "CDT"),
        ("2024-03-08", "2024-03-07T18:55:00-06:00", "CST"),
        ("2024-03-11", "2024-03-10T19:55:00-05:00", "CDT"),
        ("2024-11-01", "2024-10-31T19:55:00-05:00", "CDT"),
        ("2024-11-04", "2024-11-03T18:55:00-06:00", "CST"),
        ("2024-01-01", "2023-12-31T18:55:00-06:00", "CST"),
    ]:
        jt = datetime.combine(date.fromisoformat(tokyo_date), time(9, 55),
                              tzinfo=ZoneInfo("Asia/Tokyo"))
        ct = jt.astimezone(ZoneInfo("America/Chicago"))
        utc = jt.astimezone(timezone.utc)
        check("clock_" + tokyo_date,
              ct.isoformat() == expected_ct and ct.tzname() == expected_zone
              and utc.hour == 0 and utc.minute == 55
              and ct.date() == jt.date() - timedelta(days=1),
              {"tokyo": jt.isoformat(), "chicago": ct.isoformat(), "utc": utc.isoformat()})
        clock_rows.append(ct)
    check("evening_not_empty_overnight_slot", all(c.hour in (18, 19) for c in clock_rows),
          "09:55JST is not the 01:00-03:00CT book gap. Actual occupancy unmeasured.")

    # These closures are invented. They deliberately do NOT encode JP holidays.
    base = date(2030, 1, 4)
    fictional = {base: True, **{base + timedelta(days=k): False for k in range(1, 7)}}
    shifted = {shifted_fixture_event(date(2030, 1, d), fictional) for d in (5, 10)}
    check("fictional_shift_deduplicates", shifted == {base},
          "Two nominal dates shifted to one synthetic open day are one event, not double size.")
    check("unknown_calendar_is_unknown", shifted_fixture_event(date(2030, 1, 5), {}) is None,
          "Missing calendar does not silently become a weekday-only calendar.")
    try:
        date(2030, 2, 30)
    except ValueError:
        invalid_date_rejected = True
    else:
        invalid_date_rejected = False
    check("invalid_nominal_date", invalid_date_rejected, "No fabricated February30/month-end event.")

    # Synthetic open timestamps; deliberately two seconds after the observed close.
    observed_close = datetime(2030, 1, 4, 9, 5, tzinfo=ZoneInfo("Asia/Tokyo"))
    available = observed_close + timedelta(seconds=2)
    supplied_opens = [observed_close, observed_close + timedelta(minutes=1)]
    check("receipt_before_fill", known_next_open(available, supplied_opens) == supplied_opens[1],
          "09:05:02 receipt cannot obtain the already elapsed09:05:00 open.")
    check("missing_exact_open", known_next_open(available, [observed_close]) is None,
          "Missing next open stays unavailable, no carry-forward/fabricated fill.")

    # ASSUMED standard-sized illustration; not verified product spec or current fees.
    multiplier, tick = D("12500000"), D("0.0000005")
    tick_value = multiplier * tick
    fee = D("4.00")
    rt = conditional_cost(fee, tick_value, D(1))
    stress = conditional_cost(fee, tick_value, D(2))
    check("two_sided_conditional_cost", tick_value == D("6.25") and
          rt == D("16.50") and stress == D("29.00"),
          "ASSUMED $4RTfee + one adverse tick per fill=$16.50RT; two=$29.00RT.")
    with localcontext() as ctx:
        ctx.prec = 45
        assumed_s0 = D(150)
        required_s1 = 1 / (1 / assumed_s0 - 2 * rt / multiplier)
        spot_pips = (required_s1 - assumed_s0) / D("0.01")
    check("conditional_gross_hurdle", 2 * rt == D(33) and D("5.94") < spot_pips < D("5.95"),
          {"gross_2x_RT_USD": str(2 * rt), "approx_toy_spot_pips": str(spot_pips),
           "assumptions_only": True, "native_micro_rescaling_authorized": False})
    return records


def main():
    checks = run_checks()
    payload = {
        "task": "manual_post_budget_6j_mechanics_only",
        "input_kind": "invented values and fictional calendar; no empirical financial inputs",
        "script_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
        "plan_sha256": sha256(PLAN.read_bytes()).hexdigest(),
        "checks_passed": len(checks), "checks": checks,
        "economic_evaluations_added": 0, "gross_screens_added": 0, "hypotheses_added": 0,
        "strategy_edge_measured": False, "new_market_data_or_native_spec_admitted": False,
        "verdict": "MECHANICAL_CONSISTENCY_ONLY; NEEDS_DATA_AND_SOURCE_CONFIRMATION",
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("x") as f:
        json.dump(payload, f, indent=2)
        f.write("\n")
    print(json.dumps({"passed": len(checks), "output": str(OUT.relative_to(ROOT)),
                      "economic_results": "NONE"}))


if __name__ == "__main__":
    main()
