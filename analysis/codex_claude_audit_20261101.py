"""Disconnected implementation audit; no historical strategy returns or live-system calls.
Uses frozen Claude source 3ad0b16, imported with __main__ blocks inactive.
"""
from pathlib import Path
import importlib.util, hashlib, json, os, sys, tempfile, types
from unittest.mock import patch
import datetime as dt
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'agents/codex/inputs/claude_audit_20261101/3ad0b16'
OUT=ROOT/'analysis/outputs/codex_claude_audit_20261101'
sys.path.insert(0,str(ROOT/'analysis'))

def module(name,path):
    spec=importlib.util.spec_from_file_location(name,SRC/path)
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def main():
    results={}
    q7=module('lab_Q007','analysis/lab_Q007.py');sys.modules['lab_Q007']=q7
    q9=module('audit_q9','analysis/lab_Q009.py')
    # Equal information through Wednesday's decision, different future Thursday volume.
    g=types.SimpleNamespace(trading=np.arange(3),ts=pd.to_datetime(['2020-01-08','2020-01-09','2020-01-10']),v=np.ones((3,1440)))
    g.v[:,571]=[4,1,1]
    before=q7.release_rows(g).tolist()
    g.v[1,571]=4
    after=q7.release_rows(g).tolist()
    assert before==[0] and after==[1]
    results['weekly_event_membership_depends_on_future_day']={'same_Wednesday_information':True,'before_rows':before,'after_future_Thursday_volume_change':after}
    # All fields before the 08:00 entry remain identical; changing 09:31 changes membership.
    g.v[:,571]=[1,1,1];a=q7.release_rows(g).tolist();g.v[1,571]=4;b=q7.release_rows(g).tolist()
    assert a==[] and b==[1] and q9.release_rows is q7.release_rows
    results['Q009_after_exit_selection']={'entry_CT':'08:00','exit_CT':'09:29','selector_bar_end_CT':'09:31','before':a,'after':b}
    # Missing scheduled time-exit and missing holding bars are not rejected.
    g=types.SimpleNamespace(ts=pd.to_datetime(['2020-01-09']))
    for k in ['o','h','l','c']:setattr(g,k,np.full((1,1440),np.nan))
    g.c[0,570]=100;g.c[0,575]=101
    g.o[0,577]=100;g.h[0,577]=100.1;g.l[0,577]=100;g.c[0,577]=100.1
    pnl=q7.trades(g,np.array([0]),np.array([1.0]),2)
    assert len(pnl)==1 and np.isnan(g.c[0,630])
    results['missing_time_exit_accepted']={'trade_count':len(pnl),'synthetic_net_USD':round(float(pnl.iloc[0]),6),'last_observed_CT':'09:37','required_exit_CT':'10:30','missing_path_after_last_observation':True}
    lab=module('audit_lab','analysis/lab_tools.py')
    with tempfile.TemporaryDirectory() as d:
        lab.STOP=d+'/STOP';lab.LEDGER=d+'/ledger.json'
        lab.now=lambda:dt.datetime(2026,11,1,12,tzinfo=lab.CT)
        old=[dict(id='old',date='2026-10-02T12:00-05:00',looks=40,verdict='FAIL')]
        Path(lab.LEDGER).write_text(json.dumps(old))
        lab.ideas=lambda:[dict(id='Q999',status='queued',priority=1,order=0,tier_check=True,who_pays='structural')]
        verdict=lab.can_run();assert verdict=='OK' and lab.looks_quarter()==40
        lab.summary=lambda L:None
        fake=types.SimpleNamespace(stamp=lambda:'synthetic provenance')
        with patch.dict(sys.modules,{'provenance':fake}):
            row=dict(id='Q999',title='synthetic',stage=3,verdict='PASS',looks=1,verified=[],not_verified=[],risks=[])
            try:lab.log(row);raise AssertionError('expected post-run rejection')
            except SystemExit as e:rejection=str(e)
            Path(lab.LEDGER).write_text('[]')
            row.update(stage=5,looks=0)
            lab.log(row)
        accepted=json.loads(Path(lab.LEDGER).read_text())
        assert accepted[0]['stage']==5 and accepted[0]['verdict']=='PASS'
        results['budget_check_after_execution']={'looks_spent':40,'can_run':verdict,'log_after_one_more_look':rejection}
        results['receipt_does_not_certify_gates']={'synthetic_stage5_PASS_accepted_without_artifacts':True,'no_preregistration_or_return_files_created':True}
    pp=module('audit_prepush','tools/prepush_check.py')
    pp.git=lambda *args:''
    assert pp.before([])==[] and pp.after([pp.WORK,pp.MIRROR])==[]
    results['failed_git_reads_fail_open']={'simulated_git_stdout':'','before_errors':pp.before([]),'after_errors':pp.after([pp.WORK,pp.MIRROR]),'real_git_or_push_called':False}
    prov=module('audit_provenance','analysis/provenance.py')
    with tempfile.TemporaryDirectory() as d:
        prior=os.getcwd();os.chdir(d)
        try:
            Path('data').mkdir();p=Path('data/NQ_1min_2020.csv')
            p.write_text('Date,Close\n20200101,100\n20200102,101\n');a=prov.market('NQ');ha=hashlib.sha256(p.read_bytes()).hexdigest()
            p.write_text('Date,Close\n20200101,900\n20200102,101\n');b=prov.market('NQ');hb=hashlib.sha256(p.read_bytes()).hexdigest()
        finally:os.chdir(prior)
    assert a==b and ha!=hb
    results['data_stamp_unchanged_after_same_length_edit']={'stamp_before':a,'stamp_after':b,'content_SHA256_changed':ha!=hb}
    bg=module('audit_buy_gate','analysis/buy_gate.py')
    bg.load=lambda name:([{'live_trades':40,'live_pts':1.0,'bt_pts':0.0,'drift':'OK'}] if name=='live_vs_bt.json' else [])
    # Patch only the setup read with invented in-memory content. No live files are opened.
    import io
    with patch('builtins.open',lambda *a,**k:io.StringIO('{"accounts":{}}')):
        try:bg.gate();raise AssertionError('expected undefined-edge formatting error')
        except TypeError as e:msg=str(e)
    results['undefined_edge_crashes_buy_gate']={'live_trades':40,'backtest_denominator':0,'error':msg,'live_input_reads':0}
    OUT.mkdir(parents=True,exist_ok=True)
    manifest={'frozen_Claude_commit':'3ad0b16e7101ace22b870fe32dbf09fd4e2a80ee','kind':'synthetic implementation audit only','new_return_tests':0,'audit_script_SHA256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'python':sys.version,'numpy':np.__version__,'pandas':pd.__version__,'checks':results,'sources':{str(p.relative_to(SRC)):hashlib.sha256(p.read_bytes()).hexdigest() for p in SRC.rglob('*') if p.is_file() and '__pycache__' not in str(p)}}
    (OUT/'verification.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps(results,indent=2))

if __name__=='__main__':main()
