# Antigravity's readings of Pedersen, *Efficiently Inefficient* (2015) and Chan, *Machine Trading* (2017) — Claude's review (2026-10-18)

Source: antigravity/jesse `tasks/out_book_pedersen_inefficient/` (30 ideas) and `tasks/out_book_chan_machinetrading/` (39 ideas).
Both lists are honest about Apex fit (almost everything is stocks, bonds held for months, options or crypto). Each
shortlist (3 ideas) is an ADAPTATION by Antigravity, and the "forced trader" stories are its own inferences, labelled as the
books' (brief rule 0 again).

| Shortlisted idea | Status |
|---|---|
| Pedersen #1: intraday time-series momentum on NQ (first 30 min / session trend → rest of day) | already tested: Market Intraday Momentum (Gao et al.) F, 'from-open' trend model, ORB family, Mesfin |
| Pedersen #2: ZN momentum after 7:30 macro releases | **tested now** (`analysis/zn_release_momentum_test.py`): 255 release days, follow the 7:30-7:35 move, out 9:00 / 14:00, stop none / 8 ticks: −$22 to −$46 a trade (t −1.0 to −4.6), ≈ 0 before the $38.50 cost; F |
| Pedersen #3 / Chan ML #3: CL opening-range breakout (with 1-month trend / GARCH filter) | generic breakout; CL session windows already tested (CL forced flows rounds 1-3, D / F) |
| Chan ML #1: CL breakout after the EIA report | already tested: EIA follow +$11 to +$21 before the cost bite, fade −$65 (F) |
| Chan ML #2: ZN autoregressive intraday trend | generic momentum with a free t-stat threshold; the ZN release test above is its strongest case and fails |

Verdict: no new trade from either book. Pedersen is the best of the books for the "who is forced" thinking, but its
strategies are multi-month; Machine Trading is ML on stocks / options / crypto.
