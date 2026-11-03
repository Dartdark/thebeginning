"""Report existing frozen design outcomes; no new strategy returns or variants."""
from pathlib import Path
import gzip,hashlib,json,sys
import numpy as np
import pandas as pd
import metrics as M

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'analysis/outputs/codex_noise15_20261103'
REPORT=ROOT/'agents/codex/results/noise15_20261103.md'

def read_csv(path,**kwargs):
    return pd.read_csv(path if path.exists() else Path(str(path)+'.gz'),**kwargs)

def main():
    r=json.loads((OUT/'design_results.json').read_text());models=r['models']
    assert all(not x['design_pass'] for x in models.values())
    literal=read_csv(OUT/'literal_globex_trades.csv')
    originals=['attempt1','attempt2']
    comparisons={}
    for name in originals:
        old=read_csv(OUT/name/'literal_globex_trades.csv')
        assert old.equals(literal[list(old.columns)])
        comparisons[name]='All original literal trade fields equal completed execution.'
    ranked=len(pd.read_csv(ROOT/'TRIALS.csv'));n=ranked+2
    for name,x in models.items():
        t=read_csv(OUT/(name+'_trades.csv'));known=t[t.path_known]
        assert np.isclose(known.gross_nq.sum()-known.slippage_nq.sum()-known.commission_nq.sum(),known.net_nq.sum())
        x['known_ranked_plus_new_minimum']=n
        x['multiplicity_t_lower_bound']=M.t_threshold(n)
        x['per_trade_dsr_lower_bound_trials']=M.deflated_sharpe(known.net_nq,n)
        x['complete_trades_with_tainted_history']=int((known.tainted_history_samples>0).sum())
    run=dict(status='design_reject',source_rule_unchanged=True,
        original_preregistration='3780dde0970c4c7a71477d752f056cdf87aa4b3e',
        accounting_amendments=['ebf69a0be42c078085fd2b8fa4f2d89c8d9ae24a','84a753e3213d9e55e3f975e8d89a8b9634606fc9'],
        completed_command='python analysis/codex_noise15_20261103.py design --commit 84a753e3213d9e55e3f975e8d89a8b9634606fc9',
        economic_definitions_executed=['N15_LITERAL_GLOBEX','N15_PROTECTED_GLOBEX'],
        literal_engine_executions=3,protected_engine_executions=1,
        stopped_attempts=['attempt1/receipt.json','attempt2/receipt.json'],same_trade_checks=comparisons,
        controls_not_executed=['N15_RANDOM_SIDE','N15_RANDOM_TIME','N15_RANDOM_DROP'],
        historical_validation_executed=False,independent_review='pending',account_comparisons_executed=False,
        homes={h:'No advancement: design gates failed; no measured BASE/ADD/REPLACE/EMPTY comparison.'
               for h in ['50K evaluation','150K evaluation','50K funded','150K funded','personal ladder/full portfolio']},
        scout_budget_unchanged={'hypotheses':4,'economic_definitions':10},
        metrics_supplement={name:{k:x[k] for k in ['known_ranked_plus_new_minimum','multiplicity_t_lower_bound',
           'per_trade_dsr_lower_bound_trials','complete_trades_with_tainted_history']} for name,x in models.items()})
    (OUT/'run.json').write_text(json.dumps(run,indent=2)+'\n')
    rows=['|Profile|Trades|Win|Net / NQ|$/trade|PF|Daily t|Trade t|Sharpe|Sortino|Calmar|Ulcer%|Closed-day DD|',
          '|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|']
    for name,x in models.items():
        v=x['metrics'];rows.append(f"|{name}|{v['trades']}|{v['win']:.1%}|${v['total']:,.2f}|${v['avg']:.2f}|{v['profit_factor']:.3f}|{v['daily_t']:.4f}|{v['trade_t']:.4f}|{v['sharpe']:.3f}|{v['sortino']:.3f}|{v['calmar']:.3f}|{v['ulcer']:.2f}|${v['max_dd']:,.2f}|")
    sides=['|Profile|Side|n|Net/NQ|Mean/NQ|PF|t trade|Sharpe|Sortino|Calmar|Ulcer%|DD|',
           '|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|']
    for name,x in models.items():
        for v in x['by_side'][1:]:
            sides.append(f"|{name}|{v['side']}|{v['trades']}|${v['total']:,.2f}|${v['avg']:.2f}|{v['profit_factor']:.3f}|{v['trade_t']:.3f}|{v['sharpe']:.3f}|{v['sortino']:.3f}|{v['calmar']:.3f}|{v['ulcer']:.2f}|${v['max_dd']:,.2f}|")
    years=['|Year|Literal net/NQ|Protected net/NQ|','|---|---:|---:|']
    a,b=list(models.values())
    for x,y in zip(a['by_year'],b['by_year']):years.append(f"|{x['year']}|${x['total']:,.2f}|${y['total']:,.2f}|")
    costs=['|Profile|Reference gross/NQ|Slippage/NQ|Commission/NQ|Extra-tick stress net/NQ|Extra cost to zero/complete trade|',
           '|---|---:|---:|---:|---:|---:|']
    for name,x in models.items():costs.append(f"|{name}|${x['gross_nq']:,.2f}|${x['slippage_nq']:,.2f}|${x['commission_nq']:,.2f}|${x['stress_net_nq']:,.2f}|${x['breakeven_extra_cost_per_complete_trade']:.2f}|")
    REPORT.write_text(f'''# N15 full-Globex noise-band upload: REJECT advancement

Summary: Positive conditional design profit does not establish the advertised Sharpe3.7or portfolio value.
Literal:3,512complete-path trades,+$70,123/NQ,PF1.078,Sharpe0.889,daily t1.994.
Safety adaptation:+$64,951/NQ,PF1.073,Sharpe0.828; both have only3/5positive design years.
Partial feature histories and unresolved holding paths remain; literal code also has late/cross-date exits.
Both fail frozen design gates: no2023+validation, null/MC or account bench; no allocation recommended.

## Scope, source and reproducibility

**2018-02-01–2022-12-31**, user-confirmed NQ15-minute full Globex, America/Chicago. January2018is extra warm-up
chosen from the timestamp inventory before returns;2017overnight startsDecember1. No later-year data opened.
Supplied claim:+$6,335,PF1.30,Sharpe3.7; the user does not know its period. No source report/ledger, costs,
annualization or independent result was supplied. Our different design interval cannot verify that claim.
These are reconstructions, not native MultiCharts-confirmed or executed profits.

Original source[bytes](../inputs/noise15_20261103/source.txt), SHA256
ed5459d14a9ce57dc5dd78c4ef8d40372f30206f5965f96c8aa1dc29be714f47.
[Evidence](../evidence/noise15_20261103.md), [plan](../plans/noise15_20261103.md),
[inputs/versions](../inputs/noise15_20261103/inventory.json), [context](../inputs/noise15_20261103/context.json).
Original preregistration3780dde; bookkeeping amendments ebf69a0and84a753e preceded their reruns. Both stopped
attempts and their outputs are preserved; all original literal trade fields match the completed replay exactly.
No signal, fill, parameter, history, session, cost or gate changed after outcomes. Two economic definitions,
four engine executions: literal3(two accounting stops), protected1. Three conditional controls remain unused.
The separate scout ledger remains4/10and10/30; no selection-history reset, paused program or optimization.

Runner:[codex_noise15_20261103.py](../../../analysis/codex_noise15_20261103.py).
Reporter:[codex_noise15_report_20261103.py](../../../analysis/codex_noise15_report_20261103.py).
[Full run receipt](../../../analysis/outputs/codex_noise15_20261103/run.json).
Reproduce in the configured environment with the12owned hashed inputs:

```sh
python analysis/codex_noise15_20261103.py design --commit 84a753e3213d9e55e3f975e8d89a8b9634606fc9
python analysis/codex_noise15_report_20261103.py
```

## Five questions

1. **What is it about?** A price-based NQnoise-band momentum adaptation:20prior same-slot moves, candle direction,
   EMA20exit threshold,50-point stop/25-point target, reversals, entry counters and14:30flat signal.
2. **What does it find?** Our conditional design reconstruction is profitable but fails t/year/data-history gates.
   The advertised Sharpe3.7is unverified. This is a code review/backtest, not a new full reading of the2024paper.
3. **Why money, if any?** Price persistence beyond a historical noise envelope is the proposed explanation.
   No forced participant flow or incremental portfolio alpha was identified. Positive reconstructed profit alone
   does not establish that explanation or durable net expectancy.
4. **Can we build on it?** No current advancement. The fixed submission and safety adaptation both fail; do not
   change bands, clocks, sides or targets to rescue them. Preserve the existing noise-area family history.
5. **Can strategy code be made?** Yes: supplied PowerLanguage and the reproducible Python replay exist. Source
   compilation, platform trade matching, independent verification and account placement remain unestablished.

## Rule fidelity and execution assumptions

The code resets TodayOpen on calendar Date change. On ordinary full-Globex15-minute charts the00:00bar opens
around23:45the previous date; it does not explicitly use08:30or the17:00session reopen. EMA uses all observed
chart bars. The lookback reads20stored slot observations before updating today, with no current-bar future leak.
14:30is slot23outside the22history slots, but the separate14:30flat branch still acts. Do not invent a missing
flat just from the array bound. A14:30next-bar market exit can execute around14:30, not necessarily14:45.

Built-in stop/target are prearmed, per contract and fill-anchored. The revision uses actual BigPointValue:
50/25points on NQ or MNQ, fixing the earlier CODE.txt's unchanged-input MNQ500/250point conversion problem.
Source2NQnominal stop$2,000equals the50Kinitial trail before fees/slips;3nominal stops$6,000. The daily counter
is based on latest closed-position loss amount, not a guaranteed account loss limit. Stop gaps can exceed it.

UseGrid24aggregation and grid._walk's O-H-L-C/O-L-H-C intraminute convention. Market/stop fills pay one adverse
0.25tick; targets need1point trade-through. Levels are based on the modeled slipped fill. NQcommission$7.25RT.
Stop-count P&L excludes commission, a disclosed platform assumption. Exact MC BarMagnifier/IOG/settings, EMA
seeding, native contract/roll and broker fill parity are not established. No repair to source orders was deployed.

Literal source preserves equality-only flatten and shortened-session carry risk. Protected keeps source features,
but vetoes cash holiday/half-day entries and adds the prespecified next-bar late-flat fallback. It is a substantive
research adaptation, not the author's verified source. Its calendar guard is conservative, not venue authentication.

## Conditional design results

**Per one NQ**, not the default2NQposition and not a capitalized account. Tables include only trades whose observed
holding paths/entry clocks meet the frozen complete-path definition. History-tainted trades are retained and flagged.
Daily statistics are complete-trade contributions booked by exit date, weekend exits moved to Monday. A date with
another unknown-path trade is not thereby a fully known strategy-return date. Closed-day DD/Ulcer are not native
intraday/account risk. The separate chart-mark audit uses actual observed chart closes, not fictitious liquidation.

{chr(10).join(rows)}

At source2NQthe conditional totals are+$140,246literal and+$129,902protected; costs/positions scale linearly here.
That does not make them safe for an evaluation or predict payouts. One-MNQquote/fee diagnostics give+$5,203.62and
+$4,700.84over the same design interval with$1.24RTfees; these are price-proxy diagnostics, not native funded results.

{chr(10).join(sides)}

{chr(10).join(years)}

2018is partial. Neither variant has4/5positive years. Literal daily t1.9940and trade t1.9970are below2;
rounding either to2.00does not pass. Protected daily t1.8559and trade t1.8538also fail. With the known minimum
{n}trials({ranked}ranked CSVrows+2new definitions), the multiplicity tbar is{M.t_threshold(n):.3f}; additional
unranked/author searches remain unknown. Per-trade DSR is
{models['literal_globex']['per_trade_dsr_lower_bound_trials']:.4f}literal and
{models['protected_globex']['per_trade_dsr_lower_bound_trials']:.4f}protected at that lower-bound count.

{chr(10).join(costs)}

## Source/data limits and gate disposition

Literal closes3,518trades:3,512complete paths,6unresolved.833closed trades use at least one partial/misaligned
history/anchor sample;{models['literal_globex']['complete_trades_with_tainted_history']}of those have complete holding paths.
Three cross calendar dates;5are cross-date or exit at/after the16:00minute label. These are reconstruction flags,
not observed broker incidents. Protected closes3,485:3,484complete paths,1unresolved;826history-tainted,
{models['protected_globex']['complete_trades_with_tainted_history']}with complete holding paths; zero cross-date/late exits.
Unknown intervals conservatively include unclassified closures; not all missing observations are data-provider errors.
No missing return is filled, no unknown-path win/loss is adopted, and no favorable clean subset earns promotion.

Both pass the>=500trade/99.5%complete-path/gross-net/stress/terminal-flat checks. Both fail daily t, trade t,
4/5positive years and zero-tainted-selected-history checks. No thresholds or history exclusions were weakened.
Design rejection stops dependent work. No2023+validation, bootstrap/null/random-drop/MonteCarlo, independent
raw-spec checker or account comparisons ran. Negative gates are not evidence of measured harm to every account.

## Current-portfolio verdicts

Read-only current plan sources were refreshed at Claude5b20aa4, including the19-piece personal book and adopted
inverse-vol ladder. Older equal-unit totals are not silently used as current allocation. Native dependencies
would require another refresh if an earned account stage existed.

|Home|Verdict|Actual BASE/ADD/REPLACE/EMPTY result|
|---|---|---|
|50Kevaluation|No advancement: failed design gates|Not run; no pass-probability gain claimed|
|150Kevaluation|No advancement: failed design gates|Not run; no timing/risk gain claimed|
|50Kfunded|No advancement; raw source also has timing/risk concerns|Not run; no payouts/blow-up estimate claimed|
|150Kfunded|No advancement: failed design gates|Not run; not inferred from50K|
|Personal ladder and full book|No advancement: failed design gates|Not run; no incremental profit/DD measured|

Selected version: **none**. Independent verification pending; no MultiCharts compilation/trade match, forward/live
evidence, rank, allocation or trading change. Tell Claude to review this report, the frozen code/input ledger and
the two preserved accounting-stop receipts. Execution lessons are retained in EXECUTION_REFERENCES.md.
''')
    # Lossless deterministic compression keeps stopped attempts and complete
    # ledgers reviewable without duplicating megabytes of plain CSV in Git.
    artifacts=[]
    sources={p for p in OUT.rglob('*.csv')}|{Path(str(q)[:-3]) for q in OUT.rglob('*.csv.gz')}
    for p in sorted(sources):
        q=Path(str(p)+'.gz');raw=p.read_bytes() if p.exists() else gzip.decompress(q.read_bytes())
        q.write_bytes(gzip.compress(raw,mtime=0))
        assert gzip.decompress(q.read_bytes())==raw
        artifacts.append(dict(path=q.relative_to(ROOT).as_posix(),original_sha256=hashlib.sha256(raw).hexdigest(),
                              gzip_sha256=hashlib.sha256(q.read_bytes()).hexdigest(),original_bytes=len(raw),
                              gzip_bytes=q.stat().st_size))
    (OUT/'artifact_manifest.json').write_text(json.dumps(artifacts,indent=2)+'\n')
    print(json.dumps(dict(report=REPORT.relative_to(ROOT).as_posix(),design_reject=True,
        literal_net=models['literal_globex']['metrics']['total'],literal_sharpe=models['literal_globex']['metrics']['sharpe'],
        literal_dsr=models['literal_globex']['per_trade_dsr_lower_bound_trials'],trade_fields_unchanged=True,
        compressed_artifacts=len(artifacts),new_return_variants=0),indent=2))

if __name__=='__main__':main()
