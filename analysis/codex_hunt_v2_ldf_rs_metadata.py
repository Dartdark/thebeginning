"""H07 selected owned-RS metadata only, raw XLSX ZIP/XML and pure fixtures.

Import reads no workbook. Runtime reads Date DAY before any other row value;
out-of-design rows never expose Time/Type/Signal/IDs/entryPrice/Contracts.
Exit Price and all outcome cells are never decoded. A malformed selected event
stream vetoes the whole source before the caller may compute any feature.
"""
from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal, InvalidOperation, localcontext
from fractions import Fraction
import hashlib
import io
import json
from pathlib import Path
import posixpath
import re
import xml.etree.ElementTree as ET
import zipfile

NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
REL = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"
CELL_RE = re.compile(r"^([A-Z]+)([1-9][0-9]*)$")
NUMBER_RE = re.compile(r"^[+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[eE][+-]?[0-9]+)?$")
DATE_RE = re.compile(r"^(?:([0-9]{4})-([0-9]{2})-([0-9]{2})|([0-9]{1,2})/([0-9]{1,2})/([0-9]{4}))(?:[ T]([0-9]{1,2}):([0-9]{2})(?::([0-9]{2})(?:\.([0-9]{1,9}))?)?(?: (AM|PM))?)?$")
ASCII_SPACE = " \t\r\n\v\f"
DESIGN_YEARS = tuple(range(2018, 2023))
WORKBOOK_SHA256 = "6cc3bedab9b44a0598339c177eaa2933bf0c0e01de29af1fe3a6b4f1ade69977"
TIME_TOLERANCE_SECONDS = Fraction(1, 10000)
HEADER = {"A": "Trade #", "B": "Order #", "C": "Type", "D": "Signal", "E": "Date", "F": "Time", "G": "Price", "H": "Contracts"}
SETTING_KEYS = ("Symbol Name", "Compression", "Start Date", "End Date", "TradeDir", "NumContracts", "DecideHHMM", "FlatHHMM", "RthStartHHMM", "RthEndHHMM", "ZMin", "BetaDays", "StopFrac", "TgtFrac", "AtrDays", "SkipHolidays")
EXPECTED_NUMERIC_SETTINGS = dict(TradeDir="0", NumContracts="1", DecideHHMM="900", FlatHHMM="1500", RthStartHHMM="830", RthEndHHMM="1500", ZMin="1.25", BetaDays="20", StopFrac="0.6", TgtFrac="1.0", AtrDays="20")


def _xml(raw):
    if b"<!DOCTYPE" in raw.upper() or b"<!ENTITY" in raw.upper():
        raise ValueError("DTD/entities are forbidden in workbook metadata.")
    return ET.fromstring(raw)


def _decimal(raw):
    if not isinstance(raw, str) or NUMBER_RE.fullmatch(raw) is None:
        raise ValueError("Expected strict ASCII finite decimal metadata.")
    value = Decimal(raw)
    if not value.is_finite():
        raise ValueError("Nonfinite selected metadata number.")
    return value


def _positive_integer(raw):
    value = _decimal(raw)
    if value <= 0 or value != value.to_integral_value():
        raise ValueError("ID/quantity must be an exact positive integer; no truncation.")
    return int(value)


def date_day(raw):
    """Numeric1900-system Date is interpreted as DAY before any Time value."""
    value = _decimal(raw)
    if value < 1:
        raise ValueError("Excel1900 Date serial must be positive.")
    integer = int(value)  # Deliberate documented Excel day component, not ID repair.
    if integer == 60:
        raise ValueError("Excel's fictitious1900-02-29 is not a real date.")
    # Exact Excel1900 day convention; source design dates are well after1900.
    base = date(1899, 12, 31) if integer < 60 else date(1899, 12, 30)
    day = base + timedelta(days=integer)
    fraction = Fraction(value) - integer
    return dict(day=day, date_integer=integer, date_fraction=fraction, raw_date=raw)


def reconcile_clock(date_info, raw_time):
    value = _decimal(raw_time)
    if value < 0:
        raise ValueError("Excel Time cannot be negative.")
    integer = int(value)
    fraction = Fraction(value) - integer
    if integer and integer != date_info["date_integer"]:
        raise ValueError("Nonzero Time day component differs from Date day component.")
    if date_info["date_fraction"] and abs(date_info["date_fraction"] - fraction) * 86400 > TIME_TOLERANCE_SECONDS:
        raise ValueError("Nonzero Date fractional clock differs from Time fraction.")
    minutes = fraction * 1440
    nearest = (minutes.numerator * 2 + minutes.denominator) // (2 * minutes.denominator)
    error_seconds = abs(minutes - nearest) * 60
    if not 0 <= nearest < 1440 or error_seconds > TIME_TOLERANCE_SECONDS:
        raise ValueError("Time is not an exact minute within fixed1e-4second representation tolerance.")
    if date_info["date_fraction"]:
        date_minutes = date_info["date_fraction"] * 1440
        if abs(date_minutes - nearest) * 60 > TIME_TOLERANCE_SECONDS:
            raise ValueError("Date fractional clock does not identify the same exact minute.")
    return dict(minute=int(nearest), raw_date=date_info["raw_date"], raw_time=raw_time,
        date_integer=date_info["date_integer"], time_integer=integer,
        date_fraction=str(date_info["date_fraction"]), time_fraction=str(fraction),
        minute_error_seconds=str(error_seconds), exact_minute_tolerance_seconds="0.0001")


