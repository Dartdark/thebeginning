"""IFT input feasibility only: column/time coverage, hashes and source flags.

Never computes candidate signals, excursions or returns.
"""
from pathlib import Path
import hashlib
import json
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]

def main():
    rows=[]
    for p in sorted((ROOT/'data').glob('OF_1min_*.csv')):
        d=pd.read_csv(p,usecols=['date','time','volume','upvol','downvol'])
        # Header/exporter explicitly uses Eastern chart times, not CT.
        minute=(d.time//100)*60+d.time%100
        rows.append(dict(path=str(p.relative_to(ROOT)),rows=len(d),
            first_date=int(d.date.min()),last_date=int(d.date.max()),
            first_hhmm_et=int(d.time.min()),last_hhmm_et=int(d.time.max()),
            outside_export_rth_window=int(((d.time<930)|(d.time>1615)).sum()),
            rows_before_0930_et=int((minute<570).sum()),
            volume_equals_up_fraction=float((d.volume==d.upvol).mean()),
            both_sides_zero_rows=int(((d.upvol==0)&(d.downvol==0)).sum())))
    native=[]
    for p in sorted((ROOT/'data').glob('NQ*.csv')):
        native.append(dict(path=str(p.relative_to(ROOT)),columns=pd.read_csv(p,nrows=0).columns.tolist()))
    source=ROOT/'agents/codex/inputs/ift_nq5_flow/IFT_NQ5_Flow_Signal.txt'
    note=source.with_name('research_note.txt')
    result=dict(kind='no-return source/input audit',return_trials=0,order_flow_time_zone='Eastern per exporter',
        of_files=rows,native_nq_headers=native,
        source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
        research_note_sha256=hashlib.sha256(note.read_bytes()).hexdigest(),
        blockers=['No native full-Globex 5-minute UpTicks/DownTicks series',
                  'RTH order-flow exports cannot reproduce overnight shorts or continuous 500-bar rank',
                  'No original MC trade-list export or matching Python walk-forward schedules'],
        account_destinations={k:'BLOCKED before return trials: required full-session directional volume missing'
          for k in ['50K evaluation','150K evaluation','50K funded','150K funded','personal portfolio']})
    out=ROOT/'analysis/outputs/codex_ift_nq5_flow';out.mkdir(parents=True,exist_ok=True)
    (out/'data_audit.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(of_files=len(rows),of_rows=sum(r['rows'] for r in rows),
          first_hhmm_et=min(r['first_hhmm_et'] for r in rows),last_hhmm_et=max(r['last_hhmm_et'] for r in rows),
          outside_rth_rows=sum(r['outside_export_rth_window'] for r in rows),
          native_nq_files=len(native),return_trials=0),indent=2))

if __name__=='__main__': main()
