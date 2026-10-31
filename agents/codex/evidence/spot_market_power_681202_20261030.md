# Spot market power, SSRN 681202: DON'T TEST

Summary: the uploaded March 2005 paper provides theoretical equilibria, not an empirical outsider strategy.
Modeled profits rely on supply control or belief-driven price impact across two derivative stages.
Our owned bars, aggregate COT and order-flow records do not identify the necessary actor-specific states.
No directional event, entry clock, bounded exit, gross-versus-cost estimate or power census can be specified from it.
Keep the market-structure lesson; do not invent an OHLCV strategy or revive earlier hedging-pressure tests.

Source: Muermann and Shore, *Spot Market Power and Futures Market Trading*, supplied 36-page PDF.
[Full review](../results/spot_market_power_681202_20261030.md).
Return trials: **0**, including proxy, parameter, gross screen and account trials.

1. **Participant/force:** a physical monopolist optimizes its supply after taking a derivative position. This is discretion
   and endogenous incentives, not an exogenously scheduled forced order we can identify beforehand. Section 4 also
   describes a separate non-producer benefiting through price-moving intermediate trades and an earlier contract.
2. **Side/size/clock:** concealed producer positions randomize long/short. No usable observed size, real calendar clock,
   publication/receipt delay, event count, contract volume comparison or outsider decision rule is supplied.
3. **Contract transmission:** the commodity spot/futures link is modeled directly. Transmission to a current NQ/ES
   signal or a particular executable CL/MCL event is not established. Contract-stage payoffs in Section 4 matter.
4. **Data:** inventory inspected owned continuous NQ/ES/CL/GC OHLCV, `data/cot/deacot*.zip`, financial COT archives and
   existing order-flow intake. These are not timestamped identified-producer positions, production decisions, market-maker
   beliefs or a calibrated demand slope. No exact empirical input is offered by the source, so no acquisition was attempted.
5. **Costs/gap:** no measurable gross opportunity, spread/slippage saving, independent intraday slot or native-micro cost
   bridge. Simulation with guessed supply elasticity or order sizes would illustrate assumptions rather than test edge.
6. **Power:** no defined observable event universe, effective sample, per-trade variation or estimated after-cost mean.
   Power is unavailable, not zero; no invented opportunity count or t-statistic.
7. **Prior work/falsifiers:** exact SSRN/title/author search found no duplicate. Existing CL/GC hedging-pressure rejection
   concerns a different aggregate COT rule. Full position observability, storage arbitrage, weak physical supply control,
   changed price schedules or non-identifiable participant states can remove the proposed inference.
8. **Failure/diversification:** our marketable/passive role and common losses cannot be measured without a rule.
   Short-run price impact, missing intermediate exposure and market-maker repricing could reverse the assumed gain.
   No stop, time exit, concurrent exposure cap, offset-before-breach or diversification benefit has been established.

Decision: **DON'T TEST as a current portfolio candidate**. This is source/feasibility work only. If a separately justified
observable event emerges later, first establish its information clock and actor identification with no return calculation.
