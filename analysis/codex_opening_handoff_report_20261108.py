"""Reconcile and report the frozen opening-handoff design output; no market replay."""
from pathlib import Path
import json
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'analysis/outputs/codex_opening_handoff_20261108'
REPORT=ROOT/'agents/codex/results/opening_handoff_20261108.md'

def table(df,columns):
    def f(x):
        if isinstance(x,(float,np.floating)):return f'{x:,.2f}' if np.isfinite(x) else '—'
        return str(x)
    return '| '+' | '.join(columns)+' |\n| '+' | '.join(['---']*len(columns))+' |\n'+'\n'.join('| '+' | '.join(f(v) for v in r)+' |' for r in df[columns].itertuples(index=False,name=None))+'\n'


def main():
    d=OUT/'design';r=json.loads((d/'results.json').read_text());m=pd.read_csv(d/'metrics.csv')
    rec=[]
    for p in sorted(d.glob('*_trades.csv')):
        t=pd.read_csv(p);daily=pd.read_csv(p.with_name(p.name.replace('_trades','_daily')))
        assert np.allclose(t.gross,(t.exit-t.entry)*t.side*20)
        assert np.allclose(t.net,t.gross-t.commission-t.slippage)
        assert np.allclose(t.native_mnq_net,t.gross/10-2.25)
        assert abs(t.net.sum()-daily.net.sum())<.005
        assert abs(t.native_mnq_net.sum()-daily.native_mnq_net.sum())<.005
        assert not t.missing_held_closes.sum()
        rec.append({'case':p.stem.removesuffix('_trades'),'trades':len(t),'gross':t.gross.sum(),
                    'commission':t.commission.sum(),'slippage':t.slippage.sum(),'net':t.net.sum(),
                    'native_mnq_net':t.native_mnq_net.sum(),'missing_held_minutes':0})
    pd.DataFrame(rec).to_csv(OUT/'cash_reconciliation.csv',index=False)
    controls=pd.DataFrame([{'case':k,**v} for k,v in r['filter_controls'].items()])
    effects=pd.DataFrame([{'case':k,**v} for k,v in r['paired_effects'].items()])
    report="""# FC/ONB/T opening handoff combinations: REJECT

Summary: Two frozen price-based combinations fail the 2018–22 design screen; no new strategy selected.
Continuation:60 trades,+$24,015 per NQ,t1.62; reversal:58,+$8,255,t0.61.
Both remove profitable trades and have lower Sharpe/Calmar than the common opening-drive parent.
Neither beats the registered matched random-subset profit/DD gates; delay and extra-cost stress remain positive.
Stop: no 2023+ combination returns, account bench, MultiCharts code or plan/live changes.

Plan: `agents/codex/plans/opening_handoff_20261108.md`, original `99d6209`, adapter amendment `9a34a7d`.
Evidence: `agents/codex/evidence/opening_handoff_20261108.md`.
Script: `analysis/codex_opening_handoff_20261108.py`.
Reporter: `analysis/codex_opening_handoff_report_20261108.py`.
Output: `analysis/outputs/codex_opening_handoff_20261108/`.
Trials: five fixed economic cases (parent, two candidates, their two delay stresses), plus registered random-drop
controls. Retain the aborted exact-anchor protocol's three partial price replays as prior execution history.
The prior18-case ingredient study and all earlier component searches remain selection history. Not independent discovery.

## Rule (as tested)

**Common entry/exits:** after the completed first30-minute opening drive, trade its direction at the09:01
close-labelled bar OPEN (09:00 civil CT). Use FCv2's100-point entry-bar stop,150-point next-bar trailing stop,
through-close market-exit fallback and no target. Break-even disabled using the source BER>0 guard.
Normal flatten at14:59-labelled OPEN, early-close flatten at11:31. One entry/day, no compounding.

**Continuation:** require the opening drive, overnight move and ONB overnight-location bias to agree;
15-minute ADX14>30; the09:00 close must break the first15-minute range in the drive direction.

**Reversal:** the opening drive must reverse the overnight move, with the cash-open price in the overnight
range's corresponding outer third (a down night starts in the lower third, an up night in the upper third).
Use the same ADX and first15-minute breakout confirmation. T supplies the overnight fade direction;
ONB supplies location/breakout/ADX confirmation; FC supplies opening drive and exit management.
This is a later confirmed reversal, not T's original pre-open entry or heavy-volume rule.

**Parent:** all eligible nonzero first30-minute drives with identical entry/exits. The two mandatory delay
cases enter09:02-labelled OPEN with the stop anchored to that fill; they cannot become selected variants.

Night direction uses first observed bar OPEN from previous17:01 through current08:29 versus08:29close.
ONB range covers previous23:01 through current08:30; cash-open is08:31-labelled OPEN. All candidate
features mature by09:00, before entry. No source MC trade-list outcomes, native up-tick Volume, total-volume
proxy, full-history-fitted ML score, calendar coefficient selection or other future return is used.
The proposed continuation/reversal pressure mechanism is unverified; prices do not identify forced actors.

## Results

Design2018-01-01–2022-12-30,2017 warm-up. All dollars below are total period profit at **1NQ** (20$/point),
$7.25 round-trip commission plus1tick on each market/stop fill ($17.25 total). No target fills.
Native1MNQ uses2$/point and$1.25 commission plus$1 round-trip slippage. A smaller commission bridge
means native MNQ net is not simply NQ net divided by10. Zero-P&L admitted sessions remain in ratios.
These are standalone fixed-size research results, not payout dollars, annual returns or recommended sizes.

### Five fixed cases
"""
    report+=table(m[m.period.eq('design')&m.side.eq('all')],['case','trades','total','avg','t_trade','profit_factor','sharpe','max_dd','calmar','native_mnq_total'])
    report+="""
Continuation concentrates to60 trades and raises average trade to$400, but t1.62 fails even the cheap t2
hurdle. Its Sharpe0.79 and Calmar are below the parent. Reversal has t0.61 and Sharpe0.30. Both are positive
in aggregate but lack the registered evidence needed to advance. The parent itself has t2.44 and is only
a comparator, not a newly approved strategy. Continuation's larger mean/PF alone is not a pass.

### Data counts and execution checks

Common universe:1,042 sessions. Excluded241 declared quarterly-roll-calendar dates,4 sessions with unknown
execution paths and2 zero drives. The first30 minutes and execution paths are fully observed on admitted
sessions; no held minute is fabricated or forward-filled. Roll-calendar exclusions apply equally to all cases.
Candidate counts60/58 imply assumed t2 mean hurdles of$516/$525 using the predeclared$2,000 trade SD,
versus observed means$400/$142; that power assumption is not an economic validation.

Nine synthetic fixture groups pass: both entry-stop directions, adverse gap, next-bar trail, through-close
fallback, BE genuinely off, normal/early flatten, delayed entry and native fees. These verify modeled code,
not actual MultiCharts/broker fills. The independent source FCv2 exit port is reused; no native parity for
these new combinations is claimed. Gross-to-net and daily/trade/native-micro sums reconcile to half a cent.
"""
    report+=table(pd.DataFrame(rec),['case','trades','gross','commission','slippage','net','native_mnq_net','missing_held_minutes'])
    report+="""
### Adapter failure retained

Original committed99d6209 erroneously required an exact17:01 source bar. Most exports lack that minute;
only35 parent events,3 continuation events and0 reversal events were admitted. The process replayed35 parent
and3+3 continuation/delay trades in memory, then failed normalizing the empty reversal dataframe. No
candidate economic summary from this attempt was printed or inspected, but those partial looks are retained.
The feature receipt, exclusions and traceback are in `aborted_exact_anchor/`; they are not erased or claimed
zero-return work. Source T actually uses the first observed reopening bar. The data-adapter/universe amendment
and empty numeric-dtype fix were committed9a34a7d before corrected returns. No clock or parameter was chosen
using P&L. The corrected protocol changes admission materially, as explicitly recorded in the plan.
Do not interpret the five nominal definitions as five untouched historical looks; these are source-informed
rules with prior component testing plus the retained partial adapter attempt.

## Placebos and account level

Both candidates are pure nested filters of the parent: retained date/side/entry/exit/net match exactly.
The excluded parent trades earn money: continuation removes982 trades averaging+$120.61,t2.10;
reversal removes984 averaging+$136.38,t2.37. Both fail the requirement that the filter remove losing trades.
Each was compared with1,000 within-year equal-count random subsets, seed20261108. Profit exceedance is
15.3% for continuation and45.7% for reversal, above the required<=5%; DD-no-worse shares68.9%/67.6%
also fail<=5%. These descriptive shares are not selection-adjusted p-values.
"""
    report+=table(controls,['case','removed_n','removed_total','removed_mean','removed_t','random_profit_ge_actual','random_dd_le_actual'])
    report+="""
Paired candidate-minus-parent daily cash differences use1,000 moving20-session blocks. The total delta
is period dollars; percentile intervals below are annualized dollars. Both intervals are entirely negative.
They measure this realized filtered-parent comparison, not the probability a strategy will fail in future.
"""
    report+=table(effects,['case','total','annual_p5','annual_p50','annual_p95'])
    report+="""
Both candidates remain positive under the fixed one-minute delay and another1tick/leg fee stress. Those
checks do not compensate for failed significance/profit/filter gates. Because neither design candidate
passes, **no recent-return replay, random-side replay, Monte Carlo, current-book BASE/ADD/REPLACE/EMPTY,
funded/evaluation bench, forward promotion or MultiCharts code stage is run**. These are intentionally missing,
not invented. Prior component research on2023+ is already seen; this study did not compute new combination
returns there. No improvement to evaluation, funded or personal portfolios is established.

### Gate record
"""
    gates=pd.DataFrame({k:v['checks'] for k,v in r['gates'].items()}).reset_index().rename(columns={'index':'check'})
    report+=table(gates,['check','Continuation','Reversal'])
    report+="""
## What could make this wrong

- These are price-only combinations of selected existing ingredients. Missing native up-tick gates are omitted
  openly; a claim about a full FC+T volume hybrid would need those inputs and a separate registered protocol.
- Both source history and the preceding ingredient outputs informed the definitions. Recent history is already
  known and no fresh historical holdout exists; no independence or causal flow discovery is claimed.
- Sparse60/58 event sets make averages uncertain. A profitable net number can arise from a few large trades.
  Side/year tables below are diagnostics and do not authorize a post-hoc long-only, short-only or year filter.
- Daily realized drawdown omits open trade marks. A100-point MNQ stop models roughly$202.25 loss before gaps;
  account cushion, simultaneous strategies and floor touches require an earned chronological replay.
- Fixed100/150-point exits are inherited, not optimized for price level. One-minute OHLC misses tick order,
  queueing and actual bid/ask spread. Modeled slippage does not measure execution quality.
- Calendar dates5–21 of quarterly months are excluded before entry as a conservative roll precaution. This is
  broader than exact roll dates and cannot guarantee all seams are gone. No global largest-gap adjustment or
  future-aware roll signal was applied. The4 incomplete-path exclusions are research data admission; a live
  strategy cannot know future data quality. All candidates share the same admitted universe.
- Reusing FC exit logic shifts the proposed T reversal into a later confirmation/longer holding interval.
  The original T signal's short pre-open edge does not establish a later continuation of that reversal.
- The maker has reconciled cash and synthetic execution; independent Claude/native verification is pending.
  No TIER, plan, live, broker, VPS, API-key, paid-data, scout-state or schedule change was made.

## Differences between MultiCharts code and the test

No new PowerLanguage code was written because the design gates failed. The Python source port uses FCv2
exit chronology with new price-derived admission, removes source volume selection and disables BE as declared.
It does not reproduce the native FC or T classifier, nor reuse the fitted ONB ML model. No deployment proposed.

## Whole / long / short results

`win` is a fraction; ratios use the admitted common calendar and$50,000 reporting capital. MaxDD uses initial
zero peak. This reporting capital does not establish required margin or safe account size.
"""
    report+=table(m[m.period.eq('design')],['case','side','trades','win','total','avg','t_trade','sharpe','sortino','profit_factor','calmar','ulcer','max_dd','worst_trade'])
    report+='\n## By year, all sides\n\n'
    report+=table(m[~m.period.eq('design')],['case','period','trades','win','total','avg','t_trade','sharpe','sortino','profit_factor','calmar','ulcer','max_dd'])
    REPORT.write_text(report)
    print('Saved report and cash checks; selected:',r['selected'])

if __name__=='__main__':main()
