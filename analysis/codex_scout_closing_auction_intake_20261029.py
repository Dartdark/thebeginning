"""Bounded public-source acquisition for one scout cycle; never computes returns.

Downloads are local-only. Records failures and hashes; no credentials or vendor SDKs.
Run from the research repository using the configured Python environment.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import urllib.error
import urllib.request

SOURCES = {
    "author_auction_data": "https://www.dropbox.com/scl/fi/rork4v1osy8arvc0ezsm2/auction_data.zip?rlkey=qu9uacnrbuxxf4zbyfifgoht8&dl=1",
    "mendeley_file_inventory": "https://data.mendeley.com/public-api/datasets/dcrnzrmfxy/versions/1/files",
    "challet_full_source": "https://arxiv.org/html/1802.01921v2",
    "bogousslavsky_full_source": "https://www.aeaweb.org/conference/2021/preliminary/paper/H9T4hef7",
    "nasdaq_noii_directory": "https://emi.nasdaq.com/ITCH/Nasdaq%20ITCH/NOII/",
}
LIMIT = 32 * 1024 * 1024


def acquire(item, destination):
    name, url = item
    started = datetime.now(timezone.utc).isoformat()
    result = {"name": name, "url": url, "attempted_at": started,
              "access": "named_public_url_normal_proxy", "return_work": False}
    path = destination / (name + ".source")
    if path.exists():
        raw = path.read_bytes()
        result.update(status="existing_bytes_preserved", bytes=len(raw),
                      sha256=hashlib.sha256(raw).hexdigest(), local_path=str(path))
        return result
    try:
        request = urllib.request.Request(url, headers={"User-Agent": "BeginningResearch/1.0 public research intake"})
        with urllib.request.urlopen(request, timeout=12) as response:
            size = response.headers.get("Content-Length")
            if size and int(size) > LIMIT:
                raise ValueError("Advertised artifact exceeds 32MiB intake limit; no partial file accepted")
            raw = response.read(LIMIT + 1)
            if len(raw) > LIMIT:
                raise ValueError("Artifact exceeds 32MiB intake limit; no partial file accepted")
            content_type = response.headers.get("Content-Type", "")
            with path.open("xb") as handle:
                handle.write(raw)
            result.update(status="downloaded_unvalidated", http_status=response.status,
                          content_type=content_type, bytes=len(raw),
                          sha256=hashlib.sha256(raw).hexdigest(), local_path=str(path))
    except urllib.error.HTTPError as exc:
        result.update(status="http_denied_or_unavailable", http_status=exc.code,
                      error=exc.reason)
    except (urllib.error.URLError, TimeoutError, ValueError, OSError) as exc:
        result.update(status="unavailable", error=type(exc).__name__ + ": " + str(exc))
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--download", action="store_true", help="Attempt each named public URL once")
    parser.add_argument("--summarize", action="store_true", help="Summarize existing receipts; no network or returns")
    parser.add_argument("--root", type=Path, default=Path("."))
    args = parser.parse_args()
    output = args.root / "analysis/outputs/codex_scout_closing_auctions_20261029"
    target = output / "acquisition_receipts.json"
    if args.summarize:
        receipt = json.loads(target.read_text(encoding="utf-8"))
        summary = {
            "return_tests_executed": False,
            "attempts": len(receipt["attempts"]),
            "downloads": sum(r["status"] == "downloaded_unvalidated" for r in receipt["attempts"]),
            "planning_only": [{"assumed_events": n, "assumed_sd_nq_usd": 300,
                               "net_mean_for_t2_usd": 600 / math.sqrt(n),
                               "gross_mean_with_17_25_nq_cost_usd": 600 / math.sqrt(n) + 17.25}
                              for n in (249, 124)],
            "warning": "Planning assumptions from existing QQQ evidence; no observed candidate SD or alpha."
        }
        (output / "feasibility_summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(summary, indent=2))
        return
    if not args.download:
        print(json.dumps(SOURCES, indent=2))
        return
    if target.exists():
        print(target.read_text(encoding="utf-8"))
        return  # Preserve history and do not retry an unchanged denial.
    local = args.root / "agents/codex/inputs/scout_closing_auctions_20261029/local"
    local.mkdir(parents=True, exist_ok=True)
    with ThreadPoolExecutor(max_workers=5) as executor:
        receipts = list(executor.map(lambda item: acquire(item, local), SOURCES.items()))
    report = {"cycle": "scout-closing-auctions-20261029", "return_tests_executed": False,
              "attempts": receipts, "no_retry_after_denial": True,
              "note": "HTTP success is not a data, source-version, licence or trading-availability pass."}
    output.mkdir(parents=True, exist_ok=True)
    with target.open("x", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2)
        handle.write("\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
