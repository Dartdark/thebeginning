# PrimeSync ES/NQ 15m/30m: TEST — an assumed reconstruction for a cheap screen

Summary: User requested code and a comparison of full-target versus partial-profit exits.
Rules are incomplete; the parameters in the plan are explicit, unoptimized implementation assumptions.
No supplied trade list or numerical results independently establishes an edge or institutional participation.
Eligible for a bounded design screen, not promotion or live trading.

Source: user's PrimeSync description and follow-up, 2026-10-27.
New return trials before this sheet: 0. Author's previous search count unknown.

## Mechanism and information

Hypothesis: a completed-bar SMA150 cross, VWAP side, elevated volume/range and
non-chop conditions predict continuation. No forced buyer, deadline, parent order
or residual demand is demonstrated. Volume/expansion also proxy volatility and
price momentum; a same-session random-side control is required before promotion.
All features use completed bars, followed by next-minute open execution. Use total
futures volume (Ticks), not MC's intraday up-volume field. VWAP is a chart-bar
typical-price/volume approximation from 08:30 CT, not trade-level VWAP.

## Feasibility, direction and executable risk

Use existing NQ/ES Grid24 caches and 15/30-minute aggregated bars, full Globex
indicator history, normal cash sessions only. Source missing-minute and roll
contamination must remain visible. Direction is symmetric long/short; no side
selection is authorized. Default details are frozen in plans/primesync.md.
Fixed $500 micro-equivalent stop-risk budget; quantities divisible by 3 in both
exit styles so one-third exits are executable. Entry/stop slippage, native assumed
micro fees and limit trade-through are charged. Overnight/carry is prohibited.
No evidence of a presently empty portfolio time window is established.

## Power, prior work and falsifiers

Actual event counts/dispersion are unavailable before construction; report counts
and stop if fewer than 100 total context-events or fewer than 30 per context in
design. Correlated contexts cannot be treated as independent trade observations.
Related MA/VWAP/ADX momentum and generic breakout screens in TIER_LIST have often
failed; this exact SMA150 reconstruction was not located. A superior exit alone
does not establish a profitable entry. Net losses, random-side-like results,
unresolved price paths or disappearing gains after roll exclusions refute advancement.

## Failure/diversification

Whipsaw, delayed fills, gap-through stops, missing bars, changing volume semantics
and repeated macro shocks can cause losses. Likely overlaps VB/ONB/RS/FC2B/ST/PT;
neither the trend label nor a stop guarantees an account-level hedge. Stop and
target levels remain frozen to actual entry and the initial ATR risk. No widening
after favorable milestones; partial exits do not manufacture extra observations.
No inferred payout or personal-portfolio benefit is permitted without later replay.

## Next gate

Commit the plan before returns. Two exit variants, applied to the four user-named
market/timeframe contexts: eight evaluated cells, transparently counted; no search
over contexts or entry parameters. Select one common exit style on design only.
Full account comparisons and recent validation require the design gate; an exact
MC/Python match and independent review remain prerequisites for any placement.
