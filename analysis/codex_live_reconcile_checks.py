"""Offline regression fixtures for report identity, coverage and matching; no strategy runs."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import pandas as pd

import codex_live_reconcile as R


class ReconcileChecks(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="codex_reconcile_")
        self.root = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def report(self, adx=30, compression="15 Minutes", ml=False, end="2026-10-23 16:00", paired=True, symbol="@NQ", risk=0):
        path = self.root / "report.xlsx"
        st = [["NQ Overnight Bias", None], ["ADXMin", adx], ["Compression", compression],
              ["Symbol Name", symbol], ["RiskPerTrade", risk], ["Start Date", "2018-01-02 09:00"], ["End Date", end]]
        if ml:
            st += [["UseMLFilter", "true"]]
        trades = [dict(Type="Entry Long", Date="2026-10-20 09:00", Contracts=1, Price=20000., Signal="Entry"),
                  dict(Type="Exit Long", Date="2026-10-20 10:00", Contracts=1, Price=20010., Signal="Exit")]
        with pd.ExcelWriter(path) as writer:
            pd.DataFrame(st).to_excel(writer, sheet_name="Settings", index=False, header=False)
            pd.DataFrame(trades if paired else trades[:1]).to_excel(writer, sheet_name="List of Trades", index=False, startrow=2)
        return path

    def import_report(self, path):
        return R.expected_from_report(path, "ONB_ADX30", "ACCOUNT-01", "MNQ", 2,
                                      "2026-10-19", "2026-10-23", self.root)

    def records(self, name, rows):
        cols = ["account","strategy","symbol","entry_time","exit_time","side","qty","entry","exit"]
        path = self.root / name
        pd.DataFrame(rows, columns=cols).to_csv(path, index=False)
        return path

    def row(self, day="2026-10-20", account="ACCOUNT-01", strategy="ONB_ADX30", qty=2, price=20000.):
        return [account,strategy,"MNQ",day+" 09:00",day+" 10:00",1,qty,price,20010.]

    def test_report_key_and_explicit_micro_size(self):
        path = self.import_report(self.report())
        x = R.normalized(path)
        self.assertEqual(x.strategy.tolist(), ["ONB_ADX30"])
        self.assertEqual(x.qty.tolist(), [2])
        self.assertEqual(x.backtest_report_qty.tolist(), [1])
        self.assertEqual(x.account.tolist(), ["ACCOUNT-01"])

    def test_adx20_is_refused(self):
        with self.assertRaisesRegex(ValueError, "ADXMin=30"):
            self.import_report(self.report(adx=20))

    def test_variable_report_sizes_preserved_on_same_root_only(self):
        path = R.expected_from_report(self.report(symbol="@MNQ",risk=1100), "ONB_ADX30", "ACCOUNT-01", "MNQ", "report",
                                      "2026-10-19", "2026-10-23", self.root)
        self.assertEqual(R.normalized(path).qty.tolist(), [1])
        with self.assertRaisesRegex(ValueError, "same NQ/MNQ"):
            R.expected_from_report(self.report(), "ONB_ADX30", "ACCOUNT-01", "MNQ", "report",
                                   "2026-10-19", "2026-10-23", self.root)

    def test_risk_sizing_cannot_be_overwritten_as_fixed(self):
        with self.assertRaisesRegex(ValueError, "Risk-sized report"):
            self.import_report(self.report(risk=1100))

    def test_funded_ml_is_refused_even_at_adx30(self):
        with self.assertRaisesRegex(ValueError, "Funded ML"):
            self.import_report(self.report(ml=True))

    def test_wrong_interval_is_refused(self):
        with self.assertRaisesRegex(ValueError, "15 Minutes"):
            self.import_report(self.report(compression="30 Minutes"))

    def test_old_report_and_unpaired_trade_are_refused(self):
        with self.assertRaisesRegex(ValueError, "complete session span"):
            self.import_report(self.report(end="2026-10-09 16:00"))
        with self.assertRaisesRegex(ValueError, "unpaired"):
            self.import_report(self.report(paired=False))

    def test_ambiguous_chart_tag_is_refused(self):
        with self.assertRaisesRegex(ValueError, "ambiguous chart tag"):
            R.normalized(self.records("ambiguous.csv", [self.row(strategy="ONB")]))

    def test_missed_first_day_account_and_strategy_isolation_and_size(self):
        e = self.records("expected.csv", [self.row(day="2026-10-19"), self.row(account="ACCOUNT-02"), self.row()])
        b = self.records("broker.csv", [self.row(account="ACCOUNT-02", strategy="ONB_ML2_MC"),
                                        self.row(qty=4, price=20000.5)])
        x = R.canonical_comparison(e, b, True, self.root)
        self.assertEqual(x.status.value_counts().to_dict(), {"missed":2, "extra":1, "wrong_size":1})
        wrong = x[x.status=="wrong_size"].iloc[0]
        self.assertEqual(wrong.entry_slip_ticks, 2)
        self.assertEqual(wrong.broker_gross, 76) # 9.5 points * $2 * four MNQ
        self.assertEqual(wrong.expected_gross, 40)
        self.assertTrue((x[x.status=="missed"].entry_time==pd.Timestamp("2026-10-19 09:00")).any())

    def test_incomplete_coverage_never_means_missed(self):
        e = self.records("expected.csv", [self.row()])
        b = self.records("broker.csv", [])
        x = R.canonical_comparison(e, b, False, self.root)
        self.assertEqual(x.status.tolist(), ["unresolved_incomplete_coverage"])

    def test_explicit_report_scope_excludes_other_accounts(self):
        e = self.records("expected.csv", [self.row()])
        b = self.records("broker.csv", [self.row(), self.row(account="ACCOUNT-02")])
        x = R.canonical_comparison(e, b, True, self.root, scope=("ACCOUNT-01","ONB_ADX30","MNQ"))
        self.assertEqual(x.status.tolist(), ["matched"])
        summary = json.loads((self.root/"verified_execution_summary.json").read_text())
        self.assertEqual(summary["input_rows_before_scope_and_date_filters"]["broker"], 2)
        self.assertEqual(summary["broker_rows"], 1)

    def test_sunday_entry_kept_in_monday_session(self):
        row = self.row(day="2026-10-18", strategy="MON_BR")
        row[3], row[4] = "2026-10-18 19:00", "2026-10-19 08:00"
        e = self.records("expected.csv", [row, self.row(day="2026-10-26")])
        b = self.records("broker.csv", [])
        x = R.canonical_comparison(e, b, True, self.root, "2026-10-19", "2026-10-23")
        self.assertEqual(x.strategy.tolist(), ["MON_BR"])
        self.assertEqual(x.status.tolist(), ["missed"])

    def test_empty_inputs_write_valid_summary(self):
        x = R.canonical_comparison(self.records("e.csv", []), self.records("b.csv", []), False, self.root)
        self.assertTrue(x.empty)
        self.assertEqual(json.loads((self.root/"verified_execution_summary.json").read_text())["status_counts"], {})

    def test_dashboard_precision_is_a_day_fact_not_an_execution(self):
        text = '| SYNTH-01 | 2026-10-21 | −$575.82 | balance |\n| SYNTH-02 | 2026-10-21 | −$575.82 | balance |'
        actuals = R.dashboard_actuals(text, '2026-10-21')
        self.assertEqual({k:v['net'] for k,v in actuals.items()}, {'1':-575.82,'2':-575.82})
        self.assertEqual(R.dashboard_actuals(text, '2026-10-20'), {})
        self.assertNotIn('entry_time', actuals['1'])

    def test_cli_compares_without_audit_or_live_reads(self):
        report = self.report()
        b = self.records("broker.csv", [self.row()])
        # CLI is restricted to Codex output paths. Use a unique temporary directory there,
        # then remove it, retaining no synthetic evidence alongside actual audit outputs.
        outputs = Path(__file__).resolve().parent / "outputs"
        with tempfile.TemporaryDirectory(prefix="codex_fixture_", dir=outputs) as out:
            result = subprocess.run([sys.executable, str(Path(R.__file__)), "--compare-only",
                "--expected-report", str(report), "--report-key", "ONB_ADX30", "--account", "ACCOUNT-01",
                "--symbol", "MNQ", "--expected-qty", "2", "--broker", str(b), "--coverage-complete",
                "--start", "2026-10-19", "--end", "2026-10-23", "--output", out], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads((Path(out)/"verified_execution_summary.json").read_text())["status_counts"], {"matched":1})
            self.assertFalse((Path(out)/"audit_summary.json").exists())


if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(ReconcileChecks)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    out = Path(__file__).resolve().parent / "outputs/codex_live_reconcile_followup"
    out.mkdir(exist_ok=True)
    R.json_write(out / "fixture_check_results.json", dict(tests_run=result.testsRun,
        successful=result.wasSuccessful(), failures=[str(t) for t,_ in result.failures],
        errors=[str(t) for t,_ in result.errors], synthetic_only=True,
        actual_weekly_reconciliation_run=False, powershell_executed=False, strategy_trials=0))
    raise SystemExit(0 if result.wasSuccessful() else 1)
