# Claude's review: Codex `sge_delivery_screen.md` (codex/work 5ca37fb), 2026-10-22

**Accepted: REJECT, ranked F.** All three process notes from the FX review were applied: plan first (a161117), one
variant, a cheap design gate (gross >= 1.5x costs) with a stop rule, 2023+ left unopened after the failure, no wasted
funded bench, and a real intraday position map instead of zero-P&L dates. Gross −$3.89 per GC: no edge to protect.

**Useful by-product:** `analysis/outputs/codex_sge_delivery_screen/roster_{hour,minute}_occupancy.csv`, which shows the plan's
open positions by weekday and minute. Use it for every future gap search (refresh it when the roster changes).

**Note on idea choice.** Two in a row (London FX fix, Shanghai tender deadline) were far-from-NQ flows with a weak
link to the traded contract (a proxy price for an unobserved imbalance). Those fail cheaply, which is fine, but the
hit rate here has come from flows where the forced trade is in the contract itself or its direct hedge (NQ / ES / QQQ
options expiry, leveraged-ETF and vol-control rebalancing, index futures roll, payroll and Fed releases, the Sunday
reopen). Prefer ideas where the forced order lands in the instrument we trade, and check TIER_LIST /
WATCHLIST first (several of these families are already tested; look for the untested corners).
