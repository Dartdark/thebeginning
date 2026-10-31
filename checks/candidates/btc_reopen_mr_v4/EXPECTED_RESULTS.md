# Expected results

## REFERENCE ONLY — SPENT RESEARCH PERIOD

Window: **2018-06-11 through 2024-09-01**

Later BTC outcomes (**2024-09-02 through 2026-08-31**) remain sealed / unopened
in the research program and are **not** part of this package.

---

## A) Expected native Ninja Strategy Analyzer result

Commission off / slippage 0 / Standard Last fills.

| Metric | Reference |
| --- | --- |
| Trades | **121** |
| Long | **49** |
| Short | **72** |
| Approx native PnL | **+$31,925** |
| Approx PF | **~2.00** |
| Approx native Strategy Analyzer MaxDD | **~$4,075** |

Sources for these figures include the forum native spent documentation and the
zero-cost 121-trade economics certificate panel.

### Why your native run might differ slightly

Small differences may occur if:

- data vendor differs
- roll / merge data differs
- historical BTC continuous series differs
- spot BTCUSD mapping differs
- Trading Hours template differs
- Ninja historical data revisions differ

Investigate data/identity/merge first. **Do not tune parameters to force parity.**

---

## B) Realistic execution warning (NOT reproduced by this package)

The native result is **NOT** the economically realistic headline result.

Matched realistic-execution panel (external synchronous-BBO reconstruction):

| Track | Trades | PnL | PF | MaxDD |
| --- | ---: | ---: | ---: | ---: |
| Same-panel native (Last fills on 118 BBO-valid trade IDs) | 118 | +$30,475 | (panel) | (panel) |
| External synchronous-BBO + Ninja Lifetime commission | 118 | **+$10,877.20** | **1.2653** | **$6,354.40** |

Interpretation:

- Realistic execution removed roughly **~64%** of the same-panel native PnL
  (30475 -> 10877.20).
- The realistic BBO reconstruction used **external** historical order-book / BBO
  data.
- That external data is **NOT** included here and must **not** be redistributed
  from proprietary vendor archives via this package.

Do **not** change Slippage / Commission / strategy logic inside Strategy Analyzer
merely to force-match the Lifetime BBO reconstruction.
