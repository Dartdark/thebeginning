"""Frozen evaluation baseline: calendar deadline, native costs, adverse DLL bound.

No entry/sizing optimization and no new alpha tests. See committed plan.
"""
import argparse
import ast
import glob
import hashlib
import json
from pathlib import Path
import subprocess
import warnings

import numba
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
INP = ROOT / 'agents/codex/inputs/eval_focus_20261109'
OUT = ROOT / 'analysis/outputs/codex_eval_focus_20261109'
SOURCE = Path('/workspace/thebeginning')
RAW_REF = 'fe35af99aa90d7f31b91f8693859251bb44dd9ab'
SEED = 20261109
NAMES = ['LEGACY_21', 'CALENDAR_30', 'NATIVE_30', 'NATIVE_30_ADVERSE_DLL']


def digest(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def bind(path, names, ns, remove_holiday_import=False):
    tree = ast.parse(path.read_text())
    nodes = [n for n in tree.body if isinstance(n, (ast.FunctionDef, ast.ClassDef)) and n.name in names]
    assert {n.name for n in nodes} == set(names), path
    if remove_holiday_import:
        for n in nodes:
            for child in ast.walk(n):
                if isinstance(child, ast.If):
                    child.body = [v for v in child.body if not (isinstance(v, ast.ImportFrom) and v.module == 'replica')]
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(path), 'exec'), ns)
    return ns


@numba.njit
def evaluate(w, real, dates, stops, starts, initial, target, drawdown, dll, adverse):
    # outcome: 1 pass, -1 floor failure, 0 timeout; adverse-before-target on a minute tie.
    answer = np.zeros((len(starts), 6))
    for ii in range(len(starts)):
        s = starts[ii]
        bal, floor, pauses, done = initial, initial - drawdown, 0, False
        for d in range(s, stops[s]):
            lim = max(floor, bal - dll)
            interrupted = False
            for j in range(w.shape[1]):
                mark = bal + w[d, j]
                if mark <= lim:
                    if lim == floor or (adverse and mark <= floor):
                        answer[ii] = np.array([-1., d-s+1., dates[d]-dates[s]+1., pauses, mark-initial, j])
                        done, interrupted = True, True
                        break
                    bal = mark if adverse else lim
                    pauses += 1
                    interrupted = True
                    break
                if bal + real[d, j] - initial >= target:
                    answer[ii] = np.array([1., d-s+1., dates[d]-dates[s]+1., pauses, bal+real[d,j]-initial, j])
                    done, interrupted = True, True
                    break
            if done:
                break
            if not interrupted:
                bal += real[d, -1]
            floor = max(floor, bal - drawdown)  # no funded PA lock
        if not done:
            answer[ii] = np.array([0., stops[s]-s, 30., pauses, bal-initial, -1.])
    return answer


def fixtures():
    def one(w, r, dates=None, stop=None, adverse=False):
        w, r = np.array(w, float), np.array(r, float)
        ds = np.arange(len(w), dtype=np.int64) if dates is None else np.array(dates, dtype=np.int64)
        stops = np.full(len(w), len(w) if stop is None else stop, dtype=np.int64)
        return evaluate(w, r, ds, stops, np.array([0], dtype=np.int64), 100., 90., 40., 20., adverse)[0]
    # Up $60 raises the floor to $120. Two subsequent DLL-size losses reach that floor;
    # a PA floor locked at $101 would survive the same sequence.
    assert one([[0,60],[-21,-21],[-21,-21]], [[0,60],[-21,-21],[-21,-21]])[0] == -1
    assert one([[0,0],[100,100]], [[0,0],[100,100]], dates=[0,30], stop=1)[0] == 0
    x = one([[-21,-21],[0,0]], [[0,-21],[0,0]])
    assert x[0] == 0 and x[3] == 1 and x[4] == -20
    # After first DLL pause only $20 room remains; an overshoot of $25 reaches the trail on day two.
    assert one([[-21,-21],[-25,-25]], [[0,-21],[0,-25]])[0] == -1
    # One adverse bar can cross both DLL and trail, while a perfect DLL fill would book only $20.
    assert one([[-45,-45]], [[0,-45]], adverse=True)[0] == -1
    assert one([[-45,-45]], [[0,-45]], adverse=False)[0] == 0
    assert one([[-21,-21],[-25,100]], [[0,-21],[100,100]])[0] == -1
    # Floor always wins a target/floor tie, independently of a profitable last mark.
    assert one([[-45,100]], [[100,100]], adverse=True)[0] == -1
    return {'passed': True, 'checks': 8}


