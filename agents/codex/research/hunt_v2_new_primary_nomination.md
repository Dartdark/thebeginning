# New independent input lead: CME margin-change observations — NEEDS DATA

Decision: **do not register H05 yet**. A public collector points to an actual exchange collateral
requirement, distinct from price/calendar/OF proxies. It supplies a concrete new source question,
but no verified complete2018–26history, original announcement/effective clock or forced intraday
futures direction has been established. A collector's observation timestamp is not an exchange
deadline. No margin values, price/data rows, signals, returns or new economic tests were read/run.

Source-only discovery,2026-10-26. Read AGENTS/BUILDER/LESSONS/task/progress and existing hunt source
maps; inspected latest adopted/ranking source7f0800f read-only. Current program3/60economic evaluations,
4/10hypotheses,2gross screens; prior65t6 preserved. New source review adds0/0/0. H01–H04 and I01–I03
stay closed; root owns counters. No old missing-input audit was rerun, no stopped web tool/403 was
retried, and no purchase/account/external message/operating change occurred.

## Question and bounded prior distinction

An exchange maintenance/performance-bond increase makes a given open futures position require more
collateral. A constrained holder can post funds, hedge elsewhere or reduce exposure. That is an actual
balance-sheet constraint, unlike inferring a collateral call from a price decline. It might support a
future fixed risk gate on an adopted piece, **if** its date, availability, product/contract coverage
and applicable effective deadline can be established before a decision.

It does not identify a compulsory market order, net long-versus-short demand, unhedged inventory or
which minute positions are reduced. Clearing members/brokers can impose different customer requirements,
and exchange margin changes respond to volatility already in prices. The strongest immediate question
is incremental risk information beyond price/volatility controls, not a new unconditional directional
trade. No parent leg, sign/threshold, holding interval or expected edge is selected by this source note.

Scoped latest TIER/MINED and local source-map searches found user strategy names containing'Margin',
account/cushion sizing and price-derived volatility/risk gates, but no exact dated CME performance-bond
change input rule. This is bounded novelty of an input question, not proof no related research exists.
Prior vol-control, VIX/regime and account-risk tests remain relevant. The closed OF filters do not
validate it; a new parent or clock cannot be picked from favorable strategy outcomes.

## New public GitHub evidence, with immutable identities

Five repository-metadata queries were made: `CME historical margin requirements`, `CME performance
bond advisories`, `futures margin changes historical data`, `CME margin`, and `GLD holdings`.
The first three returned no repository matches. The shorter CME query returned actual scraper repos
and an unrelated computer-vision'Class Margin Equilibrium' repository. The latter's README was
recognized as unrelated, not cited as futures research. No economic/data file was opened.

**Primary data endpoint referenced by collector source, not requested/verified here:**
`https://www.cmegroup.com/CmeWS/mvc/Margins/OUTRIGHT.csv`.
README points to CME's Outrights/Vol Scans margin page. A URL in source code is a provenance lead,
not a newly authenticated exchange release or historical primary-policy document.

|Public repository/source|Immutable pin/blob|Source-only finding|
|---|---|---|
|BrunoProgramming/cme_margin|commit93cc090bd7f680292436012b13c4e6fb44fc411f,2020-11-05|Tree includes `data/cme_margin.csv`,26,989,907bytes, blob21c9202c0918bd2ea017fa80baeb1e467e10241c; contents NOT read|
|Same README|blob9a71723fa768f3a586bace86c44d3d69d46c38a8|Current-margin downloader architecture, not a documented complete historical announcement archive|
|Same `cme_margin/cme_margin.py`|blob76cbe7b92c4c49bb467a5665149f90331d193f44|Official endpoint, required schema, local UTC poll timestamp and change-retention logic described below|
|Same `.github/workflows/cron.yml`|blobbd8f83d8657d4e6ea48f39a889a9222b60371ca5|Scheduled every6hours, downloads then commits changed CSV; workflow source does not prove every historical run or receipt|
|Same LICENSE|blob1b29365877d3633b25cf66c23305329e846cbc2f|MIT software license; do not infer that it grants CME-data redistribution rights|
|phungvankhanh/cme_margin|commit6fdc830e277bff852b294fb9dfc22cb61b87ac51,2020-05-19|Same collector source; tree has979,151byte CSV, bloba173b390d99f2a530b9a85ae92453b2ae669e752; contents NOT read|

Exact first candidate URL for a future committed intake, **not fetched here**:
`https://raw.githubusercontent.com/BrunoProgramming/cme_margin/93cc090bd7f680292436012b13c4e6fb44fc411f/data/cme_margin.csv`.
The schema below is the code's required-column subset, not a verified exact header order/full schema
for that CSV. The pinned file's actual header and metadata coverage still need intake.

Only README, source, workflow, license, branch/commit and tree metadata were fetched. Neither scraper,
container nor any remote code was executed. A subsequent origin-repository metadata lookup did not
yield a usable structured metadata object; it was not retried or treated as a verified archive.
No assumption follows that the two forks are independent observations or together cover2018–26.

