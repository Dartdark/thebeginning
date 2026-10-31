"""Saved-output comparisons and coverage audit; no new strategy returns."""
from pathlib import Path
import importlib
import json
import pickle
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'agents/codex/runtime/or_pullback_python'))
sys.path.insert(0, str(ROOT/'analysis'))
import numpy as np
import pandas as pd
import codex_or_pullback_plan as P
import codex_or_pullback_portfolio as A


def main():
    out = A.OUT
    references, comparisons = [], []
    import codex_ob_v2_accounts as acc
    for fee in (1.04, 1.24):
        frame = pd.read_csv(out/f'evaluation_starts_{fee:.2f}.csv', index_col=0, parse_dates=True)
        base = frame['BASE__outcome']
        valid = base.notna() & (frame.index.year >= 2018)
        references.append(dict(fee=fee, full_calendar_valid_starts=int(valid.sum()),
                                pass_rate=float((base[valid] == 'pass').mean()),
                                saved_reference=.498 if fee == 1.04 else None,
                                difference_from_saved=float((base[valid] == 'pass').mean()-.498) if fee == 1.04 else None))
        dates = frame.index
        eligible = set(pd.read_csv(out/'daily_joint_pnl.csv', index_col=0, parse_dates=True).index)
        complete = np.array([d in eligible for d in dates])
        ok21 = np.array([i+21 <= len(frame) and complete[i:i+21].all() for i in range(len(frame))])
        for column in frame.columns:
            name = column.removesuffix('__outcome')
            for ref in ('BASE', 'EMPTY_VB'):
                delta = (frame[column] == 'pass').to_numpy(int)-(frame[ref+'__outcome'] == 'pass').to_numpy(int)
                for cohort, mask in (('2018_plus', dates.year >= 2018),
                                      ('2018_22', (dates.year >= 2018) & (dates.year < 2023)),
                                      ('2023_plus', dates.year >= 2023)):
                    d = delta[ok21 & mask]
                    ci = acc.paired_ci(d, block=20)
                    comparisons.append(dict(fee=fee, config=name, reference=ref, cohort=cohort,
                                            paired_pass_difference=d.mean(), ci_lo=ci[0], ci_hi=ci[1],
                                            interval='95% circular20day bootstrap of paired chronological start outcomes'))
    A.dump(out/'evaluation_baseline_reference.json', references)
    pd.DataFrame(comparisons).to_csv(out/'evaluation_paired_differences.csv', index=False)
    manifest_path = out/'reproduction.json'
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    manifest['scripts'] = {p.name:A.sha(p) for p in (ROOT/'analysis').glob('codex_or_pullback*.py')}
    manifest['market_cache_hashes'] = {name:A.sha(ROOT/'scratch_data'/name) for name in
            ('g24.pkl', 'ge.pkl', 'cl.pkl', 'lab.pkl', 's_rank_gap2.pkl', 'single_print_sessions.pkl')}
    manifest['coverage_supplement'] = 'complete-session daily diagnostics, full-calendar baseline audit, paired evaluation intervals'
    A.dump(manifest_path, manifest)
    print(json.dumps(references), flush=True)


def refresh_overlap():
    out = A.OUT
    with P.pinned_imports(P.DEFAULT_RUNTIME, ROOT/'scratch_data'):
        with (ROOT/'agents/codex/runtime/or_pullback_current_lab.pkl').open('rb') as f:
            lab = pickle.load(f)
        ledgers = {m:pd.read_csv(out/'replay'/f'{m}_trades.csv', parse_dates=['date'])
                   for m in ('reported_rule', 'literal_mc_delay')}
        audit = pd.read_csv(out/'replay/reported_rule_audit.csv', parse_dates=['date'])
        dates = set(audit.loc[audit.status == 'eligible', 'date'])
        eligible = np.array([pd.Timestamp(d) in dates for d in lab.g.ts[lab.tr]])
        for mode, trades in ledgers.items():
            w, r = A.candidate_paths(lab.g, trades)
            lab.C[mode] = r[lab.tr, -1]
        A.overlap(lab, ledgers, eligible=eligible)


if __name__ == '__main__':
    refresh_overlap()
    main()
