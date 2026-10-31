"""Execution fixtures, frozen-output tables and chart for the gold design screen."""
from pathlib import Path
import json
import hashlib
import os
from importlib.metadata import version
import numpy as np
import pandas as pd
os.environ.setdefault('MPLCONFIGDIR','/tmp/codex_xau_mpl')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import codex_xau_st_break_free as X

OUT=X.OUT


def checks():
    day=np.zeros(3,dtype=np.int64)
    # Signal after the first minute; next-minute long stop is 100 - 3*1 = 97.
    f=np.array([[60_000,0,100,1,1,1,1,40]],float)
    a=np.array([[0,100,100,101,99,1],[60_000,100,96,101,95,1],[120_000,96,96,97,95,1]],float)
    t,d=X.replay(a,f,day,1,0)
    assert len(t)==1 and t[0,7]==0 and t[0,4]==97
    assert np.isclose(d.sum(),-327.25)
    # Carried bracket must gap at 90, not sell retroactively at the 97 stop.
    b=a.copy();b[1]=[60_000,100,100,101,99,1];b[2]=[120_000,90,91,92,89,1]
    t,d=X.replay(b,f,day,1,0)
    assert len(t)==1 and t[0,4]==90 and np.isclose(d.sum(),-1027.25)
    # Delayed entry would already be through its frozen stop: reject stale order.
    t,d=X.replay(b,f,day,1,0,60_000)
    assert len(t)==0 and np.isclose(d.sum(),0)
    # A short target at 95 requires trade-through, not an exact touch.
    f[0,5]=-1
    c=a.copy();c[1]=[60_000,100,95,101,95,1];c[2]=[120_000,95,96,97,95,1]
    t,d=X.replay(c,f,day,1,0)
    assert len(t)==1 and t[0,7]==2
    c[1,4]=94.8
    t,d=X.replay(c,f,day,1,0)
    assert len(t)==1 and t[0,7]==1 and t[0,4]==95
    return dict(entry_bar_protection=True,gap_fills_at_open=True,stale_delayed_order_skipped=True,
                target_touch_insufficient=True,target_trade_through_fills=True)


def input_eligibility():
    a,_=X.load_design()
    f=pd.read_csv(OUT/'decisions_design.csv')
    out=[]
    for variant,delay in [('primary',0),('delay_1m',60_000)]:
        trades=pd.read_csv(OUT/f'trades_{variant}.csv')
        ent=pd.to_datetime(trades.entry_time).astype('int64').to_numpy()//1_000_000
        ex=pd.to_datetime(trades.exit_time).astype('int64').to_numpy()//1_000_000
        actual=set(trades.entry_i.astype(int))
        start=int(pd.Timestamp('2018-01-01',tz='America/Chicago').timestamp()*1000)
        missing=stale=valid=0
        for row in f.itertuples():
            tm=int(row.decision_ms)
            if tm<start or row.signal==0:continue
            k=np.searchsorted(ent,tm,side='left')-1
            if k>=0 and ex[k]>tm:continue
            due=tm+delay;j=np.searchsorted(a[:,0],due)
            if j==len(a) or int(a[j,0])!=due:
                missing+=1;continue
            stop=row.close-row.signal*row.atr4*(3 if row.signal==1 else 4)
            if (row.signal==1 and a[j,1]<=stop) or (row.signal==-1 and a[j,1]>=stop):
                stale+=1;continue
            assert j in actual,('Unexplained eligible entry mismatch',variant,tm,j)
            valid+=1
        assert valid==len(actual),(variant,valid,len(actual))
        out.append(dict(variant=variant,flat_signal_opportunities=valid+missing+stale,
                        missing_entry_minute=missing,stale_stop=stale,executed=valid))
    return out


