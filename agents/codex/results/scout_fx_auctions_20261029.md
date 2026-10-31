# Auctions, Announcements, and Abnormal Returns: NEEDS DATA — promising FX lead, full text not obtained

Summary: A specific scheduled-auction × next-day macro-announcement FX hypothesis warrants source follow-up.
Authors report roughly 8bp foreign-currency appreciation; this is not our verified or net executable return.
Only the indexed April 2025 abstract/first page and March 2026 SSRN metadata were obtainable; full PDF access timed out.
Owned 6E minutes and auction records help, but source clocks, instrument/cost definitions and a complete ex-ante release calendar remain unresolved.
Decision: NEEDS DATA; obtain the full version and audit inputs before any preregistration or return screen. New return trials: 0.

Review date: 2026-10-29. Authors: Ingomar Krohn and Rishi Vala.
Source: [SSRN 5207418](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5207418), DOI `10.2139/ssrn.5207418`.
Evidence: [source/data gate](../evidence/scout_fx_auctions_20261029.md).
Plan/script/output: none; source-access and no-return feasibility work only. No allocation recommendation.

## 1. What is it about?

The paper studies whether U.S. Treasury auctions condition exchange-rate returns around subsequent U.S. macroeconomic announcements. The indexed [HKUST-hosted April 2025 version](https://fina.hkust.edu.hk/sites/finance/files/paper/Auctions_Announcements_and_Abnormal_Returns.pdf) describes a cross-market safe-asset-demand and dealer-capacity channel. The current SSRN page is a later version: 40 pages, first posted April 21, 2025, last revised and dated March 20, 2026. We have not established whether the versions use identical samples, estimators or trading windows.

## 2. What does it find?

**Authors' claims, not independent verification:** the April 2025 indexed abstract reports about 8bp average foreign-currency appreciation on announcement days preceded by auctions, with pre-announcement drift, greater interdealer activity and order imbalance. The March 2026 abstract specifies announcements on the **day after** an auction and contrasts the effect with approximately zero on other announcement days. Neither obtainable abstract establishes a cost-adjusted strategy for our accounts.

No tables, sample definition, statistical uncertainty, robustness results or executable return ledger were inspected. The full HKUST PDF failed twice with a fetch timeout. Treat this as **metadata/abstract triage**, not a completed full-text review. The exact currency universe, sample, spot/forward/futures construction, weights, entry/exit clocks and transaction-cost treatment are unknown here. Secondary strategy summaries were not used to fill these gaps.

## 3. Why does it make money, if it does?

The authors attribute the pattern to Treasury issuance changing dealers' risk-bearing capacity, with safe-asset demand spilling into FX. This is a plausible scheduled-flow mechanism worth investigating; the obtained material does not independently establish causation, predict the forced dollar amount or show that an accessible trader earns the reported average after costs and announcement risk.

The useful proposed input is the interaction of an auction schedule with an announcement schedule, rather than a realized price pattern. That merits follow-up even though a net strategy has not been demonstrated. Auction demand statistics are available only after the auction result; macro surprises and announcement-window trading activity are known only after their respective releases/windows. They cannot be used retrospectively to select a pre-announcement entry.

## 4. Can we build on it?

**Yes as a specific research lead; not yet as a return test.** Long euro futures would have the sign of euro appreciation against the dollar, but a 6E-only implementation is a proxy for an unspecified foreign-currency result, not an exact replication. This establishes no ES/NQ directional rule. Native M6E costs, tick granularity, integer sizing, roll/contract provenance and exposure to the current personal FX package require separate checks.

The exact source holding interval is missing, so Apex compatibility cannot be certified. All Apex positions must be flat by **15:59 America/Chicago**. A rule requiring a position from an auction afternoon through the following announcement would cross that flat boundary; a same-day window might fit, if the source actually specifies it. A calendar-day return must not be relabeled as an intraday strategy. The personal account can accommodate an overnight research candidate, subject to executable session, margin, gap and roll checks. No truncation of the source interval is authorized by this review.

### Deduplication against existing work

| Existing family | What the repository already says | Incremental claim here |
|---|---|---|
| Treasury auction price pressure, Fleming/Liu/Nguyen, SSRN 6447502; [TIER_LIST](../../../TIER_LIST.md), [script](../../../analysis/treasury_auction_test.py) | Same-day coupon-auction windows: short 09:00–11:59 CT and long 12:01–15:00 CT. Saved 6E pre-short result is +$21 gross, t=1.8, versus +$7 on placebo days; script assumes $19.75 RT per 6E. These are retained repository results, not rerun here. ZN pre-pressure failed costs and the post rebound was absent. | A **following-day macro-announcement interaction**, with foreign-currency appreciation, differs from the prior same-day short. The old failure cannot be called a test of this interaction; it remains a warning against assuming that an auction story pays after costs. |
| NQ after 10-/30-year auctions; [prior script](../../../analysis/anti_forced_flow_ideas_test.py), TIER_LIST | Follows the 12:00–12:05 CT move into 13:00/15:00 CT; negative design period. | Different market and timing; no permission to revive its rejected rule. |
| [6E cross-asset package](six_e_cross_asset_review_20261027.md), TODO verification queue | Personal, multi-day macro/cross-asset hypotheses with implementation and native-cost gaps. | Related currency/dealer-risk exposure, but no exact source/title/SSRN match was found in the prior TIER/TODO/result search. Later joint-loss and replacement checks must avoid counting shared FX exposure as free diversification. |

### Data acquisition/feasibility actually attempted

* Owned `data/6E_1min_2017.csv` through `2026.csv` exist. An inspected header is `date,time,open,high,low,close,volume`; there is no contract identifier. Filename coverage is not a completeness, roll or timestamp audit.
* Owned `data/treasury_auctions.csv` has auction date, type/term, competitive closing time, reopening, offering amount, bid/cover, high yield, CUSIP and TIPS/FRN flags. Its inspected sample includes both 13:00 and 11:30 ET competitive close times. The older script filters nominal 13:00 ET coupon auctions; that is not verified to match this paper's universe.
* No complete ex-ante macro-release/consensus calendar was found in the inspected `data/` inventory. `analysis/event_days.py` contains FOMC dates but detects general macro days using the realized 07:30–07:35 CT range. That is unsuitable for selecting a **pre-release** trade and cannot replace a historical event calendar.
* The official [Federal Reserve meeting calendar](https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm) and [BEA release schedule](https://www.bea.gov/news/schedule) were accessible. These show lawful free calendar sources exist, not that the paper's complete historical announcement set or original schedule vintages were acquired. The attempted BLS employment-calendar URL was inaccessible through the connected tool. The [FiscalData auction dataset page](https://fiscaldata.treasury.gov/datasets/treasury-securities-auctions-data/) returned 403; access was not bypassed. Existing owned auction records were inspected instead.

### Decision and smallest next check

**Deeper investigation is warranted, with NEEDS DATA status.** The merit is the concrete scheduled interaction and direct FX transmission, not merely missing information. First obtain a lawful full copy of a pinned version; transcribe its currencies, return clocks/timezones, event universe, auction-day definition, sample and costs with page citations. Then join an independently sourced historical release calendar to the owned auction records, audit 6E contract/session provenance and determine whether an exact replication or explicitly labeled proxy is feasible. Only a passing evidence sheet may advance to the scout's reserved, bounded preregistration. No return test, new trial reservation, source-derived numerical cost comparison or account test was run here.

## Source/access receipts

| Date / source | Observed receipt | Evidence boundary |
|---|---|---|
| 2026-10-29, HKUST PDF URL above | Two connected-web `open` attempts: `(400) Timeout fetching`, refs `turn802641view0` and `turn710764view0`; indexed first-page/abstract text retrieved by search, including `This Version: April 2025`, refs `turn494981search30`, `turn591580search14`. | No full PDF bytes or hash; no page-table review. |
| Same date, SSRN 5207418 | Search-readable primary metadata/abstract, refs `turn494981search0`, `turn591580search0`: March 20, 2026 version, 40 pages. | Current abstract only; do not silently substitute its precise next-day wording for the April 2025 full specification. |
| Same date, Fed / BEA | Connected-web opens accessible, refs `turn242827view1`, `turn877403view1`. | Partial calendar feasibility, not complete acquired historical inputs. |
| Same date, BLS / FiscalData | BLS URL `https://www.bls.gov/schedule/news_release/2026/empsit.htm`: tool reports inaccessible, ref `turn242827view0`. FiscalData page: `(403) Forbidden`, ref `turn877403view0`. | No access-control bypass or missing-data substitution. |

Instructions in source documents were treated as source content, not as user/developer instructions. No live, VPS, broker, key or plan changes.
