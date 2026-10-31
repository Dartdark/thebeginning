# H09 MES helpers: source/synthetic review PASS, admission still required

This is an independent source and invented-input check of the two helpers below, before any actual ES input header, schema, row, price, ATR, event count, endpoint return, schedule generation, or financial study was accessed by this reviewer. It is **not** a source-admission PASS, a design result, a book improvement, MC parity or permission to advance past an unsuccessful source/support gate. The main admission implementation and final committed preregistration remain separate review targets.

Reviewed source: literal functional PL from Git blob `33e4a6a1c57dc0867d6ee9b26c310879ebd08f18`, `funded_strategies/ES_MOC_Follow.txt`, pinned adopted commit `d14dc9a153df128aafd3f48d4fea2aa78b88bb28`. The reviewer read code, including shared calendar implementation constants, but did not generate or apply an actual date schedule. Prior source performance comments were not used to certify this check. Budget unchanged: **5 economic evaluations / 8 registered hypotheses / 4 gross screens**, plus the archived t6 history; this review adds none.

## Bound code

| File | SHA256 |
|---|---|
| `analysis/codex_hunt_v2_mes_parent.py` | `b69057f5967a35d45619a60476c4a821edccda6e578483ce4c34044ae56302c3` |
| `analysis/codex_hunt_v2_mes_execution.py` | `3e805d34ec3f92fd099cde61c3d2d817daa8d792fab39a2bdb34fbc80e311079` |
| Shared `analysis/grid.py` | `a30ddd4533c9b9d9bdd50f161deded3a2864605f1b81bf4605f74b1d23bc7405` |
| Shared calendar source `analysis/codex_s03_calendar.py` | `705713195b1be61cd648d1b72718442b6cec7581587ca8c537d491cf1312bceb` |

## Findings

- The parent preserves the PL's observed five-minute chart-date state: midnight belongs to the new date, prior weekday TRs enter the 15-item ring only on the subsequent observed date, and the `DayClose > 0` guard wraps `PrevDayClose` updates too. A Sunday observed close changes the next weekday's previous-close reference without being counted as a weekday TR. Partial historical chart bars remain flagged; no complete-feed claim follows.
- Reference C1400, decision C1450, the `.30 * ATR` signed-move condition, native next-open O1451 and fixed C1500 endpoint match the source clock convention. Same-date future bars cannot change an already recorded decision, ATR or size. A reference/decision made from a partial bar remains provisional and flagged. The helper intentionally does not discover entirely absent expected dates; the caller must do so.
- Affordability uses the **native-ceiled** protective distance `D = ceil(A) * .25`, then `2 * (5 * D + 3.74) <= 250`. Exact rational arithmetic correctly permits A=97 and rejects any positive amount above 97 after tick rounding. The source nomination's unrounded shorthand must not override this helper or the final plan. A minimum one MES remains even when its planned loss exceeds the research allowance; it is not a hard risk cap.
- The execution helper clones shared `grid.execute` globals and calls the unmodified raw-path shared walk. It anchors the stop on the adverse executed entry, charges adverse exit once, and computes MES cashflows directly at $5 per point with $1.24 round-trip commission. It does not divide an ES net result by ten or double-charge entry slippage.
- Entry-bar protection is active. When adverse entry slippage leaves the raw entry OPEN already through the anchored stop, the exit uses that worse raw OPEN, followed by adverse cover/sale slippage. Later open gaps use the shared walk's worse-open treatment. Stop protection remains active throughout the C1500 minute before a surviving time exit. Target-through is N/A because there is no target.
- Four-tick stress changes entry fill and stop anchor, so it can change the stop reached. It is correctly a separate frozen execution definition rather than identical-path fee repricing. Quantities must remain frozen from the primary affordability feature.
- Missing exact entry/held/time bars, invalid native quotes, fractional/zero quantities, changed clocks/stop/target and duplicate-date tickets are rejected. Source grid arrays and shared globals remain unchanged. The per-trade excursion output is explicitly not a valid joint account path.