class SelectedStrings:
    def __init__(self, archive):
        self.archive, self.cache = archive, {}

    def get(self, index_raw):
        if re.fullmatch(r"[0-9]+", index_raw) is None:
            raise ValueError("Invalid selected shared-string index.")
        index = int(index_raw)
        if index in self.cache:
            return self.cache[index]
        if "xl/sharedStrings.xml" not in self.archive.namelist():
            raise ValueError("Shared-string table absent.")
        with self.archive.open("xl/sharedStrings.xml") as handle:
            found = -1
            for _, element in ET.iterparse(handle, events=("end",)):
                if element.tag != NS + "si": continue
                found += 1
                if found == index:
                    value = "".join(item.text or "" for item in element.iter(NS + "t"))
                    self.cache[index] = value
                    return value
                element.clear()
        raise ValueError("Selected shared-string index absent.")


def _cell(cell, strings, numeric_required=False, expected_style=None):
    if cell is None:
        raise ValueError("Required selected cell absent.")
    if cell.find(NS + "f") is not None:
        raise ValueError("Selected source cells may not contain formulas.")
    vs, ins = cell.findall(NS + "v"), cell.findall(NS + "is")
    if len(vs) > 1 or len(ins) > 1 or (vs and ins):
        raise ValueError("Ambiguous multiple selected cell values.")
    kind = cell.get("t", "n")
    if expected_style is not None and cell.get("s") != str(expected_style):
        raise ValueError("Selected Date/Time style differs from frozen source schema.")
    if numeric_required and kind != "n":
        raise ValueError("Frozen selected Date/Time must be numeric Excel cells.")
    if kind == "inlineStr": return "".join(item.text or "" for item in cell.iter(NS + "t")), False
    raw = "" if not vs or vs[0].text is None else vs[0].text
    if kind == "s": return strings.get(raw), False
    if kind in ("str", "d"): return raw, False
    if kind == "n": return raw, True
    if kind == "b": return raw, False
    raise ValueError("Unsupported selected cell type.")


def _rows(archive, location):
    seen = set()
    with archive.open(location) as handle:
        for _, element in ET.iterparse(handle, events=("end",)):
            if element.tag != NS + "row": continue
            raw_row = element.get("r", "")
            if re.fullmatch(r"[1-9][0-9]*", raw_row) is None or int(raw_row) in seen:
                raise ValueError("Missing/noncanonical/duplicate worksheet row coordinate.")
            row = int(raw_row); seen.add(row); cells = {}
            for cell in element.findall(NS + "c"):
                match = CELL_RE.fullmatch(cell.get("r", ""))
                if match is None or int(match.group(2)) != row or match.group(1) in cells:
                    raise ValueError("Missing/mismatched/duplicate selected worksheet cell coordinate.")
                cells[match.group(1)] = cell
            yield row, cells
            element.clear()


def _locations(archive):
    if len(archive.namelist()) != len(set(archive.namelist())):
        raise ValueError("Duplicate workbook ZIP members.")
    book = _xml(archive.read("xl/workbook.xml"))
    props = book.find(NS + "workbookPr")
    if props is not None and props.get("date1904", "0") not in ("0", "false"):
        raise ValueError("Frozen owned workbook requires Excel1900 system.")
    relationships = _xml(archive.read("xl/_rels/workbook.xml.rels"))
    result = {}
    for expected_name, expected_member in (("List of Trades", "xl/worksheets/sheet3.xml"), ("Settings", "xl/worksheets/sheet8.xml")):
        sheets = [item for item in book.iter(NS + "sheet") if item.get("name") == expected_name]
        if len(sheets) != 1: raise ValueError("Required unique owned sheet missing:" + expected_name)
        identifier = sheets[0].get(REL + "id")
        hits = [item for item in relationships if item.get("Id") == identifier]
        if len(hits) != 1 or hits[0].get("TargetMode") == "External":
            raise ValueError("Required sheet relationship is ambiguous/external.")
        target = hits[0].get("Target", "")
        location = posixpath.normpath(target.lstrip("/")) if target.startswith("/") else posixpath.normpath(posixpath.join("xl", target))
        if location != expected_member or location not in archive.namelist():
            raise ValueError("Sheet member differs from source-only frozen inventory.")
        result[expected_name] = location
    styles = _xml(archive.read("xl/styles.xml"))
    xfs = styles.find(NS + "cellXfs")
    if xfs is None or len(xfs) <= 8 or xfs[7].get("numFmtId") != "14" or xfs[8].get("numFmtId") != "21":
        raise ValueError("Frozen Date7/14 and Time8/21 style definitions differ.")
    return result


