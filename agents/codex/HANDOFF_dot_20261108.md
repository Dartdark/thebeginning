# Dot handoff: futures strategy research and project coordination

Summary: Help the user develop evidence-backed futures strategies for evaluation, funded and personal accounts.
Codex builds/tests; Claude independently checks; the user decides what enters a plan or trades.
This is an orientation handoff, not an instruction to start research, change a schedule or deploy anything.
The latest recorded user instruction pauses the lab and scheduled paper scout; preserve that pause.
First action: read the sources below and return a read-only inventory of state, conflicts and unfinished work.

## 1. What the user is trying to do

The project is **Dartdark/thebeginning**, a private GitHub repository. The user develops systematic futures strategies, mainly NQ/MNQ and ES/MES, with some CL/MCL and other markets. MultiCharts PowerLanguage is the target platform; Python is the research and account-simulation environment.

There are three different jobs for a strategy:

| Book | Objective | What can disqualify an otherwise profitable strategy |
|---|---|---|
| 50K/150K evaluations | Reach the target under the actual evaluation rules, at a sensible fee and speed | Trailing drawdown, daily limits, time constraints, overlap with the existing stack |
| 50K/150K funded accounts | Collect payouts while surviving the account rules | Payout caps, qualifying days, consistency, withdrawals, drawdown sequence and shared losses |
| Personal account | Improve the portfolio's return and risk at available capital | Open-position losses, margin, overnight/weekend exposure, concentration and execution |

Standalone profitability, an A rank or a low daily correlation does **not** establish a place in any book. A payout-capped portfolio can have very little room for another profitable strategy. Conversely, an unsuitable evaluation strategy can still merit personal-account research.

The user's own designs are **Vault Break and Overnight Bias**. Most other uploaded designs were found externally. Preserve source attribution. The user wants to learn which ingredients create the edge, and ultimately build original strategies around a coherent market hypothesis rather than stack arbitrary indicators.

## 2. Roles and authority

- **User:** chooses objectives, approves portfolio membership, sizes and any live change.
- **Codex:** implements research, tests hypotheses and code, prepares reproducible evidence and proposed PowerLanguage. Works only on `codex/work`.
- **Claude:** reviews independently, checks reproduction and practical fit, maintains the reviewed rankings/plans through its own authorized workflow.
- **Dot:** proposed coordinator. Maintain a clear task/status map, locate sources and permitted free data, assemble complete Codex task briefs and user-forwarded Claude review packets, and identify stale or contradictory state. Do not present this proposed role as an already configured integration.

Agreement between two assistants is not verification. Preserve disagreements and settle factual questions with the smallest appropriate check. No automatic Dot-to-Claude relay has been established. Preparing a packet is different from sending a message; this handoff authorizes no external messages.

## 3. Repository access and branch discipline

Repository: https://github.com/Dartdark/thebeginning

| Purpose | Branch / source checked for this handoff |
|---|---|
| Codex research and scout history | `codex/work`, research head `5ac817b` before this handoff |
| Latest reviewed operational/plan notes | `claude/nq-trading-strategy-params-5h9d20`, head `19e26d0c46d78ecc2347cb178dfaec96cb2bbf8b` |
| Pinned raw snapshot used by the latest ingredient study | `fe35af99aa90d7f31b91f8693859251bb44dd9ab` |

These are **November 8, 2026 snapshots**, not a guarantee of the state when Dot reads this. Fetch and inspect newer evidence. Read branch-specific files at their actual ref; fetch alone does not merge their contents.

1. Inspect repository identity, branch, worktree changes and concurrent work before editing.
2. Reuse `codex/work`; do not reset, force-push or discard existing work. If it is absent, follow the original handoff's source-branch instruction rather than inventing a new history.
3. Never push to `claude/*` or `antigravity/*`. Pull/reconcile `codex/work` before a normal push. Do not merge the Claude branch wholesale just to obtain a brief.
4. Some **Codex-only scout history is absent on the current Claude branch**. Replacing the Codex tree with Claude's tree would lose important context.
5. Do not merge, click **Fix**, or review PR #2. Its old `@codex` mailbox attempt was blocked by an environment-configuration response; no working mention-based relay has been demonstrated.

