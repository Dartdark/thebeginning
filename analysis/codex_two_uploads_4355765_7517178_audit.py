"""Source-table arithmetic and file/schema receipts only; zero empirical strategy trials."""
from pathlib import Path
import csv
import hashlib
import json
import math
import subprocess

OUT=Path('analysis/outputs/codex_two_uploads_4355765_7517178')

def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    # Table4, refit every20 observations; all five displayed evaluation lengths.
    # Transcribed source values checked against rendered PDF, not independently reproduced HE.
    source_he={
        'Copper':{'DCC':[.004,-.003,.001,-.001,.007], 'ADCC':[.004,-.004,.000,-.002,.004]},
        'Gas':{'DCC':[.002,.003,-.004,-.001,.009], 'ADCC':[.002,.002,-.004,.000,.008]},
        'Gold':{'DCC':[.009,-.052,-.021,-.027,-.023], 'ADCC':[.008,-.063,-.026,-.044,-.037]},
        'Brent oil':{'DCC':[-.005,-.016,-.005,-.003,-.007], 'ADCC':[-.005,-.015,-.006,-.004,-.006]},
    }
    rows=[]
    for asset, models in source_he.items():
        for model, values in models.items():
            for length,he in zip([100,500,1000,1500,2000],values):
                rows.append(dict(asset=asset,model=model,refit=20,evaluation_length=length,
                                 source_HE=he,variance_change_pct=-100*he,
                                 standard_deviation_change_pct=100*(math.sqrt(1-he)-1)))
    with (OUT/'source_he_refit20.csv').open('w') as f:
        writer=csv.DictWriter(f,fieldnames=rows[0]); writer.writeheader();writer.writerows(rows)
    assert all(r['source_HE']<0 for r in rows if r['asset']=='Brent oil')
    assert all(r['source_HE']<0 for r in rows if r['asset']=='Gold' and r['evaluation_length']>=500)
    etf={'in_sample_source':{'long_short_annual_return_pct':17.57,'long_short_sharpe':.98,'benchmark_annual_return_pct':5.82,'benchmark_sharpe':.14},
         'jan_aug_2026_source':{'long_return_pct':27.59,'short_basket_underlying_return_pct':15.97,'long_short_return_pct':8.54,'benchmark_return_pct':16.82,'long_short_sharpe':.54,'benchmark_sharpe':2.01,'long_short_max_dd_pct':-13.45,'benchmark_max_dd_pct':-7.86},
         'source_one_way_monthly_turnover':{'long':.3616,'short':.4220},
         'source_oos_relative_return_pp':8.54-16.82,
         'warning':'Short basket return is not the P&L earned by shorting it; CAGR legs cannot simply be subtracted.'}
    files={}
    for num in ['4355765','7517178']:
        root=Path('agents/codex/inputs')/('ssrn'+num)
        files[num]={str(p):{'sha256':sha(p),'bytes':p.stat().st_size} for p in sorted(root.iterdir()) if p.is_file()}
    census={}
    for pattern in ['*BTC*','*GC*','*CL*','*NG*','*HG*','*Brent*','*holdings*','*NAV*','*shares*','*flows*']:
        census[pattern]=[str(p) for p in sorted(Path('data').rglob(pattern)) if p.is_file()][:35]
    headers={}
    for p in [Path('data/BTCUSD_spot_1min_2020.csv'),Path('data/BTC_1min_2020.csv')]:
        if p.exists():
            with p.open() as f:headers[str(p)]=next(csv.reader(f))
    result=dict(source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
                script_sha256=sha(__file__),source_files=files,source_he_values=rows,etf_source=etf,
                owned_filename_census=census,inspected_headers=headers,return_trials=0,
                audit_scope='Source arithmetic, PDF tables and bounded input census; no economic replication')
    (OUT/'audit.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS: source-table signs/variance units, ETF OOS comparison and file/schema receipts; zero strategy trials.')

if __name__=='__main__':main()
