"""Disconnected synthetic contract tests. Authored but NOT RUN in this chat.

Run: python3 -m unittest discover -s agents/codex/tests -p test_us100_donchian_core.py -v
No prices are read and no strategy-return trial is performed.
"""
import sys
import unittest
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "analysis"))
from codex_us100_donchian_core import InputError, Minute, Snapshot, Policy, Position, NativeCore

T = datetime(2024, 1, 2, 9, 0, tzinfo=ZoneInfo("America/Chicago"))
ALLOW = Policy(True, False, "synthetic-open")
BLOCK = Policy(False, False, "synthetic-block")
FLAT = Policy(False, True, "synthetic-cutoff")


def bar(at=T, o=100, h=101, l=99, c=100, contract="MNQH4", gap=False):
    return Minute(at, o, h, l, c, contract, gap)


def snap(at=T, close=106, high=105, low=95, atr=2):
    return Snapshot(at, close, high, low, atr)


def held():
    core = NativeCore()
    core.position = Position(T-timedelta(minutes=15), 100.25, 97, "MNQH4")
    return core


class CoreContractTests(unittest.TestCase):
    def test_last_close_strictly_breaks_older_channel(self):
        core = NativeCore()
        core.step(bar(h=120), ALLOW, snap(close=105, high=105))
        self.assertIsNone(core.position)  # intraminute high is not a close signal

    def test_future_indicator_rejected_before_trading(self):
        core = NativeCore()
        with self.assertRaises(InputError):
            core.step(bar(), ALLOW, snap(at=T+timedelta(minutes=15)))
        self.assertIsNone(core.position)

    def test_initial_stop_is_active_on_entry_minute(self):
        core = NativeCore()
        result = core.step(bar(l=96), ALLOW, snap())
        self.assertEqual(core.trades[0].reason, "stop")
        self.assertAlmostEqual(core.trades[0].entry, 100.25)
        self.assertAlmostEqual(core.trades[0].exit, 96.75)
        self.assertAlmostEqual(core.cash, -8.04)
        self.assertAlmostEqual(result["adverse"], -8.04)
        self.assertFalse(core.reconcile()["open_position"])

    def test_stop_gap_fills_at_worse_open(self):
        core = held()
        core.step(bar(o=90, h=91, l=89, c=90), BLOCK)
        self.assertEqual(core.trades[0].reason, "gap_stop")
        self.assertAlmostEqual(core.trades[0].exit, 89.75)
        self.assertAlmostEqual(core.cash, -22.04)

    def test_trailing_updates_only_with_completed_snapshot(self):
        core = held()
        core.step(bar(o=110, h=140, l=109, c=110), BLOCK)
        self.assertEqual(core.position.stop, 97)
        self.assertEqual(core.position.entry, 100.25)

    def test_new_trailing_stop_is_active_immediately(self):
        core = held()
        core.step(bar(o=110, h=111, l=105, c=110), BLOCK,
                  snap(close=104, high=105))
        self.assertEqual(core.trades[0].reason, "stop")
        self.assertAlmostEqual(core.trades[0].exit, 105.75)

    def test_calendar_cutoff_closes_and_does_not_reenter(self):
        core = held()
        core.step(bar(o=102, h=103, l=101, c=102), FLAT, snap())
        self.assertEqual(core.trades[0].reason, "calendar_flat")
        self.assertIsNone(core.position)
        self.assertEqual(len(core.trades), 1)
        self.assertAlmostEqual(core.cash, 1.96)

    def test_bad_cutoff_policy_rejected(self):
        with self.assertRaises(InputError):
            NativeCore().step(bar(), Policy(True, True, "bad"))

    def test_channel_exit_uses_previous_completed_close(self):
        core = held()
        core.step(bar(), BLOCK, snap(close=94, high=105, low=95))
        self.assertEqual(core.trades[0].reason, "channel")
        self.assertAlmostEqual(core.cash, -2.04)

    def test_positive_open_equity_not_replaced_by_closed_cash(self):
        core = held()
        r = core.step(bar(o=110, h=111, l=109, c=110), BLOCK)
        self.assertAlmostEqual(r["adverse"], (109-100.25)*2-1.04)
        self.assertGreater(r["adverse"], 0)

    def test_duplicate_event_rejected(self):
        core = NativeCore()
        core.step(bar(), BLOCK)
        with self.assertRaises(InputError):
            core.step(bar(), BLOCK)

    def test_unresolved_data_gap_with_position_rejected(self):
        core = NativeCore()
        core.step(bar(), ALLOW, snap())
        with self.assertRaises(InputError):
            core.step(bar(at=T+timedelta(minutes=2)), BLOCK)

    def test_held_contract_switch_rejected(self):
        core = NativeCore()
        core.step(bar(), ALLOW, snap())
        with self.assertRaises(InputError):
            core.step(bar(at=T+timedelta(minutes=1), contract="MNQM4"), BLOCK)

    def test_declared_closed_session_gap_retains_gap_risk(self):
        core = NativeCore()
        core.step(bar(), ALLOW, snap())
        core.step(bar(at=T+timedelta(days=2), o=90, h=91, l=89, c=90, gap=True), BLOCK)
        self.assertEqual(core.trades[0].reason, "gap_stop")

    def test_round_trip_fee_is_charged_once(self):
        core = held()
        core.step(bar(), FLAT)
        net = core.cash
        core.step(bar(at=T+timedelta(minutes=1)), FLAT)
        self.assertEqual(core.cash, net)
        self.assertEqual(core.reconcile()["closed_trades"], 1)

    def test_missing_calendar_and_naive_clocks_rejected(self):
        with self.assertRaises(InputError):
            NativeCore().step(bar(), Policy(True, False, ""))
        with self.assertRaises(InputError):
            NativeCore().step(bar(at=T.replace(tzinfo=None)), BLOCK)

    def test_native_stop_rounding(self):
        self.assertEqual(NativeCore().stop_tick(97.24), 97)
        self.assertEqual(NativeCore().stop_tick(97.25), 97.25)


if __name__ == "__main__":
    unittest.main()