Bundled artificial fixtures passed: parent five groups and execution ten groups. An additional independent analytic stop-only oracle matched **400 invented paths**: both directions, primary one-tick and fixed four-tick fills, 100 deterministic random paths in each combination. Exact affordability-boundary and future-bar-poison checks also passed. These are software checks, not market observations or economic evaluations.

## Required caller boundaries

The helper's candidate list is provisional. Before any raw endpoints or stop outcomes, admission must bind explicit allowed files and dependencies, validate all raw rows/duplicates/clock/source eras, audit every expected normal decision date, resolve source/calendar contradictions, enforce exact reference/decision/entry/held paths and all frozen support/null-combinatorial gates. Shared `g.trading`, future last-bar membership, forward filling and later endpoint fallback must not decide eligibility. A shared cash-calendar exclusion can differ from the literal PL predicate; contradictory observed qualifying dates require explicit source adjudication rather than quiet deletion. Native ES proxy history, MES prelisting/liquidity, receipt and incomplete past ATR-source limits remain limits.

No actual gross/stopped metrics, 2023+ validation, book bench, placebo, funded/evaluation path, PowerLanguage draft or promotion was run in this review. A changed helper hash invalidates this binding until the change is reviewed.

## Initial preregistration source review

Reviewed the subsequently written `plans/hunt_v2_mes_moc_affordability.md` before actual inputs. Its conservative normal-cash calendar guard is explicitly a frozen research port in addition to the literal PL predicate. That disclosed choice is not itself a fatal source mismatch or a claim of MC parity. Keep literal/shared disagreements and unexpected observations visible; missing references on a normal eligible date still block globally.

Two placebo details were sent to root for clarification **before commitment/new inputs**:

1. A random earlier entry must not be restricted to dates that qualify for the actual strategy at the future C1450 decision. Such future event-date membership leaks even if direction is recomputed at the earlier clock. The random-date pool must be normal eligible dates selected without future C1450 qualification, membership or side, with ATR/quantity known causally for the sampled date. Fix the native decision/next-open/end keys and missingness treatment.
2. The user requires identical exits. A shifted ten-minute window changes the strategy's fixed C1500 time exit. For the required random-time test, retain the same active stop and exact C1500 terminal exit while randomizing only the causal entry time; a shifted ten-minute exit may be a separately labelled supplemental diagnostic but cannot replace the required same-exit check.

These affect future promotion placebos, not the pure helpers' invented-input PASS. No actual returns were used to choose this correction. Final plan and actual placebo implementation require a matching review before those phases.

**Final pre-input plan review: PASS for the corrected preregistration**, SHA256 `2ae71ec9c6d3b479b9d780e5fdda2b662393a70da7d5d82a1c208df21f3349a3`. The corrected recipe samples distinct normal-cash dates uniformly within each year, matching actual EXTRA counts, without future C1450 signal/event membership or side. Affordability comes from that sampled date's causal prior ATR and the frozen slice. Sampled decisions C1300..C1450 in five-minute steps use their own preceding 50-minute close move (zero receives a uniform random sign), no original signal threshold, exact next native OPEN, the sampled date's rounded quarter-ATR stop and **the same fixed C1500 exit**. Required source missingness blocks instead of triggering a redraw. Uniform original-entry random-side paths retain identical stop/time/fill/fee rules. Both required total-net empirical p values use the frozen 1,000 draws, seed2026102719 and `(1 + #nulltotalnet >= actualtotalnet) / 1001`. This resolves both initial findings before actual inputs/returns; the findings remain recorded as review history. The eventual implementation must still be checked against this exact recipe before placebo execution.

## Reproduce the independent invented-path check

