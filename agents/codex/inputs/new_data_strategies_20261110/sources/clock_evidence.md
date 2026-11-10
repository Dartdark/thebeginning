# Publication admission, reviewed November9,2026 Pacific

Direct container requests to NYFed/FRED failed (receipts retained); the connected web reader opened primary sources.
No account, subscription, payment or external contact was used.

- NYFed, [reference-rate policy](https://www.newyorkfed.org/markets/reference-rates/additional-information-about-reference-rates):
  EFFR/OBFR are normally released9am Eastern on the following business day; SOFR/TGCR/BGCR around8am.
  Core rate revisions occur only on initial publication day, normally2:30pm. Later quarterly summary-statistic
  updates can differ. Admit **percentRate only**, never retrospective percentiles/volumes as contemporaneous features.
- ARRC, [February2021 SOFR guide, p.5](https://resources.newyorkfed.org/medialibrary/Microsites/arrc/files/2021/users-guide-to-sofr2021-update.pdf):
  the effective-date label is the transaction date, not publication; the guide corroborates next-business-day
  publication and same-day revision. Its2019example explicitly discusses waiting until3pm to reference the rate.
  This is a historical policy basis, not a recovered feed-receipt log.
- Cboe, [term-index methodology, pp.10–11](https://cdn.cboe.com/resources/indices/governance/Volatility_Index_Methodology_Selected_SPX_Target_Expected_Volatility_Term_Indices.pdf):
  VIX9D is a9-day SPX option-implied-volatility index disseminated during cash-market hours; launchOctober2013.
  Design2018–22 is after launch. Current methodology is not treated as a reconstructed historical option/Greek series.
- Cboe, [EOD summary delivery](https://datashop.cboe.com/main-channel-end-of-day-summary):
  distinguishes closing observation time from next-trading-day distribution. We do not buy/use that product;
  for the owned official daily histories use **two completed NQ sessions earlier**, avoiding reliance on a
  same-evening website update. Missing exact source dates remain unknown; no forward/back filling.

Rates: model each effective date as available at3pm Eastern on its next observed reference-rate business date,
then use only after that time. This policy-derived availability is an explicit conservative model, not measured latency.
Use both rate types from the same effective date, no stale carry beyond7calendar days, no invented2017SOFR.
Cboe: source/primary-value reconciliation was already completed; historical restatements and exact individual
row receipts remain a limitation. These close-only data cannot reveal intraday volatility or signed dealer inventory.
No primary histories are rewritten and original available_at fields remain blank; derived clocks live in outputs.
