"""Archive free primary clock evidence; add sidecars without changing fund data."""
import csv, datetime as dt, gzip, hashlib, io, json, re, sys
from pathlib import Path
from html.parser import HTMLParser
from codex_new_data_20261108 import read_url

OUT=Path('agents/codex/inputs/gold_clocks_20261108')
URLS={
 'sponsor_20181220':'https://www.sec.gov/Archives/edgar/data/1415311/000119312518354569/d677409dex991.htm',
 'rule_20181227':'https://www.govinfo.gov/content/pkg/FR-2018-12-27/html/2018-28007.htm',
 'prospectus_201901':'https://www.sec.gov/Archives/edgar/data/1415311/000119312519001612/d652113d424b3.htm',
 'prospectus_201903':'https://www.sec.gov/Archives/edgar/data/1415311/000119312519090686/d702010d424b3.htm',
 'prospectus_202210':'https://www.sec.gov/Archives/edgar/data/1415311/000119312522254074/d395346d424b3.htm',
 'annual_2019':'https://www.sec.gov/Archives/edgar/data/1415311/000119312520056815/d816057d10k.htm',
 'sponsor_2020_10k':'https://www.proshares.com/globalassets/proshares/documents/10k/pstii_10k_123120.pdf',
 'sponsor_2018_10k_probe':'https://www.proshares.com/globalassets/proshares/documents/10k/pstii_10k_123118.pdf',
 'sponsor_2020q3':'https://www.proshares.com/globalassets/proshares/documents/10q/pstii_10q_09302020.pdf',
 'sponsor_current_UGL':'https://www.proshares.com/our-etfs/leveraged-and-inverse/ugl',
 'sponsor_current_GLL':'https://www.proshares.com/our-etfs/leveraged-and-inverse/gll'}

class Text(HTMLParser):
 def __init__(self):super().__init__();self.chunks=[];self.skip=0
 def handle_starttag(self,t,a):
  if t in ('script','style'):self.skip+=1
  if t in ('p','tr','div','br'):self.chunks.append('\n')
 def handle_endtag(self,t):
  if t in ('script','style'):self.skip=max(0,self.skip-1)
 def handle_data(self,s):
  if not self.skip:self.chunks.append(s)

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,x):
 with p.open('x',encoding='utf-8') as f:json.dump(x,f,indent=2)
def source_paths():
 p=Path('agents/codex/inputs/new_data_primary_local_20261108')
 return [x for x in p.rglob('*') if x.is_file() and ('UGL' in x.name or 'GLL' in x.name)]

def fetch():
 OUT.mkdir(exist_ok=False);(OUT/'raw').mkdir();(OUT/'text').mkdir()
 before={str(p):sha(p) for p in source_paths()};receipts=[]
 for name,url in URLS.items():
  r={'id':name,'url':url,'requested_at_utc':dt.datetime.utcnow().isoformat()+'Z'}
  try:
   b,h,u=read_url(url,25);ext='.pdf' if b.startswith(b'%PDF') else '.html';p=OUT/'raw'/(name+ext+'.gz')
   with p.open('xb') as f:
    with gzip.GzipFile(filename='',mode='wb',fileobj=f,mtime=0) as z:z.write(b)
   assert gzip.decompress(p.read_bytes())==b
   r.update(status='SAVED_NOT_CLOCK_ADMITTED',path=str(p.relative_to(OUT)),bytes=len(b),sha256=hashlib.sha256(b).hexdigest(),compressed_bytes=p.stat().st_size,compressed_sha256=sha(p),headers={k:v for k,v in h.items() if k.lower() in ('date','last-modified','etag','content-type')},final_url=u)
   if ext=='.html':
    parser=Text();parser.feed(b.decode('utf-8','replace'));s=''.join(parser.chunks);(OUT/'text'/(name+'.txt')).write_text(s,encoding='utf-8')
  except Exception as e:r.update(status='FAILED',error=str(e))
  receipts.append(r);print(name,r['status'],flush=True)
 dump(OUT/'acquisition_receipt.json',receipts)
 assert before=={str(p):sha(p) for p in source_paths()}
 dump(OUT/'preserved_input_hashes.json',before)

