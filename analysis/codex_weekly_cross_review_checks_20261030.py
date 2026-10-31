"""Offline checks of five weekly findings; no signals/account simulation/live access.

Sources are pinned archived bytes. Market inputs for logic fixtures are synthetic;
the separate ST script reconciles only existing fixed trades and their cash/path marks.
"""
from pathlib import Path
from types import SimpleNamespace
from fnmatch import fnmatchcase
import ast,datetime as dt,hashlib,json,math,os,runpy,sys,tempfile,types
from zoneinfo import ZoneInfo
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
INPUT=ROOT/'agents/codex/inputs/weekly_cross_review_20261030'
SOURCE=INPUT/'source'
OUT=ROOT/'analysis/outputs/codex_weekly_cross_review_20261030'
def load_functions(path,names,env):
    tree=ast.parse((SOURCE/path).read_text())
    body=[x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name in names]
    assert {x.name for x in body}==set(names)
    exec(compile(ast.Module(body=body,type_ignores=[]),path,'exec'),env)
    return env
def main():
    OUT.mkdir(parents=True,exist_ok=True)
    for r in json.loads((INPUT/'source_manifest.json').read_text()):
        assert hashlib.sha256((ROOT/r['local']).read_bytes()).hexdigest()==r['sha256']
    results={}
    ps=(SOURCE/'live/vps/watchdog.ps1').read_bytes();line=ps.splitlines()[84]
    assert b'$Logs\x02*.csv' in line
    sample=r'C:\TradingLogs\20261030.csv'
    bad_pattern=r'C:\TradingLogs'+'\x02*.csv';fixed_pattern=r'C:\TradingLogs\2*.csv'
    assert not fnmatchcase(sample,bad_pattern) and fnmatchcase(sample,fixed_pattern)
    assert b'if ($null -eq $eqNow) { continue }' in ps
    results['floor_path']={'defect_reproduced':True,'source_line':85,'bad_literal_hex':b'$Logs\x02*.csv'.hex(' '),
        'bad_matches_daily_log':False,'corrected_matches_daily_log':True,
        'verification_limit':'Python byte/wildcard/control-flow check; PowerShell and installed VPS not exercised'}
    thin=(SOURCE/'analysis/onb_cushion_test.py').read_text();ramp=(SOURCE/'analysis/ramp_budget_test.py').read_text()
    live=(SOURCE/'apex_strategies/NQ_Overnight_Bias_ADX30.txt').read_text()
    assert 'qo = risk(1100, 0.25)' in thin and '* a["k"]' in thin
    assert '"ONB30": rk(1100, 0.25)' in ramp and 'evaluation(Wc * 2.5, Rc * 2.5' in ramp
    assert 'Qty = Floor(RiskPerTrade / (StopPts * BigPointValue))' in live
    rows=[]
    for name,risk,stop in [('ONB',1100,100),('EOS',500,150)]:
        old=2.5*math.floor(risk/(stop*2));new=math.floor(2.5*risk/(stop*2))
        assert old!=new
        rows.append(dict(case='150K '+name,stop_points=stop,simulated_mnq=old,executable_mnq=new))
    old=math.floor(1100/200)*.5;new=math.floor(550/200);assert old==2.5 and new==2
    rows.append(dict(case='50K ONB, half1100cushion',stop_points=100,simulated_mnq=old,executable_mnq=new))
    results['integer_sizing']={'defect_reproduced':True,'fixtures':rows,'account_outcome_effect':'Not simulated; direction unresolved'}
    env={'np':np,'pd':pd,'TOL':2,'TICK':{'NQ':.25},'PV':{'NQ':20},'_BARS':{}}
    lc=load_functions('analysis/leak_checks.py',['bars','_window','fill_sanity','delay','sharpe','tstat','report'],env)
    idx=pd.date_range('2024-01-02 09:55','2024-01-02 10:10',freq='min')
    lc['_BARS']['NQ']=pd.DataFrame({'open':100.,'high':110.,'low':90.,'close':100.},index=idx)
    f=pd.DataFrame(dict(entry_time=pd.to_datetime(['2024-01-02 10:00']*6),
        exit_time=pd.to_datetime(['2024-01-02 10:05']*4+['2024-01-02 10:00']*2),side=1,
        entry=[100.]*4+[999.]*2,exit=[102.,103.,104.,105.,1000.,1001.]))
    _,direct=lc['fill_sanity'](f,'NQ',5,offsets=(0,));_,old=lc['report']('synthetic same-bar fixture',f,'NQ',5)
    assert len(direct)==12 and np.isclose(direct.ok.mean(),2/3) and old['l1']==1 and old['l1_ok']
    patched=(SOURCE/'analysis/leak_checks.py').read_text().replace('F = F[F.exit_time > F.entry_time]','F = F[F.exit_time >= F.entry_time]')
    tree=ast.parse(patched);body=[x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=='report']
    exec(compile(ast.Module(body=body,type_ignores=[]),'L1_fixture_correction','exec'),lc)
    _,fixed=lc['report']('synthetic same-bar fixture',f,'NQ',5)
    assert np.isclose(fixed['l1'],2/3) and not fixed['l1_ok']
    vt=pd.read_csv(INPUT/'vault_closed_trade_times.csv',parse_dates=['entry_time','exit_time'])
    same=vt[vt.entry_time==vt.exit_time]
    results['g10_same_bar']={'defect_reproduced':True,'fixture_fills':len(direct),
        'direct_valid_fraction':float(direct.ok.mean()),'original_report_valid_fraction':old['l1'],
        'corrected_fixture_valid_fraction':fixed['l1'],'report_closed_rows':len(vt),'excluded_same_bar_rows':len(same),
        'excluded_exit_types':same.exit_signal.value_counts().to_dict(),
        'verification_limit':'Synthetic impossible fills; excluded historical fills have not been judged invalid. Open-sentinel identification needs explicit treatment.'}
    st={'np':np,'POINT_VALUE':20.,'COST':7.25,'SLIP':.25}
    load_functions('analysis/funded_lab.py',['with_slippage'],st);load_functions('analysis/portfolio.py',['paths'],st)
    grid=SimpleNamespace(o=np.array([[100.,100.]]),l=np.array([[99.,80.]]),h=np.array([[101.,101.]]))
    examples=[]
    for kind in ['stop',0,'target',1]:
        t=pd.DataFrame([dict(day=0,j0=0,j1=1,side=1,entry=100.,exit=90. if kind in ['stop',0] else 110.,kind=kind)])
        slipped=st['with_slippage'](t);w,r=st['paths'](grid,slipped)
        examples.append(dict(kind=kind,slips=int(slipped.slips.iloc[0]),worst_per_mnq=float(w[0,1]/10),close_per_mnq=float(r[0,-1]/10)))
    assert examples[0]['worst_per_mnq']<examples[1]['worst_per_mnq'] and examples[0]['close_per_mnq']==examples[1]['close_per_mnq']
    assert np.isclose(examples[3]['close_per_mnq']-examples[2]['close_per_mnq'],.5)
    results['swing_target_kind']={'defect_reproduced':True,'synthetic_fixtures':examples,
        'fixed_ledger_reconciliation':'kind_adapter_audit.json','account_outcome_effect':'Not simulated'}
    # Pinned premarket Python, fake files, inert unrelated helpers; no live path opened.
    stub=types.ModuleType('live_guard');stub.floors=lambda *a:{};stub.chart_versions=lambda *a:[];stub.stale_versions=lambda *a:[]
    previous=sys.modules.get('live_guard');sys.modules['live_guard']=stub
    check=runpy.run_path(str(SOURCE/'analysis/premarket_check.py'),run_name='offline_premarket')['check']
    day=dt.date(2026,10,30);asof=dt.datetime(2026,10,30,8,22,tzinfo=ZoneInfo('America/Chicago'));oldcwd=Path.cwd();cases=[]
    try:
        with tempfile.TemporaryDirectory(prefix='weekly_premarket_') as td:
            root=Path(td);(root/'live/trades').mkdir(parents=True);(root/'live/health').mkdir()
            (root/'live/expected_setup.json').write_text(json.dumps({'accounts':{'#2':{'id':'ACCT2','status':'live','suffix':'-2'}},'charts':{'VB-2':{'qty':8}}}))
            (root/'live/health/20261030.csv').write_text('open,2026-10-30 08:15:00,mc_processes=1\n')
            os.chdir(root)
            for hhmm in [5,815]:
                rows=[['ACCT','VB-2','@MNQ','ACCT2','1','0','50000','0','','','','','20261030',str(hhmm)],
                      ['POS','VB-2','@MNQ','0','0','','','','','','','0','20261030',str(hhmm)],
                      ['SIG','VB-2','@MNQ','test 2026-10-30','0','','','','','','','0','20261030',str(hhmm)]]
                (root/'live/trades/20261030.csv').write_text('\n'.join(','.join(x) for x in rows)+'\n')
                result=check(day);assert result==[]
                capture=asof.replace(hour=hhmm//100,minute=hhmm%100);age=(asof-capture).total_seconds()
                cases.append(dict(capture=hhmm,original_status='ALL GREEN',elapsed_seconds=age,proposed_capture_fresh=age<=900))
            assert not cases[0]['proposed_capture_fresh'] and cases[1]['proposed_capture_fresh']
    finally:
        os.chdir(oldcwd)
        if previous is None:sys.modules.pop('live_guard',None)
        else:sys.modules['live_guard']=previous
    results['premarket_capture_age']={'defect_reproduced':True,'asof':asof.isoformat(),'fixtures':cases,
        'verification_limit':'Fake files and stubbed floor/version helpers; demonstrates stale-record acceptance, not installed runtime behavior'}
    out=dict(reviewed_ref='16145ab15c09fa9489a58ef651f5711c1ef2599f',passed=all(x['defect_reproduced'] for x in results.values()),
        meaning='All five reported defects reproduced; this does not mean the reviewed implementations passed',
        new_strategy_return_trials=0,live_access=False,findings=results)
    (OUT/'checks.json').write_text(json.dumps(out,indent=2)+'\n')
    watched=sorted(p for p in INPUT.rglob('*') if p.is_file())
    watched+=sorted(p for p in OUT.rglob('*') if p.is_file() and p.name!='artifact_manifest.json')
    watched += [Path(__file__),ROOT/'analysis/codex_weekly_st_kind_audit_20261030.py',
        ROOT/'agents/cross_review/2026-10-30_codex.md',ROOT/'agents/cross_review/2026-10-30_codex_response.md',
        ROOT/'agents/codex/proposals/weekly_cross_review_20261030.md']
    manifest={'reviewed_claude_head':out['reviewed_ref'],'independent_assessment_commit':'bb260776d72a3dff6bd569f6bcddf9c458fb6c51',
        'new_strategy_return_trials':0,'live_access':False,
        'files':[{'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in watched if p.exists()]}
    (OUT/'artifact_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps(out,indent=2))
if __name__=='__main__':main()
