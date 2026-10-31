"""Report/audit saved GreenORB outcomes; no strategy search or new return test."""
from pathlib import Path
import hashlib,json,subprocess,sys
from importlib.metadata import version
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'analysis/outputs/codex_greenorb'
REPORT=ROOT/'agents/codex/results/greenorb_20261030.md'
PREREG='c32fee6'

def read(name):return json.loads((OUT/name).read_text())
def dump(name,obj):(OUT/name).write_text(json.dumps(obj,indent=2)+'\n')
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def usd(x):return f'${x:,.2f}'
def table(headers,rows):
    return '\n'.join(['| '+' | '.join(headers)+' |','|'+'|'.join(['---']*len(headers))+'|']+
                     ['| '+' | '.join(map(str,row))+' |'for row in rows])

def raw_feature_audit(t):
    """Maker reconciliation directly from CSVs, without Grid24/strategy imports.

    Uses saved events only. It is a feature/clock check, not an independent
    economic rebuild, a new variant or proof of native MNQ/Liqport parity.
    """
    wanted=set(pd.to_datetime(t.date).dt.strftime('%Y%m%d').astype(int))
    wanted.update(pd.to_datetime(t.date).sub(pd.Timedelta(days=1)).dt.strftime('%Y%m%d').astype(int))
    parts=[]
    for y in range(2018,2023):
        for stem in ('NQ_1min_','NQ_1min_ON_'):
            z=pd.read_csv(ROOT/f'data/{stem}{y}.csv')
            parts.append(z[z.date.isin(wanted)].copy())
    raw=pd.concat(parts,ignore_index=True)
    assert not raw.duplicated(['date','time']).any()
    raw['j']=raw.time//100*60+raw.time%100
    groups={int(date):z.set_index('j').sort_index()for date,z in raw.groupby('date')}
    for s in t.itertuples():
        dt=pd.Timestamp(s.date);d=groups[int(dt.strftime('%Y%m%d'))]
        prev=groups[int((dt-pd.Timedelta(days=1)).strftime('%Y%m%d'))]
        r=d.loc[511:525];hi=r.high.max();lo=r.low.min()
        colours=[np.sign(d.loc[j,'close']-d.loc[j-4,'open'])for j in (515,520,525)]
        assert all(int(x)==s.side for x in colours)
        assert np.isclose(s.stop_px,lo if s.side==1 else hi)
        prefix=prev.loc[961:];first=None
        for j in range(530,661,5):
            p=pd.concat([prefix,d.loc[:j]])
            good=np.isfinite(p[['high','low','close','volume']]).all(axis=1)&(p.volume>=0)
            p=p[good];vw=((p.high+p.low+p.close)/3*p.volume).sum()/p.volume.sum()
            c=d.loc[j,'close'];direction=1 if c>hi and c>vw else -1 if c<lo and c<vw else 0
            if direction==s.side and s.side*(c-s.stop_px)/c<.01:
                first=j;break
        assert first==s.j0-1
        assert np.isclose(s.entry,d.loc[s.j0,'open']+s.side*.5)
    return dict(events_checked=len(t),all_colours_or_stops_first_signals_next_opens_match=True,
                status='maker raw-CSV feature reconciliation only; independent review pending')

