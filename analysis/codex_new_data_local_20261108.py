"""Primary intake follow-up: immutable download receipts, reconciliation, packaging."""
import csv, datetime as dt, decimal, gzip, hashlib, io, json, re, shutil, sys
from pathlib import Path
from urllib.parse import urljoin, urlparse
from concurrent.futures import ThreadPoolExecutor
from codex_new_data_20261108 import read_url

ROOT=Path('agents/codex/inputs/new_data_primary_local_20261108')
P=Path('scratch_data/new_data_primary_local_02/raw')
M=Path('scratch_data/new_data_macro_local_02/raw')
D=decimal.Decimal
def dump(p,x):
    p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('x',encoding='utf-8') as f: json.dump(x,f,indent=2,default=str)
def rows(p): return list(csv.DictReader(p.open(encoding='utf-8-sig',newline='')))
def savecsv(p,rs):
    if not rs:return
    p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('x',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(rs[0]));w.writeheader();w.writerows(rs)
def date(s):return dt.datetime.strptime(s,'%m/%d/%Y').date().isoformat()
def links(text,base):return sorted(set(urljoin(base,x.replace('&amp;','&')) for x in re.findall(r'href=[\"\x27]([^\"\x27]+)',text,re.I)))
def documents():
    dest=Path('scratch_data/new_data_documents_local_01');dest.mkdir(exist_ok=False)
    rec=[];seen=set()
    def fetch(url):
        r={'url':url,'received_at_utc':dt.datetime.utcnow().isoformat()+'Z'}
        try:
            b,h,u=read_url(url,25);name=hashlib.sha256(url.encode()).hexdigest()[:20]+Path(urlparse(u).path).suffix
            (dest/name).write_bytes(b);r.update(status='SAVED',path=name,bytes=len(b),sha256=hashlib.sha256(b).hexdigest(),final_url=u,content_type=h.get('Content-Type',''))
            return r,b
        except Exception as e:r.update(status='FAILED',error=str(e));return r,b''
    seeds=['https://treasurydirect.gov/auctions/buy-backs/', 'https://www.newyorkfed.org/markets/treasury-reinvestments-purchases.html','https://markets.newyorkfed.org/static/docs/markets-api.html']
    candidates=[]
    for url in seeds:
        r,b=fetch(url);rec.append(r);seen.add(url)
        for u in links(b.decode('utf-8','replace'),url):
            if urlparse(u).hostname in ('treasurydirect.gov','www.treasurydirect.gov') and any(x in u.lower() for x in ('buyback','buy-back')):candidates.append(u)
            if urlparse(u).hostname=='www.newyorkfed.org' and any(x in u.lower() for x in ('schedule','operating_schedule','treasury_schedule')):candidates.append(u)
    for t in ('UGL','GLL','UCO','SCO','BOIL','KOLD'):
        for u in links((P/'proshares'/(t+'-page.html')).read_text(encoding='utf-8'), 'https://www.proshares.com'):
            if any(x in u.lower() for x in ('prospect','summary_pro','statutory')) and urlparse(u).hostname in ('www.proshares.com','www.proshares.comassets','prospectus.proshares.com'):candidates.append(u)
    first=sorted(set(candidates)-seen)
    with ThreadPoolExecutor(max_workers=6) as ex:
        for r,b in ex.map(fetch,first):
            rec.append(r);seen.add(r['url'])
            if 'html' in r.get('content_type','').lower():
                for u in links(b.decode('utf-8','replace'),r['url']):
                    if urlparse(u).hostname in ('treasurydirect.gov','www.treasurydirect.gov') and any(x in u.lower() for x in ('.xml','.pdf','.xsd')):candidates.append(u)
    second=sorted(set(candidates)-seen)
    with ThreadPoolExecutor(max_workers=6) as ex:
        for r,b in ex.map(fetch,second):rec.append(r)
    dump(dest/'receipt.json',rec)
    print('Documents',len(rec),'saved',sum(r['status']=='SAVED' for r in rec))

