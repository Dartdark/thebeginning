# Current-book delta and bounded baseline uncertainty at615485f

Source/header review, 2026-10-26. Working branch remains `codex/work`; no fetch, branch change, commit,
shared-file edit, strategy run, financial CSV row, trade-list body, pickle, raw price or result-output
read was performed for this note. Only source/docs, Git object metadata, file availability, CSV headers
and the third/header row of existing MultiCharts List of Trades sheets were inspected. H01/H02 remain
closed. New hypotheses/evaluations/return calculations: **0/0/0**.

## 1. Exact source delta: adopted books unchanged

Previous source `92b1d4cde768bcfce019cf9a95944158dd0ebba3`; new source
`615485fca3160a4c48761f44b0d1972e7b623ef4`, already available locally after root's fetch.
The complete tree diff adds `analysis/vb_cushion_sizing_test.py` and its output, and changes only
`LESSONS.md`, `MULTICHARTS_PITFALLS.md` and `TODO.md` besides those additions.
The new experiment's **output was not opened**. Operations notes were read as documentation only;
no live setting or system was accessed or changed.

Git blob equality verifies that these adopted definitions/interfaces are unchanged:

| Path | Same Git blob at both pins |
|---|---|
| `analysis/personal_portfolio.py` | `80d90aca24b413957ea32721334bf08191d8f162` |
| `analysis/personal_variants.py` | `32a6d57deffc17dbef03c95acdde558834cd8aa2` |
| `personal_strategies/PORTFOLIO.md` | `d175bfe07f183f05c05c3d56c88eb384c85821ee` |
| `funded_strategies/FUNDED_PLAN.md` | `5004629c7913bf92591cf14ef3e2a42337fa9831` |
| `analysis/funded_lab.py` | `645f608db95756e1840b4bde4890a122aa895775` |
| `analysis/funded_bootstrap.py` | `62dadf15e8cdc549b9ddc96d9647ab11ebb46aaf` |
| `analysis/combine_levers_test.py` | `d15909bf3f0db0b639dd97b32162277a47a219e6` |
| `analysis/plan_150k_test.py` | `c44a07d7d10ed9078285bdd47f5aea674c9d9fd7` |
| `analysis/montecarlo.py` | `dcec81d67d3a57f1143ec18e7ec00de3cfdaa457` |
| `TIER_LIST.md` | `2b37b76fe74189ef87b044e8f1aa51cdd755bd0d` |

No replacement of the original [bench source map](hunt_v2_bench_source_map.md) is needed. Its
adopted-book map continues to apply, with the input-availability clarification in section3 below:

- Personal: current19 columns, current weight1 per piece; SwingTarget v3 and PAPERTREND v2 IN,
  BB_MRM OUT, OT replaces OvernightAnomaly. Both MondayLong and DualThrust remain. The S30 column
  contains one MNQ **and** one MES; nineteen columns do not imply nineteen single-contract exposures.
  The future aggressive variant's selected weights2 are not the adopted current comparison.
- 50K funded: VB normal/flagged1/1 plus SwingTarget1; OT1 replaces MondayLong; RS long1 and MOC2MES.
  Preserve the other current source legs/risk sizes. The stale `funded_bootstrap.PLAN` alone omits
  adopted overlays and is not the current roster.
- 150K funded: SwingTarget2 replaces DualThrust2; OT2 and MondayLong remain, RS both sides1;
  preserve the documented cushion/risk-sizing ladder and integer flooring after scaling.
- Evaluation: unchanged combine stack. 50K has VB8, ONB_ADX30 risk1100, BridgeMonday2, EOS risk500;
  150K has VB20, Bridge5, ONB risk2750, EOS risk1250. Do not scale an already-floored50K risk quantity
  by2.5 or add ST/DT/RS/OT to the adopted evaluation baseline.

The new VB script tests cushion-dependent reductions of VB or the whole evaluation set against
VB8 always. These are experimental comparison rows; the new lesson records a negative conclusion
about the proposed VB reductions. Neither a new experiment nor an operations TODO changes the
adopted plan source. This note makes no numerical result claim or independent attestation about that
experiment. The whole-set0.5 reference also needs actual integer-contract treatment before it could
be described as executable; this review did not run or repair it.

## 2. Answer to the new feasibility question

**Fees/reentries are not inherently unbounded.** Several corrections are exactly recoverable from
retained ticket metadata, and the remainder can have conservative bounds from verified trade caps.
An always-UNRESOLVED bench cannot distinguish a robust improvement from a small publication-method
effect. A future eligible candidate should face a preregistered baseline correction/envelope audit,
with the same source uncertainty carried through all four paired rows.