def _fraction_decimal(value):
    with localcontext() as context:
        context.prec = max(30, len(str(abs(value.numerator))) + len(str(value.denominator)) + 5)
        return Decimal(value.numerator) / Decimal(value.denominator)


def _setting_bound(raw, numeric):
    """Preserve full Settings interval; no date-only truncation/clock fitting."""
    if numeric:
        info = date_day(raw)
        day, seconds = info["day"], info["date_fraction"] * 86400
        codec = "Excel1900fullserial;fullfractionretained"
    else:
        match = DATE_RE.fullmatch(raw)
        if match is None: raise ValueError("Settings coverage timestamp is not frozen ISO/US optional-clock codec.")
        y, m, d, um, ud, uy, h, minute, second, digits, ampm = match.groups()
        day = date(int(y or uy), int(m or um), int(d or ud))
        hour, minute, second = int(h or 0), int(minute or 0), int(second or 0)
        if ampm:
            if not 1 <= hour <= 12: raise ValueError("Invalid Settings AM/PM hour.")
            hour = hour % 12 + (12 if ampm == "PM" else 0)
        if not (0 <= hour < 24 and 0 <= minute < 60 and 0 <= second < 60):
            raise ValueError("Invalid Settings full clock.")
        seconds = Fraction(hour * 3600 + minute * 60 + second) + (Fraction(Decimal("0." + digits)) if digits else 0)
        codec = "ISO/USdatewithoptional24hourorAMPMclock;fullprecisionretained"
    whole = int(seconds)
    fraction = seconds - whole
    suffix = format(_fraction_decimal(fraction), "f").split(".", 1)[1].rstrip("0") if fraction else ""
    timestamp = f"{day.isoformat()}T{whole // 3600:02d}:{whole % 3600 // 60:02d}:{whole % 60:02d}" + ("." + suffix if suffix else "")
    return dict(raw=raw, codec=codec, timestamp=timestamp, date=day.isoformat(), day_ordinal=day.toordinal(),
        seconds_numerator=str(seconds.numerator), seconds_denominator=str(seconds.denominator),
        source_timezone_assumption="reportexchangeCT;notverifiedbrokerreceipt")


def _bound_key(bound):
    return Fraction(bound["day_ordinal"] * 86400) + Fraction(int(bound["seconds_numerator"]), int(bound["seconds_denominator"]))


def timestamp_within_coverage(settings, date_iso, minute):
    """Exact rational full-timestamp interval test, no datetime truncation."""
    if int(minute) != minute or not 0 <= minute < 1440:
        raise ValueError("Coverage query must use an exact valid minute label.")
    instant = Fraction(date.fromisoformat(date_iso).toordinal() * 86400 + int(minute) * 60)
    return _bound_key(settings["supported_start_exact"]) <= instant <= _bound_key(settings["supported_end_exact"])


def _settings(archive, location, strings):
    found, faults = {}, []
    for row_id, cells in _rows(archive, location):
        if "A" not in cells: continue
        key, _ = _cell(cells["A"], strings)
        if key not in SETTING_KEYS: continue  # No nonallowlisted B value is decoded.
        if key in found:
            faults.append(dict(source_row_id=row_id, issue="duplicate_required_Settings_key", key=key)); continue
        try:
            raw, numeric = _cell(cells.get("B"), strings)
            found[key] = dict(raw=raw, numeric=numeric, source_cell=f"B{row_id}")
        except (ValueError, InvalidOperation) as exc:
            faults.append(dict(source_row_id=row_id, key=key, issue=str(exc)))
    for key in SETTING_KEYS:
        if key not in found: faults.append(dict(issue="missing_required_Settings_key", key=key))
    start = end = None
    if not faults:
        try:
            if found["Symbol Name"]["raw"].strip(ASCII_SPACE) not in ("@NQ", "@NQ#C"):
                raise ValueError("Settings Symbol Name does not support frozen NQ source identity.")
            if re.sub(r"[ \t\r\n\v\f]+", "", found["Compression"]["raw"]) not in ("1Minute", "1Minutes"):
                raise ValueError("Settings Compression is not frozen1Minute.")
            for key, expected in EXPECTED_NUMERIC_SETTINGS.items():
                if _decimal(found[key]["raw"].strip(ASCII_SPACE)) != Decimal(expected):
                    raise ValueError("Noncanonical current RS setting:" + key)
            if found["SkipHolidays"]["raw"].strip(ASCII_SPACE).lower() not in ("true", "1"):
                raise ValueError("Canonical RS SkipHolidays must be true.")
            start = _setting_bound(found["Start Date"]["raw"], found["Start Date"]["numeric"])
            end = _setting_bound(found["End Date"]["raw"], found["End Date"]["numeric"])
            if _bound_key(start) > _bound_key(end): raise ValueError("Settings source coverage is reversed.")
        except (ValueError, TypeError, InvalidOperation, OverflowError) as exc:
            faults.append(dict(issue=str(exc)))
    return dict(passed=not faults, selected_settings=found, issues=faults,
        supported_start=start["timestamp"] if start else None, supported_end=end["timestamp"] if end else None,
        supported_start_exact=start, supported_end_exact=end,
        absence_is_flat_only_under_declared_report_coverage_assumption=True,
        complete_external_MC_history_verified=False, other_Settings_values_read=False)


