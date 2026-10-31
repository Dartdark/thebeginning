"""Post-review, disconnected checks of Claude's corrections; no return tests/live I/O."""
from pathlib import Path
from types import SimpleNamespace
from zoneinfo import ZoneInfo
import ast,datetime as dt,hashlib,json,os,re,runpy,subprocess,sys,tempfile,types
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
REF='302abe292498361820018fadd0716972f3606847'
INPUT=ROOT/'agents/codex/inputs/weekly_cross_review_20261030/fix_followup_302abe2'
OUT=ROOT/'analysis/outputs/codex_weekly_fix_acceptance_20261030'
FILES=['agents/cross_review/2026-10-30_summary.md','analysis/premarket_check.py','analysis/leak_checks.py',
       'analysis/onb_cushion_test.py','analysis/ramp_budget_test.py','analysis/swing_target_bench.py',
       'analysis/outputs/onb_cushion_test_output.txt','analysis/outputs/ramp_budget_test_output.txt','live/vps/watchdog.ps1',
       'apex_strategies/Apex_Chart_Monitor.txt','apex_strategies/Strategy_Heartbeat_Snippet.txt']
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(p,obj):p.write_text(json.dumps(obj,indent=2,allow_nan=False,default=str)+'\n')
def code(path):return (INPUT/path).read_text()
def functions(path,names,env):
    body=[n for n in ast.parse(code(path)).body if isinstance(n,ast.FunctionDef)and n.name in names]
    assert {n.name for n in body}==set(names)
    exec(compile(ast.Module(body=body,type_ignores=[]),path,'exec'),env)
    return env

