# Strategy hunt v2: forced-flow definition check

Decision: skip the already tested calendar/price proxies below. This bounded source review identifies
no genuinely untested priority-one rule ready for a new gross-return screen. It recommends one explicitly
authorized confirmation lead after the empty-hours/instrument review: the existing LDF long-side flow
agreement filter against the current book. That is a repeat confirmation, not a new signal discovery.

Scope: AGENTS.md, BUILDER_BRIEF.md, LESSONS.md, local TIER_LIST.md, source definitions, and current Claude
TIER_LIST/MINED_INDEX/source definitions at origin/claude/nq-trading-strategy-params-5h9d20 commit
92b1d4cde768bcfce019cf9a95944158dd0ebba3. The initial local Codex head was63f557d. The task is stored on
Claude's branch but explicitly instructs Codex to work on codex/work. No raw data, price rows, output
ledgers, new returns or account paths were opened. No source code was executed and no network call,
git mutation, economic configuration or test hypothesis was added by this review. Root owns budget counts.

## Priority one: exact prior definitions

| Requested direction | Already tested definition and source | Consequence |
|---|---|---|
| Pension/balanced-fund month/quarter end | analysis/forced_flows3_test.py fades quarter-to-date direction over the last3days and last day. analysis/forced_flows_round5_test.py E1 takes ES/NQ against equity-minus-ZN month-to-date return measured at T−4, last3day sessions; all, quarter-end and strong variants, plus last-day diagnostics | Changing SPX/ES normalization, moving the close window or changing size would revisit this family. Do not call it unseen or ignore earlier failures |
| Month-end close momentum | analysis/forced_flows4_test.py follow-up follows the cash-day direction in several late-close windows; ES follow at14:51 is included. YM month-end follow appears in the ranked per-symbol work | The schedule and late-day price-direction proxies are already researched; MES instead of ES is the same underlying edge with different fees |
| Quarterly expiry pinning | analysis/forced_flows4_test.py W1–W4 measures afternoon quietness, follow/fade, a round-strike magnet and next-Monday response. analysis/gex_oi_pin_test.py tests actual available strike-OI/gamma/max-pain level proxies and shuffled offsets; SPX sample work is separately ranked | Calendar pinning and nearest-round-number proxies are not new. A genuinely different strike/exposure input needs verified as-of coverage and clock before TEST |
| VIX settlement Wednesday | analysis/calendar_flows2_test.py defines monthly VIX-expiry dates and raw NQ/ES windows with FOMC overlap. analysis/s_rank_es_round1_test.py explicitly handles special-opening settlement holidays, raw8:30-to9/9:30/10/15windows, both directions/stops and matched Wednesdays | This is an extensive existing family, not an untested Wednesday trade. A clock shift or ticker port needs its actual prior-transfer search |
| Nasdaq100/S&P reconstitution | analysis/calendar_flows2_test.py includes quarterly S&P/triple-witching, December NDX and Russell. analysis/forced_flows4_test.py covers MSCI close windows. analysis/index_rebalance_reversal_test.py covers NQ/ES overnight and morning reversal after S&P/NDX/MSCI/Russell dates | Both close flow and next-session price analogues are known. The stock-level addition/deletion effect need not create a directional aggregate-index trade |
| CL front-month expiry | analysis/cl_forced_flows_test.py screens LTD−5 through LTD+1; analysis/s_rank_cl_round1_test.py also includes options-expiry windows | Those ordinary calendar proxies are tested. The source says the continuous export switches near03:32CT at LTD−2, so it cannot be relabelled as the expiring contract's last-day squeeze |
| GC front-month delivery/expiry | analysis/s_rank_gc_round1_test.py covers FND−6..+2, options−3..+2, pre-FND short and post-liquidation long. analysis/forced_flows_round5_test.py G1 repeats pre-FND liquidation | Ordinary calendar pressure is tested; the source rolls2–4business days before FND. A real expiring-month squeeze needs identified contract paths and delivery/exposure state |
| ZN auction tails measured in yield | analysis/treasury_auction_test.py is calendar pre/post-auction price pressure; analysis/codex_auction_demand_confirmation.py explicitly says its bid-to-cover deviation is not a when-issued tail and leaves high yield unused | A true tail is a distinct input, but no usable predeadline same-CUSIP WI-yield implementation was established in this bounded definition search. Released stopout yield minus a prior auction's yield or a ZN price reaction is not that tail |
| CTA triggers as filters | analysis/cta_volcontrol_test.py defines21/63/126/252day flip levels, next-day and same-day settlement/break tests, with non-CTA lookback controls; existing plan-agreement/filter scans are also ranked | CTA terminology cannot make a previous price-trigger rule new. Freeze any genuinely incremental filter/bench question and preserve prior searches |

