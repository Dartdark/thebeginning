# Transfer the acquired Bridge research data to the cloud checkout

Summary: The acquisition report and hashes reached GitHub; its five actual CSVs remain in ignored Windows scratch_data.
Run this task on the home-PC Codex session that has those exports. No new data download or backtest is needed.
Package only the audited2018–22 exports, preserve originals, then publish the new research directory on codex/work.

Read AGENTS.md and BUILDER_BRIEF.md. Inspect status and reuse codex/work; never reset, force-push, discard work,
change another checkout's branch, or push claude/* or antigravity/*. Pull/merge origin/codex/work normally.

Confirmed source directory from the acquisition report:
`C:\CodexRepo\scratch_data\codex_bridge_20261108_01`

Use the existing configured Python (the acquisition used Python3.7; the packager uses stdlib only):

```text
python analysis/codex_bridge_transfer_pack.py
```

An alternate --source is allowed only if it contains the same five audited exports. The script verifies all original
byte counts/SHA256s before creating a destination, refuses an existing destination, gzip-compresses without
changing CSV contents, verifies decompressed hashes and rechecks originals. No overwriting or relocation of inputs.

It creates exactly:
`agents/codex/inputs/bridge_native_2018_22_20261108/`
with five .csv.gz files plus transfer_manifest.json. Review the manifest and sizes. Stage only those six research
files (use git add -f for those explicit paths only if required), commit, fetch/merge the current codex/work and push
to origin codex/work. Preserve unrelated edits. Report the resulting commit to the user.

If a source hash differs or the directory already exists, stop and report it; don't rewrite the audit or replace
an old package. If the source isn't at that path, locate these five filenames in the home PC's known research
folders. Do not inspect credentials, API keys, broker configuration, live charts or the VPS. No external messages,
paid data, backtests, strategy settings, continuous-contract repairs or trading-plan changes.

The cloud session will verify the compressed/original hashes and source coverage independently after fetch.
Transport does not resolve roll/build provenance, missing sessions, correction clocks or historical receipt delay.
The source's UpVol/DownVol are documented aggressor categories, not native PowerLanguage tick-direction fields.
Don't reinterpret the new files as exact replacements for native FC/T up-tick inputs.
