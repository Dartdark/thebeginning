"""Render saved unchanged-baseline validation; no price input or new simulation."""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def usd(v):
    return f'${v:,.2f}'


def main():
    s=json.loads((ROOT/'analysis/outputs/codex_delgado_es_baseline/summary.json').read_text())
    d=json.loads((ROOT/'analysis/outputs/codex_delgado_es/design/summary.json').read_text())
    a=d['summaries']['base'][0]; b=s['summaries'][0]; f=s['full_summaries'][0]
    comparison=[]
    for label,row in [('2018–22design',a),('2023–2026-10-09historical validation',b),('2018–2026-10-09full',f)]:
        comparison.append(f"|{label}|{row['trades']}|{usd(row['net'])}|{row['return_sharpe']:.3f}|"
            f"{row['t_return']:.3f}|{usd(row['max_dd'])}|{row['return_dsr']:.3f}|{usd(row['stress_net'])}|")
    side=[]
    for r in s['summaries']:
        side.append(f"|{r['side']}|{r['trades']}|{100*r['win']:.1f}%|{usd(r['net'])}|{usd(r['avg'])}|"
                    f"{usd(r['mean_per_es_lot'])}|{r['t_trade']:.3f}|{r['sharpe']:.3f}|{r['sortino']:.3f}|"
                    f"{r['profit_factor']:.3f}|{r['calmar']:.3f}|{r['ulcer']:.3f}|{usd(r['max_dd'])}|")
    annual=[]
    for r in s['yearly']:
        annual.append(f"|{r['year']}|{r['trades']}|{usd(r['net'])}|{usd(r['long_net'])}|{usd(r['short_net'])}|"
                      f"{100*r['return_complete_days']:.2f}%|")
    boot=s['bootstrap']['daily_return']['metrics']['sharpe']
    boot_d=s['bootstrap']['dollar_pnl']['metrics']['annual']
    null=s['side_control']
    criteria='\n'.join(f"|{k}|{'PASS' if v else 'FAIL'}|" for k,v in s['criteria'].items())
    content=f'''# Unchanged ES baseline: profitable history, weak recent validation; no allocation earned

Summary: The baseline can be evaluated independently; failed modifications do not disqualify it.
Unchanged2023–October9,2026complete-day net+$49,755, but return Sharpe.550versus1.281in2018–22.
2025+$852.50and2026−$32,910; daily dollar drawdown expands to$56,842.50.
Return t1.065and90%block-bootstrap Sharpe interval−.175to1.261fail the frozen validation checks.
Keep as unpromoted research evidence; no personal/prop allocation or further tuning. Missing-path limits retained.

User explicitly nominated the baseline after seeing the comparison; do not present it as an untouched winner.
Plan: [baseline-only protocol](../plans/delgado_es_baseline_20261108.md), committed`8c89fd79`before new
recent returns. [Evidence](../evidence/delgado_es_baseline_20261108.md). Original modified-candidate
failure remains in[the ES comparison](delgado_es_20261108.md).
Core engine unchanged from4740cdd2; runner frozen at`{s['manifest']['run_commit']}`before outcomes.
[Runner](../../../analysis/codex_delgado_es_baseline.py) · [core](../../../analysis/codex_delgado_es.py) ·
[report renderer](../../../analysis/codex_delgado_es_baseline_report.py) ·
[full receipt/metrics/bootstrap/controls](../../../analysis/outputs/codex_delgado_es_baseline/summary.json).
Date: November8,2026(America/Los_Angeles). Independent review pending. No live/MC/account changes.

## Rule and result identity

Same14prior normal-session same-time noise band and typical-price total-volume VWAP, symmetric1.0band,
half-hour09:00–14:30CTchecks, next observed minute-open market fills, prior14daily-vol sizing and final
requested4xcap. Same$100,000startingNAVin2018, whole ES contracts and reinvested modeled profits.
Same$50/point,.25tick,$5roundtrip commission plus one adverse tick/side ($30normalRT/ESlot).
Normal EOD14:59decision→15:00close-stamped minute open; corresponding early-close clocks unchanged.
No filters, optimized parameters, side selection or rule repair. Core/code/cache/raw hashes match prior run.

The design daily and trade CSVs match the original2018–22files **byte for byte**, checked before recent
summaries. Thus this evaluates the same baseline. No replay or new selection of the rejected modified rules.
There are still3economic rule definitions in the original comparison; this task adds one conservative
post-design selection observation. Combined multiplicity lower bound{s['selection_count_lower_bound']},
tbar{s['t_bar']:.3f}. Do not reset trials to1or call2023+pristine OOS: related/source history was already seen.

Recent starts with modeledNAV{usd(s['recent_start_nav'])}carried from2018–22, not a new$100kreset. Actual
recent filled quantities1–4ES. The table's dollars therefore describe this compounded reference sleeve,
not a starter personal account, fixed-oneEScurve, fractional MES model or an Apex drawdown/payout account.

## Standalone comparison

Complete-day observations only; known no-trade days remain zeros. Daily-return Sharpe/t use each day's
startNAV. Dollar metrics use actual modeled quantities. Full-period statistics can hide recent deterioration.

|Window|Known trades|Net|Return Sharpe|Return t|Closed daily maxDD|Return DSR|Fixed-fill extra-tick stress net|
|---|---:|---:|---:|---:|---:|---:|---:|
{chr(10).join(comparison)}

Recent complete-day dollar-P&L metrics (joint replay slices, not new one-side strategies):

|Side|Trades|Win|Net|Mean/trade|Mean/ESlot/trade|Trade t|Dollar Sharpe|Sortino|PF|Calmar|Ulcer%|Daily DD|
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
{chr(10).join(side)}

Ulcer uses the inherited$100kreference reporting capital; it is not marked-equity margin risk. Daily dollar
maxDDincludes the initial reporting peak; it omits unknown intraday paths. These dollar/return Sharpe metrics
are different because capital compounds. No perNQnumbers substituted for ES dollars.

|Year|Trades|Net|Long net|Short net|Complete-day compounded return|
|---|---:|---:|---:|---:|---:|
{chr(10).join(annual)}

2026endsOctober9. The known-day compounded return is conditional where a day is excluded; it is not a
claim that a whole missing calendar path was observed. Positive2023/24does not establish a stable future edge;
2025is nearly flat after costs and2026loses on both sides. No year-based switch or short-removal rescue.

## Gross/net and uncertainty

Recent known-day gross{usd(b['gross'])}−slippage{usd(b['slippage'])}−commission{usd(b['commission'])}
={usd(b['net'])}. Adding another tick per side on the same filled quantities leaves{usd(b['stress_net'])},
so much of the recent gross gain is consumed by execution costs. This stress holds quantities fixed rather
than pretending it is a new independently compounded strategy.

There are{s['known_recent_days']}known days out of{s['recent_calendar_days']}recent calendar sessions.
2024-10-09has one held-price gap; its observed endpoint net+$2,140is excluded from complete-day metrics
and retained in raw ledgers. All recent observed-endpoint net{usd(s['observed_recent_endpoint_net'])}
reconciles to daily endpoint changes. No missing return is imputed as0. Conditional observed NAVends
{usd(b['nav_end_observed_path'])}; that path includes the flagged endpoint outcomes for later modeled sizing.
Earlier wholly absent2020-11-30and held2022-01-24remain flagged in full history. No unknown day removed
because of its profitability; exclusion rule was frozen before outcomes.

1000moving-block samples,20days, seed7323419, using the existing repository helper: recent **return**
Sharpe90%interval[{boot['p5']:.3f},{boot['p95']:.3f}]; recent annual dollar-profit90%interval
[{usd(boot_d['p5'])},{usd(boot_d['p95'])}]. These are conditional historical resampling intervals, not
probabilities of future viability or a native personal capital recommendation. Unknown-day removal compresses
the observed calendar; the bootstrap cannot recover missing paths or guarantee an unseen regime.

1000fixed-duration/quantity random-side controls, seed7323420: net/Sharpe plus-one pvalue
{null['net_pvalue']:.4f}/{null['sharpe_pvalue']:.4f}; null netp5/p95
[{usd(null['net_p5'])},{usd(null['net_p95'])}]. Exits and quantities are conditioned on the actual strategy;
this is descriptive rather than an independently causal full-policy placebo. It does not establish promotion.
DSR is likewise a historical selection statistic, not a probability of future profit.

## Frozen decision

|Requirement|Outcome|
|---|---|
{criteria}

The baseline is profitable over the recent aggregate but does not pass its own recent-strength gate:
return t<2andbootstrap lowerSharpe<0. Multiplicity evidence is weaker still. Hence no standalone current
recommendation and no rescue optimization. The reason is its **own** recent result, not the failed add-ons.

## Account placement and implementation limits

|Home|Verdict|Account comparison|
|---|---|---|
|Personal|No allocation earned: weak recent validation; native margin/coverage unverified|Not run|
|50Kevaluation|No advancement: statistical and native risk limits|Not run|
|150Kevaluation|No advancement; not inferred from50K|Not run|
|50Kfunded|No payout/contribution benefit established|Not run|
|150Kfunded|No payout/contribution benefit established|Not run|

No BASE/ADD/REPLACE/EMPTYaccount result is invented. Original protocol identifies personal PAPERTREND
and propVBreplacement, but the required statistical/native path gates are unmet. Existing current-book
cashflows were not rebuilt because no account stage was earned. Reference sleeve profit alone cannot
show improvement to the personal ladder at its actual integer sizes, capital and margin budget.

No recent cap flags;3earlier small marked4xbreaches remain. The requested entry cap cannot guarantee
actual marked exposure through a gap/loss. Native contract/roll identity, actual ES spread/commission eras,
broker margin, missing held-price paths and independent execution/platform verification remain open. A
continuous-price research reconstruction is not native execution certification. No MultiCharts/live code.

Tell Claude: review `agents/codex/results/delgado_es_baseline_20261108.md`; unchanged baseline validates
weakly in recent history, with2025flat/2026losses, so no current personal/prop place is established.

Reproduce at the frozen code/input identity: `python3 analysis/codex_delgado_es_baseline.py`.
Render saved outcomes without any new returns: `python3 analysis/codex_delgado_es_baseline_report.py`.
'''
    (ROOT/'agents/codex/results/delgado_es_baseline_20261108.md').write_text(content)
    print('Rendered baseline validation report from saved outputs; no new returns.')


if __name__=='__main__':
    main()
