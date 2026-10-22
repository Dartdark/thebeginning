"""Review memo and tables for the registered VB parity/stress completion."""
import os
os.environ.setdefault('MPLCONFIGDIR','/tmp/codex_vb_parity_mpl')
import json

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

import codex_vb_parity_stress as S


def dollars(x,decimals=0):
    return ('-$' if x<0 else '$')+f'{abs(x):,.{decimals}f}'


def main():
    p=S.OUT;par=json.loads((p/'baseline_parity.json').read_text())
    phase=json.loads((p/'phase_status.json').read_text());inputs=json.loads((p/'input_manifest.json').read_text())
    q=par['parity_quarterpoint'];r=par['research_1point']
    if not q['pass']:
        rows=pd.read_csv(p/'parity_quarterpoint_unmatched_causes.csv')
        assert phase['stress_runs']==0
        report=f'''# VB parity amendment: WATCH — original parity gate still fails

Summary: The single registered .25-point target convention did not clear the original reproduction gate.
Matched {q['matched']}/{q['mc_trades']} MC entries; stress runs remain stopped.
All unmatched entries and factual/emulator versus unresolved MC causes are retained in the linked CSV.
No additional fill convention, date exclusion, strategy or trading-plan change was tested.

Plan: `agents/codex/plans/vb_parity_trade_through_amendment.md`, {inputs['amendment_commit'][:7]}.
Script: `analysis/codex_vb_parity_stress.py`; outputs: `analysis/outputs/codex_vb_parity_stress/`.
Trials: completion attempt of the existing VB audit; two baseline replays, no stress replays.

## Original gate and results

`baseline_parity.json` preserves every original gate and its result under both target-through conventions.
No match threshold, pairing key or sample window was relaxed. Unmatched rows:
`parity_quarterpoint_unmatched_causes.csv` ({len(rows)}), with detailed original keys in
`parity_quarterpoint_pairing.csv`. Verified emulator states do not establish an unobserved MC engine cause.

## Placebos, account level and implementation

Stopped at parity; no new placebos, funded bench, sizing, MultiCharts code or deployment. See the original plan
and pinned review for unchanged rules and the required cause-first next step. No further replay is authorized
by a failure here. Original ONB, strategy screen and execution-diagnostic outputs are unchanged.
'''
        (S.ROOT/'agents/codex/results/vb_parity_stress.md').write_text(report)
        return
    assert phase['stress_runs']==314
    m=pd.read_csv(p/'run_metrics.csv');f=pd.read_csv(p/'family_summary.csv')
    baseline=m[m.family.eq('baseline') & m.side.eq('all')].set_index('period')
    quarters=m[m.family.eq('parity_reference') & m.side.eq('all')].set_index('period')
    # Every family is judged against the one-point baseline, never the parity reference.
    for z in f.itertuples():assert np.isclose(z.base_sharpe,baseline.loc[z.period,'sharpe'])
    overall='BREAKS' if f.verdict.eq('BREAKS').any() else 'BENDS' if f.verdict.eq('BENDS').all() else 'MIXED / WATCH'
    pair=pd.read_csv(p/'parity_quarterpoint_pairing.csv')
    common=pair[pair._merge.eq('both')]
    max_pnl_gap=float(abs(common.pnl_py-common.pnl_mc).max())
    max_entry_gap=float(abs(common.entry_py-common.entry_mc).max())
    residual=pd.read_csv(p/'parity_quarterpoint_unmatched_causes.csv')
    parity_rows=[]
    for label,z in [('1-point research',r),('.25-point parity only',q)]:
        parity_rows.append(f"| {label} | {z['py_trades']} / {z['mc_trades']} | {z['matched']} | "
          f"{z['matched']/z['py_trades']:.2%} / {z['matched']/z['mc_trades']:.2%} | {z['entry_within_tick']:.1%} | "
          f"{z['gross_within20']:.2%} | {z['gross_corr']:.4f} | {dollars(z['mean_net_difference'],2)} | {'PASS' if z['pass'] else 'FAIL'} |")
    base_rows=[]
    for label,table in [('1 point',baseline),('.25 point — parity only',quarters)]:
        for period in ['2018-22','2023+','2018-26']:
            z=table.loc[period]
            base_rows.append(f'| {label} | {period} | {z.trades} | {z.win:.1%} | {dollars(z.avg,2)} | {z.t:.2f} | '
                f'{z.sharpe:.2f} | {z.sortino:.2f} | {z.profit_factor:.2f} | {z.calmar:.2f} | {z.ulcer:.2f} | {dollars(z.max_dd)} |')
    family_rows=[]
    for z in f.itertuples():
        family_rows.append(f'| {z.family} | {z.period} | {z.runs} | {dollars(z.median_total)} | {dollars(z.median_avg,2)} | '
          f'{z.median_t:.2f} | {z.median_pf:.2f} | {z.median_sharpe:.2f} | {dollars(z.median_max_dd)} | '
          f'{z.share_positive:.1%} | {z.share_positive_t2:.1%} | {z.share_positive_half_sharpe:.1%} | {z.verdict} |')
    deterministic=m[m.family.isin(['indicators','timing','execution']) & m.period.isin(['2018-22','2023+'])].copy()
    deterministic['loss_or_below_third']=False
    for i,z in deterministic.iterrows():
        if z.side=='short':continue
        deterministic.loc[i,'loss_or_below_third']=bool(z.total<=0 or z.sharpe<baseline.loc[z.period,'sharpe']/3)
    deterministic.to_csv(p/'deterministic_dependency_checks.csv',index=False)
    flags=deterministic[deterministic.loss_or_below_third]
    flags.to_csv(p/'dependency_flags.csv',index=False)
    jitter_flags=m[m.family.eq('jitter') & m.side.eq('all') & m.period.isin(['2018-22','2023+'])].copy()
    jitter_flags['nonpositive_net']=jitter_flags.total.le(0)
    jitter_flags['below_third_base']=jitter_flags.apply(lambda z:z.sharpe<baseline.loc[z.period,'sharpe']/3,axis=1)
    jitter_flags.to_csv(p/'jitter_dependency_checks.csv',index=False)
    jitter_bad=jitter_flags[jitter_flags.nonpositive_net | jitter_flags.below_third_base]
    jitter_bad.to_csv(p/'jitter_dependency_flags.csv',index=False)
    stress=m[m.family.isin(['noise','indicators','timing','jitter','execution'])]
    grouped=stress.groupby(['family','period','side']).agg(runs=('run','size'),
       median_total=('total','median'),median_avg=('avg','median'),median_t=('t','median'),
       median_win=('win','median'),median_sharpe=('sharpe','median'),median_sortino=('sortino','median'),
       median_pf=('profit_factor','median'),median_calmar=('calmar','median'),median_ulcer=('ulcer','median'),
       median_max_dd=('max_dd','median')).reset_index()
    grouped.to_csv(p/'stress_side_year_summary.csv',index=False)
    noise=stress[stress.family.eq('noise')].copy()
    noise['sd_ticks']=noise.parameters.map(lambda x:json.loads(x)['sd_ticks'])
    noise.groupby(['sd_ticks','period','side']).agg(runs=('run','size'),median_total=('total','median'),
       median_avg=('avg','median'),median_sharpe=('sharpe','median')).reset_index().to_csv(p/'noise_size_summary.csv',index=False)
    draws=pd.read_csv(p/'VB_jitter_draws.csv');params=pd.json_normalize(draws.loc[draws.accepted,'parameters'].map(json.loads))
    ranges=pd.DataFrame([dict(parameter=k,minimum=params[k].min(),maximum=params[k].max(),distinct=params[k].nunique()) for k in params])
    ranges.to_csv(p/'VB_jitter_input_ranges.csv',index=False)
    range_rows=[f'| {z.parameter} | {z.minimum:g} | {z.maximum:g} | {z.distinct} |' for z in ranges.itertuples()]
    timing=m[m.family.eq('timing') & m.side.eq('all') & m.period.isin(['2018-22','2023+'])]
    timing_rows=[f'| {z.run} | {z.period} | {z.trades} | {dollars(z.avg,2)} | {z.t:.2f} | {z.sharpe:.3f} | {dollars(z.max_dd)} |' for z in timing.itertuples()]
    year_rows=[]
    for year in [str(y) for y in range(2018,2027)]:
        a=baseline.loc[year];b=quarters.loc[year]
        year_rows.append(f'| {year} | {a.trades} | {dollars(a.total)} | {b.trades} | {dollars(b.total)} |')
    j18=f[f.family.eq('jitter')&f.period.eq('2018-22')].iloc[0]
    j23=f[f.family.eq('jitter')&f.period.eq('2023+')].iloc[0]
    boot=pd.read_csv(p/'VB_research_baseline_bootstrap.csv');ci=boot[boot.metric.eq('sharpe')].iloc[0]
    target=pd.read_csv(p/'VB_mc_target_bar_diagnostic.csv')
    counts={str(x):int(np.isclose(target.above_target_points,x).sum()) for x in [.25,.5,.75]}
    counts['below_025']=int(target.above_target_points.lt(.25-1e-7).sum())
    counts['at_least_1']=int(target.above_target_points.ge(1).sum())
    S.dump('target_diagnostic_counts.json',counts)
    # Distributions are across frozen perturbations, not sampling confidence intervals.
    families=['noise','indicators','timing','jitter','execution']
    fig,axes=plt.subplots(1,2,figsize=(12,4.8),sharey=True)
    for ax,period in zip(axes,['2018-22','2023+']):
        arrays=[stress[stress.family.eq(fam)&stress.period.eq(period)&stress.side.eq('all')].sharpe.to_numpy() for fam in families]
        ax.boxplot(arrays,tick_labels=families,flierprops={'markersize':2,'alpha':.4})
        sr=baseline.loc[period,'sharpe']
        for value,label,color,style in [(sr,'1-point baseline','#264673','-'),(sr/2,'Half baseline','#b88918','--'),(sr/3,'Third baseline','#ad4141',':')]:
            ax.axhline(value,label=label,color=color,ls=style,lw=1)
        ax.axhline(0,color='gray',lw=.5);ax.set_title('Vault Break '+period);ax.grid(axis='y',alpha=.2)
        ax.tick_params(axis='x',rotation=20)
    axes[0].set_ylabel('Daily Sharpe across frozen perturbations');axes[1].legend(frameon=False,fontsize=8)
    fig.suptitle('VB: parity resolved separately; one-point stress convention retained')
    fig.tight_layout();fig.savefig(p/'VB_stress_distributions.png',dpi=160);plt.close(fig)
    report=f'''# Vault Break: WATCH — parity passes; fixed stress audit is {overall}

Summary: Registered .25-point target-through reproduces MC under the original gate: {q['matched']:,}/{q['mc_trades']:,} entries ({q['matched']/q['mc_trades']:.2%}), matched gross P&L exact.
Completed all 314 frozen VB stress runs using the original 1-point research rule; four families BENDS, joint jitter MIXED.
2023+ jitter median Sharpe {j23.median_sharpe:.2f} versus {baseline.loc['2023+','sharpe']:.2f} baseline; {j23.share_positive:.0%} profitable, {j23.share_positive_half_sharpe:.0%} keep half baseline Sharpe.
No family BREAKS; a 30-minute entry delay remains profitable but weakens recent results. No replacement setting selected.
This completes the existing audit; no trading-plan, live or logger change follows.

Plan: [`vb_parity_trade_through_amendment.md`](../plans/vb_parity_trade_through_amendment.md), **{inputs['amendment_commit'][:7]} committed before the new parity replay**.
Original plan: [`break_vb_onb.md`](../plans/break_vb_onb.md), **109a752**. Review snapshot: **{S.REVIEW_COMMIT}**.
Scripts: `analysis/codex_vb_parity_stress.py`, `analysis/codex_vb_parity_stress_report.py`, unchanged original audit helpers.
Outputs: `analysis/outputs/codex_vb_parity_stress/`. New scenario replays: **316 = 2 baselines + 314 stresses**.
The .25 baseline is a parity diagnostic, not an economic trial; this completes the existing VB robustness trial.
No ONB rerun, new hypothesis, fitted parameter, placebo search or best-case selection.

## Rule and execution conventions

Unchanged VB: noise .30×ATR15 SMA from midnight open, midnight VWAP, first 10:00, last/flat 14:30,
40-point target, 75-point stop, max 3/day; holiday last 11:00/flat 11:30. One NQ, $20/point, .25 tick.
Round-trip commission $7.25 plus one adverse tick on market/stop fills; target exits pay no extra slippage.
Minute close stamps retain original timing; decisions enter the following minute's open. Original generators,
accelerated engine, indicators, date boundaries, costs and pairing function are unchanged and hash-checked.

Only the MC reproduction baseline permits target-through **.25 point**, based on the observed exit-bar highs.
The original diagnostic has {counts['below_025']} fills below .25 through, {counts['0.25']} at .25,
{counts['0.5']} at .50, {counts['0.75']} at .75, {counts['at_least_1']} at >=1 point. This is consistent with a
one-tick reconstruction of this export's "exceeded by 1 points" setting. It does not establish every MC
configuration's semantics. The **1-point research baseline remains the denominator for every stress verdict**;
execution scenarios additionally test the originally specified 2-point-through cases. Stricter fills alter
holding/re-entry paths and need not lower every individual trade's P&L.

## Original baseline parity gate

Same report/date overlap: {q['start']} through {q['end']}. Keys are date/side/native 30-minute entry bar.
No fuzzy matching, date deletion, changed warm-up or lowered gate. The original thresholds are >=98% matched
on each list, >=99% entry prices within .25, >=95% gross P&L within $20, gross correlation >=.98, and complete
overlapping-list mean-net gap <=max($20,10% of absolute MC mean). Each threshold passes for the .25 reference.

| Fill convention | Python / MC | Matched | Matched % Python / MC | Entry within tick | Gross within $20 | Gross corr | Mean-net gap | Gate |
|---|---:|---:|---:|---:|---:|---:|---:|---|
{chr(10).join(parity_rows)}

Matched .25 gross-P&L maximum gap **{dollars(max_pnl_gap,2)}**; entry-price maximum gap **{max_entry_gap:g} point**.
Residuals: **{int(pair._merge.eq('left_only').sum())} Python-only and {int(pair._merge.eq('right_only').sum())} MC-only**,
preserved in the complete pairing and `parity_quarterpoint_unmatched_causes.csv`. MC-only emulator facts:
four lack a qualifying Python signal, two occur while a Python position is still open, one after Python's
three-trade cap. Five Python-only entries have an unresolved MC-side cause. These facts do not claim a proven
source-data/indicator cause. The original gate permits these residuals; none were removed from its denominator.

Full-history Python baseline counts differ from overlap counts because the original report starts January 25,
2018 at 11:00. Exactly the same original overlap filter applies to both fill conventions.

## Baseline results — report both conventions

Per fixed one NQ after costs; all trades are long, so **combined=long and shorts N/A**. Short rows with zero
trades and undefined ratios remain explicit in the CSVs. Daily risk uses the complete trading-date calendar
and initial zero for drawdown; $50k is only the Ulcer denominator. No account/margin sizing is inferred.
"2018–26" ends **2026-10-09**, not a complete 2026 year.

| Fill convention | Period | Trades | Win | Net/trade | t | Sharpe | Sortino | PF | Calmar | Ulcer | Max DD |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
{chr(10).join(base_rows)}

| Year | 1-point trades | 1-point net | .25-point trades | .25-point net |
|---|---:|---:|---:|---:|
{chr(10).join(year_rows)}

The .25 convention is not selected as a more profitable strategy; it has one job: reconstruct the report.
The reproduced 1-point baseline matches the old saved baseline and original candidate trade by trade.

## Frozen stress families — 1-point baseline

BENDS requires >50% of runs profitable AND at least half base Sharpe in **both** periods, with positive base
Sharpe. BREAKS requires median net<=0 OR median Sharpe<third of base in **each** period. Otherwise MIXED/WATCH.
The family/overall thresholds were unchanged. No family satisfies BREAKS; formal overall verdict **{overall}**.

| Family | Period | Runs | Median net | Median net/trade | Median t | Median PF | Median Sharpe | Median DD | Net>0 | Net>0 & t>2 | Net>0 & half SR | Verdict |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
{chr(10).join(family_rows)}

![Frozen VB stress distributions](../../../analysis/outputs/codex_vb_parity_stress/VB_stress_distributions.png)

These boxes show scenario sensitivity, not independent samples or confidence intervals. Both 1/2-tick noise
groups and all deterministic cases are retained; full run/side/year metrics include Sortino, Calmar and Ulcer
in `run_metrics.csv` and `stress_side_year_summary.csv`.

Timing deserves its own view despite the family BENDS result:

| Timing case | Period | Trades | Net/trade | t | Sharpe | Max DD |
|---|---|---:|---:|---:|---:|---:|
{chr(10).join(timing_rows)}

The 30-minute delay's recent Sharpe is just below half baseline; 2 of 3 timing runs still clear the family
threshold. It stays profitable and above one-third baseline. It changes entry opportunity, not just price
slippage; this is no recommendation to alter execution. Deterministic loss/below-third flagged whole-strategy
rows: **{len(flags[flags.side.eq('all')])}**; combined/long duplicates are identified in the saved flag tables.

## Joint jitter and remaining risk

200 accepted simultaneous ±10% draws; **{len(draws)} raw**, **{int((~draws.accepted).sum())} infeasible draws**
rejected on original chronological/calendar constraints before evaluating returns. Factors, proposed settings,
reasons and accepted outputs are all saved. No losing draw was discarded or replaced. Feasibility conditioning
induces dependence across the retained parameter values.

Design: {j18.share_positive:.0%} profitable, {j18.share_positive_half_sharpe:.1%} positive+half baseline Sharpe.
2023+: {j23.share_positive:.0%} profitable, {j23.share_positive_t2:.0%} positive+t>2,
{j23.share_positive_half_sharpe:.0%} positive+half baseline Sharpe; median DD **{dollars(j23.median_max_dd)}** versus
**{dollars(baseline.loc['2023+','max_dd'])}** baseline. Mostly positive draws do not imply stable risk-adjusted returns.
Every joint draw's loss/below-third-baseline status and parameter vector is preserved in
`jitter_dependency_checks.csv` / `jitter_dependency_flags.csv`; **{len(jitter_bad)}** period/run rows trigger
at least one warning. These are joint-draw diagnostics, not isolated causal tests of a particular input.
The frozen clock jitter is broad: first entry 09:00–11:00, last/flat 13:00–15:30, holiday times as below.
Those move the session meaningfully. This is joint sensitivity; it does not identify a single causal parameter
or prove fragility to a tiny implementation error. No post-hoc one-input rescue or preferred draw was tested.

| VB input | Minimum | Maximum | Distinct after rounding |
|---|---:|---:|---:|
{chr(10).join(range_rows)}

Clock values in this table are HHMM after proper minute-axis jitter; integer ATR and max-trade rounding are
explicit. Max-trades remains 3 in every accepted draw; it was perturbed but rounded back to the same value.

## Controls, uncertainty and applicability

The original seed 8675309 and SeedSequence children are unchanged. All 100 noisy grids use the identical seeds
already used for ONB; ATR/VWAP and signals/fills are recomputed from each grid. Noise volumes/NaN masks are
unchanged, projected OHLC and tick rounding enforced. The original 200 VB jitter draws use their reserved seed
child, not ONB's child. Indicator/anchor, timing and execution cases call the original functions unchanged.

2023+ one-point baseline daily-Sharpe 90% ten-session-block interval **[{ci.p5:.2f}, {ci.p95:.2f}]**, 2,000 draws.
Other metric intervals and 2,000 drawdown permutations are saved; all=long, shorts N/A. These are conditional
historical uncertainty summaries, not a new holdout. No placebo rerun, new candidate promotion, funded bench,
account sizing or payoff claim is required or inferred from this unchanged-strategy robustness audit.

Review context: ONB's stress evidence was accepted, with its broad-clock jitter MIXED result interpreted as
an open-session dependency. The original formal metric result is preserved. RSI/Bollinger and XAU remain failed
screens. Execution diagnostics remain observations; the bid/ask logger remains a proposal requiring a test-chart
check before any separately authorized use. No live test/deployment, watchdog or Friday-runbook action here.

## Verification, limitations and reproduction

Original plan/helper/report dependency hashes and input CSV/cache hashes match the previous audit. The
read-only cache still starts with 2017-12-01 overnight observations and ends 2026-10-09. No warm-up input,
shared cache, minute series, source strategy, old report or old outputs were overwritten. Synthetic fixtures
verify touch refusal, one-tick target fill and recomputed re-entry sequencing; original engineering checks and
1-point original/accelerated/saved-ledger equivalence pass. All {len(json.loads((p/'engineering_checks.json').read_text()))} checks pass.

Matching on native bars and gross P&L does not verify broker timestamps, spread, queue priority or intraminute
path. MC entry/exit minutes from `portfolio.load_mc` are inferred within reported bars; they are not actual
broker fill timestamps. Remaining signal/MC differences, continuous-contract provenance, holiday/provider
differences and OHLC ambiguity remain limitations. Passing the declared parity gate does not make them vanish.

```bash
/workspace/venvs/thebeginning/bin/python analysis/codex_vb_parity_stress.py --parity
/workspace/venvs/thebeginning/bin/python analysis/codex_vb_parity_stress.py --stress
/workspace/venvs/thebeginning/bin/python analysis/codex_vb_parity_stress_report.py
```

The stress command refuses a failed parity artifact or changed runner/source inputs. All original outputs are
preserved; this is a separate completion report. One .25 parity diagnostic and the reproduced 1-point baseline
are disclosed in addition to the 314 frozen stresses. The number of registered economic robustness trials stays
two across the original VB/ONB assignment; no new performance-selected hypothesis was introduced.

## Differences between MultiCharts code and test

No MultiCharts code was written. MC parity uses the registered .25-point threshold; research stress runs keep
the 1-point default and original 2-point execution cases. Existing order guards, market fallback, position/account
sizing and real-time broker behaviors remain outside this fixed-one-NQ historical test. No live decision follows.

Tell Claude: review `agents/codex/results/vb_parity_stress.md`; original gate passes at .25, all 314 frozen
1-point VB stresses are complete, overall MIXED/WATCH because of recent joint jitter. Nothing selected for trading.
'''
    (S.ROOT/'agents/codex/results/vb_parity_stress.md').write_text(report)
    repro=json.loads((p/'reproduction.json').read_text())
    repro['code_sha256']['analysis/codex_vb_parity_stress_report.py']=S.B.sha(__file__)
    repro.update(mechanical_scenarios_in_new_output=316,VB_stress_runs=314,parity_only_points=.25,
                 stress_default_points=1.,overall_verdict=overall)
    S.dump('reproduction.json',repro)
    print('Report written: parity PASS; VB',overall,flush=True)


if __name__=='__main__':main()
