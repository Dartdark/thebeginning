# Synergistic paper packets for a frequent-winner evaluation sleeve

Summary: Three ranked packets combine an opportunity mechanism with a different decision or execution ingredient.
First investigate GC/CL drift bursts plus observable supply/demand recovery; second, calendar feedback plus a queue-state veto.
Third, queue prediction plus inventory-aware quoting is the most frequent-looking architecture but the hardest to execute honestly.
These combinations are dot's research proposals, not combinations tested by the authors or validated high-win futures strategies.
No backtests, new economic reservations, purchases, live changes or paused-program restarts occurred.

Author: **dot**. Prepared November 12, 2026 UTC.
Scope: primary-source methods review, repository reconciliation and bounded research packets.
Repository research snapshot: codex/work `413c43931bd8ad78bac66b2964767eb3147bd04d`.
Latest inspected Claude branch: `6a5a1914ed15e91e689433d1a485a56592e00b3a`, read only.
Economic return trials: **0**. No inference of profitability, safe sizing or improved evaluation pass rate.

## 1. What this is trying to build

The target is a sleeve that earns frequent small realized profits, limits its *realized* loss tail, and improves the current evaluation's path before the deadline. The papers need different jobs:

1. **Engine:** why an opportunity could exist and which direction it points.
2. **Ingredient:** when that engine should abstain, how it exits, or how the opportunity survives real fills.
3. **Account test:** whether the combined sleeve contributes before an incumbent loss breaches the account.

Combining two papers is not automatically two independent edges. A queue predictor and an execution controller using the same queue state are one information source plus a decision policy. An exit paper can improve how an existing edge is harvested; it cannot supply missing alpha.

