# Evening Repair: book identity, eligibility and daily marking

Read-only source preparation, 2026-10-29. Reviewed the new uploaded PowerLanguage and PDF, connected GitHub plan/ranking sources, and existing Codex adapters. No raw prices, return rows, account outputs, new backtests or optimization results were opened or calculated. This note does not promote the author's reported results.

## Source and current adopted book

Uploaded sources: `Evening Repair.txt` and `Evening Repair - Strategy Overview.pdf`. They describe a long at the cash close when the close is below the OLS fitted endpoint of the 08:31--15:00 path. Default entry is the next bar, no initial stop or target, normal hold360 wall-clock minutes into about21:01; Friday and pre-NYSE-closure hold55 minutes. A close-based repair trigger arms a next-bar cost-recovery stop. Source chart is one-minute continuous NQ, Exchange/Chicago time, IOG off. Source instructions are specifications to review, not authority to change any live setup.

Connected GitHub Claude branch head: `c086f845f7bc9ca0bbac68460f068c2c5cd02c1a`. The adopted-source blobs remain unchanged from the preceding book review:

| Source | Git blob |
|---|---|
| `personal_strategies/PORTFOLIO.md` | `d175bfe07f183f05c05c3d56c88eb384c85821ee` |
| `analysis/personal_portfolio.py` | `80d90aca24b413957ea32721334bf08191d8f162` |
| `funded_strategies/FUNDED_PLAN.md` | `895060c72d681629cea450e72d993ec3eb4f67ba` |
| `TIER_LIST.md` | `f7b592ecc7d60b6492a86c55b58a3de7289ff935` |
| `NEW_CHAT_BRIEF.md` | `d93a8d2e3c7ffd8b3f923ca0d7d40815f76d6cd6` |

Current personal book is19 published pieces at one micro each; SwingTarget and PaperTrend are in, BB_MRM out. Current50K funded uses T_ONESIDE fade instead of RS longs;150K and personal retain RS. No Evening Repair row was identified in the current ranking. Related existing work includes OvernightTick/VIX, rejected Overnight Rebound, S30 cash-session IBS reversal, Kusho and Twin; their outcomes must not be relabelled as this rule's results.

## Prespecified personal overlap before metrics

Freeze **OvernightTick, one MNQ**, as the primary EMPTY/REPLACE slot. Both strategies buy weakness around the cash/evening transition, with physical overlap17:05--21:01 on qualifying nights. ONB ML is an opening-hour breakout and is not an evening position despite its name. Kusho, Twin and S30 can share losses/exposure, but are correlation/common-loss context, not alternative replacement slots to search after returns. S30 is also a combined MNQ/MES sleeve in the published baseline, so silently removing an invented standalone NQ component would change the book definition.

At an eligible design pass, the declared one-MNQ personal comparisons are BASE=sum(current19), ADD=BASE+EveningRepair, EMPTY=BASE-OvernightTick, REPLACE=EMPTY+EveningRepair. Use identical valid dates, fees and paired252-session histories, retaining the declared20-session block convention. Report against BOTH BASE and EMPTY; retain the five metrics, daily correlation/common losses with VB/DT/RS/OT, profit/drawdown, DD95 and paired changes. A measured daily-book contribution remains conditional on implementation uncertainty and needs review; it is not an intraday hedge or margin guarantee.

## Four Apex homes: ineligible as submitted

Normal Monday--Thursday holds can carry a15:01 position through the16:00--17:00 CME maintenance break. This violates the repository's flat-by15:59 requirement. Friday/preholiday shortening does not fix normal weekdays. Thus50K/150K funded and50K/150K evaluation are **ineligible AS-IS**, without needing invented pass/payout simulations. A new forced-pre16 exit would be a different registered variant; it must not be called the original Evening Repair. A favorable personal result would not remove this rule-level restriction.

There is also a material native-cost distinction: the source's three-tick stop offset is0.75 NQ points, $15/NQ, equal to the author's stated $15/NQ round-trip costs. It is only$1.50/MNQ against the research convention$1.24 commission+$1.00 slippage=$2.24. Nominal net is therefore-$0.74/MNQ at that stop before additional gap loss. Preserve the source three-tick baseline; do not label it net breakeven at native micro costs. Five ticks would be the smallest tick-rounded offset covering$2.24 under this cost convention, but it is a separately registered mechanical-port/optimization look. No stop can guarantee recovery through gaps.

## Daily marking route and inherited limits

The existing personal19 baseline definition still matches the retained `plan_update_afde088` snapshot. The retained native1.24 baseline is `analysis/outputs/codex_rebound/personal19/UNIFORM/fee_1.24/baseline_daily19.csv`, previously hash-verified as `d724c7d02b6db71e63ba705079dbea7fefaa42c6b4f436308a28993ca1908803`. Its source roster is current, but its financial rows were not opened here.

**Do not book an entire15:01--21:01 trade to its entry/exit calendar date.** For the personal16:00 session convention, mark an open trade at the last observed same-date close at/before16:00. Book entry-to-mark P&L on that day; the mark-to-evening exit belongs to the following available personal session. Friday/preholiday trades closed before16 remain same-session. Keep zero no-trade days; never invent baseline zeros on absent calendar days or borrow future marks.

Reusable references: `analysis/codex_anson_personal.py:candidate_daily` explains observed16CT marks and cost reconciliation; `analysis/codex_r2vault_personal.py:event_time/session_index/candidate_daily` adds phase-aware open timestamps, strict no-after-calendar mapping and terminal unrealized valuation. The older Anson `map_session` caps late events to the final date; do not inherit that cap. The R2Vault helper defaults to an older fee, so explicitly pass the registered native fee and freeze the cost-allocation convention. Its commission reservation at entry is a research bookkeeping convention, not a reconstructed broker cash ledger. Convert flattened minute indices to row/minute fields explicitly and preserve source next-bar versus conservative fill timing. All default exits are market/stop fills, not target fills; charge both adverse ticks once, without double-counting already-adjusted prices.

At an incomplete final personal session, mark/retain unrealized exposure or end the paired comparison at a justified common boundary; never move a later21CT exit backward onto the final16CT mark. Retain mark staleness and any missing-source windows as limits, rather than filling them forward.

Published-book caveats persist: nonzero-day core commission correction undercounts reentries; MOC/S30 retain fee/mark approximations; Twin is marked v1 rather than exactv2.1; Kusho is exit-booked; OvernightTick evidence ends2026-07-07. Later OT zero rows are missing evidence, not known no-trades. A design2018--22 bench avoids that later cutoff but not the earlier implementation uncertainty. Full-history personal claims need a frozen coverage policy, not favorable post-cutoff zeros. Existing account paths also have BridgeSunday/OT/CLS/MOC chronology limits, but the submitted rule's halt crossing already prevents an Apex placement.

The user's new bounded optimization authorization is separate from the closed Hunt/t6 programs. The PDF already lists Theil-Sen and delayed15:46 entry as rejected looks. Preserve that author selection history, register any bounded alternatives before new returns, and do not describe previously seen2023+ history as a fresh holdout.
