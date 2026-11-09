# Evaluation macro inputs: acquired; source validation remains open

Summary: The futures files, release calendars and macro actual/forecast panel are already in the repository.
The current issue is validating those inputs, not asking the user to acquire them again.
Saved official calendars corroborate 60 CPI and 60 payroll release dates; 249 claims clocks match.
One payroll clock error is resolved in a derived sidecar; the original dataset is unchanged.
No strategy return test ran; historical forecast/first-actual provenance still needs checking.

User steering: “We have the data alr I think.”
Script: `analysis/codex_eval_owned_macro_reconcile_20261109.py`.
Output: `agents/codex/inputs/eval_focus_20261109/macro_reconciliation/`.
Return trials: **0**; no new economic definition, plan/live/schedule change or scout-history update.

## Inventory actually checked

- Existing local raw files: ten annual daytime/full-day files per market, 2017–26, for NQ, ES, YM, GC, CL, 6E and ZN. NQ also has the separate overnight exports. This is a file inventory, not a certification of every interval, roll or native contract.
- Codex's already committed official BLS/BEA/Fed release calendar: `agents/codex/inputs/scout_acquisition_20261029/fx_calendar/primary_release_calendar_2018_2022.csv`.
- Already committed claims calendar and official embargo-header facts: `agents/codex/inputs/scout_acquisition_20261029/claims_calendar/`.
- Macro actual/forecast panel acquired and saved in the preceding task: `agents/codex/inputs/eval_focus_20261109/macro_intake/snapshot/data/investing-us-macro-consensus.json`.
- `data/macro_proxies_daily.csv` contains daily market proxies (rates/ETFs/commodity prices), not announcement actual/forecast values. It cannot substitute for the latter panel.

Both branch trees were checked; latest fetched Claude head `8b9f27d`. No additional macro surprise/forecast panel was found there. Its new stop-day/gap-fade research does not change this input inventory. No external contacts or paid data request was made.

## Reconciliation using existing data, 2018–22

| Series | Actual + forecast rows | Official date matches | Official clock facts available | Matching clocks | Discrepancies |
|---|---:|---:|---:|---:|---:|
| Headline CPI YoY | 60 | 60 | 60 | 60 | 0 |
| Core CPI YoY | 60 | 60 | 60 | 60 | 0 |
| Nonfarm payrolls | 60 | 60 | 60 | 59 | **1** |
| Initial jobless claims | 261 | 261 | 249 | 249 | 0 |
| Retail sales MoM | 60 | Not covered by this saved agency calendar | — | — | Not assessed |

Headline/core CPI are different series on the same 60 release dates, not 120 independent events. Official archived schedule/printed embargo facts do not establish historical vendor receipt timestamps. Twelve 2018 claims rows retain unknown printed embargo times; no weekday/time guess fills them. Retail needs its Census source cross-check, not an assertion that the numerical rows are absent.

## Payroll clock repair

The macro occurrence panel timestamps March 6, 2020 payrolls at **12:30 UTC**, equivalent to **07:30 New York** that day. Our existing official BLS calendar lists 08:30 New York / **13:30 UTC**.

The [BLS release, page 1](https://www.bls.gov/news.release/archives/empsit_03062020.pdf) independently prints **8:30 a.m. EST, March 6, 2020**, with a payroll headline of **+273,000**. The original vendor timestamp is preserved. The derived `clock_sidecar.csv` records 13:30 UTC as the source-supported clock and identifies its provenance. It does not fill an actual feed receipt or forecast-availability field.

The current PDF discloses a September 23, 2020 reissue concerning selected household tables. It is not an original March network capture. Do not use it to certify that every historical actual or field is unrevised.

## What is still being checked

The remaining admission questions are the forecast's pre-release value/definition, initial actual versus later revision/correction, source-version rules and publication-to-entry availability. These are data-validation questions. No additional user acquisition is needed to perform the next audit of the material we already have. That is not a guarantee no further source evidence will ultimately be needed.

The previous “missing data” shorthand was too broad: field coverage and official calendar evidence are present. Their presence alone does not clear a one-minute announcement-surprise strategy for returns. The active evaluation research task continues through its source/clock/vintage gate without resetting any prior trial, invoking a duplicate scout or treating an available file as verified profitability.
