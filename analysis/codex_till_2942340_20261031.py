"""Source identity and owned-data filename census only; no signals or returns."""
from pathlib import Path
import hashlib,json,subprocess
ROOT=Path(__file__).resolve().parents[1]
folder=ROOT/'agents/codex/inputs/till_2942340_20261031'
data=Path('/workspace/thebeginning/data')
result=dict(source='SSRN2942340, Till and Eagleeye, January17 2017',
    input_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in folder.iterdir() if p.is_file()},
    pdfinfo=subprocess.check_output(['pdfinfo',str(folder/'paper.pdf')],text=True),
    owned_filename_census=[p.name for p in sorted(data.glob('*')) if p.is_file() and any(x in p.name.upper() for x in ['NG','ZC','ZW','CL','WHEAT'])],
    scope='Filename metadata, not certified maturity/price/clock coverage; existing paired-data gates remain unresolved',
    economic_trials=0,returns_computed=False)
out=ROOT/'analysis/outputs/codex_till_2942340_20261031/source_receipt.json'
out.parent.mkdir(parents=True,exist_ok=True)
out.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
