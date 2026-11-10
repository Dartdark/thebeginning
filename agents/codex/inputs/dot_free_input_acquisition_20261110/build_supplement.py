"""dot: source-only acquisition and normalization, not a strategy/return test.
Run from any empty output directory: python build_supplement.py
Requires Python standard library and curl. Source HTML/ZIP remain local; compact outputs are shareable.
"""
import csv,datetime,hashlib,io,json,pathlib,subprocess,zipfile
P=pathlib.Path('.')
S=[
(2018,'20170511b','2017-05-11T14:00:00-04:00','01-31 03-21 05-02 06-13 08-01 09-26 11-08 12-19'),
(2019,'20180525a','2018-05-25T12:00:00-04:00','01-30 03-20 05-01 06-19 07-31 09-18 10-30 12-11'),
(2020,'20190517a','2019-05-17T10:00:00-04:00','01-29 03-18 04-29 06-10 07-29 09-16 11-05 12-16'),
(2021,'20200702a','2020-07-02T10:00:00-04:00','01-27 03-17 04-28 06-16 07-28 09-22 11-03 12-15'),
(2022,'20210604a','2021-06-04T11:00:00-04:00','01-26 03-16 05-04 06-15 07-27 09-21 11-02 12-14'),
(2023,'20220624a','2022-06-24T14:00:00-04:00','02-01 03-22 05-03 06-14 07-26 09-20 11-01 12-13'),
(2024,'20230623a','2023-06-23T11:30:00-04:00','01-31 03-20 05-01 06-12 07-31 09-18 11-07 12-18'),
(2025,'20240809a','2024-08-09T13:30:00-04:00','01-29 03-19 05-07 06-18 07-30 09-17 10-29 12-10'),
(2026,'20240809a','2024-08-09T13:30:00-04:00','01-28 03-18 04-29 06-17 07-29 09-16 10-28 12-09')]
receipts=[]
def acquire(name,url):
 p=P/name
 if not p.exists(): subprocess.run(['curl','-f','-L','--max-time','45','-sS',url,'-o',str(p)],check=True)
 b=p.read_bytes(); receipts.append(dict(filename=name,url=url,bytes=len(b),sha256=hashlib.sha256(b).hexdigest(),verified_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),historical_receipt_verified=False));return b
rows=[]
for year,key,published,dates in S:
 url=f'https://www.federalreserve.gov/newsevents/pressreleases/monetary{key}.htm'
 b=acquire('fed2025_2026.html' if year>=2025 else f'fed{year}.html',url)
 if b'Federal Open Market Committee' not in b: raise ValueError('Unexpected source HTML')
 for d in dates.split():
  date=f'{year}-{d}'
  rows.append(dict(meeting_end_date=date,source_url=url,schedule_notice_declared_release_at=published,tentative_date_known_in_advance=True,statement_time_et='14:00' if year>=2025 else '',statement_clock_explicit_in_this_notice=year>=2025,actual_feed_receipt_at='',event_treatment='cancelled_regular_slot_do_not_trade' if date=='2020-03-18' else 'future_tentative_as_of_2026_11_10' if date>'2026-11-10' else 'tentative_schedule_not_actual_release_confirmation'))
with (P/'fomc_advance_schedule.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=rows[0]);w.writeheader();w.writerows(rows)
b=acquire('cot2018.zip','https://www.cftc.gov/files/dea/history/deacot2018.zip')
z=zipfile.ZipFile(io.BytesIO(b)); source=list(csv.DictReader(io.StringIO(z.read('annual.txt').decode('utf-8-sig'))))
codes={'001602','002602','005602','007601','026603','033661','073732','080732','083731','057642','054642','067651','023651','022651','111659','088691','084691','085692','076651'}
fields=['Market and Exchange Names','As of Date in Form YYYY-MM-DD','CFTC Contract Market Code','Open Interest (All)','Commercial Positions-Long (All)','Commercial Positions-Short (All)','Traders-Commercial-Long (All)','Traders-Commercial-Short (All)','Contract Units']
selected=[{k:r[k].strip() for k in fields} for r in source if r['CFTC Contract Market Code'].strip() in codes]
selected.sort(key=lambda r:(r[fields[2]],r[fields[1]]))
with (P/'cot2018_commodity_sample.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(selected)
summary={'author':'dot','scope':'data normalization only; no return or strategy tests','fomc_schedule_rows':len(rows),'cot_archive_rows':len(source),'cot_selected_rows':len(selected),'cot_market_codes':sorted({r[fields[2]] for r in selected}),'cot_date_min':min(r[fields[1]] for r in selected),'cot_date_max':max(r[fields[1]] for r in selected),'cot_actual_release_at':None,'cot_as_originally_published_values_verified':False,'cot_unique_code_date_keys':len({(r[fields[2]],r[fields[1]]) for r in selected}),'receipts':receipts}
(P/'acquisition_manifest.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps({k:v for k,v in summary.items() if k!='receipts'},indent=2))
# Current official schedule snapshot; not an archived advance notice.
import re,html
b=acquire('eia_schedule.html','https://www.eia.gov/petroleum/supply/weekly/schedule.php')
tables=re.findall(r'<table\b.*?</table>',b.decode(),re.S|re.I)
ex=[]
for table in tables:
 if 'Alternate release date' not in table:continue
 for tr in re.findall(r'<tr\b.*?</tr>',table,re.S|re.I):
  cells=[html.unescape(re.sub('<[^>]+>','',v)).strip() for v in re.findall(r'<t[dh]\b[^>]*>(.*?)</t[dh]>',tr,re.S|re.I)]
  if len(cells)==5 and cells[1]!='Alternate release date': ex.append(dict(zip(['week_ending','release_date','release_day','release_time_et','holiday'],cells)))
(P/'eia_schedule_snapshot.json').write_text(json.dumps({'author':'dot','source_url':'https://www.eia.gov/petroleum/supply/weekly/schedule.php','snapshot_verified_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'historical_advance_notice_verified':False,'default':'Wednesday 10:30 America/New_York','exceptions':ex},indent=2)+'\n')
summary['eia_exception_rows']=len(ex);summary['receipts']=receipts
(P/'acquisition_manifest.json').write_text(json.dumps(summary,indent=2)+'\n')
