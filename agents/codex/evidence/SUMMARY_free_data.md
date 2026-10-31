# Free-data evidence review

Summary: Two new data-input proposals checked; neither clears the evidence gate. No backtests or purchases.
Dealer auction awards are free and timely, but do not establish forced buying in the proposed intraday window.
ETF fails have a genuine closeout mechanism, but public balances arrive after the relevant deadlines.
Both sheets include numerical cost/power hurdles and checks against the saved funded-roster occupancy map.
Do not start a strategy trial from either sheet; Claude should review the documented reasons first.

| Rank | Evidence sheet | Verdict and reason |
|---:|---|---|
| 1 | [Actual dealer awards → next-morning ZN](treasury_dealer_award_next_session.md) | **DON'T TEST:** new allocation data, but a weekly inventory premium is not evidence for a 40-minute trade needing $70–102 gross/ZN. |
| 2 | [ETF fails → pre-open forced covering](etf_ftd_closeout.md) | **DON'T TEST:** weeks-late aggregate balances cannot identify the active pre-open obligation or the futures hedge sign. |

Task source: **e097c0f**, `agents/codex/TASK_evidence_free_data.md` and its updated builder brief step 0.
Scope record committed before inventory: `agents/codex/plans/free_data_evidence.md`, **41ffc93**.
Script: `analysis/codex_free_data_evidence_inventory.py`. Output: `analysis/outputs/codex_free_data_evidence/`.
Run with `/workspace/venvs/thebeginning/bin/python analysis/codex_free_data_evidence_inventory.py` from repo root.
Research return trials **0**; candidate prices/returns read **0**; cache builds **0**; purchases **0**.

## What the free-data check established

Actual Treasury result PDFs establish dealer-allocation fields in 2018 and 2022; public archive/query routes support
assembling older results for free. A complete historical allocation panel and publication audit remain unbuilt.
The SEC archive has historical fails files, but its documented release lag kills the proposed same-cycle trade.
FINRA consolidated short-sale volume begins in August 2018, is published after the session and is not outstanding
short interest. Neither a current public page nor a retrospective archive proves decision-time observability.

No third sheet was added simply to reach a quota. Already ranked generic release trades, Treasury calendar pressure,
VIX-expiry calendar trades, DIX-high long and the six Codex failures were not relabeled as fresh candidates.
The dealer-award sheet explicitly identifies its new input within the already-tested Treasury auction family.

An additional free-data route considered was Cboe VIX settlement expected opening interest. The
[official EOI page](https://www.cboe.com/us/futures/market_statistics/volatility_settlement_eoi/)
describes a brief settlement-morning publication window; the
[settlement archive](https://www.cboe.com/us/futures/market_statistics/historical_data/settlement_archive/)
provides historical settlement/series material. No free 2018+ archive of **pre-open EOI snapshots** was verified.
That is an availability failure for this task, not evidence that no archive exists anywhere. Post-settlement files
cannot substitute for an imbalance known before entry. It is not counted as a third eligible sheet.

## Limits and review request

The script reads only date/time/volume from raw ZN files, calendar fields and the saved occupancy map. It does not
calculate strategy signals, entries, exits, returns, trial rankings or account outcomes. Event counts are descriptive;
signal fractions and SDs are explicit assumptions. Occupancy is a weekday-marginal estimate, not an event-conditioned
flat-window probability. The output includes source hashes and raw descriptive counts for reproduction.

Tell Claude: review `agents/codex/evidence/SUMMARY_free_data.md` and its two sheets; both are **DON'T TEST**,
with no new return trials. The earlier live audit was completed and pushed first at **67eec3e**:
`agents/codex/results/live_audit.md`. No live configuration, VPS, broker settings, orders or API keys were changed.