def audit():
    ROOT.mkdir(exist_ok=False);summary={'funds':{},'indices':{},'macro':{}}
    secondary=Path('agents/codex/inputs/new_data_20261108/audit/normalized')
    for t in ('UGL','GLL','UCO','SCO','BOIL','KOLD'):
        raw=rows(P/'proshares'/(t+'-historical_nav.csv'));norm=[];bad=0;zero=0
        old={r['date']:r for r in rows(secondary/(t+'_nav_assets_shares.csv'))};diff=[];common=0
        for r in raw:
            d=date(r['Date']);nav=D(r['NAV']);shares=D(r['Shares Outstanding (000)'])*1000;assets=D(r['Assets Under Management']);err=abs(nav*shares/assets-1) if assets else D(1)
            bad+=err>D('.01');zero+=shares<=0
            norm.append({'date':d,'nav_usd_source_basis':str(nav),'prior_nav_usd_source_basis':r['Prior NAV'],'nav_change_percent':r['NAV Change (%)'],'nav_change_usd':r['NAV Change ($)'],'shares_outstanding_000_source':r['Shares Outstanding (000)'],'shares_outstanding_source_basis':str(shares),'net_assets_usd':str(assets),'relative_identity_error':str(err),'available_at':''})
            if d in old:
                common+=1;o=old[d]
                ds={k:str(D(v)-D(o[k])) for k,v in [('nav_usd_source_basis',nav),('shares_outstanding_source_basis',shares),('net_assets_usd',assets)]}
                if any(D(v)!=0 for v in ds.values()):diff.append(dict(date=d,**ds))
        assert len({r['date'] for r in norm})==len(norm)
        savecsv(ROOT/'normalized'/(t+'.csv'),sorted(norm,key=lambda r:r['date']));savecsv(ROOT/'reconciliation'/(t+'_differences.csv'),diff)
        summary['funds'][t]={'rows':len(norm),'first':min(r['date'] for r in norm),'last':max(r['date'] for r in norm),'overlap_dates':common,'differing_rows_decimal_exact':len(diff),'identity_gt_1pct':bad,'nonpositive_shares':zero,'design_identity_gt_1pct':sum(D(r['relative_identity_error'])>D('.01') for r in norm if '2018'<=r['date']<'2023')}
    for t in ('VVIX','SKEW','VIX9D','GVZ','OVX'):
        raw=rows(P/'cboe'/(t+'_History.csv'));norm=[]
        for r in raw:
            c=r.get(t) or r.get('CLOSE');norm.append({'date':date(r['DATE']),'close_index_points':c,'available_at':''})
        oldfile=secondary/(t+'_daily_close.csv');old={r['date']:r['close_index_points'] for r in rows(oldfile)} if oldfile.exists() else {};diff=[r for r in norm if r['date'] in old and D(r['close_index_points'])!=D(old[r['date']])]
        savecsv(ROOT/'normalized'/(t+'.csv'),norm);savecsv(ROOT/'reconciliation'/(t+'_differences.csv'),diff)
        summary['indices'][t]={'rows':len(norm),'first':min(r['date'] for r in norm),'last':max(r['date'] for r in norm),'overlap':sum(r['date'] in old for r in norm),'different_closes':len(diff),'SKEW_dates':{d:any(r['date']==d for r in norm) for d in ('2018-12-03','2019-07-05')} if t=='SKEW' else None}
    allops=[];rates=[]
    for y in range(2017,2027):
        ops=json.loads((M/'nyfed'/('treasury_results_%d.json'%y)).read_text())['treasury']['auctions'];rr=json.loads((M/'nyfed'/('reference_rates_%d.json'%y)).read_text())['refRates'];allops+=ops;rates+=rr
        summary['macro'][str(y)]={'operations':len(ops),'details':sum(len(o.get('details',[])) for o in ops),'rates':len(rr),'first_operation':min((o['operationDate'] for o in ops),default=None),'last_operation':max((o['operationDate'] for o in ops),default=None)}
    assert all(r['effectiveDate']<='2026-11-08' for r in rates)
    keys=[(o['operationId'],o['operationDate']) for o in allops];assert len(keys)==len(set(keys))
    flat=[dict((k,v) for k,v in o.items() if k!='details') for o in allops]
    # JSON preserves variable fields and nested details losslessly; blank availability separate.
    dump(ROOT/'normalized'/'nyfed_operations.json',[dict(o,available_at='') for o in allops]);dump(ROOT/'normalized'/'nyfed_rates.json',[dict(r,available_at='') for r in rates])
    summary['rate_types']={t:{'rows':len([r for r in rates if r['type']==t]),'first':min(r['effectiveDate'] for r in rates if r['type']==t),'last':max(r['effectiveDate'] for r in rates if r['type']==t)} for t in set(r['type'] for r in rates)}
    summary['buybacks']={}
    for t in ('operations','security_details'):
        pages=list((M/'treasury').glob('buybacks_'+t+'_page*.json'));js=[json.loads(p.read_text()) for p in pages];rs=sum((j['data'] for j in js),[])
        assert len(rs)==int(js[0]['meta']['total-count']);assert len(pages)==int(js[0]['meta']['total-pages'])
        savecsv(ROOT/'normalized'/('buybacks_'+t+'.csv'),[dict(r,available_at='') for r in rs]);summary['buybacks'][t]={'rows':len(rs),'pages':len(pages),'first':min(r['operation_date'] for r in rs),'last':max(r['operation_date'] for r in rs)}
    # Exact raw bytes compressed for transport, with source and compressed hashes.
    files=[]
    for label,src in [('primary',P.parent),('macro',M.parent),('documents',Path('scratch_data/new_data_documents_local_01')),('sandbox_primary',Path('scratch_data/new_data_primary_local_01')),('sandbox_macro',Path('scratch_data/new_data_macro_local_01'))]:
        for p in sorted(src.rglob('*')):
            if not p.is_file():continue
            b=p.read_bytes();target=ROOT/'transport'/label/(str(p.relative_to(src))+'.gz');target.parent.mkdir(parents=True,exist_ok=True)
            with target.open('xb') as f:
                with gzip.GzipFile(filename='',mode='wb',fileobj=f,mtime=0) as z:z.write(b)
            c=target.read_bytes();assert gzip.decompress(c)==b
            files.append({'path':str(target.relative_to(ROOT)),'original_bytes':len(b),'original_sha256':hashlib.sha256(b).hexdigest(),'compressed_bytes':len(c),'compressed_sha256':hashlib.sha256(c).hexdigest()})
    dump(ROOT/'transport_manifest.json',files);dump(ROOT/'qa_summary.json',summary);print(json.dumps(summary,indent=2))

