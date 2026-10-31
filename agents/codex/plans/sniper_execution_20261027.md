# SniperAlgo: frozen mechanics review, not an alpha backtest

Scope: review the user's pasted SniperAlgo and account placement. One unchanged code configuration; zero new economic evaluations. No markets, returns, parameter sweep, strategy rescue, Hunt restart, PowerLanguage or account/live changes.

Evidence: [execution-only feasibility gate](../evidence/sniper_execution_20261027.md).
The supplied class corresponds to the public MIT-licensed vnpy/vnpy_algotrading SniperAlgo. Public upstream sources are pinned to commit `bee959dc464749f7cce66e766249ccdbb2d4869a` and copied under `agents/codex/inputs/sniper_review_20261027/public_upstream/`, with license. These are public source copies, not new private input exports.

## Frozen procedure

Use a disconnected, deterministic harness. Execute the original SniperAlgo and upstream AlgoTemplate class bodies, plus upstream engine send/cancel/order/trade routing methods. Supply minimal in-memory contract/order/tick/trade objects and a fake gateway. Do not import vn.py into an active gateway, install packages, connect to a broker or issue external messages. Integer synthetic contract volumes only; the replacement rounding helper is restricted to that tested domain. Preserve source hashes and event traces.

Predeclared cases:

1. Paused template suppresses new orders.
2. An unfavorable buy quote produces no order.
3. A favorable buy quote caps child size at displayed ask depth and uses the caller's limit price.
4. A favorable sell quote uses displayed bid depth and forwards CLOSE offset.
5. Partial fill accounting updates before the callback; after cancellation, only the unfilled target is resubmitted.
6. A completed quantity finishes the algorithm and suppresses subsequent tick orders.
7. The next tick cancels a live child even if the quote remains favorable.
8. Further ticks repeat cancellation requests until terminal acknowledgement.
9. Before order acknowledgement the retained ID prevents resubmission, but active-order cancellation may have nothing to cancel.
10. An invalid zero ask with positive quoted size passes the class's buy condition; determine what reaches the fake gateway.
11. Zero depth produces zero quantity; determine whether inherited engine protection prevents a gateway order.
12. A delayed terminal callback for an older order arrives while a newer one is active; inspect ID tracking and possible simultaneous children.
13. A cancellation reports a partial fill before its trade callback; inspect resubmission and cumulative filled quantity when the delayed and new fills arrive.
14. Timer callbacks without new ticks do not supply a missing execution deadline.

Checks assert what the fixed source does; reproducing an unsafe behavior is **not** a safety pass. Invalid quotes and asynchronous event sequences are constructed stress examples, not observed historical losses. The fake gateway does not simulate queue priority, true latency, exchange fills, rejection policy, slippage or account returns. Do not infer production framework parity from passing harness assertions.

## Decision and placement

No valid standalone backtest exists without an external signal, complete entry/exit schedule and executable fill data. Record metrics as unavailable, not zero. All five plans receive explicit no-standalone-slot verdicts; execution research is conditional and carries no measured benefit. Report whether inherited protections change any initial static concern. Save the original behavior and failures without modifying the supplied algo. Do not bench invented parent orders or change plans to fit this utility.
