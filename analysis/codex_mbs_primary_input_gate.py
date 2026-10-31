"""Reproduce the bounded saved-PDF content audit, without prices or returns.

This is a source-content search, not a primary-data sufficiency test. Absence of
one of the terms does not establish absence of every relevant economic concept.
Human review is still required; no TEST decision follows from term counts.
"""

from __future__ import annotations

import csv
import hashlib
import io
import json
from pathlib import Path
import re
import subprocess
from datetime import datetime, timezone


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "analysis/outputs/codex_mbs_primary_input_gate"
SOURCE_HASHES = {
    "papers/ssrn-1405583.pdf": "107648166b70e3f991b17bcf48575801472129247cf724ed61e7eb8426176095",
    "papers/ssrn-2679218.pdf": "fc1c13d5514f48b18aaef3a19efac4092a8fe8133c70b9904ce751714da1ab94",
    "papers/ssrn-3247865.pdf": "1bc54915eb2778b1b6a8eacfa0b07fb8c568f2cd5caa3ded45fa28f47c83c73e",
    "papers/ssrn-4501707.pdf": "e2068d89c2a7bfe38de36f695186991a16b6e5c87724751083d351993f119cce",
}
TERMS = ("mortgage", "MBS", "prepayment", "negative convexity", "DV01")
PATTERN_TEXT = "|".join(r"\b" + re.escape(term) + r"\b" for term in TERMS)
PATTERN = re.compile(PATTERN_TEXT, re.IGNORECASE)
FIELDS = ("source", "sha256", "pdf_page", "match_index_on_page", "term", "matched_text", "context")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def normalize_text(value: str) -> str:
    return " ".join(value.split())


def main() -> None:
    # An audit against unchanged hashes is not a new research observation.
    # Refuse to overwrite a successful retained audit.
    if (OUTPUT / "manifest.json").exists():
        raise SystemExit("A retained audit already exists; do not repeat the same-hash audit.")

    rows = []
    sources = []
    for relative, expected_hash in SOURCE_HASHES.items():
        source = ROOT / relative
        source_bytes = source.read_bytes()
        actual_hash = sha256_bytes(source_bytes)
        if actual_hash != expected_hash:
            raise SystemExit(f"Reviewed source hash changed: {relative}")
        converted = subprocess.check_output(
            ["pdftotext", str(source), "-"], text=True, encoding="utf-8"
        )
        pages = converted.split("\f")
        if pages and not pages[-1].strip():
            pages.pop()
        counts = {term: 0 for term in TERMS}
        matched_pages = set()
        source_hits = 0
        for page_number, page in enumerate(pages, start=1):
            for hit_index, match in enumerate(PATTERN.finditer(page), start=1):
                matched = match.group(0)
                term = next(term for term in TERMS if term.casefold() == matched.casefold())
                counts[term] += 1
                source_hits += 1
                matched_pages.add(page_number)
                rows.append(
                    {
                        "source": relative,
                        "sha256": actual_hash,
                        "pdf_page": page_number,
                        "match_index_on_page": hit_index,
                        "term": term,
                        "matched_text": matched,
                        "context": normalize_text(
                            page[max(0, match.start() - 150) : match.end() + 250]
                        ),
                    }
                )
        # Do not bind counts to a file that changed during extraction.
        if sha256_bytes(source.read_bytes()) != expected_hash:
            raise SystemExit(f"Reviewed source changed during extraction: {relative}")
        sources.append(
            {
                "source": relative,
                "sha256": actual_hash,
                "bytes": len(source_bytes),
                "pdf_pages": len(pages),
                "first_page_excerpt": normalize_text(pages[0])[:1000],
                "term_counts": counts,
                "total_hits": source_hits,
                "matched_pdf_pages": sorted(matched_pages),
            }
        )

    csv_buffer = io.StringIO(newline="")
    writer = csv.DictWriter(csv_buffer, fieldnames=FIELDS, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    csv_bytes = csv_buffer.getvalue().encode("utf-8")
    version = subprocess.run(
        ["pdftotext", "-v"], capture_output=True, text=True, check=True
    )
    manifest = {
        "audit": "mbs_primary_input_gate_20261026",
        "purpose": "Reproducibility of the existing bounded saved-PDF source-content audit",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "command": "/workspace/venvs/thebeginning/bin/python -B analysis/codex_mbs_primary_input_gate.py",
        "script": "analysis/codex_mbs_primary_input_gate.py",
        "script_sha256": sha256_bytes(Path(__file__).read_bytes()),
        "base_git_commit": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip(),
        "pdftotext_version": (version.stdout + version.stderr).splitlines()[0],
        "page_number_basis": "One-based PDF pages separated by pdftotext form-feed characters",
        "search_regex": PATTERN_TEXT,
        "search_flags": ["IGNORECASE"],
        "context_bounds_characters": {"before": 150, "after": 250},
        "sources": sources,
        "page_hits_csv": "analysis/outputs/codex_mbs_primary_input_gate/page_hits.csv",
        "page_hits_csv_sha256": sha256_bytes(csv_bytes),
        "total_hits": len(rows),
        "new_economic_configurations": 0,
        "new_return_trials": 0,
        "prices_or_financial_outputs_read": False,
        "network_requests": 0,
        "automated_finding_limit": (
            "Term counts locate text for manual review; zero matches do not establish absence of "
            "every relevant exposure concept. General literature is not an as-of risk/exposure dataset."
        ),
        "human_decision_report": "agents/codex/research/mbs_primary_input_gate_20261026.md",
        "economic_test_authorized_by_audit": False,
    }
    OUTPUT.mkdir(parents=True, exist_ok=True)
    (OUTPUT / "page_hits.csv").write_bytes(csv_bytes)
    (OUTPUT / "manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(
        json.dumps(
            {"sources": len(sources), "total_hits": len(rows), "new_return_trials": 0,
             "output": str(OUTPUT.relative_to(ROOT))}
        )
    )


if __name__ == "__main__":
    main()
