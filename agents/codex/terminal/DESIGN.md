# Beginning Research Terminal design system

Local research software for one trader overseeing academic research, strategy tests and independent review.
Use this file in both Claude and Codex before changing the terminal. It governs presentation, never economic gates.

## Product and visual direction

A calm, readable working desk for repeated use on a computer, with a useful narrow-screen layout.
Preserve the existing dark charcoal and pale-green identity. Use system sans for interface/prose and tabular numerals
for comparisons; monospace is for code, paths and identifiers. No remote fonts, animation libraries or external assets.
Primary pages are **Operate** surfaces; document reading is **Read**. Do not put marketing introductions above the work.

## Tokens

The authoritative CSS tokens are in `static/style.css`'s “Shared research desk system” block.

| Token | Value | Purpose |
|---|---|---|
| `--bg` | `#101619` | Workspace background |
| `--panel` | `#182024` | Grouped working surface |
| `--text` | `#edf1ef` | Primary text |
| `--muted` | `#aab7bd` | Secondary text, readable at body size |
| `--accent` | `#d0eea2` | Primary action, selected navigation, source links |
| `--blue` | `#b2d5e5` | Neutral source/reference status |
| `--red` | `#f0b6ae` | Rejection or load failure, always with text |
| `--warning` | `#edd39a` | Outstanding review, limitations |
| `--line` | `#344248` | Structural separators |
| `--control-line` | `#63747b` | Input boundaries |
| Spacing | 4 / 8 / 12 / 16 / 24 / 32 px | Group related content; separate sections |
| Panel radius | 8 px | Consistent, restrained grouping |

Body text 14px, supporting copy at least 12px on the redesigned surfaces; headings 30/22/15px.
Tables use `font-variant-numeric: tabular-nums`, right-aligned measurements, left-aligned row labels.
Use textual units in each metric. No green/red cell heatmap implying a recommendation.

## Information hierarchy

- Overview: current local snapshot → saved totals → review desk and scout checkpoint → recent reports.
- Strategy research: searchable records → selected record → explicit stages → five-question analysis and sources.
- Strategy results: comparison/context/home → recorded verdict → dates, size, costs → BASE/ADD/REPLACE/EMPTY → limitations and artifacts.
- Keep raw CSV inspection accessible. Do not guess units or reinterpret arbitrary CSV schemas.
- A frozen historical comparison must name its portfolio snapshot. It is not today's portfolio or a live forecast.

## Evidence semantics

`Not recorded` means unknown, never zero or a failed gate. Missing/ambiguous rows remain explicit.
Document presence means only “file present”; it does not prove preregistration order, gate acceptance or independence.
Use exact saved dispositions and attributed findings. Keep source claims, our simulations, independent review and trading
approval separate. New comparisons require an explicit registered schema, report, costs, dates and size.
Do not rank contexts, select a winner from viewed returns or produce new financial computations in the UI.
Use the existing result files; no return engine or command runner belongs in the terminal.

## Interaction and responsive rules

Native labeled inputs, buttons and disclosure controls. Provide keyboard-visible focus, a skip link and modal labeling.
Use consistent authored stroke SVG for navigation. Interactive controls target 44px height.
At 1100px the overview stacks. At 700px navigation becomes horizontally scrollable, forms stack and the candidate
list sits above its detail. Tables scroll inside a labeled, keyboard-focusable region; the page itself must fit 360px.
Loading/error/empty states explain what is missing and how to recover. Late responses must not replace a newer view.
No decorative motion. Preserve local-only operation, CSP, document/result allowlists and existing user notes/PDF stores.

## Design review workflow

Inspect the running incumbent, implement within this system, then review desktop and narrow-screen renders together.
Check keyboard navigation, contrast, missing/malformed records, exact CSV figures, delayed response races and the
existing terminal tests. Save review evidence and limits for the human/Claude handoff. A maker's UI checks are not
independent verification of either the software or its economic results.

References: [Google DESIGN.md](https://github.com/google-labs-code/design.md) (format inspiration; this file is a
human-readable project contract, not claimed to pass its alpha CLI schema), [Impeccable Operate](https://github.com/pbakaus/impeccable/blob/main/.agents/skills/impeccable/reference/operate.md)
and [audit guidance](https://github.com/pbakaus/impeccable/blob/main/.agents/skills/impeccable/reference/audit.md).
Applied manually; no upstream hooks, binary, installer or third-party agents are installed.
