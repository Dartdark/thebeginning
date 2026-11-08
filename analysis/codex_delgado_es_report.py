"""Render saved ES design outcomes; reads no raw market data and runs no returns."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT/'analysis/outputs/codex_delgado_es/design/summary.json'


def money(x):
    return f'${x:,.2f}'


def main():
    s=json.loads(SOURCE.read_text())
    summaries=s['summaries']
    main_rows=[]
    side_rows=[]
    for name in ('base','shadow','candidate'):
        for row in summaries[name]:
            side_rows.append(f"|{name}|{row['side']}|{row['trades']}|{100*row['win']:.1f}%|"
                f"{money(row['net'])}|{money(row['avg'])}|{money(row['mean_per_es_lot'])}|"
                f"{row['t_trade']:.3f}|{row['sharpe']:.3f}|{row['sortino']:.3f}|"
                f"{row['profit_factor']:.3f}|{row['calmar']:.3f}|{row['ulcer']:.3f}|{money(row['max_dd'])}|")
        r=summaries[name][0]
        main_rows.append(f"|{name}|{money(r['net'])}|{r['return_sharpe']:.3f}|{r['t_return']:.3f}|"
                         f"{money(r['max_dd'])}|{r['return_dsr']:.3f}|{money(r['stress_net'])}|")
    years=[]
    for i,b in enumerate(s['yearly']['base']):
        c=s['yearly']['candidate'][i]
        years.append(f"|{b['year']}|{money(b['net'])}|{money(c['net'])}|{money(c['long_net'])}|"
                     f"{money(c['short_net'])}|{c['trades']}|")
    criteria='\n'.join(f"|{k}|{'PASS' if v else 'FAIL'}|" for k,v in s['gates']['candidate_criteria'].items())
    bridge=[]
    for name in ('base','shadow','candidate'):
        r=summaries[name][0]; g=s['gates'][name]
        observed=r['nav_end_observed_path']-100000
        bridge.append(f"|{name}|{money(r['gross'])}|{money(r['slippage'])}|{money(r['commission'])}|"
                      f"{money(r['net'])}|{money(observed)}|{money(observed-r['net'])}|"
                      f"{g['unknown_days']}|{g['unknown_trades']}|{g['fill_cap_breaches']}|")
    report=f'''# Delgado rules on ES: REJECT selected adaptation at design gate

Summary: Yes—owned ES data can test a labeled futures adaptation; this historical test is complete.
2018–22complete-day net: BASE$107,475versus CANDIDATE$25,517.50on$100,000initial referenceNAV.
Daily-return Sharpe falls1.281→0.663; maximum daily closed-P&L drawdown barely improves$16,420→$15,330.
Candidate fails daily/trade significance, baseline profit retention and return/drawdown improvement gates.
Stop: no new2023+returns, tuning or account simulation; no current allocation. Unknown paths remain disclosed.

Plan: [frozen protocol](../plans/delgado_es_20261108.md), initial commit`1c0e1a54`, exact code/clock
clarification frozen **before returns** at`{s['manifest']['git_commit']}`.
[Evidence](../evidence/delgado_es_20261108.md) · [source paper review](delgado_7323419_review.md).
Code: [replay](../../../analysis/codex_delgado_es.py) · [12synthetic checks](../test_delgado_es.py) ·
[report renderer](../../../analysis/codex_delgado_es_report.py).
Outputs: [complete JSON/hash manifest](../../../analysis/outputs/codex_delgado_es/design/summary.json),
`analysis/outputs/codex_delgado_es/design/*_daily.csv`, `*_trades.csv`, `*_cap_breaches.json`.
Date: November8,2026(America/Los_Angeles). Independent review pending.
New financial definitions:3(BASE,SHADOW,CANDIDATE); shadow is mechanical/nonselectable, no winner search.
Known multiplicity lower bound:{s['trials_lower_bound']};tbar{s['t_bar']:.3f}, including80source alternatives.

## Rule as tested

ES futures price/volume on close-stamped CT minute bars, using the existingGrid24cache. No SPY/ES÷10
price or share-cost conversion. BASE uses14prior normal-session same-clock mean absolute open movement,
gap-aware bands and typical-price cumulative-volume VWAP. At09:00–14:30CT half hours, enter beyond both
band and VWAP. Long exits on close<=max(upper,VWAP); short exits on close>=min(lower,VWAP).
Reversals close and reopen with both legs charged. Exits are checkpoint markets, not intraminute stops.

Candidate follows the source's frozen long1.3/short1.6band multipliers, short size.75, relative-volume size
clip(.5,1.5), band-binding size.7and previous30known SHADOW-day performance size.9/1.1. SHADOW is the
same candidate without that performance overlay. No parameter/side/calendar/market search followed results.

Base exposure min(4,.02/prior14daily-returnSD) times$100,000initial and subsequent modeled day-startNAV.
All multipliers precede the final requested4xcap. Whole ES lots round toward zero, using decision-close price;
entry quantity is not chosen with the future fill-open. Actual order size in this run was1–3EScontracts; some
small targets round to zero, particularly under candidate discounts. This discrete effect is part of this tested
implementation. It does not preserve the smooth fractional-share sizing of SPY. A microcontract study would
need a separate frozen sizing/cost/launch-date protocol rather than dividing these returns by10.

Market fills use the next observed native minute open with one adverse.25point tick/side. ES$50/point;
commission$5/roundtrip/lot, so ordinary total modeled cost$30/roundtrip/lot. Fees are stated research
assumptions, not verified historical broker statements. No native MES trades before its launch are invented.
Normal flatten decision14:59CTfills15:00close-stamped minute open; early sessions11:59→12:00.
No broker margin, cash interest or native quarterly roll ledger is inferred from the notional guard.

## Design results:2018–22only

The tables use **1,257complete days out of1,259cash-calendar days**. They retain real zero-trade known days.
Two days are unknown:2020-11-30absent, and2022-01-24with a held-price gap. Price and volume are never
forward/back-filled. Once current cumulativeVWAPis incomplete, new entries stop; held positions close on
the first subsequently observed open and remain flagged. The gapped trade is excluded from complete-day
statistics, retained in the raw ledger/bridge below. This is conditional observed-data reconstruction, not a
complete executable financial history. The source's2007–24or2000–26SPYperformance is not reproduced.

|Definition|Complete-day net|Daily-return Sharpe|Daily-return t|Daily maxDD|Return DSR|Extra-tick fixed-fill stress net|
|---|---:|---:|---:|---:|---:|---:|
{chr(10).join(main_rows)}

Daily-return Sharpe/t use each day's modeled startNAV, as capital compounds. Dollar-P&L Sharpe below is
a different statistic. Drawdown is the closed daily dollar path, with initialNAV included as a peak; it does not
measure intraday margin needs or worst open loss. DSR is a historical selection correction, not future success.
No candidate is selected: full candidate failed. The profitable baseline was a comparator, not a replacement
winner; its DSR also falls below.95and its existing family/coverage concerns remain.

|Definition|Side|Trades|Win|Net|Mean/trade|Mean net/ESlot/trade|Trade t|Dollar Sharpe|Sortino|PF|Calmar|Ulcer%|Daily DD|
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
{chr(10).join(side_rows)}

Side rows are slices of the same joint strategy, not newly selected long-only/short-only replays. Dollars are
actual modeled whole-ES quantities, not perNQ. Net/ESlot/trade averages each trade's normalized net; it is
not a fixed-one-contract equity curve or a claim of equivalent MES fills.

|Year|BASEnet|CANDIDATEnet|Candidate long|Candidate short|Candidate trades|
|---|---:|---:|---:|---:|---:|
{chr(10).join(years)}

## Gross/net bridge, missing paths and risk

|Definition|Complete gross|Slippage|Commission|Complete net|All observed-endpoint net|Flagged-day bridge|Unknown days|Unknown trades|Fill/marked cap flags|
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
{chr(10).join(bridge)}

Every observed endpoint trade satisfies gross−slippage−commission=net, and observed closed trade totals
equal observed daily endpoint totals. Excluded unknown-path returns are NaN, never zero-return evidence.
The absent day's observed cash bridge0does not establish that a real strategy would have stayed flat.
The observed endpoint path, including the flagged known entry/exit endpoints, updates later modeled sizing;
this is another reason the capital path is conditional rather than independently certified.

Pre-return audit found10cash sessions with missing minutes in2017–Oct2022, including2020halt periods.
Other gaps can occur while flat and causally suppress entries; their missing prices are not invented. Missing
2020-11-30blocks subsequent adjacent-close volatility windows rather than bridging the missing session.
The cache has continuous ES prices/volume; historical contract IDs, roll adjustments and execution at native
contract prices remain unverified. Source covariance/flow interpretation is not a measured forced ES order.

The requested4xnotional cap does not guarantee actual marked exposure stays below4through a gap/loss.
BASEhas3fill/mark cap flags; candidate/shadow0in this run. These flags are retained, never retrospectively
resized with future prices. Final targets and actual exposure/cash paths are distinct. Broker margin feasibility
and smaller personal-account affordability were not established by this$100kreference reconstruction.

## Frozen gates and stop

|Criterion|Outcome|
|---|---|
{criteria}

The candidate's trade t1.360and return t1.481are below2; it retains only about24%of BASEnet and its
net/drawdown ratio is substantially worse. Positive profit and four positive years do not overcome those
failures. The source's overlays did not transfer beneficially to this whole-ES implementation.

Following the committed stop rule, no new2023+calculation, bootstrap, placebo, random-drop or account
simulation ran. Past2023+ES/NQstudies remain prior evidence, not newly obtained validation. No rescue
variant, threshold change, favorable-side selection or shadow promotion. Twelve synthetic causality/fill/
rounding/cost checks passed before returns; these complement rather than replace the historical result.

## All five account homes

|Home|Verdict|BASE/ADD/REPLACE/EMPTY|
|---|---|---|
|Personal|No place earned: candidate fails design; capital/margin/coverage unverified|Not run after failed gate|
|50Kevaluation|No place earned; source-reference sizing is not an Apex account model|Not run|
|150Kevaluation|No place earned; candidate fails same design gate|Not run|
|50Kfunded|No place earned; no payout/risk improvement established|Not run|
|150Kfunded|No place earned; not inferred from50K|Not run|

No MultiCharts strategy was written; source/continuous-price/fill and native margin parity remain unverified.
Tell Claude: review `agents/codex/results/delgado_es_20261108.md`; the requested ES adaptation was actually
tested, made positive conditional design profit, but its selected overlays substantially underperform BASE.

Reproduce original design with `python3 analysis/codex_delgado_es.py --stage design` at the frozen code
commit. Rebuild this report without returns: `python3 analysis/codex_delgado_es_report.py`.
'''
    (ROOT/'agents/codex/results/delgado_es_20261108.md').write_text(report)
    print('Rendered saved design outcomes; no new return calculation.')


if __name__ == '__main__':
    main()
