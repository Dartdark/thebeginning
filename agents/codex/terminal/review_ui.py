"""Read-only browser acceptance review; optional Playwright + local Chromium, no return work.

Run from any directory: python agents/codex/terminal/review_ui.py --output /tmp/terminal-ui-review
A temporary local HTTP server and isolated runtime are closed on completion. No discovery POSTs.
"""
import argparse
import csv
from decimal import Decimal, ROUND_HALF_UP
import hashlib
import json
from pathlib import Path
import platform
import shutil
import subprocess
import tempfile
import threading
from datetime import datetime, timezone
from playwright.sync_api import sync_playwright
import server


def run(output):
    output.mkdir(parents=True, exist_ok=True)
    assertions = []
    errors = []
    def check(condition, description):
        if not condition:
            raise AssertionError(description)
        assertions.append(description)

    with tempfile.TemporaryDirectory() as runtime:
        original = server.RUNTIME
        server.RUNTIME = Path(runtime)
        http = server.ThreadingHTTPServer(('127.0.0.1', 0), server.Handler)
        thread = threading.Thread(target=http.serve_forever, daemon=True)
        thread.start()
        base = f'http://127.0.0.1:{http.server_port}'
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(executable_path=shutil.which('chromium'), headless=True, args=['--no-sandbox'])
                page = browser.new_page(viewport={'width':1440, 'height':1100})
                page.on('pageerror', lambda error: errors.append(str(error)))
                page.goto(base)
                page.get_by_role('heading', name='Research overview', exact=True).wait_for()
                page.keyboard.press('Tab')
                check(page.locator('.skip-link').evaluate('(el)=>el===document.activeElement'), 'Keyboard begins at skip link')
                page.keyboard.press('Enter')
                check(page.locator('#main').evaluate('(el)=>el===document.activeElement'), 'Skip link focuses main content')
                check('not connected' in page.locator('.desk-snapshot').inner_text(), 'Overview makes local-only snapshot explicit')
                page.screenshot(path=str(output/'overview-desktop.png'), full_page=True)
                page.goto(base+'/#results')
                page.locator('.comparison-table').wait_for()
                page.locator('.skip-link').focus()
                page.keyboard.press('Enter')
                check(page.locator('#main h1').inner_text()=='Strategy results', 'Skip link preserves the active page')
                registry = json.loads((Path(__file__).parent/'result_sets.json').read_text())['sets'][0]
                fields = {'personal':['annual','dd95','capital','return_dd','sharpe'],
                          'funded':['year1','year2','blown','days6','delta_year1','lo','hi'],
                          'evaluations':['pass_rate','starts']}
                originals = {kind:list(csv.DictReader((server.ROOT/path).open())) for kind,path in registry['files'].items()}
                configs = ['BASE','ADD','REPLACE_VB','EMPTY_VB']
                cells = 0
                for home in ['personal','funded-50','funded-150','evaluations-50','evaluations-150']:
                    kind = home.split('-')[0]
                    page.locator('#comparison-home').select_option(home)
                    for context in registry['contexts']:
                        page.locator('#comparison-context').select_option(context)
                        for cohort in ['all','recent'] if kind=='evaluations' else ['all']:
                            if kind=='evaluations':page.locator('#comparison-cohort').select_option(cohort)
                            page.locator('.comparison-table').wait_for()
                            for column,config in enumerate(configs):
                                source = [r for r in originals[kind] if r['context']==context and r['config']==config and
                                          (kind=='personal' or r['account']==home.split('-')[1]) and
                                          (kind!='evaluations' or r['cohort']==cohort)]
                                check(len(source)==1, f'Unique saved row: {home}/{context}/{cohort}/{config}')
                                for row_index,key in enumerate(fields[kind]):
                                    value = source[0][key]
                                    # Browser Intl formatting is deterministic here; compare to the raw source value, not recomputed returns.
                                    actual = page.locator('.comparison-table tbody tr').nth(row_index).locator('td').nth(column).inner_text()
                                    n = float(value)
                                    if key in ['blown','pass_rate']:expected=f'{100*n:.2f}%'
                                    elif key in ['return_dd','sharpe']:expected=f'{n:.3f}'
                                    elif key in ['days6','starts']:expected=f'{n:,.0f}'
                                    else:expected=('-' if n<0 else '')+'$'+format(abs(Decimal(value)).quantize(Decimal('1'),rounding=ROUND_HALF_UP),',f')
                                    check(actual==expected, f'CSV parity: {home}/{context}/{cohort}/{config}/{key} ({actual} vs {expected})')
                                    cells += 1
                page.locator('#comparison-home').select_option('funded-150')
                page.locator('#comparison-context').select_option('ES30')
                page.locator('.comparison-table').wait_for()
                page.screenshot(path=str(output/'results-desktop.png'), full_page=True)
                page.get_by_role('button', name='Read full report', exact=True).click()
                page.get_by_role('dialog').wait_for()
                check('PrimeSync' in page.locator('#reader-title').inner_text(), 'Source report opens in labeled document reader')
                page.keyboard.press('Escape')
                check(not page.locator('#reader').is_visible(), 'Document reader closes with Escape')
                page.get_by_role('button', name='Browse raw CSV files').click()
                page.locator('.data-table tbody tr').first.wait_for()
                page.locator('#row-search').fill('BASE')
                check(page.locator('.data-table tbody tr').count()>0, 'Raw CSV filtering remains available')
                page.get_by_role('button', name='Back to comparisons').click()
                page.locator('.comparison-table').wait_for()

                # Exercise real error, missing-row and duplicate-row presentation, without changing any source files.
                result_pattern='**/api/result?*'
                page.route(result_pattern, lambda route: route.fulfill(status=500,json={'error':'Synthetic UI load failure'}))
                page.locator('#comparison-home').select_option('funded-50')
                page.get_by_role('alert').wait_for()
                check(page.get_by_role('button',name='Retry loading').is_visible(), 'Failed load offers retry and keeps results unknown')
                check('Not recorded' in page.locator('.comparison-table').inner_text(), 'Failed load does not reuse previous account values')
                page.unroute(result_pattern)
                page.get_by_role('button',name='Retry loading').click()
                page.locator('.comparison-table').wait_for()
                page.route(result_pattern, lambda route: route.fulfill(json={'rows':[{'context':'NQ15','config':'BASE','annual':'0'}, {'context':'NQ15','config':'ADD','annual':'12'}, {'context':'NQ15','config':'ADD','annual':'13'}], 'truncated':False}))
                page.locator('#comparison-home').select_option('personal')
                page.locator('.comparison-table').wait_for()
                check('Ambiguous duplicate rows' in page.locator('.comparison-table').inner_text(), 'Duplicate configurations are explicitly ambiguous')
                check('Not recorded' in page.locator('.comparison-table').inner_text(), 'Missing configurations remain unknown')
                check(page.locator('.comparison-table tbody tr').first.locator('td').first.inner_text()=='$0', 'A recorded zero remains a real zero')
                page.unroute(result_pattern)

                # Deliberately settle two requests in reverse order. The last selected home must win.
                page.evaluate('''() => {
                  window.__originalApi=window.api; window.__pending=[];
                  window.api=()=>new Promise(resolve=>window.__pending.push(resolve));
                  const home=document.querySelector('#comparison-home');
                  home.value='funded-150';home.dispatchEvent(new Event('change'));
                  home.value='personal';home.dispatchEvent(new Event('change'));
                  window.__pending[1]({rows:[{context:'NQ15',config:'BASE',annual:'12345'}],truncated:false});
                }''')
                page.locator('.comparison-table').wait_for()
                page.evaluate("window.__pending[0]({rows:[{context:'NQ15',config:'BASE',account:'150',year1:'99999'}],truncated:false})")
                check(page.locator('.comparison-table tbody tr').first.locator('td').first.inner_text()=='$12,345', 'Late response cannot overwrite the newer account selection')
                page.evaluate('''() => {
                  document.querySelector('#comparison-home').value='funded-50';
                  document.querySelector('#comparison-home').dispatchEvent(new Event('change'));
                  location.hash='overview';
                }''')
                page.get_by_role('heading',name='Research overview',exact=True).wait_for()
                page.evaluate("() => {window.__pending[2]({rows:[],truncated:false});window.api=window.__originalApi;}")
                check(page.locator('#main h1').inner_text()=='Research overview', 'Late comparison response cannot replace a different route')

                page.goto(base+'/#strategies')
                page.locator('.stage-list').wait_for()
                page.locator('#candidate-search').fill('2687614')
                check(page.locator('.candidate-item').count()==1, 'SSRN ID search selects an exact saved analyst record')
                check('Stopped at design' in page.locator('.stage-list').inner_text(), 'Failed design gate remains stopped without invented later-stage success')
                page.get_by_text('Five-question analysis',exact=True).click()
                check(page.locator('.question-details h3').count()==5, 'Five paper questions are present, including explicit missing answers')
                page.screenshot(path=str(output/'strategy-desktop.png'), full_page=True)
                page.locator('#candidate-search').fill('no-such-synthetic-paper-999')
                check('No matching record' in page.locator('#candidate-detail').inner_text(), 'Empty search explains recovery')

                # Record strings are untrusted, even though their files are local.
                page.route('**/api/catalog', lambda route: inject_catalog(route))
                page.reload()
                page.locator('.candidate-item').first.wait_for()
                check(page.locator('.candidate-item').first.inner_text().startswith('<img'), 'Untrusted record markup displays as text')
                check(page.locator('.candidate-detail img').count()==0, 'Untrusted record markup creates no image/script element')
                check(page.evaluate('window.__injected') is None, 'Untrusted record cannot execute script')
                page.unroute('**/api/catalog')
                page.reload()
                page.locator('.candidate-item').first.wait_for()
                check(page.locator('.candidate-item').count()>1, 'Real repository data restored after isolated injection fixture')

                # Mobile viewport emulation; this is not a physical touch-device certification.
                for width in [360,390,768]:
                    page.set_viewport_size({'width':width,'height':900})
                    for route,heading in [('overview','Research overview'),('results','Strategy results'),('strategies','Strategy research')]:
                        page.goto(base+'/#'+route)
                        page.get_by_role('heading',name=heading,exact=True).wait_for()
                        if route=='results':page.locator('.comparison-table').wait_for()
                        if route=='strategies':page.locator('.stage-list').wait_for()
                        check(page.evaluate('document.documentElement.scrollWidth <= innerWidth'), f'No page overflow: {route} at {width}px')
                        if route=='results' and width==390:
                            region=page.get_by_role('region',name='Account comparison; scroll horizontally for all configurations')
                            region.focus();page.keyboard.press('End')
                            region.evaluate('(el)=>{el.scrollLeft=el.scrollWidth;}')
                            check(region.evaluate('(el)=>el.scrollLeft>0'), 'Narrow comparison table scrolls within its labeled region')
                            region.evaluate('(el)=>{el.scrollLeft=0;}')
                        if width==390:page.screenshot(path=str(output/f'{route}-mobile.png'),full_page=True)
                page.set_viewport_size({'width':1440,'height':1100})
                for route in ['library','queue','execution','scout','inbox','notes']:
                    page.goto(base+'/#'+route)
                    page.locator('#main h1').wait_for()
                    if route=='scout':page.locator('#scout-search').wait_for()
                    check(page.locator('#main h1').count()==1, 'Existing view remains available: '+route)
                check(not errors, 'No browser JavaScript errors across all nine views')
                version=browser.version
                browser.close()
        finally:
            http.shutdown(); http.server_close(); thread.join(); server.RUNTIME=original
    source_files=['server.py','desk.py','result_sets.json','static/index.html','static/style.css','static/app.js','static/desk.js','review_ui.py']
    receipt=dict(reviewed_at=datetime.now(timezone.utc).isoformat(), base_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=server.ROOT,text=True).strip(),
        python=platform.python_version(),chromium=version, assertions_passed=len(assertions),csv_cells_checked=cells,
        checks=assertions,browser_errors=errors, screenshots=sorted(p.name for p in output.glob('*.png')),
        source_sha256={f:hashlib.sha256((Path(__file__).parent/f).read_bytes()).hexdigest() for f in source_files},
        limits=['Maker-run UI acceptance; independent Claude review pending.','Headless Chromium and emulated viewports, no physical mobile or screen-reader certification.','No return tests, discovery, live access or portfolio changes.','No Impeccable binary/hook or detector execution; manual published-guidance audit.'])
    (output/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps({k:receipt[k] for k in ['assertions_passed','csv_cells_checked','browser_errors','chromium']},indent=2))


def inject_catalog(route):
    response=route.fetch()
    catalog=response.json()
    catalog['desk']['records']=[dict(title='<img src=x onerror="window.__injected=1">',record_path='agents/codex/research/scout/records/fixture.json',summary='Untrusted test fixture',verdict='metadata_only')]
    route.fulfill(json=catalog)


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',type=Path,default=Path('/tmp/terminal-ui-review'))
    run(parser.parse_args().output)
