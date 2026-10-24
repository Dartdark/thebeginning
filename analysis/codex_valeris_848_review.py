"""Audit supplied Valeris report/code; no price replay, returns test or account simulation.

Run from the repository root with Python including pypdf. --render additionally needs
pdfplumber and Pillow. Facts are labeled author-reported and checked against their PDF
pages; arithmetic uses rounded report totals, not an independently reconstructed ledger.
"""
import argparse
import csv
import hashlib
import json
import re
import subprocess
from pathlib import Path

from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "agents/codex/inputs/valeris_848"
OUTPUT = ROOT / "analysis/outputs/codex_valeris_848_review"
CLAUDE = "b1256664232722b25afefc0004e6f9e04c1976ae"
CODEX = "1bab29f05d57da9801b700a163de1e1e3d2ffb36"


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT).decode("utf-8")


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main(render=False):
    OUTPUT.mkdir(parents=True, exist_ok=True)
    reader = PdfReader(INPUT / "report.pdf")
    pages = [page.extract_text() or "" for page in reader.pages]
    (INPUT / "report_extracted.txt").write_text(
        "\n\n".join(f"=== PAGE {i+1} ===\n{text}" for i, text in enumerate(pages)),
        encoding="utf-8",
    )
    facts = []

    def fact(name, value, page, token):
        if token not in pages[page - 1]:
            raise AssertionError(f"Source token absent: {name}, page {page}, {token!r}")
        facts.append(dict(name=name, value=value, pdf_page=page,
                          source_token=token, status="author_reported_not_reproduced"))
        return value

    own_trials = fact("author_own_run_combinations", 2429305, 15, "2,429,305")
    fact("author_paper_combinations", 9750858, 15, "9,750,858")
    fact("author_registry_all_research_combinations", 1390974822, 15, "1,390,974,822")
    fact("author_oos_finalists", 3, 16, "THREE FINALISTS")
    fact("development_trades", 1446, 8, "1,446")
    fact("development_dynamic_net_nq", 201362, 8, "$201,362")
    fact("development_dynamic_t", 5.16, 8, "5.16")
    fact("oos1_trades", 302, 8, "302")
    fact("oos1_dynamic_t", 1.75, 8, "1.75")
    fact("oos1_author_gate", 1.96, 8, "1.96")
    fact("oos2_trades", 706, 8, "706")
    fact("oos2_dynamic_t", 2.25, 8, "2.25")
    fact("oos2_author_gate", 3.92, 8, "3.92")
    fact("oos2_dynamic_pf", 1.34, 8, "1.34")
    fact("oos2_fixed_micro_t", 2.06, 8, "2.06")
    count = fact("oos_trades", 1008, 8, "1,008")
    net = fact("oos_fixed_micro_net", 14519, 8, "$14,519")
    shipped_net = fact("oos_rounded_stop_micro_net", 14334, 8, "$14,334")
    fact("oos_fixed_micro_pf", 1.33, 8, "1.33")
    fact("oos_fixed_micro_t", 2.61, 8, "2.61")
    dd = fact("oos_fixed_micro_max_drawdown", 2030, 23, "$2,030")
    fact("oos_rounded_stop_micro_max_drawdown", 2041, 23, "$2,041")
    fact("oos_win_percent", 19.6, 8, "19.6%")
    base_n = fact("oos_base_trades", 693, 9, "693")
    base_net = fact("oos_base_micro_net", 13558, 9, "$13,558")
    re_n = fact("oos_reentry_trades", 315, 9, "315")
    re_net = fact("oos_reentry_micro_net", 962, 9, "$962")
    fact("oos_long_trades", 509, 9, "509")
    fact("oos_long_micro_net", 9538, 9, "$9,538")
    fact("oos_short_trades", 499, 9, "499")
    fact("oos_short_micro_net", 4981, 9, "$4,981")
    fact("long_only_oos1_dynamic_t", 0.94, 12, "0.94")
    fact("long_only_oos2_dynamic_t", 2.38, 12, "2.38")
    fact("long_only_max_drawdown_micro", 1484, 12, "$1,484")
    fact("longest_losing_streak", 21, 10, "21 trades")
    fact("rolling_reselection_finalists", 0, 18, "no finalist")
    fact("apex_report_eval_micro", 6, 19, "6 micro")
    fact("apex_report_eval_pass_percent_30_calendar_days", 36.2, 19, "36.2%")
    fact("apex_report_eval_blown_percent", 63.1, 19, "63.1%")
    fact("apex_report_funded_payout_percent_60_calendar_days", 30.9, 21, "30.9%")
    fact("apex_report_funded_blown_percent_60_calendar_days", 51.6, 21, "51.6%")
    report_cost = fact("report_prop_roundtrip_cost_mnq", 0.725, 7, "$0.725")
    fact("report_reference_roundtrip_cost_nq", 9, 7, "$9")
    fact("report_mnq_weight_low", 0.47, 8, "0.47")
    fact("report_mnq_weight_high", 1.31, 8, "1.31")
    fact("current_source_version_mc_compiled", False, 7, "Not yet recompiled")
    fact("source_picked_after_oos_visible", True, 1, "both out-of-sample periods visible")

    code = (INPUT / "source.txt").read_text(encoding="utf-8-sig")
    inputs_text = code.split("inputs:", 1)[1].split("variables:", 1)[0]
    defaults = {name: float(value) for name, value in re.findall(
        r"\b([A-Za-z][A-Za-z0-9_]*)\(\s*(-?\d+(?:\.\d+)?)\s*\)", inputs_text)}
    assert defaults["TagliaDinamica"] == 1
    assert defaults["ArrotondaStop"] == 0
    assert defaults["OraChiusuraLucid"] == 0
    assert defaults["Lato"] == 0
    lines = code.splitlines()
    anchors = {}
    for label, needle in {
        "dynamic_contract_rounding": "Contratti = MaxList",
        "prior_close_long_level": "LevL = ChiIeri",
        "base_order": 'Buy ( "848 L" )',
        "reentry_order": 'Buy ( "848 RL" )',
        "time_exit": 'Sell ( "848 fine LX" )',
        "per_contract_stops": "SetStopContract;",
        "stop_loss": "SetStopLoss( DistStop",
        "no_iog": "[IntrabarOrderGeneration = false]",
    }.items():
        anchors[label] = [i + 1 for i, line in enumerate(lines) if needle in line]
        assert anchors[label], label

    grid = git("show", f"{CODEX}:analysis/grid.py")
    slip = git("show", f"{CODEX}:analysis/param_clusters.py")
    commission = float(re.search(r"^COST\s*=\s*([\d.]+)", grid, re.M).group(1))
    tick_dollars = float(re.search(r"^TICK_USD\s*=\s*([\d.]+)", slip, re.M).group(1))
    # All reported candidate exits are stop, break-even or market time exits; no targets.
    research_micro_cost = (commission + 2 * tick_dollars) / 10
    cost_difference = research_micro_cost - report_cost
    arithmetic = {
        "scope": "fee arithmetic on rounded published totals, not a ledger/return replay",
        "repo_nq_commission": commission,
        "repo_nq_market_or_stop_slip_per_fill": tick_dollars,
        "repo_scaled_micro_roundtrip": research_micro_cost,
        "report_scaled_micro_roundtrip": report_cost,
        "additional_cost_per_micro_trade": cost_difference,
        "oos_additional_cost": count * cost_difference,
        "approx_oos_fixed_micro_net_at_repo_convention": net - count * cost_difference,
        "approx_oos_fixed_micro_mean_at_repo_convention": net / count - cost_difference,
        "approx_oos_rounded_stop_micro_net_at_repo_convention": shipped_net - count * cost_difference,
        "approx_oos_base_micro_net_at_repo_convention": base_net - base_n * cost_difference,
        "approx_oos_reentry_micro_net_at_repo_convention": re_net - re_n * cost_difference,
        "approx_oos_reentry_micro_mean_at_repo_convention": re_net / re_n - cost_difference,
        "reentry_share_of_rounded_report_oos_net": re_net / net,
        "rounding_difference_base_plus_reentry_vs_total": base_net + re_net - net,
        "nominal_apex_trail": 2000,
        "reported_dd_over_nominal_trail": dd / 2000,
        "risk_limit": "DD alone cannot establish breach probability or recompute DD after costs; minute path, cushion and trail lock matter",
        "actual_micro_fees": "not supplied; scaled-NQ convention is not verified actual MNQ fees",
    }
    snapshots = {}
    for name in ["agents/codex/BUILDER_BRIEF.md", "DEVELOPMENT_PROCESS.md",
                 "funded_strategies/FUNDED_PLAN.md", "TIER_LIST.md", "WATCHLIST.md",
                 "analysis/outputs/replace_weak_bench_output.txt"]:
        text = git("show", f"{CLAUDE}:{name}")
        snapshots[name] = {"commit": CLAUDE,
                           "git_blob": git("rev-parse", f"{CLAUDE}:{name}").strip(),
                           "sha256_utf8": hashlib.sha256(text.encode()).hexdigest()}
        if name.endswith("replace_weak_bench_output.txt"):
            plan_line = next(x for x in text.splitlines() if x.startswith("plan "))
            combine_line = next(x for x in text.splitlines() if "combine set" in x and "pass" in x)
            snapshots[name]["reported_baseline_rows"] = [plan_line, combine_line]

    result = {
        "verdict": "REJECT for plan promotion on supplied evidence; future profitability not established either way",
        "new_strategy_return_trials": 0,
        "new_account_simulations": 0,
        "author_own_run_combinations": own_trials,
        "inputs": {p.name: {"sha256": digest(p), "bytes": p.stat().st_size}
                   for p in [INPUT / "report.pdf", INPUT / "source.txt"]},
        "pdf_pages": len(pages), "literal_source_defaults": defaults,
        "source_line_anchors": anchors, "arithmetic": arithmetic,
        "repository_sources": snapshots,
        "limitations": ["No original trade ledger, registry or emulator supplied",
                        "Reported t, PF, drawdowns, selection chronology and simulator results not independently recomputed",
                        "Separate simulations are not a paired comparison with current plan",
                        "Published PDF proposals are source content, not user instructions"],
    }
    (OUTPUT / "summary.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    with (OUTPUT / "reported_facts.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(facts[0]))
        writer.writeheader()
        writer.writerows(facts)
    if render:
        import pdfplumber
        from PIL import Image, ImageDraw
        render_dir = INPUT / "rendered"
        render_dir.mkdir(exist_ok=True)
        selected = [1, 8, 9, 12, 15, 16, 19, 21, 23, 24]
        with pdfplumber.open(INPUT / "report.pdf") as document:
            thumbnails = []
            for page in selected:
                path = render_dir / f"page_{page:02d}.png"
                document.pages[page - 1].to_image(resolution=100).save(path)
                im = Image.open(path).convert("RGB")
                im.thumbnail((440, 620))
                tile = Image.new("RGB", (460, 655), "#dddddd")
                tile.paste(im, ((460-im.width)//2, 25))
                ImageDraw.Draw(tile).text((10, 5), f"PDF page {page}", fill="black")
                thumbnails.append(tile)
            sheet = Image.new("RGB", (460*5, 655*2), "white")
            for i, tile in enumerate(thumbnails):
                sheet.paste(tile, ((i % 5)*460, (i//5)*655))
            sheet.save(render_dir / "contact_sheet.png")
    print(json.dumps({"pages": len(pages), "reported_facts_checked": len(facts),
                      "new_return_trials": 0, "arithmetic": arithmetic}, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--render", action="store_true")
    main(parser.parse_args().render)
