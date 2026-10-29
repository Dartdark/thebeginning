# Beginning Research Terminal

A local research app for Dartdark/thebeginning. Python 3.10+ standard library; no package installation,
broker connection, hosting account or API key required. Dark interface with nine working views.

## Open on your computer

Pull `codex/work` into a research checkout. On Windows, double-click **start_terminal.cmd** in this folder.
It uses the Python launcher (`py -3`) and opens your default browser. If you use a configured virtual environment,
set `THEBEGINNING_PYTHON` to its Python executable before launching. Python must already be installed.

Linux/macOS: `bash agents/codex/terminal/start_terminal.sh` from the repository. The script prefers the configured
`/workspace/venvs/thebeginning/bin/python` when present, otherwise `python3`.

Direct launch from the repository:

    /workspace/venvs/thebeginning/bin/python agents/codex/terminal/server.py

Then open http://127.0.0.1:8765 on the **same machine**. Use `--port 8766` if occupied. Stop with Ctrl+C.
The cloud executor's localhost is not your computer's localhost; the Windows launcher is the desktop handoff.

## What works

- Overview: actual report/evidence/preregistration/reference counts and recently saved files.
- Research library: full-text search, document-type and verdict filters, sorting, readable source documents.
- Strategy research: the evidence, plan and report catalog. Source labels do not certify independent verification.
- Results lab: existing CSV output viewer, row filtering and CSV export. Original names/units remain visible.
- Verification queue: reads the promising-strategy section of TODO.md, including negative follow-ups.
- Execution references: searchable, expandable entries from EXECUTION_REFERENCES.md.
- Paper inbox: local PDF upload/drop, SHA-256 deduplication, native PDF preview and optional pdftotext extraction.
- Research notes: create/save/delete durable user-authored notes with source links and four-question prompts.
- Research scout: public SSRN DOI metadata discovery, deduplication, relevance filters, access receipts and saved analyst dispositions.

Refresh reloads the working tree; it does not fetch GitHub. Pull remote changes outside the app, then refresh.
The source links point to codex/work. Document contents are escaped; PDF text is treated as untrusted source material.

## Persistence and limits

PDFs, extracted text and notes are stored under `agents/codex/runtime/terminal/`, ignored by Git. They survive
server restarts on that computer. Back up that folder to retain personal notes/imports. They are not synchronized
to another computer, committed, or uploaded by the app. No data is sent to a cloud analysis service.
The note store uses revision checks to reject stale saves from another tab.

The local **Discover papers** button queries Crossref metadata only; scores indicate relevance, never alpha.
It does not read papers, call a model or run returns. Importing a PDF also does not review or test it.
Crossref is incomplete and may be blocked by network policy; failed/skipped requests remain visible.
SSRN login/downloads remain in your browser; access controls are not bypassed. The Results lab reads saved runs.

## Daily autonomous research

The separate **SSRN research scout** app automation was created enabled on 2026-10-29 with daily recurrence.
Its identifier and creation-time status are recorded in `agents/codex/research/scout/config.json`.
App automation settings are authoritative; this terminal displays a saved configuration, not live scheduler status.
The task uses Codex's connected search/GitHub and an execution environment when available, independent of this local web server.
It discovers and deduplicates papers, reads obtainable full text, answers the four review questions, and retains execution lessons.
For an eligible strategy it can autonomously acquire owned/free data, preregister and run gated research tests.
Material source/data gaps stop dependent tests. An unavailable execution environment means source work only.
No new external service key is needed; this does not guarantee every future source or test is accessible.

The [operating contract](../research/scout/WORKFLOW.md) reserves a bounded first batch: 10 new hypotheses,
30 economic definitions including gross screens/controls, at most 1 new hypothesis and 3 full-source reviews per cycle.
Evidence, committed code/preregistration, checked-head lease and budget reservation precede return work.
Failed design gates stop the candidate; passing rules still need historical validation, independent review and actual account comparisons.
The app alerts only on a new worthwhile finding, material result or user-action blocker. Routine failures stay in receipts.
The user decides allocations. Paused t6/Hunt programs remain paused, with their earlier trial history preserved.

Analyst records are committed under `agents/codex/research/scout/records/`. Pull `codex/work` and refresh to see them here.
There is no automatic Git pull, live source synchronization, shared-user account or broker control.
Use this on a research computer, not the VPS. It binds only to localhost and rejects foreign origins/Host headers.
It intentionally offers no arbitrary command runner or generic filesystem browser.

## Check

    cd agents/codex/terminal
    /workspace/venvs/thebeginning/bin/python -m unittest -v test_terminal.py test_scout.py test_scout_gates.py
    node --check static/app.js

Integration tests use a temporary isolated note/inbox store; they do not edit real user data or run return tests.
