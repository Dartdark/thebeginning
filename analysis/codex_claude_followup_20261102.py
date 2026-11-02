"""Read-only source audit plus isolated Python/PowerShell checks; no live/VPS/GitHub actions.
PowerShell script is run ONLY with -Dir=<temporary folder> -NoAlert; never C:\\TradingLogs.
"""
from pathlib import Path
import contextlib,hashlib,importlib.util,io,json,os,subprocess,sys,tempfile,types
from unittest.mock import patch
import pandas as pd
ROOT=Path(__file__).resolve().parents[1];SRC=ROOT/'agents/codex/inputs/claude_followup_20261102/cf4cc1e'
OUT=ROOT/'analysis/outputs/codex_claude_followup_20261102'
PS=Path('/workspace/review_tools/pwsh/pwsh')
def load(name,p):
 s=importlib.util.spec_from_file_location(name,SRC/p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def main():
 out={};D=load('latest_dashboard','analysis/dashboard_data.py')
 dates=['20261030','20261031','20261101','20261102','20261103'];tags=['VB150','ONB150','EOS150','MON_BR150']
 maps={tag:{d:D.split(tag,d)[1] for d in dates} for tag in tags}
 assert all(v['20261030']=='#3' and v['20261102']=='#4' for v in maps.values())
 out['date_effective_tags']=maps
 B=load('latest_buy','analysis/buy_gate.py');B.load=lambda name:([dict(live_trades=40,live_pts=1.,bt_pts=0.,drift='OK')] if name=='live_vs_bt.json' else [])
 with patch('builtins.open',side_effect=lambda *a,**k:io.StringIO('{"accounts":{}}')):r=B.gate()
 assert r[0]=='PLAN ONLY' and r[3] is None;out['unknown_edge_no_longer_crashes']=r
 G=load('latest_guard','analysis/live_guard.py');cfg=json.loads((SRC/'live/expected_setup.json').read_text())
 assert not cfg.get('pending_install')
 G.versions=lambda:{'NQ_Vault_Break':'NQ_Vault_Break 2026-11-01'}
 df=pd.DataFrame([dict(event='SIG',tag='VB150',side='NQ_Vault_Break 2020-01-01')])
 with patch('builtins.open',side_effect=lambda *a,**k:io.StringIO(json.dumps(cfg))):v=G.chart_versions(df,['VB150'])
 assert len(v)==1;out['version_mute_removed']=v
 K=load('latest_kill','analysis/kill_switch.py')
 K.run=lambda *a:types.SimpleNamespace(returncode=128,stdout='',stderr='invented failure')
 with contextlib.redirect_stdout(io.StringIO()):ok=K.push('invented test')
 assert ok is False;out['failed_commit_not_reported_pushed']=ok
 wd=(SRC/'live/vps/watchdog.ps1').read_text();assert '$c[3] -eq $v.id' in wd
 st=(SRC/'live/vps/status_push.ps1').read_text()
 assert 'Set-Location $Out' not in st and 'git -C $Out -c user.name=' in st and 'rev-parse --show-toplevel' in st
 out['source_boundary_fixes']={'watchdog_balance_exact_column':True,'status_git_explicit_worktree':True,'status_branch_identity_check':True}
 # Win32 error mapping: GetFileAttributesA's -1 means failure, not necessarily verified file absence.
 files=list((SRC/'apex_strategies').glob('*.txt'))+list((SRC/'funded_strategies').glob('*.txt'))
 assert len(files)==6
 for p in files:assert 'KillOn = GetFileAttributesA("C:\\TradingLogs\\KILL") <> -1;' in p.read_text()
 out['win32_error_mapping']={'all_six_same_rule':True,'missing_file_return':-1,'other_failure_return':-1,'source_KillOn_on_either':False,'native_Windows_API_called':False}
 assert PS.exists()
 env=dict(os.environ,XDG_CACHE_HOME='/workspace/review_tools/cache',XDG_CONFIG_HOME='/workspace/review_tools/config',XDG_DATA_HOME='/workspace/review_tools/data',POWERSHELL_TELEMETRY_OPTOUT='1')
 def call(folder,*args,wrapper=None):
  cmd=[str(PS),'-NoProfile','-File',str(wrapper or SRC/'live/vps/kill.ps1')]
  if wrapper:cmd+=['-Target',str(SRC/'live/vps/kill.ps1'),'-TestDir',str(folder)]
  else:cmd+=['-Dir',str(folder),'-NoAlert',*args]
  r=subprocess.run(cmd,capture_output=True,text=True,env=env,timeout=15)
  return {'code':r.returncode,'stdout':r.stdout.strip(),'stderr':r.stderr.strip(),'flag':(folder/'KILL').exists(),'local':(folder/'KILL_LOCAL').exists(),'remote':(folder/'KILL_REMOTE').exists()}
 with tempfile.TemporaryDirectory(prefix='codex_kill_scratch_') as temp:
  d=Path(temp);rows=[]
  rows.append(call(d,'-Remote'));rows.append(call(d));rows.append(call(d,'-Remote','-Resume'))
  assert rows[-1]['flag'] and rows[-1]['local'] and not rows[-1]['remote']
  rows.append(call(d,'-Resume'));assert not rows[-1]['flag']
  out['actual_powershell_latch_sequence']=rows
 with tempfile.TemporaryDirectory(prefix='codex_manual_flag_') as temp:
  d=Path(temp);a=call(d,'-Remote');(d/'KILL').write_text('documented by-hand local kill')
  b=call(d,'-Remote','-Resume');assert not b['flag']
  out['documented_by_hand_kill_can_be_cleared']={'remote_kill':a,'after_manual_KILL_file_then_remote_resume':b}
 with tempfile.TemporaryDirectory(prefix='codex_flag_failure_') as temp:
  d=Path(temp);(d/'KILL_LOCAL').write_text('local hold');(d/'KILL_REMOTE').write_text('remote hold')
  wrapper=d/'inject.ps1'
  wrapper.write_text('''param([string]$Target,[string]$TestDir)
function Set-Content {
 param($Path,$Value)
 if ($Path -eq "$TestDir\\KILL") { Write-Error "injected effective flag write failure"; return }
 Microsoft.PowerShell.Management\\Set-Content -Path $Path -Value $Value
}
& $Target -Dir $TestDir -NoAlert -Remote -Resume
exit $LASTEXITCODE
''')
  r=call(d,wrapper=wrapper);assert r['local'] and not r['flag'] and r['code']==0 and 'no kill latch left' in r['stdout']
  out['resume_effective_flag_verification_gap']=r
 # Source relay guard cases: no actual remote repository reads or latches.
 relay=(SRC/'live/vps/claude_alert_relay.ps1').read_text()
 assert '$fetchOk -and $treeOk -and -not $remoteKill' in relay
 out['unknown_remote_read_resume_guard']={'requires_successful_fetch_and_tree_read':True,'native_relay_not_executed':True}
 OUT.mkdir(parents=True,exist_ok=True)
 out['runtime']={'PowerShell':subprocess.check_output([str(PS),'-NoProfile','-Command','$PSVersionTable.PSVersion.ToString()'],env=env,text=True).strip(),'platform':sys.platform,'Windows_native_acceptance':False,'live_folders_touched':False,'alerts_sent':False}
 m={'Claude_head':'cf4cc1ef0105b30b936ff954a8d0d63e9cf2f202','checks':out,'script_SHA256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'source_SHA256':{str(p.relative_to(SRC)):hashlib.sha256(p.read_bytes()).hexdigest() for p in SRC.rglob('*') if p.is_file() and '__pycache__' not in str(p)}}
 (OUT/'checks.json').write_text(json.dumps(m,indent=2)+'\n');print(json.dumps(out,indent=2))
if __name__=='__main__':main()
