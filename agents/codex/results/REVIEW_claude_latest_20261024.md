# Claude latest strategy work: material review findings

Summary: Reviewed Claude35c4f2af, focusing PAPERTREND, the capital-expansion rule and the S03 cross-reference.
The capital/risk framing is useful; two concrete evaluation-model corrections precede trusting small gains.
PAPERTREND needs trade-list reconciliation and paired portfolio uncertainty; its statistical FAIL remains open.
S03's referenced code test is distinct from the bulletin reconstruction and used an older personal baseline.
Read-only review: no strategy reruns, allocation/live changes or edits to Claude-owned files.

## 1. Correct 150K integer sizing before evaluation comparisons

`analysis/papertrend_bench.py` builds ONB/EOS quantities with `floor(risk/stop_cost)` for50K, then multiplies
those floored arrays by2.5 for150K. This can produce fractional futures quantities and differs from flooring
the150K dollar-risk quantities. Fixed VB8->20 and Bridge2->5 scale exactly; risk-sized legs need separate
calculation at ONB$2750 and EOS$1250. Reuse the current canonical quantity engine.

Smallest check: assert every executable quantity is an integer, compare per-date ONB/EOS quantities with
the actual150K implementation, then rerun the same fixed evaluation configurations on paired valid starts.
No new parameter or size search is needed.

## 2. Reprice evaluation paths at real micro fees

The same evaluation path calls `portfolio.paths(...)/10`. That function recalculates net from slipped
entry/exit prices minus its NQ COST, rather than using a candidate's supplied net. The inherited$7.25/NQ
commission becomes$0.725/MNQ, below the documented$1.04 actual fee (and$1.24 stress).
Reprice baseline and challenger per actual round trip, preserving once-only slippage, before assessing
changes such as50.1%->50.3%. This finding is about the evaluated path code, not proof all funded/personal
fee calculations are wrong.

## 3. PAPERTREND parity and promotion are separate questions

The saved matched-period output is582 trades versus535 in the report: **8.8% more**, not15%.
Net$209236 versus$167378 is **25.0% higher**. Similar PF1.68/1.66 does not establish source parity.
Obtain the actual code and trade list; match entry date/time/side/fill and exits, then attribute unmatched
trades before tuning any rule to force the counts to agree.

The checker reports DSR0.865 below0.95 and FAIL. Reproducing the Python implementation or resolving
the MC trade count does not repair a statistical failure. Do not retroactively turn39 examined variants
into a<=3-variant preregistration. The source's original fixed rule and any preregistered robustness work
should be distinguished from settings chosen after looking at historical outcomes. A discretionary user
exception must be labelled explicitly rather than reported as passing the standard gates.

## 4. Improve the capital-expansion decision memo

The new bench correctly distinguishes more profit from better use of capital. For PAPERTREND, the claimed
personal increase$37.1k->$39.4k comes with capital$33.6k->$35.6k; the point return/DD improves8.3->8.7.
That is a plausible candidate, not yet a demonstrated improvement. Save paired history indices and report
intervals for incremental annual profit and drawdown/risk-adjusted benefit. Compare at the same starting
capital using executable whole-micro allocations and the actual ladder threshold. Continuous equal-DD
rescaling is informative but not always tradable. Preserve separate speed, bad-case-year and breach outcomes
for Apex, whose payout cap can conceal useful changes.

## 5. Keep S03 versions and baseline dates separate

Claude's cited `agents/codex/results/s03_v2.md` exists on codex/work and includes actual account comparisons.
It is a different, supplied-code study: stop rounding away from entry, source ring-buffer semantics, and
actual micro costs. It is not `s03_noisearea.md`, the bulletin reconstruction with different declared choices.
Therefore the citation is not fabricated and should not be replaced with this reconstruction's numbers.

However, the cited personal test explicitly uses14 pieces, versus the current17-piece portfolio, and its
account results use2243/2262 dates, excluding19 including stress sessions. Its historical no-placement
conclusion must retain those qualifications. Current funded plans also changed with Overnight Tick/VIX.
Rerun on the current frozen roster and clearly audited coverage before presenting the old verdict as a
current-plan finding. Our bulletin reconstruction's account tests remain blocked by missing held prices;
that is UNKNOWN contribution, not independently confirmed no gain.

## Scope and references

Claude ref35c4f2af410c274cb54d346374a3c84237242082; reviewed `analysis/papertrend_bench.py`,
`analysis/portfolio.py`, `analysis/personal_portfolio.py`, `analysis/overnight_tick_bench.py`, PAPERTREND outputs/
checker patches, `personal_strategies/PORTFOLIO.md`, and Codex's existing `agents/codex/results/s03_v2.md`.
This is a focused source/report review, not an independent recreation of every recent strategy or plugin.
