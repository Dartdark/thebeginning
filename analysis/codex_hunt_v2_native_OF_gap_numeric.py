"""I03 pure same-key numeric concordance; never reads market data or files.

Only the outer committed intake may supply its prebound raw selected rows.
There are no timestamps, inter-key operations, prices-to-returns or signals.
Exactly equal finite Decimal tuples collapse once, including format variants.
Contradictory/invalid duplicates stay unresolved; all raw formats/IDs remain.
"""
from __future__ import annotations

from decimal import Decimal, InvalidOperation, localcontext
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import re

PRICE_FIELDS = ("open", "high", "low", "close")
FIELDS = {"native": (*PRICE_FIELDS, "volume"), "OF": (*PRICE_FIELDS, "volume", "upvol", "downvol")}
ASCII_SPACE = " \t\r\n\v\f"
NUMBER_RE = re.compile(r"^[+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[eE][+-]?[0-9]+)?$")
TICK = Fraction(1, 4)


def decimal_value(raw):
    if not isinstance(raw, str):
        raise ValueError("Selected fields must remain raw CSV strings.")
    text = raw.strip(ASCII_SPACE)
    if NUMBER_RE.fullmatch(text) is None:
        raise ValueError("Not a strict ASCII decimal/exponent number.")
    number = Decimal(text)
    if not number.is_finite():
        raise ValueError("Selected number must be finite.")
    return number


def exact_text(value):
    """Exact JSON-safe decimal for finite-decimal Fraction calculations."""
    fraction = value if isinstance(value, Fraction) else Fraction(value)
    numerator, denominator = fraction.numerator, fraction.denominator
    # All calculations are sums/differences of Decimals and division by.25.
    # A base10 representation is exact at this precision; no numeric repair.
    with localcontext() as context:
        context.prec = max(28, len(str(abs(numerator))) + len(str(denominator)) + 4)
        return str(Decimal(numerator) / Decimal(denominator))


def _numeric_selected(raw, kind):
    values, issues = {}, []
    for name in FIELDS[kind]:
        try:
            values[name] = decimal_value(raw[name])
        except (ValueError, TypeError, InvalidOperation):
            values[name] = None
            issues.append(dict(field=name, issue="invalid_or_nonfinite_ASCII_number"))
    numeric_complete = all(value is not None for value in values.values())
    price_complete = all(values[name] is not None for name in PRICE_FIELDS)
    quantities = FIELDS[kind][4:]
    quantity_complete = all(values[name] is not None for name in quantities)
    for name in PRICE_FIELDS:
        number = values[name]
        if number is None:
            continue
        if number <= 0:
            issues.append(dict(field=name, issue="OHLC_not_positive"))
        if (Fraction(number) / TICK).denominator != 1:
            issues.append(dict(field=name, issue="OHLC_off_quarter_point_tick"))
    if price_complete:
        op, hi, lo, close = (values[name] for name in PRICE_FIELDS)
        if hi < lo:
            issues.append(dict(field="high,low", issue="high_below_low"))
        if lo > min(op, close):
            issues.append(dict(field="low", issue="low_above_open_or_close"))
        if hi < max(op, close):
            issues.append(dict(field="high", issue="high_below_open_or_close"))
    for name in quantities:
        if values[name] is not None and values[name] < 0:
            issues.append(dict(field=name, issue="quantity_negative"))
    alias = None
    auxiliary = None
    if kind == "OF" and values["volume"] is not None and values["upvol"] is not None:
        alias = values["volume"] == values["upvol"]
        if not alias:
            issues.append(dict(field="volume,upvol", issue="OF_volume_alias_not_equal_upvol"))
    if kind == "OF" and values["upvol"] is not None and values["downvol"] is not None:
        auxiliary = exact_text(Fraction(values["upvol"]) + Fraction(values["downvol"]))
    return dict(values={name: str(value) if value is not None else None for name, value in values.items()},
        numeric_complete=numeric_complete, valid=not issues, issues=issues,
        OHLC_numeric_complete=price_complete, quantity_numeric_complete=quantity_complete,
        any_zero_OHLC=any(values[name] == 0 for name in PRICE_FIELDS if values[name] is not None),
        all_zero_OHLC=price_complete and all(values[name] == 0 for name in PRICE_FIELDS),
        zero_quantity_fields=[name for name in quantities if values[name] is not None and values[name] == 0],
        OF_volume_alias_pass=alias, OF_auxiliary_up_plus_down_total=auxiliary)