def _merges(archive, location):
    top_to_pair, row_to_top = {}, {}
    with archive.open(location) as handle:
        for _, item in ET.iterparse(handle, events=("end",)):
            if item.tag != NS + "mergeCell": continue
            ref = item.get("ref", "")
            match = re.fullmatch(r"A([1-9][0-9]*):A([1-9][0-9]*)", ref)
            if match is None: continue
            top, bottom = int(match.group(1)), int(match.group(2))
            if top < 4: continue
            if bottom != top + 1 or top in row_to_top or bottom in row_to_top:
                raise ValueError("Trade# inheritance requires unique exact two-row A merges.")
            top_to_pair[top] = dict(top=top, bottom=bottom, merge_ref=ref)
            row_to_top[top] = row_to_top[bottom] = top
    return top_to_pair, row_to_top


def _parse_events(archive, location, strings):
    pairs, row_to_top = _merges(archive, location)
    events, issues, excluded = [], [], []
    top_ids, selected_rows, header_seen = {}, {}, False
    for row_id, cells in _rows(archive, location):
        if row_id < 3: continue
        if row_id == 3:
            for column, expected in HEADER.items():
                raw, _ = _cell(cells.get(column), strings)
                if raw != expected: raise ValueError("Frozen List of Trades header differs:" + column)
            header_seen = True; continue
        if not header_seen: raise ValueError("Header row3 absent.")
        # Date is the ONLY row value examined before the design-year filter.
        if "E" not in cells:
            # Trailing presentation rows without selected trade cells are not events.
            if not any(column in cells for column in ("A", "B", "C", "D", "F", "G", "H")): continue
            issues.append(dict(source_row_id=row_id, issue="selected_event_Date_absent")); continue
        try:
            raw_date, _ = _cell(cells["E"], strings, numeric_required=True, expected_style=7)
            info = date_day(raw_date)
        except (ValueError, TypeError, OverflowError, InvalidOperation) as exc:
            issues.append(dict(source_row_id=row_id, issue="invalid_Date_day_metadata", reason=str(exc))); continue
        day = info["day"]
        if day.year not in DESIGN_YEARS:
            excluded.append(dict(source_row_id=row_id, date=day.isoformat(), issue="outside2018_22_onlyDateinterpreted")); continue
        try:
            raw_time, _ = _cell(cells.get("F"), strings, numeric_required=True, expected_style=8)
            clock = reconcile_clock(info, raw_time)
            raw_type, _ = _cell(cells.get("C"), strings)
            match = re.fullmatch(r"(Entry|Exit)[ \t]*(Long|Short)", raw_type.strip(ASCII_SPACE))
            if match is None: raise ValueError("Malformed selected Entry/Exit side type.")
            event_type, side_name = match.groups(); side = 1 if side_name == "Long" else -1
            raw_signal, _ = _cell(cells.get("D"), strings)
            signal = raw_signal.strip(ASCII_SPACE)
            valid_signal = {"RS.L"} if event_type == "Entry" and side > 0 else {"RS.S"} if event_type == "Entry" else {"RS.LS", "RS.LT", "RS.LF", "RS.LSG"} if side > 0 else {"RS.SS", "RS.ST", "RS.SF", "RS.SSG"}
            if signal not in valid_signal: raise ValueError("Selected signal does not identify same-side owned RS event.")
            raw_order, _ = _cell(cells.get("B"), strings)
            if not raw_order.strip(ASCII_SPACE):
                raise ValueError("Selected Order# metadata is absent.")
            order_id = raw_order  # Opaque present metadata; no numeric/uniqueness/ordering inference.
            if row_id not in row_to_top: raise ValueError("Selected event lacks an explicit Trade# two-row merge.")
            top = row_to_top[row_id]; pair = pairs[top]
            raw_trade = None
            if row_id == top:
                raw_trade, _ = _cell(cells.get("A"), strings)
                top_ids[top] = _positive_integer(raw_trade)
            elif "A" in cells:
                # A merge's bottom must be absent/empty, never a competing ID.
                bottom, _ = _cell(cells["A"], strings)
                if bottom: raise ValueError("Merged bottom has its own Trade# value.")
            if top not in top_ids: raise ValueError("No admitted top-row Trade# exists for this selected merge.")
            trade_id = top_ids[top]
            if (row_id == top) != (event_type == "Entry"):
                raise ValueError("Trade merge must be Entry top and Exit bottom.")
            # Contracts is position-event metadata. Exit Price is NEVER decoded.
            raw_qty, _ = _cell(cells.get("H"), strings)
            quantity = _positive_integer(raw_qty)
            if quantity != 1: raise ValueError("Current RS source requires exactly one contract per event.")
            entry = None
            if event_type == "Entry":
                raw_entry, _ = _cell(cells.get("G"), strings)
                number = _decimal(raw_entry)
                if number <= 0 or (Fraction(number) * 4).denominator != 1:
                    raise ValueError("Owned RS entry must be positive exact quarter tick.")
                entry = float(number)
                if not math_is_finite(entry): raise ValueError("Owned RS entry is not finite representable.")
            event = dict(date=day.isoformat(), minute=clock["minute"], type=event_type.upper(), side=side,
                entry=entry, quantity=quantity, trade_id=trade_id, order_id=order_id,
                source_row_id=row_id, source_id=f"List of Trades!row{row_id}", merge_ref=pair["merge_ref"],
                pair_top_row=top, raw_type=raw_type, raw_signal=raw_signal, raw_order_id=raw_order,
                raw_top_trade_id=raw_trade, clock_audit=clock,
                canonical_entry_clock=clock["minute"] == 541 if event_type == "Entry" else None)
            events.append(event); selected_rows[row_id] = event
        except (ValueError, TypeError, OverflowError, InvalidOperation) as exc:
            issues.append(dict(source_row_id=row_id, date=day.isoformat(), issue="malformed_selected_event", reason=str(exc)))
    if not header_seen: raise ValueError("Required List of Trades header absent.")
    # Pair integrity is independent of ascending/descending report presentation.
    physical_rows = [event["source_row_id"] for event in events]
    grouped = {}
    for presentation_index, event in enumerate(events):
        event["physical_presentation_index"] = presentation_index
        grouped.setdefault(event["pair_top_row"], []).append(event)
    seen_trade, entry_dates = set(), set()
    for top, members in grouped.items():
        entries = [event for event in members if event["type"] == "ENTRY"]
        exits = [event for event in members if event["type"] == "EXIT"]
        if len(entries) != 1 or len(exits) != 1 or len(members) != 2:
            issues.append(dict(pair_top_row=top, issue="declared_merge_lacks_exactly_one_entry_and_exit")); continue
        entry, exit_event = entries[0], exits[0]
        if any(exit_event[name] != entry[name] for name in ("date", "trade_id", "side", "quantity", "merge_ref")):
            issues.append(dict(pair_top_row=top, issue="exit_pair_side_quantity_date_or_merge_mismatch"))
        if (exit_event["date"], exit_event["minute"]) < (entry["date"], entry["minute"]):
            issues.append(dict(pair_top_row=top, issue="exit_before_entry"))
        if entry["trade_id"] in seen_trade or entry["date"] in entry_dates:
            issues.append(dict(pair_top_row=top, issue="duplicate_trade_ID_or_multiple_entry_date"))
        seen_trade.add(entry["trade_id"]); entry_dates.add(entry["date"])
    events.sort(key=lambda event: (event["date"], event["minute"], event["trade_id"],
        0 if event["type"] == "ENTRY" else 1, event["source_row_id"]))
    active = None
    for event in events:
        if event["type"] == "ENTRY":
            if active is not None:
                issues.append(dict(source_row_id=event["source_row_id"], issue="chronological_positions_overlap"))
            active = event
        else:
            if active is None or active["trade_id"] != event["trade_id"]:
                issues.append(dict(source_row_id=event["source_row_id"], issue="chronological_exit_without_matching_open_entry"))
            active = None
    if active is not None: issues.append(dict(source_row_id=active["source_row_id"], issue="unclosed_selected_entry"))
    if any(event["pair_top_row"] not in selected_rows or event["pair_top_row"] + 1 not in selected_rows for event in events):
        issues.append(dict(issue="selected_trade_merge_pair_row_missing_or_outside_design"))
    return dict(events=events, issues=issues, excluded_date_rows=excluded,
        physical_event_source_row_ids=physical_rows, chronological_event_source_row_ids=[event["source_row_id"] for event in events],
        presentation_sort_applied=physical_rows != [event["source_row_id"] for event in events],
        chronological_sort="date,minute,Trade_ID,ENTRYbeforeEXITwithinpair,source_row_ID;physicalorderretained",
        raw_Date_DAY_before_other_row_values=True, exit_price_or_PNL_MAE_MFE_decoded=False,
        future_year_Time_Type_Signal_ID_Price_Contracts_decoded=False,
        noncanonical_entry_dates=sorted({event["date"] for event in events if event["type"] == "ENTRY" and not event["canonical_entry_clock"]}),
        merging="Trade# inheritance ONLY exact unique declared A[top]:A[top+1]; no arbitrary forward-fill")


