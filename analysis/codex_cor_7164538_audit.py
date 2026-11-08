"""Source-only COR arithmetic, dimensional/example and repository receipt checks; no backtest."""
from pathlib import Path
import csv
import hashlib
import json
import subprocess

ROOT=Path('agents/codex/inputs/ssrn7164538')
OUT=Path('analysis/outputs/codex_cor_7164538')

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def cor(before_asset,before_market,after_asset,after_market):
    denominator=abs(after_asset-after_market)
    return abs(before_asset-before_market)/denominator if denominator else None

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    # All are valid RSI values. Eq12 itself has no clipping or normalization into [0,1].
    e=cor(70,50,51,50)
    assert e==20 and cor(70,50,50,50) is None
    assert cor(60,50,40,50)==1 and cor(60,50,20,50)<1
    source=dict(with_cor=dict(return_pct=41.56,win_pct=85.71,trades=7,sharpe=1.51,dd_pct=-9.35),
                without_cor=dict(return_pct=43.77,win_pct=77.78,trades=9,sharpe=1.35,dd_pct=-9.29))
    with (ROOT/'repository/best_atr_leveraged_1h_no_cor.csv').open() as f:
        tsll=next(row for row in csv.DictReader(f) if row['ticker']=='TSLL')
    with (ROOT/'repository/best_atr_stock_1h.csv').open() as f:
        tsla=next(row for row in csv.DictReader(f) if row['ticker']=='TSLA')
    assert abs(float(tsll['total_return_pct'])-43.77)<.01
    assert float(tsll['trades'])==9 and abs(100*float(tsll['win_rate'])-77.78)<.01
    # Sizing Eq10 with price100 and price-unit ATR2; compare to shares at one ATR risk distance.
    equity,risk,price,atr=100000.,.01,100.,2.
    published_size=equity*risk/(price*atr)
    one_atr_risk_shares=equity*risk/atr
    result=dict(source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),script_sha256=sha(__file__),
                source_sha256={str(p):sha(p) for p in ROOT.rglob('*') if p.is_file()},
                source_headline_comparison=source,
                source_comparison_delta=dict(return_percentage_points=41.56-43.77,sharpe=1.51-1.35,
                    dd_percentage_points=-9.35-(-9.29),headline_wins_implied=6,headline_win_fraction=6/7),
                equation12_counterexample=dict(before_asset=70,before_market=50,after_asset=51,after_market=50,COR=e,
                    zero_denominator_result='undefined without extra rule',bounded_by_one=False),
                equation10_conditional_units_example=dict(cash_usd=equity,assumed_loss_risk_fraction=risk,
                    price_usd_per_share=price,atr_usd_per_share=atr,published_numeric_size=published_size,
                    one_atr_loss_distance_share_size=one_atr_risk_shares,
                    warning='Printed Eq10 is not native share sizing if ATR has price units; implementation is unavailable'),
                pinned_repository_tsll_no_cor=tsll,pinned_repository_tsla_cor=tsla,
                paper_TSLA_COR_1h_return_pct=13.59,
                repository_code_status='Only LFS pointers retrieved; materialized code request proxy403; no author code executed',
                owned_filename_census={pattern:[str(p) for p in Path('data').rglob(pattern) if p.is_file()][:20]
                    for pattern in ['*TSLL*','*TSLA*','*SPXL*','*GSPC*','*TQQQ*']},
                return_trials=0,verification='Source/math/CSV checks only, not empirical performance replication')
    (OUT/'audit.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ['source_comparison_delta','equation12_counterexample','return_trials']},indent=2))

if __name__=='__main__':main()
