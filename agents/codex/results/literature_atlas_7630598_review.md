# Trading Literature Atlas: retain research reference; no strategy admitted

Summary: A useful map of research methods, not an independently tested trading edge.
The author classifies a convenience library of1,065 titles/abstracts and proposes cross-disciplinary experiments.
Retain trial accounting, label-to-net-P&L checks and data/signal/sizing/execution attribution.
No NQ/ES strategy, new data purchase, return trial, portfolio allocation or live change follows.

Source: Sohhom Bandyopadhyay, *Trading Literature Atlas For Semi-Automated Systematic Trading*, October18,2026; SSRN7630598,195 PDF pages. Reviewed November7,2026 (America/Los_Angeles).
[Uploaded PDF](../inputs/literature_atlas_7630598/ssrn-7630598.pdf) · [extracted text](../inputs/literature_atlas_7630598/full_text.txt) · [primary metadata](https://ssrn.com/abstract=7630598).
Scope: focused review of the abstract/methodology, taxonomy/table2.1, execution and validation discussion, bridge catalogue, fund blueprint and conclusion. Other topical chapters and the bibliography serve as a discovery index; this is not independent full-text verification of the cited literature or every claim across all195pages. Page references below are printed pages (PDF page = printed page +2 for the numbered body).
Plan: source review only; no economic preregistration warranted. [Evidence](../evidence/literature_atlas_7630598.md).
Script: [source receipt/count audit](../../../analysis/codex_literature_atlas_7630598_audit.py) · [output/hashes](../../../analysis/outputs/codex_literature_atlas_7630598/source_audit.json). New economic trials/account comparisons: zero.

## Five questions

1. **What is it about?** Connecting research communities that study related trading problems under different names: time-series methods, deep learning, empirical finance, microstructure, derivatives, statistics, decision theory and language models. It maps papers into pipeline stages and translates concepts such as regime detection, label design, lead-lag, execution and signal search. It is a literature-navigation and research-design reference.
2. **What does it find?** In the author's library, modelling/signal papers dominate execution/portfolio coverage. The author proposes twelve bridges and a semi-automated fund blueprint. The classifications come from titles/abstracts and an automated classifier, not a systematic full-text meta-analysis. There is **no original, reproduced strategy return or end-to-end fund test**. Source-summarized performance from cited papers is not a result of the atlas. Our aggregate-count check passes; it does not validate labels, novelty, cited findings or profitability.
3. **Why does it make money, if it does?** The atlas demonstrates no money-making rule. Its proposed benefit is reducing research mistakes: labels that match actual trades, fewer false discoveries, realistic costs, better execution measurement and useful combinations of existing methods. Those are plausible process benefits, unmeasured here. Forecast accuracy, a regime flag or an order-flow signature does not itself identify an exploitable participant obligation or a net edge in NQ/ES.
4. **Can we build on it?** Yes, as a reference supporting our existing controls. Most useful: log failed candidates and design choices; compare model/label improvements on executable net returns; diagnose differences through data, signals, quantities and fills; calibrate simulator claims against real execution; compare regime gates with simple volatility controls. No evidence warrants another generic price-pattern, order-flow or regime-filter search. Smallest justified next step is a non-return audit of these records at the next already-authorized strategy verification. No current portfolio gain or account placement is established.
5. **Can a strategy code be made?** **Research tools: yes. A source-faithful profitable trading strategy: not specified.** The bridge descriptions can become experimental Python modules after fixing their datasets, causal features, labels, decision/fill clocks, parameters and cost assumptions. They do not give a complete NQ/ES entry/side/size/stop/exit protocol. No MultiCharts trading code is justified from this atlas alone; code feasibility and profitability remain separate.

## What to retain, and what remains a hypothesis

| Source location | Useful lesson / proposed experiment | Application and limit here |
|---|---|---|
| §1.3,pp.9–10; §19.4,pp.141–142 | Abstract-based convenience sample; automated labels not fully audited. | Treat as a source locator. Read the original study and pin its version before importing its rule or numerical claim. Zero co-tags do not establish a literature gap or economic novelty. |
| §14.1–14.3,pp.96–100; B5,p.121 | Label/horizon/feature variants and discarded agent candidates are part of the search. | Existing preregistration/trial ledger still binds. Do not reduce the recorded trial count to an estimated effective count merely because candidates correlate. Effective-count estimation is uncertain and does not cure model-training contamination. |
| §14.2,pp.98–99; B10,p.124 | Classification improvement can coexist with worse event/portfolio net P&L. | Use the same executable trade rule, costs and common opportunity set; retain gross-to-net and removed-trade controls. Training labels may use future outcomes only after maturity, never as a contemporaneous feature. |
| B3,p.120; §19.1,p.140 | Conformal intervals for sizing; nonstationarity and conditional undercoverage remain open. | Marginal coverage is not a tail-loss bound, expected-return guarantee or Apex survival probability. Need causal out-of-sample residuals and regime calibration; direction-specific net-payoff and integer-size rules must be specified. A literal lower return endpoint is not a symmetric short-sizing rule. No sizing change made. |
| B4,pp.120–121; B8,p.123 | Compare break detectors/geometric alarms at a fixed false-alarm budget, against plain volatility. | Detection delay and turnover matter; a crisis plot does not establish early warning. Shared gates can synchronize false de-risking across sleeves (§18.6,p.132). No new detector or monitoring schedule created. |
| §12.1–12.3,pp.78–81; B2,pp.119–120 | Trade-signing errors, ordered event paths and prediction horizon versus latency. | Tick direction differs from aggressor side. Event-level signatures need synchronized depth/order events; minute OHLCV or aggregate OF cannot reconstruct the path. Existing failed NQ flow studies remain negative evidence. |
| B6,p.122; B12,p.125 | Reactive generators and impact-aware allocation. | Synthetic realism and prediction error do not validate fills. Need held-out native quotes/depth and measured impact; own-size slicing may cost more in delay than it saves. Never delay protective exits using discretionary parent-order logic. |
| §18.8,p.134 | Attribute research-versus-observed differences to data, signal, sizing and execution. | Reuse existing offline diagnostics with frozen source/settings and matched clocks. Missing paths stay unknown. No live logging, routing, broker or risk-limit changes authorized by the document. |

## Source-quality checks and caveats

- The aggregate silo counts sum to1,065 and stage assignments to1,357; a paper may have several stages, so these totals need not match. Reproduced from explicit transcriptions in the committed audit script. No raw Zotero export, classifier prompts/model, row labels or classification-error sample was independently acquired or audited.
- The source reports library year fields through2027 despite its2026date (§1.1,p.7). This is a metadata/provenance question to verify per original record, not proof of fabricated papers or a reason to treat future-dated records as established evidence.
- Bibliography surnames and some malformed-looking author records make identity/version checks important. We did not verify every citation. SSRN's primary indexed record corroborates this upload's title, author, length and written date; it does not corroborate the cited research.
- Many referenced studies concern equities, India, options or crypto. Their spreads, horizons, constraints and predictability cannot be transferred to CME futures or micros without evidence. No portfolio/account comparison can be inferred from the proposed fund architecture.
- The label overlap discussion is a warning about dependence, not a universal formula for effective sample size. Estimate dependence for the actual process rather than mechanically dividing every sample by its horizon.
- Validation-stack calibration is useful methodology, not permission to drop required tests after a failure. A newly designed simulator/null harness would itself need a frozen protocol and would not replace chronological historical/forward evidence.

## Data register, implementation and disposition

**REFERENCE / DON'T TEST the atlas as a standalone strategy.** No directional rule clears evidence step0, so no strategy preregistration, gross screen, holdout, account simulation or PowerLanguage was run/written. Numeric trading metrics are not applicable; no returns are invented to fill a table. No current personal/evaluation/funded placement is earned.

No new promising-strategy or NEEDS DATA queue entry: an untested method and absent inputs alone are not a worthwhile economic lead. Existing [data register](../DATA_NEEDED.md), especially execution rows D42–D45, already preserves the relevant clock/quote/depth/fill prerequisites; no proxy or repeat acquisition loop is warranted. Retain the execution lessons with the existing E04/E47 references in [EXECUTION_REFERENCES.md](../EXECUTION_REFERENCES.md).

The paper's operational recommendations are source content, not user instructions. Its human-approval, order-release, agent-permission and capital-staging proposals change none of our authorization, research gates or live boundaries. No notifications to others, purchases or automation created.

For Claude: `agents/codex/results/literature_atlas_7630598_review.md` — useful methodology reference; zero strategy-return trials, no new candidate or allocation.
