# Codex: status and history (written by Claude, 2026-10-22)

## Setup
- Codex (OpenAI) is the **strategy builder** since 2026-10-22; Claude reviews and checks everything; the user decides.
- Brief: `agents/codex/BUILDER_BRIEF.md` (entry point `AGENTS.md`). Works on branch **`codex/work`**, writes only under
  `agents/codex/`, `analysis/codex_*`, `analysis/outputs/codex_*`; never touches live trading, the VPS or `claude/*`.
- Runs in the Codex app (local project `C:\CodexRepo`, or cloud). `C:\TradingVault` stays the journal vault only.
- Model (user's screenshot, 2026-10-24): **GPT-6.1 Sol**, effort setting 'Light', in the Codex app's cloud mode with the
  `thebeginning` environment. Mailbox thread for @codex mentions was PR #2 (closed unmerged 2026-10-24).
- **@codex mailbox attempt (2026-10-24): not working.** 7 test mentions on PR #2; each time the connector answered only
  'create an environment for this repo', even with two GitHub-linked cloud environments for Dartdark/thebeginning listed
  (Codex: mentions use the legacy Codex Cloud, environments were made in the newer system). Stopped retrying; next step
  would be OpenAI Support (legacy environment ID + the latest failed connector reply). File relay used meanwhile
  (`agents/codex/NOTE_mailbox_setup_2026-10-24.md`).

## Tests (blind, branch `codex/tests`): both PASS (`agents/codex/results/GRADES.md`)
- Test 1, Antigravity's Vault Break Combined claim: REJECT with every key finding (worse on 2023+, removed trades
  profitable, drawdown cut = random, 2 MNQ arithmetic error) and more (funded bench, MultiCharts parity).
- Test 2, Antigravity's PowerLanguage code: caught all 7 issues (30-min ATR, unprotected entry bar, trade counter,
  holidays, warm-up, volume, no look-ahead) and wrote a corrected version.

## Studies since (all rejected cheaply and honestly; reviews in `agents/codex/results/REVIEW_*.md`)

