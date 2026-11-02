# Research terminal: overview and account results ready for independent UI review

Summary: Built the research overview and strategy-results redesign, with shared design rules for Claude/Codex.
The overview exposes the local snapshot, saved scout checkpoint and review desk; results show all four account configurations with provenance.
48 Python tests, three JavaScript tests and 583 browser assertions pass; all 432 displayed financial cells match their saved CSV values.
Before/after desktop and mobile screenshots, reproducible checks and a prioritized Claude review task are saved.
Independent review is pending; this UI work runs no returns, changes no portfolio and creates no live integration.

Base: `e9022dae0e2b3211549714a0420da7f5238950d2`, confirmed remote `codex/work` before editing, 2026-11-02.
Publication: only `codex/work`, using a checked latest remote parent and non-force update. Shell Git network was unavailable;
GitHub connector access supplied remote state/publication. No reset, force-push or unrelated change is part of this task.
Concurrent remote commit `b1b6de6394ef66582a19f863d6167381a755624e` added three unrelated review documents during the work;
their exact blobs/tree were preserved and the local checkout advanced without resetting the UI edits. Publication uses
that newer checked parent (or its subsequently inspected descendant), while the review captures retain the original base.

## What changed and why

| Surface | Result |
|---|---|
| Overview | Removed the large introductory hero; placed checkout freshness, saved report/record counts, parked records, remaining scout definitions, completed account outcome and checkpoint first. Recent reports explicitly use local file times. |
| Strategy results | Registered PrimeSync's existing personal, funded50K/150K and evaluation50K/150K outputs. Context/home/cohort selectors display BASE/ADD/REPLACE/EMPTY with named metrics and units. Original raw CSV viewer/filter/export remains accessible. |
| Strategy research | Search saved analyst records by title, SSRN ID or finding; inspect source/evidence/plan status, design rejection, independent-review field and all five paper questions. The full evidence/plan/report library stays available. |
| Shared design | `terminal/PRODUCT.md`, `terminal/DESIGN.md` and local `terminal/AGENTS.md` guide future Claude/Codex UI edits. Native controls, authored navigation SVGs, readable dark tokens, visible focus, skip link and responsive layout. |
| Error and unknown states | Missing/invalid files produce visible status issues; absent/duplicate account rows never silently become zeros. Older comparison responses cannot overwrite a later selection or another route. |

Read-only `terminal/desk.py` adds saved presentation data to the existing catalog. `terminal/result_sets.json` declares
one reviewed CSV schema explicitly; unsupported/incomplete mappings are excluded. It never guesses that another file
has equivalent units or comparable portfolio settings. New schema support needs a deliberate mapping and parity review.
The local server stays Python standard-library; frontend stays plain HTML/CSS/JavaScript. No new product dependency,
third-party installer, hook, command runner, remote font, API key or external analytics service was added.

## Data and evidence meaning

The initial comparison is **PrimeSync's archived study**, not a new account test and not a forecast of the user's income.
The original report and CSVs are unchanged. Common coverage is2018-01-02 through2026-07-07; the candidate is one micro per
frozen eligible entry, with archived funded/evaluation stacks and the published19-piece personal reference from Claude6416de2.
Evaluation/funded candidate commission is$1.04/micro round trip plus one adverse tick on market/stop/time fills;
personal candidate commission is$1.275/unit round trip, retaining the study's inherited portfolio accounting.
The UI repeats those limitations beside the results. REPLACE means replacing Vault Break; EMPTY means removing it.

The original no-placement verdict is preserved. The closest personal ES30 ADD improves mean-profit/p95-DD by1.8%,
below the registered5% bar. Funded year-two output is **cumulative two-year payout**, not second-year income.
Failure/pass fractions become labeled percentages; p95 drawdown remains a dollar risk measure. Whole-dollar display
uses Intl currency rounding; half-dollar ties can differ by$1 from the report's Python rounding. Raw precision is retained.
No capital, Sharpe, payoff or funded outcome is calculated from a daily proxy by this UI.

At capture, scout progress held4/10 hypotheses and10/30 definitions, so the overview showed20 definitions remaining.
Its61 saved analyst records included17 parked for data/full text and two explicit design-reject records. These are counts
of those records, not a claim to summarize every historical repository trial; prior multiplicity is untouched.
File presence means only “file present”; the UI does not verify preregistration chronology or certify an economic gate.
“Ready,” a saved lease and saved scheduler configuration do not establish current automation activity. Pull externally,
then refresh. Local imported PDFs/notes remain in the existing Git-ignored runtime and are not synchronized by this UI.

## Verification actually performed

| Check | Evidence |
|---|---|
| Existing terminal/scout/admission and new presentation tests | 48 Python unittest cases pass. HTTP tests use isolated temporary runtime; source/gate fixtures do not run returns. |
| Numeric/selection helpers | Three Node tests pass: unknown vs zero, non-finite values, account/cohort/context matching, duplicate/missing configurations. |
| Browser acceptance | 583 assertions pass in headless Chromium154.0.8037.57, Python3.12.14. All432 financial cells across112 source rows are checked against original CSV values. |
| Failure/security/races | Load error/retry, missing/duplicate/zero values, escaped injected record markup, reversed request completion, leaving results during a request, reader Escape and active-page skip link. Fixtures stay in browser interception; no research files are rewritten. |
| Responsive/regression | All nine views smoke-tested; overview/results/strategy-record pages fit360/390/768px. Narrow comparison table scrolls within its labeled region. Desktop1440px and mobile390px captures visually inspected. |
| Syntax/diff | Both JavaScript files pass `node --check`; Python modules compile; `git diff --check` passes. |
| Design contrast | Declared main text/background16.01:1, muted/panel8.04:1, accent/panel12.93:1, control-border/input3.59:1. These token-pair measurements do not certify all rendered legacy states or full WCAG conformance. |

