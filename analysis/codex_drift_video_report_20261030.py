"""Render the completed frozen video screen; no new returns/account simulations."""
from pathlib import Path
import hashlib,json,platform,subprocess,importlib.metadata
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'analysis/outputs/codex_drift_video_20261030'
RESULT=ROOT/'agents/codex/results/drift_video_20261030.md'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(p,x):Path(p).write_text(json.dumps(x,indent=2,default=str)+'\n')
def money(x):return f'${x:,.2f}'
def table(rows,headers):
    return '\n'.join(['| '+' | '.join(headers)+' |','|'+'---|'*len(headers)]+['| '+' | '.join(map(str,r))+' |' for r in rows])
def main():
    r=json.loads((OUT/'design_result.json').read_text());inv=json.loads((OUT/'design_inventory.json').read_text())
    a=json.loads((OUT/'audit.json').read_text());m=pd.read_csv(OUT/'design_metrics.csv',dtype={'year':str})
    t=pd.read_csv(OUT/'design_trades.csv',parse_dates=['date']);p=pd.read_csv(OUT/'design_placebos.csv')
    prior=json.loads((OUT/'pre_correction_halfday/design_result.json').read_text())
    if r['passed']:raise RuntimeError('This renderer is the failed-screen report, not an account runner')
    if r['source_code_sha256']!=sha(ROOT/'analysis/codex_drift_video_20261030.py'):raise RuntimeError('Code/result mismatch')
    assert abs(r['stress']['gross']-r['stress']['fees']-r['stress']['slippage']-r['stress']['total'])<1e-7
    rows=[]
    for z in m[m.year=='all'].itertuples():
        tt=t if z.side=='all' else t[t.side==(1 if z.side=='long' else -1)]
        rows.append([z.side,z.trades,f'{z.win:.1%}',money(z.avg),money(tt.net_nq.mean()),f'{z.trade_t:.2f}',f'{z.daily_t:.2f}',f'{z.profit_factor:.2f}',f'{z.sharpe:.2f}',f'{z.sortino:.2f}',money(z.max_dd),f'{z.calmar:.2f}',f'{z.ulcer:.2f}'])
    met=table(rows,['Side','Trades','Win','Avg 1 MNQ','Avg NQ fee bridge','Trade t','Daily t','PF','Sharpe','Sortino','Max DD 1 MNQ','Calmar','Ulcer'])
    years=[]
    for y in range(2018,2023):
        x=m[(m.side=='all')&(m.year==str(y))].iloc[0]
        by=lambda s: m[(m.side==s)&(m.year==str(y))].iloc[0]['total']
        years.append([y,int(x.trades),money(x.total),money(by('long')),money(by('short')),f'{x.daily_t:.2f}'])
    yr=table(years,['Year','Trades','Net all 1 MNQ','Long net','Short net','Daily t'])
    controls=[]
    for f,g in p.groupby('family'):
        controls.append([f,len(g),money(g.total.median()),money(g.total.quantile(.95)),money(r['primary']['total']),f'{r["placebo_p"][f]:.4f}'])
    ct=table(controls,['Conditional null','Draws','Median total','95th percentile','Actual total','Empirical p'])
    alt=table([[n,int(r[k]['trades']),money(r[k]['total']),money(r[k]['avg']),f'{r[k]["daily_t"]:.2f}',money(r[k]['max_dd'])] for n,k in [('Primary: two consecutive losses','primary'),('Robustness: two total losses','total_losses'),('Replayed higher-cost primary','stress')]],['View','Trades','Net 1 MNQ','Avg','Daily t','Max DD'])
    cov=pd.read_csv(OUT/'design_coverage.csv')
    missing=', '.join(cov.loc[~cov.eligible,'date'])
    boots=pd.read_csv(OUT/'design_bootstrap.csv');bb=boots[(boots.side=='all')&boots.metric.isin(['sharpe','annual','max_dd'])]
    bt=table([[z.metric,f'{z.actual:,.2f}',f'{z.p5:,.2f}',f'{z.p95:,.2f}'] for z in bb.itertuples()],['10-day block bootstrap, 5,000 draws','Actual','5%','95%'])
    receipt=dict(task='User video Drift VWAP Pullback from5:34',branch='codex/work',
        preregistration_commit=r['prereg_commit'],implementation_correction_commit='3f20093',
        input_period='2018-2022 only',inputs=inv['inputs'],source_transcript_sha256=sha(ROOT/'agents/codex/inputs/drift_video_20261030/transcript.txt'),
        python=platform.python_version(),dependencies={n:importlib.metadata.version(n) for n in ['numpy','pandas','numba','openpyxl','scipy','scikit-learn']},
        script_sha256=r['source_code_sha256'],audit=a['review'],audit_passed=a['passed'],
        candidate_definitions=2,control_families=2,control_draws_each=100,execution_stresses=1,total_definitions=5,
        implementation_runs=2,prior_failed_run_preserved='pre_correction_halfday',
        first_run_primary_unchanged=prior['primary']==r['primary'],recent_tested=False,account_tests_run=False,
        account_inputs_prepared_but_unused=True,signal_seed=301034,bootstrap_seed=301035,
        roster_ref='7a42ea76c62838109d45d168887f57a922933ef2',
        limits=['No author source code/MC parity','NQ continuous-price and volume proxy, not native MNQ fills',
                'Twelve unknown complete-session paths excluded, including March2020 halt dates',
                'Random-time null conditions on complete-day count and side order, not a tradable alternative',
                'No independent blind economic replication or forward result'])
    dump(OUT/'run_receipt.json',receipt)
    dump(OUT/'trial_ledger.json',dict(family='Existing DriftPullback family; not a new scout discovery',
        prior_family='At least15 prior definitions in drift_pullback_test.py; simplifiedv3 also previously tested',
        definitions=[dict(id=1,name='Consecutive-loss primary',selected=True),dict(id=2,name='Total-loss robustness',selected=False),
                     dict(id=3,name='Random-side conditional null',draws=100),dict(id=4,name='Random-time conditional null',draws=100),
                     dict(id=5,name='Higher-fee/tick stress with net-loss-cap replay')],
        implementation_runs=[dict(commit=r['prereg_commit'],status='Half-day cutoff implementation mismatch; failed screen preserved'),
                             dict(commit='3f20093',status='Restored frozen cutoff; no threshold/rule search; failed screen')],
        later_stages='Not earned; no recent or account returns'))
    text=f'''# Video Drift VWAP Pullback: REJECT for current-plan advancement

Summary: The reconstructed video rule is profitable, but earns no portfolio test under the frozen gates.
2018–22, 1 MNQ: {len(t):,} trades, {money(r['primary']['total'])} net, {money(r['primary']['avg'])}/trade, PF {r['primary']['profit_factor']:.2f}.
Daily t {r['primary']['daily_t']:.2f} misses2.5; the prespecified conditional timing null also fails (p={r['placebo_p']['time']:.2f}).
Keep all five current portfolios unchanged; 2023+ and new account simulations were not earned or run.

Plan: [frozen rules](../plans/drift_video_20261030.md), `{r['prereg_commit']}`.
Correction: [documented implementation repair](../plans/drift_video_20261030_implementation_correction.md), `3f20093`.
Scripts: [test](../../../analysis/codex_drift_video_20261030.py), [report](../../../analysis/codex_drift_video_report_20261030.py),
[second-agent audit](../../../analysis/codex_drift_video_audit_20261030.py).
Output: [result](../../../analysis/outputs/codex_drift_video_20261030/design_result.json),
[run receipt](../../../analysis/outputs/codex_drift_video_20261030/run_receipt.json),
[trade ledger](../../../analysis/outputs/codex_drift_video_20261030/design_trades.csv).
Trials:5 definitions, including2 controls with100 draws each;2 implementation runs of the same frozen definitions.
Earlier family trials remain counted; no new scout discovery, reservation, history reset or automation.

## Rule (as tested)

The strategy from5:34 onward is the existing **DriftPullback/VWAP momentum** family, already in TIER_LIST and the
personal capital-expansion bench. This is a video reconstruction, not an exact replication of hidden code.

- NQ, completed15-minute trend state and5-minute triggers. VWAP uses completed15-minute HLC3×volume bars from08:30CT.
- Long:15m close above VWAP, VWAP rising, previous-hour return≥0.1%; shorts mirror the conditions.
- First opposing-color5m bar means a color transition: red after non-red for longs; green after non-green for shorts.
  No VWAP touch or distance threshold. This definition is an explicit assumption.
- Entry next bar open,09:30–14:30CT decisions, flat14:55CT; known half-days11:30last decision/11:55flat.
-80-point stop,40-point long target/50-point short target; entry-bar protection,1-point target trade-through.
-One position, max4trades/day; primary stops after2consecutive net losses. Total-loss interpretation is diagnostic only.

Source timestamps:14:24–16:40 trend,16:46 first-hour wait,17:18–18:37 trigger/next-open,
21:32–23:20 brackets and guards. Transcript's early “50minute” is corrected to15minute later.
The trading-flow explanation and employment/performance statements are source claims, not independently verified facts.

## Results

**Design only:2018–22.**1,247complete cash sessions of1,259(99.05%); no unknown session is zero-filled.
All dollars below are for1MNQ except the separately labeled NQ fee bridge; that bridge applies NQ fees to the same
accepted micro-strategy ledger, not a separately executed NQ strategy. t is also shown by day to avoid treating
several entries on one day as independent sessions. Max DD includes the initial zero equity peak.

{met}

{yr}

{alt}

The alternative was not selected after results. Both daily t values are below2.5; no long-only/short-only rescue was run.
The full per-side/per-year standard metrics are in [CSV](../../../analysis/outputs/codex_drift_video_20261030/design_metrics.csv).
2023+ metrics, bootstrap and account effects are **not available** because the design failed; do not substitute
the video's own results or old family results for this rule's validation.

Cost bridge, primary1MNQ: gross **{money(r['primary']['gross'])}** − fees **{money(r['primary']['fees'])}** −
slippage **{money(r['primary']['slippage'])}** = net **{money(r['primary']['total'])}**.
Fee$1.04RT, one tick($0.50)per market/stopfill; limit target has no separately added market slippage.
Higher-cost replay: fees{money(r['stress']['fees'])}, slippage{money(r['stress']['slippage'])}, net{money(r['stress']['total'])}.
Its daily loss cap uses stressed net outcomes. Primary daily.csv's stress column is only the fixed-primary-ledger
accounting bridge; stress_trades.csv is the separately cap-replayed stress result.
Current net permits about{money(r['primary']['avg'])} extra average cost per trade before arithmetic break-even,
not a guarantee of executable spread/latency capacity.

{bt}

## Placebos and account level

{ct}

Random-side draw directions are independent of source bias; the prospective signal calendar is retained and daily
caps/occupancy replayed. The rule beats this control, which supports directional information in the combined setup.
The random-time control retains each date's **complete-day signal count and side order** while randomizing allowed
slots. This is a **retrospective conditional timing null**; those future daily labels are unavailable for deployment
at earlier randomized times. Its profits must not be advertised as an executable alternative, a causal timing edge,
or proof that random orders outperform a live strategy. The source's first-counterbar timing does not beat this
frozen null, and the independently failed daily-t gate already stops advancement. No replacement control was selected.

Frozen gates:≥500trades PASS; positive native net PASS; daily t≥2.5 **FAIL**;≥4positive years PASS;
positive cost stress PASS; side placebo p≤.05 PASS; conditional-time placebo p≤.05 **FAIL**.

| Current home | Explicit placement verdict | What was actually tested |
|---|---|---|
|50K evaluation|No eligible addition/replacement|Design failed; current account BASE/ADD/REPLACE/EMPTY not run|
|150K evaluation|No eligible addition/replacement|Same design stop; no150K pass-rate claim|
|50K funded|No eligible addition/replacement|No new payout/blow-up/timing simulation|
|150K funded|No eligible addition/replacement|No new150K payout/blow-up/timing simulation|
|Personal A–D/core/full|No eligible addition/replacement|No current19-piece return/DD/capital comparison|

Current roster was checked from the [six-plan snapshot](../inputs/greenorb/plan_snapshot/manifest.json),
Claude7a42ea76c62838109d45d168887f57a922933ef2:50Kfunded uses Tfade instead ofRS_L;150KkeepsRSboth,OT2/ST2;
evaluationVB8/20+ONBADX30+Bridge+EOS; personal19pieces. The conditional replacement was Vault Break, chosen
before outcomes from related-family overlap, not a sweep over convenient replacement slots. Some account-source
ledgers were acquired while design ran, but no candidate account input was loaded or account outcome computed.

**Prior evidence, different definition/book:** the existing v2.1 test reported5,733trades,$56/NQ,t4.0;
its1-point-through view had t3.0. On its old funded roster, ADD1MNQ raised one-year blow-ups3%→13% and cut two-year
payouts$12,436→$11,182. Simplifiedv3 later added personal dollars but reduced return/DD8.3→8.0 on an older17-piece
book. These help identify the repeated family; they are not measurements against today's portfolios or today's rule.
Sources: [old test](../../../analysis/drift_pullback_test.py),
[old output](../../../analysis/outputs/drift_pullback_test_output.txt),
[personal snapshot](../inputs/greenorb/plan_snapshot/personal_strategies/PORTFOLIO.md).

## What could make this wrong

**Implementation and audit:** a second-agent review caught that the first code allowed half-day decisions through11:50,
contrary to the committed11:30rule. The correction was committed before rerunning and preserves every original artifact
under[pre_correction_halfday](../../../analysis/outputs/codex_drift_video_20261030/pre_correction_halfday).
Primary accepted trades and P&L are unchanged; prospective/null schedules can change. Stress fee/slippage display was
also corrected; its economic net calculation was already correct. This is a repair, not a new sample or threshold change.

[Audit receipt](../../../analysis/outputs/codex_drift_video_20261030/audit.json):**{len(a['checks']):,}checks PASS**,
{len(a['sampled_signal_days'])}sampled days/{a['trailing_feature_decisions_checked']:,}independently trailing feature decisions;
all{a['minute_path_checks']['unique_saved_trades']:,}unique saved trade paths checked against raw entries/brackets/earlier hits,
plus cost/cap/daily/side/year reconciliation. This is second-agent implementation/accounting review, not a blind full-universe
economic rebuild, independent MC approval, native MNQ fill verification or forward record.

**Coverage:** unknown dates:{missing}. Several are March2020halt/limit sessions. Excluding them can flatter risk;
the observed DD is not a full-market tail-risk bound. No claim about their unobserved strategy P&L is made.
Continuous NQ history, bar-volume and one-minute path assumptions remain; native MNQ contract IDs/quotes/fills are absent.
No change from1-point researchthrough to0.25was tried to improve results. Calendar helper conservatively treatsJuly3as
early in some years, an existing disclosed limitation. Freeze source/chart/session settings for any future parity request.

**Mechanism:** a VWAP-weighted average is not the price of maximum traded volume. A large proportion of VWAP
algorithms does not demonstrate signed forced flow or future continuation. This is a price/volume pattern test.
Prior family selection and the speaker's2020–24optimization contaminate any claim that our design is pristine discovery.
No new historical validation or future forward return is represented here.

**Prop-firm claim:**49.8%per attempt gives1−(1−0.498)^4=93.65%only for independent equal-probability attempts.
Four copied simultaneous accounts can have essentially the same outcome. OneNQ's80point stop is$1,600against
a50K$2,000trail; a quoted64%hit rate alone cannot establish profitability(40/80long gross breakeven66.67%,
50/80short61.54%). Claimed3.44days must identify whether conditioned on successful attempts. Passing is not a payout.

## Differences between MultiCharts code and this test

No new MultiCharts code written: source code was not supplied and the advancement gate failed.
The archivedv3is a related version with extra distance/timing logic; do not paste it as an exact implementation
of this video.15m-heldbias, HLC3VWAP, color-transition trigger, holiday timing, first-minute eligibility, net loss
counter and immediate protection are disclosed reconstruction choices, not validated matches to the author's engine.
Useful execution lessons merged into[EXECUTION_REFERENCES.md,E09/E18](../EXECUTION_REFERENCES.md).

Reproduce:
```bash
# Use the configured Python and an isolated directory containing only the five hashed2018–22day files.
/workspace/venvs/thebeginning/bin/python analysis/codex_drift_video_20261030.py inventory --data /workspace/drift_video_inputs/design
/workspace/venvs/thebeginning/bin/python analysis/codex_drift_video_20261030.py design --data /workspace/drift_video_inputs/design
/workspace/venvs/thebeginning/bin/python analysis/codex_drift_video_audit_20261030.py
/workspace/venvs/thebeginning/bin/python analysis/codex_drift_video_report_20261030.py
```

For Claude: review`agents/codex/results/drift_video_20261030.md`; no plan allocation/ranking/live change proposed.
'''
    # Readability-only rendering; frozen protocol/code and numbers stay unchanged.
    replacements={'misses2.5':'misses 2.5','Trials:5':'Trials: 5','including2':'including 2','with100':'with 100',
        ';2 implementation':'; 2 implementation','from5:34':'from 5:34','completed15-minute':'completed 15-minute',
        'and5-minute':'and 5-minute','from08:30CT':'from 08:30 CT','Long:15m':'Long: 15m',
        'First opposing-color5m':'First opposing-color 5m','open,09:30–14:30CT':'open, 09:30–14:30 CT',
        'flat14:55CT':'flat 14:55 CT','half-days11:30last decision/11:55flat':'half-days 11:30 last decision / 11:55 flat',
        '-80-point stop,40-point long target/50-point short target':'- 80-point stop, 40-point long target / 50-point short target',
        '-One position, max4trades/day; primary stops after2consecutive':'- One position, max 4 trades/day; primary stops after 2 consecutive',
        'protection,1-point':'protection, 1-point','timestamps:14:24':'timestamps: 14:24','trend,16:46':'trend, 16:46',
        'wait,17:18':'wait, 17:18','“50minute”':'“50 minute”','to15minute':'to 15 minute',
        '**Design only:2018–22.**1,247complete cash sessions of1,259':'**Design only: 2018-01-02–2022-12-30.** 1,247 complete cash sessions of 1,259',
        'for1MNQ':'for 1 MNQ','below2.5':'below 2.5','primary1MNQ':'primary 1 MNQ','Fee$1.04RT':'Fee $1.04 RT',
        'tick($0.50)per market/stopfill':'tick ($0.50) per market/stop fill', 'fees$':'fees $','slippage$':'slippage $',
        'net$':'net $','about$':'about $','gates:≥500trades':'gates: ≥500 trades','**FAIL**;≥4positive':'**FAIL**; ≥4 positive',
        'draws.2023':'draws. 2023','no150K':'no 150K','No new150K':'No new 150K','current19-piece':'current 19-piece',
        '2022(99.05%)':'2022 (99.05%)','1,259(99.05%)':'1,259 (99.05%)','before outcomes':'before outcomes',
        'reported5,733trades,$56/NQ,t4.0':'reported 5,733 trades, $56/NQ, t 4.0','its1-point-through':'its 1-point-through',
        'had t3.0':'had t 3.0','ADD1MNQ':'ADD 1 MNQ','blow-ups3%→13%':'blow-ups 3%→13%',
        'payouts$12,436→$11,182':'payouts $12,436→$11,182','Simplifiedv3':'Simplified v3','return/DD8.3→8.0':'return/DD 8.3→8.0',
        'older17-piece':'older 17-piece','through11:50':'through 11:50','committed11:30rule':'committed 11:30 rule',
        'under[pre_correction':'under [pre_correction','audit.json):**':'audit.json): **','1,339checks':'1,339 checks',
        '40sampled':'40 sampled','2,080independently':'2,080 independently','all2,808unique':'all 2,808 unique',
        'dates:2018':'dates: 2018','March2020halt':'March 2020 halt','from1-point researchthrough to0.25':'from 1-point research trade-through to 0.25',
        'treatsJuly3as':'treats July 3 as',"speaker's2020–24optimization":"speaker's 2020–24 optimization",
        '**Prop-firm claim:**49.8%per':'**Prop-firm claim:** 49.8% per','gives1−':'gives 1−','93.65%only':'93.65% only',
        "OneNQ's80point stop is$1,600against":"One NQ's 80-point stop is $1,600 against",'a50K$2,000trail':'a 50K $2,000 trail',
        'quoted64%hit':'quoted 64% hit','profitability(40/80long':'profitability (40/80 long',
        'breakeven66.67%':'breakeven 66.67%','50/80short61.54%':'50/80 short 61.54%',
        'Claimed3.44days':'Claimed 3.44 days','archivedv3is':'archived v3 is','video.15m-heldbias':'video. 15m-held bias',
        'HLC3VWAP':'HLC3 VWAP','into[EXECUTION':'into [EXECUTION','review`agents':'review `agents'}
    for old,new in replacements.items():text=text.replace(old,new)
    RESULT.parent.mkdir(parents=True,exist_ok=True);RESULT.write_text(text)
    watched=[ROOT/'analysis/codex_drift_video_20261030.py',ROOT/'analysis/codex_drift_video_audit_20261030.py',Path(__file__),RESULT]
    watched+=sorted(p for p in OUT.rglob('*') if p.is_file() and p.name!='artifact_manifest.json')
    dump(OUT/'artifact_manifest.json',dict(files=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p)) for p in watched]))
    print(json.dumps(dict(report=str(RESULT),passed=r['passed'],primary=r['primary'],controls=r['placebo_p']),indent=2))
if __name__=='__main__':main()
