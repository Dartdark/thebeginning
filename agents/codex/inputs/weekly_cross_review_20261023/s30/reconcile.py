"""Reproduce existing-ledger reconciliation only; never execute strategy rules."""
import argparse
import csv
from decimal import Decimal
import hashlib
import json
from pathlib import Path

p = Path(__file__).resolve().parent
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--source-root', type=Path, help='Read existing S30 CSVs from this pinned-source checkout; no replay.')
args = parser.parse_args()
provenance = json.loads((p / "provenance.json").read_text())
proof = json.loads((p / "reconciliation_proof.json").read_text())
inputs = {item['name']: (args.source_root / item['path'] if args.source_root else p / item['name'])
          for item in provenance['inputs']}
for item in provenance["inputs"]:
    raw = inputs[item["name"]].read_bytes()
    actual = hashlib.sha1(f"blob {len(raw)}\0".encode() + raw).hexdigest()
    assert actual == item["blob_sha"]
    assert hashlib.sha256(raw).hexdigest() == proof["input_hashes"][item["name"]]["sha256"]
nets = []
for symbol in ("NQ", "ES"):
    with inputs[f"python_trades_{symbol}.csv"].open() as f:
        trades = list(csv.DictReader(f))
    assert len(trades) == proof["trades"][symbol]["n"]
    nets.append(sum((Decimal(t["net"]) for t in trades), Decimal(0)))
with inputs["daily_nq_es_per_micro.csv"].open() as f:
    rows = list(csv.reader(f))[1:]
trade_total = sum(nets) / 10
daily_total = sum((Decimal(r[1]) for r in rows), Decimal(0))
assert trade_total == daily_total == Decimal(proof["combined_trade_net_micro"])
assert rows[-1][0] == proof["same_terminal_date"]
print(f"PASS: corrected net trades = daily MTM = ${daily_total}; difference ${daily_total-trade_total}")