**Mark/version and missing-coverage uncertainties are separate.** Source alone cannot give a finite,
useful price-error bound for an uncapped overnight hold, an unobserved later book, or a different
strategy protocol. Do not turn a fee bound into a claim that all baseline uncertainty is resolved.
Where exact current-book reconstruction or an honest finite envelope remains unavailable, the
particular qualifying claim remains limited; this does not retroactively reopen H01/H02.

### 2a. Exact commission bridge and a cap-based bound

For leg `l` on book date `d`, define:

- `n[l,d]`: actual whole-micro round trips, preserving reentries, quantity and booking date;
- `b[l]`: commission already embedded per ticket in the saved source (exclude slippage);
- `F[l]`: frozen contract-specific native micro commission/fee assumption;
- `I[l,d]`: the indicator on which the publication adds its daily fee adjustment;
- `a[l]`: that published extra per indicated day.

If gross fills and slippage are otherwise identical, the exact daily correction is

`corrected - published = -(F[l]-b[l])*n[l,d] + a[l]*I[l,d]`.

The current fee1.24 personal wrapper uses `a=1.24-0.725=0.515` per nonzero raw plan10 day,
whereas the additional ticket-ledger pieces charge that difference per ticket. For an NQ-derived
plan10 leg whose embedded commission is verified as0.725 and whose target is1.24, this reduces to

`corrected - published = -0.515*(n-I)`.

If a verified cap is `0<=n<=M`, then a conservative remaining undercharge bound is
`0<=cost_error<=0.515*(M-I)`, provided `n>=I` is reconciled. A nonzero raw P&L day with no ticket is
itself a reconciliation failure. A zero-P&L day is **not** automatically proof of zero tickets.
Use `0.515*M` before that indicator/count relationship has been established. If fees can be lower
than the embedded source fee, retain the signed interval rather than force an undercharge model.

