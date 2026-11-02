"""Follow-up fixtures: actual frozen kill.ps1 only in temporary dirs with -NoAlert.
No live folder, remote relay, broker, chart, notification or return test is executed.
"""
from pathlib import Path
import hashlib,json,os,subprocess,tempfile,sys
ROOT=Path(__file__).resolve().parents[1];SRC=ROOT/'agents/codex/inputs/kill_reply_20261102/2a99380';OUT=ROOT/'analysis/outputs/codex_kill_reply_20261102'
PS=Path('/workspace/review_tools/pwsh/pwsh')
env=dict(os.environ,XDG_CACHE_HOME='/workspace/review_tools/cache',XDG_CONFIG_HOME='/workspace/review_tools/config',XDG_DATA_HOME='/workspace/review_tools/data',POWERSHELL_TELEMETRY_OPTOUT='1')
def main():
 out={}
 def call(d,*args,wrapper=None):
  cmd=[str(PS),'-NoProfile','-File',str(wrapper or SRC/'live/vps/kill.ps1')]
  cmd+=['-Target',str(SRC/'live/vps/kill.ps1'),'-TestDir',str(d)] if wrapper else ['-Dir',str(d),'-NoAlert',*args]
  r=subprocess.run(cmd,capture_output=True,text=True,env=env,timeout=20)
  return dict(code=r.returncode,stdout=r.stdout.strip(),stderr=r.stderr.strip(),flag=(d/'KILL').exists(),local=(d/'KILL_LOCAL').exists(),remote=(d/'KILL_REMOTE').exists())
 with tempfile.TemporaryDirectory(prefix='codex_reply_hand_') as temp:
  d=Path(temp);call(d,'-Remote');(d/'KILL').write_text('');r=call(d,'-Remote','-Resume')
  assert r['code']==0 and r['local'] and r['flag'] and not r['remote'];out['empty_hand_flag_survives_remote_resume']=r
 with tempfile.TemporaryDirectory(prefix='codex_reply_check_') as temp:
  d=Path(temp);call(d);(d/'KILL').unlink();r=call(d,'-Check')
  assert r['code']==0 and r['flag'] and r['local'];out['deleted_flag_restored_on_check']=r
 with tempfile.TemporaryDirectory(prefix='codex_reply_remote_') as temp:
  d=Path(temp);call(d,'-Remote');(d/'KILL').write_text('mine');a=call(d,'-Check');b=call(d,'-Remote','-Resume');c=call(d,'-Resume')
  assert a['flag'] and b['flag'] and b['local'] and not c['flag'];out['hand_check_then_independent_resumes']=[a,b,c]
 with tempfile.TemporaryDirectory(prefix='codex_reply_empty_') as temp:
  d=Path(temp);r=call(d,'-Check');assert r['code']==0 and not r['flag'];out['no_latches_check_stays_off']=r
 with tempfile.TemporaryDirectory(prefix='codex_reply_write_') as temp:
  d=Path(temp);(d/'KILL_LOCAL').write_text('local');(d/'KILL_REMOTE').write_text('remote')
  wrapper=d/'inject.ps1';wrapper.write_text('''param([string]$Target,[string]$TestDir)
function Set-Content {
 param($Path,$Value,$ErrorAction)
 if ($Path -eq "$TestDir\\KILL") { throw "injected effective flag write failure" }
 Microsoft.PowerShell.Management\\Set-Content -Path $Path -Value $Value -ErrorAction Stop
}
& $Target -Dir $TestDir -NoAlert -Remote -Resume
exit $LASTEXITCODE
''')
  r=call(d,wrapper=wrapper);assert r['code']==1 and r['local'] and not r['flag'] and 'KILL SWITCH ERROR' in r['stdout'] and 'Strategies trade again' not in r['stdout'];out['failed_rebuild_now_errors']=r
 # Exact six-source read logic, evaluated as a pure truth table, not the Windows API or MC engine.
 files=list((SRC/'apex_strategies').glob('*.txt'))+list((SRC/'funded_strategies').glob('*.txt'));assert len(files)==6
 for f in files:
  s=f.read_text();assert 'NoEntry = KillOn;' in s and 'GetFileAttributesA("C:\\TradingLogs") = -1 then NoEntry = true;' in s and 'NoEntry = false then' in s
  assert 'GetLastError' not in s and '2026-11-02' in s
 table=[]
 for name,realtime,fileattr,dirattr in [('historical',False,-1,-1),('known_absent',True,-1,16),('present',True,128,16),('folder_failure',True,-1,-1),('file_specific_error_parent_ok',True,-1,16)]:
  kill=realtime and fileattr!=-1;noentry=kill or (realtime and dirattr==-1)
  table.append(dict(case=name,kill=kill,no_entry=noentry,forced_exit=kill))
 assert table[-1]['no_entry'] is False and table[-2]['no_entry'] is True
 out['six_signal_truth_table']=table
 relay=(SRC/'live/vps/claude_alert_relay.ps1').read_text();assert relay.index(' -Remote -Resume')<relay.index(' -Check')
 out['relay_maintenance_order']={'remote_mutation_before_Check':True,'separate_child_processes':True,'no_relay_executed':True}
 out['runtime']={'PowerShell':subprocess.check_output([str(PS),'-NoProfile','-Command','$PSVersionTable.PSVersion.ToString()'],text=True,env=env).strip(),'platform':sys.platform,'native_Windows_or_MC':False}
 result={'Claude_head':'2a9938052011c2d33d5e4682f8bbdd72d46f5835','checks':out,'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'sources':{str(p.relative_to(SRC)):hashlib.sha256(p.read_bytes()).hexdigest() for p in SRC.rglob('*') if p.is_file()}}
 OUT.mkdir(parents=True,exist_ok=True);(OUT/'checks.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(out,indent=2))
if __name__=='__main__':main()
