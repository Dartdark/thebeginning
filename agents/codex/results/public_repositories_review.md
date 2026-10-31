# Public trading repositories and futures playbook: useful tools, unreliable strategy specifications

Summary: Reviewed all 10 repository entries, all 9 strategy archetypes, and the Jesse/risk guidance.
Best value: Jansen's research material, selective use of vectorbt, and a future Nautilus tick/event-replay prototype.
The HTML's strategies are adaptations with missing evidence/settings; several contradict their cited source or current API.
No backtests, package installation, broker integration, purchases or live changes were performed.
Treat it as a learning directory, not evidence that any listed strategy works on NQ/ES or improves our plans.

Date: 2026-10-26. Uploaded HTML was parsed as text; embedded JavaScript/imports were not executed.
Input: agents/codex/inputs/public_repositories_review/Public_Trading_Repositories_and_Futures_Strategies.html.
Scope: source-level triage and selected implementation checks, not an exhaustive security audit or full repository verification.
Return trials: 0. The user's explicit request here is document analysis, not a request to backtest all nine adaptations.

## 1. Every repository: usefulness to our actual workflow

Priority is practical research usefulness, not a profitability grade.

| Repository | Decision | Concrete use / limitation |
|---|---|---|
| stefan-jansen/machine-learning-for-trading | HIGH: study selected chapters/case studies | Best structured material for data provenance, validation, transaction costs and ML workflow. Current README describes third-edition material; examples are educational and dataset rights/availability vary. Extract methods into our workflow rather than adopting reported returns. |
| nautechsystems/nautilus_trader | HIGH potential, LATER integration | Event-driven replay of quotes/trades/order books and timestamped custom events is relevant to auction-data execution. It does not supply missing auction history or prove fills. Migrating our Apex accounting is real work; do not replace the current engine before exact parity checks. No Rithmic/MultiCharts compatibility is assumed. |
| polakowo/vectorbt | MEDIUM/HIGH for bounded research | Fast signal arrays, diagnostics and plots can help preregistered screens. Thousands of searches increase selection risk. The free/current product and paid PRO feature sets differ: do not infer full futures/leverage/limit-order support from PRO links. Current LICENSE.md is Apache2.0 with Commons Clause, not unrestricted Apache2.0. |
| microsoft/qlib | MEDIUM, later | Useful templates for feature/label datasets, ML training and evaluation. It does not automatically model CME fills, Sunday sessions or Apex payout/trailing rules. Our current scarce resource is independent data and validated hypotheses, not a larger model library. |
| je-suis-tm/quant-trading | MEDIUM as readable teaching code | Useful worked examples of Dual Thrust, spreads and statistical concepts. README explicitly uses frictionless trading assumptions. Rebuild mechanics, fees, chronology and risk before treating any result as ours. |
| freqtrade/freqtrade-strategies | MEDIUM for components, LOW as a source of proven edge | Real collection of example indicators, position management and strategy templates. Source README warns results depend on market/timeframe/period. Separate futures files from long-only examples. Its risk/execution hooks are not MultiCharts code. |
| joshyattridge/smart-money-concepts | MEDIUM for descriptive features; HIGH leakage caution | Useful algorithmic definitions for gaps/swings/structure. Some outputs need future bars and later mitigation; availability times must be explicit before they become predictors. OHLC patterns do not measure institutional orders or intent. |
| hummingbot/hummingbot | LOW for current CME/Apex; useful separate crypto project | Crypto venue connectors, inventory, arbitrage and execution lifecycle examples. Funding/basis research is economically different from NQ auctions. Hedged legs still carry fees, funding changes, liquidation, venue and legging risks. Not a route to deploy our CME plan. |
| iterativv/NostalgiaForInfinity | LOW/MEDIUM for code organization | Large Freqtrade strategy worth studying for modular signals and operational controls. The tiny HTML class is not a verified reproduction of its current logic or results. Complexity increases the audit burden; its historical performance does not transfer to the adaptation. |
| gabrielweich/jesse-strategies | LOW/MEDIUM for beginner examples | Small readable examples of Donchian and pullbacks. Cited Donchian and DaveLandry implementations are long-only; both should_short methods return False. They are not the complete bidirectional futures rules claimed in the HTML. |

