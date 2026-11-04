"""Audit already-computed Ricochet ledgers; does not generate signals or new returns."""
from pathlib import Path
import hashlib,json,subprocess
import numpy as np
import pandas as pd
from codex_ricochet1144_20261104 import metrics,dump

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'agents/codex/inputs/ricochet1144_20261104'
OUT=ROOT/'analysis/outputs/codex_ricochet1144_20261104'

def main():
    saved=json.loads((OUT/'result.json').read_text());checks={};all_years=[];parts=[]
    for name in ['causal','protected']:
        d=pd.read_csv(OUT/(name+'_trades.csv'),parse_dates=['account_date','source_session_date'])
        daily=pd.read_csv(OUT/(name+'_observed_daily.csv'),parse_dates=[0])
        idx=pd.DatetimeIndex(daily.iloc[:,0]);r=saved['candidates'][name.upper()]
        assert len(d)==r['closed_trades']==1131
        assert d.complete.sum()==r['complete_trades']==20
        assert not (d.entry.to_numpy()[1:]<d.exit.to_numpy()[:-1]).any()
        assert (d.ordinal.between(1,4)).all() and d.side.eq(1).all()
        assert np.allclose(d.net_nq,d.gross_nq-d.slippage_nq-d.commission_nq)
        assert np.allclose(d.net_nq,(d.exit_fill-d.entry_fill)*20.-7.25)
        assert np.allclose(d.net_mnq,(d.exit_fill-d.entry_fill)*2.-1.24)
        assert np.isclose(d.net_nq.sum(),daily.iloc[:,1].sum())
        assert np.isclose(d.net_nq.sum(),r['observed_path_diagnostic']['total'])
        known=d[d.complete];assert np.isclose(known.net_nq.sum(),r['complete_path']['total'])
        assert r['advance'] is False
        years=[]
        for y in range(2018,2023):
            m,_=metrics(d[d.account_date.dt.year==y],idx[idx.year==y]);m.update(candidate=name,year=y,scope='observed_path_diagnostic');years.append(m)
        all_years.extend(years)
        assert np.isclose(sum(x['total'] for x in years),d.net_nq.sum())
        for ordinal,group in d.groupby('ordinal'):
            parts.append(dict(candidate=name,ordinal=int(ordinal),trades=len(group),net_nq=float(group.net_nq.sum()),scope='descriptive executed-parent component, not standalone no-reentry test'))
        checks[name]=dict(accounting='PASS',long_trades=len(d),short_trades=0,
            observed_years_positive=sum(x['total']>0 for x in years),
            average_modeled_cost=float((d.commission_nq+d.slippage_nq).mean()),
            native_mnq_diagnostic_total=float(d.net_mnq.sum()),
            worst_observed_ticket_nq=float(d.net_nq.min()),
            cutoff_ticket_rows=d.loc[d.crossed_flat_deadline,['entry_time','exit_time','kind','net_nq']].to_dict('records'))
    pd.DataFrame(all_years).to_csv(OUT/'observed_path_years.csv',index=False)
    pd.DataFrame(parts).to_csv(OUT/'observed_path_components.csv',index=False)
    files=[dict(path=str(p.relative_to(ROOT)),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in sorted(OUT.iterdir()) if p.is_file() and p.name not in ['audit.json']]
    dump(OUT/'audit.json',dict(scope='Accounting and standard views of frozen two-candidate output only; no new parameter/control/validation return run.',
        preregistration_commit=saved['preregistration_commit'],candidate_checks=checks,artifacts=files,
        author_chain_rows_sum=2479423,author_chain_total_claim=5867006,author_batch_claim=9900000,
        source_arithmetic='Printed rows do not sum to the stated chain total; an unprovided run register could explain omitted counts. Batch/chain scopes differ; no independent validation.',
        stdout_error='First run wrote all ledgers/result.json and then exited1 on final json.dumps numpy boolean. Display-only repair made afterward; no market simulation rerun.',
        publication='Local preregistration6d6d3e7 preceded returns; remote push confirmed afterward once network permission restored proxy access. No fetched-remote claim before outcomes; this is the direct upload program, not scout admission.',
        repository_head_at_audit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()))
    print('PASS:both1131-ticket ledgers,price/cost/native-micro equations,trade-to-day/year totals,nonoverlap,ordinal caps and retained quality flags. No new economic outcomes.')

if __name__=='__main__':main()
