"""Compare published table cells and a printed reward identity; no market returns.

python analysis/codex_7013523_source_check.py UPLOADED.pdf --output OUTPUT.json
Requires pdftotext. The original PDF is already archived in the research repository.
"""
import argparse
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import re
import subprocess


ROOT = Path(__file__).resolve().parents[1]
ORIGINAL = ROOT / "agents/codex/inputs/rl_ensemble_3690996_20261030/source.pdf"
ROWS = ("Cumulative Return", "Annual Return", "Annual Volatility", "Sharpe Ratio", "Max Drawdown")
COLUMNS = ("Ensemble", "PPO", "A2C", "DDPG", "Min-Variance", "DJIA")


def table(path):
    text = subprocess.check_output(["pdftotext", "-layout", str(path), "-"], text=True).replace("−", "-")
    result = {}
    for label in ROWS:
        rows = re.findall(r"^\s*" + re.escape(label) + r"\s+([^\n]+)$", text, re.MULTILINE)
        if len(rows) != 1:
            raise ValueError(f"Expected exactly one table row: {label}")
        values = re.findall(r"-?\d+(?:\.\d+)?%?", rows[0])
        if len(values) != 6:
            raise ValueError(f"Expected six cells: {label}")
        result[label] = values
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("uploaded_pdf", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    uploaded, original = table(args.uploaded_pdf), table(ORIGINAL)
    matches = sum(Decimal(a.rstrip("%")) == Decimal(b.rstrip("%"))
                  for label in ROWS for a, b in zip(uploaded[label], original[label]))
    if matches != 30:
        raise ValueError(f"Table differs: {matches}/30 numerical cells match")
    # Constructed one-stock purchase, illustrating printed Eq. 4 versus Eqs. 6/9.
    # Eq. 1 excludes fees from its cash update; Eq. 4 subtracts the fee separately.
    cash, p0, p1, held, bought = map(Decimal, ("1000", "100", "110", "0", "1"))
    fee = p0 * bought * Decimal("0.001")
    after_cash_before_fee = cash - p0 * bought
    nav_reward = after_cash_before_fee + p1 * (held + bought) - (cash + p0 * held) - fee
    printed_expansion = (p1 - p0) * held - fee
    assert nav_reward == Decimal("9.90") and printed_expansion == Decimal("-0.10")
    result = dict(
        status="SOURCE_COMPARISON_AND_CONSTRUCTED_ARITHMETIC_ONLY", economic_trials=0,
        original_source="Yang, Liu, Zhong and Walid (2020), SSRN 3690996",
        uploaded_source="Dikshant Lama (2026), SSRN 7013523", columns=COLUMNS,
        uploaded_table=uploaded, original_table=original, matching_numerical_cells=matches,
        printed_equation_example=dict(cash_usd=str(cash), old_shares=str(held), buy_shares=str(bought),
            fill_price=str(p0), next_mark=str(p1), fee_usd=str(fee),
            nav_reward_eq4_usd=str(nav_reward), printed_eq6_eq9_usd=str(printed_expansion),
            limitation="Constructed printed-equation inconsistency; no claim about unavailable author runtime"),
        sha256={"uploaded_pdf": hashlib.sha256(args.uploaded_pdf.read_bytes()).hexdigest(),
                "original_pdf": hashlib.sha256(ORIGINAL.read_bytes()).hexdigest(),
                "script": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()})
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(f"30/30 published table values match; constructed reward identity differs; saved {args.output}")


if __name__ == "__main__":
    main()
