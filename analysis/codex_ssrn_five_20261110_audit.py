"""Uploaded paper versions and retrospective CL endpoint audit. No signals or economic returns."""
from pathlib import Path
import hashlib
import json
import re
import subprocess

import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
INPUT=ROOT/'agents/codex/inputs/ssrn_five_20261110'
OUT=ROOT/'analysis/outputs/codex_ssrn_five_20261110'
IDS=['2485314','2089463','2174501','2298565','3747330']


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    versions={}
    for id in IDS:
        pdf=INPUT/'source'/f'ssrn-{id}.pdf'
        text=subprocess.check_output(['pdftotext','-layout',str(pdf),'-'],text=True)
        assert f'abstract={id}' in text
        pages=text.split('\f')
        info=subprocess.check_output(['pdfinfo',str(pdf)],text=True)
        n=int(re.search(r'^Pages:\s*(\d+)',info,re.M)[1])
        assert len([p for p in pages if p.strip()])==n
        versions[id]=dict(pdf_sha256=sha(pdf),pages=n,ssrn_identity_matched=True,
                          text_sha256=hashlib.sha256(text.encode()).hexdigest())
        if id=='2174501':
            assert 'Current Version: June 2012' in text
            assert '1.36' in pages[52] and '1.45' in pages[52] and '1.42' in text
            assert 'For bonds, we similarly use the negative of the past five year return' in text
            assert 'Value = 5 year' in text and 'yield change' in text
            versions[id]['version_issues']=['body_1_42_vs_table_I_1_36_and_1_45',
                'main_text_bond_past_return_vs_table_and_later_text_yield_change']
        if id=='2298565':
            assert 'November 2016' in text
            assert '1.80' in text and '-0.67' in text and '-1.62' in text
        if id=='2485314':
            assert 'May 21, 2014' in text and '8.42%' in text and '3.98%' in text
        if id=='2089463':
            assert 'This version: September, 2011' in text and '52 are statistically' in text
        if id=='3747330':
            assert 'August 2021' in text and 'N=385' in text and 'N=77' in text
    api=pd.read_csv(INPUT/'api_schedule_2021_2022.csv',parse_dates=['week_end','publication'])
    assert len(api)==106 and set(api.schedule_year)=={2021,2022}
    api=api.drop_duplicates(['week_end','publication'])
    # An advance schedule's date is not proof of an actual receipt; do not invent that clock.
    eia_path=ROOT/'analysis/outputs/codex_eia_inventory_input_gate/design_archive_calendar.csv'
    eia=pd.read_csv(eia_path,parse_dates=['release_date','week_ending'])
    paired=api.merge(eia,left_on='week_end',right_on='week_ending',how='inner')
    paired=paired[paired.publication.dt.year.isin([2021,2022]) & paired.weekday.eq('Tuesday')
                  & paired.release_date.eq(paired.publication+pd.Timedelta(days=1))].copy()
    assert not paired.release_date.duplicated().any()
    frames=[];price_hashes={}
    for year in [2021,2022]:
        path=ROOT/f'data/CL_1min_{year}.csv'
        price_hashes[str(path.relative_to(ROOT))]=sha(path)
        frame=pd.read_csv(path)
        assert frame.columns.tolist()==['date','time','open','high','low','close','volume']
        assert not frame.duplicated(['date','time']).any()
        frames.append(frame)
    d=pd.concat(frames,ignore_index=True)
    idx=d.set_index(['date','time'])
    rows=[]
    for r in paired.itertuples():
        a=int(r.publication.strftime('%Y%m%d')); b=int(r.release_date.strftime('%Y%m%d'))
        required={'api_start':(a,1530),'api_end':(a,1600),'eia_entry_clock':(b,830),'eia_exit_clock':(b,929)}
        row=dict(api_schedule_year=int(r.schedule_year),api_date=str(r.publication.date()),
                 eia_date=str(r.release_date.date()),week_end=str(r.week_end.date()),
                 exact_eia_clock_verified=bool(r.exact_release_clock_verified),
                 original_publication_bytes_verified=bool(r.original_first_publication_bytes_verified))
        for name,key in required.items():
            exists=key in idx.index
            good=exists and np.isfinite(idx.loc[key,['open','high','low','close']].to_numpy(float)).all()
            row[name+'_present']=bool(good)
        minutes=list(range(831,860))+list(range(900,930))
        held=idx.reindex(pd.MultiIndex.from_tuples([(b,t) for t in minutes],names=['date','time']))
        row['pre_eia_path_missing_bars']=int((~np.isfinite(held[['open','high','low','close']]).all(axis=1)).sum())
        row['all_endpoint_rows_present']=all(row[n+'_present'] for n in required)
        row['all_planned_rows_present']=row['all_endpoint_rows_present'] and row['pre_eia_path_missing_bars']==0
        rows.append(row)
    q=pd.DataFrame(rows)
    q.to_csv(OUT/'cl_endpoint_audit_2021_2022.csv',index=False)
    audit=dict(api_schedule_rows=106,retrospectively_matched_normal_pairs=len(q),
               all_endpoint_rows_present=int(q.all_endpoint_rows_present.sum()),
               all_endpoint_and_planned_path_rows_present=int(q.all_planned_rows_present.sum()),
               pairs_by_year={str(y):int(n) for y,n in q.groupby(pd.to_datetime(q.eia_date).dt.year).size().items()},
               all_exact_eia_clocks_verified=bool(q.exact_eia_clock_verified.all()),
               all_original_release_bytes_verified=bool(q.original_publication_bytes_verified.all()),
               timestamp_timezone='assumed Chicago close labels; upstream CL export settings not independently authenticated',
               actual_api_receipts_verified=False,bloomberg_consensus_panel_present=False,native_contract_ids_present=False,
               signal_returns_computed=False,forward_returns_computed=False,price_hashes=price_hashes,
               api_schedule_sha256=sha(INPUT/'api_schedule_2021_2022.csv'),eia_archive_calendar_sha256=sha(eia_path))
    # Selected paper cells remain source claims, never independently reproduced performance.
    claims={
      '2485314':{'scope':'24 commodities,1990–2011,monthly', 'table':'Table2 PanelD',
                 'generic_net_annual_percent':3.98,'low_turnover_net_annual_percent':8.42,
                 'generic_sharpe':.25,'low_turnover_sharpe':.60,'low_turnover_t':2.74},
      '2089463':{'scope':'58 instruments,1985–2009,monthly','table':'Equation5 and Section4.1/4.2',
                 'positive_instruments':58,'pointwise_significant_5pct':52,'factor_alpha_percent_per_month':1.58},
      '2174501':{'scope':'eight market groups,throughJuly2011,monthly','table':'TableI PanelB; bodySectionII.A',
                 'global_combo_P3_minus_P1_sharpe':1.36,'global_combo_factor_sharpe':1.45,'narrative_combo_sharpe':1.42,
                 'gross_returns':True,'bond_rule_internal_discrepancy':True},
      '2298565':{'scope':'cross-asset monthly portfolios,November2016 draft','table':'TableII global and TableIX costs',
                 'global_gross_sharpe':1.20,'put_carry_gross_sharpe':1.80,'put_carry_two_half_spreads_sharpe':-.67},
      '3747330':{'scope':'WTI,2011–August2019','table':'Table2 PanelA and Table8',
                 'events':385,'extreme_events':77,'full_sample_sharpe':.67,'extreme_sharpe':2.10,
                 'post_API_to_pre_EIA_OLS_slope':.17,'regression_R2':.04,'net_profit_verified':False}}
    record=dict(versions=versions,source_claims=claims,cl_audit=audit,new_return_trials=0,
                economic_rule_preregistered=False,independent_validation=False,
                script_sha256=sha(__file__),git_head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip())
    (OUT/'source_and_data_audit.json').write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps({'versions':versions,'cl_audit':audit,'new_return_trials':0},indent=2))


if __name__=='__main__':
    main()
