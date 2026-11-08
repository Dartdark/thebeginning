"""Synthetic execution/causality checks only, before financial data runs."""
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[2]/'analysis'))
import codex_delgado_es as E


def day():
    result = dict(date=pd.Timestamp('2018-01-02'), close_j=900,
                  o=np.full(1440,1000.), c=np.full(1440,1000.), mask=np.ones(1440,dtype=bool),
                  vwap=np.full(1440,1000.), opening=1000., prior_close=1000.,
                  sigma=np.full(12,.001), relative_volume=np.ones(12), vol=.01,
                  missing_minutes=0, all_missing=False)
    result['c'][540] = 1002.
    result['o'][541] = 1003.
    return result


class Mechanics(unittest.TestCase):
    def test_features_exclude_current_and_future_return_history(self):
        dates=[d for d in pd.bdate_range('2017-01-03',periods=40)
               if E.calendar_status(d)['kind']=='normal']
        n=len(dates)
        grid=SimpleNamespace(dates=np.array([int(d.strftime('%Y%m%d')) for d in dates]))
        for name in ('o','h','l','c','v'):
            setattr(grid,name,np.full((n,1440),1000.))
        grid.h[:]=1002.; grid.l[:]=998.; grid.v[:]=10.
        for i in range(n):
            grid.c[i,540:901]=1000+np.sin(i)*.1
        before=E.build_features(grid,'2017-12-31')[20]
        grid.c[20,540]=1001.  # Current close changes current feature, never its prior-history estimator.
        grid.c[21:,:]=1001.5
        after=E.build_features(grid,'2017-12-31')[20]
        self.assertTrue(np.array_equal(before['sigma'],after['sigma']))
        self.assertEqual(before['vol'],after['vol'])

    def test_native_contract_and_cost_identity(self):
        daily,t,_ = E.replay([day()], 'base')
        self.assertEqual(len(t), 1)
        self.assertEqual(t.iloc[0].lots, 3)
        self.assertEqual(t.iloc[0].entry_decision_j, 540)
        self.assertEqual(t.iloc[0].entry_fill_j, 541)
        self.assertEqual(t.iloc[0].exit_fill_j, 571)
        self.assertEqual(t.iloc[0].gross, -450.)
        self.assertEqual(t.iloc[0].slippage, 75.)
        self.assertEqual(t.iloc[0].commission, 15.)
        self.assertEqual(t.iloc[0].net, -540.)
        self.assertEqual(daily.net.sum(), t.net.sum())

    def test_future_fill_open_does_not_choose_quantity(self):
        a = day()
        _,first,_ = E.replay([a], 'base')
        a['o'][541] = 1600.
        _,second,flags = E.replay([a], 'base')
        self.assertEqual(first.iloc[0].lots, second.iloc[0].lots)
        self.assertTrue(flags)  # Do not retrospectively resize to pretend cap always held.

    def test_missing_requested_fill_is_not_zero_known_day(self):
        a = day(); a['mask'][541] = False
        daily,_,_ = E.replay([a], 'base')
        self.assertFalse(daily.complete.iloc[0])
        self.assertTrue(np.isnan(daily.return_value.iloc[0]))

    def test_missing_held_path_flag_and_first_observed_exit(self):
        a = day(); a['mask'][550] = False
        daily,t,_ = E.replay([a], 'base')
        self.assertTrue(t.iloc[0].unknown_path)
        self.assertEqual(t.iloc[0].exit_fill_j, 551)
        self.assertFalse(daily.complete.iloc[0])

    def test_cap_after_all_multipliers_and_cost_reserve(self):
        q = E.quantity(100000, 100000, 1000, .001, 1, 'candidate', rv=1.5, performance=1.1)
        self.assertEqual(q, 7)
        self.assertLessEqual(q*1000*50, 4*(100000-q*5))

    def test_short_cost_and_payoff_sign(self):
        a=day(); a['c'][540]=998.; a['o'][541]=997.
        daily,t,_=E.replay([a], 'base')
        self.assertEqual(t.iloc[0].side, -1)
        self.assertLess(t.iloc[0].net, 0)
        self.assertGreater(t.iloc[0].exit, t.iloc[0].exit_raw)

    def test_integer_rounding_and_small_account(self):
        self.assertEqual(E.quantity(1000,1000,5000,.01,1,'base'),0)
        self.assertIsInstance(E.quantity(100000,100000,5000,.01,1,'base'),int)

    def test_relative_volume_missing_does_not_create_lot(self):
        self.assertEqual(E.quantity(100000,100000,1000,.01,1,'candidate',rv=np.nan),0)

    def test_missing_day_has_no_imputed_return(self):
        a=day(); a['mask'][:]=False; a['all_missing']=True
        daily,t,_=E.replay([a],'base')
        self.assertTrue(t.empty)
        self.assertFalse(daily.complete.iloc[0])
        self.assertTrue(np.isnan(daily.return_value.iloc[0]))

    def test_no_new_entry_after_flat_data_gap(self):
        a=day(); a['mask'][520]=False
        _,t,_=E.replay([a],'base')
        self.assertTrue(t.empty)

    def test_performance_overlay_uses_previous_thirty_shadow_days(self):
        days=[]
        for dt in pd.bdate_range('2018-01-02', periods=31):
            a=day(); a['date']=dt; days.append(a)
        shadow={a['date']:.001 for a in days}
        daily,_,_=E.replay(days,'candidate',shadow)
        self.assertTrue((daily.performance_scale.iloc[:30] == 1).all())
        self.assertEqual(daily.performance_scale.iloc[30],.9)
        shadow[days[-1]['date']]=-100.
        other,_,_=E.replay(days,'candidate',shadow)
        self.assertEqual(daily.performance_scale.tolist(),other.performance_scale.tolist())


if __name__ == '__main__':
    unittest.main()
