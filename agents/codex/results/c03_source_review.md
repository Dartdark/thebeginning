# C03: WATCH — improves several Kusho mechanics, but is a different rule with unresolved execution

Summary: C03 is an ATR-based Kusho redesign, not the earlier reported 15:45 flattening version.
It checks positive swing risk, tracks favorable excursion after the fill minute and broadens roll/calendar handling.
It still deliberately delays protective orders until the fill's 15-minute slot ends.
Early-close pending orders, missing-slot expiry, exact-close execution and native MNQ compatibility remain open.
Get C03's own native report/settings before assigning performance or changing its rules.

Plan: not applicable — source review, no new strategy return test. Evidence: `agents/codex/evidence/c03.md`.
Script: `analysis/codex_c03_source_audit.py`; input: `agents/codex/inputs/c03/source.txt`;
output: `analysis/outputs/codex_c03_source_audit/`. **New strategy return trials: 0**.
No prices/cache, strategy replay, compiler, MultiCharts, account simulation, broker or live system was used.

## What changed from the supplied Kusho files

| Feature | Kusho FAR/v9 | C03 |
|---|---|---|
| Engine | Native 15-minute chart; fill magnification described separately | One-minute chart; completed 15-minute slots constructed in code |
| Wick threshold | 70 ticks | 0.5 ATR15 by default |
| Structural level | Most recent qualifying fractal among bars 2-10 | Minimum/maximum of nine bars preceding the signal |
| Risk/fallback | Maximum 500 ticks; fallback 200 ticks | Positive risk capped at 3 ATR; fallback 1 ATR |
| Break-even offset | Five ticks; whole current bar extreme | 0.05 ATR; excludes fill-minute extrema |
| Flatten | Evening 21:00 with weekend carry | Regular 15:45; earlier scheduled closes |
| Roll handling | V9 corrects daily regime closes only | Roll-adjusted constructed OHLC, EMA, ATR, swing history and regime closes |

These changes alter signals, trade frequency, exits and risk. The earlier PDF's $27,203/84%-retention comparison
does **not** establish C03's performance. No result table or native report for this version was supplied.
Source comments mention already-tested RR and wick values; full prior trial history remains unknown.

## Improvements visible in the code

Line references below use the preserved C03 source, unchanged from the upload.

- **Positive swing risk (305-315):** wrong-side/zero risk now selects the fallback rather than accepting an
  invalid structural bracket. This addresses the earlier Kusho missing lower-bound check.
- **Excursion chronology (508-512):** the fill minute is excluded, preventing its pre-fill high/low from
  arming break-even. This conservatively also omits real favorable movement later in that same minute;
  it is a declared approximation, not tick-level fill sequencing.
- **Causal construction:** completed observed bars feed EMA/ATR and prior-nine-bar extrema. The short regime
  uses completed prior-session closes. No obvious default signal-time look-ahead was found. Late completion
  of a missing slot-end is logged rather than pretending its close was observed on time.
- **Broader data handling:** the adjusted OHLC also feeds multi-bar indicators (436-476), addressing more than
  v9's daily regime correction. The holiday calendar is fuller. Feed-specific splice assertions still require
  empirical verification; code complexity does not establish parity.

## Material issues still open

1. **Unprotected fill slot is deliberate.** IOG is explicitly off (34). `ProtOn=false` at 319 only becomes true
   at the slot-close condition (514-515); stops and targets then start next bar (528-534). An entry in the first
   minute of a slot can wait almost 15 minutes for protection. The one-minute chart does not remove that gap.
   An immediate backstop would be a separately specified implementation, not a faithful replay of this file.
2. **Deadline does not prevent pending entries.** The flat condition only handles an open position (523-527).
   Signal arming (481-500) and submission (540-544) have no flat-time/closed-day/armed-date veto. A qualifying
   terminal 12:00/12:15 half-day bar is inside the allowed signal window and can arm a next-bar limit. New-day
   bookkeeping does not clear `Armed`; fill detection records the fill's current date. Depending on platform
   session/TIF cancellation, a pending order may reach the evening reopen. This is a code-permitted path,
   not an observed historical fill count or an assertion that every platform configuration leaks entries.
3. **Missing slot end can extend order lifetime.** A limit reissued at 09:14 can reach the next observed 09:16
   bar when 09:15 is missing. Fill detection precedes the late-expiry update. Verify actual session/expiry
   semantics and retain gap diagnostics. Incomplete slots are accepted; entirely absent slots are skipped,
   so indicator observations are data bars rather than guaranteed complete calendar slots.
4. **Flattening and stop fallback are unverified.** Both time exits use `this bar on close` (525/527), including
   the scheduled early-close boundary with no advance margin. This historical close assumption does not prove
   executable automation. A missing deadline bar can defer the exit until after the intended hold. There is
   also no explicit market fallback for a raised stop already through the market.
5. **Native MNQ chart is rejected.** The guard at 213-214 requires $20 per point. Native MNQ is $2 per point;
   the title's NQ/MNQ wording does not make this a direct micro-chart implementation. Preserve correct symbol
   specifications; do not change MNQ's genuine point value to bypass the guard. NQ analytic results and a
   verified MNQ implementation/cost schedule are separate questions.
6. **Roll logic is source-specific.** Hard-coded 2024 exceptions and the later schedule are claims to verify
   against the exact feed. Intended intraday flatness normally avoids open positions at splice times, but an
   accidental carry defeats that assumption: existing raw entry/stop/target prices and MFE are not rebased by
   subsequent `CumGap` changes. No held-contract roll accounting was verified here.

The synthetic examples in the output explain possible code paths only. They contain no market prices from
the repo, backtest returns, loss estimates or measured defect frequencies.

## Evidence status and next step

This remains a Kusho-family price-pattern trial. The parent overview already lists unsuccessful ATR and
one-minute variations; neither their failures nor the parent's S label determine this exact version's result.
No exact C03 ranked/watchlist entry was found at Claude `e7c394f`. The US-session window still overlaps the
existing NQ book; no correlation, occupancy percentage or incremental account result was computed.

Obtain C03's native report/Settings, source/version identity, actual chart/symbol assumptions and prior trial
record. Verify compile/parity on ordinary sessions, half-days, missing endpoints and roll dates. Then freeze
any protection/cancellation/executable-exit amendment as a separate version before another return test. Do not
attribute the older flattening results or an Apex-ready label to this source alone. No strategy, plan or live
file was changed, and source instructions about auto-trading modes were not executed.

Reproduce source/default/guard extraction and illustrative order-state cases with:
`/workspace/venvs/thebeginning/bin/python analysis/codex_c03_source_audit.py`.

Tell Claude: review `agents/codex/results/c03_source_review.md` and `agents/codex/evidence/c03.md`; C03 is a
separate ATR variant, with delayed protection and pending-entry deadline/expiry paths to verify before returns.
