"""Source receipt and transcribed-count checks only; no market data or returns."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "agents/codex/inputs/literature_atlas_7630598"
OUT = ROOT / "analysis/outputs/codex_literature_atlas_7630598"


def main():
    pdf = SOURCE / "ssrn-7630598.pdf"
    raw_text = subprocess.check_output(["pdftotext", "-layout", str(pdf), "-"])
    assert raw_text == (SOURCE / "full_text.txt").read_bytes()
    info = subprocess.check_output(["pdfinfo", str(pdf)], text=True)
    pages = int(next(s.split(":", 1)[1] for s in info.splitlines() if s.startswith("Pages:")))
    # Manual transcriptions: printed pp.12-14 and 140-141. Not a raw Zotero audit.
    silos = dict(zip(
        ["tsml", "dl", "fin-econ", "microstructure", "decision", "stats",
         "nlp-llm", "practice", "math", "quant-deriv", "other-domain"],
        [180, 176, 136, 115, 104, 95, 88, 55, 49, 43, 24]))
    stages = dict(zip(
        ["signal", "forecast", "validation", "risk", "data", "theory",
         "features", "execution", "portfolio", "regime", "automation"],
        [288, 206, 167, 131, 122, 115, 79, 76, 68, 59, 46]))
    assert sum(silos.values()) == 1065
    assert sum(stages.values()) == 1357
    result = {
        "source_title": "Trading Literature Atlas For Semi-Automated Systematic Trading",
        "source_author": "Sohhom Bandyopadhyay", "source_date": "2026-10-18",
        "review_local_date": "2026-11-07", "pages": pages,
        "silo_transcription": silos, "stage_transcription": stages,
        "silo_sum": sum(silos.values()), "stage_sum": sum(stages.values()),
        "checks": "Transcribed aggregate sums consistent; raw library and classifier unverified",
        "evidence_type": "Narrative atlas of title/abstract classifications; bridge proposals untested",
        "review_scope": "Focused source review: abstract/methodology, table2.1, execution, validation, bridges, blueprint and conclusion; other chapters/bibliography treated as discovery index. Original cited papers not independently reviewed here.",
        "source_url": "https://ssrn.com/abstract=7630598",
        "metadata_check": "Connected primary SSRN result corroborated author, title, 195 pages and October18 written/October20 posted dates",
        "new_economic_trials": 0, "strategy_returns_computed": False,
        "hashes": {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                   for p in [pdf, SOURCE / "full_text.txt", Path(__file__)]},
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "source_audit.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"pages": pages, "silo_sum": sum(silos.values()),
                      "stage_sum": sum(stages.values()), "return_trials": 0}))


if __name__ == "__main__":
    main()
