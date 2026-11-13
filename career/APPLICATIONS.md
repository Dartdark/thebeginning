# Applications, week of 2026-11-04 (drafts by Claude; retype in your own words before sending)

Fill every [bracket] yourself. Never claim a degree, job or credential you don't have: these platforms test you, and a
mismatch gets the account closed. Order = fastest money first.

## Checklist

| # | Where | Link | Pick / apply as | Status |
|---|---|---|---|---|
| 1 | Mercor | https://mercor.com (Explore jobs) | finance / trading / quant domain-expert roles; also "generalist" roles | [ ] |
| 2 | Outlier (Scale AI) | https://outlier.ai | expert contributor: finance, maths or coding | [ ] |
| 3 | Alignerr (Labelbox) | https://www.alignerr.com | finance / economics expert | **SKIP: not hiring in California (user 2026-11-06); recheck later or apply honestly if you move** |
| 4 | Micro1 | https://www.micro1.ai | AI interview; finance or Python roles | [ ] |
| 5 | DataAnnotation | https://www.dataannotation.tech | starter assessment (general + coding) | [ ] |
| 6 | Upwork + Fiverr | https://www.upwork.com, https://www.fiverr.com | gig: "MultiCharts / PowerLanguage strategy coding and backtest review" | [ ] |
| 7 | Anthropic HackerOne / Gray Swan arena | https://hackerone.com/anthropic, https://app.grayswan.ai | sign up; prize-based, no steady pay | [ ] |
| 8 | Anthropic Residency (stretch) | https://alignment.anthropic.com/2026/anthropic-residency/ | by **Nov 22**; also opt in to the Fellows Program | [ ] |
| 9 | AI video gigs (Upwork + Fiverr, added 2026-11-05) | https://www.upwork.com, https://www.fiverr.com | gig: "short AI videos (ads, explainers, social clips) made with an AI workflow". Build 1-2 sample clips first as a portfolio. Workflow: Claude/Codex + a video model; Seedance runs on Volcano Engine (China), so a US-friendly video model may be easier to sign up for. Costs money per second of video: set a budget before starting. Guide: the Eian article (TIER_LIST F row, 2026-11-05) | [ ] |

Each platform asks for a resume: base it on `career/resume_section_v2_my_voice.md` + your own school / work history.
Expect skills tests or a recorded AI interview on 1-5: take them when rested, they usually allow one try.

## Background (user 2026-11-06: "describe everything i've done with u"; Claude's draft from the repo, check every line)

**Education:** University of San Francisco (USF), B.S. Finance, 2023.

**Freelance coding and trading-strategy development (2023 - now):** coded TradingView / MultiCharts strategies for retail traders and built Python backtests for clients; strategy coding, backtesting and automation.

**Independent project: systematic futures trading research and live automation (Oct 2026 - now)**
- Built a research and trading operation for CME index futures (NQ / ES, also CL, GC, 6E, ZN) aimed at prop-firm (Apex)
  evaluation and funded accounts, working with AI coding assistants (Claude Code, Codex) as research staff.
- Tested and ranked 370+ strategies and ideas from academic papers, practitioner articles, books and trading forums in
  one S-to-F tier list; most fail, and each verdict records why.
- Validation standard I set and enforce: real commissions and slippage on every fill; tests by year from 2018; a sealed
  2023+ holdout; random-entry placebos; walk-forward; bootstrap intervals and Monte Carlo at trading size; a minimum t-stat
  or deflated Sharpe that rises with the number of ideas tried; an independent "checker" that rebuilds each rule from its
  spec before anything is promoted.
- Replicated published research (e.g. order-flow papers using tick-level order-book data) and showed where reported
  edges disappear after costs or when filters chosen in-sample are re-tested.
- Ran automated strategies live on four funded-evaluation accounts through MultiCharts + Rithmic on a Windows VPS:
  routing checks, a remote kill switch, heartbeats, a pre-market check and a phone watchdog. All four accounts failed
  during a losing stretch; I then replayed every live trade against the backtest (15 of 15 matched) to prove the
  execution was right and the loss was the strategy's normal variance, and tested whether position sizing could have
  saved them (it could not).
- Managed position sizing under trailing-drawdown rules, a monthly budget for the operation, and the decision of when to
  stop buying accounts (a buy gate tied to drawdown and cash).
- Built dashboards and daily journals, and set up code reviews by a second AI model with every finding logged and fixed.

**Skills**
- Trading / finance: futures market structure, intraday and overnight strategies, order flow, backtest validation,
  overfitting and look-ahead detection, risk and position sizing, prop-firm rules, reading quant papers.
- Tools: MultiCharts / PowerLanguage (read, review, debug, deploy), Python (pandas, numpy) for backtests (written with
  AI assistance, which I review and test), Rithmic, The Bridge order-flow data, Git / GitHub, Windows VPS operations.
