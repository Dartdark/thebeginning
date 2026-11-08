"""Behavioral tests on invented observations; no market returns or profitability test."""
import copy
import math
import sys
import unittest
from datetime import timedelta
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'analysis'))
import codex_delta_straddle_strategy as engine


class Signals(unittest.TestCase):
    def test_source_universe_and_weights(self):
        self.assertEqual(len(engine.WEIGHTS), 41)
        self.assertEqual(engine.WEIGHTS['ES1'], .1206)
        self.assertEqual(engine.WEIGHTS['NQ1'], .0132)
        self.assertIn('YM1_Australian3Y', engine.WEIGHTS)
        self.assertNotIn('YM', engine.WEIGHTS)
        self.assertEqual(engine.HORIZONS, (32, 64, 126, 252, 504))

    def test_known_sample_t_statistics(self):
        # Alternating +/- .01 plus .0001: sample t = .01 * sqrt(n-1).
        result = engine.signal([.0001 + (.01 if i % 2 else -.01) for i in range(504)])
        for horizon in engine.HORIZONS:
            expected = math.erf(.01 * math.sqrt(horizon - 1) / math.sqrt(2))
            self.assertAlmostEqual(result['components'][str(horizon)], expected, places=13)

    def test_zero_mean_signal(self):
        self.assertAlmostEqual(engine.signal([-.01, .01] * 252)['signal'], 0)

    def test_ewma_constant_magnitude(self):
        self.assertAlmostEqual(engine.signal([-.01, .01] * 252)['annual_vol'], .01 * math.sqrt(252))

    def test_odd_signal_and_equal_vol(self):
        data = [.0002 + .01 * math.sin(i) for i in range(504)]
        a, b = engine.signal(data), engine.signal([-x for x in data])
        self.assertAlmostEqual(a['signal'], -b['signal'])
        self.assertEqual(a['annual_vol'], b['annual_vol'])
        self.assertLessEqual(abs(a['signal']), 1)

    def test_warmup(self):
        with self.assertRaises(ValueError):
            engine.signal([-.01, .01] * 251)

    def test_zero_variance_rejected(self):
        with self.assertRaises(ValueError):
            engine.signal([.001] * 504)

    def test_invalid_returns(self):
        for value in (float('nan'), float('inf'), -1., True):
            with self.subTest(value=value), self.assertRaises(ValueError):
                engine.signal([-.01, .01] * 251 + [value, .01])


