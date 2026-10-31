"""Synthetic engineering checks only; no historical observations or strategy returns."""
from dataclasses import replace
from datetime import datetime, timedelta, timezone
from decimal import Decimal
import unittest

from codex_weekly_basis_reversal import Contract, Settlement, build_direction


class SignalContractTests(unittest.TestCase):
    def setUp(self):
        self.start = datetime(2000, 1, 7, 20, tzinfo=timezone.utc)
        self.end = self.start + timedelta(days=7)
        self.front = Contract('SYNTH-F', 'SYNTH', 'USD', self.end + timedelta(days=60))
        self.back = Contract('SYNTH-B', 'SYNTH', 'USD', self.end + timedelta(days=90))
        def obs(id, event, price):
            return Settlement(id, event, event + timedelta(minutes=30), Decimal(price))
        self.fs = obs('SYNTH-F', self.start, '100')
        self.fe = obs('SYNTH-F', self.end, '104')
        self.bs = obs('SYNTH-B', self.start, '200')
        self.be = obs('SYNTH-B', self.end, '202')
        self.options = dict(decision_at=self.end + timedelta(days=3),
                            planned_exit_at=self.end + timedelta(days=10),
                            minimum_remaining_days=30)

    def signal(self, **changes):
        args = dict(front=self.front, deferred=self.back, front_start=self.fs,
                    front_end=self.fe, deferred_start=self.bs, deferred_end=self.be,
                    **self.options)
        args.update(changes)
        return build_direction(**args)

    def test_reverse_front_relative_strength(self):
        s = self.signal()
        self.assertEqual((s.front_side, s.deferred_side), (-1, 1))

    def test_reverse_deferred_relative_strength(self):
        s = self.signal(front_end=replace(self.fe, price=Decimal('99')))
        self.assertEqual((s.front_side, s.deferred_side), (1, -1))

    def test_exact_equal_growth_is_flat(self):
        s = self.signal(front_end=replace(self.fe, price=Decimal('101')))
        self.assertEqual((s.front_side, s.deferred_side), (0, 0))

    def test_latest_available_leg_controls_decision(self):
        with self.assertRaisesRegex(ValueError, 'availability'):
            self.signal(deferred_end=replace(self.be, available_at=self.options['decision_at']))

    def test_cannot_use_settlement_before_publication(self):
        with self.assertRaisesRegex(ValueError, 'availability'):
            self.signal(decision_at=self.end + timedelta(minutes=1))

    def test_rolling_endpoint_cannot_switch_contract(self):
        with self.assertRaisesRegex(ValueError, 'identity'):
            self.signal(front_start=replace(self.fs, contract_id='SYNTH-OLD'))

    def test_missing_or_misaligned_leg_not_filled(self):
        with self.assertRaisesRegex(ValueError, 'matched'):
            self.signal(deferred_start=replace(self.bs, event_at=self.start-timedelta(days=1)))

    def test_first_notice_protects_delivery(self):
        with self.assertRaisesRegex(ValueError, 'expiry buffer'):
            self.signal(front=replace(self.front, first_notice_at=self.end+timedelta(days=20)))

    def test_exit_cannot_reach_contract_deadline(self):
        with self.assertRaisesRegex(ValueError, 'holding'):
            self.signal(planned_exit_at=self.front.last_trade_at)

    def test_negative_zero_nan_prices_stop_protocol(self):
        for price in ('0', '-1', 'NaN', 'Infinity'):
            with self.subTest(price=price), self.assertRaisesRegex(ValueError, 'positive'):
                self.signal(front_end=replace(self.fe, price=Decimal(price)))

    def test_mixed_commodity_and_currency_rejected(self):
        for change in ({'commodity':'OTHER'}, {'currency':'EUR'}):
            with self.subTest(change=change), self.assertRaises(ValueError):
                self.signal(deferred=replace(self.back, **change))

    def test_naive_clocks_rejected(self):
        with self.assertRaisesRegex(ValueError, 'Timezone'):
            self.signal(decision_at=self.options['decision_at'].replace(tzinfo=None))
        with self.assertRaisesRegex(ValueError, 'Timezone'):
            self.signal(front=replace(self.front, last_trade_at=self.front.last_trade_at.replace(tzinfo=None)))

    def test_availability_before_event_rejected(self):
        with self.assertRaisesRegex(ValueError, 'before its event'):
            self.signal(front_end=replace(self.fe, available_at=self.start))

    def test_explicit_buffer_and_increasing_times_required(self):
        for change in ({'minimum_remaining_days':True}, {'minimum_remaining_days':-1},
                       {'planned_exit_at':self.options['decision_at']}):
            with self.subTest(change=change), self.assertRaises(ValueError):
                self.signal(**change)


if __name__ == '__main__':
    unittest.main()
