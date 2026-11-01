"""Offline review of Claude dff44f1. Never executes PowerShell, live tools or order code.
Default: invented-record/source-control-flow checks. --q003: fixed 2018-22 replication only.
"""
from pathlib import Path
import ast,contextlib,datetime as dt,hashlib,importlib.util,io,json,os,sys,types
from unittest.mock import patch
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'agents/codex/inputs/review_20261101/dff44f1'
OUT=ROOT/'analysis/outputs/codex_review_20261101'
sys.path.insert(0,str(ROOT/'analysis'))

def module(name,path):
 s=importlib.util.spec_from_file_location(name,SRC/path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def checks():
 out={};G=module('review_guard','analysis/live_guard.py');D=module('review_dashboard','analysis/dashboard_data.py')
 cfg=json.loads((SRC/'live/expected_setup.json').read_text())
 row='ACCT,VB150,MNQ,APEX-681524-04,0,0,150000,0,0,0,0,0,0,20261102,0830\n'
 with patch.object(G.glob,'glob',return_value=['live/trades/20261102.csv']),patch('builtins.open',side_effect=lambda *a,**k:io.StringIO(row)):
  try:G.floors('20261102',cfg);raise AssertionError('expected missing max_stop')
  except KeyError as e:out['new_account_floor_crash']={'exception':repr(e),'all_real_logs_unread':True}
 actual={t:D.split(t) for t in ['VB150','ONB150','EOS150','MON_BR150']}
 assert all(a=='#3' for _,a in actual.values())
 assert all('20261102'>D.CLOSED_AFTER[a] for _,a in actual.values())
 out['new_account_tags_rejected']={'tag_mapping':actual,'new_account4_trades_dropped_on_20261102':True}
 G.versions=lambda:{'NQ_Vault_Break':'NQ_Vault_Break 2026-11-01'}
 df=pd.DataFrame([dict(event='SIG',tag='VB150',side='NQ_Vault_Break 2020-01-01')])
 with patch('builtins.open',side_effect=lambda *a,**k:io.StringIO(json.dumps(cfg))): muted=G.chart_versions(df,['VB150'])
 assert muted==[]
 without={**cfg,'pending_install':{}}
 with patch('builtins.open',side_effect=lambda *a,**k:io.StringIO(json.dumps(without))): alarms=G.chart_versions(df,['VB150'])
 assert len(alarms)==1
 out['pending_mute_masks_any_old_version']={'with_pending':muted,'after_removing_pending':alarms}
 # Literal control-flow replay, not a PowerShell runtime/integration test.
 relay=(SRC/'live/vps/claude_alert_relay.ps1').read_text();kill=(SRC/'live/vps/kill.ps1').read_text()
 assert '$remote = [bool](git ls-tree' in relay and 'elseif (-not $remote -and (Test-Path $mark))' in relay
 assert 'Remove-Item $Flag -Force' in kill and 'KILL_REMOTE' not in kill
 def relay_step(remote,flag,mark):
  if remote and not flag:return True,True,'kill'
  if not remote and mark:return False,False,'resume'
  return flag,mark,'none'
 flag,mark,_=relay_step(True,False,False)
 # Manual KILL only rewrites the same flag; it cannot clear the remote ownership marker.
 manual_flag=True
 flag,mark,act=relay_step(False,manual_flag,mark)
 assert not flag and act=='resume'
 out['manual_kill_cleared_by_remote_resume']={'source_control_flow_replay':True,'after_remote_then_manual_then_remote_resume_flag':flag}
 flag,mark,act=relay_step(False,True,True) # empty/error ls-tree output casts to False in the source
 assert not flag
 out['failed_remote_read_can_resume']={'failed_ls_tree_empty_output_cast':False,'source_replay_action':act,'flag_after':flag,'no_native_powershell_run':True}
 status=(SRC/'live/vps/status_push.ps1').read_text()
 assert '$ErrorActionPreference = "SilentlyContinue"' in status and 'Set-Location $Out' in status
 assert 'git push -q -f $url vps-status:vps-status' in status and 'git checkout -q -b vps-status' in status
 # Source path: existing working repo, failed Set-Location, .git found, so no init/checkout; add/amend applies to work repo.
 out['status_failed_directory_change_path']={'conditional_on_failed_SetLocation':True,'original_cwd':'C:\\TradingRepo','git_add_and_amend_target':'inherited working repo','remote_push_refspec':'vps-status:vps-status','native_script_not_executed':True}
 K=module('review_kill','analysis/kill_switch.py');calls=[]
 def failed_run(*a):
  calls.append(a);return types.SimpleNamespace(returncode=128,stdout='claude/test\n' if a[:2]==('git','rev-parse') else '',stderr='synthetic failure')
 K.run=failed_run
 with contextlib.redirect_stdout(io.StringIO()) as cap:K.push('invented test')
 assert len([c for c in calls if c[:2]==('git','push')])==3
 out['remote_command_does_not_fail_on_push_failure']={'push_helper_returned_normally':True,'failed_pushes':3,'actual_git_calls':0}
 B=module('review_buy_gate','analysis/buy_gate.py')
 B.load=lambda n:([{'live_trades':40,'live_pts':1.,'bt_pts':0.,'drift':'OK'}] if n=='live_vs_bt.json' else [])
 with patch('builtins.open',side_effect=lambda *a,**k:io.StringIO('{"accounts":{}}')):
  try:B.gate();raise AssertionError('expected undefined-edge failure')
  except TypeError as e:out['buy_gate_undefined_edge_crash']={'exception':str(e)}
 # Definition of the new account, arithmetic only; no assertions of installed chart settings.
 assert cfg['accounts']['#4']['trail']==4000 and cfg['accounts']['#4']['lock']==150100
 assert cfg['charts']['VB150']['qty']==20 and cfg['charts']['MON_BR150']['qty']==5
 out['account4_rules_arithmetic']={'trail':4000,'lock':150100,'target_source':159000,'VB_stop_USD':20*2*75,'ONB_intended_risk_USD':2750}
 out['not_started_guard']={'20261101_before_20261102_busdays':int(np.busday_count('2026-11-02',np.datetime64('2026-11-01')+1))}
 # Review the six actual order-source files without compiling or running them.
 files=['apex_strategies/NQ_Vault_Break.txt','apex_strategies/NQ_Vault_Break_SP.txt','apex_strategies/NQ_Overnight_Bias.txt','apex_strategies/NQ_Overnight_Bias_ADX30.txt','funded_strategies/NQ_Expiration_Open_Short.txt','apex_strategies/Bridge_Monday_Long_L644NQ.txt']
 order_checks={}
 for f in files:
  s=(SRC/f).read_text();assert 'if GetAppInfo(aiRealTimeCalc) = 1 then KillOn = ELC.PathExists' in s
  assert 'KillOn = false then' in s and 'if KillOn and MarketPosition > 0 then Sell ("KILL LX") next bar at market;' in s
  assert 'if KillOn and MarketPosition < 0 then BuyToCover ("KILL SX") next bar at market;' in s
  order_checks[f]={'real_time_guard':True,'entry_gate_present':True,'both_strategy_position_exit_branches':True,'compiled_or_trade_matched':False}
 out['six_strategy_source_checks']=order_checks
 OUT.mkdir(exist_ok=True,parents=True)
 result={'Claude_commit':'dff44f136141aaf78c99c7042a8aca570bbff29a','mode':'synthetic/source review only','checks':out,'script_SHA256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
 (OUT/'priority1_checks.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))

def q003():
 """Replicate exactly the three already-examined rules; no change, rescue, or holdout opening."""
 OUT.mkdir(exist_ok=True,parents=True)
 # Import exact frozen parsers/metrics, bypass cache, read design-period source files only.
 grid=module('review_grid24','analysis/grid24.py');metric=module('review_metrics','analysis/metrics.py')
 with patch.dict(sys.modules,{'grid24':grid,'metrics':metric}):Q=module('review_Q003','analysis/lab_Q003.py')
 files=sorted(list((ROOT/'data').glob('6E_1min_201[89].csv'))+list((ROOT/'data').glob('6E_1min_202[012].csv')))
 assert len(files)==5
 # Grid24's two reads use this exact frozen file list, all before 2023.
 with patch.object(grid.glob,'glob',return_value=[str(p) for p in files]):g=grid.Grid24('unused',night_pattern='')
 rows=g.trading;idx=pd.DatetimeIndex(g.ts[rows]);assert idx.year.min()==2018 and idx.year.max()==2022
 me=pd.Series(idx,index=idx).groupby(idx.to_period('M')).transform('max').to_numpy()==idx.to_numpy()
 F=np.array([Q.fix_col(t) for t in g.ts[rows]])
 rng=np.random.default_rng(7);rpt={};Ts={};ledgers=[]
 for v in (1,2,3):
  mask=me if v in (1,2) else np.ones(len(rows),bool)
  x=Q.run(g,rows[mask],F[mask],v);Ts[v]=x
  # Independently reconstruct the frozen prices, side and $17.50 bridge for each eligible date.
  independent={}
  for row,fix in zip(rows[mask],F[mask]):
   if v in (1,3):a,b,e,z=g.c[row,fix-30],g.c[row,fix-5],g.o[row,fix-4],g.c[row,fix];side=np.sign(b-a)
   else:a,b,e,z=g.c[row,fix-30],g.c[row,fix],g.o[row,fix+2],g.c[row,fix+30];side=-np.sign(b-a)
   if not np.all(np.isfinite([a,b,e,z])) or side==0:continue
   d=pd.Timestamp(g.ts[row]);gross=float(side*(z-e)*125000);net=gross-17.5;independent[d]=net
   ledgers.append(dict(variant=v,date=str(d.date()),side=int(side),entry=float(e),exit=float(z),gross=gross,commission=5.,slippage=12.5,net=net))
  y=pd.Series(independent).sort_index();assert x.index.equals(y.index) and np.allclose(x.values,y.values,atol=1e-8)
  by=x.groupby(x.index.year).sum();daily=x.reindex(pd.date_range('2018-01-01','2022-12-31',freq='B'),fill_value=0.)
  assert np.isclose(daily.sum(),x.sum());m=metric.perf(daily,x)
  rpt[str(v)]={'trades':len(x),'average':float(x.mean()),'gross_average':float(x.mean()+17.5),'t':float(Q.tstat(x)),'PF':float(Q.pf(x)),'by_year':{str(k):float(vv) for k,vv in by.items()},'stage1':bool(Q.tstat(x)>=2 and Q.pf(x)>=1.15 and len(x)>=(80 if v==3 else 40)),'metrics':{k:float(m[k]) for k in ['sharpe','sortino','profit_factor','calmar','ulcer']}}
 best=max(Ts,key=lambda v:Q.tstat(Ts[v]));x=Ts[best]
 if best in (1,2):
  pool=np.where(~me)[0];P=Q.run(g,rows[pool],F[pool],best).reindex(pd.DatetimeIndex(g.ts[rows[pool]]))
  pm=np.array([P.iloc[rng.choice(len(P),int(me.sum()),replace=False)].mean() for _ in range(500)])
 else:
  hours=[h*60 for h in range(3,15) if h not in (10,11)];pm=np.array([Q.run(g,rows,rng.choice(hours,len(rows)),3).mean() for _ in range(500)])
 result={'kind':'unchanged historical design replication','Claude_commit':'dff44f136141aaf78c99c7042a8aca570bbff29a','new_definitions':0,'prior_variants_retained':[1,2,3],'holdout_return_rows_read':0,'variants':rpt,'best_variant':best,'placebo_draws':500,'placebo_p':float(np.mean(pm>=x.mean())),'stage1_pass':rpt[str(best)]['stage1'],'independent_price_arithmetic_reconciled':True,'run_script_SHA256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'inputs':{str(f.relative_to(ROOT)):hashlib.sha256(f.read_bytes()).hexdigest() for f in files},'source_SHA256':{str(p.relative_to(SRC)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [SRC/'analysis/lab_Q003.py',SRC/'analysis/grid24.py',SRC/'analysis/metrics.py']},'limits':'No original author data, actual fills, account benches or holdout returns; source eligibility/calendar conventions preserved.'}
 pd.DataFrame(ledgers).to_csv(OUT/'Q003_design_trades.csv',index=False)
 (OUT/'Q003_replication.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))

if __name__=='__main__':q003() if '--q003' in sys.argv else checks()
