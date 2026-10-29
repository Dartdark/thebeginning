"""Render saved hourly CHoCH controls and reconstruct side/year diagnostics."""
import json
from pathlib import Path
import numpy as np
import pandas as pd
import codex_choch_placebos as study


def table(rows,columns):
    def fmt(x):
        if isinstance(x,float):return f'{x:,.4f}'
        return str(x)
    return '\n'.join(['| '+' | '.join(columns)+' |','| '+' | '.join(['---']*len(columns))+' |']+
                     ['| '+' | '.join(fmt(r.get(c,'')) for c in columns)+' |' for r in rows])


def side_years(dest,catalog):
    """Derived-only exact attribution, no price reads or new random draws."""
    ids=catalog.outcome_id.to_numpy(int)
    assert np.array_equal(ids,np.arange(len(catalog)))
    net=catalog.net_mnq.to_numpy(float)
    sides=catalog.side.to_numpy(int)
    years=pd.to_datetime(catalog.entry_time).dt.year.to_numpy(int)
    records=[]
    for name in ['RS','RT','RD']:
        with np.load(dest/'paths'/name/'paths.npz',allow_pickle=False) as z:
            choice=z['chosen_outcome_ids'].astype(int);admitted=z['admitted_mask']
            values=net[choice];chosen_sides=sides[choice];chosen_years=years[choice]
            assert np.isfinite(values[admitted]).all(), 'Unknown attribution requires explicit bounds'
            values=np.where(admitted,values,0.)
            for trial in range(len(choice)):
                for label,mask in [('long',chosen_sides[trial]==1),('short',chosen_sides[trial]==-1)]:
                    records.append(dict(null=name,trial=trial+1,group=label,
                        admitted=int((admitted[trial]&mask).sum()),net_total=float(values[trial,mask].sum())))
                for year in range(2018,2023):
                    mask=chosen_years[trial]==year
                    records.append(dict(null=name,trial=trial+1,group=str(year),
                        admitted=int((admitted[trial]&mask).sum()),net_total=float(values[trial,mask].sum())))
    rows=pd.DataFrame(records)
    rows.to_csv(dest/'control_year_side_attribution.csv',index=False)
    summary=[]
    for (name,group),frame in rows.groupby(['null','group'],sort=False):
        summary.append(dict(null=name,group=group,net_p5=float(frame.net_total.quantile(.05)),
                            net_p50=float(frame.net_total.quantile(.5)),net_p95=float(frame.net_total.quantile(.95)),
                            trades_p50=float(frame.admitted.quantile(.5))))
    return summary


