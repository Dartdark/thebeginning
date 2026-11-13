# Codex data, 2026-11-09 (copied from origin/codex/work on 2026-11-10)
- `investing_us_macro_consensus.json`: Investing.com economic-calendar history for 14 US macro series (FRED IDs), with actual /
  forecast (consensus) / previous and the release time (UTC). Source: Codex `agents/codex/inputs/eval_focus_20261109/macro_intake/`
  (FRED US Macro Core Data snapshot). Codex marked it NOT research-admitted (no signal / return work done on it yet).
- `macro_events_2018plus.csv`: the same flattened (series, time UTC, actual, forecast, previous), releases from 2018; last real
  releases April / May 2026 (rows after that have no actual).
- `BOIL.csv`, `KOLD.csv`: ProShares 2x natural-gas funds (NAV / assets), as the other LETF files; `buybacks_security_details.csv`:
  Treasury buyback security details. From Codex `new_data_primary_local_20261108/normalized/`.
