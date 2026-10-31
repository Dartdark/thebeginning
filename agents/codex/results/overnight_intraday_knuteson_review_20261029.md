# Overnight versus intraday returns: WATCH for attribution; no new strategy trial
Summary: Knuteson plots large historical overnight/intraday return differences across 21 markets through September 2020.
The return pattern and the author's manipulation explanation are separate claims; the plots do not identify the cause.
The paper acknowledges no continued divergence since 2008 in its two U.S. index examples.
Related local overnight-futures tests are weak after costs; retain session-attribution lessons, not a new allocation.

Source: Bruce Knuteson, *Strikingly Suspicious Overnight and Intraday Returns*,
[SSRN 3705017](https://ssrn.com/abstract=3705017), user-uploaded four-page PDF.
SHA256: `fd94ef9130f97e4cfabcd4c69aafa44b321e28448220673304656ec7dc2e9d57`.
Review date: 2026-10-29. Source findings only; no independent reproduction. New return trials: **0**.
Repo context: codex/work `d9fc0aef8d946b552ac4ce74597735094fdc7af7`.

## 1. What is it about?

The split between stock-market close-to-next-open returns and open-to-close returns.
Figure 1 compounds each component separately for 21 indices/ETFs, using Yahoo Finance histories through
September 30, 2020 or the last available observation. Histories start at different dates; some finish earlier.
The author then argues that repeated portfolio expansion near the open and contraction later in the day by
large market-neutral quant firms could create the pattern.

The descriptive chart and causal allegation must be assessed separately. Neither is an executed futures strategy.

## 2. What does it find?

Figure 1 reports strongly positive cumulative overnight components and negative intraday components for
most examples, with China displaying the opposite split. The SPY example shows approximately +1,288%
overnight and −8% intraday over its available history beginning in 1993. These are separately compounded
components, not amounts one can add to get a buy-and-hold return, nor dollar profits from an audited strategy.

Crucial qualification: section II and footnote 17 acknowledge that the overnight/intraday divergence in the
two U.S. examples largely stopped after 2008. Footnote 18 names individual U.S. stocks with continued
divergence, which does not establish a current NQ/ES index signal.
The chart mixes indices and ETFs; the NASDAQ Composite is not the Nasdaq-100.

The author cites earlier literature for robustness to alternative opening/closing prices and vendors and supplies
a figure-code link. This four-page article does not present a new controlled participant-level causal study,
a complete modern after-cost trade ledger or prospective account evidence.
Published code/data references make reproduction possible in principle; they were not downloaded or run here.

## 3. Why does it make money, if it does?

The proposed explanation is asymmetric price impact: buying/expanding near the open and selling/contracting
later may have unequal persistent effects. The author suggests that marks on a sufficiently large existing
portfolio could outweigh trading costs.

That is an allegation/model narrative, not demonstrated participant behavior or an implementable edge for us.
No linked trading records, identified counterparties, causal experiment or audited manipulation profits are
provided in this article. Consistent aggregate charts do not uniquely identify manipulation or rule out all
risk, information, inventory, auction, investor-demand and measurement explanations. Greater intraday variance
also does not, by itself, determine where price discovery occurs or the sign of expected returns.

Even a real overnight premium is not free money: an outsider pays spreads/fees, takes overnight gap risk and
must enter/exit at executable prices. Market-neutral portfolio effects do not imply that buying NQ overnight
and shorting it every day is profitable today. No manipulative execution is proposed or implemented here.

## 4. Can we build on it?

**For return attribution and execution diagnostics, yes. For a new strategy test now, no.**

The source-code lead is [the author's figure repository/site](https://bruceknuteson.github.io/spy-day-and-night).
A reproduction must first verify raw/adjusted open-close consistency, dividends, splits, missing observations,
official opens versus actual executable auction fills, local calendars/timezones and comparable sample periods.
The underlying cash index/ETF history is not a futures cash ledger; futures carry, maintenance breaks, rolls,
spreads and contract identity require explicit treatment. These checks are not claims that this specific chart is wrong.

Split a frozen strategy's cash P&L into non-overlapping session components before assigning its edge to the
intraday entry rule. Reconcile all components, costs, rolls and open inventory back to the total.
An overnight component might be equity beta, not evidence that the entry filter works.
Observed post-order price movement cannot, alone, establish our price impact; separate own fills from market movement.

Prior pinned TIER_LIST evidence, **not rerun and not an exact replication**:
- `analysis/overnight_round.py`, 2018–26, overnight long 15:00→08:30:
  ES net $29 per full contract (t=0.9), NQ net $83 (t=1.4). Gross results are stronger, illustrating cost sensitivity.
- Overnight Drift and its sentiment filters were also tested; filters did not earn a funded improvement.

Ordinary close-to-next-open holds do not fit the current Apex intraday constraints. The personal account permits
the horizon, but weak related net results still do not establish a new place in that portfolio.
This source offers no new current-market feature, forced obligation or untouched evidence justifying reopening
the existing overnight family. An intraday-short adaptation would be a distinct protocol requiring its own evidence,
not a harmless replication of a cumulative chart.

## Decision and retention

**No new return screen or strategy-queue entry.** Keep the session-attribution lesson in EXECUTION_REFERENCES.
The empirical pattern merits careful measurement; the article's causal confidence exceeds the evidence presented here.
No backtests, data purchases, execution automation, allocation or live/VPS modifications.
Account contribution, execution savings and future profitability remain unverified.

For Claude: `agents/codex/results/overnight_intraday_knuteson_review_20261029.md`.
