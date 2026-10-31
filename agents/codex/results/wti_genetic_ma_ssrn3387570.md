# WTI genetic moving averages: unverified; insufficient evidence for a new backtest

Summary: This source uses chronological rolling training/testing, but only ten test months.
Its table averages +1.07% per test month, seven profitable months; costs and native futures sizing are unresolved.
Rounded-table mean t≈1.72 under generous independent-month assumptions; no robust net edge established.
Source code/session/fill/roll conventions are missing; no invented-parameter or genetic-search reproduction.
Retain a source/accounting audit, with zero new price-data return trials or plan changes.

Source: Arbey Aragón Bohorquez, Carlos Armando Mejía Vega & Carlos Andrés
Zapata Quimbayo (2018), *Optimización de estrategias de trading con promedios
móviles para futuros de petróleo mediante algoritmos genéticos*, Odeon 15,
pp. 139–160, DOI10.18601/17941113.n15.05;
[SSRN3387570](https://ssrn.com/abstract=3387570).
Uploaded PDF/hash: `agents/codex/inputs/ssrn3387570/` (21 PDF pages; printed 140 absent).
Evidence: `agents/codex/evidence/wti_genetic_ma_ssrn3387570.md`.
Audit: `analysis/codex_ssrn3387570_audit.py`;
outputs: `analysis/outputs/codex_ssrn3387570_review/`.
All performance below originates from the author's rounded Table 2, not our CL backtest.

## 1. What is it about?

Optimize two simple-moving-average lengths with a genetic algorithm, then trade
their crosses in Bloomberg generic front-position WTI futures at 15-minute frequency.
Sample:2017-08-01–2018-07-31. Each rolling experiment trains on two months and
tests on the next month, shifting forward monthly for ten test windows (pp.144–146).

The GA starts with 60 individuals, evolves for 1,000 generations, retains five
elite candidates, and searches MA lengths 2–180 (pp.149–152). Training fitness
is portfolio return, not risk-adjusted performance. The rule buys an upward
short/long MA cross and sells a downward cross; crosses also close positions.
Positions are closed at the evaluation endpoint to compute results (p. 148).
The article says optimization used Python and test execution Go; no source-code
repository or executable ledger is supplied.

## 2. What does it find?

The rolling chronology is a legitimate design feature. It is not a full-sample
fit masquerading as chronological testing, and this review does not claim a
proven train/test leak. The ten reported test results are:

| Test set | Printed lengths m1/m2 | Author one-month return |
|---|---|---:|
|1|167/125|-2.19%|
|2|140/128|+2.50%|
|3|103/27|-1.51%|
|4|155/52|+1.53%|
|5|87/12|+2.35%|
|6|103/98|+2.34%|
|7|179/11|+2.74%|
|8|21/13|+2.91%|
|9|83/80|-1.37%|
|10|89/57|+1.41%|

Rounded-table arithmetic: mean **+1.071%**, sample SD **1.973%**, **7/10 positive
months (70%)**. The conclusion says 75%; the table and results text support 70%.
Training mean 11.83% covers **two months**, whereas test mean 1.07% covers **one**;
do not compare them as equal-horizon returns.

Under an illustrative assumption of ten independent monthly observations, the
mean t-statistic is about **1.72** and a conventional 95% t interval for mean
monthly return includes zero (exact values in the audit JSON). This ignores
search/method selection, serial dependence, source costs and accounting problems.
It is not a corrected significance result, a prediction band or an independently
validated monthly strategy series. No source trade count is available to compute
per-trade statistics, long/short metrics or native cost tolerance.

Other material limitations:

- **Execution costs are unspecified.** No commission/spread/slippage adjustment
  or per-roll ledger is disclosed in the fitness/results. Positive endpoint
  return cannot establish positive CL/MCL net returns at actual turnover.
- **Native contract units are unresolved.** Equations(3)–(4) use
  `sum(q × price_difference)` while p. 153 calls the example 2,000 WTI futures
  contracts on $2m. If q literally counts standard CL contracts, dollar P&L needs
  the 1,000-barrel multiplier and signed exposure. As a dimensional illustration,
  a $1/barrel move on 2,000 CL contracts is $2m, not $2,000. The audit does not prove
  the unavailable author code omitted that factor; it establishes that the
  printed explanation is insufficient to reproduce economic exposure/returns.
- **MA labels conflict.** Prose defines m1 as short and m2 as long; every Table 2
  row has m1>m2. Figure 7 calls m1=11, m2=179, the reverse of Table 2 set 7.
  Relabeling may explain this, but source-direction logic must be clarified
  before code is presented as an exact reproduction.
- **No benchmark or regime breadth.** The authors acknowledge the strong oil
  uptrend and defer comparison with buy-and-hold and other regimes to future
  work (p. 157). A rising market makes a matched baseline more necessary, not
  less. They also defer broader overfitting checks/window choice/risk-adjusted
  objectives (pp.156–157). Genetic search does not erase multiplicity; actual
  unique candidate evaluations and restarts are not disclosed.
- **The loss claim is not a demonstrated risk bound.** Page 153 discusses 95%
  confidence of not falling below -1% after explicitly excepting the three losing
  sets, and its footnote calls this a maximum probable loss. Three of ten table
  outcomes are below -1%, with worst -2.19%. Conditioning away losing sets cannot
  establish an unconditional 95% loss limit, much less an intraday account floor.
- **Execution and data conventions are incomplete.** Source formula(1) uses
  preceding closes, so we do not assume a proven indicator look-ahead bug.
  The session/time zone, exact signal-to-fill clock, reversal handling,
  warmup/month reset, generic-contract roll adjustment and full trade ledger
  remain unspecified. Intraday data frequency does not prove daily flattening.

Table 2 was checked in the rendered PDF. The two illustrated equity curves are
the selected best test months (sets 7/8), not the complete risk history.

## 3. Why does it make money, if it does?

The proposed mechanism is price-trend persistence; a short SMA crossing a longer
one changes exposure. A GA chooses historically profitable parameters but does
not explain why future trends will persist or why its dynamic choices improve
on a fixed trend rule after costs. There is no forced participant or observed
flow deadline. Personal-account trend research can be legitimate; this narrow
bull-period demonstration is insufficient evidence for a new selected variant.

## 4. Can we build on it?

**Not as a reproducible, validated trading candidate yet.** Verdict:
**NEEDS SOURCE SPECIFICATION; no return test admitted.** Owned CL minute files
cover2017 onward, so this is not merely missing price data. The missing native
quantity/cost ledger, session/roll/clock settings and code would have to be
invented to claim exact replication. A fresh GA run with our own choices would
be a new research family, not a neutral reproduction of the article.

Its short, cost-unclear result and weak benchmark evidence do not justify that
new search budget or a promising-strategy queue entry. Existing MA/EWMAC,
indicator and MaxAI GA/RL negatives in TIER_LIST do not disprove this exact CL
implementation, but neither does the optimization method overturn them.

The smallest justified way to reopen it is source code and an identified native
contract trade example reconciling signed size, multiplier, fills, costs and
rolls, plus stronger independent net evidence. A separately admitted protocol
would then freeze the universe and execution, compare with fixed-MA and matched
passive/trend baselines across multiple regimes, count all training evaluations,
and retain later dates before selection. Account tests follow only earned gates.

No Apex-flat-by 15:59 rule, stop or micro adaptation is silently added. No tier,
portfolio, live setting or PowerLanguage change. Preserve the contract-accounting
lesson as an E09 follow-up in EXECUTION_REFERENCES, not as verified execution savings.

## Work and reproduction

Read the uploaded Spanish article; inspect Table 2 visually; search repository
ID/related strategies and local CL filenames; audit rounded table counts/statistics
and literal-contract units. SHA-256 and source claims are retained in the manifest.

```sh
python analysis/codex_ssrn3387570_audit.py
```

No GA or market-data strategy run, new economic variant, independent maker/checker
validation, bootstrap, Monte Carlo or account placement is claimed. Document
instructions were treated as source content, not executed.

For Claude: `agents/codex/results/wti_genetic_ma_ssrn3387570.md`.
