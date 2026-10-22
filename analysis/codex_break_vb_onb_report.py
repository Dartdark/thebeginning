"""Tables, figure and review memo from the frozen VB/ONB stress outputs."""
import os
os.environ.setdefault('MPLCONFIGDIR','/tmp/codex_break_mpl')
import json
from importlib.metadata import version

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

import codex_break_vb_onb as B


def dollar(x):return ('-$' if x<0 else '$')+f'{abs(x):,.0f}'


def money_cents(x):return ('-$' if x<0 else '$')+f'{abs(x):,.2f}'


def main():
    out=B.OUT;m=pd.read_csv(out/'run_metrics.csv');f=pd.read_csv(out/'family_summary.csv')
    parity=json.loads((out/'baseline_parity.json').read_text());manifest=json.loads((out/'run_manifest.json').read_text())
    onb=m[(m.strategy=='ONB_ADX30')&(m.family=='baseline')]
    base=onb[onb.side=='all'].set_index('period');draws=pd.read_csv(out/'ONB_ADX30_jitter_draws.csv')
    accepted=draws[draws.accepted].copy();params=pd.json_normalize(accepted.parameters.map(json.loads))
    ranges=[]
    for k in params:
        ranges.append(dict(parameter=k,min=params[k].min(),max=params[k].max(),distinct=int(params[k].nunique())))
    pd.DataFrame(ranges).to_csv(out/'ONB_ADX30_jitter_input_ranges.csv',index=False)
    # Full period/side/year summaries from all retained runs, not selected winners.
    stress=m[m.family.ne('baseline')]
    side_summary=stress.groupby(['strategy','family','period','side']).agg(runs=('run','size'),
      median_net=('total','median'),median_avg=('avg','median'),median_t=('t','median'),median_sharpe=('sharpe','median'),
      median_sortino=('sortino','median'),median_pf=('profit_factor','median'),median_calmar=('calmar','median'),
      median_ulcer=('ulcer','median'),median_max_dd=('max_dd','median')).reset_index()
    side_summary.to_csv(out/'stress_side_year_summary.csv',index=False)
    deterministic=m[m.family.isin(['indicators','timing','execution'])&m.period.isin(['2018-22','2023+'])].copy()
    deterministic['below_third_base']=False
    for i,z in deterministic.iterrows():
        b=m[(m.strategy==z.strategy)&m.family.eq('baseline')&m.period.eq(z.period)&m.side.eq(z.side)].iloc[0]
        deterministic.loc[i,'below_third_base']=bool(z.total<=0 or z.sharpe<b.sharpe/3)
    deterministic.to_csv(out/'deterministic_dependency_checks.csv',index=False)
    noise=m[m.family.eq('noise')].copy();noise['sd_ticks']=noise.parameters.map(lambda s:json.loads(s)['sd_ticks'])
    noise_rows=[]
    for (sd,period,side),x in noise.groupby(['sd_ticks','period','side']):
        noise_rows.append(dict(sd_ticks=sd,period=period,side=side,runs=len(x),median_net=float(x.total.median()),
          median_avg=float(x.avg.median()),median_t=float(x.t.median()),median_sharpe=float(x.sharpe.median()),
          share_positive=float(x.total.gt(0).mean()),share_positive_t2=float((x.total.gt(0)&x.t.gt(2)).mean())))
    pd.DataFrame(noise_rows).to_csv(out/'noise_size_summary.csv',index=False)
    flags=deterministic[deterministic.below_third_base]
    whole_flags=flags[flags.side.eq('all')]
    flags.to_csv(out/'dependency_flags.csv',index=False)
    baseline_rows=[]
    for z in onb[onb.period.isin(['2018-22','2023+'])].itertuples():
        baseline_rows.append(f'| {z.period} | {z.side} | {z.trades} | {z.win:.1%} | {dollar(z.avg)} | {z.t:.2f} | {z.sharpe:.2f} | {z.sortino:.2f} | {z.profit_factor:.2f} | {z.calmar:.2f} | {z.ulcer:.2f} | {dollar(z.max_dd)} |')
    family_rows=[]
    for z in f.itertuples():
        family_rows.append(f'| {z.family} | {z.period} | {z.runs} | {dollar(z.median_total)} | {dollar(z.median_avg)} | {z.median_t:.2f} | {z.median_pf:.2f} | {z.median_sharpe:.2f} | {dollar(z.median_max_dd)} | {z.share_positive:.0%} | {z.share_positive_t2:.1%} | {z.share_positive_half_sharpe:.1%} | {z.verdict} |')
    years=onb[onb.period.str.fullmatch(r'20\d\d')].pivot(index='period',columns='side',values='total')
    year_rows=['| '+str(y)+' | '+' | '.join(dollar(years.loc[y,s]) for s in ['all','long','short'])+' |' for y in years.index]
    side_rows=[]
    for z in side_summary[side_summary.period.isin(['2018-22','2023+'])&side_summary.side.ne('all')].itertuples():
        side_rows.append(f'| {z.family} | {z.period} | {z.side} | {dollar(z.median_net)} | {z.median_t:.2f} | {z.median_sharpe:.2f} | {z.median_pf:.2f} | {dollar(z.median_max_dd)} |')
    jitter23=m[m.family.eq('jitter')&m.period.eq('2023+')&m.side.eq('all')]
    jitter18=m[m.family.eq('jitter')&m.period.eq('2018-22')&m.side.eq('all')]
    s23=f[f.family.eq('jitter')&f.period.eq('2023+')].iloc[0]
    noise_small=pd.DataFrame(noise_rows);noise_size_rows=[]
    for z in noise_small[noise_small.period.isin(['2018-22','2023+'])&noise_small.side.eq('all')].itertuples():
        noise_size_rows.append(f'| {z.sd_ticks} ticks | {z.period} | {z.runs} | {dollar(z.median_net)} | {z.median_sharpe:.2f} | {z.share_positive_t2:.0%} |')
    target=pd.read_csv(out/'VB_mc_target_bar_diagnostic.csv')
    vb=parity['VB'];ob=parity['ONB_ADX30']
    vbb=m[m.strategy.eq('VB')&m.family.eq('baseline')&m.side.eq('all')&m.period.isin(['2018-22','2023+'])]
    vb_rows=[f'| {z.period} | {z.trades} | {dollar(z.avg)} | {z.t:.2f} | {z.sharpe:.2f} | {dollar(z.total)} |' for z in vbb.itertuples()]
    unmatched_onb=pd.read_csv(out/'ONB_ADX30_baseline_pairing.csv')
    onb_py_dates=', '.join(unmatched_onb.loc[unmatched_onb._merge.eq('left_only'),'date'].astype(str))
    onb_mc_dates=', '.join(unmatched_onb.loc[unmatched_onb._merge.eq('right_only'),'date'].astype(str))
    # One chart: distributions across specified perturbations; these are not sampling CIs.
    families=['noise','indicators','timing','jitter','execution']
    fig,axes=plt.subplots(1,2,figsize=(12,4.8),sharey=True)
    for ax,period in zip(axes,['2018-22','2023+']):
        arrays=[m[m.family.eq(fam)&m.period.eq(period)&m.side.eq('all')].sharpe.to_numpy() for fam in families]
        ax.boxplot(arrays,tick_labels=families,showfliers=True,flierprops={'markersize':2,'alpha':.35})
        sr=base.loc[period,'sharpe']
        ax.axhline(sr,color='#264673',lw=1.2,label='Baseline')
        ax.axhline(sr/2,color='#ba8b14',ls='--',lw=1,label='Half baseline')
        ax.axhline(sr/3,color='#ae4141',ls=':',lw=1,label='Third baseline')
        ax.axhline(0,color='gray',lw=.5);ax.set_title('ONB ADX30 '+period);ax.grid(axis='y',alpha=.2)
        ax.tick_params(axis='x',rotation=20)
    axes[0].set_ylabel('Daily Sharpe across frozen stress runs');axes[1].legend(frameon=False,fontsize=8)
    fig.suptitle('Parameter jitter weakens recent results; no replacement setting selected',fontsize=12)
    fig.tight_layout();fig.savefig(out/'ONB_stress_distributions.png',dpi=160);plt.close(fig)
    boot=pd.read_csv(out/'ONB_ADX30_baseline_bootstrap.csv');ci=boot[boot.side.eq('all')&boot.metric.eq('sharpe')].iloc[0]
    td=m[m.family.eq('timing')&m.run.eq('entry_one_bar_later')&m.side.eq('all')].set_index('period')
    typed_checks=json.loads((out/'engineering_checks.json').read_text())
    # Numerical jitter associations are not a one-at-a-time causal test. Save distributions without selecting inputs.
    report=f'''# Break tests: WATCH — ONB parameter sensitivity; Vault Break reproduction blocked

Summary: ONB ADX30 bends under price noise, indicator swaps, timing shifts and execution friction; joint jitter is MIXED.
For 2023+, jitter median Sharpe is {s23.median_sharpe:.2f} versus {base.loc['2023+','sharpe']:.2f} baseline; {s23.share_positive:.0%} stay profitable but only {s23.share_positive_half_sharpe:.0%} retain half the baseline Sharpe.
Vault Break fails the frozen reproduction gate: {vb['matched']:,}/{vb['mc_trades']:,} reference entries match ({vb['matched']/vb['mc_trades']:.2%}); its stress runs were stopped.
Completed {manifest['mechanical_runs']} mechanical runs: two baselines plus ONB's 314 fixed stress runs; no optimization or selected replacement.
No trading-plan, live, MultiCharts, VPS or account changes. These results require Claude's review.

Plan: [`break_vb_onb.md`](../plans/break_vb_onb.md), **109a752 committed before any baseline/test result**.
Task snapshot: `ece20f05bd8bac31424d10fc04e0e858f288c28e`; copied task under `agents/codex/inputs/break_vb_onb/`.
Scripts: `analysis/codex_break_vb_onb.py`, `analysis/codex_break_vb_onb_report.py`.
Output: `analysis/outputs/codex_break_vb_onb/`. Two registered robustness trials: ONB complete, VB stopped at parity.
Originally planned 630 total runs; 314 VB stress runs were not run. No best settings or new strategies were selected.

## Rule and frozen decision

VB: midnight noise/VWAP breakout, ATR 15 SMA, noise 0.30, 10:00–14:30 decisions, target 40 / stop 75 points, up to 3/day.
ONB evaluation: 23:00–08:30 range, top/bottom-third bias, 08:30–08:45 opening-range stop entry, ADX 14 > 30,
ATR 15 SMA stop 0.25 and 3R target, one/day, flat 14:30; reviewed holiday times. Fixed one NQ throughout.
Round-trip costs $7.25 plus one tick for each market/stop fill; target exits carry no extra slippage. Targets require
one point of trade-through. Stress execution cases extend costs/through-price exactly as preregistered.

Each family **BENDS** only when more than half its runs simultaneously stay profitable and retain at least half
that period's base Sharpe in **both 2018–22 and 2023+**. It **BREAKS** if median net<=0 or median Sharpe<third of base
in each period. Otherwise MIXED/WATCH. Overall ONB is **MIXED/WATCH** because joint jitter fails BENDS for 2023+;
no family satisfies the stronger BREAKS rule. A successful family is not proof of an enduring edge.

## Baseline reproduction gate

Both accelerated implementations reproduce their named original candidate functions trade by trade within numerical
tolerance. That is separate from matching MultiCharts. Matched keys are date/side/entry chart bar, with no fuzzy
day-only match; unmatched records remain in `*_baseline_pairing.csv`.

| Strategy | Python / MC on report overlap | Matched entries | Entries within one tick | Gross P&L within $20 | Gross correlation | Mean-net difference | Gate |
|---|---:|---:|---:|---:|---:|---:|---|
| VB | {vb['py_trades']} / {vb['mc_trades']} | {vb['matched']} | {vb['entry_within_tick']:.1%} | {vb['gross_within20']:.2%} | {vb['gross_corr']:.4f} | {money_cents(vb['mean_net_difference'])} | FAIL: matched fraction of MC below 98% |
| ONB_ADX30 | {ob['py_trades']} / {ob['mc_trades']} | {ob['matched']} | {ob['entry_within_tick']:.1%} | {ob['gross_within20']:.2%} | {ob['gross_corr']:.4f} | {money_cents(ob['mean_net_difference'])} | PASS |

Tolerance gates were frozen before testing: >=98% matching each list, >=99% entry-price agreement, >=95% gross
P&L agreement within $20, correlation>=.98 and mean-net gap <=max($20,10% of MC mean). Entry-price, gross-tolerance and correlation
columns use common entries; mean-net differences use the complete overlapping lists. Matching fractions include
all reference/replica entries in the overlap.
VB's full 2018–26 candidate has 1,742 trades; its report-overlap comparison excludes early warm-up entries before
the report's January 25, 2018 11:00 start. ONB comparison uses the supplied ADX30/.25 report, not ADX20 or funded ML.

ONB unmatched dates: Python-only **{onb_py_dates}**; MC-only **{onb_mc_dates}**. These rows remain in the evidence.

VB target diagnostic: {int((~target.through1_present).sum())} of {len(target)} MultiCharts target exits have an observed
reported exit-bar high below target+one point in the owned minute data. On 2018-04-17, the first target was 6832.50,
the MC exit bar ended 13:30 with an observed high 6833.25, and the Python one-point-through model exited later.
That can change later re-entry opportunities even when the first trade's profit is the same. This identifies an
execution/data-reconciliation issue; it does **not** establish a replacement fill threshold or explain every unmatched
trade. Source-data differences, report assumptions and the actual MC fill convention need checking. No threshold was
changed to make the gate pass. VB gets **PARITY FAIL / inconclusive stress evidence**, not an economic-edge failure.

For transparency, the unvalidated VB Python baseline only:

| Period | Trades | Net/NQ trade | t | Daily Sharpe | Total net/NQ |
|---|---:|---:|---:|---:|---:|
{chr(10).join(vb_rows)}

All VB side/year metrics remain in `run_metrics.csv`; shorts are N/A because VB is long-only. No VB stress family
verdict is invented. Resolving its fill parity is the prerequisite to completing that audit, under the original gate.

## ONB baseline results

Per fixed one NQ, after costs. Daily risk metrics use intraday closed P&L on the full available trading calendar;
an initial zero observation ensures the first loss counts in drawdown. $50k is only the Ulcer reporting denominator,
not a capital recommendation or the variable RiskPerTrade 1100 MNQ deployment. Full2018–26 and year/side tables are saved.

| Period | Side | Trades | Win | Net/trade | t | Sharpe | Sortino | PF | Calmar | Ulcer | Max DD |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
{chr(10).join(baseline_rows)}

| Year | All net/NQ | Longs | Shorts |
|---|---:|---:|---:|
{chr(10).join(year_rows)}

## ONB stress families

Medians across every predeclared run; net totals and means are per fixed NQ. Positive+t>2 and positive+half-Sharpe
are separate diagnostic shares. Per-run trade-t is not a new promotion test, and draw/seed outcomes are correlated.

| Family | Period | Runs | Median total | Median net/trade | Median t | Median PF | Median Sharpe | Median max DD | Net>0 | Net>0 & t>2 | Net>0 & half Sharpe | Verdict |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
{chr(10).join(family_rows)}

![ONB distributions across frozen stress runs](../../../analysis/outputs/codex_break_vb_onb/ONB_stress_distributions.png)

The boxes show variation across specified scenarios, not confidence intervals or independent samples.
Noise broken out by its two predeclared sizes:

| Noise SD | Period | Seeds | Median total | Median Sharpe | Positive & t>2 |
|---|---|---:|---:|---:|---:|
{chr(10).join(noise_size_rows)}

Indicator runs were ATR 10/20 SMA, ATR 10/15/20 Wilder and OR ending 09:00 with the actual 08:30 open retained.
Timing runs were entry delayed 15m, flat 15m earlier and flat 15m later. The delayed-entry version remains positive:
net/trade {dollar(td.loc['2018-22','avg'])} / {dollar(td.loc['2023+','avg'])}, Sharpe {td.loc['2018-22','sharpe']:.2f} /
{td.loc['2023+','sharpe']:.2f} across the two periods. This is a historical robustness perturbation, not a recommendation
to change the live entry. All execution cases—including 3-tick market/stop slippage and 2-point target-through—remain
positive and retain half base Sharpe in both periods.

## Jitter, side risks and dependency flags

Exactly 200 feasible simultaneous ±10% perturbations were evaluated. Raw draws: {len(draws)}; infeasible before any
return evaluation: {len(draws)-len(accepted)}. Their original factors, proposed parameters and rejection reasons are saved
in `ONB_ADX30_jitter_draws.csv`. Constraints are chronological/calendar feasibility, not profitability. Conditioning on
those constraints makes retained parameters dependent. Clocks were multiplied in elapsed minutes, snapped to 15m,
and capped before 15:59 / holiday 11:45. The previous-day overnight start stayed on an unwrapped axis, including
post-midnight starts correctly. Native bar size, boolean holiday handling and fixed-unit sizing stayed unchanged.

Design jitter: {int(jitter18.total.gt(0).sum())}/{len(jitter18)} profitable. Recent jitter:
{int(jitter23.total.gt(0).sum())}/{len(jitter23)} profitable, {int((jitter23.total.gt(0)&jitter23.t.gt(2)).sum())}/{len(jitter23)}
positive with t>2; only {int((jitter23.total.gt(0)&jitter23.sharpe.ge(base.loc['2023+','sharpe']/2)).sum())}/{len(jitter23)}
positive with half base Sharpe. Recent median drawdown rises from baseline {dollar(base.loc['2023+','max_dd'])} to
{dollar(s23.median_max_dd)} per NQ. Joint specification changes materially weaken recent risk-adjusted results.
The frozen numeric-clock jitter is broad: accepted overnight-end times range from 07:45 to 09:15, OR-end times from
08:00 to 09:30, and regular flat times from 13:00 to 15:45. Overnight start ranges from the preceding 20:45 to
current-day 01:15. These alter the traded session substantially; this result does not establish fragility to a tiny
implementation error. Actual input ranges are retained below and in the CSV.
This does not isolate a single causal parameter; no post-hoc OAT rescue or preferred jitter draw was tested.

Whole-strategy deterministic settings flagged at loss or below one-third base Sharpe: **{len(whole_flags)}**.
Side-specific flagged rows: **{len(flags[flags.side.ne('all')])}**; every check is saved in
`deterministic_dependency_checks.csv` / `dependency_flags.csv`. No isolated deterministic swap in the registered set
was necessary to keep the whole ONB profitable, but that does not erase the joint-jitter weakness.
`ONB_ADX30_jitter_input_ranges.csv` records actual distinct values after rounding; e.g. structural EntryBufTicks 2,
RiskPerTrade 0 and fixed one-contract units were not transformed into new sizing or live-buffer strategies.

| Family | Period | Side | Median total | Median t | Median Sharpe | Median PF | Median max DD |
|---|---|---|---:|---:|---:|---:|---:|
{chr(10).join(side_rows)}

Full Sortino, Calmar, Ulcer, win rates and all individual side/year results are in `run_metrics.csv`; grouped
side/year medians are in `stress_side_year_summary.csv`. Long/short diagnostics do not select a new side-only rule.

## Controls, uncertainty and account applicability

Master seed 8675309, all 100 price-noise realizations and 200 accepted jitter settings retained. Noise is independent
across minute OHLC fields before tick rounding and OHLC projection; volume/NaN masks stay fixed. Both indicators
and fills use the perturbed prices. ATR/Wilder use completed past weekday ranges, including explicit first-n seeding.
Noise scenarios are an artificial stress model, not a claim about actual market-data measurement error.

ONB 2023+ baseline 10-session-block bootstrap 90% Sharpe interval [{ci.p5:.2f}, {ci.p95:.2f}]; all/long/short intervals and
drawdown permutations are saved. Those describe uncertainty conditional on this history. The 2023+ sample has been
seen repeatedly in prior research; these stress results are historical sensitivity, not fresh validation. No new
entry-time/random-side placebo or funded addition/replacement bench was run for this unchanged-strategy audit.
No account-size, payout, broker-margin or blow-up conclusion follows from fixed-one-NQ metrics. Two copied live
account orders would not be independent market evidence; this audit does not use those execution rows as a sample.

## Implementation verification and limits

All {len(typed_checks)} engineering checks pass: native-bar delay activation, no late delayed entry, extended OR using both
completed bars, future OR extrema excluded, Wilder seed/past-only availability, repeatable OHLC-valid noise and jitter
clock constraints. Accelerators were compared with the named original generators before stress runs; matching a
candidate is not the same as passing the independent MC gate. No stress was run before plan 109a752.
The early first implementation stopped on JSON serialization of a NumPy boolean after computing baselines; that
serialization defect was fixed before any stress results. No gate, signal or parameter definition changed afterward.

The configured `scratch_data/g24.pkl` was reused read-only and checked against owned day/night CSV observations;
cache/source hashes, observed span and matched input row count are in `input_manifest.json`. Data ends 2026-10-09.
Warm-up starts 2017-12-01 with the existing overnight observations; the new 2017 daytime export was not needed for
ONB's close baseline match. No shared cache, data file or source strategy was rebuilt/overwritten. Continuous-contract
provenance, holiday/provider differences and minute OHLC path assumptions remain limits. ONB's source candidate
also retains the repository's entry-minute stop/target convention; this is not an independent tick-engine audit.
Current live market-fallback/entry-buffer/rejection guards are outside the historical report/candidate comparison.

## Reproduction and review

```bash
/workspace/venvs/thebeginning/bin/python analysis/codex_break_vb_onb.py
/workspace/venvs/thebeginning/bin/python analysis/codex_break_vb_onb_report.py
```

All tested seeds/settings, raw infeasible draws, per-run metrics, parity pairs, diagnostics, source/code hashes and
package versions are committed. No PowerLanguage code, trading plan, live/VPS file, account or ranked list changed.
The outcome is an evidence report: ONB MIXED/WATCH; VB reproduction blocked. Resolving VB parity requires source/
execution review, not loosening the frozen gate or silently choosing a better fill threshold.

Tell Claude: review `agents/codex/results/break_vb_onb.md`, especially the VB target-fill discrepancy and ONB's weaker
2023+ simultaneous-parameter-jitter distribution; no live or plan action has been taken.
'''
    (B.ROOT/'agents/codex/results/break_vb_onb.md').write_text(report)
    dependencies=['analysis/codex_break_vb_onb.py','analysis/codex_break_vb_onb_report.py','analysis/candidates24.py',
      'analysis/candidates.py','analysis/grid24.py','analysis/grid.py','analysis/portfolio.py','analysis/param_clusters.py',
      'analysis/metrics.py','analysis/resampling.py','agents/codex/plans/break_vb_onb.md']
    repro=dict(plan_commit='109a752',task_source_commit='ece20f05bd8bac31424d10fc04e0e858f288c28e',
      mechanical_runs=manifest['mechanical_runs'],robustness_trials=2,VB_stress_runs=0,ONB_stress_runs=314,
      versions={p:version(p) for p in ['numpy','pandas','numba','openpyxl','scipy','scikit-learn']},
      code_sha256={p:B.sha(B.ROOT/p) for p in dependencies},live_changes=False,trading_plan_changes=False)
    (out/'reproduction.json').write_text(json.dumps(repro,indent=2)+'\n')
    print('Report written; ONB MIXED/WATCH, VB PARITY FAIL; no changes selected')


if __name__=='__main__':main()
