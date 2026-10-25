# SPY closing-auction imbalance → ES: NEEDS DATA

Summary: Test whether published SPY closing demand adds information beyond existing late-day momentum.
Scheduled matching is documented; persistent executable ES pressure is a hypothesis.
No original auction-message sample, symbol-level quote or verified historical receipt clock is available.
Inspect SPY/Arca data first; no return test, purchase, strategy code or plan change.
Return trials: 0 for this candidate; related price-proxy auction studies were already tested.

Prepared 2026-10-25. This is an evidence sheet, not a strategy preregistration.
Source pin: Claude `c95951783557ca9e5dd1bbb85d6c9412ded2020b`; earlier Codex sheets read from codex/work `96c568d1c2a9b70bf947fae6a1d6dbb37955d59d`.

## 1. Who trades, and what causes the trade?

Close-benchmarked investors submit auction orders to obtain official closing-price exposure. SPY has an Arca closing auction; sources S1–S4 document the instrument, auction channel and data product.
Orders that remain live are subject to eligibility and matching rules; a published imbalance is not a guarantee every share must execute.
No evidence here establishes that all ETF creations, leveraged-fund resets or pensions use this auction, or that their futures hedging remains undone.

Prediction: unusually large signed SPY closing demand leaves a same-direction ES response after the observation becomes actionable.
Liquidity providers may demand compensation for inventory risk, but they can also absorb or pre-hedge the imbalance completely. Public dissemination attracts competing arbitrageurs.
The prior idea card's suggestion that capacity limits keep large players away is not established and is not a premise of this sheet.

## 2. Direction, size and timing known before entry

Observe SPY closing-auction messages only. Preserve explicitly defined imbalance side, total imbalance quantity, paired quantity, reference/indicative prices, auction type, sequence and timestamps.
Do not apply the side field to a different quantity without the historical specification confirming its meaning.
Indicative prices can change the reported imbalance without fresh orders; preserve those fields to distinguish repricing from order revisions.

Candidate quantity: signed unmatched shares × the contemporaneously available reference price, in dollars.
Normalize by a fixed trailing scale of completed prior auctions, never today's final auction volume. Exact denominator/warm-up awaits fields and coverage.
ES contract-equivalent notional = signed dollars / (50 × contemporaneous ES price), assuming a 100% ES hedge solely as an upper-bound illustration.
Actual hedge fraction is unknown and can be zero. Compare with previously observed ES dollar turnover in the intended window; there is no measured flow-size estimate yet.

Historical Arca schedule described by earlier inspected documents: publication from 15:00 ET, freeze at 15:59 ET, cross at 16:00 ET. Reverify each historical rule era; do not import NYSE or Nasdaq's 15:50 ET clock into Arca.
A 15:55 ET observation is an illustration, not a chosen parameter. Final decision, latency, first executable quote and exit will be committed before returns.
All timestamps must use America/New_York with conversion to America/Chicago and UTC; explicitly handle early closes and auction delays.
A source timestamp is not a customer receipt timestamp. If receipt history is absent, label the reconstructed delay and stress it; no zero-latency fills.

## 3. Does the flow reach ES or MES?

SPY and ES reference the S&P 500, giving a plausible direct hedge/arbitrage route. ETF inventory, options and stock baskets can absorb demand instead.
One ETF's imbalance does not measure aggregate S&P demand. Signed volume is not evidence that ES market orders of that size remain.
Failure to detect incremental ES transmission after an executable delay defeats this candidate, even if SPY itself moves.

## 4. Data feasibility and information beyond momentum

| Input | Product / fields | Coverage and timing gate | Availability / cost |
|---|---|---|---|
| SPY auction messages | TAQ NYSE Arca Order Imbalances; original closing messages, side/size/prices/type/time/sequence | Product advertised from 2012-01-30 in prior source audit; SPY 2018–22 completeness and historical schemas unverified | Missing. Quote/sample requested by user; no response as of this task |
| Auction results | SPY official auction print, size, actual completion time, corrections | Needed for prior-auction normalization and event audit | Not verified |
| SPY quotes | Historical NBBO around observations | Distinguish indicative price from executable price; preserve quote times | Missing in repo |
| ES prices and execution | Existing one-minute ES bars; synchronized ES bid/ask for executable validation | Bars support only coarse later screening; no quote-level fill claim from OHLC | Existing bars; quote coverage/cost unresolved |
| Calendar/reference | Exchange sessions, early closes, delayed auctions, symbol/schema/rule changes | Available before trading; archive actual versions | Must assemble during no-return intake |

Sources S1–S4 below were inspected by the earlier Codex work, not newly downloaded in this task. A sample directory listing is not evidence that files were parsed.
New input is actual auction order interest. Required later controls: preceding ES return and volatility, time to close, SPY indicative-price displacement relative to NBBO, and existing ES MOC price signal.
Do not select only dates when the existing portfolio is flat. A low average correlation alone will not establish incremental information.

Commercial list prices recorded in S6: Arca $500/data month; 2018-01 through 2026-09 = 105 months ≈ $52,500; 2018–22 ≈ $30,000.
These are inherited document figures, not a current personal-research or SPY-only quote, and no purchase is authorized.
Request a symbol/time-filtered extract, research terms and a sample. Nasdaq NOII via a reseller is an alternative *different* QQQ/NQ study; verify venue, schema, price and coverage separately. It is not interchangeable SPY data.

## 5. Costs and actual intraday gaps

Reference full-ES market round trip under the prior repo convention: $5 commission + two $12.50 ticks = $30 (0.60 point).
A 1.5× cost hurdle is $45 (0.90 point). These are budgeting references; actual ES/MES fees, spread and adverse selection must be verified before returns.
Do not divide full-ES commission by ten to invent native MES fees.
No plausible gross move has been measured, so economic feasibility is unresolved.

