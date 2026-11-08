#!/usr/bin/env python3
"""Offline acquisition-integrity checks; exercises no strategy or network."""
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import urllib.parse
from unittest.mock import patch

SCRIPT = Path(__file__).with_name('codex_new_data_20261108.py')
spec = importlib.util.spec_from_file_location('intake', SCRIPT)
intake = importlib.util.module_from_spec(spec)
spec.loader.exec_module(intake)


def main():
    passed = []
    with tempfile.TemporaryDirectory(prefix='codex_data_check_') as name:
        root = Path(name)
        reproduced = root / 'reproduced'
        result = intake.audit(intake.PACKAGE, reproduced)
        reference = intake.PACKAGE / 'audit'
        paths = sorted(p.relative_to(reference) for p in reference.rglob('*.csv'))
        if not paths or any((reference / p).read_bytes() != (reproduced / p).read_bytes() for p in paths):
            raise AssertionError('Normalized CSV reproduction differs')
        passed.append('All saved normalized/quarantine CSVs reproduce byte-for-byte from verified sources')
        assert result['source_files'] == 49 and result['trials_run'] == 0
        boil = next(r for r in result['funds'] if r['ticker'] == 'BOIL')
        assert boil['status'].startswith('QUARANTINED')
        assert boil['identity_errors_above_1pct'] == 1178 and boil['nonpositive_rows'] == 82
        passed.append('Real BOIL failures remain quarantined; no rows filled or reconstructed')

        corrupted = root / 'corrupted'
        corrupted.mkdir()
        manifest = json.loads((intake.PACKAGE / 'secondary_sources.json').read_text())
        intake.dump(corrupted / 'secondary_sources.json', manifest)
        first = manifest['files'][0]
        file = corrupted / first['local_path']
        file.parent.mkdir(parents=True)
        file.write_bytes((intake.PACKAGE / first['local_path']).read_bytes() + b'x')
        try:
            intake.audit(corrupted, root / 'should_not_admit')
        except ValueError as error:
            assert 'Changed source blob' in str(error)
        else:
            raise AssertionError('Corrupt source accepted')
        passed.append('Changed source bytes are rejected before normalization')

        for raw, kind in [(b'<html>blocked</html>', 'nav_csv'),
                          (b'{"error":"forbidden"}', 'json_data'),
                          (b'{"refRates":[]}', 'json_data'),
                          (b'{"data":[],"meta":{}}', 'fiscal_json')]:
            try:
                intake.payload_info(raw, kind)
            except ValueError:
                pass
            else:
                raise AssertionError('Invalid/empty data payload accepted')
        passed.append('HTML, API errors and empty data are rejected')

        jobs = {'files': [
            {'id': 'blocked', 'group': 'test', 'url': 'https://example.invalid/block',
             'file': 'blocked.csv', 'kind': 'nav_csv'},
            {'id': 'paged', 'group': 'test', 'url': 'https://example.invalid/table?format=json',
             'file': 'paged.json', 'kind': 'fiscal_json'}]}
        intake.dump(root / 'jobs.json', jobs)
        called = []

        def simulated_fetch(url, timeout):
            called.append(url)
            if '/block' in url:
                return b'<html>denied</html>', {}, url
            page = int(urllib.parse.parse_qs(urllib.parse.urlparse(url).query)['page[number]'][0])
            raw = json.dumps({'data': [{'id': 2 * page - 1}, {'id': 2 * page}],
                              'meta': {'total-pages': 2, 'total-count': 4}}).encode()
            return raw, {'Content-Type': 'application/json'}, url

        with patch.object(intake, 'read_url', simulated_fetch), contextlib.redirect_stdout(io.StringIO()):
            counts = intake.fetch_primary(root / 'jobs.json', root / 'fetch', 1, None)
        assert counts == {'downloaded': 2, 'failed': 1} and len(called) == 3
        receipt = json.loads((root / 'fetch/acquisition_receipt.json').read_text())
        assert receipt['requests'][0]['status'] == 'FAILED'
        assert (root / 'fetch/rejected/blocked.csv').exists()
        assert not (root / 'fetch/raw/blocked.csv').exists()
        rows = [r for p in sorted((root / 'fetch/raw').glob('paged_page*.json'))
                for r in json.loads(p.read_text())['data']]
        assert [r['id'] for r in rows] == [1, 2, 3, 4]
        passed.append('Complete pagination and partial-failure receipts; rejected HTML cannot masquerade as a CSV')

        command = subprocess.run([sys.executable, str(SCRIPT), 'audit', '--output', str(reproduced)],
                                 capture_output=True, text=True)
        assert command.returncode != 0 and 'FileExistsError' in command.stderr
        passed.append('CLI refuses an existing output directory')

    print(json.dumps({'status': 'PASS', 'checks': passed, 'network_requests': 0, 'strategy_trials': 0}, indent=2))


if __name__ == '__main__':
    main()
