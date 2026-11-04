"""Render retained account outcomes only; no signals, tests or selection run."""
from pathlib import Path
import csv
import json
import re

ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / 'agents/codex/runtime/eval_audit_20261104'
OUT = ROOT / 'agents/codex/results'
BASE = ROOT / 'agents/codex/inputs/eval_audit_20261104'
REPORT = OUT / 'eval_audit_20261104.md'


def read(p):
    return json.loads(p.read_text())


def name(p):
    s = p['label']
    if s in ('CURRENT', 'EMPTY'):
        return s
    return s.replace('FIXED_ONLY_', '').replace('_20MICRO', ' 20 MNQ').replace('_MARKET_TARGET_GUARD', ' + target guard')


def pct(x):
    return f'{100*x:.1f}%'


def stats(t):
    return ' / '.join(pct(t['rates'][x]) for x in ('pass', 'fail', 'expire', 'unknown'))


def readable_prose(text):
    """Space source-note typography without changing code, links or figures."""
    before_code = re.findall(r'`[^`]*`', text)
    before_links = re.findall(r'\]\(([^)]+)\)', text)
    parts = re.split(r'(`[^`]*`|\]\([^)]+\))', text)
    for i in range(0, len(parts), 2):
        s = parts[i].replace('a$249150K', 'a $249 150K').replace('Account#', 'Account #')
        s = re.sub(r'([A-Za-z])(\d)', r'\1 \2', s)
        s = re.sub(r'(\d)([A-Za-z])', r'\1 \2', s)
        s = s.replace('FC 2 B', 'FC2B').replace('50 K', '50K').replace('150 K', '150K')
        s = s.replace('RTper', 'RT per')
        for old, new in {'failedOctober':'failed October', 'OnNovember':'On November',
                         'RecentOctober':'Recent October', 'theNovember':'the November',
                         'endJune':'end June', 'throughJuly':'through July',
                         'two-sidedMNQ':'two-sided MNQ', 'executionOK':'execution OK'}.items():
            s = s.replace(old, new)
        s = re.sub(r'%([A-Za-z])', r'% \1', s)
        s = re.sub(r'(?<=[A-Za-z])(?=\$)', ' ', s)
        s = re.sub(r'(?<=[A-Za-z%]),(?=\d)', ', ', s)
        s = re.sub(r'(?<=[A-Za-z]):(?=[A-Za-z0-9])', ': ', s)
        s = re.sub(r';(?=\S)', '; ', s)
        s = re.sub(r'(\d\+)(?=[A-Za-z])', r'\1 ', s)
        s = s.replace('×', ' × ')
        parts[i] = s
    result = ''.join(parts)
    assert before_code == re.findall(r'`[^`]*`', result)
    assert before_links == re.findall(r'\]\(([^)]+)\)', result)
    return result