- AI: directing several AI agents (research, independent checking, code review), writing their task specs, and verifying
  their output instead of trusting it.

## Short profile (paste into "About" / headline fields)

Headline: **Systematic futures trader and backtest reviewer (MultiCharts, Python, prop-firm risk)**

About (≈80 words): I build and test systematic trading strategies for futures. Since October 2026 I have tested 370+ ideas
from papers and traders with real costs, rules fixed before results, and checks on years never used for tuning; most fail,
and I record why. I run live automated strategies on prop-firm accounts through MultiCharts and Rithmic on a VPS, with
alarms for drawdown limits and live-vs-backtest drift. I'm good at finding where a backtest fools itself: look-ahead,
overfitting, wrong costs, time zones. USF Finance graduate (2023); freelance coder and strategy developer.

## Mercor answers (draft 2026-11-06; fields from memory of Mercor's usual form, may differ: retype in your own words)

**Headline:** Finance graduate (USF, B.S. 2023) | Systematic futures strategy developer | Python + MultiCharts backtesting

**Summary:** I develop and validate systematic trading strategies for CME futures. Since 2023 I've freelanced: coding
TradingView and MultiCharts strategies for retail traders and building Python backtests for clients. My own research
program has tested 370+ strategy ideas from academic papers and practitioners with real costs, sealed holdout years and
random-entry placebos; most fail, and I document why. I've run automated strategies live on prop-firm accounts and
audited live trades against backtests. I'm strong at spotting where an analysis fools itself.

**Work experience**
- Freelance strategy developer and coder (self-employed), 2023 - present. Coded and debugged TradingView / MultiCharts
  strategies for retail traders; built Python backtests for clients; reviewed strategies for look-ahead bias, overfitting
  and unrealistic cost assumptions.
- Independent systematic futures research and live trading, Oct 2026 - present. 370+ ideas tested and ranked; live
  automated execution on a VPS with risk controls; live-vs-backtest reconciliation (15/15 trades matched).

**Education:** University of San Francisco, B.S. Finance, 2023.