The browser harness exposed two harness issues before passing: Python banker rounding versus Intl half-away currency
rounding, and a same-document reload that retained an injected fixture. Both were corrected; the final screenshots use
real restored repository records. Tests also prompted explicit skip-link route preservation and late-response guards.
No failed financial screen was rescued, and no economic definition was added by these engineering checks.

Reproduce from `agents/codex/terminal`:

```bash
/workspace/venvs/thebeginning/bin/python -m unittest -v test_terminal.py test_scout.py test_scout_gates.py test_desk.py
node --check static/app.js
node --check static/desk.js
node test_desk.js
# Optional development-only dependencies: Playwright and Chromium already installed in this environment.
/workspace/venvs/thebeginning/bin/python review_ui.py --output /tmp/terminal-ui-review
```

[Browser receipt and hashes](../terminal/review/20261102/receipt.json).
[Launch/readme](../terminal/README.md); on the user's computer pull `codex/work`, restart the terminal server and refresh.
The cloud's localhost is not the user's desktop. No hosting or live-site publication was performed.

## Visual evidence

| Surface | Before | After desktop | After narrow viewport |
|---|---|---|---|
| Overview | [Original](../terminal/review/20261102/overview-before.png) | [Overview](../terminal/review/20261102/overview-desktop.png) | [390px](../terminal/review/20261102/overview-mobile.png) |
| Results | [Original raw viewer](../terminal/review/20261102/results-before.png) | [ES30,150K funded](../terminal/review/20261102/results-desktop.png) | [NQ15, personal](../terminal/review/20261102/results-mobile.png) |
| Analyst record | Existing document catalog retained in library | [Design rejection and five questions](../terminal/review/20261102/strategy-desktop.png) | [Record browser](../terminal/review/20261102/strategies-mobile.png) |

Captures precede the final report/commit, so their footer shows the base head plus local edits. The receipt records
that base and hashes of the reviewed UI files/inputs. Later pulls or this report can change counts/local file ordering.

## Manual Impeccable-informed review and limits

Applied the public **Operate**, **audit** and **craft-floor** guidance manually after inspecting incumbent renders:
prioritize the working task, preserve meaningful data, use consistent native controls, check contrast/focus and inspect
real responsive renders. The upstream context launcher was unavailable/not installed; existing code/README supplied
context and the new PRODUCT/DESIGN files preserve it. No Impeccable binary, detector, automatic hook or third-party
agent ran, and no numerical Impeccable audit score is claimed.

Manual findings addressed: P1 ambiguous financial units/provenance and unknown-state handling on comparisons;
P2 marketing content displacing oversight, tiny supporting copy and inconsistent navigation icons; P2 responsive
form/table behavior and missing shared design context. Existing origin checks, CSP and read allowlists remain.
This is a maker's source/browser audit, not a certified accessibility or independent economic review.

Remaining review scope: physical touch devices, screen readers, other browsers and Windows desktop launch were not
exercised here. Legacy document/scout views retain some compact styling; this task is not a complete redesign of all
nine views. The explicit account-comparison registry currently covers PrimeSync only; the other supported CSV output
remains in the raw viewer. Malformed core catalog documents can still make the overall catalog load fail, with the
existing refresh/recovery UI. The terminal reads working files without a transactional cross-file Git snapshot.
These limits must not be presented as verified compatibility or current account monitoring.

Sources inspected2026-11-02: [Google DESIGN.md](https://github.com/google-labs-code/design.md) for the shared-context idea;
[Impeccable SKILL](https://github.com/pbakaus/impeccable/blob/main/.agents/skills/impeccable/SKILL.md)
(blobc0dd2530c9968963b1f63bf50b227c4a33996e3b),
[Operate](https://github.com/pbakaus/impeccable/blob/main/.agents/skills/impeccable/reference/operate.md)
(blob524f2c3ae9fa497284e9699f3ca5320cce5d05cf),
[audit](https://github.com/pbakaus/impeccable/blob/main/.agents/skills/impeccable/reference/audit.md)
(blob13bf0d7c71802a48af4863c08ee3ed898f72c4b2),
[craft floor](https://github.com/pbakaus/impeccable/blob/main/.agents/skills/impeccable/reference/craft-floor.md)
(blobfd7280103f7ef4b009b38ce58f594c44c0f04caa).
This project's DESIGN.md is a human-readable contract; conformance to Google's alpha format/CLI is not claimed.

## Claude handoff

[Priority-ordered review task](../TASK_terminal_ui_review_20261102.md).
Ask Claude to verify economic presentation/status first, implementation/regression second and usability third;
return a severity-ranked verdict to the user. No external message was sent. Independent verification remains pending.
No trading plans/allocations, live strategy code, VPS, broker settings, API keys or scout progress/trial history changed.
