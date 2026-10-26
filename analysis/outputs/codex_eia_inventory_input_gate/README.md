# EIA input gate: no strategy returns

Rebuild the audited calendar/component panel with:

`/workspace/venvs/thebeginning/bin/python -B analysis/codex_eia_inventory_input_gate.py`

Rebuild the report with `analysis/codex_eia_inventory_input_gate_report.py` (optional `--update-program`).

- `serial_sources/` is the only admitted source directory for this parser. Every row must pass independent
  calendar/URL/PDF/week-ending/weekly-prose checks; existence alone does not make it usable.
- `acquired/` and `verified_sources/` retain diagnostic attempts, including wrong-edition and failed tool
  responses from concurrent reference resolution. Do not ingest or backfill from them.
- `samples/` contains five separately verified source examples and publication/revision proof. Samples are
  parser checks, not backfill for missing panel editions.
- Hashes on converted JSON/text are not raw-PDF hashes or proof of immutable original vintages.
- All261calendar editions, including excluded/missing ones, appear in `design_component_audit.csv`.
- `access_gate.json` records the web capacity stop and the executor's missing EIA host access. No further
  web calls, direct denied-host requests, changed proxy or policy bypass followed the stop.
- `analysis/codex_eia_inventory_fetch.py --check-access` is an offline readiness check. Only after reviewed
  official-host access may its bounded downloader run. Future native captures remain quarantined until audited.

No CL price files, strategy forward returns, t statistics, account paths or economic configuration trials
were calculated in this source-intake phase. No design-pass or intermediate t milestone is established.
