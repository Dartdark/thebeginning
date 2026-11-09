"""Cross-check macro release clocks against already-owned calendars; no returns."""
import hashlib
import io
import json
from pathlib import Path
import subprocess

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'agents/codex/inputs/eval_focus_20261109/macro_reconciliation'
MACRO = ROOT/'agents/codex/inputs/eval_focus_20261109/macro_intake/snapshot/data/investing-us-macro-consensus.json'
CAL = 'agents/codex/inputs/scout_acquisition_20261029/fx_calendar/primary_release_calendar_2018_2022.csv'
CLAIMS = 'agents/codex/inputs/scout_acquisition_20261029/claims_calendar/claims_calendar_2018_2022.csv'


def committed(path):
    return subprocess.check_output(['git','show','HEAD:'+path],cwd=ROOT)


def main():
    raw_cal,raw_claims=committed(CAL),committed(CLAIMS)
    calendar=pd.read_csv(io.BytesIO(raw_cal));claims=pd.read_csv(io.BytesIO(raw_claims))
    raw=MACRO.read_bytes();source=json.loads(raw)
    rows=[];summary=[]
    for series in source['series']:
        if series['eventId'] not in [733,736,227,294,256]:continue
        x=pd.DataFrame(series['occurrences']);x['utc']=pd.to_datetime(x.occurrenceTime,utc=True)
        x=x[(x.utc>='2018-01-01')&(x.utc<'2023-01-01')].copy();x['date']=x.utc.dt.strftime('%Y-%m-%d')
        if series['eventId'] in [733,736,227]:
            family='EMPLOYMENT_SITUATION' if series['eventId']==227 else 'CPI'
            c=calendar[calendar.release_family.eq(family)]
            y=x.merge(c,left_on='date',right_on='release_date',how='left',validate='one_to_one')
            y['official_utc']=pd.to_datetime(y.event_time_utc,utc=True)
            y['evidence']='current official archived schedule; not an original receipt'
        elif series['eventId']==294:
            y=x.merge(claims,left_on='date',right_on='release_date',how='left',validate='one_to_one')
            y['official_utc']=pd.to_datetime(y.embargo_lift_utc,utc=True)
            y['evidence']='retained official printed embargo-header facts; not an original receipt'
        else:
            y=x.copy();y['release_date']=None;y['source_url']=None
            y['official_utc']=pd.to_datetime(pd.Series([None]*len(y),index=y.index),utc=True)
            y['evidence']='no matching agency calendar in this saved packet'
        matched=y.release_date.notna();timed=y.official_utc.notna();same=y.utc.eq(y.official_utc)
        summary.append({'series':series['label'],'series_rows':len(y),'actual_and_forecast':int((y.actual.notna()&y.forecast.notna()).sum()),
                        'official_date_matches':int(matched.sum()),'official_clock_facts':int(timed.sum()),
                        'clock_matches':int((same&timed).sum()),'clock_discrepancies':int((~same&timed).sum())})
        for z in y.to_dict('records'):
            original=z['utc'];official=z['official_utc'];corrected=official if pd.notna(official) else None
            rows.append({'event_id':series['eventId'],'series':series['label'],'occurrence_id':z['occurrenceId'],
                         'release_date':z['date'],'vendor_utc':str(original),'official_clock_utc':str(official) if pd.notna(official) else None,
                         'derived_clock_utc':str(corrected) if corrected is not None else None,
                         'clock_changed':bool(pd.notna(official) and original!=official),'source_url':z['source_url'],
                         'evidence':z['evidence'],'forecast_available_at':None,'actual_receipt_at':None,'return_admitted':False})
    OUT.mkdir(parents=True,exist_ok=True)
    pd.DataFrame(summary).to_csv(OUT/'coverage.csv',index=False)
    pd.DataFrame(rows).to_csv(OUT/'clock_sidecar.csv',index=False)
    manifest={'return_tests':0,'source_macro_sha256':hashlib.sha256(raw).hexdigest(),
              'calendar':{'path':CAL,'sha256':hashlib.sha256(raw_cal).hexdigest()},
              'claims':{'path':CLAIMS,'sha256':hashlib.sha256(raw_claims).hexdigest()},
              'source_values_modified':False,'clock_corrections':int(sum(z['clock_changed'] for z in rows)),
              'return_admitted':False,'remaining':['pre-release forecast history/provenance','first-actual vintages and corrections','publication-to-decision availability','retail official clock cross-check','12 claims embargo times'],
              'primary_payroll_crosscheck':{'url':'https://www.bls.gov/news.release/archives/empsit_03062020.pdf',
                  'inspected':'page 1, embargo header and headline, 2026-11-09','printed_clock':'2020-03-06 08:30 EST',
                  'utc':'2020-03-06T13:30:00Z','payroll_headline_thousands':273,
                  'caveat':'PDF says reissued September 23, 2020; it is not an original March HTTP/feed receipt.'}}
    (OUT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(pd.DataFrame(summary).to_string(index=False))
    assert hashlib.sha256(MACRO.read_bytes()).hexdigest()==manifest['source_macro_sha256']
    assert manifest['clock_corrections']==1


if __name__=='__main__':main()
