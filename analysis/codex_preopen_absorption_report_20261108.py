"""Report the frozen pre-open design ledgers; no signal generation or return search."""
from pathlib import Path
import json
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'analysis/outputs/codex_preopen_absorption_20261108'
REPORT=ROOT/'agents/codex/results/preopen_absorption_20261108.md'


def table(df,cols):
    def fmt(x):
        if isinstance(x,(float,np.floating)):return f'{x:,.2f}' if np.isfinite(x) else '—'
        return str(x)
    return '| '+' | '.join(cols)+' |\n| '+' | '.join(['---']*len(cols))+' |\n'+'\n'.join('| '+' | '.join(fmt(v) for v in row)+' |' for row in df[cols].itertuples(index=False,name=None))+'\n'


def main():
    p=OUT/'design';r=json.loads((p/'results.json').read_text());m=pd.read_csv(p/'metrics.csv')
    rec=[]
    for file in p.glob('*_trades.csv'):
        t=pd.read_csv(file);d=pd.read_csv(file.with_name(file.name.replace('_trades','_daily')))
        assert np.allclose(t.gross,(t.exit-t.entry)*t.side*20)
        assert np.allclose(t.net,t.gross-t.commission-t.slippage)
        assert np.allclose(t.native_mnq_net,t.gross/10-2.25)
        assert abs(t.net.sum()-d.net.sum())<.005 and abs(t.native_mnq_net.sum()-d.native_mnq_net.sum())<.005
        assert not t.missing_held_closes.sum()
        rec.append({'case':file.stem.removesuffix('_trades'),'trades':len(t),'gross':t.gross.sum(),
                    'commission':t.commission.sum(),'slippage':t.slippage.sum(),'net':t.net.sum(),
                    'native_mnq_net':t.native_mnq_net.sum(),'extra_tick_net':t.extra_tick_cost_net.sum()})
    pd.DataFrame(rec).to_csv(OUT/'cash_reconciliation.csv',index=False)
    controls=pd.DataFrame([{'parent':k,**v} for k,v in r['filter_controls'].items()])
    effects=pd.DataFrame([{'parent':k,**v} for k,v in r['paired_effects'].items()])
    a=json.loads((OUT/'audit/no_return_receipt.json').read_text())
    ex=pd.read_csv(OUT/'audit/exclusions.csv')
    text="""# Pre-open signed-flow absorption: REJECT

Summary: Five transported NQ files verified byte-for-byte;1,755,357 native bars support an exploratory design screen.
The absorption rule loses$6,386.50 per NQ on34trades,t−1.17,PF0.55; one-minute delay loses$7,006.50.
Both long and short sides lose, and every year with an absorption trade loses;2018 has no signals.
Heavy-total-volume comparator earns$37,658,t2.59, but repeats a known T-style mechanism and is not selectable.
No new strategy selected, later-period replay, funded/evaluation/personal bench, PowerLanguage or plan/live change.

Plan: `agents/codex/plans/preopen_absorption_20261108.md`, committed `e2d85b7` before returns.
Evidence: `agents/codex/evidence/preopen_absorption_20261108.md`.
Script: `analysis/codex_preopen_absorption_20261108.py`.
Reporter: `analysis/codex_preopen_absorption_report_20261108.py`.
Output: `analysis/outputs/codex_preopen_absorption_20261108/`.
No-return audit committed `ce84389` before design execution. Five registered definitions: four signal rules
(including three comparators) plus one mandatory delay stress. One eligible new candidate, Absorption.
Keep all prior T/flow searches,18ingredient cases and the failed five-case price-only handoff as selection history.
No implementation rerun, post-result parameter change or side/direction rescue in this study.

## Rule (as tested)

On NQ, use the overnight price move from the first observed bar OPEN after previous17:01 through current
08:28CTclose. Fade that direction. The price-only confirmation requires the last15-minute move08:14–08:28
to stall/reverse relative to the overnight direction. Absorption additionally requires last15-minute signed
aggressor volume to agree with the overnight direction, with absolute signed-volume share at least its own
previous60valid observations' median (minimum20). Today never enters its own median.

The comparator HeavyTotal requires native total night volume>1.4times the previous20valid nights' median.
It is an explicitly TOTAL-volume comparison, not a reconstruction of native PowerLanguage up-tick Volume.
PlainFade trades all admitted nonzero overnight moves. All four share entry/exits/costs/calendar.
Absorption is a pure subset of both PlainFade and PriceOnly on side, entry, exit and net cash.

Feature cutoff08:28close, with a full minute allowed for assumed receipt/processing; enter08:30-labelled
OPEN at08:29civil CT, before the cash bell. Delayed case enters08:31-labelled OPEN at08:30civil CT.
Exit08:45-labelled OPEN at08:44civil CT. The scheduled OPEN exit precedes that bar's intrabar stop.
Stop0.40times mean high-low range of previous20fully observed08:31–15:00RTHsessions, rounded adversely
onto the0.25tick, active on the entry bar. Gap stop fills at worse OPEN/stop. No TP, BE, trail or re-entry.
This uses inherited T timing/range risk, not the later09:00opening-handoff clock that already failed.

Historical receipt/corrections are unknown; the1-minute allowance is an exploratory assumption, not certified
point-in-time availability. Raw-price stop geometry and modeled slippage follow the preregistered source-style
cash bridge; native broker anchoring/tick fills are not independently established.

## Results

2018-01-01–2022-12-30 design, one fixed NQ contract,$20/point; commission$7.25round trip and one adverse
tick per entry/market-stop exit=$17.25total cost. Native1MNQ ledger uses$2/point,$1.25commission and$1slippage.
All values are total period dollars, not annual dollars, payouts, recommended leverage or a current-book result.
The whole source trading calendar has1,291dates (confirmed in the audit receipt); skipped/nontrading events
carry zero cash for ratios. Common eligible event universe1,022dates. Native2017warm-up wasn't supplied, so
the first21source calendar mornings lack required prior histories and are excluded openly.

### Five fixed cases
"""
    # Source calendar count is measured, never inferred from conditional event counts.
    text=text.replace('has1,291dates', 'has'+format(a['input_audit']['calendar_sessions'],',')+'dates')
    text+=table(m[m.period.eq('design')&m.side.eq('all')],['case','trades','total','avg','t_trade','profit_factor','sharpe','max_dd','native_mnq_total','worst_trade'])
    text+="""
Absorption fails before any subtle comparison: gross−$5,800,net−$6,386.50,PF0.55,t−1.17. Its modeled native
1MNQ total is−$656.50. Delaying another minute and adding another tick per leg both remain negative.
The t statistic is descriptive and not selection-adjusted; a negative result does not need statistical
significance to fail the registered positive-edge screen. Both trade directions lose.

PlainFade's gross edge is too small for its costs. PriceOnly loses even before fees. HeavyTotal is positive,
consistent with a known activity-conditioned fade family, but it is a comparator frozen before outcomes.
Its positive result cannot replace the failed candidate or establish a new book contribution. It changes the
original native T volume field/cutoff, warm-up and admission, so old T verification/portfolio gains do not transfer.

### Cash and native-cost reconciliation
"""
    text+=table(pd.DataFrame(rec),['case','trades','gross','commission','slippage','net','native_mnq_net','extra_tick_net'])
    text+="""
Gross, fees, slippage, daily/trade net and native-micro totals reconcile to half a cent. Native MNQ net is
not NQ net divided by10, because the modeled native commission differs. Initial-zero-peak daily DD is used;
that DD excludes intraday open-loss marks and is not an Apex floor-risk estimate.

## Input admission, timing and gaps

Five gzip objects and all five decompressed CSVs match the exact transfer-manifest sizes/SHA256s; original
CSV bytes sum109,365,550. Native row count1,755,357. All inspected rows have valid quarter-tick OHLC,
finite nonnegative integer volumes, no duplicate CT timestamps and total=buy+sell. ET close labels convert
using America/New_York→America/Chicago, including DST, with no added minute. Year files concatenate before
night features. Only native prices/quantities are used; the older owned NQ CSVs provide calendar dates only.
No source, legacy export or cached grid is overwritten, backfilled or spliced.

Fields UpVol/DownVol are documented by the vendor as aggressor buy/sell volume. This is a source claim,
not independent reconstruction from raw trade/quote messages. It is not ordinary tick-direction volume.
The earlier OF export's misleading total-volume field is never used; native total is the verified sum.
Original contract/build/roll/adjustment map, exceptional-side classification and historical receipt remain
unverified. Thus even a profitable screen would remain conditional research, not native/live readiness.

Eligibility requires>=836of928nominal overnight closes and an observed08:28end, plus complete last15-minute
features. Missing bars stay missing. Known history only is used. The prior daily-range history takes20complete
native cash sessions; partial sessions do not silently supply underestimated ranges. No unknown held execution
minutes survive; the same execution-path admission applies to all normal/delay cases.

Exclusions:236declared quarterly roll-calendar dates,21warm-up,9night-coverage/decision-close dates and3zero
night directions. The calendar restriction is dates5–21ofMarch/June/September/December; it is deliberately
broader than exact rolls and is not a future-largest-gap splice. Residual roll risk persists. Coverage excludes
stress dates; do not generalize the retained sample to missing limit/halts or claim protection on those dates.
The nine overnight data/coverage exclusions are listed below. No extra post-result exclusions were added.
"""
    text+=table(ex[ex.reason.eq('night_coverage_or_decision_close')],['date','reason'])
    text+="""
Pre-return counts were PlainFade1,022;PriceOnly459;HeavyTotal203;Absorption34. Under the assumed$1,000NQ
trade SD,34events need about$343net/trade for t2, before dependence/selection corrections. Actual data only
barely meet the30-event cheap minimum; no threshold was loosened. Ten synthetic fixture groups cover modeled
long/short entry stops, gaps, adverse rounding, exit-OPEN priority, delay anchoring, missing-path rejection,
clock conversion and native fees. They are implementation checks, not native MC/broker verification.

## Placebos and account level

Both nested comparisons pass exact common-date trade identity. Removing PlainFade opportunities discards
+$4,252net,mean+$4.30,t0.17. Removing PriceOnly opportunities discards−$18,051,mean−$42.47,t−1.06;
that comparison reduces losses but does not turn Absorption profitable. Neither comparison beats matched-count
random subsets on profit or DD at the registered<=5%shares. Counts are matched within calendar year,1000runs,
seed20261108; descriptive null shares are not multiple-testing-adjusted p-values.
"""
    text+=table(controls,['parent','removed_n','removed_total','removed_mean','removed_t','random_profit_ge_actual','random_dd_le_actual'])
    text+="""
Paired candidate-minus-parent daily cash deltas use1000moving20-session blocks. Total is period dollars;
percentile columns are annualized dollars on the full source trading-date calendar. Both intervals contain
zero, so neither meets the required positiveP5incremental gate.
"""
    text+=table(effects,['parent','total','annual_p5','annual_p50','annual_p95'])
    text+="""
The registered design gate fails. No2023+native file acquisition/replay, random-direction replay, MonteCarlo,
funded/evaluation/personal BASE/ADD/REPLACE/EMPTY, new forward promotion or PowerLanguage stage followed.
Neither improved payouts nor reduced account blow-up risk is established. Missing later/account results are
intentional stop-rule outcomes, not placeholders to be filled by reopening a failed strategy.

### Every registered gate
"""
    text+=table(pd.DataFrame([{'gate':k,'passed':bool(v)} for k,v in r['checks'].items()]),['gate','passed'])
    text+="""
## Scientific context: five source questions

1. About: persistent signed trading and adaptive liquidity in LSE stocks.
2. Finding: liquidity responses can offset predictable flow and bound price impact.
3. Profit: no net NQ strategy is demonstrated; stalled impact need not reverse.
4. Build on it: it motivates measuring flow versus response; the NQ/opening prediction is ours.
5. Code: this minute-volume screen is implementable; exact source replication needs trade/quote events.

Primary full source: Farmer/Gerig/Lillo/Mike2006, https://arxiv.org/html/physics/0602015 . It supplies conceptual
context and a warning, not numerical parameters or proof of our forecast. This is not a paper replication.

## What could make this wrong

Small sample, selected prior ideas, source classification, unresolved rolls/builds/receipt and missing stress
sessions limit inference. Minute OHLC cannot certify the sequence of trades, spread, queue, liquidity-provider
identity or actual latency. A stop does not establish safety on an Apex account. There is no quote-based
absorption measurement here: flow-price disagreement is an explicitly declared observable hypothesis.
No independent economic checker or native MC confirmation was performed for these new rules. Conditional
source audit/synthetic parity and two models agreeing would still not establish a profitable/live strategy.

## MultiCharts differences and outcome

No new PowerLanguage code, chart modification or plan change because design failed. Python uses native
aggressor categories; original T's up-tick classifier is a different input. One-minute receipt allowance and
08:28feature cutoff are explicit changes from the existing T source. No later side/weekday/threshold/follow
variant is authorized by this result. Original strategies retain their existing review/ranking status.

## Whole / long / short

`win` is a fraction; PF is per trade. Ratios use the full common calendar with zero cash on skipped dates,
and$50,000reporting capital. A zero-event year has no inferential t/PF; dashes indicate unavailable ratios.
"""
    text+=table(m[m.period.eq('design')],['case','side','trades','win','total','avg','t_trade','sharpe','sortino','profit_factor','calmar','ulcer','max_dd'])
    text+='\n## By year, all sides\n\n'
    text+=table(m[~m.period.eq('design')],['case','period','trades','win','total','avg','t_trade','sharpe','sortino','profit_factor','calmar','ulcer','max_dd'])
    REPORT.write_text(text)
    print('Saved report; all five cash/native ledgers reconcile. Selection:',r['selected'])


if __name__=='__main__':main()
