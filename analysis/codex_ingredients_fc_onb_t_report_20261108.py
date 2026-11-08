"""Summarize already frozen ledgers; no signal generation or rule selection."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
import resampling as R

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'analysis/outputs/codex_ingredients_fc_onb_t_20261108'
REPORT=ROOT/'agents/codex/results/ingredients_fc_onb_t_20261108.md'

def table(df,cols):
    def f(x):
        if isinstance(x,(float,np.floating)):return f'{x:,.2f}' if np.isfinite(x) else '—'
        return str(x)
    return '| '+' | '.join(cols)+' |\n| '+' | '.join(['---']*len(cols))+' |\n'+'\n'.join('| '+' | '.join(f(x) for x in row)+' |' for row in df[cols].itertuples(index=False,name=None))+'\n'


def main():
    metrics=[];effects=[];controls=[];comparison=[];bootstrap=[];receipts={};mismatches=[]
    for phase in ['design','recent']:
        d=OUT/phase;receipt=json.loads((d/'summary.json').read_text());receipts[phase]=receipt
        m=pd.read_csv(d/'metrics.csv');metrics.append(m)
        e=pd.read_csv(d/'paired_effects.csv');e['period']=phase;effects.append(e)
        for fam,c in receipt['pure_filter_controls'].items():
            controls.append({'period':phase,'family':fam,**{k:v for k,v in c.items() if not isinstance(v,list)}})
        for fam in ['FC2B','ONB30','ONBML','Tfade']:
            z=m[(m.family==fam)&m.variant.eq('original')&m.side.eq('all')&m.period.eq(phase)]
            comparison.append(z)
        a=pd.read_csv(d/'Tfade__original_trades.csv');b=pd.read_csv(d/'Tfade__no_heavy_gate_trades.csv')
        both=a.merge(b,on='date',suffixes=('_fixed','_allnight'),how='left')
        bad=both[both.side_fixed.ne(both.side_allnight)|both.entry_fixed.ne(both.entry_allnight)|both.exit_fixed.ne(both.exit_allnight)]
        bad=bad.copy();bad['period']=phase;mismatches.append(bad)
        # Confirm all ledgers' cash bridges and calendar reconciliation, including native micro fees.
        for p in sorted(d.glob('*_trades.csv')):
            t=pd.read_csv(p);daily=pd.read_csv(str(p).replace('_trades.csv','_daily.csv'))
            assert np.allclose(t.gross,(t.exit-t.entry)*t.side*20)
            assert np.allclose(t.net,t.gross-t.commission-t.slippage)
            assert np.allclose(t.native_mnq_net,t.gross/10-1.25-t.slippage/10)
            assert abs(t.net.sum()-daily.net.sum())<.005
            if phase=='recent':
                z=R.bootstrap(daily.net,n=1000,block=20,seed=20261108,chunk=250)
                for k,r in z.iterrows():bootstrap.append({'case':p.name.removesuffix('_trades.csv'),'metric':k,**r.to_dict()})
    pd.concat(mismatches).to_csv(OUT/'Tfade_allnight_common_date_mismatches.csv',index=False)
    pd.DataFrame(bootstrap).to_csv(OUT/'recent_bootstrap.csv',index=False)
    pd.DataFrame(controls).to_csv(OUT/'filter_controls_flat.csv',index=False)
    allm=pd.concat(metrics,ignore_index=True);alle=pd.concat(effects,ignore_index=True)
    allm.to_csv(OUT/'all_metrics.csv',index=False)
    summary="""# FC 2B, ONB and T_ONESIDE ingredients: WATCH — diagnostics only

Summary: Tested 18 frozen cases; both ONBs share a breakout core, with different settings and an added ML filter.
T_ONESIDE's fade direction and pre-open timing contributed in both periods; its stop mainly limits tails.
FC's flow selection concentrates return and lowers drawdown; its break-even rule reduced net profit in both periods.
ONB ML's calendar block is the clearest fitted-score contributor; this is in-sample attribution, not validation.
No rule, size, plan or live change; independent review pending.

Plan: `agents/codex/plans/ingredients_fc_onb_t_20261108.md`, commit `b0e5112`.
Script: `analysis/codex_ingredients_fc_onb_t_20261108.py`.
Reporter: `analysis/codex_ingredients_fc_onb_t_report_20261108.py`.
Output: `analysis/outputs/codex_ingredients_fc_onb_t_20261108/`.
Trials run: 18 distinct fixed diagnostic definitions plus the registered controls; no optimum selected.
Design receipt committed as `0c11d55` before recent execution. No implementation reruns or rescue variants.