def supplement():
    dest=Path('scratch_data/new_data_supplement_local_01');dest.mkdir(exist_ok=False)
    jobs=[]
    ops=json.loads((M/'treasury/buybacks_operations_page001.json').read_text())['data']
    for o in ops:
        if o['operation_date']<'2024':continue
        for key in ('preliminary_ann_pdf','preliminary_ann_xml','final_ann_pdf','final_ann_xml','results_pdf','results_xml','special_ann_pdf'):
            for name in o[key].split(', '):
                if name!='null':jobs.append(('https://treasurydirect.gov/instit/annceresult/press/preanre/'+o['operation_date'][:4]+'/'+name,'doc',None))
    jobs.append(('https://home.treasury.gov/system/files/221/Tentative-Buyback-Schedule.xml','doc',None))
    jobs.append(('https://www.newyorkfed.org/markets/desk-operations/treasury-securities','doc',None))
    # Disjoint inclusive half-year queries check annual union/count completeness.
    for y in range(2017,2027):
        for typ,endpoint in [('operations','tsy/all/results/details'),('rates','rates/all')]:
            for start,end in [(str(y)+'-01-01',str(y)+'-06-30'),(str(y)+'-07-01',str(y)+'-12-31' if y<2026 else '2026-11-08')]:
                jobs.append(('https://markets.newyorkfed.org/api/'+endpoint+'/search.json?startDate='+start+'&endDate='+end,typ,y))
    rec=[];pieces={}
    def fetch(job):
        url,typ,y=job;r={'url':url,'kind':typ,'year':y,'received_at_utc':dt.datetime.utcnow().isoformat()+'Z'}
        try:
            b,h,u=read_url(url,25);name=hashlib.sha256(url.encode()).hexdigest()+('.json' if typ!='doc' else Path(urlparse(u).path).suffix or '.html');(dest/name).write_bytes(b)
            r.update(status='SAVED',path=name,bytes=len(b),sha256=hashlib.sha256(b).hexdigest(),headers={k:v for k,v in h.items() if k.lower() in ('date','content-type','etag','last-modified')})
            return r,b
        except Exception as e:r.update(status='FAILED',error=str(e));return r,b''
    with ThreadPoolExecutor(max_workers=6) as ex:
        for r,b in ex.map(fetch,sorted(set(jobs),key=lambda x:x[0])):
            rec.append(r)
            if r['status']=='SAVED' and r['kind']!='doc':
                j=json.loads(b);rs=j['treasury']['auctions'] if r['kind']=='operations' else j['refRates'];pieces.setdefault((r['kind'],r['year']),[]).extend(rs)
    checks=[]
    for (typ,y),rs in sorted(pieces.items()):
        annual=json.loads((M/'nyfed'/(('treasury_results_' if typ=='operations' else 'reference_rates_')+str(y)+'.json')).read_text());old=annual['treasury']['auctions'] if typ=='operations' else annual['refRates']
        same=sorted(json.dumps(r,sort_keys=True) for r in rs)==sorted(json.dumps(r,sort_keys=True) for r in old)
        checks.append({'kind':typ,'year':y,'annual_count':len(old),'halfyear_union_count':len(rs),'exact_record_multiset_match':same})
    dump(dest/'receipt.json',rec);dump(dest/'completeness_checks.json',checks)
    print('Supplement',len(rec),'saved',sum(r['status']=='SAVED' for r in rec),'annual partitions matched',sum(r['exact_record_multiset_match'] for r in checks),'of',len(checks))