def math_is_finite(value):
    return value == value and abs(value) != float("inf")


def read_owned_rs(path, verify_source_hash=True):
    """Runtime owned source -> global protocol audit and non-return event list.

    verify_source_hash=False is ONLY for artificial BytesIO fixtures. Normal
    runtime binds the exact authoritative owned file SHA before metadata.
    """
    audit = dict(global_pass=False, protocol_supported=False, settings=None, events=[],
        issues=[], source_sha256=None, complete_external_MC_history_verified=False,
        no_exit_price_or_PNL_read=True, native_marks_or_returns_calculated=False)
    try:
        if not verify_source_hash and not isinstance(path, io.BytesIO):
            raise ValueError("Hash bypass is permitted only for artificial in-memory BytesIO fixtures.")
        if verify_source_hash:
            if not isinstance(path, (str, Path)): raise ValueError("Owned runtime requires a bound filesystem path.")
            digest = hashlib.sha256(Path(path).read_bytes()).hexdigest()
            audit["source_sha256"] = digest
            if digest != WORKBOOK_SHA256: raise ValueError("Authoritative owned RS workbook hash differs.")
        with zipfile.ZipFile(path) as archive:
            locations = _locations(archive); strings = SelectedStrings(archive)
            settings = _settings(archive, locations["Settings"], strings)
            audit["settings"] = settings; audit["protocol_supported"] = settings["passed"]
            audit["supported_start"], audit["supported_end"] = settings["supported_start"], settings["supported_end"]
            if not settings["passed"]:
                audit["issues"].extend(settings["issues"]); return audit
            stream = _parse_events(archive, locations["List of Trades"], strings)
            audit.update(stream)
            audit["issues"] = stream["issues"]
            for event in stream["events"]:
                if not timestamp_within_coverage(settings, event["date"], event["minute"]):
                    audit["issues"].append(dict(source_row_id=event["source_row_id"], issue="event_outside_Settings_report_coverage"))
            audit["global_pass"] = not audit["issues"]
            audit["entry_price_metadata_rows_converted"] = sum(event["type"] == "ENTRY" for event in stream["events"])
            audit["event_stream_authorized_for_asof_features"] = audit["global_pass"]
            audit["no_selective_unknown_from_future_fault"] = True
    except (ValueError, TypeError, OverflowError, InvalidOperation, KeyError, ET.ParseError, zipfile.BadZipFile) as exc:
        audit["issues"].append(dict(issue="whole_source_metadata_failure", reason=str(exc)))
        audit["global_pass"] = False
    return audit


