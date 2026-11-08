"""Audit quoted tables/statistical arithmetic only; no market prices or backtest.

All returns below are author numbers or explicitly conditional arithmetic on
those numbers. They are not a newly reproduced strategy or economic trial.
"""
import csv
import datetime as dt
import hashlib
import json
from pathlib import Path
import subprocess

import numpy as np
from scipy.stats import t

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'agents/codex/inputs/ssrn6477100_20261108'
OUT=ROOT/'analysis/outputs/codex_ssrn6477100_20261108'


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    text=(BASE/'paper.txt').read_text()
    assert 'Wonpyo Han' in text and 'March 2026' in text
    assert '-0.64%' in text and '-13.19%' in text and '0.036' in text
    main_rows=[('V1',-4.33,-19.08,6.0,38.4),('V3',-2.76,-17.52,8.6,50.1)]
    with (OUT/'author_table1.csv').open('w',newline='') as f:
        w=csv.writer(f,lineterminator='\n');w.writerow(['profile','mean_return_pct','reported_mean_alpha_pct','mean_drawdown_pct','win_pct']);w.writerows(main_rows)
    bear=[('Bear22',-18.6,19.0),('Bull24b',-22.3,21.7),('Bear25',-43.6,31.2)]
    conditional=[dict(period=k,buy_hold_pct=b,reported_alpha_pct=a,
                      implied_strategy_pct_if_alpha_is_simple_excess=b+a) for k,b,a in bear]
    with (OUT/'table3_conditional_arithmetic.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(conditional[0]),lineterminator='\n');w.writeheader();w.writerows(conditional)
    adaptive=[('always_on',-2.27,-14.83,.171),('EMA_adaptive',-.64,-13.19,.217)]
    with (OUT/'author_table8.csv').open('w',newline='') as f:
        w=csv.writer(f,lineterminator='\n');w.writerow(['profile','mean_return_pct','mean_alpha_pct','alpha_p']);w.writerows(adaptive)
    fees=np.array([.1,.2,.3,.5]);means=np.array([-3.47,-6.89,-10.15,-16.22]);slope,intercept=np.polyfit(fees,means,1)
    fit=intercept+slope*fees;r2=1-float(((means-fit)**2).sum()/((means-means.mean())**2).sum())
    scout=ROOT/'agents/codex/research/scout/progress.json';p=json.loads(scout.read_text())
    receipt=dict(
        checked_at_utc=dt.datetime.now(dt.timezone.utc).isoformat(),
        checked_codex_head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        checked_remote_codex=subprocess.check_output(['git','rev-parse','origin/codex/work'],cwd=ROOT,text=True).strip(),
        source=dict(id='ssrn:6477100',title='Adaptive Limits of Algorithmic Cryptocurrency Trading from a Complex Adaptive Systems Perspective: An Empirical Study on Human-AI Collaborative Strategy',
            author='Wonpyo Han, Hansung University',version='March 2026; PDF metadata March 27, 2026',pages=17,
            path=str((BASE/'paper.pdf').relative_to(ROOT)),sha256=sha(BASE/'paper.pdf'),text_sha256=sha(BASE/'paper.txt'),
            permission='owned_upload',provenance='User attachment file_00000000352481fd810ac040177fe83b',
            access_method='Full uploaded text read; Tables 1/3 and 6/7/8 visually checked'),
        source_sample='Ten selected surviving Binance crypto assets, hourly OHLCV, June 2022 through March 2026; eight retrospective periods; study reports 80 main and over 160 total experiments',
        quoted_arithmetic=dict(
            table1_buy_hold_pct=14.87,
            table1_reconciliation=[dict(profile=k,return_pct=r,reported_alpha_pct=a,
                return_minus_buy_hold_pct=r-14.87,reported_minus_simple_alpha_pp=a-(r-14.87)) for k,r,a,_,_ in main_rows],
            table1_caveat='Residuals 0.12/0.11 pp exceed ordinary rounding of three two-decimal means, if alpha is simple same-sample excess. Definitions/weights require raw reconciliation, not an accusation of fabrication.',
            table3_conditional=conditional,table3_caveat='Implied arithmetic only under simple-excess definition; no independent reconstruction of original strategy returns.',
            table8_adaptive_minus_always_return_pp=-.64-(-2.27),
            table8_adaptive_minus_always_alpha_pp=-13.19-(-14.83),
            table8_two_sided_p_from_t_n=float(2*t.sf(abs(2.185),34)),
            table8_both_mean_returns_negative=True,
            table8_caveat='Paired p arithmetic agrees with 0.036 under iid pairs; independence, selection correction and chronological strategy validity not established.',
            table7_return_change_pp_per_point1_fee=float(slope*.1),table7_fit_r_squared=r2,
            table7_all_mean_returns_negative=bool((means<0).all()),
            table7_caveat='Arithmetic on reported fee-study means only; no observed spread, fill or native futures cost validation. A low-fee viability threshold is not established by negative means.'),
        owned_input_mapping=dict(method='Filename metadata only; no raw prices or returns loaded',
            crypto_names=sorted(q.name for q in (ROOT/'data').glob('*.csv') if any(x in q.name.upper() for x in ['BTC','ETH','SOL','BNB','XRP','ADA','DOGE','AVAX','LINK','DOT','FEAR','GREED'])),
            conclusion='Owned BTC series and ETH perpetual 30-minute data do not establish the exact ten-asset Binance hourly universe, V3 formula or sentiment availability. No proxy or new acquisition loop justified.'),
        prior_family='Generic indicator/regime filters overlap existing failed/qualified work; exact study is not falsely called already tested.',
        disposition='dont_test',new_economic_trials=0,market_return_tests_run=False,independent_economic_verification=False,
        scout_preserved=dict(sha256=sha(scout),hypotheses=p['hypotheses_started'],definitions=p['economic_definitions'],lease=p['lease']),
        root_trials_sha256=sha(ROOT/'TRIALS.csv'))
    (OUT/'source_audit.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(dict(disposition='dont_test',new_return_trials=0,adaptive_minus_always_pp=1.63,
                         quoted_p_check=receipt['quoted_arithmetic']['table8_two_sided_p_from_t_n'],
                         both_adaptive_means_negative=True)))


if __name__=='__main__':main()