## Rule (as tested)

- **FC 2B v2:** opening-drive direction and historical flow-selected MC entry dates; exact v2 exit replica,
  including entry-bar backstop, 100-point stop, 150-point trail, 66-point BE trigger and next-open flatten.
  Four cases: original, all opening drives without the flow date gate, BE disabled only, trail disabled only.
- **ONB ADX30:** overnight location sets direction, 08:30–08:45 CT opening-range breakout,
  ADX >30, stop 0.25 daily ATR and 3R target. Four cases: original, no ADX, two-sided first breakout
  without the overnight direction restriction, no target while preserving the stop.
- **ONB ML v2:** the same core with ADX >20 and stop 0.30 ATR, plus the frozen score.
  Five cases: original; no score at these same parent settings; remove calendar, price or volatility
  terms separately. Remaining coefficients, intercept and thresholds stay fixed. No refit/recentering.
  The no-ML parent is deliberately **not** the differently configured ADX30 strategy.
- **T_ONESIDE:** active fade-only v2, not the OS leg. Fade the overnight move on MC-selected heavy-night
  dates, 0.40 ATR stop active from entry, exit at the 08:45-labelled bar open.
  Five cases: original, all valid nights without the volume hurdle, follow the same selected nights,
  enter one minute later at the cash bell, remove only the stop. Regular entry is the 08:30-labelled
  bar's open (08:29 civil CT); delayed entry is 08:31-labelled open (08:30 civil CT).

**Information/data scope:** design 2018-01-01–2022-12-30, unchanged historical replication
2023-01-01–2026-10-09. Earlier data supply warm-up only. T's all-night universe starts 2018-01-30,
the first retained MC fade event. Both recent history and MC ledgers were already known.
FC and T use up-tick `Volume` in MultiCharts; exported total ticks cannot reconstruct that field.
Their original admission is therefore taken from retained MC dates/sides. Removing that gate is a
conditional comparison with an all-drive/all-night universe, not a deployable reconstructed volume signal.

**Mechanism versus evidence:** FC proposes opening-flow continuation; ONB proposes overnight location
followed by opening participation; T proposes reversal of an unusually active overnight move near the
cash open. These tests identify return/risk dependencies in the rules. They do not identify participants,
measure forced orders, establish a causal explanation, or prove these mechanisms remain profitable live.

## Results

All amounts are **one NQ contract**, fixed size, net of $7.25 round-trip commission and one 0.25-point
adverse tick per market/stop fill; target exit has no modeled slippage. These are total period profits,
not annual dollars or account payouts. Native MNQ ledgers use $1.25 commission plus native tick costs,
not NQ net divided by ten. DD below is daily realized equity drawdown with the initial zero peak,
not intraday account drawdown or a funded-account safety estimate.

### Original baselines
"""
    summary+=table(pd.concat(comparison),['family','period','trades','total','avg','t_trade','sharpe','profit_factor','max_dd','worst_trade','native_mnq_total'])
    summary+="""
### What drives each strategy

**FC 2B: flow selection concentrates opportunity; exits have different roles.** Removing the flow gate
raises total net from $129,353 to $151,204 early and $87,259 to $114,708 recently, but DD rises from
$8,885 to $32,598 and $15,251 to $33,646. The removed trades are positive in aggregate, so this is
not a strict profitable-versus-losing-trades filter success. It retains much of the return at far fewer trades
and lower historical DD. Removing BE adds $3,380 / $8,190 net; the recent paired annual interval
includes zero. Removing the trail is almost neutral early (original minus no-trail −$20), but loses
$22,600 recently and raises DD to $19,136; recent paired annual contribution is $2,366–$10,008
(5th–95th percentile). The trail is period-dependent; BE is not an established alpha source.
None of this justifies changing the frozen production/forward rule.

**ONB ADX30: overnight direction and ADX mainly concentrate exposure and control realized DD.**
Two-sided first breakout produces almost the same early net ($124,237 vs $123,768) but much worse
DD ($33,990 vs $7,581). Recently it earns $107,693 vs $127,569 with DD $32,103 vs $13,571.
This direction intervention can change which entry occurs first, so it is not a pure removed-trade filter.
Removing ADX costs $8,661 early but adds $25,997 recently; DD worsens in both periods. The 3R target
is close to neutral early; removing it adds $10,885 recently, with unchanged recent maximum DD.
The paired recent target contribution interval includes zero. ADX/target are not uniformly profit-producing
ingredients, and the no-target case has not earned any book change.

