"""Compare source/defaults and audit published OB v2 arithmetic; no new backtest."""
from pathlib import Path
import csv
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT/'agents/codex/inputs/ob_v2'
OUT = ROOT/'analysis/outputs/codex_ob_v2_comparison'
REFERENCES = ['apex_strategies/NQ_Overnight_Bias_ADX30.txt',
              'funded_strategies/NQ_Overnight_Bias_ML.txt',
              'analysis/bridge_onb_orb_test.py', 'analysis/outputs/bridge_onb_orb_test_output.txt',
              'analysis/onb_adx30_confirm.py', 'analysis/outputs/onb_adx30_confirm_output.txt']


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def defaults(path):
    code = re.sub(r'\{.*?\}', '', path.read_text(), flags=re.S)
    code = re.sub(r'//[^\n]*', '', code)
    block = re.search(r'inputs:(.*?)(?:variables:|vars:)', code, re.I|re.S).group(1)
    return {k: (v.lower() == 'true' if v.lower() in ('true', 'false') else float(v))
            for k, v in re.findall(r'(\w+)\(\s*([\d.]+|true|false)\s*\)', block, re.I)}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    text = (INPUT/'overview_extracted.txt').read_text()
    rows = []
    for y,n,p,q in re.findall(r'\b(20\d{2})\s+(\d+)\s+\$([\d,.]+)\s+\$([\d,.]+)\s*$', text, re.M):
        row = dict(year=int(y), claimed_trades=int(n), claimed_net_MNQ=float(p.replace(',', '')),
                   claimed_net_NQ=float(q.replace(',', '')))
        assert row['claimed_net_MNQ']*10 == row['claimed_net_NQ']
        rows.append(row)
    assert len(rows)==10
    with (OUT/'overview_annual_claims.csv').open('w') as f:
        w=csv.DictWriter(f, fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
    totals={}
    for label,keep in [('full',lambda y:True),('2017_22',lambda y:y<=2022),
                       ('2018_22',lambda y:2018<=y<=2022),('2023_plus',lambda y:y>=2023)]:
        totals[label]={k:sum(r[k] for r in rows if keep(r['year'])) for k in rows[0] if k!='year'}
    assert totals['full']['claimed_trades']==603 and totals['full']['claimed_net_MNQ']==23094.5
    prior=(ROOT/REFERENCES[3]).read_text()
    labels=['Bridge ORB (Python replica)','ours: ONB ADX30 (MC, combine)','ours: ONB ML v2 (MC, funded)']
    metrics={}
    for label in labels:
        m=re.search(r'^'+re.escape(label)+r'\s+n=\s*(\d+)\s+win\s+(\d+)%\s+avg\s+\$\s*([\d.]+)\s+PF\s+([\d.]+)\s+t=\s*([\d.]+)',prior,re.M)
        assert m,label
        n,win,avg,pf,t=m.groups()
        metrics[label]=dict(trades=int(n),win_pct=float(win),average_NQ=float(avg),PF=float(pf),t=float(t))
    uploaded=(INPUT/'source.txt').read_text()
    entry=uploaded.split('if canWork then begin')[1].split('// ------------------- Exits')[0]
    assert 'L-SL-FB' in entry and 'S-SL-FB' in entry
    data=dict(operation='source comparison, published-claim arithmetic and reading existing result files',
              new_strategy_return_trials=0, independent_replication_of_uploaded_strategy=False,
              author_annual_claim_totals=totals,
              implied_author_full_average_NQ=totals['full']['claimed_net_NQ']/totals['full']['claimed_trades'],
              prior_unfiltered_comparison_2018_26=metrics,
              prior_combine_pair_pass_pct=dict(our_ADX30=46.9,unfiltered_Bridge=38.9),
              prior_bench_is_uploaded_v2=False,
              defaults=dict(uploaded=defaults(INPUT/'source.txt'),
                            our_ADX30=defaults(ROOT/REFERENCES[0]),our_funded_ML=defaults(ROOT/REFERENCES[1])),
              source_features=dict(preissues_bracket_with_entry=True,
                                   uploaded_contains_SetExitOnClose='SetExitOnClose;' in uploaded,
                                   raw_MC_report_supplied=False,
                                   source_comments_request_IOG_off_but_no_directive=not bool(re.search(r'\[IntrabarOrderGeneration',uploaded,re.I))),
              inventory_snapshot='e7c394f')
    (OUT/'summary.json').write_text(json.dumps(data,indent=2)+'\n')
    manifest=dict(input_sha256={str(p.relative_to(ROOT)):sha(p) for p in sorted(INPUT.iterdir())},
                  comparison_source_sha256={p:sha(ROOT/p) for p in REFERENCES},
                  code_sha256={str(Path(__file__).relative_to(ROOT)):sha(Path(__file__))})
    (OUT/'reproduction.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps(dict(author_totals=totals,prior_comparison=metrics,new_strategy_return_trials=0),indent=2))


if __name__=='__main__':
    main()
