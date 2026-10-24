"""Independent Anson saved-output arithmetic; no new price returns or selection."""
from pathlib import Path
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'agents/codex/runtime/or_pullback_python'),str(ROOT/'analysis')]
import numpy as np
import pandas as pd
OUT=ROOT/'analysis/outputs/codex_anson'

def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()

def mask(d,period):
    y=pd.DatetimeIndex(d).year
    if period=='2018_plus':return y>=2018
    if period=='2018_22':return (y>=2018)&(y<2023)
    if period in ('2018_24','2018_24_author_IS'):return (y>=2018)&(y<2025)
    if period=='2023_plus':return y>=2023
    if period in ('2025_plus','2025_plus_replication'):return y>=2025
    return y==int(period)

def main():
    checks=0
    stats=pd.read_csv(OUT/'diagnostics/standard_stats.csv')
    for model,sub in stats.groupby('model'):
        t=pd.read_csv(OUT/'replay'/f'{model}_trades.csv',parse_dates=['date'])
        if model=='intended_apex':
            a=pd.read_csv(OUT/'replay'/f'{model}_audit.csv',parse_dates=['date'])
            t=t[t.date.isin(set(a.loc[a.account_eligible,'date']))]
            early=a.set_index('date').early_close_proxy.reindex(t.date).to_numpy(bool)
            np.testing.assert_array_equal(t.exit_j,np.minimum(t.entry_j+100,np.where(early,691,896)))
        for row in sub.itertuples():
            z=t[mask(t.date,row.period)]
            if row.group=='long':z=z[z.side>0]
            if row.group=='short':z=z[z.side<0]
            x=(z.exit-z.entry)*z.side*20-row.fee_micro*10-10
            expected=dict(trades=len(x),avg=x.mean(),avg_mnq=x.mean()/10,total_mnq=x.sum()/10,
                          t=x.mean()/x.std(ddof=1)*np.sqrt(len(x)),win=(x>0).mean())
            for k,v in expected.items():
                np.testing.assert_allclose(getattr(row,k),v,rtol=0,atol=1e-8,equal_nan=True);checks+=1
    funded=pd.read_csv(OUT/'accounts/funded_summary.csv')
    for row in funded.itertuples():
        z=np.load(OUT/'accounts'/f'funded_results_{row.fee:.2f}_{row.context}_{row.cohort}.npz')
        a,b=z[row.config+'__250'],z[row.config+'__500']
        assert a.shape==b.shape==(1000,5)
        vals=dict(year1=a[:,0].mean(),year1_p5=np.percentile(a[:,0],5),year1_p95=np.percentile(a[:,0],95),
                  year2=b[:,0].mean(),year2_p5=np.percentile(b[:,0],5),year2_p95=np.percentile(b[:,0],95),
                  blown=b[:,3].mean(),all6=(b[:,1]==6).mean(),days6=np.median(np.where(b[:,1]==6,b[:,2],np.inf)))
        for k,v in vals.items():np.testing.assert_allclose(getattr(row,k),v,rtol=0,atol=1e-10);checks+=1
    exact=[]
    for fee in (1.04,1.24):
        p=json.loads((OUT/'accounts'/f'funded_parity_{fee:.2f}.json').read_text())
        assert all(x['exact'] and x['original']==x['lookup'] for x in p)
        exact+=p
    assert len(exact)==220
    ev=pd.read_csv(OUT/'accounts/evaluation_summary.csv')
    for (fee,context),sub in ev.groupby(['fee','context']):
        d=pd.read_csv(OUT/'accounts'/f'evaluation_starts_{fee:.2f}_{context}.csv',parse_dates=['date'])
        valid_col=next(c for c in d if 'complete' in c)
        for row in sub.itertuples():
            ok=d[valid_col]&mask(d.date,row.cohort)
            o=d.loc[ok,row.config+'__outcome']
            assert len(o)==row.starts
            for k,v in (('passed',(o=='pass').mean()),('failed',(o=='fail').mean()),('timed_out',(o=='time').mean())):
                np.testing.assert_allclose(getattr(row,k),v,rtol=0,atol=1e-12);checks+=1
    personal=pd.read_csv(OUT/'personal/mc_summary.csv')
    for row in personal.itertuples():
        z=np.load(OUT/'personal'/f'paired_mc_{row.cohort}.npz')
        p,d=z[row.config+'__profit'],z[row.config+'__dd']
        assert len(p)==len(d)==5000
        vals=dict(profit_p5=np.quantile(p,.05),profit_p50=np.median(p),profit_p95=np.quantile(p,.95),
                  profit_mean=p.mean(),p_losing_year=(p<=0).mean(),dd_p50=np.median(d),dd_p95=np.quantile(d,.95),
                  capital_20pct=np.quantile(d,.95)/.2)
        for k,v in vals.items():np.testing.assert_allclose(getattr(row,k),v,rtol=0,atol=1e-8);checks+=1
    c=pd.read_csv(OUT/'personal/candidate_daily.csv',index_col=0).iloc[:,0]
    t=pd.read_csv(OUT/'replay/intended_raw_trades.csv')
    np.testing.assert_allclose(c.sum(),(t.gross_points*2-2.275).sum(),rtol=0,atol=1e-7)
    t['date']=pd.to_datetime(t.date)
    context=[]
    for period in ('2018_22','2018_24_author_IS','2025_plus_replication'):
        s=t[mask(t.date,period)]
        x=s.gross_points*20-20.4
        context.append(dict(period=period,trades=len(s),net_sd_nq=x.std(ddof=1),
                            median_prior_bar_range_points=s.average_range.median(),
                            median_abs_trade_points=s.gross_points.abs().median()))
    (OUT/'risk_scale_context.json').write_text(json.dumps(dict(periods=context,
        reported_ci_width_ratio=655/123,reported_sample_only_width_ratio=np.sqrt(2023/352),
        caveat='Approximate comparison assumes comparable CI construction and independent sampling; not a new sized strategy'),indent=2)+'\n')
    result=dict(arithmetic_fields_checked=checks,standard_rows=len(stats),funded_rows=len(funded),evaluation_rows=len(ev),
                personal_rows=len(personal),funded_production_exact_parity=len(exact),personal_raw_trades=len(t),
                source_no_selection=True,review='PASS WITH CONCERNS; not original MC parity')
    (OUT/'independent_output_audit.json').write_text(json.dumps(result,indent=2)+'\n')
    manifest=dict(preregistration='928c0ea',context='e34d71cd3537a9f019d2521e280fc92f3ffdb4c6',python=sys.version,
         scripts={p.name:sha(p) for p in (ROOT/'analysis').glob('codex_anson*.py')},
         input_source=sha(ROOT/'agents/codex/inputs/anson_momentum/source.txt'),
         market_cache=sha(ROOT/'scratch_data/g24.pkl'),prepared_accounts=sha(ROOT/'agents/codex/runtime/anson_plan.pkl'))
    (OUT/'final_reproduction.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
