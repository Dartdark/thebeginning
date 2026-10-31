"""Constructed mechanics only. No historical data or economic outcomes."""
import copy
import json
from pathlib import Path
import unittest
from decimal import Decimal

from codex_rad_double_sort import build_plan


def fixture():
    symbols = [f'SYNTH{i:02}' for i in range(22)]
    packet = dict(ranking_month='2021-01', formation_session='2021-02-01',
                  decision_at='2021-02-01T10:00:00+00:00', reference_nav='4000',
                  universe_provenance='SYNTHETIC fixed 22-symbol universe',
                  calendar_provenance='SYNTHETIC two-session month, not an exchange calendar',
                  universe_available_at='2021-01-01T00:00:00+00:00',
                  calendar_available_at='2021-01-01T00:00:00+00:00',
                  universe={s: ['2021-01-30', '2021-01-31'] for s in symbols},
                  warmup_sessions={s: '2020-12-31' for s in symbols},
                  observations=[], entry_contracts={})
    for i, symbol in enumerate(symbols):
        previous = Decimal(100)
        for day in (30, 31):
            front = previous * (Decimal(100) + i) / 100
            packet['observations'].append(dict(
                symbol=symbol, session=f'2021-01-{day}', previous_session=f'2021-01-{day-1}' if day==31 else '2020-12-31',
                front_id=symbol+'-F', second_id=symbol+'-S', previous_close_contract_id=symbol+'-F',
                front_expiry='2021-02-20', second_expiry='2021-03-20',
                front_close=str(front), second_close='100', previous_close=str(previous),
                front_event_at=f'2021-01-{day}T20:00:00+00:00',
                second_event_at=f'2021-01-{day}T20:00:00+00:00',
                front_available_at=f'2021-01-{day}T20:01:00+00:00',
                second_available_at=f'2021-01-{day}T20:01:00+00:00',
                previous_event_at=('2021-01-30' if day==31 else '2020-12-31')+'T20:00:00+00:00',
                previous_available_at=('2021-01-30' if day==31 else '2020-12-31')+'T20:01:00+00:00'))
            previous = front
        packet['entry_contracts'][symbol] = dict(
            contract_id=symbol+'-F', currency='USD', reference_price='100', multiplier='1', fx_to_account='1',
            reference_price_event_at='2021-01-31T20:00:00+00:00',
            reference_price_available_at='2021-01-31T20:01:00+00:00',
            fx_event_at='2021-01-31T20:00:00+00:00', fx_available_at='2021-01-31T20:01:00+00:00',
            spec_available_at='2020-12-31T20:01:00+00:00',
            earliest_fill_at='2021-02-01T11:00:00+00:00',
            next_roll_or_exit_at='2021-02-15T20:00:00+00:00',
            delivery_or_last_trade_deadline='2021-02-20T20:00:00+00:00',
            roll_calendar_provenance='SYNTHETIC delivery/roll schedule')
    return packet


