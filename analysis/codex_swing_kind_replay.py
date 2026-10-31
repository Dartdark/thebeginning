"""Frozen accounting rerun; see agents/codex/plans/swing_kind_replay_20261031.md.

PYTHONPATH=/tmp/codex_replay_deps python3 analysis/codex_swing_kind_replay.py prepare
Then worker 50|150 SEED N, and summarize. All simulators remain repository code.
"""
import gc
import hashlib
import json
from pathlib import Path
import pickle
import platform
import subprocess
import sys
import time

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SP = ROOT / 'scratch_data'
OUT = ROOT / 'analysis/outputs/codex_swing_kind_replay_20261031'
OUT.mkdir(parents=True, exist_ok=True)
mode, *args = sys.argv[1:]
# Shared helpers read argv at import; give them the actual scratch directory.
sys.argv = ['replay', str(SP), 'library']
import funded_bootstrap as FB
import funded_sim as F50
import funded_sim150 as F150
import swing_target_bench as ST
from funded_lab import with_slippage


def save(name, obj):
    (OUT / name).write_text(json.dumps(obj, indent=2, default=str) + '\n')


def allocations(which):
    plans = ST.plans50() if which == 50 else ST.plans150()
    base = next(iter(plans.values()))
    # Controls isolate the reduced slot from the candidate contribution.
    if which == 50:
        plans.update({'EMPTY RS longs': {k:v for k,v in base.items() if k != 'RS_L'},
                      'EMPTY EOS': {k:v for k,v in base.items() if k != 'EOS'},
                      'EMPTY VB normal 1': {**base, 'VB_N': 1}})
    else:
        plans.update({'EMPTY DT': {k:v for k,v in base.items() if k != 'DT'},
                      'EMPTY DT 1': {**base, 'DT': 1}})
    # Duplicate only allocations containing ST; controls are shared verbatim.
    plans.update({'legacy: '+k: {('ST_OLD' if a == 'ST' else a):v for a,v in p.items()}
                  for k,p in list(plans.items()) if 'ST' in p})
    return plans


def prepare():
    import single_print_test as S
    import relative_strength_test as RS
    import s_rank_gap_round2_test as GAP
    import cl_forced_flows_test as CL
    import overnight_tick_bench as OT
    from build_lab import REPORTS
    from funded_lab import Lab
    from portfolio import load_mc
    # Reuse fixed helper functions, never their parameter-search __main__ blocks.
    g = pickle.load(open(SP/'g24.pkl', 'rb'))
    # Apply the preregistered date boundary BEFORE constructing paths. The
    # shared build_lab currently encounters an out-of-window midnight exit.
    lab = Lab(g)
    atr = g.daily_atr(15)
    required = ['VB', 'ONB_ML2_MC', 'EOS', 'MON_MC', 'LDF_MC', 'NFP_MC']
    cache_audit = []
    for name in required:
        path, stop = REPORTS[name]
        t = load_mc(g, path)
        outside = t.date > '2026-10-09'
        cache_audit.append(dict(strategy=name, loaded=len(t), outside_window=int(outside.sum())))
        t = t.loc[~outside].reset_index(drop=True)
        assert (t.j1 >= t.j0).all(), 'Unresolved in-window baseline trade geometry'
        lab.add(name, t, stop_pts=stop*atr)
    pickle.dump(lab, open(SP/'lab.pkl', 'wb'))
    del lab
    save('cache_build_audit.json', cache_audit)
    pickle.dump(g, open(SP/'nq.pkl', 'wb'))
    _, flags = S.frame()
    flags.to_pickle(SP/'single_print_sessions.pkl')
    del g
    d, n, e = RS.load()
    RS.trades(d, n, RS.signals(d, n, e)).to_csv(SP/'rs_trades.csv', index=False)
    del d, n, e
    cl = CL.load('CL')
    sym = GAP.Sym('CL', cl)
    bars, _ = GAP.rolls_cl(sym)
    sym.set_rolls(bars)
    frame = GAP.sunday_frame(sym)
    pickle.dump({'frames': {'CL': frame}}, open(SP/'s_rank_gap2.pkl', 'wb'))
    del cl, sym
    ledger = ROOT/'analysis/outputs/codex_swing_target/CODE_BE_trades.csv'
    (SP/'swing_be.csv').write_bytes(ledger.read_bytes())
    audits = {}
    for which in (50, 150):
        lab = OT.lab_for(which)
        t = ST.pt_trades(lab.g)
        old = t.copy()
        old['kind'] = old.kind.map({0: 'stop', 1: 'target', 2: 'time'})
        # Holiday repairs already used numeric time exits in the original adapter.
        repairs = pd.read_csv(ledger, parse_dates=['date'])
        repair_days = repairs.loc[repairs.apex_flat_violation, 'date']
        old.loc[old.date.isin(repair_days), 'kind'] = 2
        lab.add('ST', t)
        lab.add('ST_OLD', old)
        dates = pd.DatetimeIndex(lab.g.ts[lab.tr])
        expected = (with_slippage(t).exit-t.entry)*t.side*20-7.25
        assert np.allclose(expected, t.net), 'Corrected raw trade accounting differs from ledger'
        assert np.isclose(lab.C['ST'].sum()*10, t.net.sum())
        ix = np.where((dates >= '2018-01-01') & (dates <= '2026-10-09'))[0]
        for key in list(lab.W):
            lab.W[key] = lab.W[key][ix]
            lab.C[key] = lab.C[key][ix]
            if key in lab.stop: lab.stop[key] = lab.stop[key][ix]
        lab.tr = lab.tr[ix]
        lab.D = len(ix)
        lab.yr = lab.yr[ix]
        audits[str(which)] = dict(days=lab.D, first=str(dates[ix][0]), last=str(dates[ix][-1]),
            trades=len(t), kinds=t.kind.value_counts().to_dict(),
            corrected_net_per_NQ=float(t.net.sum()),
            corrected_minus_legacy_net_per_MNQ=float((lab.C['ST']-lab.C['ST_OLD']).sum()),
            holiday_repairs=[str(x.date()) for x in repair_days], plans=allocations(which))
        pickle.dump(lab, open(SP/f'codex_st_replay_{which}.pkl', 'wb'))
        del lab
        gc.collect()
    files = [ledger, Path(__file__), ROOT/'analysis/swing_target_bench.py',
             ROOT/'analysis/funded_bootstrap.py', ROOT/'analysis/funded_sim.py',
             ROOT/'analysis/funded_sim150.py']
    files += sorted((ROOT/'data').glob('*1min*.csv'))
    files += sorted((ROOT/'mc_reports').glob('*.xlsx'))
    save('manifest.json', dict(commit=subprocess.check_output(['git','rev-parse','HEAD'], text=True).strip(),
         python=platform.python_version(), numpy=np.__version__, pandas=pd.__version__,
         hashes={str(f.relative_to(ROOT)):hashlib.sha256(f.read_bytes()).hexdigest() for f in files},
         audits=audits, seeds=[1,2], histories_per_seed=250, block=20, horizon=500,
         fees='Inherited $7.25/NQ divided by 10; $.50/MNQ per non-limit fill; not native micro fees'))
    print(json.dumps(audits, default=str), flush=True)


