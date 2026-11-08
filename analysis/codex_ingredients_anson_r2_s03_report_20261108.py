"""Make the requested ingredient grids from frozen ledgers; no price replay."""
import json

import numpy as np
import pandas as pd

import codex_ingredients_anson_r2_s03_20261108 as C

LABELS={
    'ANSON':{'original':'As is: strength4.5 / hold20, early adapter',
        'fade_direction':'Fade momentum direction','no_strength_gate':'Remove strength threshold',
        'hold_6':'Hold6 bars instead of20','no_early_adapter':'Remove early-close adapter'},
    'R2':{'original':'As is: CT vault/slope,75stop/40target, flat guard',
        'fade_break':'Fade upward trigger, mirrored bracket','no_R2_gate':'Refresh vault every bar (no R² gate)',
        'no_slope_gate':'Remove positive-slope gate','no_stop':'No stop; target/flatten retained'},
    'S03':{'original':'As is: band+VWAP entry,0.4sigma stop',
        'fade_direction':'Fade direction; virtual-source band exits','no_entry_VWAP':'Remove entry VWAP confirmation',
        'no_entry_band':'Remove entry band crossing; follow VWAP','no_sigma_stop':'No sigma stop'},
}


def main():
    out=C.OUT;whole,years,audits,grid=[],[],[],[]
    phases={};effects={}
    for phase in ('design','recent'):
        receipt=json.loads((out/phase/'summary.json').read_text())
        C.check(receipt['implementation_gates_passed'] and receipt['rule_cases']==15
                and receipt['script_sha256']==C.sha(C.ROOT/C.CODE),'Changed or unfinished phase')
        phases[phase]=pd.read_csv(out/phase/'metrics.csv')
        effects[phase]=pd.read_csv(out/phase/'paired_effects.csv')
    for family,variants in C.FAMILIES.items():
        for variant in variants:
            stem=family+'__'+variant;trades=[];days={side:[] for side in ('all','long','short')}
            for phase in ('design','recent'):
                t=pd.read_csv(out/phase/(stem+'_trades.csv'),parse_dates=['date','entry_date','exit_date_actual'])
                C.check(np.allclose(t.gross-t.commission-t.slippage,t.net),'Cost bridge mismatch')
                trades.append(t)
                marked={}
                for side in days:
                    d=pd.read_csv(out/phase/(stem+'_'+side+'_daily.csv'),index_col=0,parse_dates=True)
                    sub=t if side=='all' else t[t.side.eq(1 if side=='long' else -1)]
                    C.check(abs(sub.net.sum()-d.net.sum())<.005,'Marked side total mismatch')
                    days[side].append(d);marked[side]=d
                C.check(np.allclose(marked['all'].net,marked['long'].net+marked['short'].net),'Daily sides mismatch')
                worst=t.loc[t.source_adverse_mark.idxmin()]
                audits.append({'family':family,'variant':variant,'phase':phase,'trades':len(t),
                    'worst_mark_entry':str(worst.entry_date.date()),'worst_mark_exit':str(worst.exit_date_actual.date()),
                    'worst_mark':float(worst.source_adverse_mark),'net_on_worst_mark':float(worst.net),
                    'unknown_minutes_on_worst_mark':int(worst.unknown_held_minutes),
                    'cross_date':int(t.entry_date.ne(t.exit_date_actual).sum()),
                    'late_after_1559':int(t.late_after_1559.sum()),'unknown_held_minutes':int(t.unknown_held_minutes.sum()),
                    'tainted_history_trades':int(t.tainted_prior_sessions.gt(0).sum()) if family=='S03' else None})
            t=pd.concat(trades,ignore_index=True)
            for side in days:
                sub=t if side=='all' else t[t.side.eq(1 if side=='long' else -1)]
                d=pd.concat(days[side]);C.check(d.index.is_unique and d.index.is_monotonic_increasing,'Era calendars overlap')
                row={'family':family,'variant':variant,'period':'2018-2026-10-09','side':side,**C.H.metrics(sub,d)}
                C.check(abs(row['net_total']-row['trade_net_total'])<.005,'Whole marked total mismatch')
                whole.append(row)
                for year in sorted(set(d.index.year)):
                    years.append({'family':family,'variant':variant,'side':side,'year':year,
                        **C.H.metrics(sub[sub.date.dt.year.eq(year)],d[d.index.year==year])})
                if side=='all' or variant=='original':
                    g={'family':family,'variant':variant,'side':side,
                       'change':LABELS[family][variant] if side=='all' else 'Baseline '+side+'-trade contribution',
                       'full_trades':row['trades'],'full_avg':row['avg'],'full_t':row['t_trade'],
                       'full_net':row['net_total'],'full_dd':row['max_dd']}
                    for phase,m in phases.items():
                        q=m[(m.family==family)&(m.variant==variant)&(m.side==side)&(m.period==phase)].iloc[0]
                        for col in ['trades','avg','t_trade','net_total','max_dd','worst_trade','worst_source_adverse_mark']:
                            g[phase+'_'+col]=q[col]
                    if side!='all':g['read']='Baseline contribution; not a side-only strategy rerun'
                    elif variant=='original':g['read']='Base'
                    else:
                        contrasts=[effects[p][(effects[p].family==family)&(effects[p].intervention==variant)].iloc[0]
                                   for p in ('design','recent')]
                        deltas=[r.base_minus_intervention_net for r in contrasts]
                        if all(abs(v)<.005 for v in deltas):g['read']='Same net in both eras; compare paths/counts'
                        elif all(v>0 for v in deltas):
                            g['read']='Original adds net in both eras'
                            if all(r.annual_effect_p5>0 for r in contrasts):g['read']+='; both paired bounds positive'
                            else:g['read']+='; separation remains uncertain'
                        elif all(v<0 for v in deltas):g['read']='Original sacrifices net in both eras; compare protection/exposure'
                        else:g['read']='Conditional or zero profit effect across eras'
                        g['read']+='; recent DD $'+format(g['recent_max_dd'],',.0f')
                    grid.append(g)
    w=pd.DataFrame(whole);y=pd.DataFrame(years);gg=pd.DataFrame(grid)
    for (family,variant,side),a in y.groupby(['family','variant','side']):
        q=w[(w.family==family)&(w.variant==variant)&(w.side==side)].iloc[0]
        C.check(abs(a.net_total.sum()-q.net_total)<.005,'Marked yearly totals mismatch')
    w.to_csv(out/'whole_metrics.csv',index=False);y.to_csv(out/'year_side_metrics.csv',index=False)
    y[y.variant.eq('original')&y.side.eq('all')].to_csv(out/'original_year_metrics.csv',index=False)
    gg.to_csv(out/'ingredient_grid.csv',index=False)
    C.B.dump(out/'path_ledger_audit.json',{'all_checks_passed':True,'cases':audits,'new_market_return_definitions':0})
    lines=['Cells show design2018–22 / recent2023–2026-10-09. Net standard-NQ dollars after stated costs.','']
    money=lambda v: '—' if pd.isna(v) else ('−' if v<0 else '')+'$'+format(abs(v),',.0f')
    number=lambda v:'—' if pd.isna(v) else format(v,'.2f')
    for family in C.FAMILIES:
        lines += ['**'+family+'**','', '| Change | $ a trade | t | Read |', '|---|---:|---:|---|']
        for r in gg[gg.family==family].itertuples():
            if r.side!='all' and r.design_trades+r.recent_trades==0: continue
            lines.append('| '+r.change+' | '+money(r.design_avg)+' / '+money(r.recent_avg)+' | '
                         +number(r.design_t_trade)+' / '+number(r.recent_t_trade)+' | '+r.read+' |')
        lines.append('')
    (out/'ingredient_grid.md').write_text('\n'.join(lines).rstrip()+'\n')
    print('ORIGINALS WHOLE HISTORY')
    print(w[w.variant.eq('original')&w.side.eq('all')][['family','trades','avg','t_trade','net_total','sharpe','sortino',
        'profit_factor','max_dd','calmar','ulcer']].round(2).to_string(index=False))
    print('GRID DATA')
    print(gg[gg.side.eq('all')][['family','variant','design_avg','design_t_trade','recent_avg','recent_t_trade',
        'design_net_total','recent_net_total','recent_max_dd']].round(2).to_string(index=False))


if __name__=='__main__': main()
