# Forward-guidance revision: source-input gate only

This plan freezes a metadata census before examining any new strategy returns. It is not an economic
preregistration. There are zero economic configurations, no selected signal timeframe and no executable
trading rule. Only 1-, 5-, 15- or 30-minute signal frames could qualify in a later, separate plan.

## Mechanism and novelty boundary

A genuinely different earnings input could be an issuer's revision to its own previously published
forward guidance for the SAME future fiscal horizon. Investors may update prospective cash-flow beliefs;
no compulsory order, predictable index-futures allocation or delayed response is established. This is
not realized EPS surprise versus analyst estimates. The existing megacap earnings family already uses
that surprise direction. Changing the ticker, magnitude or clock would not create a distinct family.

Before an economic TEST, require original guidance documents and their publication/receipt histories,
prior and new ranges, comparable horizons and units, share-count/currency/accounting changes,
withdrawals and simultaneous releases. Require as-of index membership/weights and justified transmission
into the traded contract. A later-vintage earnings table or a pre/post-market label cannot substitute.

## Frozen no-return census

Script: analysis/codex_forward_guidance_input_gate.py.
Inputs: data/ndx_megacap_earnings.csv and data/dow_heavy_earnings.csv, plus their existing definition scripts
analysis/megacap_earnings_nq_test.py and analysis/ym_dow_events_test.py for source bindings only.
Read CSV headers and ticker/fiscalDateEnding/reportedDate/reportTime metadata. Do not use realized EPS,
analyst estimates, surprises, raw futures prices, strategy ledgers or account outcomes. Do not fetch data.

1. Retain exact schemas, source hashes and presence/absence of explicitly named required fields. A missing
   literal field is a schema finding, not proof that no external source could supply the concept.
2. Inventory 2018-22 report dates by issuer/year and pre/post-market/other labels. Retain invalid identity
   dates, fiscal horizons after report dates, unknown labels and repeated issuer/fiscal-period keys.
3. Save all selected metadata rows and duplicate groups. Date multiplicity is counted without merging
   issuers into a signal. No next-session entry date, direction, event exclusion or return is computed.
4. Count distinct report dates and simultaneous issuer reports for a design-era opportunity ceiling.
   These are reported-date candidates, not observed guidance changes, eligible trade sessions, independent
   events or a measured effective sample size. Do not promote a hypothetical power calculation.
5. Stop at NEEDS DATA if original comparable guidance, before-entry clocks, historical weights or contract
   transmission are absent. Missing inputs authorize no price-only, EPS-derived or modern-weight proxy.

Output: analysis/outputs/codex_forward_guidance_input_gate/. Retain every census exception; no repair,
forward remapping, holiday inference or future backfill. The script refuses an already completed intake
with the same bound inputs. Preserve results when new source material arrives instead of overwriting them.

## Later gates and costs

The source gate cannot choose a threshold, entry time, holding period or price direction from past outcomes.
An eligible evidence sheet would precede a separate committed <=5-configuration economic preregistration,
2018-22 cheap design first, then committed selection before one previously seen 2023+ validation.

Existing NQ research assumptions are $7.25 round trip plus $5 per market/stop fill; MNQ $1.24 plus $0.50
per such fill, separately calculated. These are assumptions, not fresh broker quotes or verified native
MNQ fills. Two-market-fill costs are $17.25/$2.24, respectively. No expected gross edge or ability to pay
these costs is established. Native micro listing, parity, fees and complete paths remain later gates.

No accounts, PowerLanguage or deployment follow from this census. It adds zero return trials and no
milestone alert. Prior failures and cumulative 65 evaluations/63 unique economic rules are unchanged;
pending MBS/EIA source work is preserved. A failed data gate does not pause the continuing research program.