An earlier local source checkout is `/workspace/thebeginning` on branch `work`; it is not the research branch. The research checkout for this handoff is `/workspace/paper_review_20261108` on `codex/work`. These paths are machine-specific, not instructions to assume Dot has the same filesystem.

## 4. Required reading and freshness

Read `AGENTS.md` and **all of** `agents/codex/BUILDER_BRIEF.md` before a Codex task. Then read:

| Context | Files |
|---|---|
| Repository map and current state | `README.md`, `NEW_CHAT_BRIEF.md` |
| Research standard | `DEVELOPMENT_PROCESS.md`, `CLAUDE.md`, `agents/codex/RESEARCH_CONTROLS.md`, `agents/codex/USER_CODE_WORKFLOW.md` |
| Prior work and unresolved findings | `TIER_LIST.md`, `WATCHLIST.md`, `TODO.md`, `LESSONS.md`, `agents/codex/results/GRADES.md` |
| Platform and retained execution lessons | `MULTICHARTS_PITFALLS.md`, `agents/codex/EXECUTION_REFERENCES.md` |
| Actual books | `apex_strategies/README.md`, `funded_strategies/FUNDED_PLAN.md`, `funded_strategies/README.md`, `personal_strategies/PORTFOLIO.md`, `portfolio/README.md` |
| Tools/programs | `agents/codex/terminal/README.md`, `agents/codex/research/scout/WORKFLOW.md`, `SEARCH_PROFILE.md`, `config.json`, `progress.json`, `continuation.json` in that scout directory |
| Coordination and data | `agents/codex/TASK_weekly_cross_review.md`, `agents/codex/DATA_NEEDED.md`, `lab/README.md`, presence/content of `lab/STOP` |

**Freshness warning:** the Codex branch's top-level briefs and book documents can lag the Claude branch. Read the latest Claude copies without overwriting Codex work. Even the latest brief contains historical paragraphs that conflict with its newer dated “Now” section. Prefer a dated, explicit user decision and supporting artifacts over a stale roster sentence. Record the conflict rather than silently choosing a convenient version.

## 5. Current recorded operational state — do not confuse this with fresh broker verification

The latest Claude brief checked here says:

- **No live accounts remain:** the four recorded accounts failed by November 4. This is repository-reported status, not a broker query performed for this handoff.
- **The user stopped the strategy lab and paper-scout schedule on November 5.** Pre-market and afternoon journal/dashboard jobs were also stopped. The morning brief, Friday review, reminders and a roll reminder were recorded as still on. Their actual scheduler state was not inspected here.
- Funded **Vault Break size was reduced from 3 to 2 MNQ** in the relevant bench plan. A per-strategy cushion cap was adopted for funded use; evaluation caps were not adopted. Seven funded code files were written but **not compiled**.
- **Twin Continuation, 2 MNQ, was added by the user to the 150K evaluation and funded plans on November 8.** Its account-specific code was not yet compiled. Do not infer that the ordinary overnight personal version is evaluation-legal unchanged.
- Personal **Overnight Tick / VIX was approved at 2 MNQ** on November 8.
- **FINRA short-volume longs remain PENDING**, with a proposed 1 MNQ personal slot only after the forward requirement. MultiCharts matching does not cure its post hoc selection. Do not count it as a deployed or cleared portfolio component.
- Bridge noise-area 15-minute longs were approved for personal at 1 MNQ, with early-close and fill-latency readiness still requiring attention. Exact code/replay evidence must be checked before treating a readiness item as complete.

**Critical simulation correction:** evaluation engines had incorrectly applied the funded floor lock at starting balance + $100. The latest Claude work corrected evaluations to keep trailing; the funded PA lock remains intentional. Many benches were rerun, but some old candidate, sizing and fee results were not. Daily-loss-limit fills at the limit and a 30-calendar-day clock remain unmodelled in the cited evaluation work. Do not recycle old pass rates, payout forecasts or scaling projections as current calculations.

