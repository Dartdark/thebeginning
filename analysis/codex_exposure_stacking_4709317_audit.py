"""Source-code and constructed mathematical checks; no strategy returns.
Run from repository root: python analysis/codex_exposure_stacking_4709317_audit.py
"""
from pathlib import Path
import hashlib
import json
import numpy as np

ROOT = Path('agents/codex/inputs/exposure_stacking_4709317')
OUT = Path('analysis/outputs/codex_exposure_stacking_4709317')


def objective(M, w, folds, normalize=False):
    errors, budgets = [], []
    for k in folds:
        keep = np.ones(len(M), bool)
        keep[k] = False
        pred = M[keep].T @ w[keep]
        if normalize:
            pred = pred / w[keep].sum()
        errors.append(float(np.mean(np.sum((M[k] - pred)**2, axis=1))))
        budgets.append(float(pred.sum()))
    return float(np.mean(errors)), budgets


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    notebook = json.loads((ROOT / 'author_notebook.ipynb').read_text())
    code = '\n\n'.join(''.join(c.get('source', [])) for c in notebook['cells'] if c['cell_type'] == 'code')
    helper = code[code.index('def exposure_stacking('):code.index('num_samples = B', code.index('def exposure_stacking('))]
    (OUT / 'inspected_author_helper.txt').write_text('# Source: Fortitudo Technologies replication notebook, Copyright 2021-2026; GPLv3-or-later.\n# Original license notice retained in agents/codex/inputs/exposure_stacking_4709317/author_notebook.ipynb.\n' + helper)
    assert 'M_l[K_l, :] = 0' in helper
    assert 'A = matrix(np.ones((1, num_samples)))' in helper
    assert "re_rar = re_rr[1, :] / re_rr[0, :]" in code
    assert 'risk_return[0, b] = pf @ cov_run @ pf' in code

    M = np.tile([0.6, 0.4], (4, 1))
    w = np.ones(4) / 4
    folds = [np.array([0, 1]), np.array([2, 3])]
    err, budgets = objective(M, w, folds)
    norm_err, norm_budgets = objective(M, w, folds, normalize=True)
    np.testing.assert_allclose(err, 0.13)
    np.testing.assert_allclose(norm_err, 0)
    Q = np.array([[1., 0.], [1., 0.], [0., 1.], [0., 1.]])
    alt = np.array([0.5, 0, 0.5, 0])
    np.testing.assert_allclose(Q.T @ w, Q.T @ alt)
    naive = lambda v: float(np.mean(np.sum((Q - Q.T @ v)**2, axis=1)))
    np.testing.assert_allclose(naive(w), naive(alt))
    result = {
        'evidence_kind': 'source notebook inspection and constructed algebra checks, not historical/model-case-study replication',
        'return_trials': 0,
        'identical_fully_invested_portfolios': {
            'base_exposure': [0.6, 0.4], 'global_weights': w.tolist(),
            'published_fold_prediction_budgets': budgets,
            'published_mean_squared_exposure_error': err,
            'fold_renormalized_prediction_budgets': norm_budgets,
            'fold_renormalized_mean_squared_error': norm_err,
            'final_full_weight_portfolio_budget': float((M.T @ w).sum()),
            'qualification': 'Renormalization is an illustrative different objective, not a source correction or proposed replacement. Positive loss is built into the published masked objective; it does not alone disprove utility.'},
        'naive_objective_nonunique_weights': {
            'uniform_weights': w.tolist(), 'alternative_weights': alt.tolist(),
            'same_exposure': (Q.T @ w).tolist(), 'same_objective': naive(w)},
        'notebook_risk_adjusted_statistic': 'expected return / variance, not expected return / standard deviation',
        'scale_illustration': [
            {'exposure_scale': c, 'mean': .1*c, 'variance': .04*c*c,
             'mean_over_variance': (.1*c)/(.04*c*c), 'zero_rate_mean_over_sd': (.1*c)/np.sqrt(.04*c*c)}
            for c in [1., .5]],
        'limitations': 'No historical weights, native integer quantities, turnover, fees, margin, chronology or Apex account contribution evaluated. No claim that actual author portfolios differ only by leverage.'
    }
    (OUT / 'checks.json').write_text(json.dumps(result, indent=2) + '\n')
    manifest = {
        'title': 'Portfolio Optimization and Parameter Uncertainty',
        'authors': ['Laura Kristensen', 'Anton Vorobets'], 'ssrn': '4709317',
        'version_date': '2026-02-04', 'first_version': '2024-01-30',
        'notebook_url': 'https://raw.githubusercontent.com/fortitudo-tech/fortitudo.tech/main/examples/9_PortfolioOpt_ParamUncertainty.ipynb',
        'notebook_retrieved': '2026-11-08',
        'notebook_scope': 'Downloaded mutable main; pinned by content hash. Legacy helper warns to prefer ft.exposure_stacking. Current library implementation not inspected.',
        'files': {p.name: {'sha256': hashlib.sha256(p.read_bytes()).hexdigest(), 'bytes': p.stat().st_size}
                  for p in [ROOT/'source.pdf', ROOT/'author_notebook.ipynb']},
        'review_scope': '15-page source, published notebook, deterministic synthetic mechanics only',
        'notebook_license': 'GPLv3-or-later notice retained in notebook; original notebook unmodified'
    }
    (ROOT / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