def parse_selected_group(rows, kind):
    """Same-key rows only; exact Decimal duplicate semantics, every ID retained."""
    if kind not in FIELDS:
        raise ValueError("kind must be exactly native or OF.")
    if not isinstance(rows, list) or not rows:
        raise ValueError("A selected group must contain one or more raw source rows.")
    fields = FIELDS[kind]
    selected, structural = [], []
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            structural.append(dict(group_row=index, issue="source_row_not_dict")); continue
        source_id = row.get("source_id")
        if not isinstance(source_id, str) or not source_id:
            structural.append(dict(group_row=index, issue="missing_exact_source_id"))
        raw = {name: row.get(name) for name in fields}
        if any(not isinstance(raw[name], str) for name in fields):
            structural.append(dict(group_row=index, source_id=source_id, issue="missing_or_nonstring_selected_field"))
        selected.append(dict(source_id=source_id, **raw))
    source_ids = [row.get("source_id") for row in selected]
    if len(source_ids) != len(set(value for value in source_ids if isinstance(value, str))):
        structural.append(dict(issue="duplicate_or_invalid_source_ID"))
    base = dict(kind=kind, source_ids=source_ids, raw_selected_rows=selected,
        selected_fields=list(fields), input_source_rows=len(rows), duplicate_excess_rows=max(0, len(rows) - 1),
        raw_duplicate_policy="Exactly equal finite Decimal selected tuples collapse once; no tolerance; every raw format and source ID retained; invalid/contradictory duplicates unresolved.",
        no_temporal_or_return_operations=True)
    if structural:
        return dict(**base, status="UNRESOLVED_STRUCTURE", resolved=False, valid=False, numeric_complete=False,
            values=None, distinct_raw_variants=None, issues=structural, variants=[])
    variants = {}
    for row in selected:
        key = tuple(row[name] for name in fields)
        if key not in variants:
            variants[key] = dict(raw_selected={name: row[name] for name in fields}, source_ids=[])
        variants[key]["source_ids"].append(row["source_id"])
    parsed = []
    for variant in variants.values():
        parsed.append(dict(**variant, **_numeric_selected(variant["raw_selected"], kind)))
    complete = all(variant["numeric_complete"] for variant in parsed)
    tuples = {tuple(Decimal(variant["values"][name]) for name in fields) for variant in parsed} if complete else set()
    if len(rows) > 1 and (not complete or len(tuples) != 1):
        issue = "invalid_selected_duplicates_unresolved" if not complete else "contradictory_exact_Decimal_selected_tuples"
        return dict(**base, status="DUPLICATE_INVALID" if not complete else "DUPLICATE_CONFLICT", resolved=False, valid=False,
            numeric_complete=False, values=None, distinct_raw_variants=len(parsed),
            distinct_numeric_variants=len(tuples) if complete else None, format_variation=len(parsed) > 1,
            issues=[dict(issue=issue)], variants=parsed)
    variant = parsed[0]
    return dict(**base, status="VALID" if variant["valid"] else "INVALID_SELECTED_FIELDS", resolved=True,
        valid=variant["valid"], numeric_complete=variant["numeric_complete"], values=variant["values"],
        distinct_raw_variants=len(parsed), distinct_numeric_variants=1 if complete else None,
        format_variation=len(parsed) > 1, issues=variant["issues"], variants=parsed,
        OHLC_numeric_complete=variant["OHLC_numeric_complete"], quantity_numeric_complete=variant["quantity_numeric_complete"],
        any_zero_OHLC=variant["any_zero_OHLC"], all_zero_OHLC=variant["all_zero_OHLC"],
        zero_quantity_fields=variant["zero_quantity_fields"], OF_volume_alias_pass=variant["OF_volume_alias_pass"],
        OF_auxiliary_up_plus_down_total=variant["OF_auxiliary_up_plus_down_total"])


