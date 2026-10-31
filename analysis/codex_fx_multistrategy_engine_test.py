"""Synthetic correctness checks; no economic returns or strategy validation."""
import copy
import json
from pathlib import Path
import unittest

import numpy as np
import pandas as pd
import codex_fx_multistrategy_engine as E


class Mechanics(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.packet = E.synthetic_packet()
        cls.data, _, _ = E.validate(cls.packet)
        cls.raw, cls.returns = E.features(cls.data)
        cls.cov = E.asset_covariance(cls.returns)
        cls.plan = E.build_plan(cls.packet)

    def reject(self, mutation):
        packet = copy.deepcopy(self.packet)
        mutation(packet)
        with self.assertRaises((ValueError,KeyError)):
            E.build_plan(packet)

    def test_demo_finite_deterministic_and_constraints(self):
        p = E.build_plan(self.packet)
        self.assertEqual(p,self.plan)
        self.assertTrue(p["synthetic"])
        self.assertFalse(p["source_replication"])
        self.assertEqual(len(p["signals"]),12)
        self.assertEqual(len(p["positions"]),8)
        self.assertLessEqual(p["ideal_annual_volatility"],.10+1e-10)
        self.assertLessEqual(p["rounded_annual_volatility"],.10+1e-10)
        self.assertLessEqual(p["rounded_gross"],3.+1e-10)
        self.assertAlmostEqual(sum(p["sleeve_allocations"].values()),1.,places=7)
        self.assertTrue(all(x>=0 for x in p["sleeve_allocations"].values()))
        json.dumps(p,allow_nan=False)

    def test_equal_baseline_and_whole_contracts(self):
        p = E.build_plan(self.packet,"equal")
        np.testing.assert_allclose(list(p["sleeve_allocations"].values()),np.ones(12)/12)
        for x in p["positions"]:
            self.assertIsInstance(x["reference_contracts"],int)
            self.assertLessEqual(abs(x["rounded_weight"]),abs(x["ideal_weight"])+1e-10)

    def test_prior_rank_ties_and_extremes(self):
        frame = pd.DataFrame(np.ones((64,8)),columns=E.SYMBOLS)
        np.testing.assert_equal(E.prior_percentile(frame),np.zeros(8))
        frame.iloc[-1]=2.
        np.testing.assert_equal(E.prior_percentile(frame),np.ones(8)*.5)
        frame.iloc[-1]=0.
        np.testing.assert_equal(E.prior_percentile(frame),np.ones(8)*-.5)

    def test_rank_warmup_is_required(self):
        with self.assertRaises(ValueError):
            E.prior_percentile(pd.DataFrame(np.ones((63,8)),columns=E.SYMBOLS))

    def test_negative_yields_and_signal_formulas(self):
        self.assertTrue((self.data.yield_1y<0).any())
        expected=(self.data.yield_1y-self.data.usd_yield_1y).unstack().reindex(columns=E.SYMBOLS)
        np.testing.assert_allclose(self.raw["carry_1y"],expected)
        r=self.returns
        expected=np.log1p(r).iloc[-63:].sum()
        np.testing.assert_allclose(self.raw["momentum_63"].iloc[-1],expected)

    def test_covariance_psd_and_marginal_budgets(self):
        self.assertGreater(np.linalg.eigvalsh(self.cov).min(),0.)
        score=np.array([.5,-.3,.2,-.4,.1,-.2,.5,-.1])
        w=E.signed_budget(score,self.cov)
        np.testing.assert_equal(np.sign(w),np.sign(score))
        rc=w*(self.cov@w)
        np.testing.assert_allclose(rc/rc.sum(),np.abs(score)/np.abs(score).sum(),atol=1e-5)

    def test_zero_signal_cash(self):
        np.testing.assert_equal(E.signed_budget(np.zeros(8),self.cov),np.zeros(8))
        w,a=E.combine({"off":np.zeros(8)},self.cov,"equal")
        np.testing.assert_equal(w,np.zeros(8)); np.testing.assert_equal(a,[0.])

    def test_future_observation_rejected(self):
        self.reject(lambda p:p["observations"][-1].update(available_at="2026-10-02T00:00:00Z"))

    def test_event_after_availability_rejected(self):
        self.reject(lambda p:p["observations"][-1].update(event_at="2026-10-01T00:00:00Z"))

    def test_naive_clock_rejected(self):
        self.reject(lambda p:p.update(decision_at="2026-10-01T00:00:00"))

    def test_missing_currency_or_session_rejected(self):
        self.reject(lambda p:p["observations"].pop())
        self.reject(lambda p:p.update(observations=[r for r in p["observations"] if r["symbol"]!="6J"]))

    def test_duplicate_rejected(self):
        self.reject(lambda p:p["observations"].append(p["observations"][-1]))

    def test_splice_rejected(self):
        self.reject(lambda p:p["observations"][-1].update(previous_close_contract_id="OLD-CONTRACT"))

    def test_previous_close_and_session_reconcile(self):
        self.reject(lambda p:p["observations"][-1].update(previous_close=2.))
        self.reject(lambda p:p["observations"][-1].update(previous_session="2026-09-28"))

    def test_roll_with_same_incoming_contract_return(self):
        p=copy.deepcopy(self.packet)
        p["observations"][-1].update(contract_id="NEW-6S",previous_close_contract_id="NEW-6S",
                                     close=2.,previous_close=2.)
        data,_,_=E.validate(p)
        _,r=E.features(data)
        self.assertEqual(r.iloc[-1]["6S"],0.)

    def test_missing_negative_nonfinite_prices_rejected(self):
        for value in (0.,-1.,float("nan"),float("inf")):
            with self.subTest(value=value):
                self.reject(lambda p:p["observations"][-1].update(close=value))

    def test_shared_macro_consistency(self):
        self.reject(lambda p:p["observations"][-1].update(usd_yield_1y=999.))

    def test_reference_and_metadata_clock(self):
        self.reject(lambda p:p["reference_contracts"]["6E"].update(price_available_at="2026-10-02T00:00:00Z"))
        self.reject(lambda p:p["reference_contracts"]["6E"].update(spec_available_at="2026-10-02T00:00:00Z"))

    def test_action_before_expiry_and_fill_after_decision(self):
        self.reject(lambda p:p["reference_contracts"]["6E"].update(delivery_or_expiry_at="2026-10-15T00:00:00Z"))
        self.reject(lambda p:p["reference_contracts"]["6E"].update(earliest_fill_at=p["decision_at"]))

    def test_margin_and_quote_currency(self):
        self.reject(lambda p:p.update(margin_budget_usd=.01))
        self.reject(lambda p:p["reference_contracts"]["6E"].update(quote_currency="EUR"))

    def test_frozen_month_and_calendar(self):
        self.reject(lambda p:p.update(rebalance_month="2026-11"))
        self.reject(lambda p:p.update(sessions=p["sessions"][::-1]))
        self.reject(lambda p:p.update(calendar_available_at="2026-10-02T00:00:00Z"))

    def test_reference_rounding_may_hold_cash(self):
        p=copy.deepcopy(self.packet); p.update(nav_usd=100.,margin_budget_usd=100.)
        plan=E.build_plan(p)
        self.assertTrue(plan["all_rounded_to_zero"])
        self.assertEqual(plan["reference_margin_usd"],0.)

    def test_diversification_ratio_dominates_equal_at_same_sleeves(self):
        m=np.array([list(x.values()) for x in self.plan["sleeve_exposures"].values()])
        c=m@self.cov@m.T
        sigma=np.sqrt(np.diag(c))
        a=np.array(list(self.plan["sleeve_allocations"].values()))
        equal=np.ones(12)/12
        ratio=lambda w:(w@sigma)/np.sqrt(w@c@w)
        self.assertGreaterEqual(ratio(a)+1e-6,ratio(equal))

    def test_insufficient_calendar_stops_before_optimization(self):
        self.reject(lambda p:p.update(sessions=p["sessions"][-315:]))

    def test_zero_risk_history_rejected(self):
        with self.assertRaises(ValueError):
            E.asset_covariance(self.returns*0.)

    def test_unknown_mode_rejected(self):
        with self.assertRaises(ValueError):
            E.build_plan(self.packet,"best_backtest")


if __name__ == "__main__":
    unittest.main(verbosity=2)
