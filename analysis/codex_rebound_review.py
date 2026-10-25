"""Independent synthetic source/engine review; no history or return outputs."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
from types import SimpleNamespace

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scratch_data/codex_deps'))
sys.path.insert(0,str(ROOT/'analysis'))
import numpy as np
import pandas as pd
import codex_rebound_engine as E

OUT=ROOT/'analysis/outputs/codex_rebound/independent_review.json'
REPORT=ROOT/'agents/codex/results/overnight_rebound_source_review.md'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def fixtures():
    dates=pd.date_range('2021-01-08',periods=5) # Friday through Tuesday
    arrays=[np.full((5,1440),np.nan) for _ in range(4)]
    def bar(d,j,op,hi,lo,cl):
        for a,v in zip(arrays,[op,hi,lo,cl]):a[d,j]=v
    bar(0,511,100,106,94,100)
    bar(0,900,100,105,95,99) # Friday down, known range12
    bar(2,1021,100,101,80,100) # pre-entry low must not affect MAE
    bar(2,1022,101,102,100.5,101)
    bar(3,180,103,104,102,103)
    bar(3,181,104,105,103,104)
    g=SimpleNamespace(o=arrays[0],h=arrays[1],l=arrays[2],c=arrays[3],
        D=5,ts=dates.to_numpy(),trading=np.array([0,3,4]))
    one,_=E.replay(g,sunday_multiplier=1)
    two,_=E.replay(g,sunday_multiplier=2)
    assert len(one)==len(two)==1
    a,b=one.iloc[0],two.iloc[0]
    assert a.signal_day==0 and a.day==2 and a.exit_day==3
    assert a.j0==1022 and a.j1==181 and a.entry==101 and a.exit==104
    assert a.reason=='time' and a.pnl==b.pnl==60
    assert a.qty==1 and b.qty==2
    assert a.mae==10 and a.entry_minute_adverse_px==100.5
    assert a.cross_date and not a.crosses_1559_ct and not a.crosses_1545_ct
    # A short null's nominal stop is107, but next open110 is its actual fill.
    bar(2,1023,110,111,109,110)
    short=E.replay_market(g,np.array([[2,1022,-1,12,1]],float))
    s=short.iloc[0]
    assert s.entry==101 and s.exit==110 and s.reason=='stop'
    assert s.mae==180 and s.exit_phase=='open'
    assert short.attrs['requested_signals']==short.attrs['closed_signals']==1
    # An intentionally late exit crosses the next CME-day flat checkpoint.
    raw=two[E.COLUMNS].to_numpy(float)
    raw[0,E.COLUMNS.index('j1')]=961
    raw[0,E.COLUMNS.index('exit_phase_code')]=0
    late=E._frame(g,raw)
    assert late.iloc[0].crosses_1559_ct and late.iloc[0].crosses_1545_ct
    # Explicit terminal IDs distinguish an unresolved null from zero profit.
    bar(4,1022,100,101,99,100)
    unfinished=E.replay_market(g,np.array([[4,1022,1,12,1]],float))
    assert len(unfinished)==0
    assert unfinished.attrs['requested_signals']==1 and unfinished.attrs['closed_signals']==0
    assert unfinished.attrs['unclosed_signal_ids']==[0]
    return dict(friday_signal_waits_until_sunday=True,sunday_qty_kept_separate_from_unit_pnl=True,
        market_entry_and_exit_use_next_native_open=True,pre_entry_low_excluded_from_mae=True,
        short_null_gap_stop_uses_worse_open=True,short_gap_mae_reconciles=True,
        ordinary_overnight_not_misclassified_as_flat_violation=True,
        actual_next_day_flat_crossing_detected=True,unclosed_null_has_explicit_signal_id=True)


def main():
    candidates=[ROOT/'agents/codex/inputs/rebound/NQ_Overnight_Rebound_strategy.txt',
                ROOT/'agents/codex/inputs/rebound/source.txt',
                Path(r'C:\Users\dmoto\Downloads\NQ_Overnight_Rebound_strategy.txt')]
    source=next(p for p in candidates if p.exists())
    source_hash,engine_hash=sha(source),sha(Path(E.__file__))
    parent=E.synthetic_checks()
    assert all(parent.values())
    independent=fixtures()
    result=dict(status='PASS WITH LIMITS: source/engine/synthetic review',
        source_path=str(source),source_sha256=source_hash,engine_sha256=engine_hash,
        review_script_sha256=sha(Path(__file__)),provided_synthetic_suite=parent,
        independent_fixtures=independent,research_history_loaded=False,return_outputs_inspected=False,
        independent_full_raw_data_replication=False,multicharts_parity_established=False,
        account_permission_or_promotion_verified=False,new_economic_trials=0,
        assumptions=['Declared ET chart normalized to CT cache; ET calendar Date retained',
                     'Unrounded half-range stop; next available native-bar fills',
                     'Simultaneous pending time exit/stop gap priced at same open, with market label retained'],
        literature_verified=['Primary abstracts or first-page abstracts; not every original full paper',
            'NY Fed July2026 follow-up flags 2021-25 European-hour drift fade including NQ/YM'])
    assert sha(source)==source_hash and sha(Path(E.__file__))==engine_hash
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n',encoding='utf-8')
    REPORT.write_text(f'''# Overnight Rebound source and engine: PASS WITH LIMITS

Summary: No material causal execution blocker found against the frozen source-replication plan.
The supplied synthetic suite and independent Friday/Sunday, short-gap, timing and account-calendar fixtures pass.
The source has no explicit16:45ET/weekend guard; its safety exit is a next-bar cash-session instruction.
The older research supports related hypotheses, while a July2026 primary update reports a faded European-open drift.
This is not independent full-data replication, platform parity, broker permission or a promotion verdict.

Plan: `agents/codex/plans/overnight_rebound.md`, preregistered **d94d815**.
Script: `analysis/codex_rebound_review.py`. Output: `analysis/outputs/codex_rebound/independent_review.json`.
Source hash: `{source_hash}`. Engine hash: `{engine_hash}`. New economic trials: **0**.
No price-history cache, strategy return output, live/VPS/broker configuration or API key was opened.

## Source and clock audit

- Source lines5/19/25–28 assume an ET-stamped PC chart and subtract60 minutes. The CT research grid must normalize
  that declared display, not subtract60 again. Raw ET Date matters after23:00CT; normal17:01 entries share the same calendar date.
- Header line6's claim that a wrong clock necessarily gives no trades is not generally true: line45 tests `>=EntryCT`,
  not equality. A wrong shift can produce a different, late strategy rather than no strategy.
- Lines30–42 build cash open/range from the08:31-labeled bar's open through the15:00 close; range is known before entry.
  The exact15:00 signal is required. Missing/shortened cash sessions can skip the evening signal; there is no lookback-history array to repair.
- Lines45–49 consume the armed signal once. A normal down Friday remains armed until Sunday because no Friday-evening/Saturday
  bars consume it. Sunday quantity uses raw chart Date/DayOfWeek, not the adjusted `CTt`; late23:00CT already belongs to Monday ET.
- Entry17:01 close submits next-native-bar market, normally the17:02-labeled bar's open (about17:01 wall CT/18:01ET).
  Exit03:00 close submits the03:01-labeled bar's open, about03:00 wall CT/04:00ET. Do not add another minute to label translation.
- Line53's half-cash-range protective stop is active on the entry bar. Worse stop gaps fill at the open. No target/stop path conflict exists.
- Line55 uses `>=03:00` through08:30, so missing the exact03:00 bar can be caught by the first later bar.
  Line57's fallback starts at08:31 and submits another next-bar exit. It can therefore already hold into the next cash session.
- There is **no explicit16:45ET or Friday/weekend liquidation guard**. Claims of always meeting those limits need actual exception counts.
  A delayed next-available-bar instruction is not an invented punctual liquidation.
- Ordinary17→03 midnight crossing is within a17→16 CME/account day under the adopted current-plan convention.
  Test crossings of the next flat/maintenance checkpoint, not calendar-date changes alone. This convention does not verify broker permission.

## Engine review

Read-through agrees with the planned close-time state sequence: cash ranges update at the source15:00 close, new orders act on the
next available native open, and only post-entry prices contribute to MAE. Quantity is separate from unit P&L and MAE.
The engine retains the ET calendar date and exposes late/safety/open positions and missing held minutes.
Simultaneous pending market exit and gap-stop opens have the same price; the helper keeps the market label. Native MC labeling is unverified.

The parent's synthetic suite passes. Independent additional fixtures verify:

- A down Friday waits until Sunday; Sunday2 doubles quantity without doubling the unit P&L field.
- An earlier pre-entry low is excluded; a normal evening-to-morning trade crosses dates without crossing the next15:59 checkpoint.
- A short null with nominal stop107 pays a worse next open110, with adverse excursion matching its actual entry101.
- A true late next-day exit is flagged; an unresolved terminal null retains its explicit signal ID instead of disappearing as zero P&L.

No material causal blocker was found. This review uses the parent's helper and synthetic arrays; it does not rebuild966 trades,
verify923 shared days/correlation, inspect return results, certify costs/account baselines, or replace an independent raw-data checker.

## Primary literature and scope

1. **Liu et al.** The [current SSRN abstract](https://ssrn.com/abstract=2730304), revised2025, describes buying cross-sectional
   overnight losers for subsequent intraday reversal. That is a different signal/holding direction from NQ cash losses→overnight long.
   The original2016 full text was not independently verified; the current primary abstract was visible in the public search index.
2. **Abdi2018.** The [university paper](https://ux-tauri.unisg.ch/RePEc/usg/sfwpfi/WPF-1829.pdf) studies common-stock quote midpoints:
   an overnight market decline, further intraday declines in volatile stocks, then another overnight reversal. Related liquidity mechanism,
   not a direct test of this NQ down-cash-day rule. Abstract/intro verified, not a full empirical-paper audit.
3. **Bondarenko–Muravyev.** The [publisher abstract](https://www.cambridge.org/core/journals/journal-of-financial-and-quantitative-analysis/article/abs/market-return-around-the-clock-a-puzzle/089E33AC0B4D3B9A02CBA31EDF6505B3)
   documents historical unconditional European-open concentration in ES futures. It does not validate this NQ filter, half-range stop or Sunday size.
4. **Boyarchenko–Larsen–Whelan.** The [NY Fed paper](https://www.newyorkfed.org/research/staff_reports/sr917.html) offers a relevant
   inventory-pressure/asymmetric selloff-reversal hypothesis. The cited mechanism is not itself verification of the submitted parameter set.
5. **Cliff–Cooper–Gulen2008.** The [primary indexed abstract](https://ssrn.com/abstract=1004081) documents broad historical overnight
   equity premium across stocks/indexes/futures. It does not establish profitability of the modern conditional18–04 strategy.

Direct SSRN opens returned403; no access bypass was attempted. Primary indexed abstracts, the publisher page and university/Fed sources
were used with the access limits above; no secondary retail-strategy commentary supplies the empirical claims here.

## Material current update

The same NY Fed authors' [July1,2026 follow-up](https://libertystreeteconomics.newyorkfed.org/2026/07/the-disappearing-overnight-drift/)
reports that the02:00–03:00ET premium flattened during2021–25, including NQ/YM, with weaker closing-imbalance predictability.
This cautions against carrying the older timing story forward unchanged. It does not alone refute a down-day18:00–04:00NQ strategy:
that conditions differently and includes other hours. Attribution and recent controls are needed before claiming the cited mechanism.

## Prior repository context

The older Overnight Drift backup had weak incremental funded evidence; part of its return was general overnight long exposure.
Liu's cross-sectional overnight→intraday family is also already ranked and failed a clean synchronized-clock test here.
Neither is an exact duplicate of this upload. Compare all-night totals, removed up/flat nights and random dropping before crediting
the down-day filter; a higher filtered PF alone is insufficient. The reported336-model search and other rejected filters remain prior trials.
''',encoding='utf-8')
    print(json.dumps(dict(status=result['status'],synthetic_checks_pass=True,
        no_history_or_return_outputs_accessed=True,output=str(OUT)),indent=2))


if __name__=='__main__':main()
