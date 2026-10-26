# Hunt v2: annual commodity-index reweighting source gate — NEEDS DATA

Decision: **no TEST candidate is established**. Genuine, preannounced annual target-weight changes could
be a different input from the repository's monthly commodity-roll calendar proxies. The required
vintaged weights, pre-rebalance exposure, index-linked assets, implementation clocks and identified
contract mapping were not established in this source-only review. A January-only calendar restriction,
different window or price-direction substitute would revisit a known family rather than supply them.

This review adds **0 hypotheses, 0 gross screens and 0 counted economic evaluations**. At the checkpoint
read here v2 had3/60 counted evaluations,2/10 hypotheses and2 gross screens. H01 and H02 remain CLOSED;
the archived65 t6 evaluations and earlier commodity searches remain selection history. Root owns counters.

## Sources and scope

Read AGENTS.md, BUILDER_BRIEF.md, RESEARCH_CONTROLS.md, LESSONS.md, TASK_strategy_hunt_v2.md and the current
progress record. Consulted repository map/process/brief/watchlist instructions and existing hunt source
maps. Latest fetched Claude source inspected read-only: **615485f**, including TIER_LIST.md and
MINED_INDEX.md. Branch/writes remain codex/work; the Claude source location does not authorize writes there.

Targeted source searches covered annual commodity target weights, GSCI, BCOM, commodity-index rebalancing,
January and relevant existing scripts. Input filenames were inventoried under data/ and agents/codex/inputs/.
No raw price rows, financial CSV bodies, trade lists, saved returns or account arrays were opened. No strategy
module was imported/executed, no network acquisition or web search was attempted, and no completed source
or data audit was rerun. An independent source-only helper checked prior definitions without file edits.

## Exact prior-family distinction

| Existing definition | Source | Consequence |
|---|---|---|
| Short continuous CL on business days5–9, front-run on1–4, compare with other days | analysis/cl_forced_flows_test.py:107–118 | This is an already researched monthly calendar proxy, not observed annual target-weight demand. |
| Business-day groups1–4,5–9(GSCI),6–10(BCOM),11+, individual days1–12, overnight/day/settlement-hour/after windows | analysis/s_rank_cl_round1_test.py:204–226 | Moving the clock or choosing January does not erase this extensive calendar/window selection history. |
| Monthly front-running and roll-window studies ranked | TIER_LIST.md at615485f, rows around195 and329; MINED_INDEX consulted | Existing negative studies remain relevant. No actual announced annual-weight/AUM input was found in this scoped source search. |

This establishes a distinction between inputs, not a new gross edge. It does not establish that every
public annual-reweighting study or all possible commodity strategies have been exhausted.

## Mechanism question before data

**Participant/cause:** an index-tracking fund or a dealer hedging an index-linked liability may need to
move exposure toward newly published annual target weights. The tracking mandate could impose a scheduled
rebalance. That is a plausible participant and obligation; neither its actual outstanding futures-linked
assets nor the fraction hedged through the relevant CL/GC contract was measured here. An index name or
published target percentage alone is not proof of an executable futures order.

**Direction and size:** new target minus the previous year's target is insufficient. Returns, monthly
rolls, asset subscriptions/redemptions and contract prices change actual pre-rebalance weights and
contract counts. The needed input is the change from the *then-current* executable exposure toward the
new target, with an independently supported linked-asset/hedge estimate. Routine rolls simultaneously
sell one month and buy another; annual reweighting can add or remove exposure. Combining them into a
single front-month direction without contract mapping could assign the wrong sign.

**Clock:** an archived announcement/publication time, locally usable availability allowance, applicable
methodology vintage and exact implementation session/contract schedule are needed for every year. A
generic monthly business-day convention does not verify annual effective dates, holidays, methodology
changes or when the newly announced information could first be traded. No new event_time, available_at,
decision_time or first-fill clock was admitted in this review.

**Transmission:** genuine commodity index exposure concerns the constituent futures rather than a stock
index proxy, but an owned continuous CL/GC export does not identify all index-held contract months. The
existing CL source expressly describes an unadjusted continuous front month rolling before expiry.
Separate month paths/IDs may be necessary to distinguish outright annual demand from calendar-spread
roll pressure. No synthetic spread or expiring-month path may be invented from that continuous series.

## Specific input and power limits

The scoped filename/source inventory found named CL and GC one-minute annual exports2017–26, but no
admitted GSCI/BCOM annual announcement/weight/AUM archive. File presence does not verify row coverage,
native micro prices, contract identity, licence or as-of history. Their market values were not opened.

Before a TEST decision, establish:

1. Dated, authentic2018–26 annual target-weight publications and methodology/effective-date vintages,
   including publication versus actual usable receipt/availability times.
2. Corresponding pre-rebalance actual weights/exposure and an independently supported linked-asset/
   hedge quantity. Do not infer a dollar-flow estimate solely from price returns or old target weights.
3. Index contract schedules and observed month identities/paths matched to owned price exports; retain
   any irreducible continuous-contract limitation rather than silently changing the traded instrument.
4. Native MCL/MGC commission, tick/slippage and decision-to-fill assumptions, plus a simple frozen
   time/stop exit and matched calendar-only control. No raw gross hurdle or return has been measured.
5. A credible power calculation. Design2018–22 offers only five annual reweighting episodes per index;
   several days or two commodities from one episode are dependent observations, not dozens of independent
   annual shocks. The user prefers100+ trades, but counting windows cannot manufacture independent power.

No requests to buy data, create an account, alter network policy or use a live/VPS/broker system follow.
No newly verified primary-source panel was acquired, so no eight-question TEST evidence sheet or strategy
preregistration was written. The unverified input/clock/power questions stop this idea before raw returns.

## Next action

Preserve this as **NEEDS DATA / no current TEST** for an actual announced-weight-driven annual rule.
Do not substitute a January calendar trade, normalize old returns or tune a window after inspecting CL/GC
outcomes. A genuinely new admissible input could justify a future mechanism sheet and committed finite
preregistration; the present source note does not consume or reset the economic budget, pause the hunt,
claim a workspace-access blocker, or establish a book improvement.
