# Applications, week of 2026-11-04 (drafts by Claude; retype in your own words before sending)

Fill every [bracket] yourself. Never claim a degree, job or credential you don't have: these platforms test you, and a
mismatch gets the account closed. Order = fastest money first.

## Checklist

| # | Where | Link | Pick / apply as | Status |
|---|---|---|---|---|
| 1 | Mercor | https://mercor.com (Explore jobs) | finance / trading / quant domain-expert roles; also "generalist" roles | [ ] |
| 2 | Outlier (Scale AI) | https://outlier.ai | expert contributor: finance, maths or coding | [ ] |
| 3 | Alignerr (Labelbox) | https://www.alignerr.com | finance / economics expert | [ ] |
| 4 | Micro1 | https://www.micro1.ai | AI interview; finance or Python roles | [ ] |
| 5 | DataAnnotation | https://www.dataannotation.tech | starter assessment (general + coding) | [ ] |
| 6 | Upwork + Fiverr | https://www.upwork.com, https://www.fiverr.com | gig: "MultiCharts / PowerLanguage strategy coding and backtest review" | [ ] |
| 7 | Anthropic HackerOne / Gray Swan arena | https://hackerone.com/anthropic, https://app.grayswan.ai | sign up; prize-based, no steady pay | [ ] |
| 8 | Anthropic Residency (stretch) | https://alignment.anthropic.com/2026/anthropic-residency/ | by **Nov 22**; also opt in to the Fellows Program | [ ] |
| 9 | AI video gigs (Upwork + Fiverr, added 2026-11-05) | https://www.upwork.com, https://www.fiverr.com | gig: "short AI videos (ads, explainers, social clips) made with an AI workflow". Build 1-2 sample clips first as a portfolio. Workflow: Claude/Codex + a video model; Seedance runs on Volcano Engine (China), so a US-friendly video model may be easier to sign up for. Costs money per second of video: set a budget before starting. Guide: the Eian article (TIER_LIST F row, 2026-11-05) | [ ] |

Each platform asks for a resume: base it on `career/resume_section_v2_my_voice.md` + your own school / work history.
Expect skills tests or a recorded AI interview on 1-5: take them when rested, they usually allow one try.

## Background (user 2026-11-06: "describe everything i've done with u"; Claude's draft from the repo, check every line)

**Education:** University of South Florida (USF), Finance.

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
overfitting, wrong costs, time zones. Finance student at the University of South Florida (USF).

## Answers that come up on the AI-training platforms

- **Domain expertise?** Futures markets, systematic trading, backtesting and strategy validation, position sizing under
  prop-firm drawdown rules, reading and checking quant research papers.
- **Example of catching an error?** A strategy looked like it traded 15-minute bars from 08:30, but the chart session
  template started at 09:30 Central; the backtest numbers halved. I matched 4,704 trades against a port of the code,
  found the one-hour shift, and fixed the setup. (2026-11-03, `MULTICHARTS_PITFALLS.md`.)
- **Hours per week?** [your real number around the job, e.g. 10-15 evenings / weekends]
- **Coding?** I read, review and debug Python and PowerLanguage; I write code with AI assistants and verify it by running tests (e.g. replaying live trades against the backtest).

## Upwork / Fiverr gig

Title: **I'll code, backtest and audit your MultiCharts / TradeStation strategy**
- What you get: your idea coded in PowerLanguage/EasyLanguage, a backtest with real commissions and slippage, an audit for
  look-ahead and overfitting, and live-setup notes (sessions, time zones, broker mapping, prop-firm limits).
- Starter price: [$40-80 for a small strategy] to get first reviews; raise after 3-5 five-star jobs.
- Rule: never trade a client's account and never promise returns.

## Anthropic Residency (stretch; by Nov 22)

Honest positioning: early-career, but a working example of careful empirical research done alone with AI tools.
Draft answer, "Why do you want to do this / relevant experience" (retype it yourself):
> For the past [N] weeks I have run a one-person research operation on financial markets, using AI coding agents to
> write the code while I set the questions and the rules for what counts as evidence. I learned the hard way that a
> result is cheap and a trustworthy result is not: I pre-register tests, hold out data, count every trial against a
> multiple-testing bar, and have a second AI independently rebuild candidates to catch my mistakes. Most of my ideas
> fail, and I keep records of why. I want to bring that discipline (evaluating whether a system really does what it
> appears to do) to AI safety, where the same failure modes, overfitting and fooling yourself, matter far more.
> [Your background in one or two lines.]

Attach: resume; optionally a short write-up of one test end to end (the live-vs-backtest replay is a good one).
