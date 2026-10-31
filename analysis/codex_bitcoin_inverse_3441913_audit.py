"""No-return source arithmetic / input-identity audit for SSRN3441913.

Does not use historical prices to calculate returns or backtest a candidate.
"""
import csv
import hashlib
import json
from pathlib import Path
import subprocess

import numpy as np

ROOT = Path('agents/codex/inputs/ssrn3441913')
OUT = Path('analysis/outputs/codex_bitcoin_inverse_3441913_audit')


def constants(rho=.59):
    mu = np.array([.4085, .6002 - .47 ** 2])
    nu1, nu2, nu3 = .5994 ** 2, .47 ** 2, rho * .5994 * .47
    covariance = np.array([[nu1, nu3], [nu3, nu2]])
    determinant = np.linalg.det(covariance)
    if determinant <= 1e-14:
        raise ValueError('Source requires nonsingular covariance')
    c = np.linalg.solve(covariance, mu)
    closed = np.array([(.4085 * nu2 - .6002 * nu3 + nu2 * nu3) / determinant,
                       (.6002 * nu1 - .4085 * nu3 - nu1 * nu2) / determinant])
    assert np.allclose(c, closed)
    assert np.allclose(covariance @ c, mu)
    # Printed B.2 uses +nu1*nu2 in its numerator, contradicting C2 in (4.3).
    b2_c2 = (.6002 * nu1 - .4085 * nu3 + nu1 * nu2) / determinant
    return dict(rho=rho, C1=float(c[0]), C2=float(c[1]), determinant=float(determinant),
                condition_number=float(np.linalg.cond(covariance)),
                printed_B2_implied_C2=float(b2_c2),
                B2_minus_theorem_C2=float(b2_c2 - c[1]))


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    primary = constants()
    # Source's one-contract example: BTC P&L first, then conversion into USD.
    btc_pnl = 1 / 100 - 1 / 200
    usd_pnl = btc_pnl * 205
    assert np.isclose(btc_pnl, .005) and np.isclose(usd_pnl, 1.025)
    assert np.isclose((1 / 200 - 1 / 100) * 205, -usd_pnl)
    assert 1 / 100 - 1 / 100 == 0
    try:
        constants(1.)
    except ValueError:
        pass
    else:
        raise AssertionError('Singular covariance must not produce a position')
    schemas = {}
    for name in ['data/BTC_1min_2019.csv', 'data/BTCUSD_spot_1min_2019.csv']:
        with Path(name).open() as handle:
            schemas[name] = next(csv.reader(handle))
    result = dict(
        source_title='Optimal Bitcoin Trading with Inverse Futures', source_version='August 23, 2019',
        source_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip(),
        file_sha256={str(p): hashlib.sha256(p.read_bytes()).hexdigest()
                     for p in sorted(ROOT.iterdir()) if p.is_file()},
        script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        primary_calibration=primary,
        # Conditional source-formula diagnostics only; never fitted to performance.
        correlation_diagnostics=[constants(rho) for rho in [.59, .9, .99, .9962]],
        power_weights_at_Z1=[dict(alpha=alpha, spot_weight=primary['C1'] / (1-alpha),
                                 futures_face_value_to_wealth=primary['C2'] / (1-alpha))
                                for alpha in [-2., -.5, .1]],
        source_table2_claims=[dict(utility='exponential', risk_parameter=g, sharpe=s, sortino=t)
                              for g,s,t in [(.5,5.07,2.28),(1.,4.96,2.09),(1.5,4.86,1.99)]] +
                             [dict(utility='power',risk_parameter=a,sharpe=s,sortino=t)
                              for a,s,t in [(-2.,4.86,1.87),(-.5,4.91,1.89),(.1,4.93,1.90)]] +
                             [dict(utility='all_in_spot',sharpe=4.40,sortino=1.59)],
        inverse_payoff_example=dict(contract_face_usd=1, entry=100, exit=200, conversion_spot=205,
                                    pnl_btc=btc_pnl, pnl_usd=usd_pnl),
        inspected_owned_schemas=schemas,
        acquisition_receipt=json.loads((ROOT/'acquisition_receipts.json').read_text()),
        assertions='PASS: matrix/closed formula agreement, residual, payoff signs/units, singular guard',
        return_trials=0, empirical_replication=False,
        decision='NEEDS MATCHING DATA AND SPECIFICATION; accounting reference retained')
    (OUT/'audit.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ['file_sha256','source_table2_claims','acquisition_receipt']},indent=2))


if __name__ == '__main__':
    main()
