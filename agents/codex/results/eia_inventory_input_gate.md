# CL inventory components: NEEDS DATA; source intake only

Summary: Acquired and audited a new EIA fundamentals input; no strategy returns were calculated.
The design calendar has 261 editions on 260 dates; 156 component triples pass source/text checks.
105 editions remain excluded; historical exception clocks, revisions and native execution inputs need review.
Program remains 60 evaluations/58 unique rules. No design-pass or t4/4.5/5/6 milestone; continue research.

Plan: agents/codex/plans/eia_inventory_input_gate.md, source-intake commit5723c95. This is not an economic preregistration.
Scripts: analysis/codex_eia_inventory_input_gate.py and analysis/codex_eia_inventory_input_gate_report.py.
Outputs: analysis/outputs/codex_eia_inventory_input_gate/. New economic/return trials:0.

## New input and what was actually done

Official EIA archived Highlights contain weekly commercial crude inventories excluding SPR, total motor
gasoline and distillate fuel changes, all in million barrels. Those components could distinguish total-stock
tightening from crude transferred into refined products. The older CL tests used calendars, price reactions
and sweep patterns. No claim of a compulsory order, consensus surprise, slow pricing or profitable trade
has been established. No entry/exit/threshold family has been selected from returns.

The calendar was reconstructed from the official archive's release-date and data-ending columns, not from
a Wednesday shortcut. Every week ending 2017-12-29–2022-12-23 appears once.
There are223Wednesday,33Thursday and5Friday editions. June29,2022 has two distinct editions, including the
delayed June17 data. A date alone is not a unique key. Calendar dates do not prove exact intraday availability.

The source collector followed actual issue/Highlights links through the connected web app. Converted source
blocks, canonical URLs, captureUTC and explicit unknowns are retained. Original PDF bytes were not downloaded;
the stored SHA256 values identify converted-source JSON, not raw PDF bytes or first-publication files.
Concurrent web reference resolution initially returned some wrong editions. Those failed attempts remain in
acquired/ and verified_sources/ with their audits; the ingestion code ignores both directories. The admitted
panel is rebuilt only from serial_sources/ after independent identity checks. No wrong source is backfilled
from a later edition, current time series, sample value or price move.

## Source identity, parsing and complete coverage audit

Before extracting values, the script checks calendar sourcekey/release/week identifiers, the actual converted
document header URLs, exact same-issue Highlights path, one-page PDF metadata and first PDF week-ending.
The delayed June2022 edition has its own source path. A malformed2019-01-09HTML week header is flagged;
PDF/index agreement remains mandatory. Missing, mismatched and ambiguous sources have explicit audit rows.

The parser uses signed weekly change sentences, with exact inventory subjects, million-barrel units and
last-week/previous-week scope. It rejects annual wording, missing/duplicate amounts and ambiguous unchanged
language. It does not subtract rounded stock levels: the2022-12-29crude change is+0.7, even though rounded
levels419.0−418.2give+0.8. Five actual saved sample responses across2018–22 reconcile numerically. Synthetic
tests include units, weekly scope, wrong URLs/weeks, duplicate editions and distinguishing ordinary5,403data
from an actualHTTP403 error.