Closest comparators are ES MOC Follow and Late-Day Flow. The pre-close window overlaps the auction strategy and can overlap Monday exposure.
Existing occupancy maps under `analysis/outputs/codex_sge_delivery_screen/roster_*_occupancy.csv` describe an older roster; the earlier sheets' high post-close flat fraction does not apply to this pre-close proposal.
Refresh occupancy for the actual roster only at the appropriate later stage; no claim of an empty window is made here.
Assess edge on all eligible sessions; assess overlap and joint losses afterward.

## 6. Power before returns

Planning assumption: 252 equity sessions/year × five design years = 1,260 opportunities before gaps, warm-up and thresholds; not an event census.
Assume per-trade SD $200 per ES purely for budgeting; the sample must establish a plausible volatility scale without optimizing the rule.
For n independent observations, net mean for t≈2 is 2×SD/√n.

| Retained fraction (assumed) | n | Required net $/ES | Gross including $30 reference costs |
|---|---:|---:|---:|
| 100% | 1,260 | 11.27 | 41.27 |
| 50% | 630 | 15.94 | 45.94 |
| 20% | 252 | 25.20 | 55.20 |

Reproduction: `analysis/codex_spy_close_evidence_budget.py`; SD scenarios and effective-sample stress saved under `analysis/outputs/codex_spy_close_evidence/`.
Clustering lowers effective n. These thresholds are detection illustrations, not promotion gates or predicted profits.
If enough informative messages exist only on a handful of rebalance dates, stop or write a separately justified design; do not pool unrelated flows after a weak result.

## 7. Already researched and falsifiers

This is the same family as Claude's `checks/ideas/closing_imbalance.md` (S7), and its NYSE closing-imbalance evidence proposal.
Earlier Codex sheet A concerns SPY opening revisions; sheet B concerns post-auction reversal. Those are distinct future predictions sharing data, not independent flow families.
Existing ES MOC, WATCHLIST #10/#12/#20, pooled MOC studies and futures order-flow filters provide prior warnings; price-only approaches weakened after 2023.
Incremental input here is SPY's published pre-close auction imbalance; changing the clock on old price bars is not this study.

Falsifiers written before returns:
- Only final/revised summaries are available, original publication order cannot be reconstructed, or messages are stale/too sparse.
- Imbalance changes mostly reflect reference-price movements, without independent order information.
- Relation vanishes after preceding momentum/indicative-price controls, or only SPY moves.
- Response finishes before a defensible delayed ES entry.
- Gross effects fail realistic costs or depend on a few exceptional dates.
A failed follow-pressure prediction does not authorize switching to reversal, another timestamp or a favorable threshold without a new preregistered trial.

## 8. Failure, executable risk and diversification

| Question | Prediction / evidence needed |
|---|---|
| What ends the opportunity? | Faster repricing, better offsetting liquidity, feed/rule changes or less predictable imbalance persistence; require stable behavior across rule eras |
| Liquidity role | Initial candidate would take ES liquidity after receiving a message; measure spread, impact and adverse selection. Passive orders would be a separate execution assumption |
| Clustered losses | Imbalances cancel/flip, informed price moves overwhelm them, and closing liquidity deteriorates; replay noisy/rebalance/news days without post-hoc exclusions |
| Shared losses | ES MOC and LDF may lose simultaneously; NQ and ES share equity exposure. Joint-loss and chronological account tests required later |
| Offset before breach? | Unknown. A post-close recovery cannot rescue an account that breached earlier; do not count another account's hedge |

Before TEST: freeze a maximum holding period ending before the cash close, an executable catastrophe stop in ES points, account-size risk cap, quote/data stale limits and no-new-order behavior on data failure.
Exact numerical stop/size remain unresolved; none is inferred from a smooth backtest. No deployment is proposed.
At account stage: base, addition, ES-MOC replacement and empty-slot control, actual integer contracts/native costs, concurrent exposure, payout distributions, blow-ups and days to six payouts.

## Decision and next gate

**NEEDS DATA.** Finish the no-return acceptance checklist in `agents/codex/evidence/spy_close_imbalance_data_gate.md`.
A schema or sample alone can pass format checks but cannot establish multi-year feasibility.
If data/timing/cost/power are viable, write and commit one primary follow-pressure rule, explicit risk/execution, at most five total variants including robustness tests, and a numerical cheap-screen stop rule before any returns.
Use 2018–22 design first. Already-seen 2023+ is historical validation, not fresh evidence. No full bench until the cheap screen passes.
No order-flow logger, VPS change, vendor contact, subscription, trial account or purchase is authorized by this document.

## Source register

- S1: NYSE auction mechanics: https://www.nyse.com/trade/auctions
- S2: Historical product: https://www.nyse.com/market-data/historical/taq-order-imbalances
- S3: Historical Arca specification referenced by earlier audit: https://www.nyse.com/publicdocs/nyse/data/Integrated_Feed_Client_Specification_v2.4a.pdf
- S4: SPY issuer: https://www.ssga.com/us/en/individual/etfs/state-street-spdr-sp-500-etf-trust-spy
- S5: `agents/codex/results/flow_evidence_sheets.md`, prior source register accessed 2026-10-22; read at codex/work pin above.
- S6: `agents/claude_evidence/NYSE_QUOTE_EMAIL.md`, Claude source pin above; price figures and unanswered user quote request are separate facts.
- S7: `checks/ideas/closing_imbalance.md`, Claude source pin above; shared family, proposed hedge direction remains unverified.
- S8: `agents/claude_evidence/COMPARISON.md`, Claude source pin above; Arca and NYSE are separate products.

