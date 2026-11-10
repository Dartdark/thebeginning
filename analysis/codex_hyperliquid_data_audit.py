# Author/origin: dot. Retained original audit; repository codex_ naming is not independent authorship.
"""Bounded public-market D32 data audit. No returns, accounts, credentials or orders."""
import json, urllib.request, pathlib, hashlib, datetime, csv, collections, time
ROOT=pathlib.Path(__file__).resolve().parents[1]
OUT=ROOT/'analysis/outputs/codex_hyperliquid_audit_20261110'
OUT.mkdir(parents=True,exist_ok=True)
def ms(s): return int(datetime.datetime.fromisoformat(s).replace(tzinfo=datetime.timezone.utc).timestamp()*1000)
def iso(t): return datetime.datetime.fromtimestamp(t/1000,datetime.timezone.utc).isoformat()
receipts=json.loads((OUT/'receipts.json').read_text()) if (OUT/'receipts.json').exists() else []
def get(name,body):
    # Preserve immutable raw samples; reruns audit cached data, not changing snapshots.
    if (OUT/(name+'.json')).exists():
        raw=(OUT/(name+'.json')).read_bytes()
        receipt=next(r for r in receipts if r['name']==name)
        assert receipt['request']==body and receipt['sha256']==hashlib.sha256(raw).hexdigest(), 'Cached source mismatch'
        return json.loads(raw)
    start=datetime.datetime.now(datetime.timezone.utc).isoformat()
    req=urllib.request.Request('https://api.hyperliquid.xyz/info',data=json.dumps(body).encode(),headers={'Content-Type':'application/json'})
    with urllib.request.urlopen(req,timeout=40) as r: raw=r.read(); status=r.status
    end=datetime.datetime.now(datetime.timezone.utc).isoformat()
    (OUT/(name+'.json')).write_bytes(raw)
    receipts.append(dict(name=name,request=body,request_started_utc=start,response_received_utc=end,status=status,bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest()))
    (OUT/'receipts.json').write_text(json.dumps(receipts,indent=2))
    time.sleep(.25)
    return json.loads(raw)
def funding(name,start,end): return get(name,dict(type='fundingHistory',coin='BTC',startTime=ms(start),endTime=ms(end)))
a=funding('btc_funding_20261108','2026-11-08','2026-11-09')
probes={}
for name,start,end in [('design_2018_2022','2018-01-01','2023-01-01'),('early_2023','2023-01-01','2024-01-01'),('jan2024','2024-01-01','2024-01-02'),('jan2025','2025-01-01','2025-01-02'),('jan2026','2026-01-01','2026-01-02')]:
    rows=funding(name,start,end)
    probes[name]=dict(count=len(rows),first=iso(rows[0]['time']) if rows else None,last=iso(rows[-1]['time']) if rows else None)
c=get('btc_candles_1m_20261108',dict(type='candleSnapshot',req=dict(coin='BTC',interval='1m',startTime=ms('2026-11-07T23:58:00'),endTime=ms('2026-11-09T00:01:00'))))
p=get('predicted_snapshot',dict(type='predictedFundings'))
m=get('context_snapshot',dict(type='metaAndAssetCtxs'))
hours=[int(x['time'])//3600000 for x in a]
cs={int(x['t']):x for x in c}
matched=[]
for f in a:
    hour=int(f['time'])//3600000*3600000
    prev=cs.get(hour-60000)
    at=cs.get(hour)
    matched.append(dict(event_time_ms=f['time'],event_time_utc=iso(f['time']),funding_rate_decimal=f['fundingRate'],premium=f['premium'],previous_minute_close=prev['c'] if prev else None,previous_candle_end_ms=prev['T'] if prev else None,event_minute_open=at['o'] if at else None,event_minute_close=at['c'] if at else None,available_at_historical=None,oracle_at_payment=None))
with (OUT/'matched_observations.csv').open('w',newline='') as out:
    w=csv.DictWriter(out,fieldnames=matched[0].keys()); w.writeheader();w.writerows(matched)
summary=dict(funding_rows=len(a),first=iso(a[0]['time']),last=iso(a[-1]['time']),duplicate_timestamps=len(a)-len(set(x['time'] for x in a)),missing_hour_bins=len(set(range(min(hours),max(hours)+1))-set(hours)),min_hour_offset_ms=min(x['time']%3600000 for x in a),max_hour_offset_ms=max(x['time']%3600000 for x in a),unique_rates=sorted(set(x['fundingRate'] for x in a)),candle_rows=len(c),matched_prior_minutes=sum(x['previous_minute_close'] is not None for x in matched),probes=probes,btc_prediction=[x for x in p if x[0]=='BTC'],btc_context=m[1][next(i for i,x in enumerate(m[0]['universe']) if x['name']=='BTC')],matched_first=matched[0])
early=json.loads((OUT/'early_2023.json').read_text())
summary['early_2023_intervals_hours']=dict(collections.Counter(round((y['time']-x['time'])/3600000) for x,y in zip(early,early[1:])))
summary['early_2023_cadence_transition']=[dict(previous=iso(early[i-1]['time']),event=iso(early[i]['time']),next=iso(early[i+1]['time']),previous_rate=early[i]['fundingRate'],next_rate=early[i+1]['fundingRate']) for i in range(1,len(early)-1) if round((early[i]['time']-early[i-1]['time'])/3600000)!=round((early[i+1]['time']-early[i]['time'])/3600000)]
ct=[int(x['t']) for x in c]
summary['candle_duplicates']=len(ct)-len(set(ct))
summary['candle_missing_minutes']=(max(ct)-min(ct))//60000+1-len(set(ct))
(OUT/'summary.json').write_text(json.dumps(summary,indent=2))
print(json.dumps(summary,indent=2))
