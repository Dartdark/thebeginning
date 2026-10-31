"""Constructed engineering checks, not financial strategy outcomes."""
import copy
import json
import math
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from decimal import Decimal

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "analysis"))
sys.path.insert(0, str(ROOT / "agents/codex/research/commodity_skew"))
from codex_commodity_skew import adjusted_skew, build_plan, rank_scores, unique_object, UNIVERSE
from synthetic_example import make_packet


class SkewBuildTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base = make_packet()
        cls.valid = build_plan(cls.base)
        cls.selected = cls.valid["positions"][0]["commodity"]

    def setUp(self):
        self.packet = copy.deepcopy(self.base)

    def rejected(self):
        with self.assertRaises((ValueError, KeyError, ArithmeticError)):
            build_plan(self.packet)

    def spec(self):
        return self.packet["entry_contracts"][self.selected]

    def test_known_analytical_sample_skew(self):
        self.assertAlmostEqual(adjusted_skew([-0.01, -0.01, -0.01, 0.03]), 2.0)
        self.assertAlmostEqual(adjusted_skew([-0.03, 0.01, 0.01, 0.01]), -2.0)

    def test_skew_scale_invariance_and_nonfinite(self):
        self.assertAlmostEqual(adjusted_skew([-1, -1, -1, 3]), adjusted_skew([-1e100]*3 + [3e100]))
        for values in ([0, 0, 0], [1, 1, 1], [1, 2], [1, 2, math.nan], [1, 2, math.inf]):
            with self.subTest(values=values), self.assertRaises(ValueError):
                adjusted_skew(values)

    def test_exact_low_and_high_rank_direction(self):
        scores = [dict(commodity=c, skewness=float(i)) for i, c in enumerate(UNIVERSE)]
        long, short = rank_scores(list(reversed(scores)))
        self.assertEqual([p["commodity"] for p in long], list(UNIVERSE[:4]))
        self.assertEqual([p["commodity"] for p in short], list(reversed(UNIVERSE[-4:])))

    def test_cutoff_ties_are_not_arbitrary_positions(self):
        scores = [dict(commodity=c, skewness=float(i)) for i, c in enumerate(UNIVERSE)]
        for boundary in ((3, 4), (17, 18)):
            tied = copy.deepcopy(scores)
            tied[boundary[1]]["skewness"] = tied[boundary[0]]["skewness"] + 1e-14
            with self.subTest(boundary=boundary), self.assertRaises(ValueError):
                rank_scores(tied)

    def test_eight_targets_with_correct_signs_and_no_leverage(self):
        plan = build_plan(self.packet)
        self.assertEqual(len(plan["positions"]), 8)
        self.assertEqual(sum(p["signed_quantity"] > 0 for p in plan["positions"]), 4)
        self.assertEqual(sum(p["signed_quantity"] < 0 for p in plan["positions"]), 4)
        self.assertTrue(all(type(p["signed_quantity"]) is int for p in plan["positions"]))
        self.assertLessEqual(Decimal(plan["gross_reference_weight"]), 1)
        self.assertEqual(len(plan["scores"]), 22)
        self.assertEqual(plan["window_start"], "2025-01-01")

    def test_cost_bridge_and_integer_floor_in_dollars(self):
        for commodity, spec in self.packet["entry_contracts"].items():
            spec.update(contract_id=f"SYN-{commodity}-OTHER", reference_price="100", multiplier="1000",
                        tick_size="0.25", commission_usd_per_contract_side="2")
        plan = build_plan(self.packet)
        self.assertTrue(all(abs(p["signed_quantity"]) == 1 for p in plan["positions"]))
        self.assertEqual(Decimal(plan["gross_reference_weight"]), Decimal("0.8"))
        self.assertEqual(Decimal(plan["net_reference_weight"]), 0)
        self.assertEqual(Decimal(plan["entry_from_flat_commission_estimate_usd"]), 16)
        self.assertEqual(Decimal(plan["entry_from_flat_slippage_estimate_usd"]), 2000)
        self.assertEqual(Decimal(plan["unchanged_contract_roundtrip_cost_estimate_usd"]), 4032)

    def test_unaffordable_selected_leg_stops_whole_plan(self):
        self.packet["reference_nav_usd"] = "1"
        self.rejected()

    def test_no_reduced_or_substituted_universe(self):
        del self.packet["universe"][UNIVERSE[0]]
        self.rejected()
        self.packet = copy.deepcopy(self.base)
        self.packet["universe"]["NQ"] = self.packet["universe"].pop(UNIVERSE[0])
        self.rejected()

    def test_missing_nonselected_asset_is_not_dropped(self):
        selected = {p["commodity"] for p in self.valid["positions"]}
        other = next(c for c in UNIVERSE if c not in selected)
        self.packet["observations"] = [r for r in self.packet["observations"] if r["commodity"] != other]
        self.rejected()

    def test_missing_single_bar_and_duplicate_bar(self):
        self.packet["observations"].pop()
        self.rejected()
        self.packet = copy.deepcopy(self.base)
        self.packet["observations"].append(copy.deepcopy(self.packet["observations"][0]))
        self.rejected()

    def test_twelve_month_calendar_and_warmup_required(self):
        self.packet["universe"][UNIVERSE[0]] = self.packet["universe"][UNIVERSE[0]][25:]
        self.rejected()
        self.packet = copy.deepcopy(self.base)
        self.packet["warmup_sessions"][UNIVERSE[0]] = "2025-01-01"
        self.rejected()

    def test_previous_session_and_clock_alignment(self):
        self.packet["observations"][1]["previous_session"] = "2024-12-31"
        self.rejected()
        self.packet = copy.deepcopy(self.base)
        self.packet["observations"][1]["previous_event_at"] = "2025-01-01T13:00:00-06:00"
        self.rejected()
        self.packet = copy.deepcopy(self.base)
        self.packet["observations"][1]["previous_available_at"] = "2025-01-01T14:02:00-06:00"
        self.rejected()

    def test_splice_return_rejected(self):
        self.packet["observations"][1]["previous_contract_id"] = "OUTGOING-DIFFERENT-CONTRACT"
        self.rejected()

    def test_incoming_contract_uses_its_own_previous_price(self):
        row = self.packet["observations"][0]
        row.update(contract_id="INCOMING", previous_contract_id="INCOMING", previous_close="200")
        # This would be inconsistent on an unchanged contract, but a roll needs the incoming prior close.
        self.assertEqual(build_plan(self.packet)["status"], "OFFLINE_RESEARCH_TARGETS_ONLY")

    def test_unchanged_contract_price_mismatch_rejected(self):
        self.packet["observations"][1]["previous_close"] = "777"
        self.rejected()

    def test_invalid_prices_do_not_remove_events(self):
        for value in ("0", "-1", "NaN", "Infinity", 100):
            with self.subTest(value=value):
                self.packet = copy.deepcopy(self.base)
                self.packet["observations"][0]["close"] = value
                self.rejected()

    def test_future_and_naive_measurements_rejected(self):
        for field, value in (("available_at", "2026-01-02T00:00:00-06:00"),
                             ("event_at", "2025-01-01T14:00:00"),
                             ("available_at", "2025-01-01T13:00:00-06:00")):
            with self.subTest(field=field, value=value):
                self.packet = copy.deepcopy(self.base)
                self.packet["observations"][0][field] = value
                self.rejected()

    def test_future_universe_and_price_provenance_rejected(self):
        for kind in ("universe", "calendar", "price"):
            self.packet = copy.deepcopy(self.base)
            self.packet[kind + "_available_at"] = self.packet["decision_at"]
            self.rejected()

    def test_expired_and_inconsistent_history_ids(self):
        self.packet["observations"][0]["last_trade_date"] = "2024-12-30"
        self.rejected()
        self.packet = copy.deepcopy(self.base)
        self.packet["observations"][1]["last_trade_date"] = "2027-01-01"
        self.rejected()

    def test_same_contract_cannot_masquerade_as_another_commodity(self):
        next_asset = len(self.packet["universe"][UNIVERSE[0]])
        self.packet["observations"][next_asset]["contract_id"] = self.packet["observations"][0]["contract_id"]
        self.packet["observations"][next_asset]["previous_contract_id"] = self.packet["observations"][0]["contract_id"]
        self.rejected()

    def test_non_usd_native_tick_costs_convert_to_usd(self):
        for commodity, spec in self.packet["entry_contracts"].items():
            spec.update(contract_id=f"SYN-{commodity}-OTHER", currency="EUR", reference_price="100",
                        multiplier="100", fx_to_usd="2", tick_size="0.5",
                        commission_usd_per_contract_side="3", slippage_ticks_per_side=2)
        plan = build_plan(self.packet)
        # floor(125000 / (100*100*2)) = 6 per leg. Per-leg slippage = 6*2*0.5*100*2 = 1200.
        self.assertEqual(Decimal(plan["entry_from_flat_slippage_estimate_usd"]), 9600)
        self.assertEqual(Decimal(plan["entry_from_flat_commission_estimate_usd"]), 144)

    def test_decision_month_must_follow_ranking(self):
        self.packet["decision_at"] = "2025-12-31T23:00:00-06:00"
        self.rejected()
        self.packet["decision_at"] = "2026-02-01T00:00:00-06:00"
        self.rejected()

    def test_selected_quote_must_be_fresh_and_consistent(self):
        self.spec()["reference_event_at"] = "2025-12-30T14:00:00-06:00"
        self.rejected()
        self.packet = copy.deepcopy(self.base)
        self.spec()["reference_price"] = "777"
        self.rejected()

    def test_selected_fx_and_spec_clocks(self):
        for field in ("fx_available_at", "spec_available_at"):
            self.packet = copy.deepcopy(self.base)
            self.spec()[field] = self.packet["decision_at"]
            self.rejected()
        self.packet = copy.deepcopy(self.base)
        self.spec()["fx_to_usd"] = "2"
        self.rejected()

    def test_delivery_and_last_trade_deadlines(self):
        self.spec()["delivery_deadline_at"] = self.spec()["next_roll_or_exit_at"]
        self.rejected()
        self.packet = copy.deepcopy(self.base)
        self.spec()["last_trade_at"] = "2026-02-01T00:00:00-06:00"
        self.rejected()

    def test_no_entry_at_decision_or_action_after_holding_month(self):
        self.spec()["earliest_fill_at"] = self.packet["decision_at"]
        self.rejected()
        self.packet = copy.deepcopy(self.base)
        self.spec()["next_roll_or_exit_at"] = "2026-02-01T00:00:00-06:00"
        self.rejected()

    def test_nonnegative_explicit_costs(self):
        for field, value in (("slippage_ticks_per_side", -1), ("slippage_ticks_per_side", True),
                             ("slippage_ticks_per_side", 0.5), ("commission_usd_per_contract_side", "-1")):
            self.packet = copy.deepcopy(self.base)
            self.spec()[field] = value
            self.rejected()

    def test_duplicate_json_keys_rejected(self):
        with self.assertRaises(ValueError):
            json.loads('{"commodity": 1, "commodity": 2}', object_pairs_hook=unique_object)

    def test_cli_invalid_packet_preserves_existing_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            packet, output = Path(tmp) / "bad.json", Path(tmp) / "result.json"
            packet.write_text('{"ranking_month":"2025-12"}')
            output.write_text("prior valid artifact")
            result = subprocess.run([sys.executable, str(ROOT / "analysis/codex_commodity_skew.py"),
                                     str(packet), "--output", str(output)], capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(output.read_text(), "prior valid artifact")


if __name__ == "__main__":
    unittest.main()
