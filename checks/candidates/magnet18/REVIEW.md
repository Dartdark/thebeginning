# MAGNET18 (user's upload 2026-10-24: `Magnet18_proto.txt` + `MAGNET18_research_note.pdf`; same author as T_ONESIDE)

## The rule (frozen, long only, no stop)
At the 10:30 CT bar close, if NQ is > session VWAP + 2 pt OR > the 08:29 open + 2 pt → buy at 10:30:00, sell at 14:29:00.
Optional Moreira-Muir size overlay (22-day RV above its median → fewer lots; default off) and an early-close skip (default off).
Note: MultiCharts 2016-26 2,288 trades, 58.3%, $165, PF 1.30 (with the size overlay, $5 slip); IS 58.7% / OOS 57.6%. The
author's open questions: VWAP reclaim vs never-left, and the same gate on ES.

## Rebuild (`analysis/magnet18_test.py`, 2018-2026, per NQ, $7.25 + 1 tick per fill)
Parity at the note's 0.5 pt cost: $152, 59.0%, PF 1.26 (note $165 / 58.3% / 1.30). 61% of days gated (3.0 a week).

| per NQ | trades | avg | PF | t | years + | 2018-22 | 2023-26 |
|---|---|---|---|---|---|---|---|
| **MAGNET18** | 1,376 | $133 | 1.22 | 2.3 | 7/9 (2019, 2026 lose) | $116 | $157 |
| every day long (no gate) | 2,257 | $38 | 1.06 | 0.8 | 6/9 | $1 | $86 |
| complement (gate false) | 881 | −$112 | 0.86 | −1.4 | | | |
| open + 2 only | 1,163 | $140 | 1.24 | 2.2 | 9/9 | $104 | $188 |
| VWAP + 2 only | 1,215 | $91 | 1.15 | 1.7 | 7/9 | $116 | $60 |
| after their split 2023-09-08 | 485 | $120 | 1.15 | 0.9 | | | |

- Gate minus complement $245 (t 2.5): the morning's direction persists into the afternoon (= our 'Morning direction at the
  European close' row: longs $154, same 10:30 clock, already worse in the funded plan).
- Daily Sharpe 0.78, Sortino 1.17, Calmar 0.58, Ulcer 5.9, **max DD $35.4k per NQ**; 2023+ Sharpe 0.72 (5-95% 0.01-1.43,
  P(≤ 0) 5%). Long only (no short side). t 2.33 < bar 3.58, DSR 0.28. 2026 so far −$15.3k.
- Monte Carlo 1 MNQ: one-year P(loss) 17.6%, **P(hit the $2,000 EOD trail) 31%**.
- Early-close days: the file (UseEarlyCls false) holds through the 12:00 CT halt and sells after the 17:00 reopen: 47 such
  trades. Not allowed on Apex; in Python they are $105 on average.

## The author's two questions
1. **Reclaim vs never-left**: reclaim (the morning traded at / below VWAP or the open, then held) $126 (956); never-left $150
   (420). Never-left is not weaker → by the author's own test the inventory story goes; it is 'green at 10:30'
   (open + 2 alone carries it: $140, 9/9 years).
2. **ES** (+0.5 pt): gate $49 (t 1.5), every day $4, complement −$66; never-left $93 vs reclaim $33. Alive but weak on ES too:
   generic morning momentum, stronger on NQ.

## Apex
Evaluation (combine set 50.1%): + 1 / 2 / 3 MNQ 49.1 / 47.7 / 46.3%; in place of EOS 48.3 / 46.9%. Worse at every size.
Funded bootstrap not run: the same signal as the European-close row, which lowered the funded plan (+1 MNQ blown 13%), and a
31% one-year trail-hit chance at 1 MNQ on its own.

## Verdict: C
A real but small morning-momentum effect (long-only, NQ-beta heavy, $35k drawdown per NQ), below the multiple-testing bar,
and it lowers the evaluation pass rate. Not for Apex; not added to the personal portfolio (Sharpe 0.78 vs the portfolio's
2.97; ask if wanted).
