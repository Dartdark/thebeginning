"""Retain source identity only; no trading signals, external data or returns."""
from pathlib import Path
import hashlib,json,subprocess
root=Path(__file__).resolve().parents[1]
inputs=root/'agents/codex/inputs/dogs_dow_2697334_20261031'
out=root/'analysis/outputs/codex_dogs_dow_2697334_20261031'
out.mkdir(parents=True,exist_ok=True)
record=dict(source='SSRN2697334, Ghouse and Ahmad, conceptual Dogs of the Dow review',
 input_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs.iterdir() if p.is_file()},
 pdfinfo=subprocess.check_output(['pdfinfo',str(inputs/'paper.pdf')],text=True),
 source_rule=dict(selected_stocks=10,rebalance='annual'),original_empirical_test=False,economic_trials=0,
 evidence_gate='DONT_TEST from this source alone',returns_computed=False)
(out/'source_receipt.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps(record,indent=2))
