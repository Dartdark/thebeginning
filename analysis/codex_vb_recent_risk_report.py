"""Verify the frozen VB audit and render its report without new return variants."""
from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scratch_data/codex_deps'))
sys.path.insert(0, str(ROOT / 'analysis'))
import numpy as np
import pandas as pd
import codex_vb_recent_risk as A
import metrics as M
import resampling as R
from trials import parse_tier_list

OUT = A.OUT
REPORT = ROOT / 'agents/codex/results/vb_recent_risk.md'


def read(name):
    return json.loads((OUT / name).read_text(encoding='utf-8'))


def table(frame, columns):
    """columns: source, title, cell formatter; no optional tabulate dependency."""
    lines = ['| ' + ' | '.join(c[1] for c in columns) + ' |',
             '| ' + ' | '.join('---' for _ in columns) + ' |']
    for _, row in frame.iterrows():
        lines.append('| ' + ' | '.join(fmt(row[key]) for key, _, fmt in columns) + ' |')
    return '\n'.join(lines)


money = lambda x: f'-${-x:,.2f}' if x < 0 else f'${x:,.2f}'
number = lambda x: f'{x:.2f}'
integer = lambda x: str(int(x))
percent = lambda x: f'{x:.1%}'
text = str


def verify():
    manifest, gate, stop = read('manifest.json'), read('design_gate.json'), read('validation_gate.json')
    assert all(A.sha(ROOT / p) == h for p, h in manifest['hashes'].items())
    assert manifest['baseline_trade_for_trade_pass']
    assert not gate['survivors'] and stop['validation_alternative_replays'] == 0
    assert stop['status'] == 'STOP: no design survivor' and not stop['full_account_bench_run']
    assert set(p.name for p in OUT.glob('*_validation_trades.csv')) == set()
    baseline = pd.read_csv(OUT / 'BASE_trades.csv', parse_dates=['date'])
    metrics = pd.read_csv(OUT / 'baseline_metrics.csv')
    eq = pd.read_csv(OUT / 'baseline_equity_daily.csv', parse_dates=['date'])
    days = pd.DatetimeIndex(eq.date)
    # Reconcile every baseline table row against its ledger, independent direct
    # arithmetic, including a starting zero in both daily and trade drawdowns.
    for _, row in metrics.iterrows():
        z = baseline[baseline.date.between(row.first_date, row.last_date)]
        d = z.groupby('date').net.sum().reindex(days[(days >= row.first_date) & (days <= row.last_date)], fill_value=0.)
        trade_eq = np.r_[0., z.net.cumsum().to_numpy()]
        day_eq = np.r_[0., d.cumsum().to_numpy()]
        assert len(z) == row.trades
        assert np.isclose(z.net.sum(), row.total)
        assert np.isclose(z.pnl.sum() - row.total_cost, row.total)
        assert np.isclose((np.maximum.accumulate(trade_eq) - trade_eq).max(), row.max_trade_dd)
        assert np.isclose((np.maximum.accumulate(day_eq) - day_eq).max(), row.max_dd)
    assert (baseline.side == 1).all()
    design = pd.read_csv(OUT / 'design_metrics.csv')
    reference = design[design.model.eq('BASE')].iloc[0]
    for name in A.MODELS:
        z = baseline[baseline.date.dt.year.le(2022)] if name == 'BASE' else pd.read_csv(OUT / (name + '_design_trades.csv'), parse_dates=['date'])
        assert z.date.max() < pd.Timestamp('2023-01-01')
        row = design[design.model.eq(name)].iloc[0]
        assert len(z) == row.trades and np.isclose(z.net.sum(), row.total)
        assert z.groupby(z.date.dt.year).net.sum().gt(0).sum() == 5
        material = ((row.max_trade_dd <= .85 * reference.max_trade_dd and row.total >= .95 * reference.total)
                    or (row.total >= 1.15 * reference.total and row.max_trade_dd <= 1.05 * reference.max_trade_dd))
        pass_gate = (name != 'BASE' and row.total > 0 and row.t >= 2 and row.profit_factor >= 1.2
                     and row.calmar >= reference.calmar and material)
        assert pass_gate == next(m['survives'] for m in gate['models'] if m['model'] == name)
    account = read('archived_account_audit.json')
    closes = pd.read_csv(OUT / 'archived_chart_closes.csv')
    assert all(A.sha(ROOT / r['path']) == r['sha256'] for r in account['sources'])
    assert len(closes) == account['close_rows'] == 6
    assert len(closes.drop_duplicates(['entry_date', 'entry_time', 'entry_price'])) == account['observed_market_entry_labels'] == 3
    assert closes.gross_arithmetic_matches.all() and not account['complete_broker_fills']
    for tag in account['chart_tags']:
        assert np.isclose(closes[closes.tag.eq(tag['tag'])].profit_usd.sum(), tag['gross_chart_sum'])
    mc = read('stored_mc_export_audit.json')
    assert A.sha(ROOT / mc['path']) == mc['sha256']
    assert mc['recent']['last_date'] == manifest['last_complete_date'] == '2026-10-09'
    assert not mc['extended_calendar_verified']
    missing = pd.read_csv(OUT / 'missing_held_minutes.csv', parse_dates=['date'])
    assert not missing.date.ge(A.START).any()
    checks = dict(baseline_trade_for_trade_saved_ledger=manifest['baseline_trade_for_trade_pass'],
                  baseline_summary_and_initial_zero_dd_reconciled=True,
                  all_four_alternatives_design_only=True, all_four_failed_gate=True,
                  chart_account_copies_not_counted_as_independent=True,
                  stored_report_not_zero_filled_past_verified_calendar=True,
                  recent_missing_held_minutes=0, source_hashes_unchanged=True,
                  caches_rebuilt=False, live_changes=False)
    A.dump('report_checks.json', checks)
    return baseline, metrics, eq, design, manifest, missing