class Mechanics(unittest.TestCase):
    def setUp(self):
        self.p = fixture()

    def reject_row(self, field, value):
        self.p['observations'][0][field] = value
        with self.assertRaises(ValueError): build_plan(self.p)

    def test_both_sorts_and_gross_integer_budget(self):
        r = build_plan(self.p)
        self.assertEqual([x['symbol'] for x in r['positions'] if x['side']==1],
                         ['SYNTH21','SYNTH20','SYNTH19','SYNTH18'])
        self.assertEqual([x['symbol'] for x in r['positions'] if x['side']==-1],
                         ['SYNTH00','SYNTH01','SYNTH02','SYNTH03'])
        self.assertEqual(Decimal(r['gross_reference_weight']), 2)
        self.assertEqual([x['signed_quantity'] for x in r['positions']], [10]*4+[-10]*4)

    def test_carry_changes_selection_within_frozen_momentum_tails(self):
        for row in self.p['observations']:
            i = int(row['symbol'][-2:])
            row['second_close'] = str(Decimal(row['front_close']) * (Decimal(100)+i)/100)
        r=build_plan(self.p)
        self.assertEqual([x['symbol'] for x in r['positions']],
                         ['SYNTH14','SYNTH15','SYNTH16','SYNTH17','SYNTH07','SYNTH06','SYNTH05','SYNTH04'])

    def test_missing_nonselected_symbol_still_stops(self):
        self.p['observations']=[r for r in self.p['observations'] if r['symbol']!='SYNTH10']
        with self.assertRaises(ValueError): build_plan(self.p)

    def test_duplicate_stops(self):
        self.p['observations'].append(copy.deepcopy(self.p['observations'][0]))
        with self.assertRaises(ValueError): build_plan(self.p)

    def test_same_contract_return_required(self): self.reject_row('previous_close_contract_id','OTHER')
    def test_nonpositive_price(self): self.reject_row('front_close','0')
    def test_nan(self): self.reject_row('second_close','NaN')
    def test_late_information(self): self.reject_row('second_available_at','2021-02-01T10:01:00+00:00')
    def test_impossible_information(self): self.reject_row('front_available_at','2021-01-30T19:59:00+00:00')
    def test_naive_clock(self): self.reject_row('front_event_at','2021-01-30T20:00:00')
    def test_maturity_order(self): self.reject_row('second_expiry','2021-02-19')
    def test_measurement_mismatch(self): self.reject_row('second_event_at','2021-01-30T20:02:00+00:00')
    def test_prior_session_gap(self):
        self.p['observations'][1]['previous_session']='2021-01-29'
        with self.assertRaises(ValueError): build_plan(self.p)

    def test_no_silent_unaffordable_leg(self):
        self.p['reference_nav']='1'
        with self.assertRaises(ValueError): build_plan(self.p)

    def test_delivery_deadline(self):
        self.p['entry_contracts']['SYNTH21']['delivery_or_last_trade_deadline']='2021-02-10T00:00:00+00:00'
        with self.assertRaises(ValueError): build_plan(self.p)

    def test_late_fx(self):
        self.p['entry_contracts']['SYNTH21']['fx_available_at']='2021-02-01T10:01:00+00:00'
        with self.assertRaises(ValueError): build_plan(self.p)

    def test_tied_tails_unresolved(self):
        for row in self.p['observations']: row['previous_close']=row['front_close']
        with self.assertRaises(ValueError): build_plan(self.p)

    def test_integer_rounding_never_increases_gross(self):
        self.p['reference_nav']='4999'
        r=build_plan(self.p)
        self.assertLess(Decimal(r['gross_reference_weight']),2)
        self.assertTrue(all(abs(Decimal(x['reference_signed_weight']))<=Decimal('.25') for x in r['positions']))

    def test_late_universe(self):
        self.p['universe_available_at']='2021-02-02T00:00:00+00:00'
        with self.assertRaises(ValueError): build_plan(self.p)

    def test_unverified_warmup(self): self.reject_row('previous_session','2020-12-30')

    def test_late_formation(self):
        self.p['decision_at']='2021-02-15T10:00:00+00:00'
        with self.assertRaises(ValueError): build_plan(self.p)

    def test_late_monthly_action(self):
        self.p['entry_contracts']['SYNTH21']['next_roll_or_exit_at']='2021-03-01T10:00:00+00:00'
        self.p['entry_contracts']['SYNTH21']['delivery_or_last_trade_deadline']='2021-03-20T10:00:00+00:00'
        with self.assertRaises(ValueError): build_plan(self.p)

    def test_previous_clock_must_match_calendar(self):
        self.p['observations'][1]['previous_event_at']='2021-01-29T20:00:00+00:00'
        with self.assertRaises(ValueError): build_plan(self.p)


if __name__ == '__main__':
    unittest.main(verbosity=2)
