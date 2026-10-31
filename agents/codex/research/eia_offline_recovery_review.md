# EIA source intake: offline representation review, 2026-10-26

This continues source-intake plan5723c95. It is not an economic preregistration or a strategy result.
No futures-price files, returns or new network requests were used. The EIA access blocker was already
reported; it has not changed and does not justify another notification.

## Preserved baseline and independent review

The baseline is commit02ca706:156 complete component triples from218 captured serial-source files and
261 expected editions. Copies of the original panel, all261audit rows, coverage and hashes are in
analysis/outputs/codex_eia_inventory_input_gate/offline_review_20261026/.

Two independent read-only reviewers inspected the actual saved converted issue/PDF text before these
repairs: one reviewed numeric representations and one reviewed the failed PDF identity. Their expected
triples and original serial-source SHA256 values are retained in expected_recoveries.json. Hashes identify
the unchanged converted-source JSON, not native PDF bytes or original publication vintages.

| Release / week ending | Crude excluding SPR | Gasoline | Distillate | Representation repaired |
|---|---:|---:|---:|---|
| 2019-12-11 / 2019-12-06 | +0.8 | +5.4 | +4.1 | Leading decimal `.8 million barrels` |
| 2020-02-20 / 2020-02-14 | +0.4 | -2.0 | -0.6 | Explicit400thousand barrels |
| 2020-02-26 / 2020-02-21 | +0.5 | -2.7 | -2.1 | Explicit500thousand barrels |
| 2020-03-04 / 2020-02-28 | +0.8 | -4.3 | -4.0 | Explicit800thousand barrels |
| 2020-03-18 / 2020-03-13 | +2.0 | -6.2 | -2.9 | Blank PDF metadata title |
| 2020-04-08 / 2020-04-03 | +15.2 | +10.5 | +0.476 | Explicit476thousand barrels |
| 2020-06-24 / 2020-06-19 | +1.4 | -1.7 | +0.249 | Explicit249,000barrels |
| 2020-07-15 / 2020-07-10 | -7.5 | -3.1 | -0.453 | Explicit453,000barrels |
| 2020-08-05 / 2020-07-31 | -7.4 | +0.419 | +1.6 | Explicit419,000barrels |

Values are million barrels. Quantity conversion divides explicit thousands by1,000 and explicit barrels
by1,000,000. Every admitted row retains the original amount/unit, factor, direction, weekly scope and
literal normalized source phrase. No stock-level subtraction or later-edition backfill is used.

The blank metadata-title exception requires the exact official same-issue URL, one-page metadata,
the internal official title atL0@P0 and matching first week-ending. An absent internal title still fails;
the audit retains a warning. The issue release date and archive week must independently match.

## Reproduced result and parser review

The rebuilt panel contains165triples with170 verified source identities. All156 original triples and all
218 captured file hashes/presence are unchanged. Exactly the nine independently reviewed keys are added.
The remaining96exclusions are43missing files,48missing document texts and5qualitative unchanged reports.
Those five remain excluded under the intake plan; neither “unchanged” nor “virtually unchanged” was filled
with zero. A partial fundamental panel is not an executable trading history.

A fresh review of the parser identified two synthetic ambiguity cases: trailing annual/per-day scope
and a contradictory second subject sentence that did not itself match the numeric grammar. The parser
now requires valid weekly-clause termination and one occurrence of each inventory subject before numeric
matching. Observed `and are ...` / `but are ...` stock-level commentary remains valid. Added engineering
checks reject both cases; the original five actual PDF samples and the complete baseline still reconcile.
This source/parser review is not the independent raw-spec strategy checker required before promotion.

Reproduce with the existing project Python:

```text
/workspace/venvs/thebeginning/bin/python -B analysis/codex_eia_inventory_input_gate.py
/workspace/venvs/thebeginning/bin/python -B analysis/codex_eia_inventory_input_gate.py --offline-review
/workspace/venvs/thebeginning/bin/python -B analysis/codex_eia_inventory_input_gate_report.py --update-program
```

## Unresolved source and execution gates

Normal10:30Eastern Highlights publication policy is not historical receipt or exception-clock evidence.
The delayed June17,2022 data would originally have appeared June23 and were published with June24data on
June29; the saved notice does not supply an intraday time. The2018June27correction concerns a production
percentage. The2026notice identifies “summary text,” not specifically the Highlights PDF; it does not prove
that these archived Highlights inventory fields were revised. Original-vintage and field-parity checks
remain open rather than being inferred from dated URLs or source hashes.

The existing reviewed-host-access requirement remains scoped to further EIA acquisition. Native CL/MCL
fees, listing/parity, session and roll treatment also remain unresolved. No economic rule, allowed signal
timeframe or entry clock has been frozen. Program counts remain60evaluations/58unique; completed returns,
all4/4.5/5/6milestones and the already delivered blocker snapshot are preserved. Continue source research
and screen distinct feasible mechanisms; no validation, account tests or PowerLanguage follows this repair.
