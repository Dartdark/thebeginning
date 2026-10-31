# Idea card: trade the real closing-auction imbalance (user + Claude, 2026-10-25; process: S_RANK_PROGRAM.md)

Status: stage 0 agreed; waiting for data (NYSE quote / sample; Databento XNAS.ITCH 'imbalance' schema).

- Who is forced: index funds, ETFs (QQQ / SPY creations), leveraged ETFs, pensions and anyone with a market-on-close
  order must trade in the 15:00 CT closing auction regardless of price. The exchanges publish the running imbalance
  (Nasdaq NOII every few seconds from 14:50 CT; NYSE from 14:50 CT, 15:00 ET-style feeds) before the cross.
- When: every trading day, 14:50 -> 15:00 CT (~250 a year; ~100-150 with a size filter).
- Direction: a large buy (sell) imbalance has to be filled at the close -> liquidity providers and futures arbitrage push
  NQ / ES the same way into 15:00; part of it comes back after the cross (the post-settlement reversal we measured).
- Why not arbitraged: the imbalance is public but the size needed to offset a multi-billion imbalance is not; the trade is
  short (10 minutes) and capacity-limited, which keeps large players away.
- What we already know from price alone: ES MOC Follow (B, in the plan) follows a big 14:00 -> 14:50 move into 15:00
  using price as a proxy for the imbalance; post-settlement reversal real but below costs (NQ faded since 2023).
- What kills it: the imbalance adds nothing over the price proxy (same trades as ES MOC Follow); the effect is all in
  quarter-end / rebalance days (too few); the published imbalance arrives too late to act before 15:00.
- Stage 1 plan (look only, design years only): signed NQ / ES move 14:50 -> 15:00 by imbalance size (shares x price,
  scaled by average close volume), vs the price-proxy days; does a large imbalance on a quiet-price day still move it?
- Data routes (cheapest first): (1) Databento XNAS.ITCH 'imbalance' schema (Nasdaq NOII; self-serve, usage-based,
  new-account credit) for QQQ + the top NDX names; NYSE / Arca integrated feed for SPY. (2) NYSE TAQ Order Imbalances
  quote + free sample (agents/claude_evidence/NYSE_QUOTE_EMAIL.md, datasales@nyse.com). (3) Nasdaq NOII directly
  (noii.nasdaq.com/enroll).
