# Rousse–Sévi WTI inventory information: NEEDS DATA / no causal pre-release strategy

Summary: The uploaded 2016 paper associates pre-EIA selling with subsequently revealed inventory surprises.
Its source experiment is observational, not a frozen ex-ante trading rule or a net-return backtest.
Owned minute CL bars and 165 component releases do not supply tick OI or the Bloomberg survey dispersion.
No economic trials. Do not select pre-release shorts with the later surprise label or repeat failed price-only fades.

Source: Rousse and Sévi, *Informed trading in oil-futures market*, November 4, 2016,
[SSRN 2874907](https://ssrn.com/abstract=2874907), user-supplied 34-page PDF.
SHA256: `c1ab7b57b5ec30d1fe5ecf14f38a92797951e3a5ec24fb4b70ce305ba0270544`.
Review: [full assessment](../results/rousse_sevi_oil_2874907.md).
Audit: `analysis/codex_rousse_sevi_oil_input_audit.py` → `analysis/outputs/codex_rousse_sevi_oil_input_audit/audit.json`.

## 1. Participant and cause

Informed traders may trade before an inventory announcement; public-news traders subsequently reprice WTI.
Superior analysis and anticipation can also explain the result: authors explicitly do not establish a leak.
No measured mandate or compelled dollar quantity is supplied. The statistical association does not identify
participants or give us access to their information. This is a possible informational advantage, not forced flow.

## 2. Direction, size and clock

Positive inventory surprise means actual inventory change above survey expectations, economically bearish oil.
Table 3 finds negative order-imbalance coefficients before such releases, despite contradictory buyer wording
in the abstract/body. No standalone predictive threshold or future-price target was validated.
The source sample has 402 announcements, February 2007–October 2014, including 43 positive 3σ surprises.
Exact dollar flows are not given; a normalized imbalance cannot establish order size without its denominator.

| Field | Availability | Consequence |
|---|---|---|
| Individual forecasts / survey median and dispersion | Forecast vintage before announcement; exact receipt needed | Predictor input only if genuinely known at decision |
| Published actual inventory change | Announcement plus receipt/parsing delay | Cannot select an earlier trade |
| 3σ positive-surprise classification | Requires both actual and survey | Retrospective label for pre-release analysis; usable after release only |
| Tick-rule OI over a window | After its complete ordered tape is received | Cannot fill at the beginning of that same window |
| A post-release reversal | Entry strictly after actual receipt and decision | First announcement jump is not capturable retrospectively |

Use event-relative clocks. The paper calls its times EST but figures say Eastern time; resolve historical DST,
10:35/11:00 exceptions and our CL export timezone before aligning any data. Standard 10:30 New York is 09:30
Chicago with local DST rules; a fixed UTC−5 assumption is not established. No order/fill protocol is frozen.

## 3. Transmission

Source observations are directly in front-month NYMEX WTI CL, with volume-based contract switching.
No direct NQ/ES alpha follows from a discussion of oil affecting equities. A CL finding would require its own
CL/MCL execution and account tests, not an NQ point-value conversion.

## 4. Independent inputs and feasibility

| Input | What we have | Missing / limits |
|---|---|---|
| CL | Ten yearly minute OHLCV files, 2017–26; dates/schema inspected without price returns | No source-period 2007–14 tape; no ordered transactions or source OI |
| EIA component data | 165 admitted design-panel rows with component changes | Zero rows marked verified release clock or immutable first publication; no consensus/dispersion |
| Survey | No matching panel identified by owned-data discovery or bounded primary-source/web check | Bloomberg individual forecasts or verified median plus cross-sectional SD, vintages and usage rights; cost unquoted |
| Actual release events | Existing official calendar/source captures; current EIA page accessible via connected web | Complete first-print values, exceptions, receipt, matching exact inventory series |

The paper's prose says total petroleum excluding SPR; any replication must reconcile its exact Bloomberg event
with the official series rather than assume all petroleum components or substitute another inventory total.
Cross-sectional forecast SD is not a rolling time-series SD of actual changes. API news released after the survey
can change the market's information set; a later API estimate cannot be backdated into the forecast vintage.

## 5. Costs and account gaps

No gross-to-net strategy bridge is demonstrated by the paper. Its conditional average price curve is not an
executable return. Existing repository CL convention is $7.25/CL plus one $10 tick per market/stop fill ($27.25
round trip for two fills); it is a historical research assumption, not a verified current MCL fee or event spread.
New work needs announcement spread/gap stresses and native whole contracts. Same-symbol Sunday CL exposure,
weekday macro losses and before-breach diversification are unmeasured; no occupancy-based event selection.

## 6. Power before returns

At the old sample's 43/402 positive-event frequency, 260 design weeks would yield about 28 eligible events
before exclusions. This assumes unchanged frequency, not observed 2018–22 data. Assuming 0.5% trade SD gives
an approximate t=2 net-mean hurdle of 0.19% per event, before multiple-testing adjustments and cost additions.
These calculations are in the audit JSON. The paper does not supply a trade-return SD, independent post-entry
net returns or a power claim that satisfies the strategy gates. Do not pool events or relax thresholds afterward.

## 7. Prior work and falsifiers

No exact SSRN/title hit found in TIER_LIST/WATCHLIST or saved Codex review search.
Existing F-tier CL studies already tested unconditional EIA pre-drift, first-five-minute follow/fade and sweep
fades (`analysis/cl_forced_flows_test.py`, `cl_forced_flows_round2_test.py`). Repeating these is not this paper.
The separate EIA-component input project remains NEEDS DATA and does not supply analyst surprises.
Falsifiers before returns: unavailable survey vintages, wrong series, unreconciled tape/timezones, too few events,
or any use of actuals before publication. No independent out-of-sample predictive model has been established.

## 8. Failure and diversification

| Question | Pre-test limit |
|---|---|
| Mechanism failure | Public anticipation, absorption, survey staleness, pit-era dependence or false inference of informed trading |
| Liquidity role | A marketable entry consumes liquidity; source OI is not a fill-quality or spread-saving measure |
| Clustered losses | Oil shocks, wrong event clocks, gap-through stops and small event count |
| Common losses | Possible macro/oil exposure overlap; joint chronology unmeasured |
| Offset before account breach | None demonstrated; annual diversification cannot establish intraday protection |

## Decision

**NEEDS DATA** for faithful mechanism replication or a separately preregistered post-release strategy.
**DON'T TEST** a pre-release rule selected with the future surprise, or an OHLCV stand-in for tick OI.
The smallest later check, only when matching data arrives, is one-event timestamp/series/tick-sign reconciliation,
then a no-return design coverage/power census. No promising-strategy queue entry: the paper does not yet supply
a causal rule with demonstrated net merits. Retain the execution lesson in E49. No new return test, tier change,
account comparison, order code, installation or live change follows from this review.
