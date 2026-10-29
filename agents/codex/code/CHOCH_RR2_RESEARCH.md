# CHoCH 1:2 research runner

Implementation: `analysis/codex_choch_rr2.py`.
Specification: `agents/codex/plans/choch_rr2_20261028.md`.
Results: `agents/codex/results/choch_rr2_20261028.md`.

Four fixed variants: 4h R1/R2 at 2R, and hourly intraday R1/R2 at 2R. Eight ledgers include matched signal-close benchmarks. Shared original CHoCH signals, minute execution, metrics and corrected data helpers are reused, not copied into a separate live strategy. There is no broker code or MultiCharts deployment.

From the repository root, `python -B analysis/codex_choch_rr2.py` runs synthetic mechanics only. The recorded financial execution used `python -B analysis/codex_choch_rr2.py --design` after committing the plan and passing checks. The runner refuses to overwrite an existing design result directory; preserve saved evidence before any separately named reproduction. It expects the already staged reconciled 2017–22 sources under the ignored local input directory from the preceding corrected-source task. Raw uploads are not published; their hashes and the earlier reconstruction code identify the owned inputs.

No variant passed the frozen economic gate. Do not extend this runner to 2023+ or tune it silently. Any approved follow-up should be registered separately with its own output path and cumulative counts. The original RR1 failure, data limits and source/engineering retries remain in the repository.
