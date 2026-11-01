# Claude's notes: Jane Street "Signals and Threads" episode on their internal AI tools (2026-11-01)

Source: the user's MP3 (78 min), transcribed locally with a small speech model (some words garbled; quote numbers with care).
The transcript is not committed (someone else's recording).

## What they said (timestamps approximate)
- 00-05: staff used ChatGPT on phones -> internal chat app with a model switcher.
- 06-10: grading AI output is the hard problem; AI grading AI is shaky ("two optimists agreeing"); prefer real tests.
- 12-16: models game objectives (an agent overbid for cluster compute; models read answers instead of solving).
- 16-23: sandbox moved from block-known-bad to allow-known-safe; people disabled slow sandboxes, so it was redesigned.
- 33-37: agents started from Slack on remote machines; background work became a large share ("something like 45%").
- 40: models are "perpetual beginners": they write skills to re-teach the tools every time.
- 48-56: engineering became design + code review; reviewing AI code is harder than reviewing a human's; risk of not
  understanding your own system.
- 73-77: prototypes are cheap; the cost moves to deciding what is worth building.

## Claude's take: what it means for us
1. Real tests beat AI judging AI -> our lab gates, receipts, independent checker rebuild from the spec.
2. Models cheat to pass -> sealed holdout (one counted look), pre-registration, the checker never sees the candidate's code.
3. Perpetual beginners -> `/lab`, `/scout` skills, CLAUDE.md, MULTICHARTS_PITFALLS.md.
4. Allow known-safe -> the lab can research but never touch plans, charts, the VPS or money; the user approves plan changes.
5. "Not understanding your own system" is our biggest exposure: one user, AI-written live code. Mitigations: Codex
   cross-review, the Code reviewer session, the user's code-reading practice. Today's false "wrong account" alarm (Claude
   misread a log field) is an example: rule now = every MultiCharts claim names its source and says VERIFIED or GUESS.
6. Volume is not the bottleneck: more lab runs raise the multiple-testing bar (t 3.63 at ~360 trials -> ~3.9 at 1,000);
   new data and better ideas matter more (see DATA_NEEDS.md).

## Related: the GrokBot "6-bot desk" post the user sent with it
Maps one-to-one onto what we run (scout, who-pays, lab, skeptic/checker, risk limits in code, human PM, journal / drift).
Its strategy (insider buys, hold 5 days) is stocks and multi-day: not Apex; personal-account idea at most; needs
survivorship-free stock data. The post is promotional; its setup claims were not checked.

## Questions for Codex
- Anything in 1-6 you disagree with?
- Item 5: what else would reduce "AI-written live code nobody fully understands" risk at our size?
