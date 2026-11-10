"""One frozen loss-side partial-exit screen; see committed plan. No live interfaces."""
from pathlib import Path
import argparse
import hashlib
import json
import os
import subprocess

import numba
import numpy as np
import pandas as pd

import codex_eval_focus_baseline_20261109 as F
import codex_vb_recent_risk as V
from grid import _walk
from portfolio import paths
import dual_thrust_bench as DTB
import metrics as M

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'analysis/outputs/codex_vb_loss_split_20261110'
PLAN = 'agents/codex/plans/vb_loss_split_20261110.md'
MODELS = ['BASE', 'SPLIT', 'REDUCED', 'EMPTY']
SEED = 20261110


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def dump(name, value):
    (OUT/name).write_text(json.dumps(value, indent=2, default=str)+'\n')


def frozen_raw_root():
    """Materialize exact preregistered Git bytes; never rewrite shared raw data."""
    destination = Path('/workspace/vb_loss_split_source')
    (destination/'data').mkdir(parents=True,exist_ok=True)
    # The inherited provenance check resolves Git blobs relative to SOURCE.
    # Give the snapshot its own metadata and read-only access to existing objects.
    subprocess.run(['git','init','-q',str(destination)],check=True)
    common=subprocess.check_output(['git','rev-parse','--path-format=absolute','--git-common-dir'],cwd=ROOT,text=True).strip()
    (destination/'.git/objects/info/alternates').write_text(str(Path(common)/'objects')+'\n')
    for year in range(2017,2027):
        for prefix in ['NQ_1min_','NQ_1min_ON_']:
            rel=f'data/{prefix}{year}.csv'
            frozen=subprocess.check_output(['git','show',F.RAW_REF+':'+rel],cwd=ROOT)
            p=destination/rel
            if not p.exists() or p.read_bytes()!=frozen:
                p.write_bytes(frozen)
    if not (destination/'mc_reports').exists():
        (destination/'mc_reports').symlink_to(ROOT/'mc_reports',target_is_directory=True)
    return destination


@numba.njit
def evaluate(w, r, dates, ends, starts, adverse):
    answer = np.zeros((len(starts), 5))
    for ii in range(len(starts)):
        s = starts[ii]
        bal, floor, pauses, done = 150000., 146000., 0, False
        for d in range(s, ends[s]):
            finish = int(bal >= 156000.)
            lim = max(floor, bal-2000.)
            interrupted = False
            for j in range(w.shape[2]):
                mark = bal+w[finish,d,j]
                if mark <= lim:
                    if lim == floor or (adverse and mark <= floor):
                        answer[ii] = np.array([-1.,d-s+1.,dates[d]-dates[s]+1.,pauses,mark-150000.])
                        done, interrupted = True, True
                        break
                    bal = mark if adverse else lim
                    pauses += 1
                    interrupted = True
                    break
                if bal+r[finish,d,j] >= 159000.:
                    answer[ii] = np.array([1.,d-s+1.,dates[d]-dates[s]+1.,pauses,bal+r[finish,d,j]-150000.])
                    done, interrupted = True, True
                    break
            if done:
                break
            if not interrupted:
                bal += r[finish,d,-1]
            floor = max(floor, bal-4000.)
        if not done:
            answer[ii] = np.array([0.,ends[s]-s,30.,pauses,bal-150000.])
    return answer