def main():
    verification=checks();verification['entry_eligibility']=input_eligibility()
    (OUT/'execution_verification.json').write_text(json.dumps(verification,indent=2)+'\n')
    m=pd.read_csv(OUT/'metrics.csv');d=pd.read_csv(OUT/'daily_primary.csv',index_col=0,parse_dates=True)
    t=pd.read_csv(OUT/'trades_primary.csv');gate=json.loads((OUT/'design_gate.json').read_text())
    manifest=json.loads((OUT/'manifest.json').read_text())
    total=m[(m.variant=='primary')&(m.period=='2018-22')]
    annual=m[(m.variant=='primary')&m.period.ne('2018-22')].pivot(index='period',columns='side',values='total')
    b=pd.read_csv(OUT/'design_bootstrap.csv')
    # Reproducible planning arithmetic; assumptions are not observed trade SD.
    p=pd.DataFrame([dict(n=n,assumed_sd=sd,net_hurdle=2*sd/np.sqrt(n),
        gross_hurdle=2*sd/np.sqrt(n)+X.COST) for n in [50,100] for sd in [1000,2000]])
    p.to_csv(OUT/'planning_power.csv',index=False)
    fig,(ax,ddax)=plt.subplots(2,1,figsize=(10,6),sharex=True,gridspec_kw={'height_ratios':[2,1]})
    for c,label,color in [('all','Combined','#263b65'),('long','Longs','#1f8b67'),('short','Shorts','#b24a4a')]:
        ax.plot(d.index,d[c].cumsum(),label=label,color=color,lw=1.2)
    eq=d['all'].cumsum();peak=np.maximum.accumulate(np.r_[0.,eq.to_numpy()])[1:]
    ddax.fill_between(d.index,eq-peak,0,color='#b24a4a',alpha=.45)
    ax.axhline(0,color='gray',lw=.5);ax.legend(frameon=False,ncol=3)
    ax.set_title('XAUSTBreakFree defaults — GC futures adaptation, 2018–22')
    ax.set_ylabel('Cumulative net $ / GC');ddax.set_ylabel('Drawdown $ / GC')
    for a in [ax,ddax]:a.grid(alpha=.2)
    fig.tight_layout();fig.savefig(OUT/'design_equity.png',dpi=160);plt.close(fig)
    def money(v):return ('-$' if v<0 else '$')+f'{abs(v):,.2f}'
    rows=[]
    for z in total.itertuples():
        rows.append(f'| {z.side} | {z.trades} | {z.win:.1%} | {money(z.avg)} | {z.t:.2f} | {z.sharpe:.2f} | {z.sortino:.2f} | {z.profit_factor:.2f} | {z.calmar:.2f} | {z.ulcer:.2f} | {money(z.max_dd)} |')
    year_rows=['| '+year+' | '+' | '.join(money(annual.loc[year,c]) for c in ['all','long','short'])+' |' for year in annual.index]
    sharpe=b[(b.side=='all')&(b.metric=='sharpe')].iloc[0]
    a=total[total.side=='all'].iloc[0]
    delay=m[(m.variant=='delay_1m')&(m.period=='2018-22')&(m.side=='all')].iloc[0]
    text=f'''# Uploaded gold breakout: REJECT — fixed-default GC design screen fails

Summary: Tested the supplied XAUSTBreakFree defaults on GC futures, 2018–22, with overnight holds.
{int(a.trades)} trades: gross {money(t.gross.sum())}, net {money(t.net.sum())}, PF {a.profit_factor:.2f}, t {a.t:.2f}.
Marked daily Sharpe {a.sharpe:.2f}; max drawdown {money(a.max_dd)} per fixed one GC; only two positive years.
One-minute delay net {money(delay.total)}. Registered design gate fails; 2023+ remains unopened.
Reject further work on this tested version; RSI/Bollinger remains queued separately. No live changes.

Plan: `agents/codex/plans/xau_st_break_free_screen.md`, **498e12f**.
Evidence: [`xau_st_break_free.md`](../evidence/xau_st_break_free.md).
Scripts: `analysis/codex_xau_st_break_free.py`, `analysis/codex_xau_st_break_free_report.py`.
Outputs: `analysis/outputs/codex_xau_st_break_free/`. Trials: **2 execution variants; 0 parameter searches**.

## Rule (as tested)

One-hour GC breakouts of the prior 85 session-hour high/low, gated by four-hour Supertrend 24/4, EMA 10 and
ADX 10 long / 15 short. Long stop 3×ATR4 and trail 6.5×ATR4; short stop 4×ATR4, trail 3.5×ATR4 and target
5×ATR4. Exit-on-flip is zero. ATR uses period 14. All supplied defaults remain fixed; no optimization/DNA was supplied.

Signal methods are executed from the preserved class using official Rust indicators. Four-hour anchor visibility
matches the source's literal `[:-1]`, including discarding the just-completed bucket on a boundary. Hourly channel
excludes the current hour. UTC clock buckets, real CT→UTC conversion, New York schedule and observed bars only.
Entry is next-minute open, bracket active immediately, hourly trailing changes effective only afterward. Market
closed/missing-entry-minute signals are skipped. Costs are $27.25 per GC round trip, including conservative two-tick
slippage even for targets. Targets require a GC tick of trade-through; gap stops fill at the observed open.

## Results

Fixed one GC, daily marked P&L; $50k is a reporting denominator, not a recommended account balance. These are GC
adaptation results, not reproduced XAU-USD/video returns. Completed-trade means/t and daily risk metrics differ
in aggregation by design. The full year/side tables are in `metrics.csv`.

| Side | Trades | Win | Net/trade | t | Sharpe | Sortino | PF | Calmar | Ulcer | Max DD |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
{chr(10).join(rows)}

Gross average is {money(t.gross.mean())} versus $27.25 costs; commission/slippage total {money(len(t)*X.COST)}.
Double costs on the same trades produce {money(t.net.sum()-len(t)*X.COST)}. Delay variant: {int(delay.trades)}
trades, {money(delay.avg)} net/trade, t {delay.t:.2f}, PF {delay.profit_factor:.2f}. No terminal position remains.
Mean holding duration is {t.hours.mean():.1f} clock hours; this is not an Apex-intraday strategy.

Calendar-year marked-to-market net P&L (a crossing-year trade contributes to each holding year's marks):

| Year | Combined | Longs | Shorts |
|---|---:|---:|---:|
{chr(10).join(year_rows)}

![Design equity and drawdown](../../../analysis/outputs/codex_xau_st_break_free/design_equity.png)

The registered gates requiring t≥2, gross mean ≥1.5×cost, at least three positive years, positive delayed P&L and
positive double-cost P&L all fail; support ≥30 passes. 2023+ is **not opened**. Do not tune thresholds or select
long-only after these results. No frozen-rule holdout, account-sizing study or forward candidate follows a failed gate.

## Placebos and account level

1,000 conditional random-side full single-position replays at the original signal opportunity hours give
p={manifest['conditional_side_p']:.3f} for net dollars at least as large as the tested rule. This controls direction
conditional on those hours, not independent timing skill. No filter/removal comparison was selected.
The design daily ten-session-block bootstrap gives a 90% Sharpe interval [{sharpe.p5:.2f}, {sharpe.p95:.2f}].
Side-specific bootstrap, permutation and closed-trade Monte Carlo outputs are saved; they describe conditional
uncertainty and sequence risk, not proof against the author's unknown prior search (its prompt asks for ≥200 variants).

Personal-account sizing was not run after design failure. Fixed one-GC drawdown is not a 3%-risk account result.
No Apex funded addition/replacement bench: overnight holds are ineligible and the design gate already failed.

## What could make this wrong

- Owned GC is a continuous futures export, not the author's XAU-USD history. Contract-level rollover/adjustment
  provenance and actual executable quotes remain unverified; no large gaps were deleted to improve results.
- Uploaded holiday overrides mostly cover 2026–27. Historical holiday closures enter through absent observed
  minutes; the source's historical provider/holiday agreement was not independently reproduced.
- This is an adapter plus the existing minute walker, not the full Jesse engine. Actual author framework version,
  DNA, spread, market-close entry fills and live partial-bar behavior may differ. The source's literal boundary lag
  was retained; interpreting its comment differently would create another variant, not a correction to this result.
- Fixed one GC isolates the edge before nonlinear risk/cap sizing. No claim is made that the original 3%-risk curve
  or actual MGC commissions were reproduced. Source risk sizing changes trade weights; this unweighted screen
  does not establish its exact compounded outcome.
- Trade t ignores serial dependence; marked daily bootstrap supplies complementary uncertainty. No inference of
  universal failure on every gold venue is made from this bounded diagnostic.

## Implementation verification and code differences

Source SHA256: `{manifest['source_sha256']}`. Data hashes and official reference pin are in `manifest.json`.
Only 2017–22 files were read: {manifest['observed_minutes']:,} observed minutes, zero invalid OHLC rows and zero
duplicate UTC rows. Future-prefix invariance, supplied long/short trailing formulas, entry-bar stop protection,
gap-at-open fills, stale delayed-order rejection and target touch/trade-through fixtures pass. Entry-eligibility
reconstruction matches every replayed entry; skip counts are in `execution_verification.json`.

No MultiCharts code written. Changes from source execution: GC data/point value/tick rounding, fixed one-contract
size instead of source risk sizing, next-minute observed fills instead of decision-close fills, missing/stale-entry
rejection and conservative repository costs/target trade-through. All were specified before returns. The minute
walker was reused and extended for carried-position first-minute gap checks; no shared engine file was changed.

Reproduce with `/workspace/venvs/thebeginning/bin/python analysis/codex_xau_st_break_free.py` then
`/workspace/venvs/thebeginning/bin/python analysis/codex_xau_st_break_free_report.py`.
Requires `jesse-rust==1.3.1` in addition to configured research dependencies; existing versions were not downgraded.

Tell Claude: review `agents/codex/results/xau_st_break_free_screen.md`; **REJECT** the tested GC defaults,
two frozen execution variants, failed 2018–22 gate, 2023+ unopened. RSI/Bollinger is a separate queued task.
'''
    (X.ROOT/'agents/codex/results/xau_st_break_free_screen.md').write_text(text)
    paths=[X.ROOT/'analysis/codex_xau_st_break_free.py',Path(__file__).resolve(),
           *sorted(X.SOURCE.glob('*.py'))]
    reproduction={'python_dependencies':{n:version(n) for n in ['numpy','pandas','numba','scipy','openpyxl','scikit-learn','jesse-rust','matplotlib']},
                  'code_input_sha256':{str(p.relative_to(X.ROOT)):X.sha(p) for p in paths},
                  'holdout_opened':False,'strategy_execution_variants':2,
                  'report_checks':verification}
    (OUT/'reproduction.json').write_text(json.dumps(reproduction,indent=2)+'\n')
    print(json.dumps(verification,indent=2))
    print('Report and plot written; no additional strategy-return variants run.')


if __name__=='__main__':main()
