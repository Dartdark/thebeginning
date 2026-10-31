# Distinct input feasibility: bounded offline screen

Summary: No new TEST decision is justified by this repository-only screen. Several documented mechanical
flows require missing timely inputs or an unestablished intraday economic link; other available rules
already belong to tested families. This is not an exhaustive search or a claim that no distinct edge exists.
The EIA source intake and the broader standalone research program remain active.

Scope: instructions, saved evidence, source-code definitions, filenames and CSV headers only. No raw price
values, strategy return ledgers, new return calculations, network calls or execution/account tests. New economic
configurations evaluated: zero. No changes to failed-family gates, milestone records or notification settings.

| Mechanism | Local evidence / input | Concrete limitation and decision |
|---|---|---|
| Persistent QQQ auction imbalance transmitted to NQ | `agents/codex/plans/nasdaq_closing_faq_evidence.md`; `agents/codex/evidence/qqq_closing_imbalance_persistence.md`; saved exchange FAQs under `agents/codex/inputs/nasdaq_closing_faqs/` | Rules document a real auction clock, but timely historical QQQ NOII messages and receipt evidence are absent. Futures OHLCV cannot replace the missing imbalance. NEEDS DATA. |
| Pre-fix month-end equity hedging transmitted to 6E | `agents/codex/research/month_end_fx_hedging_feasibility.md` | Relative-country equity inputs and the actual historical WMR publication calendar remain unverified. A US-only return is an incomplete proxy; month-end alone supplies at most 60 design events. NEEDS DATA. |
| ETF delivery closeouts transmitted to ES/NQ | `agents/codex/evidence/etf_ftd_closeout.md` | Public aggregate balances arrive after relevant deadlines and do not identify active participant obligations or the futures hedge sign. The saved specification is DON'T TEST; no replacement is proposed here. |
| Dealer inventory distribution after Treasury auctions | `agents/codex/evidence/treasury_dealer_award_next_session.md`; `agents/codex/evidence/SUMMARY_free_data.md` | Actual remaining inventory, required hedge direction and an intraday distribution clock are unobserved. The saved award-based specification is DON'T TEST. Another auction-price/calendar variation would recycle existing work. |
| Treasury settlement / reserve-drain flow | Header of `data/treasury_auctions.csv` | The local schema lacks issue/payment/maturity dates and the inputs needed for net settlement cash flows. Auction dates, offering amounts and bid-to-cover alone cannot establish this different mechanism. NEEDS DATA and an evidenced futures transmission link. |
| A new response to COT publication | `data/COT_NQ.csv`; `analysis/bridge_cot_test.py`; `analysis/cot_flows.py`; `analysis/cot_reversal_index_test.py` | A local release-clock input exists, but existing rules already use dealer-rank states. No saved evidence establishes a new post-release direction or compulsory short-window futures order. No TEST decision. |
| Measured leveraged-ETF reset demand | `agents/codex/plans/ldf_flow_sizing.md`; `agents/codex/evidence/ldf_flow_sizing.md` | Historical lagged fund-asset inputs support an existing LDF upgrade. Reusing its direction or moving its window is not a distinct mechanism. Current-day creations/redemptions needed for a different flow claim are not established before entry. No new TEST decision. |

## COT clock correction

`analysis/bridge_cot_test.py` explicitly describes `data/COT_NQ.csv` as chart-time-stamped releases,
including holiday and shutdown catch-up dates, used only from the following bar. It would be incorrect to
say that the repository contains no COT release-clock input. These chart timestamps still do not establish
original publication/receipt or revision provenance. Their existence does not identify a new forced order.

## Boundary for the next step

The saved inventory also covers expiry hedging, index rolls, pension rebalancing, settlement, auction calendars
and Shanghai delivery deadlines. Existing examples include `analysis/forced_flows_round5_test.py`,
`analysis/calendar_flows2_test.py`, `analysis/index_rebalance_reversal_test.py`,
`agents/codex/plans/sge_delivery_screen.md` and `multi_strategy/PRACTITIONER_SOURCES.md`.
They are guidance and prior trials, not fresh candidates merely because a clock, ticker or threshold changes.

Continue the committed EIA source work and later distinct evidence searches. A new hypothesis can advance
only after its observable input, causal link, clock, opportunity count and native-cost feasibility support a
TEST evidence sheet and a separately committed economic preregistration. This screen adds no trial,
milestone, new user-action blocker or reason to pause research.