One additional modern-archive metadata query, `cme_margin fork:true pushed:>2023-01-01`, returned
potential code projects. One candidate's immutable tree was inspected:
`andyhudson80/cme-im-dashboard@2e1ff53543f7aa87e0e3f02a3f5cc6f1b7f8824c`(2026-04-16), containing only
`index.html`(52,012bytes, blob5caf82cb4e6255c3166b344f289b3adcf77ececb) and `render.yaml`(179bytes).
No historical CSV is in that tree. Neither file body was opened, since an HTML dashboard might embed
numeric observations. No additional data file was acquired/selected; no2023+archive was verified by
this bounded metadata extension. A modern app timestamp does not establish historical data coverage.

## Exact schema/clock pitfalls before any intake

The collector requires `Time,Exchange,Asset Class,Product Name,Product Code,Start Period,End Period,
Maintenance,Currency,Maint. Vol. Scan`. It inserts `Time=pd.Timestamp.now(tz='UTC')` after downloading.
Thus Time is a **collector poll time**, not the exchange's announcement, original publication, effective
session, customer call or executable receipt. `Start Period/End Period` identify product-period buckets;
the source does not establish that they are margin-change effective dates. They must not be renamed.

Exact producer statement, read as source code only:

```python
margin.insert(loc=0, column="Time", value=pd.Timestamp.now(tz="UTC"))
```

The workflow uses `cron: '0 */6 * * *'`. These statements establish the **intended poll clock**;
neither contains an original exchange announcement/effective-date field or a proven customer deadline.

The merger appends observations and groups by Exchange+AssetClass+ProductCode+StartPeriod+EndPeriod+
Currency, retaining rows when Maintenance differs from the previous grouped row. It does not retain
every unchanged poll, raw HTTP response, original exchange timestamp, revision notice or explicit
announcement/effective-date field. Missing unchanged polls cannot prove uninterrupted availability;
the first retained bucket observation is not necessarily a new margin increase. A new contract bucket,
currency convention, product rename or sample start can create a new first row without a policy change.
The implementation itself does not sort each group by Time before comparing adjacent rows.

No data values were inspected to decide whether NQ/MNQ or any other relevant product exists, how often
its requirements change, whether counts are complete, whether Time is monotone or whether the archive
even contains more than2020. No full-year or funding/payout inference is justified by file size or
commit dates. Historic git timestamps and an automated workflow are useful source context, not a
certified original exchange/collector receipt log or proof of an unrewritten complete history.

## Least-cost next source gate, if root pursues this new question

Before economic registration, obtain a primary exchange rule/advisory description establishing the
meaning/applicability of maintenance requirements, announcement versus effective session, product/period
mapping and relevant historical policy changes. Use permitted public sources; do not alter network
policy, buy data or infer a primary deadline from third-party code. No unconditional futures direction
or intraday entry should be invented while this link is missing.

Then commit a separate bounded **non-return** intake before source values. Start with one pinned
collector snapshot only, explicit license/provenance limits, exact headers/hashes and strict target
product identity. First inventory date/product/period/currency metadata, duplicate/conflict/ordering
states and candidate coverage; no price file, trade list or strategy output. If required periods or
identity are absent, stop rather than concatenate another favorable archive. Only after a frozen
numeric stage may valid maintenance changes be counted, separating first observations, contract-bucket
changes and genuine same-bucket revisions. Preserve every original row ID and incomplete attempt.

This could determine whether a usable independent constraint-history input exists. It cannot turn
poll Time into an authenticated original release/effective clock, manufacture missing2018–19or2021–26,
or establish a future forced order. If point-in-time availability and a defensible book risk mechanism
are later supported, write a new TEST sheet, choose a single parent/rule before returns, retain old
risk-filter multiplicity, COMMIT<=5definitions, then2018–22gross and all ordinary v2 gates. No such
TEST/plan or source admission is claimed now. No H05 counter is charged merely for this source question.

## A separate new avenue stopped without data

A helper performed three new bounded GitHub searches for GLD prospectus/custodian/settlement evidence.
Only secondary commentary/examples were returned; no verified issuer/SEC prospectus/AP-clock text was
established. GLD physical-basket transfer differs from UGL's reset, but published holdings changes can
reflect already-settled transfers, preexisting inventory and expense sales. They do not identify pending
AP orders or a later compulsory GC purchase. No10:00London/T+2historical obligation or holdings-publication
clock is asserted. The GLD-holdings metadata query identified a tracker repository but no holdings rows
were fetched. This avenue supplies no TEST, reused UGL audit or reason to execute the user's templates.

**NEEDS DATA / primary clock evidence; no new economic experiment justified by this lookup.** This
bounded result is not a global search-exhaustion claim, user-action blocker, budget pause or t6 restart.