**ONB ML: same breakout mechanism, with calendar-conditioned admission.** Dropping calendar terms
reduces early net from $117,295 to $49,958 and recent net from $108,116 to $51,694.
The original-minus-no-calendar annual intervals are positive in both periods ($7,746–$17,801 early;
$5,868–$25,219 recent). Price terms contribute $44,333 early but −$4,040 recently; volatility terms
reduce net by $39,537 early / $12,670 recently while restricting exposure. These are fixed-threshold
sensitivity tests: deleting a block changes admission and the score's level. They are not additive causal
attribution, optimized replacement scores or evidence that coefficients should be removed.
Without ML, the identically configured parent earns more total net in both periods but at larger DD.
The frozen weights were fitted on 2018–26, so **both splits are fitted-sample description**; no OOS ML claim.

**T_ONESIDE: the fade direction and the minute before the bell are the clearest repeat contributors.**
Following the same nights instead of fading turns +$47,642 / +$37,273 into −$53,638 / −$35,093.
Entering at the bell loses $8,695 / $9,905; paired annual timing contribution intervals stay positive
($263–$3,586 early, $558–$4,855 recent). These are OHLC replay differences, not measured live fill savings.
Removing the stop reduces profit by $5,565 / $3,770 and raises DD from $7,213 / $11,289 to
$11,488 / $14,904. The recent stop contribution interval includes zero; the tail-control role is clearer.
All-night fading is much weaker ($28,998 / $28,286 net, DD $24,711 / $27,411).
However, the early all-night reconstruction changes four common-date directions, so its comparison is
not a pure volume filter; do not credit its entire difference to heavy-night selection.

### Full fixed-case comparison
"""
    for phase in ['design','recent']:
        summary+='\n#### '+phase+'\n\n'
        summary+=table(allm[allm.side.eq('all')&allm.period.eq(phase)],['family','variant','trades','total','avg','t_trade','sharpe','profit_factor','max_dd','worst_trade'])
    summary+="""
## Placebos and account level

The registered T direction control actually replays reversed positions with the same stop distance and
scheduled exit; costs are charged again. It is not a sign flip of net P&L. For nested date filters,
common-date side/entry/exit/net must match before treating the difference as removed trades.
1,000 within-year equal-count random subsets provide descriptive selection controls.
Their tail shares are **not** multiple-testing-adjusted p-values and do not establish economic adoption.
"""
    summary+=table(pd.DataFrame(controls),['family','period','pure_nested_filter','removed_n','removed_total','removed_mean','removed_t','random_profit_ge_actual','random_dd_le_actual'])
    summary+="""
A small `random_profit_ge_actual` means the actual selection beats most matched-count random subsets
on total profit; `random_dd_le_actual` is the fraction with DD no worse than actual. FC's removed trades
are +$25.89 / +$42.56 per trade (t 0.44 / 0.54). ONB ML's are +$30.17 / +$107.99 (t 0.35 / 0.74).
Neither meets the strict requirement that removed trades lose. T's recent removed nights average −$10.66
(t −0.26); its removal edge is weak despite beating most random selections on total net. Early T has four
common-date direction mismatches (2018-02-07, 2018-05-25, 2018-09-06, 2022-01-21), listed in
`Tfade_allnight_common_date_mismatches.csv`; attribution to volume alone is withheld. The fixed MC
parent sides remain unchanged. No correction/search was made after seeing these differences.

Paired intervals below use original-minus-intervention **daily** cash differences, 1,000 moving
20-session blocks, seed 20261108. Dollar intervals are **annualized** while the delta column is total
period net. Positive delta favors the original. Eighteen definitions plus controls are retained; these
unadjusted diagnostic intervals must not select/promote a strategy. Original strategy standalone recent
bootstrap distributions, including annual P&L, are in `recent_bootstrap.csv` (all 18 cases).
Bootstrap DD/Calmar/Ulcer retain the repository sampler's convention; the displayed realized DD uses
its zero-start-aware `max_dd`. No claim that a bootstrap distribution is an account liquidation model.
"""
    summary+=table(alle,['family','period','component_removed','original_minus_variant','annual_effect_p5','annual_effect_p50','annual_effect_p95'])
    summary+="""