def sidecar():
 rs=[]
 for ticker in ('UGL','GLL'):
  p=Path('agents/codex/inputs/new_data_primary_local_20261108/normalized')/(ticker+'.csv')
  for r in csv.DictReader(p.open()):
   d=r['date']
   if not '2018-01-01'<=d<='2022-12-31':continue
   if d<'2019-01-04':nav='15:00 Europe/London (usually 10:00 ET; DST mismatch varies)';cutoff='09:30 ET printed policy; exceptions/conflicting older rule unresolved';benchmark='LBMA Gold Price PM';era='pre_change'
   elif d<'2019-01-07':nav='13:30';cutoff='13:00';benchmark='TRANSITION_VERIFY_ACTUAL_BENCHMARK';era='transition'
   else:nav='13:30';cutoff='13:00';benchmark='Bloomberg Gold Subindex';era='post_change'
   rs.append({'fund':ticker,'date':d,'normal_NAV_clock_policy':nav,'normal_AP_order_cutoff_policy':cutoff,'benchmark_policy':benchmark,'era':era,'holiday_exception_verified':'no','NAV_public_available_at':'','assets_public_available_at':'','shares_public_available_at':'','actual_reset_execution_time':'','clock_evidence':'see evidence_matrix.json; policy only, not day-specific execution proof'})
 with (OUT/'design_clock_sidecar.csv').open('x',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rs[0]));w.writeheader();w.writerows(rs)
 counts={t:{e:sum(r['fund']==t and r['era']==e for r in rs) for e in ('pre_change','transition','post_change')} for t in ('UGL','GLL')}
 dump(OUT/'sidecar_qa.json',{'rows':len(rs),'counts':counts,'all_actual_availability_and_execution_clocks_unknown':all(not r['NAV_public_available_at'] and not r['actual_reset_execution_time'] for r in rs)})
 print(counts)

def pdf_text():
 from pypdf import PdfReader
 hits=[]
 for name in ('sponsor_2020_10k','sponsor_2020q3'):
  reader=PdfReader(io.BytesIO(gzip.decompress((OUT/'raw'/(name+'.pdf.gz')).read_bytes())))
  pages=[]
  for i,p in enumerate(reader.pages):
   s=p.extract_text() or '';pages.append('PAGE {}\n{}'.format(i+1,s))
   if re.search(r'January\s+7,?\s+2019|NAV Calculation Time|time and manner|3:00 p.m. London',s):
    hits.append({'source':name,'page_1_based':i+1,'text':s})
  with (OUT/'text'/(name+'.txt')).open('x',encoding='utf-8') as f:f.write('\n\n'.join(pages))
 dump(OUT/'pdf_page_evidence.json',hits)
 print('Relevant PDF pages:',[(x['source'],x['page_1_based']) for x in hits])