No account purchase, deployment or resume is authorized by this handoff. “In the plan,” “user approved,” “compiled,” “matched in MultiCharts,” “forward tracked” and “currently trading” are separate states.

## 6. Strategy map — orientation, not a current sizing ledger

Use the current book files for exact membership and quantities. Do not copy every historical roster row into a new live plan.

| Family / strategy | What it broadly trades | State or caveat to retain |
|---|---|---|
| Vault Break | Directional range break | Core user design; targets and drawdown contribution require correct fill rules |
| ONB ADX30 / ONB ML | Overnight state into the cash open | Evaluation and funded versions differ; ML price-term decay is WATCHLIST #33 |
| Relative Strength | NQ move beyond its ES relationship | Longs/both-sides membership differs by book |
| Monday Long / Bridge Monday | Monday and Sunday-reopen windows | Distinct entry clocks; Bridge's no-stop tail needs open-path risk |
| Late-Day Flow | Afternoon directional flow window | Existing LETF/gamma sizing trials are not virgin hypotheses |
| EOS / NFP Fade | Expiry-open / payroll-release effects | Scheduled-event timing and exact calendar matter |
| ES MOC Follow | Move into the closing auction | Recent decay; price-based proxy is different from actual auction-imbalance data |
| CL Sunday fade | Weekend gap reversal | Contract, reopen, stop-path and missing-bar risk |
| Overnight Tick / VIX | Overnight long conditional on down-day flow/volatility | Approved personal size change above; source history is shorter than some books |
| FC 2B v2 | Existing tested morning design | A rank, forward log; prior benches did not earn an Apex slot |
| Dual Thrust v4 / Twin Continuation | Opening breakout / morning continuation | MC-confirmed source versions; current 150K-specific settings need their own readiness checks |
| S30 IBS / S47 v2 / Kusho v9 | Multi-session reversal / Europe-open impulse / extended-session pattern | Personal research/forward statuses; overnight and no-stop risks are material |
| Swing Target v3 / PAPERTREND v2 | Structural/opening breakouts | Personal candidates/members per current decisions; old funded swaps were sometimes reverted |
| Noise-area designs | Opening anchored bands and follow-through | S03 v2 ingredient diagnostic and Bridge 15-minute long code are not interchangeable versions |
| T_ONESIDE fade | Heavy overnight participation faded near the open | Historical roster notes conflict; resolve current membership from dated decisions |
| Anson / R2Vault | Strength-gated directional / R-squared-vault design | Recent decomposition does not reopen their earlier weak or unplaced verdicts |

The portfolio still concentrates economically in equity-index direction and certain opening windows. New market names, different indicators or low close-to-close correlation do not demonstrate protection during an account breach. Measure concurrent open exposure and common losing events. Do not call an absent trade day an unoccupied intraday window.

## 7. Research process — required, including when working autonomously

The user has already authorized worthwhile-paper follow-through and permitted free-data acquisition within active tasks. Avoid repeated “should I test it?” questions. **That standing workflow does not lift the explicit program pauses.**

