"""Pure metadata generator for the pre-outcome fixed-quantity admission arm.

The original registry/results stay immutable. This separate arm changes quantity
requests only; source signals, fills, held marks and target/data gates stay fixed.
No market input, source prices or account outcomes are read by this generator.
"""
from __future__ import annotations

import argparse
from itertools import combinations
import json
from pathlib import Path

import codex_eval_policies_20261104 as original

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "agents/codex/inputs/eval_audit_20261104"
SINGLE_LEVELS = (1, 2, 4, 8, 12, 20)
PAIR_LEVELS = (2, 4)
RESERVED_DERIVED = 30
DEFAULT_GOVERNOR = {"risk_fraction": 0., "aggregate_stop_fraction": 1.,
                    "cushion_buffer": 0., "target_guard": False}


def generate(originalregistry):
    """Return new candidates, aliases to originals and exact global counts.

    Accept the frozen registry object or its candidate list. The supplied object
    is never mutated. Canonical identity is exactly the original generator's
    account/book/governor signature; changing a label does not spend a new trial.
    A budget excess raises an error rather than adjusting this prespecified menu.
    """
    old = originalregistry["candidates"] if isinstance(originalregistry, dict) else originalregistry
    if not isinstance(old, list):
        raise TypeError("originalregistry must contain a candidates list")
    seen = {}
    old_ids = set()
    for row in old:
        sig = original.signature(row["account"], row["book"], row["governor"])
        candidate_id = f"E{row['account']}_{sig}"
        if row["candidate_id"] != candidate_id:
            raise ValueError("Original identity mismatch: " + row["candidate_id"])
        if sig in seen or candidate_id in old_ids:
            raise ValueError("Original registry contains duplicate canonical definitions")
        old_ids.add(candidate_id)
        seen[sig] = row
    rows, aliases, requested = [], [], []

    def add(size, family, label, book):
        book = original.canonical(book)
        gov = dict(DEFAULT_GOVERNOR)
        sig = original.signature(size, book, gov)
        requested.append(dict(account=size, family_id=family, label=label,
                              candidate_id=f"E{size}_{sig}"))
        if sig in seen:
            existing = seen[sig]
            if existing["candidate_id"] in old_ids:
                aliases.append(dict(candidate_id=existing["candidate_id"], account=size,
                    additional_label=label, existing_label=existing["label"],
                    disposition="same canonical original definition; reuse original outcome, never retest"))
            else:
                existing["aliases"].append(label)
            return
        trail = 2000. if size == 50 else 4000.
        row = dict(candidate_id=f"E{size}_{sig}", account=size, family_id=family,
            label=label, book=book, governor=gov, role="candidate", parent_id=None,
            exposure_vector={key: allocation["value"] * 100. / trail for key, allocation in book.items()},
            aliases=[],
            source_rules="Frozen original source signals/exits and strict fill/held-price/target gates; fixed integer quantity requests only; no ATR sizing or governor/target-guard assumption.")
        rows.append(row)
        seen[sig] = row

    pairs = [pair for pair in combinations(original.RISK_KEYS, 2)
             if set(pair) != {"ONB30", "ONBML"}]
    for size in (50, 150):
        for key in original.ALL_KEYS:
            for qty in SINGLE_LEVELS:
                add(size, "fixed_quantity_standalone", f"FIXED_ONLY_{key}_{qty}MICRO",
                    {key: original.lots(qty)})
        for keys in pairs:
            for qty in PAIR_LEVELS:
                add(size, "fixed_quantity_two_leg", f"FIXED_{'+'.join(keys)}_EACH{qty}MICRO",
                    {key: original.lots(qty) for key in keys})

    total = len(old) + len(rows)
    if total + RESERVED_DERIVED > original.MAX_DEFINITIONS:
        raise ValueError(f"Prespecified fixed arm exceeds global cap: {len(old)}original + {len(rows)}new + {RESERVED_DERIVED}reserved > {original.MAX_DEFINITIONS}; stop, do not trim the menu")
    return dict(program="evaluation-audit-20261104", arm="fixed_quantity_admission_amendment",
        scope="Separate pre-outcome admission-based quantity arm; original menu/outcomes remain unchanged. No market inputs or outcomes read.",
        reason="Required source-known ATR/range risk was inadmissible for many risk-sized definitions; inspect source-compatible fixed integer requests without weakening original data gates or changing source rules.",
        original_registry_path="agents/codex/inputs/eval_audit_20261104/policies.json",
        max_economic_definitions=original.MAX_DEFINITIONS,
        original_definitions=len(old), requested_definitions=len(requested),
        new_definitions=len(rows), aliases_to_original_count=len(aliases),
        total_unique_definitions=total, reserved_derived_governors=RESERVED_DERIVED,
        maximum_with_reserved=total + RESERVED_DERIVED,
        standalone_levels=list(SINGLE_LEVELS), two_leg_levels=list(PAIR_LEVELS),
        standalone_keys=list(original.ALL_KEYS), pair_keys=list(original.RISK_KEYS),
        excluded_pair=["ONB30", "ONBML"],
        per_account={str(size):dict(new_definitions=sum(r["account"] == size for r in rows),
            requested_definitions=sum(r["account"] == size for r in requested),
            aliases_to_original=sum(r["account"] == size for r in aliases)) for size in (50,150)},
        per_family={family:dict(new_definitions=sum(r["family_id"] == family for r in rows),
            requested_definitions=sum(r["family_id"] == family for r in requested))
            for family in ("fixed_quantity_standalone", "fixed_quantity_two_leg")},
        candidates=rows, aliases_to_original=aliases, requested_menu=requested,
        selection_data="2018-04-02–2022-12-31 only; amendment committed before this arm's outcomes",
        historical_validation="Previously seen2023+; no fixed-arm validation before committed nominations",
        independent_economic_verification="pending; generator/admission is not economic verification")


