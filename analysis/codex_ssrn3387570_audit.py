"""Audit printed Table 2 and contract units; no price-data strategy backtest.

Run from repository root: python analysis/codex_ssrn3387570_audit.py
"""
import hashlib
import json
import math
from pathlib import Path
import statistics

from scipy.stats import t as student_t

SOURCE = Path("agents/codex/inputs/ssrn3387570/source.pdf")
OUT = Path("analysis/outputs/codex_ssrn3387570_review")
# Transcribed Table 2, printed p.153, percentages (not decimal returns).
ROWS = [
    (1, 167, 125, 6.51, -2.19), (2, 140, 128, 6.91, 2.50),
    (3, 103, 27, 10.10, -1.51), (4, 155, 52, 10.79, 1.53),
    (5, 87, 12, 11.12, 2.35), (6, 103, 98, 15.88, 2.34),
    (7, 179, 11, 15.86, 2.74), (8, 21, 13, 11.58, 2.91),
    (9, 83, 80, 14.14, -1.37), (10, 89, 57, 15.40, 1.41),
]


def main():
    import csv
    OUT.mkdir(parents=True, exist_ok=True)
    with (OUT / "author_table2.csv").open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["set", "printed_m1", "printed_m2", "training_two_month_pct", "test_one_month_pct"])
        w.writerows(ROWS)
    x = [r[4] for r in ROWS]
    mu, sd = statistics.mean(x), statistics.stdev(x)
    se = sd / math.sqrt(len(x))
    tc = float(student_t.ppf(0.975, df=len(x) - 1))
    audit = {
        "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        "kind": "arithmetic of author-reported rounded table; not independent return replication",
        "return_trials": 0,
        "test_months": len(x), "positive_months": sum(v > 0 for v in x),
        "positive_fraction": sum(v > 0 for v in x) / len(x),
        "source_conclusion_positive_fraction_claim": 0.75,
        "test_mean_pct": mu, "test_sample_sd_pct": sd,
        "worst_test_month_pct": min(x),
        "months_below_minus_one_pct": sum(v < -1 for v in x),
        "illustrative_mean_t": mu / se,
        "illustrative_mean_95pct_ci_pct": [mu - tc * se, mu + tc * se],
        "inference_limits": "Assumes ten independent monthly observations, ignores all model/search selection and source accounting errors. Not a selection-adjusted significance result, prediction interval, drawdown bound or future-performance guarantee.",
        "source_ga": {"population": 60, "generations": 1000, "elite": 5,
                      "MA_min": 2, "MA_max": 180, "unique_candidates_evaluated": "not disclosed"},
        "table_m1_greater_than_m2_all_rows": all(r[1] > r[2] for r in ROWS),
        "naming_limit": "Figure 7 calls m1=11 short and m2=179 long; Table 2 set 7 prints m1=179,m2=11. Do not silently infer author code's direction from column names.",
        "literal_CL_contract_interpretation_only": {
            "source_quantity_claim": 2000, "source_initial_usd": 2000000,
            "CL_barrels_per_contract": 1000,
            "illustrative_price_move_usd_per_barrel": 1,
            "printed_q_times_price_move": 2000,
            "native_CL_price_pnl_usd": 2000000,
            "qualification": "Dimensional illustration only; source code/quantity units unavailable. Does not establish how authors actually computed their results.",
        },
    }
    (OUT / "arithmetic.json").write_text(json.dumps(audit, indent=2) + "\n")
    manifest = {
        "title": "Optimización de estrategias de trading con promedios móviles para futuros de petróleo mediante algoritmos genéticos",
        "authors": ["Arbey Aragón Bohorquez", "Carlos Armando Mejía Vega", "Carlos Andrés Zapata Quimbayo"],
        "publication": "Odeon 15 (2018), pp.139–160",
        "doi": "10.18601/17941113.n15.05", "ssrn": "3387570",
        "source": "user-uploaded ssrn-3387570.pdf; 21 PDF pages; printed p.140 absent",
        "sha256": audit["source_sha256"], "bytes": SOURCE.stat().st_size,
        "source_sample": ["2017-08-01", "2018-07-31"],
        "review_scope": "source review and rounded-table/unit audit; zero new market-data return tests",
    }
    (SOURCE.parent / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(audit, indent=2))


if __name__ == "__main__":
    main()