1. **Check the tier list, watchlist, lessons and prior trials first.** Identify the exact existing economic family and any failed controls. A renamed rule or shifted clock is not automatically a new hypothesis.
2. **Read the real source.** For every paper explicitly answer: what is it about; what does it find; why might it make money; can we build on it; can strategy code be made? Separate a documented return, a proposed mechanism, an execution method and a cited result.
3. **Evidence sheet before preregistration.** Use `agents/codex/templates/evidence_sheet.md`. Specify who trades/pays, why, signal and execution clocks, exact fields, costs, power, existing overlap and common-loss/diversification risk. TEST can advance; NEEDS DATA or DON'T TEST cannot advance to dependent returns.
4. **Try permitted owned/free inputs before declaring a data block.** Record exact missing fields, receipt/publication/revision gaps and actual access attempts. Park a worthwhile blocked lead and move to an eligible one within budget. Never substitute OHLC or a convenient proxy for the paper's causal input without explicitly registering a different study.
5. **Commit the exact plan and executable definitions before returns.** Include mechanism, variants/controls, selection rule, pass/fail gates, costs, dates, overlap and stop rule. Builder ceiling: at most five definitions per family; a stricter task/program ceiling wins. Count cheap gross screens and controls, preserve failures and repository-wide multiplicity.
6. **Cheap 2018–22 gross-edge-versus-cost screen first.** Only passing designs earn expensive validation and account benches. A failed gate stops its dependent stages. No threshold, window, side or exit rescue after seeing failure without genuinely new justification and a separately registered trial.
7. **Choose on design history only.** The usual split is 2018–22 / 2023 onward, but 2023+ is already seen. Call it historical replication, not a pristine holdout. Freeze before opening the next stage and preserve an honest forward log.
8. **Test mechanisms and controls.** Side/time placebos with the same exits; whole, long/short, year and era results; uncertainty and adverse tails. For a truly nested trade-removal filter, show total profit, removed-trade results and matched random drops. If a change alters future strategy state, compare the complete policies rather than pretending the trade sets are nested.
9. **Run relevant current-book BASE / ADD / REPLACE / EMPTY comparisons** at actual integer size on paired histories only after earlier gates pass. Use the latest approved book and correct evaluation/funded rules. Include payouts, breach/blown probability, horizons and payout timing where applicable; personal comparisons need capital and marked drawdown.
10. **Independent review, source/native MultiCharts parity, frozen forward evidence and user approval** precede promotion or live use. A syntax check, artifact-admission gate or two AIs agreeing is not economic verification.

The preferred research direction is **forced or scheduled flows**, including closing auctions, LETF rebalancing, direct option-expiry hedges, index rolls and release-related flows. Look for genuinely untested corners and occupied-hour gaps. Avoid endless indicator combinations, surveys, unrelated emerging-market results and crypto pump-and-dump stories.

## 8. Data, accounting and execution rules that repeatedly mattered

- **Units:** NQ $20/point; MNQ $2/point; ES $50/point; MES $5/point. NQ tick 0.25. Use each other contract's actual multiplier/tick. Two MNQ are one fifth of an NQ.
- **Native costs:** typical NQ research charges $7.25 round trip plus one tick on each market/stop fill; source/task definitions take precedence. Native micro commissions must be charged separately. Dividing a standard contract's net by ten does not automatically produce native micro net.
- **Limit fills:** the generic executor's default target requires 1 point through; the VB parity-only investigation registered 0.25 point through to match MultiCharts. Do not globally replace either setting or silently reuse a parity exception in stress tests.
- **Timing:** source timestamps, publication/receipt timestamps, decisions and forward labels are different clocks. Match exchange timezone, DST, bar-open/bar-close conventions, session holidays and early closes. No full-day feature in a morning decision.
- **OHLC is not tick replay.** Entry-bar protection, ambiguous stop/target ordering, cancellations, one-minute delays and partial exits can change results. Missing held-path bars are not evidence of safety.
- **Volume:** MultiCharts `Volume` in the relevant futures context was up-tick volume, not automatically total traded volume. Check the field/feed/chart instead of assuming equivalent definitions.
- **Rolls:** continuous price jumps, contract identity and roll timing can alter both signals and P&L. Preserve actual fill prices and account for rolls; do not casually drop real held-position losses as “bad data.”
- **Daily series must reconcile to trade results**, including fill prices, all fees and roll adjustments, before portfolio sizing. Booked P&L can hide open losses. Name the mark clock: a 23:59 cut and the prior session cut can yield different drawdowns without proving either is an accounting error.
- **Prop legality:** the builder default is flat by 15:59 Chicago time, with only the explicitly approved Sunday-to-Monday exception. Evaluate each account-specific implementation. Personal overnight permission does not remove gap, margin or forced-liquidation risk.
- **Leakage:** causal warm-up, release vintages and revisions matter. Fit learned transformations inside chronological folds, purge overlapping labels where needed and preserve information availability. Do not retrofit ML to a fixed rule merely because a tool supports it.
- **Execution audit:** two accounts on one signal equal one research event. Price observations 1/2/5 minutes around an entry are diagnostics, not proof waiting would improve a tradable strategy. Bid/ask logger and watchdog changes previously requested as proposals remain proposals unless a later explicit decision says otherwise.