def main():
    # Undefined small-subgroup statistics are JSON null, never imputed returns.
    # Keep the original console log intact; this serialization-only step is
    # reproduced after the frozen return script, without rerunning finance.
    for p in OUT.glob('*.json'):
        obj=json.loads(p.read_text(),parse_constant=lambda _:None)
        p.write_text(json.dumps(obj,indent=2,allow_nan=False)+'\n')
    r=read('design_result.json');f=read('design_filter.json');mc=read('design_montecarlo.json')
    t=pd.read_csv(OUT/'design_primary_trades.csv');daily=pd.read_csv(OUT/'design_primary_daily.csv')
    stress=pd.read_csv(OUT/'design_primary_4tick_trades.csv');coverage=pd.read_csv(OUT/'design_coverage.csv')
    primary=r['metrics']['primary'];s=primary['whole'];b=r['metrics']['no_colour']['whole']
    nested=r['metrics']['nested_colour']['whole'];removed=f['removed']
    pre=json.loads((ROOT/'agents/codex/inputs/greenorb/preregistration_manifest.json').read_text())
    frozen=next(z['sha256']for z in pre['inputs']if z['path']=='analysis/codex_greenorb.py')
    assert frozen==r['code_sha256']==sha(ROOT/'analysis/codex_greenorb.py')
    assert not list(OUT.glob('recent_*')) and not r['later_stages_earned']
    assert t.date.is_unique and t.date.equals(stress.date)
    assert ((t.j0>=531)&(t.j0<=661)&(t.j1>=t.j0)&(t.j1<=899)).all()
    assert set(t.date)<=set(coverage.loc[coverage.status=='resolved','date'])
    assert np.allclose(t.net,(t.exit-t.entry)*t.side*2-1.24)
    assert np.allclose(t.net,t.gross-t.commission-t.slippage)
    assert np.allclose(t.commission,1.24)
    assert np.allclose(t.slippage,1+(t.kind!=1).astype(int))
    assert np.isclose(t.net.sum(),daily.net.sum())
    assert np.isclose(daily.net.sum(),s['total'])
    assert np.allclose(t.target_px/.25,np.round(t.target_px/.25))
    assert (t.side*(t.target_px-t.entry)>=1.5*t.risk_pts-1e-8).all()
    audit=dict(accounting='PASS',clock_and_grid='PASS',unchanged_preregistered_return_code=True,
        preregistration_commit=subprocess.check_output(['git','rev-parse',PREREG],cwd=ROOT,text=True).strip(),
        native_MNQ_trade_match=False,independent_review='pending',raw_features=raw_feature_audit(t),
        undefined_small_subgroup_statistics='JSON null; no return imputation',
        python=sys.version,dependencies={k:version(k)for k in ('numpy','pandas','numba')},
        recent_or_account_returns_run=False,unknown_dates=coverage.loc[coverage.status!='resolved','date'].tolist(),
        worst_primary_stop_risk_dollars=float(t.risk_pts.max()*2),same_bar_stop_target_collisions=int(t.collision_bars.sum()))
    dump('audit.json',audit)
    ledger=dict(candidate='GreenORB',family='opening_drive_orb',task='direct user upload',
        preregistration_commit=audit['preregistration_commit'],return_code_sha256=frozen,
        design_years=[2018,2022],definitions_reserved=pre['reserved_definitions'],
        definitions_executed=r['definition_ids_executed'],candidate_definitions_executed=3,
        random_side_draws=1000,random_time_draws=1000,matched_random_drop_draws=1000,
        uncertainty=dict(trade_MC=10000,daily_MC=5000,design_bootstrap=5000),
        cost_sensitivities=['author RT commission1.04 on frozen ledger','exact4ticks per market/stop fill with rebuilt target'],
        parameter_search=False,side_or_year_selection=False,implementation_return_reruns=0,
        shared_prior_trial_rows=274,shared_prior_trial_variants=1226,shared_history_overwritten=False,
        scout_budget_changed=False,disposition='REJECT for advancement: filter and random-time gates failed',
        recent_or_account_definitions_executed=0)
    dump('trial_ledger.json',ledger)
    mt=table(['2018–22, 1 MNQ','Trades','Net','Win','Avg/trade','t','Sharpe','Sortino','PF','Max DD','Calmar','Ulcer %'],[
        [label,m['trades'],usd(m['total']),f"{m['win']:.1%}",usd(m['avg']),f"{m['t']:.2f}",f"{m['sharpe']:.2f}",
         f"{m['sortino']:.2f}",f"{m['profit_factor']:.2f}",usd(m['max_dd']),f"{m['calmar']:.2f}",f"{m['ulcer']:.2f}"]
        for label,m in [('Whole',s),('Long',primary['long']),('Short',primary['short'])]])
    yt=table(['Year','Whole trades / net','Long trades / net','Short trades / net','Whole t','Whole Sharpe','Whole max DD'],[
        [y,f"{m['trades']} / {usd(m['total'])}",
         f"{primary['yearly_sides'][y]['long']['trades']} / {usd(primary['yearly_sides'][y]['long']['total'])}",
         f"{primary['yearly_sides'][y]['short']['trades']} / {usd(primary['yearly_sides'][y]['short']['total'])}",
         f"{m['t']:.2f}",f"{m['sharpe']:.2f}",usd(m['max_dd'])]for y,m in primary['yearly'].items()])
    ft=table(['Frozen definition','Trades','Net','Average','Max DD'],[
        [name,m['trades'],usd(m['total']),usd(m['avg']),usd(m['max_dd'])]for name,m in
        [('Actual GreenORB',s),('First-break, no-colour control',b),('Nested colour control',nested),('Removed by nested filter',removed)]])
    bt=pd.read_csv(OUT/'design_bootstrap.csv',index_col=0)
    bttext=table(['Design block bootstrap (5,000 x10day)','Observed','5th percentile','95th percentile'],[
        [k,*[f'{bt.loc[k,c]:,.2f}'for c in ['actual','p5','p95']]]for k in ['annual','sharpe','max_dd']])
    homes=table(['Destination','Verdict','BASE / ADD / REPLACE / EMPTY outcome'],[
        [home,'No eligible place earned','Not run: failed design gates']for home in
        ['50K evaluation','150K evaluation','50K funded','150K funded','Personal (current19-piece roster)']])
    report=f'''# GreenORB: REJECT advancement; profitable design proxy, failed controls

Summary: GreenORB's owned-NQ proxy earned {usd(s['total'])} on {s['trades']} trades in 2018–22 at one MNQ after costs.
Daily Sharpe {s['sharpe']:.2f}, trade t {s['t']:.2f}, maximum drawdown {usd(s['max_dd'])}; exact four-tick stress stayed positive.
Random-time p={r['placebo_p']['time']:.4f} and the colour filter's removed-profit/random-DD tests fail.
No 2023+ or portfolio comparisons were earned; no place approved in any of the five homes.
NQ/observed-volume proxy only: native MNQ, Liqport trade parity and independent verification remain unverified.

Plan: [frozen preregistration](../plans/greenorb_20261030.md), commit `{audit['preregistration_commit']}`.
Evidence: [pre-return sheet](../plans/greenorb_evidence_20261030.md).
Code: [return test](../../../analysis/codex_greenorb.py), [report/raw-feature audit](../../../analysis/codex_greenorb_report.py).
Outputs: [result JSON](../../../analysis/outputs/codex_greenorb/design_result.json),
[trade ledger](../../../analysis/outputs/codex_greenorb/design_primary_trades.csv),
[coverage](../../../analysis/outputs/codex_greenorb/design_coverage.csv),
[trial ledger](../../../analysis/outputs/codex_greenorb/trial_ledger.json),
[audit](../../../analysis/outputs/codex_greenorb/audit.json).

## Four source questions

1. **What is it about?** A user-supplied strategy post/PDF and Liqport Python class, not an academic paper.
   Trade a 15-minute MNQ opening-range breakout only after three same-colour five-minute opening candles, with
   overnight-inclusive VWAP confirmation, opposite-OR stop, 1% maximum signal-to-stop distance and 1.5R target.
   Fixed 1 MNQ, one trade/day, next-minute market entry and 15:58 NY flatten.
2. **What does it find?** The author claims 296 MNQ trades, +$13,101, 54.7% wins, daily Sharpe 1.27 and $1,125 DD
   over January 2020–October 13, 2026. All rules were designed on that history; the claimed nine live months and trades
   were not independently verified. Our frozen 2018–22 NQ-data proxy earned {usd(s['total'])}, but failed
   advancement controls. These are different dates/inputs, not a numerical reproduction of the author's run.
3. **Why could it make money?** The proposed mechanism is continuation of one-sided opening demand.
   No participant obligation or signed flow was measured. Positive proxy profits could reflect opening momentum,
   Nasdaq drift, sparse trade selection or sample omissions. Random-side works as a diagnostic, but random-time
   p={r['placebo_p']['time']:.4f} does not establish entry timing beyond the frozen null at 5%.
4. **Can we build on it?** The declared rule was rebuilt and tested. **No further strategy development or current
   portfolio placement is justified under this preregistration.** Both the filter and timing controls fail;
   do not rescue with new caps, sides, clocks, sizing or a different VWAP. Retain the reproducible result and
   execution lessons. Native trade matching would resolve implementation questions, not erase this failed trial.

## Rule as tested

The fixed source settings are unchanged. OR is wall NY 09:30–09:45. Signals are completed five-minute closes
NY 09:50–12:00 inclusive, direction allowed only by all three strictly same-colour OR candles, strict outside-OR
and correct-VWAP-side tests. The signal-close stop fraction must be <1%. Fill at next one-minute OPEN plus adverse
two ticks; stop absolute opposite OR; target 1.5R from actual slipped fill, rounded outward to a 0.25-point tick.
Entry-bar protection is active. Target requires one tick through. Market/stop fills are adversely slipped.
Remaining positions flatten at wall 15:58 NY (CT 14:59 close-stamped bar's OPEN, before its range).
Source intraminute path is O-L-H-C for up/doji, O-H-L-C for down bars. There were
{audit['same_bar_stop_target_collisions']} primary stop/target collision bars in this design ledger; this alone
does not establish tick/native fill parity. No PowerLanguage/live code was written.

## Standalone design results

Design calendar 2018-01-01 through 2022-12-31; actual primary fills {t.date.min()} through {t.date.max()}.
Exactly 1 MNQ valuation ($2/point), no compounding or risk sizing. Returns below are conditional on resolved
full scan/holding paths. Annual/Sharpe use 252 resolved-session days; excluded dates are not treated as flat.

{mt}

{yt}

Primary costs: quote-reference gross {usd(s['gross'])} minus {usd(s['commission'])} commissions and
{usd(s['slippage'])} market/stop slippage = **{usd(s['total'])} net**. $1.24 RT commission, 2 ticks ($1) per
market/stop fill, no target slippage; no second spread charge. Gross uses the same fill-anchored target as the
costed ledger, not a separately recomputed zero-cost target. Extra-cost breakeven is {usd(s['avg'])}/trade.
The author's $1.04 RT fee on the same ledger gives {usd(s['author_fee_total'])}.
Exact four-tick execution with rebuilt targets gives **{usd(r['exact_4tick_stress']['total'])}** net;
fixed-ledger extra-slippage sensitivity is separately {usd(s['fixed_ledger_stress_total'])}.
Do not conflate the two stresses. MNQ averages x10 are mechanical NQ-equivalent dollar scales, not native NQ fees/fills.

Exit counts: {int((t.kind==1).sum())} target, {int((t.kind==0).sum())} stop, {int((t.kind==2).sum())} time.
Both sides stay visible; no long-only selection is authorized after whole-rule failure.

## Controls and gate disposition

The primary passes the cheap gate: >=80 trades, positive net, t>=2, positive exact four-tick stress, >=1,000 resolved days.
It fails the complete design gate:

{ft}

The nested filter removes {removed['trades']} trades that **earned {usd(removed['total'])}**, averaging
**+{usd(removed['avg'])}** (t={removed['t']:.2f}), rather than losing money. It cuts net profit as well as exposure.
Among 1,000 matched retained-count random subsets, upper-tail profit p={f['p_profit']:.4f}, and lower-tail
drawdown p={f['p_dd']:.4f}; it does not beat 95% on DD. Actual GreenORB can wait for a different entry, so it is
not the nested subset. Our first-break no-colour comparator is limited to one trade/day; the author's switch-off
code can trade once per direction. We do not claim to reproduce that ablation's dollars.

Random-side 1,000 draws: p={r['placebo_p']['side']:.4f}, PASS at 5%. Random-time 1,000 draws:
**p={r['placebo_p']['time']:.4f}, FAIL**. Both use primary dates and inherited risk distances, 1.5R/time/path exits;
no alternative null draw is selected as a strategy. Full null totals and subset draws are saved.

Historical shared selection ledger: 274 items/1,226 variants before this upload, preserved. Five local definitions
executed, including both null families; no parameter search. Primary t={s['t']:.2f} is below the broader
item-adjusted bar {s['trials_t_bar']:.2f}; DSR={s['dsr']:.3f}. The bounded published-rule exception still requires
clean controls, which this rule lacks. Cost sensitivities/descriptive sides/years are retained, not hidden.

## Resampling and risk diagnostics

{bttext}

Design-only trade bootstrap, 10,000 draws: total 5th/50th/95th percentiles
{usd(mc['trade']['total_p5'])}/{usd(mc['trade']['total_p50'])}/{usd(mc['trade']['total_p95'])};
95th-percentile DD {usd(mc['trade']['dd_p95'])}, 99th {usd(mc['trade']['dd_p99'])}.
The actual DD's rank is {mc['trade']['dd_rank']:.1%}; a middle rank describes ordering, not evidence that the
strategy was unselected or has an edge. One-year, 252-resolved-session, 10-day-block simulation, 5,000 draws:
net 5th/50th/95th {usd(mc['daily']['pnl_p5'])}/{usd(mc['daily']['pnl_p50'])}/{usd(mc['daily']['pnl_p95'])},
P(loss) {mc['daily']['p_loss']:.2%}, DD95 {usd(mc['daily']['dd_p95'])}. Diagnostic P(hitting $2,000 EOD trail)
{mc['daily']['p_trail_hit']:.2%} is **not** an evaluation pass rate or funded payout/blowup result: it omits
account portfolio marks, payouts and actual rule chronology. No allocation inference is earned.

## Current-plan destinations

Read-only plan snapshot refreshed at Claude `7a42ea76c62838109d45d168887f57a922933ef2`:
[manifest](../inputs/greenorb/plan_snapshot/manifest.json). ONB was prespecified as the replacement slot,
based on opening-breakout overlap. Current funded 50K T_ONESIDE/OTV changes and the personal 19-piece roster
were not replaced by an old published benchmark. No account-return simulations were run.

{homes}

This is an eligibility rejection after failed design controls, **not measured damage to all five portfolios**.
2023+ historical validation, independent raw-spec return rebuild, account BASE/ADD/REPLACE/EMPTY and MultiCharts compilation
were not earned. Do not fabricate those results to complete a table. No current portfolio/plan was modified.

## What could make this wrong

- **Data/proxy:** {r['data']['resolved_days']} resolved design paths out of {r['data']['total_weekdays']} weekdays;
  {r['data']['unknown_days']} unresolved/short paths excluded, never zero-filled. This includes important 2020
  stress dates March 9, 12, 16, 18 as well as holidays and isolated gaps. Positive observed-sample returns do not
  establish profitability across those omitted regimes. Exact dates are in coverage/audit artifacts.
- **VWAP:** {r['data']['proxy_overnight_missing_days']} resolved days have at least one missing expected overnight
  prefix minute. Available-bar NQ weights are a disclosed proxy, not full native MNQ VWAP. Exported Ticks may be
  trade volume or tick count depending on unavailable chart settings. No missing true volume is assumed zero.
- **Instrument/roll:** NQ and MNQ can differ in volumes and short-term prints. Early design dates precede MNQ
  launch. Flat intraday positions do not remove roll-splice effects on overnight VWAP or percentage-level filters.
- **Engine:** indicator endpoints/reset behavior and base/five-minute callback ordering are not supplied. At 09:45,
  bias can depend on whether the newest five-minute candle reached the buffer before the one-minute callback.
  We implement the prose's intended three opening bars, not assert exact callback parity. Author live claims and
  public run ledger were not independently accessed. Original optional limit-entry mode was not tested.
- **Statistics:** all author history was selected; our recent history is already seen. Rare trades and broad
  ORB-related research history weaken discovery claims. No new independent verification occurred.

## Audit, retained execution lessons and next action

Synthetic mechanics passed before returns: entry-bar stop, source colour-path ordering, strict target
trade-through, adverse stop gap and time-open exit. Maker raw-CSV audit independently of Grid24 calculation
reconciled all {len(t)} saved primary events' OR colours, stops, first qualifying clocks and next opens.
Cash sums, commissions, slippage, tick-rounded targets and trade/daily totals reconcile. These are maker
implementation checks, not independent economic verification or native fills.

Execution library: [E35](../EXECUTION_REFERENCES.md#e35--greenorb-fill-anchored-targets-engine-callbacks-and-source-parity),
building on E09/E18/E19. A fill-anchored R target must be rebuilt under changed slippage; callback clocks and
native-volume/session definitions matter. Keep those lessons even though no strategy advances.
No TODO promising-strategy entry: this tested proxy fails precommitted controls, and missing native inputs alone
do not establish a promising new unverified strategy. No rescue search or later-stage returns.

Reproduce from repository root with the configured Python:
```
/workspace/venvs/thebeginning/bin/python analysis/codex_greenorb.py synthetic
/workspace/venvs/thebeginning/bin/python analysis/codex_greenorb.py design
/workspace/venvs/thebeginning/bin/python analysis/codex_greenorb_report.py
```
The source test is frozen at preregistration commit above; rerunning it is an implementation reproduction,
not an unseen trial. Inputs/engine hashes and dependency versions are saved. User handoff to Claude:
`agents/codex/results/greenorb_20261030.md`. Independent verification remains pending.
'''
    REPORT.write_text(report)
    dump('artifact_manifest.json',dict(preregistration_commit=audit['preregistration_commit'],
        return_code_sha256=frozen,report_code_sha256=sha(__file__),
        files=[dict(path=str(p.relative_to(ROOT)),sha256=sha(p))for p in sorted(OUT.iterdir())
               if p.is_file() and p.name!='artifact_manifest.json'],report_sha256=sha(REPORT)))
    print('PASS: accounting, clocks, source-feature checks; report saved:',REPORT)

if __name__=='__main__':main()