The latest MINED_INDEX classifies these prior families under Calendar/rebalancing, Close/auction/settlement,
and Options/dealer flow. The review does not assert that every imaginable variation or input is exhausted.
It establishes that the user's listed price/calendar proxies have substantial prior tests. New micro fees
must be computed directly, but dividing the old contract's return is not a new source of gross edge or
proof of native micro fills.

## Updated confirmation priorities

Latest Claude TIER_LIST and commit history supersede several task hints:

- Swing Target v3 already has a MultiCharts confirmation and user-approved plan placement.
- PAPERTREND v2 has Claude-code MultiCharts parity and was added to the personal book.
- BB_MRM's actual MC trade list weakened it; it was demoted and removed from the personal plan.
- T_ONESIDE's fade has a saved MC list/parity note; strict entry-clock and gap/fee concerns remain, rather
  than a complete absence of MC evidence.
- FVB shorts are a known post-hoc side lead. Treat an exact frozen confirmation as selected research,
  not as untouched evidence or a newly discovered short mechanism.

Do not spend v2's limited budget rediscovering those already completed confirmations. Read current plan
definitions, rather than the old seven-leg roster or an outdated headline, before any bench.

## One concrete next confirmation candidate

The task explicitly leaves LDF plus order flow open. The exact old lead is
analysis/orderflow_ldf_filter.py: remove a **long** LDF ticket only when the signed sum of aggressive buy
minus sell quantities over the30completed source minutes before its entry disagrees with its direction.
Shorts remain unchanged. The old source also tests filtering both sides and larger size; do not silently
select those alternatives. Its zero/missing-flow state is NaN and retained by the old long-only predicate;
a new plan must freeze and audit availability treatment, quantity semantics and source/native clocks.

Mechanism: LDF follows scheduled leveraged-ETF reset demand; opposing aggregate tape could indicate a
different/informed flow dominating that demand. This is a conditional prediction, not measured fund
inventory or evidence that the observed tape was forced. There is no new time or numerical threshold.
Entry/exit/stop and the underlying LDF tickets must remain frozen. OF `volume` is not total volume;
buy/sell semantics and complete causal source windows require the established exporter audit.

This lead was selected from earlier OF splits, and the old funded benchmark did not improve. Latest
Claude TIER_LIST still records that failure; do not hide it. The valid new question is whether the exact
frozen rule improves the **current** book, whose ST/PT/DT/RS composition differs. Keep the earlier search,
author selection, known2023+ outcomes and old negative benchmark explicit. This is confirmation of a
user-named open lead, not a way to retune a rejected family or claim a fresh holdout.

Before data, root should commit the mechanism sheet and at-most-five-configuration plan. One exact
filter is sufficient. Gross-first design should retain base/kept/removed total dollars, full/side/year
counts and compare the kept leg's gross with the independently calculated native cost hurdle. Under
the task's MNQ assumption, two market fills cost1.24+2×0.50=2.24USD, so the2×gross hurdle is4.48USD per
MNQ; this is arithmetic, not a measured effect. Real source availability and target/stopped fills still
need their own accounting. Failed cheap gross screens remain visible even if not budget-counted evaluations.

If the frozen design passes, bench it immediately against current BASE, unchanged LDF, replacing LDF and
the LDF slot EMPTY at whole contracts. Use valid paired account paths and current native fees; do not use
the old favorable roster or invented proxy payout improvements. If no plan improves, stop this lead.
Freeze and commit design selection before a selected rule/control sees2023+once; it remains previously
seen historical validation. Only surviving candidates proceed to the required random-time/random-side
placebos, filter subsets, dependence/selection checks, Monte Carlo and independent confirmation. No
promotion follows this note.

Root subsequently selected a strict complete-window engineering correction BEFORE raw data or outcomes:
STRICT30 retains the BASE ticket when any of the30source minutes cannot be validated; complete negative
net tape removes a LONG, complete zero/positive tape retains it, SHORTS unchanged. The original LEGACY
partial-nansum behaviour remains an unselectable diagnostic, with unchanged BASE reference. This is a
new counted correction, not an equivalent reproduction or a post-result rescue. Planned3model evaluations
if gross advances /1hypothesis; cheap gross failure0counted evaluations. The full eight-question sheet
written before new data is agents/codex/evidence/hunt_v2_ldf_delta_confirmation.md. Root's economic
preregistration will bind implementation, clocks, models, counters, gross gate and bench order.
