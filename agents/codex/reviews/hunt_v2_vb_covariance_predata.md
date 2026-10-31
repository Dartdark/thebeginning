# VB incremental-variance allocation: conditional SOURCE/MATH support, no result

Independent predata review,2026-10-27. Proposed question only; H10 is not registered by this review.
Budget read before new inputs: **5/60 economic evaluations,9/10 registered hypotheses,4gross screens**,
plus archived65t6 evaluations. This review adds0hypotheses,0gross screens,0economic evaluations.
Root owns evidence admission, preregistration, implementation review and any actual execution.

Scope: instructions, existing source-history notes, pinned code/definitions at
`d14dc9a153df128aafd3f48d4fea2aa78b88bb28`, source wrappers and five invented-array mathematical
checks. No actual baseline CSV header/row, market input, calendar schedule, workbook/trade ledger,
cache, financial output or return was accessed. No maker or account engine was imported/executed.

## Exact mathematical question

Root fixed the accepted VaultBreak parent before any new return or quantity-mask observation.
LetX be one-MNQ VaultBreak daily P&L under the specified published feature convention andB the
**shadow adopted current19 book**, including its existing one-MNQ VB. On the252 completed jointly
known book rows strictly before the new date's decision, estimate

`delta = 2*Cov(B,X) + Var(X)`.

Keep baseline one MNQ; add exactly one EXTRA MNQ iffdelta<0, otherwise0. Zero means no extra.
This is the identity `Var(B+X)-Var(B)=delta` applied to past sample moments. It neither guarantees
future lower variance nor proves profitability, smaller drawdown, a hedge before breach or account
survival. B must remain the fixed shadow BASE19, rather than past POLICY P&L containing prior extras;
feeding extras back intoB would change the algorithm.

Use all252 jointly known completed rows, including VB-zero/no-trade dates. Dropping zeros changes
the forecast population. No partly observed current-day row, future full-day membership,2017 zero
padding, backfill, short warm-up or return-selected row deletion is permitted. If the adopted series
starts in2018, the first252 actual rows are warm-up; earliest possible evaluated allocation follows
that warm-up. Known previous outcomes are mature feature inputs, not current trade labels.

For paired observations lengthn, the sign can be calculated without a denominator:

`N = 2*(n*sum(B*X)-sum(B)*sum(X)) + n*sum(X*X)-sum(X)**2`.

Both sample and population covariance/variance have the same positive common denominator, so they
produce the same sign when used consistently. Freeze a numerical representation before actual data.
Do not invent an epsilon, round source money to cents or change the boundary after seeing counts.
Exact decimal/rational interpretation of serialized feature values can avoid a floating near-zero
branch without altering their declared values.

BecauseB already containsX, writingB=X+O yields the stricter equivalent condition
`Cov(X,O) < -1.5*Var(X)`. Thus low correlation alone is insufficient: the other book must have a
strong enough estimated opposite covariance. EXTRA support can legitimately be zero or sparse.
Do not rescue a support failure by replacingB withEMPTY, using merelyCov<0, changing the parent,
window or threshold, or choosing another observed favorable condition.

## Source novelty and selected ancestry

The scoped pinned-source query found covariance calculations for alpha/relative-price beta, but no
matching rolling cross-covariance allocation against the current book. This is not a certificate that
all research everywhere is new. Read prior families establish the following differences:

|Pinned source|Gitblob|Prior definition|
|---|---|---|
|`analysis/vol_target_test.py`|`8de8e274a85574322571c32703551c2b689cd390`|NQ EWMA10/20/40 volatility, trailing target and exposure caps; scalar risk scaling, not the proposed book cross-covariance condition.|
|`analysis/plan_agreement_test.py`|`2edfbe58e52b5b6934e674f8dee7e35d37269257`|Earlier same-day signal sides and trailing5/20day plan-P&L signs, not marginal covariance.|
|`analysis/personal_variants.py`|`32a6d57deffc17dbef03c95acdde558834cd8aa2`|Selected fixed one/two-micro weights and conservative/current/aggressive rosters.|
|`analysis/mnq_sharedcap_test.py`|`dc6158d84e2b4676945cdc779e5d6ecbaae0c6fd`|Realized-plus-open loss cap and netted/multi-leg execution, not a lagged moment forecast.|
|`analysis/forced_flows3_test.py`|`e49d046be0b936026d3d68fdf6f0c291e583a2cf`|Risk-parity/volatility-target fund de/releveraging premise; related risk research, not this exact current-book allocator.|

