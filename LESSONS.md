# Lessons (short rules learned the hard way)

For the user and for Claude. One line each, newest at the bottom of each section, with the date and where it came from.
Claude adds to this during the Friday review (and whenever a mistake is caught); the user can add or strike lines anytime.

## Trading and evidence
- Evaluations bought days apart are nearly one bet (outcome corr 0.73; half the time a batch of 4 all fails): expect
  whole-batch failures, and space purchases when smoother results matter more than speed (2026-11-01, firm_risk_test.py).
- Saving money is making money: the same return on less capital (or with less drawdown) counts as a real gain (user, 2026-11-01).
- One winning trade is not a strategy; being on the right side at the right time looks like skill. Judge rules over
  hundreds of trades, never by the last trade (user, 2026-10-18).
- Price patterns fail out of sample here again and again; edges that hold have a reason someone is forced to trade at a
  known time (index funds, rebalancing, payroll, weekend flows) (TIER_LIST, 2026-10).
- Stock-level effects ('abnormal returns', 'additions vs deletions') net out in NQ / ES; check that a flow pushes the whole
  index before testing it (Franz index-rebalance paper, 2026-10-18).
- A plan that beats every challenger on the same data is partly home advantage: it was picked on that data. Live results
  decide, by rules written in advance (drift alarm, mid-December gate) (2026-10-18).
- Expect live results below the backtest (published anomalies lose ~26% out of sample, ~58% after publication); the plan
  was sized to still work at 75% (2026-10-18).

## Testing
- Skipping Overnight Bias (or ONB + VB) on a thin cushion doesn't help either: counting unfinished evaluations as lost,
  every rule is worse than trading the full set (50K 1.00 losses per pass vs 1.08-1.76; 150K 1.40 vs 1.54-2.89). Thin
  cushions fail sometimes; the full set is still the best way out (`analysis/onb_cushion_test.py`, after #3 failed 2026-10-30).
- Cutting Vault Break when an evaluation's cushion is thin does not lower the fail rate per pass (0.95-1.02 vs 0.96 for
  VB 8 always; pass 47.7-48.4% vs 50.1%): a thin-cushion evaluation needs the full size to get back up (account #1 fail, 2026-10-26).
- The one-history funded bench overstates swaps: +$700 'gains' at 2 MNQ blew 17-22% on the bootstrapped bench. Decide plan
  changes only on the bootstrapped bench (replacement sweep, 2026-10-18).
- Always test a candidate against the slot left EMPTY, not only against the plan: cutting Vault Break looked like a noise-band
  win until the empty-slot control showed the same result (2026-10-18).
- A candidate can earn its place by replacing, not only by adding (user rule, CLAUDE.md, 2026-10-18).
- Count every variant you looked at; a sub-cut found after seeing results needs an untouched market or period to confirm it
  (the LETF push sub-cut failed on YM, 2026-10-18).
- In an ablation, a setting of 0 must mean 'off': check the code's guard (FC 2B 'no break-even' run armed break-even
  at once and made the exits look essential; the checker caught it) (2026-10-23).
