"""Latest-source routing compatibility checks, only invented in-memory ACCT rows.
Never executes the monitor/watchdog or reads the VPS; PowerShell wildcard is checked as a simple source-pattern case.
"""
from pathlib import Path
import importlib.util,io,json,fnmatch
from unittest.mock import patch
import pandas as pd
ROOT=Path(__file__).resolve().parents[1];SRC=ROOT/'agents/codex/inputs/review_20261101/29416b9'
OUT=ROOT/'analysis/outputs/codex_review_20261101'
def load(n,p):
 s=importlib.util.spec_from_file_location(n,SRC/p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
G=load('latest_guard','analysis/live_guard.py');H=load('latest_health','analysis/vps_health.py')
cfg=json.loads((SRC/'live/expected_setup.json').read_text())
row='ACCT,VB150,MNQ,APEX-681524-04,1,0,150000,0,APEX-681524-04,,,,20261102,0830\n'
with patch.object(G.glob,'glob',return_value=['live/trades/20261102.csv']),patch('builtins.open',side_effect=lambda *a,**k:io.StringIO(row)):
 fixed=G.floors('20261102',cfg)
assert fixed['#4']['floor']==146000 and fixed['#4']['room']==4000 and fixed['#4']['max_stop']==3000
# Typed/query account2, actual route4: don't read account2's equity as account4 equity.
wrong='ACCT,VB150,MNQ,APEX-681524-02,1,0,50000,0,APEX-681524-04,,,,20261102,0830\n'
with patch.object(G.glob,'glob',return_value=['live/trades/20261102.csv']),patch('builtins.open',side_effect=lambda *a,**k:io.StringIO(wrong)):
 no_cross=G.floors('20261102',cfg)
assert '#4' not in no_cross
watch=(SRC/'live/vps/watchdog.ps1').read_text()
assert '$_ -like ("ACCT,*," + $v.id + ",*")' in watch
pat='ACCT,*,'+cfg['accounts']['#4']['id']+',*'
assert fnmatch.fnmatchcase(wrong.strip(),pat)
assert wrong.split(',')[3]!=cfg['accounts']['#4']['id']
cols=['event','tag','symbol','side','contracts','entry_date','entry_time','entry_price','exit_date','exit_time','exit_price','profit_usd','bar_date','bar_time']
assert len(row.strip().split(','))==14
base=row.strip().split(',');bad=base.copy();bad[8]='APEX-681524-02';legacy=base.copy();legacy[8]=''
health={}
with patch('glob.glob',return_value=[]):
 for name,fields in [('right_route',base),('wrong_route',bad),('legacy_blank_route',legacy)]:
  df=pd.DataFrame([fields],columns=cols);health[name]=H.monitor_check(df,pd.Timestamp('2026-11-02').date(),cfg)
assert not any('ROUTING' in s for s in health['right_route'])
assert any('ROUTING' in s for s in health['wrong_route'])
assert not any('ROUTING' in s for s in health['legacy_blank_route'])
r={'Claude_latest_followup':'29416b993a619cf9c3e23fd7d050f59db5d35e4e','missing_max_stop_closed':fixed['#4'],
 'Python_floor_matches_typed_column_only':True,'watchdog_wildcard_matches_wrong_typed_account_via_route':True,
 'watchdog_counterexample_equity_USD':50000,'unjustified_150K_floor_USD':146000,'ACCT_fields':len(base),'health_reader':health,
 'limits':'Python helper and simple wildcard/source checks, not native PowerShell/MC execution or real routing evidence.'}
(OUT/'routing_followup.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
