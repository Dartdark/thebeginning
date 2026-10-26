# Hunt v2: pre-fix relative-equity input resolution — NEEDS DATA

This is a new source-resolution question for the previously saved
`month_end_fx_hedging_feasibility.md`, not a repeat post-fix return experiment. It asks whether NEW
admissible relative-country equity inputs and a conservative calendar restriction could make a bounded
pre-fix6E study feasible. **No TEST evidence sheet or preregistration is justified yet.** Root owns any
later input admission and hypothesis decision.

This review adds0hypotheses,0gross screens and0counted evaluations. No raw prices, equity data values,
trade lists, return ledgers or financial code were read/run. No existing source audit, blocked request or
web-search tool was retried. New connected-GitHub searches and one repository tree-name inventory were
limited to finding primary documents; no secondary trading implementation was executed or accepted as
evidence of performance. H01/H02 remain CLOSED; this is not an H02 data repair.

## What the existing primary-source review establishes

The saved feasibility note cites Melvin and Prins'2013 ECB-hosted paper, pp.4–5 and10–11:

https://www.ecb.europa.eu/events/pdf/conferences/131216/Third_FX_Workshop_MELVIN_PRINS_Equity%20hedging%20and%20exchange%20rates%20Nov%202013.pdf

It records portfolio currency hedgers, month-end adjustment at the London16:00fix, orders submitted at
least an hour before the fix, lagged country equity outperformance through the next-to-last day, and
cross-sectionally demeaned currency returns. That is a participant/obligation/clock hypothesis distinct
from fading6E's own pre-fix price move AFTER the fix. It is not a claim of current net futures profitability.

The underlying paper PDF/text was **not archived in this workspace**. The saved note does not preserve
the exact country/index list, weighting/normalization equation, local-versus-common-currency equity
convention or precise sample/end-point handling. I cannot certify a faithful formula from its summary.
The new GitHub discovery found secondary implementations/reference notes but no primary-paper copy;
their code and claims cannot fill those gaps. No original ECB/LSEG/SSRN URL was requested in this review.

## Direction: separate documented claim from a conditional algebraic translation

Documented broad claim from the saved review: a country's equity outperformance creates a need to sell
more of that country's currency to restore a currency hedge before the month-end fix. A US-only equity
month return omits relative exposure, as already recorded in the earlier feasibility note.

Conditional modelling identity, **not a verified quotation or formula from Melvin–Prins**: suppose a
currency-j prediction is a COMMON-slope negative function of `R_j - mean(R_countries)`. Then subtracting
the USD prediction from the EUR prediction to predict EURUSD cancels the shared cross-sectional mean;
the direction is proportional to `R_US - R_EUR`. Under that assumed model, US outperforming Eurozone
equities predicts EURUSD appreciation, so long6E; Eurozone outperforming predicts short6E.

This algebra does not establish that the paper uses the assumed identical slopes, that its portfolio
construction maps directly to one EURUSD future, or which equity indices it requires. A pairwise US-minus-
Eurozone rule can be proposed only as an explicitly different, independently justified translation until
the actual primary formula/series definitions are read. Do not advertise it as faithful replication or
infer a notional dollar flow from returns alone. Actual holdings, hedge fractions, contributions/withdrawals
and cross-currency netting remain unobserved.

## Conservative calendar restriction: what it solves and what it does not

Possible pre-data restriction for root to assess: use only months whose FINAL WEEKDAY is known in advance
to be an ordinary UK AND US financial-centre business day. Skip the whole month otherwise. Do not move
to an earlier UK/US date after seeing prices. Freeze exact holiday authorities, observed holidays and
exceptional closures, and convert Europe/London16:00to America/Chicago separately for every date/DST era.

This would exclude the one-centre-open situation for which the saved current WMR methodology describes
month-end discretion. It can narrow the required service-policy question to ordinary both-open dates.
It is a restricted conditional sample, **not** a reconstruction of the full historical fixing calendar or
the paper's last-trading-day sample. It also cannot establish ordinary service continuity by itself:

- A current methodology's standard timetable is not an archived2018policy/version or a record that every
  chosen historical fixing was actually published without exceptional delay/suspension.
- UK/US bank holidays and exchange trading holidays are not interchangeable financial-centre definitions.
- The2013paper establishes the earlier16:00benchmark institution, not each later service date; the widening
  of the fixing calculation window in2015 also separates eras from the original sample.
- A verified ordinary-service policy covering the research period, plus known exceptions or benchmark
  observations establishing the selected dates, is still needed under RESEARCH_CONTROLS information clocks.

If new primary policy evidence supports that narrow both-open domain, the calendar may cease to be a
global blocker; there is no reason to require observations for excluded one-centre months. Until then,
state historical policy/receipt uncertainty instead of declaring the restriction a proof of service.

## Equity inputs and information clock needed before TEST

1. Read and preserve primary text for the exact country/index universe, relative-return equation,
   weighting and currency convention; distinguish statistical replication from a simpler bilateral rule.
2. Admit actual matching US/Eurozone (and any required other-country) equity series with instrument identity,
   adjusted/unadjusted/total-return definition, timezone and closing/publication clock, revision provenance,
   coverage and warm-up. A GitHub filename or an ETF label alone does not verify these.
3. Freeze a lag using only fully published closes before decision_time. The paper's next-to-last-day
   convention must account for local holidays and different market closes; no month-end day's future close.
   An extra lag can be conservative, but changes the protocol and must be registered before returns.
4. Preserve the available_at≤decision_time bridge for every equity input and benchmark date; retrospective
   adjusted prices or corrected daily histories are not automatically the values known at the time.
5. State which contract is actually traded.6E and M6E have different point values/ticks and cost/liquidity
   assumptions. Do not divide6E costs by ten, borrow MNQ fees without evidence, or assume standard-contract
   observations verify native micro fills. Freeze per-fill cost and a stress before the gross screen.

Month-end-only still offers at most60design dates before the conservative exclusions and data losses.
The task prefers≥100but that is not permission to expand to extra days or manufacture independent
observations. A power/cost calculation using explicit assumptions must justify the small-sample study;
full2018–26 promotion, positive design/previously-seen validation, both identical-exit placebos and current
BASE/ADD/REPLACE/EMPTY book gates would remain mandatory. No design-only or selected gross statistic counts.

## Discovery provenance and decision

New GitHub search excerpts identify secondary paths such as
`chris-cheshire/project-midas-mk7` at`f9e756c...` (`month_end_equity.py`, mechanism-date/literature notes),
and `dolmikthepro-creator/TimeLab` at`d0717c1...` (behavioral-source notes and an equity-hedge study).
Those secondary texts propose US-only, US-minus-Japan or pairwise proxies. They are discovery leads,
not a primary exact-country/normalization source and not admissible evidence of current net returns.
The TimeLab recursive tree inventory contained no relevant archived primary PDF/text. No price file or
return report was fetched. Broad fuzzy search results that did not identify a relevant primary source
were not followed further.

**NEEDS DATA / primary specification and calendar evidence.** Root may continue searching for NEW actual
equity inputs and policy documents. Do not rerun the completed post-fix reversal, quietly substitute a
US-only proxy, count this source note as H03, or pause the hunt because this input gate remains unresolved.
Only a credible later eight-question TEST sheet may lead to a committed at-most-five-configuration plan.