def load_inputs():
    warnings.filterwarnings('ignore', category=RuntimeWarning)
    receipt = {'raw_ref': RAW_REF, 'files': {}, 'source_manifest_sha256': digest(INP/'source_manifest.json')}
    for year in range(2017, 2027):
        for prefix in ['NQ_1min_', 'NQ_1min_ON_']:
            name = f'{prefix}{year}.csv'
            p = SOURCE/'data'/name
            raw = p.read_bytes()
            actual = hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
            expected = subprocess.check_output(['git','-C',str(SOURCE),'rev-parse',RAW_REF+':data/'+name], text=True).strip()
            assert actual == expected, f'Raw source changed: {name}'
            clock = pd.read_csv(p, usecols=['date','time'])
            assert not clock.duplicated(['date','time']).any(), name
            receipt['files']['data/'+name] = {'git_blob': actual, 'sha256': hashlib.sha256(raw).hexdigest()}
    ns = bind(INP/'analysis/grid24.py', ['Grid24','jof'], {'np':np,'pd':pd,'glob':glob,'NMIN24':1440})
    g = ns['Grid24'](str(SOURCE/'data/NQ_1min_20*.csv'),str(SOURCE/'data/NQ_1min_ON_20*.csv'))
    jof = ns['jof']
    pp = bind(INP/'analysis/portfolio.py',['load_mc','_bar_minutes','paths'],
              {'np':np,'pd':pd,'COST':7.25,'POINT_VALUE':20.,'j_of':jof})
    bridge_file = SOURCE/'mc_reports/Backtesting Strategy Performance Report _ @NQ - 5 Minutes Bridge Monday Longs.xlsx'
    bb = bind(INP/'analysis/bridge_monday_confirm.py',['load_bridge_mc'],
              {'np':np,'pd':pd,'jof':jof,'F':str(bridge_file),'TICK':.25})
    reports = {
        'VB':'Backtesting Strategy Performance Report VB v1.xlsx',
        'ONB':'Backtesting Strategy Performance Report _ @NQ - 15 Minutes NQ Overnight Bias.xlsx',
        'EOS':'Backtesting Strategy Performance Report EOS v1.xlsx',
    }
    trades = {}
    for key, name in reports.items():
        p = SOURCE/'mc_reports'/name
        receipt['files']['mc_reports/'+name] = {'sha256':digest(p)}
        t = pp['load_mc'](g, str(p))
        t['slips'] = 1+t.kind.ne(1).astype(int)
        t['exit'] -= t.side*t.slips*.25
        trades[key] = t
    receipt['files']['mc_reports/'+bridge_file.name] = {'sha256':digest(bridge_file)}
    trades['MON_BR'] = bb['load_bridge_mc'](g)
    ns_tc = {'np':np,'pd':pd,'PV':20.,'TICK':.25,'COMM':7.25}
    # Import removal is mechanical: the same pinned holiday function is injected into the namespace.
    bind(INP/'analysis/replica.py',['is_early_close'],ns_tc)
    bind(INP/'analysis/twin_continuation_test.py',['flatten','half_day','simulate'],ns_tc,True)
    B = ns_tc['flatten'](g)
    print('Generating frozen Twin cap1 v2.1 baseline',flush=True)
    twin = ns_tc['simulate'](B, max_stop_mult=1.0, v21=True)
    twin = twin[twin.date >= '2018-01-01'].copy()
    rows0, rows1 = B['row'][twin.i0.to_numpy()], B['row'][twin.i1.to_numpy()]
    receipt['twin_cross_date_positions'] = int((rows0 != rows1).sum())
    receipt['twin_cross_session_positions'] = int((B['sess'][twin.i0.to_numpy()]!=B['sess'][twin.i1.to_numpy()]).sum())
    twin['day'] = rows1
    twin['j0'] = [int(B['j'][np.arange(a,b+1)[B['row'][a:b+1]==d][0]]) for a,b,d in zip(twin.i0,twin.i1,rows1)]
    twin['j1'] = B['j'][twin.i1.to_numpy()]
    trades['TWIN'] = twin
    receipt['grid'] = {'first':str(pd.Timestamp(g.ts[0]).date()),'last':str(pd.Timestamp(g.ts[-1]).date()),'trading_rows':len(g.trading)}
    return g, trades, pp, B, receipt


