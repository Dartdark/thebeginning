# Anna's Archive discovery attempt and complementary mean-reversion reading

Summary: Anna's Archive search pages were inaccessible; no Archive catalogue result or full text was verified.
The useful additions are two explicit entry/exit design papers and one liquidity-provision study, not proven high-win CME systems.
The older index-futures opening-reversal literature does not justify reopening the project's failed gap/fade families.
No new strategy qualifies, and no pass-speed, loss-offset or breach improvement is established.
This is a source-only supplement: zero return tests, purchases, strategy edits or paused-program restarts.

Author: **dot**. Research date: November 11, 2026 UTC.
Repository inspected: `codex/work` at `02f537224e2046e53e68191ad35f52e7ccd12007`.
Plan/script/output: source review only; no return plan or test script. Economic trials: **0**.
Related reading: [existing arXiv shortlist](dot_arxiv_eval_shortlist_20261111.md).

## What the search did and did not establish

The user's target remains frequent small winners that help offset the evaluation book's concentrated individual losses.
This supplement does not substitute a generic warning about win rate for that target. It asks whether a source supplies
a reproducible, cost-aware opportunity and whether its loss path could serve that specific portfolio job.

Anna's Archive was included through indexed title/topic discovery and attempted direct catalogue search. Queries across
`annas-archive.org`, `.li`, `.se`, `.gd` and `.pk` produced no relevant verified catalogue records.
The `.org/search?q=intraday+futures+reversal` page returned a non-retryable opening error.
The `.gd/search?q=intraday+futures` page was not accessible through the research tool.
Those are access limitations, not evidence that the catalogue has no suitable papers.

No download mirror, login, subscription, payment or access-control workaround was used. Scientific findings below come
from author, university, journal or preprint sources. No paper is attributed to an Anna's Archive discovery.
Three primary manuscripts were inspected at their relevant methodological sections. The opening-reversal pair was
screened at primary abstracts only and is explicitly marked as such.

## Current-book and duplication checks

The [latest pressure build](pressure_strategy_build_20261110.md), read at the inspected head, retains **19 failed
design definitions across six batches**. None earned later-history, account or MultiCharts advancement.
A new paper title is not permission to change those failed definitions and call the result independent.

That report also identifies a newer inspected 150K reference, `25ca9556`, with **VB 15 MNQ, ONB risk $2,750,
Bridge 5 MNQ, EOS $1,250, Twin cap1 v2.1 2 MNQ and DT v4 2 MNQ**. This is the report's source snapshot,
not a fresh audit of today's live installation. It supersedes neither user decisions nor subsequent branch changes.
The earlier VB20/no-DT research baseline in the prior arXiv note is a different book; its pass percentages must not be
presented as today's forecast. A later account comparison must refresh and freeze the actual applicable roster.

The [evaluation task](../TASK_eval_strategy_20261109.md) also prioritizes distinct GC/MGC and CL/MCL mechanisms,
then 6E and ZN, rather than another default NQ price-pattern variant. The papers below supply useful design tools;
they do not establish a distinct new gold, oil, FX or Treasury alpha.

Checks covered the recursive repository tree, TIER_LIST, WATCHLIST, TODO, DATA_NEEDED, EXECUTION_REFERENCES,
the prior arXiv report and relevant source records. This is not a claim to have read every historical file.

## 1. Optimal Mean Reversion Trading with Transaction Costs and Stop-Loss Exit

