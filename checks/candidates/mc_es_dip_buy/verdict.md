READY FOR THE USER'S BACKTEST - but the REFERENCE has a bug: the MC file will match the corrected Python, not the saved outputs

**File:** personal_strategies/ES_Dip_Buy.txt (2026-11-14, not compiled). Replica: replica.py (the PL code bar by bar on ES 60-min, same
roll-adjusted 1-min grid as the reference, 4h candles built from the 1h bars, data2 loop over data/VIX_VIX3M_ratio_mc.csv, MC fills).

**Reference defect (confirmed, ref_idbug_test.py):** spy_dip_filter_settle.spy() keeps the trail's best close in `bs[id(pos)]`. CPython reuses
the id of a freed dict: 1,072 of 1,116 positions started with an OLD trade's best close, which tightens the trail at once. Same pattern in
jesse_lib_rest_test.py (l.92, 117, 151) and jesse_nq_intraday_test.py (l.107, 126).
| version | unfiltered | session + drop (shadow) | block signals |
|---|---|---|---|
| reference as written | 1,116, t 0.68 | 469, $1,503/yr, t 2.65, DD $1,609 | 799, t 1.69 |
| reference fixed | 891, t 0.74 | 386, $1,562/yr, t 2.83, DD $1,671 | 462, t 2.28 |
The 'shadow beats blocking' result holds (2.83 vs 2.28), the gap is smaller.

**Replication**
- Indicators (ST4, ATR4, ADX4, EMA18, ATR1): identical to the reference at every bar after 2017-09 (debug_ind.py).
- Shadow vs FIXED reference: 891 / 891 entries, 100% same exits; P&L identical with 1-min stop walking; 1h stops (as written): 2 of 891
  exits differ, +17.6 ES points over 9 years. Against the buggy reference: 77.9% match.
- Filter flag (MC data2 loop vs prior()/RULES 'rising', session dating): 100% agree; the ratio file equals the reference series (max diff 5e-7).
- Real orders vs fixed reference session+drop: 381 vs 386 trades, 98.7% matched, per-trade P&L corr 1.000, $14,839 vs $14,575 ($1,590/yr,
  t 2.89). The 5 unmatched are same-side re-entries where MC keeps the open contract. Next-open entries +$157, entry-bar market exits -$60.

**Compile risks:** none found (no reserved names; `Close[k] of data2` already used in a compiled file; IFF numeric). Logic bugs: none.
Notes: (1) MaxBarsBack 200 also applies to data2 = 200 daily bars before the first trade (file starts 2016: fine). (2) Keep MC's default of one
entry a direction, or same-side kept re-entries add a contract. (3) Unadjusted @ES: $15,338 vs $14,839 (small); prefer back-adjusted.
(4) l.70-71: if MC stamps an early-close bar 12:15, OK = 11 makes a 15-minute pseudo 4h candle (minor; compute OK from minutes - 1).
(5) Header l.23 '$1,560 a year, DD $1,609' mixes fixed and buggy numbers; corrected Python: $1,562/yr, DD $1,671.

**Gates** (replica trades): G1 FAIL (DSR 0.41), G2 PASS, G3 PASS 9/9, G4 FAIL (-$1,807 without the best 5%), G5 FAIL (no placebo), G6 PASS,
G7 PASS, G8 PASS, G10 PASS (100% fills in bar), G11 PASS (94% Sharpe kept), G13 PASS. Shorts: 141 trades, $107 total (no edge).
**Leaks:** filter uses ratio closes dated before the session; evening entries use that day's 15:15 CT close, stamped 16:00 - known by then.
Live: the VPS file for session D+1 may still hold close D-1's flag until CBOE posts close D (vix_ts_daily.ps1 'up to 4 days later'; GUESS).
