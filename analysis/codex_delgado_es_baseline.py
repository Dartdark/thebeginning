"""Once-only unchanged ES baseline historical validation; no rule search.

Protocol: agents/codex/plans/delgado_es_baseline_20261108.md.
Reuses frozen core; requires exact prior-design prefix and input identity.
"""
import hashlib
import json
import pickle
import subprocess
from pathlib import Path

import numpy as np
import pandas as pd

import codex_delgado_es as E
from resampling import bootstrap

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'analysis/outputs/codex_delgado_es_baseline'


def main():
    previous = json.loads((E.OUT/'design/summary.json').read_text())
    if E.digest(Path(E.__file__)) != previous['manifest']['code_sha256']:
        raise ValueError('Frozen strategy code mismatch')
    if E.digest(ROOT/'scratch_data/ge.pkl') != previous['manifest']['cache_sha256']:
        raise ValueError('Frozen market cache mismatch')
    for name, expected in previous['manifest']['raw_hashes'].items():
        if E.digest(ROOT/name) != expected:
            raise ValueError(f'Raw file mismatch: {name}')
    with (ROOT/'scratch_data/ge.pkl').open('rb') as file:
        grid = pickle.load(file)
    days = E.build_features(grid, '2026-12-31')
    daily, trades, flags = E.replay(days, 'base')
    # Verify unchanged design prefix BEFORE inspecting, summarizing or writing recent outcomes.
    prefix_hashes = {}
    for label, frame in [('daily', daily), ('trades', trades)]:
        rendered = frame.loc[frame.date < '2023-01-01'].to_csv(index=False).encode()
        prior = E.OUT/f'design/base_{label}.csv'
        if hashlib.sha256(rendered).hexdigest() != E.digest(prior):
            raise ValueError(f'Prior design {label} CSV differs; halt without recent inspection')
        prefix_hashes[label] = E.digest(prior)
    OUT.mkdir(parents=True, exist_ok=True)
    daily.to_csv(OUT/'full_daily.csv', index=False)
    trades.to_csv(OUT/'full_trades.csv', index=False)
    recent = daily[daily.date >= '2023-01-01'].copy()
    recent_trades = trades[trades.date >= '2023-01-01'].copy()
    recent.to_csv(OUT/'recent_daily.csv', index=False)
    recent_trades.to_csv(OUT/'recent_trades.csv', index=False)
    trials = previous['trials_lower_bound'] + 1  # conservative extra post-design nomination, no reset.
    summaries, annual = E.summarize(recent, recent_trades, trials)
    full_summary, full_annual = E.summarize(daily, trades, trials)
    known = recent[recent.complete].set_index('date')
    eligible = recent_trades[~recent_trades.unknown_path & recent_trades.date.isin(known.index)]
    assert abs(recent_trades.net.sum()-recent.net.sum()) < 1e-6
    assert np.allclose(recent_trades.gross-recent_trades.slippage-recent_trades.commission, recent_trades.net)
    intervals = {}
    for key, values, capital in [('dollar_pnl', known.net, E.CAPITAL), ('daily_return', known.return_value, 1.)]:
        result = bootstrap(values, n=1000, block=20, seed=7323419, capital=capital)
        result.to_csv(OUT/f'bootstrap_{key}.csv')
        intervals[key] = {'metrics': result.to_dict(orient='index'),
                          'p_sharpe_le_zero': result.attrs['p_sharpe_le_0']}
    # Fixed-duration/quantity side placebo; not an endogenous independent-policy validation.
    rng = np.random.default_rng(7323420)
    codes = known.index.get_indexer(eligible.date)
    assert (codes >= 0).all()
    nulls = []
    gross = eligible.gross.to_numpy()
    costs = (eligible.commission+eligible.slippage).to_numpy()
    for run in range(1000):
        values = rng.choice([-1., 1.], len(eligible))*gross-costs
        grouped = np.bincount(codes, weights=values, minlength=len(known))
        nulls.append({'run': run, 'net': float(grouped.sum()),
                      'dollar_sharpe': float(grouped.mean()/grouped.std(ddof=1)*np.sqrt(252))})
    null = pd.DataFrame(nulls)
    null.to_csv(OUT/'fixed_duration_side_controls.csv', index=False)
    row = summaries[0]
    criteria = {'recent_net_positive': row['net'] > 0,
                'recent_extra_tick_stress_positive': row['stress_net'] > 0,
                'three_of_four_years_positive': sum(r['net'] > 0 for r in annual) >= 3,
                'daily_return_t_at_least_2': row['t_return'] >= 2,
                'at_least_300_trades': row['trades'] >= 300,
                'bootstrap_return_sharpe_p5_positive': intervals['daily_return']['metrics']['sharpe']['p5'] > 0}
    result = {'scope': 'UNCHANGED BASELINE HISTORICAL VALIDATION, NOT A CLEAN HOLDOUT',
        'recent_start': str(recent.date.iloc[0].date()), 'recent_end': str(recent.date.iloc[-1].date()),
        'initial_nav_2018': E.CAPITAL, 'recent_start_nav': float(recent.start_nav.iloc[0]),
        'summaries': summaries, 'yearly': annual, 'full_summaries': full_summary, 'full_yearly': full_annual,
        'bootstrap': intervals, 'criteria': criteria, 'descriptive_watch_pass': all(criteria.values()),
        'account_admitted': False, 'account_simulations_run': False,
        'unknown_recent_days': recent.loc[~recent.complete, ['date','net']].assign(
            date=lambda x:x.date.dt.strftime('%Y-%m-%d')).to_dict('records'),
        'unknown_recent_trades': int(recent_trades.unknown_path.sum()),
        'observed_recent_endpoint_net': float(recent_trades.net.sum()),
        'known_recent_net': row['net'], 'known_recent_days':len(known), 'recent_calendar_days':len(recent),
        'full_cap_flags':flags, 'recent_cap_flags':[f for f in flags if f['date'] >= '2023-01-01'],
        'side_control': {'samples':1000, 'conditional_fixed_duration_quantity':True,
            'net_pvalue':float((1+(null.net >= row['net']).sum())/1001),
            'sharpe_pvalue':float((1+(null.dollar_sharpe >= row['sharpe']).sum())/1001),
            'net_p5':float(null.net.quantile(.05)), 'net_p95':float(null.net.quantile(.95))},
        'selection_count_lower_bound':trials, 't_bar':E.t_threshold(trials),
        'manifest': {'preregistration_commit':'8c89fd79',
            'run_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
            'core_code_sha256':E.digest(Path(E.__file__)), 'runner_sha256':E.digest(Path(__file__)),
            'plan_sha256':E.digest(ROOT/'agents/codex/plans/delgado_es_baseline_20261108.md'),
            'design_prefix_hashes':prefix_hashes, 'prior_manifest':previous['manifest'],
            'bootstrap_seed':7323419,'side_control_seed':7323420,'block':20,'samples':1000}}
    (OUT/'summary.json').write_text(json.dumps(E.clean_json(result),indent=2,allow_nan=False)+'\n')
    print(json.dumps(E.clean_json({'recent':row, 'yearly':annual, 'criteria':criteria,
                                  'bootstrap_return_sharpe':intervals['daily_return']['metrics']['sharpe'],
                                  'unknown_recent_days':result['unknown_recent_days'],
                                  'recent_cap_flags':len(result['recent_cap_flags'])}),allow_nan=False))


if __name__ == '__main__':
    main()
