# Local official-primary acquisition, 2026-11-08

See [the acquisition report](../../results/new_data_local_20261108.md).

`transport/` contains gzip copies of original response bytes and acquisition receipts, including the initial
sandbox DNS failures, successful normal-network downloads, linked documents and NYFed partition queries.
`transport_manifest.json` and `supplement_manifest.json` preserve both original/compressed byte counts and
SHA256s. Decompress for exact originals; no line-ending or numeric rewriting was applied to raw payloads.

`normalized/` is separate derived research data, with unknown available_at left blank. Fund shares use exact
Decimal source-thousands ×1000 conversion only. `reconciliation/` retains all overlapping numeric differences.
`qa_summary.json`, `supplement_qa.json`, `document_clock_qa.json`, `historical_clock_flags.json` and
`dispositions.json` retain coverage, failures/limits and source-clock boundaries.

BOIL remains quarantined across the entire dataset: original sponsor history still contains82zero-share rows
and1,178identity failures. Do not infer shares with AUM/NAV. Other funds/indices pass source reconciliation,
not historical-publication or trading admission. Current fund holdings/prospectuses and the future tentative
buyback calendar are snapshots, not2018–22weights or outcomes. Historic buyback programs/tests remain distinct
from the regular modern program. NYFed results are post-operation information.

Reproduction: run the two fetch-primary commands in the local task into fresh `_02` directories after preserving
the initial `_01` DNS-failure receipts; run `analysis/codex_new_data_local_20261108.py` modes `documents`, `audit`,
`supplement`, `prospectuses`, `finalize`, `clocks`, `package-supplement` in that order. Destinations must be new;
do not rerun against this existing package. Current public histories may change on future acquisition.
No backtest, trial reservation, strategy/live/VPS/broker setting or credential access was performed.