def native_micro(baseline, days):
    """Reprice identical BASE trades at native MNQ fees; no signal/size selection."""
    rows = []
    recent_days = days[(days >= A.START) & (days <= A.ASOF)]
    for fee in [1.04, 1.24]:
        z = baseline[baseline.date.isin(recent_days)].copy()
        # Gross micro P&L is /10. Native micro commission is NOT /10 of NQ fee.
        z['net'] = z.pnl / 10 - fee - .5 * (1 + z.kind.ne(1).astype(int))
        m = A.measure(z, recent_days, 'BASE_1_MNQ', 'requested_partial')
        m['rt_fee_per_mnq'] = fee
        m['full_target_net'] = 40 * 2 - fee - .5
        m['full_stop_loss'] = 75 * 2 + fee + 1.
        m['full_bracket_breakeven'] = m['full_stop_loss'] / (m['full_stop_loss'] + m['full_target_net'])
        rows.append(m)
    frame = pd.DataFrame(rows)
    frame.to_csv(OUT / 'native_mnq_risk_illustration.csv', index=False)
    return frame


def multiple_testing(baseline, design):
    log = parse_tier_list(str(ROOT / 'TIER_LIST.md'))
    count = len(log) + 4
    rows = []
    for name in A.MODELS:
        z = baseline[baseline.date.dt.year.le(2022)] if name == 'BASE' else pd.read_csv(OUT / (name + '_design_trades.csv'))
        rows.append(dict(model=name, period='2018-22', t=float(design.loc[design.model.eq(name), 't'].iloc[0]),
                         dsr_item_plus_four=M.deflated_sharpe(z.net, count)))
    for period, z in [('all', baseline), ('2023+', baseline[baseline.date.dt.year.ge(2023)])]:
        rows.append(dict(model='BASE', period=period,
                         t=float(z.net.mean() / z.net.std() * np.sqrt(len(z))),
                         dsr_item_plus_four=M.deflated_sharpe(z.net, count)))
    result = dict(current_ranked_items=len(log), added_bracket_alternatives=4, item_plus_four=count,
                  t_threshold=M.t_threshold(count), parsed_variant_count=int(log.variants.sum()),
                  prior_720_parameter_combinations_separate_context=True,
                  prior_314_stresses_not_new_economic_models=True, rows=rows,
                  no_promotion=True, tier_list_sha256=A.sha(ROOT / 'TIER_LIST.md'))
    A.dump('multiple_testing.json', result)
    return result


