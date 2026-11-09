"""No-return intake of a public historical macro actual/consensus snapshot.

Read JSON only. No external code imports/execution and no trading signals/P&L.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'agents/codex/inputs/eval_focus_20261109/macro_intake'
REF = 'c3e2d4c79868ee516dc0ed111e1e4a28608a3a8b'
URL = 'https://github.com/superpilot69/fred-us-macro-open-data'


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--source',default='/tmp/eval_macro_source_20261109')
    args=ap.parse_args()
    source=Path(args.source)
    assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=source,text=True).strip()==REF
    OUT.mkdir(parents=True,exist_ok=True)
    manifest={'source':URL,'commit':REF,'return_tests':0,'admitted_for_strategy_returns':False,'files':{},'reason':'Historical forecast/initial-actual receipt and revision provenance not established; timestamp anomaly found.'}
    for fn in ['README.md','LICENSE.md','metadata/dataset-metadata.json','metadata/series-catalog.json','data/investing-us-macro-consensus.json']:
        raw=(source/fn).read_bytes()
        manifest['files'][fn]={'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()}
        # Preserve public source data and notices for independent audit. Never execute upstream code.
        target=OUT/'snapshot'/fn;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw)
    data=json.loads((source/'data/investing-us-macro-consensus.json').read_text())
    rows=[]; anomalies=[]
    for series in data['series']:
        if series['eventId'] not in [733,736,227,294,256]:continue
        x=pd.DataFrame(series['occurrences']);x['utc']=pd.to_datetime(x.occurrenceTime,utc=True)
        x=x[(x.utc>='2018-01-01')&(x.utc<'2023-01-01')].copy()
        x['et']=x.utc.dt.tz_convert('America/New_York')
        valid=x.actual.notna()&x.forecast.notna()
        rows.append({'event_id':series['eventId'],'label':series['label'],'design_rows':len(x),
                     'actual_and_forecast':int(valid.sum()),'duplicate_release_timestamps':int(x.utc.duplicated().sum()),
                     'off_0830_et':int(x.et.dt.strftime('%H:%M').ne('08:30').sum()),
                     'forecast_available_at_receipts':0,'initial_actual_verified_against_primary_archive':0})
        for z in x[x.et.dt.strftime('%H:%M').ne('08:30')].itertuples():
            anomalies.append({'event_id':series['eventId'],'label':series['label'],'occurrence_id':z.occurrenceId,
                              'source_timestamp':z.occurrenceTime,'new_york_timestamp':str(z.et),
                              'status':'needs primary release-clock verification; source value not silently changed'})
    pd.DataFrame(rows).to_csv(OUT/'design_coverage.csv',index=False)
    (OUT/'clock_anomalies.json').write_text(json.dumps(anomalies,indent=2)+'\n')
    (OUT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(pd.DataFrame(rows).to_string(index=False))
    print('Admission: NEEDS DATA / audit; zero returns tested.')


if __name__=='__main__':main()
