"""Frozen source-only earnings metadata census; plan ac88ccd.

No EPS values, price observations, forecasts, strategy returns or next-session
mapping enter this audit. Report-date counts are not observed guidance changes.
"""
from __future__ import annotations

import csv
from collections import Counter
from datetime import date, datetime, timezone
import hashlib
import io
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis/outputs/codex_forward_guidance_input_gate"
PLAN = "agents/codex/plans/forward_guidance_input_gate.md"
PLAN_COMMIT = "ac88ccd"
INPUTS = ("data/ndx_megacap_earnings.csv", "data/dow_heavy_earnings.csv")
DEFINITIONS = ("analysis/megacap_earnings_nq_test.py", "analysis/ym_dow_events_test.py")
META = ("ticker", "fiscalDateEnding", "reportedDate", "reportTime")
REQUIRED = {
    "same_future_horizon": ("guidanceFiscalPeriod", "priorGuidanceFiscalPeriod"),
    "comparable_interval": ("guidanceLow", "guidanceHigh", "priorGuidanceLow", "priorGuidanceHigh"),
    "metric_units_basis": ("guidanceMetric", "guidanceUnits", "guidanceAccountingBasis"),
    "original_documents": ("guidanceDocumentURL", "priorGuidanceDocumentURL", "originalDocumentHash"),
    "before_entry_timing": ("publicationTimestamp", "receiptTimestamp", "priorPublicationTimestamp"),
    "vintage_and_normalization": ("dataVintage", "guidanceStatus", "currency", "shareCountBasis"),
    "index_transmission": ("indexMembershipAsOf", "indexWeightAsOf"),
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parsedate(value: str) -> date | None:
    try:
        result = date.fromisoformat(value)
        return result if result.isoformat() == value else None
    except (ValueError, TypeError):
        return None


def csvbytes(rows: list[dict], fields: list[str] | tuple[str, ...]) -> bytes:
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue().encode()


def main() -> None:
    if OUT.exists() and any(OUT.iterdir()):
        raise SystemExit("Retained source census exists; do not repeat or overwrite it.")
    current_plan = (ROOT / PLAN).read_bytes()
    committed_plan = subprocess.check_output(["git", "show", f"{PLAN_COMMIT}:{PLAN}"], cwd=ROOT)
    if current_plan != committed_plan:
        raise SystemExit("Source gate differs from its committed plan.")
    bound_paths = (*INPUTS, *DEFINITIONS, PLAN)
    hashes = {p: digest(ROOT / p) for p in bound_paths}
    selected, exceptions, schemas, excluded, all_metadata_counts = [], [], {}, {}, {}
    for relative in INPUTS:
        with (ROOT / relative).open(newline="", encoding="utf-8-sig") as handle:
            reader = csv.DictReader(handle)
            fields = reader.fieldnames or []
            if len(fields) != len(set(fields)) or not set(META) <= set(fields):
                raise ValueError(f"Missing/duplicate metadata columns: {relative}")
            schemas[relative] = {
                "header": fields,
                "required_literal_fields": {
                    concept: {field: field in fields for field in names}
                    for concept, names in REQUIRED.items()
                },
                "literal_field_limit": "No alias inference; absence is schema-only, not an exhaustive external-source finding.",
            }
            outside, total = 0, 0
            for line, raw in enumerate(reader, start=2):
                total += 1
                # Explicit metadata projection: other source fields never enter the study.
                row = {k: raw.get(k, "").strip() for k in META}
                row.update(source=relative, source_line=line)
                reported, fiscal = parsedate(row["reportedDate"]), parsedate(row["fiscalDateEnding"])
                issues = []
                if not row["ticker"]:
                    issues.append("empty_ticker")
                if reported is None:
                    issues.append("invalid_reported_date")
                if fiscal is None:
                    issues.append("invalid_fiscal_date")
                if reported is not None and fiscal is not None and fiscal > reported:
                    issues.append("fiscal_end_after_report_date")
                if row["reportTime"] not in ("pre-market", "post-market"):
                    issues.append("unknown_report_time_label")
                in_design = reported is not None and 2018 <= reported.year <= 2022
                row["issues"] = "|".join(issues)
                row["in_design_report_date_window"] = in_design
                if reported is None or in_design:
                    if issues:
                        exceptions.append(row.copy())
                if in_design:
                    selected.append(row)
                else:
                    outside += 1
            excluded[relative] = outside
            all_metadata_counts[relative] = total

    columns = ("source", "source_line", *META, "in_design_report_date_window", "issues")
    summaries = []
    for relative in INPUTS:
        for year in range(2018, 2023):
            rows = [r for r in selected if r["source"] == relative and r["reportedDate"].startswith(str(year))]
            labels = Counter(r["reportTime"] for r in rows)
            summaries.append(dict(source=relative, year=year, metadata_rows=len(rows),
                                  issuers=len({r["ticker"] for r in rows}),
                                  distinct_report_dates=len({r["reportedDate"] for r in rows}),
                                  pre_market=labels["pre-market"], post_market=labels["post-market"],
                                  unknown_labels=sum(n for k, n in labels.items() if k not in ("pre-market", "post-market"))))

    identity_counts = Counter((r["source"], r["ticker"], r["fiscalDateEnding"]) for r in selected)
    duplicate_rows = [dict(r, same_source_issuer_fiscal_key_count=identity_counts[
        (r["source"], r["ticker"], r["fiscalDateEnding"])]) for r in selected
        if identity_counts[(r["source"], r["ticker"], r["fiscalDateEnding"])] > 1]
    dated = {}
    for r in selected:
        key = r["reportedDate"]
        item = dated.setdefault(key, {"metadata_rows": 0, "issuers": set(), "sources": set()})
        item["metadata_rows"] += 1
        item["issuers"].add(r["ticker"])
        item["sources"].add(r["source"])
    dates = [dict(reported_date=key, metadata_rows=v["metadata_rows"],
                  distinct_issuers=len(v["issuers"]), issuers="|".join(sorted(v["issuers"])),
                  sources="|".join(sorted(v["sources"]))) for key, v in sorted(dated.items())]
    artifacts = {
        "design_report_metadata.csv": csvbytes(selected, columns),
        "metadata_exceptions.csv": csvbytes(exceptions, columns),
        "repeated_identity_groups.csv": csvbytes(duplicate_rows, (*columns, "same_source_issuer_fiscal_key_count")),
        "yearly_census.csv": csvbytes(summaries, ("source", "year", "metadata_rows", "issuers", "distinct_report_dates", "pre_market", "post_market", "unknown_labels")),
        "combined_report_dates.csv": csvbytes(dates, ("reported_date", "metadata_rows", "distinct_issuers", "issuers", "sources")),
    }
    if hashes != {p: digest(ROOT / p) for p in bound_paths}:
        raise RuntimeError("Source changed during census; no successful artifact written.")
    manifest = dict(
        audit="forward_guidance_metadata_input_gate", decision="NEEDS DATA",
        completed_utc=datetime.now(timezone.utc).isoformat(), plan=PLAN, source_plan_commit=PLAN_COMMIT,
        economic_preregistration=False, new_economic_configurations=0, new_return_trials=0,
        execution_workspace=str(ROOT), interpreter="/workspace/venvs/thebeginning/bin/python",
        git_head=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        script="analysis/codex_forward_guidance_input_gate.py", script_sha256=digest(Path(__file__)),
        input_sha256=hashes, schemas=schemas, metadata_fields_used=list(META),
        source_metadata_rows=all_metadata_counts, outside_design_or_invalid_report_date_rows=excluded,
        design_window="2018-01-01 through 2022-12-31, by reportedDate only",
        selected_metadata_rows=len(selected), distinct_design_report_dates=len(dates),
        distinct_design_issuers=len({r["ticker"] for r in selected}),
        simultaneous_multi_issuer_report_dates=sum(r["distinct_issuers"] > 1 for r in dates),
        repeated_same_source_issuer_fiscal_groups=sum(v > 1 for v in identity_counts.values()),
        repeated_identity_rows=len(duplicate_rows), exceptions=len(exceptions),
        economic_events_observed=False, original_guidance_documents_observed=False,
        exact_receipt_timestamps_observed=False, original_data_vintages_established=False,
        historical_index_membership_and_weights_observed=False,
        prices_read=False, eps_or_surprise_values_used=False, financial_outputs_read=False,
        strategy_signals_generated=False, strategy_paths_replayed=False, network_requests=0,
        limits=[
            "Report dates are a local metadata opportunity ceiling, not guidance events, trading dates or independent samples.",
            "A metadata key repetition is retained without assuming duplicate error or original release identity.",
            "Pre/post-market labels do not establish exact release/receipt or DST clocks.",
            "Current collected issuer sets do not establish historical membership; selection/survivorship remains unresolved.",
            "No price-only or EPS-derived substitute, threshold, clock or economic rule is authorized.",
        ],
        artifacts_sha256={name: hashlib.sha256(blob).hexdigest() for name, blob in artifacts.items()},
    )
    OUT.mkdir(parents=True, exist_ok=True)
    for name, blob in artifacts.items():
        (OUT / name).write_bytes(blob)
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps({key: manifest[key] for key in ("decision", "selected_metadata_rows", "distinct_design_report_dates", "distinct_design_issuers", "simultaneous_multi_issuer_report_dates", "repeated_identity_rows", "exceptions", "new_return_trials")}))


if __name__ == "__main__":
    main()