def worker(which, seed, n):
    lab = pickle.load(open(SP/f'codex_st_replay_{which}.pkl', 'rb'))
    FB.F = F50 if which == 50 else F150
    start = time.time()
    res, y1, minutes = FB.Boot(lab).run(allocations(which), n=n, L=20, seed=seed,
                                      ref=1500. if which == 50 else 3000.)
    rows=[]
    for name, values in res.items():
        for i, v in enumerate(values):
            rows.append(dict(plan=name, seed=seed, history=i, paid2=v[0], payouts=v[1],
                             days=v[2], blown=v[3], first=v[4], paid1=y1[name][i]))
    pd.DataFrame(rows).to_csv(OUT/f'paths_{which}_{seed}.csv', index=False)
    print(which, seed, n, 'done', round(time.time()-start), 'seconds', minutes, 'minutes', flush=True)


def summarize():
    rng=np.random.default_rng(20261031)
    tables=[]; pairs=[]
    for which in (50,150):
        df=pd.concat([pd.read_csv(OUT/f'paths_{which}_{s}.csv') for s in (1,2)])
        assert df.groupby('plan').size().eq(500).all()
        base=f'{which}K plan'
        by={k:v.sort_values(['seed','history']).reset_index(drop=True) for k,v in df.groupby('plan')}
        for name, d in by.items():
            t6=np.where(d.payouts.eq(6), d.days, np.inf)
            tables.append(dict(account=which,plan=name,y1=d.paid1.mean(),y1_p5=d.paid1.quantile(.05),
                y2=d.paid2.mean(),y2_p5=d.paid2.quantile(.05),blown=d.blown.mean(),
                all6=d.payouts.eq(6).mean(),days6=np.median(t6)))
        for name, d in by.items():
            if name.startswith('legacy:'): continue
            refs=[base] if name != base else []
            if 'legacy: '+name in by: refs.append('legacy: '+name)
            if 'ST' in allocations(which)[name]:
                p=allocations(which)[name]; empty={k:v for k,v in p.items() if k!='ST'}
                refs += [k for k in by if k.startswith('EMPTY') and allocations(which)[k]==empty]
            for ref in dict.fromkeys(refs):
                row=dict(account=which,plan=name,reference=ref)
                for metric in ('paid1','paid2','blown'):
                    delta=(d[metric]-by[ref][metric]).to_numpy()
                    boot=np.mean(delta[rng.integers(0,len(delta),(5000,len(delta)))] ,axis=1)
                    row[metric+'_diff']=delta.mean()
                    row[metric+'_ci_low'],row[metric+'_ci_high']=np.quantile(boot,[.025,.975])
                row['payout2_win_tiehalf']=np.mean(d.paid2>by[ref].paid2)+.5*np.mean(d.paid2==by[ref].paid2)
                pairs.append(row)
    pd.DataFrame(tables).to_csv(OUT/'summary.csv',index=False)
    pd.DataFrame(pairs).to_csv(OUT/'paired_effects.csv',index=False)
    print(pd.DataFrame(tables).round(3).to_string(index=False))
    print(pd.DataFrame(pairs).round(3).to_string(index=False))


if __name__=='__main__':
    if mode=='prepare': prepare()
    elif mode=='worker': worker(*map(int,args))
    elif mode=='summarize': summarize()
    else: raise ValueError(mode)
