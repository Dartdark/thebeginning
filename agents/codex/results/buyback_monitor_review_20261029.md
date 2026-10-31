# Buyback Monitor, July 2009: execution/accounting reference; no strategy established
Summary: Gumport marks historical corporate repurchases against July 10, 2009 stock prices.
Of 273 sampled firms, 179 repurchased shares; 45 of those programs are profitable under the author's measure.
This is capital-allocation hindsight, not causal evidence that buybacks destroy value or a tested short signal.
Retain the all-in-cost/disclosure lesson in EXECUTION_REFERENCES; no new return test or strategy queue entry.

Source: M. A. Gumport, *The Buyback Monitor – July 2009: Corporate Stock Buyback Profits of 273 Firms
From 2000 into 2009*, initial release July 13, 2009, Rev.1.
[SSRN 1433183](https://ssrn.com/abstract=1433183), user-uploaded PDF.
SHA256: `780a79b44b5575c59e729242ca89d613fb9630bc7032469319227416f23b9113`.
Review date: 2026-10-29. Source-only findings, not independently reproduced. New return trials: **0**.
Repo context: codex/work `fd8a54f386752423aba0dfdb19ad2d4a4659b694`.

## 1. What is it about?

How corporate stock-repurchase programs look when cumulative purchase spending and acquired shares are
valued using a later stock price. The sample comprises 273 public companies, largely technology firms,
with repurchases generally collected from 2000 into early 2009 and measured against July 10, 2009 prices.
It is a corporate capital-allocation report, not an event study or a backtested trading strategy.
The final section summarizes the author's other publications; those summaries are not independent results
established by the main sample.

## 2. What does it find?

| Source claim | Interpretation |
|---|---|
| 179 of 273 companies repurchased shares, spending approximately $263 billion. | Historical sampled activity, not a current flow estimate or comprehensive market universe. |
| 45 of 179 programs (about 25%) were profitable at the terminal price. | Programs measured at that date, not a trader's win rate, and not evidence that 75% lose in every subsequent period. |
| Reported average decline of repurchased shares is 19.7%; author estimates prices would be 8.4% higher absent buybacks. | The first is the report's retrospective measure. The second is a model-based counterfactual, not an identified causal stock-price effect. |
| Adding assumed foregone interest and other adjustments leads the author to suggest losses exceeding 30%. | This is an adjusted estimate, not a fully observed independent ledger of actual costs and realized losses. |

References: abstract; summary p.4; methodology/cost qualifications pp.5–10; discussion/conclusion pp.12–14.
The author explicitly acknowledges that the depressed terminal market prices skew the results and rankings can reverse.
Sample selection is largely tech-oriented and not established as a complete point-in-time investable universe.
The result mixes purchase timing, company performance, market declines and capital structure.
It does not compare matched firms or isolate a counterfactual unaffected by the repurchase decision.
Market-value return on spent cash also is not the same as total shareholder wealth including dividends and financing.

## 3. Why does it make money, if it does?

No external trading profit is demonstrated. A company buying below value can benefit continuing holders;
buying above value can do the reverse. This paper's terminal mark is not an observable intrinsic-value signal
available when a trader must enter. A share-price fall after repurchases does not establish a future continuation
or reversal edge, and a completed repurchase cannot be used as though its later disclosure was already known.

A buyback is a plausible source of demand while actually executing, but announcements, authorizations, bank
contracts, delivered shares and subsequent open-market purchases are distinct events. This report does not
establish a fixed future buying schedule, signed hedge requirement or residual ES/NQ price impact.
Stock-level activity must not automatically be promoted to net index demand.

## 4. Can we build on it?

**For execution/accounting diligence, yes; as a ready strategy, no.**

The report highlights omitted commissions, foregone net interest and costs/hedge legs around accelerated
share repurchases. Its appendix summarizes ASR and commission case studies, but those are source leads
requiring their original contracts/data, not verified evidence about current execution or regulatory rules.

Useful retained lesson: distinguish implementation shortfall from the market move after a purchase; reconcile
actual filled quantity/price, fees and related funding/hedging legs before accepting a claimed saving.
Use a preselected benchmark and horizon. A later drawdown is not, by itself, proof of bad execution.

A new corporate-flow hypothesis would first need dated authorizations versus actual execution disclosures,
historical receipt times, exact contracts, quantities, benchmarks and expiry/settlement provisions.
SEC filings and historical program documents would be starting sources; no availability/licensing audit was
performed here. Quarterly/monthly disclosed totals cannot reconstruct same-day intraday buying.
ASR initial share delivery cannot simply be treated as an equal-sized contemporaneous market order.
Any current rule claim requires current primary sources.

TIER_LIST already includes buyback-blackout calendar testing with no demonstrated benefit.
That is not an exact replication of this report, but this report supplies no reason to reopen that trial.
No specific new candidate meets the promising-strategy queue's documented-merit requirement.

## Decision and retention

**DON'T TEST as a strategy from this source alone.** No net P&L, predictive statistic, account contribution
or forward evidence is provided for an external trader. No new return trial, account allocation, code or live change.
Execution lesson retained as E13 in [EXECUTION_REFERENCES.md](../EXECUTION_REFERENCES.md).
For Claude: `agents/codex/results/buyback_monitor_review_20261029.md`.
