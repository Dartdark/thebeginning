"""Regression checks for the MC `open` sentinel that stopped the data rebuild."""
from pathlib import Path
import sys
from types import SimpleNamespace
import unittest

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "analysis"))
from codex_refresh_audit import closed_report_mask


class ReportSelectionTest(unittest.TestCase):
    def setUp(self):
        self.grid = SimpleNamespace(dates=np.array([20261009, 20261012]), D=2)

    def test_unfinished_midnight_exit_is_excluded(self):
        entries = pd.DataFrame({"Date": ["2026-10-09 09:15", "2026-10-12 09:15"]})
        exits = pd.DataFrame({"Signal": ["ON Bias SX", "open"]})
        np.testing.assert_array_equal(closed_report_mask(self.grid, entries, exits), [True, False])

    def test_case_and_whitespace_are_normalized(self):
        entries = pd.DataFrame({"Date": ["2026-10-12 09:15"]})
        exits = pd.DataFrame({"Signal": [" OPEN "]})
        np.testing.assert_array_equal(closed_report_mask(self.grid, entries, exits), [False])

    def test_missing_grid_dates_do_not_shift_exit_alignment(self):
        entries = pd.DataFrame({"Date": ["2026-10-08", "2026-10-09", "2026-10-12", "2026-10-13"]})
        exits = pd.DataFrame({"Signal": ["open", "Stop Loss", "open", "Profit Target"]})
        np.testing.assert_array_equal(closed_report_mask(self.grid, entries, exits), [True, False])

    def test_other_exit_labels_are_preserved(self):
        entries = pd.DataFrame({"Date": ["2026-10-09", "2026-10-12"]})
        exits = pd.DataFrame({"Signal": [None, "reopen exit"]})
        np.testing.assert_array_equal(closed_report_mask(self.grid, entries, exits), [True, True])

    def test_unpaired_rows_fail(self):
        with self.assertRaisesRegex(ValueError, "Unpaired"):
            closed_report_mask(self.grid, pd.DataFrame({"Date": ["2026-10-12"]}),
                               pd.DataFrame({"Signal": []}))


if __name__ == "__main__":
    unittest.main()