**Account level:** not run. This task dissects existing ingredients; it neither selects a replacement nor
measures payout contribution. No BASE/ADD/REPLACE/EMPTY, leverage choice, evaluation pass probability,
funded blow-up rate or improvement to the current stack is established by these results. Any proposed
new combination requires a separate bounded preregistration and the actual current-book comparisons.

## What could make this wrong

- Exact MC baseline entry/gross parity: FC 443/443 early and 327/327 recent; T 228/228 early and
  130/130 recent. All common entries and gross P&L match, with no missing parent events, side differences
  or cross-date trades. This verifies conditional replay, not the missing up-tick classifier.
- ONB ADX30's custom core exactly matches the pinned original engine on the same inputs/settings.
  This is internal implementation identity, not a new independent MultiCharts comparison. ML adds a
  source port of the fixed score; its deleted-block cases have no MC parity claim.
- A small number of unobserved nominal held closes remain: FC original recent 3; FC all-drive early 7 /
  recent 4; FC no-BE/no-trail recent 3 each; ONB no-ADX early 1; ONB no-bias recent 4; T all-night early 3.
  All other cases have zero. Existing engine missing-bar policies remain; no future fill or invented prices.
  Even with matching realized MC P&L, intrabar risk around missing bars is uncertain.
- ONB source execution retains 1-point target trade-through and OHLC ordering. Two-sided counterfactual
  simultaneous touches use a declared nearer-extreme rule; real order of touches needs tick data.
- FC no-BE correctly uses BER=0 with the v2 `BER > 0` guard; it does not accidentally arm BE immediately.
  Every stop/target intervention preserves the other exit inputs. T stop rounding is fixed before execution.
- Both ONBs share a directional breakout core; their nominal profits cannot be added as independent edges.
  Calendar-block dominance does not isolate individual weekdays versus turn-of-month contributions.
- One-way component deletion measures dependencies conditional on the remaining system. It does not
  show interactions, statistical independence, optimal rules, forced institutional trading or live causality.
- No new learned model, honest ML holdout, forward log observation or independent economic verification.
  Both time periods were already seen historically; recent is replication, not an untouched holdout.
- The immutable input manifest and raw Git-blob checks pin data to the retained source snapshot;
  the reporter checks gross, commission, slippage, native micro fees and daily/trade sums to half a cent.

## Differences between MultiCharts and this test

No MultiCharts code was written or changed. FC/T selected source dates and sides come from MC ledgers
because native up-tick volume is absent. Exit replays use minute OHLC, not ticks or broker fills.
ONB is a source-style repository engine, not a newly verified native chart export. T's all-night control uses
observed overnight direction, which differs from four early MC-selected directions. These limits remain
visible even though original FC/T baseline realized results match exactly.

## Practical ingredient conclusion

For later, separately registered idea design: FC contributes **opening-flow selection and continuation**;
ONB contributes **overnight location plus opening-range participation**, with the ML version adding
**calendar-based selection rather than a separate core signal**; T contributes **pre-open overnight reversal**.
T's fade is directionally different from FC/ONB continuation, so combining all three as simultaneous
confirmations may reject the opportunity each was intended to capture. First identify whether a proposed
new rule uses a continuation regime or a pre-open reversal regime. No hybrid was tested in this task.

## Detailed long/short and annual results

`all_metrics.csv` includes every whole/long/short result and every year, plus costs, worst trade and native
MNQ totals. The following tables retain the required standard metrics. `win` is a fraction; profit factor
is per trade. Annualized ratios use the shared calendar including zero-P&L sessions and $50,000 capital.
"""
    for phase in ['design','recent']:
        summary+='\n### '+phase+': whole / long / short\n\n'
        summary+=table(allm[allm.period.eq(phase)],['family','variant','side','trades','win','total','avg','t_trade','sharpe','sortino','profit_factor','calmar','ulcer','max_dd'])
    summary+='\n### By year, all sides\n\n'
    summary+=table(allm[~allm.period.isin(['design','recent'])],['family','variant','period','trades','win','total','avg','t_trade','sharpe','sortino','profit_factor','calmar','ulcer','max_dd'])
    REPORT.write_text(summary)
    print('Saved',REPORT,'with',len(allm),'metric rows and',len(bootstrap),'bootstrap rows; all ledger bridges reconcile.')

if __name__=='__main__':main()
