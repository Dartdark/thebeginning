"""Read-only presentation of saved research. File presence never certifies a gate."""
from datetime import datetime, timezone
import json


def snapshot(root, documents, results):
    allowed = {p.relative_to(root).as_posix() for p in documents}
    csvs = {p.relative_to(root).as_posix() for p in results}
    issues = []

    def read(path):
        try:
            value = json.loads((root / path).read_text(encoding='utf-8'))
            if not isinstance(value, dict):
                raise ValueError('Expected an object')
            return value
        except (OSError, ValueError):
            issues.append(f'Could not read {path}. Its status is unknown.')
            return {}

    def text(value):
        return value[:6000] if isinstance(value, str) else ''

    records = []
    directory = root / 'agents/codex/research/scout'
    for path in sorted((directory / 'records').glob('*.json')):
        value = read(path.relative_to(root))
        if not value:
            continue
        record = {key: text(value.get(key)) for key in (
            'id', 'ssrn_id', 'title', 'summary', 'verdict', 'updated_at', 'about',
            'findings', 'mechanism', 'build_on', 'code_feasibility', 'evidence_level',
            'return_eligibility', 'source_revision', 'independent_verification')}
        record['full_text_read'] = value.get('full_text_read') is True
        record['record_path'] = path.relative_to(root).as_posix()
        # Only documents already admitted by the terminal can open in its reader.
        for key in ('report_path', 'evidence_path', 'plan_path'):
            path_value = value.get(key)
            record[key] = path_value if isinstance(path_value, str) and path_value in allowed else None
        records.append(record)
    records.sort(key=lambda row: row['updated_at'], reverse=True)
    progress = read(directory.relative_to(root) / 'progress.json')
    program = {'status': text(progress.get('status')),
               'lease_recorded': bool(progress['lease']) if 'lease' in progress else None}
    for key in ('hypotheses_started', 'economic_definitions', 'max_hypotheses', 'max_economic_definitions'):
        value = progress.get(key)
        program[key] = value if type(value) is int and value >= 0 else None

    registry = read('agents/codex/terminal/result_sets.json')
    sets = []
    seen = set()
    for item in registry.get('sets', []) if isinstance(registry.get('sets'), list) else []:
        if not isinstance(item, dict) or not isinstance(item.get('report_path'), str) or item['report_path'] not in allowed:
            issues.append('A comparison has no readable source report; it is not displayed.')
            continue
        item = dict(item)
        required = ('id', 'title', 'sample', 'sizing', 'costs', 'method', 'outcome', 'verification', 'limits', 'comparison_note')
        mapping = item.get('configurations')
        contexts = item.get('contexts')
        if (any(not isinstance(item.get(key), str) or not item[key] for key in required)
                or item.get('schema') != 'primesync_accounts_v1'
                or not isinstance(mapping, dict)
                or any(not isinstance(mapping.get(key), str) or not mapping[key] for key in ('BASE', 'ADD', 'REPLACE', 'EMPTY'))
                or len({mapping[key] for key in ('BASE', 'ADD', 'REPLACE', 'EMPTY')}) != 4
                or not isinstance(contexts, list) or not contexts
                or any(not isinstance(value, str) or not value for value in contexts)
                or len(set(contexts)) != len(contexts)
                or item['id'] in seen):
            issues.append('A comparison has an unsupported or incomplete schema; inspect the registry and raw outputs.')
            continue
        seen.add(item['id'])
        item['plan_path'] = item.get('plan_path') if isinstance(item.get('plan_path'), str) and item['plan_path'] in allowed else None
        files = item.get('files', {})
        item['files'] = {key: path for key, path in files.items() if isinstance(path, str) and path in csvs} if isinstance(files, dict) else {}
        item['missing_files'] = [key for key in ('personal', 'funded', 'evaluations') if key not in item['files']]
        sets.append(item)
    return dict(records=records, program=program, comparisons=sets, issues=issues,
                loaded_at=datetime.now(timezone.utc).isoformat())
