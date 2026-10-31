"""Read-only artifact admission for the first design return command.

Checks immutable artifacts and a locally fetched claim snapshot. It does not fetch,
execute research, verify economic claims, or prove that the remote remains unchanged.
The workflow's remote reread and economic/source-review gates remain mandatory.
"""
import argparse
from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[3]
PROGRESS_PATH = 'agents/codex/research/scout/progress.json'
PROPOSAL_PREFIX = 'agents/codex/research/scout/proposals/'
PERMISSIONS = {'owned_upload', 'open_access', 'permitted_access'}


def git(root, *args):
    return subprocess.check_output(['git', *args], cwd=root, stderr=subprocess.DEVNULL)


def full_sha(value):
    return isinstance(value, str) and re.fullmatch(r'[0-9a-f]{40}', value) is not None


def nonempty(value):
    return isinstance(value, str) and bool(value.strip())


def committed(root, path, commit):
    relative = path.relative_to(root).as_posix()
    if git(root, 'show', commit + ':' + relative) != path.read_bytes():
        raise ValueError('Committed artifact differs: ' + relative)


def checked_path(root, relative, prefixes):
    if not isinstance(relative, str) or '\\' in relative:
        raise ValueError('Artifact path must be a canonical relative path')
    if any(part in {'', '.', '..'} for part in relative.split('/')):
        raise ValueError('Artifact path traversal or alias')
    path = (root / relative).resolve()
    if not path.is_relative_to(root):
        raise ValueError('Artifact outside admitted research paths')
    canonical = path.relative_to(root).as_posix()
    if canonical != relative or not any(canonical.startswith(p) for p in prefixes):
        raise ValueError('Artifact outside admitted research paths or symlink alias')
    if not path.is_file():
        raise ValueError('Missing artifact: ' + relative)
    return path


def read_object(path):
    value = json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(value, dict):
        raise ValueError('Expected a JSON object: ' + str(path))
    return value


def utc_time(value):
    if not isinstance(value, str):
        raise ValueError('Lease needs explicit UTC timestamps')
    try:
        parsed = datetime.fromisoformat(value.replace('Z', '+00:00'))
    except ValueError as error:
        raise ValueError('Invalid lease timestamp') from error
    if parsed.tzinfo is None or parsed.utcoffset() != timedelta(0):
        raise ValueError('Lease needs explicit UTC timestamps')
    return parsed


def validate_ledger(progress, allow_empty=False):
    if progress.get('program') != 'paper-scout-20261029':
        raise ValueError('Wrong research program')
    if not allow_empty and progress.get('status') not in {'ready', 'running'}:
        raise ValueError('Research program is not active')
    rows = progress.get('trials')
    if not isinstance(rows, list):
        raise ValueError('Trial ledger must be a list')
    by_run, by_family, definitions = {}, {}, set()
    economic = 0
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError('Invalid trial reservation')
        for field in ['hypothesis_id', 'run_id', 'source_id', 'proposal_path']:
            if not nonempty(row.get(field)):
                raise ValueError('Missing reservation ' + field)
        if re.fullmatch(r'[0-9a-f]{64}', str(row.get('proposal_sha256', ''))) is None:
            raise ValueError('Reservation must freeze the proposal SHA256')
        if row['run_id'] in by_run:
            raise ValueError('Duplicate reservation run_id')
        candidates, controls = row.get('candidate_variants'), row.get('control_variants')
        count = row.get('economic_definitions')
        if (type(candidates) is not int or type(controls) is not int or
                type(count) is not int or not 1 <= candidates <= 3 or
                not 0 <= controls <= 2 or count != candidates + controls or count > 5):
            raise ValueError('Invalid reservation counts')
        ids = row.get('definition_ids')
        if (not isinstance(ids, list) or len(ids) != count or
                not all(nonempty(item) for item in ids) or len(set(ids)) != count or
                definitions.intersection(ids)):
            raise ValueError('Economic definition IDs must be unique and complete')
        definitions.update(ids)
        by_run[row['run_id']] = row
        family = by_family.setdefault(row['hypothesis_id'], [0, 0])
        family[0] += candidates
        family[1] += controls
        if family[0] > 3 or family[1] > 2 or sum(family) > 5:
            raise ValueError('Per-hypothesis definition budget exceeded')
        economic += count
    hypotheses = len(by_family)
    if (type(progress.get('hypotheses_started')) is not int or
            type(progress.get('economic_definitions')) is not int or
            progress['hypotheses_started'] != hypotheses or
            progress['economic_definitions'] != economic or
            not (0 if allow_empty else 1) <= hypotheses <= 10 or
            not (0 if allow_empty else 1) <= economic <= 30):
        raise ValueError('Hypothesis/economic counters disagree with ledger or exceed budget')
    return by_run


