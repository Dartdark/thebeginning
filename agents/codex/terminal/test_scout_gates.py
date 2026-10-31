import copy
from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
import scout_gates


class Gates(unittest.TestCase):
    """Disconnected synthetic artifacts only; no strategy code or market test runs."""

    def setUp(self):
        self.build_fixture()

    def rebuild(self, **changes):
        self.tmp.cleanup()
        self.build_fixture(**changes)

    def build_fixture(self, proposal_changes=None, review_changes=None, evidence_text=None):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.now = datetime(2026, 10, 29, 12, tzinfo=timezone.utc)
        self.git('init', '-b', 'codex/work')
        self.put('baseline.txt', 'synthetic baseline')
        self.commit()
        parent = self.git('rev-parse', 'HEAD')
        self.record_path = 'agents/codex/research/scout/records/1234567.json'
        self.proposal_path = 'agents/codex/research/scout/proposals/fixture.json'
        self.put('agents/codex/evidence/test.md', '# Fixture: TEST\n' if evidence_text is None else evidence_text)
        self.put('agents/codex/plans/test.md', '# Frozen synthetic fixture\n')
        self.put('analysis/codex_synthetic_fixture.py', '# No market execution\n')
        self.put('data/fixture.txt', 'synthetic,not-market-data')
        self.put('agents/codex/inputs/source.txt', 'synthetic source fixture')
        self.proposal = dict(
            hypothesis_id='h1', run_id='r1', lease_owner='fixture-owner', source_id='ssrn:1234567',
            candidate_variants=1, control_variants=1, definition_ids=['h1-c1', 'h1-b1'],
            phase='design', design_start='2018-01-01', design_end='2022-12-31',
            review_record=self.record_path, evidence_path='agents/codex/evidence/test.md',
            plan_path='agents/codex/plans/test.md', code_paths=['analysis/codex_synthetic_fixture.py'],
            inputs=[self.input_record('data/fixture.txt')], information_clock='Known before decision',
            native_costs='Frozen fixture costs', entry_exit_rule='Fixture only',
            gross_stop_rule='Frozen', data_failure_stop_rule='Stop')
        self.proposal.update(proposal_changes or {})
        self.review = dict(
            id='ssrn:1234567', hypothesis_id='h1', evidence_path=self.proposal['evidence_path'],
            plan_path=self.proposal['plan_path'], full_text_read=True, evidence_level='source_review',
            return_eligibility='TEST', verdict='review_pending', about='a', findings='f',
            mechanism='m', build_on='b', source_artifact=dict(
                **self.input_record('agents/codex/inputs/source.txt'),
                version='synthetic v1', access_method='disconnected fixture'))
        self.review.update(review_changes or {})
        self.put(self.record_path, self.review)
        paths = [self.proposal[key] for key in ['review_record', 'evidence_path', 'plan_path']] + self.proposal['code_paths']
        self.proposal['artifact_sha256'] = {
            path: hashlib.sha256((self.root/path).read_bytes()).hexdigest() for path in paths}
        self.progress = dict(
            program='paper-scout-20261029', status='running', hypotheses_started=1,
            economic_definitions=2, lease=dict(
                run_id='r1', owner='fixture-owner', checked_parent=parent,
                claimed_at=(self.now-timedelta(minutes=10)).isoformat(),
                expires_at=(self.now+timedelta(minutes=50)).isoformat()),
            trials=[dict(hypothesis_id='h1', run_id='r1', source_id='ssrn:1234567',
                         proposal_path=self.proposal_path, candidate_variants=1, control_variants=1,
                         economic_definitions=2, definition_ids=['h1-c1', 'h1-b1'], status='reserved')])
        self.freeze()

    def tearDown(self):
        self.tmp.cleanup()

    def put(self, relative, value):
        path = self.root/relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value, sort_keys=True) if isinstance(value, (dict, list)) else value,
                        encoding='utf-8')

    def input_record(self, relative):
        return dict(path=relative, sha256=hashlib.sha256((self.root/relative).read_bytes()).hexdigest(),
                    permission='owned_upload', provenance='disconnected synthetic fixture')

    def git(self, *args):
        return subprocess.check_output(['git', *args], cwd=self.root, text=True,
                                       stderr=subprocess.DEVNULL).strip()

    def commit(self):
        self.git('add', '.')
        self.git('-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.invalid',
                 'commit', '--allow-empty', '-m', 'Disconnected fixture')

    def proof(self):
        self.claim = self.git('rev-parse', 'HEAD')
        self.git('update-ref', 'refs/remotes/origin/codex/work', self.claim)
        fetch = Path(self.git('rev-parse', '--git-path', 'FETCH_HEAD'))
        if not fetch.is_absolute():
            fetch = self.root/fetch
        # Synthetic local proof fixture, not an actual remote synchronization claim.
        fetch.write_text(self.claim + "\t\tbranch 'codex/work' of fixture\n", encoding='utf-8')

    def freeze(self, preregister=True, rehash=True):
        self.put(self.proposal_path, self.proposal)
        if rehash:
            self.progress['trials'][0]['proposal_sha256'] = hashlib.sha256(
                (self.root/self.proposal_path).read_bytes()).hexdigest()
        self.put(self.record_path, self.review)
        self.put(scout_gates.PROGRESS_PATH, self.progress)
        self.commit()
        self.proof()
        if preregister:
            self.envelope = dict(preregistration_commit=self.claim, proposal_path=self.proposal_path)

    def admit(self):
        return scout_gates.check(self.envelope, self.root, confirmed_claim=self.claim, now=self.now)

    def test_committed_fixture_admitted_without_execution(self):
        result = self.admit()
        self.assertTrue(result['admitted'])
        self.assertEqual(result['definitions_reserved'], 2)
        self.assertIn('remote snapshot may change', result['note'])

    def test_uncommitted_hash_update_cannot_repair_input_revision(self):
        self.put('data/fixture.txt', 'revised synthetic data')
        with self.assertRaisesRegex(ValueError, 'hash'):
            self.admit()
        self.proposal['inputs'][0] = self.input_record('data/fixture.txt')
        self.put(self.proposal_path, self.proposal)
        with self.assertRaisesRegex(ValueError, 'Committed artifact differs'):
            self.admit()

    def test_committed_protocol_cannot_reuse_old_reservation(self):
        self.proposal['native_costs'] = 'different after registration'
        self.freeze(rehash=False)
        with self.assertRaisesRegex(ValueError, 'original budget reservation'):
            self.admit()

    def test_rewriting_reservation_hash_does_not_erase_history(self):
        self.proposal['native_costs'] = 'changed protocol'
        self.freeze()
        with self.assertRaisesRegex(ValueError, 'history'):
            self.admit()

    def test_later_commit_cannot_rebind_frozen_implementation(self):
        self.put(self.proposal['code_paths'][0], '# changed synthetic implementation\n')
        self.freeze()
        with self.assertRaisesRegex(ValueError, 'Frozen artifact hash differs'):
            self.admit()
        code = self.proposal['code_paths'][0]
        self.proposal['artifact_sha256'][code] = hashlib.sha256((self.root/code).read_bytes()).hexdigest()
        self.freeze()
        with self.assertRaisesRegex(ValueError, 'history'):
            self.admit()

    def test_rejected_reservation_cannot_return_to_reserved(self):
        self.progress['trials'][0]['status'] = 'design_reject'
        self.freeze()
        self.progress['trials'][0]['status'] = 'reserved'
        self.freeze()
        with self.assertRaisesRegex(ValueError, 'cannot reopen'):
            self.admit()

    def test_uncommitted_plan_and_progress_fail(self):
        self.put(self.proposal['plan_path'], 'changed')
        with self.assertRaisesRegex(ValueError, 'Frozen artifact hash differs'):
            self.admit()
        self.put(self.proposal['plan_path'], '# Frozen synthetic fixture\n')
        self.progress['economic_definitions'] = 1
        self.put(scout_gates.PROGRESS_PATH, self.progress)
        with self.assertRaisesRegex(ValueError, 'Committed artifact differs'):
            self.admit()

    def test_envelope_overrides_and_missing_remote_proof_fail(self):
        self.envelope['native_costs'] = 'outside immutable body'
        with self.assertRaisesRegex(ValueError, 'envelope'):
            self.admit()
        del self.envelope['native_costs']
        self.git('update-ref', 'refs/remotes/origin/codex/work', self.progress['lease']['checked_parent'])
        with self.assertRaisesRegex(ValueError, 'fetched origin'):
            self.admit()

    def test_fetch_head_must_name_the_branch(self):
        fetch = self.root/self.git('rev-parse', '--git-path', 'FETCH_HEAD')
        fetch.write_text(self.claim + "\t\tbranch 'other' of fixture\n", encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'FETCH_HEAD'):
            self.admit()

    def test_wrong_branch_fails(self):
        self.git('checkout', '-b', 'fixture-unapproved')
        with self.assertRaisesRegex(ValueError, 'codex/work'):
            self.admit()

    def test_absent_foreign_expired_and_invalid_leases_fail(self):
        valid = copy.deepcopy(self.progress['lease'])
        variants = [None, dict(valid, owner='someone-else'), dict(valid, run_id='r2'),
                    dict(valid, expires_at=(self.now-timedelta(seconds=1)).isoformat()),
                    dict(valid, claimed_at=(self.now+timedelta(seconds=1)).isoformat()),
                    dict(valid, expires_at=(self.now+timedelta(hours=3)).isoformat()),
                    dict(valid, expires_at='2026-10-29T12:50:00'),
                    dict(valid, checked_parent='not-a-sha')]
        for lease in variants:
            with self.subTest(lease=lease):
                self.progress['lease'] = lease
                self.freeze()
                with self.assertRaises(ValueError):
                    self.admit()

    def test_counters_must_be_real_integers_and_derived(self):
        valid = copy.deepcopy(self.progress)
        for field, value in [('hypotheses_started', True), ('economic_definitions', -1),
                             ('hypotheses_started', 2), ('economic_definitions', 3)]:
            with self.subTest(field=field, value=value):
                self.progress = copy.deepcopy(valid)
                self.progress[field] = value
                self.freeze()
                with self.assertRaisesRegex(ValueError, 'counters'):
                    self.admit()

    def test_invalid_duplicate_and_reused_reservations_fail(self):
        valid = copy.deepcopy(self.progress)
        mutations = [
            lambda row: row.update(economic_definitions=-2),
            lambda row: row.update(candidate_variants=True),
            lambda row: row.update(definition_ids=['same', 'same']),
            lambda row: row.update(source_id='ssrn:7654321')]
        for mutate in mutations:
            with self.subTest(mutation=mutate):
                self.progress = copy.deepcopy(valid)
                mutate(self.progress['trials'][0])
                self.freeze()
                with self.assertRaises(ValueError):
                    self.admit()

    def extra_reservation(self, family, run, count=1):
        return dict(hypothesis_id=family, run_id=run, source_id='ssrn:7654321',
                    proposal_path='agents/codex/research/scout/proposals/other.json',
                    proposal_sha256='a'*64, candidate_variants=count, control_variants=0,
                    economic_definitions=count, definition_ids=[run+'-'+str(i) for i in range(count)],
                    status='reserved')

    def test_family_budget_accumulates_across_runs(self):
        self.progress['trials'].append(self.extra_reservation('h1', 'r2', count=3))
        self.progress['economic_definitions'] = 5
        self.freeze()
        with self.assertRaisesRegex(ValueError, 'Per-hypothesis'):
            self.admit()

    def test_actual_family_count_exceeding_ten_fails(self):
        for i in range(2, 12):
            self.progress['trials'].append(self.extra_reservation('h'+str(i), 'r'+str(i)))
        self.progress.update(hypotheses_started=11, economic_definitions=12)
        self.freeze()
        with self.assertRaisesRegex(ValueError, 'budget'):
            self.admit()

    def test_removed_prior_reservation_fails(self):
        self.progress['trials'].append(self.extra_reservation('h2', 'r2'))
        self.progress.update(hypotheses_started=2, economic_definitions=3)
        self.freeze()
        self.progress['trials'].pop()
        self.progress.update(hypotheses_started=1, economic_definitions=2)
        self.freeze(preregister=False)
        with self.assertRaisesRegex(ValueError, 'history'):
            self.admit()

    def test_source_requires_full_read_eligibility_and_matching_identity(self):
        changes = [('full_text_read', False), ('return_eligibility', 'NEEDS DATA'),
                   ('id', 'ssrn:7654321'), ('hypothesis_id', 'other'),
                   ('plan_path', 'agents/codex/plans/other.md'), ('verdict', 'dont_test'),
                   ('verdict', 'invented-disposition')]
        for field, value in changes:
            with self.subTest(field=field):
                self.rebuild(review_changes={field: value})
                with self.assertRaises(ValueError):
                    self.admit()

    def test_full_source_bytes_and_permission_are_checked(self):
        self.put('agents/codex/inputs/source.txt', 'revised source')
        with self.assertRaisesRegex(ValueError, 'hash'):
            self.admit()

    def test_source_hash_is_not_optional(self):
        source = copy.deepcopy(self.review['source_artifact'])
        del source['sha256']
        self.rebuild(review_changes={'source_artifact': source})
        with self.assertRaisesRegex(ValueError, 'SHA256'):
            self.admit()

    def test_source_permission_is_not_inferred_from_a_hash(self):
        source = copy.deepcopy(self.review['source_artifact'])
        source['permission'] = 'not-established'
        self.rebuild(review_changes={'source_artifact': source})
        with self.assertRaisesRegex(ValueError, 'permission'):
            self.admit()

    def test_evidence_disposition_is_exact(self):
        for header in ['# Fixture: TESTING\n', '# Fixture: TEST / NEEDS DATA\n', '']:
            with self.subTest(header=header):
                self.rebuild(evidence_text=header)
                with self.assertRaisesRegex(ValueError, 'exact TEST'):
                    self.admit()

    def test_paths_reject_traversal_and_symlinks(self):
        self.put('outside.md', '# Fixture: TEST\n')
        self.put('outside.py', '# disconnected fixture\n')
        self.put('analysis/codex_container/dummy.txt', 'fixture')
        for path in ['agents/codex/evidence/../../../outside.md',
                     'analysis/codex_container/../../outside.py']:
            with self.subTest(path=path):
                with self.assertRaisesRegex(ValueError, 'traversal'):
                    scout_gates.checked_path(self.root, path, ['agents/codex/evidence/', 'analysis/codex_'])
        alias = self.root/'analysis/codex_alias.py'
        alias.symlink_to('../outside.py')
        with self.assertRaisesRegex(ValueError, 'symlink'):
            scout_gates.checked_path(self.root, 'analysis/codex_alias.py', ['analysis/codex_'])

    def test_date_and_cost_gates_remain_binding(self):
        for changes, message in [({'design_end': '2026-12-31'}, '2018'),
                                 ({'native_costs': ''}, 'native_costs')]:
            with self.subTest(changes=changes):
                self.rebuild(proposal_changes=changes)
                with self.assertRaisesRegex(ValueError, message):
                    self.admit()


if __name__ == '__main__':
    unittest.main()
