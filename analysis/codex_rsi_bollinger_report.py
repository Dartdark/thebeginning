"""Report and chart from frozen GC/NQ RSI/Bollinger design outputs."""
import os
os.environ.setdefault('MPLCONFIGDIR','/tmp/codex_rsi_mpl')
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import codex_rsi_bollinger_screen as S


def money(v):return ('-$' if v<0 else '$')+f'{abs(v):,.2f}'


def main():
    p=S.OUT;m=pd.read_csv(p/'metrics.csv')
    gates=json.loads((p/'design_gates.json').read_text());manifest=json.loads((p/'manifest.json').read_text())
    fig,axes=plt.subplots(2,2,figsize=(12,7),sharex='col',gridspec_kw={'height_ratios':[2,1]})
    sections=[]
    for k,(market,(pv,tick,cost,through)) in enumerate(S.SPECS.items()):
        rows=m[(m.market==market)&(m.variant=='primary')&(m.period=='2018-22')]
        row=rows[rows.side=='all'].iloc[0]
        stress=m[(m.market==market)&(m.variant=='stress')&(m.period=='2018-22')&(m.side=='all')].iloc[0]
        t=pd.read_csv(p/f'{market}_trades_primary.csv')
        d=pd.read_csv(p/f'{market}_daily_primary.csv',index_col=0,parse_dates=True)
        b=pd.read_csv(p/f'{market}_bootstrap.csv');bs=b[(b.side=='all')&(b.metric=='sharpe')].iloc[0]
        metrics_rows=[]
        for z in rows.itertuples():
            metrics_rows.append(f'| {z.side} | {z.trades} | {z.win:.1%} | {money(z.avg)} | {z.t:.2f} | {z.sharpe:.2f} | {z.sortino:.2f} | {z.profit_factor:.2f} | {z.calmar:.2f} | {z.ulcer:.2f} | {money(z.max_dd)} |')
        annual=m[(m.market==market)&(m.variant=='primary')&m.period.ne('2018-22')].pivot(index='period',columns='side',values='total')
        years=['| '+str(y)+' | '+' | '.join(money(annual.loc[y,s]) for s in ['all','long','short'])+' |' for y in annual.index]
        eligibility=pd.read_csv(p/f'{market}_eligibility.csv')
        erows=['| '+z.variant+' | '+str(z.signal_hours)+' | '+str(z.missing_activation)+' | '+str(z.unfilled)+' | '+str(z.invalid_bracket)+' |' for z in eligibility.itertuples()]
        hurdle=2*row.trade_sd/np.sqrt(row.trades)
        failed=', '.join(c for c,v in gates[market].items() if c not in ['pass','holdout_opened'] and not v)
        concentration=(f'The largest win, {money(t.net.max())}, contributes {t.net.max()/t.net.sum():.1%} of total net; '
          f'the largest loss is {money(t.net.min())}. This is concentration reporting, not a rule that removes trades.'
          if t.net.sum()>0 else f'The largest loss is {money(t.net.min())}.')
        sections.append(f'''### {market}: design gate FAIL

| Side | Trades | Win | Net/trade | t | Sharpe | Sortino | PF | Calmar | Ulcer | Max daily DD |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
{chr(10).join(metrics_rows)}

Gross {money(t.gross.sum())}; net {money(t.net.sum())}; average gross {money(row.gross_avg)} versus
{money(cost)} costs. Double costs: {money(t.net.sum()-len(t)*cost)}. Stress: {int(stress.trades)} trades,
{money(stress.total)} net, t {stress.t:.2f}. Mean holding time {row.mean_holding_hours:.1f} hours;
longest {t.hours.max():.1f} hours. Terminal open positions: {int(t.terminal.sum())}.

Actual closed-trade SD {money(row.trade_sd)} implies an approximate t=2 net-mean hurdle of {money(hurdle)},
against observed {money(row.avg)}. Independence is only an approximation; small support does not become reliable
because the win rate is high. Failed gates: `{failed}`. Do not promote or select a side-only rescue.

Calendar-year marked-to-market net (cross-year positions contribute to each holding year's marks):

| Year | Combined | Longs | Shorts |
|---|---:|---:|---:|
{chr(10).join(years)}

10-session-block design bootstrap 90% daily-Sharpe interval: [{bs.p5:.2f}, {bs.p95:.2f}].
Conditional random-side p={manifest[market]['conditional_side_p']:.3f} for at least the observed net dollars.
{concentration}

Pre-return opportunity audit; these are all signal hours, including those when an existing position would block
entry. Unfilled counts are for the prescribed direction, conditional on an observed activation minute. They are
not executed-trade counts and do not include subsequent single-position blocking. No wrong-side brackets occurred.

| Variant | Signal hours | Missing activation minute | No strict limit fill | Invalid bracket |
|---|---:|---:|---:|---:|
{chr(10).join(erows)}
''')
        for side,label,color in [('all','Combined','#263b65'),('long','Longs','#1f8b67'),('short','Shorts','#b24a4a')]:
            axes[0,k].plot(d.index,d[side].cumsum(),label=label,color=color,lw=1.2)
        eq=d['all'].cumsum();peak=np.maximum.accumulate(np.r_[0.,eq.to_numpy()])[1:]
        axes[1,k].fill_between(d.index,eq-peak,0,color='#b24a4a',alpha=.45)
        axes[0,k].set_title(f'{market}: one full contract, fixed rules, 2018–22')
        axes[0,k].legend(frameon=False,fontsize=9);axes[0,k].axhline(0,color='gray',lw=.6)
        axes[0,k].set_ylabel('Cumulative net $');axes[1,k].set_ylabel('Daily drawdown $')
        for ax in axes[:,k]:ax.grid(alpha=.2)
    fig.tight_layout();fig.savefig(p/'design_equity.png',dpi=160);plt.close(fig)
    primary=m[(m.variant=='primary')&(m.period=='2018-22')&(m.side=='all')].set_index('market')
    gc,nq=primary.loc['GC'],primary.loc['NQ']
    report=f'''# RSI/Bollinger on gold and NQ: REJECT — neither passes the frozen design screen

Summary: Tested the uploaded hourly RSI/Bollinger rules separately on GC and NQ, 2018–22, with overnight holds.
Gold: {int(gc.trades)} trades, {money(gc.total)} net, t {gc.t:.2f}; NQ: {int(nq.trades)} trades, {money(nq.total)} net, t {nq.t:.2f}.
NQ's positive total is weak evidence: daily Sharpe {nq.sharpe:.2f}, max daily drawdown {money(nq.max_dd)} per full contract.
Both fail the >=30-trade and t>=2 gates; delayed/stricter fills do not rescue the evidence. 2023+ stays unopened.
Do not advance this tested version to live or sizing; the video's crypto results are not futures validation.

Plan: [`rsi_bollinger_screen.md`](../plans/rsi_bollinger_screen.md), committed **d299ce1 before returns**.
Evidence: [`rsi_bollinger_standalone.md`](../evidence/rsi_bollinger_standalone.md).
Scripts: `analysis/codex_rsi_bollinger_screen.py`, `analysis/codex_rsi_bollinger_report.py`.
Outputs: `analysis/outputs/codex_rsi_bollinger_screen/`. Trials: **4 market/execution combinations; no search**.

## Rule (as tested)

Hourly decisions. Four-hour RSI(14)>70 for longs / <30 for shorts; price above/below four-hour Supertrend(10,3).
ADX(14)>20 hourly and >40 four-hour on both sides. Passive entry at the hourly lower/upper Bollinger(20,2)
band. Cancel/refresh pending orders each hour. At fill, recompute hourly ATR and opposite band using only the
visible forming hour, set a six-ATR stop and fixed opposite-band target. No trailing, moving target or time exit.
The supplied class executes the signals and on_open_position brackets; original source bytes are preserved.

Primary activation next minute, GC one tick / NQ one point of trade-through for entry and target. Stress activation
one minute later and double trade-through. All levels rounded to contract ticks; no favorable limit improvement
is credited. The minute OHLC nearest-extreme path determines ambiguity. Only the path after entry can trigger
its brackets. Opening gaps honor an already-resting stop/target before later extremes. The existing grid._walk
is reused with causal entry-path and carried-open extensions. Costs: GC $27.25 / NQ $17.25 per full-contract round
trip, including conservative slippage charged on passive fills as well. These are assumed research costs.

Fixed one GC or one NQ isolates the edge; this is an explicit adaptation of the source's crypto quantity helper
followed by times-five sizing. It does not reproduce either the video equity curve or a 3%-risk personal account.
No risk sizing, compounding, micro-contract rounding or margin sufficiency was inferred from these results.

Only 2018–22 minute files were opened for this RSI screen. The separate gold breakout task read 2017–22.
Both RSI markets start with 2018 data, warm up 240 visible four-hour and hourly bars and first become eligible
at **2018-02-23 13:00 UTC**. Dates before that contain no strategy trades. Continuous exports are CT close-stamped;
subtract one minute, convert DST-aware to UTC, aggregate observed UTC-clock hours. The partially formed current
four-hour candle is visible; its future extrema/close are never visible. Closures are absent observations.

## Results

All figures are per fixed full contract, not per micro and not an account-sizing recommendation. Daily marked
P&L includes unrealized changes across holding days. Maximum drawdown here is on daily marks; intraday exposure
can be worse. $50k is only the denominator for Ulcer/annualized reporting. PF, win rate and t use closed trades;
daily risk metrics use marked equity. Full side/year/stress tables are retained in `metrics.csv`.

{chr(10).join(sections)}
![Frozen GC and NQ equity and daily drawdowns](../../../analysis/outputs/codex_rsi_bollinger_screen/design_equity.png)

2023 onward was **not opened** because both cheap design gates failed. No historical-replication table is fabricated.
The failed gate stops optimization, alternative thresholds, side-only versions, account sizing and forward promotion.

## Placebos and account level

Each market has 1,000 full single-position random-side replays at the original signal opportunity hours. Opposite
sides use their own band limit and fill-time ATR/target, with the same expiry, costs and execution. They can have
different trade counts, as a different limit may not fill. This is a conditional directional comparison, not an
independent test of timing. Both reported p-values and bootstrap intervals are diagnostic, not evidence that the
author's prior research/search is absent. A block bootstrap with so few trade episodes is itself uncertain.

No funded addition/replacement bench or Apex blow-up claim: the rules hold overnight and failed their edge gates.
No personal-account capital or compound-return estimate was run. Removing a formal trailing drawdown limit
does not remove losses, gap exposure or margin calls. Portfolio occupancy was not used to select test events;
joint portfolio diversification remains unmeasured, and GC/NQ trades were not pooled as independent observations.

## What could make this wrong

- **Different market and engine.** The video tests BTC and then ETH/DOGE, not futures. The exact original Jesse
  release and venue data are unknown. This uses pinned official Rust 1.3.1 kernels / SDK reference
  `9a3ebe075d9d0af5f012f921f46c2286f234af68` through a research adapter, not a full Jesse engine reproduction.
- **Small, selected video sample.** The transcript's final single-asset example reports 37 BTC trades over roughly
  3.5 years after inspecting sizing and correcting the short-direction bug. Adding correlated coins yields 75
  trades in the video; that does not establish 75 independent risk episodes or validate the GC/NQ transfer.
  The author explicitly says the fivefold quantity multiplier no longer preserves 3% risk. High win rates alone
  do not establish expectancy: this GC version wins about 64% and still loses overall.
- **Fills.** No quote, queue-position or tick-order history was supplied. The required trade-through, adverse costs
  and activation stress are conservative OHLC assumptions, not verified live fills. ATR/bands at fill include only
  a reconstructed observable path prefix; actual intraminute arrival order can differ from that path.
- **Continuous data.** Roll/back-adjustment provenance and contract-level executable quotes remain unverified.
  Large moves were not removed to improve the result; roll or missing-minute effects can change multi-day P&L.
  Grid24 drops duplicate date/time input rows; manifests' duplicate counts refer to the later UTC-observation check.
- **Adaptations.** Crypto quantities become one full futures contract, prices are tick-rounded, and the market
  calendar follows owned observations. The undefined watch_list.bbw UI call is not invoked. These choices are
  disclosed and frozen, not claims of a repaired production strategy or video-result reproduction.

## Verification and reproducibility

Source-method fixtures check both entry directions, cancellation and frozen brackets. Execution fixtures check
strict entry trade-through, hourly expiry, exclusion of a target hit before entry, stop protection on the entry
minute and stop/target priority on opening gaps. Prefix rebuilds check both an active exact four-hour boundary
and a subsequent partial four-hour bucket against full-history decisions. All passed; zero invalid brackets.
The carried-target gap guard was added during implementation verification; all four variants and controls were
rerun under the same frozen rule. This is a correctness fix, not a selected alternate strategy.

The manifest records all input SHA256 values and first warm-up time; the pre-return audit records eligibility
before return replay. Planning power arithmetic uses declared SD assumptions and is saved separately from actual
trade SD. Reproduction hashes and dependency versions are in `reproduction.json`; seed 314159.

```bash
/workspace/venvs/thebeginning/bin/python analysis/codex_rsi_bollinger_screen.py
/workspace/venvs/thebeginning/bin/python analysis/codex_rsi_bollinger_report.py
```

## Differences between MultiCharts code and the test

No MultiCharts strategy or live files were written. This is a personal-account research adaptation with overnight
holds, so it cannot be copied unchanged into the current intraday Apex plan. Send this result to Claude for review;
the tested versions fail and need no live implementation.
'''
    (S.ROOT/'agents/codex/results/rsi_bollinger_screen.md').write_text(report)
    repro_path=p/'reproduction.json';repro=json.loads(repro_path.read_text())
    repro['code_hashes']['analysis/codex_rsi_bollinger_report.py']=S.sha(__file__)
    repro_path.write_text(json.dumps(repro,indent=2)+'\n')


if __name__=='__main__':main()
