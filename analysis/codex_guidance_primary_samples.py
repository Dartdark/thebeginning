"""Audit retained public filing-candidate captures without prices or returns.

Source extension0e991ef, allocation correctiona7a551d. A Git blob match
authenticates repository bytes, not an issuer original or historical receipt.
"""
from __future__ import annotations

import csv
from datetime import datetime, timezone
from html.parser import HTMLParser
import hashlib
import io
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis/outputs/codex_guidance_primary_samples"
PIN = "3931b22077eee1e0d2b77a8c5a61ab415d51ae0b"
SPEC = (
    ("sample_0.json", "data/sgml/0001564590-20-004475-minimal.txt", "2ad0167ad5abb1938c21a61f92b20d7a13180ff4"),
    ("sample_1.json", "data/html/Oracle.8-K.html", "79d7d2e7a5be827776903832c0dffaf1cd8cec92"),
    ("sample_2.json", "LICENSE.txt", "dc9079e0ebc14cc9432b5070a8a23267a399667e"),
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class Text(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.pieces: list[str] = []

    def handle_data(self, data: str) -> None:
        self.pieces.append(data)


def main() -> None:
    if (OUT / "manifest.json").exists():
        raise SystemExit("Retained audit exists; do not repeat unchanged captures.")
    plan = ROOT / "agents/codex/plans/forward_guidance_public_sources.md"
    frozen = subprocess.check_output(
        ["git", "show", "a7a551d:agents/codex/plans/forward_guidance_public_sources.md"], cwd=ROOT
    )
    if plan.read_bytes() != frozen:
        raise ValueError("Source extension differs from committed allocation correction.")
    rows, captures = [], []
    for name, source_path, expected_blob in SPEC:
        path = OUT / "captures" / name
        payload = json.loads(path.read_text())
        request, response = payload["request"], payload["response"]
        assert request == {"repository_full_name": "dgunning/edgartools", "ref": PIN, "path": source_path}
        assert not response.get("isError", False)
        content = response["structuredContent"]
        assert content["sha"] == expected_blob
        body = content["content"].encode("utf-8")
        git_blob = hashlib.sha1(b"blob " + str(len(body)).encode() + b"\0" + body).hexdigest()
        if git_blob != expected_blob:
            raise ValueError("Connector text differs from observed Git blob: " + source_path)
        raw = body.decode("utf-8")
        parser = Text()
        parser.feed(raw)
        text = " ".join(" ".join(parser.pieces).split())
        acceptance = re.findall(r"<ACCEPTANCE-DATETIME>(\d{14})", raw)
        form = re.findall(r"CONFORMED SUBMISSION TYPE:\s*([^\n]+)", raw)
        accession = re.findall(r"ACCESSION NUMBER:\s*([0-9-]+)", raw)
        event_date = re.search(r"Date of Report \(Date of earliest event reported\):\s*(\w+ \d+, \d{4})", text)
        flags = []
        if "-minimal" in source_path:
            flags.append("minimal_fixture_filename")
        if "Multiple complex XBRL tags that caused the original parsing issue" in raw:
            flags.append("authored_parsing_fixture_comment")
        if source_path == "LICENSE.txt":
            decision = "code_license_only_not_guidance_data"
        elif flags:
            decision = "reject_source_admission_reduced_fixture_not_authenticated_original"
        else:
            decision = "reject_source_admission_2024_non_earnings_disclosure_outside_design"
        row = dict(
            capture=name, repository_path=source_path, pinned_commit=PIN,
            git_blob_sha=git_blob, utf8_bytes=len(body),
            content_sha256=hashlib.sha256(body).hexdigest(),
            acceptance_raw="|".join(acceptance), submission_type="|".join(form),
            accession="|".join(accession), event_date=event_date.group(1) if event_date else "",
            guidance_word_matches=len(re.findall(r"\bguidance\b", text, flags=re.I)),
            earnings_word_matches=len(re.findall(r"\bearnings\b", text, flags=re.I)),
            item_202_word_matches=len(re.findall(r"\bItem\s+2\.02\b", text, flags=re.I)),
            fixture_flags="|".join(flags), admission_decision=decision,
            issuer_original_authenticated=False, exact_receipt_established=False,
            same_horizon_guidance_pair_admitted=False,
        )
        # These assertions bind the manual source interpretation to the inspected
        # samples; no automatic term-count TEST or economic selection follows.
        if name == "sample_0.json":
            assert acceptance == ["20200213071218"] and form == ["10-K"]
            assert accession == ["0001564590-20-004475"] and len(flags) == 2
        elif name == "sample_1.json":
            assert row["event_date"] == "November 14, 2024"
            assert "Oracle Corporation" in text and "Item 5.07" in text
            assert row["guidance_word_matches"] == row["earnings_word_matches"] == row["item_202_word_matches"] == 0
        else:
            assert "MIT License" in raw and 'the "Software"' in raw
        rows.append(row)
        captures.append(dict(path=str(path.relative_to(ROOT)), sha256=sha(path)))

    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=list(rows[0]), lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    table = buffer.getvalue().encode()
    manifest = dict(
        kind="retained_public_filing_candidate_source_audit", decision="NEEDS DATA",
        completed_utc=datetime.now(timezone.utc).isoformat(),
        source_extension_commit="0e991ef", allocation_correction_commit="a7a551d",
        source_plan=str(plan.relative_to(ROOT)), source_plan_sha256=sha(plan),
        script="analysis/codex_guidance_primary_samples.py", script_sha256=sha(Path(__file__)),
        pinned_repository="dgunning/edgartools", pinned_commit=PIN,
        captures=captures, samples=rows, filing_candidate_samples=2, code_license_files=1,
        admitted_original_guidance_pairs=0, economic_configurations=0, new_return_trials=0,
        raw_futures_files_read=False, strategy_returns_read_or_calculated=False,
        remote_code_executed=False, network_requests_by_audit_script=0,
        sample_audit_csv_sha256=hashlib.sha256(table).hexdigest(),
        source_interpretation_limit="Git blob identity is repository-byte provenance, not original issuer authenticity, complete release, first publication or actual receipt.",
        discovery_capture_limit=(
            "Earlier root discovery/listing connector responses were visible during the turn but their ephemeral "
            "stores were lost across environment restart before disk retention. No exact raw responses are "
            "reconstructed or claimed. Only the three actual retained file responses above support this audit."
        ),
        derivative_source_review="agents/codex/research/guidance_public_source_20261026.md",
        derivative_manifest="analysis/outputs/codex_guidance_public_source/review_manifest.json",
        no_material_milestone_or_alert=True,
    )
    if any(sha(ROOT / x["path"]) != x["sha256"] for x in captures):
        raise RuntimeError("Capture changed before final audit commit.")
    (OUT / "sample_audit.csv").write_bytes(table)
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps({"decision": manifest["decision"], "candidate_files": 2,
                      "git_blob_checks_passed": len(rows), "admitted_pairs": 0, "new_return_trials": 0}))


if __name__ == "__main__":
    main()
