"""Paper/code consistency and delivered-panel metadata; no financial return test."""
import csv
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "agents/codex/inputs/assemblage_var_7508198"
UP = BASE / "upstream"


def main():
    # Invented fixture: every named constituent has zero time mean. Ranks do not.
    panel = [[-1.0, 1.0], [1.0, -1.0]]
    ranks = [sorted(row) for row in panel]
    mean_cols = lambda x: [sum(c) / len(c) for c in zip(*x)]
    assert mean_cols(panel) == [0.0, 0.0]
    assert mean_cols(ranks) == [-1.0, 1.0]
    # Nonnegative weights summing to one do not force a zero rank-index mean.
    w = [1.0, 0.0]
    rank_mean = sum(a * b for a, b in zip(w, mean_cols(ranks)))
    assert rank_mean == -1.0
    # Equal weights do preserve the cross-sectional mean, before/after sorting.
    assert [sum(r) / 2 for r in panel] == [sum(r) / 2 for r in ranks]
    # Static paper/code convention comparison; not a VAR fit.
    named_penalty = sum((a - .5) ** 2 for a in [.75, .25])
    code_penalty = sum(sd * (a - .5) ** 2 for sd, a in zip([1, 2], [.75, .25]))
    assert named_penalty == .125 and code_penalty == .1875
    gain_paper = 10 / 2 * math.log(4)
    gain_code = 10 * math.log(4)
    assert gain_code == 2 * gain_paper
    est = (UP / "code/funcs/estimation.R").read_text()
    cv = (UP / "code/funcs/cv.R").read_text()
    irf = (UP / "code/02_irf_bands.R").read_text()
    assert "if (rank) {" in est and "confun = eq_mean" in est
    assert "sum(diff(est$comps_sd * w)^2)" in est
    assert "sum(est$comps_sd * (w - shrink_to)^2)" in est
    assert "holdout = 0L" in cv and "holdout_gain(des$Z" in cv
    assert "use_dummies = !is_bench" in irf
    delivered = {}
    for p in sorted((UP / "data").glob("*transformed.csv")):
        with p.open() as f:
            reader = csv.reader(f)
            header = next(reader)
            rows = list(reader)
        values = [[float(v) for v in row[1:]] for row in rows]
        assert all(math.isfinite(v) for row in values for v in row)
        delivered[p.name] = dict(rows=len(rows), components=len(header) - 1,
                                 start=rows[0][0], end=rows[-1][0],
                                 rank_column_means=mean_cols([sorted(r) for r in values]))
    report = {
        "upstream_url": "https://github.com/timmy-o-toole/Assemblage_VAR",
        "upstream_commit": "530073900c3c1bad158476bedc730e2736c46e66",
        "review_local_date": "2026-11-07",
        "paper_claims_not_reproduced": dict(sample="1975-01 through 2025-04; COVID excluded",
            benchmark_ip_peak_percent=-.16, richer_component_ip_peak_percent=[-.24, -.32],
            bands=.68, regional_wind_weight=.40, national_wind_weight=.65),
        "synthetic_rank_fixture": dict(named_means=mean_cols(panel), rank_means=mean_cols(ranks),
            weights=w, rank_index_mean=rank_mean, conclusion="Printed automatic mean-constraint claim false in general; actual code imposes constraint"),
        "synthetic_penalty_fixture": dict(paper=named_penalty, code_sd_weighted=code_penalty),
        "likelihood_convention": "Code Log0-Log1 is negative twice printed S_T; weighted penalties also differ; do not port lambda unchanged",
        "static_code_findings": ["Rank mean constraint explicit", "CV refits VAR on validation block",
            "CV includes final excluded estimation month", "Benchmark IRF bypasses gap dummies; assembled IRFs enable them"],
        "delivered_panels": delivered,
        "full_R_replication_run": False, "financial_return_trials": 0,
        "hashes": {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                   for p in sorted(BASE.rglob("*")) if p.is_file()},
    }
    report["script_sha256"] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    out = ROOT / "analysis/outputs/codex_assemblage_var_7508198/source_audit.json"
    out.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"panels": {k: [v['rows'], v['components']] for k,v in delivered.items()},
                      "rank_counterexample": "PASS", "static_checks": "PASS", "return_trials": 0}))


if __name__ == "__main__":
    main()
