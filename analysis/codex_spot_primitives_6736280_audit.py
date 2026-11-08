"""Source identities and finite illustrative checks; zero market-return trials.

Constructed probability/cashflow examples test logical implications, not the
profitability of momentum, reversion, carry, market making or arbitrage.
"""
from itertools import product
from pathlib import Path
import hashlib
import json
import math
import subprocess

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'agents/codex/inputs/spot_primitives_6736280'
OUT = ROOT / 'analysis/outputs/codex_spot_primitives_6736280'


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    text = (SOURCE / 'source.txt').read_text()
    pdfinfo = subprocess.check_output(['pdfinfo', str(SOURCE / 'source.pdf')], text=True)
    assert 'Pages:           18' in pdfinfo
    assert 'It does\nnot propose new empirical evidence' in text
    for phrase in ['3.6 A Qualification: Yield-Bearing Assets', '6. Regime Dependence',
                   '5.3 Arbitrage as Spatial Mean Reversion', '5.4 Pairs Trading as Relative Mean Reversion']:
        assert phrase in text

    checks = []
    def check(label, ok):
        assert ok, label
        checks.append(label)

    # Exact stationary positive-price two-state Markov chain: P=100+X,
    # X in {-1,+1}; probability .9 of staying, .1 of switching each step.
    # Enumerate the stationary law of three consecutive levels, no simulation.
    paths = []
    for a, b, c in product([-1., 1.], repeat=3):
        w = .5 * (.9 if a == b else .1) * (.9 if b == c else .1)
        paths.append((a, b, c, w))
    moment = lambda f: sum(w * f(a, b, c) for a, b, c, w in paths)
    level_cov = moment(lambda a, b, c: a * b)
    change_var = moment(lambda a, b, c: (b - a) ** 2)
    change_cov = moment(lambda a, b, c: (b - a) * (c - b))
    change_corr = change_cov / change_var
    conditional_next_high = 100 + .9 - .1
    check('stationary finite probability law sums to one', math.isclose(moment(lambda a, b, c: 1), 1))
    check('stationary level mean and variance', math.isclose(moment(lambda a, b, c: b), 0, abs_tol=1e-12) and math.isclose(moment(lambda a, b, c: b*b), 1))
    check('positive level autocorrelation with conditional reversion', math.isclose(level_cov, .8) and conditional_next_high < 101)
    check('level and arithmetic-change correlations differ', math.isclose(change_corr, -.1))

    # A price at a fixed historical reference can have a positive expected
    # return, e.g. a priced risk premium. This example posits that distribution;
    # it does not identify it in actual efficient markets or supply a signal.
    reference = entry = 100.
    expected_next = .55 * 101 + .45 * 99
    expected_net = expected_next - entry - .02
    check('fixed-reference middle does not imply zero expected price change', entry == reference and math.isclose(expected_next - entry, .1))
    check('illustrative positive risk-premium expectation after assumed costs', math.isclose(expected_net, .08))

    # Hypothetical simultaneous firm executable quotes, identical fungible
    # units, with both legs locked and settlement/delivery assured by assumption.
    # Actual venues add legging, financing, delivery and counterparty constraints.
    locked_net = 101 - 99 - .2
    check('locked two-venue cash spread needs no later price convergence', math.isclose(locked_net, 1.8))
    flat_price_income = 100 - 100 + 5
    check('total-return income at unchanged price', flat_price_income == 5)

    # Log prices L1=W and L2=W+.01V, independent unit-variance random-walk
    # increments. Return correlation ~1, while spread variance grows with time.
    rho = 1 / math.sqrt(1 + .01**2)
    var100, var1000 = .01**2 * 100, .01**2 * 1000
    check('nearly perfect return correlation can coexist with nonstationary spread', rho > .9999 and var1000 > var100)
    check('growing expected fundamentals do not mechanically force a price gain', 12/10-1 > 0 and 100/100-1 == 0)

    audit = dict(
        kind='Source inspection and constructed mathematical/cashflow checks, not historical or empirical alpha evidence',
        return_trials=0, checks_passed=len(checks), checks=checks,
        source_claims=dict(new_empirical_evidence=False, standalone_backtest=False,
                           claimed_exhaustive_primitives=['mean reversion', 'momentum'],
                           author_acknowledges_yield=True, ex_ante_regime_algorithm=False),
        examples=dict(
            stationary_two_state=dict(prices=[99,101], stay_probability=.9, level_lag1_correlation=level_cov,
                                      arithmetic_change_lag1_correlation=change_corr,
                                      expected_next_price_given101=conditional_next_high,
                                      scope='Distinguish levels, changes and horizons; no claim that every reversion strategy has this law'),
            fixed_reference=dict(entry=entry, reference=reference, up_probability=.55,
                                 possible_next_prices=[99,101], expected_price_gain=expected_next-entry,
                                 assumed_total_cost=.02, expected_net=expected_net,
                                 scope='Assumed one-period priced-risk distribution; not a discovered trading edge'),
            simultaneous_arbitrage=dict(buy_ask=99, sell_bid=101, assumed_total_cost=.2, locked_net=locked_net,
                                       scope='Outside narrow single-venue scope, but corrects the paper\'s own multi-venue extension; simultaneous execution/settlement assumed'),
            income=dict(entry=100, exit=100, cash_income=5, total_gain=flat_price_income,
                        scope='Source already acknowledges income in section3.6; it excludes/relabels it rather than proving it absent'),
            correlated_log_random_walks=dict(return_correlation=rho, spread_variance_at100=var100,
                                            spread_variance_at1000=var1000,
                                            scope='Correlation alone does not establish cointegration or profitable convergence'),
            expected_growth=dict(earnings_before=10, earnings_after=12, price_before=100, price_after=100,
                                 scope='Hypothetical already-anticipated growth; not a valuation model or company observation')),
        source_pdf_sha256=sha(SOURCE/'source.pdf'), code_sha256=sha(__file__),
        decision='DO NOT TEST: no new complete rule, causal regime classifier or CME evidence; taxonomy is not an alpha hypothesis')
    (OUT/'audit.json').write_text(json.dumps(audit, indent=2)+'\n')
    manifest = dict(title='The Two Primitives of Spot Market Strategy', author='Fikri Direnç Aktaş',
                    document_date='May 2026', pages=18, printed_pages='i–ii and1–16',
                    uploaded_filename='ssrn-6736280.pdf', source_pdf_sha256=sha(SOURCE/'source.pdf'),
                    source_text_sha256=sha(SOURCE/'source.txt'), review_date='2026-11-08',
                    scope='All18uploaded PDF pages read; focused literature-horizon metadata check; no complete cited-literature replication',
                    source_type='Conceptual working paper; not a supplied strategy or empirical test')
    (SOURCE/'manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
    print(json.dumps(audit, indent=2))


if __name__ == '__main__':
    main()
