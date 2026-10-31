"""No-return archive and latest-plan input verification for uploaded S03v2."""
from pathlib import Path
import hashlib
import json
import subprocess

ROOT=Path(__file__).resolve().parents[1]
PIN="760df42"


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    src=Path("C:/Users/dmoto/Downloads/v2 code.txt")
    dest=ROOT/"agents/codex/inputs/s03_v2/source.txt"
    dest.parent.mkdir(parents=True,exist_ok=True)
    if dest.exists() and dest.read_bytes()!=src.read_bytes():
        raise ValueError("Existing source archive differs")
    dest.write_bytes(src.read_bytes())
    previous=json.loads((ROOT/"analysis/outputs/codex_r2vault/context_inventory.json").read_text())
    ref=subprocess.check_output(["git","rev-parse",PIN],cwd=ROOT).decode().strip()
    checks=[]
    for item in previous["comparisons"]:
        path=item["path"]
        current=subprocess.check_output(["git","rev-parse",ref+":"+path],cwd=ROOT).decode().strip()
        checks.append(dict(path=path,previous=item["current"],current=current,unchanged=current==item["current"]))
    result=dict(source_sha256=sha(dest),source_bytes=dest.stat().st_size,reference=ref,
        baseline_dependencies=checks,changed=[r for r in checks if not r["unchanged"]],
        previous_inventory_sha256=sha(ROOT/"analysis/outputs/codex_r2vault/context_inventory.json"),
        baseline_cache_sha256=sha(ROOT/"agents/codex/runtime/anson_plan.pkl"),
        personal_cache_sha256=sha(ROOT/"agents/codex/runtime/anson_personal_baseline.pkl"),new_returns=False)
    out=ROOT/"analysis/outputs/codex_s03_v2"
    out.mkdir(parents=True,exist_ok=True)
    (out/"context.json").write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(dict(ref=ref,source_hash=result["source_sha256"],checked=len(checks),changed=result["changed"])))


if __name__=="__main__":main()