def compare_groups(native_group, of_group):
    """Compare one fixed same-key pair; no key/clock or cross-time operation."""
    if native_group.get("kind") != "native" or of_group.get("kind") != "OF":
        raise ValueError("Pair must be native then OF.")
    resolved = all(group.get("resolved") for group in (native_group, of_group))
    ohlc_comparable = resolved and all(group.get("OHLC_numeric_complete") for group in (native_group, of_group))
    quantity_comparable = resolved and all(group.get("quantity_numeric_complete") for group in (native_group, of_group))
    comparable = ohlc_comparable and quantity_comparable
    result = dict(native_source_ids=native_group.get("source_ids", []), OF_source_ids=of_group.get("source_ids", []),
        comparable=bool(comparable), OHLC_comparable=bool(ohlc_comparable), quantity_comparable=bool(quantity_comparable),
        both_valid=bool(native_group.get("valid") and of_group.get("valid")),
        per_field={field: dict(exact=None, abs_error_ticks=None, within_one_tick=None) for field in PRICE_FIELDS},
        exact_OHLC_tuple=None, within_one_tick_OHLC_tuple=None,
        native_volume_equals_OF_aux_total=None, OF_alias_pass=of_group.get("OF_volume_alias_pass"),
        native_volume=None, OF_auxiliary_up_plus_down_total=of_group.get("OF_auxiliary_up_plus_down_total"),
        mismatch_source_ids=[], issues=[], diagnostic_one_tick_is_not_admission=True,
        no_temporal_or_return_operations=True)
    if not resolved:
        result["issues"].append("unresolved_duplicate_or_invalid_numeric_group;no_pair_value_chosen")
        result["mismatch_source_ids"] = list(result["native_source_ids"]) + list(result["OF_source_ids"])
        return result
    n, f = native_group["values"], of_group["values"]
    for field in PRICE_FIELDS:
        if n[field] is None or f[field] is None:
            result["per_field"][field] = dict(exact=None, abs_error_ticks=None, within_one_tick=None)
            continue
        left, right = Decimal(n[field]), Decimal(f[field])
        ticks = abs(Fraction(left) - Fraction(right)) / TICK
        result["per_field"][field] = dict(exact=left == right, abs_error_ticks=exact_text(ticks), within_one_tick=ticks <= 1)
    if ohlc_comparable:
        result["exact_OHLC_tuple"] = all(v["exact"] for v in result["per_field"].values())
        result["within_one_tick_OHLC_tuple"] = all(v["within_one_tick"] for v in result["per_field"].values())
    if n["volume"] is not None:
        result["native_volume"] = n["volume"]
    if n["volume"] is not None and f["upvol"] is not None and f["downvol"] is not None:
        native_volume = Decimal(n["volume"])
        auxiliary = Fraction(Decimal(f["upvol"])) + Fraction(Decimal(f["downvol"]))
        result["OF_auxiliary_up_plus_down_total"] = exact_text(auxiliary)
        result["native_volume_equals_OF_aux_total"] = Fraction(native_volume) == auxiliary
    if not comparable:
        result["issues"].append("partial_numeric_comparison;missing_fields_remainunknown")
    if not result["both_valid"]:
        result["issues"].append("selected_field_integrity_invalid;comparison_not_data_admission")
    if not result["exact_OHLC_tuple"] or not result["native_volume_equals_OF_aux_total"] or result["OF_alias_pass"] is not True or not result["both_valid"]:
        result["mismatch_source_ids"] = list(result["native_source_ids"]) + list(result["OF_source_ids"])
    return result


