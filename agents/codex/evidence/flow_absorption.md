# NQ Flow Absorption: TEST

Summary: New standalone entry hypothesis: aggressive volume fails to move price in its own direction.
Buy a strong up-close bar despite net aggressive selling; mirror for shorts, with delayed market entry.
The Bridge buy/sell minute volumes are available; their old plan-filter/large-print tests do not prove this rule.
Test five frozen candidate/control configurations on2018-22 first; a failure ends this hypothesis, not t6 research.

Sources: `analysis/orderflow_test.py`, `analysis/bridge_filter_scan.py`, `analysis/whale_balanced_book_test.py`,
`TIER_LIST.md` order-flow rows, `data/OF_1min_*.csv` and raw NQ files. No new return tests yet.

1. **Who and why:** marketable buyers/sellers consume resting liquidity. An up-close despite net selling may
   indicate demand replenishment/absorption; covering by sellers could extend the move. This is an inference,
   not directly observed passive order replenishment or a compulsory flow. It can instead be stale reporting.
2. **Known inputs:** completed5/15-minute bar NQ OHLC and summed aggressive buy/sell volume. Signed delta
   fraction is (upvol-downvol)/(upvol+downvol); do not use the export's misleading volume field as total volume.
   Entry waits one additional native minute after the signal close. Actual historical receive times are absent.
3. **Transmission:** trade NQ directly, one position; no basket/old-strategy tickets/second contract leg.
4. **Data:** committed OF minutes2018-01-02--2026-07-07, source ET labels mapped to CT by minus60minutes.
   Use only upvol/downvol and source close, not potentially revised profile/POC/cumulative-day fields.
   Require complete bars, nonnegative finite quantities and source/native close agreement within0.25point at
   every input minute. Record duplicates/missing rows; conflicting duplicates fail intake rather than overwrite.
   Fee/receipt/independent raw-feed verification remain assumptions; no paid input/key/account needed.
5. **Costs:** NQ$7.25RT plus$5 per slipped fill; target needs1point through. MNQ$1.24RT plus$0.50 per slipped
   fill, independently modeled. No known empty window; exposure overlaps existing morning/daytime NQ legs.
6. **Power:** assumed1-2 events/day yields~1,200-2,400design tickets; atSD$600/NQ, t6 needs~$73-$104 net/trade.
   These are feasibility assumptions, not forecast profits. Daily dependence and multiple searches can erase a t6.
7. **Prior work:** broad flow predictors, plan-flow filters and large prints mostly failed. Opening-delta/price
   disagreement favored price over delta in a different once-daily study; it is related prior evidence, not this
   higher-frequency absorption rule. Count it, the failed Cash-Open Repair5models, and all new variants.
8. **Failure/risk:** stale flow labels, iceberg inference failure, persistent informed order flow, trend reversals,
   spread/queue costs and simultaneous NQ plan losses. Market/stop orders consume liquidity. Stops do not
   guarantee the quoted loss; no tail hedge or before-breach offset is established. Stop0.10 prior ATR, target0.15,
   max30minutes, flat14:55CT, max4tickets/day, no early/holiday entries. Data failure blocks new entries.

TEST the frozen rule and price-only controls. Reject if design fails or the flow gate only removes profitable
trades without beating matched random dropping. No promotion/live action. Continue a different preregistered
hypothesis after a failure under the user's continuing t6 mandate.