def _fixture_source(event_changes=None, settings_changes=None, future_poison=True, merges=True):
    from xml.sax.saxutils import escape
    event_changes, settings_changes = event_changes or {}, settings_changes or {}
    def cell(column, row, value, numeric=False, style=None):
        attrs = f' r="{column}{row}"' + (f' s="{style}"' if style is not None else "")
        if numeric: return f'<c{attrs} t="n"><v>{escape(str(value))}</v></c>'
        return f'<c{attrs} t="inlineStr"><is><t>{escape(str(value))}</t></is></c>'
    def make_row(row_id, values):
        return f'<row r="{row_id}">' + "".join(cell(column, row_id, *value) for column, value in values.items()) + '</row>'
    rows = [make_row(3, {column: (label,) for column, label in HEADER.items()})]
    specs = {
        4: {"A": ("1", True), "B": ("1", True), "C": ("Entry Long",), "D": ("RS.L",), "E": ("43102", True, 7), "F": ("0.375694444444444", True, 8), "G": ("100.25", True), "H": ("1", True), "I": ("POISON_PROFIT", True)},
        5: {"B": ("2", True), "C": ("Exit Long",), "D": ("RS.LF",), "E": ("43102", True, 7), "F": ("0.625", True, 8), "G": ("POISON_EXIT_PRICE", True), "H": ("1", True), "I": ("POISON_PROFIT", True)},
    }
    if future_poison:
        specs[6] = {"A": ("POISON_FUTURE_ID", True), "B": ("POISON_FUTURE_ORDER", True), "C": ("POISON_FUTURE_TYPE",), "D": ("POISON_FUTURE_SIGNAL",), "E": ("44928", True, 7), "F": ("POISON_FUTURE_TIME", True, 8), "G": ("POISON_FUTURE_PRICE", True), "H": ("POISON_FUTURE_QTY", True)}
    for row_id, updates in event_changes.items():
        specs.setdefault(row_id, {}).update(updates)
    for row_id, values in sorted(specs.items()): rows.append(make_row(row_id, values))
    merge_refs = ["A4:A5"] if merges is True else merges if isinstance(merges, list) else []
    merged = '<mergeCells>' + ''.join(f'<mergeCell ref="{ref}"/>' for ref in merge_refs) + '</mergeCells>' if merge_refs else ''
    sheet = f'<worksheet xmlns="{NS[1:-1]}"><sheetData>' + "".join(rows) + '</sheetData>' + merged + '</worksheet>'
    settings = {"Symbol Name": ("@NQ", False), "Compression": ("1 Minute", False), "Start Date": ("2017-09-01", False), "End Date": ("2022-12-31", False), **{key: (value, True) for key, value in EXPECTED_NUMERIC_SETTINGS.items()}, "SkipHolidays": ("True", False), "Commission": ("POISON_UNAUTHORIZED_SETTING", True)}
    settings.update(settings_changes)
    setting_rows = [make_row(i, {"A": (key,), "B": values}) for i, (key, values) in enumerate(settings.items(), start=1)]
    setting_xml = f'<worksheet xmlns="{NS[1:-1]}"><sheetData>' + "".join(setting_rows) + '</sheetData></worksheet>'
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        archive.writestr("xl/workbook.xml", f'<workbook xmlns="{NS[1:-1]}" xmlns:r="{REL[1:-1]}"><workbookPr date1904="0"/><sheets><sheet name="List of Trades" r:id="r3"/><sheet name="Settings" r:id="r8"/></sheets></workbook>')
        archive.writestr("xl/_rels/workbook.xml.rels", '<Relationships><Relationship Id="r3" Target="worksheets/sheet3.xml"/><Relationship Id="r8" Target="worksheets/sheet8.xml"/></Relationships>')
        archive.writestr("xl/styles.xml", f'<styleSheet xmlns="{NS[1:-1]}"><cellXfs>' + ''.join(f'<xf numFmtId="{14 if i == 7 else 21 if i == 8 else 0}"/>' for i in range(9)) + '</cellXfs></styleSheet>')
        archive.writestr("xl/worksheets/sheet3.xml", sheet)
        archive.writestr("xl/worksheets/sheet8.xml", setting_xml)
    buffer.seek(0)
    return buffer