The current 150K project reference is **ONB ADX30 risk $2,750; Bridge Monday 5 MNQ; EOS risk $1,250; Twin cap1 2 MNQ; Dual Thrust 2 MNQ**. The November 11 [VB-removal commit](https://github.com/Dartdark/thebeginning/commit/9e4ad82f7d7233b6606c41043580fa3fa1e0bf8d) and latest [FUNDED_PLAN](https://github.com/Dartdark/thebeginning/blob/6a5a1914ed15e91e689433d1a485a56592e00b3a/funded_strategies/FUNDED_PLAN.md) agree. This is a repository plan, not a live installation audit. Refresh again before any account test. Older VB20/no-DT and VB15/DT benchmarks are different books.

The active [evaluation task](../TASK_eval_strategy_20261109.md) prioritizes distinct GC/MGC and CL/MCL mechanisms, then 6E/ZN. A different market is not assumed uncorrelated. The report therefore puts direct GC/CL source evidence ahead of another generic NQ fade.

## 2. Ranked packets at a glance

| Rank | Paper bundle | Engine | Distinct ingredient | Status |
|---|---|---|---|---|
| 1 | Christensen–Oomen–Renò + Cont–Kukanov–Stoikov | Short-lived drift-burst reversal | Quote-event supply/demand recovery gate | Best direct GC/CL evidence fit; native data and causal trigger missing |
| 2 | Li–Chen–Liu + Gould–Bonart | Cross-maturity feedback into the leading contract | Front-contract queue-state veto | Best repeated relative-dislocation idea; paired native quotes missing |
| 3 | Gould–Bonart + Cartea–Donnelly–Jaimungal + Lalor–Swishchuk | Very short-horizon queue prediction | Inventory-aware quote/withdraw decisions plus adverse-fill validation | Most execution-sensitive; research only, not current MultiCharts-ready |

Ranking is a research priority, not an estimate of expected return. Packet 1 has stronger market fit but not necessarily enough opportunities. Packet 2 has a different price anchor but an unverified CME transfer. Packet 3 can generate many signals while producing very few profitable executable trades.

## 3. Packet 1: GC/CL burst reversal + supply/demand recovery

**Engine paper:** [The drift burst hypothesis](https://arxiv.org/html/2601.08974v1), Sections 5.1–5.3, Tables 2–4 and footnote 24.

**Ingredient paper:** [The price impact of order book events](https://arxiv.org/html/1011.6402v2), Sections 2–4.

### Why these belong together

A large price displacement identifies where a reversal might be worth investigating. It does not establish that the pressure driving it has stopped. The second paper contributes a different observable: changes in displayed supply and demand, including quote changes that trade-volume bars omit.

**Local interaction hypothesis:** a burst that is followed by an already-observed reversal of depth-scaled OFI is more likely to offer a cost-covering retracement than a burst during continued one-sided depletion. The gate is intended to reject the continuing-pressure cases that could become a large losing fade. This is our conjecture, not a result established in either paper.

### Candidate research construction, not a completed preregistration

- Use the source-style backward-looking detector on native GC quotes first. CL is a separately counted replication, not a free additional choice.
- Create the event on a first threshold crossing with a frozen cooldown. Do not backdate entry to the best extremum in a later window.
- Use one fixed, short, completed observation window after the crossing. A permitted entry would be opposite the original burst only if signed OFI now opposes the burst and a prespecified executable-spread condition is satisfied.
- Measure OFI from ordered top-of-book updates. Depth-normalized OFI is a feature; it is not proof that an identifiable market maker replenished liquidity.
- Enter only after that window and processing latency. The price at the trigger or at the window's favorable extreme is unavailable as a guaranteed fill.
- Freeze one stop, one target, one maximum holding time and an entry cutoff before returns. No averaging down, risk increases after losses or repeated same-burst re-entry. A planned stop remains subject to gaps and slippage.

**Complementarity test:** compare the combined rule with the same detector, decision delay, risk and exits without the OFI gate. Also compare a matched price-only recovery condition. If the second ingredient simply restates the rebound already visible in price, there is no demonstrated OFI contribution.

**What invalidates it:** first-crossing results disappear after the confirmation delay; removed events are not net losers; random drops match the apparent risk improvement; stressed costs remove the edge; or remaining opportunities are too sparse to affect a 30-calendar-day evaluation. A fresh title does not justify retuning the earlier NQ pressure failures.

**Tail concern:** this is still a liquidity-taking contrarian position. It may lose when all markets reprice together. Gold/oil labels do not protect the book. Test losses on current-book stress episodes, including whether any gains occur before the account's first breach.

**Feasibility:** owned GC/CL minute prices support an inventory check, not faithful burst/OFI reconstruction. Need native bid/ask prices and sizes, event sequence, contract identity, exchange/receive clocks, and the intended MGC/MCL execution history. No complete matching free panel was verified here. Research feature code is feasible; a source-faithful trade test and deployed strategy are not ready.

## 4. Packet 2: calendar feedback + queue-state veto

**Engine paper:** [High-frequency lead-lag relationships in the Chinese stock index futures market](https://arxiv.org/html/2501.03171v1), Sections 2.2, 3.3 and 4.4.

**Ingredient paper:** [Queue Imbalance as a One-Tick-Ahead Price Predictor in a Limit Order Book](https://arxiv.org/pdf/1512.03492), Sections 5–6.

### Why these belong together

The first engine uses a relationship between two maturities as a short-term anchor. The second asks whether the tradable contract's current queue state supports another move away from that anchor. These measure different objects: *relative displacement* versus *immediate depletion pressure*.

**Local interaction hypothesis:** fade a leading-contract dislocation only when its own queue state no longer strongly predicts continuation in the dislocation's direction. The queue model acts as an abstention gate, not a second reason to chase the same price move.

### Candidate research construction

- Retain the source's basic residual: current front-minus-next spread minus its past-only EMA. Select contract roles using a rule knowable before the session.
- Trade only the liquid leading contract in this packet. That is distinct from opening a two-leg calendar spread.
- Fit a simple queue-imbalance probability model on past data. Use it only as a frozen veto on the proposed trade, then compare with the unfiltered engine.
- Require both maturity observations to have arrived before the decision; stale next-month quotes can manufacture a dislocation. Fix maximum quote age, synchronization and roll rules before testing.
- Use a causal decision schedule. Do not copy research observations sampled using the known time of the next price change.
- Recover the engine's full exit/reversal protocol before claiming replication. A bounded-stop/short-target adaptation is a new local rule and must be labeled and counted.

**Complementarity test:** the queue gate must add value after conditioning on the size of the spread residual, spread cost, time of day and quote age. Compare with an equal-coverage veto using only the leading contract's recent price move. A gain entirely explained by dropping stale quotes is data cleaning, not additional alpha.

**What invalidates it:** the residual is mostly asynchronous-price error; only the lagging contract moves while the front provides no retracement; realistic delay consumes the edge; the gate raises win rate by deleting profitable trades; or the outright front position retains unacceptable directional tails.

**Important non-combination:** the OU stop-loss paper below cannot simply be attached as an “optimal stop” here. The signal is a spread, but the traded P&L is one outright contract. Those are different state/payoff processes. Trading both maturities would change the strategy, costs, integer sizing and family definition.

**Market and data fit:** CME index maturities are the closer translation of the source than commodity storage/seasonality spreads. GC/CL calendar applications would require a distinct economic justification rather than changing the symbol. Need simultaneous identified expiries, native front/micro costs and quote receipts; continuous minute files are insufficient. Source-reading value is high; implementation readiness is low.

## 5. Packet 3: queue prediction + inventory-aware execution + adverse-fill testing

**Engine paper:** [Gould and Bonart](https://arxiv.org/pdf/1512.03492).

**Decision/exit ingredient:** [Enhancing Trading Strategies with Order Book Signals](https://kclpure.kcl.ac.uk/ws/files/115267447/Enhancing_Trading_Strategies_CARTEA_Accepted_24_Jan_18_GREEN_AAM.pdf), Cartea, Donnelly and Jaimungal; Sections 3–5 and queue-fill extension.

**Execution-validation ingredient:** [Market Simulation under Adverse Selection](https://arxiv.org/html/2409.12721v1), Lalor and Swishchuk; Sections 4–5.

### Why these belong together

The predictor estimates direction. The controller decides whether to quote, stop quoting or reduce inventory given that signal and current exposure. The third paper challenges whether the apparent small profits survive the fact that favorable fills may be missed while unfavorable fills arrive.

**Local interaction hypothesis:** the same forecast is more useful when it changes both entry permission and liquidation urgency than when it mechanically opens a fixed-size trade every time a probability crosses a threshold. Expected improvement must come from fewer costly filled mistakes, not a higher unconditional classification score.

### Candidate research construction

- One simple chronological queue predictor, not a deep model search.
- One-unit maximum inventory, no averaging down, no size ladder. Decide explicitly whether the selected market's minimum tradable unit meets the proposed sleeve loss budget.
- Use signal/inventory/time state to allow or withdraw each quote side. Include a short fixed maximum inventory age and an emergency flattening policy, all priced at executable quotes.
- Freeze order lifetime, cancellation/replace delay, queue priority, partial-fill accounting, fees and the losing-fill path.
- Compare a fixed-entry/exit predictor baseline with the inventory-aware policy using identical signals and risk bounds.
- Validate using an event replay that can fill bad orders while missing good ones. Do not assume the simulation paper's illustrative 0.2 probability is a universal fill rate.

**Complementarity test:** unchanged predictive probabilities, different execution policy. Separate signal accuracy, filled-trade accuracy, profit per submitted order, profit per filled order, missed opportunities, inventory losses and cancellation races. The controller is not an independently discovered signal.

**What invalidates it:** profitability requires front-of-queue priority, zero latency, all touched limits filling, midprice liquidation or fee rates the user cannot obtain; stressed losses still cluster with ONB/Twin/DT; or the policy merely postpones marking losses. With native retail costs, one predicted tick may be insufficient.

**Feasibility:** this is the most demanding packet. Existing minute bars and summarized book/wall fields do not provide event ordering or queue position. It needs a native order-lifecycle replay before any MultiCharts port. A research model can be written; a reliable executable CME sleeve has not been established. No broker API or live access is required or authorized for the proposed research stage.

## 6. Paper cards: five questions, with evidence boundaries

### Christensen, Oomen and Renò: drift bursts

- **About:** detecting brief explosive moves in CME midquotes.
- **Finds:** at threshold 4.0, GC has 1,324 events and 78.1% opposite-sign five-minute returns; CL has 1,606 and 71.3%, during 2012–17. These are descriptive reversal incidences, not net trade wins.
- **Why money:** transient urgent demand could leave a retracement; no executable strategy is demonstrated.
- **Build:** use the backward detector, then independently establish a causal trade.
- **Can code:** yes for the detector; conditional for trading. Five-second evaluations use five-minute drift and 25-minute volatility bandwidths. Footnote 24 selects a local extremum within five minutes. First-crossing entry changes the event definition. The 2026 arXiv posting is not a new 2026 sample.

### Cont, Kukanov and Stoikov: order-book events

- **About:** best-quote changes from trades, additions and cancellations.
- **Finds:** depth-scaled OFI explains contemporaneous short-interval stock price changes better than volume alone.
- **Why money:** it measures pressure and liquidity, not an established future-return strategy.
- **Build:** use observable supply/demand change as an ingredient; do not infer future alpha from same-window fit.
- **Can code:** yes from ordered bid/ask prices and sizes. Ordinary buy/sell volume and two wall summaries cannot reconstruct that stream. Distinguishing specific replenishment actions requires richer event semantics.

### Li, Chen and Liu: calendar feedback

- **About:** near/next-maturity relationships in CFFEX futures, 2022–24.
- **Finds:** authors report roughly 26–168 OOS trades/day after assumed fees/spread; win rates are not reported. The first 400 days select a threshold.
- **Why money:** relative-price feedback may restrain the leading contract.
- **Build:** conditional on CME replication, synchronous receipt and complete rules. Their roughly 500 ms feed arrives across maturities in a fixed sequence, a material transfer issue.
- **Can code:** yes after resolving intermediate exit/reversal semantics and risk. The source trades the leading contract, caps one lot and flattens daily. Latency is not established by taking the current bid/ask in a backtest.

### Gould and Bonart: queue imbalance

- **About:** best-bid versus best-ask queue size predicting the next midprice direction.
- **Finds:** predictive classification in ten Nasdaq stocks, stronger for large-tick stocks; random 80/20 validation, not chronological.
- **Why money:** queue depletion can precede a price change, but classification does not establish after-cost returns.
- **Build:** a simple transparent baseline and veto.
- **Can code:** yes, with native quotes and past-only logistic fitting. Their research sampling picks a random point between successive price changes; the interval endpoint is future information at that point. Use an online sampling rule instead. This is a transportability issue, not an allegation that their descriptive study is invalid.

### Cartea, Donnelly and Jaimungal: book signals and inventory

- **About:** joint quote, imbalance and inventory decisions.
- **Finds:** their 2014 Nasdaq study reports improved simulated performance using imbalance; the paper also documents severe adverse selection in naive spread capture.
- **Why money:** avoid unfavorable quoting and manage directional inventory.
- **Build:** use the decision architecture, not the equity Sharpe headline.
- **Can code:** yes as a model-based controller. Inventory penalties and terminal liquidation are explicit. Initial front-of-queue assumptions are supplemented by an imbalance-dependent probabilistic fill extension. Neither establishes the user's actual queue priority, cancellation latency or all-in futures costs.

### Lalor and Swishchuk: adverse fills

- **About:** fill assumptions in market-making simulation, with ES, NQ, CL and ZN applications.
- **Finds:** admitting adverse fills and reducing favorable-fill probability materially worsens outcomes.
- **Why money:** it supplies no new alpha; it can reject fictitious profits.
- **Build:** mandatory stress design for packet 3, also useful whenever packets 1–2 use passive orders.
- **Can code:** yes as a stress harness, but state-dependent empirical fills and order chronology must replace portable constant assumptions. More conservative simulation is not proof of live accuracy.

## 7. Optional exit-design pair, not a fourth alpha claim

[Leung and Li, Optimal Mean Reversion Trading with Transaction Costs and Stop-Loss Exit](https://arxiv.org/html/1411.5062) supplies joint entry/target/stop geometry for an assumed OU *tradable spread*. Its model can exclude entries too close to a stop. [Kitapbayev and Leung, Mean Reversion Trading with Sequential Deadlines and Transaction Costs](https://arxiv.org/html/1707.03498) supplies finite entry and holding-window boundaries.

For each: **about** optimal timing under assumed dynamics; **finds** mathematical boundaries, not a verified CME edge; **why money** assumed mean reversion must exceed costs; **build** only after identifying a genuinely tradable mean-reverting state; **can code** yes for a numerical solver with past-only parameter estimates.

These are compatible ingredients to investigate for an already-admitted residual strategy, not a license to attach OU labels to every price fade. The second paper's exit window starts at entry, not automatically at 15:59 CT. Combining a hard stop, session deadline and account constraint requires a new jointly specified problem, not splicing two separate “optimal” solutions. Jumps can overshoot model stops. The project's failed OU/VWAP filter and index-pair families remain closed.

## 8. Shared preregistration and trial contract

This document is a **proposal**, not a return-ready preregistration. Before any returns:

1. Admit one packet and one market only after exact inputs, clocks and family duplication checks. Record source versions, code/input hashes and actual usable dates.
2. Freeze the complete event, synchronization, feature, entry, stop, target, time exit, daily entry cap, cooldown, integer size, fees and latency rules. Unknown values remain blockers rather than researcher discretion.
3. Proposed initial budget per admitted family: at most **four economic definitions**: engine baseline; engine plus ingredient; matched price-only/naive-policy control; one predeclared timing/side control. At most two selectable candidates. Count controls and gross screens. More variants require a new recorded allocation, never a reset.
4. For a removal filter, report total dollars, the removed trades' net results and an equal-count random-drop distribution of at least 1,000 draws. Win rate alone is not an acceptance gate.
5. Run the cheap 2018–22 design gate only if matching data genuinely exist. A shorter/newer native panel requires a declared revised study; already-seen later years are not a fresh holdout. Keep chronological fitting and mature labels.
6. Failure stops dependent work. Do not reopen a failed rule by changing window, ticker, threshold, stop or model. New inputs justify a feasibility review, not automatic TEST admission.
7. Only earned survivors receive later historical replication, paired current-book tests, independent/native-platform checks and frozen forward observation.

The scout still records **4/10 hypotheses, 10/30 economic definitions, null lease**. These are its existing counters, not this packet's new allowance. No reservations or counters changed. The latest Claude branch retains [lab/STOP](https://github.com/Dartdark/thebeginning/blob/6a5a1914ed15e91e689433d1a485a56592e00b3a/lab/STOP); the explicit scout/lab/t6/Hunt pauses remain controlling. The stale scout “ready” field is not authorization to run it.

## 9. What would count as a real contribution to Daniel's book

After the strategy independently earns the account stage, freeze BASE/ADD/REPLACE/EMPTY, the replacement slot and one integer candidate size before seeing results. Do not optimize size against recent account outcomes.

Primary outcome remains paired improvement in **pass probability before 30 calendar days**, with the active task's prespecified interval and execution-stress requirements. Report timeout and breach rates and the whole time-to-pass distribution, not only the successful paths.

Also report:

- Wins per active day and per calendar month; median gain, average gain/loss, profit factor, consecutive losses and total net profit.
- Maximum single realized loss, worst adverse excursion, 95%/99% loss tails and clusters, with sample-size limits.
- Worst-day and incumbent-loss-episode P&L, timestamped before breach/DLL lockout. Report normal periods too.
- Spread, commission, slippage, latency and emergency-liquidation costs separately; native micros are not standard-contract net P&L divided by ten.
- Same account netting, order priority, simultaneous exposure, early closes and actual integer finish sizing in every arm. No fill exactly at a breached DLL by assumption.

No high win rate or negative ordinary correlation is treated as proof of an offset. The intended success is repeated modest *net* gains with losses small enough and early enough to improve this particular evaluation path.

## 10. Existing work preserved and next handoff

Read alongside [pressure build](pressure_strategy_build_20261110.md), [prior arXiv shortlist](dot_arxiv_eval_shortlist_20261111.md), [exit/liquidity reading](dot_archive_eval_reading_20261111.md), [RESEARCH_CONTROLS](../RESEARCH_CONTROLS.md) and [DATA_NEEDED](../DATA_NEEDED.md).

All **19 Codex pressure definitions failed** their design gates. Earlier innovation fades, absorption, liquidity-vacuum, book filters, OU/VWAP and index-pair studies remain in selection history. Latest Claude work separately contains jump-fade code and testing; this report does not duplicate or adopt it. Native event data would change what can be measured, not erase prior failures.

**Smallest next step:** a no-return data/specification admission for packet 1, then packet 2 if packet 1 is blocked. Verify whether a permitted existing/free source supplies the actual event sequence and receipts. Do not buy data, contact vendors, substitute bar proxies or start packet 3 because the first two lack inputs. The useful deliverable today is these testable interactions and their rejection conditions, not a guessed backtest.

Primary full text was inspected through arXiv and the King's College accepted manuscript. The first King's portal PDF route returned 403; its public `/ws/files/` manuscript route was readable. No paywall workaround or restricted source was used. Older source reports were reused as context, with methods rechecked for the combinations here.

**For independent review:** `agents/codex/results/dot_synergistic_paper_packets_20261112.md`. Research attributed to dot; author findings, local hypotheses and prior repository results remain separate.
