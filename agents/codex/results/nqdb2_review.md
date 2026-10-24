# NQDB2: WATCH as a Vault Break variant; improvement unverified

Summary: DriftBreak v2 is a Vault Break v8-family strategy with a four-bar downside-drift veto, not a new independent exposure.
The new veto has no supplied performance evidence; older v8 results were weaker than v1 and cannot decide this version.
Dollar brackets are $800/$1,500 per contract: 40/75 points on NQ, but 400/750 if the chart is switched unchanged to MNQ.
Keep the plan unchanged; confirm source/settings and isolate the veto before any claim that it improves our Vault Break.

Scope: `agents/codex/plans/nqdb2_source_review.md`; evidence: `agents/codex/evidence/nqdb2.md`.
Inputs: `agents/codex/inputs/nqdb2/`; script/output: `analysis/codex_nqdb2_review.py`,
`analysis/outputs/codex_nqdb2_review/summary.json`. New strategy-return trials / account simulations: **0 / 0**.
Context: Claude `febc65f1573040abf9a697d1d3468e1bce48c4c0`, Codex `73a5f242cd4dfb549507e24eea1a6bdae0663e65`.

## Rule as delivered

The trimmed header specifies @NQ, 30-minute, Central time, one-minute Bar Magnifier. Long when a close is above the
first calendar-date bar's open plus 0.3 times the mean last 15 date-bucket high-low ranges, and above its date-anchored
VWAP. Decisions are 10:00–14:00 inclusive, at most two order submissions/date; entry next bar, one contract by default.
The default veto rejects four-bar returns <=-0.10%; **slight negative drift is allowed**, not only rising prices.
Four continuous 30-minute bars span two hours; a gap or restricted session can make the elapsed lookback longer.
VWAP slope is diagnostic only. Target/stop $800/$1,500 per contract, seven consecutive closes below VWAP trigger a
market exit; normal flatten from 15:30 is next-bar market. CutoffDate 1991231 corresponds to 2099-12-31, so seal is off.

## Comparison with current Vault Break

Pinned reference: `apex_strategies/NQ_Vault_Break_SP.txt`, blob `c27ca4c4ea32d01e1366efce1bfe06ce68b9770f`.
Source defaults below are not all the current account's configured quantities/overlays.

| Component | Uploaded NQDB2 | Current VB SP source |
|---|---|---|
| Core | Long above noise boundary and VWAP | Same family |
| Boundary | Mean calendar-date H-L; Sunday partials can count | Weekday true ranges, including prior-close gaps; Sunday excluded |
| Added veto | Four bars' price drift <=-0.10% blocks entry | No equivalent gate |
| VWAP | Intraday `Volume` | Intraday `Ticks` |
| Attempts/trades | Two submissions | Three trades, completed/open-position counting |
| Entry cutoff | 14:00 inclusive | Before normal 14:30 cutoff; also last decision14:00 on a regular 30-minute grid |
| Normal flatten | 15:30, next bar | 14:30, bar close |
| Safeguards/overlays | SetExitOnClose and next-date carry guard | Explicit early-close times, stop-rejection guard; SP sizing available |

On the regular :00/:30 bar grid, **both entry-clock conditions admit the same normal decision times**; do not call
this an earlier effective cutoff. Their normal flatten times do differ. Other bar alignments require the actual template.

Latest TIER_LIST row101 already reports Bridge VaultBreak v8, the same range/VWAP-exit family: old mean $82/NQ,
PF1.23 versus v1 $92/PF1.26. That historical comparison favored v1; it **does not test NQDB2's veto or today's plan**.
VB Combined's previously rejected clock/distance filters are also not this veto. No exact drift-veto row was found.

## Source findings and unit checks

1. **Protection is prearmed.** Unconditional built-in stop/target calls at262–264 execute while flat. Multiplying
   per-contract dollar inputs by NumContracts under SetStopPosition is coherent; do not label the first bar unprotected.
   [MultiCharts SetStopLoss](https://www.multicharts.com/trading-software/index.php?title=SetStopLoss).
2. **Dollars versus points need explicit instrument mapping.** At one NQ, $800/$1,500 is 40/75 points. At one MNQ,
   unchanged inputs mean 400/750 points with the same dollar amounts. Two contracts mean $1,600 target/$3,000 nominal
   stop, not a smaller micro risk budget. Current VB expresses 40/75 in points and converts with BigPointValue. This
   arithmetic excludes fees, adverse fills and account rules; no actual loss or recommended size is inferred.
3. **Chart/session and IOG remain material settings.** Calendar Date resets (89,174) are not a Globex/RTH session
   identifier. The session template changes its open/range/VWAP, and missing bars can change the anchor. IOG is not
   forced off. Only VWAPPrev has a per-bar guard (169–172); range insertion, cumulative volume and below-VWAP counting
   can repeat on intrabar calculations. Pin IOG off for the stated bar-based interpretation; one-minute Magnifier alone
   does not redefine decisions as one-minute bars. No platform behavior was tested here.
4. **VWAP weighting differs from ours.** Source181–186 uses Volume; for intraday Trade Volume charts that means
   up-tick volume, while Ticks supplies total volume. Replacing it with an ordinary total-volume Python VWAP changes
   the rule. Existing NQ prices are available; the outstanding issue is exact weighting/MC parity, not buying another
   generic price feed. [MultiCharts Volume](https://www.multicharts.com/trading-software/index.php?title=Volume).
5. **Holiday/live fallback is not established.** No explicit early-close schedule or rejected-stop guard is present.
   SetExitOnClose follows chart sessions and is documented as backtesting compatibility, with real-time last-tick
   rejection risk; it is not evidence of a working holiday exit. A next-date carry guard acts after the carry occurred.
   No realized carry is measured. Next-bar market does not by itself imply a 30-minute physical delay.
   [MultiCharts SetExitOnClose](https://www.multicharts.com/trading-software/index.php?title=SetExitOnClose).
6. **Comments are not authoritative.** LatestEntry is actively tested at240 despite line12 calling it inert. DTrades
   increments when an order is submitted (249–250): rejected attempts can consume the quota, while same-bar filled/
   closed trades are not automatically missed. The untrimmed header and actual settings would settle intended behavior.

## Performance, placebos and account relevance

No results report, exact-version ledger, selection history, confidence intervals, side statistics or account bench was
supplied. Profitability and contribution are **unknown**, not zero. It is long only; short statistics are not applicable.
No hidden holdout remains merely because CutoffDate has a “seal” label. Input comments suggesting 2/4/6-bar searches
are document content, not authorization for new trials.

This largely shares the plan's existing long NQ risk. There is no measured correlation, joint-loss reduction, gap-filling
or payout improvement. A future test should distinguish veto-on/off under otherwise identical source settings before
mixing in current VB's different range, weighting, clock and re-entry rules. For a filter, report total net, removed
trades and their uncertainty, random removals and counterfactual re-entry paths—not only a higher retained-trade mean.
Only after the design gate passes should it face the current-plan addition/replacement/empty-slot account comparison.

## Decision

**Treat as an unvalidated VB improvement candidate. Do not add it as independent diversification or replace live VB.**
First obtain the original untrimmed header, chart session/IOG/volume/fill settings and existing exact-version MC report.
No external GLD signal file is needed here. Any return comparison needs a separate committed preregistration with frozen
settings and trial count. No parameter choice, source repair, new backtest, compile, cache build or live/plan/PR change
occurred. The static audit ran and compiled; two read-only subreviews checked execution and prior-variant context.
