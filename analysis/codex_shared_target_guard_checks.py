"""Disconnected writer/reference tests. No MultiCharts compiler or broker."""
from datetime import datetime, timezone
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import codex_shared_target_guard as g

OUT = Path(__file__).resolve().parents[1] / 'analysis/outputs/codex_shared_target_guard_20261028'
OUT.mkdir(parents=True, exist_ok=True)


def at(s):
    return datetime.fromisoformat(s).replace(tzinfo=g.CT)


class Checks(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=OUT)
        self.folder = Path(self.temp.name)
        self.c = g.initialize(self.folder, 'PAPER50', 50000)
        self.now = at('2026-10-28T17:01')
        self.r = g.make_snapshot(self.c, '51480.25', self.now, 1, True)

    def tearDown(self):
        self.temp.cleanup()

    def test_fixed_targets_and_no_reinitialization(self):
        self.assertEqual(self.c['target_cents'], 5305000)
        other = g.initialize(self.folder, 'PAPER150', 150000)
        self.assertEqual(other['target_cents'], 15905000)
        with self.assertRaises(ValueError):
            g.initialize(self.folder, 'PAPER50', 150000)

    def test_cent_precision_and_nonfinite(self):
        self.assertEqual(g.cents('51480.25'), 5148025)
        for v in ['NaN', 'Infinity', '-1', '0', '12.345', '1,200', 'abc', '21474836.48']:
            with self.subTest(v=v), self.assertRaises(ValueError):
                g.cents(v)

    def test_explicit_flat_confirmation(self):
        with self.assertRaises(ValueError):
            g.make_snapshot(self.c, '50000', self.now, 1, False)

    def test_rollover_midnight_and_expiry(self):
        row = g.make_snapshot(self.c, '50000', at('2026-10-28T16:30'), 1, True)
        self.assertEqual(row['SessionDate'], 20261029)
        self.assertEqual(g.validate(row, self.c, self.now), 'VALID_SNAPSHOT')
        self.assertEqual(g.validate(row, self.c, at('2026-10-29T00:05')), 'VALID_SNAPSHOT')
        self.assertEqual(g.validate(row, self.c, at('2026-10-29T15:59')), 'VALID_SNAPSHOT')
        for stamp in ['2026-10-28T16:59', '2026-10-29T16:00', '2026-10-29T17:00']:
            with self.subTest(stamp=stamp), self.assertRaises(ValueError):
                g.validate(row, self.c, at(stamp))

    def test_weekends_and_dst(self):
        for stamp in ['2026-10-30T16:00', '2026-10-31T12:00', '2026-11-01T15:59']:
            with self.subTest(stamp=stamp), self.assertRaises(ValueError):
                g.session_date(at(stamp), publishing=True)
        # Chicago 17:00 is 22:00 UTC in summer and 23:00 UTC after fall-back.
        self.assertEqual(g.session_date(datetime(2026, 10, 28, 22, tzinfo=timezone.utc)), 20261029)
        self.assertEqual(g.session_date(datetime(2026, 11, 1, 23, tzinfo=timezone.utc)), 20261102)
        self.assertEqual(g.session_date(datetime(2026, 3, 8, 22, tzinfo=timezone.utc)), 20260309)

    def test_account_target_and_checksum_rejection(self):
        for key, value in [('Token', self.c['token'] % g.MAX_INT + 1),
                           ('TargetCents', 15905000), ('Schema', 2), ('FlatConfirmed', 0),
                           ('BalanceCents', 0), ('AsOfTime', 2500)]:
            r = dict(self.r, **{key: value})
            r['Checksum'] = g.checksum(r)
            with self.subTest(key=key), self.assertRaises(ValueError):
                g.validate(r, self.c, self.now)
        r = dict(self.r, BalanceCents=5000000)
        with self.assertRaises(ValueError):
            g.validate(r, self.c, self.now)

    def test_future_and_mixed_revision(self):
        row = g.make_snapshot(self.c, '50000', at('2026-10-28T17:02'), 1, True)
        with self.assertRaises(ValueError):
            g.validate(row, self.c, self.now)
        with self.assertRaises(ValueError):
            g.validate(self.r, self.c, self.now, end_revision=2)

    def test_malformed_duplicate_missing_fields(self):
        text = g.encode(self.r)
        for bad in [text.replace('Schema=1', 'Schema=junk'), text + 'Revision=1\n',
                    text.replace('FlatConfirmed=1\n', ''), text + '[Other]\nx=1\n',
                    '[DEFAULT]\nSchema=1\n' + text]:
            with self.subTest(bad=bad[:30]), self.assertRaises((ValueError, g.configparser.Error)):
                g.parse_snapshot(bad)
        with self.assertRaises(FileNotFoundError):
            (self.folder / 'missing.ini').read_text()

    def test_publish_restart_preserves_configuration(self):
        first = g.publish(self.folder, 'PAPER50', '51480.25', self.now, True)
        second = g.publish(self.folder, 'PAPER50', '51500', at('2026-10-29T00:05'), True)
        self.assertEqual((first['Revision'], second['Revision']), (1, 2))
        self.assertEqual(second['TargetCents'], self.c['target_cents'])
        disk = g.parse_snapshot((self.folder / 'PAPER50.ini').read_text())
        self.assertEqual(g.validate(disk, self.c, at('2026-10-29T00:06')), 'VALID_SNAPSHOT')

    def test_second_account_cannot_consume_first(self):
        other = g.initialize(self.folder, 'PAPER150', 150000)
        with self.assertRaises(ValueError):
            g.validate(self.r, other, self.now)
        with self.assertRaises(ValueError):
            g.alias('../PAPER50')

    def test_exclusive_writer_and_atomic_failure(self):
        g.publish(self.folder, 'PAPER50', '50000', self.now, True)
        before = (self.folder / 'PAPER50.ini').read_bytes()
        with g.writer_lock(self.folder / 'PAPER50.lock'):
            with self.assertRaises(FileExistsError):
                g.publish(self.folder, 'PAPER50', '50500', self.now, True)
        with patch.object(g.os, 'replace', side_effect=OSError('simulated sharing violation')):
            with self.assertRaises(OSError):
                g.publish(self.folder, 'PAPER50', '50500', self.now, True)
        self.assertEqual((self.folder / 'PAPER50.ini').read_bytes(), before)
        self.assertFalse((self.folder / 'PAPER50.lock').exists())
        self.assertEqual(sorted(p.name for p in self.folder.iterdir()), ['PAPER50.ini', 'PAPER50.json'])

    def test_target_met_and_revision_exhaustion(self):
        row = g.make_snapshot(self.c, '53050', self.now, 1, True)
        self.assertEqual(g.validate(row, self.c, self.now), 'TARGET_ALREADY_MET')
        with self.assertRaises(ValueError):
            g.make_snapshot(self.c, '50000', self.now, g.MAX_INT + 1, True)

    def test_actual_contract_math_and_tick_rounding(self):
        # 53,050 - 51,480.25 = 1,569.75. At 8 MNQ that is 98.109375 points.
        self.assertEqual(g.limit_price(5148025, 5305000, 20000, 2, 8, '.25', 1), Decimal('20098.25'))
        self.assertEqual(g.limit_price(5148025, 5305000, 20000, 2, 8, '.25', -1), Decimal('19901.75'))
        self.assertEqual(g.limit_price(5000000, 5305000, 20000, 20, 1, '.25', 1), Decimal('20152.5'))
        self.assertEqual(g.limit_price(15000000, 15905000, 20000, 2, 20, '.25', 1), Decimal('20226.25'))
        self.assertEqual(g.limit_price(5000000, 5000051, -1, 2, 1, '.25', -1), Decimal('-1.50'))
        for q in [0, -1, 1.5]:
            with self.assertRaises(ValueError):
                g.limit_price(5000000, 5305000, 20000, 2, q, '.25', 1)

    def test_draft_default_and_mc_date_encoding(self):
        s = (Path(__file__).resolve().parents[1] / 'agents/codex/code/Apex_Target_Guard_Shared_RESEARCH.txt').read_text()
        self.assertIn('EnableOrders(false)', s)
        self.assertIn('ConfirmChicagoClock(false)', s)
        self.assertIn('TodayYMD = TodayEL + 19000000;', s)
        self.assertIn('Rev1 = Rev2', s)
        self.assertIn('CS = CalcCS', s)
        self.assertIn('GetAppInfo(aiRealTimeCalc) = 1', s)
        self.assertNotIn('StartBalance(', s)
        order_lines = [l.strip() for l in s.splitlines() if 'next bar at Px limit;' in l]
        self.assertEqual(len(order_lines), 2)
        self.assertTrue(all(l.startswith('if EnableOrders then ') for l in order_lines))


if __name__ == '__main__':
    result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Checks))
    summary = dict(tests=result.testsRun, failures=len(result.failures), errors=len(result.errors),
                   windows_api_executed=False, multicharts_compiled=False, broker_connected=False,
                   deployed=False, economic_trials=0,
                   code_sha256=hashlib.sha256(Path(g.__file__).read_bytes()).hexdigest(),
                   powerlanguage_sha256=hashlib.sha256((Path(__file__).resolve().parents[1] /
                       'agents/codex/code/Apex_Target_Guard_Shared_RESEARCH.txt').read_bytes()).hexdigest())
    (OUT / 'verification.json').write_text(json.dumps(summary, indent=2) + '\n')
    raise SystemExit(0 if result.wasSuccessful() else 1)
