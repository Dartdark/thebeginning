# Beginning Research Terminal

A local research app for Dartdark/thebeginning. Python 3.10+ standard library; no package installation,
broker connection, hosting account or API key required. Dark interface with eight working views.

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

Refresh reloads the working tree; it does not fetch GitHub. Pull remote changes outside the app, then refresh.
The source links point to codex/work. Document contents are escaped; PDF text is treated as untrusted source material.

## Persistence and limits

PDFs, extracted text and notes are stored under `agents/codex/runtime/terminal/`, ignored by Git. They survive
server restarts on that computer. Back up that folder to retain personal notes/imports. They are not synchronized
to another computer, committed, or uploaded by the app. No data is sent to a cloud analysis service.
The note store uses revision checks to reject stale saves from another tab.

This is a functional research workspace, not an automated quant-research engine. Importing a PDF does not review it,
run an LLM, backtest a strategy, update TODO, or approve an allocation. The Results lab reads existing runs only.
SSRN login/downloads remain in your own browser. Use the chat workflow to request review of a new imported paper.
There are no live market feeds, automated source sync, shared-user accounts or broker controls.
Use this on a research computer, not the VPS. It binds only to localhost and rejects foreign origins/Host headers.
It intentionally offers no arbitrary command runner or generic filesystem browser.

## Check

    cd agents/codex/terminal
    /workspace/venvs/thebeginning/bin/python -m unittest -v test_terminal.py
    node --check static/app.js

Integration tests use a temporary isolated note/inbox store; they do not edit real user data or run return tests.