def verify_ledger_history(root, current):
    """Earlier reservations may gain results/status, never lose/change definitions."""
    stable_fields = ['hypothesis_id', 'run_id', 'source_id', 'proposal_path',
                     'proposal_sha256', 'candidate_variants', 'control_variants',
                     'economic_definitions', 'definition_ids']
    seen, closed = {}, set()
    commits = git(root, 'log', '--format=%H', '--reverse', '--', PROGRESS_PATH).decode().splitlines()
    for commit in commits:
        record = json.loads(git(root, 'show', commit + ':' + PROGRESS_PATH))
        if record.get('program') != 'paper-scout-20261029':
            continue
        rows = validate_ledger(record, allow_empty=True)
        for key, row in rows.items():
            if key in closed and row.get('status') == 'reserved':
                raise ValueError('A completed/rejected reservation cannot reopen')
            if row.get('status') in {'design_reject', 'historical_pass', 'candidate',
                                     'closed', 'cancelled', 'dont_test'}:
                closed.add(key)
        immutable = {key: {field: row.get(field) for field in stable_fields}
                     for key, row in rows.items()}
        if any(immutable.get(key) != value for key, value in seen.items()):
            raise ValueError('Committed reservation history was removed or rewritten')
        seen = immutable
    immutable_current = {key: {field: row.get(field) for field in stable_fields}
                         for key, row in current.items()}
    if immutable_current != seen:
        raise ValueError('Current ledger differs from committed reservation history')


def confirm_local_claim(root, confirmed_claim, lease, proposal, now):
    if not full_sha(confirmed_claim):
        raise ValueError('A full --confirmed-claim commit is required')
    head = git(root, 'rev-parse', 'HEAD').decode().strip()
    remote = git(root, 'rev-parse', 'refs/remotes/origin/codex/work').decode().strip()
    if head != confirmed_claim or remote != confirmed_claim:
        raise ValueError('HEAD and fetched origin/codex/work must equal confirmed claim')
    fetch_path = Path(git(root, 'rev-parse', '--git-path', 'FETCH_HEAD').decode().strip())
    if not fetch_path.is_absolute():
        fetch_path = root / fetch_path
    fetched = fetch_path.read_text(encoding='utf-8').splitlines()
    if not any(line.startswith(confirmed_claim + '\t') and
               "branch 'codex/work' of " in line for line in fetched):
        raise ValueError('FETCH_HEAD does not contain the confirmed codex/work claim')
    if not isinstance(lease, dict):
        raise ValueError('Active committed lease required')
    if (lease.get('run_id') != proposal.get('run_id') or
            lease.get('owner') != proposal.get('lease_owner') or
            not nonempty(lease.get('owner'))):
        raise ValueError('Lease run/owner differs from proposal')
    claimed, expires = utc_time(lease.get('claimed_at')), utc_time(lease.get('expires_at'))
    if not claimed <= now < expires or not timedelta(0) < expires - claimed <= timedelta(hours=2):
        raise ValueError('Lease is expired, future-dated or exceeds two hours')
    checked_parent = lease.get('checked_parent')
    if not full_sha(checked_parent) or checked_parent == confirmed_claim:
        raise ValueError('Lease needs its previously checked remote parent')
    git(root, 'merge-base', '--is-ancestor', checked_parent, confirmed_claim)