The source-confirmed VB v1 cap is3 tickets/date (`analysis/vault_break_v8_test.py`, v1 path and
default `max_tr=3`; it is the plan's VB v1 MC report). Conditional on source/export reconciliation,
VB's residual at a nonzero publication day is therefore at most `2*0.515=1.03` per one MNQ;
without a usable day indicator, at most `3*0.515=1.545`. These are **cost-arithmetic ceilings**, not
observed ticket counts, sample profits or proof of source parity. Other legs need their own source
caps or exact ticket counts; the VB cap must not be copied across the book.

Prefer exact counts over a worst-case cap whenever retained entry/exit metadata supplies them.
Reading just Date/Time/Type/Contracts after an authorized audit can establish fee counts without
searching candidate returns. Match partial exits/scale-outs by order/trade identifiers and normalize
the report's Contracts to the actual fixed-micro allocation; counting entry rows blindly is unsafe.

Important source exceptions:

- **MOC/MES:** source commission is5.00/ES, or0.50/MES, not0.725. The existing plan10 extra is still
  `(F_MNQ-0.725)*I`; use the general formula with `b=0.50` and actual `F_MES` and counts. If both
  frozen fee assumptions were1.24 and there were exactly one round trip on each indicated day,
  the remaining correction would be-0.225/day. That is conditional arithmetic, not a measured effect.
- **S30:** the combined saved daily series already embeds7.25/NQ and5.00/ES plus its native price
  slippage, divided by10. The personal wrapper adds no native-fee top-up. Reprice its NQ and ES
  tickets separately: subtract `(F_MNQ-0.725)*n_NQ` and `(F_MES-0.50)*n_ES` on their frozen exit-cost
  dates. Both retained ticket headers contain entry/exit dates, enough to count costs later; there
  are no actual counts in this review. Do not subtract another full round-trip cost from marked days.
- **CLS/MCL:** the inspected source uses7.25/CL, hence0.725/MCL, and already pays native CL tick
  slippage in entry/exit prices. Its native target fee must be separately frozen as `F_MCL`.
- **FC2B/DT/OT/Kusho/S47/ST/PT and Twin's retained ledger:** existing adapters charge the native
  commission adjustment per ticket. Reentry counts need not remain a generic uncertainty if the
  source units, gross/net bridge, dates and adopted version reconcile. ST/PT source nets already
  include17.25/NQ (commission7.25 plus adverse ticks); do not charge slippage again. Twin's fee
  credit uses its retained ledger's exit-session dates while preserving published daily marks.

The repo's common1.24 experiment label is a research assumption; it does not independently verify
one broker's current MNQ/MES/MCL rate. Freeze the actual declared native fee schedule by instrument
and any prespecified fee stress before comparing a new candidate. Fees and fill/latency uncertainty
must remain separate; a finite commission bound does not bound market-impact errors.

### 2b. Propagate uncertainty through drawdown and paired MC

Let `x[d]` be one published portfolio's daily net and `e[d]` its correction. For a calendar/path,
write `E[t]=sum(e[1:t])`, including `E[0]=0`. The maximum-drawdown functional obeys

`abs(DD(x+e)-DD(x)) <= max(E)-min(E)`.

Thus `abs(e[d])<=u[d]` gives the conservative ceiling `U=sum(u[d])`. For a fee-only missing charge
`e[d]=-c[d]`, `0<=c[d]<=u[d]`, cumulative correction is nonincreasing, so

`profit-U <= corrected_profit <= profit`, and `DD <= corrected_DD <= DD+U`.

For general signed errors, use `profit+-U` and `max(0,DD-U)..DD+U`. Historical annual profit has
error at most `252*U/T` on a `T`-day common calendar. For each paired252-day MC history, recompute
its own `U=sum(u[drawn_date])` **with repeated dates counted repeatedly**. A full-history fee bound
must not be reused without accounting for resampling multiplicities.

Ratio bounds require a strictly positive drawdown denominator. With nonnegative profit lower bound,
use `profit_lower/DD_upper` and `profit_upper/DD_lower`; otherwise use signed interval arithmetic
over the endpoint combinations. Zero/undefined denominators do not produce an automatic passing
infinite ratio. A conservative robust comparison is candidate-row ratio lower bound minus control
ratio upper bound, for BOTH BASE and EMPTY; its paired5%quantile must stay positive when that gate
is preregistered. Exact corrected shared paths are much sharper than independent worst-case bounds.

All rows share common errors from retained baseline legs. ADD minus BASE and REPLACE minus EMPTY
cancel common baseline corrections in **profit differences**, when candidate sizing/trading is fixed.
They do **not** cancel them in return/DD or loss-risk comparisons, whose denominators and losses
depend on the entire path. REPLACE versus BASE also removes the slot's own P&L **and uncertainty**;
EMPTY likewise excludes that slot. Carry the correct leg-level error sets, do not apply the same
total envelope after deleting a leg, and never treat publication-versus-replay changes as candidate alpha.

For a future design pass, freeze before the first book comparison: exact-cost repaired baseline when
possible; each residual leg's uncertainty set and justification; whole-contract allocation; common
date coverage; shared MC histories/seeds; and acceptance of the worst-case or prespecified paired
uncertainty test. Do not choose an error budget or select convenient correction scenarios after seeing
which makes the candidate pass. A point improvement can be reported while its qualifying status is
conditional; no always-reject constant or automatic pass should replace this audit.

### 2c. Marks, protocol differences and coverage

- **Kusho exit-date booking:** it is a fully specified publication convention, so it does not make
  that narrowly defined published-series comparison unknowable. A stronger personal daily-mark
  claim requires marking open exposure. With the same trades/costs and a complete native mark grid,
  cumulative booking error is the open position's unrealized P&L (plus any explicitly different fee
  timing), which can be measured or bounded from held-period prices and quantity. Its price bound
  cannot be inferred from commission or a stop that can gap. Reconcile start/end carries and rolls.
- **Twin:** published personal source explicitly uses the v1 checker ledger, while the piece is
  named v2.1. Existing v2 MC report is a possible fixed sensitivity/reference, not exact v2.1 parity.
  The source's uncapped overnight stop/version changes do not have a useful source-only finite
  dollar bound. Full prices/actual altered tickets or the exact v2.1 MC list are needed. Even a finite
  observed v1-v2 difference would not prove an envelope contains every v2.1 change.
- **S30 daily marks:** exact native fee correction can preserve its existing daily mark series.
  Verifying/rebuilding its price marks and contract-switch adjustments requires the separate source
  prices/jump provenance; the retained ledger headers lack those price/jump fields. Do not substitute
  an exit-only series and call its DD the original daily-marked book.
- **OT cutoff:** use complete common coverage ending no later than2026-07-07 for a future full-book
  comparison. There is no source-based bound for missing postcutoff strategy returns. Later zeros
  must not be counted as observed no-trade days. This is irrelevant to a complete2018-22 comparison
  but remains a limit on later full-history claims.
- **Funded/evaluation:** a personal daily correction does not fix OT/CLS constant adverse proxies,
  Bridge's missing Sunday19:00-to-midnight path or MOC's close-only path. Account pass/payout logic is
  discontinuous at breaches; a small daily fee bound is not a joint-path certificate. Repair those
  chronological inputs or establish a valid account-level robust path envelope first.

## 3. Inputs now known to be available, without opening financial rows

