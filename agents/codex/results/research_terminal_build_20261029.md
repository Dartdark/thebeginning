# Beginning Research Terminal: local research workspace built
Summary: Built eight working views over the repository with PDF import and durable local notes.
The initial catalog indexed320 research documents and4 supported saved CSV outputs.
Seven HTTP integration tests and JavaScript syntax checks pass; visual browser QA was unavailable here.
Source is local-only; no hosting, broker/VPS/live controls, new return tests or allocation changes.

Entry point and desktop instructions: [terminal/README.md](../terminal/README.md).
Windows launcher: [start_terminal.cmd](../terminal/start_terminal.cmd).
Linux/macOS launcher: [start_terminal.sh](../terminal/start_terminal.sh).

## Implemented

Overview, full-text research library, strategy document catalog, saved-results CSV viewer/filter/export,
verification queue, searchable execution references, PDF inbox and create/save/delete research notes.
Source reports open in an escaped Markdown reader with links back to codex/work.
All counts and outputs come from the local repository, not placeholder performance data.

The original repository documents remain authoritative. Verdict badges are extracted from source headings;
they do not certify independent checks. Recent ordering is working-file modification time, not an audit of Git dates.
Refresh rereads local files and does not fetch GitHub. This is a functional first version, not an automated LLM
paper-review engine, live data terminal or backtest orchestrator.

## Storage and boundaries

Imports/notes live in agents/codex/runtime/terminal, under the already ignored runtime directory.
They persist on the user's computer but are not automatically committed, backed up or shared with other computers.
PDF extraction uses pdftotext if installed; otherwise the PDF remains previewable and extraction is marked unavailable.
The server listens only on127.0.0.1 and requires codex/work. Foreign Host/Origin requests and paths outside the
research document/CSV allowlists are refused. There is no arbitrary filesystem or shell-command API.
No existing research result or live file is edited by app operations.

## Validation

Configured Python:/workspace/venvs/thebeginning/bin/python. Integration tests run against a temporary isolated
note/inbox store and an ephemeral loopback server, leaving real runtime data unchanged.
Checks: catalog/source retrieval; path restrictions; note persistence/stale-save conflicts; foreign origins/hosts;
PDF validation/deduplication/retrieval; saved result/static assets; invalid/oversized writes. All seven pass.
node --check static/app.js passes. No supported browser-control/forwarded preview was available, so rendered visual
and interactive browser QA are not claimed. The cloud host's localhost is not the user's desktop localhost.
Use the local Windows launcher after pulling codex/work on the research PC; no VPS installation is requested.

For Claude: agents/codex/results/research_terminal_build_20261029.md.
