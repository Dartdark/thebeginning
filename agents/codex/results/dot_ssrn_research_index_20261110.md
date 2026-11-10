# dot: SSRN research index
Author: dot. Updated 2026-11-10. Research continues to the agreed deadline; this is an interim index.

## What is worth pursuing first
1. Commodity curve research: Basis Momentum, Relative Basis, and curve-aware momentum. Strong foundations, but later implementations show weaker and regime-sensitive returns; native-contract data and modern validation remain gates.
2. Publication-lag-aware commercial-position changes: A Tale of Two Premiums. Distinct from the failed gold-only crowding screen, but broad data, costs and a clean holdout remain missing.
3. Pre-refunding Treasury timing: a small calendar overlay hypothesis, not a standalone Sharpe-4 strategy.
4. Intraday factor-zoo SPY forecasting: stronger OOS design, but requires a separate equity-factor data pipeline and an explicitly flat-overnight adaptation if that is the goal.

No fresh strategy has been shown here to improve the existing portfolio or account survival. No return tests were run. “Intraday” below means holding-time fit or a labeled adaptation, not a blanket certification of Apex eligibility. Existing-data status never follows from ticker names alone.

5. Business-cycle FX sorting with real-time macro vintages: stronger timing discipline than most public-macro candidates, still requiring broad licensed forward data and current validation.
6. Same-day EUR/USD session flows: a transparent low-input intraday hypothesis, with old institutional spot evidence rather than proven 6E results.

