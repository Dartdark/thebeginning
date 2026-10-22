"""Write the fixed-rule ES reconstruction report from saved screen artifacts."""
import os
os.environ.setdefault('MPLCONFIGDIR','/tmp/codex_davey_mpl')
import json

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

import codex_davey_keltner as S


def money(x):
    return ('-$' if x<0 else '$')+f'{abs(x):,.2f}'


def main():
    p=S.OUT
    m=pd.read_csv(p/'metrics.csv')
    manifest=json.loads((p/'manifest.json').read_text())
    gates=json.loads((p/'design_gate.json').read_text())
    assert not gates['historical_replication_opened']
    t=pd.read_csv(p/'trades_primary.csv',parse_dates=['date'])
    stress=pd.read_csv(p/'trades_two_tick.csv')
    d=pd.read_csv(p/'daily_primary.csv',index_col=0,parse_dates=True)
    f=pd.read_csv(p/'design_decisions.csv')
    checks=json.loads((p/'engineering_checks.json').read_text())
    primary=m[(m.variant=='primary') & (m.period=='2018-22')].set_index('side')
    r=primary.loc['all']
    # Saved-ledger invariants independently verify arithmetic and specification.
    ordered=t.sort_values(['day','j0','j1'],kind='stable')
    prior=ordered.groupby('day').j1.shift()
    assert (ordered.j0>=prior.fillna(-1)).all()
    assert np.allclose(t.net,t.gross-30)
    assert np.allclose(stress.net,stress.gross-55)
    assert np.allclose(t.gross,(t.exit-t.entry)*t.side*50)
    assert np.allclose(t['entry']/.25,np.round(t['entry']/.25))
    assert np.allclose(t.initial_stop/.25,np.round(t.initial_stop/.25))
    assert set(t.date.dt.year)<=set(range(2018,2023))
    assert np.isclose(t.net.sum(),d['all'].sum())
    assert np.allclose(d['all'],d['long']+d['short'])
    decision=f.set_index(['day','j'])
    for z in t.itertuples():
        row=decision.loc[(z.day,z.decision_j)]
        assert row.signal==z.side and z.j0==z.decision_j+1 and bool(row.valid)
        assert z.j1<=row.flat
        expected=np.round((z.entry-z.side*(4 if z.side==1 else 1)*row.atr)/.25)*.25
        assert np.isclose(z.initial_stop,expected)
    saved_checks=dict(no_overlapping_positions=True,ES_costs_and_PnL=True,tick_rounding=True,
                       design_only_dates=True,daily_side_reconciliation=True,
                       original_signal_next_open_and_initial_stop=True,all_positions_intraday=True)
    S.dump(p/'saved_ledger_checks.json',saved_checks)

    fig,axes=plt.subplots(3,1,figsize=(11,9),sharex=True)
    gross=t.groupby('date').gross.sum().reindex(d.index,fill_value=0.)
    ds=pd.read_csv(p/'daily_two_tick.csv',index_col=0,parse_dates=True)
    axes[0].plot(d.index,gross.cumsum(),label='Gross',color='#72839b')
    axes[0].plot(d.index,d['all'].cumsum(),label='Net: $30 costs',color='#263b65')
    axes[0].plot(d.index,ds['all'].cumsum(),label='Net: $55 costs',color='#b24a4a')
    axes[0].set_title('ES reconstruction: 30-minute / momentum 20 / threshold 50, one contract')
    axes[0].set_ylabel('Cumulative $')
    for side,color in [('long','#1f8b67'),('short','#b24a4a')]:
        axes[1].plot(d.index,d[side].cumsum(),label=side.title(),color=color)
    axes[1].set_ylabel('Net by side $')
    eq=d['all'].cumsum().to_numpy();peak=np.maximum.accumulate(np.r_[0.,eq])[1:]
    axes[2].fill_between(d.index,eq-peak,0,color='#b24a4a',alpha=.5)
    axes[2].set_ylabel('Daily drawdown $')
    for ax in axes:
        ax.grid(alpha=.2);ax.axhline(0,color='gray',lw=.6)
    axes[0].legend(frameon=False);axes[1].legend(frameon=False)
    fig.tight_layout();fig.savefig(p/'design_equity.png',dpi=150);plt.close(fig)

    metric_rows=[]
    for side,z in primary.iterrows():
        metric_rows.append(f'| {side} | {int(z.trades)} | {z.win:.1%} | {money(z.avg)} | {z.t:.2f} | '
          f'{z.sharpe:.2f} | {z.sortino:.2f} | {z.profit_factor:.2f} | {z.calmar:.2f} | {z.ulcer:.2f} | {money(z.max_dd)} |')
    annual=m[(m.variant=='primary') & m.period.ne('2018-22')].pivot(index='period',columns='side',values='total')
    year_rows=['| '+str(y)+' | '+' | '.join(money(annual.loc[y,s]) for s in ['all','long','short'])+' |'
               for y in annual.index]
    variant_rows=[]
    for name in ['primary','two_tick']:
        z=m[(m.variant==name) & (m.period=='2018-22') & (m.side=='all')].iloc[0]
        variant_rows.append(f'| {name} | {int(z.trades)} | {money(z.total)} | {money(z.avg)} | {z.t:.2f} |')
    b=pd.read_csv(p/'design_bootstrap.csv');per=pd.read_csv(p/'design_permutation.csv').set_index('side')
    bootstrap_rows=[]
    for side in ['all','long','short']:
        z=b[(b.side==side)&(b.metric=='sharpe')].iloc[0]
        pp=per.loc[side]
        bootstrap_rows.append(f'| {side} | [{z.p5:.2f}, {z.p95:.2f}] | {money(pp.dd95)} |')
    fail=[k for k,v in gates.items() if not v and k not in ['pass','historical_replication_opened']]
    widened=t.stop_widenings.gt(0)
    exit_counts=t.kind.value_counts().to_dict()
    pp=pd.read_csv(p/'conditional_random_side.csv')
    p5,p50,p95=pp.net.quantile([.05,.5,.95])
    report=f'''# Davey-inspired ES momentum/Keltner: REJECT — the chosen reconstruction loses before costs

Summary: Tested one discretionary reconstruction of the user's incomplete ES strategy screenshot, 2018–22.
{int(r.trades):,} trades: gross/trade {money(r.gross_avg)}, net/trade {money(r.avg)}, net {money(r.total)}, t {r.t:.2f}.
Both sides lose and all five design years are negative; two-tick fills and doubled costs also fail.
Stop here: no optimization, 2023+, account bench or live code; this does not refute the author's unknown settings.

Plan: [`davey_keltner_screen.md`](../plans/davey_keltner_screen.md), **{manifest['plan_commit'][:7]} committed before returns**.
Evidence: [`davey_keltner.md`](../evidence/davey_keltner.md).
Scripts: `analysis/codex_davey_keltner.py`, `analysis/codex_davey_keltner_report.py`.
Outputs: `analysis/outputs/codex_davey_keltner/`.
Trials: **2 execution variants of one rule, plus 1 analytic double-cost rescore; 1,000 conditional random-side controls**.

## Rule (as tested)

ES, one full contract; daytime 30-minute bars. Momentum **20 bars both sides**, Keltner **5 bars, ±0.5 ATR**,
threshold **50**. Center SMA5, true-range averages SMA5/SMA15. The screenshot/transcript do not provide the
momentum values, threshold, chart interval/session, exact platform version or order settings. These are explicitly
chosen assumptions, not recovered author settings. At threshold 50, the channel-width term cancels: this buys
below SMA5 when above C[20], sells above SMA5 when below C[20]. Channel rank is not clipped to [0,100].

Next-minute-open market entries/exits, one position, no pyramiding; contrary signals can reverse. Long exits
when rank>50, short when rank<50. Stop initially 4×ATR15 long / 1× short; reset from the entry reference at each
later decision using completed ATR, allowing widening. No profit target. Stop active on the entry minute;
carried gaps fill at the observed open. Repository `grid._walk` traverses minute OHLC; its general fixed-bracket
engine is extended because this rule needs changing stops and indicator exits.

Normal session 08:30–15:00 CT, chart closes 09:00 onward; early-close session ends 11:30 per the repo calendar.
Scheduled exit is the open of the minute stamped 15:00, actual 14:59 CT; early 11:29 CT. This extra intraday exit
is an adaptation: the screenshot contains no scheduled flatten. Only complete observed 30-minute bars inform
decisions; missing bars are not forward-filled. 2017 ES is warm-up only; returns use 2018–22 exclusively.

Costs are $5 ES commission plus $12.50 each market/stop fill: **$30 round trip**. Stress uses two adverse ticks
each way, **$55**. Prices/stops use raw reference levels, costs deducted afterward as in repo convention;
this does not shift stop anchors by the charged entry slippage. No MES fill or capital recommendation is made.

## Results

All amounts are per one full ES with no compounding, leverage scaling, account stop or margin simulation.
Daily P&L is booked on each intraday trade's date; zero on no-trade dates. Initial zero is included for drawdown.
The $50k denominator used by `metrics.perf` is a reporting convention: this loss path crosses zero capital,
so percentage/Ulcer statistics are mathematical diagnostics, not a survivable $50k account simulation.

| Side | Trades | Win | Net/trade | Trade t | Daily Sharpe | Sortino | PF | Calmar | Ulcer | Max daily DD |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
{chr(10).join(metric_rows)}

Combined net daily t **{r.daily_t:.2f}**. Gross total **{money(r.gross_total)}**, commission/slippage
**{money(t.cost.sum())}**, mean hold **{r.mean_minutes:.1f} minutes**, worst trade **{money(r.worst_trade)}**.
Gross means: longs {money(primary.loc['long','gross_avg'])}, shorts {money(primary.loc['short','gross_avg'])}.
The {primary.loc['long','win']:.1%} long win rate still loses money; asymmetric/wide losses matter.
Trades with at least one stop widening: **{int(widened.sum()):,}/{len(t):,} ({widened.mean():.1%})**.
Exit types: stop {exit_counts.get(0,0)}, indicator {exit_counts.get(2,0)}, reversal {exit_counts.get(3,0)},
scheduled flatten {exit_counts.get(4,0)}. All fills remain intraday; missing entry activations {manifest['missing_entry']},
late scheduled exits {manifest['late_flat']}.

Calendar-year net:

| Year | Combined | Longs | Shorts |
|---|---:|---:|---:|
{chr(10).join(year_rows)}

Execution/cost checks (same fixed signal and raw-price path):

| Variant | Trades | Total net | Net/trade | Trade t |
|---|---:|---:|---:|---:|
{chr(10).join(variant_rows)}

Double total primary costs ($60/trade): **{money(manifest['net_if_double_total_cost'])}**.
Observed trade SD {money(r.trade_sd)} gives an approximate t=2 net-mean hurdle
**{money(2*r.trade_sd/np.sqrt(r.trades))}**, versus observed {money(r.avg)}. Trading-day dependence remains relevant.
Failed gates: `{', '.join(fail)}`. The >=100-trade, engineering and no-late-flat gates pass; the economic gates fail.

![Fixed-contract ES gross/net performance and drawdowns](../../../analysis/outputs/codex_davey_keltner/design_equity.png)

**2023+ not opened.** No historical-replication results, side-only rescue or alternative settings were run.
The result rejects these chosen parameters/session; an omitted timeframe or threshold could behave differently.
The screenshot is insufficient to attribute this result to Davey's actual strategy.

## Placebos and account level

1,000 full single-position random-side replays at the original nonzero opportunity decisions, with side-specific
stops/exits unchanged. Conditional p **{manifest['placebo_p']:.3f}** for controls at least as profitable as the
strategy. Control total-net 5/50/95%: {money(p5)} / {money(p50)} / {money(p95)}. Most controls also lose.
Direction randomization can alter holding times/trade counts; this conditions on the original opportunity clock
and does not validate independent timing or remove source selection. It cannot rescue the failed cost screen.

Design diagnostics, 2,000 ten-session-block bootstrap draws and 2,000 daily permutations:

| Side | Daily Sharpe 90% block interval | 95th percentile shuffled daily DD |
|---|---:|---:|
{chr(10).join(bootstrap_rows)}

These are uncertainty diagnostics of the chosen losing rule, not independent confirmation. Bootstrap PF is
daily aggregation (`pf_day`), whereas the main table's PF is per trade. Full metric intervals and permutations
are saved. The bootstrap uses exactly the observed trading dates; main metrics also prepend one zero for DD,
causing an immaterial one-observation difference in annualized point estimates.

No funded addition/replacement/empty-slot bench, Apex Monte Carlo, personal-account sizing or live code:
the cheap edge gate failed. Saved occupancy context was disclosed before testing; candidate events were never
selected for plan-flat dates. Joint losses/diversification remain unmeasured.

## What could make this wrong

- **Reconstruction:** chosen 20/20/50 and 30-minute daytime bars are unknown-author substitutes. Threshold 50
  reduces to a center crossing. No optimization was used to make the result look better. The source's claimed
  post-June 2021 performance is not our independent holdout: parameters and raw ledger were not supplied.
- **Indicators/platform:** SMA Keltner/ATR, observed-bar history, reversals/no pyramiding, tick rounding and
  first-minute protection are frozen research definitions. Official TradeStation/MultiCharts parity remains
  unverified; the screenshot's conditional stop statements may have different entry-bar behavior.
- **Data/fills:** continuous ES roll/back-adjustment provenance and quote-level execution are unverified.
  The audit found partial/absent bars; absent scheduled-flat observations occurred only on dates with zero
  complete RTH bars/signals. No held exit required a late fill. These include an unexplained no-RTH date,
  2020-11-30; it is preserved in `missing_flat_audit.csv`, not silently assigned a profitable trade.
- **Risk:** stop distances can widen and differ 4:1 across sides; one ES is not fit to the Apex trail merely
  because it is the video's baseline. Pre-return median long stop proxy was $2,066.67, 95th percentile $5,493.33.
  Actual worst trade {money(r.worst_trade)}. A stop is not a guaranteed loss cap; actual spreads/slippage can be worse.
- **Prior selection:** 2018–22 overlaps the author's development and many prior repository pattern tests.
  A predeclared reconstruction does not erase that history. A failed arbitrary reconstruction cannot establish
  that every possible implementation fails; no new rule is selected after seeing these outcomes.

## Verification and reproduction

**{len(checks)} engineering checks passed before primary replay**, including entry-minute stops, gaps,
next-open exits, causally updated widening stops, reversal/no pyramiding, missing-entry cancellation,
early flatten, historical-prefix invariance and ES cost scaling. **{len(saved_checks)} saved-ledger check groups**
verify original signal/next-open/initial-stop consistency, tick levels, no overlapping positions, design-only
dates, intraday exits, arithmetic and daily side reconciliation. These are engine checks, not platform parity.

Source/data/code/config hashes and dependency versions are preserved. No shared cache was built or changed.
No live/VPS/broker/API-key access or source-branch push occurred.

```bash
/workspace/venvs/thebeginning/bin/python analysis/codex_davey_keltner.py --run
/workspace/venvs/thebeginning/bin/python analysis/codex_davey_keltner_report.py
```

The optional `--audit` mode rebuilds counts/features/power only, without returns. The committed pre-return
counts and manifest establish what was known before the plan. The return runner checks that the plan content
is committed before executing. No change to the rule or correctness rerun was required after return inspection.

## Differences between MultiCharts code and the test

No new MultiCharts code was written. Relative to the supplied screenshot: missing inputs/chart/session/order
settings are filled explicitly; one-contract/no-compounding sizing retained; scheduled intraday flatten added;
entry-minute stop protection specified; signal/indicator calculations, minute data, gap fills and cost treatment
fixed above. Original source transcript/transcription remain unchanged. Send the result path to Claude for review.
'''
    (S.ROOT/'agents/codex/results/davey_keltner_screen.md').write_text(report)
    repro_path=p/'reproduction.json';repro=json.loads(repro_path.read_text())
    repro['hashes']['analysis/codex_davey_keltner_report.py']=S.sha(__file__)
    S.dump(repro_path,repro)
    print('Report saved; saved-ledger checks passed:',len(saved_checks))


if __name__=='__main__':main()