def fixtures():
    # Native OHLC mechanics: target, partial-loss/recovery, full loss, gap through both stops.
    def walk(o,h,l,c,stop):
        return _walk(np.array(o,float),np.array(h,float),np.array(l,float),np.array(c,float),
                     0,len(o)-1,1,100.-stop,140.,1.)
    a = walk([100],[142],[90],[140],37.5)
    assert a[1:3] == (140.,1)
    f = walk([100,100],[105,142],[60,95],[100,140],75.)
    p = walk([100,100],[105,142],[60,95],[100,140],37.5)
    assert f[1:3] == (140.,1) and p[1:3] == (62.5,0)
    f = walk([100],[105],[20],[30],75.)
    p = walk([100],[105],[20],[30],37.5)
    assert f[1] == 25. and p[1] == 62.5
    f = walk([100,10],[105,15],[90,0],[95,5],75.)
    p = walk([100,10],[105,15],[90,0],[95,5],37.5)
    assert f[1] == p[1] == 10.
    # Same nearest-extreme order: high-first target wins, low-first partial stop wins.
    assert walk([138],[142],[60],[100],37.5)[2] == 1
    assert walk([65],[142],[60],[100],37.5)[2] == 0
    assert 7*37.5*2+8*75*2 == 1725.
    assert int(np.floor(15*.5+.5)) == 8
    assert int(np.floor(.75*8)) == 6
    F.fixtures()
    # Use same account constants but controlled paths: raised EOD floor and adverse DLL overshoot.
    def account(w0,r0,adverse):
        w = np.array([w0,w0],float)
        r = np.array([r0,r0],float)
        return evaluate(w,r,np.arange(len(w0),dtype=np.int64),
                        np.full(len(w0),len(w0),dtype=np.int64),np.array([0],dtype=np.int64),adverse)[0]
    assert account([[0,6000],[-2001,-2001],[-2001,-2001]],
                   [[0,6000],[0,-2001],[0,-2001]],False)[0] == -1
    assert account([[-4500,-4500]],[[0,-4500]],True)[0] == -1
    assert account([[-4500,-4500]],[[0,-4500]],False)[0] == 0
    return {'split_mechanics_checks':9,'new_account_checks':3,'inherited_account_checks':8,'passed':True}


def vb_paths(g, raw):
    # Keep true raw bracket anchoring; charge entry and exit slippage on their own legs.
    t = raw.copy()
    t['entry'] += .25
    t['exit'] -= .25*t.kind.ne(1)
    w,r = paths(g,t)
    fw,fr = np.zeros_like(g.o),np.zeros_like(g.o)
    for z in t.itertuples():
        fw[z.day,z.j0:] += .525
        fr[z.day,z.j1:] += .525
    w,r = w/10-fw,r/10-fr
    t['native_gross'] = (raw.exit-raw.entry)*2
    t['commission'] = 1.25
    t['slippage'] = .5*(1+raw.kind.ne(1).astype(int))
    t['native_net'] = t.native_gross-t.commission-t.slippage
    expected = t.groupby('day').native_net.sum().reindex(np.arange(g.D),fill_value=0).to_numpy()
    assert np.allclose(r[:,-1],expected)
    assert np.allclose(w[:,-1],r[:,-1])
    return (np.ascontiguousarray(w[g.trading]),np.ascontiguousarray(r[g.trading])),t


def paired_band(delta):
    rng = np.random.default_rng(SEED)
    nb = (len(delta)+59)//60
    starts = rng.integers(0,len(delta),(2000,nb))
    ix = ((starts[:,:,None]+np.arange(60))%len(delta)).reshape(2000,-1)[:,:len(delta)]
    return np.quantile(delta[ix].mean(axis=1),[.05,.95]).tolist()


