"""Reproduce the preregistered ORPullback joint-account comparison (1ad4306).

Run with the existing numpy/pandas interpreter. Optional task-local scientific
dependencies are discovered below; no cache or package installation is performed.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import pickle
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'agents/codex/runtime/or_pullback_python'))
sys.path.insert(0, str(ROOT / 'analysis'))
import numpy as np
import pandas as pd
import codex_or_pullback_plan as P

OUT = ROOT / 'analysis/outputs/codex_or_pullback_portfolio'
PREREG = '1ad4306'


def dump(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, default=str, allow_nan=True) + '\n', encoding='utf-8')


def sha(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def candidate_paths(g, t, fee=1.04):
    """Per-MNQ adverse/realized paths, correctly excluding pre-entry OHLC.

    Entry slip and RT fee are present from the close entry. Exit slip appears
    at exit. A filled stop caps the adverse path at its executable gap/stop
    price; open exits do not include later minute extremes. Target intrabar
    marks retain the reference bench's conservative within-minute ambiguity.
    """
    w = np.zeros(g.o.shape)
    r = np.zeros_like(w)
    for x in t.itertuples():
        d, e, z = int(x.day), int(x.entry_j), int(x.exit_j)
        if e >= z:
            raise ValueError('Close entry must precede exit')
        entry_cost = fee + .25 * 2
        net = (x.exit-x.entry)*x.side*2 - entry_cost - (.5 if x.kind != 1 else 0)
        w[d, e] -= entry_cost
        adverse = g.l[d, e+1:z+1] if x.side > 0 else g.h[d, e+1:z+1]
        v = (adverse-x.entry)*x.side*2-entry_cost
        if not np.isfinite(v).all():
            raise ValueError('Missing held minute OHLC')
        if x.kind == 0 or x.exit_phase == 'open':
            v[-1] = net
        else:
            v[-1] = min(v[-1], net)
        w[d, e+1:z+1] += v
        w[d, z+1:] += net
        r[d, z:] += net
    return w, r


def path_fixture():
    from types import SimpleNamespace
    g = SimpleNamespace(o=np.full((1, 12), 100.), l=np.full((1, 12), 99.),
                        h=np.full((1, 12), 101.))
    g.l[0, 2] = 1.  # Extreme before the close entry cannot become held risk.
    t = pd.DataFrame([dict(day=0, entry_j=2, exit_j=5, side=1, entry=100.,
                           exit=50., kind=0, exit_phase='intrabar')])
    w, r = candidate_paths(g, t)
    assert w[0, 2] == -1.54 and w[0, 3] == -3.54
    np.testing.assert_allclose(w[0, 5:], -102.04)
    assert not r[0, :5].any()
    np.testing.assert_allclose(r[0, 5:], -102.04)
    return dict(entry_ohlc_excluded=True, stop_cap_and_fee_timing=True)


def allocations(base):
    empty = {k: v for k, v in base.items() if k not in ('VB_N', 'VB_F')}
    plans = dict(BASE=base, EMPTY_VB=empty)
    for mode in ('reported_rule', 'literal_mc_delay'):
        plans[f'{mode}__ADD_1'] = {**base, mode: 1}
        plans[f'{mode}__ADD_2'] = {**base, mode: 2}
        plans[f'{mode}__REPLACE_VB_2'] = {**empty, mode: 2}
    return plans


def paired_summary(results, acc, fee, cohort):
    rows, diffs = [], []
    for name, (a, b) in results.items():
        rows.append(dict(fee=fee, cohort=cohort, config=name,
                         year1=a[:, 0].mean(), year1_p5=np.percentile(a[:, 0], 5),
                         year1_p95=np.percentile(a[:, 0], 95), year2=b[:, 0].mean(),
                         year2_p5=np.percentile(b[:, 0], 5), year2_p95=np.percentile(b[:, 0], 95),
                         blown=b[:, 3].mean(), all6=(b[:, 1] == 6).mean(),
                         days6=np.median(np.where(b[:, 1] == 6, b[:, 2], np.inf))))
        for ref in ('BASE', 'EMPTY_VB'):
            aa, bb = results[ref]
            for metric, delta in (('year1', a[:, 0]-aa[:, 0]),
                                  ('year2', b[:, 0]-bb[:, 0]),
                                  ('blown', b[:, 3]-bb[:, 3])):
                ci = acc.paired_ci(delta)
                diffs.append(dict(fee=fee, cohort=cohort, config=name, reference=ref,
                                  metric=metric, delta=delta.mean(), lo=ci[0], hi=ci[1]))
    return rows, diffs


def run_funded(lab, fb, fs, fee, eligible):
    import codex_ob_v2_accounts as acc
    acc.F = fs
    plans = allocations(P.CURRENT_PLAN)
    dates = pd.DatetimeIndex(lab.g.ts[lab.tr])
    histories = {}
    for cohort, start in (('2018_plus', '2018-01-01'), ('2023_plus', '2023-01-01')):
        boot = fb.Boot(lab, start=start)
        # An unknown candidate return is not a zero return. Restrict all plans
        # to the same complete candidate sessions; record the calendar change.
        boot.days = boot.days[eligible[boot.days]]
        histories[cohort] = np.concatenate([boot._histories(250, 500, 20, s) for s in (1, 2, 3, 4)])
        np.save(OUT / f'funded_histories_{cohort}.npy', histories[cohort])
    rows, diffs, checks, resources = [], [], [], []
    all_results = {}
    for name, plan in plans.items():
        start = time.monotonic()
        keys = sorted(plan)
        w = np.stack([lab.W[k] for k in keys])
        c = np.stack([lab.C[k] for k in keys])
        names, sizes = lab._base({k: plan[k] for k in keys})
        assert names == keys
        if not np.isfinite(w).all() or not np.isfinite(c).all():
            raise ValueError('Nonfinite account path')
        table = acc.make_table(w, c, sizes)
        fixed = histories['2018_plus'][[0, 1, 17, 333, 999]]
        checks.extend(acc.parity_check(w, c, table, fixed, f'{fee}/{name}'))
        for cohort, hist in histories.items():
            all_results.setdefault(cohort, {})[name] = (acc.run_table(table, hist, 250),
                                                        acc.run_table(table, hist, 500))
        resources.append(dict(config=name, fee=fee, seconds=time.monotonic()-start,
                              max_quantity_states=int(table['counts'].max())))
        print(f'funded fee={fee} {name} done {resources[-1]["seconds"]:.1f}s', flush=True)
        del w, c, table
    for cohort, results in all_results.items():
        a, b = paired_summary(results, acc, fee, cohort)
        rows += a
        diffs += b
        np.savez_compressed(OUT / f'funded_results_{fee:.2f}_{cohort}.npz',
                            **{f'{k}__{h}': results[k][i] for k in results for i, h in enumerate((250, 500))})
    dump(OUT / f'funded_parity_{fee:.2f}.json', checks)
    dump(OUT / f'funded_resources_{fee:.2f}.json', resources)
    return rows, diffs


def baseline_reference(lab, fb, fs):
    """Run reference before the common complete-session restriction."""
    import codex_ob_v2_accounts as acc
    acc.F = fs
    keys = sorted(P.CURRENT_PLAN)
    w = np.stack([lab.W[k] for k in keys])
    c = np.stack([lab.C[k] for k in keys])
    _, b = lab._base({k: P.CURRENT_PLAN[k] for k in keys})
    table = acc.make_table(w, c, b)
    boot = fb.Boot(lab)
    hist = np.concatenate([boot._histories(250, 500, 20, s) for s in (1, 2, 3, 4)])
    parity = acc.parity_check(w, c, table, hist[[0, 1, 17, 333, 999]], 'reference_full_calendar')
    a, z = acc.run_table(table, hist, 250), acc.run_table(table, hist, 500)
    expected = dict(year1=9180, year2=11982, blown=.076, all6=.908, days6=263)
    actual = dict(year1=a[:, 0].mean(), year2=z[:, 0].mean(), blown=z[:, 3].mean(),
                  all6=(z[:, 1] == 6).mean(), days6=np.median(np.where(z[:, 1] == 6, z[:, 2], np.inf)))
    dump(OUT / 'baseline_reference.json', dict(saved_reference=expected, actual=actual,
          delta={k: actual[k]-expected[k] for k in expected}, exact_simulator_parity=parity))
    print('baseline_reference ' + json.dumps(actual), flush=True)


def evaluation(g, portfolio, fl, fee, ledgers, eligible_dates):
    import combine_levers_test as cl
    import build_lab
    import bridge_monday_confirm
    from grid24 import jof
    portfolio.COST = fee*10
    tr = g.trading
    dates = pd.DatetimeIndex(g.ts[tr])
    atr = g.daily_atr(15)[tr]
    risk = lambda dollars, a: np.floor(dollars / (np.nan_to_num(a*atr, nan=1e12)*2))[:, None]
    ts = dict(VB=fl.with_slippage(portfolio.load_mc(g, build_lab.REPORTS['VB'][0])),
              ONB30=fl.with_slippage(portfolio.load_mc(g, cl.ONB30)),
              MON_BR=bridge_monday_confirm.load_bridge_mc(g),
              EOS=fl.with_slippage(portfolio.load_mc(g, build_lab.REPORTS['EOS'][0])))
    pp = {k: tuple(x[tr]/10 for x in portfolio.paths(g, t)) for k, t in ts.items()}
    q = dict(VB=8., ONB30=risk(1100, .25), MON_BR=2., EOS=risk(500, build_lab.REPORTS['EOS'][1]))
    base_w = sum(pp[k][0]*q[k] for k in q)
    base_r = sum(pp[k][1]*q[k] for k in q)
    empty_w, empty_r = base_w-pp['VB'][0]*8, base_r-pp['VB'][1]*8
    plans = dict(BASE=(base_w, base_r), EMPTY_VB=(empty_w, empty_r))
    for mode, t in ledgers.items():
        w, r = candidate_paths(g, t, fee)
        for n in (1, 2):
            plans[f'{mode}__ADD_{n}'] = (base_w+w[tr]*n, base_r+r[tr]*n)
        plans[f'{mode}__REPLACE_VB_2'] = (empty_w+w[tr]*2, empty_r+r[tr]*2)
    rows, raw = [], {}
    one = lambda p, c, n: 1.
    # Retain real calendar and trade-day horizon. Omit starts whose 21-day
    # evaluation includes unknown candidate sessions, rather than compress time.
    complete = np.array([d in eligible_dates for d in dates])
    starts_ok = np.array([complete[i:i+cl.MAXD].all() and i+cl.MAXD <= len(tr)
                          for i in range(len(tr))])
    for name, (w, r) in plans.items():
        results = [cl.challenge(w, r, np.arange(s, min(s+cl.MAXD, len(tr))), one)
                   for s in range(len(tr))]
        outcome = np.array([x[0] if x else '' for x in results])
        days = np.array([x[1] if x else 0 for x in results])
        raw[name] = (outcome, days)
        for cohort, mask in (('2018_plus', dates.year >= 2018),
                              ('2018_22', (dates.year >= 2018) & (dates.year < 2023)),
                              ('2023_plus', dates.year >= 2023)):
            ok = starts_ok & mask
            rows.append(dict(fee=fee, cohort=cohort, config=name, starts=int(ok.sum()),
                              passed=(outcome[ok] == 'pass').mean(), failed=(outcome[ok] == 'fail').mean(),
                              timed_out=(outcome[ok] == 'time').mean(),
                              median_pass_days=np.median(days[ok & (outcome == 'pass')]),
                              change_vs_base=(outcome[ok] != raw['BASE'][0][ok]).mean()))
        print(f'evaluation fee={fee} {name} done', flush=True)
    pd.DataFrame({f'{k}__outcome': v[0] for k, v in raw.items()}, index=dates).to_csv(OUT/f'evaluation_starts_{fee:.2f}.csv')
    return rows


def overlap(lab, ledgers, fee=1.04, eligible=None):
    keys = list(P.CURRENT_PLAN)
    names, b = lab._base(P.CURRENT_PLAN)
    # Descriptive full-size integer exposures; funded quantities also depend on
    # cushion during actual simulations above, so this is not an account result.
    q = np.floor(b+1e-9)
    daily = sum(lab.C[k]*q[i] for i, k in enumerate(names))
    df = pd.DataFrame({k: lab.C[k] for k in keys}, index=pd.DatetimeIndex(lab.g.ts[lab.tr]))
    df['PLAN_FULL_SIZE'] = daily
    if eligible is None:
        eligible = np.ones(lab.D, dtype=bool)
    records = []
    for mode, t in ledgers.items():
        df[mode] = lab.C[mode]
        loss = (daily < 0) & eligible
        cc = lab.C[mode]
        records.append(dict(mode=mode, plan_loss_days=int(loss.sum()),
                            candidate_net_on_plan_loss_days=cc[loss].sum(),
                            candidate_avg_on_plan_loss_days=cc[loss].mean(),
                            joint_loss_days=int((loss & (cc < 0)).sum()),
                            correlation_with_plan=float(np.corrcoef(daily[eligible], cc[eligible])[0, 1])))
    df.loc[eligible].to_csv(OUT/'daily_joint_pnl.csv')
    df.loc[eligible].corr().to_csv(OUT/'daily_correlations.csv')
    dump(OUT/'overlap_summary.json', records)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--scratch', default='scratch_data')
    ap.add_argument('--baseline-cache', default='agents/codex/runtime/or_pullback_current_lab.pkl')
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    started = time.monotonic()
    P.prepare_sources()
    with P.pinned_imports(P.DEFAULT_RUNTIME, Path(args.scratch).resolve()):
        fs = importlib.import_module('funded_sim')
        fb = importlib.import_module('funded_bootstrap')
        fl = importlib.import_module('funded_lab')
        portfolio = importlib.import_module('portfolio')
        import codex_or_pullback_replay as replay
        cache = Path(args.baseline_cache)
        if not cache.is_file():
            raise FileNotFoundError('Build and reconcile the frozen baseline with codex_or_pullback_plan first')
        with cache.open('rb') as f:
            lab = pickle.load(f)
        ledgers, audits = {}, {}
        for mode in replay.TIMING_MODES:
            t = pd.read_csv(OUT/'replay'/f'{mode}_trades.csv', parse_dates=['date'])
            audit = pd.read_csv(OUT/'replay'/f'{mode}_audit.csv', parse_dates=['date'])
            ledgers[mode], audits[mode] = t, audit
        eligible_dates = set(audits['reported_rule'].loc[audits['reported_rule'].status == 'eligible', 'date'])
        eligible = np.array([pd.Timestamp(d) in eligible_dates for d in lab.g.ts[lab.tr]])
        dump(OUT/'account_calendar.json', dict(eligible=int(eligible.sum()), total=lab.D,
                excluded_dates=[str(pd.Timestamp(d).date()) for d in lab.g.ts[lab.tr][~eligible]],
                funded_policy='same complete sessions for all configurations',
                evaluation_policy='same real 21-day windows, exclude any window with unknown candidate sessions'))
        dump(OUT/'path_fixture.json', path_fixture())
        baseline_reference(lab, fb, fs)
        fr, fd, er = [], [], []
        for fee in (1.04, 1.24):
            if fee > 1.04:
                lab.real_fees(.20, list(P.CURRENT_PLAN))
            for mode, t in ledgers.items():
                w, r = candidate_paths(lab.g, t, fee)
                lab.W[mode], lab.C[mode] = w[lab.tr], r[lab.tr, -1]
            if fee == 1.04:
                overlap(lab, ledgers, eligible=eligible)
            a, b = run_funded(lab, fb, fs, fee, eligible)
            fr += a
            fd += b
            pd.DataFrame(fr).to_csv(OUT/'funded_summary.csv', index=False)
            pd.DataFrame(fd).to_csv(OUT/'funded_paired_differences.csv', index=False)
            er += evaluation(lab.g, portfolio, fl, fee, ledgers, eligible_dates)
            pd.DataFrame(er).to_csv(OUT/'evaluation_summary.csv', index=False)
        dump(OUT/'reproduction.json', dict(preregistration_commit=PREREG, current_plan_ref=P.PINNED_REF,
              strategy_variants=2, fee_regimes=2, allocations_per_fee=8, funded_cohorts=2,
              paired_histories=1000, block_length=20, seeds=[1, 2, 3, 4], seconds=time.monotonic()-started,
              inputs={str(p):sha(p) for p in [ROOT/'agents/codex/inputs/or_pullback/source.txt',
                      ROOT/'agents/codex/inputs/or_pullback/report.pdf', cache]},
              scripts={p.name:sha(p) for p in (ROOT/'analysis').glob('codex_or_pullback*.py')}))


if __name__ == '__main__':
    main()
