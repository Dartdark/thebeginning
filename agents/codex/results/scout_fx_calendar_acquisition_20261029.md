# FX paper calendar acquisition: usable facts acquired; exact paper test remains NEEDS DATA

Summary: Acquired943 primary calendar/header facts for2018–22:783 BLS,118 BEA and42 Fed statement documents.
The calendar includes60 CPI,60 Employment Situation,60 PPI,59 national GDP-estimate and59 PCE-release rows.
A separate591-row public-repository inventory preserves secondary provenance and exclusions; all180 CPI/NFP/PPI dates match the official schedules.
Original schedule availability/receipt remain unknown; five BEA10:00ET exceptions and three off-cycle Fed clocks are retained.
No prices or returns were calculated; full source-paper event definitions and historical advance-knowledge checks remain open.

Date:2026-10-29. Related paper: Krohn/Vala, [SSRN5207418](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5207418).
This acquisition supplies actual machine-readable calendar data, not a claim that the entire paper or strategy can now be replicated.
The [earlier source/testability review](scout_5207418_testability_20261029.md) remains the source-specification boundary.

## Files and reproduction

- [Primary calendar CSV](../inputs/scout_acquisition_20261029/fx_calendar/primary_release_calendar_2018_2022.csv): government calendar/header facts with local and UTC times, source URLs, locators, status and explicit unknown-knowledge fields.
- [Separate secondary CSV](../inputs/scout_acquisition_20261029/fx_calendar/secondary_calendar_inventory_2018_2022.csv): public-repository date inventory. It is not merged into the primary calendar or silently adopted as our event-selection rule.
- [Source evidence folder](../inputs/scout_acquisition_20261029/fx_calendar/): BLS extracted calendar facts, BEA line evidence and two2018 header checks,42 Fed statement header facts/access receipts, and version-pinned secondary date facts.
- [Offline builder/validator](../../../analysis/codex_acquire_fx_calendar_20261029.py) and [manifest](../../../analysis/outputs/codex_fx_calendar_acquisition_20261029.json).

From the repository:

    /workspace/venvs/thebeginning/bin/python analysis/codex_acquire_fx_calendar_20261029.py

The builder reconstructs both CSVs from retained source facts, validates date/weekday and UTC conversion, checks12 CPI and12 Employment Situation rows per year, reconciles secondary dates and writes hashes/counts. It never reads price data or computes a financial return.

## Actual coverage

| Material | Acquired rows | Evidence scope |
|---|---:|---|
| Official BLS annual schedules2018–22 | 783 | All acquired timed entries, including60 each CPI, Employment Situation, PPI, JOLTS and import/export prices;20 ECI and55 productivity/cost releases. Other timed BLS items remain retained. |
| Official BEA annual schedules | 118 | 59 national GDP-estimate and59 Personal Income and Outlays rows; regional GDP and state PCE are not relabeled as national releases. |
| Official Fed statement headers | 42 | 8/8/10/8/8 published statement documents by2018/19/20/21/22; not42 scheduled meetings. |
| Secondary Midas date inventory | 591 | 259 initial-claims,60 each CPI/NFP/PPI,56 retail-sales,19 advance GDP,38 later GDP estimates and39 curated scheduled-FOMC dates. Its exclusions remain explicit secondary curation. |

The source-printed clocks are preserved. BEA PCE10:00ET exceptions occur on2018-12-21,2019-11-27,2019-12-20,2020-11-25 and2021-11-24. The first is independently corroborated by the official release header;2019's two exceptions are printed in footnote3 and the later ones appear as explicit row exceptions. Blanket08:30 labeling would be wrong.

Fed headers explicitly print14:00ET for39 documents;2020-03-03 prints10:00EST,2020-03-15 prints17:00EDT, and2020-03-23 prints08:00EDT. These are declared release clocks, not first wire receipt or proof that the corresponding event was scheduled beforehand. Meeting dates remain unknown in the source facts. The2020 corpus includes off-cycle actions and is not an eight-meeting template.

## Sources and acquisition evidence

