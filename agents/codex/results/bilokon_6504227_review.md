# Strategy-relative regimes: useful qualified method; no trading candidate

Summary: Four-page theoretical on/off control framework, not a strategy, empirical study or profitability result.
Useful idea: define states by a particular strategy's future net PnL and account for switching costs.
The reduced-state proof needs a reward-sufficiency assumption beyond Markov prices; a finite example exposes it.
Utility-optimal binary action need not preserve the future PnL distribution or establish a minimal predictive state.
Retain the qualified method; no regime filter, return test, new data lead, allocation or ES-baseline rescue.

Source: Paul Alexander Bilokon, *Strategy-Relative Market Regimes as Filtration Compressions*, April1,2026,
[SSRN6504227](https://ssrn.com/abstract=6504227), postedApril20,2026. Four pages, read in full.
[Archived upload](../inputs/bilokon_6504227/ssrn-6504227.pdf) ·
[full extracted text](../inputs/bilokon_6504227/full_text.txt).
ReviewedNovember8,2026(America/Los_Angeles). Source's statements are claims to assess, not user instructions.
Scope: [bounded source/math audit](../plans/bilokon_6504227_source_audit.md), commit`3923934f`before
constructed checks. [Audit script](../../../analysis/codex_bilokon_6504227_audit.py) ·
[exact-number/assumption receipt](../../../analysis/outputs/codex_bilokon_6504227/source_audit.json).
Four mathematical fixtures; **zero market-return trials**. No strategy code or independently verified alpha.

## Five paper-review answers

1. **What is it about?** A regime is defined relative to one fixed strategy: a binary active/inactive decision
   based on currently available information. Choose those decisions to maximize expected utility of future
   strategy PnL, less a switching penalty, with a terminal reward. It connects dynamic programming with
   information compression and an alternative information-bottleneck formulation.
2. **What does it find?** It presents a Bellman recursion and conditional optimal-policy existence/uniqueness
   statements. There is **no dataset, fitted predictor, backtest, Sharpe, return, drawdown or cost-calibrated
   empirical result**. The reduced-state claim needs an additional sufficiency assumption as explained below;
   the binary optimal-action interpretation does not prove distribution-preserving or minimal compression.
3. **Why does it make money, if it does?** No money-making result is demonstrated. A filter could help only
   if a causally estimated forecast identifies differences in **future net** strategy value that exceed switching/
   execution/opportunity costs. An optimal decision assuming those forecasts are known does not show that
   we can estimate them reliably. Bounded measurable utility is not itself a dollar-profit objective.
4. **Can we build on it?** Yes, as a qualified research framework: evaluate regime information per strategy,
   preserve information clocks and prior activation/holdings, compare with always-on and simple baselines,
   and penalize switching. It does not diagnose a live regime or explain how to avoid our ES baseline's recent
   losses in advance. Existing price/strategy ledgers make a newly specified study possible; this upload lacks
   the predictor/estimator/validation specification. Do not invent it after examining2025/26losses.
5. **Can a strategy code be made?** **A research gating/decision tool can be coded; the paper does not specify
   a complete trading strategy.** A deployable rule would need a fixed underlying strategy, admissible features,
   interval and available-at clocks, training/update process, conditional payoff/transition estimates, utility,
   switching penalty in consistent units, initial mode, tie/terminal rules and native execution/cash accounting.
   A Bellman solver with supplied model probabilities is not a profitable estimated regime detector.

## What the objective actually does

The source maximizes expected sum of `u(s_t * X_(t+1)) - lambda * 1[s_t != s_(t-1)]`, plus a terminal
reward, whereXis the PnL increment of a **fixed** strategy andsis0/1. The proposed state is current
observableZand previous activation. Given a sufficient state, bounded rewards, exogenous Markov transitions
and finite actions, backward dynamic programming is standard and implementable. No-tie conditions provide
conditional policy uniqueness up to indistinguishability; uniqueness is not predictive accuracy or profitability.

For a state model that really is sufficient, defineD_tas the on-minus-off expected utility plus continuation
value **before** the switching penalty. An inactive strategy turns on whenD_t>lambda; an active strategy
stays on whenD_t>−lambda. This is hysteresis. Our inventedD=.05,lambda=.1example stays off if already
off and stays on if already on. Thus the same forecast can imply different actions depending on prior mode.
This is a mathematical decision example, not a calibrated0.1dollar/percent transaction cost or market result.

The penalty encourages persistence; it does not prove a minimum regime duration, make a noisy forecast
predictive, or guarantee positive financial returns. General bounded measurable utility need not even be
monotone in money. Utility/cost/terminal choices are substantive modeling inputs, absent in numerical form.

## Qualification1: MarkovZdoes not establish a sufficient reward state

Theorem1assumesZis Markov andm_t(z,a)=E[u(aX_(t+1))|Z_t=z]is bounded/measurable. A regular
conditional law givenZ_texists in many settings even when earlier observations still predictX. The allowed
policy can use the entire history. Therefore MarkovZalone does **not** imply its state contains all information
needed to evaluate those history-adapted choices. The proof needs, for example,

`E[u(aX_(t+1)) | allowed history] = m_t(Z_t,a)`

or a correctly augmented sufficient reward state and corresponding Bellman recursion. These assumptions
should be explicit; this is not a criticism of dynamic programming when its state really is closed.

Constructed finite example satisfying the literal listed MarkovZ/bounded reward/terminal assumptions:

- Z0is an equally likely binary observation;Z1=Z2=0deterministically. This is a finite Markov process.
- A fixed strategy hasX1=1andX2=.5ifZ0=1or−.4ifZ0=0. Utility is bounded`clamp(x,-1,1)`;
  switching cost and terminal reward are0. These are invented utility units, not market returns.
- A history-adapted optimal policy is active at time0and active at time1only on the remembered positive branch:
  expected objective **1.25**.
- A feedback policy using only(Z1,previous activation) loses the bit when both branches optimally start active.
  Enumerating all such policies gives best objective **1.05**. Encoding the bit via activation sacrifices earlier
  reward and cannot recover the full-history optimum.

The script exhaustively enumerates the possible policies with exact rational arithmetic. This demonstrates
the missing sufficiency condition under the literal source setup; it does not establish a general impossibility
of useful binary regimes. Independent formal review is pending. Adding the remembered bit toZrestores the
relevant reward information; choosing such a predictive state from real data is the unanswered research task.

## Qualification2: optimal action is not a sufficient future-distribution summary

The objective contains expected utility and switching cost, not a constraint preserving the full conditional
PnL distribution or an explicit minimality optimization. The information-theoretic alternatives insection9are
presented without an equivalence theorem/calibration connecting them to this reward problem.

Our second constructed example uses two equally likely observable states: one givesX=+.5/−.5with
probabilities.7/.3; the other always givesX=.2. Expected clipped-linear utility is+.2in both, so with no
switching cost the unique optimal action is **always on**. Its binary label has0bits of information aboutX,
whereasZcontains1bit because the conditional supports are disjoint. Thus a useful optimal action may discard
distributional information. The source's “minimal predictive state” remark is an interpretation, not a demonstrated
full-distribution sufficiency/minimality theorem.

The separate zero-reward/zero-cost fixture ties both actions, illustrating the importance of the source's explicit
strict-separation uniqueness condition. It is **not** a counterexample to that conditional uniqueness theorem.

## Research and execution use for our repository

- Assess whether a feature forecasts a **specific strategy's** next mature net outcome. Volatility clustering,
  bull/bear labels or past losing periods do not automatically identify a profitable switch.
- Fit forecasts/transition estimates using information and labels available at each fit time. An ex-post label
  built from future PnL cannot be the contemporaneous trading input. No full-sample regime classification.
- Retain an always-on/shadow strategy ledger during off periods to avoid losing counterfactual outcomes.
  The model assumes fixed-strategyX; closing/reopening existing positions can alter the actual future path.
  Either choose flat decision boundaries or replay native positions, orders, costs and state transitions.
- A constant utility switching penalty does not replace dollar commission, bid/ask, slippage, delayed fills,
  margin or open-risk accounting. The prior activation bit alone need not encode actual positions/pending orders.
- Treat any new feature/model/utility/penalty/threshold choice as a new prespecified hypothesis. Existing
  [research controls](../RESEARCH_CONTROLS.md) already require past-only clocks, fitting, multiplicity and
  matched baseline/random-drop/account checks. This source does not waive them or add a new monitor.

Prior context is mixed and must remain strategy-specific. The repository's generic Markov/regime20and
VB/LDFmeta-label studies largely failed in[TIER_LIST.md](../../../TIER_LIST.md); the OvernightTick/VIX
rule has separate positive empirical evidence. Our[unchanged ES baseline](delgado_es_baseline_20261108.md)
weakened in recent history; that observation is not an entry-time regime predictor. The[Harris review](ssrn2810170_review.md)
already retains the distinction between historical significance and future stability. No failed family is revived.

## Decision and all five homes

**DONT TEST as a standalone strategy from this upload; retain qualified methods only.** It lacks a specified
testable forecast/rule, not merely a purchasable dataset. Owned ES/NQ prices are not the binding obstacle.
No further raw-data acquisition, strategy planner or return test is justified by this theory alone. No new
TODOpromising-strategy or DATA_NEEDEDshopping item: those lists are for actual leads, not unspecified models.

|Home|Verdict|
|---|---|
|Personal|No strategy/allocation nominated; no account contribution measured|
|50Kevaluation|No testable rule/account result|
|150Kevaluation|No testable rule/account result|
|50Kfunded|No testable rule/payout evidence|
|150Kfunded|No testable rule/payout evidence|

No BASE/ADD/REPLACE/EMPTY, trade/year/side metrics or simulations: there is no specified strategy to run.
No blanket rejection of all regime methods and no claim synthetic proofs establish financial utility.
The useful findings are retained in[EXECUTION_REFERENCES.md](../EXECUTION_REFERENCES.md).
Tell Claude: review `agents/codex/results/bilokon_6504227_review.md`; useful strategy-relative/cost-aware
regime concept, with a missing state-sufficiency assumption and unproven predictive-compression interpretation;
no empirical profitability or new trading candidate.
