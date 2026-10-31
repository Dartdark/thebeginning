"""Metadata-only dated-VX panel audit. Does not calculate signals or returns."""
import collections
import hashlib
import json
from pathlib import Path
import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[1]
INPUT = REPO/'agents/codex/inputs/calvados_2379985_20261030'
ROOT = REPO/'analysis/outputs/codex_calvados_2379985_20261030/metadata_check'
ROOT.mkdir(parents=True, exist_ok=True)
manifest = json.loads((INPUT / 'panel_manifest.json').read_text())
cal = pd.DatetimeIndex(pd.read_csv(INPUT/'cfe_calendar.csv', parse_dates=['date']).date)
# Primary exception: VX traded and daily-settled at08:30CT on2018-12-05.
# https://cdn.cboe.com/resources/schedule_update/2018/Cboe-to-Observe-National-Day-of-Mourning-on-Wednesday-December-5-2018.pdf
design = cal[(cal >= '2018-01-01') & (cal <= '2022-12-31')]
raw_frames, file_summaries = [], []
for item in manifest['files']:
    p = Path(item['path'])
    data = p.read_bytes()
    assert hashlib.sha1(f'blob {len(data)}\0'.encode()+data).hexdigest() == item['git_blob_sha']
    f = pd.read_csv(p)
    f['date'] = pd.to_datetime(f['Trade Date'])
    expiry = pd.Timestamp(item['expiry'])
    f['expiry'] = expiry
    f['file'] = p.name
    expected_lifecycle = cal[(cal >= f.date.min()) & (cal <= min(expiry, f.date.max()))]
    missing = expected_lifecycle.difference(pd.DatetimeIndex(f.date)).strftime('%Y-%m-%d').tolist()
    file_summaries.append(dict(file=p.name, records=len(f), first=f.date.min().strftime('%Y-%m-%d'),
        last=f.date.max().strftime('%Y-%m-%d'), expiry=item['expiry'],
        duplicate_dates=int(f.date.duplicated().sum()), missing_lifecycle_dates=missing,
        off_calendar_dates=pd.DatetimeIndex(f.date).difference(cal).strftime('%Y-%m-%d').tolist(),
        nonpositive_settle=int((f.Settle <= 0).sum()), nonpositive_open=int((f.Open <= 0).sum()),
        nonpositive_close=int((f.Close <= 0).sum()), high_below_low=int((f.High < f.Low).sum()),
        zero_volume=int((f['Total Volume'] <= 0).sum()), futures_labels=f.Futures.unique().tolist()))
    raw_frames.append(f)
panel = pd.concat(raw_frames, ignore_index=True)
panel = panel[(panel.date >= '2017-11-01') & (panel.date <= '2022-12-31')].copy()
cal_ns = cal.values
panel['tts'] = np.searchsorted(cal_ns, panel.expiry.values, side='right') - np.searchsorted(cal_ns, panel.date.values, side='right')
eligible = panel[(panel.date >= '2018-01-01') & (panel.date <= '2022-12-31') & panel.tts.between(15,93)].copy()
warmup_missing, warmup_bad, next_open_missing, next_open_bad = [], [], [], []
for e, rows in eligible.groupby('expiry'):
    native = panel[panel.expiry == e].set_index('date')
    for d in rows.date:
        k = cal.get_loc(d)
        previous = cal[k-10:k+1]
        if not previous.isin(native.index).all():
            warmup_missing.append(dict(date=str(d.date()),expiry=str(e.date())))
        elif (native.loc[previous,'Settle'] <= 0).any():
            warmup_bad.append(dict(date=str(d.date()),expiry=str(e.date())))
        nd = cal[k+1]
        if nd > pd.Timestamp('2022-12-31'):
            # End-of-design liquidation metadata lives in original files, not truncated panel.
            native = pd.concat(raw_frames,ignore_index=True).query('expiry == @e').set_index('date')
        if nd not in native.index:
            next_open_missing.append(dict(date=str(d.date()),expiry=str(e.date()),next_date=str(nd.date())))
        elif native.loc[nd,'Open'] <= 0:
            next_open_bad.append(dict(date=str(d.date()),expiry=str(e.date()),next_date=str(nd.date())))

