# I04 CME collector metadata: 2020-only archive, no economic nomination

Summary: one pinned archive was acquired and its timestamp/identity metadata inventoried. It covers
May 16–November 5, 2020 only. NQ/MNQ appear on eight poll dates and ES/MES on five; these are not counts
of margin increases. No maintenance amount was interpreted. Missing history and primary release/
effective clocks prevent admission for the2018–26 goal. No H05 or qualifying book candidate follows.

**Running budget:3/60 economic evaluations,4/10 registered hypotheses,2 gross screens; archived t6 = 65.**
I04 adds 0 to each. All previous failures and source/selection history remain preserved.

Mechanism: `agents/codex/evidence/hunt_v2_new_primary_nomination.md` (NEEDS DATA).
Source: `agents/codex/research/hunt_v2_new_primary_nomination.md`.
Plan: `agents/codex/plans/hunt_v2_cme_margin_metadata_intake.md`, initial **7ff1d6a**, effective
reviewed code/plan **03e2b52**, committed/pushed before acquisition.
Script: `analysis/codex_hunt_v2_cme_margin_metadata.py`, SHA256
`29e7b12936bf3f11426abdab056265c8110edd84be372f989473cd4a7ff5d136`.
Review: `agents/codex/reviews/hunt_v2_cme_margin_metadata_preexecution.md`.
Outputs: `analysis/outputs/codex_hunt_v2_cme_margin_metadata/`.

## Question and archive identity

Exchange collateral requirements are a distinct potential risk input: an increase can require more
collateral from applicable clearing exposure. Constrained holders can post funds or offset/reduce
positions; no compulsory futures side, hedge fraction or intraday deadline follows automatically.
The prospective question was whether a genuine published requirement change could add information
beyond existing price/volatility controls on an adopted piece. No parent, trade clock or threshold
was selected and no trading TEST was justified.

The GitHub app identified the new public collector snapshot. Its oversized raw CSV was downloaded
once through the permitted pinned GitHub URL into the ignored local cache, without an account,
purchase, CME endpoint request, redirect or retry. Metadata interpretation began only after these
bindings passed:

| Binding | Measured identity |
|---|---|
| Repository | BrunoProgramming/cme_margin |
| Immutable commit | 93cc090bd7f680292436012b13c4e6fb44fc411f |
| Path | data/cme_margin.csv |
| Bytes | 26,989,907 |
| Git blob SHA1 | 21c9202c0918bd2ea017fa80baeb1e467e10241c |
| SHA256 | ab5c00d9e2d182143b58bddb28dd30fde336b9ae0a5984c78295330c45910829 |

The exact ten-field schema matched the producer-code subset. Only Time,exchange,asset class,product
name/code,period-label strings,currency and original record IDs were interpreted. Maintenance,
Maint.Vol.Scan and every other financial field remained unselected/unconverted. The collector's
MIT software license does not establish CME-data redistribution rights; the full raw file remains
local and Git-ignored. Saved ledgers contain factual metadata and immutable source identifiers.

## Actual metadata coverage

The once-only intake ran20:39:14–20:39:25 UTC on 2026-10-26. It inventoried241,391 rows and 1,609 raw
product-identity combinations, with125 distinct poll timestamps on 124 UTC dates. All timestamps were
valid explicit UTC and all observed rows belonged to 2020. The archive starts
2020-05-16T17:29:19Z and ends2020-11-05T06:13:41Z.

| Fixed target label | Rows | Distinct poll dates | First poll UTC | Last poll UTC |
|---|---:|---:|---|---|
| NQ | 12 | 8 | 2020-05-16 17:29:19 | 2020-09-29 06:16:59 |
| MNQ | 12 | 8 | 2020-05-16 17:29:19 | 2020-09-29 06:16:59 |
| ES | 11 | 5 | 2020-05-16 17:29:19 | 2020-09-19 00:40:29 |
| MES | 11 | 5 | 2020-05-16 17:29:19 | 2020-09-19 00:40:29 |

The observed target names are E-MINI NASDAQ 100 FUTURES, MICRO E-MINI NASDAQ 100 FUTURE,
E-MINI S&P 500 FUTURES and MICRO E-MINI S&P 500 FUTURES, under CME/EQUITY INDEX/USD. Exact raw strings
and contract-period labels are retained; these observations do not substitute for original CME
product/applicability documentation. No alternative code was selected after inspection.

Required years 2018, 2019 and 2021–26 are absent for all four targets. There are0 invalid timestamp rows,
0 empty identity rows and 0 raw/canonical duplicate metadata groups. The original global sequence has
17,898 time decreases; same-raw-contract-bucket sequences have 0. Global ordering can reflect grouped
storage; neither statistic establishes margin-level correctness. Original order was retained.

The producer saves selected changes rather than every unchanged poll. Twelve NQ rows across eight
dates are not twelve increases, eight independent policy shocks or eight known effective sessions.
Initial/bucket observations and changes cannot be distinguished without a separately authorized
numeric stage. Missing dates cannot be filled into a continuous observed margin state.

## Clock and evidence boundary

Time is inserted by the collector after a download. It is not an exchange announcement, effective
deadline, original public receipt or applicable customer collateral call. Start/EndPeriod describe
contract buckets and were never relabelled as effective dates. The intended six-hour cron does not
prove every poll succeeded or that unrecorded observations were unchanged. No modern full historical
archive or authenticated primary policy/effective-time panel was admitted.

The final status is **DIAGNOSTIC_ONLY_NEEDS_PRIMARY_CLOCK_AND_HISTORY**. This snapshot cannot support
the requested design/history or2023+validation. No numeric margin stage, price series, strategy,
gross/net return, five trading metrics, t/DSR, placebo, Monte Carlo, current-book bench or PowerLanguage
was run. There is no invented collateral-to-futures order conversion or funded/pass/payout claim.

## Verification and next action

Seven synthetic groups and independent metadata/transport mock checks passed before acquisition.
The executed program rechecked code and cache bindings; root verified all 11 saved artifact hashes
and confirmed the raw cache is Git-ignored. Compressed ledgers retain every target row, metadata
duplicate/invalid record and sequence flag. The original attempt is immutable; it was not retried.

This source intake is complete and unadmitted. Do not reopen it unchanged, append a convenient fork,
invent missing years or infer primary deadlines from poll times. A genuinely new admissible primary
history/clock could support a future source question; H05 would still need its own TEST sheet and
committed finite economic plan. Continue distinct research under the remaining budget. This is no
user-action blocker or reason to pause the program; t6 and its watcher remain stopped.

Claude review: `agents/codex/results/hunt_v2_cme_margin_metadata.md`.