| Study | Result | Lesson added to the brief |
|---|---|---|
| Overlap risk cap / ES MOC size | REJECT | — |
| Marginal contribution of each plan strategy | No removal passed: keep all 10, ES MOC 2 MES | Its "VB overlap sizing next" not accepted (not pre-registered; VB's overlap days are its best) |
| London FX-fix reversal (6E) | F: no gross edge | Screen gross-vs-costs first; aim at intraday gaps; prefer flows forced today |
| Shanghai gold delivery deadline (GC) | F: no gross edge | Built the plan's minute-by-minute occupancy map (useful) |
| FOMC minutes reaction (NQ) | F: 19 trades, t 0.14 | Power check before testing; never select events on the plan's own positions |

## Process upgrade (2026-10-22)
- **Evidence sheet first** (brief step 0): who is forced to trade, direction / size / timing known beforehand, reaches
  NQ / ES directly, data that separates it from momentum, beats costs in a real gap, **power**, already tested?
- **Forward log** (`agents/codex/FORWARD_LOG.md`): 2023+ is worn out; any pass is frozen and paper-tracked first.

## Evidence-sheet competition (`agents/claude_evidence/COMPARISON.md`)
- Both independently converged on **auction imbalance data** and **leveraged-ETF rebalancing sized by fund assets**.
  Codex: deeper on data traps and more original; Claude: power numbers and decision-ready verdicts.
- Agreed order: (1) LETF data feasibility → (2) auction data feasibility → (3) Codex's SPX expiry-hedge idea.

## Where things stand
1. **LETF data: free and clean** (`data/letf/`, ProShares daily assets since inception; reset demand per 1% move grew
   ~8x since 2018). Codex pre-registered the **Late-Day Flow sizing test** (1/2/3 MNQ by flow rank; zero returns run).
   Claude approved **with 3 changes** before any return (`REVIEW_ldf_flow_sizing_prereg.md`): 2017 warm-up data
   (user export), momentum controls (the flow rank correlates 0.38 with the trailing 63-day NQ return), and a
   passable data gate (prior-day assets + two-day lag stress).
2. **Auction data: expensive at list price** (~$52k SPY/Arca + ~$58k NYSE for 2018-26). Email NYSE for a SPY-only
   quote and free sample before anything else.
3. Nothing has changed in the live plan.

## Update 2026-10-22: LDF flow sizing REJECTED at design
Incremental t 0.30; momentum-adjusted high − low −$54 per NQ (t −0.49); placebo p 0.45; D−2 stress fails. LDF stays 2 MNQ.
Claude's own slip: asking for a 252-session momentum control meant the May-2017 export only warmed up from May 2018,
so 38 early-2018 trades were excluded. With the point estimate negative, more trades would not change the verdict.
Next on the agreed list: auction data (waiting on NYSE's reply), then Codex's SPX expiry-hedge idea.

## Update 2026-10-22: live audit + free-data sheets
Live audit useful (logger = chart state, not fills; false MISMATCH / REJECTED alarms fixed in `analysis/vps_health.py`).
Free-data sheets: both DON'T TEST. Research paused until new data or a strong outside idea; Codex's next work = live
reconciliation and monitoring (`REVIEW_live_audit_free_data.md`).

## Previous message for Codex
```
Review in agents/codex/results/REVIEW_ldf_flow_sizing_prereg.md (claude branch). Amend the plan before any return:
(1) 2017 NQ daytime warm-up (user exporting NQ_1min_2017.csv) or register the later start openly; (2) add trailing
63/252-session NQ returns to the gate-4 regression and a trailing-63 tercile to the gate-5 placebo cells, and report
the rank's correlation with them first; (3) data gate: D-1 assets + the two-session lag stress suffice for an
exploratory design screen; start archiving dated fund snapshots. Commit the amendment, then run the 2018-22 screen
once NQ_1min_2017.csv is in data/.
```

## Update 2026-10-22 (evening): break test, execution diagnostics, two gold screens
- ONB ADX30 break test: BENDS on noise / indicators / timing / execution; joint jitter MIXED (session-clock shifts). No change.
- VB: parity 97.5% < 98%: MC fills targets with 1 tick through, Python needs 1 point. Codex to rerun with a parity-only
  1-tick setting under the original gate, then the frozen VB stress families.
- Execution diagnostics accepted (observation only); bid/ask logger stays a proposal (test chart first).
- RSI/Bollinger (GC, NQ) and XAU ST Break Free (GC): both F. Review: `REVIEW_break_vb_onb_and_rest.md`.

## Update 2026-10-22 (late): VB parity + stress accepted; ES Keltner guess F
- VB: MC parity 99.6% with the 1-tick target rule; stress same as ONB (BENDS, jitter MIXED). No change.
- ES Keltner tested with Codex's own settings at the user's request: F for that version; Davey's own stays open.

## Update 2026-10-24 (Claude read codex/work up to 541d111)
13 studies of user uploads, all pre-registered where returns were run; none changes a plan. Return tests: S03 v2 (B by
numbers, t 3.73, DSR 0.855, no placement), NQDB2 (C, VB variant, veto fails), R2Vault (C), ORPullback (D), Anson (D),
night volume switch (= Claude's T_ONESIDE, B; Codex: + 1 MNQ funded 1y +$345, 2y +$25 [−$124, +$180], WATCH; consistent
with Claude's bench). Source reviews only (no code / data to test): Valeris 848 (REJECT, 2.4M combinations, OOS t fails),
GC risk-adjusted (REJECT, $20k risk budget), noise-band CODE.txt (REJECT, $2,000 stop), NQ PROP ORB (WATCH, no SL70
results), GC_COMBO v2 (WATCH; Claude since got the MC report: C, worse on the funded bench), Overnight TickRSV/VIX
(WATCH: needs the code and report). Data note from NQDB2: two missing 1-2 minute bars in data/NQ_1min (2018-07-26
13:43-13:44, 2025-06-02 11:03) plus the known 15:16-15:30 day/night seam; minor, not a defect that changes results.

## Codex 2026-10-25 (codex/work db1c88b), read by Claude 2026-10-25
- **NQ Day Flow Six (WATCH):** the plan's six intraday NQ legs (VB, ONB ML v2, Monday Long, EOS, LDF, NFP) at 1 MNQ each from
  their MC tickets: 3,615 trades, $7.9k a year, Sharpe 2.37, adjusted t 6.77, closed-EOD DD $2.6k; 2018 −$342, 4-tick stress
  t 5.89. Not new alpha: a recombination of legs already in the funded plan (personal REPLACE = −$67 a year, i.e. the same
  thing). **Useful by-product:** two MC tickets held through a session halt: Monday Long 2023-07-03 (early close, out 17:05)
  and NFP Fade 2023-04-07 (Good Friday, out Sunday 17:05). Claude confirmed both in the MC lists (only these two across all
  nine plan lists) and fixed the code (Monday Long skips Jul 3 / Dec 24 Mondays, NFP Fade skips Good Friday); paste in
  `TODO.md`; `MULTICHARTS_PITFALLS.md` entry added.
- Swing Target and Overnight Rebound: already handled on the Claude branch (TIER_LIST rows; Swing Target v3 in the plans).

## Codex 2026-10-26 overnight (codex/work 63f557d), read by Claude 2026-10-26: the standalone t6 program
User mandate to Codex (2026-10-25): keep researching until a NEW standalone strategy reaches trade t and daily NW(5) t >= 6.
14 pre-registered hypotheses, 65 counted evaluations (63 unique), **none passes**; every rejection stopped at the 2018-22
design screen except two: Opening Path Persistence (design t 4.19 -> 2023+ t 1.27, full 3.67: decayed, not retuned) and
Opening Pressure (CP5 t 2.52; its OWN5 control t 4.19 is result-informed, a lead only). Two data gates blocked: EIA
inventory components (eia.gov not reachable from Codex's environment) and forward-guidance revisions (no clean source).
Claude's view: process is clean (pre-registration, design-first stop rules, trial ledger). A standalone t >= 6 is about
2x the best strategy in the book (VB t 4.6; whole 6-leg plan t 6.8); each failed trial raises the multiple-testing bar
for the next. Suggested to the user: cap the program or redirect it (e.g. data the book lacks, or confirmation of B items).

## Update 2026-10-29 (Claude read codex/work up to 72d5ecf, ~60 commits since 10/25): nothing passes, plans unchanged
- **Strategy Hunt v2:** 10 hypotheses (H01-H10), final audit PASS = no qualifying strategy.
- **User uploads tested:** NQ gap-down long REJECT (t 1.19, random-side p 0.13; author's $602k not reproduced);
  ORB30 EMA WATCH (PF 1.31 design / 1.21 validation, no plan gain, no MC parity); PrimeSync WATCH (no plan clears the
  placement gates); six-leg euro package fails the frozen design gate (t 2.2, Weekly Breakout loses); hourly CHoCH
  rejected (t 1.22; random-side p 0.11, random-delay p 0.21); FOMC monthly-coefficient paper DON'T TEST.
- **Built, not installed:** Shared Target Guard v1 (one balance entry per account for all its charts; monitor-first).
  Worth a look with the Chart Monitor's Rithmic balances.
- **In progress:** Evening Repair (preregistered 10/29 07:09; source-only scope frozen 07:40; no returns yet).
- **Conflict:** Codex recorded (10/28) a preference to paste complete code in chat; the user's rule since 10/29 is links
  only (CLAUDE.md 'Code in chat'). Tell Codex.
- **Target Guard review (Claude, 2026-10-29):** Codex's Shared Target Guard v1 (Python writer + INI per account, one manual
  balance a session) is sound but needs a daily manual entry and an untested INI read in PowerLanguage. Superseded by
  `apex_strategies/Apex_Target_Guard_v2.txt`: Rithmic reports the account balance as Equity (NetWorth is 0 for Apex), so
  the guard reads it itself, no typing, and with open P&L included it guards the account's target, not one chart's.
  Not installed until the next live trade shows whether Equity includes open P&L. Codex's 14 checks remain a useful
  reference (tick rounding, already-met target).

## Update 2026-11-10 (Claude read codex/work b44f159b; summaries read, no Codex script rerun)
- **VB split stop** (7 of 15 MNQ out at -37.5 pts): REJECT, 150K design pass 38.3 -> 35.7% (adverse DLL fills 35.0 -> 33.8%);
  VB removed entirely 31.9%: VB earns its place. Agrees with Claude's earlier VB loss-trim results.
- **VB / ONB tail review + dot loss map:** the 4 lost accounts had an ONB stop larger than the cushion left (e.g. $1,940 room vs
  $2,478 risk). No costless fix found; finish mode (adopted) is the best lead. Claude's 11/08 cushion-cap bench already covered the
  'cap the stop at the room' idea for evaluations (fewer fails, fewer passes: not adopted); funded charts have the cushion guard.
- **New-data strategies (NY Fed funding, VIX9D):** 3 arms, all fail design; best pre-open fear rebound t 1.47 at 1 MNQ (gate 2.5).
- **Gold crowded-long liquidation:** feasibility census fails (38 events 2018-22); no returns run. Claude's papers_1110 COT test
  had GC alone t 2.5 for fading weekly non-commercial changes (1 of 8 markets, not an item): a different signal; note only.
- **Papers:** NG informed-forecast (SSRN 2826684) WATCH / needs analyst forecast data; five commodity-curve papers (2485314 etc.)
  need a contract panel; dot's validation audit adds that basis-momentum weakened in later samples (Baba-Yara & Bondatti, SSRN
  4345427) and that 'A Tale of Two Premiums Revisited' (2023) supports the weekly position-change premium (no executable timing).
  Same verdicts as Claude's batches today (TIER_LIST basis-momentum / relative basis / KRT / FX sessions rows).
- **Whop / Unbiased Trading reviews:** one lead, MNQ two-bar compression (community claim PF 1.59 on 110 trades): unverified.
- Nothing changes in any plan.
