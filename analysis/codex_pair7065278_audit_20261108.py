"""Frozen source/formula/synthetic audit; never evaluate historical strategy returns."""
from pathlib import Path
import ast,hashlib,json,os,subprocess,tempfile,sys
from datetime import datetime,time,timezone
from zoneinfo import ZoneInfo
import numpy as np
import pandas as pd
import openpyxl
ROOT=Path(__file__).resolve().parents[1]
IN=ROOT/'agents/codex/inputs/pair7065278_20261108'
SRC=IN/'source'
OUT=ROOT/'analysis/outputs/codex_pair7065278_audit_20261108'
PLAN='agents/codex/plans/pair7065278_audit_20261108.md'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def run():
 for path in [PLAN,Path(__file__).relative_to(ROOT).as_posix()]:
  subprocess.run(['git','cat-file','-e','HEAD:'+path],cwd=ROOT,check=True)
  subprocess.run(['git','diff','--exit-code','HEAD','--',path],cwd=ROOT,check=True)
 for r in json.loads((SRC/'manifest.json').read_text()):assert sha(SRC/r['path'])==r['sha256']
 p=SRC/'code/pairtrading_final.py';source=p.read_text()
 wb=openpyxl.load_workbook(SRC/'output/PairTrade_Final_Metrics_20260706_1147.xlsx',data_only=False)
 cache=openpyxl.load_workbook(SRC/'output/PairTrade_Final_Metrics_20260706_1147.xlsx',data_only=True)
 dims={s.title:[s.max_row,s.max_column] for s in wb}
 checks=[];groups={}
 def check(name,value):
  checks.append(dict(name=name,passed=bool(value)))
  if not value:raise AssertionError(name)
 cost=.0015;gross=np.array([-.01,0.,.01]);paper=gross*(1-cost);implemented=gross-cost
 formula=wb['Strategy']['I3'].value
 check('literal additive implementation', '-IF(H3<>H2, Inputs!$B$4, 0)' in formula)
 check('source cost decreases all outcomes',np.all(implemented<gross))
 check('paper equation reduces loss magnitude',paper[0]>gross[0])
 groups['1_cost']=dict(gross=gross.tolist(),paper_net=paper.tolist(),source_net=implemented.tolist(),formula=formula,
  finding='Paper multiplicative equation is wrong; code/workbook additive equation does not share that error')
 tree=ast.parse('\n'.join(x for x in source.splitlines() if not x.startswith('!')))
 node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='load_clean')
 with tempfile.TemporaryDirectory() as folder:
  pd.DataFrame(dict(DATE=[20250115,20250116],TIME=[160000]*2,OPEN=[499.,501.])).to_csv(Path(folder)/'fixture.csv',index=False)
  env=dict(pd=pd,np=np,os=os,folder_path=folder)
  exec(compile(ast.Module(body=[node],type_ignores=[]),'source_load_clean_only','exec'),env)
  parsed=env['load_clean']('fixture','LQQ3').LQQ3.to_list()
 check('literal source parser counterexample reproduced',parsed==[49900.,501.])
 groups['2_units']=dict(declared_input_unit='GBX for both rows',input=[499.,501.],source_output=parsed,
  finding='Threshold rule cannot distinguish a real low GBX price from a pound-quoted record')
 clocks=[]
 for d in ['2025-01-15','2025-07-15','2025-03-20']:
  t=datetime.fromisoformat(d+'T16:00:00').replace(tzinfo=timezone.utc)
  ny=t.astimezone(ZoneInfo('America/New_York'));ld=t.astimezone(ZoneInfo('Europe/London'))
  clocks.append(dict(utc=t.isoformat(),new_york=ny.isoformat(),london=ld.isoformat(),
   london_ordinary_continuous_open=time(8)<=ld.time()<time(16,30)))
 check('summer16UTC outside ordinary London continuous',not clocks[1]['london_ordinary_continuous_open'])
 check('NY hour not constant11',datetime.fromisoformat(clocks[0]['new_york']).hour==11 and datetime.fromisoformat(clocks[1]['new_york']).hour==12)
 groups['3_clocks']=dict(assumption='Even granting source claim that raw TIME is UTC; native label timezone remains unverified',examples=clocks)
 full=.02-.01;half=.5*.02-.5*.01
 check('gross allocation scaling',np.isclose(full,2*half))
 groups['4_capital']=dict(source_two_leg_return=full,one_total_gross_return=half,
  interpretation='Source is100%NAV per leg (200%gross). Not necessarily invalid, but collateral/financing/weights need definition')
 alpha=wb['Summary']['B10'].value;last=wb['Strategy'].max_row
 check('source alpha refers to empty Summary terminal cell',f'B{last}/B2' in alpha and wb['Summary'][f'B{last}'].value is None)
 groups['5_alpha']=dict(formula=alpha,summary_actual_rows=dims['Summary'][0],referenced_terminal_row=last,
  finding='Unqualified references resolve to Summary; B2 is strategy total return, not benchmark starting price')
 examples=[]
 for prior,z in [(1,.8),(-1,-.8)]:
  paper_next=0 if abs(z)<.25 else prior
  code_next=0 if ((prior==1 and z>-.25)or(prior==-1 and z<.25)) else prior
  examples.append(dict(prior=prior,z=z,paper_next=paper_next,source_code_next=code_next))
 check('exit overshoot parity differs',all(x['paper_next']!=x['source_code_next'] for x in examples))
 groups['6_exit']=examples
 check('previous signal applied', '*H2)' in formula)
 check('OPEN and160000 selected',"df['TIME'] == 160000" in source and "[['DATE', 'OPEN']]" in source)
 groups['7_fill']=dict(previous_signal=True,current_open_snapshot=True,
  finding='Holdings lag does not prove an executable decision-to-later-fill timestamp or synchronized raw venues')
 dates=[wb['Strategy'].cell(i,1).value for i in range(2,last+1)]
 cached={f'B{i}':cache['Summary'][f'B{i}'].value for i in [2,3,4,5,6,8,9,10]}
 check('source workbook405rows',len(dates)==405)
 check('source caches not evaluated results',all(x==0 for x in cached.values()))
 groups['8_workbook']=dict(dimensions=dims,first=dates[0],last=dates[-1],rows=len(dates),duplicate_dates=len(dates)-len(set(dates)),
  cached_summary=cached,finding='Cached zeros are unevaluated formula defaults, not a backtest result; original raw LQQ3/FX not present')
 ann=(1+1.3634)**(252/405)-1;sr=(ann-.04)/.1037
 check('claimed annualization consistent',abs(ann-.7077)<.0001)
 check('claimed CAGR Sharpe arithmetic consistent',abs(sr-6.44)<.01)
 groups['9_claims']=dict(author_total_return=1.3634,observations=405,derived_annualization=ann,source_cagr_sharpe=sr,
  author_sharpe=6.44,author_dd=-.0221,finding='Source uses CAGR excess divided by annualized volatility, not standard daily excess-mean Sharpe; no significance conclusion')
 failures=['same-unit price corruption','invalid alpha benchmark cell references','paper/code cost and exit disagreement',
  'unverified native clock/units/quotes/FX/borrow/cash and later fills','no2018-22design history']
 result=dict(scope='Synthetic mechanics/formula/input audit only; no historical return evaluation',groups=groups,
  engineering_assertions=len(checks),checks=checks,engineering_checks_passed=all(x['passed'] for x in checks),
  source_admission_passed=False,source_admission_failures=failures,economic_trials=0,historical_returns_computed=False,
  portfolio_tests_run=False,code_sha256=sha(__file__),plan_sha256=sha(ROOT/PLAN),
  plan_commit=subprocess.check_output(['git','log','-1','--format=%H','--',PLAN],cwd=ROOT,text=True).strip(),
  inputs={str(p.relative_to(IN)):sha(p) for p in IN.rglob('*') if p.is_file()},python=sys.version,
  versions=dict(numpy=np.__version__,pandas=pd.__version__,openpyxl=openpyxl.__version__))
 OUT.mkdir(parents=True,exist_ok=True);(OUT/'audit.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps(result,indent=2))
if __name__=='__main__':run()