def main():
    b, metrics, equity, design, manifest, missing = verify()
    days = pd.DatetimeIndex(equity.date)
    micro = native_micro(b, days)
    trials = multiple_testing(b, design)
    diagnostic = read('recent_diagnostic.json')
    recent = metrics[metrics.period.eq('requested_partial')].iloc[0]
    history = metrics[metrics.period.isin(['2018-22', '2023+', 'all'])]
    year = metrics[metrics.period.str.fullmatch(r'20\d\d')]
    monthly = pd.read_csv(OUT / 'baseline_2026_monthly.csv')
    monthly = monthly[monthly.period.ge('2026-08')]
    late = b[b.date.between('2026-08-25', '2026-08-31')]
    recent_table = metrics[metrics.period.isin(['requested_partial', 'last42_available'])]
    tail = pd.DataFrame(diagnostic['comparisons'])
    tail['mean_ci'] = tail.recent_minus_prior_daily_mean_90ci.apply(lambda q: f'[{money(q[0])}, {money(q[2])}]')
    base = design[design.model.eq('BASE')].iloc[0]
    design['net_change'] = design.total / base.total - 1
    design['trade_dd_change'] = design.max_trade_dd / base.max_trade_dd - 1
    reasons = {'BASE': 'reference', 'S60': 'Calmar lower; trade DD higher',
               'S50': 'PF <1.20; Calmar lower; no material gain',
               'T50': 'PF <1.20; Calmar lower; net falls 22%',
               'T60': 'No material risk or reward gain'}
    design['reason'] = design.model.map(reasons)
    cols = [('period','Period',text), ('trades','Trades',integer), ('win','Win',percent),
            ('total','Net/NQ',money), ('avg','Net/trade',money), ('t','t',number),
            ('sharpe','Sharpe',number), ('sortino','Sortino',number),
            ('profit_factor','PF',number), ('calmar','Calmar',number), ('ulcer','Ulcer',number),
            ('max_dd','EOD DD',money), ('max_trade_dd','Trade DD',money)]
    stored = read('stored_mc_export_audit.json')
    boot_path = ROOT / 'analysis/outputs/codex_vb_parity_stress/VB_research_baseline_bootstrap.csv'
    boot = pd.read_csv(boot_path)
    A.dump('report_sources.json', dict(report_script_sha256=A.sha(Path(__file__)),
           prior_baseline_bootstrap=dict(path=boot_path.relative_to(ROOT).as_posix(), sha256=A.sha(boot_path)),
           existing_bootstrap_reused=True, no_additional_strategy_replays=True))
    boot['interval'] = boot.apply(lambda r: f'{r.p5:,.2f} to {r.p95:,.2f}', axis=1)
    full_target, full_stop = 800 - 7.25 - 5, 1500 + 7.25 + 10
    lines = f'''# Vault Break: WATCH — weak recent backtest; no bracket change passes

Summary: August 25–October 9 net is {money(recent.total)}/NQ over {int(recent.trades)} trades; requested coverage after October 9 is missing.
Losses this bad occur in 8.5–10.6% of registered historical resamples: plausible drawdown, deterioration inconclusive.
The 75-point stop versus 40-point target needs a high win rate; recent win rate is {recent.win:.1%}, versus {history[history.period.eq('all')].iloc[0].win:.1%} overall.
All four fixed bracket alternatives fail the 2018–22 improvement gate; stop before alternative validation/full bench.
Actual-account performance remains unknown without verified fills and fees. No supported setting change follows.

Plan: [vb_recent_risk.md](../plans/vb_recent_risk.md), committed **{manifest['plan_commit'][:7]}** before new returns.
Scripts: `analysis/codex_vb_recent_risk.py`, `analysis/codex_vb_recent_risk_report.py`.
Outputs: `analysis/outputs/codex_vb_recent_risk/`. Economic models: **5 total = existing BASE + 4 alternatives**.

## Rule and scope

Unchanged long-only NQ VB: midnight open + .30 × prior ATR15 SMA noise band, midnight VWAP,
30-minute decisions from 10:00 CT, last/flat 14:30 CT, next-minute-open entry, maximum three/day.
Early-close last 11:00 / flat 11:30. BASE target 40 / stop 75 points. Recompute exits and re-entries for every bracket.
One NQ pays $7.25 RT plus one adverse tick at entry and at stop/time exit; target exits have no extra slippage.
Research targets require a full point through. All/long results are identical; **shorts: 0 trades, ratios N/A**.

Requested dates are August 25–October 25. The complete cached day/overnight history ends **October 9**.
Local day-only NQ extends to October 21, but overnight data ends October 9; midnight anchors prevent a valid partial patch.
No unobserved session is zero-filled. The secondary 42-session window ends October 9 and is a different date window.
Stored MC SP report has TargetPts=40, StopPts=75, NumContracts=1, FlaggedContracts=-1; it is the unfiltered reference.
Its nominal end setting is {stored['settings_end']}, but its last observed trade is {stored['last_observed_trade_date']}.
Neither field establishes complete native-bar coverage after October 9. This is not an audit of every deployed sizing/filter configuration.

## Recent results

All monetary results here are after stated costs per fixed one NQ, unless labeled MNQ or chart gross.

{table(recent_table, [('period','Window',text), ('first_date','First',text), ('last_date','Last',text), ('sessions','Sessions',integer), ('trades','Trades',integer), ('win','Win',percent), ('total','Net/NQ',money), ('profit_factor','PF',number), ('max_trade_dd','Trade DD',money)])}

Primary gross {money(recent.gross)} less {money(recent.total_cost)} costs = {money(recent.total)} net.
Average winner {money(recent.average_win)}, average loser {money(recent.average_loss)}; {int(recent.target_count)} targets,
{int(recent.stop_count)} stops, {int(recent.time_count)} time exits; longest losing streak {int(recent.longest_losing_streak)}.
In-window EOD DD is {money(recent.max_dd)}. Carrying the earlier equity peak into the window gives
{money(diagnostic['maximum_carried_eod_drawdown_inside_window'])} maximum DD; starting carried DD was
{money(diagnostic['carried_drawdown_at_window_start'])}, ending carried DD {money(diagnostic['ending_carried_eod_drawdown'])}.

{table(monthly, [('period','Calendar month',text), ('sessions','Observed sessions',integer), ('trades','Trades',integer), ('win','Win',percent), ('total','Net/NQ',money), ('max_trade_dd','Trade DD',money)])}

October is **October 1–9 only**. August and September above cover their whole observed months.
August 25–31 alone contributes {money(late.net.sum())}; September was positive. The requested-window loss does not mean two consecutive losing calendar months.

The stored unfiltered MC report gives {money(stored['recent']['total'])} over {stored['recent']['trades']} trades on the same verified calendar,
versus {money(recent.total)} / {int(recent.trades)} in the stricter research replay. Both show weakness. Existing fill/parity differences remain;
the earlier .25-point reconstruction passed the original parity gate, while 1 point remains the research rule.
Neither chart-backtest figure is realized account P&L.

## Is this a normal drawdown or deterioration?

Compare the **34 observed sessions** with prior pools only. Each pool supplies 5,000 ten-session block-bootstrap paths,
seed 20261025 plus fixed pool offset; use the first 34 cumulative observations. Net tail means P(resampled net <= recent net);
DD tail means P(resampled in-window EOD DD >= recent DD). Tail estimates include the registered +1 correction.
The mean-difference interval resamples both recent and earlier data, reporting recent minus earlier dollars per session.

{table(tail, [('pool','Earlier pool',text), ('earlier_pool_sessions','Sessions',integer), ('net_lower_tail_frequency','Net lower tail',percent), ('dd_upper_tail_frequency','DD upper tail',percent), ('mean_ci','Mean difference 90% CI / NQ/day',text)])}

Both 90% mean-difference intervals include zero. Neither adverse tail crosses the registered 5% threshold.
Registered verdict: **within historical range; deterioration inconclusive**. Overall stays WATCH because the current period/account cannot be completed.
This is roughly one equally bad or worse net result per 9–12 comparable historical resamples, conditional on those distributions.
It is not the probability the strategy is healthy. A permanent regime change can remain undetectable in this short sample.
Overlapping actual historical-window net tail fractions are {tail.iloc[0].overlapping_window_net_lower_fraction:.1%} / {tail.iloc[1].overlapping_window_net_lower_fraction:.1%};
DD fractions are {tail.iloc[0].overlapping_window_dd_upper_fraction:.1%} / {tail.iloc[1].overlapping_window_dd_upper_fraction:.1%}.
Those windows overlap and are descriptive, not independent tests.

## Why the stops feel large

The fixed bracket deliberately risks **75 points to win 40**: one full stop consumes 1.875 full gross targets.
Before costs, full-bracket break-even win rate is {75 / 115:.2%}. At stated NQ costs it is
{full_stop / (full_stop + full_target):.2%} (full win {money(full_target)}, full loss {money(full_stop)}).
Time exits and gaps change realized payoff, so that bracket threshold must not be applied as the break-even rate of every trade.
The recent realized average win/loss mix implies {recent.realized_breakeven_win_rate:.1%} break-even, versus {recent.win:.1%} realized wins.

At **8 MNQ**, a full bracket is $640 target versus $1,200 stop **before costs**. The archived chart rows show that scale;
they do not verify broker outcomes. A smaller contract count scales dollar exposure without changing the point payoff.
The table below reprices the same recent BASE ledger for **one MNQ** using native fees, not one tenth of NQ commissions.
These $1.04 / $1.24 RT fees are inherited research assumptions; actual fees are unverified. Micro fills may also differ from NQ.

{table(micro, [('rt_fee_per_mnq','RT fee/MNQ',money), ('total','Recent net / 1 MNQ',money), ('max_trade_dd','Recent trade DD / 1 MNQ',money), ('full_target_net','Full target net',money), ('full_stop_loss','Full stop loss',money)])}

This is a risk illustration, not a chosen size or funded/evaluation account recommendation. Other strategies, simultaneous losses,
intraday mark-to-market, trailing limits and payout rules are outside this standalone table.

## Bounded optimization: all four alternatives fail

Only **2018–22** alternative returns were computed. Gate: positive net, t>=2, PF>=1.20, >=4 positive years,
Calmar >=BASE, plus either DD <=85% BASE with net >=95%, or net >=115% BASE with DD <=105%.
Gate DD is trade-level; Calmar uses daily EOD DD. All five models have five positive design years.

{table(design, [('model','Model',text), ('target','Target',integer), ('stop','Stop',integer), ('trades','Trades',integer), ('win','Win',percent), ('total','Design net/NQ',money), ('profit_factor','PF',number), ('t','t',number), ('max_trade_dd','Trade DD',money), ('net_change','Net vs BASE',percent), ('trade_dd_change','DD vs BASE',percent), ('calmar','Calmar',number), ('reason','Gate result',text)])}

A 60-point stop slightly increases net but makes historical trade DD worse; a 50-point stop cuts profit and PF.
Larger targets also fail the fixed improvement gate. **No supported optimization among these changes.**
The top-20% cluster contains one setting; it cannot establish a stable plateau. Three overlapping design-fold summaries
are retained in `design_folds.csv`, with no fold-driven selection. No alternative 2023+ replay, recent-window rescue,
extra grid, placebo search, execution-stress extension or full funded bench was run after this cheap-screen failure.

## Historical baseline context

{table(history, cols)}

{table(year, cols)}

Shorts are N/A for every row. Daily ratios include non-trading strategy days on the verified session calendar;
an initial zero is prepended so an immediate loss counts in DD. Ulcer uses the repo's $50,000 reference capital.
Trade DD includes closed-trade sequence, not open-position excursions. **2026 ends October 9.**
2026 year-to-date PF is {year[year.period.eq('2026')].iloc[0].profit_factor:.2f} versus {history[history.period.eq('all')].iloc[0].profit_factor:.2f} overall:
the cushion is thin, even though the recent diagnostic does not establish a permanent decline.

Reuse the prior unchanged BASE 2023+ ten-session/5,000-run bootstrap rather than recomputing it:

{table(boot, [('metric','Metric (daily PF)',text), ('actual','Actual',number), ('interval','90% bootstrap interval',text)])}

Source: `analysis/outputs/codex_vb_parity_stress/VB_research_baseline_bootstrap.csv`, hash recorded in `report_sources.json`.
That existing bootstrap omits the extra initial-zero metric observation; its point estimates differ slightly from the table above.
Previously examined 2023+ history is historical validation, not fresh holdout or forward evidence.

## Actual-account audit and missing inputs

Available archived VB logs are only October 20–21: 142 raw rows, 98 after exact deduplication, six chart closes
across VB / VB-2 account copies and **three shared entry labels**. Separate gross chart sums are -$1,760 / -$1,752;
they must not be added as independent evidence or called executed net losses. The prior order audit has an October 20
rejected entry despite a chart CLOSE row. No complete broker exit/fee ledger exists here.
**Actual-account verdict: INSUFFICIENT VERIFIED FILLS.** No actual/backtest ratio or actual-account deterioration claim.

Needed to finish both sides through October 23:

- Broker execution/trade export for August 25–October 23, including fills, exits, quantity, fees, account/strategy mapping and timezone.
- Complete matching NQ day **and overnight** minute exports through October 23, plus current MC strategy report/settings
  identifying the deployed variant, size and single-print filter configuration. Broker credentials are not needed.
- If available, the account equity/drawdown export to reconcile overlapping strategy positions and account limits.

## Trials, checks and limitations

Four new bracket alternatives; BASE is an unchanged repeat. Prior VB work includes 720 parameter combinations and 314
robustness stresses. Identical engineering reruns do not create new selected models. Current ranked-item count is
{trials['current_ranked_items']}; item count plus four is {trials['item_plus_four']}, t bar **{trials['t_threshold']:.2f}**.
Design DSRs and t statistics at that count are saved in `multiple_testing.json`; none promotes a replacement.
The ranked-item count does not capture every unpublished historical search. No shared trial/ranking file was edited.

Verification: all **1,742** BASE trades reproduce the saved ledger (dates, entries, exits, direction, kind, gross and net).
Independent ledger checks reconcile totals/costs and initial-zero DD, restrict every alternative to pre-2023, confirm the stop gate,
separate account copies and verify source hashes. Synthetic checks cover initial losses, streaks and changed-exit re-entry eligibility.
Missing held-minute inventory: {len(missing)} historical trades / {int(missing.missing_held_minutes.sum())} minutes; **none in this recent window**.
Those historical gaps remain in the baseline; no favorable deletion or cache repair. Fills, source adjustments, one-minute path assumptions,
small recent sample and incomplete current coverage can all affect the conclusion.

No PowerLanguage, live strategy, account/VPS setting or logger changed. No cache rebuilt or package installed.
This audit supports completing current data/fill reconciliation before considering another optimization family.

Reproduce using the installed scientific Python environment (manifest records the exact interpreter):

```powershell
$vbPython = '{manifest['interpreter']}'
& $vbPython -B analysis/codex_vb_recent_risk.py --phase design
& $vbPython -B analysis/codex_vb_recent_risk.py --phase validation
& $vbPython -B analysis/codex_vb_recent_risk_report.py
```

Claude review path: `agents/codex/results/vb_recent_risk.md`.
'''
    REPORT.write_text(lines, encoding='utf-8')
    print(json.dumps(dict(report=str(REPORT), verification='PASS', native_mnq=micro[['rt_fee_per_mnq','total','max_trade_dd']].to_dict('records'),
                          trials=trials['item_plus_four'], t_threshold=trials['t_threshold']), indent=2))


if __name__ == '__main__':
    main()