The [BLS2018 annual page](https://www.bls.gov/schedule/2018/home.htm) and matching2019–22 pages were accessible through the connected reader. Actual dated rows were extracted; monthly release dates were not generated from first-Friday or other calendar rules. The pages explicitly state Eastern Time. Their current archival contents do not prove original pre-event publication or actual dissemination.

BEA material came from the [2018 official PDF](https://www.bea.gov/sites/default/files/2017-12/2018rd.pdf),
[2019 SCB schedule](https://apps.bea.gov/scb/issues/2018/12-december/1218-news-releases-2019.htm),
[2020 schedule](https://apps.bea.gov/scb/issues/2019/12-december/1219-news-releases-2020.htm),
[2021 schedule](https://apps.bea.gov/scb/issues/2020/12-december/1220-news-releases-2021.htm) and
[2022 schedule](https://apps.bea.gov/scb/issues/2021/12-december/1221-news-releases-2022.htm).
The2018 PDF prints times but no zone; New York context is supported by2018 primary PCE headers for [July31](https://www.bea.gov/news/2018/personal-income-and-outlays-june-2018) and [December21](https://www.bea.gov/news/2018/personal-income-and-outlays-november-2018), not by individual checks of every2018 header. That distinction is in the CSV clock-evidence field.

The2019 SCB page explicitly says it incorporates new dates following the government shutdown. Its printed December19,2018 issue date is **not** evidence that later calendar edits were known then. No available-at timestamp is fabricated from the issue date, mirror filename or today's retrieval.

[BEA's January30,2019 delay notice](https://www.bea.gov/news/blog/2019-01-30/new-dates-set-some-delayed-releases)
explicitly identifies the originally scheduled January30 GDP advance and January31 December-PIO releases as delayed,
with new dates still undetermined in that notice. The revised annual page later shows February28 initial GDP
(replacing advance and second estimates) and March1 December-PIO combined with January personal income only;
its footnote excludes January outlays from that combined event. The retained [schedule-history facts](../inputs/scout_acquisition_20261029/fx_calendar/bea_shutdown_schedule_history.json)
keep original plans and later revised dates separate. This is why the current calendar has59 GDP-estimate and59 PIO
rows across five years rather than a nominal60 each. No canceled January release, duplicate GDP estimate or missing
outlays event was filled in. Revised calendar rows remain schedule facts, not independently verified actual releases.

The public [Midas repository](https://github.com/chris-cheshire/project-midas-mk7) was read at commit`f9e756cbbca3a0576178412a48e1e374c9c76cfe`. Only factual dates were extracted with attribution; no foreign code was run or copied, and no repository license was found. Selected original file hashes and commented date mentions are retained. Secondary claims/GDP/retail curation may omit genuine releases and cannot dictate our universe. Independent primary schedule checks agree on all60 CPI,60 NFP and60 PPI dates in2018–22. The first macro repo examined, YangXiaoShawn/open-economic-quant-macroeconomics at`276b6746752afb5485545fbaf482ae290d905f6d`, documented release-clock acquisition but did not commit the required empirical calendar files; its synthetic fixtures were not used.

U.S. government calendar/header facts are cited to their agencies; logos and endorsement are not implied. U.S. Bureau of Labor Statistics data were transcribed into research fields on2026-10-29; BLS cannot vouch for data or analyses after retrieval. This acquisition used no BEA API, key, purchase, login, subscription or author contact.

## Remaining gates

**Paper connection:** it is about auction timing and following-day macro-announcement FX returns; its roughly8bp result and dealer-capacity mechanism remain author claims. Calendar acquisition helps build a later replication, but is not return verification or recovery of the full paper's currency basket, event universe, holding interval or costs.

Every primary and secondary row leaves original schedule-publication/available-at and actual feed receipt blank. The source-paper event selection remains unverified, and current archived calendars may contain revisions. ADP, ISM manufacturing and Conference Board source histories were not acquired here and are not assumed paper requirements merely because a secondary review mentions them. Initial-claims primary acquisition is being handled separately by the parent task.

The next check is to bind the full paper's actual event specification to these sourced facts, reconstruct schedule changes/advance knowledge where needed, and audit the matching futures contract/session history without looking at returns. Only a TEST evidence sheet, committed bounded preregistration/code/reservation and checked-head lease can open a gross screen. No return trial, plan change or allocation occurred in this task.

For Claude: `agents/codex/results/scout_fx_calendar_acquisition_20261029.md`.