```json
{
  "stage": "source_intake_only",
  "strategy_return_trials": 0,
  "expected_editions": 261,
  "serial_source_files_present": 218,
  "identities_verified": 169,
  "complete_triples": 156,
  "all_expected_identities_verified": false,
  "complete_component_panel": false,
  "missing_source_keys": [
    "2022-03-09__2022-03-04",
    "2022-03-16__2022-03-11",
    "2022-03-23__2022-03-18",
    "2022-03-30__2022-03-25",
    "2022-04-06__2022-04-01",
    "2022-04-13__2022-04-08",
    "2022-04-20__2022-04-15",
    "2022-04-27__2022-04-22",
    "2022-05-04__2022-04-29",
    "2022-05-11__2022-05-06",
    "2022-05-18__2022-05-13",
    "2022-05-25__2022-05-20",
    "2022-06-02__2022-05-27",
    "2022-06-08__2022-06-03",
    "2022-06-15__2022-06-10",
    "2022-06-29__2022-06-17",
    "2022-06-29__2022-06-24",
    "2022-07-07__2022-07-01",
    "2022-07-13__2022-07-08",
    "2022-07-20__2022-07-15",
    "2022-07-27__2022-07-22",
    "2022-08-03__2022-07-29",
    "2022-08-10__2022-08-05",
    "2022-08-17__2022-08-12",
    "2022-08-24__2022-08-19",
    "2022-08-31__2022-08-26",
    "2022-09-08__2022-09-02",
    "2022-09-14__2022-09-09",
    "2022-09-21__2022-09-16",
    "2022-09-28__2022-09-23",
    "2022-10-05__2022-09-30",
    "2022-10-13__2022-10-07",
    "2022-10-19__2022-10-14",
    "2022-10-26__2022-10-21",
    "2022-11-02__2022-10-28",
    "2022-11-09__2022-11-04",
    "2022-11-16__2022-11-11",
    "2022-11-23__2022-11-18",
    "2022-11-30__2022-11-25",
    "2022-12-07__2022-12-02",
    "2022-12-14__2022-12-09",
    "2022-12-21__2022-12-16",
    "2022-12-29__2022-12-23"
  ],
  "excluded_source_keys": [
    "2018-06-27__2018-06-22",
    "2018-12-28__2018-12-21",
    "2019-01-04__2018-12-28",
    "2019-04-10__2019-04-05",
    "2019-12-11__2019-12-06",
    "2020-02-20__2020-02-14",
    "2020-02-26__2020-02-21",
    "2020-03-04__2020-02-28",
    "2020-03-11__2020-03-06",
    "2020-03-18__2020-03-13",
    "2020-04-08__2020-04-03",
    "2020-05-06__2020-05-01",
    "2020-06-24__2020-06-19",
    "2020-07-15__2020-07-10",
    "2020-08-05__2020-07-31",
    "2020-10-15__2020-10-09",
    "2021-02-03__2021-01-29",
    "2021-02-24__2021-02-19",
    "2021-05-05__2021-04-30",
    "2021-05-12__2021-05-07",
    "2021-05-19__2021-05-14",
    "2021-05-26__2021-05-21",
    "2021-06-03__2021-05-28",
    "2021-06-09__2021-06-04",
    "2021-06-16__2021-06-11",
    "2021-06-23__2021-06-18",
    "2021-06-30__2021-06-25",
    "2021-07-08__2021-07-02",
    "2021-07-14__2021-07-09",
    "2021-07-21__2021-07-16",
    "2021-07-28__2021-07-23",
    "2021-08-04__2021-07-30",
    "2021-08-11__2021-08-06",
    "2021-08-18__2021-08-13",
    "2021-08-25__2021-08-20",
    "2021-09-01__2021-08-27",
    "2021-09-09__2021-09-03",
    "2021-09-15__2021-09-10",
    "2021-09-22__2021-09-17",
    "2021-09-29__2021-09-24",
    "2021-10-06__2021-10-01",
    "2021-10-14__2021-10-08",
    "2021-10-20__2021-10-15",
    "2021-10-27__2021-10-22",
    "2021-11-03__2021-10-29",
    "2021-11-10__2021-11-05",
    "2021-11-17__2021-11-12",
    "2021-11-24__2021-11-19",
    "2021-12-01__2021-11-26",
    "2021-12-08__2021-12-03",
    "2021-12-15__2021-12-10",
    "2021-12-22__2021-12-17",
    "2021-12-29__2021-12-24",
    "2022-01-05__2021-12-31",
    "2022-01-12__2022-01-07",
    "2022-01-20__2022-01-14",
    "2022-01-26__2022-01-21",
    "2022-02-02__2022-01-28",
    "2022-02-09__2022-02-04",
    "2022-02-16__2022-02-11",
    "2022-02-24__2022-02-18",
    "2022-03-02__2022-02-25",
    "2022-03-09__2022-03-04",
    "2022-03-16__2022-03-11",
    "2022-03-23__2022-03-18",
    "2022-03-30__2022-03-25",
    "2022-04-06__2022-04-01",
    "2022-04-13__2022-04-08",
    "2022-04-20__2022-04-15",
    "2022-04-27__2022-04-22",
    "2022-05-04__2022-04-29",
    "2022-05-11__2022-05-06",
    "2022-05-18__2022-05-13",
    "2022-05-25__2022-05-20",
    "2022-06-02__2022-05-27",
    "2022-06-08__2022-06-03",
    "2022-06-15__2022-06-10",
    "2022-06-29__2022-06-17",
    "2022-06-29__2022-06-24",
    "2022-07-07__2022-07-01",
    "2022-07-13__2022-07-08",
    "2022-07-20__2022-07-15",
    "2022-07-27__2022-07-22",
    "2022-08-03__2022-07-29",
    "2022-08-10__2022-08-05",
    "2022-08-17__2022-08-12",
    "2022-08-24__2022-08-19",
    "2022-08-31__2022-08-26",
    "2022-09-08__2022-09-02",
    "2022-09-14__2022-09-09",
    "2022-09-21__2022-09-16",
    "2022-09-28__2022-09-23",
    "2022-10-05__2022-09-30",
    "2022-10-13__2022-10-07",
    "2022-10-19__2022-10-14",
    "2022-10-26__2022-10-21",
    "2022-11-02__2022-10-28",
    "2022-11-09__2022-11-04",
    "2022-11-16__2022-11-11",
    "2022-11-23__2022-11-18",
    "2022-11-30__2022-11-25",
    "2022-12-07__2022-12-02",
    "2022-12-14__2022-12-09",
    "2022-12-21__2022-12-16",
    "2022-12-29__2022-12-23"
  ],
  "exclusion_reasons": {
    "missing_document_text": 48,
    "missing_serial_source": 43,
    "published_weekly_change_parse_failure": 13,
    "invalid_document_header": 1
  },
  "retained_by_release_year": {
    "2018": 50,
    "2019": 49,
    "2020": 42,
    "2021": 15
  },
  "html_header_warning_keys": [
    "2019-01-09__2019-01-04"
  ],
  "extra_serial_source_filenames": [],
  "ignored_diagnostic_directories": [
    "acquired",
    "verified_sources"
  ],
  "no_backfill_from_samples_or_diagnostic_attempts": true,
  "hash_basis": "SHA256 of each saved serial-source JSON file, containing exact converted web text; NOT raw PDF bytes.",
  "immutable_original_vintages_verified": false,
  "actual_release_clocks_verified": false,
  "economic_preregistration_authorized": false,
  "known_clock_revision_limits": [
    "Normal Highlights publication policy10:30Eastern is not historical client receipt evidence.",
    "Holiday/disruption clocks and multiple-edition dates require independent handling before strategy tests.",
    "Archived dated files may contain later corrections; original first-publication bytes are not established.",
    "2018June27updated production statistic does not itself prove an inventory-field correction.",
    "2026August26summary sign correction demonstrates mutability; it is source-review evidence, not a design observation."
  ],
  "five_sample_parity": {
    "2018-01-04": {
      "week_ending": "2017-12-29",
      "crude_ex_spr_change_mb": -7.4,
      "gasoline_change_mb": 4.8,
      "distillate_change_mb": 8.9
    },
    "2019-01-09": {
      "week_ending": "2019-01-04",
      "crude_ex_spr_change_mb": -1.7,
      "gasoline_change_mb": 8.1,
      "distillate_change_mb": 10.6
    },
    "2020-07-08": {
      "week_ending": "2020-07-03",
      "crude_ex_spr_change_mb": 5.7,
      "gasoline_change_mb": -4.8,
      "distillate_change_mb": 3.1
    },
    "2021-04-07": {
      "week_ending": "2021-04-02",
      "crude_ex_spr_change_mb": -3.5,
      "gasoline_change_mb": 4.0,
      "distillate_change_mb": 1.5
    },
    "2022-12-29": {
      "week_ending": "2022-12-23",
      "crude_ex_spr_change_mb": 0.7,
      "gasoline_change_mb": -3.1,
      "distillate_change_mb": 0.3
    }
  }
}
```

