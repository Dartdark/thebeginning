# Codex: status and history (written by Claude, 2026-10-22)

## Setup
- Codex (OpenAI) is the **strategy builder** since 2026-10-22; Claude reviews and checks everything; the user decides.
- Brief: `agents/codex/BUILDER_BRIEF.md` (entry point `AGENTS.md`). Works on branch **`codex/work`**, writes only under
  `agents/codex/`, `analysis/codex_*`, `analysis/outputs/codex_*`; never touches live trading, the VPS or `claude/*`.
- Runs in the Codex app (local project `C:\CodexRepo`, or cloud). `C:\TradingVault` stays the journal vault only.

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