**Skills (tags):** Quantitative finance, Futures, Algorithmic trading, Backtesting, Risk management, Python, pandas,
NumPy, PowerLanguage / EasyLanguage, Pine Script [only if you've coded TradingView yourself], Statistics, Git,
Data analysis, Research paper review.

**Hourly rate expected:** $45-60/hour (Mercor finance-expert roles often list ~$50-100; start mid-range to get hired,
raise after good reviews).

**Availability:** 10-15 hours a week, evenings and weekends (Pacific time); can start immediately.

**AI interview (about 15-20 min, spoken): stories to have ready, 1-2 minutes each**
1. *Walk me through a project.* The research program: an idea comes in from a paper, I freeze the rule before seeing
   results, test it 2018-2022, look at 2023+ only once, compare to random entries, add commissions and slippage. Most
   ideas fail; the ones that pass go to an independent check before going live.
2. *A time you found an error.* The MultiCharts session template started at 09:30 instead of 08:30 Central, so a
   strategy's backtest halved. I matched 4,704 trades against a code port, found the one-hour shift, fixed the setup.
3. *A failure.* Four evaluation accounts failed in a losing stretch. Instead of changing the strategy I replayed every
   live trade against the backtest (all matched), measured how rare the stretch was (about the 6th percentile, ~5 times a
   year) and tested whether smaller sizing would have helped (it didn't). Lesson: separate execution errors from variance.
4. *How do you use AI tools?* As research staff: I write the task spec, have one agent build and a second one check, and
   I verify results by running them; I never trust a number I didn't see computed.
5. *Why Mercor / AI training?* My work is judging whether an analysis is right; that's what evaluating model answers in
   finance needs.

Tips: quiet room, camera on, speak in concrete numbers, say "I don't know" rather than guess. Don't claim live profits.

## Answers that come up on the AI-training platforms

- **Domain expertise?** Futures markets, systematic trading, backtesting and strategy validation, position sizing under
  prop-firm drawdown rules, reading and checking quant research papers.
- **Example of catching an error?** A strategy looked like it traded 15-minute bars from 08:30, but the chart session
  template started at 09:30 Central; the backtest numbers halved. I matched 4,704 trades against a port of the code,
  found the one-hour shift, and fixed the setup. (2026-11-03, `MULTICHARTS_PITFALLS.md`.)
- **Hours per week?** 10-15 (evenings and weekends).
- **Coding?** I read, review and debug Python and PowerLanguage; I write code with AI assistants and verify it by running tests (e.g. replaying live trades against the backtest).

## Upwork / Fiverr gig

Title: **I'll code, backtest and audit your MultiCharts / TradeStation strategy**
- What you get: your idea coded in PowerLanguage/EasyLanguage, a backtest with real commissions and slippage, an audit for
  look-ahead and overfitting, and live-setup notes (sessions, time zones, broker mapping, prop-firm limits).
- Starter price: $50 for a small strategy (one entry rule, one market) to get first reviews; raise after 3-5 five-star jobs.
- Rule: never trade a client's account and never promise returns.

## Anthropic Residency (stretch; by Nov 22)

Honest positioning: early-career, but a working example of careful empirical research done alone with AI tools.
Draft answer, "Why do you want to do this / relevant experience" (retype it yourself):
> For the past several weeks I have run a one-person research operation on financial markets, using AI coding agents to
> write the code while I set the questions and the rules for what counts as evidence. I learned the hard way that a
> result is cheap and a trustworthy result is not: I pre-register tests, hold out data, count every trial against a
> multiple-testing bar, and have a second AI independently rebuild candidates to catch my mistakes. Most of my ideas
> fail, and I keep records of why. I want to bring that discipline (evaluating whether a system really does what it
> appears to do) to AI safety, where the same failure modes, overfitting and fooling yourself, matter far more.
> I graduated from the University of San Francisco with a B.S. in Finance (2023) and have worked since then as a
> freelance coder and trading-strategy developer.

Attach: resume; optionally a short write-up of one test end to end (the live-vs-backtest replay is a good one).

## Answers for every other application (draft 2026-11-06; forms change, so map these to whatever fields appear)

Reuse everywhere: resume (`career/resume.pdf`), headline and summary from the Mercor section, 10-15 h/week, Pacific time.

### 2. Outlier (Scale AI)
- **Expertise areas to pick:** Finance; Mathematics/Statistics (only if you are comfortable with the test); Coding: Python.
- **Highest education:** Bachelor's, Finance, University of San Francisco, 2023.
- **Describe your expertise (short):** Systematic futures trading and backtest validation; I review whether a quantitative
  analysis is correct (look-ahead, overfitting, costs) and write and check Python data analysis.
- **Screening tasks:** you will grade or write AI answers. Be slow and exact: check every number, say what is wrong and why,
  follow the style guide literally. Quality scores decide whether you keep getting work.

### 3. Alignerr (Labelbox): ON HOLD, not hiring in California (2026-11-06)
- **Domain:** Finance / Economics. **Level:** Bachelor's + professional (freelance since 2023).
- **Why a good fit (2-3 lines):** I spend most of my time judging whether a financial analysis holds up, re-running it with
  real costs and held-out data. That is the same skill as checking an AI model's finance answers for errors.
- **Assessment:** finance questions (time value, valuation, derivatives, statistics). Revise futures basics, options
  Greeks, CAPM, bond pricing before you start.

### 4. Micro1
- **Role to pick:** Finance expert / Python (data analysis) contributor.
- **AI interview (spoken, ~20 min):** use the 5 stories in the Mercor section. Likely technical questions: Sharpe vs
  Sortino, what overfitting is and how you detect it (holdout, placebo, multiple-testing bar), how futures margin and
  rollover work, a pandas question (groupby, merge, rolling windows).

### 5. DataAnnotation
- **Starter assessment:** general (writing, fact-checking AI answers) + coding (Python). No essay needed; the test is the
  application. Write full sentences, justify each rating, catch factual errors. Then take the Finance qualification when
  offered.

### 6. Upwork + Fiverr (MultiCharts / backtest gig)
- **Profile title:** Futures Strategy Developer | MultiCharts, EasyLanguage, Python Backtesting
- **Overview:** I code, backtest and audit trading strategies. You get your rules coded in PowerLanguage / EasyLanguage or
  Python, a backtest with real commissions and slippage, results by year, and an honest audit: look-ahead bias,
  overfitting, session and time-zone settings, prop-firm limits. Finance degree (USF 2023), freelancing since 2023. I
  never trade your account and never promise returns.
- **Rate:** $40-50/hour or $50 per small fixed job to start; raise after 3-5 five-star reviews.
- **First proposals (template):** "Hi [name], I read your rules for [strategy]. I'd code it in [platform], backtest
  [market] [years] with [$ per side] costs, and send the trade list plus a short note on anything that looks too good
  (e.g. [specific risk you spotted]). Turnaround [2-3] days. One question first: [one real question about their rules]."

### 7. Anthropic HackerOne / Gray Swan arena
- Sign-up is just an account; no essay. Read each program's rules first, test only in scope, report exactly what you did.
  Prize-based: treat it as practice, not income.

### 8. Anthropic Residency: see the section above (deadline **Nov 22**).

### 9. Upwork + Fiverr (AI video)
- **Gig title:** Short AI Videos for Ads and Social Media (concept to finished clip)
- **Description:** I plan, script and produce short AI-generated videos: story, shot list, consistent characters and
  style, editing and color. You approve the story and style before anything is generated, so there are no surprises.
- **Before listing:** make 1-2 sample clips (needs a video-model budget; wait for a paycheck). Price after you know your
  cost per second of video.
