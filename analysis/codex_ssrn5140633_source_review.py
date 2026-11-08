"""Audit source identity, quoted arithmetic and owned metadata only. No return test.

The Table 6 observations below are transcriptions of author results, not newly
computed market performance. No raw OHLC, daily price panel or strategy runner
is loaded. Run with the configured project Python from any working directory.
"""
import csv
import datetime as dt
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'agents/codex/inputs/ssrn5140633_20261108'
OUT = ROOT / 'analysis/outputs/codex_ssrn5140633_20261108'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    paper = (BASE / 'paper.txt').read_text()
    assert 'This version: February 17, 2025' in paper
    assert '16.24%' in paper and '18.51%' in paper and '−22.63%' in paper
    rows = [
        ('1-month', 14.32, 20.90, -42.42, .69),
        ('3-month', 16.23, 20.95, -30.29, .77),
        ('12-month', 15.80, 24.15, -45.26, .65),
        ('combined', 16.24, 18.51, -22.63, .88),
        ('buy-and-hold', 2.53, 14.12, -45.24, .18),
    ]
    with (OUT / 'author_table6.csv').open('w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['author_profile', 'annual_return_pct', 'annual_volatility_pct',
                    'maximum_drawdown_pct', 'reported_sharpe'])
        w.writerows(rows)
    prior = ROOT / 'analysis/outputs/overnight_round_output.txt'
    old = prior.read_text()
    assert 'return 4.4%/yr, vol 9.6%, Sharpe 0.46, max DD -16.8%, t 1.3' in old
    assert '2018-12-20..2026-10-14' in old
    description = ROOT / 'agents/codex/inputs/scout_20261101/free_daily_panel/local/tf_system_data_descriptive_df.csv'
    with description.open() as f:
        descriptions = list(csv.DictReader(f))
    scout = ROOT / 'agents/codex/research/scout/progress.json'
    progress = json.loads(scout.read_text())
    receipt = dict(
        reviewed_at_utc=dt.datetime.now(dt.timezone.utc).isoformat(),
        checked_codex_head=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        checked_remote_codex=subprocess.check_output(['git', 'rev-parse', 'origin/codex/work'], cwd=ROOT, text=True).strip(),
        claude_source_ref=subprocess.check_output(['git', 'rev-parse', 'origin/claude/nq-trading-strategy-params-5h9d20'], cwd=ROOT, text=True).strip(),
        source=dict(id='ssrn:5140633', title='Trend Following Strategies: A Practical Guide',
            authors=['Chuan Shi', 'Xiangbin Lian'], version='February 17, 2025', pages=41,
            path=str((BASE / 'paper.pdf').relative_to(ROOT)), sha256=sha(BASE / 'paper.pdf'),
            text_sha256=sha(BASE / 'paper.txt'), permission='owned_upload',
            access_method='User-uploaded PDF; pdftotext -layout; all 41 pages read; Table 6 page visually checked',
            attachment='file_000000008b5081fd813f94088fe60f23', url='https://ssrn.com/abstract=5140633'),
        independent_checks=dict(
            scope='Arithmetic of quoted numbers only; not return replication or Sharpe-convention certification',
            combined_quoted_return_div_vol=16.24 / 18.51,
            buy_hold_quoted_return_div_vol=2.53 / 14.12,
            combined_vol_vs_buy_hold_ratio=18.51 / 14.12,
            combined_vol_vs_approx_12pct_objective_ratio=18.51 / 12,
            conclusion='Ratios round to the quoted Sharpes. Benchmark is not risk matched. Single-asset scaling does not guarantee portfolio volatility.'),
        owned_input_check=dict(
            method='Filename inventory and existing acquisition/provenance/descriptive metadata; no raw price returns read',
            minute_export_names=sorted(p.name for p in (ROOT / 'data').glob('*1min*.csv')),
            public_panel_description_rows=len(descriptions),
            public_panel_metadata_sha256=sha(description),
            mapped_inputs='Owned US futures can support a separately justified adaptation. The acquired global daily panel is not the exact 36 Chinese domestic assets/contract returns.',
            namespace_warning='Source Table 3 ZN is zinc; owned CME ZN is a US Treasury-note future. Names alone do not map instruments.',
            exact_source_replication='No matching full source universe/contract-roll/execution conventions established; no new data request or acquisition loop warranted for a duplicate family.'),
        prior_evidence=dict(path=str(prior.relative_to(ROOT)), sha256=sha(prior),
            period='2018-12-20 through 2026-10-14', annual_net_pct=4.4, annual_vol_pct=9.6,
            sharpe=.46, t=1.3, max_drawdown_pct=-16.8,
            status='Repository-reported existing six-market weekly adaptation, not rerun or independently validated; code uses ffill, fillna(0) and retrospective largest-jump roll adjustment.'),
        disposition='dont_test', economic_family='diversified-monthly-time-series-momentum-volatility-scaling',
        reason='Already-researched family; monthly holdings incompatible with Apex; no new owned-data-compatible advantage or risk-matched net evidence demonstrated.',
        new_economic_trials=0, source_return_tests_run=False, new_portfolio_comparisons_run=False,
        scout_unchanged=dict(progress_sha256=sha(scout), hypotheses=progress['hypotheses_started'],
                             definitions=progress['economic_definitions'], lease=progress['lease']),
        root_trials_sha256=sha(ROOT / 'TRIALS.csv'),
        independent_economic_verification='not performed',
    )
    (OUT / 'source_receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(dict(source_sha256=receipt['source']['sha256'], pages=41,
                         disposition='dont_test', new_return_trials=0,
                         combined_quoted_return_div_vol=receipt['independent_checks']['combined_quoted_return_div_vol'])))


if __name__ == '__main__':
    main()