Run from repository root with `/workspace/venvs/thebeginning/bin/python -B`; the script below reads no data files or schedule. The helpers' own fixtures can be reproduced with `-B analysis/codex_hunt_v2_mes_parent.py --fixtures` and `-B analysis/codex_hunt_v2_mes_execution.py`. Runtime cache location is fixed by the execution helper under `analysis/outputs/codex_hunt_v2_mes_affordability/cache/numba`; the reviewed path used the Python shared walk, not compilation.

```python
import sys, math
sys.dont_write_bytecode = True
sys.path.insert(0, 'analysis')
import codex_hunt_v2_mes_parent as p
import codex_hunt_v2_mes_execution as e
import numpy as np
import pandas as pd
from types import SimpleNamespace
from fractions import Fraction
from datetime import date, timedelta

assert p.fixtures()['passed'] and e.fixtures()['passed']
rng = np.random.default_rng(314159)
n = 0
for side in (-1, 1):
    for slip in (1, 4):
        for _ in range(100):
            atr = Fraction(int(rng.integers(1, 800)), 20)
            distance = math.ceil(atr) * .25
            shape = (1, 1440)
            a = {name: np.full(shape, 100.) for name in ('o','h','l','c')}
            for j in range(891, 901):
                op = 100 + int(rng.integers(-24, 25)) * .25
                close = op + int(rng.integers(-8, 9)) * .25
                a['o'][0,j], a['c'][0,j] = op, close
                a['h'][0,j] = max(op,close) + int(rng.integers(0,9)) * .25
                a['l'][0,j] = min(op,close) - int(rng.integers(0,9)) * .25
            g = SimpleNamespace(**a, v=np.ones(shape),
                ts=np.array([np.datetime64('2000-03-15')]), last_j=np.array([1439]))
            entry = a['o'][0,891] + side * slip * .25
            stop = entry - side * distance
            xj, kind, raw_exit = 900, 2, a['c'][0,900]
            for j in range(891, 901):
                op = a['o'][0,j]
                through = op <= stop if side == 1 else op >= stop
                touched = a['l'][0,j] <= stop if side == 1 else a['h'][0,j] >= stop
                if through or touched:
                    xj, kind, raw_exit = j, 0, op if through else stop
                    break
            expected_net = side * ((raw_exit - side*slip*.25) - entry) * 5 - 1.24
            signals = pd.DataFrame([dict(day=0,dj=890,side=side,atr=float(atr),
                atr_exact=str(atr),stop_points=distance,exit_j=900,qty=1)])
            actual = e.execute_mes(g, signals, slippage_ticks=slip)[0].iloc[0]
            assert actual.exit_j == xj and actual.kind == kind
            assert abs(actual.net_mes - expected_net) < 1e-9
            n += 1
assert n == 400
assert p.affordability(Fraction(97))['qty_extra'] == 1
assert p.affordability(Fraction(970000000000000001,10000000000000000))['qty_extra'] == 0
assert p.affordability(Fraction(97))['planned_two_mes_risk'] == 249.98

def bar(day,j,hi=101,lo=99,cl=100):
    return dict(date=day,minute=j,open=100,high=hi,low=lo,close=cl,
        bar_id=day+':'+str(j),complete_five_minutes=True,
        exact_native_close_present=True,source_ids=['INVENTED'])
history = []
for off in range(60):
    d = date(2000,1,1) + timedelta(days=off)
    if d.weekday() < 5:
        history.append(bar(d.isoformat(),600))
day = '2000-03-15'
calendar = lambda d: dict(kind='normal',cash_close_j=900,reason='INVENTED')
decision = [bar(day,840),bar(day,890,hi=101,cl=101)]
base = p.reconstruct_parent(history+decision,calendar_auditor=calendar)
future = p.reconstruct_parent(history+decision+[bar(day,1435,hi=10000,lo=1,cl=500)],
    calendar_auditor=calendar)
assert base['candidates'] == future['candidates']
assert base['candidates'][0]['atr_exact'] == '2/1'
assert all(ref != 'CT5M_TR:'+day for ref in base['candidates'][0]['atr_reference_ids'])
```