# Expected monthly identities are the acquired expiry files, not selected from outcomes.
expiries = sorted(panel.expiry.unique())
keys = set(zip(panel.date, panel.expiry))
missing_eligible, by_date = [], []
for d in design:
    expected = [pd.Timestamp(e) for e in expiries if 15 <= np.searchsorted(cal_ns, pd.Timestamp(e).to_datetime64(), side='right')-np.searchsorted(cal_ns, d.to_datetime64(), side='right') <= 93]
    missing = [e.strftime('%Y-%m-%d') for e in expected if (d,e) not in keys]
    if missing: missing_eligible.append(dict(date=d.strftime('%Y-%m-%d'), expiries=missing))
    by_date.append(dict(date=d.strftime('%Y-%m-%d'), expected_monthly_candidates=len(expected), missing=len(missing)))

bad_open = eligible[eligible.Open <= 0][['Trade Date','file','tts','Open','Settle','Total Volume']]
bad_settle = eligible[eligible.Settle <= 0][['Trade Date','file','tts','Settle']]
bad_hilo = eligible[eligible.High < eligible.Low][['Trade Date','file','tts','High','Low','Open','Settle','Total Volume']]
zero_volume = eligible[eligible['Total Volume'] <= 0][['Trade Date','file','tts','Open','Settle','Total Volume']]
for name, frame in [('eligible_nonpositive_open',bad_open),('eligible_nonpositive_settle',bad_settle),('eligible_high_below_low',bad_hilo),('eligible_zero_volume',zero_volume)]:
    frame.to_csv(ROOT / f'{name}.csv', index=False)
pd.DataFrame(by_date).to_csv(ROOT/'candidate_identity_coverage.csv',index=False)

spot = pd.read_csv(json.loads((INPUT/'data_gate.json').read_text())['spot_path'],parse_dates=['DATE'])
spot_idx = pd.DatetimeIndex(spot.DATE)
summary = dict(scope='Metadata only; no candidate signals or returns',
    calendar='pandas_market_calendars CFE5.5.0 plus primary2018-12-05VXsession exception; other official historical verification still required; times ignored because its CFE hours are outdated',
    tts_convention='Count valid CFE dates strictly after observation through expiry inclusive; this audit freezes a count convention, not source exactness',
    files=len(file_summaries),design_calendar_days=len(design),first_design=str(design.min().date()),last_design=str(design.max().date()),
    design_days_missing_all_contracts=design.difference(pd.DatetimeIndex(panel.date.unique())).strftime('%Y-%m-%d').tolist(),
    spot_missing_design_dates=design.difference(spot_idx).strftime('%Y-%m-%d').tolist(),
    spot_extra_design_dates=spot_idx[(spot_idx >= '2018-01-01') & (spot_idx <= '2022-12-31')].difference(design).strftime('%Y-%m-%d').tolist(),
    eligible_rows=len(eligible),eligible_nonpositive_open=len(bad_open),eligible_nonpositive_settle=len(bad_settle),
    eligible_high_below_low=len(bad_hilo),eligible_zero_volume=len(zero_volume),
    duplicate_contract_date_rows=int(panel.duplicated(['date','expiry']).sum()),missing_expected_eligible=missing_eligible,
    candidate_counts=dict(collections.Counter(a['expected_monthly_candidates'] for a in by_date)),
    rms10_warmup_missing=warmup_missing,rms10_warmup_nonpositive=warmup_bad,
    next_session_open_missing=next_open_missing,next_session_open_nonpositive=next_open_bad,
    lifecycle_missing_count=sum(len(a['missing_lifecycle_dates']) for a in file_summaries),
    files_with_lifecycle_gaps=[a for a in file_summaries if a['missing_lifecycle_dates']],
    files_with_off_calendar_rows=[a for a in file_summaries if a['off_calendar_dates']],
    file_summaries=file_summaries)
(ROOT/'panel_metadata_audit.json').write_text(json.dumps(summary,indent=2))
print(json.dumps({k:v for k,v in summary.items() if k not in ['file_summaries','files_with_off_calendar_rows','files_with_lifecycle_gaps']},indent=2))
print('Files with lifecycle gaps:',len(summary['files_with_lifecycle_gaps']))
print('Files with off-calendar rows:',len(summary['files_with_off_calendar_rows']))