No framework here natively establishes our funded-account rules, native micro fees, roll accounting, session mapping or portfolio contribution. Those require explicit adapters and validation.
GitHub stars and labels such as production/institutional are not measurements of trading edge. No decisions here depend on the HTML's star counts.

## 2. Every strategy archetype

| HTML archetype | Assessment | Why / what would be required |
|---|---|---|
| 1 NFI futures scalper | NEEDS SPECIFICATION / code repair | Generic trend-plus-oversold recipe, not verified NFI parity. Code's RSI short threshold is68 while prose gives72; prose also has a breakdown branch missing from code and different trailing/target behavior. Symbol/timeframe, provenance and runtime version are absent. Current Jesse calls fail as described below. |
| 2 Triple Supertrend | LOW PRIORITY; code repair before any test | Three transforms of the same prices are not three independent confirmations. It can be a testable trend rule, but sideways-market immunity is unsupported. HTML code checks levels, not a new three-way flip; uses invalid current Supertrend fields. Linked Supertrend.py itself populates long entry/exit, not this short-side adaptation; a separate futures example exists. |
| 3 Asymmetric Dual Thrust | RELATED / already researched | Prior-range breakout is a real established family. Document's four-day lookback and0.55/0.45 thresholds are new settings, not verified necessities from liquidation mechanics. They differ from our tested Dual Thrust v4. No reason to re-optimize our stronger existing version or inherit its A rank. A crypto session boundary must be defined. |
| 4 FVG/order-block/liquidity sweep | NEEDS CAUSAL SPECIFICATION; do not prioritize for alpha | Identifies chart patterns, not who placed orders. Exact swing confirmation, sweep rule, expiry/mitigation, order-block definition, invalidation and fills are missing. Library can label past events using future observations; apparent backtest edge could be leakage. A bullish FVG does not guarantee the proposed stop is below the entry: validate positive risk from actual prices. |
| 5 Donchian/Turtle | REFERENCE BASELINE, not new portfolio edge | A clear breakout baseline once window/session and lagging are explicit. Original Jesse code excludes the current candle and uses a long-only channel system; HTML changes it to20/10 and adds shorts. If the upper channel includes today's bar, close>highest(high) is impossible. Any personal multi-sector trend application requires its own data/rules; not an instant Apex candidate. |
| 6 Dave Landry two-bar pullback | NEEDS SPECIFICATION; source mismatch | Original example buys lower lows with a trend filter and closes after closes exceed preceding highs. HTML describes buying a subsequent breakout and adds shorts. Those are different entries/exits. Four-/six-hour hints do not specify market, session, risk or exact orders. |
| 7 Cointegrated pairs | REFERENCE THEORY; LOW priority on our index futures | Correlation is insufficient; estimate hedge ratio and spread scale using prior data, enforce chronological cointegration checks and integer two-leg sizing. Crypto funding/basis affect both P&L and stability. Our NQ/ES and related intraday spread tests already failed costs; this document supplies no new evidence to overturn them. |
| 8 Almgren–Chriss / TWAP | USEFUL EXECUTION CONCEPT, not standalone alpha | Referenced file really exists and implements slicing with Freqtrade callbacks. Optimal execution trades impact against price risk; it cannot eliminate slippage. At our small micro sizes, waiting to slice can sacrifice a short-lived signal. Requires actual order-size/volume/impact evidence before use. |
| 9 PSAR trailing scalper | EXIT EXAMPLE ONLY; presentation materially overstated | Cited class describes itself as a custom-stop example with placeholder entries. It does not establish the advertised volatility-regime, bidirectional perpetual scalper or flash-crash protection. An exit tool requires testing against existing exits; stops do not guarantee fills. |

None of the nine includes new evidence of measured scheduled demand. Hummingbot's funding/basis tools could support a *separate* crypto scheduled-cash-flow study, but no such strategy is specified or tested here.

## 3. Concrete Jesse defects and risk-guidance corrections

