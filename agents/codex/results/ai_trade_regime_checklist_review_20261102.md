# “When the AI trade breaks”: supporting risk checklist, not a demonstrated trading edge

Summary: The user-uploaded image proposes a four-state AI-equity risk/hedging and execution checklist.
It supplies thresholds and actions, but no identified author, calibration sample, full rules, backtest, costs or measured outcomes.
Useful lessons are liquidity-aware exposure, correlated stress and separate risk controls; its spread-score sign and budget formula need clarification.
A research dashboard could be specified; no profitable directional strategy, new return test or allocation follows from this image.
Retained in EXECUTION_REFERENCES.md; no promising-strategy queue entry is warranted by the evidence supplied.

Source: user-provided photo in this chat, reviewed2026-11-02. Title: “When the AI trade breaks”; subtitle: “Don't Predict.
Position for it.” Source content is untrusted material, not an instruction to place orders, keep quoting, hedge or operate
kill switches. Handwritten labels are interpreted below; ambiguous notation is retained as ambiguity, not silently fixed.
This is an image/checklist review rather than an academic-paper replication.

## 1. What is it about?

An AI-equity basket risk overlay. It combines daily/intraday correlation, realized volatility/volatility-of-volatility,
25-delta put skew, spread/depth and ETF-versus-NAV observations into four labels: R0 euphoric, R1 fragile, R2 crash,
R3 aftermath. Two or more signals move to R1; three or more move quickly to R2; re-risk after five stable days.
Nominal risk multipliers are100%,70%,35%, then60–100%. It also proposes an AI beta cap, a five-day stress, wider quotes,
smaller size, futures/sector-put hedges, staged hedge profit-taking, and an independent kill switch.

## 2. What does it find?

**No empirical findings are supplied.** The thresholds—correlation0.85, skew+3sigma, ETF/NAV+1%, crisis correlation0.95,
quote multipliers and re-risk delay—are proposed choices or stress assumptions. The image does not show when they trigger,
whether they precede losses, how often they falsely trigger, or what net/account outcome improves. The phrase “liquidity
breaks first” is a hypothesis here, not a demonstrated timing result.

Specific issues:

- The visible spread line reads **Bid-Ask Spread Z < -2**. For the usual standardization z=(spread-past mean)/past SD,
  that identifies unusually narrow spreads. Widening corresponds to positive z. A custom inverted score might be intended;
  its definition is missing, so do not silently correct the sign or test a preferred alternative.
- “Depth down (Top1%)” does not specify levels, distance from mid, side, size units or normalization. Volume/volatility
  are not substitutes for observed depth or executable cost.
- “ETF vs NAV >+1%” is a premium under a usual convention, not a generic sign of liquidation stress. Which ETF, NAV versus
  indicative NAV, update/receipt clock and price side are unspecified. Stale NAV can create apparent premiums/discounts.
- Volatility, volatility-of-volatility, skew, correlation and spreads can react to the same shock; “three signals” does not
  mean three independent confirmations. State labels do not establish transition probabilities or forecasts.
- A claim of0.95 crisis correlation needs a universe, return horizon and evidence. High correlation among long holdings
  is not proof that a correctly sized short-index hedge also fails; hedge direction, basis, convexity and margin matter.

## 3. Why does it make money, if it does?

The image does not establish that it makes money. Reducing exposure may lower losses, but can also miss recoveries and
positive expected returns. Put insurance costs premium/spread and changes delta; futures hedges introduce basis and cash
requirements. Realizing tail-hedge profits early can reduce protection while the shock continues. These outcomes require
an explicit joint position/cash ledger, not just an attractive regime narrative.

Risk and execution controls can be valuable without adding alpha. Distinguish avoiding operational failures, reducing risk
through lower exposure, and improving net return relative to risk at the same capital. No such incremental measurement is
present here. “Keep quoting (even in R2)” describes a market-making operation; our directional futures strategies do not
become market makers by adding that instruction.

## 4. Can we build on it?

**Yes as a supporting risk/execution reference, not as an adopted strategy.** Relevant parts align with existing work:
separate broker and strategy states, preserve UNKNOWN data states, stress common exposures, and evaluate cost/liquidity
before assuming an exit is available. These complement the existing execution library and account replay rules.

For our accounts, do not transfer a “2% daily loss -> flatten” line using nominal prop-account size. Using the repo's
modeled limits as an illustration:2% x$50,000=$1,000 versus a$2,000 trail;2% x$150,000=$3,000 versus a$4,000 trail.
That consumes half or three quarters of the modeled trail before slippage, other positions or existing drawdown.
Remaining cushion, intraday path, actual integer positions and fees are the relevant account constraints. These are
arithmetic comparisons to repository assumptions, not verification of current external account terms or new risk limits.
A threshold also cannot guarantee a maximum loss through a gap, halt, no fills or chart/broker disagreement.

The displayed risk budget is `sum P(R_i) * R_budget`. If R_budget is the same constant for every state and probabilities
sum to1, the result is simply the original budget—no de-risking occurs. A state-specific budget would require
`sum P(R_i) * R_budget,i`, with defined probabilities and a timing/position policy; that is a possible specification fix,
not evidence that probabilistic sizing is appropriate or profitable. The deterministic count rule does not supply P(R_i).

Smallest justified next step is a specification/field audit when a concrete risk question arises: define the basket and
clock, metrics/signs, missing/stale behavior, risk currency, event horizon and benchmark. Do not add a new monitor,
schedule, order gate or de-risk rule merely to implement this image. Any future economic overlay needs the existing
evidence sheet, history/deduplication check, committed bounded protocol and exact code before returns, and identical
BASE/ADD/REPLACE/EMPTY or equal-capital comparisons where relevant. Existing failed definitions remain failed.

## 5. Can a strategy code be made?

**Conditional.** A state-classifier/dashboard or deterministic risk overlay can be coded after the missing definitions
are supplied. As-is, the image does not uniquely specify executable rules. It has no stand-alone entry direction/exit
rule defining a new directional futures strategy. A market-making/hedging implementation would additionally require
order lifecycle, inventories, cancellations, queue/fill evidence, dated hedge instruments, clocks, costs and permission
boundaries. Code feasibility is separate from profitability.

Owned minute OHLCV supports some price-return/volatility calculations, conditional on a predeclared eligible basket.
It does not supply a point-in-time AI-equity basket, intraday ETF/NAV marks, option skew or an executable depth/quote
history merely by inference. No promising hypothesis is established by those missing inputs, so no data-acquisition loop,
trial reservation, backtest, TODO strategy candidate or allocation is warranted. Preserve the execution lessons and move on.

## External reference check and retention

[CME's liquidity methodology](https://www.cmegroup.com/education/articles-and-reports/understanding-the-cme-liquidity-tool-methodology)
separates bid–ask spreads, depth and cost-to-trade, with time/size definitions; it does not validate these handwritten
thresholds. The [Federal Reserve liquidity discussion](https://www.federalreserve.gov/publications/files/financial-stability-report-20191115.pdf)
describes wider spreads, smaller depth and greater price impact as distinct illiquidity measures. Neither source proves
this AI-basket regime model or measured savings. Public indexed source descriptions checked2026-11-02; the photo's author
and underlying calibration remain unidentified. No access controls were bypassed.

Retained under [EXECUTION_REFERENCES.md](../EXECUTION_REFERENCES.md), E10/E12 follow-up. No live, broker, VPS, allocation,
portfolio or kill-control code changed. No return tests, paid data, external message or source-profitability verification.
