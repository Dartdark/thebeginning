# Community Research page: dot source review

Author/origin: **dot**. Reviewed 2026-11-10.
Source: second user-supplied Whop export, Community Research page. Private export, screenshots and personal handles are not republished.

Summary: No new validated candidate emerges from this page.
Fast Alphas, RollZone, North Star VIX, Relative Strength and regime gauges already have relevant repository research.
The news-selection result warns about selection risk; its printed sample boundary needs clarification.
The NinjaTrader MCP reference is unreviewed tooling, not an acquired or approved integration.
Trials run: 0. No new strategy tests, strategy/settings changes, installations or schedules.

## Findings and disposition

### Fast Alphas: existing negative design screen

The [November 8 test](fast_alpha_books_20261108.md) screened 24 frozen instrument/version streams across five book types; none earned advancement. On all six fully resolved streams, delayed entry and combined entry/exit timing **reduced net profit versus immediate execution**. This does not mean each delayed stream had an absolute net loss. Partial conditional improvements elsewhere were weak/incomplete, and no controls, 2023+ validation or account stage was earned. Do not restart the same timing search from the community discussion.

### RollZone: corrections already retained; parity still unresolved

The [archived implementation](../inputs/weekly_cross_review_20261106/source/analysis/rollzone_24h_test.py) already includes the discussed reset `wf = 1 + break / ATR`, next-line high condition, all completed ranges including half-days, and a 75-point cap. Those changes are not a new untested repair.

The [archived verdict](../inputs/weekly_cross_review_20261106/source/checks/candidates/rollzone_24h/verdict.md) is **C, not for any Apex plan; personal capital-expansion bench only**. Author parity remains unresolved: trade counts match but yearly gross P&L differs, so the author's MultiCharts trade list is needed. The archived review is earlier evidence, not a fresh test or independent verification by dot.

### North Star VIX: replicated, but weaker portfolio fit

The [existing tier-list entry](../../../TIER_LIST.md) records the tradable next-open version at 9.0% CAGR, Sharpe 0.75 and 20.4% maximum drawdown. With the modeled personal-book sleeve, Sharpe fell from 3.04 to 2.91 and maximum drawdown rose from about $5.9k to $8.3k. It is already C: replicated historical standalone returns do not establish incremental portfolio benefit. No Apex adaptation or new allocation follows.

### Relative Strength and regime gauges: already researched

Relative Strength NQ/ES was already reconstructed and MultiCharts-confirmed, with a B, near-A assessment in the [tier list](../../../TIER_LIST.md). The page does not establish a distinct new rule or a reason to change settings.

The repository's six regime-gauge sizing rules already failed their stated joint design/recent-period gate. Retain that negative result rather than treating the page's regime discussion as evidence for reopening them.

### Event-news selection: unverified deterioration, not a rescue prescription

The source describes 67 news categories and 46 selected strategies, and reports in-sample PF 1.62 versus out-of-sample PF 0.98. These are author claims, not independently reproduced results. Both printed date ranges include 2023, so the exact split boundary and possible overlap must be clarified before describing it as clean out-of-sample evidence.

The sharp reported degradation is a selection/overfitting warning. Switching markets does not itself repair it or demonstrate a new edge. Exact rules, category definitions, initial-release/forecast clocks, costs, trade ledger and nonoverlapping selection/evaluation dates would be needed before an economic test.

### NinjaTrader MCP: referenced tooling only

A NinjaTrader MCP ZIP is referenced but was not supplied. Its source code, permissions, data depth, supported operations, safety and credential handling remain unverified. It could be a data/tooling route, but no acquisition, installation, broker access or persistent connection is claimed or authorized by this review. Inspect provenance, contents and exact permissions first if a later task supplies it; do not infer read-only behavior from the MCP label.

## Five review questions

1. **What is it about?** Community research on execution timing, range breakouts, volatility allocation, relative strength, regime gates, event selection and possible platform tooling.
2. **What does it find?** The meaningful strategy families mostly duplicate existing research. No newly validated candidate is established. The news example reports deterioration and an unclear sample boundary; the tooling package is absent.
3. **Why might it make money?** Source narratives such as short-horizon reversion, range expansion, volatility risk premium and relative-strength continuation are hypotheses or existing tested families, not proof from this page. The repository's standalone and account evidence, including failures, matters more than the narrative.
4. **Can we build on it?** Retain existing results and resolve concrete missing evidence: RollZone author trade-list parity; news rule/clock/split identity; or the actual tooling package and permission surface. No failed strategy is revived, no new queue candidate is justified, and no new backtest was run.
5. **Can a strategy code be made?** Existing code already covers Fast Alphas, RollZone, VIX allocation and Relative Strength. Exact reproduction of the event-news selection is conditional on missing rules, data and clocks. NinjaTrader MCP is tooling, not a directional strategy, and cannot be assessed from a referenced but missing ZIP. Coding feasibility never establishes profitability or permission for live use.

## Scope

Prepared against `codex/work` at `afadc49b93ae42fba11a7c2ef6fda28b6a5934ab`. dot's contribution is source synthesis and reconciliation with prior research. Existing author/researcher findings remain attributed to their sources. This report changes no rankings, plans, live systems or research schedules.
