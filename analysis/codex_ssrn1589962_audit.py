"""Audit printed model arithmetic in SSRN1589962; no fitted model or returns.

Run from the repository root: python analysis/codex_ssrn1589962_audit.py
Inputs below are transcribed from Tables 2/3, printed pages 14/15.
"""
from decimal import Decimal
import hashlib
import json
import math
from pathlib import Path

SOURCE = Path("agents/codex/inputs/ssrn1589962/source.pdf")
OUT = Path("analysis/outputs/codex_ssrn1589962_review")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    garch = {"alpha": "0.3878", "beta": "0.5659"}
    gjr = {"alpha": "0.150", "beta": "0.601", "gamma": "0.745"}
    normal_p = lambda t: math.erfc(abs(t) / math.sqrt(2))
    marked = {"GARCH alpha0": 2.381, "GJR alpha1": 2.148,
              "GJR gamma1": 2.557, "GJR delta3": -2.315}
    result = {
        "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        "source_bytes": SOURCE.stat().st_size,
        "evidence_kind": "printed-parameter arithmetic, not independent estimation",
        "return_trials": 0,
        "garch_table2": garch,
        "gjr_table3": gjr,
        "garch_alpha_plus_beta": str(sum(map(Decimal, garch.values()))),
        "gjr_alpha_plus_beta_omits_asymmetry": str(Decimal(gjr["alpha"]) + Decimal(gjr["beta"])),
        "gjr_symmetric_innovation_feedback": str(Decimal(gjr["alpha"]) + Decimal(gjr["beta"]) + Decimal(gjr["gamma"]) / 2),
        "qualification": "alpha+beta+gamma/2 is the standard GJR feedback under symmetric standardized innovations. Exogenous variance regressors require additional assumptions; no empirical stationarity conclusion is established here.",
        "selected_t_statistics_marked_one_percent": {
            k: {"printed_t": t, "two_sided_asymptotic_normal_p": normal_p(t)}
            for k, t in marked.items()
        },
        "garch_expected_volume_table2": "-0.3486",
        "garch_expected_volume_prose_page10": "-3.483",
    }
    (OUT / "model_arithmetic.json").write_text(json.dumps(result, indent=2) + "\n")
    manifest = {
        "title": "Futures Trading and Spot Market Volatility: A Case of S&P CNX Nifty Index",
        "authors": ["P. Sakthivel", "B. Kamaiah"],
        "source_url": "https://ssrn.com/abstract=1589962",
        "source": "user-uploaded ssrn-1589962.pdf, 15 pages",
        "publication_note": "Accepted Series: GITAM Review of International Business; publication date not verified",
        "sha256": result["source_sha256"], "bytes": SOURCE.stat().st_size,
        "sample_as_reported": ["2000-07-01", "2008-02-28"],
        "review_scope": "full-text review and deterministic arithmetic check; no model estimation, forecast test, strategy return test or account simulation",
    }
    (SOURCE.parent / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
