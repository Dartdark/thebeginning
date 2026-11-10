import sys,json,hashlib,collections,csv
from pathlib import Path
p=Path(__file__).parent
sys.path.insert(0,str(p/'packages'))
import pyarrow as pa, pyarrow.parquet as pq
import numpy as np
out=[]
for symbol in ['ES','NQ']:
 f=p/(symbol+'.parquet'); t=pq.read_table(f); ts=t['ts'].cast(pa.int64()).to_numpy(); dt=ts.astype('datetime64[us]'); years=dt.astype('datetime64[Y]').astype(str); m=years<'2018'
 a={c:t[c].to_numpy() for c in ['open','high','low','close','volume']}
 dest=p/(symbol+'_1min_pre2018_UTC.csv')
 with dest.open('w',newline='') as h:
  w=csv.writer(h); w.writerow(['timestamp_utc','symbol','open','high','low','close','volume'])
  for i in np.flatnonzero(m): w.writerow([str(dt[i])+'Z',symbol]+[a[c][i] for c in a])
 out.append(dict(symbol=symbol,source='https://huggingface.co/datasets/syncster-data/historical-market-data/resolve/main/data/futures/1m/'+symbol+'.parquet',source_sha256=hashlib.sha256(f.read_bytes()).hexdigest(),source_bytes=f.stat().st_size,rows=t.num_rows,first_utc=str(dt.min())+'Z',last_utc=str(dt.max())+'Z',year_rows=dict(collections.Counter(years)),extract=dest.name,extract_rows=int(m.sum()),extract_sha256=hashlib.sha256(dest.read_bytes()).hexdigest(),duplicates=len(ts)-len(np.unique(ts)),out_of_order=int((np.diff(ts)<0).sum()),off_minute=int((ts%60000000!=0).sum()),bad_ohlc=int(((a['low']>np.minimum(a['open'],a['close']))|(a['high']<np.maximum(a['open'],a['close']))|(a['low']>a['high'])).sum()),nulls={c:int(np.isnan(v).sum()) for c,v in a.items()},negative_volume=int((a['volume']<0).sum())))
(p/'manifest_qa.json').write_text(json.dumps(out,indent=2))
print(json.dumps(out,indent=2))