def daily_paths(g, trades, pp, B):
    tr = g.trading
    paths = {}
    stats = []
    for key,t in trades.items():
        if key != 'TWIN':
            w,r = pp['paths'](g,t)
        else:
            w,r = np.zeros_like(g.o),np.zeros_like(g.o)
            for z in t.itertuples():
                cost = (z.exit-z.entry)*z.side*20-z.net
                adverse = (B['l'] if z.side>0 else B['h'])[z.i0:z.i1+1]
                a = (adverse-z.entry)*z.side*20-cost
                a[-1] = z.net if z.kind==0 else min(a[-1],z.net)
                ix=np.arange(z.i0,z.i1+1); m=B['row'][ix]==z.day
                a_exit=a[m].copy(); js=B['j'][ix[m]]
                if (~m).any():a_exit[0]=min(a_exit[0],a[~m].min())
                w[z.day,js] += a_exit
                w[z.day,z.j1+1:] += z.net
                r[z.day,z.j1:] += z.net
        # Additional native fee is charged at the same conservative entry/exit clocks as the parent helper.
        fw,fr = np.zeros_like(g.o),np.zeros_like(g.o)
        missing = 0
        expected = 0.
        for z in t.itertuples():
            fw[z.day,z.j0:] += .525
            fr[z.day,z.j1:] += .525
            missing += int(np.isnan(g.c[z.day,z.j0:z.j1+1]).sum())
            expected += ((z.exit-z.entry)*z.side*20-7.25) if key!='TWIN' else z.net
        assert np.isclose(r[:,-1].sum(),expected,atol=.005), (key,'trade/path net mismatch')
        assert np.allclose(w[:,-1],r[:,-1],atol=1e-7), (key,'unclosed daily position')
        paths[key] = tuple(np.ascontiguousarray(x[tr]) for x in (w/10,r/10,fw,fr))
        stats.append({'piece':key,'trades':len(t),'source_per_nq_total':expected,'native_1mnq_total':expected/10-.525*len(t),
                      'missing_held_closes':missing,'last_trade':str(pd.to_datetime(t.date).max().date())})
    return paths,stats


