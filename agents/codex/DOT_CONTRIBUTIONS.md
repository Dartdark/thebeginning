# dot trading contributions

Summary: This index identifies trading work prepared by **dot**, separately from Codex's and Claude's research.
The November 10 package preserves prior findings, acquisition provenance and reproducible local paths.
It is documentation and artifact retention, not a new strategy test, portfolio decision or research-program restart.

## Attribution convention
- Author/origin: **dot**. New dot reports use a `dot_` filename and an explicit author line.
- Scripts retained at an existing `codex_` path have a dot attribution comment; that path is a repository convention, not evidence of independent Codex authorship.
- Sources by the user, Codex, Claude, providers and external creators remain credited. dot synthesis is not independent validation of their results.
- Commit subject for this package begins `dot:`. Existing Git identity is left unchanged; the message and files identify origin explicitly.
- Trading work belongs on `codex/work`; never push to `claude/*` or `antigravity/*`. No secret, restricted raw collection or live system change belongs in this package.

## November 10, 2026 deliverables
| dot contribution | Saved report / provenance | Disposition |
|---|---|---|
| Hyperliquid funding feasibility audit | [Audit](results/hyperliquid_data_audit_20261110.md), [script](../../analysis/codex_hyperliquid_data_audit.py), [request receipts and hashes](inputs/dot_trading_20261110/hyperliquid_receipts.json) | Partial final-rate acquisition. D32 NEEDS DATA; no returns. Raw and matched market observations remain local. |
| VB/ONB terminal-loss map | [dot synthesis](results/dot_vb_onb_loss_map_20261110.md) | Account floor can precede strategy stop. Broker/chart mismatch and account #1 remain unresolved. |
| Unbiased Trading review | [dot review](results/dot_unbiased_trading_review_20261110.md) | Representative methods/data/tool review, not exhaustive or a verified strategy. |
| Pre-2018 ES/NQ acquisition | [dot report](results/dot_pre2018_acquisition_20261110.md), [QA manifest](inputs/dot_trading_20261110/pre2018_manifest_qa.json), [original extraction script](inputs/dot_trading_20261110/pre2018_validate_extract.py) | Starts May 29, 2016; isolated, unadmitted, not an approved research extension. |
| Listed-provider acquisition | [dot report](results/dot_listed_providers_20261110.md), [coverage](inputs/dot_trading_20261110/listed_coverage.csv), [source manifest](inputs/dot_trading_20261110/listed_manifest.json), [original downloader](inputs/dot_trading_20261110/listed_download.py) | 48 FRED series + 4 World Bank panels. Current revised snapshots, not point-in-time surprises. |
| Earlier macro intake delivery | [Existing intake](inputs/eval_focus_20261109/macro_intake/), [later Codex reconciliation](results/eval_owned_data_reconciliation_20261109.md) | dot surfaced an already-committed copy and a payroll-clock discrepancy. Do not attribute Codex's later sidecar or tests to dot. |

Package source hashes and local artifact locations: [provenance](inputs/dot_trading_20261110/provenance.json).
Local raw paths are not cloud or fresh-clone availability guarantees.

## Publication scope and verification
Prepared against `codex/work` at `84108c9c`, after a non-destructive fast-forward from `eebf2cea`.
No backtest, download, strategy run, compile, live/broker/VPS change, external message, schedule change or scout/lab restart was performed for this publication.
Prior acquisition/audit checks are reported as prior checks; they were not rerun here.
Only explicit package paths are staged. Existing raw Hyperliquid responses and matched observations remain untracked and untouched because redistribution rights remain unresolved.
The included acquisition scripts describe earlier work. Running them can write files or contact providers; they are not executed by this documentation task. Fresh downloads are not exact replay of an immutable capture.
Do not rerun rejected screens: [latest Codex new-data screen](results/new_data_strategies_20261110.md) is separate Codex work and found no qualifying candidate.

## Whop review addendum (2026-11-10)

Author/origin: **dot**. [Source review](results/dot_whop_review_20261110.md): MNQ two-bar compression retained for a rule/parity check; Turnaround Tuesday low priority; Kusho broker/chart anecdote retained with unverified status. No new strategy tests or rank/plan changes. Private export and screenshots are not republished. Prepared against `cc168c49`; published separately from the acquisition package above.

## Community Research page addendum (2026-11-10)

Author/origin: **dot**. [Second-page source review](results/dot_whop_community_research_20261110.md): existing Fast Alphas negative screen, RollZone parity limits, VIX/Relative Strength/regime research, event-news selection warning and absent NinjaTrader MCP package. No new validated candidate, tests, strategy changes or installation. Private export and screenshots are not republished.

## Synergistic paper packets (2026-11-12)

Author/origin: **dot**. [Ranked research packets](results/dot_synergistic_paper_packets_20261112.md) combine drift-burst reversal with quote-event supply/demand recovery; calendar feedback with a queue-state veto; and queue prediction with inventory-aware execution and adverse-fill validation. Includes primary-source methods, explicit interaction hypotheses, ablations, invalidation conditions, causal clocks, data requirements and proposed bounded trials. Latest inspected 150K reference excludes VB; no live installation claim. Native event/receipt inputs and complete trading specifications remain blockers. Zero backtests, reservations, purchases, live changes or paused-program restarts. Report publication: `0f713a1e60d2dd103815820fdee53cb3e1d4185c`.
