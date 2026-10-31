# C1 SPXW signed-book intake specification — unsent research draft

Purpose: evaluate the expiry hedge-removal hypothesis in SSRN7330098. This document was not sent to Cboe or any author.
No account, licence, trial, subscription, order or payment was opened.

## Smallest initial intake

Confirm eligibility and the current access procedure for the **fixed July1–December31 2022** free sample of C1
one-minute, ten-minute and EOD Open-Close data listed in the October1 2026 fee schedule, printed p.12.
It is offered to TPHs and non-TPHs who have not previously subscribed to the respective dataset or received its sample.
Eligibility, account/licence requirements, delivery and entitlement must be confirmed by the user/vendor; no access is guaranteed.
The published offer does not make the underlying files anonymously downloadable or grant redistribution rights.

Before any broader history, request one complete PM-expiring SPXW series with its actual listing/inception date,
all initial/prior inventory and full sessions through expiry, plus corresponding option and SPX quotes/deltas.
A six-month calendar slice alone may omit the starting inventory of series already trading at its beginning.

## Required raw fields and clocks

- Native option identifier, underlying/root, expiry date/time, AM/PM settlement, put/call, strike and100 multiplier.
- C1 participant market-maker buy and sell **contract volumes**, including the appropriate open/close components;
  customer-only flow, total OI, trade counts and an assumed dealer sign are insufficient.
- Daily EOD MM net flows from every selected series' inception, and the most recently **received** intraday cumulative
  MM buy/sell snapshot. Do not add cumulative snapshots repeatedly. A missing initial book cannot be zero-filled.
- Exchange event/end timestamps, snapshot-label convention, original publication/delivery timestamps, file receipt times,
  processing lag, sequence/version identifiers, and rules for corrections, breaks, cancellations and final restatements.
- RTH/GTH/Curb and holiday/early-close coverage by date. Current product history says C1 GTH starts2023-12-11;
  establish how the original2020–23 sample's overnight trades can be reconciled. Do not impose later coverage retroactively.
- Matching option bid/ask/IV/delta and underlying inputs with their own event/publication/receipt clocks.
  The intraday Open-Close product does not contain all EOD OHLC/OI fields, nor does it supply the required complete Greek surface.

The regulator's one-minute example is a15:30–15:31 interval delivered about2–5minutes after interval end;
this is not permission to enter at15:30 with its completed information. The product was introduced in2025 even
though archived files extend to2019; establish historical subscriber availability separately from a file's trade timestamp.
Any ten-minute alternative is a different timing protocol requiring its own evidence and preregistration.

## Required source and licence answers

Confirm original-as-delivered versus later corrected records, full series-inception coverage, minimum historical date,
which data was actually published at the time, and any missing symbols/sessions. A T+1 trade-detail record can audit
inventory but cannot become a same-day predictor. Confirm internal use, cloud processing and approved parties before
loading licensed raw records. Keep any licensed raw files in the git-ignored `licensed_raw/` folder; commit only permitted
manifests/hashes, code and aggregate reports. The current dataset page prohibits external raw redistribution.

## Public price evidence, not an order or binding quote

October1 2026 fee schedule, printed p.12, lists one-minute subscription12,000USD/month (144,000USD/year),
historical last-four-years4,000USD/month and five-or-more-years2,500USD/month. The specific free sample is2022H2.
The adjacent p.13 lists up to one month of TBT trial for eligible first-time users. Academic rates are not assumed
available for this profit-seeking project. Applicability, boundary years, proration, symbols, taxes and licence costs
require a vendor quote; none was requested. No money was spent.