def summarize(z):
    passed = z[:,0] == 1
    p = float(passed.mean())
    return dict(starts=len(z),passed=p,failed=float((z[:,0]==-1).mean()),expired=float((z[:,0]==0).mean()),
                fee_per_pass_index=1/p if p else None,
                median_pass_trading=float(np.median(z[passed,1])) if passed.any() else None,
                median_pass_calendar=float(np.median(z[passed,2])) if passed.any() else None)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--fixtures-only',action='store_true')
    args = parser.parse_args()
    check = fixtures()
    print('Disconnected checks:',check,flush=True)
    if args.fixtures_only:
        return
    for name in [PLAN,str(Path(__file__).relative_to(ROOT))]:
        committed = subprocess.check_output(['git','show','HEAD:'+name],cwd=ROOT)
        assert committed == (ROOT/name).read_bytes(), 'Commit plan and exact code before returns'
    OUT.mkdir(parents=True,exist_ok=True)
    prereg = subprocess.check_output(['git','log','-1','--format=%H','--',PLAN],cwd=ROOT,text=True).strip()
    F.SOURCE = frozen_raw_root()
    g,trades,pp,B,receipt = F.load_inputs()
    try:
        os.chdir(F.SOURCE)
        trades['DT'] = DTB.dt_trades(g)
        trades['DT']['date'] = pd.to_datetime(g.ts[trades['DT'].day.to_numpy(dtype=int)])
    finally:
        os.chdir(ROOT)
    # No new alternative outcome later than design; existing non-VB ledgers are frozen sources.
    trades = {k:t[t.date.lt('2023-01-01')].copy() for k,t in trades.items() if k!='VB'}
    pieces,stats = F.daily_paths(g,trades,pp,B)
    p = {k:(z[0]-z[2],z[1]-z[3]) for k,z in pieces.items()}
    del pieces
    full = V.replay(g,'BASE',lo='2018-01-01',hi='2023-01-01')
    shallow = full.copy()
    for i,z in full.iterrows():
        d,j0,j1 = int(z.day),int(z.j0),int(z.j1)
        e,k,kind,mae = _walk(g.o[d],g.h[d],g.l[d],g.c[d],j0,j1,1,z.entry-37.5,z.entry+40.,1.)
        shallow.loc[i,['j1','exit','kind','pnl','mae']] = [e,k,kind,(k-z.entry)*20,abs(mae-z.entry)*20]
    shallow[['day','j0','j1','kind']] = shallow[['day','j0','j1','kind']].astype(int)
    pfull,tf = vb_paths(g,full)
    pshallow,ts = vb_paths(g,shallow)
    assert (shallow.j1 <= full.j1).all()
    assert np.array_equal(full[['day','j0']].to_numpy(),shallow[['day','j0']].to_numpy())
    tf.to_csv(OUT/'design_full_leg.csv',index=False)
    ts.to_csv(OUT/'design_shallow_leg.csv',index=False)
    dates = pd.DatetimeIndex(g.ts[g.trading])
    ordinal = dates.values.astype('datetime64[D]').astype(np.int64)
    ends = np.searchsorted(ordinal,ordinal+30)
    starts = np.flatnonzero((dates>='2018-01-02')&(ordinal+30<=np.datetime64('2023-01-01','D').astype(int))).astype(np.int64)
    atr = g.daily_atr(15)[g.trading]
    risk = lambda dollars,m:np.floor(dollars/(np.nan_to_num(m*atr,nan=1e12)*2))
    qty = {'ONB':risk(2750,.25),'EOS':risk(1250,.30),
           'MON_BR':np.full(len(dates),5.),'TWIN':np.full(len(dates),2.),'DT':np.full(len(dates),2.)}
    other=[]
    for finish in [False,True]:
        q={k:np.maximum(1,np.floor(v*.5+.5))*(v>0) if finish else v for k,v in qty.items()}
        other.append(tuple(sum(p[k][j]*v[:,None] for k,v in q.items()) for j in range(2)))
    del p
    rows=[]; outcomes={}; records=[]
    for model in MODELS:
        states=[]
        for f,total in [(0,15),(1,8)]:
            q1,q2 = (0,total) if model=='BASE' else (total//2,total-total//2) if model=='SPLIT' else (0,int(.75*total)) if model=='REDUCED' else (0,0)
            states.append(tuple(np.ascontiguousarray(other[f][j]+q1*pshallow[j]+q2*pfull[j]) for j in range(2)))
        w=np.stack([s[0] for s in states]); r=np.stack([s[1] for s in states])
        for adverse in [False,True]:
            name='ADVERSE_DLL' if adverse else 'CLIPPED_DLL'
            z=evaluate(w,r,ordinal,ends,starts,adverse)
            outcomes[(model,name)]=z
            row=dict(model=model,protocol=name,**summarize(z))
            base=outcomes.get(('BASE',name),z)
            delta=(z[:,0]==1).astype(float)-(base[:,0]==1).astype(float)
            row.update(pass_delta=float(delta.mean()),pass_delta_90=paired_band(delta),
                       baseline_fails_to_pass=int(((base[:,0]==-1)&(z[:,0]==1)).sum()),
                       baseline_passes_lost=int(((base[:,0]==1)&(z[:,0]!=1)).sum()))
            rows.append(row)
            for s,zz in zip(starts,z):
                records.append(dict(model=model,protocol=name,start=dates[s],outcome=int(zz[0]),
                                    trading_days=zz[1],calendar_days=zz[2],dll_pauses=zz[3],end_profit=zz[4]))
            print(model,name,json.dumps(row),flush=True)
        del w,r,states
    pd.DataFrame(rows).to_csv(OUT/'design_accounts.csv',index=False)
    pd.DataFrame(records).to_csv(OUT/'design_start_outcomes.csv',index=False)
    # Standalone diagnostics at the normal integer size, not a new selection objective.
    diagnostic=[]
    for model,net in [('BASE',15*tf.native_net),('SPLIT',7*ts.native_net+8*tf.native_net),
                      ('REDUCED',11*tf.native_net),('EMPTY',0*tf.native_net)]:
        for year in ['design']+list(range(2018,2023)):
            mask=np.ones(len(tf),bool) if year=='design' else tf.date.dt.year.eq(year).to_numpy()
            ds=dates[(dates.year>=2018)&(dates.year<=2022)] if year=='design' else dates[dates.year==year]
            x=net[mask]
            daily=pd.Series(x.to_numpy(),index=tf.date[mask]).groupby(level=0).sum().reindex(ds,fill_value=0.)
            daily=pd.concat([pd.Series([0.],index=[ds[0]-pd.Timedelta(days=1)]),daily])
            m=M.perf(daily,x)
            diagnostic.append(dict(model=model,year=year,side='all/long',net=float(x.sum()),
                                   t=float(x.mean()/x.std()*np.sqrt(len(x))) if x.std() else None,**m))
    pd.DataFrame(diagnostic).to_csv(OUT/'design_vb_metrics.csv',index=False)
    altered=shallow.kind.eq(0)
    fate=[]
    delta=7*(ts.native_net-tf.native_net)
    for kind,label in [(0,'original_stop'),(1,'original_target'),(2,'original_time')]:
        ix=altered & full.kind.eq(kind)
        fate.append(dict(original_fate=label,trimmed_trades=int(ix.sum()),
                         delta_normal_15mnq=float(delta[ix].sum())))
    pd.DataFrame(fate).to_csv(OUT/'design_trim_fate.csv',index=False)
    gates=[]
    for protocol in ['CLIPPED_DLL','ADVERSE_DLL']:
        b=next(z for z in rows if z['model']=='BASE' and z['protocol']==protocol)
        s=next(z for z in rows if z['model']=='SPLIT' and z['protocol']==protocol)
        c=next(z for z in rows if z['model']=='REDUCED' and z['protocol']==protocol)
        efficiency=s['pass_delta']>=.02 and s['pass_delta_90'][0]>=0 and s['failed']<=b['failed']
        safety=s['failed']<=b['failed']-.10 and s['pass_delta']>=-.01 and s['pass_delta_90'][0]>=-.02
        timing=s['median_pass_calendar']<=b['median_pass_calendar']+3
        control=s['passed']>c['passed']
        gates.append(dict(protocol=protocol,efficiency=efficiency,safety=safety,timing=timing,
                          beats_reduced_pass_rate=control,passes=(efficiency or safety) and timing and control))
    survive=all(z['passes'] for z in gates)
    dump('design_gate.json',dict(survives=survive,protocols=gates,
         status='DESIGN SURVIVOR: historical validation required' if survive else 'REJECT: stop dependent validation',
         new_economic_proposals=1,total_definitions=4,alternative_2023_outcomes_run=False))
    receipt.update(prereg_commit=prereg,code_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
                   code_sha256=sha(__file__),fixtures=check,source_branch_head='ec7f9571',
                   plan_sha256=sha(ROOT/PLAN),dependencies={x.__name__:x.__version__ for x in [np,pd,numba]},
                   phase='design2018_2022',target_through_points=1.,mnq_commission_rt=1.25,
                   design_vb_trades=len(full),design_start_count=len(starts),
                   full_leg_held_missing_closes=sum(int(np.isnan(g.c[int(z.day),int(z.j0):int(z.j1)+1]).sum()) for z in full.itertuples()))
    for name in ['analysis/codex_eval_focus_baseline_20261109.py','analysis/candidates24.py',
                 'analysis/codex_break_vb_onb.py','analysis/grid.py','analysis/grid24.py',
                 'analysis/dual_thrust_test.py','analysis/dual_thrust_bench.py','analysis/portfolio.py','analysis/metrics.py']:
        receipt['files'][name]={'sha256':sha(ROOT/name)}
    dump('manifest.json',receipt)
    pd.DataFrame(stats).to_csv(OUT/'other_piece_reconciliation.csv',index=False)
    dump('mechanical_checks.json',check)
    print('GATE:',survive,gates,flush=True)


if __name__=='__main__':
    main()