def hashed_input(root, item, prefixes):
    if not isinstance(item, dict):
        raise ValueError('Invalid input/source record')
    path = checked_path(root, item.get('path'), prefixes)
    digest = item.get('sha256')
    if not isinstance(digest, str) or re.fullmatch(r'[0-9a-f]{64}', digest) is None:
        raise ValueError('A full SHA256 is required')
    if hashlib.sha256(path.read_bytes()).hexdigest() != digest:
        raise ValueError('Input/source hash differs')
    if item.get('permission') not in PERMISSIONS or not nonempty(item.get('provenance')):
        raise ValueError('Input/source permission and provenance must be declared')
    return path


def check(envelope, root=ROOT, confirmed_claim=None, now=None):
    root = Path(root).resolve()
    now = now or datetime.now(timezone.utc)
    if not isinstance(envelope, dict) or set(envelope) != {'preregistration_commit', 'proposal_path'}:
        raise ValueError('Use an envelope with preregistration_commit and proposal_path only')
    if git(root, 'branch', '--show-current').decode().strip() != 'codex/work':
        raise ValueError('Research must run on codex/work')
    commit = envelope.get('preregistration_commit')
    if not full_sha(commit):
        raise ValueError('Use a full committed preregistration SHA')
    git(root, 'merge-base', '--is-ancestor', commit, 'HEAD')
    proposal_path = checked_path(root, envelope.get('proposal_path'), [PROPOSAL_PREFIX])
    committed(root, proposal_path, commit)
    proposal = read_object(proposal_path)
    if 'preregistration_commit' in proposal:
        raise ValueError('Commit SHA belongs in the envelope, not the immutable body')
    for field in ['hypothesis_id', 'run_id', 'lease_owner', 'source_id']:
        if not nonempty(proposal.get(field)):
            raise ValueError('Missing proposal ' + field)
    if re.fullmatch(r'ssrn:[0-9]+', proposal['source_id']) is None:
        raise ValueError('Use an explicit SSRN source ID')
    codes = proposal.get('code_paths')
    if (not isinstance(codes, list) or not codes or
            not all(nonempty(item) for item in codes) or len(set(codes)) != len(codes)):
        raise ValueError('Frozen implementation paths required')
    frozen = proposal.get('artifact_sha256')
    expected_paths = [proposal.get(key) for key in ['review_record', 'evidence_path', 'plan_path']] + codes
    if (not all(nonempty(path) for path in expected_paths) or not isinstance(frozen, dict) or
            set(frozen) != set(expected_paths)):
        raise ValueError('Freeze every review/evidence/plan/code artifact SHA256 in the proposal')
    for relative, digest in frozen.items():
        artifact = checked_path(root, relative, ['agents/codex/research/scout/records/',
                                                'agents/codex/evidence/', 'agents/codex/plans/',
                                                'analysis/codex_'])
        if not isinstance(digest, str) or re.fullmatch(r'[0-9a-f]{64}', digest) is None:
            raise ValueError('Invalid frozen artifact SHA256')
        if hashlib.sha256(artifact.read_bytes()).hexdigest() != digest:
            raise ValueError('Frozen artifact hash differs: ' + relative)

    progress_path = checked_path(root, PROGRESS_PATH, ['agents/codex/research/scout/'])
    progress = read_object(progress_path)
    confirm_local_claim(root, confirmed_claim, progress.get('lease'), proposal, now)
    committed(root, progress_path, confirmed_claim)
    reservations = validate_ledger(progress)
    verify_ledger_history(root, reservations)
    prior_progress = json.loads(git(root, 'show', commit + ':' + PROGRESS_PATH))
    prior_reservations = validate_ledger(prior_progress)
    reservation = reservations.get(proposal['run_id'])
    if reservation is None or prior_reservations.get(proposal['run_id']) != reservation:
        raise ValueError('Matching preregistered budget reservation required')
    for field in ['hypothesis_id', 'source_id', 'candidate_variants', 'control_variants', 'definition_ids']:
        if reservation.get(field) != proposal.get(field):
            raise ValueError('Reservation association differs: ' + field)
    if reservation.get('proposal_path') != envelope['proposal_path'] or reservation.get('status') != 'reserved':
        raise ValueError('Reservation is not this pending first-design proposal')
    if hashlib.sha256(proposal_path.read_bytes()).hexdigest() != reservation['proposal_sha256']:
        raise ValueError('Proposal differs from its original budget reservation')
    if proposal.get('phase') != 'design':
        raise ValueError('Only first design returns are covered; later gates remain binding')
    if proposal.get('design_start') != '2018-01-01' or proposal.get('design_end') != '2022-12-31':
        raise ValueError('First design must remain 2018–22')

    record_path = checked_path(root, proposal.get('review_record'), ['agents/codex/research/scout/records/'])
    committed(root, record_path, commit)
    review = read_object(record_path)
    for field, expected in [('id', proposal['source_id']), ('hypothesis_id', proposal['hypothesis_id']),
                            ('evidence_path', proposal.get('evidence_path')), ('plan_path', proposal.get('plan_path'))]:
        if review.get(field) != expected:
            raise ValueError('Source review association differs: ' + field)
    if (review.get('full_text_read') is not True or
            review.get('evidence_level') not in {'source_review', 'independently_reproduced'}):
        raise ValueError('Metadata/abstract-only records cannot authorize returns')
    if review.get('return_eligibility') != 'TEST' or review.get('verdict') not in {
            'review_pending', 'historical_pass', 'candidate'}:
        raise ValueError('Source review is not eligible for this return test')
    for field in ['about', 'findings', 'mechanism', 'build_on']:
        if not nonempty(review.get(field)):
            raise ValueError('Four-question review missing')
    source = review.get('source_artifact')
    hashed_input(root, source, ['papers/', 'agents/codex/inputs/'])
    if not nonempty(source.get('version')) or not nonempty(source.get('access_method')):
        raise ValueError('Source version and access method required')
    evidence = checked_path(root, proposal.get('evidence_path'), ['agents/codex/evidence/'])
    plan = checked_path(root, proposal.get('plan_path'), ['agents/codex/plans/'])
    for path in [evidence, plan]:
        committed(root, path, commit)
    lines = evidence.read_text(encoding='utf-8').splitlines()
    if not lines or re.fullmatch(r'#+ .+: TEST\s*', lines[0]) is None:
        raise ValueError('Evidence sheet has not reached exact TEST disposition')

    for relative in codes:
        path = checked_path(root, relative, ['analysis/codex_'])
        if path.suffix != '.py' or path.parent != root / 'analysis':
            raise ValueError('Expected analysis/codex_*.py research source')
        committed(root, path, commit)
    inputs = proposal.get('inputs')
    if not isinstance(inputs, list) or not inputs:
        raise ValueError('Hashed owned/permitted inputs required')
    for item in inputs:
        hashed_input(root, item, ['data/', 'agents/codex/inputs/', 'analysis/outputs/codex_'])
    for field in ['information_clock', 'native_costs', 'entry_exit_rule', 'gross_stop_rule', 'data_failure_stop_rule']:
        if not nonempty(proposal.get(field)):
            raise ValueError('Missing frozen ' + field)
    return {'admitted': True, 'phase': 'design', 'hypothesis_id': proposal['hypothesis_id'],
            'run_id': proposal['run_id'], 'definitions_reserved': reservation['economic_definitions'],
            'preregistration_commit': commit, 'confirmed_claim_snapshot': confirmed_claim,
            'note': 'Artifact admission only; remote snapshot may change. No execution, economic/source truth, '
                    'implementation parity or later gate is certified; reread the remote claim before returns.'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['check'])
    parser.add_argument('envelope')
    parser.add_argument('--confirmed-claim', required=True)
    args = parser.parse_args()
    try:
        print(json.dumps(check(read_object(Path(args.envelope)), confirmed_claim=args.confirmed_claim), indent=2))
    except (ValueError, OSError, KeyError, TypeError, AttributeError, subprocess.CalledProcessError) as error:
        print(json.dumps({'admitted': False, 'error': str(error)}))
        raise SystemExit(2)
