"""Static weekly Kusho/C03 roll-transformation audit; no strategy returns.

Pinned Claude52a6543 source snapshots are read as text only. The illustrative
indicator values use invented constants; no cached grid or market prices are
read and no replay/account/Monte Carlo helper is executed.

Use --source-root /path/to/pinned-checkout to read the original repository
paths instead of the optional flat local input archive.
"""
from pathlib import Path
import argparse
import hashlib
import json

ROOT=Path(__file__).resolve().parents[1]
INPUT=ROOT/'agents/codex/inputs/weekly_cross_review_20261023/strategy'
OUT=ROOT/'analysis/outputs/codex_weekly_strategy_audit'


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-root',type=Path,
                        help='Checkout at 52a6543589941455b775d46dfc23dcfbf16ec188; reads original source paths.')
    args=parser.parse_args()
    if args.source_root is None:
        sources={name:INPUT/name for name in ['kusho_test.py','C03.txt','Kusho_v9.txt','REVIEW.md']}
    else:
        source_root=args.source_root.resolve()
        sources={'kusho_test.py':source_root/'analysis/kusho_test.py',
                 'C03.txt':source_root/'checks/candidates/kusho/C03.txt',
                 'Kusho_v9.txt':source_root/'checks/candidates/kusho/Kusho_v9.txt',
                 'REVIEW.md':source_root/'checks/candidates/kusho/REVIEW.md'}
    OUT.mkdir(parents=True,exist_ok=True)
    py=sources['kusho_test.py'].read_text()
    c03=sources['C03.txt'].read_text()
    v9=sources['Kusho_v9.txt'].read_text()
    data_block=py.split('class Data:',1)[1].split('\ndef run(',1)[0]
    flags=dict(raw_grid_enters_python_indicators='B = g.bars(15)' in data_block,
               python_indicator_block_uses_gap_adjustment=any(k in data_block for k in ['CumGap','KOff','LastGap']),
               native_C03_adjusts_OHLC='H15 = High[KBack] - KOff' in c03 and 'C15 = Close[KBack] - KOff' in c03,
               native_C03_EMA_uses_adjusted_C15='EMA15 = EMA15 + EMAAlpha * (C15 - EMA15)' in c03,
               native_v9_adjusts_regime_close='CurC15 = Close - CumGap' in v9,
               python_removes_jumps_only_in_terminal_net='gross -= (c[j] - c[p]) * pos' in py)
    assert flags['raw_grid_enters_python_indicators'] and not flags['python_indicator_block_uses_gap_adjustment']
    assert all(flags[k] for k in ['native_C03_adjusts_OHLC','native_C03_EMA_uses_adjusted_C15','native_v9_adjusts_regime_close','python_removes_jumps_only_in_terminal_net'])
    # Invented one-bar +20 splice, underlying close unchanged at100. EMA50 and
    # ATR20 were warm at100 and2. No market event frequency is inferred.
    ema_prior,atr_prior,gap=100.,2.,20.
    raw_close,raw_high,raw_low=120.,121.,119.
    raw_ema=ema_prior+2/51*(raw_close-ema_prior)
    adjusted_ema=ema_prior+2/51*((raw_close-gap)-ema_prior)
    raw_tr=max(raw_high-raw_low,abs(raw_high-100),abs(raw_low-100))
    adjusted_tr=max(raw_high-raw_low,abs(raw_high-gap-100),abs(raw_low-gap-100))
    raw_atr=atr_prior+(raw_tr-atr_prior)/20
    adjusted_atr=atr_prior+(adjusted_tr-atr_prior)/20
    c03_example=dict(previous_EMA50=ema_prior,previous_ATR20=atr_prior,gap_points=gap,
                     raw_EMA50=raw_ema,adjusted_EMA50=adjusted_ema,
                     raw_ATR20=raw_atr,adjusted_ATR20=adjusted_atr,
                     raw_close_above_EMA=raw_close>raw_ema,
                     adjusted_close_above_EMA=raw_close-gap>adjusted_ema)
    # Invented mild drop99 after60 constant100 sessions plus20 contract gap.
    # Prior50-SMA and its5-session-lag value both100; current rawclose119.
    adj_mean=(49*100+99)/50
    raw_mean=(49*100+119)/50
    v9_example=dict(last_raw_close=119.,last_adjusted_close=99.,
                    raw_SMA50=raw_mean,adjusted_SMA50=adj_mean,previous_5lag_SMA50=100.,
                    raw_DOWN=(119<raw_mean and raw_mean<100),
                    adjusted_DOWN=(99<adj_mean and adj_mean<100))
    assert c03_example['raw_close_above_EMA'] and not c03_example['adjusted_close_above_EMA']
    assert not v9_example['raw_DOWN'] and v9_example['adjusted_DOWN']
    out=dict(pinned_ref='52a6543589941455b775d46dfc23dcfbf16ec188',operation='static code + invented indicator arithmetic only',
             new_strategy_return_trials=0,source_flags=flags,synthetic_C03=c03_example,synthetic_v9_DOWN=v9_example,
             historical_effect_measured=False,
             consequence='Published Kusho/C03 replays do not reproduce default native roll transformations; exact signals, risk and ranking need controlled parity.',
             input_sha256={name:hashlib.sha256(p.read_bytes()).hexdigest() for name,p in sorted(sources.items())},
             script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    (OUT/'summary.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out,indent=2))


if __name__=='__main__':main()