- Book a Sunday-evening exit on the Monday trading date, or daily metrics silently drop it (Kusho, 2026-10-23).
- A path helper must take the instrument's own $ a point: matching trade nets do not prove the intraday worst paths are right
  (twin_continuation_bench.grids marked ES at NQ's $20; Codex 2026-11-08, fixed, MO-on-ES benches rerun).
- Quote a multi-day strategy's drawdown from DAILY MARKS, never from trades booked at exit: S30 IBS < 0.10 showed $24.8k booked vs $45.3k
  marked (2026-11-08, caught via Codex's S30 study). The book tests used marks; the standalone line did not.
- An engine proven on NQ does not transfer to other markets by moving its clock (MO and noise band failed on CL / GC / ZN,
  2026-11-08); the one that transferred (OT on ES) was the same trade. Test a new market's own mechanism instead.
- A daily P&L series must add up to the trade nets (costs, fills, roll jumps): check the totals match before using it for
  sizing or Monte Carlo (S30's first daily series overstated it by ~$3k; Codex caught it, 2026-10-23).

## Research sources
- Read the PDF before trusting a summary: Antigravity misread the FOMC paper's key number (2026-10-18).
- A paper with 'proposed', 'framework', 'may' and no 'we find' has no results (gamma expiration draft, 2026-10-18).
- Check `TIER_LIST.md` for a paper's title / SSRN id before testing: Treasury auctions came back as 'new' (2026-10-18).
- Never attach a finding, number or citation to a source that doesn't state it (Antigravity's invented citations, 2026-10).
- One market out of many is not an edge: Davey's MACD crossover passed 6 of 220 market / bar-size tests (coffee 360-min
  the "best", PF 1.1). Plain indicator entries need a forced-flow reason before we spend a trial on them (2026-10-22).
- A plan near Apex's payout cap can't use a better strategy: FC 2B (A), S47 v2, OB v2 and Kusho all added nothing as
  additions or replacements; judge a candidate on the bench, not on its own t-stat (2026-10-23).
- The small uncorrelated pieces keep the funded plan alive: removing ES MOC alone takes blown 7.0% → 9.5%; replacing a
  'weak' diversifier with a strong same-hours strategy makes the plan worse (2026-10-23).
- Split a multi-day strategy's profit into weekend / weekday and into 'holding the index for the same days' before
  crediting the pattern (Kusho: 40-44% from weekend holds; S30: about half index drift) (2026-10-23).

## Live operations
- After copying a chart set to a new account, check the strategy's Auto Trading account on every chart: account #3's
  copies sent 150K-size orders to #2 (28 MNQ on a 50K, 2026-10-26). The chart-trading panel's account is not the one used.
- A dropped connection costs real trades (missed winner 2026-10-12): reliability (VPS, screen sleep off) beats speed.
- Rithmic rejects stops already through the market: every strategy needs the stop guard (ONB rejection 2026-10-14).
- A copier sends every account the same size; cushion sizing needs per-account groups or multipliers (2026-10-19).
- Copied evaluations pass or fail together; stagger new evaluations 5-10 trading days apart (2026-10-15).
- "Permission denied, contact the FCM" from Rithmic was a wrong password: check the simple things first, and set
  up / test a second machine only after the close (VPS move, 2026-10-19).
- Read the broker's reason before calling it a bug: the 'repeating 0.00 orders' were Apex's daily loss limit
  ('Account is done for day'); after any Apex lock, reset the charts (auto-trading off/on, flat) before the next open (2026-10-19).
- After pasting code, read its first comment lines: "Study is missing Data 2" on FC 2B was the Overnight Sentiment code
  pasted under the FC 2B name (2026-10-23).
- A day-session chart doesn't stop a trade at a holiday's 12:00 halt: FC 2B v1 held 26 holiday trades to the 17:00 reopen;
  every strategy needs the early-close list and an explicit early flatten (2026-10-23).
- (2026-10-26) On a live-account incident, read the evidence (Order Tracker, Logs, the bench's rule file, TODO) BEFORE
  answering. Three wrong guesses in a row (Target Guard, a manual exit, a 'missed' daily loss limit that the 150K bench
  already models) cost the user's trust. Say 'I don't know yet, send X' instead of guessing a cause.
- (2026-10-27) A green AA button doesn't mean the strategy runs: ONB's code hadn't compiled and a +135-pt trade was missed
  (~$4,300 across #2 and #3). Confirm 'compiled successfully' after every paste; trust the missed-trade panel.
- (2026-10-29) An alarm that has never fired is not proven: the VPS watchdog failed to parse for 8 days and sent
  nothing. Test every alert path end to end (watchdog.ps1 -Test, test pushes) when it's built.
- (2026-10-30) Apex enforces the trailing floor intraday: #3 was liquidated mid-trade on a touch of $146,000 even though the
  trail only moves at end of day. Cushion = balance minus floor must cover the worst open loss, not just the day's close.
- (2026-10-30, Friday review) A chart left running for a closed account keeps logging trades and rejections: retire the
  account in `journal_trades.CLOSED` and `live/expected_setup.json` the day it closes, and turn its charts off.
- Never write PowerShell or Windows paths through a Python string: "\2" became an invisible control character and silenced
  the new floor alarm (2026-10-30, Codex cross-review). Use raw strings or write the file directly.
- The weekly review must check Claude's own week of code, not only Codex's: five defects this week were all in new Claude code (2026-10-30).

## Corrections from the user (one line per correction, added in the same reply; user rule 2026-11-01)
- 2026-11-11, user's Orders log ('wait was it a dual thrust trade?'): I said a 2-lot BUY STP on the VB chart came from no strategy. It was Twin's breakout entry: MultiCharts draws every working order of the same account + symbol on EVERY chart. Rule: before calling an order 'not from a strategy', check the Orders / Logs tab's Strategy column and every chart on that symbol, not only the chart it is drawn on.
- 2026-11-06: "lettering is too bold" (re-rendering the edited resume nested bold inside bold rows: Inter-Black). Rule: after re-rendering a document, compare its fonts (pdffonts) and look with the previous approved version before sending.
- 2026-11-09: "80 is a legit improvement. Yea it's still negative in 18-22 but it's less negative so it still is an improvement" (I judged a
  variant only against the book and missed that it beats the current version in every period). Rule: judge a variant on TWO bars - vs
  the current version of the piece (is it better in both periods?) and vs the book (does adding it help?) - and report both.
- 2026-11-08: "the job doesnt start till the 10th and first payday likely wont be till the 17th" (I called Friday 11/13 'Friday's purchase' from an old alert). Rule: dates of the user's money / job come from the user's latest words, not from an old alert or to-do; say 'per the to-do' and ask when unsure.
- 2026-11-06: "university of san francisco" (I expanded "USF" to South Florida). Rule: never expand an abbreviation or fill a fact about the user (school, employer, dates) by guessing; ask, or keep it exactly as they wrote it.
- (2026-10-30, "you sent me the v2 version") Before sending a deliverable, open the exact file being sent and check its
- 2026-11-01: "cmon this is money on the line i need u to be tight especially on checking multicharts". Rule: every MultiCharts claim says its source (screenshot / code line / log field + what writes it) and VERIFIED or GUESS; never send the user to change a live setting on a guess.
- 2026-11-01: "i alr did?" (I said the x150 charts routed to closed #3 from the ACCT log rows; those rows show the Chart Monitor's typed AccountName input, not the order routing). Rule: know what a log field measures before calling it a defect; ACCT.account = monitor input only.
- 2026-11-01: "dont drop it i want to do it" (I removed the VPS screenshot after Defender blocked it, without asking). Rule: when something the user asked for hits a blocker, keep it and offer the safe way through; ask before dropping a feature.
  title, version and date match what was asked; regenerate rather than resend an older copy.
- (2026-10-30, "the agreed plan is not what we just discussed") When a document restates numbers or a plan, re-derive
  them from the latest decision in this conversation / TODO, not from the document's earlier version.
- (2026-11-01, "why are your replies double?") Write the reply text once, after the PushNotification call, never before
  and after it.
- 2026-11-02: "2pm pst" (I read "Wed 2 at 2pm" as Central). Rule: a time the user gives without a zone is ambiguous; ask or state the zone assumed in the reply before scheduling.
- 2026-11-04: "maybe make it a soft guide not a strict rule" (I wrote the Sharpe > 3.15 x corr pre-screen as a rule). Rule: heuristics go in the docs as guides; only the bench decides.
- (2026-11-01, "where's the code?") Don't assume the user can open a file link on the phone: when they need to read
  something now (a task, code to review), put it in the reply as well as the link.
- (2026-11-06, Friday review; Codex eval audit) A fixed dollar-risk stop can exceed the account's remaining cushion:
  three of four failures had the planned ONB stop above room-to-floor. Cap each entry's risk by the live cushion.
- 2026-11-09: cutting a strategy's 'weak' side because the other side carried 2023+ never helped the books (4 of 4 pieces, `analysis/side_focus_test.py`): the weaker side still earns and smooths the other. Side splits are information; change a side only when it loses money in both periods.
- 2026-11-09: borrowing a proven filter from one strategy for another strategy's engine failed 4 of 4 (`analysis/ingredient_combos_test.py`): a filter is proven only on its own engine. Combine ingredients only when the mechanism says the filter fixes that engine's failure mode, and expect the placebo to decide.
- 2026-11-10: when a filter / regime is the BEST of many tried on a piece, judge it against random splits picked the SAME way (best of N random), never against plain random skips: the Apex-book sweep's funded skips (+$280, blown 2.2% -> 0.2%) were matched by best-of-63 random splits (`analysis/apex_sweep_placebo.py`), while the Overnight Tick version beat them (`analysis/ot_version_placebo.py`).
