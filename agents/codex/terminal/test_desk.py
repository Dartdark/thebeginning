"""Presentation admission and unknown-state checks; no return tests."""
import json
from pathlib import Path
import tempfile
import unittest
import desk


class DeskTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.scout = self.root / 'agents/codex/research/scout'
        (self.scout / 'records').mkdir(parents=True)
        self.report = self.root / 'agents/codex/results/report.md'
        self.report.parent.mkdir(parents=True)
        self.report.write_text('# Report')
        self.csv = self.root / 'analysis/outputs/codex_fixture/personal.csv'
        self.csv.parent.mkdir(parents=True)
        self.csv.write_text('context,config,annual\nES30,BASE,0\n')
        self.registry = self.root / 'agents/codex/terminal/result_sets.json'
        self.registry.parent.mkdir(parents=True)
        self.registry.write_text('{"sets":[]}')
        (self.scout / 'progress.json').write_text('{"status":"ready","lease":null,"hypotheses_started":4,"economic_definitions":10,"max_hypotheses":10,"max_economic_definitions":30}')

    def tearDown(self):
        self.temp.cleanup()

    def read(self):
        return desk.snapshot(self.root, [self.report], [self.csv])

    def test_budget_uses_saved_record_without_changing_it(self):
        before = (self.scout / 'progress.json').read_bytes()
        value = self.read()
        self.assertEqual(value['program']['economic_definitions'], 10)
        self.assertFalse(value['program']['lease_recorded'])
        self.assertEqual((self.scout / 'progress.json').read_bytes(), before)
        (self.scout / 'progress.json').write_text('{"economic_definitions":true,"max_hypotheses":"10"}')
        value = self.read()
        self.assertIsNone(value['program']['economic_definitions'])
        self.assertIsNone(value['program']['max_hypotheses'])

    def test_file_presence_is_not_an_independent_pass(self):
        (self.scout / 'records/1.json').write_text(json.dumps(dict(title='Paper', report_path='agents/codex/results/report.md',
            plan_path='../../etc/passwd', evidence_path=['bad'], full_text_read='true', independent_verification='pending')))
        record = self.read()['records'][0]
        self.assertIsNone(record['plan_path'])
        self.assertIsNone(record['evidence_path'])
        self.assertFalse(record['full_text_read'])
        self.assertEqual(record['independent_verification'], 'pending')
        self.assertNotIn('gate_pass', record)

    def test_corrupt_or_missing_state_is_visible_not_zero(self):
        (self.scout / 'progress.json').write_text('{bad')
        (self.scout / 'records/bad.json').write_text('[]')
        value = self.read()
        self.assertEqual(len(value['issues']), 2)
        self.assertIsNone(value['program']['economic_definitions'])
        self.assertEqual(value['records'], [])

    def test_registry_requires_source_and_explicit_schema(self):
        self.registry.write_text(json.dumps({'sets':[{'report_path':'live/trades/file.csv'}, {'report_path':'agents/codex/results/report.md'}]}))
        value = self.read()
        self.assertEqual(value['comparisons'], [])
        self.assertEqual(len(value['issues']), 2)

    def test_missing_result_is_not_substituted_with_another_account(self):
        original = json.loads((Path(__file__).parent / 'result_sets.json').read_text())['sets'][0]
        original.update(report_path='agents/codex/results/report.md', files={'personal':self.csv.relative_to(self.root).as_posix(), 'funded':'../../etc/passwd'})
        self.registry.write_text(json.dumps({'sets':[original]}))
        item = self.read()['comparisons'][0]
        self.assertEqual(list(item['files']), ['personal'])
        self.assertEqual(item['missing_files'], ['funded','evaluations'])


if __name__ == '__main__':
    unittest.main()