def render():
    d=study.OUT/'design';s=json.loads((d/'summary.json').read_text());n=s['nulls']
    actual=s['covered_baseline'];full=s['full_source_baseline']
    cat=pd.read_csv(d/'outcome_catalog.csv');sy=side_years(d,cat)
    out=['# Hourly R2 CHoCH: direction and timing controls; no promotion',
         f"Summary: The hourly two-candle CHoCH 1:2 foundation made ${actual['net_total']:,.2f}/MNQ on 408 resolved design trades, trade t={actual['trade_t']:.3f}. "
         f"Random-side p={n['RS']['p_profit']:.4f}; causal random-delay p={n['RD']['p_profit']:.4f}; neither clears the frozen .05 diagnostic threshold. "
         'The earlier-entry random-time counterfactual is explicitly noncausal and cannot be traded. The full-source unknown path and prior failures remain. No 2023+ validation, account benchmarks or promotion follow.',
         f"Plan [preregistration](../plans/choch_h1_r2_placebos_20261029.md), public commit `{s['preregistration_commit']}`; implementation commit `{s['implementation_commit']}`. "
         'Scripts: [catalog/study](../../../analysis/codex_choch_placebos.py), [path replay](../../../analysis/codex_choch_placebo_paths.py), [report](../../../analysis/codex_choch_placebo_report.py). '
         'Saved [summary](../../../analysis/outputs/codex_choch_placebos_20261029/design/summary.json) contains code/input hashes and dependency versions.',
         '## Fixed rule and costs',
         'NQ signal, one native MNQ: strict hourly swing confirmed by two completed candles on EACH side; causal core HH/HL/LH/LL trend and opposing-swing close break. '
         'Primary fill OPEN(signal+2), stop prior confirmed opposite swing, target twice fill-to-stop distance, one position, normal 09:00–14:00 CT signal hours/flatten OPEN of close-labelled 15:58; early 09:00/10:00/flatten OPEN 11:30. '
         '$2/point, $1.24 commission plus $1.00 slippage round trip = $2.24/trade. Gross 1:2 is not the realized payout of timed exits. '
         'Shared execution protects the entry bar, takes worse stop gaps and requires 1-point target-through. Entry beyond stop is charged immediate round trip. No altered side, swing or filter.',
         '## Coverage and baseline',
         'The original full source baseline is reproduced. For finite matched controls, the analysis uses sessions with all expected-open minutes 09:00 through planned liquidation observed. '
         'This is a future data-completeness research restriction, **not an executable entry filter or coverage-removal alpha**. Covered daily metrics use exactly complete cash-session dates, including complete no-event dates; full source retains its earlier weekday clock. '
         'Missing prior context still resets structure. Raw inputs are the same 11 hash-bound reconciled DAY/ON sources, 2017 warm-up and 2018–22 only. '
         'Close-labelled CT timestamps are the operating source assumption; exporter timestamp identity and continuous-contract roll identity remain independently unverified.',
         f"Coverage: `{s['coverage']}`.",
         table([dict(sample=x['model'],trades=x['trades'],net=x['net_total'],trade_t=x['trade_t'],NW5=x['daily_NW5'],Sharpe=x['sharpe'],Sortino=x['sortino'],PF=x['profit_factor'],Calmar=x['calmar'],Ulcer=x['ulcer'],maxDD=x['max_dd'],unknown=x['unresolved']) for x in [full,actual]],['sample','trades','net','trade_t','NW5','Sharpe','Sortino','PF','Calmar','Ulcer','maxDD','unknown']),
         'Full versus covered yearly totals:',
         table([dict(sample=x['model'],**{str(y['year']):y['net_mnq'] for y in x['years']}) for x in [full,actual]],['sample','2018','2019','2020','2021','2022']),
         'Full versus covered, both sides:',
         table([dict(sample=x['model'],side=z['side'],trades=z['trades'],net=z['net_total'],trade_t=z['trade_t'],win=z['win'],Sharpe=z['sharpe'],Sortino=z['sortino'],PF=z['profit_factor'],Calmar=z['calmar'],Ulcer=z['ulcer'],maxDD=z['max_dd']) for x in [full,actual] for z in x['sides']],['sample','side','trades','net','trade_t','win','Sharpe','Sortino','PF','Calmar','Ulcer','maxDD']),
         '## What each control tests',
         '**RS random side:** fair +/- side at the actual signal clock. Keep original potential-fill-to-swing risk distance and reflect the bracket at that fill; re-execute minute stop/target/time exits. '
         'This tests direction conditional on actual event dates/times/risk. The mirrored stop is a matched bracket, not a newly confirmed opposing swing.',
         '**RT random time:** uniform legal hours on the same actual event day, retaining original side/risk distance and translating the bracket around the new fill. '
         '**Earlier draws inherit information from a later actual signal. RT is a noncausal conditional counterfactual, not a tradable alternative or promotion placebo.** It also conditions on chosen days, so it cannot establish calendar-day selection.',
         '**RD random delay:** uniform actual hour or later legal hours, retaining side/risk and translated bracket. Original potential fill/risk is observed at the original fill clock before any later delayed fill. '
         'This is a causal post-signal delay benchmark, not unrestricted random-time trading.',
         'All original eligible events on audited sessions are supplied, not just previously admitted or profitable trades. '
         'SeedSequence 20261029 spawns independent RS/RT/RD streams; all 1,000 paths each are saved. Requests sort by scheduled entry, original signal and event ID; entries at/before the last exit are blocked, never retried. '
         'Thus realized trade counts/holding minutes may differ. Pending delayed requests may coexist, with one-position admission at their scheduled fills. '
         'The immutable outcome catalog plus chosen IDs/admission masks reconstructs each complete trade ledger; no best seed is selected.',
         '## Randomization results',
         f"Matched BASE net **${actual['net_total']:,.2f}**, DD **${actual['max_dd']:,.2f}**, {actual['trades']} trades. "
         'Primary p counts null net>=BASE in exact cents, includes ties, plus-one denominator 1001. DD p counts nullDD<=BASE; joint counts both. '
         'Quantiles describe the 1,000 finite-sample random paths; they do not represent 1,000 independent market histories.',
         table([dict(null=name,complete=n[name]['complete_paths'],null_net_p5=n[name]['quantiles']['net_total']['5'],null_net_p50=n[name]['quantiles']['net_total']['50'],null_net_p95=n[name]['quantiles']['net_total']['95'],profit_p=n[name]['p_profit'],DD_p=n[name]['p_dd'],joint_p=n[name]['p_joint'],profit_p19=n[name]['p_profit_19'],trades_p50=n[name]['quantiles']['admitted']['50'],minutes_p50=n[name]['quantiles']['exposure_minutes']['50']) for name in ['RS','RT','RD']],['null','complete','null_net_p5','null_net_p50','null_net_p95','profit_p','DD_p','joint_p','profit_p19','trades_p50','minutes_p50'])]
    out.append('Raw diagnostic threshold is p<=.05. Direction/causal-delay specificity requires RS AND RD each to pass; RT cannot establish a causal pass. '
        'Conservative 19p is only context for 16 prior inspected economic/control definitions plus these 3 fixed null questions. It is not the repo-wide promotion correction or a fresh holdout. '
        'There are no new promoted alpha definitions; 3,000 draws do not erase earlier selection or create independent histories.')
    out.append('Year/side null attribution (same path admissions; USD net quantiles):')
    out.append(table(sy,['null','group','net_p5','net_p50','net_p95','trades_p50']))
    out.append('## Execution, stresses and saved evidence')
    out.append(table([dict(null=name,stop_first_profit_p=n[name]['stop_first']['p_profit'],double_cost_net_p5=n[name]['quantiles']['extra_cost_net']['5'],double_cost_net_p50=n[name]['quantiles']['extra_cost_net']['50'],double_cost_net_p95=n[name]['quantiles']['extra_cost_net']['95'],unknown_paths=n[name]['unknown_paths']) for name in ['RS','RT','RD']],['null','stop_first_profit_p','double_cost_net_p5','double_cost_net_p50','double_cost_net_p95','unknown_paths']))
    out.append('Full catalog retains gross/commission/slippage/net, risk, stop/target, entry/exit, collisions and stop-first outcome. '
        'Every per-path CSV records the five metrics, t/NW5, counts, side exposure and earlier/equal/later admissions; compressed paths retain all choice IDs/masks/daily/stress increments. '
        'Daily sums reconcile to admitted trade cents. Source/session/clock audits, excluded sessions/trades and original full baseline remain saved. '
        'Synthetic checks cover shared-engine parity, exact risk reflection/translation, original-clock reconstruction, missing-risk propagation, early closes, one-position/tie/unknown bounds and integer-cent ranks. '
        'The shared minute collision assumption is stressed stop-first with identical draws; extra $2.24/trade is a cost stress, not a tuned rule.')
    out.append('All derived results, including full compact control ledgers, are in the [evidence archive](../../../analysis/outputs/codex_choch_placebos_20261029/evidence.zip); uploaded raw CSVs are excluded. '
        'Independent saved-artifact review is distinct from the fresh raw-spec financial checker required before promotion.')
    out.append('## Five plan homes and verdict')
    out.append(table([dict(home=home,verdict='No earned slot',limit=limit) for home,limit in [
        ('Personal19','Full foundation economic/data gates fail; no ADD/REPLACE/EMPTY or one-year plan MC run.'),
        ('50K funded','No current-book paired bootstrap; no payout/blow improvement established.'),
        ('150K funded','No current-book paired bootstrap; no payout/blow improvement established.'),
        ('50K evaluation','No valid current joint account-path comparison; no pass-rate improvement established.'),
        ('150K evaluation','No valid current joint account-path comparison; no pass-rate improvement established.')]],['home','verdict','limit']))
    out.append('Current adopted book/ranking sources are unchanged at the recorded Claude source snapshot; existing personal/funded/evaluation path and fee limitations remain. '
        'The null experiment cannot repair full-source t1.22, the unknown path, prior structural/filter selection, missing historical validation, dependence evidence or plan contribution. '
        'No 2023+ prices/returns, additional filters, account simulation, PowerLanguage or live/settings changes were authorized by these diagnostics or performed.')
    out.append('Verdict: finish this diagnostic and retain the foundation as unqualified research. A favorable conditional comparison alone cannot make it a plan candidate. '
        'For Claude: review `agents/codex/results/choch_h1_r2_placebos_20261029.md` with all saved controls and limitations.')
    path=study.ROOT/'agents/codex/results/choch_h1_r2_placebos_20261029.md'
    path.write_text('\n\n'.join(out)+'\n');print(path)


if __name__=='__main__':render()
