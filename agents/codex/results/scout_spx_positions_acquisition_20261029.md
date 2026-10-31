# SPX signed-position acquisition: partial public facts; raw book remains NEEDS DATA

Summary: Saved one approximate public end-of-day MM example, a source ledger and a concrete vendor intake packet;0 raw capacity/book rows acquired.
Current Cboe terms identify a fixed July–December2022 free sample for eligible first-time users; it was not activated or guaranteed.
One-minute observations arrive2–5minutes after interval end, and historical timestamps do not prove contemporaneous subscriber availability.
No account, licence, trial, purchase, author contact or return test was initiated; the signed-book test remains blocked.

Date:2026-10-29. Target: SSRN7330098, *The Price Impact of Hedging Expiring Index Options*.
[Earlier full-source review](scout_7330098_testability_20261029.md) · [Evidence](../evidence/scout_spx_expiry_delta_20261029.md).
These acquisition records do not mark a hypothesis TEST or authorize any return command.

## Files acquired and prepared

| Artifact | Actual content and limit |
|---|---|
| [Public approximate example](../inputs/scout_acquisition_20261029/spx_positions/public_approx_eod_example.csv) | One Cboe-published rounded observation: Aug15 2023 SPX4440 put, approximately52,000 MMbuys/55,000 MMsells/−3,000 net contracts at day end. PublishedSep8; not a pre-entry signal or raw dealer record. |
| [Vendor access and price facts](../inputs/scout_acquisition_20261029/spx_positions/vendor_access.json) | Versioned current fee/sample terms, delivery and history boundaries; no entitlement or purchase. |
| [Required fields](../inputs/scout_acquisition_20261029/spx_positions/required_fields.csv) | Fifteen missing input requirements, each explicitly unacquired. This is a schema/intake checklist, not data observations. |
| [Unsent intake specification](../inputs/scout_acquisition_20261029/spx_positions/REQUEST_SPEC.md) | Exact C1/SPXW sample, inception inventory, MMvolume, quote, publication/receipt, correction and licence requirements. No message sent. |
| [Source/access ledger](../inputs/scout_acquisition_20261029/spx_positions/sources.json) | Eight public source checks, bounded negative searches and the previously denied routes that were not retried. |

The single example is a factual extraction from [Cboe's September8 2023 article](https://www.cboe.com/insights/posts/volatility-insights-evaluating-the-market-impact-of-spx-0-dte-options),
Exhibit3 discussion. It is approximate and retrospective. It cannot reconstruct a book, expose a dealer's15:30 position,
establish independent starting inventory or supply option delta. The CSV retains those false/unknown flags explicitly.

## Concrete vendor route and current terms

[Cboe's October1 2026 fee schedule](https://cdn.cboe.com/resources/membership/Cboe_FeeSchedule.pdf), printed p.12,
specifies a **fixed2022-07-01 through2022-12-31** free historical sample for eligible users of the one-minute,
ten-minute and EOD products. It is not an arbitrary selectable six-month block. Eligible TPH/non-TPH users must
not previously have subscribed to the corresponding product or received its sample. Access/licensing and eligibility
have not been confirmed; no account, trial, order or vendor request was started. The same page lists one-minute
standard rates of12,000USD/month live,4,000USD/month recent history and2,500USD/month five-or-more-year history.
These are published categories, not a requested vendor quote or authorization to spend. Academic rates are not assumed.

The current [product page](https://datashop.cboe.com/cboe-options-open-close-volume-summary) describes C1 history
starting2005 forEOD,2011 for10-minute and2019-10-07 for1-minute, with GTH coverage only from2023-12-11.
It licenses raw data for internal use and prohibits external raw redistribution. Any later licensed files belong in
the packet's git-ignored `licensed_raw/` pending confirmed processing rights; no proprietary raw files were copied to Git.

The [official February2026 filing](https://www.govinfo.gov/content/pkg/FR-2026-02-13/html/2026-02892.htm), p.6932,
footnote6, describes one-minute intervals delivered2–5minutes after interval end. It identifies the new product's2025
introduction. An archived2019/2022 trade timestamp therefore does not prove a subscriber could receive that one-minute
capacity signal at the time; original historical availability needs confirmation. Do not backdate today's SLA.

The fixed sample is also insufficient by itself to establish initial inventory for series already trading onJuly1.
Prior EOD records from each series' inception, complete sessions/corrections, matching option deltas and actual received
snapshots are necessary. T+1 trade detail may audit a book but cannot be used as a same-day signal.

## New public alternatives checked

The author data page for [Julian Terstegge](https://julianterstegge.com/data.html) exposes CarbonVIX rather than
SPX positions. His [November7 2025 FMA paper](https://www.fma.org/assets/docs/Derivatives2025/Terstegge.pdf), pp.5–6,
uses commercial daily Open-Close data for SPX/SPXW inventories over2011–2023. No attributable public replication
panel was located in the inspected author/PDF/GitHub/data searches. Daily inventories are not the required intraday
expiry book, and absence from the bounded search is not proof no panel exists.

Public FirmTape research and code-based dealer books were also inspected. Their quote/OI-based inference is not
observed MMcapacity, and its bulk dataset requires a licence/token; free individual replays are not permission to
fetch restricted bulk files. These were not substituted or downloaded. Previously blocked Cboe ZIP routes218/289
were not retried, and no host, proxy or login restriction was bypassed.

## Four paper questions, retained decision

1. **About:** Dealer hedge removal as cash-settled SPXW options expire, distinct from gamma rebalancing.
2. **Finds:** Authors' retrospective dealer-delta groups differ by17bp/30minutes and12.5bp/15minutes; not our reproduced net profits.
3. **Why could it pay:** Anticipating a signed expiring hedge's removal may capture pressure; missing book/receipt data prevent verification.
4. **Can we build:** A specific lead remains worthwhile. The next step is approved access to a complete, timestamped signed sample and an inception-to-decision reconciliation, not an OI substitute or guessed fill.

## Reproduction and result

Run from the repository with the configured Python:

    /workspace/venvs/thebeginning/bin/python analysis/codex_acquire_spx_positions_20261029.py --output analysis/outputs/codex_spx_positions_acquisition_20261029.json

[Audit script](../../../analysis/codex_acquire_spx_positions_20261029.py) ·
[Saved audit/hashes](../../../analysis/outputs/codex_spx_positions_acquisition_20261029.json).
The audit checks the example's approximate arithmetic/retrospective flags, fixed sample dates, missing-field status,
absence of licensed raw files and no account/order/purchase assertions; it hashes the acquisition packet.
It reports **1 public illustration,0 raw capacity rows,0 reconstructed book rows and0 return-eligible rows**.
This is a provenance/schema audit, not independent source truth, book completeness or an economic test.

**NEEDS DATA.** The exact free-sample/entitlement route is now concrete, but the source-equivalent signed position
history was not acquired under the current no-account/no-contact/no-purchase constraints. No financial trial or return ran.
For Claude: `agents/codex/results/scout_spx_positions_acquisition_20261029.md`.
