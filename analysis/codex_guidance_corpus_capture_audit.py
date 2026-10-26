"""Verify retained public-source captures offline, without executing source code.

This is artifact verification, not a new source acquisition or metadata census.
It cannot establish historical publication/receipt or an economic TEST decision.
"""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = ROOT / "analysis/outputs/codex_guidance_public_source"
REVIEW = DIRECTORY / "review_manifest.json"
OUTPUT = DIRECTORY / "capture_audit.json"
FILE_CAPTURES = {
    "ectsum_readme.json": "repository_readme",
    "ectsum_prepare.json": "remote_preprocessing_source_read_only",
    "ectsum_train_files.json": "corpus_filename_list",
    "ectsum_lyb_ect.json": "derivative_transcript",
    "ectsum_lyb_summary.json": "derivative_summary",
    "ectsum_noc_q2.json": "derivative_transcript",
    "ectsum_noc_q3.json": "derivative_transcript",
    "ectsum_license_txt.json": "repository_license_text",
}
REQUIRED_PROCESSING_LITERALS = (
    "summ_path = f'{dataPath}/gt_summaries/'",
    "summ_lines = [line.strip() for line in f_summ_in.readlines()]",
    "if labels[idx] == 1:",
    "if re.search(pattern7, line_pp):",
    "entry['doc'] = '\\n'.join(doc_lines_new)",
)


def sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def git_blob_sha(value: bytes) -> str:
    frame = b"blob " + str(len(value)).encode("ascii") + b"\0" + value
    return hashlib.sha1(frame).hexdigest()


def main() -> None:
    if OUTPUT.exists():
        raise SystemExit("A retained capture audit exists; do not overwrite or repeat it.")
    review_bytes = REVIEW.read_bytes()
    manifest = json.loads(review_bytes)
    retained = manifest["captures"]
    names = [item["capture"] for item in retained]
    if len(names) != len(set(names)) or any(Path(name).name != name for name in names):
        raise ValueError("Capture manifest has duplicate or unsafe filenames.")
    rows, bodies = [], {}
    for item in retained:
        name = item["capture"]
        raw_bytes = (DIRECTORY / name).read_bytes()
        actual = sha256(raw_bytes)
        if actual != item["sha256"]:
            raise ValueError(f"Retained capture changed: {name}")
        capture = json.loads(raw_bytes)
        if set(capture) != {"capture_id", "tool_response"}:
            raise ValueError(f"Unexpected capture wrapper: {name}")
        if capture["capture_id"] + ".json" != name:
            raise ValueError(f"Capture identity mismatch: {name}")
        structured = capture["tool_response"].get("structuredContent", {})
        reported_blob = structured.get("sha")
        if reported_blob != item["source_git_blob_sha"]:
            raise ValueError(f"Reported file hash mismatch: {name}")
        row = {
            "capture": name,
            "capture_sha256": actual,
            "category": FILE_CAPTURES.get(name, "discovery_metadata_or_error"),
            "exact_request_arguments_retained": False,
            "response_display_url": structured.get("display_url"),
            "error": structured.get("error"),
        }
        if name in FILE_CAPTURES:
            if structured.get("encoding") != "utf-8" or not isinstance(structured.get("content"), str):
                raise ValueError(f"Expected UTF-8 file response: {name}")
            source_bytes = structured["content"].encode("utf-8")
            reconstructed = git_blob_sha(source_bytes)
            if reconstructed != reported_blob:
                raise ValueError(f"Reconstructed Git blob hash mismatch: {name}")
            row.update(source_git_blob_sha=reported_blob,
                       reconstructed_git_blob_sha=reconstructed,
                       source_text_sha256=sha256(source_bytes),
                       source_utf8_bytes=len(source_bytes),
                       reconstructed_blob_matches=True)
            bodies[name] = structured["content"]
        elif reported_blob is not None:
            raise ValueError(f"Unclassified file response: {name}")
        rows.append(row)

    if set(bodies) != set(FILE_CAPTURES):
        raise ValueError("The expected file-capture set does not reconcile.")
    source_lines = bodies["ectsum_prepare.json"].splitlines()
    processing = []
    for literal in REQUIRED_PROCESSING_LITERALS:
        hits = [index for index, line in enumerate(source_lines) if literal in line]
        if not hits:
            raise ValueError(f"Expected preprocessing evidence missing: {literal}")
        for index in hits:
            processing.append({
                "literal": literal,
                "source_line": index + 1,
                "bounded_context": [
                    {"source_line": j + 1, "text": source_lines[j][:220]}
                    for j in range(max(0, index - 2), min(len(source_lines), index + 4))
                ],
            })

    # No source content, capture or old manifest may be modified by verification.
    if REVIEW.read_bytes() != review_bytes or any(
        sha256((DIRECTORY / row["capture"]).read_bytes()) != row["capture_sha256"]
        for row in rows
    ):
        raise RuntimeError("Retained inputs changed during offline verification.")
    result = {
        "audit": "offline_guidance_corpus_capture_verification",
        "completed_utc": datetime.now(timezone.utc).isoformat(),
        "script": str(Path(__file__).relative_to(ROOT)),
        "script_sha256": sha256(Path(__file__).read_bytes()),
        "review_manifest": str(REVIEW.relative_to(ROOT)),
        "review_manifest_sha256": sha256(review_bytes),
        "retained_response_count": len(rows),
        "capture_sha256_matches": len(rows),
        "utf8_file_response_count": len(bodies),
        "reconstructed_git_blob_matches": len(bodies),
        "derivative_transcripts": sum(row["category"] == "derivative_transcript" for row in rows),
        "derivative_summaries": sum(row["category"] == "derivative_summary" for row in rows),
        "captures": rows,
        "preprocessing_evidence": processing,
        "processing_finding": (
            "The inspected preprocessing source selects training-document lines using derived-summary "
            "membership or a numerical-pattern condition. It was read as text, never executed. "
            "The inspected transcript fixtures remain distinct from that generated training JSON."
        ),
        "request_ledger_complete": False,
        "limitations": [
            "Wrappers retain capture_id and tool_response, not exact request arguments or independent acquisition timestamps.",
            "Sixteen actual responses are not a complete call ledger; the directory-not-file response was not retained as actual JSON.",
            "Source display URLs and blob hashes cannot reconstruct missing request arguments or original receipt clocks.",
            "The samples were read before receiving the allocation message; no claim is made that they predate the source-plan commit.",
            "The immutable old review manifest's pre-extension wording is qualified by this audit and allocation correction a7a551d.",
            "A repository license does not authenticate third-party transcript rights, original statements or event-time availability.",
            "Hash integrity and processing-code evidence are not proof of a comparable guidance pair, index transmission or delayed price edge.",
        ],
        "allocation_correction_commit": "a7a551d",
        "new_source_fetches": 0,
        "remote_code_executed": False,
        "local_metadata_census_repeated": False,
        "new_economic_configurations": 0,
        "new_return_trials": 0,
        "futures_prices_read": False,
        "strategy_return_files_read": False,
        "admitted_original_guidance_pairs": 0,
        "economic_test_eligible": False,
        "decision": "NEEDS DATA; offline artifact integrity verified only",
    }
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: result[k] for k in (
        "retained_response_count", "utf8_file_response_count", "derivative_transcripts",
        "derivative_summaries", "new_source_fetches", "new_return_trials", "decision"
    )}))


if __name__ == "__main__":
    main()