def bootstrap(d):
    rng = np.random.default_rng(SEED)
    nb = (len(d)+59)//60
    starts = rng.integers(0,len(d),(2000,nb))
    ix = ((starts[:,:,None]+np.arange(60))%len(d)).reshape(2000,-1)[:,:len(d)]
    return np.quantile(d[ix].mean(axis=1),[.05,.95]).tolist()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--fixtures-only',action='store_true')
    args = parser.parse_args()
    check = fixtures()
    print('Account fixtures:',check,flush=True)
    if args.fixtures_only:
        return
    for name in ['agents/codex/plans/eval_focus_baseline_20261109.md','analysis/codex_eval_focus_baseline_20261109.py']:
        subprocess.run(['git','diff','--exit-code','HEAD','--',name],cwd=ROOT,check=True)
        subprocess.run(['git','ls-files','--error-unmatch',name],cwd=ROOT,check=True,stdout=subprocess.DEVNULL)
    OUT.mkdir(parents=True,exist_ok=True)
    g,trades,pp,B,receipt = load_inputs()
    receipt.update(code_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
                   code_sha256=digest(__file__),fixtures=check,dependencies={x.__name__:x.__version__ for x in [np,pd,numba]})
    (OUT/'input_manifest.json').write_text(json.dumps(receipt,indent=2)+'\n')
    paths,stats = daily_paths(g,trades,pp,B)
    pd.DataFrame(stats).to_csv(OUT/'piece_reconciliation.csv',index=False)
    tr=g.trading; dates=pd.DatetimeIndex(g.ts[tr]); days=(dates.values.astype('datetime64[D]').astype(np.int64))
    end30=np.searchsorted(days,days+30)
    end21=np.arange(len(days))+21
    starts=np.where((dates>='2018-01-02')&(dates<='2026-09-01')&(days+30<=days[-1]+1)&(end21<=len(days)))[0].astype(np.int64)
    atr=g.daily_atr(15)[tr]
    risk=lambda usd,m:np.floor(usd/(np.nan_to_num(m*atr,nan=1e12)*2))
    q50={'VB':np.full(len(days),8.),'ONB':risk(1100,.25),'EOS':risk(500,.30),'MON_BR':np.full(len(days),2.)}
    q150={'VB':np.full(len(days),20.),'ONB':risk(2750,.25),'EOS':risk(1250,.30),'MON_BR':np.full(len(days),5.),'TWIN':np.full(len(days),2.)}
    records=[]; summaries=[]; differences=[]
    for account,initial,tgt,dd,dll,q in [('50K',50000.,3000.,2000.,1000.,q50),('150K',150000.,9000.,4000.,2000.,q150)]:
        assert all(np.equal(v,np.floor(v)).all() for v in q.values())
        w=sum(paths[k][0]*v[:,None] for k,v in q.items())
        r=sum(paths[k][1]*v[:,None] for k,v in q.items())
        fw=sum(paths[k][2]*v[:,None] for k,v in q.items())
        fr=sum(paths[k][3]*v[:,None] for k,v in q.items())
        results={}
        for n,name in enumerate(NAMES):
            ans=evaluate(w-fw if n>=2 else w,r-fr if n>=2 else r,days,end21 if n==0 else end30,starts,initial,tgt,dd,dll,n==3)
            results[name]=ans
            for s,z in zip(starts,ans):
                records.append({'account':account,'protocol':name,'start':dates[s],'deadline_exclusive':dates[s]+pd.Timedelta(days=30),
                                'outcome':{1:'pass',-1:'fail',0:'time'}[int(z[0])],'trading_days':int(z[1]),'calendar_days':int(z[2]),
                                'dll_pauses':int(z[3]),'end_profit':z[4],'last_minute':int(z[5])})
            masks={'full':np.ones(len(starts),bool),'design':days[starts]+30<=np.datetime64('2023-01-01','D').astype(np.int64),'recent':dates[starts].year>=2023}
            masks.update({str(y):dates[starts].year==y for y in range(2018,2027)})
            for period,m in masks.items():
                if not m.any():continue
                a=ans[m]; win=a[:,0]==1
                summaries.append({'account':account,'protocol':name,'period':period,'starts':len(a),'pass_rate':win.mean(),
                                  'fail_rate':(a[:,0]==-1).mean(),'timeout_rate':(a[:,0]==0).mean(),
                                  'median_trading_days_if_pass':float(np.median(a[win,1])) if win.any() else None,
                                  'median_calendar_days_if_pass':float(np.median(a[win,2])) if win.any() else None,
                                  'evaluation_fees_per_pass':float(1/win.mean()) if win.any() else None})
                if n:
                    prev=results[NAMES[n-1]][m]
                    diff=(a[:,0]==1).astype(float)-(prev[:,0]==1).astype(float)
                    differences.append({'account':account,'protocol':name,'compared_to':NAMES[n-1],'period':period,'paired_pass_change':diff.mean(),'band90':bootstrap(diff)})
            print(account,name,{k:round(v,4) if isinstance(v,float) else v for k,v in summaries[-len(masks)].items()} if False else
                  'pass %.2f%% fail %.2f%% time %.2f%%'%(100*(ans[:,0]==1).mean(),100*(ans[:,0]==-1).mean(),100*(ans[:,0]==0).mean()),flush=True)
    pd.DataFrame(records).to_csv(OUT/'start_outcomes.csv',index=False)
    pd.DataFrame(summaries).to_csv(OUT/'summary.csv',index=False)
    (OUT/'paired_differences.json').write_text(json.dumps(differences,indent=2)+'\n')
    (OUT/'checks.json').write_text(json.dumps({'fixtures':check,'new_alpha_trials':0,'account_protocols':4,'source_reconciled':True,
            'independent_review':'pending','limitations':['minute-extrema aggregation','Sunday Bridge approximation','DLL execution bound','report history coverage']},indent=2)+'\n')


if __name__=='__main__':
    main()