def package_supplement():
    src=Path('scratch_data/new_data_supplement_local_01');files=[]
    for p in sorted(src.rglob('*')):
        if not p.is_file():continue
        b=p.read_bytes();target=ROOT/'transport'/'supplement'/(str(p.relative_to(src))+'.gz');target.parent.mkdir(parents=True,exist_ok=True)
        with target.open('xb') as f:
            with gzip.GzipFile(filename='',mode='wb',fileobj=f,mtime=0) as z:z.write(b)
        c=target.read_bytes();assert gzip.decompress(c)==b
        files.append({'path':str(target.relative_to(ROOT)),'original_bytes':len(b),'original_sha256':hashlib.sha256(b).hexdigest(),'compressed_bytes':len(c),'compressed_sha256':hashlib.sha256(c).hexdigest()})
    dump(ROOT/'supplement_manifest.json',files)

def prospectuses():
    dest=Path('scratch_data/new_data_supplement_local_01/prospectuses');dest.mkdir(exist_ok=False)
    rec=[];urls=set()
    for r in json.load(open('scratch_data/new_data_documents_local_01/receipt.json')):
        if 'regulatory-document' in r['url']:
            for u in links((Path('scratch_data/new_data_documents_local_01')/r['path']).read_text(encoding='utf-8'),r['url']):
                if u.endswith('.pdf') and 'proshares.com/' in u:urls.add(u)
    for u in sorted(urls):
        try:
            b,h,final=read_url(u,25);assert b.startswith(b'%PDF');name=Path(urlparse(u).path).name;(dest/name).write_bytes(b);rec.append({'url':u,'path':name,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'status':'SAVED'})
        except Exception as e:rec.append({'url':u,'status':'FAILED','error':str(e)})
    dump(dest/'receipt.json',rec);print(rec)

