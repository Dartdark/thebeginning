# S30, cash-session IBS reversal: Claude's review, 2026-10-23

Rebuild `analysis/s30_ibs_test.py` (output `analysis/outputs/s30_ibs_test_output.txt`), NQ and ES (no RTY data here).
Long when the 08:30-15:00 session closes in its bottom 20% (IBS < 0.20), out when a session closes in its top 20%; no stop,
holds overnight / weekends. **Not Apex-legal**; personal account only. Source: Pagonidis (NAAIM 2014), thresholds not fitted.

| Per full contract, 2018-26 | Trades | Win | $ / trade | PF | t | 2018-22 | 2023+ | Years + |
|---|---|---|---|---|---|---|---|---|
| NQ | 253 | 70% | $1,352 | 1.82 | 3.5 | $1,303 (t 3.1) | $1,427 (t 2.0) | 7/9 (2018, 2024 lose) |
| ES | 240 | 67% | $818 | 1.85 | 3.6 | $785 (t 2.7) | $867 (t 2.4) | 8/9 (2018 loses) |
- Rebuild ≈ author (NQ ~$34k per micro 2018-26 vs their $36.9k incl. 2017; ES ~$19.6k vs $22.6k).
- **About half is market drift:** holding the index for S30's days in the market would have made ~$173k (NQ) / ~$95k (ES)
  per contract vs S30 $342k / $196k. Random entry sessions with S30's own hold lengths: $591 / $339 a trade vs $1,352 / $818
  (p 0.03 each). The short mirror loses (2023+ t −1.6 / −1.4): it's a long-side, bull-market-friendly effect.
- Risk: no stop, so open drawdowns are large: daily-marked max DD $52.0k per NQ ($5.2k per MNQ), $44.2k per ES; Sharpe
  0.84 / 0.86 daily. NQ and ES legs correlate 0.78 (one bet, not two). Corr with the funded plan +0.08.
- Personal portfolio (`analysis/personal_portfolio.py` §6): full 12 + S30 (NQ + ES, 1 micro each) $26.1k a year vs $20.1k,
  return / DD 6.5 vs 7.1, capital at the 20% rule $32.0k vs $23.6k.
- **Correction 2026-10-23 (Codex's audit, codex/work 80f3bed):** the first daily series marked raw 15:00 closes and left out
  costs, entry / exit fills and roll jumps, so it overstated the pair by ~$3.0k per micro over 2018-26 ($56,832 vs $53,833).
  Rebuilt so the daily marks reconcile to the trade nets to the cent; the numbers above are the corrected ones.

## Verdict: B, personal-account candidate for an account of ~$33k+
Real (published, unfitted thresholds, both markets, random-entry p 0.03) but half of it is the index's drift, no stop and
multi-day holds. Adds ~$6k a year at 1 micro per market with a slightly worse return / drawdown; add it once the personal
account is past ~$33k. Live note: positions open at a quarterly roll have to be rolled by hand.
