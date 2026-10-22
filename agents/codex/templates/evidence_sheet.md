# <candidate>: <TEST / NEEDS DATA / DON'T TEST>

Summary: <question, current evidence, decisive limitation, cheapest next step; at most five lines total>

Sources: <primary sources, effective dates, local paths / pinned commits>
Return trials: <all variants already examined, including failures; zero if none>
This sheet precedes a strategy preregistration. TEST means eligible to write that plan, not permission to trade.

## 1. Who trades, and what forces or causes the trade?

<Identify participant, obligation/mandate/hedge/deadline and why another participant cannot absorb it for free.
Separate source facts from predictions. Explain why the mechanism still operates today.>

## 2. Direction, size and timing known before entry

<Define information available at decision time, publication versus receipt, expected direction, rough dollar flow,
comparison with contract volume, and the decision → order → fill → exit clock with timezone/DST conventions.
Label assumed sizes and hedge fractions. Do not infer the force solely from a prior price move.>

## 3. Does the flow reach the traded contract or its direct hedge?

<Explain transmission to NQ/ES or their micro contracts; identify netting, options, cash baskets and other offsets.
A similar benchmark is a plausible connection, not proof of incremental futures demand.>

## 4. New information and data feasibility

| Input | Source / exact product and fields | Historical coverage / warm-up | Point-in-time timing / revisions | Owned, free, or verified cost |
|---|---|---|---|---|
| <input> | <primary URL> | <verified versus advertised> | <known versus unresolved> | <include licence / receipt limits> |

<State what varies independently of price momentum/reversal; identify required controls. A directory listing,
worked example or sample establishes only what was actually inspected. Retain original data/provenance and hashes
when later obtained. No keys in reports. Archive inputs for a later forward phase when separately scoped.>

## 5. Costs and actual intraday gaps

<Compare plausible gross move against commission, spread, slippage and latency; identify actual hours with no open
position from the saved occupancy map. State source/roster snapshot. Distinguish weekday averages from overlap on
candidate events. Do not select edge-test events based on whether the existing plan is flat.>

## 6. Power before a return test

<Give 2018–22 opportunity count, assumed/observed event frequency and warm-up loss, plausible SD, and the net mean
needed for t ≥ 2: approximately 2 × SD / sqrt(effective n). Add costs for the gross hurdle. Label assumptions,
account for clustering and multiple trials, and stop if the requirement is implausible. This is not promotion.>

## 7. Already tested and falsifiers

<List TIER_LIST / WATCHLIST / analysis hits and pinned reviewer references. Explain the incremental input or
mechanism. A different ticker or a reversed direction need not create a new family. State observable results that
would refute the prediction before returns; failure does not authorize changing the clock, direction or threshold.>

## 8. Failure and diversification — required supplement

| Question | Prediction before results | Evidence needed / what would refute it |
|---|---|---|
| What would stop the mechanism working? | <absorption, information repricing, mandate/rule change, crowding> | <observable failure> |
| What liquidity role do our actual orders play? | <marketable or passive, expected adverse selection and missed fills> | <quotes / fills; strategy style alone does not determine order type> |
| How could losses grow or cluster? | <persistent trend, whipsaw, illiquidity, gaps, data outage> | <predeclared scenarios and executable risk at proposed size> |
| Which existing strategy shares those losses? | <name, time overlap, common factor; label unmeasured> | <joint losses / conditional P&L later, not only average correlation> |
| Could an offset arrive before an account breach? | <entry timing versus loss timing; account and symbol netting> | <chronological account replay later; annual diversification is insufficient> |

Specify proposed stop/time exit, data-failure handling and maximum concurrent exposure before a return test. Stops
have execution risk; neither a stop nor a paired strategy guarantees protection. Do not size from a short smooth
track record or the Gaussian mean/variance approximation to Kelly; general Kelly itself does not require Gaussian
returns. A mean-reversion rule is not necessarily short volatility, and a trend rule is not necessarily a useful
tail hedge: report observed state-dependent behavior later rather than assigning protection from the label.

At the later account stage compare base, addition, replacement and empty-slot control, at actual contract sizes and
costs. Report payout ranges, blow-up risk and time to six payouts, along with concurrent exposure and loss timing.
Do not add hedges to another account as a workaround; existing account/netting restrictions still apply.

## Decision and next gate

**<TEST / NEEDS DATA / DON'T TEST>** — <reason and smallest next action>.
Keep source inspection, no-return data checks, descriptive mechanism studies and strategy validation separate.
Preserve cheap-screen stop rules: plan committed before returns, at most five variants, 2018–22 design first;
2023+ only after the design gate and described honestly if already seen, then independent review, the funded bench
and a separately frozen forward log before any trading decision. Count every return variant actually examined.

This supplements `agents/codex/BUILDER_BRIEF.md` and `DEVELOPMENT_PROCESS.md`; it does not loosen either standard.