def fixtures():
    result = read_owned_rs(_fixture_source(), verify_source_hash=False)
    assert result["global_pass"] and len(result["events"]) == 2
    assert result["events"][0]["minute"] == 541 and result["events"][1]["minute"] == 900
    assert result["events"][1]["entry"] is None and result["events"][1]["trade_id"] == 1
    assert len(result["excluded_date_rows"]) == 1 and not result["exit_price_or_PNL_MAE_MFE_decoded"]
    whole = reconcile_clock(date_day("43102"), "43102.375694444444444")
    assert whole["minute"] == 541 and whole["time_integer"] == 43102
    assert reconcile_clock(date_day("43102.375694444444444"), "0.375694444444444")["minute"] == 541
    for date_raw, time_raw in (("43102", "43103.375694444444444"), ("43102.5", ".375694444444444"), ("43102", ".375700"), ("43102", "NaN")):
        try: reconcile_clock(date_day(date_raw), time_raw)
        except ValueError: pass
        else: raise AssertionError("Malformed/inconsistent full-serial clock admitted.")
    no_merge = read_owned_rs(_fixture_source(merges=False), verify_source_hash=False)
    assert not no_merge["global_pass"]
    bad_exit = read_owned_rs(_fixture_source({5: {"F": ("POISON_INVALID_EXIT_TIME", True, 8)}}), verify_source_hash=False)
    assert not bad_exit["global_pass"] and not bad_exit["event_stream_authorized_for_asof_features"]
    mismatch = read_owned_rs(_fixture_source({5: {"C": ("Exit Short",), "D": ("RS.SF",)}}), verify_source_hash=False)
    assert not mismatch["global_pass"]
    opaque_order = read_owned_rs(_fixture_source({4: {"B": ("OPAQUE_SAME",)}, 5: {"B": ("OPAQUE_SAME",)}}), verify_source_hash=False)
    assert opaque_order["global_pass"] and opaque_order["events"][0]["order_id"] == "OPAQUE_SAME"
    absent_order = read_owned_rs(_fixture_source({5: {"B": ("",)}}), verify_source_hash=False)
    assert not absent_order["global_pass"]
    wrong_params = read_owned_rs(_fixture_source(settings_changes={"TradeDir": ("1", True)}), verify_source_hash=False)
    assert not wrong_params["global_pass"] and not wrong_params["events"]
    noncanonical = read_owned_rs(_fixture_source({4: {"F": (".376388888888889", True, 8)}}), verify_source_hash=False)
    assert noncanonical["global_pass"] and noncanonical["noncanonical_entry_dates"] == ["2018-01-02"]
    mutated_future_exit = read_owned_rs(_fixture_source({5: {"F": (".590277777777778", True, 8), "D": ("RS.LT",)}}), verify_source_hash=False)
    assert mutated_future_exit["global_pass"]
    def prefix(stream):
        assert stream["global_pass"]
        return [{key: event[key] for key in ("date", "minute", "type", "side", "entry", "trade_id", "order_id")}
            for event in stream["events"] if event["minute"] < 840]
    assert prefix(result) == prefix(mutated_future_exit)
    descending_changes = {
        4: {"E": ("43103", True, 7)}, 5: {"E": ("43103", True, 7)},
        6: {"A": ("2", True), "B": ("OPAQUE",), "C": ("Entry Long",), "D": ("RS.L",), "E": ("43102", True, 7), "F": (".375694444444444", True, 8), "G": ("100.25", True), "H": ("1", True)},
        7: {"B": ("OPAQUE",), "C": ("Exit Long",), "D": ("RS.LF",), "E": ("43102", True, 7), "F": (".625", True, 8), "G": ("POISON_EXIT_PRICE", True), "H": ("1", True)}
    }
    descending = read_owned_rs(_fixture_source(descending_changes, future_poison=False, merges=["A4:A5", "A6:A7"]), verify_source_hash=False)
    assert descending["global_pass"] and descending["presentation_sort_applied"]
    assert descending["physical_event_source_row_ids"] == [4, 5, 6, 7] and descending["chronological_event_source_row_ids"] == [6, 7, 4, 5]
    quantity_fault = read_owned_rs(_fixture_source({5: {"H": ("2", True)}}), verify_source_hash=False)
    assert not quantity_fault["global_pass"]
    numeric_bounds = read_owned_rs(_fixture_source(settings_changes={"Start Date": ("43102.375", True), "End Date": ("43102.625", True), "Compression": ("1 Minutes", False)}), verify_source_hash=False)
    assert numeric_bounds["global_pass"] and numeric_bounds["supported_start"] == "2018-01-02T09:00:00" and numeric_bounds["supported_end"] == "2018-01-02T15:00:00"
    text_bounds = read_owned_rs(_fixture_source(settings_changes={"Start Date": ("2018-01-02T09:00:00", False), "End Date": ("1/2/2018 3:00:00 PM", False)}), verify_source_hash=False)
    assert text_bounds["global_pass"] and text_bounds["supported_end"] == "2018-01-02T15:00:00"
    assert _setting_bound("1/2/2018 12:00 AM", False)["timestamp"] == "2018-01-02T00:00:00"
    starts_after_entry = read_owned_rs(_fixture_source(settings_changes={"Start Date": ("2018-01-02 09:01:00.000000001", False)}), verify_source_hash=False)
    assert not starts_after_entry["global_pass"]  # Exact1ns boundary, no date truncation or timestamp rounding.
    narrow_end = read_owned_rs(_fixture_source(settings_changes={"End Date": ("2018-01-02T14:59:59", False)}), verify_source_hash=False)
    assert not narrow_end["global_pass"]
    wrong_compression = read_owned_rs(_fixture_source(settings_changes={"Compression": ("5 Minutes", False)}), verify_source_hash=False)
    assert not wrong_compression["global_pass"]
    bypass = read_owned_rs("NO_SUCH_SOURCE_MUST_NOT_BE_OPENED.xlsx", verify_source_hash=False)
    assert not bypass["global_pass"] and "only for artificial" in bypass["issues"][0]["reason"]
    json.dumps(result, allow_nan=False)
    return dict(passed=True, actual_RS_or_Date_Time_price_exit_PNL_values_read=False,
        checks=["Settingsidentity/canonicalparams/coverageonlyallowlistedBvalues", "DateDAYbeforefutureTime/Type/Signal/IDs/Price/Qtypoison",
            "numericDate7fmt14/Time8fmt21/Excel1900", "wholeTimeinteger/datefractionconsistency/nooffset/exactminute",
            "explicit2rowTradeIDinheritance/noarbitraryffill", "exitPrice/PNLpoisonneverdecoded",
            "globalmalformedexit/pair/orderpresencefaultblocksourcebeforefeatures;Orderopaque/noguessedrelation", "noncanonicalvalidclockretainedUNKNOWNday",
            "futurevalidexitmutationdoesnotchangeasofprefix", "descendingreportpresentationchronologicallysorted/allphysicalIDsretained",
            "exitquantityfullclosemetadata/hashbypassonlyartificialmemory",
            "fullserial/ISO/US-AMPMSettingsbounds retainexactclock/noDaytruncation;1nsboundary",
            "1Minute/1Minutessemanticcompressiononly"],
        script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())


if __name__ == "__main__":
    result = fixtures()
    output = Path(__file__).resolve().parent / "outputs/codex_hunt_v2_ldf_rs_open_loss" / f"metadata_synthetic_checks_{result['script_sha256'][:12]}.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("x") as handle:
        json.dump(result, handle, indent=2, allow_nan=False); handle.write("\n")
    print(json.dumps(result, allow_nan=False))
