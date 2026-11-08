"""Frozen whole-ES observed-data adaptation of SSRN7323419, not a SPY replica.

Run --stage design first. No imputed prices; next observed minute opens only.
See agents/codex/plans/delgado_es_20261108.md. No broker or live I/O.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import pickle
import subprocess
from pathlib import Path

import numpy as np
import pandas as pd

from codex_s03_calendar import calendar_status
from metrics import perf, deflated_sharpe, t_threshold

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'analysis/outputs/codex_delgado_es'
CAPITAL, POINT, TICK, FEE_RT = 100000., 50., .25, 5.
CHECKS = np.arange(540, 871, 30)  #09:00..14:30CT, closes


def digest(path):
    with open(path, 'rb') as source:
        hasher = hashlib.sha256()
        for block in iter(lambda: source.read(1024 * 1024), b''):
            hasher.update(block)
        return hasher.hexdigest()


def build_features(grid, end):
    """Past-only feature formation. Never calculate returns beyond declared stage end."""
    days, normal_history, cash_returns = [], [], []
    previous_close = np.nan
    for row, integer_date in enumerate(grid.dates):
        dt = pd.Timestamp(str(integer_date))
        if dt > pd.Timestamp(end):
            break
        cal = calendar_status(dt)
        if cal['kind'] not in ('normal', 'early'):
            continue
        close_j = cal['cash_close_j']
        o, h, l, c, v = (getattr(grid, name)[row].copy() for name in ('o','h','l','c','v'))
        mask = (np.isfinite(o) & np.isfinite(h) & np.isfinite(l) & np.isfinite(c) & np.isfinite(v)
                & (o > 0) & (l > 0) & (h >= np.maximum(o, c)) & (l <= np.minimum(o, c)) & (v >= 0))
        within = np.arange(511, close_j + 1)
        prefix = np.logical_and.accumulate(mask[within])
        volume = np.cumsum(np.where(mask[within], v[within], 0.))
        pv = np.cumsum(np.where(mask[within], (h[within]+l[within]+c[within])/3*v[within], 0.))
        vw = np.full(1440, np.nan)
        cv = np.full(1440, np.nan)
        valid = prefix & (volume > 0)
        vw[within[valid]] = pv[valid] / volume[valid]
        cv[within[prefix]] = volume[prefix]
        opening = o[511] if mask[511] else np.nan
        curve = np.where(mask[CHECKS], np.abs(c[CHECKS]/opening - 1), np.nan)
        cumulative = cv[CHECKS]
        if len(normal_history) >= 14:
            prior_curve = np.array([x[0] for x in normal_history[-14:]])
            prior_volume = np.array([x[1] for x in normal_history[-14:]])
            sigma = prior_curve.mean(axis=0)
            average_volume = prior_volume.mean(axis=0)
        else:
            sigma, average_volume = np.full(12, np.nan), np.full(12, np.nan)
        vol = float(np.std(cash_returns[-14:], ddof=1)) if len(cash_returns) >= 14 else np.nan
        days.append(dict(date=dt, row=row, close_j=close_j, o=o, c=c, mask=mask, vwap=vw,
                         opening=opening, prior_close=previous_close, sigma=sigma,
                         relative_volume=cumulative / average_volume, vol=vol,
                         missing_minutes=int((~mask[within]).sum()),
                         all_missing=not bool(mask[within].any())))
        if cal['kind'] == 'normal':
            normal_history.append((curve, cumulative))
        today_close = c[close_j] if mask[close_j] else np.nan
        cash_returns.append(today_close / previous_close - 1 if np.isfinite(previous_close) else np.nan)
        previous_close = today_close
    return days


def quantity(day_nav, current_nav, price, vol, side, model, rv=1., binding=False, performance=1.):
    """Fixed at decision price; never accepts a future fill price for order sizing."""
    if not all(np.isfinite(x) and x > 0 for x in (day_nav, current_nav, price, vol)):
        return 0
    multiplier = min(4., .02 / vol)
    if model != 'base':
        if not np.isfinite(rv) or not np.isfinite(performance):
            return 0
        multiplier *= float(np.clip(rv, .5, 1.5)) * (.7 if binding else 1.)
        multiplier *= .75 if side < 0 else 1.
        multiplier *= performance
    wanted = math.floor(day_nav * min(4., multiplier) / (price * POINT))
    # q*notional <= 4*(current_nav - q*roundtripcommission).
    reserve_cap = math.floor(4 * current_nav / (price * POINT + 4 * FEE_RT))
    return max(0, min(wanted, reserve_cap))


def replay(days, model, shadow=None):
    nav, daily, trades, cap_breaches = CAPITAL, [], [], []
    shadow = {} if shadow is None else shadow
    shadow_history = []
    for day in days:
        if day['date'] < pd.Timestamp('2018-01-01'):
            continue
        start_nav, day_net, unknown = nav, 0., day['all_missing']
        perf_scale = 1.
        if model == 'candidate' and len(shadow_history) >= 30 and np.isfinite(shadow_history[-30:]).all():
            perf_scale = .9 if sum(shadow_history[-30:]) > 0 else 1.1
        held = None
        disabled = False
        index = 511
        while index <= day['close_j']:
            if not day['mask'][index]:
                disabled = True
                if held is not None:
                    held['unknown_path'] = True
                    unknown = True
                    held['force_exit'] = True
                index += 1
                continue
            if held is not None:
                marked_nav = (nav + day_net + held['side']*(day['c'][index]-held['entry_raw'])*POINT*held['lots']
                              - (FEE_RT+TICK*POINT)*held['lots'])
                lev = held['lots']*day['c'][index]*POINT/marked_nav if marked_nav > 0 else float('inf')
                if lev > 4 + 1e-12 and not held.get('marked_cap_flagged'):
                    cap_breaches.append(dict(date=day['date'].isoformat(), mark_j=index, leverage=lev))
                    held['marked_cap_flagged'] = True
            # A missing observation triggers first observed open liquidation; no future entries that day.
            if held is not None and held.get('force_exit'):
                exit_index, reason = index, 'missing_path_exit'
            elif index == day['close_j'] - 1:
                if held is None:
                    break
                exit_index, reason = index + 1, 'scheduled_flat'
            elif index in CHECKS and index < day['close_j'] - 1:
                k = int((index - 540) // 30)
                sigma, vw = day['sigma'][k], day['vwap'][index]
                current, opened, previous = day['c'][index], day['opening'], day['prior_close']
                if not np.isfinite([sigma, vw, opened, previous]).all():
                    index += 1
                    continue
                long_vm, short_vm = (1., 1.) if model == 'base' else (1.3, 1.6)
                upper = max(opened, previous) * (1 + long_vm * sigma)
                lower = min(opened, previous) * (1 - short_vm * sigma)
                long_stop, short_stop = max(upper, vw), min(lower, vw)
                exit_now = held is not None and ((held['side'] == 1 and current <= long_stop)
                                                 or (held['side'] == -1 and current >= short_stop))
                direction = 1 if current > long_stop else -1 if current < short_stop else 0
                if held is not None and not exit_now:
                    index += 1
                    continue
                exit_index, reason = index + 1, 'checkpoint'
                # Freeze potential reversal quantity BEFORE reading the next minute's open.
                requested = 0
                if direction and not disabled:
                    bound = upper >= vw if direction == 1 else lower <= vw
                    marked_nav = nav + day_net
                    if held is not None:
                        marked_nav += (held['side']*(current-held['entry_raw'])*POINT
                                       - FEE_RT - 2*TICK*POINT)*held['lots']
                    requested = quantity(start_nav, marked_nav, current, day['vol'], direction,
                                         model, day['relative_volume'][k], bound, perf_scale)
            else:
                index += 1
                continue
            # No price invention or retrospective decision to skip an earlier signal.
            if exit_index > day['close_j'] or not day['mask'][exit_index]:
                disabled = True
                unknown = unknown or held is not None or (reason == 'checkpoint' and requested > 0)
                if held is not None:
                    held.update(unknown_path=True, force_exit=True)
                index += 1
                continue
            raw = day['o'][exit_index]
            if held is not None:
                side, lots = held['side'], held['lots']
                gross = side * (raw - held['entry_raw']) * POINT * lots
                slip = 2 * TICK * POINT * lots
                commission = FEE_RT * lots
                net = gross - slip - commission
                trades.append(dict(date=day['date'], side=side, lots=lots,
                    entry_decision_j=held['decision_j'], entry_fill_j=held['fill_j'], exit_fill_j=exit_index,
                    entry_raw=held['entry_raw'], exit_raw=raw,
                    entry=held['entry_raw'] + side*TICK, exit=raw-side*TICK,
                    gross=gross, slippage=slip, commission=commission, net=net,
                    stress_net=net - 2*TICK*POINT*lots, unknown_path=held['unknown_path'], reason=reason))
                day_net += net
                held = None
            if reason == 'checkpoint' and requested and not disabled:
                # Direction/quantity came from the decision close, not from raw (future open).
                held = dict(side=direction, lots=requested, decision_j=index, fill_j=exit_index,
                            entry_raw=raw, unknown_path=False)
                actual_nav = nav + day_net - requested*(FEE_RT+TICK*POINT)
                leverage = requested * raw * POINT / actual_nav if actual_nav > 0 else float('inf')
                if leverage > 4 + 1e-12:
                    cap_breaches.append(dict(date=day['date'].isoformat(), fill_j=exit_index, leverage=leverage))
            index = exit_index
        if held is not None:
            raise ValueError(f"Unresolved terminal position {day['date']}; cannot invent a close")
        nav += day_net
        if nav <= 0:
            raise ValueError('Nonpositive research NAV: path stopped')
        daily.append(dict(date=day['date'], net=day_net, start_nav=start_nav, end_nav=nav,
                          return_value=day_net/start_nav if not unknown else np.nan,
                          complete=not unknown, missing_minutes=day['missing_minutes'],
                          performance_scale=perf_scale))
        shadow_history.append(shadow.get(day['date'], np.nan))
    columns = ['date','side','lots','entry_decision_j','entry_fill_j','exit_fill_j','entry_raw','exit_raw',
               'entry','exit','gross','slippage','commission','net','stress_net','unknown_path','reason']
    return pd.DataFrame(daily), pd.DataFrame(trades, columns=columns), cap_breaches


def t_stat(values):
    a = np.array(values, dtype=float)
    a = a[np.isfinite(a)]
    return float(a.mean() / a.std(ddof=1) * math.sqrt(len(a))) if len(a) > 1 and a.std() else np.nan


def summarize(daily, trades, trials):
    known = daily[daily.complete].set_index('date')
    selected = trades[~trades.unknown_path & trades.date.isin(known.index)] if len(trades) else trades
    rows = []
    for label, side in [('whole', None), ('long', 1), ('short', -1)]:
        t = selected if side is None else selected[selected.side == side]
        x = t.groupby('date').net.sum().reindex(known.index, fill_value=0.) if len(t) else pd.Series(0., index=known.index)
        numbers = perf(x, t.net if len(t) else [], CAPITAL)
        # Correct repository's omission of initial capital as a drawdown peak.
        equity = CAPITAL + x.cumsum().to_numpy()
        peak = np.maximum.accumulate(np.r_[CAPITAL, equity])[1:]
        numbers['max_dd'] = float(np.max(peak-equity)) if len(equity) else 0.
        numbers['calmar'] = numbers['annual']/numbers['max_dd'] if numbers['max_dd'] else None
        numbers.update(side=label, net=float(x.sum()), t_trade=t_stat(t.net if len(t) else []),
                       t_daily=t_stat(x), mean_per_es_lot=float((t.net/t.lots).mean()) if len(t) else None,
                       dsr_daily=float(deflated_sharpe(x, trials)), complete_days=len(x),
                       commission=float(t.commission.sum()) if len(t) else 0.,
                       slippage=float(t.slippage.sum()) if len(t) else 0.,
                       gross=float(t.gross.sum()) if len(t) else 0.,
                       stress_net=float(t.stress_net.sum()) if len(t) else 0.)
        if side is None:
            numbers['t_return'] = t_stat(known.return_value)
            numbers['return_sharpe'] = float(known.return_value.mean()/known.return_value.std()*math.sqrt(252))
            numbers['return_dsr'] = float(deflated_sharpe(known.return_value, trials))
            numbers['nav_end_observed_path'] = float(daily.end_nav.iloc[-1])
        rows.append(numbers)
    years = []
    for year, block in known.groupby(known.index.year):
        t = selected[selected.date.dt.year == year]
        years.append(dict(year=int(year), net=float(block.net.sum()), trades=len(t),
                          return_complete_days=float(np.prod(1+block.return_value)-1),
                          complete_days=len(block),
                          long_net=float(t.loc[t.side == 1, 'net'].sum()),
                          short_net=float(t.loc[t.side == -1, 'net'].sum())))
    return rows, years


def clean_json(obj):
    if isinstance(obj, dict):
        return {k:clean_json(v) for k,v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [clean_json(v) for v in obj]
    if isinstance(obj, (float, np.floating)) and not np.isfinite(obj):
        return None
    if isinstance(obj, np.generic):
        return obj.item()
    return obj


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--stage', choices=['design', 'recent'], required=True)
    args = parser.parse_args()
    if args.stage == 'recent':
        prior = json.loads((OUT/'design/summary.json').read_text())
        if not prior['design_pass']:
            raise ValueError('Design failed: new 2023+ returns forbidden by frozen protocol')
    end = '2022-12-31' if args.stage == 'design' else '2026-12-31'
    with (ROOT/'scratch_data/ge.pkl').open('rb') as file:
        grid = pickle.load(file)
    days = build_features(grid, end)
    results = {}
    for model in ('base', 'shadow', 'candidate'):
        shadow = dict(zip(results['shadow'][0].date, results['shadow'][0].return_value)) if model == 'candidate' else None
        results[model] = replay(days, model, shadow)
    trials = len(pd.read_csv(ROOT/'TRIALS.csv')) + 3 + 80
    destination = OUT/args.stage
    destination.mkdir(parents=True, exist_ok=True)
    summaries, annual, gates = {}, {}, {}
    for model, (daily, trades, breaches) in results.items():
        if args.stage == 'recent':
            daily = daily[daily.date >= '2023-01-01'].copy()
            trades = trades[trades.date >= '2023-01-01'].copy()
        daily.to_csv(destination/f'{model}_daily.csv', index=False)
        trades.to_csv(destination/f'{model}_trades.csv', index=False)
        summaries[model], annual[model] = summarize(daily, trades, trials)
        gates[model] = {'unknown_days': int((~daily.complete).sum()), 'calendar_days': len(daily),
                        'unknown_trades': int(trades.unknown_path.sum()), 'fill_cap_breaches': len(breaches)}
        (destination/f'{model}_cap_breaches.json').write_text(json.dumps(breaches, indent=2)+'\n')
        # Reconcile complete and incomplete observed-endpoint ledgers without zeroing unknown days.
        assert abs(trades.net.sum()-daily.net.sum()) < 1e-6
        assert np.allclose(trades.gross-trades.slippage-trades.commission, trades.net)
    a, b = summaries['candidate'][0], summaries['base'][0]
    ratio = lambda x: x['net']/x['max_dd'] if x['max_dd'] else 0.
    gates['candidate_criteria'] = {
        'at_least_300_trades': a['trades'] >= 300,
        'at_least_95pct_days_known': 1-gates['candidate']['unknown_days']/gates['candidate']['calendar_days'] >= .95,
        'positive_net': a['net'] > 0, 'positive_stress': a['stress_net'] > 0,
        'four_positive_years': sum(r['net'] > 0 for r in annual['candidate']) >= 4,
        'daily_return_t_at_least_2': a['t_return'] >= 2,
        'trade_t_at_least_2': a['t_trade'] >= 2,
        'net_dd_improves_10pct': ratio(a) >= 1.1*ratio(b),
        'retains_70pct_baseline_net': b['net'] <= 0 or a['net'] >= .7*b['net']}
    summary = dict(stage=args.stage, end=end, trials_lower_bound=trials, t_bar=t_threshold(trials),
        summaries=summaries, yearly=annual, gates=gates,
        design_pass=all(gates['candidate_criteria'].values()),
        account_admission=False,
        manifest={'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
                  'code_sha256':digest(Path(__file__)), 'cache_sha256':digest(ROOT/'scratch_data/ge.pkl'),
                  'raw_hashes':{str(p.relative_to(ROOT)):digest(p) for p in sorted((ROOT/'data').glob('ES_1min_20*.csv'))},
                  'plan_sha256':digest(ROOT/'agents/codex/plans/delgado_es_20261108.md'),
                  'point_value':POINT, 'tick':TICK, 'fee_roundtrip_es':FEE_RT,
                  'initial_research_nav':CAPITAL, 'numpy':np.__version__, 'pandas':pd.__version__},
        coverage=[{'date':d['date'].isoformat(), 'missing_minutes':d['missing_minutes']} for d in days
                  if d['missing_minutes']])
    (destination/'summary.json').write_text(json.dumps(clean_json(summary),indent=2,allow_nan=False)+'\n')
    print(json.dumps(clean_json({'design_pass':summary['design_pass'], 'whole':{m:s[0] for m,s in summaries.items()},
                                 'criteria':gates['candidate_criteria']}),allow_nan=False))


if __name__ == '__main__':
    main()