def selftest():
    """Synthetic registry/identity invariants only; no source outcomes."""
    empty = generate([])
    assert empty["requested_definitions"] == 476
    assert empty["new_definitions"] == 476 and empty["aliases_to_original_count"] == 0
    assert empty["per_family"]["fixed_quantity_standalone"]["requested_definitions"] == 216
    assert empty["per_family"]["fixed_quantity_two_leg"]["requested_definitions"] == 260
    assert len({r["candidate_id"] for r in empty["candidates"]}) == 476
    first = dict(empty["candidates"][0])
    first["label"] = "SYNTHETIC_ORIGINAL_ALIAS"
    first["aliases"] = ["preserve"]
    before = json.dumps(first, sort_keys=True)
    one = generate([first])
    assert json.dumps(first, sort_keys=True) == before
    assert one["new_definitions"] == 475 and one["aliases_to_original_count"] == 1
    assert one["aliases_to_original"][0]["candidate_id"] == first["candidate_id"]
    for row in empty["candidates"]:
        assert row["governor"] == DEFAULT_GOVERNOR
        assert all(v["kind"] == "lots" and isinstance(v["value"], int) for v in row["book"].values())
        assert not {"ONB30", "ONBML"}.issubset(row["book"])
        assert all(k in original.ALL_KEYS for k in row["book"])
    # Source key order and account identity remain separate, deterministic.
    assert generate([]) == empty
    return {"status": "PASS", "checks": "476 requested, canonical dedupe, original immutability, aliases, integer lots, governor off, pair exclusions, deterministic output; synthetic metadata only"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--original", type=Path, default=BASE / "policies.json")
    parser.add_argument("--output", type=Path, default=BASE / "fixed_policies.json")
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args()
    if args.selftest:
        print(json.dumps(selftest(), indent=2))
        return
    obj = generate(json.loads(args.original.read_text()))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(obj, indent=2, allow_nan=False) + "\n")
    print(json.dumps({k: obj[k] for k in ["original_definitions", "requested_definitions", "new_definitions", "aliases_to_original_count", "total_unique_definitions", "maximum_with_reserved", "per_account", "per_family"]}, indent=2))


if __name__ == "__main__":
    main()
