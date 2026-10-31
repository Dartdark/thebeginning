"""H04 selected ENTRY metadata from XLSX XML; no engine reads outcome cells.

Import/fixtures never open an owned workbook.  The runtime reader decodes only
header names and the Type/Date/(optional Time)/Price cells required below.
Date+ENTRY+registered-universe selection PRECEDES Price/time conversion.  An
as-yet unknown workbook format fails admission rather than trying an offset.
"""
from __future__ import annotations

from datetime import date, datetime, time, timedelta
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
import hashlib
import io
import json
from pathlib import Path
import posixpath
import re
import xml.etree.ElementTree as ET
import zipfile

import pandas as pd

NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
REL = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"
DATE_RE = re.compile(r"^(?:([0-9]{4})-([0-9]{2})-([0-9]{2})|([0-9]{2})/([0-9]{2})/([0-9]{4}))(?:[ T]([0-9]{2}):([0-9]{2})(?::([0-9]{2}))?(?: (AM|PM))?)?$")
TIME_RE = re.compile(r"^([0-9]{2}):([0-9]{2})(?::([0-9]{2}))?(?: (AM|PM))?$")
NUM_RE = re.compile(r"^[+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[eE][+-]?[0-9]+)?$")
CELL_RE = re.compile(r"^([A-Z]+)([1-9][0-9]*)$")
YEARS = tuple(range(2018, 2023))
COLUMNS = ("source_row_id", "date", "side", "entry", "entry_j", "MCclock_verified")


def _safe_xml(raw):
    if b"<!DOCTYPE" in raw.upper() or b"<!ENTITY" in raw.upper():
        raise ValueError("DTD/entities are not permitted in workbook metadata.")
    return ET.fromstring(raw)