All261calendar rows—including failures—are retained in design_component_audit.csv. The usable observations
and per-source hashes are in design_components.csv. design_input_frequency.csv contains fundamental-only
counts, not trade counts or P&L; no rule is selected from these counts. A keyword scan of observed issue
notices is retained in design_issue_notice_scan.csv; it is not proof that every correction is identified.

## Remaining gates before any strategy return test

The original2018/2022AppendixB describes normal Highlights publication at10:30Eastern, earlier than the
full report. Actual historical receipt, holiday/disruption clocks and field-specific corrections require their
own handling. The2018June27issue documents an updated production statistic; that alone does not establish
an inventory-field correction. A2026notice records an inventory-summary sign corrected after initial release.
That2026example is source-review evidence, not a design observation. Archived dated files are not established
as immutable first vintages. No retrospective timestamp or corrected value has been called an observed live input.

CL/MCL execution also needs explicit instrument parameters. Shared grid._walk is reusable, but NQ-specific
grid.execute/F.replay hardcode the wrong point value/costs/target-through. Do not use the old CL-net-divided-
by-ten bench as native-MCL evidence. Fees, listing history, native price parity, the energy session calendar,
continuous-contract roll treatment and missing/negative-price coverage remain scoped preflight items.
See agents/codex/research/eia_cl_execution_preflight.md. No proxy-derived account improvement is claimed.

## Scoped source-access blocker and prepared next action

The connected web tool explicitly stopped further calls after its capacity limit. The direct-fetch preflight
confirms that www.eia.gov is absent from this executor's restricted host policy. No direct network request,
proxy change, policy bypass, broker setting or API configuration change was attempted. Existing workspace
and raw futures data remain available; this blocker concerns the new EIA input acquisition.

analysis/codex_eia_inventory_fetch.py is prepared for bounded official-source downloads after reviewed host
access. Its --check-access run made zero network requests and found pdftotext available. It preserves current
PDF bytes/HTML/text and hashes, refuses unapproved hosts, and stops on401/403/429; native captures would
still need identity/parity/vintage review before admission. It is not a trading implementation.

Required action to finish this acquisition: allow www.eia.gov through the managed cloud environment's reviewed
network configuration. The runtime skill says: “Configuration changes require the environment configuration
workflow and its user review.” No such setting was changed here. access_gate.json retains the actual tool-stop
message and source-file hash. Do not repeatedly alert while this scoped blocker is unchanged.

Resume the committed source intake first: resolve excluded editions, audit clock/revision notices and source
parity, then decide whether the evidence merits TEST. Only then commit an economic plan with<=5configurations
before2018–22returns. No2023+strategy validation, trade ledgers, t statistic, promotion check, account bench or
PowerLanguage was produced here. Input work does not complete t6 or create an intermediate t milestone.
The separate source-access blocker requires the action above; the research continuation remains enabled.
Last completed strategy-return experiment remains the rejected
Correlation Risk Budget study; its execution marker and all prior performance/milestone history are preserved.
Claude review path: agents/codex/results/eia_inventory_input_gate.md.