class Planner(unittest.TestCase):
    def setUp(self):
        self.packet = engine.demo_packet()

    def invalid(self, mutate):
        mutate(self.packet)
        with self.assertRaises((ValueError, KeyError)):
            engine.plan(self.packet)

    def test_full_packet_immutable_and_no_pnl(self):
        before = copy.deepcopy(self.packet)
        output = engine.plan(self.packet)
        self.assertEqual(self.packet, before)
        self.assertEqual(output['market_count'], 41)
        self.assertFalse(output['personal_account_admitted'])
        self.assertEqual(output['financial_return_trials'], 0)
        self.assertNotIn('sharpe', output)

    def test_future_available_history_rejected(self):
        self.invalid(lambda p: p['observations'][-1].update(available_at='2099-01-01T00:00:00Z'))

    def test_unaware_clock_rejected(self):
        self.invalid(lambda p: p.update(decision_at=p['decision_at'][:19]))

    def test_no_missing_or_extra_universe(self):
        self.invalid(lambda p: p['observations'][0]['returns'].pop('NQ1'))

    def test_no_dow_substitution(self):
        row = self.packet['observations'][0]['returns']
        row['YM'] = row.pop('YM1_Australian3Y')
        with self.assertRaises(ValueError):
            engine.plan(self.packet)

    def test_duplicate_calendar_rejected(self):
        self.invalid(lambda p: p['sessions'].__setitem__(1, p['sessions'][0]))

    def test_future_risk_calibration_rejected(self):
        self.invalid(lambda p: p['portfolio_multiplier'].update(sample_end_at='2099-01-01T00:00:00Z'))

    def test_stale_holdings_rejected(self):
        self.invalid(lambda p: p.update(held_asof_at='2000-01-01T00:00:00Z'))

    def test_stale_mapping_rejected(self):
        self.invalid(lambda p: p['markets']['NQ1'].update(asof_at='2000-01-01T00:00:00Z'))

    def test_nonpositive_native_price_rejected(self):
        self.invalid(lambda p: p['markets']['NQ1'].update(reference_price=-1))

    def test_expiry_before_fill_rejected(self):
        self.invalid(lambda p: p['markets']['NQ1'].update(expiry_at=p['decision_at']))

    def test_fractional_held_lots_rejected(self):
        self.invalid(lambda p: p['held']['NQ1'].update(lots=.5))

    def test_positive_latency_required(self):
        self.invalid(lambda p: p.update(latency_seconds=0))

    def test_orders_after_decision(self):
        result = engine.plan(self.packet)
        self.assertTrue(result['orders'])
        expected = engine.clock(self.packet['decision_at']) + timedelta(seconds=60)
        for order in result['orders']:
            self.assertEqual(engine.clock(order['earliest_eligible_fill_at']), expected)

    def fixed_signals(self, value):
        return patch.object(engine, 'signal', return_value={'signal': value, 'annual_vol': .1, 'components': {}})

    def test_notional_weight_not_multiplied_by_class_again(self):
        with self.fixed_signals(.5):
            output = engine.plan(self.packet)
        # 100k NAV * 10% risk * 12.06% source weight * .5 / .1.
        self.assertAlmostEqual(output['signals_and_targets']['ES1']['target_usd'], 6030.)
        self.assertEqual(output['signals_and_targets']['ES1']['target_lots'], 6)

    def test_negative_rounding_toward_zero(self):
        with self.fixed_signals(-.5):
            item = engine.plan(self.packet)['signals_and_targets']['ES1']
        self.assertEqual(item['raw_target_lots'], -6)  # -6.03, not -7

    def test_band_against_confirmed_holdings(self):
        self.packet['held']['ES1']['lots'] = 4
        with self.fixed_signals(.5):
            a = engine.plan(self.packet)['signals_and_targets']['ES1']
        self.assertEqual(a['target_lots'], 4)  # $2030 < $3015 band
        # A prior proposal must not become a fill. Actual 0 instead of 4 means trade to 6.
        self.packet['held']['ES1']['lots'] = 0
        with self.fixed_signals(.5):
            b = engine.plan(self.packet)['signals_and_targets']['ES1']
        self.assertEqual(b['target_lots'], 6)

    def test_small_reversal_stays_in_band(self):
        self.packet['held']['ES1']['lots'] = 1
        with self.fixed_signals(-.05):
            item = engine.plan(self.packet)['signals_and_targets']['ES1']
        self.assertEqual(item['target_lots'], 1)  # Local declared small sign-cross policy

    def test_large_reversal_charges_full_turnover(self):
        self.packet['held']['ES1']['lots'] = 4
        with self.fixed_signals(-.5):
            output = engine.plan(self.packet)
        orders = [o for o in output['orders'] if o['symbol'] == 'ES1']
        self.assertEqual(orders[0]['delta_lots'], -10)
        self.assertEqual(orders[0]['estimated_commission_usd'], 5.)
        self.assertEqual(orders[0]['estimated_spread_slippage_usd'], 7.5)

    def test_budget_reduction_overrides_band(self):
        self.packet['held']['ES1']['lots'] = 4
        self.packet['margin_budget_usd'] = 0
        with self.fixed_signals(.5):
            output = engine.plan(self.packet)
        self.assertEqual(output['signals_and_targets']['ES1']['target_lots'], 0)
        self.assertTrue(output['signals_and_targets']['ES1']['budget_override'])
        self.assertEqual(output['margin_usd'], 0)

    def test_both_budgets_and_integer_lots(self):
        self.packet.update(gross_limit_multiple=.02, margin_budget_usd=70.)
        output = engine.plan(self.packet)
        self.assertLessEqual(output['gross_notional_usd'], 2000.)
        self.assertLessEqual(output['margin_usd'], 70.)
        self.assertTrue(all(isinstance(v['target_lots'], int) for v in output['signals_and_targets'].values()))

    def test_roll_closes_actual_old_and_opens_new(self):
        mapping = self.packet['markets']['ES1']
        old = copy.deepcopy(mapping)
        old.update(contract_id='ES1_OLD', fee_per_lot_usd=2.)
        mapping['old_contract'] = old
        self.packet['held']['ES1'].update(contract_id='ES1_OLD', lots=4)
        with self.fixed_signals(.5):
            output = engine.plan(self.packet)
        orders = [o for o in output['orders'] if o['symbol'] == 'ES1']
        self.assertEqual([o['delta_lots'] for o in orders], [-4, 6])
        self.assertEqual([o['reason'] for o in orders], ['roll_close', 'roll_open'])
        self.assertEqual(sum(o['estimated_commission_usd'] for o in orders), 11.)

    def test_wrong_old_contract_rejected(self):
        self.packet['held']['ES1'].update(contract_id='UNKNOWN_OLD', lots=4)
        self.invalid(lambda p: p['markets']['ES1'].update(old_contract=copy.deepcopy(p['markets']['ES1'])))

    def test_estimated_costs_reconcile(self):
        output = engine.plan(self.packet)
        self.assertEqual(output['estimated_commission_usd'], sum(abs(o['delta_lots']) * .5 for o in output['orders']))
        self.assertEqual(output['estimated_spread_slippage_usd'], sum(abs(o['delta_lots']) * .75 for o in output['orders']))

    def test_later_packet_cannot_change_prior_plan(self):
        first = engine.plan(self.packet)
        later = copy.deepcopy(self.packet)
        later['observations'][-1]['returns']['ES1'] = .8
        engine.plan(later)
        self.assertEqual(first, engine.plan(self.packet))

    def test_admission_blocks_personal_even_when_mechanics_pass(self):
        self.assertFalse(engine.admission()['historical_backtest_run'])
        self.assertIn('NEEDS DATA', engine.admission()['personal'])


if __name__ == '__main__':
    unittest.main()
