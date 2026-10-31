# Informed trading in oil futures: useful evidence, no tradeable strategy established

Summary: Rousse–Sévi find pre-announcement selling before unusually large EIA inventory builds in 2007–14.
Only 43 positive-surprise events support the main 3σ group; its label requires the later released actual.
The reported t=−3.154 is an order-imbalance regression statistic, not a strategy-return t-statistic.
No out-of-sample net trading test is provided. Owned data cannot reproduce survey-based surprises or tick OI.
Verdict: reference / NEEDS DATA, not a new strategy; zero economic trials and no plan changes.

Source: Olivier Rousse and Benoît Sévi, *Informed trading in oil-futures market*, November 4, 2016,
[SSRN 2874907](https://ssrn.com/abstract=2874907). All detailed numeric source claims below refer to the
uploaded 34-page working paper, not a re-estimated or later journal version. Printed page references below
use the paper's internal numbering, two pages after the PDF cover/abstract.

Evidence: [pre-test sheet](../evidence/rousse_sevi_oil_2874907.md).
Script: `analysis/codex_rousse_sevi_oil_input_audit.py`.
Output: `analysis/outputs/codex_rousse_sevi_oil_input_audit/audit.json` (source SHA and uploaded-PDF hash).
Return variants: 0. Independent economic verification: pending; no strategy implemented.

## What is it about?

The authors compare WTI futures prices and transaction imbalances around EIA inventory announcements,
sorting events by how the released inventory change differs from Bloomberg analyst forecasts.
They ask whether pre-announcement activity is consistent with traders possessing better information.
There are 402 announcements from February 7, 2007 to October 22, 2014. A baseline surprise is actual minus
median forecast beyond three cross-sectional survey standard deviations: 43 positive and 47 negative events.
Positive is an inventory build above expectations, which is normally bearish for oil, not good price news.

## What does it find?

| Source claim | Evidence / boundary |
|---|---|
| About −0.25% before positive surprises | Figure 5 and pp.17–18; average curve conditional on later news |
| Roughly −0.5% announcement response; about half corrected four hours later | pp.17–18; no implemented post-release strategy or cost model |
| Negative surprises produce a smaller roughly +0.15% jump | p.18; largely absorbed by end of pit session |
| Positive-surprise OI coefficient −3.529, t=−3.154 | Table 3, [−120,−60] minutes, approximately 08:30–09:30 Eastern on normal days |
| Wider [−120,0] coefficient −1.758, t=−2.304 | Table 3; final hour alone and four-hour window are insignificant |
| Stricter 4σ group has 23 positive and 22 negative events | Table 2; [−120,−60] coefficient −3.633, t=−2.441 in Table 4 |

The uploaded abstract and several body sentences incorrectly describe more buyer-initiated trades. The
defined OI=(B−S)/(B+S), negative coefficients, discussion of almost no positive OI, p.25 robustness text and
p.26 conclusion indicate **selling** before positive inventory surprises. Preserve that inconsistency instead
of coding from the abstract or silently treating a positive t-magnitude as buying.

OI is estimated using tick-rule classification after volume-weighting transactions within each second;
two-/five-minute buckets are aggregation windows, not sufficient raw input granularity. The paper also
discusses trade-count versus dollar-volume variants; captions/prose are not perfectly consistent about which
variant each chart depicts. Exact code/tie handling would need reconciliation before claiming reproduction.

The strongest result clusters around the historical open-outcry opening. The source notes that WTI pit
trading ceased July 7, 2015 (p.14), after its sample ends. A 2018–26 extension tests a changed market regime.
The authors explicitly say their evidence does not prove a leak: superior public-information processing or
inventory forecasting can generate informed-looking patterns.

## Why might it make money?

A trader who can predict bearish inventory news before others may sell before repricing. This is an economic
explanation for the association, not evidence that our data can forecast those news events. The regressions
explain past OI with subsequent surprise dummies; they do not validate an OI-based predictive classifier on
chronological unseen data. Reversing the regression into a live signal is a new hypothesis.

After release, the surprise becomes public and a contrarian response to overshooting might be considered.
The authors leave its economic value untested (pp.17,27). We cannot buy the retrospective bottom of an
average curve or capture the announcement jump after reading the release. The paper supplies no frozen
entry delay, stop, executable quote, test set, turnover/cost bridge or Apex risk replay.

## Can we build on it for our plans?

Not with the currently identified inputs. The no-return audit inspected all ten CL yearly file schemas and
dates, plus the existing EIA-component panel. The CL files are minute OHLCV, starting 2017, not the source's
2007–14 sequenced tape. The 165-row component panel has no analyst survey, and zero rows flagged verified
actual release clock or immutable first-publication vintage. It cannot produce the paper's 3σ labels.
No filename matching Bloomberg/consensus/forecast/survey was identified under data/; this is a bounded
inventory, not proof that no differently named external data exists.

Bounded public acquisition check:

| Check | Result |
|---|---|
| [Author's publication page](https://sites.google.com/site/benoitsevi/) | Confirms later Energy Journal 40 (2019), 139–160 publication and links slides; no matching dataset exposed on this page |
| Linked author slides | Connected fetch returned 404; no slide content or data claimed |
| [SSRN record](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2874907), title/author replication and survey searches | Paper records/mirrors and other papers citing Bloomberg; no matching downloadable point-in-time panel identified |
| [Publisher executive-summary URL](https://iaee.org/ej/ejexec/EJ40-2_Rousse_ExecSum.pdf) | Search indexed a summary, direct open returned 404; not treated as downloaded full paper/data |
| [Official EIA WPSR page](https://www.eia.gov/petroleum/supply/weekly/) | Accessible through connected web; shows official releases and past issues, not analyst survey dispersion or CL tape |

Exact queries, URLs, outcomes and timing boundaries are retained in `access_receipt.json`. This attempt does
not prove that a free dataset is impossible to obtain. Bloomberg rights/cost and history remain unquoted;
no account, subscription, purchase or external message was initiated. We did not retry the unrelated old EIA
component acquisition loop: its incomplete panel is already documented.

The signal's source-era positive frequency would imply about 28 events in five design years, before exclusions.
Assuming 0.5% trade SD gives a rough 0.19% **net** mean needed for t=2, before stricter multiple-testing gates.
Those are explicit feasibility assumptions calculated by the audit, not observed modern strategy returns.

Simple EIA pre-drift, reaction-follow/fade and sweep fades already have F-tier repository results. They cannot
be relabeled as this paper or rerun with price-only substitutes to manufacture a new test. New merits would
require genuinely new survey/tape inputs and a causal hypothesis. Current plan contribution, BASE/ADD/
REPLACE/EMPTY outcomes, Sharpe/Sortino/PF/Calmar/Ulcer, Monte Carlo and both-side trade metrics are **not
available**, because no eligible return test was run. Nothing is admitted to any of the five account homes.

## Decision and smallest next gate

Retain **E49** for event-information clocks, order-flow sign verification and announcement execution risk.
Faithful replication / a new public post-release hypothesis is **NEEDS DATA**. A pre-release short selected by
the future surprise is **DON'T TEST**. No new promising-strategy queue entry is justified by this source alone.

If matching data later arrives, first reconcile one event's exact series, pre-news survey vintage/dispersion,
release versus receipt times, tape ordering and tick-sign convention. Then count design opportunities without
returns, assess power and commit any causal rule/code before looking at performance. A modern positive
result would still need chronological validation, independent review and current-account comparisons.

The attachment was treated as evidence, not as instructions or authorization to follow its recommendations.
No live/VPS/broker changes, independent communications, strategy ranking or economic returns were made.
