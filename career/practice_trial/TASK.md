# Practice trial: review a strategy submission

**Setting.** You are the reviewer. A contractor submitted the research note below and the code in `orb_research.py`. The
client wants to trade it on a prop account (flat by 15:59 CT, $2,000 end-of-day trailing drawdown). Decide whether the
claims hold.

**Rules (like a real trial):** work alone, no AI help, **2 hours**. You don't need to run the code (there's no data
attached); read it. Write your review in `career/practice_trial/MY_REVIEW.md` or paste it in chat.

**Your review should list:** each problem you find (where: note or line), why it matters (which way it biases the
result: too good / too bad / unknown), and how severe it is (fatal / major / minor). End with an overall verdict: accept,
revise, or reject, in 2-3 sentences. Quality of reasoning counts more than the number of findings.

---

## The submitted note: "NQ Opening Range Momentum, a robust edge"

**Idea.** The first 15 minutes of the NQ session reveal institutional direction. Trade the breakout of the 08:30-08:45 CT
range in the direction of the break, on days when the market is "active".

**Rule.**
- Opening range = high / low of 08:30-08:45 CT.
- Active day filter: the day's high-low range > 1.2 x ATR(14).
- Long if a 1-minute bar closes above the range high (short below the low), first signal only, entry at that bar's close.
- Stop: the other side of the range. Target: 2 x range width. Otherwise exit at the next day's open.

**Parameters.** I tested range lengths 5 / 10 / 15 / 20 / 30 / 45 minutes, ATR multipliers 0.8 / 1.0 / 1.2 / 1.4, and
targets 1R / 2R (48 combinations) on 2018-2026 and picked the best: 15 minutes, 1.2 x ATR, 2R.

**Results (1 NQ contract, 2018-2026).**
- 1,412 trades, 61% winners, average +$412 per trade, total +$581,744.
- Sharpe 4.1, max drawdown $9,800.
- **Out of sample (2023-2026): +$248,300, Sharpe 3.9, so the edge is robust.**
- t-stat 8.7, far above any significance threshold.

**Conclusion.** Ready for live trading at 2 NQ on a 50K prop account.
