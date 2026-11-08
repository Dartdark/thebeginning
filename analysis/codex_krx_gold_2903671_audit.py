"""No-return source-moment, fee and information-clock audit for SSRN2903671."""
import csv
from datetime import datetime
import hashlib
import json
from pathlib import Path
import subprocess
from zoneinfo import ZoneInfo

ROOT=Path('agents/codex/inputs/ssrn2903671')
OUT=Path('analysis/outputs/codex_krx_gold_2903671')

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    # Tables4–5: percentages / rounded source sample moments, not downloaded observations.
    ry1,ry2,r12=.576,-.147,-.344
    by1=(ry1-ry2*r12)/(1-r12*r12)
    by2=(ry2-ry1*r12)/(1-r12*r12)
    beta_gold=by1*.679/.978
    beta_dollar=by2*.679/.529
    r2=by1*ry1+by2*ry2
    intercept=.134-beta_gold*.006-beta_dollar*.029
    assert abs(beta_gold-.414)<.002 and abs(beta_dollar-.075)<.002
    # Table2's hypothetical 10% gross appreciation: include both displayed fees.
    purchase,buyfee,sale,sellfee=42500,128,46750,140
    pnl=sale-sellfee-purchase-buyfee
    net_funded=100*pnl/(purchase+buyfee)
    net_price_base=100*pnl/purchase
    assert net_funded<9.6 and net_price_base<9.6
    # Source Table3 winter/summer session-end conventions only, not verified historical venue rules.
    fixtures=[]
    for previous,today,endhour in [('2016-01-12','2016-01-13',7),('2016-07-12','2016-07-13',6)]:
        kst=ZoneInfo('Asia/Seoul')
        prevclose=datetime.fromisoformat(previous+'T15:30:00').replace(tzinfo=kst)
        available=datetime.fromisoformat(today+f'T{endhour:02d}:00:00').replace(tzinfo=kst)
        opening=datetime.fromisoformat(today+'T09:00:00').replace(tzinfo=kst)
        assert prevclose<available<opening
        fixtures.append(dict(previous_krx_close=prevclose.isoformat(),source_futures_session_end=available.isoformat(),
                             next_krx_open=opening.isoformat(),known_at_previous_close=False,
                             source_clock_assumption_only=True))
    census={p:[str(x) for x in Path('data').rglob(p) if x.is_file()][:25]
            for p in ['*KRX*','*krx*','*KRW*','*krw*','*DX_*','*DXY*','GC_1min_*']}
    headers={}
    p=Path('data/GC_1min_2017.csv')
    if p.exists():
        with p.open() as f:headers[str(p)]=next(csv.reader(f))
    result=dict(source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
                script_sha256=sha(__file__),source_files={str(p):sha(p) for p in ROOT.iterdir() if p.is_file()},
                source_regression_claim=dict(gold_beta=.414,gold_t=16.707,dollar_beta=.075,dollar_p=.100,adjusted_r2=.333),
                reconstruction_from_rounded_source_moments=dict(gold_beta=beta_gold,dollar_beta=beta_dollar,
                                                               unadjusted_r2=r2,intercept=intercept),
                hypothetical_source_table2=dict(gross_price_return_pct=10,claimed_net_pct=9.6,
                    recomputed_on_funded_outlay_pct=net_funded,recomputed_on_purchase_price_pct=net_price_base),
                information_clock_fixtures=fixtures,owned_filename_census=census,inspected_headers=headers,
                return_trials=0,verification='Source arithmetic and assumed-clock checks only; no economic or market-data replication')
    (OUT/'audit.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k in ['reconstruction_from_rounded_source_moments','hypothetical_source_table2','return_trials']},indent=2))

if __name__=='__main__':main()
