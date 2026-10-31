# Pre-fix month-end equity hedging: NEEDS DATA

This is a source/input feasibility screen for a possible later distinct hypothesis. It is not a preregistration,
return test, result, user-action blocker or milestone. No new returns were calculated. Continue other research
while resolving these inputs; do not silently turn this into the existing post-fix reversal strategy.

## Documented mechanism and limits

[Melvin and Prins, Equity hedging and exchange rates at the London 4pm Fix](https://www.ecb.europa.eu/events/pdf/conferences/131216/Third_FX_Workshop_MELVIN_PRINS_Equity%20hedging%20and%20exchange%20rates%20Nov%202013.pdf),
pp. 4–5 and 10–11, describes month-end portfolio hedgers placing currency orders at least an hour before
the London fix. Its equity signal uses country outperformance relative to other markets, measured through
the next-to-last day. Currency returns are cross-sectionally demeaned. This documents an actor and clock;
it does not establish a currently profitable net futures strategy.

A US-only positive-ES-month -> long-6E rule omits the relative equity and other-country exposures. It would
be a new incomplete proxy, not a replication of the paper. No verified Eurozone/global equity series was
located locally. data/SPY_daily.csv also needs provenance: its initial 2017-01-03 close is 2252.50, inconsistent
with an ordinary SPY ETF quote. The generic exporter permits arbitrary chart and filename choices, so the
filename alone is insufficient evidence of the instrument. No strategy should use it as SPY without resolution.

## Calendar, executable contracts and power

[WMR methodology](https://www.lseg.com/content/dam/ftse-russell/en_us/documents/ground-rules/wmr-fx-methodology.pdf),
sections 3.3 and 4.4.2, describes the publication service and the 15:57:30–16:02:30 fixing window. Month-end
publication may involve discretion when only one relevant financial centre is open. NYSE weekdays or UK/US
business days alone therefore do not establish the historical fix calendar. The official
[service alterations](https://www.lseg.com/content/dam/ftse-russell/en_us/documents/methodology/wmr-service-alterations.pdf)
document covers 2025–2030; earlier historical service dates remain to verify. Use Europe/London-to-
America/Chicago timezone conversion, including US/UK DST mismatch weeks.

[CME product specifications](https://www.cmegroup.com/markets/fx/fx-product-guide) give 6E as 125,000 EUR,
0.00005 minimum tick = $6.25, and M6E as 12,500 EUR, 0.0001 tick = $1.25. One tick each way therefore costs
$12.50/$2.50 before fees. Native fees, spread/liquidity and exact contract alignment need their own evidence.
The NQ adapter's point value, tick size, costs and one-point target-through cannot be reused unchanged;
micro FX costs cannot be obtained by dividing standard-contract costs by ten.

Month-end-only supplies at most 60 design events in 2018–22. Expanding to three days merely to exceed
100 observations lacks the documented one-hour month-end flow clock and would need separate evidence.
The existing agents/codex/plans/fx_fix_reversal.md instead fades 6E's own move after the fix. A properly
specified lagged-relative-equity pre-fix signal would differ, while sharing benchmark ancestry.

## Decision

NEEDS DATA for faithful relative-equity testing. Obtain verified free historical equity inputs and an actual
fix service calendar before writing any TEST evidence sheet and committed <=5-model preregistration.
Alternatively, a US-only proxy must be explicitly justified and labelled as a different, weaker hypothesis.
Do not count this feasibility note as a tested configuration or a t4.5/t5/t6 event. No purchases, external
messages, accounts, source settings or live configuration changes were made.
