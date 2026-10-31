"""Reconcile the supplied zero-cost 20-MNQ VB report; no strategy replays."""
from __future__ import annotations

import argparse
from datetime import datetime
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scratch_data/codex_deps'))
sys.path.insert(0, str(ROOT / 'analysis'))
import numpy as np
import pandas as pd
from openpyxl import load_workbook
from live_vs_backtest import read_trades, compare
import metrics as M
import resampling as R

OUT = ROOT / 'analysis/outputs/codex_vb_aug_oct'
SNAPSHOT = ROOT / 'agents/codex/inputs/vb_aug_oct/vb_aug_oct_mnq.xlsx'
PLAN = 'agents/codex/plans/vb_aug_oct_report_addendum.md'
REFERENCE = ROOT / 'mc_reports/Backtesting Strategy Performance Report _ @NQ - 30 Minutes NQ Vault Break SP.xlsx'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def dump(name, value):
    (OUT / name).write_text(json.dumps(value, indent=2, default=str, allow_nan=False) + '\n', encoding='utf-8')


def settings(path):
    r = pd.read_excel(path, sheet_name='Settings', header=None)
    return {str(row[0]): row[1] for row in r.itertuples(index=False, name=None) if len(row) > 1 and pd.notna(row[1])}


def measures(z, column):
    x = z[column].to_numpy(float)
    wins, losses = x[x > 0], x[x < 0]
    return dict(trades=len(x), winners=len(wins), losers=len(losses), win_rate=float((x > 0).mean()),
                total=float(x.sum()), avg=float(x.mean()), average_winner=float(wins.mean()) if len(wins) else None,
                average_loser=float(-losses.mean()) if len(losses) else None,
                profit_factor=float(wins.sum() / -losses.sum()) if len(losses) else None,
                max_closed_trade_dd=R.max_dd(x),
                t=float(x.mean() / x.std(ddof=1) * np.sqrt(len(x))) if len(x) > 1 and x.std(ddof=1) > 0 else None)


def mdtable(frame, columns):
    rows = ['| ' + ' | '.join(title for _, title, _ in columns) + ' |',
            '| ' + ' | '.join('---' for _ in columns) + ' |']
    for _, r in frame.iterrows():
        rows.append('| ' + ' | '.join(fmt(r[key]) for key, _, fmt in columns) + ' |')
    return '\n'.join(rows)


money = lambda x: f'-${-x:,.2f}' if x < 0 else f'${x:,.2f}'
percent = lambda x: f'{x:.1%}'
number = lambda x: f'{x:.2f}'
integer = lambda x: str(int(x))


