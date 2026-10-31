"""Behavioral implementation tests only. No sampled historical prices or empirical returns."""
import copy
from dataclasses import replace
import json
import math
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'analysis'))
from codex_bitcoin_inverse_3441913_strategy import (
    Book, Instrument, Model, Quotes, ReviewError, Settings, from_packet,
    inverse_fill, plan_rebalance, rounded,
)

EXAMPLE = Path(__file__).parent / 'research/bitcoin_inverse/synthetic_input.json'


class InverseStrategyTests(unittest.TestCase):
    def setUp(self):
        self.packet = json.loads(EXAMPLE.read_text())
        self.model = Model(**self.packet['model'])
        self.instrument = Instrument(**self.packet['instrument'])
        self.quotes = Quotes(**self.packet['quotes'])
        self.book = Book(**self.packet['book'])
        self.settings = Settings(**self.packet['settings'])
        self.now = self.packet['decision_time']

    def plan(self, **kw):
        values = dict(model=self.model, instrument=self.instrument, quotes=self.quotes,
                      book=self.book, settings=self.settings, decision_time=self.now)
        values.update(kw)
        return plan_rebalance(**values)

    def test_paper_constants_and_covariance_equations(self):
        c1, c2, cond = self.model.coefficients(1000)
        self.assertAlmostEqual(c1, .525586421391032)
        self.assertAlmostEqual(c2, 1.3215951936521102)
        a, d, b = .5994**2, .47**2, .59*.5994*.47
        self.assertAlmostEqual(a*c1+b*c2, .4085)
        self.assertAlmostEqual(b*c1+d*c2, .6002-d)
        self.assertGreater(cond, 1)

    def test_inverse_long_and_short_source_example(self):
        for n in (1, -1):
            remaining, basis, realized = inverse_fill(n, 100, -n, 200, 1)
            self.assertEqual((remaining, basis), (0, 0))
            self.assertAlmostEqual(realized, n*.005)
            self.assertAlmostEqual(realized*205, n*1.025)

    def test_add_uses_harmonic_not_arithmetic_basis(self):
        for sign in (1, -1):
            n, basis, realized = inverse_fill(sign*10, 100, sign*10, 200, 1)
            self.assertEqual(n, sign*20)
            self.assertAlmostEqual(basis, 20/(10/100+10/200))
            self.assertNotEqual(basis, 150)
            self.assertEqual(realized, 0)

    def test_partial_closes_and_reversals(self):
        for sign in (1, -1):
            n, basis, realized = inverse_fill(sign*10, 100, -sign*4, 200, 1)
            self.assertEqual((n, basis), (sign*6, 100))
            self.assertAlmostEqual(realized, sign*.02)
            n, basis, realized = inverse_fill(sign*10, 100, -sign*15, 200, 1)
            self.assertEqual((n, basis), (-sign*5, 200))
            self.assertAlmostEqual(realized, sign*.05)

    def test_inverse_cash_and_unrealized_conservation(self):
        # At a fixed mark, realized+remaining unrealized changes only by execution vs mark.
        for n in (-20, 20):
            for delta in (-30, -5, 5, 30):
                old_u = n*(1/100-1/150)
                new, basis, realized = inverse_fill(n,100,delta,160,1)
                new_u = new*(1/basis-1/150) if new else 0
                self.assertAlmostEqual(realized+new_u-old_u, delta*(1/160-1/150))

    def test_native_lot_rounding_toward_zero(self):
        self.assertEqual(rounded(.3, .1), .3)
        self.assertEqual(rounded(-.39, .1), -.3)
        self.assertEqual(rounded(.39, .1), .3)

    def test_full_proposal_cash_bridge_and_input_immutability(self):
        original = copy.deepcopy(self.packet)
        p = from_packet(self.packet)
        self.assertEqual(self.packet, original)
        self.assertEqual(p['status'], 'OFFLINE_REVIEW_ONLY')
        self.assertGreater(p['rounded_contract_target'], 0)
        self.assertAlmostEqual(p['starting_nav_usd']-p['hypothetical_ending_nav_usd'],
                               p['expected_fees_usd']+p['expected_execution_mark_difference_usd'])
        final = Book(**p['hypothetical_book'])
        self.assertGreaterEqual(final.collateral_btc, p['required_collateral_btc']-1e-12)
        self.assertGreaterEqual(final.usd_cash, 0)
        self.assertEqual(final.contracts, math.trunc(p['raw_targets']['futures_contracts']))
        self.assertTrue(all(x['earliest_eligible_fill'] > x['decision_time'] for x in p['actions']))
        self.assertEqual(p['empirical_return_trials'], 0)

    def test_zero_fee_zero_spread_conserves_nav(self):
        q = replace(self.quotes, spot_bid=40000,spot_ask=40000,futures_bid=40400,futures_ask=40400)
        s = replace(self.settings,spot_fee_rate=0,futures_fee_rate=0)
        p = self.plan(quotes=q,settings=s)
        self.assertAlmostEqual(p['hypothetical_ending_nav_usd'],100000)
        final = Book(**p['hypothetical_book'])
        # Spot risk includes BTC in the collateral wallet; do not buy the full target again outside it.
        self.assertAlmostEqual((final.spot_btc+final.collateral_btc)*q.spot_mark,
                               p['raw_targets']['spot_total_usd'],delta=s.spot_lot_btc*q.spot_mark)

    def test_existing_profit_and_loss_are_marked_before_targets(self):
        for basis in (39000,42000):
            b = replace(self.book,usd_cash=90000,collateral_btc=.25,contracts=10000,entry_price=basis)
            p = self.plan(book=b)
            u = 10000*(1/basis-1/self.quotes.futures_mark)
            self.assertAlmostEqual(p['starting_nav_usd'],100000+u*40000)
            self.assertAlmostEqual(p['starting_nav_usd']-p['hypothetical_ending_nav_usd'],
                                   p['expected_fees_usd']+p['expected_execution_mark_difference_usd'])

    def test_signed_futures_supported_without_short_spot(self):
        m = replace(self.model, mu_futures=0)
        p = self.plan(model=m,settings=replace(self.settings,risk_parameter=-2,max_gross_model_exposure=10))
        self.assertLess(p['rounded_contract_target'],0)
        self.assertGreater(p['raw_targets']['spot_total_usd'],0)

    def test_exponential_scaling_has_inverse_usd_gamma(self):
        s = replace(self.settings,utility='exponential',risk_parameter=.00002)
        p = self.plan(settings=s)
        self.assertAlmostEqual(p['raw_targets']['spot_total_usd'],.525586421391032/.00002)

    def test_future_calibration_quotes_book_are_rejected(self):
        for obj,field in [('model','available_at'),('quotes','available_at'),('book','available_at')]:
            value = getattr(self,obj)
            with self.subTest(obj=obj), self.assertRaises(ReviewError):
                self.plan(**{obj:replace(value,**{field:'2030-01-03T00:00:00Z'})})

    def test_stale_quotes_and_account_and_naive_time_rejected(self):
        for kw in [dict(decision_time='2030-01-02T01:00:00Z'),
                   dict(decision_time='2030-01-02T00:00:01'),
                   dict(book=replace(self.book,as_of='2030-01-01T00:00:00Z'))]:
            with self.subTest(kw=kw), self.assertRaises(ReviewError): self.plan(**kw)

    def test_expiry_guard_includes_latency(self):
        i = replace(self.instrument,expiry='2030-01-02T00:00:02Z')
        with self.assertRaises(ReviewError): self.plan(instrument=i)

    def test_product_and_identity_guards(self):
        for kw in [dict(instrument=replace(self.instrument,kind='perpetual')),
                   dict(instrument=replace(self.instrument,settlement_currency='USD')),
                   dict(quotes=replace(self.quotes,contract_id='OTHER')),
                   dict(book=replace(self.book,contract_id='OTHER'))]:
            with self.subTest(kw=kw), self.assertRaises(ReviewError): self.plan(**kw)

    def test_malformed_price_lots_and_contract_counts(self):
        for kw in [dict(quotes=replace(self.quotes,spot_mark=float('nan'))),
                   dict(quotes=replace(self.quotes,spot_bid=50000)),
                   dict(settings=replace(self.settings,spot_lot_btc=0)),
                   dict(book=replace(self.book,contracts=1.5,entry_price=40000)),
                   dict(book=replace(self.book,contracts=True,entry_price=40000))]:
            with self.subTest(kw=kw), self.assertRaises(ReviewError): self.plan(**kw)

    def test_maintenance_and_insufficient_collateral_are_rejected(self):
        b = replace(self.book,contracts=100000,entry_price=40000)
        with self.assertRaisesRegex(ReviewError,'maintenance'): self.plan(book=b)
        m = replace(self.model,mu_spot=.24,mu_futures=.7,correlation=0)
        with self.assertRaisesRegex(ReviewError,'collateral'):
            self.plan(model=m,settings=replace(self.settings,initial_margin_rate=.9,max_gross_model_exposure=10))

    def test_cash_borrow_and_short_spot_and_exposure_rejected(self):
        with self.assertRaisesRegex(ReviewError,'exposure'):
            self.plan(settings=replace(self.settings,max_gross_model_exposure=.2))
        with self.assertRaisesRegex(ReviewError,'short spot'):
            self.plan(model=replace(self.model,correlation=.9))
        with self.assertRaisesRegex(ReviewError,'borrowing'):
            self.plan(settings=replace(self.settings,risk_parameter=.8,max_gross_model_exposure=20))

    def test_singular_and_ill_conditioned_covariance_rejected(self):
        for rho in (1.,-1.,.99999):
            with self.subTest(rho=rho), self.assertRaises(ReviewError):
                self.plan(model=replace(self.model,correlation=rho))

    def test_invalid_risk_and_fee_parameters(self):
        for s in [replace(self.settings,risk_parameter=0),replace(self.settings,risk_parameter=1),
                  replace(self.settings,utility='exponential',risk_parameter=-1),
                  replace(self.settings,spot_fee_rate=-.1),replace(self.settings,latency_seconds=0),
                  replace(self.settings,wallet_model='exchange_verified')]:
            with self.subTest(settings=s), self.assertRaises(ReviewError): self.plan(settings=s)


if __name__ == '__main__':
    unittest.main(verbosity=2)
