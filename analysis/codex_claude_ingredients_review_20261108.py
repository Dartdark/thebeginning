"""Two source-specific synthetic checks; no market strategy return evaluation."""
import ast
import hashlib
import json
from pathlib import Path
import subprocess
from types import SimpleNamespace

import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
PLAN='agents/codex/plans/claude_ingredients_review_20261108.md'
CODE='analysis/codex_claude_ingredients_review_20261108.py'
for p in (PLAN,CODE):
    if subprocess.check_output(['git','show','HEAD:'+p],cwd=ROOT)!=(ROOT/p).read_bytes():
        raise RuntimeError('commit exact plan/code first')
source=ROOT/'agents/codex/inputs/claude_ingredients_review_20261108'
tree=ast.parse((source/'twin_continuation_bench.py').read_text())
fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='grids')
namespace={'np':np,'tc':SimpleNamespace(PV=20.)}
exec(compile(ast.Module(body=[fn],type_ignores=[]),'<retained literal grids>','exec'),namespace)
g=SimpleNamespace(o=np.zeros((1,3)))
B={'row':np.array([0,0,0]),'j':np.array([0,1,2]),'l':np.array([99.,100.,109.]),'h':np.array([101.,111.,111.])}
T=pd.DataFrame([{'i0':0,'i1':2,'exit':110.,'entry':100.,'side':1,'net':470.,'kind':0}])
W,R=namespace['grids'](g,B,T)
correct_cost=(110-100)*50-470
expected_first=(99-100)*50-correct_cost
assert R[0,-1]==470
assert W[0,0]==250 and expected_first==-80

ablation=(source/'ingredient_ablation.py').read_text()
assert 'dict(shorts=False, sl=1e6, rr=1.0)' in ablation
btree=ast.parse((source/'bridge_noise_15m_test.py').read_text())
run=next(n for n in btree.body if isinstance(n,ast.FunctionDef) and n.name=='run')
assign=next(n for n in run.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='tp' for t in n.targets))
expression=ast.unparse(assign.value)
assert expression=='sl * rr'
base_target=50*.5; ablated_target=1e6*1.
assert base_target==25 and ablated_target==1e6
result={'reviewed_claude_ref':(source/'reviewed_ref.txt').read_text().strip(),
        'scope':'literal function synthetic path and static ablation binding audit only',
        'ES_path':{'input_net':470,'copied_function_terminal_realized':float(R[0,-1]),
                   'copied_function_first_adverse_mark':float(W[0,0]),'correct_ES_first_adverse_mark':expected_first,
                   'inherited_multiplier':20,'ES_multiplier':50,'finding':'terminal reconciliation does not validate worst-path units'},
        'ablation':{'target_expression':expression,'base_stop':50,'base_target':base_target,
                    'no_stop_case_stop':1e6,'no_stop_case_target':ablated_target,
                    'finding':'no-stop-labelled case removes target too'},
        'assertions_passed':5,'economic_trials':0,'market_returns_computed':False,
        'hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(source.iterdir())},
        'preregistration_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()}
out=ROOT/'analysis/outputs/codex_claude_ingredients_review_20261108/audit.json'
out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k!='hashes'},indent=2))