Use the existing engines rather than inventing incompatible replacements: `analysis/grid24.py`, `analysis/grid.py`, `analysis/param_clusters.py`, `analysis/metrics.py`, `analysis/resampling.py`, `analysis/trials.py`, `analysis/funded_lab.py`, `analysis/funded_bootstrap.py`, `analysis/montecarlo.py`, source-specific adapters and MultiCharts exports. Check newer fixes and exact imports before using historical script names.

## 9. Most recent Codex work: ingredient decomposition

The user's requested presentation is **Change | $ a trade | t | Read**. Explain what direction, timing, filter, exit, stop and holding period contribute, including whether an apparent benefit survives both eras. Label side contributions versus standalone side-only reruns. These studies are diagnostics, not permission to alter plans or combine winners after the fact.

All report paths below are under `agents/codex/results/` on `codex/work`:

| Round | Report | Registered scope / key caution |
|---|---|---|
| Dual Thrust, RS, LDF | `ingredients_three_20261108.md` | 13 definitions; retain the original report and source versions |
| FC 2B, both ONBs, T_ONESIDE | `ingredients_fc_onb_t_20261108.md` | 18 definitions; different ONB engines must not be merged by name |
| EOS, NFP, CL | `ingredients_events_20261108.md` | 15 definitions; direction clearer than some conditional gates; CL held-path tails matter |
| Monday Long, Bridge Monday, ES MOC | `ingredients_monday_moc_20261108.md` | 15 definitions; Bridge no-stop tails, MOC recent decay and the cash-close clock matter |
| S30 NQ/ES, S47 v2, Kusho v9 | `ingredients_s30_s47_kusho_20261108.md` | 20 market/rule combinations; S30 open risk, S47 direction and Kusho stop-management tradeoffs |
| **Anson, R2Vault, S03 v2** | **`ingredients_anson_r2_s03_20261108.md`** | **15 definitions; latest completed task, result commit `5ac817b`** |

Latest round: net dollars per **one NQ**, design 2018–22 versus already-seen recent 2023–2026-10-09. These are source-adapter results, not new independent native-MC confirmations:

| Strategy / change | Design $/trade; t | Recent $/trade; t | Read |
|---|---:|---:|---|
| Anson baseline, strength 4.5 / 20-bar hold | $50; 1.24 | $166; 1.99 | Weak base; no new promotion |
| Anson fade instead | −$85; −2.09 | −$201; −2.40 | Direction is an ingredient |
| Anson without strength gate | −$30; −1.70 | −$34; −1.06 | Strength gate helps both eras |
| R2Vault baseline, 75 stop / 40 target | $24; 1.02 | $46; 1.72 | Weak base |
| R2Vault without R² refresh gate | −$15; −0.63 | $27; 1.06 | Vault gate helps; recent evidence uncertain |
| R2Vault without stop | −$14; −0.36 | $24; 0.47 | Recent DD about $23.6k → $76.7k |
| S03 v2 baseline | $112; 3.82 | $132; 2.12 | Directional band engine |
| S03 without entry band | $10; 1.25 | −$8; −0.52 | Band is central; recent DD about $22k → $108k |
| S03 without entry VWAP gate | $105; 3.70 | $117; 1.96 | Small, uncertain incremental gain; exit VWAP retained |
| S03 without stop | $123; 2.99 | $174; 1.96 | Recent total net only +$1,118; DD about $22k → $41k |

The latest plan was committed before returns (`7320764`); a syntax-only amendment (`65de599`) and partial-run checkpoint (`70e5d0a`) preserve the aborted/rerun history. A higher average after removing the S03 stop is not a portfolio improvement. Anson's earlier weak verdict, R2Vault's and S03's existing statuses remain governed by the review process.

