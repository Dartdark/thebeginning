"""Paper arithmetic and static-source audit only: no market returns or portfolio fit."""
from pathlib import Path
import ast
import hashlib
import json
import math

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'agents/codex/inputs/hidden_sharpe_7679420_20261107'


def main():
    claims = json.loads((BASE / 'source_claims.json').read_text())
    receipt = json.loads((BASE / 'access.json').read_text())
    assert hashlib.sha256((BASE / 'source.pdf').read_bytes()).hexdigest() == receipt['upload']['sha256']
    for item in receipt['author_code_files']:
        path = BASE / 'author_reference' / item['path']
        assert hashlib.sha256(path.read_bytes()).hexdigest() == item['sha256'], item['path']

    # Population identity in Proposition1/Corollary3: a fixed algebra fixture, not a simulated market.
    eigenvalues = [0.25, 1.0, 4.0]
    projected_means = [0.01, 0.02, 0.03]
    effective_z = 0.5
    oracle_squared = sum(m*m/v for m, v in zip(projected_means, eigenvalues))
    terms = [sum(effective_z**j * m*m / (v+effective_z)**(j+1)
                 for m, v in zip(projected_means, eigenvalues)) for j in range(100)]
    lower = terms[0] + terms[1] / (1-terms[1]/terms[0])
    assert math.isclose(sum(terms), oracle_squared, rel_tol=1e-12)
    assert sum(terms[:2]) <= lower <= oracle_squared

    # Check AppendixJ.1 andK.1/L.2 J=1 gradient, without claiming validation of their CLT.
    b0, b1 = terms[:2]
    h = lambda x, y: x + x*y/(x-y)
    eps = 1e-9
    numerical = [(h(b0+eps,b1)-h(b0-eps,b1))/(2*eps),
                 (h(b0,b1+eps)-h(b0,b1-eps))/(2*eps)]
    analytic = [1-b1*b1/(b0-b1)**2, b0*b0/(b0-b1)**2]
    assert all(math.isclose(a,b,rel_tol=1e-7) for a,b in zip(analytic,numerical))

    factor = claims['ridge_squared_sharpe_shortfall_factor']
    ridge_ceiling = {key: value/math.sqrt(factor) for key,value in
                     claims['prose_headline_annualized_sharpe'].items()}
    assert round(ridge_ceiling['all_stocks'],1)==5.5
    assert round(ridge_ceiling['ex_micro'],1)==3.7

    # Static source inspection. Parse text only: never import/execute downloaded author code.
    bounds = (BASE / 'author_reference/src/RMT/rmt/grs_bounds_mixin.py').read_text()
    tree = ast.parse(bounds)
    annualized_methods = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name in {'get_all_lbs','get_all_ubs'}:
            assert any(isinstance(n,ast.Return) and isinstance(n.value,ast.BinOp)
                       and isinstance(n.value.op,ast.Mult)
                       and isinstance(n.value.left,ast.Name) and n.value.left.id=='annualizer'
                       and isinstance(n.value.right,ast.Name) and n.value.right.id=='df'
                       for n in ast.walk(node))
            annualized_methods.append(node.name)
    assert len(annualized_methods)==2
    assert "use_a_corner = (~np.isfinite(ub_a_min) | (ub_a_min < lb)).any()" in bounds
    assert "df[f'multi_ub_diagcorr_pt'] = float(lb)" in bounds

    figure = claims['figure4_all_duration_hedged']
    prose = claims['section53_prose_bond_comparison']
    assert figure['equities_point'] != prose['equities_point']
    assert figure['equities_bonds_point'] != prose['equities_bonds_point']
    result = dict(
        status='PASS', scope='Arithmetic/hash/static-source checks only; no theorem, empirical or economic verification',
        market_returns_computed=False, author_package_executed=False,
        economic_definitions=0,
        population_algebra_fixture=dict(eigenvalues=eigenvalues,projected_means=projected_means,effective_z=effective_z,
                                       oracle_squared_sharpe=oracle_squared,geometric_lower_bound=lower,
                                       infinite_series_100_terms=sum(terms),gradient_analytic=analytic,gradient_finite_difference=numerical),
        source_arithmetic=dict(ridge_squared_shortfall_factor=factor,ridge_sharpe_fraction=1/math.sqrt(factor),
                               approximate_annualized_ridge_ceilings=ridge_ceiling),
        static_code_observations=dict(whole_dataframe_annualization_methods=sorted(annualized_methods),
                                      corner_point_equals_lower_bound=True,empirical_replication=False),
        source_discrepancies=dict(bond_text=prose,bond_figure=figure,reconciled=False),
        qualification='No stock/bond/futures returns were loaded or fitted. Fixture numbers are algebra checks, not strategy performance.')
    print(json.dumps(result,indent=2))


if __name__ == '__main__':
    main()