def verify():
 receipts=sum((json.loads((OUT/n).read_text()) for n in ('acquisition_receipt.json','additional_receipt.json','annual_tables_receipt.json')),[])
 saved=[r for r in receipts if 'path' in r]
 for r in saved:
  p=OUT/Path(r['path'].replace('\\','/'));b=gzip.decompress(p.read_bytes())
  assert len(b)==r['bytes'] and hashlib.sha256(b).hexdigest()==r['sha256']
  assert p.stat().st_size==r['compressed_bytes'] and sha(p)==r['compressed_sha256']
 original={k.replace('\\','/'):v for k,v in json.loads((OUT/'preserved_input_hashes.json').read_text()).items()}
 assert original=={p.as_posix():sha(p) for p in source_paths()}
 rows=list(csv.DictReader((OUT/'design_clock_sidecar.csv').open()))
 for t in ('UGL','GLL'):
  expected=[r['date'] for r in csv.DictReader((Path('agents/codex/inputs/new_data_primary_local_20261108/normalized')/(t+'.csv')).open()) if '2018-01-01'<=r['date']<='2022-12-31']
  assert [r['date'] for r in rows if r['fund']==t]==expected
 assert all(not r[k] for r in rows for k in ('NAV_public_available_at','assets_public_available_at','shares_public_available_at','actual_reset_execution_time'))
 result={'saved_sources_verified':len(saved),'failed_requests_preserved':len(receipts)-len(saved),'original_fund_files_unchanged':len(original),'sidecar_rows_verified':len(rows),'no_invented_publication_or_execution_clocks':True,'script_sha256':sha(Path(__file__))}
 # Verification is repeatable; only replace this task's derived QA receipt.
 (OUT/'verification.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
 print('Verified sources {}, original fund files {}, sidecar rows {}'.format(len(saved),len(original),len(rows)))

def more():
 urls={'prospectus_201802':'https://www.sec.gov/Archives/edgar/data/1415311/000119312518027791/d460791ds3a.htm','annual_2018':'https://www.sec.gov/Archives/edgar/data/1415311/000119312519060564/d611404d10k.htm','prospectus_202103':'https://www.sec.gov/Archives/edgar/data/1415311/000119312521073428/d222360ds3a.htm'}
 rec=[]
 for name,url in urls.items():
  r={'id':name,'url':url,'requested_at_utc':dt.datetime.utcnow().isoformat()+'Z'}
  try:
   b,h,u=read_url(url,25);p=OUT/'raw'/(name+'.html.gz')
   with p.open('xb') as f:
    with gzip.GzipFile(filename='',mode='wb',fileobj=f,mtime=0) as z:z.write(b)
   parser=Text();parser.feed(b.decode('utf-8','replace'));(OUT/'text'/(name+'.txt')).write_text(''.join(parser.chunks),encoding='utf-8')
   r.update(status='SAVED_NOT_CLOCK_ADMITTED',path=str(p.relative_to(OUT)),bytes=len(b),sha256=hashlib.sha256(b).hexdigest(),compressed_bytes=p.stat().st_size,compressed_sha256=sha(p),final_url=u)
  except Exception as e:r.update(status='FAILED',error=str(e))
  rec.append(r);print(name,r['status'],flush=True)
 dump(OUT/'additional_receipt.json',rec)

def annual_tables():
 rec=[]
 for name,url in {'annual_2021_clock_table':'https://www.sec.gov/Archives/edgar/data/1415311/000119312522054559/R18.htm','annual_2022_clock_table':'https://www.sec.gov/Archives/edgar/data/1415311/000119312523054105/R18.htm'}.items():
  b,h,u=read_url(url,25);p=OUT/'raw'/(name+'.html.gz')
  with p.open('xb') as f:
   with gzip.GzipFile(filename='',mode='wb',fileobj=f,mtime=0) as z:z.write(b)
  parser=Text();parser.feed(b.decode('utf-8','replace'))
  with (OUT/'text'/(name+'.txt')).open('x',encoding='utf-8') as f:f.write(''.join(parser.chunks))
  rec.append({'id':name,'url':url,'requested_at_utc':dt.datetime.utcnow().isoformat()+'Z','path':str(p.relative_to(OUT)),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'compressed_bytes':p.stat().st_size,'compressed_sha256':sha(p),'final_url':u,'status':'SAVED_NOT_CLOCK_ADMITTED'})
 dump(OUT/'annual_tables_receipt.json',rec)
 print('Saved annual clock tables',len(rec))

if __name__=='__main__':{'fetch':fetch,'sidecar':sidecar,'more':more,'pdf_text':pdf_text,'verify':verify,'annual_tables':annual_tables}[sys.argv[1]]()