H07's LDF/RS current-position adverse-mark question and H08/H09's fixed250USD affordability policies
remain closed and selected history. This proposal changes neither their clock, pair, source nor
threshold. A mathematical allocation objective is allowed by the user's filters/sizing goal; it is
not a newly measured forced market flow, new directional alpha, or a clean few-trial exemption.
All old parent selection, roster selection, sizing studies, t6/v2 trials and unknown family searches
must remain disclosed. The incremental EXTRA itself must qualify; POLICY cannot borrow VB's t.

## Information and implementation boundaries

The retained current19 baseline is an available **published-book daily proxy**, not authenticated
actual native cash P&L or a valid joint intraday account path. The source map and delta note already
document per-active-day fee corrections that can undercount reentries, inherited MOC/S30 conventions,
Twin's marked v1 versus v2.1 differences, Kusho exit booking and OT coverage ending2026-07-07. S30's
column includes both MNQ and MES; nineteen columns do not mean nineteen single contracts.

Inspected booking helpers do not establish a source-proven fatal design-period future-price leak:
ordinary prior exit-day booking delays a known realization, and Twin interim marks use observed
historical closes. They also do not independently certify every component or its availability clock.
SOURCE must bind exact dates/columns/cost convention and verify that each feature row's marks and
cashflows were knowable before the VB decision; Sunday/next-session mappings require particular care.
The fixed current roster is a selected historical replay, not a claim these strategies existed in2018.
No refitting on future candidate outcomes or current-date P&L is allowed.

Do not treat OT's post-cutoff zero padding as known no-trade returns or fill missing rows to obtain252
observations. Full-history coverage through the claimed endpoint must be established before promotion;
a design/source pass cannot certify unavailable later book history. Constant diagonal cost corrections
do not repair missing marks, missing coverage or different strategy versions.

Some fee uncertainty has a finite source-based ceiling: for VB's verified cap3tickets/date and the
1.24-versus.725 commission difference, residual undercharge is at most1.03USD per one MNQ on a
reconciled nonzero publication day, or1.545USD without that indicator relationship. These are source
arithmetic limits, not observed ticket counts, realized losses or an envelope for all nineteen legs.
Exact counts are preferable; every other leg needs its own valid cap/count and fee bridge.

The formula is exactly about its declared proxyX/B. If native VB rebuilt from raw source differs
from the feature's published VB slot because of entry anchors, gaps, target-through or reentries,
the forecast identity does not prove the new native parent's variance effect. Preserve the causal
one-MNQ replay and constant-two exposure controls in BASE/ADD/REPLACE/EMPTY comparisons, separating
publication/replay implementation differences from allocation alpha. Unsupported implementation
bounds leave any nominal book improvement LIMITED.

VB's max-three reentries depend on protected outcomes. SOURCE cannot simulate those outcomes and
call that a clock/count-only stage before gross. A first-qualified-proposal/day raw reference can
be nonoverlapping if prior flat/entry chronology is source-admitted; an all-proposals raw table is
overlapping diagnostic evidence. Root must freeze the raw protocol and its hurdle before data.
Neither a cap-conditioned overlap nor a raw proposal list is executable protected-strategy P&L.

## Five invented mathematical checks

Using252 invented observations (the four values[-3,-1,1,3] repeated63times) and exact Fractions:

1. B=2X: variance identity holds and the gate rejects.
2. B=-2X: identity holds and the gate accepts; estimated variance falls from4Var(X) toVar(X).
3. B=-X/2: exactdelta0, equal variance, gate rejects.
4. X=0 and arbitrary inventedB: exactdelta0, gate rejects.
5. B=X+O withO=-3X: included-baseline equivalence toCov(X,O)<-1.5Var(X) holds.

All five passed, with matching sample/population signs. They are software/mathematical examples,
not market observations, return simulations, gross screens or economic evaluations. Reproduction:

```python
from fractions import Fraction as F

def moments(x, b, ddof):
    n = len(x)
    den = n * (n - ddof)
    var = F(n * sum(z*z for z in x) - sum(x)**2, den)
    cov = F(n * sum(a*z for a,z in zip(x,b)) - sum(x)*sum(b), den)
    return var, cov

x = list(map(F, [-3, -1, 1, 3])) * 63
for label,b in [('positive',[2*z for z in x]),
                ('negative',[-2*z for z in x]),
                ('boundary',[-z/2 for z in x]),
                ('zero',[F(i%3) for i in range(252)])]:
    xx = [F(0)]*252 if label == 'zero' else x
    signs = []
    for ddof in (0,1):
        v,c = moments(xx,b,ddof)
        vb,_ = moments(b,b,ddof)
        after = [a+z for a,z in zip(xx,b)]
        va,_ = moments(after,after,ddof)
        assert va-vb == 2*c+v
        signs.append(2*c+v < 0)
    assert signs[0] == signs[1] == (label == 'negative')
o = [-3*z for z in x]
b = [a+z for a,z in zip(x,o)]
v,c = moments(x,b,1)
_,co = moments(x,o,1)
assert (2*c+v < 0) == (co < F(-3,2)*v)
```

