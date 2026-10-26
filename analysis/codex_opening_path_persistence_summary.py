"""Combine frozen design and historical validation; no additional economic variants."""
import json
from pathlib import Path
import sys
import pandas as pd
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'analysis'))
import codex_t6_study_support as S
C=S.C;OUT=ROOT/'analysis/outputs/codex_opening_path_persistence'

def main():
    days=pd.DatetimeIndex(pd.concat([pd.read_csv(OUT/f'{p}_daily.csv',parse_dates=['date']).date for p in ('design','validation')]).sort_values())
    assert days.is_unique
    models={};rows=[];filters={}
    for model in ('OPP','ALL5'):
        t=pd.concat([pd.read_csv(OUT/f'{p}_{model}_trades.csv',parse_dates=['date']) for p in ('design','validation')],ignore_index=True).sort_values('date')
        assert not t.date.duplicated().any()
        # Shared grids have different date origins in design/validation. Normalize
        # keys by actual date before causal subset/full-ledger diagnostics.
        t['day']=days.get_indexer(t.date);assert (t.day>=0).all()
        models[model]=t;C.csv(OUT/f'full_{model}_trades.csv',t)
        for side,label in ((0,'all'),(1,'long'),(-1,'short')):
            x=t if not side else t[t.side==side]
            rows.append(dict(model=model,period='2018-26',side=label,**C.stats(x,days)))
        for col in ('net_mnq','stress_four_ticks'):
            x=t.copy()
            if col=='net_mnq':x['pnl']/=10.
            rows.append(dict(model=model,period='2018-26',side=col,**C.stats(x,days,column=col)))
    m=pd.DataFrame(rows);C.csv(OUT/'full_metrics.csv',m)
    filters['OPP']=C.filter_controls(models['OPP'],models['ALL5'],days);C.dump(OUT/'full_filter_diagnostics.json',filters)
    own=m[(m.model=='OPP')&(m.side=='all')].iloc[0]
    result=dict(goal_met=bool(own.t_trade>=6 and own.t_nw5>=6),trade_t=float(own.t_trade),daily_nw5_t=float(own.t_nw5),validation_trade_t=float(pd.read_csv(OUT/'validation_metrics.csv').query("model=='OPP' and side=='all' and period=='2023+'").t_trade.iloc[0]),status='below t6; continue new research',program_continues=True)
    C.dump(OUT/'full_goal_check.json',result);print(m[['model','side','trades','total','avg','profit_factor','t_trade','t_nw5','max_dd']].to_string(index=False));print(result)
    p=ROOT/'agents/codex/results/opening_path_persistence.md';old=p.read_text()
    marker='## How the trade works';tail=old[old.index(marker):]
    tail=tail[:tail.index('## Design results')]
    full=pd.concat([pd.read_csv(OUT/'design_metrics.csv'),pd.read_csv(OUT/'validation_metrics.csv'),m],ignore_index=True)
    p.write_text(f'''# NQ Opening Path Persistence: below t6; research continues

Summary: The frozen standalone5minNQ rule passed design but weakened in historical validation.
2018-22:418trades,t4.187,NW5 4.294.2023+:342trades,t1.266,NW5 1.225,net$47,885.50/NQ.
Full:760trades,net${own.total:,.2f}/NQ,trade t{own.t_trade:.3f},dailyNW5 t{own.t_nw5:.3f},PF{own.profit_factor:.3f}.
Goal notmet. Preserve the failedt6test; continue a different mechanism, without substituting a neighboring variant.

Plan: agents/codex/plans/opening_path_persistence.md,b2875a3. Design committed0275510beforevalidation.
Scripts: analysis/codex_opening_path_persistence.py,analysis/codex_opening_path_persistence_summary.py.
Outputs: analysis/outputs/codex_opening_path_persistence/.
Trials:5follow-upevaluations,4uniquenewsettings+1prior-controlnomination; program25evaluations/24unique.
Nomination selectedafter originalsource-control2018-22results; notindependentpreregistration. Unknown older
repository/author searches remain;2023+ispreviouslyseenhistoricalreplication,nota freshholdout.

'''+tail+'## Results\n\nDollars/NQ except net_mnq rows in nativeMNQ. Standardrepo metrics, initialzeroDD and cash-dayzeros.\n\n'+S.table(full)+f'''

## Controls and limits

Frozen nomination reproduced source OWN5economic ledger exactly. Allthree neighbors designpositive(t3.70--4.35),
no neighboring validation evaluated. UnfilteredALL5fullnet${filters['OPP']['base_net']:,.2f}; removednet
${filters['OPP']['removed_net']:,.2f}(avg${filters['OPP']['removed_avg']:,.2f},t{filters['OPP']['removed_t']:.3f}).
Full1000randomsubsets p(net>=kept)={filters['OPP']['p_random_net_ge_kept']:.3f}; jointbetterprofit/DD
{filters['OPP']['p_kept_better_net_and_dd']:.1%}. See separate design/validation diagnostics for staged results.
The previouslyrecorded designpass alert does not establish a qualifyingt6candidate. Validation is weaker,
full dailydependenceadjustedt is below6. No threshold, side, sizing or exit substitution made aftervalidation.
No missingheldminutes in primary. Intake audits no duplicateconflicts. SourceCTtime, completecashopen bars.
Target1pointthrough, protectedentrybar, worsestopgaps. Actualreceipt/spread/roll-splicefidelity unverified.

No t6claim, promotion, independentchecker, fullaccountbench orPowerLanguage. Contingent expensiveplacebos/
resampling/accounts are not warranted for the failedpointgoal. A positive fullhistory alone does not establish
accountutility or independence from existingcashmomentum strategies. Keepresearching distinct preregistered
mechanisms; nofavorable rescaling or postvalidationselection to force success.
Claudehandoff: agents/codex/results/opening_path_persistence.md.
''')
    p=ROOT/'agents/codex/research/t6_progress.json';q=json.loads(p.read_text());q.update(status='researching',goal_met=False,notification_event=None,latest_completed_hypothesis='NQ Opening Path Persistence historical validation',latest_result=f"Designpass did not reach goal:fulltrade t{own.t_trade:.3f},dailyNW5 {own.t_nw5:.3f};2023+trade t1.266. No neighboring substitution; continue new mechanism.",next_action='Prepare the next distinct evidence sheet/preregistration, avoiding post-validation retuning.');p.write_text(json.dumps(q,indent=2)+'\n')
    p=ROOT/'agents/codex/research/t6_program.md';q=p.read_text().replace('| NQ Opening Path Persistence | Design pass; validation pending |5evaluations(4new+1renomination);418trades,t4.19,NW5 4.29; result-informed selection disclosed |',f'| NQ Opening Path Persistence | Below t6 after historical validation |25program evaluations/24unique; fulltrade t{own.t_trade:.3f},NW5 {own.t_nw5:.3f};2023+t1.266. No retuning |');p.write_text(q)

if __name__=='__main__':main()