def finalize():
    import xml.etree.ElementTree as ET
    base=Path('scratch_data/new_data_supplement_local_01');rec=json.load((base/'receipt.json').open());checks=json.load((base/'completeness_checks.json').open());types={};invalid=[];xmlsamples=[]
    for r in rec:
        if r['status']!='SAVED':continue
        p=base/r['path'];b=p.read_bytes();assert hashlib.sha256(b).hexdigest()==r['sha256']
        ext=Path(urlparse(r['url']).path).suffix.lower()
        if ext=='.xml':
            try:
                root=ET.fromstring(b);types['valid_xml']=types.get('valid_xml',0)+1
                if len(xmlsamples)<5:xmlsamples.append({'url':r['url'],'root':root.tag,'fields':[(e.tag,e.text) for e in root.iter() if e.text and e.text.strip()][:25]})
            except Exception as e:invalid.append({'url':r['url'],'error':str(e)})
        elif ext=='.pdf':
            if not b.startswith(b'%PDF'):invalid.append({'url':r['url'],'error':'non-PDF body'})
            else:types['pdf']=types.get('pdf',0)+1
    precision={}
    for t in ('UGL','GLL','UCO','SCO','BOIL','KOLD'):
        p=ROOT/'reconciliation'/(t+'_differences.csv');rs=rows(p) if p.exists() else []
        precision[t]={k:{'changed_rows':sum(D(r[k])!=0 for r in rs),'max_abs_difference':str(max([abs(D(r[k])) for r in rs] or [D(0)]))} for k in ('nav_usd_source_basis','shares_outstanding_source_basis','net_assets_usd')}
    flags={'all_indices':'Current revised close series; original available_at and correction clock unknown; prelaunch/back-calculation status not newly certified for VVIX/SKEW/GVZ/OVX.', 'VIX9D':'Pre-October 2013 observations are back-calculated per retained original intake methodology review; not contemporary observations.', 'funds':'Decimal conversion is multiply thousands by 1000 only. No AUM/NAV share inference. All primary NAV/share values equal secondary values. Primary BOIL retains 82 zero shares and 1178 >1% identity failures.', 'documents':'Current prospectuses/schedules do not establish original 2018-22 mandate, reset execution or release clocks.'}
    dump(ROOT/'supplement_qa.json',{'requests':len(rec),'saved':sum(r['status']=='SAVED' for r in rec),'failures':[r for r in rec if r['status']!='SAVED'],'content_types':types,'invalid_document_payloads':invalid,'annual_partition_checks':checks,'xml_clock_samples':xmlsamples,'precision_comparison':precision})
    for t in ('VVIX','SKEW','VIX9D','GVZ','OVX'):
        rs=rows(ROOT/'normalized'/(t+'.csv'));ds=[r['date'] for r in rs]
        assert len(ds)==len(set(ds)) and all(D(r['close_index_points'])>0 and r['available_at']=='' for r in rs)
    dump(ROOT/'historical_clock_flags.json',flags)
    dump(ROOT/'dispositions.json',{'BOIL':'QUARANTINED_ENTIRE_DATASET_PRIMARY_STILL_FAILS_IDENTITY','other_funds':'PRIMARY_RECONCILED_NOT_HISTORICAL_CLOCK_ADMITTED','indices':'PRIMARY_CLOSE_ONLY_NOT_ORIGINAL_VINTAGE_ADMITTED','macro':'POST_EVENT_RESULTS_AND_REVISED_RATES_NOT_PRE_EVENT_SIGNALS'})
    print('Supplement requests',len(rec),'saved',sum(r['status']=='SAVED' for r in rec),'invalid',len(invalid),'partition checks',sum(c['exact_record_multiset_match'] for c in checks),'of',len(checks))

def clocks():
    import xml.etree.ElementTree as ET
    base=Path('scratch_data/new_data_supplement_local_01');out=[]
    for r in json.load((base/'receipt.json').open()):
        if r['status']!='SAVED' or not r['url'].endswith('.xml') or 'preanre' not in r['url']:continue
        root=ET.fromstring((base/r['path']).read_bytes());fields={e.tag.split('}')[-1]:e.text for e in root if e.text}
        out.append({'url':r['url'],'operation_status':fields.get('operationStatus',''),'announcement_DTM_source':fields.get('announcementDTM',''),'result_DTM_source':fields.get('resultsDTM',fields.get('resultDTM','')),'operation_start_DTM_source':fields.get('operationStartDTM',''),'operation_close_DTM_source':fields.get('operationCloseDTM',''),'settlement_date':fields.get('settlementDT',''),'available_at':''})
    savecsv(ROOT/'normalized'/'buyback_document_clocks.csv',out)
    offsets={}
    for r in out:
        s=r['operation_start_DTM_source']
        if s:offsets[s[-6:]]=offsets.get(s[-6:],0)+1
    dump(ROOT/'document_clock_qa.json',{'document_rows':len(out),'operation_start_offsets':offsets,'notice':'Source announcement/result clocks are not verified public first-receipt clocks; available_at remains unknown. Filenames are not used as announcement timestamps.'})

if __name__=='__main__':
    {'documents':documents,'audit':audit,'supplement':supplement,'package-supplement':package_supplement,'prospectuses':prospectuses,'finalize':finalize,'clocks':clocks}[sys.argv[1]]()