def _fraction_clock(value):
    number = Decimal(value)
    if not number.is_finite() or not (0 <= number < 1):
        raise ValueError("Excel Time must be a finite fraction of one day.")
    seconds = number * Decimal(86400)
    rounded = seconds.to_integral_value(rounding=ROUND_HALF_UP)
    if abs(seconds - rounded) > Decimal("0.001") or int(rounded) >= 86400:
        raise ValueError("Subsecond/noncanonical Excel clock cannot identify an exact minute.")
    count = int(rounded)
    return time(count // 3600, count % 3600 // 60, count % 60)


def _hms(h, m, s=None, ampm=None):
    hour, minute, second = int(h), int(m), int(s or 0)
    if ampm:
        if not 1 <= hour <= 12:
            raise ValueError("AM/PM hour outside1..12.")
        hour = hour % 12 + (12 if ampm == "PM" else 0)
    return time(hour, minute, second)


def date_metadata(value, numeric=False, date1904=False):
    """Date conversion is metadata-only; returns explicit clock or None."""
    if numeric:
        if not NUM_RE.fullmatch(value):
            raise ValueError("Invalid Excel date metadata number.")
        number = Decimal(value)
        if not number.is_finite() or number < 0:
            raise ValueError("Invalid Excel date metadata serial.")
        whole = int(number)
        day = (date(1904, 1, 1) if date1904 else date(1899, 12, 30)) + timedelta(days=whole)
        fraction = number - whole
        return day, _fraction_clock(str(fraction)) if fraction else None
    match = DATE_RE.fullmatch(value)
    if match is None:
        raise ValueError("Date must be exact ISO or MM/DD/YYYY metadata.")
    y, m, d, um, ud, uy, h, minute, second, ampm = match.groups()
    day = date(int(y or uy), int(m or um), int(d or ud))
    return day, _hms(h, minute, second, ampm) if h is not None else None


def clock_metadata(value, numeric=False):
    if numeric:
        if not NUM_RE.fullmatch(value):
            raise ValueError("Invalid numeric Excel Time.")
        return _fraction_clock(value)
    match = TIME_RE.fullmatch(value)
    if match is None:
        raise ValueError("Time must be exact HH:MM[:SS] or Excel day fraction.")
    return _hms(*match.groups())


class SelectedStrings:
    """Look up only selected shared-string indexes, without decoding others."""
    def __init__(self, archive):
        self.archive, self.cache = archive, {}

    def get(self, value):
        if re.fullmatch(r"[0-9]+", value) is None:
            raise ValueError("Invalid shared-string index.")
        target = int(value)
        if target in self.cache:
            return self.cache[target]
        if "xl/sharedStrings.xml" not in self.archive.namelist():
            raise ValueError("Missing selected shared-string table.")
        with self.archive.open("xl/sharedStrings.xml") as handle:
            index = -1
            for _, element in ET.iterparse(handle, events=("end",)):
                if element.tag == NS + "si":
                    index += 1
                    if index == target:
                        text = "".join(e.text or "" for e in element.iter(NS + "t"))
                        self.cache[target] = text
                        return text
                    element.clear()
        raise ValueError("Selected shared-string index is absent.")


def _cell_text(cell, strings):
    kind = cell.get("t", "n")
    if cell.find(NS + "f") is not None:
        raise ValueError("Selected metadata/entry cells may not contain formulas.")
    if kind == "inlineStr":
        return "".join(e.text or "" for e in cell.iter(NS + "t")), False
    value = cell.find(NS + "v")
    raw = "" if value is None or value.text is None else value.text
    if kind == "s":
        return strings.get(raw), False
    if kind in ("str", "d"):
        return raw, False
    if kind == "n":
        return raw, True
    raise ValueError("Unsupported selected cell type:" + kind)


def _sheet_location(archive):
    book = _safe_xml(archive.read("xl/workbook.xml"))
    props = book.find(NS + "workbookPr")
    date1904 = props is not None and props.get("date1904", "0") in ("1", "true")
    sheets = [s for s in book.iter(NS + "sheet") if s.get("name") == "List of Trades"]
    if len(sheets) != 1:
        raise ValueError("Exactly one List of Trades sheet is required.")
    relation_id = sheets[0].get(REL + "id")
    relations = _safe_xml(archive.read("xl/_rels/workbook.xml.rels"))
    hits = [r for r in relations if r.get("Id") == relation_id]
    if len(hits) != 1 or hits[0].get("TargetMode") == "External":
        raise ValueError("List of Trades must have a unique internal relationship.")
    target = hits[0].get("Target", "")
    location = posixpath.normpath(target.lstrip("/")) if target.startswith("/") else posixpath.normpath(posixpath.join("xl", target))
    if not location.startswith("xl/worksheets/") or location not in archive.namelist():
        raise ValueError("Sheet relationship escapes the worksheet allowlist.")
    return location, date1904


def _validate_sheet_coordinates(archive, location):
    """All-sheet coordinate metadata admission BEFORE selected value decoding."""
    seen_rows = set()
    with archive.open(location) as handle:
        for _, element in ET.iterparse(handle, events=("end",)):
            if element.tag != NS + "row":
                continue
            raw_row = element.get("r", "")
            if re.fullmatch(r"[1-9][0-9]*", raw_row) is None:
                raise ValueError("Missing/noncanonical worksheet row coordinate.")
            row_id = int(raw_row)
            if row_id in seen_rows:
                raise ValueError("Duplicate worksheet row coordinate; ambiguous source IDs.")
            seen_rows.add(row_id)
            columns = set()
            for cell in element.findall(NS + "c"):
                match = CELL_RE.fullmatch(cell.get("r", ""))
                if match is None or int(match.group(2)) != row_id:
                    raise ValueError("Cell coordinate is missing/invalid or disagrees with its row.")
                column = match.group(1)
                if column in columns:
                    raise ValueError("Duplicate cell column/coordinate within worksheet row.")
                columns.add(column)
            element.clear()


def read_entry_metadata(path, comparison_dates):
    """path may be a Path or artificial BytesIO; no other workbook APIs used."""
    audit = dict(sheet="List of Trades", header_row=3, selected_columns=[],
        workbook_rows_seen=0, entry_type_rows=0, eligible_design_entry_rows=0,
        invalid_selected_entry_rows=[], excluded_entry_rows=[], duplicate_design_dates=[],
        selected_price_numeric_conversions=0, future_or_exit_price_numeric_conversions=0,
        MCclock_not_verified_rows=[],
        exit_gross_net_fee_commission_cells_interpreted=False, clock_offset_search=False,
        parser="rawXLSXZIP/XML; Type+date+fixeduniverse before selected entry Price/time conversion",
        date_codec="ISO YYYY-MM-DD or MM/DD/YYYY with optional explicit HH:MM[:SS][ AM/PM]; Excel serial metadata",
        time_codec="explicit Time HH:MM[:SS][ AM/PM]/Excel dayfraction, else explicit Date clock; absentclockNOT_VERIFIED,nofabrication/noautomaticveto",
        minute_rule="exact whole minute; Excel fractional clock rounding to nearest second only within0.001second")
    rows, headers = [], {}
    with zipfile.ZipFile(path) as archive:
        if len(archive.namelist()) != len(set(archive.namelist())):
            raise ValueError("Ambiguous duplicate workbook ZIP members.")
        location, date1904 = _sheet_location(archive)
        audit["sheet_XML_member"], audit["Excel_date1904"] = location, date1904
        _validate_sheet_coordinates(archive, location)
        audit["whole_sheet_coordinate_metadata_pass"] = True
        strings = SelectedStrings(archive)
        with archive.open(location) as handle:
            for _, element in ET.iterparse(handle, events=("end",)):
                if element.tag != NS + "row":
                    continue
                row_id = int(element.get("r", "0"))
                if row_id < 3:
                    element.clear(); continue
                cells = {}
                for cell in element.findall(NS + "c"):
                    match = CELL_RE.fullmatch(cell.get("r", ""))
                    if match:
                        cells[match.group(1)] = cell
                if row_id == 3:
                    raw_headers = {}
                    for column, cell in cells.items():
                        label, _ = _cell_text(cell, strings)
                        if label in ("Date", "Type", "Price", "Time"):
                            if label in raw_headers:
                                raise ValueError("Duplicate required MC header:" + label)
                            raw_headers[label] = column
                    if not {"Date", "Type", "Price"}.issubset(raw_headers):
                        raise ValueError("Missing required ENTRY metadata header.")
                    headers = raw_headers
                    audit["selected_columns"] = list(headers)
                    audit["selected_header_cells"] = {name: column + "3" for name, column in headers.items()}
                    element.clear(); continue
                if not headers:
                    raise ValueError("Header row3 was absent.")
                audit["workbook_rows_seen"] += 1
                type_cell = cells.get(headers["Type"])
                if type_cell is None:
                    element.clear(); continue
                kind, _ = _cell_text(type_cell, strings)
                if not kind.startswith("Entry"):
                    element.clear(); continue
                audit["entry_type_rows"] += 1
                try:
                    date_cell = cells.get(headers["Date"])
                    if date_cell is None:
                        raise ValueError("Entry Date cell absent.")
                    raw_date, numeric_date = _cell_text(date_cell, strings)
                    day, date_clock = date_metadata(raw_date, numeric_date, date1904)
                except (ValueError, TypeError, OverflowError, InvalidOperation) as exc:
                    audit["invalid_selected_entry_rows"].append(dict(source_row_id=row_id, issue="entry_date_metadata_invalid", reason=str(exc)))
                    element.clear(); continue
                label = day.isoformat()
                if day.year not in YEARS or label not in comparison_dates:
                    audit["excluded_entry_rows"].append(dict(source_row_id=row_id, date=label,
                        reason="outside2018_22" if day.year not in YEARS else "outside_fixed_comparison_calendar"))
                    element.clear(); continue
                audit["eligible_design_entry_rows"] += 1
                try:
                    is_long, is_short = "Long" in kind, "Short" in kind
                    if is_long == is_short:
                        raise ValueError("Entry type must identify exactly one Long/Short side.")
                    price_cell = cells.get(headers["Price"])
                    if price_cell is None:
                        raise ValueError("Entry Price cell absent.")
                    raw_price, _ = _cell_text(price_cell, strings)
                    if NUM_RE.fullmatch(raw_price) is None:
                        raise ValueError("Entry Price is not a strict ASCII number.")
                    entry_number = Decimal(raw_price)
                    audit["selected_price_numeric_conversions"] += 1
                    if not entry_number.is_finite() or entry_number <= 0:
                        raise ValueError("Entry Price must be finite positive.")
                    entry = float(entry_number)
                    if not (entry > 0 and entry < float("inf")):
                        raise ValueError("Entry Price cannot be represented as finite positive float.")
                    explicit = None
                    if "Time" in headers and headers["Time"] in cells:
                        raw_time, numeric_time = _cell_text(cells[headers["Time"]], strings)
                        if raw_time:
                            explicit = clock_metadata(raw_time, numeric_time)
                    if explicit is not None and date_clock is not None and explicit != date_clock:
                        raise ValueError("Explicit Time and Date clock disagree.")
                    clock = explicit if explicit is not None else date_clock
                    if clock is not None and (clock.second != 0 or clock.microsecond != 0):
                        raise ValueError("Explicit ENTRY clock is not an exact whole minute.")
                    if clock is None:
                        audit["MCclock_not_verified_rows"].append(dict(source_row_id=row_id, date=label,
                            issue="NoexplicitTimeorDateclock;NOT_VERIFIED;nobarlabelinvented"))
                    rows.append(dict(source_row_id=row_id, date=label, side=1 if is_long else -1,
                        entry=entry, entry_j=clock.hour * 60 + clock.minute if clock is not None else None,
                        MCclock_verified=clock is not None))
                except (ValueError, TypeError, OverflowError, InvalidOperation) as exc:
                    audit["invalid_selected_entry_rows"].append(dict(source_row_id=row_id, date=label,
                        issue="eligible_entry_side_price_or_clock_invalid", reason=str(exc)))
                element.clear()
    if not headers:
        raise ValueError("Required header row3 absent.")
    frame = pd.DataFrame(rows, columns=COLUMNS)
    audit["duplicate_design_dates"] = sorted(frame.loc[frame.date.duplicated(keep=False), "date"].unique().tolist()) if len(frame) else []
    audit["passed"] = not audit["invalid_selected_entry_rows"] and not audit["duplicate_design_dates"]
    return frame, audit


def _fixture_workbook(records, headers=("Date", "Type", "Price", "Time")):
    main = f'<worksheet xmlns="{NS[1:-1]}"><sheetData>'
    def cell(column, row, value):
        if isinstance(value, tuple):
            raw, kind = value
            return f'<c r="{column}{row}" t="{kind}"><v>{raw}</v></c>'
        from xml.sax.saxutils import escape
        return f'<c r="{column}{row}" t="inlineStr"><is><t>{escape(value)}</t></is></c>'
    main += '<row r="3">' + "".join(cell(chr(65 + k), 3, name) for k, name in enumerate(headers)) + '</row>'
    for row, record in enumerate(records, start=4):
        main += f'<row r="{row}">' + "".join(cell(chr(65 + k), row, value) for k, value in enumerate(record)) + '</row>'
    main += '</sheetData></worksheet>'
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        archive.writestr("xl/workbook.xml", f'<workbook xmlns="{NS[1:-1]}" xmlns:r="{REL[1:-1]}"><sheets><sheet name="List of Trades" r:id="rId1"/></sheets></workbook>')
        archive.writestr("xl/_rels/workbook.xml.rels", '<Relationships><Relationship Id="rId1" Target="worksheets/sheet1.xml"/></Relationships>')
        archive.writestr("xl/worksheets/sheet1.xml", main)
    buffer.seek(0)
    return buffer


def fixtures():
    records = [
        ["2018-01-02", "Entry Long", ("100", "n"), "09:01:00", "POISON_OUTCOME"],
        ["2023-01-03", "Entry Long", ("POISON_FUTURE", "n"), ("POISON_FUTURE_TIME", "n"), "POISON_OUTCOME"],
        ["2018-01-02", "Exit Long", ("POISON_EXIT", "n"), ("POISON_EXIT_TIME", "n"), "POISON_OUTCOME"],
        ["2018-01-03", "Entry Short", ("POISON_EXCLUDED", "n"), ("POISON_EXCLUDED_TIME", "n"), "POISON_OUTCOME"],
    ]
    frame, audit = read_entry_metadata(_fixture_workbook(records, ("Date", "Type", "Price", "Time", "Profit ($)")), {"2018-01-02"})
    assert audit["passed"] and len(frame) == 1 and frame.iloc[0].entry_j == 541 and frame.iloc[0].side == 1
    assert audit["selected_price_numeric_conversions"] == 1 and audit["future_or_exit_price_numeric_conversions"] == 0
    assert not audit["exit_gross_net_fee_commission_cells_interpreted"] and len(audit["excluded_entry_rows"]) == 2
    # Exercise selected shared strings without decoding the unselected value.
    shared_source = _fixture_workbook([["2018-01-02", "Entry Long", ("100", "n"), "09:01"]])
    with zipfile.ZipFile(shared_source) as archive:
        members = {name: archive.read(name) for name in archive.namelist()}
    sheet = members["xl/worksheets/sheet1.xml"].decode()
    sheet = sheet.replace('<c r="B4" t="inlineStr"><is><t>Entry Long</t></is></c>', '<c r="B4" t="s"><v>1</v></c>')
    members["xl/worksheets/sheet1.xml"] = sheet.encode()
    members["xl/sharedStrings.xml"] = f'<sst xmlns="{NS[1:-1]}"><si><t>POISON_UNSELECTED</t></si><si><r><t>Entry </t></r><r><t>Long</t></r></si></sst>'.encode()
    shared_fixture = io.BytesIO()
    with zipfile.ZipFile(shared_fixture, "w") as archive:
        for name, content in members.items(): archive.writestr(name, content)
    shared_fixture.seek(0)
    frame, audit = read_entry_metadata(shared_fixture, {"2018-01-02"})
    assert audit["passed"] and len(frame) == 1 and frame.iloc[0].side == 1
    def malformed_sheet(modify):
        source = _fixture_workbook([["2018-01-02", "Entry Long", ("100", "n"), "09:01"]])
        with zipfile.ZipFile(source) as archive:
            parts = {name: archive.read(name) for name in archive.namelist()}
        parts["xl/worksheets/sheet1.xml"] = modify(parts["xl/worksheets/sheet1.xml"].decode()).encode()
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w") as archive:
            for name, content in parts.items(): archive.writestr(name, content)
        buffer.seek(0)
        return buffer
    mutations = (
        lambda s: s.replace('</row></sheetData>', '<c r="C4" t="n"><v>POISON_DUPLICATE_PRICE</v></c></row></sheetData>'),
        lambda s: s.replace('r="C4"', 'r="C5"'),
        lambda s: s.replace('</sheetData>', '<row r="4"><c r="A4" t="n"><v>POISON_DUPLICATE_ROW</v></c></row></sheetData>'),
    )
    for mutation in mutations:
        try: read_entry_metadata(malformed_sheet(mutation), {"2018-01-02"})
        except ValueError: pass
        else: raise AssertionError("Malformed/ambiguous worksheet coordinates admitted.")
    day, clock = date_metadata("43102.37569444444444", True)
    assert day == date(2018, 1, 2) and clock == time(9, 1)
    assert date_metadata("01/02/2018 09:01 AM")[1] == time(9, 1)
    assert clock_metadata("12:01 AM") == time(0, 1) and clock_metadata("12:01 PM") == time(12, 1)
    frame, audit = read_entry_metadata(_fixture_workbook([["2018-01-02 09:01:00", "Entry Short", ("100.25", "n")]], ("Date", "Type", "Price")), {"2018-01-02"})
    assert audit["passed"] and frame.iloc[0].side == -1 and frame.iloc[0].entry_j == 541
    _, audit = read_entry_metadata(_fixture_workbook([["2018-01-02", "Entry Long", ("100", "n")]], ("Date", "Type", "Price")), {"2018-01-02"})
    assert audit["passed"] and audit["MCclock_not_verified_rows"]
    _, audit = read_entry_metadata(_fixture_workbook([["2018-01-02 09:01", "Entry Long", ("100", "n"), "09:02"]]), {"2018-01-02"})
    assert not audit["passed"]
    _, audit = read_entry_metadata(_fixture_workbook([records[0], records[0]], ("Date", "Type", "Price", "Time", "Profit ($)")), {"2018-01-02"})
    assert not audit["passed"] and audit["duplicate_design_dates"]
    for bad in ("2018-02-30", "2018-1-02", "２０１８-01-02"):
        try: date_metadata(bad)
        except ValueError: pass
        else: raise AssertionError("Invalid Date metadata admitted.")
    for bad in ("09:01:01",):
        _, audit = read_entry_metadata(_fixture_workbook([["2018-01-02", "Entry Long", ("100", "n"), bad]]), {"2018-01-02"})
        assert not audit["passed"]
    return dict(passed=True, real_workbook_or_price_rows_read=False,
        checks=["rawXML selectedcolumns only", "whole-sheet coordinate admission beforevalues; duplicatecells/rows/mismatchedcellrowfatal",
            "ENTRY+design+fixedcalendar beforeprice/time poisonconversion", "on-demand selected sharedstrings/richtext",
            "Excelserial/dateclock metadata", "strictISO/USdate andAMPMclock", "explicitDateclockwithoutTimecolumn",
            "absententryclockNOT_VERIFIED/noautomaticveto;presentinvalid/contradictoryfatal", "duplicateentrydatesfatal", "exactminuteandrealASCIIcalendar"],
        script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())


if __name__ == "__main__":
    result = fixtures()
    output = Path(__file__).resolve().parent / "outputs/codex_hunt_v2_rs_classified_support" / f"mc_xml_synthetic_checks_{result['script_sha256'][:12]}.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("x") as handle:
        json.dump(result, handle, indent=2); handle.write("\n")
    print(json.dumps(result))