def fixtures():
    def native(source_id="N", **changes):
        return dict(source_id=source_id, open="100", high="101", low="99", close="100.25", volume="100", **changes)
    def row(kind, source_id, **changes):
        values = dict(source_id=source_id, open="100", high="101", low="99", close="100.25", volume="100" if kind == "native" else "60")
        if kind == "OF": values.update(upvol="60", downvol="40")
        values.update(changes)
        return values
    n, f = parse_selected_group([row("native", "N")], "native"), parse_selected_group([row("OF", "F")], "OF")
    exact = compare_groups(n, f)
    assert exact["comparable"] and exact["both_valid"] and exact["exact_OHLC_tuple"] and exact["native_volume_equals_OF_aux_total"]
    assert exact["OF_auxiliary_up_plus_down_total"] == "100" and f["values"]["volume"] == "60"
    altered = compare_groups(n, parse_selected_group([row("OF", "F", high="101.25")], "OF"))
    assert altered["per_field"]["close"]["exact"] and not altered["exact_OHLC_tuple"] and altered["within_one_tick_OHLC_tuple"]
    assert altered["per_field"]["high"]["abs_error_ticks"] == "1" and altered["mismatch_source_ids"] == ["N", "F"]
    distant = compare_groups(n, parse_selected_group([row("OF", "F", open="100.5")], "OF"))
    assert not distant["within_one_tick_OHLC_tuple"]
    identical = parse_selected_group([row("native", "N1"), row("native", "N2")], "native")
    assert identical["valid"] and identical["distinct_raw_variants"] == 1 and identical["source_ids"] == ["N1", "N2"]
    conflict = parse_selected_group([row("native", "N1"), row("native", "N2", high="101.25")], "native")
    assert not conflict["resolved"] and conflict["values"] is None and len(conflict["variants"]) == 2
    formats = parse_selected_group([row("native", "N1"), row("native", "N2", open="100.0")], "native")
    assert formats["resolved"] and formats["valid"] and formats["format_variation"] and formats["distinct_numeric_variants"] == 1
    invalid_duplicates = parse_selected_group([row("native", "N1", open="NaN"), row("native", "N2", open="NaN")], "native")
    assert not invalid_duplicates["resolved"] and invalid_duplicates["status"] == "DUPLICATE_INVALID"
    conflict_comparison = compare_groups(conflict, f)
    assert not conflict_comparison["comparable"]
    assert tuple(conflict_comparison["per_field"]) == PRICE_FIELDS
    assert all(value == dict(exact=None, abs_error_ticks=None, within_one_tick=None)
        for value in conflict_comparison["per_field"].values())
    for bad in ("NaN", "Infinity", "1,000", "１００", "", "1_000", None, True):
        invalid = parse_selected_group([row("native", "N", open=bad)], "native")
        assert not invalid["valid"] and not invalid["numeric_complete"]
    assert decimal_value(" \t1.0025e2\r\n") == Decimal("100.25")
    zero = parse_selected_group([row("native", "N", open="0", high="0", low="0", close="0", volume="0")], "native")
    assert not zero["valid"] and zero["all_zero_OHLC"] and zero["zero_quantity_fields"] == ["volume"]
    off_tick = parse_selected_group([row("native", "N", close="100.1")], "native")
    assert not off_tick["valid"] and any(v["issue"] == "OHLC_off_quarter_point_tick" for v in off_tick["issues"])
    geometry = parse_selected_group([row("native", "N", low="100.5")], "native")
    assert not geometry["valid"]
    negative = parse_selected_group([row("OF", "F", downvol="-1")], "OF")
    assert not negative["valid"] and negative["OF_auxiliary_up_plus_down_total"] == "59"
    alias = parse_selected_group([row("OF", "F", volume="100")], "OF")
    assert not alias["valid"] and alias["OF_volume_alias_pass"] is False
    alias_comparison = compare_groups(n, alias)
    assert alias_comparison["native_volume_equals_OF_aux_total"] and not alias_comparison["both_valid"]
    quantity = compare_groups(n, parse_selected_group([row("OF", "F", downvol="39")], "OF"))
    assert not quantity["native_volume_equals_OF_aux_total"] and quantity["exact_OHLC_tuple"]
    incomplete_quantity = parse_selected_group([row("OF", "F", downvol="NaN", volume="-1")], "OF")
    assert any(v["field"] == "volume" and v["issue"] == "quantity_negative" for v in incomplete_quantity["issues"])
    partial = compare_groups(n, incomplete_quantity)
    assert partial["OHLC_comparable"] and partial["exact_OHLC_tuple"] and not partial["comparable"]
    duplicate_id = parse_selected_group([row("native", "N"), row("native", "N")], "native")
    assert duplicate_id["status"] == "UNRESOLVED_STRUCTURE"
    json.dumps([n, f, altered, conflict, formats, zero, alias_comparison], allow_nan=False)
    return dict(passed=True, real_input_or_CSV_rows_read=False, temporal_or_return_operations=False,
        checks=["same-key exactOHLC and nativevolume vs OFauxiliarysum", "sameclose/differenthigh retainedperfield",
            "quarterpointabsdiff and <=1tickdiagnostic", "exactDecimalduplicates collapseonce allrawformats/IDs",
            "numericformatequivalents collapse; contradictory/invalidduplicates unresolved", "strictfiniteASCII decimal/exponent andwhitespace",
            "zero/invalid/geometry/tickstates retained", "OFvolumealias distinct fromauxiliarytotal",
            "quantitynegative/mismatch and allmismatchIDs; partialfieldcomparisonsretainunknowns", "sourceIDambiguityfatal/JSONsafevalues"],
        script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())


if __name__ == "__main__":
    result = fixtures()
    output = Path(__file__).resolve().parent / "outputs/codex_hunt_v2_native_OF_gap_intake" / f"numeric_synthetic_checks_{result['script_sha256'][:12]}.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("x") as handle:
        json.dump(result, handle, indent=2, allow_nan=False); handle.write("\n")
    print(json.dumps(result, allow_nan=False))
