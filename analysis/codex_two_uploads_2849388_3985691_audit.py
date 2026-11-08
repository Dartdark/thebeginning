"""Audit published arithmetic and invented spread identities, never market returns.

Inputs are the two uploaded papers, their visually checked transcriptions and a
filename/header census. No strategy, optimizer, price cache or external service runs.
"""
from decimal import Decimal as D
import hashlib
import json
from pathlib import Path
import re
import subprocess

import fitz

ROOT = Path(__file__).resolve().parents[1]
INPUTS = ROOT / "agents/codex/inputs"
OUTPUT = ROOT / "analysis/outputs/codex_two_uploads_2849388_3985691"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    sources = {}
    texts = {}
    tables = {}
    for sid, slug, pages in [("2849388", "ctt_gold_2849388", 20),
                             ("3985691", "listing_switch_3985691", 45)]:
        folder = INPUTS / slug
        receipt = json.loads((folder / "access.json").read_text())
        assert sha(folder / "source.pdf") == receipt["sha256"]
        with fitz.open(folder / "source.pdf") as doc:
            assert len(doc) == pages
            metadata = doc.metadata
        texts[sid] = (folder / "source.txt").read_text()
        tables[sid] = json.loads((folder / "transcribed_tables.json").read_text())
        sources[sid] = dict(path=str(folder.relative_to(ROOT)), pdf_pages=pages,
                            pdf_sha256=receipt["sha256"],
                            text_sha256=sha(folder / "source.txt"),
                            transcription_sha256=sha(folder / "transcribed_tables.json"),
                            pdf_metadata=metadata,
                            visually_inspected_pdf_pages=receipt["visually_inspected_pdf_pages"])
    gold = tables["2849388"]
    volume = []
    for row in gold["table4"]:
        assert row["before_lakh_INR"] in texts["2849388"]
        assert row["after_lakh_INR"] in texts["2849388"]
        ratio = D(row["after_lakh_INR"]) / D(row["before_lakh_INR"])
        assert abs(ratio - D(row["printed_ratio"])) < D("0.000003")
        volume.append(dict(window=row["window"], after_before=float(ratio),
                           decline_percent=float(100 * (1 - ratio))))
    volatility = [dict(window=row["window"], sd_increase_percent=float(
        100 * (D(row["sd_after"]) / D(row["sd_before"]) - 1))) for row in gold["table5"]]
    g = gold["modified_GARCH_table6"]
    before = D(g["alpha1"]) + D(g["alpha2"])
    after = before + D(g["alpha4"]) + D(g["alpha5"])
    assert before == D("0.971302") and after == D("0.974387")
    assert D(g["alpha5_p"]) > D("0.05") and D(g["mu1"]) > 0 and D(g["mu1_p"]) > D("0.05")
    assert "0.000320" in texts["2849388"] and "(0.46820)" in texts["2849388"]
    assert "(0.3176)" in texts["2849388"]
    tax_fraction = D(gold["historical_source_seller_tax_percent"]) / 100
    gold_results = dict(volume=volume,
        volume_decline_range_percent=[min(r["decline_percent"] for r in volume), max(r["decline_percent"] for r in volume)],
        volatility_sd=volatility, garch_pre_persistence=float(before), garch_post_persistence=float(after),
        garch_alpha5_p=float(g["alpha5_p"]), garch_mean_shift=float(g["mu1"]), garch_mean_shift_p=float(g["mu1_p"]),
        historical_source_seller_tax_bps=float(tax_fraction * 10000),
        historical_tax_on_one_lakh_INR=float(tax_fraction * 100000),
        qualification="Recomputed published-table arithmetic only, not a causal tax estimate or GARCH fit; historical Indian tax is not a CME charge.")

    nas = tables["3985691"]
    t4, t5, t6 = nas["table4"], nas["table5"], nas["table6"]
    dark_large = D(t5["dark_effective_small_pp"]) + D(t5["dark_effective_large_interaction_pp"])
    lit_large = D(t6["lit_effective_small_pp"]) + D(t6["lit_effective_large_interaction_pp"])
    assert dark_large == D("0.031") and lit_large == D("-0.054")
    assert "0.068" in texts["3985691"] and "-0.037" in texts["3985691"]
    assert "418.316" in texts["3985691"] and "-83.663" in texts["3985691"]
    nas_results = dict(
        quoted_spread_interaction_pp=float(D(nas["table3"]["quoted_spread_interaction_percentage_points"])),
        quoted_spread_interaction_bps=float(100 * D(nas["table3"]["quoted_spread_interaction_percentage_points"])),
        large_dark_volume_total_change_shares=float(1000 * (D(t4["dark_volume_small_change_thousand_shares"]) + D(t4["dark_volume_large_interaction_thousand_shares"]))),
        large_dark_share_total_change_pp=float(100 * (D(t4["dark_share_small_change_fraction"]) + D(t4["dark_share_large_interaction_fraction"]))),
        dark_effective_large_total_change_pp=float(dark_large), lit_effective_large_total_change_pp=float(lit_large),
        lit_effective_pooled_change_pp=float(D(t6["lit_effective_pooled_pp"])),
        matched_fraction_to_Nasdaq=nas["sample"]["matched_to_Nasdaq"] / nas["sample"]["NYSE_to_Nasdaq"],
        matched_fraction_to_NYSE=nas["sample"]["matched_to_NYSE"] / nas["sample"]["Nasdaq_to_NYSE"],
        qualification="Point-estimate coefficient sums, not fitted regressions. Joint SE/covariance unavailable; no significance for sums inferred. Percent units follow source captions, not relative growth or futures profits.")
    spread_cases = []
    for side, price, m0, m5 in [(1, "100.01", "100", "100.02"), (-1, "99.99", "100", "99.98")]:
        p, m, future = D(price), D(m0), D(m5)
        effective = 2 * side * (p - m) / p
        realized = 2 * side * (p - future) / p
        impact = 2 * side * (future - m) / p
        assert abs(effective - realized - impact) < D("1e-24")
        spread_cases.append(dict(side=side, price=price, contemporaneous_midpoint=m0, future_midpoint=m5,
            effective_spread_bps=float(effective * 10000), realized_spread_bps=float(realized * 10000),
            signed_midpoint_impact_bps=float(impact * 10000), identity_holds=True))

    names = sorted(subprocess.check_output(["rg", "--files", "data", "mc_reports"], cwd=ROOT, text=True).splitlines())
    pattern = re.compile(r"mcx|\btaq\b|crsp|compustat|ibes|listing.switch|nastraq", re.I)
    hits = [s for s in names if pattern.search(s)]
    headers = {}
    for rel in ["data/NQ_1min_2018.csv", "data/GC_1min_2018.csv"]:
        with (ROOT / rel).open(errors="replace") as f:
            headers[rel] = f.readline().strip()
    progress = json.loads((ROOT / "agents/codex/research/scout/progress.json").read_text())
    return dict(scope="Two requested upload reviews: source arithmetic, units and invented spread identity only",
        sources=sources, gold=gold_results, listing_switch=nas_results, invented_spread_cases=spread_cases,
        owned_filename_census=dict(files=len(names),matching_names=hits,inspected_headers=headers,
            limitation="Filename/header check only. Owned GC/NQ OHLCV exports do not establish MCX 2011-16 panels or equity NBBO/ATS/event records. No market-return rows loaded."),
        budgets=dict(hypotheses=progress["hypotheses_started"],economic_definitions=progress["economic_definitions"],
                     progress_trials_sha256=hashlib.sha256(json.dumps(progress["trials"],sort_keys=True,separators=(",", ":")).encode()).hexdigest(),
                     root_trials_sha256=sha(ROOT / "TRIALS.csv")),
        market_return_tests=0,new_hypotheses=0,new_economic_definitions=0,
        independent_empirical_verification=False,original_data_or_author_code_executed=False,
        external_messages_or_live_actions=False)


if __name__ == "__main__":
    result = main()
    OUTPUT.mkdir(parents=True, exist_ok=True)
    (OUTPUT / "source_audit.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({k: result[k] for k in ["gold", "listing_switch", "market_return_tests", "new_economic_definitions"]}, indent=2))