def main(source):
    committed = subprocess.check_output(['git', 'show', 'HEAD:' + PLAN], cwd=ROOT, text=True, encoding='utf-8')
    assert committed.replace('\r\n', '\n') == (ROOT / PLAN).read_text(encoding='utf-8').replace('\r\n', '\n')
    plan_commit = subprocess.check_output(['git', 'log', '-1', '--format=%H', '--', PLAN], cwd=ROOT, text=True).strip()
    OUT.mkdir(parents=True, exist_ok=True)
    SNAPSHOT.parent.mkdir(parents=True, exist_ok=True)
    source = Path(source).resolve()
    original_hash = sha(source)
    if SNAPSHOT.exists():
        assert sha(SNAPSHOT) == original_hash, 'Refuse to overwrite an existing different source snapshot'
    else:
        shutil.copyfile(source, SNAPSHOT)
    assert sha(SNAPSHOT) == original_hash
    st, old_st = settings(SNAPSHOT), settings(REFERENCE)
    assert st['Symbol Name'] == '@MNQ' and st['Point Value'] == '$2'
    assert float(st['NumContracts']) == 20 and float(st['TargetPts']) == 40 and float(st['StopPts']) == 75
    raw = pd.read_excel(SNAPSHOT, sheet_name='List of Trades', header=2)
    entries = raw[raw.Type.astype(str).str.startswith('Entry')].reset_index(drop=True)
    exits = raw[raw.Type.astype(str).str.startswith('Exit')].reset_index(drop=True)
    assert len(entries) == len(exits) == 39
    assert raw.Type.str.startswith('Entry').iloc[::2].all() and raw.Type.str.startswith('Exit').iloc[1::2].all()
    assert np.array_equal(entries.Contracts, exits.Contracts)
    assert np.array_equal(entries['Trade #'], np.arange(1, len(entries) + 1))
    assert np.array_equal(entries['Order #'] + 1, exits['Order #'])
    t = read_trades(SNAPSHOT)
    assert (t.qty == 20).all() and (t.side == 1).all()
    assert t.entry_time.is_monotonic_increasing and (t.exit_time >= t.entry_time).all()
    t['kind'] = np.where(t.exit_signal.str.contains('Stop'), 0, np.where(t.exit_signal.str.contains('Profit|Target'), 1, 2))
    t['trade_id'] = entries['Trade #'].astype(int)
    t['source_entry_row'] = 4 + 2 * np.arange(len(t))
    t['source_exit_row'] = t.source_entry_row + 1
    t['reported_zero_cost_pnl'] = entries['Profit ($)'].to_numpy(float)
    t['price_pnl'] = t.pts * 2 * t.qty
    t['one_mnq_gross'] = t.pts * 2
    t['reported_cumulative_pnl'] = entries['Cum. Profit ($)'].to_numpy(float)
    np.testing.assert_allclose(t.price_pnl, t.reported_zero_cost_pnl, atol=1e-8, rtol=0)
    np.testing.assert_allclose(t.price_pnl.cumsum(), t.reported_cumulative_pnl, atol=1e-8, rtol=0)
    assert (t.loc[t.price_pnl.gt(0), 'price_pnl'] == 1600).all()
    for fee in [1.04, 1.24]:
        key = f'native_fee_{fee:.2f}'
        t[key] = t.one_mnq_gross - fee - .5 * (1 + t.kind.ne(1).astype(int))
    t.to_csv(OUT / 'uploaded_trades.csv', index=False)
    wb = load_workbook(SNAPSHOT, read_only=True, data_only=True)
    summary = {cell: wb['Strategy Analysis'][cell].value for cell in ['B4','B5','B6','B16','B18','B21','B24','B25','B26','B33','B34']}
    wb.close()
    m = measures(t, 'reported_zero_cost_pnl')
    assert np.isclose(m['total'], summary['B4']) and m['trades'] == summary['B33']
    assert np.isclose(m['win_rate'], summary['B34'])
    assert np.isclose(m['max_closed_trade_dd'], -summary['B18'])
    assert np.isclose(m['profit_factor'], abs(summary['B21']))
    assert np.isclose(m['winners'] * m['average_winner'], summary['B5'])
    assert np.isclose(-m['losers'] * m['average_loser'], summary['B6'])
    monthly = []
    for month, z in t.groupby(t.session.dt.to_period('M'), sort=True):
        r = measures(z, 'reported_zero_cost_pnl')
        r.update(month=str(month), gross_per_mnq=float(z.one_mnq_gross.sum()))
        monthly.append(r)
    monthly = pd.DataFrame(monthly)
    monthly.to_csv(OUT / 'monthly.csv', index=False)
    post = t[t.session > '2026-10-09']
    pre = t[t.session <= '2026-10-09']
    segments = pd.DataFrame([dict(segment=label, **measures(z, 'reported_zero_cost_pnl'))
                             for label, z in [('through_Oct9', pre), ('after_Oct9', post), ('all_upload', t)]])
    segments.to_csv(OUT / 'segments.csv', index=False)
    native = pd.DataFrame([dict(fee_per_mnq=fee, **measures(t, f'native_fee_{fee:.2f}')) for fee in [1.04, 1.24]])
    native['total_at_20'] = native.total * 20
    native['closed_trade_dd_at_20'] = native.max_closed_trade_dd * 20
    native.to_csv(OUT / 'native_fee_illustrations.csv', index=False)
    # Reuse the existing exact-time pairing engine. Its generic live/bt names
    # are relabeled: neither input is evidence of broker executions.
    old = read_trades(REFERENCE)
    lo, hi = t.session.min(), pd.Timestamp('2026-10-09')
    old_common = old[old.session.between(lo, hi)]
    pairs, restricted_old = compare(pre, old_common, window=0)
    assert len(restricted_old) == len(old_common)
    pairs['status'] = pairs.status.replace({'extra (live only)': 'uploaded only', 'missed (backtest only)': 'reference only'})
    pairs = pairs.rename(columns={c: c.replace('live_', 'uploaded_').replace('bt_', 'reference_') for c in pairs.columns})
    pairs = pairs.rename(columns={'entry_slip_ticks': 'entry_price_difference_ticks', 'exit_slip_ticks': 'exit_price_difference_ticks'})
    assert np.isclose(pairs.uploaded_pts.sum(), pre.pts.sum())
    assert np.isclose(pairs.reference_pts.sum(), old_common.pts.sum())
    pairs.to_csv(OUT / 'common_calendar_pairing.csv', index=False)
    attribution = pairs.assign(gross_difference_at_20_mnq=(pairs.uploaded_pts - pairs.reference_pts) * 40).groupby('session').gross_difference_at_20_mnq.sum()
    attribution[~np.isclose(attribution, 0)].to_csv(OUT / 'common_period_difference_by_day.csv')
    matched = pairs[pairs.status.eq('matched')]
    pair_info = dict(common_start=str(lo.date()), common_end=str(hi.date()), uploaded_trades=len(pre), reference_trades=len(old_common),
                     counts={k:int(v) for k,v in pairs.status.value_counts().items()},
                     uploaded_gross_20mnq=float(pre.price_pnl.sum()),
                     reference_gross_scaled_20mnq=float(old_common.pts.sum() * 40),
                     total_difference_points=float(pre.pts.sum() - old_common.pts.sum()),
                     matched_point_difference=float((matched.uploaded_pts - matched.reference_pts).sum()),
                     matched_different_exit_signal=int((matched.uploaded_exit_signal != matched.reference_exit_signal).sum()))
    dump('pairing_summary.json', pair_info)
    # Source daily rows are report outputs, not independent market-data coverage.
    periodical = pd.read_excel(SNAPSHOT, sheet_name='Periodical Analysis', header=None)
    daily_start = next(i for i,v in enumerate(periodical[0]) if v == 'Daily Period Analysis')
    daily_rows = []
    for row in periodical.iloc[daily_start + 3:].itertuples(index=False, name=None):
        if isinstance(row[0], (pd.Timestamp, datetime)):
            daily_rows.append(dict(date=row[0], report_pnl=float(row[1]), report_trades=int(row[6])))
        elif daily_rows:
            break
    report_daily = pd.DataFrame(daily_rows).sort_values('date')
    expected = t.groupby('session').price_pnl.sum().reindex(pd.DatetimeIndex(report_daily.date), fill_value=0.)
    np.testing.assert_allclose(expected, report_daily.report_pnl, atol=1e-8, rtol=0)
    assert report_daily.report_trades.sum() == len(t)
    report_daily.to_csv(OUT / 'report_daily.csv', index=False)
    # Descriptive ratios on explicit weekdays only; no claim of verified bars.
    calendar = pd.bdate_range(t.session.min(), t.session.max())
    daily = t.groupby('session').one_mnq_gross.sum().reindex(calendar, fill_value=0.)
    standard = M.perf(pd.Series(np.r_[0., daily]), t.one_mnq_gross)
    standard.update(side='all/long', shorts='N/A (zero trades)', calendar='weekday accounting convention, not verified bar coverage',
                    annualization='252 sessions; interval ends at last observed trade October 21')
    dump('descriptive_standard_metrics.json', standard)
    dump('source_audit.json', dict(source_path=str(source), snapshot=SNAPSHOT.relative_to(ROOT).as_posix(), sha256=original_hash,
         plan=PLAN, plan_commit=plan_commit, settings={k:str(v) for k,v in st.items()},
         reference_settings={k:str(v) for k,v in old_st.items()}, summary_cells=summary, ledger_metrics=m,
         last_observed_trade=str(t.exit_time.max()), nominal_end=str(st['End Date']), complete_raw_coverage_verified=False,
         source_unchanged=(sha(source) == original_hash), new_strategy_replays=0, new_economic_trials=0,
         script_sha256=sha(Path(__file__)), reference_sha256=sha(REFERENCE)))
    checks = dict(equal_entry_exit_count=True, quantities_and_adjacent_orders_match=True, every_price_pnl_reconciles=True,
                  cumulative_pnl_reconciles=True, summary_profit_win_count_dd_reconciles=True, daily_totals_reconcile=True,
                  profit_factor_sign_anomaly=True, last_trade_not_assumed_raw_coverage=True,
                  no_zero_cost_pnl_called_realized_net=True, no_additional_optimization=True)
    dump('checks.json', checks)
    assert sha(source) == original_hash
    report = f'''# Vault Break August–October upload: WATCH — added losses; execution comparison unresolved

Summary: Supplied 20-MNQ backtest reports {money(m['total'])}, 39 trades, 51.3% wins and PF {m['profit_factor']:.2f}, before costs.
October contributes -$11,690, including -$7,400 after the earlier October-9 cutoff. September remains positive.
Closed-trade DD is $16,120 at 20 MNQ; reported strategy DD is $16,340. Broker results remain unverified.
Bar Magnifier is disabled, with Classic fills and zero fees/slippage; this is not comparable enough for a new deterioration probability.
The prior 8–11% tail result applies only to the original window. No new optimization or setting change follows.

Plan: [`vb_aug_oct_report_addendum.md`](../plans/vb_aug_oct_report_addendum.md), **{plan_commit[:7]}**.
Parent: [`vb_recent_risk.md`](vb_recent_risk.md), baseline audit **2f9f581** / preregistration **832f277**.
Script: `analysis/codex_vb_aug_oct_report.py`. Outputs: `analysis/outputs/codex_vb_aug_oct/`.
Source snapshot: `agents/codex/inputs/vb_aug_oct/vb_aug_oct_mnq.xlsx`, SHA256 `{original_hash}`.
New economic models/return replays: **0**. This reconciles a user-supplied backtest, not broker records or a fresh holdout.

## What the report establishes

Report settings: MNQ, $2/point, 20 contracts, target 40 / stop 75, max 3/day, 30-minute chart, original .30 ATR15 rule.
Export setting starts {st['Start Date']}; nominal end is {st['End Date']}. First/last trades are
{t.entry_time.min()} / {t.exit_time.max()}. No open trades are reported. The report's daily table ends October 21.
October 22–23 native-bar completeness is unverified. August 25–26 are outside this upload's trade range.
The attached Apex Target Guard has StartBalance=150000 / TargetBalance=159050; logger tag VB150.
Every observed exit is a normal target, stop or VB EOD, with no guard-labeled exit. This does not independently verify guard behavior.

| Metric | All = long, at 20 MNQ |
| --- | ---: |
| Reported P&L before fees/slippage | {money(m['total'])} |
| Closed trades | {m['trades']} |
| Winners / losers | {m['winners']} / {m['losers']} |
| Win rate | {percent(m['win_rate'])} |
| Average winner / average loser | {money(m['average_winner'])} / {money(m['average_loser'])} |
| Recomputed profit factor | {m['profit_factor']:.3f} |
| Closed-trade peak-to-trough DD, including initial zero | {money(m['max_closed_trade_dd'])} |
| Reported strategy DD (includes open-position effects) | {money(-summary['B16'])} |
| Gross P&L / closed-trade DD per one MNQ | {money(m['total']/20)} / {money(m['max_closed_trade_dd']/20)} |

Shorts: zero, ratios N/A. `Strategy Analysis!B21` stores **negative** PF; standard PF is positive gross profits divided by
absolute gross losses: $32,000 / $46,230 = {m['profit_factor']:.3f}. The same sign anomaly affects the average win/loss ratio.
Some unused/undefined cells show `#ERROR!`; totals above reconcile to prices and the complete closed-trade list.
Do not interpret the workbook's Adjusted Net Profit as a fee-adjusted broker result.

## Month and added-period attribution

{mdtable(monthly, [('month','Observed month',str), ('trades','Trades',integer), ('win_rate','Win',percent), ('total','Gross at 20 MNQ',money), ('gross_per_mnq','Gross / 1 MNQ',money)])}

August contains August 27–28 trades only. October's last observed trade is October 21.
September is positive, consistent with the earlier audit. October is the principal new weakness.

{mdtable(segments, [('segment','Segment',str), ('trades','Trades',integer), ('win_rate','Win',percent), ('total','Gross at 20 MNQ',money)])}

The post-cutoff four trades are October 19 stop, October 20 stop, October 21 target and stop.
They are **backtest events**; the October 20 chart trade is not proof of a broker fill, given the prior rejected-entry evidence.

## Stop versus win arithmetic and native costs

At this report's **20 MNQ**, the full stop is **$3,000** and target **$1,600**, before costs.
The point ratio remains 75/40. All 20 winners reach the full target; {int(t.kind.eq(0).sum())} losses are full stops and
{int(t.kind.eq(2).sum())} are time exits. At the observed average win/loss mix, break-even win rate is
{m['average_loser']/(m['average_loser']+m['average_winner']):.1%}; actual win rate is {m['win_rate']:.1%}.
There is no new larger point stop in this export. Dollar losses are larger because its quantity is 20 MNQ versus the earlier eight-MNQ examples.

The workbook charges **no commissions and no slippage**. Apply the already registered $1.04 / $1.24 RT native-MNQ fee
assumptions and one adverse tick at market entry and stop/time exit to these same trades:

{mdtable(native, [('fee_per_mnq','Assumed RT fee/MNQ',money), ('total','Net / 1 MNQ',money), ('total_at_20','Net at 20 MNQ',money), ('closed_trade_dd_at_20','Closed-trade DD at 20 MNQ',money)])}

These are illustrations, not actual fees, broker fills or a selected position size. They do not model changed fills, liquidity,
portfolio exposure or account-liquidation rules. Multiplying an unchanged backtest by size cannot establish account survivability.

## Common-period comparison: do not call this execution slippage

Compare exact entry-bar timestamps/side with the saved unfiltered NQ SP report, {pair_info['common_start']}–{pair_info['common_end']}.
Use the repository's `read_trades` and `compare(window=0)`, normalized to points per contract. No fuzzy match or deleted residual.
Both inputs are chart backtests. Pairing output is relabeled from the generic tool's live/bt terminology.

{pair_info['uploaded_trades']} uploaded / {pair_info['reference_trades']} reference trades: {pair_info['counts'].get('matched',0)} matched,
{pair_info['counts'].get('uploaded only',0)} uploaded-only, {pair_info['counts'].get('reference only',0)} reference-only.
Uploaded gross is {money(pair_info['uploaded_gross_20mnq'])}; reference gross scaled to 20 MNQ is
{money(pair_info['reference_gross_scaled_20mnq'])}. Total points difference is {pair_info['total_difference_points']:.2f} per contract;
matched-pair points difference is {pair_info['matched_point_difference']:.2f}.
All residuals and price differences are retained in `common_calendar_pairing.csv`.

Examples: upload adds an October 2 11:30 stopped trade, lacks the reference's October 5 13:00 target,
and has different October 6 re-entry sequencing. **Both reports have Bar Magnifier disabled.** Their limit-fill assumptions differ:
uploaded **{st['Backtesting Assumptions']}**; reference **{old_st['Backtesting Assumptions']}**.
MNQ versus NQ source prices also differ. These observations do not prove which setting caused each mismatch.
Thirty-minute OHLC without native intrabar replay can change exit ordering, same-bar fills and later re-entries.
We cannot repair that by assuming a favorable path or by choosing whichever report has better returns.

## Drawdown verdict and what is still needed

This export **increases concern**: the newer October trade list adds substantial losses. It does not establish permanent
edge decay, and the original 8–11% historical frequency must not be attached to this longer, differently simulated sample.
No new bootstrap alarm or optimization was fitted to this upload. The four bracket alternatives remain rejected by the earlier design gate.
The original audit's complete one-minute history still ends October 9; a report adds results, not the missing raw day/overnight bars.

Next comparable evidence: rerun the **same rule/quantity/dates** in a research chart with one-minute Bar Magnifier, explicit actual
commission/slippage and the documented reference limit-through assumption. Export its report/settings and matching day/overnight minute
bars through October 23. This is a controlled execution check, not an exit-parameter search. An independent offline replay can then
attribute the October 2/5/6 residuals. Merely enabling Bar Magnifier does not establish identical source data or fills.
For the actual-account side, a complete broker fill/exit/fee export is still required. No live chart/settings, account, logger or VPS was changed.

Checks: 39 adjacent entry/exit pairs, matching quantities/order numbers; every price × 20 × $2 equals reported trade P&L;
cumulative, daily, monthly and report totals/win counts reconcile; initial-zero closed-trade DD agrees with reported $16,120.
Source workbook is unchanged and preserved byte-for-byte. No cache rebuilt, library installed, new strategy variant or account bench run.
Additional weekday-based descriptive ratios are in `descriptive_standard_metrics.json`; their calendar is not proof of bar coverage.

Reproduce from repo root with the previously configured Python:

```powershell
$vbPython = '{sys.executable}'
& $vbPython -B analysis/codex_vb_aug_oct_report.py --source agents/codex/inputs/vb_aug_oct/vb_aug_oct_mnq.xlsx
```

Claude review path: `agents/codex/results/vb_aug_oct_report.md`.
'''
    (ROOT / 'agents/codex/results/vb_aug_oct_report.md').write_text(report, encoding='utf-8')
    print(json.dumps(dict(verification='PASS', gross=m, added=segments.iloc[1].to_dict(), common_period=pair_info,
                          fee_illustrations=native[['fee_per_mnq','total_at_20','closed_trade_dd_at_20']].to_dict('records')),indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=SNAPSHOT)
    main(parser.parse_args().source)
