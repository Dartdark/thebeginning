"""Audit printed paper tables only; no market data, signals or new return trials."""
from pathlib import Path
import re, json, csv, hashlib
from scipy.stats import f_oneway

ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'agents/codex/inputs/bank_nifty_4013524_20261031'
OUT=ROOT/'analysis/outputs/codex_bank_nifty_source_audit_20261031'


def main():
    pages=(SRC/'source.txt').read_text().split('\f')
    rows=[]
    pattern=r'\s*(\d{1,2}/\d{1,2}/\d{4})\s+([\d.]+)\s+([\d.]+)\s+([-\d.]+)\s+([-\d.]+)%\s+([-\d.]+)\s*$'
    for page in pages[10:14]:
        for line in page.splitlines():
            match=re.match(pattern,line)
            if match: rows.append(match.groups())
    assert len(rows)==136, 'Source extraction changed; do not silently omit table rows'
    sums=[float(r[-1]) for r in rows]
    comparisons={
        'trade_count':([27,24,26,29,30],[31,34,35,38,38]),
        'winning_count':([16,15,17,17,19],[19,21,21,24,22]),
        'losing_count':([11,9,9,12,11],[12,13,14,14,16]),
        'winning_accuracy_printed':([59.26,62.5,65.38,58.6,63.33],[61.29,61.76,60,63.16,57.89])}
    out={'scope':'Printed source-table arithmetic only, not independent historical strategy verification',
         'rows':len(rows),'positive_rows':sum(v>0 for v in sums),
         'printed_positive_row_fraction':sum(v>0 for v in sums)/len(rows),
         'sum_printed_one_lot_rupees':sum(sums),
         'max_point_difference_rounding_error':max(abs(float(r[2])-float(r[1])-float(r[3])) for r in rows),
         'max_lot_multiplication_error':max(abs(20*float(r[3])-float(r[-1])) for r in rows),
         'anova_on_printed_actual_and_generated_forecasts':{k:{'F':float(f_oneway(*v).statistic),'p':float(f_oneway(*v).pvalue)} for k,v in comparisons.items()},
         'caveat':'Forecast groups are generated from historical data, not independent realized outcomes. ANOVA compares means, not correlation or predictive accuracy.',
         'new_economic_return_trials':0,'account_simulations':0,
         'source_sha256':hashlib.sha256((SRC/'source.pdf').read_bytes()).hexdigest(),
         'code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    OUT.mkdir(parents=True,exist_ok=True)
    with (OUT/'printed_rows.csv').open('w') as f:
        writer=csv.writer(f);writer.writerow(['date_as_printed','previous_index_close','index_close','points','pct_as_printed','rupees_20x_points']);writer.writerows(rows)
    (OUT/'audit.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out,indent=2))


if __name__=='__main__':main()
