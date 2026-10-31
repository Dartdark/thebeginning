"""Check Claude724d1bb using fake logs; inspect recorded log cadence, no trading/live I/O."""
from pathlib import Path
from zoneinfo import ZoneInfo
import ast,csv,datetime as dt,hashlib,io,json,os,runpy,subprocess,sys,tempfile,types
import numpy as np,pandas as pd
ROOT=Path(__file__).resolve().parents[1]
REF='724d1bb128c47a465d35a3f4467d0f7057a376b0'
INPUT=ROOT/'agents/codex/inputs/weekly_cross_review_20261030/fix_reply_724d1bb'
OUT=ROOT/'analysis/outputs/codex_weekly_fix_reply_20261030'
def src(p):return subprocess.check_output(['git','show',REF+':'+p],cwd=ROOT)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    INPUT.mkdir(parents=True,exist_ok=True);OUT.mkdir(parents=True,exist_ok=True)
    files=['analysis/premarket_check.py','analysis/leak_checks.py'];manifest=[]
    for name in files:
        p=INPUT/name;p.parent.mkdir(parents=True,exist_ok=True);b=src(name)
        if p.exists():assert p.read_bytes()==b
        else:p.write_bytes(b)
        manifest.append(dict(path=str(p.relative_to(ROOT)),sha256=sha(p)))
    stub=types.ModuleType('live_guard');stub.floors=lambda *a:{};stub.chart_versions=lambda *a:[];stub.stale_versions=lambda *a:[]
    previous=sys.modules.get('live_guard');sys.modules['live_guard']=stub
    out=[];cwd=Path.cwd()
    try:
        m=runpy.run_path(str(INPUT/files[0]),run_name='offline_current_reply')
        with tempfile.TemporaryDirectory(prefix='claude_reply_check_')as td:
            p=Path(td);(p/'live/trades').mkdir(parents=True);(p/'live/health').mkdir()
            (p/'live/expected_setup.json').write_text(json.dumps({'accounts':{'#2':{'id':'FAKE2','status':'live','suffix':'-2'}},'charts':{'VB-2':{}}}))
            (p/'live/health/20261030.csv').write_text('open,2026-10-30 08:15:00,mc_processes=1\n');os.chdir(p)
            cases=[('fresh',815,0,815,815),('midnight',5,0,5,5),('effective_feed21min',815,840,815,815),
                   ('stale_POS_SIG',815,0,5,5),('effective_feed50min',815,2580,815,815)]
            for name,acct,age,pos,sig in cases:
                rows=[['ACCT','VB-2','@MNQ','FAKE2','1','0','50000',str(age),'','','','','20261030',str(acct)],
                      ['POS','VB-2','@MNQ','0','0','','','','','','','0','20261030',str(pos)],
                      ['SIG','VB-2','@MNQ','test','0','','','','','','','0','20261030',str(sig)]]
                (p/'live/trades/20261030.csv').write_text('\n'.join(','.join(x)for x in rows)+'\n')
                alerts=m['check'](dt.date(2026,10,30),asof=dt.datetime(2026,10,30,8,22,tzinfo=ZoneInfo('America/Chicago')))
                out.append(dict(case=name,alerts=alerts,all_green=not alerts))
        assert [x['all_green']for x in out]==[True,False,True,False,False]
        dst=dt.datetime(2026,11,2,14,22,tzinfo=dt.timezone.utc).astimezone(m['CT']).isoformat()
        assert dst=='2026-11-02T08:22:00-06:00'
    finally:
        os.chdir(cwd)
        if previous is None:sys.modules.pop('live_guard',None)
        else:sys.modules['live_guard']=previous
    names=['bars','_window','fill_sanity','delay','sharpe','tstat','report']
    env={'np':np,'pd':pd,'TOL':2,'TICK':{'NQ':.25},'PV':{'NQ':20},'_BARS':{}}
    tree=ast.parse((INPUT/files[1]).read_text())
    exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name in names],type_ignores=[]),'latest_L1L2','exec'),env)
    idx=pd.date_range('2024-01-02 09:55','2024-01-02 10:10',freq='min')
    env['_BARS']['NQ']=pd.DataFrame({'open':100.,'high':110.,'low':90.,'close':100.},index=idx)
    f=pd.DataFrame({'entry_time':pd.to_datetime(['2024-01-02 10:00']*2),'exit_time':pd.to_datetime(['2024-01-02 10:00']*2),'side':1,'entry':[999.,999.],'exit':[1000.,1001.]})
    text,res=env['report']('only same-bar',f,'NQ',5)
    assert 'UNAVAILABLE'in text and not res['l2_ok']and not res['l1_ok']
    # Archived repository logs, never an installed directory or VPS connection.
    groups={};log_sources=[]
    for day in ['20261027','20261028','20261029']:
        path='live/trades/'+day+'.csv';b=src(path)
        log_sources.append(dict(path=path,sha256=hashlib.sha256(b).hexdigest()))
        for row in csv.reader(io.StringIO(b.decode())):
            if len(row)!=14 or row[0]not in ('ACCT','POS','SIG'):continue
            try:t=int(float(row[13]));minute=t//100*60+t%100
            except ValueError:continue
            if 480<=minute<=900:groups.setdefault((day,row[0],row[1]),set()).add(minute)
    cadence={}
    for kind in ('ACCT','POS','SIG'):
        diffs=[];count=0
        for (day,k,tag),v in groups.items():
            if k==kind:diffs.extend(np.diff(sorted(v)).tolist());count+=len(v)
        u,c=np.unique(diffs,return_counts=True)
        cadence[kind]=dict(unique_tag_records=count,consecutive_gap_minutes=dict(zip(u.astype(str),c.tolist())))
    result=dict(claude_response_commit=REF,scope='post-read source/fake-log acceptance; no new strategy or account returns',
        premarket_cases=out,Chicago_post_DST=dst,all_same_bar_delay_status='UNAVAILABLE; L1 failure retained; no crash',
        limits=dict(ACCT_capture_minutes=45,POS_capture_minutes=45,SIG_capture_minutes=15,effective_feed_minutes=45),
        prior_effective_feed_minutes=15,threshold_change='21minute case now passes by changed45minute policy, not under former15minute policy',
        archived_RTH_log_cadence=cadence,log_sources=log_sources,source_files=manifest,
        installed_system_accessed=False,account_replay_run=False,new_economic_trials=0)
    (OUT/'checks.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    (OUT/'manifest.json').write_text(json.dumps(dict(ref=REF,script_sha256=sha(__file__),checks_sha256=sha(OUT/'checks.json'),source_files=manifest),indent=2)+'\n')
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()