Verified against current jesse-ai/jesse source:
- `utils.size_to_qty(position_size, entry_price, precision=3, fee_rate=0)` has no `leverage` keyword. The HTML's repeated calls raise an argument error against this version.
- Supertrend returns `SuperTrend(trend, changed)`; `.value` in the HTML is invalid. Using `.trend` would fix the field reference, not validate the rule.
- The current entry-cancellation lifecycle hook is `should_cancel_entry`, not the HTML's `should_cancel`. Confirm version-specific hooks; do not assume old example callbacks execute.
- `size_to_qty(available_margin*0.15,...)` allocates a fraction of notional; it does not make the stop-loss risk15% or any other fixed risk. Position risk depends on quantity, stop distance, contract multiplier and fees. CME requires integer contracts and NQ/MNQ point values, unlike these asset-quantity examples.
- The instruction never to use fixed dollar sizes is wrong for our purpose: a fixed dollar-at-stop budget can be appropriate. Margin availability is a feasibility constraint, not the account's acceptable loss.
- The universal50%-of-liquidation-distance rule has no supplied derivation. Cross/isolated margin, maintenance tiers, mark prices, funding and other positions matter. A stop submitted after entry is not a guarantee against a fast move or gap.
- Longs slow/shorts fast is an empirical hypothesis, not a universal law. Predetermine any asymmetry and test it separately; mirrored code does not demonstrate profitable short signals.

The HTML contains only two substantial Jesse classes, and even those do not implement all stated rules. Other archetypes lack complete executable configurations. Its claim that all strategies have complete futures lifecycle logic is false.

## 4. Critical SMC availability check

In smc.py, FVG uses `shift(-1)` to place a gap label on its middle candle; that label needs the next candle to finish.
Swing highs/lows use a centered window with future candles. Mitigation/broken indices are determined by later events.
These can be legitimate retrospective annotations. They become look-ahead if treated as known at the historical row where the label is stamped.
Any adaptation must retain separate event time and knowledge/confirmation time, recomputing only from the prefix available at each decision. Delaying one feature is not automatically enough for every output.
Nothing in these patterns alone establishes an institutional liquidity hunt.

## 5. What I recommend doing with the document

1. Keep the current research engine. First unify fees, fill assumptions, daily/trade reconciliation and account adapters; replacing software will not resolve those assumptions by itself.
2. Use Jansen's validation/data chapters selectively as a methods checklist; avoid copying additional overlapping statistical gates without a clear purpose.
3. For the auction project, retain Nautilus as a later sandbox candidate once actual messages/quotes exist. Demonstrate one identical trade/order replay against our current code before broader integration.
4. Use vectorbt only when a bounded preregistered analysis benefits from it. Speed should reduce waiting, not justify thousands of unregistered variants.
5. Keep Qlib, Hummingbot and a broad new strategy-library search out of the current critical path.
6. Do not backtest these nine narratives en masse. Define one complete hypothesis, fix the source/API discrepancies, compare with already-tested families, write evidence/preregistration and use the cheap stop rule.

No framework is installed or connected to brokerage services. No live code is changed. This review makes no trading rank or profitability claim.

## Primary-source register

Selected files inspected in addition to each repository README:
- freqtrade/freqtrade-strategies: user_data/strategies/Supertrend.py; futures/FSupertrendStrategy.py presence verified in tree; AlmgrenChrissStrategy.py; CustomStoplossWithPSAR.py.
- gabrielweich/jesse-strategies: Donchian/__init__.py; DaveLandry/__init__.py.
- je-suis-tm/quant-trading: Dual Thrust backtest.py; Pair trading backtest.py; README's frictionless assumptions.
- joshyattridge/smart-money-concepts: smartmoneyconcepts/smc.py, FVG and swing implementations.
- jesse-ai/jesse: jesse/utils.py; jesse/indicators/supertrend.py; jesse/strategies/Strategy.py.
- polakowo/vectorbt: README and LICENSE.md (Commons Clause).

Repository commit pins and links are in `analysis/outputs/codex_public_repositories_review/source_register.json`.
Branches were inspected read-only and tip pins resolved in the same review; no claim of full codebase audit or installation testing.