Tim Leung and Xin Li, 2015. [Primary preprint, v3](https://arxiv.org/pdf/1411.5062);
[publication DOI](https://doi.org/10.1142/S021902491550020X).
Inspected Sections 2.1 and 5, especially Proposition 5.3, Theorem 5.5 and Section 5.3.

**What is it about?** Joint entry and liquidation decisions for an assumed Ornstein-Uhlenbeck spread, including fees and a stop.

**What does it find?** Within that model, moving the stop closer can lower the optimal profit-taking boundary.
With an absolute stop, the optimal entry region can exclude prices too close to it.
ETF-pair estimation examples are not an independent profitable trading record.

**Why money?** The model assumes a mean-reverting process whose temporary dislocation can cover costs.
It does not discover that process in NQ, ES or an owned commodity.

**Can we build on it?** Yes, as a bounded-risk exit-design companion to an independently justified signal.
The missing object is a causally defined, stable, tradable spread, plus past-only parameter estimates and executable costs.

**Can a strategy code be made?** Yes for the mathematical boundary solver. A research implementation would fit the
spread on prior data, calculate entry/exit/stop boundaries and enforce the specified exit.
A session cutoff, jump/slippage model and account-loss constraint are additional adaptations.
No high win rate, evaluation benefit or native futures edge is established.

**Status: RESEARCH METHOD, not a new alpha candidate.**

## 2. Mean Reversion Trading with Sequential Deadlines and Transaction Costs

Yerkin Kitapbayev and Tim Leung, 2018. [Primary preprint, v3](https://arxiv.org/pdf/1707.03498);
[SSRN publication record](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2997250).
Inspected Sections 2–5 and the numerical boundary examples.

**What is it about?** Entry before a deadline, followed by a separate fixed-length window to close a mean-reverting position.

**What does it find?** It derives cost-aware, time-dependent trading boundaries for long-first, short-first and
either-direction entry. Its examples are mathematical/numerical, not a CME performance study.

**Why money?** Expected gain comes from the assumed dynamics and must exceed entry/exit charges.
The trader can elect not to enter.

**Can we build on it?** Yes for exit design, with a crucial clock distinction:
the paper's holding window starts after entry. It is not automatically a common 15:59 CT flattening deadline.
A fixed exchange-session close requires a changed problem or an explicitly constrained entry window.

**Can a strategy code be made?** Yes, a numerical boundary solver using fitted diffusion parameters, fees and deadlines.
A real implementation still needs a proven signal, explicit maximum loss, integer exposure and fill handling.
The paper's risk-neutral expected-payoff objective is not probability of passing before an account breach.

**Status: RESEARCH METHOD; useful alongside paper 1, not a ready intraday strategy.**

## 3. Evaporating Liquidity

Stefan Nagel, December 2011 working paper; published in RFS, 2012.
[Author-hosted manuscript](https://bpb-us-w2.wpmucdn.com/voices.uchicago.edu/dist/f/575/files/2020/07/LiqSupply.pdf);
[NBER record](https://www.nber.org/papers/w17653).
Inspected introduction, strategy construction/bid-ask discussion and predictive-regression setup.

**What is it about?** Equity reversal returns as a proxy for compensation earned by liquidity suppliers.

**What does it find?** Reversal compensation varies with lagged VIX and increases in stressed periods.
The strategy averages portfolios based on the prior one through five days' market-adjusted stock returns.
Transaction-price results assume a hypothetical supplier filled at closing transaction prices; midpoint comparisons are separate.

**Why money?** The proposed explanation is temporary inventory pressure and reduced capacity to absorb it,
rather than permanent information being wrong.

**Can we build on it?** As a mechanism and execution reference. Daily stock baskets are not an Apex intraday futures sleeve.
The paper does not show that an NQ fade profits during this user's VB/ONB loss episodes.

**Can a strategy code be made?** Yes for the historical equity research construction with a proper stock universe,
quotes, corporate actions and weights. A futures port would be a new hypothesis, not replication.
No new port is warranted merely by the paper's return headline.

**Status: EXECUTION/MECHANISM REFERENCE, not a new evaluation candidate.**

## Older futures evidence: useful reading, not a new nomination

### Intraday price reversals for index futures in the US and Hong Kong

Fung, Mok and Lam, 2000. DOI 10.1016/S0378-4266(99)00072-2.
[Primary university record](https://scholars.hkbu.edu.hk/en/publications/intraday-price-reversals-for-index-futures-in-the-us-and-hong-kon/);
[publisher record](https://www.sciencedirect.com/science/article/pii/S0378426699000722).

**About:** Large opening changes and later intraday reversals in S&P 500 and Hang Seng futures.
**Finds:** The primary abstract reports reversals and some after-cost opportunities, qualified as possibly economically small.
**Why money:** Investor overreaction is the proposed explanation.
**Build:** Historical motivation only; precise full-text thresholds, execution and risk rules were not recovered.
**Can code?** A generic opening-gap fade can be coded, but cannot honestly be called an exact replication from this abstract.
Existing local failures must remain controlling.

### Intraday price reversals in the US stock index futures market: A 15-year study

Grant, Wolf and Yu, 2005. DOI 10.1016/j.jbankfin.2004.04.006.
[Primary university record and abstract](https://researchwith.montclair.edu/en/publications/intraday-price-reversals-in-the-us-stock-index-futures-market-a-1/).

**About:** Opening reversals during November 1987–September 2002.
**Finds:** Statistical evidence is strong, especially after positive opening moves, but significance falls sharply with
a bid-ask transaction-cost proxy.
**Why money:** Overreaction is the interpretation; consistent executable profitability remains unresolved.
**Build:** Keep as a cost-sensitive counterpoint, not current ES/MES evidence.
**Can code?** Not a source-exact strategy without the full protocol, quotes and cost assumptions.
No win percentage, modern trade frequency or controlled loss distribution was verified here.

These are related to already-tested overnight/intraday, opening-range and generic ES mean-reversion families in
[TIER_LIST](../../../TIER_LIST.md). They are not automatically identical replications, but cannot be used to reset
the family's selection history. The same applies to the already-parked
[Short-Term Basis Reversal](../research/scout/records/5250499.json): source/rules and identified paired maturities remain
missing, and its described weekly holding does not fit this evaluation objective.

## What the papers contribute to the desired sleeve

The practical contribution is a better specification, not an invented winner:

- Preserve the goal of frequent small realized gains, while requiring a positive net edge under the actual contract's costs.
- Once a distinct signal earns admission, define entry, target, stop and time exit together. Adding a small target to a
  losing signal is not the same as finding a high-win edge.
- Separate the signal's mechanism from risk/exit engineering. Combining papers 1 and 2 with a signal creates a new local
  adaptation; neither source establishes the combined rule or guarantees that its loss is bounded in execution.
- Evaluate profit arrival before VB/ONB losses breach the account, not just daily correlation or average standalone gains.
- Freeze BASE/ADD/REPLACE/EMPTY, actual integer sizes and common start dates before an earned account comparison.
  Report pass probability before 30 calendar days, timeouts, breach probability, maximum single loss and pass-time distribution.

No numerical benefit is forecast here. The existing arXiv leads remain conditional leads, not newly validated candidates.
The next useful discovery must supply a distinct mechanism and complete observable inputs; another threshold sweep
of the nineteen rejected pressure definitions is not the next step.

## Access and provenance receipt

- Anna's Archive: indexed discovery plus two direct search attempts; no verified catalogue metadata or downloaded text.
- Fung/Grant pair: primary abstract screening only. Publisher direct opening failed for the 2000 paper; no paywall bypass.
- A related HKBU Asian-futures PDF search lead returned 403 and was not read or summarized as a full paper.
- Nagel: NBER PDF opening returned 403; independently available author-hosted manuscript was readable.
- Leung/Li and Kitapbayev/Leung: public arXiv manuscript sections were readable.
- A search-title lead, “A High Winning Opportunities Intraday Volatility Trading Method Using Artificial Immune Systems,”
  DOI 10.1007/978-3-319-92058-0_20, was not admitted: the primary chapter could not be read.
  Its title is not evidence of an appropriate hit rate, drawdown or independently tested system.
- No new data panel, raw quotes, native micro fills, backtest, portfolio promotion, automation or live change resulted.

**For independent review:** this file. All findings above are attributed to dot and separated from author claims
and previously saved Codex results.