## Decision

The completed eight-question/interface sheet
`agents/codex/research/hunt_v2_independent_book_constraint_gate.md`, SHA256
`969c2f628b6b23a4053001e9211ed4bac0952dfd23f33f9754f8a0d6273b41c1`, was then reviewed. It preserves
the shadowBASE19, prior-row completion convention, fixed VB parent, exact zero boundary, unknownq1,
counterfactual-roster and fee/mark/coverage limits, and staged raw-versus-protected distinction. Its
initial50active-feature-DAYS/3years test is explicitly only an upper-bound support screen; later
SOURCE must separately require>=100 unique qualifying first-signal dates and>=50selected dates,
matched-mask support and valid execution paths. Fifty negative-variance days without VB signals
would not establish fifty candidate trades.

Root's declared prior-row completion convention is admissible for this finite SHADOW-BOOK research
scope, conditional on source checks finding no contradictory availability evidence. It does not
authenticate original account receipts or convert inherited equity/booking proxies into actual risk.
The absence of a full core-export builder remains disclosed. Do not silently extrapolate that
conditional admission into an independently verified native-book or funded/evaluation claim.

**Conditional support for a finite SOURCE/count TEST nomination**, preserving those boundaries.
A real owned proxy input, an independently
motivated incremental-risk identity and many possible parent opportunities can justify a falsifiable
test without manufacturing an effect. No measured EXTRA frequency, power, profit, dependence,
placebo or book gain is established. Source/availability or support failure must stop it unchanged.

This is not approval of a final preregistration, source adapter, native execution or promotion.
After any genuine design pass the current book bench must come immediately, before further robustness.
All full-history native-cost significance/DSR, positive design/historical-validation, same-exit placebos,
selection/dependence and fresh independent raw-spec requirements remain. Missing joint account paths
cannot imply funded/evaluation/pass/payout gains. No live or automation action is authorized here.

## Final preregistration SOURCE review

The completed plan `agents/codex/plans/hunt_v2_vb_covariance.md`, SHA256
`8cc27b3126de97fa7260ac37938d2a6148dd7e37d82183f37f7d314e88b0825e`, receives **predata plan-review
PASS** within the conditional research scope above. This is not a FEATURE/source PASS, economic
result, executable implementation check or promotion approval. No actual input or calendar was
opened/applied for this review, and the registry remains unchanged by it.

The plan resolves the review's requested clarifications before registration/data:

- Primary and SUNDAY2 fee1.24 copies both require the pre-existing `d724c7d02b6db71e63ba705079dbea7fefaa42c6b4f436308a28993ca1908803`
  binding; date/header validation and exact frozen19-column roster precede design-only numeric use.
- Full2018–22 normal/early cash-calendar rows are required before feature evaluation. Missing expected
  rows globally veto; extra stored holiday rows remain in the252-row history. No silent compression,
  reindex-as-zero or actual schedule generation before the committed implementation.
- Strict rational delta<0, positive variance, unknown/equalityq1, fixed shadow book and the95%known/
  >=50active-feature-days/3years/nonconstant upper-bound gate are explicit. Later qualifying native
  first-proposal dates have their separate>=100base/>=50selected and matched-support requirements.
- Gross uses first proposal/date without protected reentry membership. All-proposal overlap remains
  diagnostic. Stops/targets and max-three actual tickets are evaluated only after gross authorization.
- The five economic definitions, primary native1.24 fee/.50 adverse tick and four-tick stress, target
  trade-through, entry-active/worse-gap and immediate current-book controls are frozen. Pre-MNQ
  history is labeled counterfactual NQ-price/MNQ-cost research; no historical micro-fill claim.
- Random-time and random-side retain the same protection/flat/cap rules and reexecute membership;
  both total-net **and per-executed-ticket net-mean** p<=.05 are required for each family. Counts,
  gross and fees are reported; undefined/zero-ticket nulls block interpretation without redraw.
  This prevents more null fees from being the sole reason a total-net placebo appears to pass.
- The final tenth hypothesis is completed only as its frozen gates permit, with no eleventh; the
  full bounded summary and continuation pause then follow, or earlier at60 economic evaluations.
  No paused t6/watcher is resumed. Actual future validation remains once, previously seen history.

No fatal inconsistency remains in this reviewed plan. A changed plan hash requires a scoped review
of the change before execution. Root must still commit it, review/commit the feature implementation
and obey all stage gates; unknown activation counts and baseline limits remain real.