Earlier combinations were also tested and failed. Do not recommend “combine the best three ingredients” as if the project has not tried that. A new combination needs a single causal hypothesis, exact input/clock definition, bounded preregistration and a justified comparison.

## 10. Existing scout — preserve history and the pause

Program: `paper-scout-20261029`.
Existing automation ID: **`6ae3863373308191b6f40c63f610a800`**.

The saved config describes a daily automation in `America/Los_Angeles`. Its `created_enabled` status was verified **only at creation on October 29**; the config explicitly says it does not query the live scheduler. The **newer November 5 user pause wins**. A `ready` progress field or an unfinished discovery checkpoint does not authorize resumption.

Current saved counters at the checked Codex head:

| Item | Consumed / limit |
|---|---|
| Hypotheses | **4 / 10** |
| Economic definitions, including screens and controls | **10 / 30** |
| Per checkpoint batch | At most 1 new hypothesis and 3 full-source reviews |
| Per hypothesis | At most 3 candidate variants / 5 definitions including controls |

Four saved design rejections: European-fix drift, pre-NFP ES reopen, Treasury benchmark clock and FOMC intermeeting cycle. There are 175 saved seen-record entries. These counters are program-specific, not a reset of the repository's other trials.

Last run `scout-owned-source-20261108`: 90 query submissions in 23 discovery/access batches; 14 new records; four selected primary-section checks; **zero new full reviews, hypotheses, definitions or return tests**. It saved a discovery checkpoint, not a suspended admitted backtest. Lease and active reservation were null. See:

- `agents/codex/results/scout_owned_source_20261108.md`
- `agents/codex/research/scout/continuation.json`
- `agents/codex/research/scout/runs/20261108_owned_source.json`

The saved discovery routes concern Treasury cash-opening demand, futures liquidity resilience and passive-fund predictable demand, subject to complete owned inputs and novelty. They are **checkpoint context, not a new instruction to search now**. Signed dealer inventory, actual auction messages, paired-contract basis, weather vintages and other recorded blockers remain parked until genuinely new matching inputs exist.

Do not create another scout, reset counters/notifications/seen records, claim a lease while merely orienting, flip config booleans or resume paused t6, Strategy Hunt v2 or the lab. If the user later explicitly resumes research, inspect the actual scheduler and checked-head ownership first, then follow the existing workflow, reservation and admission gates. Per-batch checkpoints do not allow resetting the overall budget.

## 11. Terminal, lab and weekly review are different things

**Research terminal:** local browser UI over committed reports, strategy/evidence library, registered results, verification queue, execution references, PDF inbox, notes and scout state. Start scripts are under `agents/codex/terminal/`; default localhost port 8765, Python 3.10+, standard library. It does not automatically pull Git or run backtests. Refresh after a pull. Its Discover button fetches metadata; importing a PDF does not review or test it. Notes/PDF inbox runtime data are local and Git-ignored, not guaranteed to sync to Dot.

**Scheduled scout:** an existing agent workflow separate from the terminal server. The scheduler is not controlled by opening the terminal. Saved flags such as `automatic_backtests: false` must be read with `scheduled_research: gated_agent` and the actual workflow, not toggled to bypass gates.

**Claude strategy lab:** separate queue/ledger/program under `lab/`. It has its own daily and sealed-look budgets. `lab/STOP` is a kill switch. Preserve its explicit pause. Do not merge its counters with the Codex scout's or launch a duplicate loop.

**Weekly cross-review:** after Friday review, each assistant writes an independent assessment before reading the other's. At most five material disagreements: claim, position, evidence, practical consequence, smallest settling check. Then one response each, checkable disputes resolved by checks, remaining judgement calls exposed to the user. New return tests still require preregistration. Files: `agents/cross_review/YYYY-MM-DD_{codex,claude,summary}.md`; instructions: `agents/codex/TASK_weekly_cross_review.md`. The latest November 6 review was already read/handled in November 8 notes; orientation is not a reason to rerun it or create another Friday schedule.

