# Antigravity's NarangBlackBox (ES 1h, antigravity/jesse 6a18e6d): Claude's verdict (2026-10-18) — F, not tested further

Rule: long when price > EMA200, EMA50 > EMA200, ADX > 18-20 and a lower-Bollinger touch with a green candle (mirror for
shorts); stop 1.6 ATR(14 h), target 2.5 ATR, middle-band ratchet, out after 24 one-hour bars; size 1.5% of $1M per trade.

Fails before any rebuild is needed:
1. **Holds overnight** (24 one-hour bars = a day or more): not allowed on Apex (flat by 15:59 CT).
2. **Losses too big for the account:** average loss $4,875, largest win $31,876; Apex's whole trailing drawdown is $2,000.
3. **Weak even as reported:** Sharpe 0.53 over 6.75 years (t ≈ 1.4), +13.9% in total on $1M (≈ 2% a year), 2020-2026
   only, no 2018-19, no costs stated (Jesse fee rate), no holdout.
4. **Tuned on the full sample:** three iterations on the same data, the best one picked; against its own Phase 2 rules
   (no written plan, no design / holdout split).
5. **Not from the book:** Narang's *Inside the Black Box* describes how quant funds are organised (alpha, risk,
   transaction-cost, execution models); it gives no EMA / Bollinger / ADX rule. The rule is moving averages + Bollinger
   mean reversion, both already F on NQ / ES (TIER_LIST: moving-average crosses, mean reversion).

No forced trader behind it, so it also fails the first question of the process.