def main():
    OUT.mkdir(parents=True,exist_ok=True);INPUT.mkdir(parents=True,exist_ok=True)
    sources=[]
    for rel in FILES:
        b=subprocess.check_output(['git','show',REF+':'+rel],cwd=ROOT)
        p=INPUT/rel;p.parent.mkdir(parents=True,exist_ok=True)
        if p.exists():assert p.read_bytes()==b
        else:p.write_bytes(b)
        sources.append(dict(path=str(p.relative_to(ROOT)),sha256=sha(p)))
    dump(INPUT/'manifest.json',dict(reviewed_claude_ref=REF,post_read_followup=True,files=sources))
    seal=json.loads((INPUT.parent/'independent_seal.json').read_text())
    assert sha(ROOT/seal['assessment_path'])==seal['assessment_sha256']
    checks={}
    ps=(INPUT/'live/vps/watchdog.ps1').read_bytes()
    assert b'$Logs\\2*.csv' in ps and b'\x02'not in ps
    checks['watchdog']=dict(literal_fixed=True,PowerShell_or_installed_runtime_test=False)
    monitor=code('apex_strategies/Apex_Chart_Monitor.txt')
    assert 'AgeSec = (ComputerDateTime - DateTime) * 86400' in monitor
    assert 'NumToStr(CurrentTime, 0)' in monitor
    # Evaluate actual corrected sizing expressions on synthetic risk inputs.
    source=ast.parse(code('analysis/onb_cushion_test.py'))
    f=next(x for x in source.body if isinstance(x,ast.FunctionDef)and x.name=='challenge')
    q=next(x for x in ast.walk(f)if isinstance(x,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='ko'for t in x.targets))
    expr=compile(ast.Expression(q.value),'corrected_ONB_quantity','eval')
    quantities=[float(eval(expr,{'np':np,'dollars':risk,'P':{'ONB_STOP':np.array([200.])},'d':0}))for risk in (2750.,550.)]
    assert quantities==[13.,2.]
    ramp=ast.parse(code('analysis/ramp_budget_test.py'))
    qn=next(x for x in ast.walk(ramp)if isinstance(x,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='q'for t in x.targets))
    rk=next(x.value for x in ast.walk(ramp)if isinstance(x,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='rk'for t in x.targets))
    rkfn=eval(compile(ast.Expression(rk),'actual_rk_lambda','eval'),{'np':np,'atr':np.array([100.,150.]),'tr':np.array([0,1])})
    qs=eval(compile(ast.Expression(qn.value),'actual_150K_quantities','eval'),{'rk':rkfn,'REPORTS':{'EOS':('unused',1.)}})
    assert qs['VB']==20 and qs['MON_BR']==5 and qs['EOS'][1,0]==4
    assert all(np.all(np.isfinite(v))and np.all(np.asarray(v)==np.floor(v))for v in qs.values())
    assert 'evaluation(Wc * 2.5' not in code('analysis/ramp_budget_test.py')
    checks['integer_sizing']=dict(actual_ONB_expressions=[dict(risk=2750,stop_points=100,mnq=13),
        dict(risk=550,stop_points=100,mnq=2)],actual_150K_EOS_150point_stop=4,
        final_quantities_integral=True,account_returns_rerun_by_this_audit=False)
    # Corrected ST adapter with four invented rows; no trading signal generation.
    source=ast.parse(code('analysis/swing_target_bench.py'))
    kinds=next(x.value for x in source.body if isinstance(x,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='ST_KIND'for t in x.targets))
    mapping=ast.literal_eval(kinds);assert mapping=={'target':1,'stop':0,'breakeven':0,'time':2}
    dates=pd.to_datetime(['2020-01-02','2020-01-03','2020-01-06','2020-07-03'])
    frame=pd.DataFrame(dict(date=dates,j0=500,j1=850,side=1,entry=100.,exit=101.,reason=['target','stop','time','time'],net=0.,apex_flat_violation=[False,False,False,True]))
    fakepd=SimpleNamespace(read_csv=lambda *a,**kw:frame.copy(),Series=pd.Series,DataFrame=pd.DataFrame,DatetimeIndex=pd.DatetimeIndex)
    env=dict(np=np,pd=fakepd,SP='',ST_KIND=mapping,jof=lambda hhmm:hhmm//100*60+hhmm%100)
    functions('analysis/swing_target_bench.py',['pt_trades'],env)
    c=np.full((4,1440),np.nan);c[:,:700]=100.
    trades=env['pt_trades'](SimpleNamespace(ts=dates.to_numpy(),c=c))
    assert trades.kind.tolist()==[1,0,2,2]and int(trades.j1.iloc[-1])==699
    checks['ST_adapter']=dict(numeric_and_holiday_kinds_pass=True,full_corrected_account_replay='still pending in Claude summary',
        direction_of_payout_change='not established by per-trade accounting improvement')
    # Actual L1/L2 functions; fake bars and planted impossible equal-time fills.
    lc=dict(np=np,pd=pd,TOL=2,TICK={'NQ':.25},PV={'NQ':20},_BARS={})
    functions('analysis/leak_checks.py',['bars','_window','fill_sanity','delay','sharpe','tstat','report'],lc)
    idx=pd.date_range('2024-01-02 09:55','2024-01-02 10:10',freq='min')
    lc['_BARS']['NQ']=pd.DataFrame(dict(open=100.,high=110.,low=90.,close=100.),index=idx)
    f=pd.DataFrame(dict(entry_time=pd.to_datetime(['2024-01-02 10:00']*6),
        exit_time=pd.to_datetime(['2024-01-02 10:05']*4+['2024-01-02 10:00']*2),side=1,
        entry=[100.]*4+[999.]*2,exit=[102.,103.,104.,105.,1000.,1001.]))
    _,res=lc['report']('post-fix same-bar fixture',f,'NQ',5)
    assert np.isclose(res['l1'],2/3)and not res['l1_ok']
    try:
        lc['report']('all same-bar fixture',f.iloc[-2:],'NQ',5)
        empty_delay='handled'
    except (AttributeError,KeyError)as e:empty_delay=type(e).__name__+': '+str(e)
    checks['L1_gate']=dict(planted_same_bar_impossible_fills_now_fail=True,valid_fraction=float(res['l1']),
        all_same_bar_input=empty_delay,whole_plan_sweep='Claude saved3512VBfills checked; not rerun here')
    # Never open real logs. Fake temporary working directory and inert helpers.
    stub=types.ModuleType('live_guard');stub.floors=lambda *a:{};stub.chart_versions=lambda *a:[];stub.stale_versions=lambda *a:[]
    prior=sys.modules.get('live_guard');sys.modules['live_guard']=stub
    cwd=Path.cwd();premarket=[]
    try:
        check=runpy.run_path(str(INPUT/'analysis/premarket_check.py'),run_name='offline_fixed_premarket')['check']
        with tempfile.TemporaryDirectory(prefix='postfix_monitor_')as td:
            p=Path(td);(p/'live/trades').mkdir(parents=True);(p/'live/health').mkdir()
            (p/'live/expected_setup.json').write_text(json.dumps({'accounts':{'#2':{'id':'FAKE2','status':'live','suffix':'-2'}},'charts':{'VB-2':{'qty':8}}}))
            (p/'live/health/20261030.csv').write_text('open,2026-10-30 08:15:00,mc_processes=1\n')
            os.chdir(p)
            cases=[('midnight_stale',5,0,5,5),('fresh_control',815,0,815,815),
                   ('capture22min_old',800,0,800,800),('14min_old_bar_captured7min_ago',815,840,815,815),
                   ('fresh_ACCT_but_stale_POS_SIG',815,0,5,5)]
            for name,acct,age,pos,sig in cases:
                rows=[['ACCT','VB-2','@MNQ','FAKE2','1','0','50000',str(age),'','','','','20261030',str(acct)],
                      ['POS','VB-2','@MNQ','0','0','','','','','','','0','20261030',str(pos)],
                      ['SIG','VB-2','@MNQ','fake','0','','','','','','','0','20261030',str(sig)]]
                (p/'live/trades/20261030.csv').write_text('\n'.join(','.join(x)for x in rows)+'\n')
                alerts=check(dt.date(2026,10,30),asof=822)
                capture_age=502-(acct//100*60+acct%100)
                premarket.append(dict(case=name,ACCT_time=acct,stored_bar_age_seconds=age,POS_time=pos,SIG_time=sig,
                    effective_feed_age_minutes=capture_age+age/60,alerts=alerts,returned_ALL_GREEN=not alerts))
    finally:
        os.chdir(cwd)
        if prior is None:sys.modules.pop('live_guard',None)
        else:sys.modules['live_guard']=prior
    assert not premarket[0]['returned_ALL_GREEN']and premarket[1]['returned_ALL_GREEN']
    assert all(x['returned_ALL_GREEN']for x in premarket[2:])
    utc=dt.datetime(2026,11,2,14,22,tzinfo=dt.timezone.utc)
    tz=dict(utc=utc.isoformat(),actual_CT=utc.astimezone(ZoneInfo('America/Chicago')).strftime('%H:%M'),
            script_fixed_UTC_minus5=(utc-dt.timedelta(hours=5)).strftime('%H:%M'))
    checks['premarket']=dict(original_midnight_case_fixed=True,remaining_false_green_cases=premarket[2:],
        complete_fixtures=premarket,post_DST_clock_example=tz,installed_system_accessed=False)
    # Distinguish total nonpasses (including21-day timeouts) from breaches only.
    text=code('analysis/outputs/onb_cushion_test_output.txt');ratios=[]
    for line in text.splitlines():
        if 'plan (everything always)'in line:
            m=re.search(r'pass\s+([\d.]+)%.*?fail\s+([\d.]+)%\s+unfinished\s+([\d.]+)%',line)
            assert m;pa,fa,tm=map(float,m.groups())
            ratios.append(dict(pass_pct=pa,breach_pct=fa,unfinished_pct=tm,
                breaches_per_pass=fa/pa,all_nonpasses_per_pass=(100-pa)/pa))
    checks['summary_ratio_units']=ratios
    result=dict(reviewed_claude_ref=REF,review_mode='post-read acceptance followup, not blind independent research',
        original_independent_assessment_unchanged=True,new_strategy_return_trials=0,
        account_return_simulations_run=False,VPS_or_broker_access=False,checks=checks)
    dump(OUT/'checks.json',result)
    report=ROOT/'agents/codex/results/weekly_fix_followup_20261030.md'
    dump(OUT/'artifact_manifest.json',dict(reviewed_ref=REF,script_sha256=sha(__file__),
        report_sha256=sha(report) if report.exists() else None,
        files=[dict(path=str(p.relative_to(ROOT)),sha256=sha(p))for p in [OUT/'checks.json',INPUT/'manifest.json']]))
    print(json.dumps(result,indent=2,default=str))
if __name__=='__main__':main()