def main():
    frozen = read(BASE / 'amended_frozen_validation_selection.json')
    reports = {(c, s): read(RUN / 'validation_amended' / f'report_{c}_{s}.json')
               for c in ('main', 'low', 'stress')
               for s in ('fresh', 'three_quarter_cushion', 'half_cushion', 'quarter_cushion')}
    current = reports['main', 'fresh']
    ids = [p['candidate_id'] for p in frozen['nominees']]
    rows = []
    for (cost, state), report in reports.items():
        for account, policies in report['accounts'].items():
            for cid, p in policies.items():
                for cohort, t in p['cohorts'].items():
                    row = dict(account=account, candidate_id=cid, label=p['label'], cost=cost,
                               initial_cushion=state, cohort=cohort, n=t['n'])
                    row.update({x: t['counts'][x] for x in ('pass', 'fail', 'expire', 'unknown')})
                    row.update({x: t[x] for x in ('pass_lower', 'pass_upper', 'fail_lower', 'fail_upper',
                                                  'conditional_pass_median_time')})
                    fee = t['fee_normalization']
                    row.update(fee_units_lower=fee['normalized_fee_per_pass_identified_lower'],
                               fee_units_upper=fee['normalized_fee_per_pass_identified_upper'])
                    rows.append(row)
    with (OUT / 'eval_audit_20261104_metrics.csv').open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator='\n')
        writer.writeheader(); writer.writerows(rows)

    selected = [(a, cid, p) for a, ps in current['accounts'].items() for cid, p in ps.items() if cid in ids]
    assert len(selected) == 4
    selected.sort(key=lambda x: (int(x[0][:-1]), x[2]['label']))
    lines = [
        '# Evaluation strategy and sizing audit — November 4, 2026', '',
        'Summary: The current plans cannot be certified optimal; documented ONB stop risks exceeded remaining account cushions.',
        'Audited36 families/18 testable sources and2,965 registered configurations, retaining809,476 overlapping account scenarios.',
        'Best identified50K frozen nominee: ONBML at20MNQ with a prospective target guard,45.1%pass/45.6%fail/9.3%expire.',
        'Current-baseline missing risk inputs prevent an identified superiority claim; depleted-cushion failure remains severe.',
        'No replacement earns the frozen recommendation gates; native execution/guard verification and user allocation review remain pending.', '',
        '## Decision', '',
        'The earlier pass-rate estimates are insufficient to establish that today\'s evaluation books are the best available.',
        'The recent loss records expose a concrete sizing problem: fixed dollar-risk budgets can exceed the account\'s',
        'remaining floor cushion. The broad comparison also found no demonstrated low-failure replacement. Preserve the',
        'existing purchase/approval boundary; these research results do not select or install a new allocation.', '',
        'The strongest fully identified50K alternative among the four frozen nominees is ONBML at20MNQ with a',
        'prospective account target guard. It still fails45.6%of historical fresh starts. The150K FC2B candidate',
        'fails65.2%. LDF reduces failures largely by expiring:54.0%of its150K starts never pass. These are',
        'conditional model results, not calibrated live-account probabilities or evidence that losing streaks end.', '',
        '## What the four losses establish', '',
        '|Account/date|Recorded remaining cushion|Planned ONB stop risk before costs|Implication|',
        '|---|---:|---:|---|',
        '|150K #3, Oct30|$1,822.60|$2,456.00 at8MNQ|Floor can liquidate before the planned stop|',
        '|50K #2, Nov4|$931.34|$1,062.00 at3MNQ|Same|',
        '|150K #4, Nov4|$1,939.60|$2,478.00 at7MNQ|Same|', '',
        'Account#1 failedOctober26; its exact final fill/floor is not independently reconstructed. The final two',
        'failures share the same NQ signal, so they are correlated exposures. They are not independent strategy trials.',
        'OnNovember4 both account equity logs were below their floors by09:50CT. Later VB chart trades are not',
        'demonstrated broker fills. The earlier chart-signal “15/15executionOK” comparison also included known rejected',
        'or post-lock/death trades. Exact broker attribution still needs the original statements; committed chart logs',
        'alone cannot reconcile it. See the [source-linked forensic report](../inputs/eval_audit_20261104/loss_forensics.md).', '',
        'A final read-only fetch found Claude advanced to `75df521` during this audit. Its `0b5ac65` follow-up now',
        'excludes the later account#2/#4 chart trades from dashboard/journal generation. The tested evaluation roster',
        'and source inputs did not change. See [source follow-up](../inputs/eval_audit_20261104/source_followup_75df521.md).', '',
        '## Search and evidence boundaries', '',
        '- Reviewed the368-row registry as36 economic/source families;18 compatible source strategies entered this study.',
        '  Failed families, multiday/early-close violations and missing material signal inputs remain excluded with reasons',
        '  in the [inventory](../inputs/eval_audit_20261104/strategy_inventory.md). VB partitions were not independent alpha.',
        '- Original2,485 configurations: uniform scaling, current-book reweights/removals, ONBML substitution, standalone',
        '  strategies, two/three-leg equal-risk books, replacements, diversification and account risk controls.',
        '- A separately committed460-case fixed-quantity arm followed input-admission findings. It includes1/2/4/8/12/20',
        '  native micros per standalone and equal2/4 per eligible pair. Its16 canonical aliases reuse earlier results.',
        '  It avoids needing ATR to calculate quantity; it does not reconstruct missing ATR or relax held-price/fill gates.',
        '- An independently sourced DT correction moved all401 time exits uniformly to their known OPEN clock.',
        '  The390 legacy CLOSE mismatches remain in original results. All401 corrected open prices matched; no favorable',
        '  touch search or source price change occurred. See [diagnosis](../inputs/eval_audit_20261104/postexecution_source_diagnosis.md).',
        '- The joint design selected four parents;20 reserved governor/target-guard definitions were committed before',
        '  their outcomes. Final nominations were committed before2023+account computation. Total2,965 registered',
        '  definitions,35 slots unspent under3,000. Conservative counts and aliases preserve multiplicity; configurations',
        '  and overlapping account starts are not independent predictive discoveries.',
        '- Primary source window:2018-04-02–2026-07-07, with2017 raw warmup. Design uses244 Monday starts with whole',
        '  expiry before2023:723,460 account records. Historical validation uses896 weekday starts2023-01-02–2026-06-08,',
        '  each with complete30-calendar-day access:8candidate/control books×12cost/cushion views=86,016 more records.',
        '  Previously seen2023+is historical validation, not fresh OOS. RecentOctober/November losses were not fitted.', '',
        '## Fresh-account historical validation', '',
        'All rows use896 identical starts. Pass time is calendar days **conditional on passing**. All four nominated',
        'books have20MNQ(two NQ minis); source signals/exits stay fixed. Three add the prospective target guard.', '',
        '|Home / frozen nominee|Pass|Fail|Expire|Unknown|Median pass days|Fee units per pass|',
        '|---|---:|---:|---:|---:|---:|---:|',
    ]
    for account, cid, p in selected:
        t = p['cohorts']['all2023plus']; f = t['fee_normalization']['normalized_fee_per_pass_identified_lower']
        lines.append(f"|{account} {name(p)}|" + '|'.join(pct(t['rates'][x]) for x in ('pass','fail','expire','unknown'))
                     + f"|{t['conditional_pass_median_time']:.2f}|{f:.2f}×|")
    lines += ['', 'Fee units are descriptive fee/P(pass), not an independent-retry forecast. The actual50K purchase price',
              'is unverified. Conditional on a$249150K purchase, FC2B implies$878.36 per pass and LDF$3,718.40,',
              'excluding activation/other charges. EMPTY has0passes/0failures/896expirations in each home.', '',
              '### Current baseline is not identified', '',
              '|Home|Confirmed pass/fail/expire/unknown counts|Identified pass-rate range|',
              '|---|---|---:|']
    for account, policies in current['accounts'].items():
        p = next(v for v in policies.values() if v['label'] == 'CURRENT')
        t = p['cohorts']['all2023plus']; c = t['counts']
        lines.append(f"|{account}|{c['pass']} / {c['fail']} / {c['expire']} / {c['unknown']}|{pct(t['pass_lower'])}–{pct(t['pass_upper'])}|")
    lines += ['', 'Missing expected-open ATR lookback observations prevent certifying the current dollar-risk quantities.',
              'UNKNOWN is neither a failure nor a no-trade day. Confirmed-pass differences against this baseline cannot',
              'be treated as improvements. All paired90%4/8-week,5,000-resample identified pass and failure contrasts',
              'span zero widely. Neither the efficiency nor safety recommendation gate is established.', '',
              '### Recent2026 source cohort', '',
              'These113 starts endJune8, with paths throughJuly7; this is not all2026 or theNovember failure period.', '',
              '|Frozen nominee|2023–25 pass/fail|2026 pass/fail/expire|',
              '|---|---|---|']
    for account, cid, p in selected:
        a, b = p['cohorts']['2023through2025'], p['cohorts']['2026']
        lines.append(f"|{account} {name(p)}|{pct(a['rates']['pass'])} / {pct(a['rates']['fail'])}|"
                     + ' / '.join(pct(b['rates'][x]) for x in ('pass','fail','expire')) + '|')
    lines += ['', 'FC2B50K deteriorates to18.6%pass/81.4%fail in the2026 cohort. No new date filter, rescue size',
              'or nominee substitution was made from this observation.', '',
              '## Costs and depleted-cushion sensitivity', '',
              'Main commission is$1.24RTper micro plus one adverse native tick per market/stop fill. A two-sidedMNQ',
              'market roundtrip therefore costs$2.24 per micro, before additional impact. Low cost is$1.04RT/one tick;',
              'stress is$2.48RT/two ticks($4.48 per two-sidedMNQ market roundtrip). Limits require frozen trade-through',
              'qualification. MES/MCL fees in unselected designs remain assumptions, not broker invoices.', '',
              '|Frozen nominee|Main fresh pass/fail|Stress fresh pass/fail|Half cushion pass/fail|Quarter cushion pass/fail|',
              '|---|---|---|---|---|']
    for account, cid, p in selected:
        cells = []
        for key in [('main','fresh'),('stress','fresh'),('main','half_cushion'),('main','quarter_cushion')]:
            t = reports[key]['accounts'][account][cid]['cohorts']['all2023plus']
            cells.append(f"{pct(t['rates']['pass'])} / {pct(t['rates']['fail'])}")
        lines.append(f"|{account} {name(p)}|" + '|'.join(cells) + '|')
    lines += ['', 'Thin-cushion starts have zero initial net profit and25/50/75%of the original trail left. They are synthetic',
              'states, not replays of the actual four accounts. Faster conditional pass times among surviving thin-cushion',
              'accounts do not offset the increased failures. All12scenario/cohort counts are retained in the',
              '[metrics CSV](eval_audit_20261104_metrics.csv) and exact case archive.', '',
              '### Why smaller risk controls did not solve the target/expiry tradeoff', '',
              'On the known100-point-stop FC2B design, the full cushion/DLL cap has50K22passes/222expirations/0failures',
              '(9.0%pass), and150K11passes/233expirations/0failures(4.5%pass), each of244starts. Tighter caps mostly',
              'expire. These controls were retained and did not win the frozen selection.',
              'For LDF/ONBML, missing historical risk inputs can cause the defined cap model to reject orders. Their',
              'zero-trade/zero-failure expirations are data-rejection outcomes, **not evidence that native ATR risk caps',
              'are safe or ineffective**. All final validation nominees have risk_fraction=0; this limitation does not',
              'create their positive pass rates. A remaining-cushion check is a necessary implementation safeguard for',
              'a proposal, but a profitable evaluation schedule still has to earn its target before expiration.', '',
              '## Engineering checks and material limits', '',
              '- Corrected model rules include EOD floor ratchet with inclusive intraday enforcement, evaluation versus',
              '  PA floor-lock distinction, market DLL liquidation/pause,30calendar-day access, net integer contract caps,',
              '  closing costs before target recognition and suppression of later orders after account termination.',
              '- Dates/closures and compressed-chart clocks are explicit; the index15-minute pause endsJune28,2021.',
              '  Source lookback gaps remain unknown. Missing returns are not interpolated. Original and amended',
              '  code, source hashes, ledgers, trial history and outcome fingerprints are preserved.',
              '- Engineering checks include35 synthetic cases/100raw-versus-fast tapes,157 actual-fill design checks',
              '  and220 checks across four frozen validation cases, including a150K pass. These validate the specified',
              '  accounting model; they are not independent native-platform economic verification.',
              '- Shared OHLC phases and cross-asset ordering remain models. Intraminute first observed liquidation prices',
              '  can differ materially from actual tick-level DLL/floor liquidation. Continuous NQ/ES/CL prices do not',
              '  verify MNQ/MES/MCL native spreads, contract rolls, latency, queue priority or size-dependent market impact.',
              '- The target guard is prospective, uninstalled/unverified. It requires account-equity monitoring, market',
              '  flattening/cancellation and suppression of further entries after reaching the realized target. Its modeled',
              '  benefit cannot be assumed from an uncompiled/native-unmatched controller or a chart-only signal log.',
              '- Fast minimum equity is a visited-node minimum plus a conservative bound, not exact joint drawdown.',
              '  No alternate tick chronology, exact native source matching, funded payouts or personal-account return',
              '  improvement is claimed. All36-family/old strategy selection histories remain relevant.', '',
              '## Reproduction and Claude handoff', '',
              '|Stage|Committed before dependent outcomes|',
              '|---|---|',
              '|Original evidence/config/exact code/2,485 definitions|`a087708b13697df4c3dd0b0814f98cb53a2b254a`|',
              '|Fixed-size arm/source-clock overlay/460 definitions|`e8e249b4e7c8946d517e8e4c9a4a3b4e62063e24`|',
              '|Joint initial selection/20 governor definitions|`67bab2a2daa808ffc7c50ebde150ed857df51b69`|',
              '|Frozen final nominees before2023+|`588e6b692e83154d056a3ecefca8eb1411f78d19`|', '',
              'Use `/workspace/venvs/thebeginning/bin/python` from repository root. Original stage commands are in',
              '[runner usage](../inputs/eval_audit_20261104/runner_usage.md). For the amended stages, use',
              '`analysis/codex_eval_amended_run_20261104.py` with `--commit e8e249b4e7c8946d517e8e4c9a4a3b4e62063e24`;',
              'derived design uses `--selection-commit 67bab2a2daa808ffc7c50ebde150ed857df51b69`, validation uses',
              '`--selection-commit 588e6b692e83154d056a3ecefca8eb1411f78d19`. Saved completed cases are reused by hash.', '',
              'The [exact case archive](eval_audit_20261104_cases.zip) and',
              '[SHA256 manifest](eval_audit_20261104_cases.manifest.json) retain account CSVs, ledgers, quality/source',
              'receipts, design/validation summaries and all12 uncertainty views. Large reconstructible tape arrays are',
              'excluded. To render this report/CSV from the retained runtime tree, run',
              '`python analysis/codex_eval_report_20261104.py`; it computes no new market outcome or selection.', '',
              'Review [Claude handoff](../inputs/eval_audit_20261104/CLAUDE_REVIEW.md),',
              '[account/source review](../inputs/eval_audit_20261104/final_results_review.md) and',
              '[raw/account engineering review](../inputs/eval_audit_20261104/validation_engineering_review.md).',
              'The remaining current-baseline requirement is source-matched per-entry stop/risk values or native sizing',
              'evidence for its ONB/EOS history. Existing free/owned minute gaps cannot certify those values. This does',
              'not authorize a recurring data chase, proxy replacement or a new outcome-selected strategy. The completed',
              'research and exact code are ready for the user to forward to Claude; no external message was sent.', '']
    REPORT.write_text(readable_prose('\n'.join(lines)))
    print(json.dumps({'report': str(REPORT.relative_to(ROOT)), 'metric_rows': len(rows),
                      'account_outcomes': 723460+86016, 'new_return_tests': 0}))


if __name__ == '__main__':
    main()