The existing retained baseline and source manifests named in the original source map remain the
starting point; this review did not hash/re-read their P&L contents. The following **local** raw MC
workbooks exist and expose a List of Trades sheet with the same row3 headers:
Trade #, Order #, Type, Signal, Date, Time, Price, Contracts, Profit ($), Profit (%), Cum. Profit ($),
Cum. Profit (%), Run-up ($/%), Drawdown ($/%). Only the header row and sheet names were read.

| Current leg/reference | Local workbook under `mc_reports/` |
|---|---|
| VB | `Backtesting Strategy Performance Report VB v1.xlsx` |
| ONB ML | `Backtesting Strategy Performance Report _ @NQ - 15 Minutes Overnight Bias ML (funded) v2.xlsx` |
| Monday | `Backtesting Strategy Performance Report _ @NQ - 5 Minutes NQ Monday Longs.xlsx` |
| EOS | `Backtesting Strategy Performance Report EOS v1.xlsx` |
| LDF | `Backtesting Strategy Performance Report _ @NQ - 5 Minutes Late Day Flow.xlsx` |
| NFP | `Backtesting Strategy Performance Report _ @NQ - 5 Minutes NFP Fade.xlsx` |
| Bridge Monday | `Backtesting Strategy Performance Report _ @NQ - 5 Minutes Bridge Monday Longs.xlsx` |
| CLS | `Backtesting Strategy Performance Report _ CL - 5 Minutes CL Sunday Gap.xlsx` |
| MES MOC | `Backtesting Strategy Performance Report _ @ES - 5 Minutes ES MOC Follow.xlsx` |
| RS | `Backtesting Strategy Performance Report _ @NQ - 1 Minute Relative Strength.xlsx` |
| Twin v2 sensitivity | `Backtesting Strategy Performance Report _ @NQ - 1 Minute Twin Continuation v2.xlsx` |

Their presence/header shape makes an exact count/booking audit feasible; it certifies neither coverage,
adopted-parameter parity, complete matching pairs nor native fills. Source-date/report hashes and
gross-to-net reconciliation are still required before their rows replace any retained baseline.

ST v3 and PAPERTREND v2 **root-level workbooks are locally absent**, although named in the remote tree.
Their retained MC-converted CSVs are present under
`agents/codex/inputs/rebound/plan_update_afde088/checks/candidates/{swing_target/mc_trades_v3.csv,papertrend/mc_trades_claude.csv}`.
Both have headers `date,side,entry,exit,kind,t_in,t_out,exit_date,gross,net`; source/hash provenance is
already retained in that snapshot manifest. They can support exact fee counts/repricing later without
pretending an uninspected local workbook exists.

Other inspected headers:

- `agents/tasks/plan_daily_pnl.csv`: date plus the10 core-leg columns; **no ticket counts**.
- `agents/codex/inputs/swing_target/plan_snapshot/checks/candidates/twin_continuation/trades.csv`:
  date,side,net,setup,entry_date,entry_time_ct,exit_time_ct,entry,exit.
- Same snapshot's `kusho/python_trades_v9_rolladj.csv`:
  date,exit_date,side,entry,exit,kind,swing,fm,xm,net,weekend.
- `agents/codex/inputs/s30/reviewer_snapshot/python_trades_{NQ,ES}.csv`:
  date,exit_date,side,net,days,i0,i1. Enough for fee counting; not enough for full price-mark rebuilding.
- S30 saved combined daily CSV: unnamed date-index column and `0`; the instrument decomposition
  is not present in that one column and must come from the two source ticket lists.
- `checks/candidates/relative_strength/trades.csv`:
  date,side,net,kind,entry,exit,z.

## 4. Recommended next bench route, after a future eligible design pass

1. Bind the unchanged current615485f source and all selected retained inputs, then reconcile exact
   per-ticket counts/fees to the published baseline without changing candidate or source selection.
   No test of a closed hypothesis is authorized by this repair.
2. Correct known deterministic commission differences; freeze every remaining per-leg cost/mark
   envelope and what it actually covers. If a required envelope cannot be justified, label that
   specific claim LIMITED/UNRESOLVED rather than call all personal arithmetic impossible.
3. Run the candidate's already-preregistered BASE/ADD/REPLACE/EMPTY on identical observed design dates,
   whole contracts, exact candidate fees and identical shared personal MC histories; report published,
   exact-repaired and predeclared robust-envelope comparisons separately. Require robust improvement
   over both controls; a change attributable to repairing BASE is not candidate alpha.
4. Only surviving, adequately bounded evidence can reach a separately committed selection/validation
   gate. A daily result never establishes funded/evaluation improvement without valid current joint
   account chronology. Missing exact Twin v2.1 marks and post-OT-cutoff book history remain explicit limits.

This note supplies formulas and feasible inputs; it does not assert a numerical uncertainty budget,
cost-corrected portfolio, new candidate, improved plan, fresh validation or trading approval.
