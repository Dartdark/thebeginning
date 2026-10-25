"""Verified report renderer for the fixed Overnight Rebound replication."""
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scratch_data/codex_deps'));sys.path.insert(0,str(ROOT/'analysis'))
import numpy as np
import pandas as pd
import codex_rebound_run as H
import resampling as R
OUT=H.OUT
money=lambda x:f'-${-x:,.2f}' if x<0 else f'${x:,.2f}'
num=lambda x:f'{x:.2f}'
pct=lambda x:f'{x:.1%}'
integer=lambda x:str(int(x))

def table(df,columns):
    lines=['| '+' | '.join(c[1] for c in columns)+' |','| '+' | '.join('---' for _ in columns)+' |']
    for _,r in df.iterrows():lines.append('| '+' | '.join(f(r[k]) for k,_,f in columns)+' |')
    return '\n'.join(lines)

def main():
    _,days,pc=H.setup()
    manifest=json.loads((OUT/'manifest.json').read_text())
    assert all(H.sha(ROOT/p)==v for p,v in manifest['hashes'].items())
    m=pd.read_csv(OUT/'metrics.csv');sig=pd.read_csv(OUT/'significance.csv');boot=pd.read_csv(OUT/'bootstrap.csv')
    nulls=pd.read_csv(OUT/'placebo_summary.csv');fil=pd.read_csv(OUT/'down_filter_summary.csv')
    risk=pd.read_csv(OUT/'native_daily_mc.csv');stress=pd.read_csv(OUT/'execution_stress.csv')
    assert nulls.unclosed.sum()==0 and (nulls.requested==nulls.closed).all()
    assert (nulls.runs==500).all() and fil.comparison_identifiable.all()
    personal=[];joint=[];contexts=[];author=[];sensitivity=[];portfolio_mc=[];replacements=[]
    personalroot=OUT/'personal19';personalroot.mkdir(exist_ok=True)
    (personalroot/'.gitignore').write_text('*.npy\n*.npz\nverification/\n',encoding='utf-8')
    for model in ['UNIFORM','SUNDAY2']:
        t=pd.read_csv(OUT/(model+'_trades.csv'),parse_dates=['date','exit_date','account_date'])
        np.testing.assert_allclose(t.pnl,(t.exit-t.entry)*20.,rtol=0,atol=1e-8)
        np.testing.assert_allclose(t.net,(t.pnl-17.25)*t.qty,rtol=0,atol=1e-8)
        assert np.isclose(H.daily(t,days).sum(),t.net.sum())
        whole=m[(m.model==model)&(m.period=='all')].iloc[0]
        assert len(t)==whole.trades and np.isclose(t.net.sum(),whole.total)
        a=t[t.account_date.between('2018-01-01','2026-07-31')]
        x=a.author_1dollar
        months=a.groupby(a.account_date.dt.to_period('M')).author_1dollar.sum().reindex(pd.period_range('2018-01','2026-07',freq='M'),fill_value=0.)
        author.append(dict(model=model,trades=len(a),contracts=float(a.qty.sum()),win=float(x.gt(0).mean()),
            total=float(x.sum()),annual=float(x.sum()/(len(months)/12)),pf=float(x[x>0].sum()/-x[x<0].sum()),
            average_win=float(x[x>0].mean()),average_loss=float(-x[x<0].mean()),worst=float(x.min()),
            worst_month=float(months.min()),dd=R.max_dd(H.daily(a,days[days<='2026-07-31'],col='author_1dollar')),
            mean_mae=float((a.mae*a.qty/10).mean()),max_mae=float((a.mae*a.qty/10).max()),
            time_exits=int(a.reason.eq('time').sum()),stop_exits=int(a.reason.eq('stop').sum()),safety_exits=int(a.reason.eq('safety').sum()),
            sunday_tickets=int(a.entry_et_dow.eq(0).sum())))
        for fee in ['1.24','1.04']:
            path=personalroot/model/('fee_'+fee)
            effects=pd.read_csv(path/'paired_effects.csv')
            z=effects[(effects.cohort=='2023_plus')&effects.config.str.endswith('__ADD')&effects.reference.str.endswith('__BASE')].copy()
            z['model']=model;z['fee']=float(fee)
            if fee=='1.24':
                personal.extend(z.to_dict('records'))
                j=pd.read_csv(path/'joint_losses.csv');j['model']=model;joint.extend(j.to_dict('records'))
                contexts.extend(json.loads((path/'account_context_limits.json').read_text())['contexts'])
                mc=pd.read_csv(path/'mc_summary.csv');mc=mc[(mc.cohort=='2023_plus')&mc.config.str.startswith('FULL__')].copy();mc['model']=model
                portfolio_mc.extend(mc.to_dict('records'))
                rep=effects[(effects.cohort=='2023_plus')&(effects.config=='FULL__REPLACE')&(effects.reference=='FULL__BASE')].copy();rep['model']=model
                replacements.extend(rep.to_dict('records'))
            else:sensitivity.extend(z[z.config=='FULL__ADD'].to_dict('records'))
            checks=json.loads((path/'saved_output_checks.json').read_text())
            assert checks['configurations']==20
            proof=json.loads((path/'manifest_update.json').read_text())
            assert proof['wrapper_sha256']==H.sha(ROOT/'analysis/codex_rebound_personal_update.py')
            assert proof['new_strategy_replays']==0
    a=pd.DataFrame(author);p=pd.DataFrame(personal);j=pd.DataFrame(joint)
    p['historical_ci']=p.apply(lambda r:f'[{money(r.historical_annual_mean_lo)}, {money(r.historical_annual_mean_hi)}]',axis=1)
    a.to_csv(OUT/'author_comparison.csv',index=False);p.to_csv(OUT/'personal_additions_compact.csv',index=False)
    assert len(contexts)==8 and all(not c['comparison_run'] for c in contexts)
    H.dump('report_checks.json',dict(primary_hashes_match=True,price_quantity_cost_daily_sums_match=True,
        all_null_signal_counts_reconciled=True,all_requested_plan_contexts_recorded=True,new_economic_models=3,
        prior_author_versions=336,personal_fee_sensitivity=sensitivity,report_script_sha256=H.sha(Path(__file__)),
        current_personal_snapshot='afde088',current_personal_legs=19,previous_17leg_outputs_preserved=True))
    g=m[(m.period.isin(['2018-22','2023+','all']))]
    yearly=m[m.period.str.fullmatch(r'20\d\d')]
    ci=boot[(boot.period=='2023+')&boot.metric.isin(['sharpe','max_dd','annual'])].copy()
    ci['interval']=ci.apply(lambda r:f'{r.p5:,.2f} to {r.p95:,.2f}',axis=1)
    sc=sig[(sig.period=='all')]
    fullp=p[p.config=='FULL__ADD'];u=fullp[fullp.model=='UNIFORM'].iloc[0];s=fullp[fullp.model=='SUNDAY2'].iloc[0]
    jf=j[j.group=='FULL']
    portfolio_mc=pd.DataFrame(portfolio_mc);replacements=pd.DataFrame(replacements)
    for model in ['UNIFORM','SUNDAY2']:
        b=portfolio_mc[(portfolio_mc.model==model)&(portfolio_mc.config=='FULL__BASE')].iloc[0]
        ad=portfolio_mc[(portfolio_mc.model==model)&(portfolio_mc.config=='FULL__ADD')].iloc[0]
        assert ad.median_profit_over_dd95<b.median_profit_over_dd95
    replacements['historical_ci']=replacements.apply(lambda r:f'[{money(r.historical_annual_mean_lo)}, {money(r.historical_annual_mean_hi)}]',axis=1)
    rr=risk[(risk.period=='2023+')&(risk.base_mnq==1)]
    columns=[('model','Model',str),('period','Period',str),('trades','Tickets',integer),('contracts','Contracts',integer),('win','Win',pct),
      ('avg','Net/ticket NQ',money),('t','t',num),('sharpe','Sharpe',num),('sortino','Sortino',num),('profit_factor','PF',num),
      ('calmar','Calmar',num),('ulcer','Ulcer',num),('max_dd','Closed EOD DD/NQ',money)]
    text=f'''# NQ Overnight Rebound: WATCH — profitable replication, no allocation recommendation

Summary: 1,004 source tickets; full PF 1.27 UNIFORM / 1.33 SUNDAY2, materially weaker than supplied claims.
Full t 2.59/2.90 fails the 3.61 ranked-item bar and 3.79 sensitivity for 336 author versions; direction is stronger than random, filter benefit unproven.
Current 19-leg personal ADD raises 2023+ mean annual profit by ${u.mean_profit_delta:,.0f}/${s.mean_profit_delta:,.0f}, but DD95 by ${u.dd95_delta:,.0f}/${s.dd95_delta:,.0f}; both reduce median profit/DD95.
All 50K/150K evaluation/funded comparisons are LIMITED by missing causal joint overnight baseline paths, not by legal calendar-date crossings.
821 unobserved held minutes, cache timing differences and absent original MC trades prevent exact parity. No live/ranking/allocation change.

Plan: [`overnight_rebound.md`](../plans/overnight_rebound.md), **{pc[:7]}** committed before new returns.
Models: UNIFORM down-day Qty1, source-default SUNDAY2, ALLNIGHTS unfiltered control (not selectable).
Prior search: author336 versions plus unknown filters. No new parameter grid or rescue optimization.
Scripts: `analysis/codex_rebound_run.py`, `codex_rebound_engine.py`, `codex_rebound_diagnostics.py`, `codex_rebound_accounts.py`, `codex_rebound_personal_update.py`, `codex_rebound_report.py`.
Source/snapshots: `agents/codex/inputs/rebound/`; outputs: `analysis/outputs/codex_rebound/`. Current19-leg baseline pinned toafde088 under committed refresh80fff8a; initial17-leg results ate1a94f7 are preserved.

## Rule and clock as replayed

Cash08:31-labeled open through15:00 close CT; arm if close<open, stop .5×cash high-low. First available close>=17:01 submits next-native-bar buy.
Normally17:02-labeled entry open and03:01-labeled next-bar exit open after03:00 decision. Friday down-day arming can enter Sunday; sourceSundayQty2
is determined by the raw ET chart date at submission. ET-display/-60 is normalized into CT; the CT cache is not shifted by another hour.
Uniform and Sunday2 have identical ticket/price paths; quantities and per-contract fees multiply exactly once. Long only; shorts0, metricsN/A.
Source08:31–15:00 safety exit retained. No new16:45ET or weekend cutoff was inserted, despite the prose's stronger guarantee.

Actual cache entry labels:543 at17:03,460 at17:02,1 at17:32. Those correspond to next-bar opens approximately one minute earlier.
Earlier history frequently has no17:01 native bar, causing the source to submit at17:02 and fill17:03. No missing bar/earlier price was fabricated.
Timing differences can affect the early/late-period comparison and claimed MC match. Known CT schedule is a declared proxy, not verified author-feed parity.
All three design2018–22 runs precede validation2023–October9,2026; previously inspected history is not fresh holdout.

## Results and costs

Per-unit NQ pays$7.25 RT plus1tick each entry/exit ($17.25 total), multiplied by actualqty. Native baseMNQ pays$1.24 RT plus$.50 eachfill;
$1.04 and author's$1 zero-slippage conventions remain separate. Source SUNDAY2 means1baseMNQ ordinary nights and2MNQ Sundays.
Tickets are distinct nights; summed contracts are not independent samples. Equity is booked to the actual17→16 account session.
Initial zero counts in drawdown, all/long are identical, and all dollar figures below use the stated NQ-cost model unless labeled otherwise.

{table(g,columns)}

{table(yearly,[('model','Model',str),('period','Year',str),('trades','Tickets',integer),('native_total','Native net/baseMNQ',money),('profit_factor','PF/NQ costs',num)])}

## Comparison with the supplied January2018–July2026 claims

Claimed uniform966tickets,55%wins,PF1.38,$2,240/year,DD$2,290 perMNQ; Sunday2PF1.44,$3,100/year,DD$3,020.
The separate mixed-size MC report claims966tickets,PF1.47,$275,430 net and$33,880 strategy DD per1NQ/Sunday2.
No report/trade export was supplied to verify its costs, intrabar assumptions or923shared-day/corr.97 claim.
Our same-calendar-window comparison below uses **the author's $1/baseMNQ RT and zero extra slippage**:

{table(a,[('model','Model',str),('trades','Tickets',integer),('contracts','Contracts',integer),('win','Win',pct),('pf','PF',num),
 ('annual','Net/year/baseMNQ',money),('dd','Closed EOD DD',money),('average_win','Avg win',money),('average_loss','Avg loss',money),
 ('worst','Worst ticket',money),('time_exits','Time exits',integer),('stop_exits','Stops',integer),('sunday_tickets','Sunday tickets',integer)])}

This does not reproduce966tickets or the claimed return strength. Closed equity DD and MC's open-position strategy DD are different quantities.
No return-selected time/price adjustment or deleted mismatch was used to force a match. Source entry/stop/time gap handling and unknown feed differences remain.

## Does the down-day filter add value?

ALLNIGHTS uses the same source stop/entry/exit but permits every valid cash session. Every down entry matches its all-night counterpart exactly.
Compare **total dollars**, not only per-trade PF:

{table(fil,[('period','Period',str),('down_tickets','Down nights',integer),('control_tickets','All nights',integer),('down_total','Down net/NQ',money),
 ('control_total','All-night net/NQ',money),('removed_total','Removed net/NQ',money),('removed_avg','Removed avg',money),('removed_t','Removed t',num),
 ('random_total_at_least_actual','Random keep >=down net',pct),('actual_jointly_beats_random_fraction','Down beats random on net+DD',pct)])}

The excluded up/flat nights are profitable overall (+$53,187/NQ, mean+$45,t1.06), so the required removed-trades-lose condition fails.
The down filter improves PF/average and lowers drawdown, but gives up profitable trades; net/DD advantage over random removal is not stable in both eras.
This is not proof that up nights have an independent edge, nor permission to adopt the all-night control. It weakens the filter's incremental claim.

{table(nulls,[('model','Model',str),('family','Fixed null',str),('actual_avg','Actual NQ/ticket',money),('null_avg','Null mean',money),('tail_at_least_actual','Null >=actual',pct)])}

500runs/family/model,502,000 closed signals each, no omitted nulls. Random-time evening entries use the cash signal already known before entry;
there is no future direction label. UNIFORM timing is not distinct from random evening times (p.257); SUNDAY2 timing p.044 is weak after prior search.
Long direction beats random side, consistent with overnight long beta/reversal rather than proof of these exact entry settings.

## Uncertainty and risk

{table(ci,[('model','Model',str),('metric','Metric',str),('actual','Actual',num),('interval','2023+90% block-bootstrap interval',str)])}

5,000 ten-session paths with initial-zero accounting; permutations/trade Monte Carlo saved separately.

{table(sc,[('model','Model',str),('scope','Trial scope',str),('trials','N',integer),('t','t',num),('t_threshold','Required t',num),('dsr','DSR',num)])}

Both versions fail the promotion bar, including the optimistic ranked-items-only comparison.336is a disclosed search count, not a clean preregistered
few-variant exception; additive sensitivity may double-count related work but still omits unknown rejected filters. No side or Sunday-only version was selected.
Validation remains profitable under4ticks perfill, but profitability under costs alone does not establish a new portfolio edge.

Standalone one-year EOD-trail illustrations at1baseMNQ (Sunday2 doubles Sunday quantity):

{table(rr,[('model','Model',str),('p_loss','P(losing year)',pct),('dd_p95','DD95',money),('p_trail_hit','P(hit$2k EODtrail)',pct)])}

These are not account pass/payout forecasts: no intraday breaches, DLL, joint positions or baseline chronology is modeled by this standalone illustration.
The20.0%/23.9%2023+trail-hit estimates are substantial at one base micro and do not support assuming high win rate means safe sizing.

## Data coverage and source verification

143 actual positions contain821 unobserved held minutes. None are in the audit's nominal16–17maintenance/weekend-closure windows;
the cause is unverified (no prints, omissions, restrictions/halts or feed gaps cannot be distinguished). Do not call them verified feed failures.
Largest ticket count289minutes is March16–17,2020; the observed exit is delayed to03:12 label. Longest contiguous gap is54minutes.
We retain all events, count gaps and fill stops at the next observed worse open when applicable; unobserved stop paths remain a limitation.
No actual closed trade crosses the15:59 daily deadline in this cache, and no terminal open position is fabricated closed.
Synthetic tests and independent code review pass, including Sunday quantity/ET calendar, entrybar stop, short-null gaps and explicit unclosed-nullIDs.
This is not an independent end-to-end raw-data replica or exact MC confirmation.

## Current personal portfolio and Apex placement

Current19-leg book andA–D starters pinned toafde088; no BB_MRM, with adopted SwingTargetv3 and PAPERTRENDv2. Model/base fees consistent at$1.24, with$1.04 sensitivity.
20fixed configurations: BASE/ADD/EMPTY/REPLACE for eachstarter andFULL. FULL replaces currentOvernightTick; starters replaceONBML.
The refreshed published19-leg baseline reconciles to about$41,475/year/$6,592 historicalDD at its own fee convention. A future intended aggressive
weighting is not silently assumed adopted. Existing OT excludes its roll-switch nights; in-hold continuous-contract-switch execution was not independently
verified for this literal Rebound source. No after-the-fact roll filter was selected.
All1004source nights are retained. Sundayqty multiplies raw unit-price P&L and contract fees exactly once.
1,000 paired252-session10-day bootstrap paths; historical annual-mean95%intervals below are different from90%standalone intervals.

{table(p,[('model','Model',str),('config','Addition',str),('mean_profit_delta','Mean annual increment',money),('historical_ci','95%historical mean CI',str),('dd95_delta','Change in DD95',money)])}

The refreshed2023+FULL outcomes at the common leg scale are:

{table(portfolio_mc,[('model','Model',str),('config','Allocation',str),('profit_mean','Mean annual profit',money),('dd_p95','DD95',money),('median_profit_over_dd95','Median profit/DD95',num)])}

{table(replacements,[('model','Model',str),('mean_profit_delta','OT-replacement annual increment',money),('historical_ci','95%historical mean CI',str),('dd95_delta','Change in DD95',money)])}

Higher modeled income buys more drawdown; there is no new statistical/promotion pass. Empty-slot controls are retained; replacement intervals
and risk tradeoffs must be read against both BASE and EMPTY, not interpreted as a proven new allocation. Original17-leg outputs remain under `personal/`.

{table(jf,[('model','Model',str),('correlation','All-history full-book daily corr',num),('joint_loss_days','Joint losing days',integer),('candidate_net_on_baseline_loss_days','Candidate net on book-loss days',money)])}

This is another NQ overnight long exposure, not a hedge. Its rebound arrives after the signal cash loss; it cannot rescue an account already breached
before entry. Existing personal booking/fee/day/Twin/MOC/S30 approximations remain, and OT data endsJuly7,2026. Source zeros afterward are not verified
no-trade activity. One legal Dec4→Dec5,2018night lacks a published personal-calendar row and is booked to the next published Dec6session by the inherited
helper; all money is retained and this mapping is logged. Daily portfolio risk/correlation is conditional on that published calendar.
After metadata/calendar review, all four original17-leg cases were repeated under the frozen adapter:28 financial CSVs hash-match.
The separate19-leg refresh freezes its wrapper/input hashes before all four new baseline-comparison runs; candidate daily paths remain unchanged.
The published new MC loader maps any pre-2018 exits to its first2018book row. That convention is preserved/logged for baseline parity;
the primary2023+comparison excludes that row. No new candidate strategy or market-return trial was introduced by either verification or refresh.

| Requested context | Result |
| --- | --- |
| 50K evaluation | LIMITED: existingBridge Sunday-night exposure is collapsed/omitted beforeMonday00:00; no valid joint overnight comparison |
| 150K evaluation | Same concrete chronology limit; no pass-rate claim inferred from50K |
| 50K funded | LIMITED: OT/CLS whole-day adverse proxies and omittedBridge night path cannot identify simultaneous overnight risk |
| 150K funded | Same joint-path limit; no payout/blown claim inferred from50K |
| PersonalA–D/FULL19 | Positive added dollars, higher DD; no allocation recommendation under significance/risk/parity limits |

Normal17→03 crosses calendar midnight inside one CME trading day under the current adopted OT-plan convention. It is **not** rejected merely for
crossing a date. Current-plan accounting is a simulation assumption, not new verification of broker rules. All eight model/Apex-context limits are saved;
we did not run an invalid account benchmark. Candidate821missing-price minutes independently limit intraday-risk precision.

## Research interpretation and decision

The literature is related, not exact validation. Liu's currently indexed result reverses **overnight** losers into the **intraday** window; Abdi studies
common stocks with additional conditioning. Bondarenko/Muravyev and Cliff/Cooper/Gulen support historical overnight timing/premium, not this NQ stop/filter.
Boyarchenko/Larsen/Whelan supplies the relevant inventory-pressure hypothesis. Their [July2026follow-up](https://libertystreeteconomics.newyorkfed.org/2026/07/the-disappearing-overnight-drift/)
reports that the narrow02–03ETdrift flattened after2020, includingNQ/YM. A broader conditional18–04rule can still be positive, but the older paper cannot
be used as current proof. Primarylinks and retrieval limits: [`overnight_rebound_source_review.md`](overnight_rebound_source_review.md).

**Keep out of the active allocations on this evidence.** The source has positive historical returns, but weaker replication, no multiple-testing pass,
unproven down-filter benefit and no clear personal return/DD improvement. The matching MC trade export/session settings would be the cheapest way
to investigate the price/timing gap; no new optimization grid or portfolio addition is justified now.
No live trading, VPS, broker/API settings, shared research caches, rankings or allocations changed.

Reproduce from repo root using the installed interpreter:

```powershell
$reboundPython = '{sys.executable}'
& $reboundPython -B analysis/codex_rebound_run.py --phase design
& $reboundPython -B analysis/codex_rebound_run.py --phase validation
& $reboundPython -B analysis/codex_rebound_diagnostics.py
foreach ($reboundModel in 'UNIFORM','SUNDAY2') {{
  foreach ($reboundFee in '1.24','1.04') {{
    & $reboundPython -B analysis/codex_rebound_accounts.py --personal --ledger "analysis/outputs/codex_rebound/${{reboundModel}}_trades.csv" --model $reboundModel --prereg d94d815 --fee $reboundFee
    & $reboundPython -B analysis/codex_rebound_personal_update.py --model $reboundModel --fee $reboundFee --amendment 80fff8a
  }}
}}
& $reboundPython -B analysis/codex_rebound_report.py
```

Claude review path: `agents/codex/results/overnight_rebound.md`.
'''
    (ROOT/'agents/codex/results/overnight_rebound.md').write_text(text,encoding='utf-8')
    print('Report verified and saved. No new economic return trials.')

if __name__=='__main__':main()