## Reports
- [Original ten](https://github.com/Dartdark/thebeginning/blob/codex/work/agents/codex/results/dot_ssrn_ten_papers_20261110.md)
- [Five provisional intraday reserves](https://github.com/Dartdark/thebeginning/blob/codex/work/agents/codex/results/dot_ssrn_intraday_slots_20261110.md)
- [Five existing-data baseline audits](https://github.com/Dartdark/thebeginning/blob/codex/work/agents/codex/results/dot_ssrn_existing_data_audit_20261110.md)
- [Pass 2: Treasury, semivariance and FX policy](https://github.com/Dartdark/thebeginning/blob/codex/work/agents/codex/results/dot_ssrn_continuation_pass2_20261110.md)
- [Pass 3: COT, expiration and volatility-overlay evidence](https://github.com/Dartdark/thebeginning/blob/codex/work/agents/codex/results/dot_ssrn_continuation_pass3_20261110.md)
- [Pass 4: EIA, jump, LEI, MOM–TOM and factor prediction](https://github.com/Dartdark/thebeginning/blob/codex/work/agents/codex/results/dot_ssrn_continuation_pass4_20261110.md)
- [Pass 5: volume risk, trade networks, search and climate](https://github.com/Dartdark/thebeginning/blob/codex/work/agents/codex/results/dot_ssrn_continuation_pass5_20261110.md)

- [Pass 6: speculative pressure, FX sessions and macro/VRP evidence](https://github.com/Dartdark/thebeginning/blob/codex/work/agents/codex/results/dot_ssrn_continuation_pass6_20261110.md)

- [6E actual-row feasibility audit for paper 38](https://github.com/Dartdark/thebeginning/blob/codex/work/agents/codex/results/dot_ssrn_6e_data_feasibility_20261110.md)

- [Independent commodity/FX validation and version audit](https://github.com/Dartdark/thebeginning/blob/codex/work/agents/codex/results/dot_ssrn_validation_audit_20261110.md)
- [Native-contract data sources, coverage and license audit](https://github.com/Dartdark/thebeginning/blob/codex/work/agents/codex/results/dot_ssrn_curve_data_feasibility_20261110.md)

- [Pass 7: Treasury month-end and naphtha relative value](https://github.com/Dartdark/thebeginning/blob/codex/work/agents/codex/results/dot_ssrn_continuation_pass7_20261110.md)

## Classified inventory
The count is research entries, not qualified strategies. Papers 11–15 are provisional reserves; 16–20 audit already-tested or blocked baselines, not five new successful ideas. See each linked report for the exact evidence status, source version, rules, costs and missing inputs.

| # | SSRN | Paper / mechanism | Primary category | Intraday / no-overnight status | Current-data status | Decision |
|---|---|---|---|---|---|---|
| 1 | [2587784](https://ssrn.com/abstract=2587784) | Basis Momentum | Personal | No | No: native curves | Priority data/modern-validation gate |
| 2 | [3404561](https://ssrn.com/abstract=3404561) | Relative Basis | Personal | No | No: three maturities | Priority data gate |
| 3 | [1343809](https://ssrn.com/abstract=1343809) | Anatomy of Commodity Futures Risk Premia | Personal | No | No: curves | Foundation |
| 4 | [996930](https://ssrn.com/abstract=996930) | Fundamentals of Commodity Futures Returns | Personal | No | No: broad universe | Foundation / known family |
| 5 | [2485314](https://ssrn.com/abstract=2485314) | Exploiting Commodity Momentum Along Futures Curves | Personal | No | No: maturity panel | Priority data gate |
| 6 | [3749061](https://ssrn.com/abstract=3749061) | Exploiting the Dynamics of Commodity Futures Curves | Personal | No | No: four maturities | Conditional; turnover |
| 7 | [2089463](https://ssrn.com/abstract=2089463) | Time Series Momentum | Personal | No | Subset adaptation only | Known trend family |
| 8 | [2174501](https://ssrn.com/abstract=2174501) | Value and Momentum Everywhere | Personal | No | No: cross-asset inputs | Foundation |
| 9 | [2298565](https://ssrn.com/abstract=2298565) | Carry | Personal | No | No: native carry inputs | Foundation |
| 10 | [2659431](https://ssrn.com/abstract=2659431) | Volatility-Managed Portfolios | Risk overlay | Not an entry rule | Adaptation only | Qualified by 26–27 |
| 11 | [7546200](https://ssrn.com/abstract=7546200) | Harvesting the Value Area | Intraday reserve | Source-gated | No: tape/profile details | Full-source gate |
| 12 | [3553682](https://ssrn.com/abstract=3553682) | Intraday Momentum in Crude Oil | Intraday ETF | Futures adaptation only | Native USO missing | Conditional/source incomplete |
| 13 | [5037563](https://ssrn.com/abstract=5037563) | Intraday Brent Seasonality | Intraday reserve | Unverified | No: ICE data | Embargo/source gate |
| 14 | [885686](https://ssrn.com/abstract=885686) | CME FX Intraday Reversals | Intraday reserve | Potential timing fit | Exact replication unverified | Old/source incomplete |
| 15 | [7155458](https://ssrn.com/abstract=7155458) | KDE Volume Nodes | Intraday reserve | Source-gated | No: level-one inputs | Not net strategy evidence |
| 16 | [2440866](https://ssrn.com/abstract=2440866) | Market Intraday Momentum | Intraday baseline | Timing fit only | Existing adaptation tested | Failed baseline |
| 17 | [2730304](https://ssrn.com/abstract=2730304) | Overnight-Intraday Reversal Everywhere | Intraday baseline | Timing fit only | Existing adaptation tested | Failed baseline |
| 18 | [4192163](https://ssrn.com/abstract=4192163) | Tale of One Day | Intraday baseline | Adaptation only | Existing adaptation tested | Failed stock-to-futures proxy |
| 19 | [3829582](https://ssrn.com/abstract=3829582) | Market Sentiment / Overnight Anomaly | Personal overnight | No | Existing adaptation tested | Failed / source input gaps |
| 20 | [7124578](https://ssrn.com/abstract=7124578) | Opening Range Reversal Dow | Intraday baseline | Timing fit only | Adaptation tested, exact rules blocked | Failed / source gate |
| 21 | [4764295](https://ssrn.com/abstract=4764295) | Pre-Refunding Treasury Gains | Personal / calendar | Separate adaptation | Event calendar and pricing unverified | Conditional; annualization caution |
| 22 | [3584014](https://ssrn.com/abstract=3584014) | Semivariance Momentum and Reversal | Personal | No | US adaptation only | Conditional; universe/OOS gaps |
| 23 | [4371901](https://ssrn.com/abstract=4371901) | Carry Activity and Monetary Policy | Personal | No | No: forwards/surprises | Conditional |
| 24 | [2449315](https://ssrn.com/abstract=2449315) | A Tale of Two Premiums | Personal | No | No: broad COT/price match | Priority source/data audit |
| 25 | [4562800](https://ssrn.com/abstract=4562800) | Third Friday Price Spike | Existing EOS support | Short-leg adaptation | Existing timing family; exact source no | Duplicate mechanism |
| 26 | [3357038](https://ssrn.com/abstract=3357038) | Performance of Volatility-Managed Portfolios | Risk-method audit | Not an entry rule | No: equity factors | Counterevidence |
| 27 | [3982504](https://ssrn.com/abstract=3982504) | Multifactor Volatility-Managed Portfolios | Portfolio method | No | No: holdings/netting | Conditional method |
| 28 | [3822093](https://ssrn.com/abstract=3822093) | EIA Intraday Return Predictability | Intraday ETF | CL adaptation only | No native USO verified | Weak gross / Sharpe caution |
| 29 | [2903629](https://ssrn.com/abstract=2903629) | Following Asset Price Jumps | FX hypothesis | Bar horizon not sufficient | ES/CL evidence negative | Reject ES/CL |
| 30 | [1108050](https://ssrn.com/abstract=1108050) | Investor Inattention and LEI | Personal | No | No: vintage signal | Conditional / ex-post design |
| 31 | [2515900](https://ssrn.com/abstract=2515900) | MOM–TOM Effect | Personal / source audit | Not original implementation | Subset adaptation different | Known family; calendar mismatch |
| 32 | [4388560](https://ssrn.com/abstract=4388560) | Intraday Factor-Zoo Prediction | Personal equity | Overnight removal changes design | No: 272 factors | Strong research; data-gated |
| 33 | [5795584](https://ssrn.com/abstract=5795584) | Volume-Driven Intraday Volatility | Risk overlay | RTH adaptation only | Partial; full sessions unverified | Forecast evidence, no trading costs |
| 34 | [4534287](https://ssrn.com/abstract=4534287) | Trade Network and Currency Returns | Personal | No | No: trade/FX panels | Conditional; vintage gate |
| 35 | [3411117](https://ssrn.com/abstract=3411117) | Fear of Hazards | Personal | No | No: vintage searches | Conditional; hindsight vocabulary |
| 36 | [7395858](https://ssrn.com/abstract=7395858) | El Niño and Currency Returns | Personal | No | No: vintage climate/FX | Conditional; version/timing gate |
| 37 | [3279425](https://ssrn.com/abstract=3279425) | Speculative Pressure | Personal | No | No: broad COT/price panel | Conditional; timing/cost gates |
| 38 | [2099321](https://ssrn.com/abstract=2099321) | Intraday FX Session Flows | Intraday hypothesis | US leg same-day Pacific; 6E adaptation | Dec2017 endpoints verified; later years/roll/fills pending | Conditional; old net spot evidence |
| 39 | [948309](https://ssrn.com/abstract=948309) | Variance Risk Premium Forecasting | Personal | No | Cash variance unavailable | Deprioritize |
| 40 | [3929119](https://ssrn.com/abstract=3929119) | Equity Prediction Reassessment | Evidence audit | Not an entry rule | Not a strategy replication | Independent VRP counterevidence |
| 41 | [2906600](https://ssrn.com/abstract=2906600) | Business Cycles and Currency Returns | Personal | No | No: vintages/forwards | Priority causal-data audit |
| 42 | [3440417](https://ssrn.com/abstract=3440417) | End-of-Month Treasury Returns | Personal | No: multi-day | Calendar simple; Treasury coverage/roll unverified | Conditional calendar lead |
| 43 | [5034739](https://ssrn.com/abstract=5034739) | Naphtha Crack Mean Reversion | Personal | No: multi-day | No: ICE/OTC executable prices | Access/execution gate |

## Guardrails for any later build
Source fidelity first; causal release timestamps and fills; realistic spread, commissions and rolls; complete sessions and contract identifiers; frozen holdout; portfolio overlap and loss-limit effects. Existing test failures are not erased by finding a similarly titled paper. Source discrepancies are documented without reopening paused experiments.