## 12. Data acquisition and registers

Use **owned and free sources only**. No paid data, subscriptions, purchases or new vendor contacts are authorized here. Publicly accessible does not imply point-in-time validity or a licence to bypass access controls.

The repo contains or references minute histories for NQ, ES, GC, CL, YM, ZN, 6E and BTC, corrected NG inputs, selected aggregate-flow fields, VIX/VXN and other volatility series, COT, FINRA, ProShares and event collections. Check exact market, dates, contract construction and workspace availability; a filename is not a quality/availability certificate. Git-ignored caches/raw collections are not guaranteed in a fresh clone.

Key recent data reports: `agents/codex/results/new_data_local_20261108.md`, `primary_data_review_20261108.md`, `gold_clocks_20261108.md` and `preopen_absorption_20261108.md` in that results directory. The absorption screen was rejected; its data is not permission to rerun the same rule. Claude copied new data to `data/codex_20261108/`, with ProShares S&P/Dow in `data/letf/` and RRP in `data/nyfed/`.

Retain these distinctions:

- Real **NYSE Arca SPY** auction imbalances and **NYSE-listed stock** auction imbalances are separate products. Price/volume bars do not supply historical messages as published. Prior quotes/sample requests are not proof data was obtained.
- ProShares NAV/assets/share histories are available, but historical publication/revision timing and intraday creation/redemption offsets are uncertain. A registered D−1 asset estimate plus D−2 stress is exploratory, not observed net hedge demand.
- VIX, open interest and unsigned options volume are not signed dealer inventory. Continuous futures are not a dated paired-contract curve. Minute OHLC is not bid/ask or order-lifecycle data.
- Treasury announcement, result, update and actual receipt clocks differ. A result document's current accepted amount cannot be made available earlier by assigning the announcement time.
- GLD/leveraged-gold reset/valuation rules have historical clock and DST issues. A policy document is not a receipt proving executed hedging at that instant.

Registers:

- **`agents/codex/DATA_NEEDED.md`:** missing exact fields/history/contracts/clocks, sources/attempts, partial acquisitions and smallest next check. Merge duplicates and preserve resolved/rejected history.
- **`TODO.md`, Promising strategies awaiting verification:** merited but unverified candidates, with source, evidence, missing check and status. Research-queue upkeep does not authorize trading-plan edits or revive rejected rules.
- **`agents/codex/EXECUTION_REFERENCES.md`:** retained execution ideas, methods, limits, prerequisites and later outcomes, including useful material with no standalone alpha. Do not sell methodological value as profitable trading evidence.

## 13. Environment and computer access

This cloud research instance has used `/workspace/venvs/thebeginning/bin/python` with numpy, pandas, numba, openpyxl, scipy and scikit-learn. Verify imports and the configured interpreter in any new environment; do not replace it casually with system Python. The setup request was `pip install numpy pandas numba openpyxl scipy scikit-learn`. Cache builds can be lengthy and are unnecessary for this handoff.

Dot's cloud computer, a Codex cloud-task environment, the user's local Windows PC and the trading VPS are different machines. Files and permissions do not automatically cross between them. The user's Bridge history/download tooling originated on the Windows desktop; this cloud chat cannot assume access to it. Local computer access is optional and must actually be connected; this document does not connect it. Cloud work can continue without the user's PC being powered on; tasks needing that PC need it available.

Official Dot references:

- https://help.openai.com/en/articles/20001530-getting-started-with-your-dot
- https://developers.openai.com/training/walkthroughs/personalize-your-dot
- https://openai.com/index/introducing-dots/

A Dot-created Codex task needs an accessible, configured repository environment. Do not assume the child task receives this conversation or all Dot memory: include the handoff path, exact goal, refs, relevant task/plan files, constraints and expected outputs in each task. Do not claim local access, a scheduled background run or a successful GitHub mention integration without checking it. Current account settings determine access/usage; no fixed weekly hours are promised here.

