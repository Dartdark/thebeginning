import csv,json,hashlib,urllib.request,datetime,time,os,sys,io
from pathlib import Path
OUT=Path(sys.argv[1]); OUT.mkdir(parents=True,exist_ok=False)
(OUT/'raw').mkdir()
receipt=[]
series='DGS1MO DGS3MO DGS6MO DGS1 DGS2 DGS3 DGS5 DGS7 DGS10 DGS20 DGS30 DFII5 DFII10 DFII20 DFII30 T5YIE T10YIE T10Y2Y T10Y3M DFF FEDFUNDS DFEDTARL DFEDTARU DTWEXBGS DEXUSEU DEXJPUS DEXUSUK WALCL WRESBAL WTREGEN RRPONTSYD WDTGAL M2SL CPIAUCSL CPILFESL PCEPI PCEPILFE PAYEMS UNRATE ICSA CCSA INDPRO RSAFS HOUST PERMIT DCOILWTICO DCOILBRENTEU DHHNGSP'.split()
def fetch(name,url,kind,extra=None):
    entry={'name':name,'url':url,'kind':kind,'retrieved_at_utc':datetime.datetime.utcnow().isoformat()+'Z','available_at':None,'historical_vintage':'current snapshot, not original-release history'}
    if extra: entry.update(extra)
    try:
        req=urllib.request.Request(url,headers={})
        with urllib.request.urlopen(req,timeout=12) as r:
            b=r.read(8000001); entry.update(status=r.status,headers=dict(r.headers))
        if len(b)>8000000: raise ValueError('8 MB response cap')
        if kind=='fred_csv':
            rows=list(csv.DictReader(io.StringIO(b.decode('utf-8-sig'))))
            if not rows or name not in rows[0] or 'observation_date' not in rows[0]: raise ValueError('unexpected CSV schema')
            valid=[x for x in rows if x[name] not in ('','.')]
            for x in valid: float(x[name])
            dates=[x['observation_date'] for x in rows]
            entry.update(rows=len(rows),nonmissing=len(valid),start=dates[0],end=dates[-1],duplicate_dates=len(dates)-len(set(dates)))
        else:
            data=json.loads(b)
            if not isinstance(data,list) or len(data)!=2 or not isinstance(data[0],dict) or data[0].get('pages')!=1: raise ValueError('unexpected JSON or unhandled pagination')
            entry.update(rows=len(data[1] or []),nonmissing=sum(x.get('value') is not None for x in (data[1] or [])),page_metadata=data[0])
        entry.update(bytes=len(b),sha256=hashlib.sha256(b).hexdigest(),file='raw/'+name+('.csv' if kind=='fred_csv' else '.json'),outcome='saved')
        (OUT/entry['file']).write_bytes(b)
    except Exception as e: entry.update(outcome='failed',error=str(e))
    receipt.append(entry)
    (OUT/'manifest.json').write_text(json.dumps(receipt,indent=2),encoding='utf-8')
    print(name,entry['outcome'],entry.get('rows',''),entry.get('error',''),flush=True)
    time.sleep(1)
for s in series:
    fetch(s,'https://fred.stlouisfed.org/graph/fredgraph.csv?id='+s+'&cosd=1990-01-01&coed=2026-11-09','fred_csv',{'source_page':'https://fred.stlouisfed.org/series/'+s})
for s in 'NY.GDP.MKTP.KD.ZG FP.CPI.TOTL.ZG NE.TRD.GNFS.ZS NY.GDP.MKTP.CD'.split():
    fetch('WB_'+s,'https://api.worldbank.org/v2/country/USA;CHN;JPN;GBR;CAN;EMU/indicator/'+s+'?format=json&date=1990:2025&per_page=20000','worldbank_json',{'source_page':'https://data.worldbank.org/indicator/'+s})
print('TOTAL',sum(x['outcome']=='saved' for x in receipt),len(receipt),flush=True)
