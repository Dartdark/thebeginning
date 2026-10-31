"""Downloaded input census only. No strategy signals, spread changes or returns."""
from pathlib import Path
import hashlib,json
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
raw=Path('/workspace/commodity_roll_data')
out=ROOT/'analysis/outputs/codex_commodity_roll_acquisition_20261031'
out.mkdir(parents=True,exist_ok=True)
rows=[]
for name in ['WHEAT','WHEAT_mini']:
 p=raw/(name+'.csv');f=pd.read_csv(p,parse_dates=['DATETIME'])
 s=f[f.DATETIME.between('2018-01-01','2022-12-31')].copy()
 daily=s.groupby(s.DATETIME.dt.normalize()).agg(rows=('PRICE','size'),valid_price=('PRICE',lambda x:x.notna().sum()),valid_forward=('FORWARD',lambda x:x.notna().sum()))
 daily.to_csv(out/(name+'_date_census.csv'))
 valid=s[['PRICE','FORWARD']].notna().all(axis=1)
 rows.append(dict(instrument=name,raw_path=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),
  git_blob_sha=hashlib.sha1(f'blob {p.stat().st_size}\0'.encode()+p.read_bytes()).hexdigest(),
  first=str(f.DATETIME.min()),last=str(f.DATETIME.max()),design_rows=len(s),design_observed_dates=len(daily),
  rows_with_both_price_forward=int(valid.sum()),dates_with_any_paired_observation=int(s.loc[valid,'DATETIME'].dt.normalize().nunique()),
  missing_by_column=s.isna().sum().to_dict(),duplicate_timestamps=int(s.DATETIME.duplicated().sum()),
  price_contract_months=sorted((s.PRICE_CONTRACT.astype(int)//100%100).unique().tolist()),
  unique_design_identity_triples=s[['PRICE_CONTRACT','CARRY_CONTRACT','FORWARD_CONTRACT']].drop_duplicates().to_dict('records'),
  limitation='Any paired intraday observation is NOT a certified synchronized close or complete event path'))
(out/'metadata.json').write_text(json.dumps(dict(pinned_source_commit='164328bd76d2937d3dd61491377704c488283bc2',files=rows,economic_trials=0,returns_computed=False),indent=2)+'\n')
print(json.dumps([{k:v for k,v in r.items() if k not in ['unique_design_identity_triples','missing_by_column']} for r in rows],indent=2))