## 14. Output style and user preferences

- Do the authorized work rather than repeatedly offering to begin. Keep concise progress updates during long active work.
- For an active research cycle, a worthwhile lead triggers development through every earned gate; it is not a reason to stop and ask whether to test. Missing-input leads are recorded and parked; continue distinct eligible discovery within budget. Do not fabricate a positive result or fish indefinitely.
- The saved report **starts with Summary of at most five lines**. Include plan/commit, script, inputs, output paths, trial count, dates, units, comparison tables and limitations.
- Show the key results **in chat as well as in the file**, with direct GitHub links. For code, provide a raw GitHub link and chart/session/input requirements. Links do not substitute for results.
- Keep author claims, local Python replication, native MultiCharts confirmation, independent review, forward evidence, user approval and deployment visibly separate.
- A clean rejection is useful. Avoid inflated language or a retrospective story implying the mechanism was proven.
- Do not ask routine permissions already covered by the active task. Ask only about a real missing decision or action outside authority, after doing independent preparation. Do not treat a proposal file as deployment authorization.

## 15. Hard boundaries

**Never touch live trading, the VPS, broker/Rithmic/Apex settings, API keys or orders.** No live code deployment, chart/input edits, account purchases or real-money action. Read-only reports do not create authority to change operational systems.

No automatic portfolio promotion, TIER_LIST edits or plan changes from Codex research. No resets/force pushes/history loss. No new scheduled automation or lifting a user pause. No messages, emails, Slack/phone alerts or contacts to Claude/vendors/others without explicit authorization. Existing workflow text mentioning notifications does not override this handoff's orientation scope.

## 16. Dot's first task — read-only

1. Confirm what repository/environment access actually exists. If unavailable, state exactly which access is missing; do not claim a successful sync.
2. Read this handoff, required briefs and current dated decisions on both branches without changing either branch's work.
3. Return a concise inventory: latest refs; approved/planned/compiled/forward/live distinctions; paused programs and unverified scheduler state; existing scout counters; unfinished Codex/Claude checks; true missing data.
4. Identify the next already-authorized task and its owner, or ask the user to choose a new objective if none is active. The last completed Codex request was the Anson/R2Vault/S03 ingredient grid.
5. Preserve all history and pauses. **No return tests, cache builds, strategy changes, schedule changes, live changes or external messages during orientation.**

## 17. Template for a later, authorized Codex task

```text
Repo: Dartdark/thebeginning. Work only on codex/work.
Read AGENTS.md, agents/codex/BUILDER_BRIEF.md and
agents/codex/HANDOFF_dot_20261108.md, then the current task-specific sources.
Fetch/inspect without resetting, force-pushing or discarding concurrent work.

Goal: [one concrete requested outcome]
Authority/state: [explicit user request; whether any program pause has been lifted]
Source refs and current book: [branch/hash/files; distinguish stale historical benches]
Task/plan/evidence: [paths and committed plan if returns are authorized]
Inputs/clocks: [exact fields, dates, contracts, availability and missing data]
Budget/gates: [prior consumed trials, allowed definitions, pass/fail and stop rule]
Scope: [source review / engineering / registered returns / earned book comparisons]
Owner/concurrency: [one task owner, lease if applicable, work already in progress]
Outputs: [reproducible script, inputs/receipts, report, chat comparison table]
Verification: [independent Claude/native/forward status and remaining checks]

Do not touch live/VPS/broker settings/API keys/orders or change trading plans.
No paid sources, external messages, new automations or unrequested program resumes.
Commit and normally push only codex/work when work is complete; provide the result
path for the user to forward to Claude. A failed gate stops dependent tests.
```

## Provenance and scope of this handoff

Prepared November 9, 2026 from Codex `5ac817b`, latest fetched Claude `19e26d0`, their November 8 source snapshots, saved scout state and the completed ingredient reports. Claude's latest brief was inspected read-only, not merged. No backtest, account audit, scheduler inspection, live deployment, external message or Dot configuration was performed to write this document. No research program was resumed.
